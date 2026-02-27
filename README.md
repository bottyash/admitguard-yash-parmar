# AdmitGuard 🛡️
**Admission Data Validation & Compliance System**  
IIT Gandhinagar · PG Diploma in AI-ML & Agentic AI Engineering · Week 1 Project

---

## What It Does

AdmitGuard replaces error-prone Excel-based admission data entry with a form that enforces real-time eligibility rules, handles borderline cases with a structured exception system, and maintains a full audit trail.

### Key Features
- ✅ **Strict rule validation** — non-negotiable rules that block submission
- ⚠️ **Soft rule validation** — threshold rules that operators can override with a rationale
- 🚨 **Exception flagging** — candidates with >2 exceptions auto-flagged for manager review
- 📜 **Audit log** — every submission logged with timestamps and exception details
- 📊 **Dashboard** — live stats (total submissions, flagged count, exception rate)
- 📥 **Export** — download all candidates as CSV or JSON
- 🔐 **Admin panel** — protected dashboard at `/prabandhak` for editing & deleting records
- 🌙 **Dark / Light mode** — theme persists via localStorage
- 💾 **SQLite persistence** — data survives server restarts

---

## How to Run

```bash
# 1. Install dependencies
pip install flask flask-cors

# 2. Start the server (from project root)
cd src/backend
python app.py

# 3. Open in browser
http://localhost:5000

# 4. Admin panel (login: admin / admin123)
http://localhost:5000/prabandhak
```

No separate frontend server needed — Flask serves both the API and the UI.

---

## Project Structure

```
admitguard-yash-parmar/
├── src/
│   ├── backend/
│   │   ├── app.py                  # Flask entry point, serves frontend
│   │   ├── db.py                   # SQLite connection & schema
│   │   ├── rules_config.py         # All rules as Python flags (editable)
│   │   ├── requirements.txt
│   │   ├── models/
│   │   │   └── candidate.py        # SQLite CRUD + audit log
│   │   ├── validators/
│   │   │   ├── strict_validators.py
│   │   │   └── soft_validators.py  # Exception + rationale logic
│   │   └── routes/
│   │       ├── candidates.py       # All API endpoints
│   │       └── admin.py            # Admin panel API + auth
│   └── frontend/
│       ├── index.html              # Single-page app (3 tabs)
│       ├── styles.css              # Dark/light design system
│       ├── app.js                  # API-driven validation (zero client-side)
│       ├── admin.html              # Admin panel UI
│       ├── admin.css               # Admin-specific styles
│       └── admin.js                # Admin panel logic
├── prompts/                        # R.I.C.E. prompts used (vibe coding log)
├── sprint-log.md                   # Sprint-by-sprint build log
└── .gitignore
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Frontend UI |
| `POST` | `/api/validate` | Validate all fields (strict + soft) |
| `POST` | `/api/validate/<field>` | Validate a single field (real-time) |
| `POST` | `/api/candidates` | Submit candidate |
| `GET`  | `/api/candidates` | List all candidates |
| `GET`  | `/api/audit-log` | Audit trail |
| `GET`  | `/api/dashboard` | Stats (total, flagged, exception rate) |
| `GET`  | `/api/export/csv` | Download all candidates as CSV |
| `GET`  | `/api/export/json` | Download all candidates as JSON |
| `GET`  | `/api/health` | Health check |
| `GET`  | `/prabandhak` | Admin panel UI |
| `POST` | `/api/admin/login` | Admin login |
| `POST` | `/api/admin/logout` | Admin logout |
| `GET`  | `/api/admin/candidates` | List candidates (admin, protected) |
| `PUT`  | `/api/admin/candidates/<id>` | Edit candidate (admin, protected) |
| `DELETE` | `/api/admin/candidates/<id>` | Delete candidate (admin, protected) |

---

## Validation Rules

### Strict Rules (no override)
| Field | Rule |
|-------|------|
| Full Name | Required, min 2 chars, no numbers |
| Email | Valid format, must be unique |
| Phone | 10-digit Indian number, starts with 6/7/8/9 |
| Highest Qualification | B.Tech / B.E. / B.Sc / BCA / M.Tech / M.Sc / MCA / MBA |
| Interview Status | Cleared / Waitlisted — Rejected blocks submission entirely |
| Aadhaar Number | Exactly 12 digits |
| Offer Letter Sent | "Yes" only if Interview is Cleared or Waitlisted |

### Soft Rules (exception possible with rationale)
| Field | Rule |
|-------|------|
| Date of Birth | Age 18–35 |
| Graduation Year | 2015–2025 |
| Percentage / CGPA | ≥ 60% or ≥ 6.0 CGPA |
| Screening Test Score | ≥ 40 / 100 |

**Exception rationale requirements:** ≥30 characters + must contain one of:  
`"approved by"` · `"special case"` · `"documentation pending"` · `"waiver granted"`

**Flagging:** >2 exceptions → `flagged_for_review: true` → warning shown

---

## Updating Rules

Edit `src/backend/rules_config.py` — no code changes needed elsewhere:

```python
RULE_AGE_MAX = 40              # Raise age limit
RULE_PERCENTAGE_MIN = 55.0     # Lower grade threshold
RULE_MAX_EXCEPTIONS_BEFORE_FLAG = 3   # Allow more exceptions before flagging
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, flask-cors |
| Database | SQLite (built-in) |
| Frontend | Vanilla HTML/CSS/JS |
| Fonts | Google Fonts (Inter) |

---

## Sprints

| Sprint | Focus | Status |
|--------|-------|--------|
| 1 | Core backend + strict validation | ✅ |
| 2 | Soft rules + exception system | ✅ |
| 3 | Frontend + audit log UI | ✅ |
| 3+ | SQLite database | ✅ |
| 4 | Export + polish + README | ✅ |
| 5 | Admin panel (KartaDharta) | ✅ |

---

*Built at IIT Gandhinagar, while sipping TEA*
