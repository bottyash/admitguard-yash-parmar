# AdmitGuard 🛡️ — Pitch Deck Content

> **Admission Data Validation & Compliance System**
> IIT Gandhinagar · PG Diploma in AI-ML & Agentic AI Engineering · Week 1 Project
> **Built by: Yash Parmar**

---

## Slide 1 — Title Slide

- **Title:** AdmitGuard 🛡️
- **Subtitle:** Admission Data Validation & Compliance System
- **Tagline:** *"Replacing error-prone Excel sheets with a real-time, rule-driven admission pipeline."*
- **Institute:** IIT Gandhinagar — PG Diploma in AI-ML & Agentic AI Engineering
- **Developer:** Yash Parmar
- **Date:** February 2026

---

## Slide 2 — The Problem

### What's broken today?
- Admission offices at universities/institutes manually enter candidate data into **Excel spreadsheets**
- **No real-time validation** — errors discovered only during audits (late-stage)
- **No exception tracking** — when a borderline candidate is admitted, there's no paper trail of *who approved it* and *why*
- **No flagging system** — too many exceptions go unnoticed by managers
- **Data loss risk** — volatile in-memory storage or unsaved spreadsheets

### Pain Points
| Issue | Impact |
|-------|--------|
| Manual data entry without checks | Invalid phone numbers, wrong email formats, duplicate records |
| No structured admission rules | Each operator applies rules differently |
| No audit trail | Compliance gaps during accreditation reviews |
| No manager escalation | Borderline candidates slip through without oversight |

---

## Slide 3 — The Solution

### AdmitGuard
A **full-stack web application** that enforces admission eligibility rules in real-time, handles exceptions with structured rationale, maintains a complete audit trail, and gives managers an admin panel for oversight.

### Core Pillars
1. 🔒 **Strict Rules** — Non-negotiable rules that block submission
2. ⚠️ **Soft Rules** — Threshold rules with override capability (requires documented rationale)
3. 📜 **Audit Trail** — Every submission, edit, and deletion is logged
4. 🔐 **Admin Panel** — Protected dashboard for managers to view, edit, and delete records

---

## Slide 4 — Architecture Overview

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, flask-cors |
| Database | SQLite (built-in, zero-config) |
| Frontend | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| Fonts | Google Fonts (Inter) |
| Auth | Flask Sessions (server-side signed cookies) |

### Architecture Pattern
```
Browser (SPA)  ←→  Flask API Server  ←→  SQLite Database
                         ↕
               Validators (Strict + Soft)
```

- **Zero client-side validation** — every keystroke/blur calls the backend API
- **Blueprint-based routing** — `candidates_bp` for public, `admin_bp` for admin
- **WAL mode SQLite** — handles concurrent reads/writes efficiently

---

## Slide 5 — Strict Validation Rules (7 Rules)

These rules **cannot be overridden**. If violated, the form blocks submission.

| # | Field | Rule | Why |
|---|-------|------|-----|
| 1 | **Full Name** | Required, ≥2 characters, no numbers | Prevents garbage entries |
| 2 | **Email** | Valid format (RFC), must be unique across all candidates | Prevents duplicates |
| 3 | **Phone** | Exactly 10 digits, must start with 6/7/8/9 | Indian mobile format validation |
| 4 | **Highest Qualification** | Must be from allowed list: B.Tech, B.E., B.Sc, BCA, M.Tech, M.Sc, MCA, MBA | Ensures program eligibility |
| 5 | **Interview Status** | Cleared / Waitlisted / Rejected — "Rejected" **blocks submission entirely** | Only qualified candidates proceed |
| 6 | **Aadhaar Number** | Exactly 12 digits, no alphabets | Indian identity verification |
| 7 | **Offer Letter Sent** | "Yes" only allowed if interview is Cleared or Waitlisted | Logical consistency check |

### How it works in the UI
- Each strict field shows a **red "STRICT" badge**
- Validation fires on **blur** (when the user leaves the field)
- Errors show inline in **red text** below the field
- The field border turns **red** on failure, **green** on success

---

## Slide 6 — Soft Validation Rules (4 Rules + Exception System)

These rules have **thresholds** that can be overridden with a documented exception.

| # | Field | Rule | Threshold |
|---|-------|------|-----------|
| 1 | **Date of Birth** | Age must be 18–35 years | Catches underage or overage candidates |
| 2 | **Graduation Year** | Must be between 2015–2025 | Ensures recent graduates |
| 3 | **Percentage / CGPA** | ≥60% or ≥6.0 CGPA (supports both modes) | Minimum academic standard |
| 4 | **Screening Test Score** | ≥40 out of 100 | Minimum screening threshold |

### Exception Override Flow
```
Soft rule fails
  ↓
⚠️ Warning shown (yellow border + message)
  ↓
Exception panel appears with toggle switch
  ↓
Operator enables exception → Rationale textarea appears
  ↓
Rationale validated:
  • Minimum 30 characters
  • Must contain at least one keyword:
    "approved by" | "special case" | "documentation pending" | "waiver granted"
  ↓
✅ Valid rationale → Exception applied, submission allowed
❌ Invalid rationale → Error shown, submission blocked
```

---

## Slide 7 — Exception Flagging System

### Automatic Manager Escalation
- If a candidate has **more than 2 exceptions** → automatically **flagged for manager review**
- A pulsing red badge appears: *"🚨 3 exceptions — Will be flagged for manager review"*
- The candidate record is stored with `flagged_for_review: true`
- The audit log entry includes all exception details and rationales

### Exception Counter Badge (Live UI)
| State | Badge Color | Message |
|-------|-------------|---------|
| 0 exceptions | 🟢 Green | "✓ No exceptions" |
| 1–2 exceptions | 🟡 Yellow | "⚠️ 1 exception (requires manager notation)" |
| 3+ exceptions | 🔴 Red (pulsing) | "🚨 3 exceptions — Will be flagged for manager review" |

---

## Slide 8 — Frontend UI — Candidate Entry Form

### Three-Tab Single-Page Application
1. **📋 Candidate Entry** — The main form with 11 validated fields
2. **📜 Audit Log** — Live activity feed of all submissions
3. **📊 Dashboard** — High-level stats + rules reference table

### Design System
- **Dark mode by default** with light/dark toggle (persisted via localStorage)
- **Glassmorphism** design — frosted glass cards with backdrop blur
- **Animated gradient background** — subtle purple radial gradients
- **Inter font** from Google Fonts for modern typography
- **Form sections** organized as: Personal Info → Academic Details → Admission Process → Identity Verification
- **Real-time validation** — every field blur triggers a backend API call (zero client-side validation)
- **Score type toggle** — seamless switch between Percentage and CGPA modes
- **Keyboard shortcut** — `Ctrl+Enter` to submit from anywhere

---

## Slide 9 — Frontend UI — Audit Log

### Full Submission History
- **Live-loading** table with all past submissions
- **Filterable** by: All | ⚠️ Exceptions | 🚨 Flagged
- **Searchable** — live search by name or email
- **Entry count badge** — dynamically updates (e.g., "12 entries")
- **Status badges** per entry:
  - Action: 📋 SUBMISSION / ✏️ ADMIN_EDIT / 🗑️ ADMIN_DELETE
  - Exceptions: ⚠️ count or "None"
  - Review Flag: 🚨 Flagged or ✓ Clean
- **Exception details** — rationale text shown inline for each exception
- **Timestamps** — formatted in Indian locale (e.g., "27 Feb 2026, 07:30 PM")

### Data Export
- **⬇ CSV** — download all candidates as a formatted CSV file
- **⬇ JSON** — download all candidates as a JSON file
- One-click export buttons in both Audit Log and Dashboard tabs

---

## Slide 10 — Frontend UI — Dashboard

### Live Statistics
| Metric | Description |
|--------|-------------|
| 👥 **Total Submissions** | Count of all candidates in the database |
| 🚨 **Flagged for Review** | Count of candidates with >2 exceptions |
| ⚠️ **Exception Rate** | Percentage of candidates with at least one exception |
| 📥 **Download Export** | One-click CSV download card |

### Embedded Rules Reference
- A styled table showing all 12 rules (strict + soft + system)
- For each rule: Field name, validation rule, type badge (Strict/Soft/System), exception availability
- Serves as an **in-app training reference** for data entry operators

---

## Slide 11 — Admin Panel (KartaDharta) 🔐

### Access
- **URL:** `localhost:5000/prabandhak`
- **Default credentials:** Username `admin` / Password `admin123`
- **Authentication:** Flask server-side sessions with signed cookies

### Features
| Feature | Description |
|---------|-------------|
| 🔐 **Login Screen** | Glassmorphism card with error handling, matches the main design system |
| 📊 **Stats Cards** | Total candidates, flagged count, exception rate — updated on every load |
| 📋 **Candidates Table** | All records in a searchable, sortable table |
| 🔍 **Search** | Live filter by name or email |
| ✏️ **Edit** | Click any row → modal with all fields pre-filled → save triggers PUT to backend |
| 🗑️ **Delete** | Delete button per row → confirmation modal → removes record and logs to audit trail |
| 🚪 **Logout** | Clears session, returns to login |
| 🛡️ **Route Protection** | All admin API endpoints return 401 if not logged in |

### Audit Integration
- Every admin **edit** creates an `ADMIN_EDIT` entry in the audit log
- Every admin **delete** creates an `ADMIN_DELETE` entry in the audit log
- Full traceability: who changed what and when

---

## Slide 12 — API Endpoints (Complete Reference)

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Frontend UI (single-page app) |
| `POST` | `/api/validate` | Validate all fields (strict + soft) |
| `POST` | `/api/validate/<field>` | Validate a single field (real-time) |
| `POST` | `/api/candidates` | Submit a new candidate |
| `GET` | `/api/candidates` | List all candidates |
| `GET` | `/api/candidates/<id>` | Get a single candidate by ID |
| `GET` | `/api/audit-log` | Full audit trail |
| `GET` | `/api/dashboard` | Stats: total, flagged, rate |
| `GET` | `/api/export/csv` | Download CSV |
| `GET` | `/api/export/json` | Download JSON |
| `GET` | `/api/health` | Health check |

### Admin Endpoints (Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/prabandhak` | Admin panel UI |
| `POST` | `/api/admin/login` | Login with credentials |
| `POST` | `/api/admin/logout` | Logout / clear session |
| `GET` | `/api/admin/status` | Check login state |
| `GET` | `/api/admin/candidates` | List all + stats |
| `PUT` | `/api/admin/candidates/<id>` | Edit candidate fields |
| `DELETE` | `/api/admin/candidates/<id>` | Delete candidate |

**Total: 18 endpoints**

---

## Slide 13 — Database Design

### SQLite Schema (2 Tables)

**`candidates` table**
| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | UUID v4 |
| full_name | TEXT NOT NULL | |
| email | TEXT NOT NULL UNIQUE | |
| phone | TEXT NOT NULL | |
| date_of_birth | TEXT | |
| highest_qualification | TEXT NOT NULL | |
| graduation_year | TEXT | |
| percentage_cgpa | TEXT | |
| score_type | TEXT | "percentage" or "cgpa" |
| screening_test_score | TEXT | |
| interview_status | TEXT NOT NULL | |
| aadhaar | TEXT NOT NULL | |
| offer_letter_sent | TEXT NOT NULL | |
| exceptions | TEXT (JSON) | Serialized list of {field, rationale} |
| exception_count | INTEGER | Computed on submission |
| flagged_for_review | INTEGER | 0 or 1 |
| submitted_at | TEXT | ISO 8601 timestamp |

**`audit_log` table**
| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | UUID v4 |
| candidate_id | TEXT | FK to candidates |
| candidate_name | TEXT | |
| candidate_email | TEXT | |
| action | TEXT | SUBMISSION / ADMIN_EDIT / ADMIN_DELETE |
| exception_count | INTEGER | |
| flagged_for_review | INTEGER | |
| exceptions | TEXT (JSON) | |
| timestamp | TEXT | ISO 8601 |

---

## Slide 14 — Project Structure

```
admitguard-yash-parmar/
├── src/
│   ├── backend/
│   │   ├── app.py                  ← Flask entry point
│   │   ├── db.py                   ← SQLite connection & schema
│   │   ├── rules_config.py         ← All rules as Python flags
│   │   ├── models/
│   │   │   └── candidate.py        ← CRUD + audit log
│   │   ├── validators/
│   │   │   ├── strict_validators.py
│   │   │   └── soft_validators.py
│   │   └── routes/
│   │       ├── candidates.py       ← Public API endpoints
│   │       └── admin.py            ← Admin API + auth
│   └── frontend/
│       ├── index.html              ← Main SPA (3 tabs)
│       ├── styles.css              ← Design system
│       ├── app.js                  ← Frontend logic
│       ├── admin.html              ← Admin panel
│       ├── admin.css               ← Admin styles
│       └── admin.js                ← Admin logic
├── prompts/                        ← 13 R.I.C.E. prompt files
├── sprint-log.md                   ← Sprint-by-sprint build log
└── README.md                       ← Full documentation
```

---

## Slide 15 — Sprint Timeline

| Sprint | Focus | Key Deliverables |
|--------|-------|------------------|
| **Sprint 1** | Core Backend | Flask app, 7 strict validators, candidate CRUD, blueprint routing |
| **Sprint 2** | Soft Rules | 4 soft validators, exception system, rationale validation, flagging, audit log, dashboard API |
| **Sprint 3** | Frontend UI | 3-tab SPA, glassmorphism design, real-time blur validation, dark/light mode |
| **Sprint 3+** | Database | SQLite persistence, WAL mode, zero API contract changes |
| **Sprint 4** | Polish | CSV/JSON export, live search, keyboard shortcuts, README |
| **Sprint 5** | Admin Panel | Login/auth, candidates table, edit/delete, admin audit trail |

**All 6 sprints completed in a single day.**

---

## Slide 16 — Development Methodology

### Vibe Coding with R.I.C.E. Prompts
Every feature was built using the **R.I.C.E. Framework**:
- **R** — Role: Define the AI assistant's persona
- **I** — Intent: What to build and why
- **C** — Constraints: Technical boundaries and requirements
- **E** — Expected Outcome: Verification criteria

### Prompt Log
13 documented R.I.C.E. prompts in `prompts/` directory:
| # | Prompt | Feature |
|---|--------|---------|
| 01 | Foundation | Flask app setup |
| 02 | Strict Validators | 7 validation rules |
| 03 | Candidate Model | In-memory CRUD |
| 04 | API Routes | RESTful endpoints |
| 05 | Soft Rules | Exception system |
| 06 | Rules Config | Python flag constants |
| 07 | Audit & Dashboard | Logging + stats |
| 08 | Frontend UI | 3-tab SPA |
| 09 | SQLite Database | Persistent storage |
| 10 | Export | CSV + JSON download |
| 11 | Polish | Search, shortcuts, scrollbar |
| 12 | Presentation | README + sprint log |
| 13 | Admin Panel | KartaDharta dashboard |

---

## Slide 17 — Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Zero client-side validation** | Single source of truth — all logic lives in the backend |
| **Rules as Python flags** (`rules_config.py`) | Non-developers can adjust thresholds without touching code |
| **SQLite over MongoDB/PostgreSQL** | Zero-config, built into Python, perfect for single-server deployment |
| **Flask sessions for admin auth** | No extra JWT libraries, inherently server-side, works with cookies |
| **Vanilla JS over React/Vue** | Minimal bundle size, no build step, instant deploy |
| **Blueprint architecture** | Clean separation of public vs admin routes |
| **WAL mode SQLite** | Concurrent read/write support without locking |
| **Hardcoded admin credentials** | Development simplicity — easily swappable to env vars for production |

---

## Slide 18 — How to Run

```bash
# 1. Clone the repository
git clone https://github.com/bottyash/admitguard-yash-parmar.git

# 2. Install dependencies (only 2 packages)
pip install flask flask-cors

# 3. Start the server
cd src/backend
python app.py

# 4. Open the application
http://localhost:5000           ← Main application
http://localhost:5000/prabandhak  ← Admin panel (admin / admin123)
```

**No build step. No npm install. No Docker. Just Python.**

---

## Slide 19 — Demo Flow (Suggested)

### Live Demo Script
1. **Open** `localhost:5000` → Show the candidate entry form
2. **Enter invalid data** → Show real-time strict validation (red errors)
3. **Fix errors, trigger soft rule** → Show exception panel with toggle + rationale
4. **Submit candidate** → Show success modal with summary
5. **Switch to Audit Log** → Show the submission with exception details
6. **Switch to Dashboard** → Show live stats
7. **Export CSV** → Download the file
8. **Open** `localhost:5000/prabandhak` → Show admin login
9. **Login** → Show candidates table
10. **Edit a candidate** → Show edit modal, save changes
11. **Delete a candidate** → Show confirmation, delete
12. **Check Audit Log** → Show ADMIN_EDIT and ADMIN_DELETE entries
13. **Toggle Dark/Light mode** → Show theme switch

---

## Slide 20 — Summary & Impact

### What AdmitGuard Delivers
- ✅ **11-field validated admission form** with 11 rules (7 strict + 4 soft)
- ✅ **Structured exception system** with rationale validation and manager flagging
- ✅ **Complete audit trail** — every action timestamped and logged
- ✅ **Data export** — CSV and JSON with one click
- ✅ **Admin panel** — secure CRUD with session authentication
- ✅ **Responsive design** — works on desktop, tablet, and mobile
- ✅ **18 API endpoints** — fully RESTful, documented
- ✅ **SQLite persistence** — data survives server restarts
- ✅ **Zero dependencies beyond Flask** — lightweight, deployable anywhere

### Built With
- **6 sprints** completed in a single day
- **13 R.I.C.E. prompts** documenting the entire vibe coding process
- **~3,000 lines of code** across Python + HTML + CSS + JS

---

*Built at IIT Gandhinagar, while sipping TEA ☕*
