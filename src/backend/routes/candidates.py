"""
AdmitGuard — Candidate API Routes
Sprint 1: Validate, Create, List candidates (strict rules only).
"""

from flask import Blueprint, request, jsonify

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.strict_validators import validate_all_strict
from models.candidate import (
    add_candidate,
    get_all_candidates,
    get_candidate_by_id,
    get_all_emails,
    get_candidate_count,
)

candidates_bp = Blueprint("candidates", __name__)


@candidates_bp.route("/api/validate", methods=["POST"])
def validate_candidate():
    """
    Validate candidate data against all strict rules.
    Returns per-field validation results.
    
    Request body: JSON with candidate fields
    Response: {
        "valid": bool,
        "errors": { field: error_message, ... },
        "results": { field: { "valid": bool, "error": str|null }, ... }
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"valid": False, "error": "Request body is required."}), 400

    existing_emails = get_all_emails()
    results = validate_all_strict(data, existing_emails)

    # Collect errors
    errors = {}
    for field, result in results.items():
        if not result["valid"]:
            errors[field] = result["error"]

    is_valid = len(errors) == 0

    return jsonify({
        "valid": is_valid,
        "errors": errors,
        "results": results,
    }), 200


@candidates_bp.route("/api/validate/<field_name>", methods=["POST"])
def validate_single_field(field_name):
    """
    Validate a single field.
    Useful for real-time field-level validation from frontend.
    
    Request body: JSON with candidate fields (at minimum the field being validated)
    Response: { "valid": bool, "error": str|null }
    """
    data = request.get_json()
    if not data:
        return jsonify({"valid": False, "error": "Request body is required."}), 400

    existing_emails = get_all_emails()

    # Map field names to validator functions
    from validators.strict_validators import (
        validate_full_name,
        validate_email,
        validate_phone,
        validate_qualification,
        validate_interview_status,
        validate_aadhaar,
        validate_offer_letter,
    )

    validators = {
        "full_name": lambda: validate_full_name(data.get("full_name", "")),
        "email": lambda: validate_email(data.get("email", ""), existing_emails),
        "phone": lambda: validate_phone(data.get("phone", "")),
        "highest_qualification": lambda: validate_qualification(
            data.get("highest_qualification", "")
        ),
        "interview_status": lambda: validate_interview_status(
            data.get("interview_status", "")
        ),
        "aadhaar": lambda: validate_aadhaar(data.get("aadhaar", "")),
        "offer_letter_sent": lambda: validate_offer_letter(
            data.get("offer_letter_sent", ""),
            data.get("interview_status", ""),
        ),
    }

    if field_name not in validators:
        return jsonify({
            "valid": False,
            "error": f"Unknown field: {field_name}"
        }), 400

    result = validators[field_name]()
    return jsonify(result), 200


@candidates_bp.route("/api/candidates", methods=["POST"])
def create_candidate():
    """
    Submit a new candidate after validation.
    Validates all strict rules first — blocks if any fail.
    
    Request body: JSON with all candidate fields
    Response: Created candidate with ID and timestamp
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    # Validate all strict rules first
    existing_emails = get_all_emails()
    results = validate_all_strict(data, existing_emails)

    errors = {}
    for field, result in results.items():
        if not result["valid"]:
            errors[field] = result["error"]

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed. Please fix the errors below.",
            "errors": errors,
        }), 422

    # All validations passed — store the candidate
    candidate = add_candidate(data)

    return jsonify({
        "success": True,
        "message": "Candidate submitted successfully.",
        "candidate": candidate,
    }), 201


@candidates_bp.route("/api/candidates", methods=["GET"])
def list_candidates():
    """
    List all submitted candidates.
    
    Response: { "candidates": [...], "total": int }
    """
    candidates = get_all_candidates()
    return jsonify({
        "candidates": candidates,
        "total": len(candidates),
    }), 200


@candidates_bp.route("/api/candidates/<candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    """
    Get a single candidate by ID.
    
    Response: candidate object or 404
    """
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return jsonify({"error": "Candidate not found."}), 404

    return jsonify({"candidate": candidate}), 200
