# Prompt 22 — v2 Frontend Rebuild (Phase 9)

## R.I.C.E. Framework

### Role
You are a frontend engineer rebuilding the AdmitGuard v2 UI as a premium dark-themed multi-step form with AI integration.

### Intent
Replace the v1 single-page form with a 5-step wizard: Personal → Education (dynamic path selector) → Work (add/remove) → Review (with live Tier 2 flags preview) → Confirmation (risk gauge + intelligence report). Add a floating LLM chat widget and real-time field validation.

### Constraints
- **Dark glassmorphism** design with Inter font, CSS variables, animations.
- **Path A/B/C selector** radio cards drive dynamic education entry rendering.
- **Work entries** are fully dynamic (add/remove with all fields).
- **Real-time blur validation** calls `POST /api/validate/<field>`.
- **Review step** calls `POST /api/validate` for Tier 2 flag preview.
- **Submission** through `POST /api/candidates` 3-tier pipeline with loading overlay.
- **Risk gauge** uses conic-gradient with color coding (green/yellow/red).
- **Chat widget** sends context-aware queries to `POST /api/llm/chat`.
- **Mobile responsive** with breakpoints at 640px.

### Changes Made
| File | Change |
|------|--------|
| `styles.css` | Rewritten — full v2 design system (glassmorphism, step indicator, path cards, entry blocks, risk gauge, chat widget, toast, loading, responsive) |
| `index.html` | Rewritten — 5-step form structure with chat widget and loading overlay |
| `app.js` | Rewritten — step navigation, dynamic education/work rendering, validation, submission, risk gauge, chat, field explainer, toasts |

### Expected Outcome (Verification)
1. ✅ Dark themed UI with gradient header, step indicators, glass cards
2. ✅ Path A/B/C selector renders correct education entries dynamically
3. ✅ Work experience add/remove works
4. ✅ Floating chat bubble visible at bottom-right
5. ✅ Server boots and serves frontend at localhost:5000
