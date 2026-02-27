# Prompt 01 — Project Foundation & Flask Setup

## R.I.C.E. Framework

### Role
You are a senior Python backend engineer setting up a new Flask project from scratch for a real-time admission data validation system called **AdmitGuard**.

### Intent
Scaffold the AdmitGuard project with a clean, maintainable folder structure. Set up a Flask application with CORS support, a health check endpoint, and placeholder blueprints for future routes. All code should live under `src/backend/`.

### Constraints
- Use Python + Flask only (no Django, FastAPI, etc.)
- Enable `flask-cors` for all API routes (`/api/*`)
- Use Blueprints for route organization (routes in `routes/` folder)
- Separate concerns: `models/`, `validators/`, `routes/` subdirectories
- Include a `requirements.txt`
- No database yet — in-memory storage only (placeholder)
- No client-side validation logic anywhere

### Examples

**Expected folder structure:**
```
src/backend/
├── app.py              # Flask entry point
├── rules_config.py     # All rule flags (empty for now)
├── requirements.txt
├── models/
│   ├── __init__.py
│   └── candidate.py    # In-memory list storage
├── validators/
│   └── __init__.py
└── routes/
    ├── __init__.py
    └── candidates.py   # Blueprint with /api/health
```

**Health check response:**
```json
{ "status": "healthy", "version": "1.0.0", "sprint": 1 }
```

**Verification:**
```bash
curl http://localhost:5000/api/health
# → {"status": "healthy", ...}
```
