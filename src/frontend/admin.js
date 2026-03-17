/**
 * AdmitGuard v2 — Admin Panel JavaScript
 * Login, dashboard, candidates (NL search, detail, email), cohorts (params editor), email log, services.
 */

const API = '';
let currentView = 'dashboard';
let allCandidates = [];
let currentCandidateId = null;
let emailCandidateData = null;

// ============================================================================
// AUTH
// ============================================================================
async function doLogin() {
    const user = document.getElementById('login-user').value.trim();
    const pass = document.getElementById('login-pass').value.trim();
    try {
        const r = await fetch(`${API}/api/admin/login`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass }), credentials: 'include',
        });
        const d = await r.json();
        if (d.success) {
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('admin-layout').classList.remove('hidden');
            loadDashboard();
            checkReplyBadge();
        } else {
            document.getElementById('login-error').textContent = d.error || 'Login failed.';
        }
    } catch (e) { document.getElementById('login-error').textContent = 'Connection error.'; }
}

async function doLogout() {
    await fetch(`${API}/api/admin/logout`, { method: 'POST', credentials: 'include' });
    document.getElementById('admin-layout').classList.add('hidden');
    document.getElementById('login-screen').classList.remove('hidden');
}

async function checkReplyBadge() {
    try {
        const r = await fetch(`${API}/api/admin/status`, { credentials: 'include' });
        const d = await r.json();
        const badge = document.getElementById('reply-badge');
        if (d.unread_replies > 0) {
            badge.textContent = d.unread_replies;
            badge.classList.remove('hidden');
        } else { badge.classList.add('hidden'); }
    } catch (e) { }
}

// ============================================================================
// NAVIGATION
// ============================================================================
function switchView(view) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-view="${view}"]`).classList.add('active');

    ['dashboard', 'candidates', 'cohorts', 'emails', 'services'].forEach(v => {
        document.getElementById(`view-${v}`).classList.toggle('hidden', v !== view);
    });

    currentView = view;
    if (view === 'dashboard') loadDashboard();
    else if (view === 'candidates') loadCandidates();
    else if (view === 'cohorts') loadCohorts();
    else if (view === 'emails') loadEmailLog();
    else if (view === 'services') loadServices();
}

// ============================================================================
// DASHBOARD
// ============================================================================
async function loadDashboard() {
    try {
        const r = await fetch(`${API}/api/admin/candidates`, { credentials: 'include' });
        const d = await r.json();
        allCandidates = d.candidates || [];
        const stats = d.stats || {};

        // Stats cards
        const cats = stats.category_distribution || {};
        document.getElementById('stats-grid').innerHTML = `
      <div class="stat-card stat-card--accent">
        <div class="stat-card__value">${stats.total_submissions || 0}</div>
        <div class="stat-card__label">Total Submissions</div>
      </div>
      <div class="stat-card stat-card--success">
        <div class="stat-card__value">${cats['Strong Fit'] || 0}</div>
        <div class="stat-card__label">Strong Fit</div>
      </div>
      <div class="stat-card stat-card--warning">
        <div class="stat-card__value">${cats['Needs Review'] || 0}</div>
        <div class="stat-card__label">Needs Review</div>
      </div>
      <div class="stat-card stat-card--danger">
        <div class="stat-card__value">${stats.flagged_count || 0}</div>
        <div class="stat-card__label">Flagged</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__value">${stats.avg_risk_score || 0}</div>
        <div class="stat-card__label">Avg Risk Score</div>
      </div>
    `;

        // Recent table (last 10)
        const recent = allCandidates.slice(0, 10);
        document.getElementById('dashboard-tbody').innerHTML = recent.map(c => `
      <tr>
        <td>${c.full_name || '—'}</td>
        <td>${c.email || '—'}</td>
        <td>${riskPill(c.risk_score)}</td>
        <td>${categoryBadge(c.category)}</td>
        <td>Path ${c.education_path || '?'}</td>
        <td style="color:var(--text-muted);font-size:0.78rem">${formatDate(c.submitted_at)}</td>
      </tr>
    `).join('') || '<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">No submissions yet.</td></tr>';
    } catch (e) { toast('Failed to load dashboard.', 'error'); }
}

// ============================================================================
// CANDIDATES
// ============================================================================
async function loadCandidates() {
    try {
        const r = await fetch(`${API}/api/admin/candidates`, { credentials: 'include' });
        const d = await r.json();
        allCandidates = d.candidates || [];
        renderCandidatesTable(allCandidates);
    } catch (e) { toast('Failed to load candidates.', 'error'); }
}

function renderCandidatesTable(candidates) {
    document.getElementById('candidates-tbody').innerHTML = candidates.map(c => `
    <tr>
      <td><strong>${c.full_name || '—'}</strong></td>
      <td style="font-size:0.8rem">${c.email || '—'}</td>
      <td>${riskPill(c.risk_score)}</td>
      <td>${categoryBadge(c.category)}</td>
      <td>${c.data_quality_score || 0}/100</td>
      <td>${c.flagged_for_review ? '⚠️' : '✅'}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="viewCandidate('${c.id}')">View</button>
        <button class="btn btn-secondary btn-sm" onclick="openEmailModal('${c.id}','${c.email}','${c.full_name}')">✉️</button>
        <button class="btn btn-danger btn-sm" onclick="deleteCandidate('${c.id}')">✕</button>
      </td>
    </tr>
  `).join('') || '<tr><td colspan="7" style="text-align:center;color:var(--text-muted)">No candidates found.</td></tr>';
}

async function viewCandidate(id) {
    try {
        const r = await fetch(`${API}/api/admin/candidates/${id}`, { credentials: 'include' });
        const d = await r.json();
        const c = d.candidate;
        const emails = d.emails || [];
        currentCandidateId = id;

        const education = c.education_entries || [];
        const work = c.work_entries || [];
        const flags = [];
        try { if (c.flags) JSON.parse(c.flags).forEach(f => flags.push(f)); } catch (e) { }

        let html = `<div class="detail-panel">
      <div class="detail-section">
        <div class="detail-section__title">👤 Personal</div>
        ${detailRow('Name', c.full_name)}${detailRow('Email', c.email)}
        ${detailRow('Phone', c.phone)}${detailRow('DOB', c.date_of_birth)}
        ${detailRow('Path', `Path ${c.education_path}`)}
      </div>
      <div class="detail-section">
        <div class="detail-section__title">📊 Intelligence</div>
        ${detailRow('Risk Score', riskPill(c.risk_score))}
        ${detailRow('Category', categoryBadge(c.category))}
        ${detailRow('Data Quality', `${c.data_quality_score || 0}/100`)}
        ${detailRow('Experience', c.experience_bucket || 'Fresher')}
        ${detailRow('Completeness', `${c.completeness_pct || 0}%`)}
        ${c.anomaly_narration ? `<div style="padding:0.6rem;background:var(--bg-glass);border-radius:6px;font-size:0.82rem;color:var(--text-secondary);margin-top:0.5rem"><strong>AI:</strong> ${c.anomaly_narration}</div>` : ''}
      </div>`;

        if (education.length) {
            html += `<div class="detail-section"><div class="detail-section__title">🎓 Education</div>
        ${education.map(e => detailRow(e.level, `${e.board_university} • ${e.score} (${e.score_scale || '%'})${e.backlog_count ? ` • ${e.backlog_count} backlog(s)` : ''}`)).join('')}
      </div>`;
        }

        if (work.length) {
            html += `<div class="detail-section"><div class="detail-section__title">💼 Work</div>
        ${work.map(w => detailRow(w.company_name, `${w.designation} • ${w.domain} • ${w.start_date} to ${w.end_date || 'Present'}`)).join('')}
      </div>`;
        }

        if (flags.length) {
            html += `<div class="detail-section"><div class="detail-section__title">⚠️ Flags</div>
        ${flags.map(f => `<div style="padding:0.4rem 0.6rem;background:var(--warning-glow);border-radius:6px;margin-bottom:0.4rem;font-size:0.82rem;color:var(--warning)">⚠ ${typeof f === 'string' ? f : f.message || JSON.stringify(f)}</div>`).join('')}
      </div>`;
        }

        if (emails.length) {
            html += `<div class="detail-section"><div class="detail-section__title">✉️ Email Thread</div>
        <div class="email-thread">${emails.map(e => `
          <div class="email-item email-item--${e.direction === 'SENT' ? 'sent' : 'received'} ${e.status === 'unread' ? 'email-item--unread' : ''}">
            <div class="email-item__header">
              <span class="email-item__subject">${e.subject || '(no subject)'}</span>
              <span class="email-item__date">${formatDate(e.sent_at)}</span>
            </div>
            <div class="email-item__body">${(e.body || '').substring(0, 300)}</div>
          </div>
        `).join('')}</div>
      </div>`;
        }

        html += `<div style="margin-top:1rem;display:flex;gap:0.5rem">
      <button class="btn btn-secondary btn-sm" onclick="openEmailModal('${c.id}','${c.email}','${c.full_name}')">✉️ Email</button>
      <button class="btn btn-danger btn-sm" onclick="deleteCandidate('${c.id}')">Delete</button>
      <button class="btn btn-secondary btn-sm" onclick="hideDetail()">Close</button>
    </div></div>`;

        document.getElementById('candidate-detail').innerHTML = html;
        document.getElementById('candidate-detail').classList.remove('hidden');
        document.getElementById('candidate-detail').scrollIntoView({ behavior: 'smooth' });
    } catch (e) { toast('Failed to load candidate.', 'error'); }
}

function hideDetail() {
    document.getElementById('candidate-detail').classList.add('hidden');
}

async function deleteCandidate(id) {
    if (!confirm('Delete this candidate? This cannot be undone.')) return;
    try {
        await fetch(`${API}/api/admin/candidates/${id}`, { method: 'DELETE', credentials: 'include' });
        toast('Candidate deleted.', 'success');
        loadCandidates();
        hideDetail();
    } catch (e) { toast('Delete failed.', 'error'); }
}

// NL Search
async function nlSearch() {
    const query = document.getElementById('nl-search').value.trim();
    if (!query) { renderCandidatesTable(allCandidates); return; }

    try {
        const r = await fetch(`${API}/api/llm/query`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });
        const d = await r.json();
        const filters = d.filters || {};

        let filtered = [...allCandidates];
        if (filters.category) filtered = filtered.filter(c => c.category === filters.category);
        if (filters.flagged_for_review !== undefined) filtered = filtered.filter(c => !!c.flagged_for_review === filters.flagged_for_review);
        if (filters.experience_bucket) filtered = filtered.filter(c => c.experience_bucket === filters.experience_bucket);
        if (filters.education_path) filtered = filtered.filter(c => c.education_path === filters.education_path);
        if (filters.risk_score_min !== undefined) filtered = filtered.filter(c => (c.risk_score || 0) >= filters.risk_score_min);
        if (filters.risk_score_max !== undefined) filtered = filtered.filter(c => (c.risk_score || 0) <= filters.risk_score_max);

        // Fallback: text search on name/email
        if (Object.keys(filters).length === 0) {
            const q = query.toLowerCase();
            filtered = allCandidates.filter(c =>
                (c.full_name || '').toLowerCase().includes(q) ||
                (c.email || '').toLowerCase().includes(q)
            );
        }

        renderCandidatesTable(filtered);
        toast(`Found ${filtered.length} result(s).`, 'success');
    } catch (e) {
        // Fallback: simple text filter
        const q = query.toLowerCase();
        const filtered = allCandidates.filter(c =>
            (c.full_name || '').toLowerCase().includes(q) || (c.email || '').toLowerCase().includes(q)
        );
        renderCandidatesTable(filtered);
    }
}

function clearSearch() {
    document.getElementById('nl-search').value = '';
    renderCandidatesTable(allCandidates);
}

// ============================================================================
// COHORTS
// ============================================================================
async function loadCohorts() {
    try {
        const r = await fetch(`${API}/api/admin/cohorts`, { credentials: 'include' });
        const d = await r.json();
        const cohorts = d.cohorts || [];

        if (cohorts.length === 0) {
            document.getElementById('cohorts-list').innerHTML =
                '<p style="text-align:center;color:var(--text-muted);padding:2rem">No cohorts created yet. Click "+ New Cohort" to create one.</p>';
            return;
        }

        document.getElementById('cohorts-list').innerHTML = `
      <div class="table-wrap"><table class="table"><thead>
        <tr><th>Name</th><th>Description</th><th>Status</th><th>Actions</th></tr>
      </thead><tbody>
        ${cohorts.map(c => `<tr>
          <td><strong>${c.name}</strong></td>
          <td style="color:var(--text-secondary)">${c.description || '—'}</td>
          <td>${c.is_active ? '<span class="badge badge--strong">Active</span>' : '<span class="badge badge--pending">Inactive</span>'}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="editCohortParams('${c.id}','${c.name}')">⚙ Params</button>
          </td>
        </tr>`).join('')}
      </tbody></table></div>`;
    } catch (e) { toast('Failed to load cohorts.', 'error'); }
}

function openCreateCohort() {
    document.getElementById('cohort-name').value = '';
    document.getElementById('cohort-desc').value = '';
    document.getElementById('cohort-modal').classList.add('open');
}

async function createCohort() {
    const name = document.getElementById('cohort-name').value.trim();
    const desc = document.getElementById('cohort-desc').value.trim();
    if (!name) { toast('Cohort name required.', 'error'); return; }

    try {
        await fetch(`${API}/api/admin/cohorts`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description: desc }), credentials: 'include',
        });
        closeModal('cohort-modal');
        toast('Cohort created!', 'success');
        loadCohorts();
    } catch (e) { toast('Failed to create cohort.', 'error'); }
}

async function editCohortParams(cohortId, cohortName) {
    try {
        const r = await fetch(`${API}/api/admin/cohorts/${cohortId}/params`, { credentials: 'include' });
        const d = await r.json();
        const tweakable = d.tweakable || {};
        const effective = d.effective_rules || {};

        let html = `<div class="detail-panel">
      <h3 style="margin-bottom:1rem">⚙️ Parameters: ${cohortName}</h3>
      <div class="param-editor" id="param-fields">`;

        Object.entries(tweakable).forEach(([key, meta]) => {
            const val = effective[key] !== undefined ? effective[key] : meta.default;
            if (meta.type === 'int' || meta.type === 'float') {
                html += `<div class="param-item">
          <label>${meta.label || key}</label>
          <input type="number" data-param="${key}" value="${val}"
            min="${meta.min || 0}" max="${meta.max || 1000}" step="${meta.type === 'float' ? '0.1' : '1'}">
        </div>`;
            }
        });

        html += `</div>
      <div style="margin-top:1rem;display:flex;gap:0.5rem">
        <button class="btn btn-primary btn-sm" onclick="saveCohortParams('${cohortId}')">Save Parameters</button>
        <button class="btn btn-secondary btn-sm" onclick="hideCohortParams()">Cancel</button>
      </div>
    </div>`;

        document.getElementById('cohort-params-editor').innerHTML = html;
        document.getElementById('cohort-params-editor').classList.remove('hidden');
        document.getElementById('cohort-params-editor').scrollIntoView({ behavior: 'smooth' });
    } catch (e) { toast('Failed to load params.', 'error'); }
}

async function saveCohortParams(cohortId) {
    const inputs = document.querySelectorAll('#param-fields [data-param]');
    const params = {};
    inputs.forEach(inp => { params[inp.dataset.param] = inp.value; });

    try {
        await fetch(`${API}/api/admin/cohorts/${cohortId}/params`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params), credentials: 'include',
        });
        toast('Parameters saved!', 'success');
    } catch (e) { toast('Failed to save params.', 'error'); }
}

function hideCohortParams() {
    document.getElementById('cohort-params-editor').classList.add('hidden');
}

// ============================================================================
// EMAIL
// ============================================================================
function openEmailModal(candidateId, email, name) {
    emailCandidateData = { id: candidateId, email, full_name: name };
    document.getElementById('email-to').value = email;
    document.getElementById('email-subject').value = '';
    document.getElementById('email-body').value = '';
    document.getElementById('email-modal').classList.add('open');
    generateDraft();
}

async function generateDraft() {
    const purpose = document.getElementById('email-purpose').value;
    try {
        const r = await fetch(`${API}/api/admin/email/draft`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate: emailCandidateData, purpose }), credentials: 'include',
        });
        const d = await r.json();
        document.getElementById('email-subject').value = d.subject || '';
        document.getElementById('email-body').value = d.body || '';
    } catch (e) {
        document.getElementById('email-subject').value = `Regarding Your Application - ${emailCandidateData?.full_name || ''}`;
        document.getElementById('email-body').value = 'Dear Applicant,\n\nThank you for your application.\n\nBest regards,\nAdmissions Team';
    }
}

async function sendEmail() {
    const btn = document.getElementById('send-email-btn');
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Sending...';

    try {
        const r = await fetch(`${API}/api/admin/email/send`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_id: emailCandidateData?.id || '',
                to_email: document.getElementById('email-to').value,
                subject: document.getElementById('email-subject').value,
                body: document.getElementById('email-body').value,
            }), credentials: 'include',
        });
        const d = await r.json();
        if (d.success) { toast('Email sent!', 'success'); closeModal('email-modal'); }
        else toast(d.error || 'Send failed.', 'error');
    } catch (e) { toast('Send failed.', 'error'); }

    btn.disabled = false; btn.innerHTML = 'Send Email';
}

async function checkReplies() {
    try {
        const r = await fetch(`${API}/api/admin/email/replies`, { credentials: 'include' });
        const d = await r.json();
        toast(`${d.new_replies || 0} new replies found.`, 'success');
        checkReplyBadge();
        loadEmailLog();
    } catch (e) { toast('Reply check failed.', 'error'); }
}

async function loadEmailLog(direction) {
    try {
        let url = `${API}/api/admin/email/log`;
        if (direction) url += `?direction=${direction}`;
        const r = await fetch(url, { credentials: 'include' });
        const d = await r.json();
        const emails = d.emails || [];

        if (emails.length === 0) {
            document.getElementById('email-log').innerHTML =
                '<p style="text-align:center;color:var(--text-muted);padding:2rem">No emails yet.</p>';
            return;
        }

        document.getElementById('email-log').innerHTML = emails.map(e => `
      <div class="email-item email-item--${e.direction === 'SENT' ? 'sent' : 'received'} ${e.status === 'unread' ? 'email-item--unread' : ''}">
        <div class="email-item__header">
          <span class="email-item__subject">${e.direction === 'SENT' ? '→' : '←'} ${e.subject || '(no subject)'}</span>
          <span class="email-item__date">${formatDate(e.sent_at)} • ${e.to_email}</span>
        </div>
        <div class="email-item__body">${(e.body || '').substring(0, 200)}${(e.body || '').length > 200 ? '...' : ''}</div>
      </div>
    `).join('');
    } catch (e) { toast('Failed to load email log.', 'error'); }
}

function emailTab(dir) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    loadEmailLog(dir === 'all' ? null : dir);
}

// ============================================================================
// SERVICES
// ============================================================================
async function loadServices() {
    try {
        const r = await fetch(`${API}/api/admin/services`, { credentials: 'include' });
        const d = await r.json();

        document.getElementById('services-panel').innerHTML = `
      <div style="max-width:500px">
        ${serviceRow('Email (SMTP/IMAP)', d.email?.available)}
        ${serviceRow('Google Sheets', d.google_sheets?.available)}
        ${serviceRow(`LLM (${d.llm?.model || 'qwen3:4b'})`, d.llm?.available)}
      </div>
      <div style="margin-top:1.5rem">
        <button class="btn btn-secondary btn-sm" onclick="triggerSheetSync()">📊 Sync All to Sheets</button>
      </div>`;
    } catch (e) { toast('Failed to load services.', 'error'); }
}

async function triggerSheetSync() {
    try {
        const r = await fetch(`${API}/api/admin/sheets/sync-all`, { method: 'POST', credentials: 'include' });
        const d = await r.json();
        toast(d.message || 'Sync complete.', d.success ? 'success' : 'error');
    } catch (e) { toast('Sync failed.', 'error'); }
}

// ============================================================================
// EXPORT
// ============================================================================
function exportCSV() { window.location.href = `${API}/api/export/csv`; }

// ============================================================================
// HELPERS
// ============================================================================
function riskPill(score) {
    const s = score || 0;
    const cls = s <= 30 ? 'risk-low' : s <= 60 ? 'risk-mid' : 'risk-high';
    return `<span class="risk-pill ${cls}">${s}</span>`;
}

function categoryBadge(cat) {
    const cls = cat === 'Strong Fit' ? 'strong' : cat === 'Needs Review' ? 'review' : cat === 'Weak Fit' ? 'weak' : 'pending';
    return `<span class="badge badge--${cls}">${cat || 'Pending'}</span>`;
}

function serviceRow(name, available) {
    return `<div class="service-row">
    <span>${name}</span>
    <span><span class="status-dot status-dot--${available ? 'on' : 'off'}"></span> ${available ? 'Connected' : 'Offline'}</span>
  </div>`;
}

function detailRow(label, value) {
    return `<div class="detail-row"><span class="detail-row__label">${label}</span><span class="detail-row__value">${value || '—'}</span></div>`;
}

function formatDate(d) {
    if (!d) return '—';
    try { return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }); }
    catch (e) { return d; }
}

function closeModal(id) { document.getElementById(id).classList.remove('open'); }

function toast(msg, type) {
    document.querySelectorAll('.toast').forEach(t => t.remove());
    const el = document.createElement('div');
    el.className = `toast toast--${type || 'success'}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3500);
}

// Auto-check auth on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const r = await fetch(`${API}/api/admin/status`, { credentials: 'include' });
        const d = await r.json();
        if (d.logged_in) {
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('admin-layout').classList.remove('hidden');
            loadDashboard();
            checkReplyBadge();
        }
    } catch (e) { }
});
