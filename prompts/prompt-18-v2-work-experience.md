# Prompt 18 — v2 Work Experience Module (FR-2)

## R.I.C.E. Framework

### Role
You are a backend engineer building the work experience validation module for AdmitGuard v2.

### Intent
Create validators that capture and validate work history entries — company, designation, domain, dates, skills — and auto-compute derived fields (total experience, career gaps, domain relevance, experience buckets).

### Constraints
- **Start date required**, end date optional (empty = currently working).
- **Domain must match** `WORK_DOMAINS` from rules_config (IT, Non-IT, Government, etc.).
- **Overlapping jobs** produce warnings, not errors (concurrent employment is allowed).
- **Skills** accept both lists and comma-separated strings (auto-normalized).
- **Derived fields auto-computed**: tenure per entry, total months, domain-relevant months, career gap list, domain transitions, experience bucket ("Fresher"/"Junior"/"Mid"/"Senior").

### Changes Made
| File | Change |
|------|--------|
| `validators/work_validators.py` | NEW — `validate_work_entry()`, `detect_overlaps()`, `compute_derived_fields()`, `validate_all_work()` |

### Expected Outcome (Verification)
1. ✅ Valid entry (TCS, SDE, IT, 2022-2024) passes
2. ✅ Missing company → rejected with `company_name` error
3. ✅ 2 jobs (TCS 2020-2022 + Infosys 2023-now) → total exp computed, 7-month gap detected, "Currently Working" status
4. ✅ Overlapping jobs (TCS + Wipro with 3-month overlap) → warning generated
