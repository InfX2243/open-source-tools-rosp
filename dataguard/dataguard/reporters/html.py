"""Interactive standalone HTML report generator for DataGuard."""

import json
from datetime import datetime
from typing import Any
from dataguard.core.models import ValidationSummary, RuleStatus, Severity
from dataguard.reporters.base import BaseReporter


class HTMLReporter(BaseReporter):
    """Renders a self-contained, interactive, beautiful HTML dashboard report."""

    def render(self, summary: ValidationSummary) -> str:
        summary_dict = json.loads(summary.model_dump_json())
        score = summary.quality_score
        score_color = "#10b981" if score >= 90 else "#f59e0b" if score >= 75 else "#ef4444"
        gate_status = "PASSED" if summary.passed_gate else "FAILED"
        gate_color = "#10b981" if summary.passed_gate else "#ef4444"

        # Calculate SVG stroke offset for quality ring (circumference = 2 * pi * 54 ~= 339.29)
        dash_offset = round(339.29 * (1.0 - (score / 100.0)), 2)

        results_json = json.dumps(summary_dict.get("results", []), indent=2)
        profile_json = json.dumps(summary_dict.get("profile", {}), indent=2)
        anomalies_json = json.dumps(summary_dict.get("anomalies", {}), indent=2)

        html_template = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DataGuard Report - {summary.dataset_name}</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --accent: #2563eb;
      --accent-glow: rgba(37, 99, 235, 0.1);
      --pass: #16a34a;
      --fail: #dc2626;
      --warn: #d97706;
      --err: #e11d48;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }}
    body {{ background-color: var(--bg); color: var(--text-main); line-height: 1.5; min-height: 100vh; padding: 2rem 1rem; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }}
    .logo-group {{ display: flex; align-items: center; gap: 0.75rem; }}
    .logo-icon {{ font-size: 2rem; }}
    .logo-title {{ font-size: 1.5rem; font-weight: 700; color: #0f172a; }}
    .badge {{ display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }}
    .badge-pass {{ background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }}
    .badge-fail {{ background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }}
    .badge-warn {{ background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }}

    .grid-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 1rem; padding: 1.25rem; backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }}
    .card-title {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
    .card-value {{ font-size: 1.75rem; font-weight: 700; }}
    
    .score-container {{ display: flex; align-items: center; gap: 1.5rem; }}
    .ring-svg {{ width: 90px; height: 90px; transform: rotate(-90deg); }}
    .ring-bg {{ fill: none; stroke: rgba(255,255,255,0.1); stroke-width: 10; }}
    .ring-val {{ fill: none; stroke: {score_color}; stroke-width: 10; stroke-dasharray: 339.29; stroke-dashoffset: {dash_offset}; stroke-linecap: round; transition: stroke-dashoffset 1s ease; }}

    .tabs {{ display: flex; gap: 0.5rem; border-bottom: 1px solid var(--card-border); margin-bottom: 1.5rem; }}
    .tab-btn {{ background: none; border: none; padding: 0.75rem 1.25rem; color: var(--text-muted); font-size: 0.95rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; }}
    .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
    .tab-btn:hover {{ color: var(--text-main); }}

    .filter-bar {{ display: flex; gap: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap; align-items: center; }}
    .filter-btn {{ background: rgba(255, 255, 255, 0.05); border: 1px solid var(--card-border); color: var(--text-muted); padding: 0.4rem 0.85rem; border-radius: 0.5rem; font-size: 0.85rem; cursor: pointer; }}
    .filter-btn.active {{ background: var(--accent-glow); color: var(--accent); border-color: var(--accent); }}
    .search-input {{ flex: 1; min-width: 200px; background: rgba(0,0,0,0.2); border: 1px solid var(--card-border); border-radius: 0.5rem; padding: 0.4rem 0.85rem; color: #fff; font-size: 0.85rem; }}

    table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    th {{ padding: 0.85rem 1rem; color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; border-bottom: 1px solid var(--card-border); font-weight: 600; }}
    td {{ padding: 0.9rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.04); font-size: 0.9rem; }}
    tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}

    .sample-box {{ margin-top: 0.5rem; padding: 0.6rem; background: rgba(0,0,0,0.3); border-radius: 0.4rem; font-size: 0.8rem; font-family: monospace; }}
    .code-pill {{ background: rgba(255, 255, 255, 0.1); padding: 0.15rem 0.4rem; border-radius: 0.25rem; font-family: monospace; font-size: 0.85rem; }}
    
    .profile-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }}
    .col-card {{ background: rgba(0,0,0,0.2); border: 1px solid var(--card-border); border-radius: 0.75rem; padding: 1rem; }}
    .col-header {{ display: flex; justify-content: space-between; font-weight: 600; margin-bottom: 0.5rem; }}
    .col-meta {{ font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }}
    .bar-bg {{ background: rgba(255,255,255,0.08); height: 6px; border-radius: 3px; overflow: hidden; margin-top: 0.25rem; }}
    .bar-fill {{ height: 100%; border-radius: 3px; }}

    .footer {{ margin-top: 3rem; text-align: center; color: var(--text-muted); font-size: 0.8rem; border-top: 1px solid var(--card-border); padding-top: 1.5rem; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-group">
        <span class="logo-icon">🛡️</span>
        <div>
          <h1 class="logo-title">DataGuard Report</h1>
          <p style="font-size:0.85rem; color:var(--text-muted);">{summary.dataset_name} &bull; {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
      </div>
      <div>
        <span class="badge" style="background: {gate_color}22; color: {gate_color}; border: 1px solid {gate_color}44;">
          Gate: {gate_status}
        </span>
      </div>
    </header>

    <div class="grid-stats">
      <div class="card score-container">
        <svg class="ring-svg" viewBox="0 0 120 120">
          <circle class="ring-bg" cx="60" cy="60" r="54"></circle>
          <circle class="ring-val" cx="60" cy="60" r="54"></circle>
        </svg>
        <div>
          <div class="card-title">Quality Score</div>
          <div class="card-value" style="color:{score_color}">{score:.1f}%</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">{summary.gate_reason or 'Evaluated'}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Dataset Scale</div>
        <div class="card-value">{summary.profile.row_count if summary.profile else 0:,} <span style="font-size:0.9rem; font-weight:normal; color:var(--text-muted);">rows</span></div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.35rem;">
          {summary.profile.column_count if summary.profile else 0} columns &bull; {summary.profile.estimated_memory_kb if summary.profile else 0:.1f} KB
        </div>
      </div>

      <div class="card">
        <div class="card-title">Rule Execution</div>
        <div class="card-value">{summary.passed_rules} <span style="font-size:1rem; color:var(--pass);">passed</span> / {summary.total_rules}</div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.35rem;">
          {summary.failed_rules} failed &bull; {summary.warned_rules} warnings &bull; {summary.total_duration_ms:.1f}ms
        </div>
      </div>
    </div>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('rules')">Validation Rules ({summary.total_rules})</button>
      <button class="tab-btn" onclick="switchTab('profiling')">Data Profiling</button>
      <button class="tab-btn" onclick="switchTab('raw')">Raw JSON</button>
    </div>

    <!-- Rules Tab Content -->
    <div id="tab-rules">
      <div class="filter-bar">
        <button class="filter-btn active" onclick="filterRules('all')">All ({summary.total_rules})</button>
        <button class="filter-btn" onclick="filterRules('fail')">Failed ({summary.failed_rules})</button>
        <button class="filter-btn" onclick="filterRules('warn')">Warnings ({summary.warned_rules})</button>
        <button class="filter-btn" onclick="filterRules('pass')">Passed ({summary.passed_rules})</button>
        <input type="text" id="ruleSearch" class="search-input" placeholder="Search rules or columns..." onkeyup="filterRulesText()" />
      </div>

      <div class="card" style="padding:0; overflow:hidden;">
        <table>
          <thead>
            <tr>
              <th style="width:90px;">Status</th>
              <th>Rule</th>
              <th>Column</th>
              <th>Severity</th>
              <th style="text-align:right;">Checked</th>
              <th style="text-align:right;">Failed</th>
              <th style="text-align:right;">Failure Rate</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody id="rulesTableBody"></tbody>
        </table>
      </div>
    </div>

    <!-- Profiling Tab Content -->
    <div id="tab-profiling" style="display:none;">
      <div class="profile-grid" id="profilingGrid"></div>
    </div>

    <!-- Raw JSON Tab Content -->
    <div id="tab-raw" style="display:none;">
      <div class="card">
        <div style="display:flex; justify-content:flex-end; margin-bottom:0.75rem;">
          <button class="filter-btn" onclick="downloadJSON()">📥 Download JSON Report</button>
        </div>
        <pre style="background:rgba(0,0,0,0.4); padding:1rem; border-radius:0.5rem; overflow-x:auto; font-size:0.85rem;"><code id="rawJsonBlock"></code></pre>
      </div>
    </div>

    <div class="footer">
      Generated with <strong>DataGuard</strong> &bull; Open-Source Data Quality & Validation Engine &bull; <a href="https://github.com" style="color:var(--accent); text-decoration:none;">Documentation</a>
    </div>
  </div>

  <script>
    const DATA = {summary.model_dump_json()};
    let currentFilter = 'all';

    function renderRulesTable() {{
      const tbody = document.getElementById('rulesTableBody');
      tbody.innerHTML = '';
      const searchTerm = (document.getElementById('ruleSearch')?.value || '').toLowerCase();

      DATA.results.forEach((r, idx) => {{
        if (currentFilter !== 'all' && r.status !== currentFilter) return;
        if (searchTerm) {{
          const target = (r.rule_name + ' ' + (r.column || '') + ' ' + r.message).toLowerCase();
          if (!target.includes(searchTerm)) return;
        }}

        let badgeClass = r.status === 'pass' ? 'badge-pass' : (r.status === 'fail' ? 'badge-fail' : 'badge-warn');
        let colDisplay = r.column ? `<span class="code-pill">${{r.column}}</span>` : '<span style="color:var(--text-muted);">&lt;dataset&gt;</span>';
        let failRate = r.failed_count > 0 ? (r.failure_rate * 100).toFixed(1) + '%' : '0.0%';

        let samplesHtml = '';
        if (r.samples && r.samples.length > 0) {{
          samplesHtml = `<div class="sample-box"><strong>Sample Failures:</strong><ul style="margin-left:1.2rem; margin-top:0.25rem;">` +
            r.samples.slice(0, 3).map(s => `<li>Row #${{s.row_index}}: ${{s.value !== null ? s.value : '&lt;NULL&gt;'}} &mdash; ${{s.reason}}</li>`).join('') +
            `</ul></div>`;
        }}

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><span class="badge ${{badgeClass}}">${{r.status}}</span></td>
          <td><strong>${{r.rule_name}}</strong></td>
          <td>${{colDisplay}}</td>
          <td><span style="font-size:0.8rem; text-transform:uppercase; color:var(--text-muted);">${{r.severity}}</span></td>
          <td style="text-align:right;">${{r.checked_count.toLocaleString()}}</td>
          <td style="text-align:right; font-weight:600; color:${{r.failed_count > 0 ? 'var(--fail)' : 'inherit'}}">${{r.failed_count.toLocaleString()}}</td>
          <td style="text-align:right;">${{failRate}}</td>
          <td>
            <div>${{r.message}}</div>
            ${{samplesHtml}}
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderProfiling() {{
      const grid = document.getElementById('profilingGrid');
      grid.innerHTML = '';
      if (!DATA.profile || !DATA.profile.columns) return;

      Object.entries(DATA.profile.columns).forEach(([colName, p]) => {{
        const colDiv = document.createElement('div');
        colDiv.className = 'col-card';
        colDiv.innerHTML = `
          <div class="col-header">
            <span>${{colName}}</span>
            <span class="code-pill">${{p.detected_type}}</span>
          </div>
          <div class="col-meta">
            <div>Nulls: <strong>${{p.null_count.toLocaleString()}}</strong> (${{p.null_percentage}}%)</div>
            <div class="bar-bg"><div class="bar-fill" style="width:${{p.null_percentage}}%; background:var(--fail);"></div></div>
          </div>
          <div class="col-meta" style="margin-top:0.5rem;">
            <div>Distinct: <strong>${{p.distinct_count.toLocaleString()}}</strong> (${{p.unique_percentage}}%)</div>
            <div class="bar-bg"><div class="bar-fill" style="width:${{p.unique_percentage}}%; background:var(--accent);"></div></div>
          </div>
          ${{p.min_value !== null ? `<div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.5rem;">Range: [${{p.min_value}}, ${{p.max_value}}] &bull; Mean: ${{p.mean_value}}</div>` : ''}}
        `;
        grid.appendChild(colDiv);
      }});
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById('tab-rules').style.display = tabId === 'rules' ? 'block' : 'none';
      document.getElementById('tab-profiling').style.display = tabId === 'profiling' ? 'block' : 'none';
      document.getElementById('tab-raw').style.display = tabId === 'raw' ? 'block' : 'none';
    }}

    function filterRules(status) {{
      currentFilter = status;
      document.querySelectorAll('.filter-bar .filter-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      renderRulesTable();
    }}

    function filterRulesText() {{
      renderRulesTable();
    }}

    function downloadJSON() {{
      const blob = new Blob([JSON.stringify(DATA, null, 2)], {{ type: 'application/json' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dataguard_${{DATA.dataset_name}}_${{Date.now()}}.json`;
      a.click();
    }}

    document.getElementById('rawJsonBlock').textContent = JSON.stringify(DATA, null, 2);
    renderRulesTable();
    renderProfiling();
  </script>
</body>
</html>
"""
        return html_template
