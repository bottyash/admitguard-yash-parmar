# Prompt 23 — v2 Admin Panel Upgrade (Phase 10)

## R.I.C.E. Framework

### Role
You are a frontend engineer rebuilding the AdmitGuard v2 admin panel with cohort management, email system, NL search, and service monitoring.

### Intent
Replace v1 admin panel with a professional sidebar layout featuring 5 views: Dashboard (stats + recent table), Candidates (NL search + detail panel with email thread), Cohorts (create + params editor), Email (compose with LLM draft + reply tracking), Services (status + Sheets sync). Login with session persistence.

### Constraints
- **Dark theme** matching main app aesthetic.
- **NL search** via LLM `query_to_filter()` with text fallback if LLM unavailable.
- **Email compose modal** with AI draft generation via `/api/admin/email/draft`.
- **Reply badge** in sidebar showing unread count.
- **Cohort params editor** renders `TWEAKABLE_PARAMS` metadata (type, min, max, default).
- **Services panel** shows live status of Email, Sheets, and LLM.

### Changes Made
| File | Change |
|------|--------|
| `admin.css` | Rewritten — sidebar layout, stats cards, table, modals, params editor, email thread, tabs, login, services |
| `admin.html` | Rewritten — 5-view layout (Dashboard/Candidates/Cohorts/Email/Services) + 2 modals (email compose, create cohort) |
| `admin.js` | Rewritten — login/nav, dashboard stats, NL search, candidate detail, cohort CRUD+params, email compose+draft+replies, services status |

### Expected Outcome (Verification)
1. ✅ Login screen → Dashboard with stats cards + recent table
2. ✅ Sidebar navigation between all 5 views
3. ✅ Cohort Management shows "+ New Cohort" button
4. ✅ Dark theme consistent with main application
