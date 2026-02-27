"""
AdmitGuard — Candidate Data Model
Sprint 1: In-memory storage for candidate records.
"""

import uuid
from datetime import datetime


# In-memory store for candidates
_candidates = []


def get_all_candidates():
    """Return all stored candidates."""
    return list(_candidates)


def get_candidate_by_id(candidate_id):
    """Return a candidate by their ID."""
    for candidate in _candidates:
        if candidate["id"] == candidate_id:
            return candidate
    return None


def get_all_emails():
    """Return list of all registered emails (for uniqueness check)."""
    return [c["email"] for c in _candidates]


def add_candidate(data):
    """
    Add a new candidate record to the store.
    Returns the created candidate with ID and timestamp.
    """
    candidate = {
        "id": str(uuid.uuid4()),
        "full_name": data.get("full_name", "").strip(),
        "email": data.get("email", "").strip().lower(),
        "phone": data.get("phone", "").strip(),
        "date_of_birth": data.get("date_of_birth", "").strip(),
        "highest_qualification": data.get("highest_qualification", "").strip(),
        "graduation_year": data.get("graduation_year", ""),
        "percentage_cgpa": data.get("percentage_cgpa", ""),
        "score_type": data.get("score_type", "percentage").strip(),
        "screening_test_score": data.get("screening_test_score", ""),
        "interview_status": data.get("interview_status", "").strip(),
        "aadhaar": data.get("aadhaar", "").strip(),
        "offer_letter_sent": data.get("offer_letter_sent", "").strip(),
        "submitted_at": datetime.now().isoformat(),
    }

    _candidates.append(candidate)
    return candidate


def get_candidate_count():
    """Return total number of candidates."""
    return len(_candidates)


def clear_all_candidates():
    """Clear all candidate records (for testing)."""
    _candidates.clear()
