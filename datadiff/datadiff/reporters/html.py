"""Standalone HTML interactive visual diff reporter."""

from __future__ import annotations

import json
from pathlib import Path
from datadiff.core.models import DiffSummary
from datadiff.reporters.base import BaseReporter


class HTMLReporter(BaseReporter):
    """Generates an interactive, standalone HTML data comparison report."""

    def render(self, diff: DiffSummary) -> str:
        r = diff.row_diff
        s = diff.schema_diff
        pol = diff.policy_report

        diff_json = diff.model_dump_json()

        # Build rows html
        mod_rows_html = ""
        for m in r.sample_modified:
            key_str = ", ".join(f"<strong>{k}:</strong> {v}" for k, v in m.key_values.items())
            fields_html = "".join(
                f"<div class='field-diff'><span class='col-name'>{fc.column}</span>: "
                f"<del class='old-val'>{fc.source_value}</del> &rarr; "
                f"<ins class='new-val'>{fc.target_value}</ins></div>"
                for fc in m.field_changes
            )
            mod_rows_html += f"""
            <tr class="mod-row">
                <td><span class="badge badge-yellow">MODIFIED</span></td>
                <td>{key_str}</td>
                <td>{fields_html}</td>
            </tr>
            """

        added_rows_html = ""
        for a in r.sample_added:
            key_str = ", ".join(f"<strong>{k}:</strong> {v}" for k, v in a.key_values.items())
            data_preview = ", ".join(f"{k}={v}" for k, v in list(a.row_data.items())[:5])
            added_rows_html += f"""
            <tr class="add-row">
                <td><span class="badge badge-green">+ ADDED</span></td>
                <td>{key_str}</td>
                <td class="code-preview">{data_preview}</td>
            </tr>
            """

        removed_rows_html = ""
        for rem in r.sample_removed:
            key_str = ", ".join(f"<strong>{k}:</strong> {v}" for k, v in rem.key_values.items())
            data_preview = ", ".join(f"{k}={v}" for k, v in list(rem.row_data.items())[:5])
            removed_rows_html += f"""
            <tr class="rem-row">
                <td><span class="badge badge-red">- REMOVED</span></td>
                <td>{key_str}</td>
                <td class="code-preview">{data_preview}</td>
            </tr>
            """

        schema_html = ""
        if not s.has_changes:
            schema_html = "<div class='alert alert-success'>No schema changes detected between source and target.</div>"
        else:
            schema_rows = ""
            for c in s.added_columns:
                schema_rows += f"<tr><td><span class='badge badge-green'>+ ADD</span></td><td><strong>{c.name}</strong></td><td>-</td><td>{c.dtype}</td></tr>"
            for c in s.removed_columns:
                schema_rows += f"<tr><td><span class='badge badge-red'>- DEL</span></td><td><strong>{c.name}</strong></td><td>{c.dtype}</td><td>-</td></tr>"
            for mig in s.type_migrations:
                schema_rows += f"<tr><td><span class='badge badge-yellow'>~ TYPE</span></td><td><strong>{mig.column}</strong></td><td>{mig.source_dtype}</td><td>{mig.target_dtype}</td></tr>"
            schema_html = f"""
            <table class="data-table">
                <thead>
                    <tr><th>Action</th><th>Column</th><th>Source Type</th><th>Target Type</th></tr>
                </thead>
                <tbody>{schema_rows}</tbody>
            </table>
            """

        gate_status_class = "gate-pass" if pol.passed else "gate-fail"
        gate_text = "PASSED" if pol.passed else "FAILED"

        failures_html = ""
        if not pol.passed:
            fail_items = "".join(f"<li>{f}</li>" for f in pol.failures)
            failures_html = f"<div class='alert alert-danger'><strong>Quality Gate Violations:</strong><ul>{fail_items}</ul></div>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataDiff Report: {diff.source_name} vs {diff.target_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --color-blue: #2563eb;
            --color-green: #16a34a;
            --color-red: #dc2626;
            --color-yellow: #ca8a04;
            --font-sans: 'Plus Jakarta Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-primary);
            color: var(--text-main);
            font-family: var(--font-sans);
            padding: 32px 24px;
            line-height: 1.5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .header h1 {{ font-size: 22px; font-weight: 800; color: #0f172a; }}
        .header .meta {{ color: var(--text-muted); font-size: 14px; margin-top: 4px; }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-green {{ background: #dcfce7; color: #15803d; }}
        .badge-red {{ background: #fee2e2; color: #b91c1c; }}
        .badge-yellow {{ background: #fef9c3; color: #a16207; }}
        .gate-pass {{ background: #dcfce7; color: #15803d; padding: 8px 16px; border-radius: 8px; font-weight: 800; }}
        .gate-fail {{ background: #fee2e2; color: #b91c1c; padding: 8px 16px; border-radius: 8px; font-weight: 800; }}
        
        .grid-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .stat-label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }}
        .stat-val {{ font-size: 28px; font-weight: 800; margin-top: 6px; }}
        .stat-val.green {{ color: var(--color-green); }}
        .stat-val.red {{ color: var(--color-red); }}
        .stat-val.yellow {{ color: var(--color-yellow); }}
        .stat-val.blue {{ color: var(--color-blue); }}
        
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .card-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: left;
        }}
        .data-table th, .data-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}
        .data-table th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
        .field-diff {{ margin: 4px 0; font-family: var(--font-mono); font-size: 13px; }}
        .col-name {{ font-weight: 600; color: #475569; }}
        del.old-val {{ background: #fee2e2; color: #991b1b; padding: 2px 4px; border-radius: 4px; text-decoration: line-through; }}
        ins.new-val {{ background: #dcfce7; color: #166534; padding: 2px 4px; border-radius: 4px; text-decoration: none; font-weight: 600; }}
        .code-preview {{ font-family: var(--font-mono); font-size: 13px; color: #334155; }}
        .alert {{ padding: 14px 18px; border-radius: 8px; margin-bottom: 16px; }}
        .alert-success {{ background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }}
        .alert-danger {{ background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }}
        ul {{ margin-left: 20px; margin-top: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>DataDiff Semantic Report</h1>
                <div class="meta">Comparing <strong>{diff.source_name}</strong> &rarr; <strong>{diff.target_name}</strong> | Time: {diff.execution_time_ms:.1f}ms</div>
            </div>
            <div class="{gate_status_class}">Gate: {gate_text}</div>
        </div>

        {failures_html}

        <div class="grid-stats">
            <div class="stat-card">
                <div class="stat-label">Source Rows</div>
                <div class="stat-val blue">{r.source_row_count:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Target Rows</div>
                <div class="stat-val blue">{r.target_row_count:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Added Rows</div>
                <div class="stat-val green">+{r.added_count:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Removed Rows</div>
                <div class="stat-val red">-{r.removed_count:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Modified Rows</div>
                <div class="stat-val yellow">{r.modified_count:,}</div>
            </div>
        </div>

        <div class="card">
            <h2 class="card-title">Schema Differences</h2>
            {schema_html}
        </div>

        <div class="card">
            <h2 class="card-title">Row-Level Differences</h2>
            <table class="data-table">
                <thead>
                    <tr><th style="width: 120px;">Type</th><th style="width: 200px;">Key</th><th>Details / Values</th></tr>
                </thead>
                <tbody>
                    {mod_rows_html}
                    {added_rows_html}
                    {removed_rows_html}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

    def write_to_file(self, diff: DiffSummary, path: Path | str) -> None:
        """Save HTML report to a file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(diff), encoding="utf-8")
