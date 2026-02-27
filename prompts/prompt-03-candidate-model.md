# Prompt 03 — Candidate Data Model (In-Memory)

## R.I.C.E. Framework

### Role
You are a Python backend engineer building the data model layer for AdmitGuard's candidate management. At this stage, use in-memory lists (no DB yet).

### Intent
Create `models/candidate.py` with functions to add candidates, retrieve them by ID or list all, check existing emails for uniqueness, and maintain a simple in-memory audit log. Each candidate must get a UUID and a timestamp on creation.

### Constraints
- Use Python `uuid` and `datetime` modules only (no ORM, no DB)
- All data stored in module-level lists: `_candidates`, `_audit_log`
- Expose clean functional interface — no classes needed
- Candidate dict must include: id, all 11 fields, exceptions list, exception_count, flagged_for_review, submitted_at
- `get_all_emails()` must return a list of emails (for uniqueness check in routes)
- Audit log entry must include: candidate_id, name, email, action, exception_count, flagged_for_review, timestamp

### Functions Required

```python
add_candidate(data, exceptions_applied, exception_count, flagged_for_review) → dict
get_all_candidates() → list[dict]
get_candidate_by_id(candidate_id) → dict | None
get_all_emails() → list[str]
get_candidate_count() → int
get_flagged_count() → int
get_exception_rate() → float   # % of candidates with ≥1 exception
get_audit_log() → list[dict]
```

### Example
```python
candidate = add_candidate(
    {"full_name": "Alice", "email": "alice@example.com", ...},
    exceptions_applied=[],
    exception_count=0,
    flagged_for_review=False
)
# → {"id": "abc-123", "full_name": "Alice", ..., "submitted_at": "2026-02-27T10:00:00"}
```
