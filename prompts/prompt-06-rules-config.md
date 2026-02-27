# Prompt 06 — Configuration-Driven Rules (`rules_config.py`)

## R.I.C.E. Framework

### Role
You are a Python engineer setting up a **single source of truth for all validation rule parameters** in AdmitGuard. Compliance teams must be able to change thresholds without touching validators or route code.

### Intent
Create `src/backend/rules_config.py` with all strict and soft rule toggle flags as Python constants. Every threshold used in the system must be defined here. Validators import from this file — they must not hardcode values.

### Constraints
- Plain Python constants only — no JSON, YAML, or .env
- All boolean flags use `RULE_` prefix
- Soft rule thresholds use descriptive names: `RULE_AGE_MIN`, `RULE_PERCENTAGE_MIN`, etc.
- File must be importable from any validator file
- Include inline comments explaining each flag
- Keep flags grouped by rule type (strict / soft)

### Example Content

```python
# ── Strict rules (non-negotiable) ───────────────────────────────────────────
RULE_FULL_NAME_ENABLED    = True   # False = skip validation entirely
RULE_FULL_NAME_MIN_LENGTH = 2
RULE_EMAIL_ENABLED        = True
RULE_PHONE_ENABLED        = True
RULE_QUALIFICATION_ENABLED = True
VALID_QUALIFICATIONS = ["B.Tech", "B.E.", "B.Sc", "BCA", "M.Tech", "M.Sc", "MCA", "MBA"]

# ── Soft rules (overridable with rationale) ──────────────────────────────────
RULE_AGE_ENABLED   = True
RULE_AGE_MIN       = 18      # years
RULE_AGE_MAX       = 35      # years

RULE_GRAD_YEAR_ENABLED = True
RULE_GRAD_YEAR_MIN     = 2015
RULE_GRAD_YEAR_MAX     = 2025

RULE_PERCENTAGE_MIN    = 60.0  # percent
RULE_CGPA_MIN          = 6.0   # on 10-pt scale

RULE_SCREENING_SCORE_MIN = 40  # out of 100

# ── Exception / flagging ─────────────────────────────────────────────────────
RULE_MAX_EXCEPTIONS_BEFORE_FLAG = 2    # > 2 → flagged for manager review
RULE_RATIONALE_MIN_LENGTH       = 30   # characters
RULE_RATIONALE_KEYWORDS = [
    "approved by", "special case",
    "documentation pending", "waiver granted",
]
```

### Usage in Validators
```python
from rules_config import RULE_AGE_MIN, RULE_AGE_MAX

def validate_date_of_birth(dob: str) -> dict:
    age = calculate_age(dob)
    if not RULE_AGE_MIN <= age <= RULE_AGE_MAX:
        return {"valid": False, "error": f"Age must be between {RULE_AGE_MIN} and {RULE_AGE_MAX}."}
```
