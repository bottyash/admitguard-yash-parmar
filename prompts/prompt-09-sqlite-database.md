# Prompt 09 — SQLite Database Layer

## R.I.C.E. Framework

### Role
You are a Python backend engineer migrating AdmitGuard from **in-memory storage** to a **persistent SQLite database**. Data must survive server restarts. No new Python packages should be required.

### Intent
Create `src/backend/db.py` with connection management and table initialization. Then rewrite `models/candidate.py` to use SQLite instead of module-level lists. All existing function signatures must remain identical so that `routes/candidates.py` needs zero changes.

### Constraints
- Use Python's built-in `sqlite3` module only — no SQLAlchemy, no extra dependencies
- Database file: `admitguard.db` stored in the `src/backend/` directory
- Enable WAL journal mode for better concurrent read performance
- `init_db()` must be idempotent (`CREATE TABLE IF NOT EXISTS`)
- Use `sqlite3.Row` as `row_factory` so rows are accessible by column name
- JSON-serialize the `exceptions` list field (TEXT column in SQLite)
- Store booleans as INTEGER (0/1), deserialize back to Python bool on read
- Call `init_db()` inside `create_app()` in `app.py` — not at import time
- `*.db` files must be added to `.gitignore`

### Schema

```sql
CREATE TABLE IF NOT EXISTS candidates (
    id                    TEXT PRIMARY KEY,
    full_name             TEXT NOT NULL,
    email                 TEXT NOT NULL UNIQUE,
    ...all 11 fields...,
    exceptions            TEXT DEFAULT '[]',   -- JSON array
    exception_count       INTEGER DEFAULT 0,
    flagged_for_review    INTEGER DEFAULT 0,   -- 0 = False, 1 = True
    submitted_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id                TEXT PRIMARY KEY,
    candidate_id      TEXT NOT NULL,
    candidate_name    TEXT NOT NULL,
    candidate_email   TEXT NOT NULL,
    action            TEXT NOT NULL DEFAULT 'SUBMISSION',
    exception_count   INTEGER DEFAULT 0,
    flagged_for_review INTEGER DEFAULT 0,
    exceptions        TEXT DEFAULT '[]',
    timestamp         TEXT NOT NULL
);
```

### Verification
```bash
# Submit a candidate, stop server, restart, then:
curl http://localhost:5000/api/candidates
# → {"total": 1, ...}  ← data persisted! ✅
```
