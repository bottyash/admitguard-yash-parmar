/**
 * AdmitGuard — Frontend Application
 * Sprint 3: Zero client-side validation. All validation via backend API.
 *
 * API Base: http://localhost:5000
 */

const API_BASE = "http://localhost:5000";

// =============================================================================
// State
// =============================================================================
const state = {
    exceptions: {},          // { fieldName: { enabled: bool, rationale: string } }
    exceptionCount: 0,
    flaggedForReview: false,
    scoreType: "percentage", // "percentage" | "cgpa"
    validFields: new Set(),  // fields that have passed validation
    invalidFields: new Set(),
    isSubmitting: false,
    auditFilter: "all",      // "all" | "flagged" | "exceptions"
};

// =============================================================================
// API Helpers
// =============================================================================
async function apiGet(path) {
    const res = await fetch(`${API_BASE}${path}`);
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    return { ok: res.ok, status: res.status, data: await res.json() };
}

// =============================================================================
// DOM Helpers
// =============================================================================
function $(id) { return document.getElementById(id); }
function el(tag, attrs = {}, ...children) {
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
        if (k === "class") e.className = v;
        else if (k === "html") e.innerHTML = v;
        else e.setAttribute(k, v);
    });
    children.forEach(c => typeof c === "string" ? e.append(c) : e.append(c));
    return e;
}

// =============================================================================
// Toast Notifications
// =============================================================================
function showToast(message, type = "success", duration = 3500) {
    const icons = { success: "✅", error: "❌", warning: "⚠️" };
    const container = $("toast-container");
    const toast = el("div", { class: `toast ${type}` });
    toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

// =============================================================================
// Field Validation (calls backend per-field)
// =============================================================================
function getFormData() {
    return {
        full_name: $("full_name")?.value || "",
        email: $("email")?.value || "",
        phone: $("phone")?.value || "",
        date_of_birth: $("date_of_birth")?.value || "",
        highest_qualification: $("highest_qualification")?.value || "",
        graduation_year: $("graduation_year")?.value || "",
        percentage_cgpa: $("percentage_cgpa")?.value || "",
        score_type: state.scoreType,
        screening_test_score: $("screening_test_score")?.value || "",
        interview_status: $("interview_status")?.value || "",
        aadhaar: $("aadhaar")?.value || "",
        offer_letter_sent: $("offer_letter_sent")?.value || "",
        exceptions: state.exceptions,
    };
}

async function validateField(fieldName) {
    const data = getFormData();
    const inputEl = $(fieldName);
    if (!inputEl) return;

    // Show loading
    setFieldState(fieldName, "loading");

    try {
        const { data: result } = await apiPost(`/api/validate/${fieldName}`, data);
        applyFieldResult(fieldName, result);
    } catch {
        // If API unreachable, don't block user
        setFieldState(fieldName, "idle");
    }
}

function applyFieldResult(fieldName, result) {
    const inputEl = $(fieldName);
    if (!inputEl) return;

    const msgEl = $(`${fieldName}-msg`);
    const exPanel = $(`${fieldName}-exception`);

    inputEl.classList.remove("is-valid", "is-invalid", "is-warning");

    if (result.valid) {
        inputEl.classList.add("is-valid");
        state.validFields.add(fieldName);
        state.invalidFields.delete(fieldName);
        if (msgEl) { msgEl.className = "field-message success"; msgEl.textContent = ""; }
        if (exPanel) exPanel.hidden = true;
    } else {
        state.validFields.delete(fieldName);
        state.invalidFields.add(fieldName);

        if (result.exception_allowed) {
            // Soft rule failure — show exception panel
            inputEl.classList.add("is-warning");
            if (msgEl) {
                msgEl.className = "field-message warning";
                msgEl.innerHTML = `⚠️ ${result.error}`;
            }
            if (exPanel) exPanel.hidden = false;
            updateExceptionCounter();
        } else {
            // Hard failure
            inputEl.classList.add("is-invalid");
            if (msgEl) {
                msgEl.className = "field-message error";
                msgEl.textContent = result.error || "Invalid value.";
            }
            if (exPanel) exPanel.hidden = true;
        }
    }
}

function setFieldState(fieldName, state) {
    const inputEl = $(fieldName);
    if (!inputEl) return;
    if (state === "loading") {
        inputEl.style.opacity = "0.7";
    } else {
        inputEl.style.opacity = "1";
    }
}

// =============================================================================
// Exception Panel Logic
// =============================================================================
function initExceptionPanel(fieldName) {
    const toggleEl = $(`${fieldName}-exception-toggle`);
    const rationaleEl = $(`${fieldName}-rationale`);
    const rationalePanelEl = $(`${fieldName}-rationale-panel`);
    const counterEl = $(`${fieldName}-rationale-counter`);

    if (!toggleEl) return;

    // Initialise state
    if (!state.exceptions[fieldName]) {
        state.exceptions[fieldName] = { enabled: false, rationale: "" };
    }

    toggleEl.addEventListener("change", () => {
        state.exceptions[fieldName].enabled = toggleEl.checked;
        if (rationalePanelEl) rationalePanelEl.hidden = !toggleEl.checked;

        // Re-validate field with new exception state
        validateField(fieldName);
        updateExceptionCounter();
    });

    if (rationaleEl) {
        rationaleEl.addEventListener("input", () => {
            const text = rationaleEl.value;
            state.exceptions[fieldName].rationale = text;

            // Update character counter
            if (counterEl) {
                counterEl.textContent = `${text.length}/30 chars minimum`;
                counterEl.className = `rationale-counter ${text.length >= 30 ? "sufficient" : "insufficient"}`;
            }
        });

        // Validate rationale on blur (re-validate whole field)
        rationaleEl.addEventListener("blur", () => validateField(fieldName));
    }
}

function updateExceptionCounter() {
    const badge = $("exception-count-badge");
    if (!badge) return;

    const enabled = Object.values(state.exceptions).filter(e => e.enabled).length;
    state.exceptionCount = enabled;

    if (enabled === 0) {
        badge.className = "exception-counter none";
        badge.innerHTML = `✓ No exceptions`;
    } else if (enabled <= 2) {
        badge.className = "exception-counter some";
        badge.innerHTML = `⚠️ ${enabled} exception${enabled > 1 ? "s" : ""} (requires manager notation)`;
    } else {
        badge.className = "exception-counter flagged";
        badge.innerHTML = `🚨 ${enabled} exceptions — Will be flagged for manager review`;
    }
}

// =============================================================================
// Score Type Toggle
// =============================================================================
function initScoreTypeToggle() {
    const pctBtn = $("score-type-percentage");
    const cgpaBtn = $("score-type-cgpa");
    const label = $("score-label");
    const hint = $("score-hint");

    if (!pctBtn || !cgpaBtn) return;

    function setScoreType(type) {
        state.scoreType = type;
        pctBtn.classList.toggle("active", type === "percentage");
        cgpaBtn.classList.toggle("active", type === "cgpa");

        if (label) label.textContent = type === "percentage" ? "Percentage (%)" : "CGPA (10-pt scale)";
        if (hint) hint.textContent = type === "percentage" ? "Minimum 60%" : "Minimum 6.0 on 10-point scale";

        // Re-validate the score field
        if ($("percentage_cgpa")?.value) validateField("percentage_cgpa");
    }

    pctBtn.addEventListener("click", () => setScoreType("percentage"));
    cgpaBtn.addEventListener("click", () => setScoreType("cgpa"));
}

// =============================================================================
// Form Submit
// =============================================================================
async function handleSubmit(e) {
    e.preventDefault();
    if (state.isSubmitting) return;

    state.isSubmitting = true;
    const submitBtn = $("submit-btn");
    const origHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = `<span class="spinner"></span> Validating…`;
    submitBtn.disabled = true;

    try {
        const data = getFormData();

        // Final full validation first
        const { data: validation } = await apiPost("/api/validate", data);

        if (!validation.valid) {
            // Show errors
            Object.entries(validation.errors || {}).forEach(([field, error]) => {
                const inputEl = $(field);
                if (inputEl) { inputEl.classList.add("is-invalid"); }
                const msgEl = $(`${field}-msg`);
                if (msgEl) {
                    msgEl.className = "field-message error";
                    msgEl.textContent = error;
                }
            });

            Object.entries(validation.soft_errors || {}).forEach(([field, info]) => {
                const inputEl = $(field);
                if (inputEl) inputEl.classList.add("is-warning");
                const exPanel = $(`${field}-exception`);
                if (exPanel) exPanel.hidden = false;
                const msgEl = $(`${field}-msg`);
                if (msgEl) {
                    msgEl.className = "field-message warning";
                    msgEl.innerHTML = `⚠️ ${info.error}`;
                }
            });

            showToast("Please fix validation errors before submitting.", "error");
            return;
        }

        // Submit candidate
        submitBtn.innerHTML = `<span class="spinner"></span> Submitting…`;
        const { ok, data: result } = await apiPost("/api/candidates", data);

        if (ok && result.success) {
            showSuccessModal(result, data);
            resetForm();
        } else {
            showToast(result.message || "Submission failed.", "error");
        }
    } catch {
        showToast("Could not reach server. Is the backend running?", "error");
    } finally {
        state.isSubmitting = false;
        submitBtn.innerHTML = origHTML;
        submitBtn.disabled = false;
    }
}

// =============================================================================
// Success Modal
// =============================================================================
function showSuccessModal(result, data) {
    const modal = $("success-modal");
    const summary = $("modal-summary");
    const warning = $("modal-warning");

    const rows = [
        ["Name", data.full_name],
        ["Email", data.email],
        ["Phone", data.phone],
        ["Qualification", data.highest_qualification],
        ["Graduation Year", data.graduation_year],
        [data.score_type === "cgpa" ? "CGPA" : "Percentage", data.percentage_cgpa + (data.score_type === "cgpa" ? "" : "%")],
        ["Screening Score", data.screening_test_score],
        ["Interview Status", data.interview_status],
        ["Offer Letter", data.offer_letter_sent],
        ["Candidate ID", result.candidate?.id?.slice(0, 8) + "…"],
    ];

    summary.innerHTML = rows.map(([k, v]) => `
    <div class="summary-row">
      <span class="summary-key">${k}</span>
      <span class="summary-val">${v || "—"}</span>
    </div>`).join("");

    if (result.flagged_for_review) {
        warning.hidden = false;
        warning.innerHTML = `🚨 This entry has ${result.exception_count} exceptions and has been flagged for manager review.`;
    } else {
        warning.hidden = true;
    }

    modal.classList.remove("hidden");
}

function closeModal() {
    $("success-modal").classList.add("hidden");
}

// =============================================================================
// Form Reset
// =============================================================================
function resetForm() {
    $("candidate-form").reset();
    state.exceptions = {};
    state.exceptionCount = 0;
    state.validFields.clear();
    state.invalidFields.clear();
    state.scoreType = "percentage";

    // Reset all field states
    document.querySelectorAll(".field-input").forEach(el => {
        el.classList.remove("is-valid", "is-invalid", "is-warning");
    });
    document.querySelectorAll(".field-message").forEach(el => el.textContent = "");
    document.querySelectorAll("[id$='-exception']").forEach(el => el.hidden = true);
    document.querySelectorAll("[id$='-exception-toggle']").forEach(el => el.checked = false);
    document.querySelectorAll("[id$='-rationale']").forEach(el => el.value = "");
    document.querySelectorAll("[id$='-rationale-panel']").forEach(el => el.hidden = true);

    updateExceptionCounter();
}

// =============================================================================
// Audit Log
// =============================================================================
let _lastLog = [];  // Cache for search

async function loadAuditLog() {
    const table = $('audit-tbody');

    table.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted)">Loading…</td></tr>`;

    try {
        const { log } = await apiGet('/api/audit-log');
        _lastLog = log;
        renderAuditLog(log);
    } catch {
        table.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--error)">Could not reach server.</td></tr>`;
    }
}

function renderAuditLog(log) {
    const table = $('audit-tbody');
    const emptyState = $('audit-empty');
    const countEl = $('audit-count');

    // Apply filter
    let filtered = log;
    if (state.auditFilter === 'flagged') filtered = log.filter(e => e.flagged_for_review);
    if (state.auditFilter === 'exceptions') filtered = log.filter(e => e.exception_count > 0);

    // Apply search
    const searchEl = $('audit-search');
    const searchQuery = searchEl?.value.trim().toLowerCase();
    if (searchQuery) {
        filtered = filtered.filter(e =>
            e.candidate_name?.toLowerCase().includes(searchQuery) ||
            e.candidate_email?.toLowerCase().includes(searchQuery)
        );
    }

    // Update count badge
    if (countEl) countEl.textContent = `${filtered.length} entr${filtered.length === 1 ? 'y' : 'ies'}`;

    if (filtered.length === 0) {
        table.innerHTML = "";
        if (emptyState) emptyState.hidden = false;
        return;
    }

    if (emptyState) emptyState.hidden = true;

    table.innerHTML = filtered.map(entry => {
        const dt = new Date(entry.timestamp);
        const timeStr = dt.toLocaleString("en-IN", {
            day: "2-digit", month: "short", year: "numeric",
            hour: "2-digit", minute: "2-digit"
        });

        const exBadge = entry.exception_count > 0
            ? `<span class="badge badge-warning">⚠️ ${entry.exception_count} exception${entry.exception_count > 1 ? "s" : ""}</span>`
            : `<span class="badge badge-neutral">None</span>`;

        const flagBadge = entry.flagged_for_review
            ? `<span class="badge badge-error">🚨 Flagged</span>`
            : `<span class="badge badge-success">✓ Clean</span>`;

        const actionBadge = `<span class="badge badge-info">📋 ${entry.action}</span>`;

        const excDetails = (entry.exceptions || []).map(ex =>
            `<div style="font-size:0.72rem;color:var(--text-muted)">• <b>${ex.field.replace(/_/g, " ")}</b>: ${ex.rationale?.slice(0, 60)}…</div>`
        ).join("");

        return `
      <tr>
        <td style="white-space:nowrap;color:var(--text-primary);font-weight:500">${entry.candidate_name}</td>
        <td style="color:var(--text-muted)">${entry.candidate_email}</td>
        <td>${actionBadge}</td>
        <td>${exBadge}${excDetails ? `<div style="margin-top:4px">${excDetails}</div>` : ""}</td>
        <td>${flagBadge}</td>
        <td style="white-space:nowrap;color:var(--text-muted);font-size:0.78rem">${timeStr}</td>
        <td style="font-size:0.72rem;color:var(--text-muted)">${entry.candidate_id?.slice(0, 8)}…</td>
      </tr>`;
    }).join("");
}

// =============================================================================
// Dashboard
// =============================================================================
async function loadDashboard() {
    try {
        const data = await apiGet("/api/dashboard");
        $("stat-total").textContent = data.total_submissions ?? 0;
        $("stat-flagged").textContent = data.flagged_count ?? 0;
        $("stat-rate").textContent = (data.exception_rate ?? 0) + "%";
    } catch {
        // silently fail
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
// Tab Navigation
// =============================================================================
function initTabs() {
    const tabs = document.querySelectorAll(".nav-tab");
    const panels = document.querySelectorAll(".tab-panel");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            const panelId = tab.getAttribute("data-panel");
            const panel = $(panelId);
            if (panel) panel.classList.add("active");

            // Load data when switching tabs
            if (panelId === "tab-audit") loadAuditLog();
            if (panelId === "tab-dashboard") loadDashboard();
        });
    });
}

// =============================================================================
// Audit Filter Buttons
// =============================================================================
function initAuditFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.auditFilter = btn.getAttribute('data-filter');
            const { log } = await apiGet('/api/audit-log');
            _lastLog = log;
            renderAuditLog(log);
        });
    });

    // Live search
    const searchEl = $('audit-search');
    if (searchEl) {
        searchEl.addEventListener('input', () => renderAuditLog(_lastLog));
    }
}

// =============================================================================
// Attach field validation listeners
// =============================================================================
function attachFieldListeners() {
    const strictFields = [
        "full_name", "email", "phone",
        "highest_qualification", "interview_status",
        "aadhaar", "offer_letter_sent",
    ];

    const softFields = [
        "date_of_birth", "graduation_year",
        "percentage_cgpa", "screening_test_score",
    ];

    const allFields = [...strictFields, ...softFields];

    allFields.forEach(field => {
        const el = $(field);
        if (!el) return;
        el.addEventListener("blur", () => validateField(field));
        if (field === "offer_letter_sent") {
            el.addEventListener("change", () => {
                validateField("offer_letter_sent");
                validateField("interview_status");
            });
        }
        if (field === "interview_status") {
            el.addEventListener("change", () => {
                validateField("interview_status");
                validateField("offer_letter_sent");
            });
        }
    });

    // Init soft field exception panels
    softFields.forEach(initExceptionPanel);
}

// =============================================================================
// Boot
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initTabs();
    initScoreTypeToggle();
    attachFieldListeners();
    initAuditFilters();
    updateExceptionCounter();

    // Form submit
    $('candidate-form')?.addEventListener('submit', handleSubmit);

    // Ctrl+Enter shortcut to submit
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            $('submit-btn')?.click();
        }
    });

    // Reset button
    $('reset-btn')?.addEventListener('click', () => {
        if (confirm('Clear all form data?')) resetForm();
    });

    // Modal close
    $("modal-close")?.addEventListener("click", closeModal);
    $("modal-new-btn")?.addEventListener("click", closeModal);
    $("success-modal")?.addEventListener("click", (e) => {
        if (e.target === $("success-modal")) closeModal();
    });

    // Initial dashboard load
    loadDashboard();
});
