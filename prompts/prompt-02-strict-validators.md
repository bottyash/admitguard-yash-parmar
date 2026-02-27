# Prompt 02 — Strict Field Validators

## R.I.C.E. Framework

### Role
You are a Python backend engineer implementing **non-negotiable validation rules** for an admission data entry system. These rules cannot be overridden under any circumstance.

### Intent
Create `validators/strict_validators.py` with individual validator functions for 7 fields. Each function must return `{"valid": bool, "error": str|None}`. Also expose `validate_all_strict(data, existing_emails)` that runs all validators and returns a combined dict.

### Constraints
- Zero client-side validation — all rules enforced server-side only
- Return consistent `{"valid": bool, "error": str|None}` shape from every function
- Email uniqueness check requires passing in existing emails list (no DB query inside validator)
- Strip and lower-case strings before validating
- Rules must be driven by `rules_config.py` flags (not hardcoded inline)
- Aadhaar must be stored/transmitted as a string (leading zeros matter)

### Field Rules

| Field | Rule |
|-------|------|
| `full_name` | Required, min 2 chars, no digits |
| `email` | Valid format (`@` + `.`), must be unique |
| `phone` | Exactly 10 digits, starts with 6/7/8/9 |
| `highest_qualification` | Must be one of: B.Tech, B.E., B.Sc, BCA, M.Tech, M.Sc, MCA, MBA |
| `interview_status` | Must be one of: Cleared, Waitlisted, Rejected |
| `aadhaar` | Exactly 12 digits |
| `offer_letter_sent` | Only "Yes" if interview is Cleared or Waitlisted |

### Example Output

```python
validate_full_name("John123")
# → {"valid": False, "error": "Full Name must not contain numbers."}

validate_email("not-an-email", [])
# → {"valid": False, "error": "Email must be a valid email address."}

validate_offer_letter("Yes", "Rejected")
# → {"valid": False, "error": "Offer letter cannot be sent if interview was Rejected."}
```

### Verification
```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John123"}'
# → {"errors": {"full_name": "Full Name must not contain numbers."}, "valid": false}
```
