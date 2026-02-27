# Prompt 08 — Frontend UI (Sprint 3)

## R.I.C.E. Framework

### Role
You are a frontend engineer building a professional, API-driven single-page application for AdmitGuard using **vanilla HTML, CSS, and JavaScript only** (no frameworks).

### Intent
Build `src/frontend/index.html`, `styles.css`, and `app.js` — a 3-tab SPA that connects to the Flask backend at `http://localhost:5000`. The form covers all 11 candidate fields, with real-time per-field validation on `blur`, dynamic exception panels for soft rule failures, and no client-side validation logic.

### Constraints
- **Zero client-side validation** — all validation via `POST /api/validate/<field>` on blur
- **No JavaScript frameworks** (no React, Vue, etc.)
- **Dark mode default**, light mode toggle that persists via `localStorage`
- **Glassmorphism** cards and modern design system with CSS custom properties
- Soft rule fields show an "Enable Exception Override" toggle + rationale textarea when the backend returns a warning
- Form submission calls `POST /api/validate` (full check) then `POST /api/candidates`
- Audit log tab auto-loads on tab switch, shows filter buttons (All/Exceptions/Flagged)
- Dashboard tab shows 3 stat cards + rules reference table

### 3 Tabs Required

1. **Candidate Entry** — form with all 11 fields
   - Personal: Full Name (strict), Email (strict), Phone (strict), Date of Birth (soft)
   - Academic: Qualification (strict), Graduation Year (soft), Percentage/CGPA with toggle (soft), Screening Score (soft)
   - Compliance: Interview Status (strict), Aadhaar (strict), Offer Letter Sent (strict)
   - Exception counter badge showing current exception count
   - Submit + Reset buttons

2. **Audit Log** — table with: Name, Email, Action badge, Exceptions, Review Flag, Timestamp, ID

3. **Dashboard** — 3 stat cards (Total, Flagged, Exception Rate) + full rules config table

### Design Tokens (CSS Variables)
```css
--bg-primary: #0f1117;
--bg-card: rgba(255,255,255,0.04);
--accent: #6366f1;
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;
--radius-md: 10px;
```

### Field State Classes
```css
.field-input.is-valid    { border-color: var(--success); }
.field-input.is-invalid  { border-color: var(--error); }
.field-input.is-warning  { border-color: var(--warning); }
```
