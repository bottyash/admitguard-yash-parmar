# Prompt 17 — v2 Education Pathway Module (FR-1)

## R.I.C.E. Framework

### Role
You are a backend engineer implementing the Indian education pathway validation module for AdmitGuard v2.

### Intent
Create validators that enforce 3 distinct Indian education pathways:
- **Path A (Standard):** 10th → 12th → UG → PG/Work
- **Path B (Diploma):** 10th → Diploma → UG (Lateral Entry) → PG/Work
- **Path C (Lateral):** 10th → ITI/Vocational → Diploma → UG → PG/Work

Each pathway has its own mandatory levels, and the validator must check per-entry validity, pathway adherence, chronological consistency, and score normalization.

### Constraints
- **10th is always mandatory** regardless of path.
- **Year of passing must be chronological** — a student can't complete 12th before 10th.
- **Score normalization** — CGPA/10 × 9.5 = percentage; CGPA/4 × 25 = percentage.
- **Levels outside the selected path** trigger warnings, not errors.
- **Backlogs only apply** to UG/PG/PhD levels.
- **Gap calculation** computes months of gap between consecutive levels, beyond expected 2-year duration.

### Changes Made
| File | Change |
|------|--------|
| `validators/education_validators.py` | NEW — `validate_education_entry()`, `validate_education_path()`, `validate_chronological_order()`, `normalize_score()`, `calculate_education_gaps()`, `validate_all_education()` |

### Expected Outcome (Verification)
1. ✅ Path A (10th + 12th + UG) validates successfully — scores normalized to 85%, 80.75%, 80%
2. ✅ Path B without Diploma rejects with clear error message
3. ✅ Chronological error (12th year < 10th year) detected and reported
4. ✅ CGPA 8.5/10 → 80.75%, CGPA 3.2/4 → 80.0%, percentage passthrough
