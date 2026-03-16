"""
AdmitGuard v2 — Email Log Model
Tracks sent/received emails per candidate for the admin dashboard.
"""

import uuid
import json
from datetime import datetime
from db import get_connection


def log_email(candidate_id, to_email, subject, body, direction="SENT",
              status="sent", message_id="", cohort_id=None):
    """
    Log an email to the email_log table.
    direction: SENT or RECEIVED
    """
    email_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO email_log (
                id, candidate_id, to_email, subject, body,
                direction, status, message_id, cohort_id, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_id, candidate_id, to_email, subject, body,
            direction, status, message_id, cohort_id, now,
        ))
    conn.close()
    return email_id


def get_emails_for_candidate(candidate_id):
    """Get all emails (sent + received) for a candidate, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM email_log WHERE candidate_id = ? ORDER BY sent_at DESC",
        (candidate_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_emails_log(direction=None, limit=100):
    """Get all email logs, optionally filtered by direction."""
    conn = get_connection()
    if direction:
        rows = conn.execute(
            "SELECT * FROM email_log WHERE direction = ? ORDER BY sent_at DESC LIMIT ?",
            (direction, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM email_log ORDER BY sent_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unread_reply_count():
    """Count received emails with status 'unread'."""
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM email_log WHERE direction = 'RECEIVED' AND status = 'unread'"
    ).fetchone()[0]
    conn.close()
    return count


def mark_reply_read(email_id):
    """Mark a received email as read."""
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE email_log SET status = 'read' WHERE id = ?",
            (email_id,)
        )
    conn.close()


def log_incoming_reply(from_email, subject, body, message_id=""):
    """
    Log an incoming reply. Tries to match to a candidate by email.
    """
    conn = get_connection()
    # Try to find candidate by email
    candidate = conn.execute(
        "SELECT id FROM candidates WHERE email = ?",
        (from_email.strip().lower(),)
    ).fetchone()
    candidate_id = candidate["id"] if candidate else ""
    conn.close()

    return log_email(
        candidate_id=candidate_id,
        to_email=from_email,
        subject=subject,
        body=body,
        direction="RECEIVED",
        status="unread",
        message_id=message_id,
    )
