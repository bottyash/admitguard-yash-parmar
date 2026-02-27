"""
AdmitGuard — Admin API Routes
Provides login/logout, candidate listing, editing and deletion for the admin panel.
Access the admin UI at: /prabandhak
"""

from functools import wraps
from flask import Blueprint, request, jsonify, session

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.candidate import (
    get_all_candidates,
    get_candidate_by_id,
    update_candidate,
    delete_candidate,
    get_candidate_count,
    get_flagged_count,
    get_exception_rate,
)

admin_bp = Blueprint("admin", __name__)

# ---------------------------------------------------------------------------
# Default admin credentials (hardcoded for development)
# ---------------------------------------------------------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------
def admin_required(f):
    """Decorator that ensures the request comes from a logged-in admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Unauthorized. Please login."}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body required."}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return jsonify({"success": True, "message": "Login successful."}), 200

    return jsonify({"success": False, "error": "Invalid credentials."}), 401


@admin_bp.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out."}), 200


@admin_bp.route("/api/admin/status", methods=["GET"])
def admin_status():
    """Check if currently logged in."""
    if session.get("admin_logged_in"):
        return jsonify({"logged_in": True, "user": session.get("admin_user")}), 200
    return jsonify({"logged_in": False}), 200


# ---------------------------------------------------------------------------
# Admin CRUD endpoints
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/candidates", methods=["GET"])
@admin_required
def admin_list_candidates():
    candidates = get_all_candidates()
    return jsonify({
        "candidates": candidates,
        "total": len(candidates),
        "stats": {
            "total": get_candidate_count(),
            "flagged": get_flagged_count(),
            "exception_rate": get_exception_rate(),
        },
    }), 200


@admin_bp.route("/api/admin/candidates/<candidate_id>", methods=["GET"])
@admin_required
def admin_get_candidate(candidate_id):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return jsonify({"error": "Candidate not found."}), 404
    return jsonify({"candidate": candidate}), 200


@admin_bp.route("/api/admin/candidates/<candidate_id>", methods=["PUT"])
@admin_required
def admin_update_candidate(candidate_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required."}), 400

    updated = update_candidate(candidate_id, data)
    if not updated:
        return jsonify({"error": "Candidate not found."}), 404

    return jsonify({
        "success": True,
        "message": "Candidate updated.",
        "candidate": updated,
    }), 200


@admin_bp.route("/api/admin/candidates/<candidate_id>", methods=["DELETE"])
@admin_required
def admin_delete_candidate(candidate_id):
    deleted = delete_candidate(candidate_id)
    if not deleted:
        return jsonify({"error": "Candidate not found."}), 404

    return jsonify({
        "success": True,
        "message": "Candidate deleted.",
    }), 200
