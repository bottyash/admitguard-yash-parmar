# Prompt 19 — v2 3-Tier Validation Engine (FR-3)

## R.I.C.E. Framework

### Role
You are a backend engineer wiring the complete 3-tier validation engine for AdmitGuard v2.

### Intent
Build a pipeline where every submission passes through 3 tiers:
- **Tier 1 (HARD REJECT)**: Missing fields, bad formats, duplicates, age, impossible dates. If fails → 422, data NOT saved.
- **Tier 2 (SOFT FLAG)**: Education gaps, backlogs, career gaps, domain transitions, no work after education, low scores. Data IS saved but flagged for review.
- **Tier 3 (ENRICHMENT)**: Auto-computed metadata — experience bucket, completeness %, education gaps, backlogs — stored alongside the candidate.

### Constraints
- **Education path/chronological errors are Tier 1** — wrong pathway or impossible year ordering blocks submission.
- **Work entry errors are Tier 1** — missing company/date blocks submission.
- **Soft flags are Tier 2** — backlogs, gaps, low scores produce flags but allow saving.
- **All validators accept cohort_rules** for per-cohort threshold overrides.
- **POST /api/validate** runs all 3 tiers as preview without saving.
- **POST /api/candidates** runs the full pipeline and saves.
- **Legacy compatibility** maintained via stub functions.

### Changes Made
| File | Change |
|------|--------|
| `validators/strict_validators.py` | Rewritten as Tier 1 — name, email, phone, age, aadhaar, mandatory fields |
| `validators/soft_validators.py` | Rewritten as Tier 2 — consumes education/work results, returns structured flags |
| `routes/candidates.py` | Rewritten — full 3-tier pipeline, education+work validators integrated, completeness scoring |

### Expected Outcome (Verification)
1. ✅ Valid Path A submission (10th+12th+UG + 2 jobs) saves successfully — dashboard shows 1 submission
2. ✅ Backlogs (2) flagged as Tier 2 soft flag
3. ✅ Invalid data (empty name, bad email, short phone) returns Tier 1 errors, 422 status
4. ✅ Dashboard shows category_distribution: {"Pending": 1}, flagged_count: 1
