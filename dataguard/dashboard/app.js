// DataGuard Web Dashboard Client Script

const API_BASE = window.location.origin;

let currentFile = null;
let currentSummary = null;

const TEMPLATES = {
  customer: `# Customer Data Quality Rules
dataset: customers.csv
version: "1.0"
description: "Rules for customer onboarding and profile integrity"

thresholds:
  fail_on: high
  min_quality_score: 85.0

dataset_checks:
  min_rows: 5
  required_columns:
    - customer_id
    - name
    - email
    - age
    - status

columns:
  customer_id:
    type: integer
    required: true
    unique: true
    min: 1
    severity: critical
    weight: 2.0

  email:
    type: string
    required: true
    format: email
    severity: high

  age:
    type: integer
    min: 18
    max: 120
    severity: medium

  status:
    type: string
    required: true
    allowed: [active, inactive, pending, suspended]
    severity: high
`,
  ecommerce: `# E-Commerce Transaction Rules
dataset: orders.json
version: "1.0"
description: "Transaction and order validation rules"

thresholds:
  fail_on: high
  min_quality_score: 90.0

columns:
  order_id:
    type: string
    required: true
    unique: true
    regex: "^ORD-[0-9]{6}$"
    severity: critical

  customer_id:
    type: integer
    required: true
    min: 1
    severity: high

  amount:
    type: float
    required: true
    min: 0.01
    max: 100000.00
    severity: critical

  currency:
    type: string
    required: true
    allowed: [USD, EUR, GBP, CAD, AUD, JPY]
    severity: high

  items_count:
    type: integer
    required: true
    min: 1
    severity: medium
`,
  basic: `# Basic Table Constraints
dataset: dataset.csv
version: "1.0"

thresholds:
  fail_on: high
  min_quality_score: 80.0

columns:
  id:
    type: integer
    required: true
    unique: true
    severity: critical

  name:
    type: string
    required: true
    severity: high
`,
};

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupDropzone();
  loadHistory();
  loadTemplate('customer');
  refreshIcons();
});

function initTheme() {
  const saved = localStorage.getItem('dataguard_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('dataguard_theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  if (icon) {
    icon.setAttribute('data-lucide', theme === 'light' ? 'moon' : 'sun');
    refreshIcons();
  }
}

function refreshIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

function loadTemplate(name) {
  const editor = document.getElementById('ruleEditor');
  if (editor && TEMPLATES[name]) {
    editor.value = TEMPLATES[name];
  }
}

function setupDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });
}

function handleFile(file) {
  currentFile = file;
  const fileNameDisplay = document.getElementById('selectedFileName');
  const fileNameText = document.getElementById('selectedFileNameText');
  if (fileNameDisplay && fileNameText) {
    fileNameText.innerHTML = `<strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
    fileNameDisplay.style.display = 'flex';
    refreshIcons();
  }
}

async function loadAndRunSample(sampleId) {
  const statusMsg = document.getElementById('validationStatus');
  const btn = document.getElementById('btnValidate');

  if (sampleId === 'customers' || sampleId === 'dirty_users') {
    loadTemplate('customer');
  } else if (sampleId === 'orders') {
    loadTemplate('ecommerce');
  }

  btn.disabled = true;
  if (statusMsg) {
    statusMsg.innerHTML = `<i data-lucide="loader-2" class="spin" style="width:14px; height:14px;"></i> Executing ${sampleId} sample...`;
    refreshIcons();
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/validations/sample/${sampleId}`, {
      method: 'POST',
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Sample run failed');
    }

    const summary = await res.json();
    currentSummary = summary;
    renderResults(summary);
    loadHistory();
  } catch (err) {
    alert('Sample Error: ' + err.message);
  } finally {
    btn.disabled = false;
    if (statusMsg) statusMsg.innerHTML = '';
  }
}

async function runLiveValidation() {
  const btn = document.getElementById('btnValidate');
  const statusMsg = document.getElementById('validationStatus');
  const rulesYaml = document.getElementById('ruleEditor').value;

  if (!currentFile) {
    alert('Please select or drop a data file (CSV, JSON, Parquet) first, or click one of the Quick Test Samples above.');
    return;
  }

  btn.disabled = true;
  if (statusMsg) {
    statusMsg.innerHTML = `<i data-lucide="loader-2" class="spin" style="width:14px; height:14px;"></i> Ingesting and evaluating rules...`;
    refreshIcons();
  }

  const formData = new FormData();
  formData.append('file', currentFile);
  formData.append('rules_yaml', rulesYaml);
  formData.append('project_name', 'Web Studio');

  try {
    const res = await fetch(`${API_BASE}/api/v1/validations/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Validation failed');
    }

    const summary = await res.json();
    currentSummary = summary;
    renderResults(summary);
    loadHistory();
  } catch (err) {
    alert('Validation Error: ' + err.message);
  } finally {
    btn.disabled = false;
    if (statusMsg) statusMsg.innerHTML = '';
  }
}

function renderResults(summary) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;

  container.style.display = 'block';
  container.scrollIntoView({ behavior: 'smooth' });

  // Update Score & Badges
  const scoreEl = document.getElementById('resScore');
  const scoreBar = document.getElementById('resScoreBar');
  const gateBadge = document.getElementById('resGateBadge');
  const countsEl = document.getElementById('resCounts');

  const score = summary.quality_score;
  scoreEl.innerText = `${score.toFixed(1)}%`;
  scoreEl.style.color = score >= 90 ? 'var(--success)' : score >= 75 ? 'var(--warning)' : 'var(--danger)';

  if (scoreBar) {
    scoreBar.style.width = `${score}%`;
    scoreBar.style.background = score >= 90 ? 'var(--success)' : score >= 75 ? 'var(--warning)' : 'var(--danger)';
  }

  const gatePassed = summary.passed_gate;
  gateBadge.className = `badge ${gatePassed ? 'badge-pass' : 'badge-fail'}`;
  gateBadge.innerHTML = gatePassed
    ? `<i data-lucide="check" style="width:14px; height:14px;"></i> Gate: PASSED`
    : `<i data-lucide="x" style="width:14px; height:14px;"></i> Gate: FAILED`;

  countsEl.innerHTML = `
    <strong>${summary.passed_rules}</strong> passed &bull; 
    <strong style="color:var(--danger);">${summary.failed_rules}</strong> failed &bull; 
    <strong>${summary.profile?.row_count || 0}</strong> rows checked in ${summary.total_duration_ms.toFixed(1)}ms
  `;

  // Render Rules Table
  const tbody = document.getElementById('resTableBody');
  tbody.innerHTML = '';

  summary.results.forEach((r) => {
    const tr = document.createElement('tr');
    const badgeClass = r.status === 'pass' ? 'badge-pass' : r.status === 'fail' ? 'badge-fail' : 'badge-warn';
    const statusIcon = r.status === 'pass' ? 'check-circle' : r.status === 'fail' ? 'x-circle' : 'alert-circle';
    const rateText = r.failed_count > 0 ? (r.failure_rate * 100).toFixed(1) + '%' : '0.0%';

    let sampleHtml = '';
    if (r.samples && r.samples.length > 0) {
      sampleHtml = `<div style="margin-top:0.4rem; font-size:0.8rem; background:rgba(0,0,0,0.35); padding:0.5rem 0.75rem; border-radius:6px; font-family:monospace; border:1px solid rgba(255,255,255,0.06);">
        <strong style="color:var(--danger);">Sample Violations:</strong><br>
        ${r.samples.map((s) => `&bull; Row #${s.row_index}: <code>${s.value !== null ? s.value : '&lt;NULL&gt;'}</code> &rarr; ${s.reason}`).join('<br>')}
      </div>`;
    }

    tr.innerHTML = `
      <td><span class="badge ${badgeClass}"><i data-lucide="${statusIcon}" style="width:13px; height:13px;"></i> ${r.status}</span></td>
      <td><strong>${r.rule_name}</strong></td>
      <td><code>${r.column || '&lt;dataset&gt;'}</code></td>
      <td><span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700;">${r.severity}</span></td>
      <td style="text-align:right;">${r.checked_count.toLocaleString()}</td>
      <td style="text-align:right; color:${r.failed_count > 0 ? 'var(--danger)' : 'inherit'}; font-weight:700;">${r.failed_count.toLocaleString()}</td>
      <td style="text-align:right;">${rateText}</td>
      <td>
        <div>${r.message}</div>
        ${sampleHtml}
      </td>
    `;
    tbody.appendChild(tr);
  });

  refreshIcons();
}

async function loadHistory() {
  const tbody = document.getElementById('historyTableBody');
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/validations/history?limit=15`);
    if (!res.ok) return;
    const history = await res.json();

    if (history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:2rem;">No validation runs recorded yet. Run a validation or sample above!</td></tr>`;
      return;
    }

    tbody.innerHTML = '';
    history.forEach((run) => {
      const tr = document.createElement('tr');
      const scoreColor = run.quality_score >= 90 ? 'var(--success)' : run.quality_score >= 75 ? 'var(--warning)' : 'var(--danger)';
      const dateStr = new Date(run.created_at).toLocaleString();

      tr.innerHTML = `
        <td><strong>#${run.id}</strong></td>
        <td><strong>${run.dataset_name}</strong></td>
        <td><strong style="color:${scoreColor}; font-size:1.05rem;">${run.quality_score.toFixed(1)}%</strong></td>
        <td><span class="badge ${run.passed_gate ? 'badge-pass' : 'badge-fail'}"><i data-lucide="${run.passed_gate ? 'check' : 'x'}" style="width:12px; height:12px;"></i> ${run.passed_gate ? 'PASS' : 'FAIL'}</span></td>
        <td>${run.row_count.toLocaleString()} rows &bull; ${run.duration_ms.toFixed(1)}ms</td>
        <td><span style="color:var(--text-muted); font-size:0.8rem;">${dateStr}</span></td>
      `;
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', () => drillDownRun(run.id));
      tbody.appendChild(tr);
    });

    refreshIcons();
  } catch (err) {
    console.error('Failed to load history', err);
  }
}

async function drillDownRun(runId) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/validations/${runId}`);
    if (res.ok) {
      const summary = await res.json();
      renderResults(summary);
    }
  } catch (err) {
    console.error('Failed to fetch run details', err);
  }
}
