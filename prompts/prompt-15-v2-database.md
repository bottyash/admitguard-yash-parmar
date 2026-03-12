# Prompt 15 — v2 Database Schema (7 Tables)

## R.I.C.E. Framework

### Role
You are a database engineer designing the persistent storage layer for AdmitGuard v2 — upgrading from a 2-table schema to a 7-table schema supporting education pathways, work experience, cohort management, email tracking, and intelligence outputs.

### Intent
Replace the v1 schema (candidates + audit_log) with a normalized 7-table schema that separates education and work entries into child tables, adds cohort management for multi-intake support, and stores intelligence layer outputs (risk scores, categories, LLM verification flags) alongside each candidate.

### Constraints
- **SQLite** — No external database server. Zero-config, built into Python.
- **WAL mode + foreign keys** — Enabled for concurrent reads and referential integrity.
- **ON DELETE CASCADE** — Child rows (education_entries, work_entries, email_log) auto-deleted when parent candidate is deleted.
- **JSON fields** — `flags`, `llm_verification_flags`, `skills`, `details` stored as serialized JSON TEXT.
- **Backward compatible routes** — Model function names kept compatible with existing route imports. Routes updated to use new signatures.

### Tables
| Table | Rows Per Candidate | Purpose |
|-------|--------------------|---------|
| `candidates` | 1 | Core info + intelligence fields + flags + cohort FK |
| `education_entries` | 1-7 (one per level) | 10th, 12th, Diploma, ITI, UG, PG, PhD |
| `work_entries` | 0-N | One per job |
| `cohorts` | N/A (standalone) | Intake cohorts |
| `cohort_params` | N per cohort | Per-cohort rule overrides |
| `email_log` | 0-N | Sent/received emails |
| `audit_log` | 1-N | All actions with JSON details |

### Changes Made
| File | Change |
|------|--------|
| `db.py` | Complete rewrite — 7-table schema |
| `models/candidate.py` | Complete rewrite — add_candidate accepts education/work/intelligence, get_candidate_by_id returns nested entries, cascade deletes, dashboard stats with category distribution |
| `routes/candidates.py` | Updated imports + submission flow (education_entries, work_entries in payload), dashboard uses new stats, CSV export includes intelligence fields |
| `routes/admin.py` | Env-based credentials, uses get_dashboard_stats instead of 3 separate count functions |

### Expected Outcome (Verification)
1. ✅ Server starts without errors — `python app.py`
2. ✅ `GET /api/health` returns v2.0.0
3. ✅ `GET /api/dashboard` returns `avg_risk_score`, `category_distribution`, `total_submissions`
4. ✅ All 7 tables created in admitguard.db: candidates, education_entries, work_entries, cohorts, cohort_params, email_log, audit_log
