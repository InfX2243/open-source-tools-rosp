// DataDiff Web Dashboard Client Logic

let currentDiffData = null;
let sourceFile = null;
let targetFile = null;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    setupDropZones();
    setupTabs();
    setupFilters();
    setupModal();
    setupRunButton();
    loadHistory();
});

// 1. Setup Drop Zones for Source and Target files
function setupDropZones() {
    const srcZone = document.getElementById('source-drop-zone');
    const srcInput = document.getElementById('source-file-input');
    const tgtZone = document.getElementById('target-drop-zone');
    const tgtInput = document.getElementById('target-file-input');

    srcZone.addEventListener('click', () => srcInput.click());
    srcInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleSourceFile(e.target.files[0]);
    });

    tgtZone.addEventListener('click', () => tgtInput.click());
    tgtInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleTargetFile(e.target.files[0]);
    });

    [srcZone, tgtZone].forEach((zone) => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.borderColor = '#2563eb';
        });
        zone.addEventListener('dragleave', () => {
            zone.style.borderColor = '#cbd5e1';
        });
    });

    srcZone.addEventListener('drop', (e) => {
        e.preventDefault();
        srcZone.style.borderColor = '#cbd5e1';
        if (e.dataTransfer.files.length) handleSourceFile(e.dataTransfer.files[0]);
    });

    tgtZone.addEventListener('drop', (e) => {
        e.preventDefault();
        tgtZone.style.borderColor = '#cbd5e1';
        if (e.dataTransfer.files.length) handleTargetFile(e.dataTransfer.files[0]);
    });
}

function handleSourceFile(file) {
    sourceFile = file;
    document.getElementById('source-file-name').textContent = file.name;
    document.getElementById('source-file-info').classList.remove('hidden');
}

function handleTargetFile(file) {
    targetFile = file;
    document.getElementById('target-file-name').textContent = file.name;
    document.getElementById('target-file-info').classList.remove('hidden');
}

// 2. 1-Click Quick Demos
async function loadSample(sampleId) {
    showLoading(true);
    try {
        const res = await fetch(`/api/v1/compare/sample/${sampleId}`);
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        renderResults(data);
        loadHistory();
    } catch (err) {
        alert('Error running sample demo: ' + err.message);
    } finally {
        showLoading(false);
    }
}

// 3. Setup Run Button
function setupRunButton() {
    const btn = document.getElementById('btn-run-compare');
    btn.addEventListener('click', async () => {
        if (!sourceFile || !targetFile) {
            alert('Please select or drop both Source and Target dataset files.');
            return;
        }

        const formData = new FormData();
        formData.append('source_file', sourceFile);
        formData.append('target_file', targetFile);
        formData.append('key', document.getElementById('key-input').value);
        formData.append('ignore_columns', document.getElementById('ignore-input').value);
        formData.append('numeric_tolerance', document.getElementById('tolerance-input').value || 0.0);
        formData.append('case_sensitive', document.getElementById('case-sensitive').checked);
        formData.append('trim_whitespace', document.getElementById('trim-whitespace').checked);

        showLoading(true);
        try {
            const res = await fetch('/api/v1/compare/upload', {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) {
                const errJson = await res.json();
                throw new Error(errJson.detail || 'Comparison failed');
            }
            const data = await res.json();
            renderResults(data);
            loadHistory();
        } catch (err) {
            alert('Comparison Error: ' + err.message);
        } finally {
            showLoading(false);
        }
    });
}

function showLoading(isLoading) {
    const spinner = document.getElementById('loading-state');
    const results = document.getElementById('results-container');
    if (isLoading) {
        spinner.classList.remove('hidden');
        results.classList.add('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

// 4. Render Results
function renderResults(diff) {
    currentDiffData = diff;
    const r = diff.row_diff;
    const s = diff.schema_diff;
    const pol = diff.policy_report;

    // Metrics
    document.getElementById('metric-row-counts').innerHTML = `${r.source_row_count.toLocaleString()} &rarr; ${r.target_row_count.toLocaleString()}`;
    document.getElementById('metric-added').textContent = `+${r.added_count.toLocaleString()}`;
    document.getElementById('metric-removed').textContent = `-${r.removed_count.toLocaleString()}`;
    document.getElementById('metric-modified').textContent = r.modified_count.toLocaleString();

    const gateVal = document.getElementById('metric-gate');
    const gateBox = document.getElementById('gate-icon-box');
    if (pol.passed) {
        gateVal.textContent = 'PASSED';
        gateVal.className = 'metric-val text-green';
        gateBox.className = 'metric-icon metric-green';
    } else {
        gateVal.textContent = 'FAILED';
        gateVal.className = 'metric-val text-red';
        gateBox.className = 'metric-icon metric-red';
    }

    // Change badges counts
    const totalRowChanges = r.added_count + r.removed_count + r.modified_count;
    document.getElementById('count-row-changes').textContent = totalRowChanges;
    const totalSchemaChanges = s.added_columns.length + s.removed_columns.length + s.type_migrations.length;
    document.getElementById('count-schema-changes').textContent = totalSchemaChanges;

    renderRowDiff(r);
    renderSchemaDiff(s);
    renderStatsDiff(diff.stats_diff);

    document.getElementById('results-container').classList.remove('hidden');
    lucide.createIcons();
}

function renderRowDiff(r, filter = 'all') {
    const tbody = document.getElementById('row-diff-tbody');
    tbody.innerHTML = '';

    const rows = [];

    if (filter === 'all' || filter === 'modified') {
        r.sample_modified.forEach(m => {
            const keyStr = Object.entries(m.key_values).map(([k, v]) => `<strong>${k}:</strong> ${v}`).join(', ');
            const fieldsHtml = m.field_changes.map(fc => `
                <div class="field-diff">
                    <span class="col-tag">${fc.column}</span>:
                    <del class="val-old">${fc.source_value}</del> &rarr;
                    <ins class="val-new">${fc.target_value}</ins>
                </div>
            `).join('');

            rows.push(`
                <tr>
                    <td><span class="badge badge-yellow">MODIFIED</span></td>
                    <td class="key-text">${keyStr}</td>
                    <td>${fieldsHtml}</td>
                </tr>
            `);
        });
    }

    if (filter === 'all' || filter === 'added') {
        r.sample_added.forEach(a => {
            const keyStr = Object.entries(a.key_values).map(([k, v]) => `<strong>${k}:</strong> ${v}`).join(', ');
            const preview = Object.entries(a.row_data).slice(0, 5).map(([k, v]) => `${k}=${v}`).join(' | ');
            rows.push(`
                <tr>
                    <td><span class="badge badge-green">+ ADDED</span></td>
                    <td class="key-text">${keyStr}</td>
                    <td class="code-data">${preview}</td>
                </tr>
            `);
        });
    }

    if (filter === 'all' || filter === 'removed') {
        r.sample_removed.forEach(rem => {
            const keyStr = Object.entries(rem.key_values).map(([k, v]) => `<strong>${k}:</strong> ${v}`).join(', ');
            const preview = Object.entries(rem.row_data).slice(0, 5).map(([k, v]) => `${k}=${v}`).join(' | ');
            rows.push(`
                <tr>
                    <td><span class="badge badge-red">- REMOVED</span></td>
                    <td class="key-text">${keyStr}</td>
                    <td class="code-data">${preview}</td>
                </tr>
            `);
        });
    }

    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: #64748b; padding: 24px;">No row-level differences matching the filter.</td></tr>`;
    } else {
        tbody.innerHTML = rows.join('');
    }
}

function renderSchemaDiff(s) {
    const tbody = document.getElementById('schema-diff-tbody');
    tbody.innerHTML = '';

    const rows = [];
    s.added_columns.forEach(c => {
        rows.push(`<tr><td><span class="badge badge-green">+ ADD</span></td><td><strong>${c.name}</strong></td><td>-</td><td>${c.dtype}</td><td>New column in target</td></tr>`);
    });
    s.removed_columns.forEach(c => {
        rows.push(`<tr><td><span class="badge badge-red">- DEL</span></td><td><strong>${c.name}</strong></td><td>${c.dtype}</td><td>-</td><td>Column deleted from target</td></tr>`);
    });
    s.type_migrations.forEach(mig => {
        rows.push(`<tr><td><span class="badge badge-yellow">~ TYPE</span></td><td><strong>${mig.column}</strong></td><td>${mig.source_dtype}</td><td>${mig.target_dtype}</td><td>Data type migration</td></tr>`);
    });

    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #16a34a; padding: 24px;">✓ Schemas are identical (0 column differences).</td></tr>`;
    } else {
        tbody.innerHTML = rows.join('');
    }
}

function renderStatsDiff(stats) {
    const tbody = document.getElementById('stats-diff-tbody');
    const alertsBox = document.getElementById('drift-alerts-container');
    tbody.innerHTML = '';
    alertsBox.innerHTML = '';

    if (stats.drift_warnings && stats.drift_warnings.length > 0) {
        alertsBox.innerHTML = `
            <div style="background: #fef9c3; border: 1px solid #fde047; padding: 12px 16px; border-radius: 8px; margin: 16px 20px; color: #854d0e;">
                <strong>Statistical Drift Warnings:</strong>
                <ul style="margin-left: 20px; margin-top: 4px;">
                    ${stats.drift_warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    const rows = Object.entries(stats.columns).map(([col, colStat]) => {
        const delta = colStat.target_null_rate_pct - colStat.source_null_rate_pct;
        const deltaColor = delta > 0 ? 'text-red' : 'text-green';
        const deltaSign = delta > 0 ? `+${delta.toFixed(1)}%` : `${delta.toFixed(1)}%`;
        return `
            <tr>
                <td><strong>${col}</strong></td>
                <td>${colStat.source_null_rate_pct.toFixed(1)}%</td>
                <td>${colStat.target_null_rate_pct.toFixed(1)}%</td>
                <td class="${deltaColor}">${deltaSign}</td>
                <td>${colStat.source_distinct_count.toLocaleString()}</td>
                <td>${colStat.target_distinct_count.toLocaleString()}</td>
            </tr>
        `;
    });

    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #64748b; padding: 24px;">No column statistics available.</td></tr>`;
    } else {
        tbody.innerHTML = rows.join('');
    }
}

// 5. History Loader
async function loadHistory() {
    try {
        const res = await fetch('/api/v1/history?limit=15');
        if (!res.ok) return;
        const historyList = await res.json();
        const tbody = document.getElementById('history-tbody');
        tbody.innerHTML = historyList.map(h => `
            <tr>
                <td><strong>#${h.id}</strong></td>
                <td>${h.source_name}</td>
                <td>${h.target_name}</td>
                <td><span class="badge ${h.passed ? 'badge-green' : 'badge-red'}">${h.passed ? 'PASSED' : 'FAILED'}</span></td>
                <td>${h.source_rows} &rarr; ${h.target_rows}</td>
                <td class="text-green">+${h.added_rows}</td>
                <td class="text-red">-${h.removed_rows}</td>
                <td class="text-yellow">${h.modified_rows}</td>
                <td>${h.execution_time_ms.toFixed(1)}ms</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Failed to load history', e);
    }
}

// 6. Tabs & Filter Interactions
function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');
            document.getElementById(target).classList.add('active');
            lucide.createIcons();
        });
    });
}

function setupFilters() {
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            if (currentDiffData) {
                renderRowDiff(currentDiffData.row_diff, chip.getAttribute('data-filter'));
            }
        });
    });
}

// 7. Modal Interaction
function setupModal() {
    const modal = document.getElementById('guide-modal');
    const btnOpen = document.getElementById('btn-guide-modal');
    const btnClose = document.getElementById('btn-close-modal');
    const overlay = document.getElementById('modal-overlay');

    btnOpen.addEventListener('click', () => modal.classList.remove('hidden'));
    btnClose.addEventListener('click', () => modal.classList.add('hidden'));
    overlay.addEventListener('click', () => modal.classList.add('hidden'));
}
