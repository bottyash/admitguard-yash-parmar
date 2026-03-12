"""
AdmitGuard v2 — Candidate Data Model
Persistent storage via SQLite with 7-table schema.
Handles candidates + education_entries + work_entries.
"""

import uuid
import json
from datetime import datetime
from db import get_connection


# =============================================================================
# CREATE
# =============================================================================

def add_candidate(data, education_entries=None, work_entries=None,
                  intelligence=None, flags=None, llm_flags=None):
    """
    Add a new candidate with education entries, work entries, and intelligence.
    Returns the created candidate dict with nested education/work.
    """
    candidate_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    intel = intelligence or {}
    flags_json = json.dumps(flags or [])
    llm_flags_json = json.dumps(llm_flags or [])

    conn = get_connection()
    with conn:
        # Insert candidate
        conn.execute("""
            INSERT INTO candidates (
                id, full_name, email, phone, date_of_birth, aadhaar,
                education_path, risk_score, category, data_quality_score,
                experience_bucket, completeness_pct, flags,
                llm_verification_flags, anomaly_narration,
                flagged_for_review, cohort_id, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            data.get("full_name", "").strip(),
            data.get("email", "").strip().lower(),
            data.get("phone", "").strip(),
            data.get("date_of_birth", "").strip(),
            data.get("aadhaar", "").strip(),
            data.get("education_path", "A"),
            intel.get("risk_score", 0),
            intel.get("category", "Pending"),
            intel.get("data_quality_score", 0),
            intel.get("experience_bucket", "Fresher"),
            intel.get("completeness_pct", 0),
            flags_json,
            llm_flags_json,
            intel.get("anomaly_narration", ""),
            1 if intel.get("flagged_for_review") else 0,
            data.get("cohort_id"),
            now,
        ))

        # Insert education entries
        for i, edu in enumerate(education_entries or []):
            edu_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO education_entries (
                    id, candidate_id, level, board_university, stream,
                    year_of_passing, score, score_scale, normalized_score,
                    backlog_count, gap_months, sort_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                edu_id, candidate_id,
                edu.get("level", ""),
                edu.get("board_university", ""),
                edu.get("stream", ""),
                edu.get("year_of_passing"),
                edu.get("score"),
                edu.get("score_scale", "percentage"),
                edu.get("normalized_score", 0),
                edu.get("backlog_count", 0),
                edu.get("gap_months", 0),
                i,
            ))

        # Insert work entries
        for i, work in enumerate(work_entries or []):
            work_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO work_entries (
                    id, candidate_id, company_name, designation, domain,
                    start_date, end_date, employment_type, skills,
                    tenure_months, sort_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                work_id, candidate_id,
                work.get("company_name", ""),
                work.get("designation", ""),
                work.get("domain", "Other"),
                work.get("start_date", ""),
                work.get("end_date", ""),
                work.get("employment_type", "Full-time"),
                json.dumps(work.get("skills", [])),
                work.get("tenure_months", 0),
                i,
            ))

        # Audit log entry
        log_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO audit_log (
                id, candidate_id, candidate_name, candidate_email,
                action, details, cohort_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, candidate_id,
            data.get("full_name", "").strip(),
            data.get("email", "").strip().lower(),
            "SUBMISSION",
            json.dumps({
                "risk_score": intel.get("risk_score", 0),
                "category": intel.get("category", "Pending"),
                "flags": flags or [],
            }),
            data.get("cohort_id"),
            now,
        ))

    conn.close()
    return get_candidate_by_id(candidate_id)


# =============================================================================
# READ
# =============================================================================

def get_all_candidates():
    """Return all candidates as list of dicts (without nested entries for list view)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM candidates ORDER BY submitted_at DESC"
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_candidate_by_id(candidate_id):
    """Return a candidate with nested education_entries and work_entries."""
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None

    candidate = _row_to_dict(row)

    # Fetch education entries
    edu_rows = conn.execute(
        "SELECT * FROM education_entries WHERE candidate_id = ? ORDER BY sort_order",
        (candidate_id,)
    ).fetchall()
    candidate["education_entries"] = [_row_to_dict(r) for r in edu_rows]

    # Fetch work entries
    work_rows = conn.execute(
        "SELECT * FROM work_entries WHERE candidate_id = ? ORDER BY sort_order",
        (candidate_id,)
    ).fetchall()
    candidate["work_entries"] = [_work_row_to_dict(r) for r in work_rows]

    conn.close()
    return candidate


def get_all_emails():
    """Return list of all registered emails (for uniqueness check)."""
    conn = get_connection()
    rows = conn.execute("SELECT email FROM candidates").fetchall()
    conn.close()
    return [r["email"] for r in rows]


def get_all_phones():
    """Return list of all registered phones (for uniqueness check)."""
    conn = get_connection()
    rows = conn.execute("SELECT phone FROM candidates").fetchall()
    conn.close()
    return [r["phone"] for r in rows]


# =============================================================================
# STATS
# =============================================================================

def get_candidate_count():
    """Return total number of candidates."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    conn.close()
    return count


def get_flagged_count():
    """Return count of candidates flagged for review."""
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM candidates WHERE flagged_for_review = 1"
    ).fetchone()[0]
    conn.close()
    return count


def get_exception_rate():
    """Return % of candidates flagged for review."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    flagged = conn.execute(
        "SELECT COUNT(*) FROM candidates WHERE flagged_for_review = 1"
    ).fetchone()[0]
    conn.close()
    if total == 0:
        return 0.0
    return round((flagged / total) * 100, 1)


def get_dashboard_stats():
    """Return comprehensive dashboard statistics."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    flagged = conn.execute(
        "SELECT COUNT(*) FROM candidates WHERE flagged_for_review = 1"
    ).fetchone()[0]

    # Category distribution
    categories = {}
    cat_rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM candidates GROUP BY category"
    ).fetchall()
    for r in cat_rows:
        categories[r["category"]] = r["cnt"]

    # Average risk score
    avg_risk = conn.execute(
        "SELECT AVG(risk_score) FROM candidates"
    ).fetchone()[0] or 0

    conn.close()

    exception_rate = round((flagged / total) * 100, 1) if total > 0 else 0.0

    return {
        "total_submissions": total,
        "flagged_count": flagged,
        "exception_rate": exception_rate,
        "avg_risk_score": round(avg_risk, 1),
        "category_distribution": categories,
    }


# =============================================================================
# AUDIT LOG
# =============================================================================

def get_audit_log():
    """Return audit log entries, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [_audit_row_to_dict(r) for r in rows]


# =============================================================================
# UPDATE / DELETE
# =============================================================================

def update_candidate(candidate_id, data):
    """
    Update editable fields of an existing candidate.
    Returns the updated candidate dict, or None if not found.
    """
    editable_fields = [
        "full_name", "email", "phone", "date_of_birth",
        "aadhaar", "education_path", "cohort_id",
    ]

    updates = []
    values = []
    for field in editable_fields:
        if field in data:
            updates.append(f"{field} = ?")
            val = data[field]
            values.append(str(val).strip() if val is not None else "")

    if not updates:
        return get_candidate_by_id(candidate_id)

    values.append(candidate_id)
    sql = f"UPDATE candidates SET {', '.join(updates)} WHERE id = ?"

    conn = get_connection()
    with conn:
        cursor = conn.execute(sql, values)
        if cursor.rowcount == 0:
            conn.close()
            return None

        now = datetime.now().isoformat()
        log_id = str(uuid.uuid4())
        candidate = conn.execute(
            "SELECT full_name, email FROM candidates WHERE id = ?",
            (candidate_id,)
        ).fetchone()
        conn.execute("""
            INSERT INTO audit_log (
                id, candidate_id, candidate_name, candidate_email,
                action, details, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, candidate_id,
            candidate["full_name"] if candidate else "",
            candidate["email"] if candidate else "",
            "ADMIN_EDIT",
            json.dumps({"updated_fields": list(data.keys())}),
            now,
        ))
    conn.close()
    return get_candidate_by_id(candidate_id)


def delete_candidate(candidate_id):
    """
    Delete a candidate by ID. Returns True if deleted, False if not found.
    Child rows (education, work, emails) cascade-deleted via FK.
    """
    conn = get_connection()
    candidate = conn.execute(
        "SELECT full_name, email FROM candidates WHERE id = ?",
        (candidate_id,)
    ).fetchone()

    if not candidate:
        conn.close()
        return False

    with conn:
        now = datetime.now().isoformat()
        log_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO audit_log (
                id, candidate_id, candidate_name, candidate_email,
                action, details, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, candidate_id,
            candidate["full_name"], candidate["email"],
            "ADMIN_DELETE",
            json.dumps({}),
            now,
        ))
        conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.close()
    return True


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
    """Convert a sqlite3.Row to a plain dict with JSON deserialization."""
    if not row:
        return None
    d = dict(row)

    # Deserialize JSON fields
    for json_field in ("flags", "llm_verification_flags"):
        if isinstance(d.get(json_field), str):
            try:
                d[json_field] = json.loads(d[json_field])
            except (ValueError, TypeError):
                d[json_field] = []

    # Convert SQLite 0/1 to Python bool
    if "flagged_for_review" in d:
        d["flagged_for_review"] = bool(d.get("flagged_for_review", 0))
    if "is_active" in d:
        d["is_active"] = bool(d.get("is_active", 1))

    return d


def _work_row_to_dict(row):
    """Convert a work_entries Row with JSON skills field."""
    if not row:
        return None
    d = dict(row)
    if isinstance(d.get("skills"), str):
        try:
            d["skills"] = json.loads(d["skills"])
        except (ValueError, TypeError):
            d["skills"] = []
    return d


def _audit_row_to_dict(row):
    """Convert an audit_log Row with JSON details field."""
    if not row:
        return None
    d = dict(row)
    if isinstance(d.get("details"), str):
        try:
            d["details"] = json.loads(d["details"])
        except (ValueError, TypeError):
            d["details"] = {}
    return d
