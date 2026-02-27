"""
AdmitGuard — SQLite Database Layer
Sprint 3+: Persistent storage using SQLite (built-in Python module).

Database file: admitguard.db (created next to this file on first run)

Tables:
  - candidates: one row per submitted candidate
  - audit_log:  one row per submission event
"""

import sqlite3
import os

# Database file lives in the backend directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admitguard.db")


def get_connection():
    """Return a SQLite connection with Row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # Better concurrency
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist. Called on app startup."""
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS candidates (
                id                      TEXT PRIMARY KEY,
                full_name               TEXT NOT NULL,
                email                   TEXT NOT NULL UNIQUE,
                phone                   TEXT NOT NULL,
                date_of_birth           TEXT,
                highest_qualification   TEXT NOT NULL,
                graduation_year         TEXT,
                percentage_cgpa         TEXT,
                score_type              TEXT DEFAULT 'percentage',
                screening_test_score    TEXT,
                interview_status        TEXT NOT NULL,
                aadhaar                 TEXT NOT NULL,
                offer_letter_sent       TEXT NOT NULL,
                exceptions              TEXT DEFAULT '[]',
                exception_count         INTEGER DEFAULT 0,
                flagged_for_review      INTEGER DEFAULT 0,
                submitted_at            TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id                  TEXT PRIMARY KEY,
                candidate_id        TEXT NOT NULL,
                candidate_name      TEXT NOT NULL,
                candidate_email     TEXT NOT NULL,
                action              TEXT NOT NULL DEFAULT 'SUBMISSION',
                exception_count     INTEGER DEFAULT 0,
                flagged_for_review  INTEGER DEFAULT 0,
                exceptions          TEXT DEFAULT '[]',
                timestamp           TEXT NOT NULL
            );
        """)
    conn.close()
