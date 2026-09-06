"""Tests for Typer CLI commands."""

from typer.testing import CliRunner
from datadiff.cli.commands import app

runner = CliRunner()


def test_cli_version():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "DataDiff version" in res.output


def test_cli_compare():
    res = runner.invoke(app, [
        "compare",
        "examples/data/customers_v1.csv",
        "examples/data/customers_v2.csv",
        "--key", "id",
        "--format", "json",
    ])
    assert res.exit_code == 0
    assert '"source_name": "customers_v1.csv"' in res.output


def test_cli_schema():
    res = runner.invoke(app, [
        "schema",
        "examples/data/customers_v1.csv",
        "examples/data/customers_v2.csv",
    ])
    assert res.exit_code == 0
    assert "SCHEMA COMPARISON" in res.output
    assert "tier" in res.output


def test_cli_profile():
    res = runner.invoke(app, [
        "profile",
        "examples/data/customers_v1.csv",
        "examples/data/customers_v2.csv",
    ])
    assert res.exit_code == 0
    assert "STATISTICAL PROFILE" in res.output
