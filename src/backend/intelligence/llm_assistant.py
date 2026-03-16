"""
AdmitGuard v2 — LLM Assistant
All AI/LLM features via local Ollama (qwen3:4b).

Features:
  1. University/board autocomplete
  2. Field explainer
  3. Soft doc verification (board, degree-stream, education consistency, company)
  4. Anomaly narration
  5. In-form chat
  6. Email draft suggestions
  7. Admin NL query → filter
  8. Profile summary
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# Ollama config from env
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")

# Try importing ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama package not installed. LLM features disabled.")


def _llm_call(prompt, system_prompt="", max_tokens=500):
    """
    Make a call to local Ollama. Returns response text or None on failure.
    Graceful fallback: never crashes, always returns None if unavailable.
    """
    if not OLLAMA_AVAILABLE:
        return None

    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"num_predict": max_tokens, "temperature": 0.3},
        )
        return response.get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.warning(f"Ollama call failed: {e}")
        return None


def _llm_json_call(prompt, system_prompt=""):
    """LLM call that expects JSON response. Parses and returns dict or None."""
    system = system_prompt + "\nRespond ONLY with valid JSON, no markdown, no explanation."
    text = _llm_call(prompt, system, max_tokens=600)
    if not text:
        return None
    try:
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return None


def is_available():
    """Check if LLM is available."""
    if not OLLAMA_AVAILABLE:
        return False
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        client.list()
        return True
    except Exception:
        return False


# =============================================================================
# 1. UNIVERSITY / BOARD AUTOCOMPLETE
# =============================================================================

def suggest_universities(query, level="UG"):
    """
    Suggest Indian university/board names based on partial input.
    Returns: list of suggestion strings.
    """
    prompt = (
        f"List 5 real Indian {'boards' if level in ('10th', '12th') else 'universities'} "
        f"matching '{query}' for {level} level education. "
        f"Return ONLY a JSON array of name strings, nothing else. "
        f"Example: [\"CBSE\", \"ICSE\"]"
    )
    result = _llm_json_call(prompt, "You are an Indian education expert.")
    if isinstance(result, list):
        return result[:5]
    return []


# =============================================================================
# 2. FIELD EXPLAINER
# =============================================================================

def explain_field(field_name, context=""):
    """
    Provide contextual help for a form field.
    Returns: explanation string.
    """
    explanations = {
        "education_path": "Indian education has 3 pathways:\n- Path A (Standard): 10th → 12th → UG\n- Path B (Diploma): 10th → Diploma → UG (Lateral Entry)\n- Path C (Lateral): 10th → ITI/Vocational → Diploma → UG",
        "lateral_entry": "Lateral entry allows Diploma holders to join directly into the 2nd year of a B.Tech/B.E. program, skipping the 1st year.",
        "score_scale": "Score scales:\n- Percentage: Out of 100\n- CGPA/10: Multiply by 9.5 to get approximate percentage\n- CGPA/4: Multiply by 25 to get approximate percentage",
        "backlog_count": "Backlogs are subjects you failed and need to re-attempt. Enter the total number of backlogs across all semesters.",
        "aadhaar": "Aadhaar is a 12-digit unique identification number issued by UIDAI to Indian residents.",
    }

    # Return static answer if available (faster)
    if field_name in explanations:
        return explanations[field_name]

    # Fall back to LLM for unknown fields
    prompt = (
        f"Explain the form field '{field_name}' in the context of an "
        f"Indian university admission application. {context} "
        f"Keep it under 3 sentences, simple language."
    )
    result = _llm_call(prompt, "You are a helpful admission counselor.")
    return result or f"This field asks for your {field_name.replace('_', ' ')}."


# =============================================================================
# 3. SOFT DOCUMENT VERIFICATION
# =============================================================================

def verify_board_name(name, level="10th"):
    """Check if a board/university name is a recognized Indian institution."""
    prompt = (
        f"Is '{name}' a real, recognized Indian "
        f"{'education board' if level in ('10th', '12th') else 'university/institution'} "
        f"for {level} level? "
        f"Return JSON: {{\"verified\": true/false, \"confidence\": 0.0-1.0, "
        f"\"flag_reason\": null or string, \"suggestion\": null or correct name}}"
    )
    result = _llm_json_call(
        prompt,
        "You are an Indian education verification expert. Be strict but fair."
    )
    if result and isinstance(result, dict):
        return {
            "verified": result.get("verified", True),
            "confidence": result.get("confidence", 0.5),
            "flag_reason": result.get("flag_reason"),
            "suggestion": result.get("suggestion"),
        }
    return {"verified": True, "confidence": 0.5, "flag_reason": None, "suggestion": None}


def verify_degree_stream_match(university, degree, stream):
    """Check if a university offers the claimed degree+stream."""
    prompt = (
        f"Does '{university}' offer '{degree}' in '{stream}'? "
        f"Return JSON: {{\"verified\": true/false, \"confidence\": 0.0-1.0, "
        f"\"flag_reason\": null or string}}"
    )
    result = _llm_json_call(
        prompt,
        "You are an Indian education verification expert."
    )
    if result and isinstance(result, dict):
        return {
            "verified": result.get("verified", True),
            "confidence": result.get("confidence", 0.5),
            "flag_reason": result.get("flag_reason"),
        }
    return {"verified": True, "confidence": 0.5, "flag_reason": None}


def verify_education_consistency(entries):
    """Check full education history for plausibility."""
    edu_summary = []
    for e in entries:
        edu_summary.append(
            f"{e.get('level', '?')}: {e.get('board_university', '?')} - "
            f"{e.get('stream', 'N/A')} ({e.get('year_of_passing', '?')})"
        )

    prompt = (
        f"Review this Indian student's education history for consistency:\n"
        f"{chr(10).join(edu_summary)}\n\n"
        f"Check for: board mismatches (e.g. CBSE 10th then SSC 12th), "
        f"impossible combinations (B.Tech from a commerce college), "
        f"or suspicious patterns.\n"
        f"Return JSON: {{\"consistent\": true/false, \"flags\": [\"issue1\", ...]}}"
    )
    result = _llm_json_call(
        prompt,
        "You are an Indian education verification expert. Flag only genuine concerns."
    )
    if result and isinstance(result, dict):
        return {
            "consistent": result.get("consistent", True),
            "flags": result.get("flags", []),
        }
    return {"consistent": True, "flags": []}


def verify_company(company_name, domain):
    """Check if a company name is plausible for the claimed domain."""
    prompt = (
        f"Is '{company_name}' a real or plausible company in the '{domain}' domain in India? "
        f"Return JSON: {{\"verified\": true/false, \"confidence\": 0.0-1.0, "
        f"\"flag_reason\": null or string}}"
    )
    result = _llm_json_call(
        prompt,
        "You are a verification expert. Be lenient with startups and small companies."
    )
    if result and isinstance(result, dict):
        return {
            "verified": result.get("verified", True),
            "confidence": result.get("confidence", 0.5),
            "flag_reason": result.get("flag_reason"),
        }
    return {"verified": True, "confidence": 0.5, "flag_reason": None}


# =============================================================================
# 4. ANOMALY NARRATION
# =============================================================================

def narrate_flags(candidate_data, flags, risk_score=0, category=""):
    """
    Generate a human-readable explanation of WHY a candidate was flagged.
    Returns: narration string.
    """
    if not flags and risk_score <= 30:
        return "No concerns identified. Candidate appears to be a strong fit."

    flag_summary = "\n".join(
        f"- [{f.get('type', 'FLAG')}] {f.get('message', '')}"
        for f in flags
    )

    prompt = (
        f"Candidate: {candidate_data.get('full_name', 'Unknown')}\n"
        f"Risk Score: {risk_score}/100 | Category: {category}\n"
        f"Flags:\n{flag_summary}\n\n"
        f"Write a concise 2-3 sentence explanation of the key concerns for "
        f"an admission reviewer. Be professional and factual."
    )
    result = _llm_call(
        prompt,
        "You are an admission review assistant. Be concise and factual."
    )
    if result:
        return result

    # Fallback: generate basic narration without LLM
    parts = []
    parts.append(f"Risk score {risk_score}/100 ({category}).")
    for f in flags[:3]:
        parts.append(f.get("message", ""))
    return " ".join(parts)


# =============================================================================
# 5. IN-FORM CHAT
# =============================================================================

def chat(question, form_context=None):
    """
    Answer a user's question during form filling.
    form_context: dict of current form state for context-aware help.
    """
    context_str = ""
    if form_context:
        path = form_context.get("education_path", "")
        if path:
            context_str = f"The student selected education Path {path}. "

    prompt = (
        f"{context_str}"
        f"Student's question while filling an admission form: {question}\n\n"
        f"Give a helpful, concise answer (2-3 sentences max). "
        f"Focus on Indian education system context."
    )
    result = _llm_call(
        prompt,
        "You are a helpful admission counselor for an Indian university. "
        "Answer questions about the admission form clearly and briefly."
    )
    return result or "I'm sorry, I couldn't process your question right now. Please try again."


# =============================================================================
# 6. EMAIL DRAFT
# =============================================================================

def draft_email(candidate_data, purpose="followup"):
    """
    Generate a professional email draft for admin to send to a candidate.
    purpose: "followup", "missing_docs", "acceptance", "rejection", "query"
    """
    name = candidate_data.get("full_name", "Candidate")
    category = candidate_data.get("category", "Pending")
    risk = candidate_data.get("risk_score", 0)

    purposes = {
        "followup": "Follow up on their application status and any pending items.",
        "missing_docs": "Request missing or incomplete documents.",
        "acceptance": "Congratulate them on being shortlisted.",
        "rejection": "Politely inform them that their application was not selected.",
        "query": "Ask for clarification about discrepancies in their application.",
    }

    prompt = (
        f"Draft a professional email to {name} (Risk: {risk}, Category: {category}).\n"
        f"Purpose: {purposes.get(purpose, purpose)}\n\n"
        f"Return JSON: {{\"subject\": \"...\", \"body\": \"...\"}}\n"
        f"Keep the body under 150 words. Be professional and warm."
    )
    result = _llm_json_call(
        prompt,
        "You are an admission office assistant composing emails."
    )
    if result and isinstance(result, dict):
        return {
            "subject": result.get("subject", f"Regarding Your Application - {name}"),
            "body": result.get("body", ""),
        }
    # Fallback
    return {
        "subject": f"Regarding Your Application - {name}",
        "body": f"Dear {name},\n\nThank you for your application. We are reviewing your submission and will get back to you shortly.\n\nBest regards,\nAdmissions Team",
    }


# =============================================================================
# 7. ADMIN NL QUERY
# =============================================================================

def query_to_filter(natural_language):
    """
    Convert a natural language query to filter parameters.
    Example: "Show flagged candidates with IT experience" →
             {"flagged_for_review": true, "domain": "IT"}
    """
    prompt = (
        f"Convert this search query to filter parameters for a candidates database:\n"
        f"\"{natural_language}\"\n\n"
        f"Available fields: full_name, email, education_path (A/B/C), "
        f"risk_score (0-100), category (Strong Fit/Needs Review/Weak Fit/Pending), "
        f"flagged_for_review (true/false), experience_bucket (Fresher/Junior/Mid/Senior), "
        f"cohort_id.\n\n"
        f"Return JSON with relevant filter key-value pairs only. "
        f"For ranges use: {{\"risk_score_min\": 30, \"risk_score_max\": 60}}\n"
        f"Example: {{\"category\": \"Strong Fit\", \"experience_bucket\": \"Mid\"}}"
    )
    result = _llm_json_call(
        prompt,
        "You are a database query assistant. Return only valid filter JSON."
    )
    return result if isinstance(result, dict) else {}


# =============================================================================
# 8. PROFILE SUMMARY
# =============================================================================

def analyze_profile(candidate_data, education_entries=None, work_entries=None):
    """
    Generate a natural-language profile summary for a candidate.
    Used on confirmation screen and admin detail view.
    """
    edu_summary = ""
    if education_entries:
        levels = [e.get("level", "?") for e in education_entries]
        edu_summary = f"Education: {' → '.join(levels)}. "

    work_summary = ""
    if work_entries:
        companies = [e.get("company_name", "?") for e in work_entries]
        work_summary = f"Work: {', '.join(companies)}. "

    name = candidate_data.get("full_name", "Unknown")
    risk = candidate_data.get("risk_score", 0)
    category = candidate_data.get("category", "Pending")

    prompt = (
        f"Summarize this admission applicant's profile in 3-4 sentences:\n"
        f"Name: {name}\n"
        f"{edu_summary}{work_summary}\n"
        f"Risk Score: {risk}/100 | Category: {category}\n"
        f"Path: {candidate_data.get('education_path', 'A')}\n\n"
        f"Highlight strengths and any concerns. Be balanced and professional."
    )
    result = _llm_call(
        prompt,
        "You are an admission review assistant providing candidate summaries."
    )
    return result or f"{name}: {category} candidate with risk score {risk}/100."
