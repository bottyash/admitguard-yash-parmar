"""
AdmitGuard — Candidate Data Model
Sprint 2: In-memory storage with exception tracking and audit log.
"""

import uuid
from datetime import datetime


# In-memory stores
_candidates = []
_audit_log = []


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


def add_candidate(data, exceptions_applied=None, exception_count=0, flagged_for_review=False):
    """
    Add a new candidate record to the store.
    Sprint 2: Now includes exception details and flagging.
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
        # Sprint 2: Exception tracking
        "exceptions": exceptions_applied or [],
        "exception_count": exception_count,
        "flagged_for_review": flagged_for_review,
        "submitted_at": datetime.now().isoformat(),
    }

    _candidates.append(candidate)

    # Add to audit log
    log_entry = {
        "id": str(uuid.uuid4()),
        "candidate_id": candidate["id"],
        "candidate_name": candidate["full_name"],
        "candidate_email": candidate["email"],
        "action": "SUBMISSION",
        "exception_count": exception_count,
        "flagged_for_review": flagged_for_review,
        "exceptions": exceptions_applied or [],
        "timestamp": candidate["submitted_at"],
    }
    _audit_log.append(log_entry)

    return candidate


def get_candidate_count():
    """Return total number of candidates."""
    return len(_candidates)


def get_flagged_count():
    """Return count of candidates flagged for manager review."""
    return sum(1 for c in _candidates if c.get("flagged_for_review"))


def get_exception_rate():
    """Return the percentage of candidates with at least one exception."""
    if not _candidates:
        return 0.0
    with_exceptions = sum(1 for c in _candidates if c.get("exception_count", 0) > 0)
    return round((with_exceptions / len(_candidates)) * 100, 1)


def get_audit_log():
    """Return the full audit log, newest first."""
    return list(reversed(_audit_log))


def clear_all_candidates():
    """Clear all candidate records and audit log (for testing)."""
    _candidates.clear()
    _audit_log.clear()
