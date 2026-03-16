"""
AdmitGuard v2 — LLM API Routes
Endpoints for all LLM-powered features.
All endpoints gracefully degrade if Ollama is unavailable.
"""

from flask import Blueprint, request, jsonify

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelligence import llm_assistant

llm_bp = Blueprint("llm", __name__)


@llm_bp.route("/api/llm/status", methods=["GET"])
def llm_status():
    """Check if Ollama LLM is available."""
    available = llm_assistant.is_available()
    return jsonify({
        "available": available,
        "model": llm_assistant.OLLAMA_MODEL,
        "base_url": llm_assistant.OLLAMA_BASE_URL,
    }), 200


# =============================================================================
# 1. UNIVERSITY / BOARD AUTOCOMPLETE
# =============================================================================

@llm_bp.route("/api/llm/suggest", methods=["POST"])
def suggest():
    """Suggest university/board names based on partial input."""
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    level = data.get("level", "UG")
    if not query or len(query) < 2:
        return jsonify({"suggestions": []}), 200
    suggestions = llm_assistant.suggest_universities(query, level)
    return jsonify({"suggestions": suggestions}), 200


# =============================================================================
# 2. FIELD EXPLAINER
# =============================================================================

@llm_bp.route("/api/llm/explain", methods=["POST"])
def explain():
    """Get explanation for a form field."""
    data = request.get_json() or {}
    field = data.get("field", "").strip()
    context = data.get("context", "")
    if not field:
        return jsonify({"error": "field is required."}), 400
    explanation = llm_assistant.explain_field(field, context)
    return jsonify({"field": field, "explanation": explanation}), 200


# =============================================================================
# 3. SOFT DOC VERIFICATION
# =============================================================================

@llm_bp.route("/api/llm/verify/board", methods=["POST"])
def verify_board():
    """Verify a board/university name."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    level = data.get("level", "10th")
    if not name:
        return jsonify({"error": "name is required."}), 400
    result = llm_assistant.verify_board_name(name, level)
    return jsonify(result), 200


@llm_bp.route("/api/llm/verify/degree", methods=["POST"])
def verify_degree():
    """Verify a degree-stream match for a university."""
    data = request.get_json() or {}
    university = data.get("university", "").strip()
    degree = data.get("degree", "").strip()
    stream = data.get("stream", "").strip()
    if not university or not degree:
        return jsonify({"error": "university and degree are required."}), 400
    result = llm_assistant.verify_degree_stream_match(university, degree, stream)
    return jsonify(result), 200


@llm_bp.route("/api/llm/verify/education", methods=["POST"])
def verify_education():
    """Verify full education history consistency."""
    data = request.get_json() or {}
    entries = data.get("entries", [])
    if not entries:
        return jsonify({"error": "entries are required."}), 400
    result = llm_assistant.verify_education_consistency(entries)
    return jsonify(result), 200


@llm_bp.route("/api/llm/verify/company", methods=["POST"])
def verify_company():
    """Verify a company name for a given domain."""
    data = request.get_json() or {}
    company = data.get("company_name", "").strip()
    domain = data.get("domain", "Other")
    if not company:
        return jsonify({"error": "company_name is required."}), 400
    result = llm_assistant.verify_company(company, domain)
    return jsonify(result), 200


# =============================================================================
# 5. IN-FORM CHAT
# =============================================================================

@llm_bp.route("/api/llm/chat", methods=["POST"])
def chat():
    """Chat with the LLM assistant during form filling."""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    form_context = data.get("form_context")
    if not question:
        return jsonify({"error": "question is required."}), 400
    answer = llm_assistant.chat(question, form_context)
    return jsonify({"question": question, "answer": answer}), 200


# =============================================================================
# 6. EMAIL DRAFT
# =============================================================================

@llm_bp.route("/api/llm/email-draft", methods=["POST"])
def email_draft():
    """Generate an email draft for a candidate."""
    data = request.get_json() or {}
    candidate_data = data.get("candidate", {})
    purpose = data.get("purpose", "followup")
    if not candidate_data:
        return jsonify({"error": "candidate data is required."}), 400
    result = llm_assistant.draft_email(candidate_data, purpose)
    return jsonify(result), 200


# =============================================================================
# 7. ADMIN NL QUERY
# =============================================================================

@llm_bp.route("/api/llm/query", methods=["POST"])
def nl_query():
    """Convert natural language to filter parameters."""
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "query is required."}), 400
    filters = llm_assistant.query_to_filter(query)
    return jsonify({"query": query, "filters": filters}), 200


# =============================================================================
# 8. PROFILE SUMMARY
# =============================================================================

@llm_bp.route("/api/llm/profile-summary", methods=["POST"])
def profile_summary():
    """Generate a profile summary for a candidate."""
    data = request.get_json() or {}
    candidate_data = data.get("candidate", {})
    education = data.get("education_entries", [])
    work = data.get("work_entries", [])
    if not candidate_data:
        return jsonify({"error": "candidate data is required."}), 400
    summary = llm_assistant.analyze_profile(candidate_data, education, work)
    return jsonify({"summary": summary}), 200
