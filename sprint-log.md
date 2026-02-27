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

## Sprint 3 — Frontend + Audit Trail ✅
**Date:** 2026-02-27 | **Commit:** `4c8d23e` | **Tag:** Frontend + Audit Trail

### Goal
Build a modern, API-driven single-page application (SPA) with no client-side validation, fully integrated with the AdmitGuard backend.

### What Was Built
- **3-Tab Glassmorphism UI** (`index.html`, `styles.css`):
  - **Candidate Entry**: Full form (11 fields) with real-time blur validation.
  - **Audit Log**: Live-loading activity feed with status badges.
  - **Dashboard**: High-level stats + embedded rules configuration table.
- **Frontend Logic** (`app.js`):
  - Zero client-side validation — every field `blur` calls the backend.
  - Dynamic exception panels — show/hide rationale textarea based on backend warnings.
  - Unified theme engine — dark mode by default with light/dark toggle.
  - Activity-dependent loading (fetch audit/stats only when switching to their tabs).
- **Embedded Rules Reference**: The configuration flags from `rules_config.py` are visually summarized for recruiters on every page.

---

## Sprint 3+ — Persistent Storage (SQLite) ✅
**Date:** 2026-02-27 | **Commit:** `fc36e1c` | **Tag:** SQLite Database

### Goal
Replace volatile in-memory storage with a persistent SQLite database without breaking existing API contracts.

### What Was Built
- **Database Module** (`db.py`):
  - SQLite schema for `candidates` and `audit_log` tables.
  - WAL mode enabled for high-performance concurrency.
- **SQLite Candidate Model** (`models/candidate.py`):
  - Function signatures preserved exactly — routes remain unchanged.
  - Handles JSON serialization for the `exceptions` list field.
  - Boolean mapping (SQLite 0/1 to Python True/False).

---

## Sprint 4 — Polish, Export & Presentation ✅
**Date:** 2026-02-27 | **Commit:** `6496a1b` | **Tag:** Sprint 4-Final

### Goal
Add data portability (export), enhance usability (search/shortcuts), and finalize documentation.

### What Was Built
- **Export Functionality**:
  - `GET /api/export/csv` — formatted CSV download with quoted headers.
  - `GET /api/export/json` — JSON file download of the candidate database.
  - UI buttons Added to Audit Log and Dashboard tabs.
- **Enhanced Search**:
  - Live search input in Audit Log — filters by name or email instantly.
  - Entry count badge updates dynamically based on filtered results.
- **Keyboard Shortcuts**:
  - `Ctrl + Enter` triggers form submission globally.
- **Documentation**:
  - **README.md**: Comprehensive manual including runner guide, API reference, and rule lookup.
  - **R.I.C.E. Prompts**: Fully documented 12-file prompt log in `prompts/`.
  - **Audit Polish**: Custom scrollbars and refined responsive layouts.

---

## Sprint 5 — Admin Panel (KartaDharta) ✅
**Date:** 2026-02-27 | **Tag:** Admin Panel

### Goal
Add a protected admin interface at `/prabandhak` for viewing, editing, and deleting candidate records with session-based authentication.

### What Was Built
- **Admin Routes** (`routes/admin.py`):
  - `POST /api/admin/login` — authenticate with username/password (default: `admin` / `admin123`)
  - `POST /api/admin/logout` — clear session
  - `GET  /api/admin/status` — check login state
  - `GET  /api/admin/candidates` — list all candidates + stats (protected)
  - `PUT  /api/admin/candidates/<id>` — update candidate fields (protected)
  - `DELETE /api/admin/candidates/<id>` — delete candidate (protected)
  - `@admin_required` decorator for route protection (returns 401)
- **Model Extensions** (`models/candidate.py`):
  - `update_candidate()` — update editable fields with `ADMIN_EDIT` audit log entry
  - `delete_candidate()` — delete record with `ADMIN_DELETE` audit log entry
- **Admin Frontend** (`admin.html` + `admin.css` + `admin.js`):
  - Glassmorphism login screen with error handling
  - Dashboard with stats cards (total, flagged, exception rate)
  - Searchable candidates data table with Edit and Delete buttons
  - Edit modal — pre-filled form for all candidate fields
  - Delete confirmation modal with candidate details
  - Theme toggle (shared with main app)

### Files
```
src/backend/
├── app.py                      # Updated: secret key, admin blueprint, /prabandhak route
├── models/
│   └── candidate.py            # Updated: update_candidate(), delete_candidate()
└── routes/
    └── admin.py                # NEW: Admin API endpoints + auth

src/frontend/
├── admin.html                  # NEW: Admin panel page
├── admin.css                   # NEW: Admin-specific styles
└── admin.js                    # NEW: Admin frontend logic
```

### Testing Results
| Test | Result |
|------|--------|
| Login screen renders at `/prabandhak` | ✅ Pass |
| Wrong credentials show error message | ✅ Pass |
| Correct login shows dashboard + table | ✅ Pass |
| Stats cards display accurate counts | ✅ Pass |
| Edit modal updates candidate in database | ✅ Pass |
| Delete removes candidate + audit logged | ✅ Pass |
| Logout clears session, APIs return 401 | ✅ Pass |
