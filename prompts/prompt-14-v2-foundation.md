# Prompt 14 — v2 Foundation & Config

## R.I.C.E. Framework

### Role
You are a backend engineer setting up the foundation for AdmitGuard v2 — a major upgrade from a simple form validator to an enterprise admission platform.

### Intent
Establish the configuration infrastructure for v2. Replace hardcoded secrets with environment variables, add new dependencies (Google Sheets, Ollama LLM, email), and prepare the project structure for 7-table database, intelligence layer, and multi-service integration.

### Constraints
- **No hardcoded secrets**: All API keys, credentials, and config in `.env` (excluded from git). `.env.example` committed as template.
- **Backward compatible startup**: App must still start with `python app.py` even if Google Sheets, Ollama, or email are not configured (graceful fallback).
- **Dependencies pinned**: All packages in `requirements.txt` with exact versions for reproducibility.
- **dotenv loaded early**: `load_dotenv()` must run before any module that reads `os.getenv()`.

### Changes Made
| File | Change |
|------|--------|
| `.env.example` | NEW — Template with all v2 config: Flask, admin, Google Sheets, Ollama, SMTP/IMAP |
| `.env` | NEW — Local dev values (gitignored) |
| `.gitignore` | Updated — Added `credentials.json`, kept `.env.example` with `!.env.example` |
| `requirements.txt` | Updated — Added `python-dotenv`, `gspread`, `google-auth`, `ollama` |
| `app.py` | Updated — Loads `.env` at startup, reads `SECRET_KEY` from env, health check bumped to v2 |

### Expected Outcome (Verification)
1. `python app.py` starts without errors (even without Google Sheets, Ollama, or email configured).
2. `GET /api/health` returns `{"version": "2.0.0", "sprint": "v2"}`.
3. `.env.example` is committed to git; `.env` and `credentials.json` are ignored.
