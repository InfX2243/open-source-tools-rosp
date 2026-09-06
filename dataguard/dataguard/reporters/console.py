"""Rich CLI terminal reporter for DataGuard."""

from io import StringIO
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from dataguard.core.models import ValidationSummary, RuleStatus, Severity
from dataguard.reporters.base import BaseReporter


class ConsoleReporter(BaseReporter):
    """Renders formatted terminal reports using Rich."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def print_report(self, summary: ValidationSummary) -> None:
        """Directly print the formatted report to the terminal console."""
        self._render_to_console(self.console, summary)

    def render(self, summary: ValidationSummary) -> str:
        """Render the report to an ANSI / string buffer."""
        buffer = StringIO()
        string_console = Console(file=buffer, force_terminal=False, color_system=None)
        self._render_to_console(string_console, summary)
        return buffer.getvalue()

    def _render_to_console(self, con: Console, summary: ValidationSummary) -> None:
        # 1. Header & Quality Score Banner
        score = summary.quality_score
        if score >= 90.0:
            score_color = "bold green"
            score_badge = "[PASS]"
        elif score >= 75.0:
            score_color = "bold yellow"
            score_badge = "[WARN]"
        else:
            score_color = "bold red"
            score_badge = "[FAIL]"

        row_count_str = f"{summary.profile.row_count:,}" if summary.profile else "N/A"
        col_count_str = f"{summary.profile.column_count}" if summary.profile else "N/A"

        header_text = Text()
        header_text.append("[DATAGUARD QUALITY REPORT]\n", style="bold cyan")
        header_text.append(f"Dataset: ", style="bold")
        header_text.append(f"{summary.dataset_name}  ", style="white")
        header_text.append(f"Rows: ", style="bold")
        header_text.append(f"{row_count_str}  ", style="white")
        header_text.append(f"Cols: ", style="bold")
        header_text.append(f"{col_count_str}  ", style="white")
        header_text.append(f"Duration: ", style="bold")
        header_text.append(f"{summary.total_duration_ms:.1f}ms\n\n", style="white")

        header_text.append("QUALITY SCORE: ", style="bold")
        header_text.append(f"{score:.1f}%  {score_badge}\n", style=score_color)

        gate_status = "PASSED" if summary.passed_gate else "FAILED"
        gate_color = "green" if summary.passed_gate else "red"
        header_text.append(f"Quality Gate: [{gate_status}] - {summary.gate_reason or ''}", style=f"bold {gate_color}")

        con.print(Panel(header_text, border_style="cyan", box=box.ROUNDED))

        # 2. Results Table
        table = Table(
            title="Validation Rules Summary",
            box=box.SIMPLE_HEAVY,
            header_style="bold magenta",
            show_lines=False,
        )
        table.add_column("Status", justify="center", width=8)
        table.add_column("Rule / Check", style="bold")
        table.add_column("Column", style="cyan")
        table.add_column("Severity", justify="center")
        table.add_column("Checked", justify="right")
        table.add_column("Failed", justify="right")
        table.add_column("Failure Rate", justify="right")
        table.add_column("Message")

        status_styles = {
            RuleStatus.PASS: ("[green]PASS[/green]", "green"),
            RuleStatus.FAIL: ("[red]FAIL[/red]", "red"),
            RuleStatus.WARN: ("[yellow]WARN[/yellow]", "yellow"),
            RuleStatus.ERROR: ("[bold red]ERR[/bold red]", "bold red"),
            RuleStatus.SKIPPED: ("[dim]SKIP[/dim]", "dim"),
        }

        severity_styles = {
            Severity.LOW: "[dim]LOW[/dim]",
            Severity.MEDIUM: "[yellow]MED[/yellow]",
            Severity.HIGH: "[bold red]HIGH[/bold red]",
            Severity.CRITICAL: "[bold magenta]CRIT[/bold magenta]",
        }

        for res in summary.results:
            status_text, _ = status_styles.get(res.status, (res.status.value, "white"))
            sev_text = severity_styles.get(res.severity, res.severity.value)
            col_text = res.column if res.column else "[dim]<dataset>[/dim]"
            rate_text = f"{res.failure_rate:.1%}" if res.failed_count > 0 else "0.0%"

            table.add_row(
                status_text,
                res.rule_name,
                col_text,
                sev_text,
                f"{res.checked_count:,}",
                f"{res.failed_count:,}",
                rate_text,
                res.message,
            )

        con.print(table)

        # 3. Failed Samples Section
        failed_results = [r for r in summary.results if r.status in (RuleStatus.FAIL, RuleStatus.ERROR) and r.samples]
        if failed_results:
            con.print("\n[bold red][!] Rule Violations & Sample Failures:[/bold red]")
            for res in failed_results:
                col_info = f" (column '{res.column}')" if res.column else ""
                con.print(f"  * [bold]{res.rule_name}[/bold]{col_info} - [{res.severity.value.upper()}]: {res.message}")
                for s in res.samples[:3]:
                    val_repr = repr(s.value) if s.value is not None else "<NULL>"
                    con.print(f"    [dim]Row #{s.row_index}:[/dim] {val_repr} -> [italic]{s.reason}[/italic]")

        # 4. Anomalies Section
        if summary.anomalies and summary.anomalies.has_anomalies:
            con.print("\n[bold yellow][!] Baseline Drift & Anomalies Detected:[/bold yellow]")
            for a in summary.anomalies.anomalies:
                con.print(f"  * [{a.severity.value.upper()}] {a.description}")

        con.print()
