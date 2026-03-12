"""
AdmitGuard v2 — SQLite Database Layer
7 tables: candidates, education_entries, work_entries,
          cohorts, cohort_params, email_log, audit_log

Database file: admitguard.db (created next to this file on first run)
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
    """Create all tables if they don't exist. Called on app startup."""
    conn = get_connection()
    with conn:
        conn.executescript("""
            -- =================================================================
            -- CANDIDATES — Core applicant info + intelligence fields
            -- =================================================================
            CREATE TABLE IF NOT EXISTS candidates (
                id                      TEXT PRIMARY KEY,
                full_name               TEXT NOT NULL,
                email                   TEXT NOT NULL UNIQUE,
                phone                   TEXT NOT NULL,
                date_of_birth           TEXT,
                aadhaar                 TEXT NOT NULL,
                education_path          TEXT DEFAULT 'A',

                -- Intelligence layer outputs
                risk_score              REAL DEFAULT 0,
                category                TEXT DEFAULT 'Pending',
                data_quality_score      REAL DEFAULT 0,
                experience_bucket       TEXT DEFAULT 'Fresher',
                completeness_pct        REAL DEFAULT 0,

                -- Flags & status
                flags                   TEXT DEFAULT '[]',
                llm_verification_flags  TEXT DEFAULT '[]',
                anomaly_narration       TEXT DEFAULT '',
                flagged_for_review      INTEGER DEFAULT 0,

                -- Cohort association
                cohort_id               TEXT,

                -- Metadata
                submitted_at            TEXT NOT NULL,

                FOREIGN KEY (cohort_id) REFERENCES cohorts(id)
                    ON DELETE SET NULL
            );

            -- =================================================================
            -- EDUCATION ENTRIES — One row per education level per candidate
            -- =================================================================
            CREATE TABLE IF NOT EXISTS education_entries (
                id                  TEXT PRIMARY KEY,
                candidate_id        TEXT NOT NULL,
                level               TEXT NOT NULL,
                board_university    TEXT NOT NULL,
                stream              TEXT DEFAULT '',
                year_of_passing     INTEGER,
                score               REAL,
                score_scale         TEXT DEFAULT 'percentage',
                normalized_score    REAL DEFAULT 0,
                backlog_count       INTEGER DEFAULT 0,
                gap_months          INTEGER DEFAULT 0,
                sort_order          INTEGER DEFAULT 0,

                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                    ON DELETE CASCADE
            );

            -- =================================================================
            -- WORK ENTRIES — One row per job per candidate
            -- =================================================================
            CREATE TABLE IF NOT EXISTS work_entries (
                id                  TEXT PRIMARY KEY,
                candidate_id        TEXT NOT NULL,
                company_name        TEXT NOT NULL,
                designation         TEXT NOT NULL,
                domain              TEXT DEFAULT 'Other',
                start_date          TEXT,
                end_date            TEXT,
                employment_type     TEXT DEFAULT 'Full-time',
                skills              TEXT DEFAULT '[]',
                tenure_months       INTEGER DEFAULT 0,
                sort_order          INTEGER DEFAULT 0,

                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                    ON DELETE CASCADE
            );

            -- =================================================================
            -- COHORTS — Intake cohorts with customizable params
            -- =================================================================
            CREATE TABLE IF NOT EXISTS cohorts (
                id                  TEXT PRIMARY KEY,
                name                TEXT NOT NULL UNIQUE,
                description         TEXT DEFAULT '',
                is_active           INTEGER DEFAULT 1,
                created_at          TEXT NOT NULL
            );

            -- =================================================================
            -- COHORT PARAMS — Per-cohort rule overrides (key-value pairs)
            -- =================================================================
            CREATE TABLE IF NOT EXISTS cohort_params (
                id                  TEXT PRIMARY KEY,
                cohort_id           TEXT NOT NULL,
                param_name          TEXT NOT NULL,
                param_value         TEXT NOT NULL,

                FOREIGN KEY (cohort_id) REFERENCES cohorts(id)
                    ON DELETE CASCADE,
                UNIQUE(cohort_id, param_name)
            );

            -- =================================================================
            -- EMAIL LOG — Sent/received emails per candidate
            -- =================================================================
            CREATE TABLE IF NOT EXISTS email_log (
                id                  TEXT PRIMARY KEY,
                candidate_id        TEXT NOT NULL,
                subject             TEXT NOT NULL,
                body                TEXT NOT NULL,
                direction           TEXT NOT NULL DEFAULT 'SENT',
                status              TEXT DEFAULT 'delivered',
                message_id          TEXT DEFAULT '',
                sent_at             TEXT NOT NULL,

                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                    ON DELETE CASCADE
            );

            -- =================================================================
            -- AUDIT LOG — All actions (submissions, edits, deletes, emails)
            -- =================================================================
            CREATE TABLE IF NOT EXISTS audit_log (
                id                  TEXT PRIMARY KEY,
                candidate_id        TEXT,
                candidate_name      TEXT DEFAULT '',
                candidate_email     TEXT DEFAULT '',
                action              TEXT NOT NULL DEFAULT 'SUBMISSION',
                details             TEXT DEFAULT '{}',
                cohort_id           TEXT,
                timestamp           TEXT NOT NULL
            );
        """)
    conn.close()
