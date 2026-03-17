/**
 * AdmitGuard v2 — Frontend Application
 * Multi-step form, dynamic education/work entries, real-time validation,
 * LLM chat, and risk score visualization.
 */

const API = '';
let currentStep = 1;
let educationPath = 'A';
let educationEntries = [];
let workEntries = [];
let submissionResult = null;

// ============================================================================
// EDUCATION PATHWAY DEFINITIONS
// ============================================================================
const PATHS = {
    A: { label: 'Standard', levels: ['10th', '12th', 'UG'] },
    B: { label: 'Lateral Entry', levels: ['10th', 'Diploma', 'UG'] },
    C: { label: 'Vocational', levels: ['10th', 'ITI', 'Diploma', 'UG'] },
};

const BOARDS = ['CBSE', 'ICSE', 'State Board', 'NIOS', 'IB', 'Cambridge', 'Other'];
const STREAMS = ['Science', 'Commerce', 'Arts/Humanities', 'Vocational', 'N/A'];
const SCORE_SCALES = ['percentage', 'cgpa_10', 'cgpa_4'];
const DOMAINS = ['IT', 'Non-IT', 'Government', 'Education', 'Healthcare', 'Finance', 'Startup', 'Other'];
const EMP_TYPES = ['Full-time', 'Part-time', 'Internship', 'Contract', 'Freelance'];

// ============================================================================
// STEP NAVIGATION
// ============================================================================
function goToStep(step) {
    // Validate current step before proceeding
    if (step > currentStep && !validateCurrentStep()) return;

    // Hide all steps
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`step-${i}`).classList.add('hidden');
    }

    // Show target step
    document.getElementById(`step-${step}`).classList.remove('hidden');

    // Update indicators
    document.querySelectorAll('.step-dot').forEach(dot => {
        const s = parseInt(dot.dataset.step);
        dot.classList.remove('active', 'completed');
        if (s === step) dot.classList.add('active');
        else if (s < step) dot.classList.add('completed');
    });

    currentStep = step;

    // Step-specific initialization
    if (step === 2) renderEducationEntries();
    if (step === 4) renderReview();

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateCurrentStep() {
    if (currentStep === 1) return validateStep1();
    if (currentStep === 2) return validateStep2();
    if (currentStep === 3) return validateStep3();
    return true;
}

// ============================================================================
// STEP 1: PERSONAL INFO VALIDATION
// ============================================================================
function validateStep1() {
    let valid = true;
    const fields = ['full_name', 'email', 'phone', 'date_of_birth', 'aadhaar'];

    fields.forEach(field => {
        const input = document.getElementById(field);
        const err = document.getElementById(`err-${field}`);
        const val = input.value.trim();

        input.classList.remove('valid', 'invalid');
        err.textContent = '';

        if (!val) {
            err.textContent = `${field.replace(/_/g, ' ')} is required.`;
            input.classList.add('invalid');
            valid = false;
            return;
        }

        // Field-specific checks
        if (field === 'full_name' && val.length < 2) {
            err.textContent = 'Name must be at least 2 characters.';
            input.classList.add('invalid'); valid = false;
        } else if (field === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
            err.textContent = 'Invalid email format.';
            input.classList.add('invalid'); valid = false;
        } else if (field === 'phone' && !/^[6-9]\d{9}$/.test(val.replace(/\D/g, ''))) {
            err.textContent = 'Must be 10 digits starting with 6-9.';
            input.classList.add('invalid'); valid = false;
        } else if (field === 'aadhaar' && val.replace(/\D/g, '').length !== 12) {
            err.textContent = 'Must be exactly 12 digits.';
            input.classList.add('invalid'); valid = false;
        } else {
            input.classList.add('valid');
        }
    });

    return valid;
}

// Real-time field validation on blur
document.addEventListener('DOMContentLoaded', () => {
    ['full_name', 'email', 'phone', 'date_of_birth', 'aadhaar'].forEach(field => {
        const input = document.getElementById(field);
        if (input) {
            input.addEventListener('blur', () => {
                if (currentStep === 1 && input.value.trim()) {
                    validateField(field, input.value);
                }
            });
        }
    });

    // Path selector
    document.querySelectorAll('.path-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.path-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            educationPath = card.dataset.path;
            renderEducationEntries();
        });
    });
});

async function validateField(field, value) {
    try {
        const resp = await fetch(`${API}/api/validate/${field}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ [field]: value }),
        });
        const data = await resp.json();
        const input = document.getElementById(field);
        const err = document.getElementById(`err-${field}`);

        input.classList.remove('valid', 'invalid');
        if (data.valid) {
            input.classList.add('valid');
            err.textContent = '';
        } else {
            input.classList.add('invalid');
            err.textContent = data.error || 'Invalid.';
        }
    } catch (e) {
        // Offline mode — skip server validation
    }
}

// ============================================================================
// STEP 2: EDUCATION ENTRIES
// ============================================================================
function renderEducationEntries() {
    const container = document.getElementById('education-entries');
    const levels = PATHS[educationPath].levels;

    // Initialize entries if path changed
    if (educationEntries.length === 0 || educationEntries[0]._path !== educationPath) {
        educationEntries = levels.map(level => ({
            _path: educationPath,
            level,
            board_university: '',
            stream: level === '10th' ? 'N/A' : '',
            year_of_passing: '',
            score: '',
            score_scale: 'percentage',
            backlog_count: 0,
        }));
    }

    container.innerHTML = educationEntries.map((entry, i) => `
    <div class="entry-block" id="edu-entry-${i}">
      <div class="entry-block__header">
        <span class="entry-block__title">${entry.level} Level</span>
      </div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Board / University <span class="form-label__required">*</span></label>
          <input type="text" class="form-input" id="edu-board-${i}"
            value="${entry.board_university}" placeholder="e.g. CBSE, IIT Gandhinagar"
            oninput="updateEduEntry(${i}, 'board_university', this.value)"
            list="boards-list">
        </div>
        <div class="form-group">
          <label class="form-label">Stream</label>
          <select class="form-select" id="edu-stream-${i}"
            onchange="updateEduEntry(${i}, 'stream', this.value)">
            ${STREAMS.map(s => `<option value="${s}" ${entry.stream === s ? 'selected' : ''}>${s}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Year of Passing <span class="form-label__required">*</span></label>
          <input type="number" class="form-input" id="edu-year-${i}"
            value="${entry.year_of_passing}" placeholder="e.g. 2022" min="2000" max="2030"
            oninput="updateEduEntry(${i}, 'year_of_passing', parseInt(this.value))">
        </div>
        <div class="form-group">
          <label class="form-label">Score <span class="form-label__required">*</span></label>
          <div style="display:flex; gap:0.5rem;">
            <input type="number" class="form-input" id="edu-score-${i}" step="0.01"
              value="${entry.score}" placeholder="Score"
              oninput="updateEduEntry(${i}, 'score', parseFloat(this.value))" style="flex:1;">
            <select class="form-select" id="edu-scale-${i}" style="width:110px;"
              onchange="updateEduEntry(${i}, 'score_scale', this.value)">
              ${SCORE_SCALES.map(s => `<option value="${s}" ${entry.score_scale === s ? 'selected' : ''}>${s === 'percentage' ? '%' : s === 'cgpa_10' ? 'CGPA/10' : 'CGPA/4'}</option>`).join('')}
            </select>
          </div>
        </div>
        ${['UG', 'Diploma'].includes(entry.level) ? `
        <div class="form-group">
          <label class="form-label">Backlogs</label>
          <input type="number" class="form-input" id="edu-backlog-${i}"
            value="${entry.backlog_count}" min="0"
            oninput="updateEduEntry(${i}, 'backlog_count', parseInt(this.value) || 0)">
        </div>` : ''}
      </div>
    </div>
  `).join('');
}

function updateEduEntry(index, field, value) {
    educationEntries[index][field] = value;
}

function validateStep2() {
    let valid = true;
    educationEntries.forEach((entry, i) => {
        if (!entry.board_university) { valid = false; showToast(`${entry.level}: Board/University is required.`, 'error'); }
        if (!entry.year_of_passing) { valid = false; showToast(`${entry.level}: Year is required.`, 'error'); }
        if (!entry.score && entry.score !== 0) { valid = false; showToast(`${entry.level}: Score is required.`, 'error'); }
    });
    return valid;
}

// ============================================================================
// STEP 3: WORK ENTRIES
// ============================================================================
function addWorkEntry() {
    workEntries.push({
        company_name: '', designation: '', domain: 'IT',
        start_date: '', end_date: '', employment_type: 'Full-time',
        skills: '',
    });
    renderWorkEntries();
}

function removeWorkEntry(index) {
    workEntries.splice(index, 1);
    renderWorkEntries();
}

function renderWorkEntries() {
    const container = document.getElementById('work-entries');
    if (workEntries.length === 0) {
        container.innerHTML = '<p class="text-sm text-muted text-center mb-1">No work experience added. Click below to add one, or skip if you\'re a fresher.</p>';
        return;
    }
    container.innerHTML = workEntries.map((entry, i) => `
    <div class="entry-block" id="work-entry-${i}">
      <div class="entry-block__header">
        <span class="entry-block__title">Experience ${i + 1}</span>
        <button class="entry-block__remove" onclick="removeWorkEntry(${i})">✕ Remove</button>
      </div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Company <span class="form-label__required">*</span></label>
          <input type="text" class="form-input" value="${entry.company_name}" placeholder="e.g. TCS"
            oninput="workEntries[${i}].company_name=this.value">
        </div>
        <div class="form-group">
          <label class="form-label">Designation <span class="form-label__required">*</span></label>
          <input type="text" class="form-input" value="${entry.designation}" placeholder="e.g. Software Engineer"
            oninput="workEntries[${i}].designation=this.value">
        </div>
        <div class="form-group">
          <label class="form-label">Domain</label>
          <select class="form-select" onchange="workEntries[${i}].domain=this.value">
            ${DOMAINS.map(d => `<option value="${d}" ${entry.domain === d ? 'selected' : ''}>${d}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Type</label>
          <select class="form-select" onchange="workEntries[${i}].employment_type=this.value">
            ${EMP_TYPES.map(t => `<option value="${t}" ${entry.employment_type === t ? 'selected' : ''}>${t}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Start Date <span class="form-label__required">*</span></label>
          <input type="date" class="form-input" value="${entry.start_date}"
            onchange="workEntries[${i}].start_date=this.value">
        </div>
        <div class="form-group">
          <label class="form-label">End Date <small class="text-muted">(empty = current)</small></label>
          <input type="date" class="form-input" value="${entry.end_date}"
            onchange="workEntries[${i}].end_date=this.value">
        </div>
        <div class="form-group form-group--full">
          <label class="form-label">Skills <small class="text-muted">(comma-separated)</small></label>
          <input type="text" class="form-input" value="${entry.skills}" placeholder="e.g. Python, Flask, AWS"
            oninput="workEntries[${i}].skills=this.value">
        </div>
      </div>
    </div>
  `).join('');
}

function validateStep3() {
    let valid = true;
    workEntries.forEach((entry, i) => {
        if (!entry.company_name.trim()) { valid = false; showToast(`Job ${i + 1}: Company name required.`, 'error'); }
        if (!entry.designation.trim()) { valid = false; showToast(`Job ${i + 1}: Designation required.`, 'error'); }
        if (!entry.start_date) { valid = false; showToast(`Job ${i + 1}: Start date required.`, 'error'); }
    });
    return valid;
}

// ============================================================================
// STEP 4: REVIEW
// ============================================================================
function renderReview() {
    const data = getFormData();
    let html = '';

    // Personal
    html += `<div class="review-section">
    <div class="review-section__title">👤 Personal Info</div>
    ${reviewRow('Name', data.full_name)}
    ${reviewRow('Email', data.email)}
    ${reviewRow('Phone', data.phone)}
    ${reviewRow('DOB', data.date_of_birth)}
    ${reviewRow('Aadhaar', maskAadhaar(data.aadhaar))}
  </div>`;

    // Education
    html += `<div class="review-section">
    <div class="review-section__title">🎓 Education (Path ${educationPath})</div>
    ${educationEntries.map(e =>
        reviewRow(e.level, `${e.board_university} • ${e.score} (${e.score_scale === 'percentage' ? '%' : e.score_scale})${e.backlog_count ? ` • ${e.backlog_count} backlog(s)` : ''}`)
    ).join('')}
  </div>`;

    // Work
    if (workEntries.length > 0) {
        html += `<div class="review-section">
      <div class="review-section__title">💼 Work Experience</div>
      ${workEntries.map(w =>
            reviewRow(w.company_name, `${w.designation} • ${w.domain} • ${w.start_date} to ${w.end_date || 'Present'}`)
        ).join('')}
    </div>`;
    }

    document.getElementById('review-content').innerHTML = html;

    // Run preview validation
    previewValidation(data);
}

function reviewRow(label, value) {
    return `<div class="review-row">
    <span class="review-row__label">${label}</span>
    <span class="review-row__value">${value || '—'}</span>
  </div>`;
}

function maskAadhaar(val) {
    if (!val || val.length < 4) return val;
    return '●●●● ●●●● ' + val.slice(-4);
}

async function previewValidation(data) {
    try {
        const resp = await fetch(`${API}/api/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        const result = await resp.json();

        const flagsDiv = document.getElementById('review-flags');
        if (result.tier2_flags && result.tier2_flags.length > 0) {
            flagsDiv.classList.remove('hidden');
            flagsDiv.innerHTML = `
        <div class="review-section">
          <div class="review-section__title">⚠️ Flags (${result.tier2_flags.length})</div>
          <ul class="flags-list">
            ${result.tier2_flags.map(f => `
              <li class="flags-list__item">⚠ ${f.message}</li>
            `).join('')}
          </ul>
          <p class="text-sm text-muted mt-1">These are informational flags and won't block your submission.</p>
        </div>`;
        } else {
            flagsDiv.classList.add('hidden');
        }

        if (!result.valid) {
            const errs = Object.entries(result.tier1_errors || {});
            if (errs.length > 0) {
                showToast(`${errs.length} validation error(s) found. Please go back and fix.`, 'error');
            }
        }
    } catch (e) {
        // Offline — skip preview
    }
}

// ============================================================================
// SUBMISSION
// ============================================================================
function getFormData() {
    return {
        full_name: document.getElementById('full_name').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        date_of_birth: document.getElementById('date_of_birth').value,
        aadhaar: document.getElementById('aadhaar').value.trim(),
        education_path: educationPath,
        education_entries: educationEntries.map(e => ({
            level: e.level,
            board_university: e.board_university,
            stream: e.stream,
            year_of_passing: e.year_of_passing,
            score: e.score,
            score_scale: e.score_scale,
            backlog_count: e.backlog_count || 0,
        })),
        work_entries: workEntries.map(w => ({
            company_name: w.company_name,
            designation: w.designation,
            domain: w.domain,
            start_date: w.start_date,
            end_date: w.end_date,
            employment_type: w.employment_type,
            skills: typeof w.skills === 'string' ? w.skills.split(',').map(s => s.trim()).filter(Boolean) : w.skills,
        })),
    };
}

async function submitApplication() {
    const btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Submitting...';
    showLoading('Processing your application through 3-tier validation...');

    try {
        const data = getFormData();
        const resp = await fetch(`${API}/api/candidates`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await resp.json();
        hideLoading();

        if (resp.status === 201) {
            submissionResult = result;
            renderConfirmation(result);
            goToStep(5);
            showToast('Application submitted successfully!', 'success');
        } else if (resp.status === 422) {
            // Tier 1 rejection
            const errors = result.errors || {};
            const msgs = Object.values(errors).slice(0, 3).join('\n');
            showToast(`Validation failed:\n${msgs}`, 'error');
        } else {
            showToast(result.error || 'Submission failed.', 'error');
        }
    } catch (e) {
        hideLoading();
        showToast('Network error. Please try again.', 'error');
    }

    btn.disabled = false;
    btn.innerHTML = '✓ Submit Application';
}

// ============================================================================
// STEP 5: CONFIRMATION
// ============================================================================
function renderConfirmation(result) {
    const intel = result.intelligence || {};
    const risk = intel.risk_score || 0;
    const category = intel.category || 'Pending';
    const dq = intel.data_quality || {};

    // Risk gauge
    let gaugeColor = '#10b981'; // green
    if (risk > 60) gaugeColor = '#ef4444';
    else if (risk > 30) gaugeColor = '#f59e0b';

    document.getElementById('risk-gauge').innerHTML = `
    <div class="risk-gauge__circle" style="--gauge-pct:${risk}; --gauge-color:${gaugeColor};">
      <div class="risk-gauge__inner">
        <span class="risk-gauge__score" style="color:${gaugeColor}">${risk}</span>
        <span class="risk-gauge__label">Risk Score</span>
      </div>
    </div>
    <div class="risk-gauge__category">
      <span class="badge badge--${category === 'Strong Fit' ? 'strong' : category === 'Needs Review' ? 'review' : category === 'Weak Fit' ? 'weak' : 'pending'}">${category}</span>
    </div>
  `;

    // Intelligence details
    document.getElementById('confirm-intel').innerHTML = `
    <div class="review-section">
      <div class="review-section__title">📊 Intelligence Report</div>
      ${reviewRow('Category', category)}
      ${reviewRow('Risk Score', `${risk}/100`)}
      ${reviewRow('Data Quality', `${dq.score || 0}/100`)}
      ${reviewRow('Experience', intel.experience_bucket || 'Fresher')}
      ${reviewRow('Confidence', intel.category_confidence || 'N/A')}
      ${intel.anomaly_narration ? `
        <div class="mt-1" style="padding:0.8rem; background:var(--bg-glass); border-radius:var(--radius-sm); font-size:0.85rem; color:var(--text-secondary);">
          <strong>AI Analysis:</strong> ${intel.anomaly_narration}
        </div>` : ''}
    </div>
  `;

    // Flags
    const flags = result.tier2_flags || [];
    const llmFlags = result.llm_flags || [];
    if (flags.length > 0 || llmFlags.length > 0) {
        document.getElementById('confirm-flags').innerHTML = `
      <div class="review-section">
        <div class="review-section__title">⚠️ Flags (${flags.length + llmFlags.length})</div>
        <ul class="flags-list">
          ${flags.map(f => `<li class="flags-list__item">⚠ ${f.message}</li>`).join('')}
          ${llmFlags.map(f => `<li class="flags-list__item flags-list__item--llm">🤖 ${f.message}</li>`).join('')}
        </ul>
      </div>`;
    }

    // Confirm message
    if (result.warning) {
        document.getElementById('confirm-message').textContent = result.warning;
    }
}

// ============================================================================
// CHAT
// ============================================================================
function toggleChat() {
    document.getElementById('chat-panel').classList.toggle('open');
}

async function sendChat() {
    const input = document.getElementById('chat-input');
    const question = input.value.trim();
    if (!question) return;

    addChatMsg(question, 'user');
    input.value = '';

    try {
        const resp = await fetch(`${API}/api/llm/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                form_context: { education_path: educationPath, step: currentStep },
            }),
        });
        const data = await resp.json();
        addChatMsg(data.answer || 'Sorry, I couldn\'t process that.', 'bot');
    } catch (e) {
        addChatMsg('I\'m offline right now. Try again later!', 'bot');
    }
}

function addChatMsg(text, role) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-msg chat-msg--${role}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// ============================================================================
// FIELD EXPLAINER
// ============================================================================
async function explainField(field) {
    try {
        const resp = await fetch(`${API}/api/llm/explain`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ field }),
        });
        const data = await resp.json();
        showToast(data.explanation || `This is the ${field} field.`, 'warning');
    } catch (e) {
        const fallbacks = {
            aadhaar: 'Aadhaar is a 12-digit unique ID issued by UIDAI.',
            education_path: 'Choose your education pathway: A (Standard), B (Diploma), or C (Vocational).',
        };
        showToast(fallbacks[field] || `Enter your ${field.replace(/_/g, ' ')}.`, 'warning');
    }
}

// ============================================================================
// UTILITIES
// ============================================================================
function showToast(message, type = 'success') {
    const existing = document.querySelectorAll('.toast');
    existing.forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function showLoading(text) {
    document.getElementById('loading-text').textContent = text || 'Processing...';
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function resetForm() {
    currentStep = 1;
    educationPath = 'A';
    educationEntries = [];
    workEntries = [];
    submissionResult = null;

    // Reset form fields
    ['full_name', 'email', 'phone', 'date_of_birth', 'aadhaar'].forEach(f => {
        const el = document.getElementById(f);
        if (el) { el.value = ''; el.classList.remove('valid', 'invalid'); }
        const err = document.getElementById(`err-${f}`);
        if (err) err.textContent = '';
    });

    // Reset path selector
    document.querySelectorAll('.path-card').forEach(c => c.classList.remove('selected'));
    document.querySelector('.path-card[data-path="A"]').classList.add('selected');

    // Reset containers
    document.getElementById('education-entries').innerHTML = '';
    document.getElementById('work-entries').innerHTML = '';
    document.getElementById('review-content').innerHTML = '';
    document.getElementById('review-flags').innerHTML = '';
    document.getElementById('review-flags').classList.add('hidden');
    document.getElementById('risk-gauge').innerHTML = '';
    document.getElementById('confirm-intel').innerHTML = '';
    document.getElementById('confirm-flags').innerHTML = '';

    goToStep(1);
}

// Initialize work entries view
document.addEventListener('DOMContentLoaded', () => {
    renderWorkEntries();
});
