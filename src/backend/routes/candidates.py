"""
AdmitGuard v2 — Candidate API Routes
Full 3-tier validation pipeline: HARD REJECT → SOFT FLAG → ENRICHMENT.
"""

from flask import Blueprint, request, jsonify, Response
import csv, io, json as _json

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelligence.risk_scorer import compute_risk_score
from intelligence.categorizer import categorize
from intelligence.data_quality import compute_data_quality
from intelligence import llm_assistant
from services import google_sheets

from validators.strict_validators import validate_all_strict
from validators.soft_validators import validate_all_soft, is_flagged_for_review
from validators.education_validators import validate_all_education
from validators.work_validators import validate_all_work
from models.candidate import (
    add_candidate,
    get_all_candidates,
    get_candidate_by_id,
    get_all_emails,
    get_all_phones,
    get_audit_log,
    get_dashboard_stats,
)

candidates_bp = Blueprint("candidates", __name__)


# =============================================================================
# 3-TIER VALIDATION (validate without saving)
# =============================================================================

@candidates_bp.route("/api/validate", methods=["POST"])
def validate_candidate():
    """
    Full 3-tier validation preview — does NOT save.
    Returns Tier 1 errors, Tier 2 flags, and Tier 3 enrichment.
    """
    data = request.get_json()
    if not data:
        return jsonify({"valid": False, "error": "Request body is required."}), 400

    existing_emails = get_all_emails()
    existing_phones = get_all_phones()

    # ---- TIER 1: HARD REJECT ----
    tier1 = validate_all_strict(data, existing_emails, existing_phones)
    tier1_errors = {f: r["error"] for f, r in tier1.items() if not r["valid"]}

    # ---- Education validation ----
    education_entries = data.get("education_entries", [])
    education_path = data.get("education_path", "A")
    edu_result = None
    if education_entries:
        edu_result = validate_all_education(education_entries, education_path)
        if not edu_result["valid"]:
            # Path/chronological errors are Tier 1
            for err in edu_result.get("path_errors", []):
                tier1_errors[f"education_path"] = err
            for err in edu_result.get("chronological_errors", []):
                tier1_errors[f"education_chronology"] = err
            for ee in edu_result.get("entry_errors", []):
                for field, msg in ee["errors"].items():
                    tier1_errors[f"education[{ee['entry_index']}].{field}"] = msg

    # ---- Work validation ----
    work_entries = data.get("work_entries", [])
    work_result = None
    if work_entries:
        work_result = validate_all_work(work_entries)
        if not work_result["valid"]:
            for we in work_result.get("entry_errors", []):
                for field, msg in we["errors"].items():
                    tier1_errors[f"work[{we['entry_index']}].{field}"] = msg

    # ---- TIER 2: SOFT FLAGS ----
    tier2_flags = validate_all_soft(data, edu_result, work_result)

    # ---- Compute enrichment preview ----
    enrichment = {}
    if work_result:
        enrichment = work_result.get("derived", {})
    if edu_result:
        enrichment["total_education_gap_months"] = edu_result.get("total_gap_months", 0)
        enrichment["total_backlogs"] = edu_result.get("total_backlogs", 0)

    is_valid = len(tier1_errors) == 0

    return jsonify({
        "valid": is_valid,
        "tier1_errors": tier1_errors,
        "tier2_flags": tier2_flags,
        "enrichment": enrichment,
        "education_warnings": edu_result.get("warnings", []) if edu_result else [],
        "work_overlaps": work_result.get("overlaps", []) if work_result else [],
        "flagged_for_review": is_flagged_for_review(tier2_flags),
    }), 200


# =============================================================================
# SINGLE FIELD VALIDATION
# =============================================================================

@candidates_bp.route("/api/validate/<field_name>", methods=["POST"])
def validate_single_field(field_name):
    """Validate a single field (Tier 1 only — instant feedback)."""
    data = request.get_json()
    if not data:
        return jsonify({"valid": False, "error": "Request body is required."}), 400

    existing_emails = get_all_emails()
    existing_phones = get_all_phones()

    from validators.strict_validators import (
        validate_full_name,
        validate_email,
        validate_phone,
        validate_age,
        validate_aadhaar,
    )

    validators = {
        "full_name": lambda: validate_full_name(data.get("full_name", "")),
        "email": lambda: validate_email(data.get("email", ""), existing_emails),
        "phone": lambda: validate_phone(data.get("phone", ""), existing_phones),
        "date_of_birth": lambda: validate_age(data.get("date_of_birth", "")),
        "aadhaar": lambda: validate_aadhaar(data.get("aadhaar", "")),
    }

    if field_name in validators:
        result = validators[field_name]()
        return jsonify(result), 200

    return jsonify({"valid": False, "error": f"Unknown field: {field_name}"}), 400


# =============================================================================
# SUBMISSION — Full 3-Tier Pipeline
# =============================================================================

@candidates_bp.route("/api/candidates", methods=["POST"])
def create_candidate():
    """
    Submit a new candidate through the full 3-tier pipeline:
      Tier 1: HARD REJECT → if fails, 422 with errors
      Tier 2: SOFT FLAG → data saved but flagged
      Tier 3: ENRICHMENT → derived fields computed and stored
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    existing_emails = get_all_emails()
    existing_phones = get_all_phones()
    education_entries = data.get("education_entries", [])
    work_entries = data.get("work_entries", [])
    education_path = data.get("education_path", "A")

    # ================================================================
    # TIER 1: HARD REJECT
    # ================================================================
    tier1 = validate_all_strict(data, existing_emails, existing_phones)
    tier1_errors = {f: r["error"] for f, r in tier1.items() if not r["valid"]}

    # Education validation (path + chronological = Tier 1)
    edu_result = None
    if education_entries:
        edu_result = validate_all_education(education_entries, education_path)
        if not edu_result["valid"]:
            for err in edu_result.get("path_errors", []):
                tier1_errors["education_path"] = err
            for err in edu_result.get("chronological_errors", []):
                tier1_errors["education_chronology"] = err
            for ee in edu_result.get("entry_errors", []):
                for field, msg in ee["errors"].items():
                    tier1_errors[f"education[{ee['entry_index']}].{field}"] = msg

    # Work validation (entry errors = Tier 1)
    work_result = None
    if work_entries:
        work_result = validate_all_work(work_entries)
        if not work_result["valid"]:
            for we in work_result.get("entry_errors", []):
                for field, msg in we["errors"].items():
                    tier1_errors[f"work[{we['entry_index']}].{field}"] = msg

    if tier1_errors:
        return jsonify({
            "success": False,
            "tier": 1,
            "message": "Validation failed. Please fix the errors below.",
            "errors": tier1_errors,
        }), 422

    # ================================================================
    # TIER 2: SOFT FLAGS
    # ================================================================
    tier2_flags = validate_all_soft(data, edu_result, work_result)
    flagged = is_flagged_for_review(tier2_flags)

    # ================================================================
    # TIER 3: ENRICHMENT
    # ================================================================
    # Get enriched education entries (with normalized scores + gap months)
    enriched_education = edu_result["entries"] if edu_result else education_entries
    enriched_work = work_result["entries"] if work_result else work_entries

    # Compute intelligence
    work_derived = work_result.get("derived", {}) if work_result else {}
    completeness = _compute_completeness(data, education_entries, work_entries)

    # Risk scoring (7-factor weighted 0-100)
    risk_result = compute_risk_score(
        education_result=edu_result,
        work_result=work_result,
        completeness_pct=completeness,
    )
    risk_score = risk_result["risk_score"]

    # Auto-categorization
    cat_result = categorize(risk_score)
    category = cat_result["category"]

    # Data quality
    dq_result = compute_data_quality(data, education_entries, work_entries, tier2_flags)

    # Anomaly narration via LLM (graceful fallback)
    narration = llm_assistant.narrate_flags(data, tier2_flags, risk_score, category)

    # LLM verification flags (async-safe: won't block if Ollama is down)
    llm_flags = []
    if education_entries and llm_assistant.is_available():
        try:
            consistency = llm_assistant.verify_education_consistency(education_entries)
            if not consistency.get("consistent", True):
                for flag_msg in consistency.get("flags", []):
                    llm_flags.append({"type": "LLM_EDUCATION", "message": flag_msg})
        except Exception:
            pass  # Never let LLM break submission

    intelligence = {
        "risk_score": risk_score,
        "category": category,
        "data_quality_score": dq_result["score"],
        "experience_bucket": work_derived.get("experience_bucket", "Fresher"),
        "completeness_pct": completeness,
        "anomaly_narration": narration,
        "flagged_for_review": flagged or risk_score > 60,
    }

    # ================================================================
    # SAVE
    # ================================================================
    candidate = add_candidate(
        data,
        education_entries=enriched_education,
        work_entries=enriched_work,
        intelligence=intelligence,
        flags=tier2_flags,
        llm_flags=llm_flags,
    )

    # ================================================================
    # GOOGLE SHEETS SYNC (fire-and-forget, never blocks submission)
    # ================================================================
    try:
        google_sheets.sync_candidate(candidate, enriched_education, enriched_work)
    except Exception:
        pass  # Never let Sheets sync break submission

    response = {
        "success": True,
        "tier": 3,
        "message": "Candidate submitted successfully.",
        "candidate": candidate,
        "tier2_flags": tier2_flags,
        "llm_flags": llm_flags,
        "intelligence": {
            "risk_score": risk_score,
            "risk_breakdown": risk_result["breakdown"],
            "category": category,
            "category_confidence": cat_result["confidence"],
            "data_quality": dq_result,
            "experience_bucket": work_derived.get("experience_bucket", "Fresher"),
            "anomaly_narration": narration,
        },
        "flagged_for_review": intelligence["flagged_for_review"],
    }

    if intelligence["flagged_for_review"]:
        response["warning"] = (
            f"⚠️ Risk score {risk_score}/100 ({category}). "
            f"{len(tier2_flags)} flag(s) — flagged for review."
        )

    return jsonify(response), 201


# =============================================================================
# READ ENDPOINTS
# =============================================================================

@candidates_bp.route("/api/candidates", methods=["GET"])
def list_candidates():
    """List all submitted candidates."""
    candidates = get_all_candidates()
    return jsonify({"candidates": candidates, "total": len(candidates)}), 200


@candidates_bp.route("/api/candidates/<candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    """Get a single candidate by ID with full detail."""
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return jsonify({"error": "Candidate not found."}), 404
    return jsonify({"candidate": candidate}), 200


@candidates_bp.route("/api/audit-log", methods=["GET"])
def audit_log():
    """Get the audit log."""
    log = get_audit_log()
    return jsonify({"log": log, "total": len(log)}), 200


@candidates_bp.route("/api/dashboard", methods=["GET"])
def dashboard():
    """Get dashboard statistics."""
    stats = get_dashboard_stats()
    return jsonify(stats), 200


# =============================================================================
# EXPORT
# =============================================================================

@candidates_bp.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Export all candidates as CSV."""
    candidates = get_all_candidates()
    fields = [
        "id", "full_name", "email", "phone", "date_of_birth",
        "aadhaar", "education_path", "risk_score", "category",
        "data_quality_score", "experience_bucket", "completeness_pct",
        "flagged_for_review", "submitted_at",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for c in candidates:
        row = {f: c.get(f, "") for f in fields}
        row["flagged_for_review"] = "Yes" if c.get("flagged_for_review") else "No"
        writer.writerow(row)
    output.seek(0)
    return Response(
        output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=admitguard_v2_export.csv"},
    )


@candidates_bp.route("/api/export/json", methods=["GET"])
def export_json():
    """Export all candidates as JSON."""
    candidates = get_all_candidates()
    payload = _json.dumps(candidates, indent=2, ensure_ascii=False)
    return Response(
        payload, mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=admitguard_v2_export.json"},
    )


# =============================================================================
# HELPERS
# =============================================================================

def _compute_completeness(data, education_entries, work_entries):
    """Compute data completeness percentage (0-100)."""
    total_fields = 0
    filled_fields = 0

    # Core fields
    core = ["full_name", "email", "phone", "date_of_birth", "aadhaar", "education_path"]
    for f in core:
        total_fields += 1
        if data.get(f):
            filled_fields += 1

    # Education entries
    edu_fields = ["level", "board_university", "year_of_passing", "score"]
    for entry in education_entries:
        for f in edu_fields:
            total_fields += 1
            if entry.get(f):
                filled_fields += 1

    # Work entries
    work_fields = ["company_name", "designation", "domain", "start_date"]
    for entry in work_entries:
        for f in work_fields:
            total_fields += 1
            if entry.get(f):
                filled_fields += 1

    if total_fields == 0:
        return 0
    return round((filled_fields / total_fields) * 100, 1)
