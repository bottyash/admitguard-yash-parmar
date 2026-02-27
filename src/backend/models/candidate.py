"""
AdmitGuard — Candidate Data Model
Sprint 3+: Persistent storage via SQLite (uses db.py).
All function signatures stay identical to previous sprint.
"""

import uuid
import json
from datetime import datetime
from db import get_connection


def get_all_candidates():
    """Return all stored candidates as list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM candidates ORDER BY submitted_at DESC").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_candidate_by_id(candidate_id):
    """Return a candidate by their ID, or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
    ).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_all_emails():
    """Return list of all registered emails (for uniqueness check)."""
    conn = get_connection()
    rows = conn.execute("SELECT email FROM candidates").fetchall()
    conn.close()
    return [r["email"] for r in rows]


def add_candidate(data, exceptions_applied=None, exception_count=0, flagged_for_review=False):
    """
    Add a new candidate record to the database.
    Returns the created candidate as a dict.
    """
    candidate_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    exceptions_json = json.dumps(exceptions_applied or [])

    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO candidates (
                id, full_name, email, phone, date_of_birth,
                highest_qualification, graduation_year, percentage_cgpa,
                score_type, screening_test_score, interview_status,
                aadhaar, offer_letter_sent, exceptions,
                exception_count, flagged_for_review, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            data.get("full_name", "").strip(),
            data.get("email", "").strip().lower(),
            data.get("phone", "").strip(),
            data.get("date_of_birth", "").strip(),
            data.get("highest_qualification", "").strip(),
            str(data.get("graduation_year", "")),
            str(data.get("percentage_cgpa", "")),
            data.get("score_type", "percentage").strip(),
            str(data.get("screening_test_score", "")),
            data.get("interview_status", "").strip(),
            data.get("aadhaar", "").strip(),
            data.get("offer_letter_sent", "").strip(),
            exceptions_json,
            exception_count,
            1 if flagged_for_review else 0,
            now,
        ))

        # Insert audit log entry
        log_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO audit_log (
                id, candidate_id, candidate_name, candidate_email,
                action, exception_count, flagged_for_review, exceptions, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            candidate_id,
            data.get("full_name", "").strip(),
            data.get("email", "").strip().lower(),
            "SUBMISSION",
            exception_count,
            1 if flagged_for_review else 0,
            exceptions_json,
            now,
        ))

    conn.close()

    return {
        "id": candidate_id,
        "full_name": data.get("full_name", "").strip(),
        "email": data.get("email", "").strip().lower(),
        "phone": data.get("phone", "").strip(),
        "date_of_birth": data.get("date_of_birth", "").strip(),
        "highest_qualification": data.get("highest_qualification", "").strip(),
        "graduation_year": str(data.get("graduation_year", "")),
        "percentage_cgpa": str(data.get("percentage_cgpa", "")),
        "score_type": data.get("score_type", "percentage").strip(),
        "screening_test_score": str(data.get("screening_test_score", "")),
        "interview_status": data.get("interview_status", "").strip(),
        "aadhaar": data.get("aadhaar", "").strip(),
        "offer_letter_sent": data.get("offer_letter_sent", "").strip(),
        "exceptions": exceptions_applied or [],
        "exception_count": exception_count,
        "flagged_for_review": flagged_for_review,
        "submitted_at": now,
    }


def get_candidate_count():
    """Return total number of candidates."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    conn.close()
    return count


def get_flagged_count():
    """Return count of candidates flagged for manager review."""
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM candidates WHERE flagged_for_review = 1"
    ).fetchone()[0]
    conn.close()
    return count


def get_exception_rate():
    """Return % of candidates with at least one exception."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    with_exc = conn.execute(
        "SELECT COUNT(*) FROM candidates WHERE exception_count > 0"
    ).fetchone()[0]
    conn.close()
    if total == 0:
        return 0.0
    return round((with_exc / total) * 100, 1)


def get_audit_log():
    """Return audit log entries, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [_audit_row_to_dict(r) for r in rows]


def clear_all_candidates():
    """Clear all data (for testing only)."""
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM candidates")
        conn.execute("DELETE FROM audit_log")
    conn.close()


# =============================================================================
# Private helpers
# =============================================================================

def _row_to_dict(row):
    """Convert a sqlite3.Row to a plain dict."""
    if not row:
        return None
    d = dict(row)
    # Deserialize JSON fields
    if isinstance(d.get("exceptions"), str):
        try:
            d["exceptions"] = json.loads(d["exceptions"])
        except (ValueError, TypeError):
            d["exceptions"] = []
    # Convert SQLite 0/1 back to Python bool
    d["flagged_for_review"] = bool(d.get("flagged_for_review", 0))
    return d


def _audit_row_to_dict(row):
    """Convert an audit_log sqlite3.Row to a plain dict."""
    if not row:
        return None
    d = dict(row)
    if isinstance(d.get("exceptions"), str):
        try:
            d["exceptions"] = json.loads(d["exceptions"])
        except (ValueError, TypeError):
            d["exceptions"] = []
    d["flagged_for_review"] = bool(d.get("flagged_for_review", 0))
    return d
