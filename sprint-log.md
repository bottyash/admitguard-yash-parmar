# AdmitGuard — Sprint Log

## Sprint 1 — Core Backend + Strict Validation ✅
**Date:** 2026-02-27 | **Commit:** `bea2a1f` | **Tag:** Sprint 1-Backend

### Goal
Set up the Flask backend with all strict rule validations and candidate CRUD API.

### What Was Built
- **Flask application** (`app.py`) with CORS support and blueprint architecture
- **Rules config as Python flags** (`rules_config.py`) — all strict rules defined as constants, not JSON
- **Strict validators** (`validators/strict_validators.py`) — 7 field validators:
  - Full Name (required, min 2 chars, no numbers)
  - Email (valid format, unique)
  - Phone (10-digit Indian number, starts with 6/7/8/9)
  - Highest Qualification (must be from allowed list)
  - Interview Status (Cleared/Waitlisted/Rejected, blocks on Rejected)
  - Aadhaar Number (exactly 12 digits, no alphabets)
  - Offer Letter (Yes/No, Yes only if interview Cleared/Waitlisted)
- **Candidate model** (`models/candidate.py`) — in-memory storage with UUID, timestamps
- **API routes** (`routes/candidates.py`):
  - `POST /api/validate` — validate all fields
  - `POST /api/validate/<field>` — validate single field (real-time)
  - `POST /api/candidates` — submit candidate (validates first, blocks on errors)
  - `GET /api/candidates` — list all candidates
  - `GET /api/candidates/<id>` — get by ID
  - `GET /api/health` — health check

### Files
```
src/backend/
├── app.py
├── rules_config.py
├── requirements.txt
├── models/
│   ├── __init__.py
│   └── candidate.py
├── validators/
│   ├── __init__.py
│   └── strict_validators.py
└── routes/
    ├── __init__.py
    └── candidates.py
```

### Testing Results
| Test | Result |
|------|--------|
| Health check endpoint | ✅ Pass |
| Validate with all invalid data (7 fields) | ✅ All errors returned |
| Submit valid candidate | ✅ `success: true` with ID + timestamp |
| List candidates | ✅ Returns 1 candidate |
| Duplicate email rejection | ✅ 422 Unprocessable Entity |

---

## Sprint 2 — Soft Rules + Exception System ✅
**Date:** 2026-02-27 | **Commit:** `fdca112` | **Tag:** Soft Rules + Exception System

### Goal
Add soft rule validations with exception override system, rationale validation, exception count flagging, and audit trail.

### What Was Built
- **Soft rule flags** added to `rules_config.py`:
  - Age limits (18–35), graduation year range (2015–2025)
  - Percentage minimum (60%), CGPA minimum (6.0)
  - Screening test score minimum (40/100)
  - Rationale requirements (≥30 chars + must contain one of: "approved by", "special case", "documentation pending", "waiver granted")
  - Exception flagging threshold (>2 exceptions → manager review)
- **Soft validators** (`validators/soft_validators.py`) — 4 soft field validators + rationale validator:
  - Date of Birth / Age check
  - Graduation Year range check
  - Percentage / CGPA threshold check (supports both modes)
  - Screening Test Score minimum check
  - Rationale validation (length + keyword check)
  - Exception counter and flagging logic
- **Updated candidate model** — now tracks:
  - `exceptions` list (field + rationale per exception)
  - `exception_count` (computed)
  - `flagged_for_review` (true if >2 exceptions)
  - Audit log with timestamps and exception details
- **Updated API routes**:
  - `POST /api/validate` — now validates strict + soft rules, handles exception overrides
  - `POST /api/candidates` — accepts `exceptions` object with per-field `{enabled, rationale}`
  - `GET /api/audit-log` — **NEW** — full audit trail of submissions
  - `GET /api/dashboard` — **NEW** — total submissions, flagged count, exception rate

### Exception Flow
```
Soft rule fails → Frontend shows exception toggle
  → Operator enables exception → Enters rationale
    → Rationale validated (≥30 chars + keyword)
      → Valid: exception applied, submission allowed
      → Invalid: rationale error shown, submission blocked
```

### Testing Results
| Test | Result |
|------|--------|
| Soft rules reject invalid age/year/percentage/score | ✅ All 4 correctly fail |
| Exception with valid rationale overrides soft rule | ✅ Submission accepted |
| Rationale too short / missing keyword → rejected | ✅ Correct error messages |
| >2 exceptions → flagged for manager review | ✅ `flagged_for_review: true` |
| Audit log records submission + exception details | ✅ Correct entries |
| Dashboard returns stats (total, flagged, rate) | ✅ Accurate numbers |

---

## Sprint 3 — Frontend + Audit Trail
**Status:** Pending

---

## Sprint 4 — Polish, Export & Presentation
**Status:** Pending
