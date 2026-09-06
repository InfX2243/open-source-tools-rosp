import sys
import os
from typing import Optional

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from dataguard import __version__
from dataguard.core.models import Severity, RuleConfig, DatasetProfile
from dataguard.core.engine import ValidationEngine
from dataguard.core.profiler import DataProfiler
from dataguard.config.loader import ConfigLoader
from dataguard.reporters.console import ConsoleReporter
from dataguard.reporters.html import HTMLReporter
from dataguard.reporters.json import JSONReporter
from dataguard.reporters.markdown import MarkdownReporter
from dataguard.sources import load_dataset

app = typer.Typer(
    name="dataguard",
    help="DataGuard: Open-Source Data Quality, Validation & Profiling Platform",
    add_completion=False,
    no_args_is_help=True,
)
console = Console(safe_box=True)


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]DataGuard[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show DataGuard version and exit",
        callback=version_callback,
        is_eager=True,
    )
):
    """DataGuard CLI entrypoint."""
    pass


@app.command(name="validate")
def validate_command(
    source: str = typer.Argument(..., help="Path to data file (CSV, JSON, Parquet) or database connection URI"),
    config: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to YAML or JSON validation rules file",
    ),
    format: str = typer.Option(
        "console",
        "--format",
        "-f",
        help="Report format: console, html, json, markdown",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output report destination file path",
    ),
    fail_on: Optional[str] = typer.Option(
        None,
        "--fail-on",
        help="Minimum violation severity triggering non-zero exit (low, medium, high, critical)",
    ),
    min_score: Optional[float] = typer.Option(
        None,
        "--min-score",
        help="Minimum overall quality score required to pass quality gate (0-100)",
    ),
    baseline: Optional[str] = typer.Option(
        None,
        "--baseline",
        "-b",
        help="Path to baseline profile JSON file for anomaly detection",
    ),
    table: Optional[str] = typer.Option(
        None,
        "--table",
        help="Table name (for SQL database sources)",
    ),
    query: Optional[str] = typer.Option(
        None,
        "--query",
        help="Custom SQL query (for SQL database sources)",
    ),
):
    """
    Validate a dataset against quality rules and evaluate quality gates.
    """
    try:
        rule_config: RuleConfig
        if config:
            rule_config = ConfigLoader.load_from_file(config)
        else:
            rule_config = RuleConfig(dataset=source)

        # Override thresholds if passed via CLI flags
        if fail_on:
            try:
                rule_config.thresholds.fail_on = Severity(fail_on.lower())
            except ValueError:
                console.print(f"[bold red]Error:[/bold red] Invalid severity '{fail_on}'. Choose from: low, medium, high, critical")
                raise typer.Exit(code=2)

        if min_score is not None:
            rule_config.thresholds.min_quality_score = min_score

        # Baseline profile for drift detection
        baseline_profile: Optional[DatasetProfile] = None
        if baseline:
            import json
            with open(baseline, "r", encoding="utf-8") as f:
                base_dict = json.load(f)
                baseline_profile = DatasetProfile(**base_dict)

        engine = ValidationEngine(rule_config)
        summary = engine.validate_source(
            source=source,
            config=rule_config,
            baseline_profile=baseline_profile,
            table=table,
            query=query,
        )

        fmt = format.lower().strip()
        if fmt == "html":
            reporter = HTMLReporter()
            rendered = reporter.render(summary)
            out_file = output or f"dataguard-report-{summary.dataset_name.replace('/', '_')}.html"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(rendered)
            console.print(f"[bold green][OK] HTML Report generated:[/bold green] {out_file}")
        elif fmt == "json":
            reporter = JSONReporter()
            rendered = reporter.render(summary)
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(rendered)
                console.print(f"[bold green][OK] JSON Report saved:[/bold green] {output}")
            else:
                console.print(rendered)
        elif fmt == "markdown" or fmt == "md":
            reporter = MarkdownReporter()
            rendered = reporter.render(summary)
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(rendered)
                console.print(f"[bold green][OK] Markdown Report saved:[/bold green] {output}")
            else:
                console.print(rendered)
        else:
            # Console format
            reporter = ConsoleReporter(console=console)
            reporter.print_report(summary)
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(reporter.render(summary))
                console.print(f"[OK] Saved console output to: {output}")

        # Quality gate exit code
        if not summary.passed_gate:
            console.print(f"[bold red][FAIL] Quality Gate Failed:[/bold red] {summary.gate_reason}")
            raise typer.Exit(code=1)
        else:
            raise typer.Exit(code=0)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error executing validation:[/bold red] {e}")
        raise typer.Exit(code=2)


@app.command(name="profile")
def profile_command(
    source: str = typer.Argument(..., help="Path to data file or database URI"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("console", "--format", "-f", help="Output format: console, json, html"),
    table: Optional[str] = typer.Option(None, "--table", help="Table name for SQL sources"),
):
    """
    Profile a dataset and generate statistical distributions and schema insights.
    """
    try:
        df = load_dataset(source, table=table)
        profile = DataProfiler.profile_dataframe(df, source_name=source)

        fmt = format.lower().strip()
        if fmt == "json":
            json_str = profile.model_dump_json(indent=2)
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(json_str)
                console.print(f"[OK] Profile saved to: {output}")
            else:
                console.print(json_str)
        else:
            # Render Rich summary table
            table_view = Table(
                title=f"Dataset Profile: {source}",
                header_style="bold cyan",
            )
            table_view.add_column("Column", style="bold")
            table_view.add_column("Type", style="dim")
            table_view.add_column("Total", justify="right")
            table_view.add_column("Nulls", justify="right")
            table_view.add_column("Null %", justify="right")
            table_view.add_column("Unique", justify="right")
            table_view.add_column("Unique %", justify="right")
            table_view.add_column("Range / Mean")

            for col_name, col in profile.columns.items():
                range_info = "-"
                if col.min_value is not None:
                    range_info = f"[{col.min_value}, {col.max_value}] (mean={col.mean_value})"

                table_view.add_row(
                    col_name,
                    col.detected_type,
                    f"{col.total_count:,}",
                    f"{col.null_count:,}",
                    f"{col.null_percentage:.1f}%",
                    f"{col.distinct_count:,}",
                    f"{col.unique_percentage:.1f}%",
                    range_info,
                )

            console.print(table_view)
            console.print(f"[dim]Total Rows: {profile.row_count:,} | Columns: {profile.column_count} | Est. Size: {profile.estimated_memory_kb:.1f} KB[/dim]\n")

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(profile.model_dump_json(indent=2))
                console.print(f"[OK] Profile metrics saved to: {output}")

    except Exception as e:
        console.print(f"[bold red]Profiling error:[/bold red] {e}")
        raise typer.Exit(code=2)


@app.command(name="init")
def init_command(
    output: str = typer.Option("rules.yaml", "--output", "-o", help="Output YAML filename"),
    template: str = typer.Option("customer", "--template", "-t", help="Template type: customer, ecommerce, basic"),
):
    """
    Generate starter validation rules configuration file.
    """
    content = ConfigLoader.get_template(template)
    if os.path.exists(output):
        overwrite = typer.confirm(f"File '{output}' already exists. Overwrite?", default=False)
        if not overwrite:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()

    with open(output, "w", encoding="utf-8") as f:
        f.write(content)

    console.print(f"[bold green][OK] Created starter rules config:[/bold green] [cyan]{output}[/cyan] (template: {template})")


@app.command(name="check-rules")
def check_rules_command(
    config: str = typer.Argument(..., help="Path to YAML or JSON rules file to check"),
):
    """
    Validate that a rules file conforms to DataGuard schema without executing checks.
    """
    try:
        cfg = ConfigLoader.load_from_file(config)
        console.print(f"[bold green][OK] Configuration valid![/bold green]")
        console.print(f"  * Dataset: [cyan]{cfg.dataset or 'Any'}[/cyan]")
        console.print(f"  * Schema Version: {cfg.version}")
        console.print(f"  * Configured Columns ({len(cfg.columns)}): {list(cfg.columns.keys())}")
        console.print(f"  * Quality Gate: fail_on={cfg.thresholds.fail_on.value.upper()}, min_score={cfg.thresholds.min_quality_score}%")
    except Exception as e:
        console.print(f"[bold red][FAIL] Configuration schema error:[/bold red]\n{e}")
        raise typer.Exit(code=1)


@app.command(name="serve")
def serve_command(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="API server host IP"),
    port: int = typer.Option(8000, "--port", "-p", help="API server port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """
    Start the DataGuard FastAPI server and web dashboard.
    """
    import uvicorn
    console.print(f"[bold cyan]Starting DataGuard API & Web Server[/bold cyan] at [bold green]http://{host}:{port}[/bold green]...")
    uvicorn.run("api.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
