"""
AdmitGuard v2 — Admin API Routes
Provides login/logout, candidate CRUD, cohort management, email system,
and Sheets sync for the admin panel.
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
    get_dashboard_stats,
    clear_all_candidates,
)
from models.cohort import (
    create_cohort,
    get_all_cohorts,
    get_cohort_by_id,
    update_cohort,
    get_cohort_params,
    update_cohort_params,
    get_effective_rules,
    get_tweakable_params,
)
from models.email_log import (
    log_email,
    get_emails_for_candidate,
    get_all_emails_log,
    get_unread_reply_count,
    mark_reply_read,
    log_incoming_reply,
)
from services import email_service
from services import google_sheets
from intelligence import llm_assistant

admin_bp = Blueprint("admin", __name__)

# ---------------------------------------------------------------------------
# Admin credentials from environment (fallback to defaults for dev)
# ---------------------------------------------------------------------------
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


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


# ===========================================================================
# AUTHENTICATION
# ===========================================================================

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
    if session.get("admin_logged_in"):
        return jsonify({
            "logged_in": True,
            "user": session.get("admin_user"),
            "unread_replies": get_unread_reply_count(),
        }), 200
    return jsonify({"logged_in": False}), 200


# ===========================================================================
# CANDIDATES
# ===========================================================================

@admin_bp.route("/api/admin/candidates", methods=["GET"])
@admin_required
def admin_list_candidates():
    candidates = get_all_candidates()
    stats = get_dashboard_stats()
    return jsonify({
        "candidates": candidates,
        "total": len(candidates),
        "stats": stats,
    }), 200


@admin_bp.route("/api/admin/candidates/<candidate_id>", methods=["GET"])
@admin_required
def admin_get_candidate(candidate_id):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return jsonify({"error": "Candidate not found."}), 404
    # Include email thread
    emails = get_emails_for_candidate(candidate_id)
    return jsonify({"candidate": candidate, "emails": emails}), 200


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
        "success": True, "message": "Candidate updated.", "candidate": updated,
    }), 200


@admin_bp.route("/api/admin/candidates/<candidate_id>", methods=["DELETE"])
@admin_required
def admin_delete_candidate(candidate_id):
    deleted = delete_candidate(candidate_id)
    if not deleted:
        return jsonify({"error": "Candidate not found."}), 404
    return jsonify({"success": True, "message": "Candidate deleted."}), 200


# ===========================================================================
# COHORTS
# ===========================================================================

@admin_bp.route("/api/admin/cohorts", methods=["GET"])
@admin_required
def list_cohorts():
    cohorts = get_all_cohorts()
    return jsonify({"cohorts": cohorts, "total": len(cohorts)}), 200


@admin_bp.route("/api/admin/cohorts", methods=["POST"])
@admin_required
def create_new_cohort():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Cohort name is required."}), 400
    cohort = create_cohort(data["name"], data.get("description", ""))
    return jsonify({"success": True, "cohort": cohort}), 201


@admin_bp.route("/api/admin/cohorts/<cohort_id>", methods=["GET"])
@admin_required
def get_cohort_detail(cohort_id):
    cohort = get_cohort_by_id(cohort_id)
    if not cohort:
        return jsonify({"error": "Cohort not found."}), 404
    return jsonify({"cohort": cohort}), 200


@admin_bp.route("/api/admin/cohorts/<cohort_id>", methods=["PUT"])
@admin_required
def update_cohort_detail(cohort_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required."}), 400
    updated = update_cohort(
        cohort_id,
        name=data.get("name"),
        description=data.get("description"),
        is_active=data.get("is_active"),
    )
    if not updated:
        return jsonify({"error": "Cohort not found."}), 404
    return jsonify({"success": True, "cohort": updated}), 200


@admin_bp.route("/api/admin/cohorts/<cohort_id>/params", methods=["GET"])
@admin_required
def get_params(cohort_id):
    params = get_cohort_params(cohort_id)
    effective = get_effective_rules(cohort_id)
    tweakable = get_tweakable_params()
    return jsonify({
        "params": params,
        "effective_rules": effective,
        "tweakable": tweakable,
    }), 200


@admin_bp.route("/api/admin/cohorts/<cohort_id>/params", methods=["PUT"])
@admin_required
def update_params(cohort_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required."}), 400
    updated = update_cohort_params(cohort_id, data)
    if updated is None:
        return jsonify({"error": "Cohort not found."}), 404
    return jsonify({
        "success": True,
        "params": updated,
        "effective_rules": get_effective_rules(cohort_id),
    }), 200


# ===========================================================================
# EMAIL
# ===========================================================================

@admin_bp.route("/api/admin/email/send", methods=["POST"])
@admin_required
def send_email():
    """Send email to a candidate. Optionally use LLM to draft."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required."}), 400

    candidate_id = data.get("candidate_id", "")
    to_email = data.get("to_email", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not to_email or not subject or not body:
        return jsonify({"error": "to_email, subject, and body are required."}), 400

    result = email_service.send_email(to_email, subject, body, candidate_id)

    if result["success"]:
        log_email(
            candidate_id=candidate_id,
            to_email=to_email,
            subject=subject,
            body=body,
            direction="SENT",
            status="sent",
            message_id=result.get("message_id", ""),
        )
        return jsonify({"success": True, "message": f"Email sent to {to_email}."}), 200
    else:
        return jsonify({
            "success": False,
            "error": result.get("error", "Failed to send email."),
        }), 500


@admin_bp.route("/api/admin/email/draft", methods=["POST"])
@admin_required
def draft_email():
    """Use LLM to generate an email draft."""
    data = request.get_json() or {}
    candidate_data = data.get("candidate", {})
    purpose = data.get("purpose", "followup")
    draft = llm_assistant.draft_email(candidate_data, purpose)
    return jsonify(draft), 200


@admin_bp.route("/api/admin/email/replies", methods=["GET"])
@admin_required
def check_email_replies():
    """Check IMAP for new replies and log them."""
    replies = email_service.check_replies()
    new_count = 0
    for reply in replies:
        # Check if already logged (by message_id)
        from_email = reply.get("from", "")
        # Extract email from "Name <email>" format
        if "<" in from_email and ">" in from_email:
            from_email = from_email.split("<")[1].split(">")[0]

        log_incoming_reply(
            from_email=from_email.strip(),
            subject=reply.get("subject", ""),
            body=reply.get("body", ""),
            message_id=reply.get("message_id", ""),
        )
        new_count += 1

    return jsonify({
        "success": True,
        "new_replies": new_count,
        "unread_count": get_unread_reply_count(),
    }), 200


@admin_bp.route("/api/admin/email/log", methods=["GET"])
@admin_required
def email_log():
    """Get email log, optionally filtered by direction."""
    direction = request.args.get("direction")
    emails = get_all_emails_log(direction=direction)
    return jsonify({
        "emails": emails,
        "total": len(emails),
        "unread_count": get_unread_reply_count(),
    }), 200


@admin_bp.route("/api/admin/email/<candidate_id>/thread", methods=["GET"])
@admin_required
def email_thread(candidate_id):
    """Get email thread for a specific candidate."""
    emails = get_emails_for_candidate(candidate_id)
    return jsonify({"emails": emails, "total": len(emails)}), 200


@admin_bp.route("/api/admin/email/<email_id>/read", methods=["POST"])
@admin_required
def mark_read(email_id):
    """Mark an email reply as read."""
    mark_reply_read(email_id)
    return jsonify({"success": True}), 200


# ===========================================================================
# GOOGLE SHEETS
# ===========================================================================

@admin_bp.route("/api/admin/sheets/status", methods=["GET"])
@admin_required
def sheets_status():
    available = google_sheets.is_available()
    return jsonify({"available": available}), 200


@admin_bp.route("/api/admin/sheets/sync-all", methods=["POST"])
@admin_required
def sheets_sync_all():
    """Trigger a full resync of all candidates to Google Sheets."""
    candidates = get_all_candidates()
    success = google_sheets.sync_all_candidates(candidates)
    return jsonify({
        "success": success,
        "message": f"Synced {len(candidates)} candidates." if success else "Sync failed.",
    }), 200 if success else 500


# ===========================================================================
# SERVICE STATUS
# ===========================================================================

@admin_bp.route("/api/admin/services", methods=["GET"])
@admin_required
def service_status():
    """Return status of all external services."""
    return jsonify({
        "email": {"available": email_service.is_available()},
        "google_sheets": {"available": google_sheets.is_available()},
        "llm": {
            "available": llm_assistant.is_available(),
            "model": llm_assistant.OLLAMA_MODEL,
        },
    }), 200
