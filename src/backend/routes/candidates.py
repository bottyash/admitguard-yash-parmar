"""
AdmitGuard — Candidate API Routes
Sprint 2: Validate (strict + soft), exception handling, create, list, audit log.
"""

from flask import Blueprint, request, jsonify

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.strict_validators import validate_all_strict
from validators.soft_validators import (
    validate_all_soft,
    count_exceptions,
    is_flagged_for_review,
    validate_date_of_birth,
    validate_graduation_year,
    validate_percentage_cgpa,
    validate_screening_score,
    validate_rationale,
)
from models.candidate import (
    add_candidate,
    get_all_candidates,
    get_candidate_by_id,
    get_all_emails,
    get_candidate_count,
    get_flagged_count,
    get_exception_rate,
    get_audit_log,
)

candidates_bp = Blueprint("candidates", __name__)


@candidates_bp.route("/api/validate", methods=["POST"])
def validate_candidate():
    """
    Validate candidate data against ALL rules (strict + soft).
    Handles exception overrides for soft rules.
    
    Request body: {
        ...candidate fields...,
        "exceptions": {
            "field_name": {"enabled": true, "rationale": "..."},
            ...
        }
    }
    Response: {
        "valid": bool,
        "errors": { field: error_message, ... },
        "strict_results": { ... },
        "soft_results": { ... },
        "exception_count": int,
        "flagged_for_review": bool
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"valid": False, "error": "Request body is required."}), 400

    existing_emails = get_all_emails()

    # Run strict validations
    strict_results = validate_all_strict(data, existing_emails)

    # Run soft validations with exception handling
    exceptions = data.get("exceptions", {})
    soft_results = validate_all_soft(data, exceptions)

    # Collect all errors
    errors = {}
    soft_errors = {}

    for field, result in strict_results.items():
        if not result["valid"]:
            errors[field] = result["error"]

    for field, result in soft_results.items():
        if not result["valid"]:
            if result.get("exception_allowed"):
                soft_errors[field] = {
                    "error": result["error"],
                    "exception_allowed": True,
                    "rationale_error": result.get("rationale_error"),
                }
            else:
                errors[field] = result["error"]

    # Calculate exception stats
    exception_count = count_exceptions(soft_results)
    flagged = is_flagged_for_review(exception_count)

    is_valid = len(errors) == 0 and len(soft_errors) == 0

    return jsonify({
        "valid": is_valid,
        "errors": errors,
        "soft_errors": soft_errors,
        "strict_results": strict_results,
        "soft_results": soft_results,
        "exception_count": exception_count,
        "flagged_for_review": flagged,
    }), 200


@candidates_bp.route("/api/validate/<field_name>", methods=["POST"])
def validate_single_field(field_name):
    """
    Validate a single field (strict or soft).
    For soft fields, also handles exception + rationale validation.
    
    Request body: JSON with candidate fields + optional exceptions
    Response: { "valid": bool, "error": str|null, ... }
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

    strict_validators = {
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

    soft_validators = {
        "date_of_birth": lambda: validate_date_of_birth(data.get("date_of_birth", "")),
        "graduation_year": lambda: validate_graduation_year(data.get("graduation_year", "")),
        "percentage_cgpa": lambda: validate_percentage_cgpa(
            data.get("percentage_cgpa", ""),
            data.get("score_type", "percentage"),
        ),
        "screening_test_score": lambda: validate_screening_score(
            data.get("screening_test_score", "")
        ),
    }

    if field_name in strict_validators:
        result = strict_validators[field_name]()
        result["rule_type"] = "strict"
        return jsonify(result), 200

    if field_name in soft_validators:
        result = soft_validators[field_name]()

        # Check if exception is being applied
        exceptions = data.get("exceptions", {})
        exception_info = exceptions.get(field_name, {})
        exception_enabled = exception_info.get("enabled", False)

        result["exception_applied"] = False
        result["rationale_valid"] = None
        result["rationale_error"] = None

        if not result["valid"] and result.get("exception_allowed") and exception_enabled:
            rationale = exception_info.get("rationale", "")
            rationale_result = validate_rationale(rationale)
            result["rationale_valid"] = rationale_result["valid"]
            result["rationale_error"] = rationale_result.get("error")

            if rationale_result["valid"]:
                result["exception_applied"] = True
                result["valid"] = True
                result["error"] = None

        return jsonify(result), 200

    return jsonify({"valid": False, "error": f"Unknown field: {field_name}"}), 400


@candidates_bp.route("/api/candidates", methods=["POST"])
def create_candidate():
    """
    Submit a new candidate after full validation (strict + soft).
    Blocks if strict rules fail or soft rules fail without valid exceptions.
    
    Request body: {
        ...candidate fields...,
        "exceptions": {
            "field_name": {"enabled": true, "rationale": "..."},
            ...
        }
    }
    Response: Created candidate with ID, timestamp, and exception details
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    # ---- Strict validation ----
    existing_emails = get_all_emails()
    strict_results = validate_all_strict(data, existing_emails)

    strict_errors = {}
    for field, result in strict_results.items():
        if not result["valid"]:
            strict_errors[field] = result["error"]

    if strict_errors:
        return jsonify({
            "success": False,
            "message": "Strict validation failed. These errors cannot be overridden.",
            "errors": strict_errors,
        }), 422

    # ---- Soft validation with exceptions ----
    exceptions = data.get("exceptions", {})
    soft_results = validate_all_soft(data, exceptions)

    soft_errors = {}
    for field, result in soft_results.items():
        if not result["valid"]:
            soft_errors[field] = {
                "error": result["error"],
                "exception_allowed": result.get("exception_allowed", False),
                "rationale_error": result.get("rationale_error"),
            }

    if soft_errors:
        return jsonify({
            "success": False,
            "message": "Soft rule validation failed. Enable exceptions with valid rationale to override.",
            "soft_errors": soft_errors,
        }), 422

    # ---- All passed — collect exception details ----
    exception_count = count_exceptions(soft_results)
    flagged = is_flagged_for_review(exception_count)

    exceptions_applied = []
    for field, result in soft_results.items():
        if result.get("exception_applied"):
            exception_info = exceptions.get(field, {})
            exceptions_applied.append({
                "field": field,
                "rationale": exception_info.get("rationale", ""),
            })

    # Store candidate
    candidate = add_candidate(
        data,
        exceptions_applied=exceptions_applied,
        exception_count=exception_count,
        flagged_for_review=flagged,
    )

    response = {
        "success": True,
        "message": "Candidate submitted successfully.",
        "candidate": candidate,
        "exception_count": exception_count,
        "flagged_for_review": flagged,
    }

    if flagged:
        response["warning"] = f"⚠️ This entry has {exception_count} exceptions and has been flagged for manager review."

    return jsonify(response), 201


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


@candidates_bp.route("/api/audit-log", methods=["GET"])
def audit_log():
    """
    Get the audit log of all submissions with exception details.
    Response: { "log": [...], "total": int }
    """
    log = get_audit_log()
    return jsonify({
        "log": log,
        "total": len(log),
    }), 200


@candidates_bp.route("/api/dashboard", methods=["GET"])
def dashboard():
    """
    Get dashboard statistics.
    Response: {
        "total_submissions": int,
        "flagged_count": int,
        "exception_rate": float
    }
    """
    return jsonify({
        "total_submissions": get_candidate_count(),
        "flagged_count": get_flagged_count(),
        "exception_rate": get_exception_rate(),
    }), 200
