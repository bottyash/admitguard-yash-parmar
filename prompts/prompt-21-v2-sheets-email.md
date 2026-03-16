# Prompt 21 — v2 Google Sheets Sync + Email Service (FR-5)

## R.I.C.E. Framework

### Role
You are a backend engineer integrating Google Sheets auto-sync and an automated email system into AdmitGuard v2.

### Intent
Every candidate submission auto-syncs to a Google Sheet (17 columns). Admins can send emails to candidates via SMTP from the admin panel with LLM-drafted suggestions, track IMAP replies, and view email threads per candidate — all with graceful degradation if services are unconfigured.

### Constraints
- **Google Sheets**: Requires GCP service account credentials.json + GOOGLE_SHEETS_SPREADSHEET_ID in .env. Falls back silently if not configured.
- **Email**: Requires EMAIL_ADDRESS + EMAIL_PASSWORD (Gmail app password) in .env. Falls back silently.
- **Fire-and-forget sync**: Sheets sync in submission pipeline is wrapped in try/except — never blocks submission.
- **Email logging**: All sent/received emails logged to email_log table with candidate FK.
- **IMAP reply scan**: Checks last 50 inbox emails for "Re:" subjects, auto-matches to candidates by email.
- **Admin cohort routes**: Full CRUD + per-cohort param UPSERT + effective_rules merge + tweakable params metadata.

### Changes Made
| File | Change |
|------|--------|
| `services/google_sheets.py` | NEW — sync_candidate, sync_all_candidates, auto-headers |
| `services/email_service.py` | NEW — SMTP send, IMAP reply check |
| `services/__init__.py` | NEW — package init |
| `models/email_log.py` | NEW — log/query/unread count/mark-read/auto-match |
| `routes/admin.py` | Rewritten — cohort CRUD+params, email send/draft/replies/thread/mark-read, Sheets sync, service status |
| `routes/candidates.py` | Updated — Sheets sync after save |

### Expected Outcome (Verification)
1. ✅ Server boots clean with all new imports
2. ✅ Health: v2.0.0 with llm_available indicator
3. ✅ Email/Sheets gracefully disabled (no .env credentials configured)
4. ✅ Admin routes registered: cohorts, email, sheets, services
