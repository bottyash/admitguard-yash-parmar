# Prompt 04 — Candidate API Routes

## R.I.C.E. Framework

### Role
You are a Python/Flask backend engineer implementing RESTful API routes for the AdmitGuard admission system.

### Intent
Create `routes/candidates.py` as a Flask Blueprint with all required API endpoints. Routes must delegate all business logic to `validators/` and `models/` — no raw validation logic inline in routes.

### Constraints
- Use Flask Blueprint (`candidates_bp`)
- No validation logic inside route handlers — delegate to `validators/strict_validators.py` etc.
- Return consistent JSON response shapes
- All routes prefixed with `/api/`
- HTTP status codes: `200` (OK), `201` (Created), `400` (Bad request), `404` (Not found), `422` (Validation error)
- Reject candidates whose interview status is "Rejected" outright
- No authentication required

### Endpoints Required

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/validate` | Validate all fields, return errors dict |
| `POST` | `/api/validate/<field>` | Validate a single named field |
| `POST` | `/api/candidates` | Create candidate (full validation first) |
| `GET`  | `/api/candidates` | List all candidates |
| `GET`  | `/api/candidates/<id>` | Get single candidate |
| `GET`  | `/api/audit-log` | Get audit trail |
| `GET`  | `/api/dashboard` | Get stats |

### Response Shapes

**Validate (POST /api/validate):**
```json
{
  "valid": false,
  "errors": { "full_name": "Full Name must not contain numbers." },
  "soft_errors": {},
  "exception_count": 0,
  "flagged_for_review": false
}
```

**Create candidate success:**
```json
{ "success": true, "message": "Candidate submitted successfully.", "candidate": {...} }
```

**Create candidate failure:**
```json
{ "success": false, "message": "Strict validation failed.", "errors": {...} }
```
