# Prompt 10 — Export Functionality (CSV & JSON)

## R.I.C.E. Framework

### Role
You are a Python backend engineer adding **data portability** to AdmitGuard. Recruiters need to export the candidate list for external processing.

### Intent
Implement two new `GET` endpoints in `routes/candidates.py` for exporting all candidate data as CSV and JSON file downloads. The CSV must be properly quoted and include all fields plus exception totals.

### Constraints
- Use Python's built-in `csv` module and `io.StringIO` — no temporary files on disk
- CSV headers must be human-readable (e.g., "Full Name", "Exception Count")
- JSON export should use `json.dumps(indent=2)` for readability
- Both endpoints must set `Content-Disposition: attachment; filename=...` headers
- Include exception details (joined string) in the CSV "Exceptions" column
- JSON export should return the same shape as `get_all_candidates()` but as a file download

### Endpoints

**`GET /api/export/csv`**
- Content-Type: `text/csv`
- Filename: `admitguard_candidates_YYYYMMDD.csv`

**`GET /api/export/json`**
- Content-Type: `application/json`
- Filename: `admitguard_candidates_YYYYMMDD.json`

### Verification
```bash
# Test download headers
curl -I http://localhost:5000/api/export/csv
# → HTTP/1.1 200 OK
# → Content-Disposition: attachment; filename=...
```
