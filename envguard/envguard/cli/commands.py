"""
Typer CLI implementation for EnvGuard.
"""

import sys
import os
from typing import List, Optional
import typer
from rich.console import Console

from envguard import __version__
from envguard.core.checker import check_env
from envguard.core.differ import diff_environments
from envguard.core.generator import generate_env_example
from envguard.core.reporter import (
    export_json,
    generate_html_report,
    render_check_report,
    render_diff_report,
    render_scan_report,
    render_secrets_report,
)
from envguard.core.scanner import scan_codebase
from envguard.core.secrets import scan_text_for_secrets

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = typer.Typer(
    name="envguard",
    help="EnvGuard -- Open-Source Environment & Secret Governance Suite",
    add_completion=False,
)
console = Console(safe_box=True)


@app.command()
def version():
    """Display the EnvGuard version."""
    console.print(f"[bold cyan]EnvGuard[/bold cyan] version [bold green]{__version__}[/bold green] (ROSP Tools Suite)")


@app.command()
def check(
    env_file: str = typer.Option(".env", "--env", "-e", help="Path to the target .env file to audit"),
    example: Optional[str] = typer.Option(None, "--example", "-x", help="Path to .env.example reference file"),
    schema: Optional[str] = typer.Option(None, "--schema", "-s", help="Path to .env.schema.yaml file"),
    strict: bool = typer.Option(False, "--strict", help="Fail build on warnings or undocumented extra keys"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, html"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="File to write HTML or JSON report to"),
):
    """
    Validate .env against .env.example or a declarative schema file.
    """
    if not os.path.exists(env_file):
        console.print(f"[bold red]Error:[/bold red] Target environment file not found: {env_file}")
        raise typer.Exit(code=1)

    # Auto-detect .env.example if not provided
    if not example and not schema:
        parent_dir = os.path.dirname(env_file) or "."
        default_example = os.path.join(parent_dir, ".env.example")
        if os.path.exists(default_example):
            example = default_example

    result = check_env(
        env_path=env_file,
        example_path=example,
        schema_path=schema,
        strict=strict,
    )

    if format == "json":
        json_data = export_json(result.model_dump())
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(json_data)
            console.print(f"[green]JSON report saved to {output}[/green]")
        else:
            print(json_data)
    elif format == "html":
        html_content = generate_html_report(result)
        out_path = output or "envguard_report.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        console.print(f"[green]HTML report saved to {out_path}[/green]")
    else:
        render_check_report(result)

    # CI/CD Exit Code handling
    if not result.passed:
        raise typer.Exit(code=1)
    if strict and result.issues:
        raise typer.Exit(code=1)


@app.command()
def generate(
    codebase: Optional[str] = typer.Option(None, "--codebase", "-c", help="Directory path to scan for env usages"),
    source_env: Optional[str] = typer.Option(None, "--source-env", "-s", help="Path to an existing .env to sanitize"),
    output: str = typer.Option(".env.example", "--output", "-o", help="Path to write the sanitized .env.example"),
    print_only: bool = typer.Option(False, "--print-only", "-p", help="Output to terminal instead of writing to disk"),
):
    """
    Scan codebase and generate a sanitized .env.example template.
    """
    scan_res = None
    if codebase and os.path.exists(codebase):
        console.print(f"[cyan]Scanning codebase in [bold]{codebase}[/bold] for environment variables...[/cyan]")
        scan_res = scan_codebase(codebase)
        render_scan_report(scan_res)

    if not codebase and not source_env:
        # Default: scan current working directory
        console.print("[cyan]Scanning current directory for environment variables...[/cyan]")
        scan_res = scan_codebase(".")
        render_scan_report(scan_res)

    content = generate_env_example(
        scan_result=scan_res,
        source_env_path=source_env,
        output_path=None if print_only else output,
    )

    if print_only:
        print(content)
    else:
        console.print(f"[bold green]✔ Successfully generated sanitized template: [bold]{output}[/bold green]")


@app.command()
def diff(
    file1: str = typer.Argument(..., help="Path to the first environment file (e.g., staging.env)"),
    file2: str = typer.Argument(..., help="Path to the second environment file (e.g., prod.env)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table or json"),
):
    """
    Safely compare two environment files with value redaction and entropy check.
    """
    if not os.path.exists(file1):
        console.print(f"[bold red]Error:[/bold red] File not found: {file1}")
        raise typer.Exit(code=1)
    if not os.path.exists(file2):
        console.print(f"[bold red]Error:[/bold red] File not found: {file2}")
        raise typer.Exit(code=1)

    diff_res = diff_environments(file1, file2)

    if format == "json":
        print(export_json(diff_res.model_dump()))
    else:
        render_diff_report(diff_res)


@app.command(name="scan-secrets")
def scan_secrets(
    paths: List[str] = typer.Argument(..., help="Files or directories to scan for unmasked secrets"),
    fail_on_leak: bool = typer.Option(True, "--fail-on-leak/--no-fail", help="Exit with code 1 if leaks are found"),
):
    """
    Scan files for unmasked credentials, API keys, and cryptographic private keys.
    """
    all_findings = []
    for path in paths:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            findings = scan_text_for_secrets(content, file_path=path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path):
                if any(ignored in dirpath for ignored in (".git", "node_modules", "venv", "__pycache__")):
                    continue
                for fname in filenames:
                    file_p = os.path.join(dirpath, fname)
                    try:
                        with open(file_p, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        findings = scan_text_for_secrets(content, file_path=file_p)
                        all_findings.extend(findings)
                    except Exception:
                        pass

    render_secrets_report(all_findings)

    if all_findings and fail_on_leak:
        raise typer.Exit(code=1)


@app.command(name="ui")
def start_ui(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host IP to bind web server"),
    port: int = typer.Option(8765, "--port", "-p", help="Port to listen on"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Automatically open default browser"),
):
    """
    Launch the interactive EnvGuard Web Dashboard & REST API.
    """
    import webbrowser
    import uvicorn

    url = f"http://{host}:{port}"
    console.print(f"[bold cyan]EnvGuard Web Dashboard[/bold cyan] starting on [bold green]{url}[/bold green]")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    uvicorn.run("envguard.api.app:app", host=host, port=port, reload=False)


@app.command(name="dashboard", hidden=True)
def start_dashboard(
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8765, "--port", "-p"),
    open_browser: bool = typer.Option(True, "--open/--no-open"),
):
    """Alias for 'envguard ui'."""
    start_ui(host=host, port=port, open_browser=open_browser)


if __name__ == "__main__":
    app()
