"""Self-contained HTML report generator for ContainerSec."""

from __future__ import annotations

import html
from containersec.core.models import ScanResult, Severity


def to_html_report(result: ScanResult) -> str:
    """Generate a clean, standalone HTML report."""
    findings_html = ""
    for f in result.findings:
        sev_class = f.severity.value.lower()
        line_str = f"Line {f.line_number}: " if f.line_number else ""
        findings_html += f"""
        <div class="card finding {sev_class}">
          <div class="finding-header">
            <span class="badge badge-{sev_class}">{f.severity.value}</span>
            <span class="rule-id">{html.escape(f.rule_id)}</span>
            <span class="title">{html.escape(f.title)}</span>
          </div>
          <p class="desc">{html.escape(f.description)}</p>
          {f'<div class="code-snippet"><code>{line_str}{html.escape(f.line_content or "")}</code></div>' if f.line_content else ''}
          {f'<div class="fix-box"><strong>Remediation:</strong> {html.escape(f.fix_suggestion)}</div>' if f.fix_suggestion else ''}
        </div>
        """

    if not result.findings:
        findings_html = """
        <div class="card empty-state">
          <h3>✅ Clean Dockerfile!</h3>
          <p>No CIS Benchmark violations or security misconfigurations were detected.</p>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ContainerSec Report — {html.escape(result.file_path)}</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --text-dim: #94a3b8;
      --border: #334155;
      --critical: #ef4444;
      --high: #f97316;
      --medium: #eab308;
      --low: #3b82f6;
      --success: #10b981;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 30px;
    }}
    .container {{ max-width: 1000px; margin: 0 auto; }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 20px;
      margin-bottom: 25px;
    }}
    .header h1 {{ margin: 0; font-size: 24px; color: #38bdf8; }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      text-align: center;
    }}
    .stat-val {{ font-size: 28px; font-weight: 700; margin-top: 5px; }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 15px;
    }}
    .finding {{ border-left: 5px solid #64748b; }}
    .finding.critical {{ border-left-color: var(--critical); }}
    .finding.high {{ border-left-color: var(--high); }}
    .finding.medium {{ border-left-color: var(--medium); }}
    .finding.low {{ border-left-color: var(--low); }}
    .finding-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
    .badge {{
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .badge-critical {{ background: var(--critical); color: white; }}
    .badge-high {{ background: var(--high); color: white; }}
    .badge-medium {{ background: var(--medium); color: black; }}
    .badge-low {{ background: var(--low); color: white; }}
    .badge-info {{ background: #64748b; color: white; }}
    .rule-id {{ color: #38bdf8; font-family: monospace; font-weight: 600; }}
    .title {{ font-weight: 600; }}
    .desc {{ color: var(--text-dim); margin: 6px 0; font-size: 14px; }}
    .code-snippet {{
      background: #090d16;
      padding: 10px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 13px;
      margin: 10px 0;
      overflow-x: auto;
    }}
    .fix-box {{
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      padding: 10px;
      border-radius: 6px;
      font-size: 13px;
      margin-top: 8px;
    }}
    .empty-state {{ text-align: center; padding: 40px; color: var(--success); }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>🛡️ ContainerSec Scan Report</h1>
        <div style="color: var(--text-dim); margin-top: 4px; font-size: 13px;">Target: {html.escape(result.file_path)} | Time: {result.execution_time_ms}ms</div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 32px; font-weight: 800; color: #38bdf8;">{result.score.points}/100</div>
        <div style="color: var(--text-dim); font-size: 12px;">Grade: {result.score.grade.value}</div>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div style="color: var(--text-dim); font-size: 12px;">Critical</div>
        <div class="stat-val" style="color: var(--critical);">{result.critical_count}</div>
      </div>
      <div class="stat-card">
        <div style="color: var(--text-dim); font-size: 12px;">High</div>
        <div class="stat-val" style="color: var(--high);">{result.high_count}</div>
      </div>
      <div class="stat-card">
        <div style="color: var(--text-dim); font-size: 12px;">Medium</div>
        <div class="stat-val" style="color: var(--medium);">{result.medium_count}</div>
      </div>
      <div class="stat-card">
        <div style="color: var(--text-dim); font-size: 12px;">Low / Info</div>
        <div class="stat-val" style="color: var(--low);">{result.low_count + result.info_count}</div>
      </div>
      <div class="stat-card">
        <div style="color: var(--text-dim); font-size: 12px;">Passed Rules</div>
        <div class="stat-val" style="color: var(--success);">{len(result.passed_rules)}</div>
      </div>
    </div>

    <h2>Findings ({len(result.findings)})</h2>
    {findings_html}
  </div>
</body>
</html>
"""
    return html_content
