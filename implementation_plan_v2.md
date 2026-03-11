# AdmitGuard v2 — Implementation Plan

Enterprise-grade admission platform: Indian education pathways, work experience, 3-tier validation, intelligence layer (risk scoring + 8 LLM features via Ollama), Google Sheets sync, cohort management, automated email.

## Prerequisites

> [!IMPORTANT]
> - **Ollama** installed + `ollama pull qwen3:4b`
> - **Google Sheets**: GCP service account + credentials.json + Sheet shared with service account
> - **Email (SMTP/IMAP)**: Gmail app password for sending + reply tracking

> [!WARNING]
> Near-complete rewrite. v1 data is not migrated. Each phase = one commit you can push.

---

## Phased Execution Plan

Each phase is self-contained. After each phase I'll pause so you can review, test, and `git commit + push`.

---

### Phase 1: Foundation & Config
**Commit:** `feat(admitguard-v2): foundation — env config and dependencies`

| Item | Detail |
|------|--------|
| `.env.example` | SECRET_KEY, ADMIN creds, Google Sheets, Ollama, SMTP/IMAP |
| [.gitignore](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/.gitignore) | Add .env, credentials.json, *.db |
| [requirements.txt](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/requirements.txt) | Add python-dotenv, gspread, google-auth, ollama |
| **Prompt log** | `prompts/prompt-14-v2-foundation.md` |

---

### Phase 2: Database Layer (7 tables)
**Commit:** `feat(admitguard-v2): database schema — 7 tables`

| Table | Purpose |
|-------|---------|
| [candidates](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/routes/candidates.py#287-298) | Core info + education_path + cohort_id + intelligence fields + flags |
| `education_entries` | FK→candidates. Level, board, stream, year, score, normalized_score, backlogs, gap |
| `work_entries` | FK→candidates. Company, designation, domain, dates, type, skills |
| `cohorts` | id, name, description, is_active |
| `cohort_params` | FK→cohorts. param_name, param_value |
| `email_log` | FK→candidates. subject, body, direction (SENT/RECEIVED), status, message_id |
| [audit_log](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/routes/candidates.py#313-324) | Enriched from v1 |

**Prompt log:** `prompts/prompt-15-v2-database.md`

---

### Phase 3: Rules Config + Cohort Model
**Commit:** `feat(admitguard-v2): rules config and cohort management`

- Rewrite [rules_config.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/rules_config.py) with 3-tier structure + education paths + risk weights
- New `models/cohort.py` — create/list cohorts, get/update params, `get_effective_rules(cohort_id)` merges defaults with overrides

**Prompt log:** `prompts/prompt-16-v2-rules-cohorts.md`

---

### Phase 4: Education Pathway Module (FR-1)
**Commit:** `feat(admitguard-v2): education pathways — Indian system`

- New `validators/education_validators.py` — Path A/B/C enforcement, score normalization, per-entry validation
- Update [models/candidate.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/models/candidate.py) — education entries CRUD
- Dynamic frontend education form (path selector → show/hide fields)

**Prompt log:** `prompts/prompt-17-v2-education.md`

---

### Phase 5: Work Experience Module (FR-2)
**Commit:** `feat(admitguard-v2): work experience module`

- New `validators/work_validators.py` — per-entry validation, date logic, derived fields (total exp, domain-relevant, gaps, status)
- Update [models/candidate.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/models/candidate.py) — work entries CRUD
- Frontend work experience form (add/remove entries, tag input for skills)

**Prompt log:** `prompts/prompt-18-v2-work-experience.md`

---

### Phase 6: Validation Engine (FR-3)
**Commit:** `feat(admitguard-v2): 3-tier validation engine`

- Rewrite [validators/strict_validators.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/validators/strict_validators.py) → Tier 1 (HARD REJECT)
- Rewrite [validators/soft_validators.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/validators/soft_validators.py) → Tier 2 (SOFT FLAG)
- Tier 3 (ENRICHMENT) computed in [routes/candidates.py](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/src/backend/routes/candidates.py)
- Update `POST /api/validate` and `POST /api/candidates` for new payload shapes
- All validators accept cohort_params for cohort-specific thresholds

**Prompt log:** `prompts/prompt-19-v2-validation-engine.md`

---

### Phase 7: Intelligence Layer + LLM (FR-4)
**Commit:** `feat(admitguard-v2): intelligence layer and LLM features`

| Feature | File |
|---------|------|
| Risk Scoring (0-100) | `intelligence/risk_scorer.py` |
| Auto-Categorization | `intelligence/categorizer.py` |
| Data Quality Score | `intelligence/data_quality.py` |
| LLM: Autocomplete, field help, soft doc verification, anomaly narration, in-form chat, email drafts, admin NL query, profile summary | `intelligence/llm_assistant.py` |

New routes: `/api/llm/suggest`, `/api/llm/explain`, `/api/llm/verify`, `/api/llm/chat`, `/api/llm/profile-summary`, `/api/llm/draft-email`, `/api/llm/query`

**Prompt log:** `prompts/prompt-20-v2-intelligence.md`

---

### Phase 8: Google Sheets + Email Service (FR-5)
**Commit:** `feat(admitguard-v2): google sheets sync and email service`

- `services/google_sheets.py` — auto-sync candidate to sheet, setup headers, graceful fallback
- `services/email_service.py` — SMTP send, IMAP reply poll, email thread history
- `models/email_log.py` — log/query emails
- Admin routes: send email, check replies, view thread

**Prompt log:** `prompts/prompt-21-v2-sheets-email.md`

---

### Phase 9: Frontend — Multi-Step Form
**Commit:** `feat(admitguard-v2): frontend rebuild — multi-step form`

- 5-step form: Personal → Education (dynamic path) → Work → Review → Confirmation
- LLM chat widget (floating bubble)
- Soft doc verification warnings on blur
- Risk score gauge + category badge on confirmation
- Loading spinners, mobile responsive

**Prompt log:** `prompts/prompt-22-v2-frontend.md`

---

### Phase 10: Admin Panel Upgrade
**Commit:** `feat(admitguard-v2): admin panel — cohorts, email, NL search`

- Cohort management: selector, create modal, params editor (sliders/inputs)
- Email dashboard: compose modal with LLM draft, replies tab with badge, thread viewer
- Enhanced table: risk score + category columns, expandable detail, NL search bar

**Prompt log:** `prompts/prompt-23-v2-admin-panel.md`

---

### Phase 11: Deployment & Documentation
**Commit:** `feat(admitguard-v2): deploy and documentation`

- Deploy to live URL
- README rewrite (architecture, setup, live URL, Sheet link, screenshots)
- [sprint-log.md](file:///D:/IITGn/Projects/Week1/admitguard-yash-parmar/sprint-log.md) update with v2 sprints
- Final sweep: error handling, edge cases

**Prompt log:** `prompts/prompt-24-v2-deployment.md`

---

## Verification Plan

After each phase, I'll run relevant tests before pausing. Full verification after Phase 10:

1. **3 personas**: Diploma student, working professional (5yr + gap), fresher — all must flow correctly
2. **Tier 1 rejection**: Missing fields, impossible dates, duplicate email
3. **Google Sheets**: Submit → row appears in 30s
4. **LLM features**: Chat, autocomplete, doc verification, email draft
5. **Cohort switch**: Change thresholds → different validation behavior
6. **Email flow**: Send from admin → candidate receives → reply → shows on dashboard
