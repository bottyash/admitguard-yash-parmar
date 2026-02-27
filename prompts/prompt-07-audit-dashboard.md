# Prompt 07 — Audit Log & Dashboard API Endpoints

## R.I.C.E. Framework

### Role
You are a Python/Flask backend engineer adding **management visibility** features to AdmitGuard — an audit trail and a statistics dashboard.

### Intent
Add two read-only GET endpoints to the candidate routes blueprint: one for a full audit log of all submissions (with exception details), and one for aggregate stats used by the dashboard UI.

### Constraints
- Both endpoints are `GET` — no mutation
- Audit log must show every submission, newest first
- Audit log entries must include: candidate name, email, exception count, flagged status, exception rationale details, timestamp, candidate_id
- Dashboard stats are computed on-the-fly from the model layer (no caching yet)
- Exception rate = (candidates with ≥1 exception / total candidates) × 100, rounded to 1 decimal

### Endpoints

**`GET /api/audit-log`**
```json
{
  "log": [
    {
      "id": "uuid",
      "candidate_id": "uuid",
      "candidate_name": "Alice Smith",
      "candidate_email": "alice@example.com",
      "action": "SUBMISSION",
      "exception_count": 1,
      "flagged_for_review": false,
      "exceptions": [
        {"field": "date_of_birth", "rationale": "approved by senior counselor"}
      ],
      "timestamp": "2026-02-27T10:00:00"
    }
  ],
  "total": 1
}
```

**`GET /api/dashboard`**
```json
{
  "total_submissions": 10,
  "flagged_count": 2,
  "exception_rate": 40.0
}
```

### Verification
```bash
curl http://localhost:5000/api/audit-log
curl http://localhost:5000/api/dashboard
```
