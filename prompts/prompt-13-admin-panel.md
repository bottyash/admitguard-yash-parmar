# Prompt 13 — Admin Panel (प्रबंधक)

## R.I.C.E. Framework

### Role
You are a full-stack engineer building an authenticated admin panel for the AdmitGuard application.

### Intent
Add a protected admin interface at `/prabandhak` that allows an administrator to log in, view all candidates, edit any field, and delete records — with full audit logging. The admin panel must match the existing design system (glassmorphism + dark mode) and use Flask sessions for authentication.

### Constraints
- **Route**: Admin UI must be served at `localhost:5000/prabandhak` (प्रबंधक = manager in Hindi).
- **Default Credentials**: Username `admin`, Password `admin123` — hardcoded for development.
- **Authentication**: Use Flask `session` (server-side signed cookie). A `@admin_required` decorator protects all admin API endpoints, returning 401 if not logged in.
- **No New Dependencies**: Use only Flask's built-in session support — no JWT, no extra auth libraries.
- **Edit Restrictions**: Only candidate data fields may be edited (not `id`, `submitted_at`, or computed fields like `exception_count`).
- **Audit Trail**: Every admin edit logs an `ADMIN_EDIT` entry; every delete logs an `ADMIN_DELETE` entry to the existing `audit_log` table.
- **Frontend**: Standalone `admin.html` + `admin.js` + `admin.css` — reuses the main `styles.css` design tokens. Login screen with glassmorphism card, data table with search, edit modal, and delete confirmation modal.

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/admin/login` | Authenticate with username/password |
| `POST` | `/api/admin/logout` | Clear session |
| `GET`  | `/api/admin/status` | Check if currently logged in |
| `GET`  | `/api/admin/candidates` | List all candidates + stats (protected) |
| `GET`  | `/api/admin/candidates/<id>` | Get single candidate (protected) |
| `PUT`  | `/api/admin/candidates/<id>` | Update candidate fields (protected) |
| `DELETE` | `/api/admin/candidates/<id>` | Delete candidate (protected) |

### Expected Outcome (Verification)
1. Navigate to `localhost:5000/prabandhak` → Login form appears.
2. Enter wrong credentials → Error message: "Invalid credentials."
3. Enter `admin` / `admin123` → Dashboard with candidates table and stats.
4. Click ✏️ Edit → Modal with pre-filled fields → Save → Updated in database + audit log.
5. Click 🗑️ Delete → Confirmation modal → Confirm → Record removed + audit log entry.
6. Click 🚪 Logout → Returns to login screen. Protected APIs return 401.
