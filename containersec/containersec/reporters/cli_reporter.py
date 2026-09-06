"""Rich CLI console reporter for ContainerSec."""

from __future__ import annotations

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from containersec.core.models import PolicyReport, ScanResult, ScoreGrade, Severity

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(safe_box=True)


def print_scan_report(result: ScanResult, policy_report: PolicyReport | None = None) -> None:
    """Print an attractive, color-coded security report to the terminal."""
    # Header Banner
    console.print()
    console.rule("[bold cyan]ContainerSec -- Dockerfile Security Scan[/bold cyan]")
    console.print(f"[dim]File:[/dim] [bold]{result.file_path}[/bold] | [dim]Lines:[/dim] {result.total_lines} | [dim]Instructions:[/dim] {result.total_instructions} | [dim]Time:[/dim] {result.execution_time_ms:.1f}ms")
    console.print()

    # Findings Table
    if not result.findings:
        console.print(
            Panel(
                "[bold green][PASS] No security issues found![/bold green]\nYour Dockerfile complies with all CIS Docker Benchmark checks.",
                title="[bold green]Scan Passed[/bold green]",
                border_style="green",
            )
        )
    else:
        table = Table(
            title=f"Security Findings ({len(result.findings)} detected)",
            box=box.ROUNDED,
            header_style="bold magenta",
            show_lines=True,
        )
        table.add_column("Severity", justify="center", width=12)
        table.add_column("Rule ID", style="cyan", width=12)
        table.add_column("Line", justify="center", width=6)
        table.add_column("Description & Remediation", style="white")

        severity_styles = {
            Severity.CRITICAL: "[bold white on red] CRITICAL [/bold white on red]",
            Severity.HIGH: "[bold red]HIGH[/bold red]",
            Severity.MEDIUM: "[bold yellow]MEDIUM[/bold yellow]",
            Severity.LOW: "[bold blue]LOW[/bold blue]",
            Severity.INFO: "[dim]INFO[/dim]",
        }

        for f in result.findings:
            sev_badge = severity_styles.get(f.severity, str(f.severity))
            line_str = str(f.line_number) if f.line_number else "-"

            desc_text = f"[bold]{f.title}[/bold]\n[dim]{f.description}[/dim]"
            if f.line_content:
                desc_text += f"\n[yellow]  Code: [/yellow][dim italic]{f.line_content.strip()}[/dim italic]"
            if f.fix_suggestion:
                desc_text += f"\n[green]  Fix:  [/green]{f.fix_suggestion}"

            table.add_row(sev_badge, f.rule_id, line_str, desc_text)

        console.print(table)

    console.print()

    # Score Summary Card
    grade_colors = {
        ScoreGrade.A_PLUS: "bold green",
        ScoreGrade.A: "green",
        ScoreGrade.B: "cyan",
        ScoreGrade.C: "yellow",
        ScoreGrade.D: "bright_red",
        ScoreGrade.F: "bold red",
    }
    gcolor = grade_colors.get(result.score.grade, "white")

    summary_text = Text()
    summary_text.append("Security Score: ", style="bold")
    summary_text.append(f"{result.score.points}/100 ", style="bold underline")
    summary_text.append(f"(Grade: {result.score.grade.value})\n", style=gcolor)
    summary_text.append(f"Critical: {result.critical_count}  |  ", style="bold red")
    summary_text.append(f"High: {result.high_count}  |  ", style="red")
    summary_text.append(f"Medium: {result.medium_count}  |  ", style="yellow")
    summary_text.append(f"Low: {result.low_count}  |  ", style="blue")
    summary_text.append(f"Info: {result.info_count}\n", style="dim")
    summary_text.append(f"Passed Checks: {len(result.passed_rules)} rules", style="dim green")

    border_color = "red" if result.critical_count > 0 or result.high_count > 0 else "green"
    console.print(
        Panel(
            summary_text,
            title="[bold]Scan Summary[/bold]",
            border_style=border_color,
            expand=False,
        )
    )

    # Policy Gate Evaluation
    if policy_report:
        console.print()
        if policy_report.passed:
            console.print(
                Panel(
                    "[bold green][PASS] CI/CD Quality Gate: PASSED[/bold green]\nAll security threshold criteria were met.",
                    border_style="green",
                )
            )
        else:
            fail_text = "\n".join([f"  * {msg}" for msg in policy_report.failures])
            console.print(
                Panel(
                    f"[bold red][FAIL] CI/CD Quality Gate: FAILED[/bold red]\n\n{fail_text}",
                    border_style="red",
                )
            )
