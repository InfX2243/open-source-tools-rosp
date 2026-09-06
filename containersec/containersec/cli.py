"""ContainerSec Command Line Interface."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from containersec import __version__
from containersec.core.config import load_config
from containersec.core.engine import SecurityEngine
from containersec.core.fixer import DockerfileFixer
from containersec.core.models import Severity
from containersec.reporters.cli_reporter import print_scan_report
from containersec.reporters.html_reporter import to_html_report
from containersec.reporters.json_reporter import to_json_report
from containersec.reporters.sarif_reporter import to_sarif_report
from containersec.rules import ALL_RULES

app = typer.Typer(
    name="containersec",
    help="ContainerSec — Open-Source Dockerfile & Container Security Linter",
    add_completion=False,
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(safe_box=True)


@app.command()
def scan(
    path: Path = typer.Argument(Path("Dockerfile"), help="Path to Dockerfile or directory containing Dockerfile"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, sarif, html"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save output to file"),
    fail_on: Optional[str] = typer.Option(None, "--fail-on", help="Exit code 1 if findings at or above severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to .containersec.yaml config file"),
):
    """Scan a Dockerfile for security vulnerabilities, secrets, and CIS benchmark violations."""
    target_file = path
    if target_file.is_dir():
        target_file = target_file / "Dockerfile"

    if not target_file.exists():
        console.print(f"[bold red]Error:[/bold red] Target file not found: {target_file}")
        raise typer.Exit(code=2)

    config = load_config(config_file)
    engine = SecurityEngine(config=config)

    try:
        result = engine.scan_file(target_file)
        policy_report = engine.evaluate_policy(result)
    except Exception as e:
        console.print(f"[bold red]Scan Error:[/bold red] {e}")
        raise typer.Exit(code=2)

    # Format dispatch
    if format == "json":
        out_str = to_json_report(result, policy_report)
        if output:
            output.write_text(out_str, encoding="utf-8")
            console.print(f"[green]JSON report saved to {output}[/green]")
        else:
            print(out_str)
    elif format == "sarif":
        out_str = to_sarif_report(result)
        if output:
            output.write_text(out_str, encoding="utf-8")
            console.print(f"[green]SARIF report saved to {output}[/green]")
        else:
            print(out_str)
    elif format == "html":
        out_str = to_html_report(result)
        out_path = output or Path("containersec-report.html")
        out_path.write_text(out_str, encoding="utf-8")
        console.print(f"[green]HTML report saved to {out_path}[/green]")
    else:
        print_scan_report(result, policy_report)

    # Policy / Fail-on exit code determination
    should_fail = not policy_report.passed
    if fail_on:
        sev_order = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        try:
            target_idx = sev_order.index(fail_on.upper())
            for f in result.findings:
                if sev_order.index(f.severity.value) >= target_idx:
                    should_fail = True
                    break
        except ValueError:
            pass

    if should_fail:
        raise typer.Exit(code=1)


@app.command()
def fix(
    path: Path = typer.Argument(Path("Dockerfile"), help="Path to Dockerfile to fix"),
    write: bool = typer.Option(False, "--write", "-w", help="Overwrite file with remediated contents"),
):
    """Automatically fix common security issues (non-root user, ADD->COPY, cache cleanups)."""
    target = path if path.is_file() else path / "Dockerfile"
    if not target.exists():
        console.print(f"[bold red]Error:[/bold red] Dockerfile not found: {target}")
        raise typer.Exit(code=2)

    content = target.read_text(encoding="utf-8", errors="replace")
    engine = SecurityEngine()
    result = engine.scan_content(content, str(target))

    fixer = DockerfileFixer(content, result)
    fixed_content, changes = fixer.fix()

    if not changes:
        console.print("[green]No auto-fixable issues detected.[/green]")
        return

    console.print(f"[bold cyan]ContainerSec Auto-Fixer[/bold cyan] found {len(changes)} remediations:")
    for change in changes:
        console.print(f"  [green][FIX][/green] {change}")

    if write:
        target.write_text(fixed_content, encoding="utf-8")
        console.print(f"\n[bold green]Success:[/bold green] Applied fixes to {target}")
    else:
        console.print("\n[dim]-- Dry Run (use --write to apply modifications) --[/dim]\n")
        console.print(fixed_content)


@app.command()
def rules():
    """List all available CIS benchmark and security rules."""
    table = Table(title="Available ContainerSec Rules", box=box.ROUNDED)
    table.add_column("Rule ID", style="cyan", width=14)
    table.add_column("Severity", justify="center", width=10)
    table.add_column("Category", style="magenta", width=14)
    table.add_column("CIS Benchmark", style="blue", width=16)
    table.add_column("Title & Description", style="white")

    for rule_cls in ALL_RULES:
        defn = rule_cls().definition()
        table.add_row(
            defn.rule_id,
            defn.severity.value,
            defn.category,
            defn.cis_benchmark or "-",
            f"[bold]{defn.title}[/bold]\n[dim]{defn.description}[/dim]",
        )

    console.print(table)


@app.command()
def init():
    """Create a starter .containersec.yaml configuration file."""
    config_file = Path(".containersec.yaml")
    if config_file.exists():
        console.print("[yellow].containersec.yaml already exists.[/yellow]")
        return

    sample_yaml = """# ContainerSec Scan & Policy Configuration
# Documentation: https://github.com/open-source-tools/containersec

target_path: "Dockerfile"
severity_threshold: "LOW"   # INFO, LOW, MEDIUM, HIGH, CRITICAL

# CI/CD Quality Gate Policy
policy:
  max_critical: 0
  max_high: 0
  max_medium: 2
  min_score: 80
  fail_on_secrets: true

# Ignored Rule IDs
ignore_rules:
  # - CIS-4.6  # Uncomment to ignore missing HEALTHCHECK
"""
    config_file.write_text(sample_yaml, encoding="utf-8")
    console.print("[bold green]Created starter .containersec.yaml[/bold green]")


@app.command()
def serve(
    port: int = typer.Option(8002, "--port", "-p", help="Port to run Web UI & API"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address"),
):
    """Launch the ContainerSec Web Dashboard & REST API server."""
    import uvicorn
    console.print(f"[bold green]Starting ContainerSec Web Dashboard at http://{host}:{port}[/bold green]")
    uvicorn.run("containersec.api.app:app", host=host, port=port, reload=False)


@app.command()
def version():
    """Display the version of ContainerSec."""
    console.print(f"ContainerSec version [bold cyan]{__version__}[/bold cyan]")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
