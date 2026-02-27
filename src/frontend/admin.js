/**
 * AdmitGuard — Admin Panel JavaScript
 * Handles login, candidate management, editing, and deletion.
 */

const API = "http://localhost:5000";

// =============================================================================
// DOM Helpers
// =============================================================================
function $(id) { return document.getElementById(id); }

function showToast(message, type = "success", duration = 3500) {
    const icons = { success: "✅", error: "❌", warning: "⚠️" };
    const container = $("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

// =============================================================================
// API Helpers (with credentials for session cookies)
// =============================================================================
async function api(method, path, body = null) {
    const opts = {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: "include",
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API}${path}`, opts);
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
}

// =============================================================================
// State
// =============================================================================
let _candidates = [];
let _deleteTarget = null;

// =============================================================================
// Auth
// =============================================================================
async function checkLoginStatus() {
    try {
        const { data } = await api("GET", "/api/admin/status");
        if (data.logged_in) {
            showDashboard(data.user);
        }
    } catch { /* not logged in */ }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = $("admin-username").value.trim();
    const password = $("admin-password").value.trim();
    const errorEl = $("login-error");

    if (!username || !password) {
        errorEl.textContent = "Please enter both username and password.";
        errorEl.hidden = false;
        return;
    }

    const loginBtn = $("login-btn");
    loginBtn.disabled = true;
    loginBtn.innerHTML = `<span class="spinner"></span> Signing in…`;

    try {
        const { ok, data } = await api("POST", "/api/admin/login", { username, password });
        if (ok && data.success) {
            errorEl.hidden = true;
            showDashboard(username);
            showToast("Welcome, admin!", "success");
        } else {
            errorEl.textContent = data.error || "Invalid credentials.";
            errorEl.hidden = false;
        }
    } catch {
        errorEl.textContent = "Could not reach server.";
        errorEl.hidden = false;
    } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = "🔓 Sign In";
    }
}

async function handleLogout() {
    try {
        await api("POST", "/api/admin/logout");
    } catch { /* ignore */ }
    $("admin-dashboard").hidden = true;
    $("login-screen").style.display = "";
    $("admin-username").value = "";
    $("admin-password").value = "";
    showToast("Logged out successfully.", "warning");
}

function showDashboard(username) {
    $("login-screen").style.display = "none";
    $("admin-dashboard").hidden = false;
    $("admin-user-label").textContent = `👤 ${username}`;
    loadCandidates();
}

// =============================================================================
// Load Candidates
// =============================================================================
async function loadCandidates() {
    const tbody = $("admin-tbody");
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:48px;color:var(--text-muted)">Loading…</td></tr>`;

    try {
        const { ok, data } = await api("GET", "/api/admin/candidates");
        if (!ok) {
            if (data.error === "Unauthorized. Please login.") {
                handleLogout();
                return;
            }
            throw new Error(data.error);
        }

        _candidates = data.candidates || [];

        // Update stats
        if (data.stats) {
            $("admin-stat-total").textContent = data.stats.total ?? 0;
            $("admin-stat-flagged").textContent = data.stats.flagged ?? 0;
            $("admin-stat-rate").textContent = (data.stats.exception_rate ?? 0) + "%";
        }

        renderCandidates(_candidates);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:48px;color:var(--error)">Error loading data: ${err.message}</td></tr>`;
    }
}

function renderCandidates(list) {
    const tbody = $("admin-tbody");
    const emptyEl = $("admin-empty");
    const countEl = $("admin-candidate-count");

    // Apply search filter
    const query = $("admin-search")?.value.trim().toLowerCase();
    let filtered = list;
    if (query) {
        filtered = list.filter(c =>
            c.full_name?.toLowerCase().includes(query) ||
            c.email?.toLowerCase().includes(query)
        );
    }

    countEl.textContent = `${filtered.length} record${filtered.length !== 1 ? "s" : ""}`;

    if (filtered.length === 0) {
        tbody.innerHTML = "";
        emptyEl.hidden = false;
        return;
    }
    emptyEl.hidden = true;

    tbody.innerHTML = filtered.map(c => {
        const exBadge = c.exception_count > 0
            ? `<span class="badge badge-warning">⚠️ ${c.exception_count}</span>`
            : `<span class="badge badge-neutral">0</span>`;

        const flagBadge = c.flagged_for_review
            ? `<span class="badge badge-error">🚨 Flagged</span>`
            : `<span class="badge badge-success">✓ Clean</span>`;

        const interviewBadge = c.interview_status === "Cleared"
            ? `<span class="badge badge-success">✅ ${c.interview_status}</span>`
            : c.interview_status === "Rejected"
                ? `<span class="badge badge-error">❌ ${c.interview_status}</span>`
                : `<span class="badge badge-warning">⏳ ${c.interview_status}</span>`;

        return `
        <tr data-id="${c.id}">
            <td style="font-weight:500;color:var(--text-primary);white-space:nowrap">${c.full_name}</td>
            <td style="color:var(--text-muted)">${c.email}</td>
            <td style="white-space:nowrap">${c.phone}</td>
            <td>${c.highest_qualification || "—"}</td>
            <td>${interviewBadge}</td>
            <td>${exBadge}</td>
            <td>${flagBadge}</td>
            <td>
                <div class="admin-actions">
                    <button class="btn-edit" onclick="openEditModal('${c.id}')">✏️ Edit</button>
                    <button class="btn-delete" onclick="openDeleteModal('${c.id}')">🗑️</button>
                </div>
            </td>
        </tr>`;
    }).join("");
}

// =============================================================================
// Edit Modal
// =============================================================================
const EDIT_FIELDS = [
    "full_name", "email", "phone", "date_of_birth",
    "highest_qualification", "graduation_year", "percentage_cgpa",
    "screening_test_score", "interview_status", "aadhaar", "offer_letter_sent",
];

function openEditModal(id) {
    const candidate = _candidates.find(c => c.id === id);
    if (!candidate) return;

    $("edit-id").value = id;
    $("edit-modal-subtitle").textContent = `${candidate.full_name} — ${candidate.email}`;

    EDIT_FIELDS.forEach(field => {
        const el = $(`edit-${field}`);
        if (el) el.value = candidate[field] || "";
    });

    $("edit-modal").classList.remove("hidden");
}

function closeEditModal() {
    $("edit-modal").classList.add("hidden");
}

async function handleEditSave(e) {
    e.preventDefault();
    const id = $("edit-id").value;
    const saveBtn = $("edit-save");
    saveBtn.disabled = true;
    saveBtn.innerHTML = `<span class="spinner"></span> Saving…`;

    const payload = {};
    EDIT_FIELDS.forEach(field => {
        const el = $(`edit-${field}`);
        if (el) payload[field] = el.value;
    });

    try {
        const { ok, data } = await api("PUT", `/api/admin/candidates/${id}`, payload);
        if (ok && data.success) {
            showToast("Candidate updated successfully!", "success");
            closeEditModal();
            loadCandidates();
        } else {
            showToast(data.error || "Update failed.", "error");
        }
    } catch {
        showToast("Could not reach server.", "error");
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = "💾 Save Changes";
    }
}

// =============================================================================
// Delete Modal
// =============================================================================
function openDeleteModal(id) {
    const candidate = _candidates.find(c => c.id === id);
    if (!candidate) return;

    _deleteTarget = id;
    $("delete-candidate-info").innerHTML = `
        <div><strong>Name:</strong> ${candidate.full_name}</div>
        <div><strong>Email:</strong> ${candidate.email}</div>
        <div><strong>ID:</strong> ${candidate.id.slice(0, 8)}…</div>
    `;
    $("delete-modal").classList.remove("hidden");
}

function closeDeleteModal() {
    $("delete-modal").classList.add("hidden");
    _deleteTarget = null;
}

async function handleDeleteConfirm() {
    if (!_deleteTarget) return;

    const confirmBtn = $("delete-confirm");
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = `<span class="spinner"></span> Deleting…`;

    try {
        const { ok, data } = await api("DELETE", `/api/admin/candidates/${_deleteTarget}`);
        if (ok && data.success) {
            showToast("Candidate deleted.", "warning");
            closeDeleteModal();
            loadCandidates();
        } else {
            showToast(data.error || "Delete failed.", "error");
        }
    } catch {
        showToast("Could not reach server.", "error");
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = "🗑️ Delete";
    }
}

// =============================================================================
// Theme Toggle
// =============================================================================
function initThemeToggle() {
    const btn = $("theme-toggle");
    const saved = localStorage.getItem("admitguard-theme") || "dark";
    setTheme(saved);

    btn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "dark";
        setTheme(current === "dark" ? "light" : "dark");
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("admitguard-theme", theme);
    const btn = $("theme-toggle");
    if (btn) btn.innerHTML = theme === "dark"
        ? `🌙 <span>Dark</span>`
        : `☀️ <span>Light</span>`;
}

// =============================================================================
// Boot
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();

    // Login form
    $("login-form")?.addEventListener("submit", handleLogin);

    // Logout
    $("logout-btn")?.addEventListener("click", handleLogout);

    // Refresh
    $("admin-refresh-btn")?.addEventListener("click", loadCandidates);

    // Search
    $("admin-search")?.addEventListener("input", () => renderCandidates(_candidates));

    // Edit modal
    $("edit-form")?.addEventListener("submit", handleEditSave);
    $("edit-cancel")?.addEventListener("click", closeEditModal);
    $("edit-modal")?.addEventListener("click", e => {
        if (e.target === $("edit-modal")) closeEditModal();
    });

    // Delete modal
    $("delete-confirm")?.addEventListener("click", handleDeleteConfirm);
    $("delete-cancel")?.addEventListener("click", closeDeleteModal);
    $("delete-modal")?.addEventListener("click", e => {
        if (e.target === $("delete-modal")) closeDeleteModal();
    });

    // Check if already logged in
    checkLoginStatus();
});
