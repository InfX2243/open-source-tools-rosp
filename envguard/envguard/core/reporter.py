"""
Rich terminal formatting, JSON serializing, and HTML reporting for EnvGuard.
"""

import sys
import json
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from envguard.core.models import (
    CheckResult,
    DiffResult,
    DiffType,
    ScanCodebaseResult,
    SecretFinding,
    Severity,
)

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(safe_box=True)

SEVERITY_COLORS = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "cyan",
    Severity.INFO: "blue",
}


def render_check_report(result: CheckResult) -> None:
    """Print an aesthetic, readable Rich terminal summary of validation results."""
    title = f"EnvGuard Audit: {result.env_path}"
    console.print(Panel(title, style="bold cyan", expand=False))

    if not result.issues:
        console.print(
            Panel(
                "[bold green][OK] All environment variables passed validation! Zero drift detected.[/bold green]",
                border_style="green",
            )
        )
        return

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Severity", min_width=10, no_wrap=True)
    table.add_column("Type", min_width=16, no_wrap=True)
    table.add_column("Variable", min_width=18)
    table.add_column("Line", width=6, justify="right")
    table.add_column("Details", style="dim")

    for issue in result.issues:
        color = SEVERITY_COLORS.get(issue.severity, "white")
        table.add_row(
            f"[{color}]{issue.severity.value}[/{color}]",
            issue.issue_type.value,
            f"[bold]{issue.key}[/bold]",
            str(issue.line_number or "-"),
            issue.message,
        )

    console.print(table)

    # Summary box
    summary_text = (
        f"Checked: [bold]{result.total_checked}[/bold] variables | "
        f"Critical: [bold red]{result.critical_count}[/bold red] | "
        f"High: [bold red]{result.high_count}[/bold red] | "
        f"Medium: [bold yellow]{result.medium_count}[/bold yellow] | "
        f"Low: [bold cyan]{result.low_count}[/bold cyan]"
    )
    status_style = "red" if not result.passed else "green"
    status_label = "FAILED" if not result.passed else "PASSED WITH WARNINGS"
    console.print(Panel(f"[{status_style}]Status: {status_label}[/{status_style}] | {summary_text}", border_style=status_style))


def render_diff_report(diff: DiffResult) -> None:
    """Print safe redacted environment diff table."""
    console.print(Panel(f"EnvGuard Redacted Diff\n[dim]{diff.file1_path} -> {diff.file2_path}[/dim]", style="bold blue", expand=False))

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Status", min_width=8, no_wrap=True)
    table.add_column("Variable Key", min_width=15)
    table.add_column("File 1 (Len/Ent/Preview)", min_width=20)
    table.add_column("File 2 (Len/Ent/Preview)", min_width=20)

    for f in diff.fields:
        if f.diff_type == DiffType.MATCH:
            status = "[green]MATCH[/green]"
        elif f.diff_type == DiffType.ADDED:
            status = "[bold green]+ ADDED[/bold green]"
        elif f.diff_type == DiffType.REMOVED:
            status = "[bold red]- REMOVED[/bold red]"
        else:
            status = "[yellow]MODIFIED[/yellow]"

        col1 = f"{f.file1_len or 0}b | ent:{f.file1_entropy or 0.0} | [dim]{f.masked_preview1 or '-'}[/dim]" if f.file1_present else "[dim]<none>[/dim]"
        col2 = f"{f.file2_len or 0}b | ent:{f.file2_entropy or 0.0} | [dim]{f.masked_preview2 or '-'}[/dim]" if f.file2_present else "[dim]<none>[/dim]"

        table.add_row(status, f"[bold]{f.key}[/bold]", col1, col2)

    console.print(table)
    console.print(
        f"[dim]Summary: Total {diff.total_keys} keys | {diff.matched} matched | {diff.modified} modified | "
        f"{diff.added} added | {diff.removed} removed[/dim]\n"
    )


def render_scan_report(scan: ScanCodebaseResult) -> None:
    """Print variables discovered across the codebase."""
    console.print(Panel("EnvGuard Codebase Scan", style="bold magenta", expand=False))

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Discovered Key", width=25)
    table.add_column("Occurrences", width=14, justify="right")
    table.add_column("First Reference (Path:Line)", style="dim")

    for key, refs in sorted(scan.variables.items()):
        first = refs[0]
        table.add_row(
            f"[bold green]{key}[/bold green]",
            str(len(refs)),
            f"{first.file_path}:{first.line_number} ({first.language})",
        )

    console.print(table)
    console.print(f"[dim]Scanned {scan.files_scanned} files. Found {len(scan.variables)} unique env variables ({scan.total_references} usages).[/dim]\n")


def render_secrets_report(findings: List[SecretFinding]) -> None:
    """Print detected secret leaks."""
    if not findings:
        console.print(Panel("[bold green][OK] No secret leaks or unmasked credentials detected.[/bold green]", border_style="green"))
        return

    console.print(Panel(f"[bold red][ALERT] DETECTED {len(findings)} UNMASKED SECRETS[/bold red]", border_style="red", expand=False))
    table = Table(show_header=True, header_style="bold red", expand=True)
    table.add_column("Severity", width=12)
    table.add_column("Secret Type", width=25)
    table.add_column("File:Line", width=30)
    table.add_column("Masked Preview", width=20)

    for f in findings:
        color = SEVERITY_COLORS.get(f.severity, "red")
        loc = f"{f.file_path}:{f.line_number}" if f.file_path else f"Line {f.line_number}"
        table.add_row(
            f"[{color}]{f.severity.value}[/{color}]",
            f.secret_type,
            loc,
            f.masked_preview,
        )

    console.print(table)


def export_json(data: dict) -> str:
    """Serialize model or dictionary to formatted JSON."""
    return json.dumps(data, indent=2)


def generate_html_report(result: CheckResult) -> str:
    """Generate self-contained HTML report."""
    issues_html = ""
    for i in result.issues:
        color = "#ef4444" if i.severity in (Severity.CRITICAL, Severity.HIGH) else "#f59e0b"
        issues_html += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 10px; color: {color}; font-weight: bold;">{i.severity.value}</td>
            <td style="padding: 10px;"><code>{i.issue_type.value}</code></td>
            <td style="padding: 10px; font-weight: bold; color: #38bdf8;">{i.key}</td>
            <td style="padding: 10px;">{i.line_number or '-'}</td>
            <td style="padding: 10px; color: #cbd5e1;">{i.message}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EnvGuard Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; }}
        .card {{ background: #1e293b; border-radius: 10px; padding: 24px; max-width: 1000px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
        h1 {{ margin-top: 0; color: #38bdf8; display: flex; align-items: center; gap: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ text-align: left; padding: 12px; background: #334155; color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
        code {{ background: #090d16; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>EnvGuard Audit Report</h1>
        <p><strong>Environment File:</strong> <code>{result.env_path}</code></p>
        <p><strong>Status:</strong> <span style="color: {'#22c55e' if result.passed else '#ef4444'}; font-weight: bold;">{'PASSED' if result.passed else 'FAILED'}</span></p>
        <table>
            <thead>
                <tr><th>Severity</th><th>Type</th><th>Key</th><th>Line</th><th>Message</th></tr>
            </thead>
            <tbody>{issues_html or '<tr><td colspan="5" style="padding: 20px; text-align: center; color: #22c55e;">No issues found. Everything is clean!</td></tr>'}</tbody>
        </table>
    </div>
</body>
</html>"""
