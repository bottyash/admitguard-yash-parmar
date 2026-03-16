"""
AdmitGuard v2 — Google Sheets Sync Service
Auto-syncs candidate data to a Google Sheet after submission.
Gracefully degrades if credentials are not configured.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# Config from .env
SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
SHEETS_WORKSHEET_NAME = os.getenv("GOOGLE_SHEETS_WORKSHEET_NAME", "AdmitGuard_v2")

# Try imports
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    logger.warning("gspread/google-auth not installed. Google Sheets sync disabled.")


def _get_client():
    """Get authenticated gspread client. Returns None if unavailable."""
    if not GSPREAD_AVAILABLE:
        return None
    if not SHEETS_SPREADSHEET_ID:
        logger.info("GOOGLE_SHEETS_SPREADSHEET_ID not set. Sheets sync disabled.")
        return None

    cred_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '..', '..', SHEETS_CREDENTIALS_FILE
    )
    if not os.path.exists(cred_path):
        logger.warning(f"Credentials file not found: {cred_path}")
        return None

    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(cred_path, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Google Sheets auth failed: {e}")
        return None


def is_available():
    """Check if Sheets sync is configured and available."""
    return _get_client() is not None


def _ensure_headers(worksheet):
    """Ensure the first row has column headers."""
    headers = [
        "ID", "Full Name", "Email", "Phone", "DOB", "Aadhaar",
        "Education Path", "Risk Score", "Category", "Data Quality",
        "Experience Bucket", "Completeness %", "Flagged",
        "Education Summary", "Work Summary", "Flags", "Submitted At",
    ]
    existing = worksheet.row_values(1)
    if not existing or existing[0] != "ID":
        worksheet.update("A1", [headers])


def sync_candidate(candidate, education_entries=None, work_entries=None):
    """
    Sync a candidate record to Google Sheets.
    Appends a new row. Returns True on success, False on failure.
    """
    client = _get_client()
    if not client:
        return False

    try:
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)

        # Get or create worksheet
        try:
            worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=SHEETS_WORKSHEET_NAME, rows=1000, cols=20
            )

        _ensure_headers(worksheet)

        # Build education summary
        edu_summary = ""
        if education_entries:
            parts = []
            for e in education_entries:
                level = e.get("level", "?")
                board = e.get("board_university", "?")
                score = e.get("normalized_score", e.get("score", "?"))
                parts.append(f"{level}: {board} ({score}%)")
            edu_summary = " | ".join(parts)

        # Build work summary
        work_summary = ""
        if work_entries:
            parts = []
            for w in work_entries:
                company = w.get("company_name", "?")
                role = w.get("designation", "?")
                parts.append(f"{company} ({role})")
            work_summary = " | ".join(parts)

        # Build flags summary
        flags = candidate.get("flags", [])
        if isinstance(flags, str):
            try:
                flags = json.loads(flags)
            except (json.JSONDecodeError, TypeError):
                flags = []
        flags_summary = "; ".join(
            f.get("message", str(f)) if isinstance(f, dict) else str(f)
            for f in flags
        )

        row = [
            candidate.get("id", ""),
            candidate.get("full_name", ""),
            candidate.get("email", ""),
            candidate.get("phone", ""),
            candidate.get("date_of_birth", ""),
            candidate.get("aadhaar", ""),
            candidate.get("education_path", ""),
            candidate.get("risk_score", 0),
            candidate.get("category", "Pending"),
            candidate.get("data_quality_score", 0),
            candidate.get("experience_bucket", "Fresher"),
            candidate.get("completeness_pct", 0),
            "Yes" if candidate.get("flagged_for_review") else "No",
            edu_summary,
            work_summary,
            flags_summary,
            candidate.get("submitted_at", ""),
        ]

        worksheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"Synced candidate {candidate.get('id')} to Google Sheets.")
        return True

    except Exception as e:
        logger.error(f"Google Sheets sync failed: {e}")
        return False


def sync_all_candidates(candidates):
    """Bulk sync all candidates. For admin-triggered full resync."""
    client = _get_client()
    if not client:
        return False

    try:
        spreadsheet = client.open_by_key(SHEETS_SPREADSHEET_ID)
        try:
            worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=SHEETS_WORKSHEET_NAME, rows=1000, cols=20
            )

        _ensure_headers(worksheet)

        rows = []
        for c in candidates:
            flags = c.get("flags", [])
            if isinstance(flags, str):
                try:
                    flags = json.loads(flags)
                except (json.JSONDecodeError, TypeError):
                    flags = []
            flags_summary = "; ".join(
                f.get("message", str(f)) if isinstance(f, dict) else str(f)
                for f in flags
            )
            rows.append([
                c.get("id", ""),
                c.get("full_name", ""),
                c.get("email", ""),
                c.get("phone", ""),
                c.get("date_of_birth", ""),
                c.get("aadhaar", ""),
                c.get("education_path", ""),
                c.get("risk_score", 0),
                c.get("category", "Pending"),
                c.get("data_quality_score", 0),
                c.get("experience_bucket", "Fresher"),
                c.get("completeness_pct", 0),
                "Yes" if c.get("flagged_for_review") else "No",
                "", "", flags_summary,
                c.get("submitted_at", ""),
            ])

        if rows:
            worksheet.append_rows(rows, value_input_option="USER_ENTERED")

        logger.info(f"Bulk synced {len(rows)} candidates to Google Sheets.")
        return True

    except Exception as e:
        logger.error(f"Bulk sync failed: {e}")
        return False
