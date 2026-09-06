"""Typer CLI application for DataDiff."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console

import datadiff
from datadiff.config.loader import ConfigLoader
from datadiff.core.engine import DataDiffEngine
from datadiff.core.models import DiffConfig, NormalizationRules
from datadiff.reporters.console import ConsoleReporter
from datadiff.reporters.html import HTMLReporter
from datadiff.reporters.json import JSONReporter
from datadiff.reporters.markdown import MarkdownReporter

app = typer.Typer(
    name="datadiff",
    help="DataDiff: Git-like Semantic Data Comparison & Change Detection Platform",
    add_completion=False,
)
console = Console()


@app.command(name="compare")
def compare_datasets(
    source: str = typer.Argument(..., help="Path to source (old) dataset file"),
    target: str = typer.Argument(..., help="Path to target (new) dataset file"),
    key: Optional[List[str]] = typer.Option(None, "--key", "-k", help="Primary key column(s) to match rows"),
    ignore_columns: Optional[List[str]] = typer.Option(None, "--ignore-column", "-i", help="Columns to exclude from row diff"),
    tolerance: Optional[float] = typer.Option(None, "--tolerance", "-t", help="Numeric tolerance threshold for float differences"),
    case_sensitive: bool = typer.Option(True, "--case-sensitive/--ignore-case", help="Whether string comparisons are case-sensitive"),
    trim_whitespace: bool = typer.Option(True, "--trim/--no-trim", help="Whether to strip whitespace before comparing strings"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to YAML/JSON configuration file"),
    format: str = typer.Option("console", "--format", "-f", help="Output format: console, json, html, markdown"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save comparison output to file"),
) -> None:
    """Compare two datasets and explain schema, row, and statistical changes."""
    cfg = DiffConfig()

    if config:
        cfg = ConfigLoader.load_from_file(config)

    # CLI option overrides
    if key:
        cfg.key = key
    if ignore_columns:
        cfg.ignore_columns.extend(ignore_columns)
    if tolerance is not None:
        cfg.rules.numeric_tolerance = tolerance
    cfg.rules.case_sensitive = case_sensitive
    cfg.rules.trim_whitespace = trim_whitespace

    try:
        diff = DataDiffEngine.compare_sources(
            source=source,
            target=target,
            config=cfg,
        )
    except Exception as e:
        console.print(f"[bold red]Error running comparison:[/bold red] {e}")
        raise typer.Exit(code=2)

    # Render format
    fmt = format.lower()
    if fmt == "json":
        reporter = JSONReporter()
        rendered = reporter.render(diff)
        if output:
            reporter.write_to_file(diff, output)
            console.print(f"[dim green][OK] JSON report saved to {output}[/dim green]")
        else:
            print(rendered)
    elif fmt == "html":
        html_reporter = HTMLReporter()
        rendered = html_reporter.render(diff)
        out_path = output or f"datadiff_report_{diff.source_name}.html"
        html_reporter.write_to_file(diff, out_path)
        console.print(f"[bold green][OK] HTML report generated successfully at:[/bold green] [cyan]{out_path}[/cyan]")
    elif fmt == "markdown" or fmt == "md":
        md_reporter = MarkdownReporter()
        rendered = md_reporter.render(diff)
        if output:
            Path(output).write_text(rendered, encoding="utf-8")
            console.print(f"[dim green][OK] Markdown report saved to {output}[/dim green]")
        else:
            print(rendered)
    else:
        # Default console
        console_reporter = ConsoleReporter(console)
        console_reporter.render(diff)
        if output:
            # Also save JSON if output path given without specific non-console format
            JSONReporter().write_to_file(diff, output)

    # Exit code based on policy quality gate
    if not diff.policy_report.passed:
        raise typer.Exit(code=1)


@app.command(name="schema")
def compare_schema(
    source: str = typer.Argument(..., help="Path to source (old) dataset"),
    target: str = typer.Argument(..., help="Path to target (new) dataset"),
) -> None:
    """Compare schema columns and types between two datasets."""
    from datadiff.comparators.schema import SchemaComparator
    from datadiff.core.engine import DataDiffEngine

    adapter_a = DataDiffEngine.load_adapter(source)
    adapter_b = DataDiffEngine.load_adapter(target)
    df_a = adapter_a.load()
    df_b = adapter_b.load()

    schema_diff = SchemaComparator.compare(df_a, df_b)

    console.print()
    console.print(f"[bold cyan]SCHEMA COMPARISON:[/bold cyan] {Path(source).name} -> {Path(target).name}")
    console.print("=" * 60)

    if not schema_diff.has_changes:
        console.print("[bold green][OK] Both datasets have identical schemas![/bold green]")
        console.print()
        return

    for col in schema_diff.added_columns:
        console.print(f" [bold green]+ ADDED COLUMN:[/]    [green]{col.name}[/] ({col.dtype})")
    for col in schema_diff.removed_columns:
        console.print(f" [bold red]- REMOVED COLUMN:[/]  [red]{col.name}[/] ({col.dtype})")
    for mig in schema_diff.type_migrations:
        console.print(f" [bold yellow]~ TYPE CHANGED:[/]    [yellow]{mig.column}[/]: {mig.source_dtype} -> {mig.target_dtype}")
    console.print()


@app.command(name="profile")
def profile_datasets(
    source: str = typer.Argument(..., help="Path to source (old) dataset"),
    target: str = typer.Argument(..., help="Path to target (new) dataset"),
) -> None:
    """Compare column statistical profiles and identify data drift."""
    from datadiff.comparators.statistics import StatsComparator
    from datadiff.core.engine import DataDiffEngine

    df_a = DataDiffEngine.load_adapter(source).load()
    df_b = DataDiffEngine.load_adapter(target).load()

    stats_diff = StatsComparator.compare(df_a, df_b)

    console.print()
    console.print(f"[bold cyan]STATISTICAL PROFILE & DRIFT ANALYSIS[/bold cyan]")
    console.print("=" * 60)

    if stats_diff.drift_warnings:
        for w in stats_diff.drift_warnings:
            console.print(f" [bold yellow]![/] {w}")
    else:
        console.print("[dim green][OK] No significant statistical drift detected.[/dim green]")

    console.print()


@app.command(name="init")
def init_config(
    path: str = typer.Option("datadiff.yaml", "--path", "-p", help="Output file path for config template"),
) -> None:
    """Generate a starter datadiff.yaml configuration template."""
    out_file = Path(path)
    if out_file.exists():
        console.print(f"[yellow]Warning: {out_file} already exists. Overwriting...[/yellow]")
    content = ConfigLoader.generate_starter_yaml()
    out_file.write_text(content, encoding="utf-8")
    console.print(f"[bold green][OK] Generated DataDiff configuration template at:[/bold green] [cyan]{out_file}[/cyan]")


@app.command(name="serve")
def serve_dashboard(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host interface to bind"),
    port: int = typer.Option(8001, "--port", "-p", help="Port to serve API and dashboard"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
) -> None:
    """Launch the DataDiff REST API and Interactive Web Dashboard."""
    import uvicorn
    console.print(f"[bold green][OK] Starting DataDiff Web UI & REST API on http://{host}:{port}[/bold green]")
    uvicorn.run("datadiff.api.app:app", host=host, port=port, reload=reload)


@app.command(name="version")
def show_version() -> None:
    """Display DataDiff version."""
    console.print(f"[bold blue]DataDiff[/bold blue] version [cyan]{datadiff.__version__}[/cyan]")


if __name__ == "__main__":
    app()
