# Prompt 16 — v2 Rules Config + Cohort Management

## R.I.C.E. Framework

### Role
You are a backend engineer implementing the configuration layer for AdmitGuard v2 — a 3-tier validation rules system with per-cohort overrides managed through the admin UI.

### Intent
Replace v1's flat rules (strict + soft) with a comprehensive 3-tier system (Hard Reject / Soft Flag / Enrichment), define all 3 Indian education pathways (A/B/C), and build a cohort model that lets admins tweak validation thresholds per intake batch via a UI — without touching code.

### Constraints
- **rules_config.py stays as Python flags** — same pattern as v1, but vastly expanded.
- **Cohort overrides are additive** — `get_effective_rules(cohort_id)` merges defaults with per-cohort overrides. Missing overrides fall back to defaults.
- **Type-safe merging** — override values stored as TEXT in SQLite, auto-cast to match the default's type (int → int, float → float).
- **TWEAKABLE_PARAMS metadata** — drives admin UI rendering (param name, label, type, min/max/step).
- **Audit logged** — cohort creation and param updates logged to audit_log.

### Changes Made
| File | Change |
|------|--------|
| `rules_config.py` | Complete rewrite — Tier 1/2/3 rules, EDUCATION_PATHS (A/B/C), SCORE_SCALES, KNOWN_BOARDS, WORK_DOMAINS, RISK_WEIGHTS |
| `models/cohort.py` | NEW — create/list/update cohorts, get/update/delete params, `get_effective_rules()`, `get_tweakable_params()` |

### Expected Outcome (Verification)
1. ✅ Server starts — rules_config imports work across all modules
2. ✅ `EDUCATION_PATHS["A"]["required"]` returns `["10th", "12th", "UG"]`
3. ✅ `get_effective_rules()` returns all default values when no cohort_id
4. ✅ After `update_cohort_params(id, {"age_minimum": "21"})`, `get_effective_rules(id)` returns `age_minimum: 21`
