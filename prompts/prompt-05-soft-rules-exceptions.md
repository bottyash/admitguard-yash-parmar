# Prompt 05 — Soft Rule Validators & Exception System

## R.I.C.E. Framework

### Role
You are a Python backend engineer implementing the **soft rule validation** layer for AdmitGuard. Soft rules can be overridden with a manager-approved rationale.

### Intent
Create `validators/soft_validators.py` with per-field validators for 4 fields that use configurable thresholds. Each validator must indicate whether an exception is allowed and expose `validate_all_soft(data, exceptions)` that applies rationale checking when a rule is overridden.

### Constraints
- Soft rule thresholds come from `rules_config.py` — never hardcoded inline
- Each validator returns `{"valid": bool, "error": str|None, "exception_allowed": bool, "exception_applied": bool}`
- Exception override requires: (1) `enabled: true`, (2) rationale ≥ 30 characters, (3) rationale contains at least one approved keyword
- Approved rationale keywords: `"approved by"`, `"special case"`, `"documentation pending"`, `"waiver granted"`
- `count_exceptions(soft_results)` returns count of applied exceptions
- `is_flagged_for_review(exception_count)` returns `True` if count > `RULE_MAX_EXCEPTIONS_BEFORE_FLAG`

### Rules

| Field | Rule |
|-------|------|
| `date_of_birth` | Age 18–35 (inclusive) |
| `graduation_year` | 2015–2025 (inclusive) |
| `percentage_cgpa` | ≥ 60% or ≥ 6.0 CGPA (depends on `score_type`) |
| `screening_test_score` | ≥ 40 |

### Example

```python
# Exception with valid rationale
validate_date_of_birth("1980-01-01")
# → {"valid": False, "error": "Age must be between 18 and 35.", "exception_allowed": True, "exception_applied": False}

# After exception override with valid rationale
result["exception_applied"] = True
result["valid"] = True
```

**Flagging logic:**
```python
count_exceptions(soft_results)     # → 3
is_flagged_for_review(3)           # → True  (RULE_MAX = 2)
```
