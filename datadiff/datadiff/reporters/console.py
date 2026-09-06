"""Rich terminal console reporter for DataDiff."""

from __future__ import annotations

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from datadiff.core.models import DiffSummary
from datadiff.reporters.base import BaseReporter


class ConsoleReporter(BaseReporter):
    """Outputs structured git-style diffs to the terminal using Rich."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(highlight=False)

    def render(self, diff: DiffSummary) -> None:
        """Render complete terminal comparison summary."""
        c = self.console

        # Header Panel
        header_text = Text()
        header_text.append("DATASET DIFF: ", style="bold white")
        header_text.append(f"{diff.source_name}", style="cyan")
        header_text.append(" -> ", style="bold bright_black")
        header_text.append(f"{diff.target_name}", style="bold magenta")
        header_text.append(f" ({diff.execution_time_ms:.1f}ms)", style="dim")

        c.print()
        c.print(Panel(header_text, style="blue", box=box.ROUNDED))

        # 1. Summary Metrics Table
        grid = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        grid.add_column("Metric", style="bold")
        grid.add_column("Count", justify="right")
        grid.add_column("Metric2", style="bold")
        grid.add_column("Count2", justify="right")

        r = diff.row_diff
        grid.add_row(
            "Rows in Source:", f"{r.source_row_count:,}",
            "[green]+ Added Rows:[reset]", f"[bold green]{r.added_count:,}[reset]"
        )
        grid.add_row(
            "Rows in Target:", f"{r.target_row_count:,}",
            "[red]- Removed Rows:[reset]", f"[bold red]{r.removed_count:,}[reset]"
        )
        grid.add_row(
            "Match Keys:", f"{', '.join(r.keys) if r.keys else 'None'}",
            "[yellow]~ Modified Rows:[reset]", f"[bold yellow]{r.modified_count:,}[reset]"
        )
        grid.add_row(
            "Duplicate Keys:", f"{r.duplicate_keys_count}",
            "[dim]= Unchanged Rows:[reset]", f"[dim]{r.unchanged_count:,}[reset]"
        )

        c.print(Panel(grid, title="[bold]Row-Level Summary[/bold]", border_style="bright_blue", box=box.ROUNDED))

        # 2. Schema Diff Section
        s = diff.schema_diff
        if s.has_changes:
            schema_table = Table(title="Schema Differences", box=box.SIMPLE_HEAVY, show_header=True)
            schema_table.add_column("Change", justify="center", width=8)
            schema_table.add_column("Column", style="bold")
            schema_table.add_column("Source Type", style="cyan")
            schema_table.add_column("Target Type", style="magenta")
            schema_table.add_column("Details", style="dim")

            for col in s.added_columns:
                schema_table.add_row("[green]+ ADD[/green]", col.name, "-", col.dtype, "[green]New column in target[/green]")
            for col in s.removed_columns:
                schema_table.add_row("[red]- DEL[/red]", col.name, col.dtype, "-", "[red]Removed from source[/red]")
            for mig in s.type_migrations:
                schema_table.add_row("[yellow]~ TYPE[/yellow]", mig.column, mig.source_dtype, mig.target_dtype, "[yellow]Data type changed[/yellow]")

            c.print(schema_table)
            c.print()
        else:
            c.print("[dim green][OK] Schemas are perfectly aligned (0 changes)[/dim green]")
            c.print()

        # 3. Modified Records Sample
        if r.sample_modified:
            c.print(f"[bold yellow]MODIFIED RECORDS[/bold yellow] [dim](Showing up to {len(r.sample_modified)} samples):[/dim]")
            for mod in r.sample_modified:
                key_desc = ", ".join(f"{k}={v}" for k, v in mod.key_values.items())
                c.print(f"  [bold yellow]Key ({key_desc})[/bold yellow]:")
                for fc in mod.field_changes:
                    c.print(f"    [dim]{fc.column}:[/dim] [red]'{fc.source_value}'[/red] [bold]->[/bold] [green]'{fc.target_value}'[/green]")
            c.print()

        # 4. Added Records Sample
        if r.sample_added:
            c.print(f"[bold green]ADDED RECORDS[/bold green] [dim](Showing up to {len(r.sample_added)} samples):[/dim]")
            for add in r.sample_added:
                key_desc = ", ".join(f"{k}={v}" for k, v in add.key_values.items())
                sample_vals = " | ".join(f"{k}={v}" for k, v in list(add.row_data.items())[:4])
                c.print(f"  [green]+ [{key_desc}][/green] {sample_vals}")
            c.print()

        # 5. Removed Records Sample
        if r.sample_removed:
            c.print(f"[bold red]REMOVED RECORDS[/bold red] [dim](Showing up to {len(r.sample_removed)} samples):[/dim]")
            for rem in r.sample_removed:
                key_desc = ", ".join(f"{k}={v}" for k, v in rem.key_values.items())
                sample_vals = " | ".join(f"{k}={v}" for k, v in list(rem.row_data.items())[:4])
                c.print(f"  [red]- [{key_desc}][/red] {sample_vals}")
            c.print()

        # 6. Statistical Drift Alerts
        if diff.stats_diff.drift_warnings:
            c.print(Panel(
                "\n".join(f"[bold yellow]![/bold yellow] {w}" for w in diff.stats_diff.drift_warnings),
                title="[bold yellow]Statistical Drift Warnings[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED,
            ))

        # 7. CI/CD Policy Quality Gate
        pol = diff.policy_report
        if pol.passed:
            gate_text = Text()
            gate_text.append("[OK] QUALITY GATE PASSED", style="bold green")
            gate_text.append(" - Dataset diff complies with all configured policies.")
            c.print(Panel(gate_text, border_style="green", box=box.ROUNDED))
        else:
            fail_text = "\n".join(f" [FAIL] {err}" for err in pol.failures)
            c.print(Panel(
                f"[bold red]QUALITY GATE FAILED ({len(pol.failures)} policy violation(s)):[/bold red]\n{fail_text}",
                border_style="red",
                box=box.ROUNDED,
            ))
        c.print()
