"""End-to-end integration tests for Typer CLI commands."""

import pytest
from typer.testing import CliRunner
from dataguard.cli.commands import app

runner = CliRunner()


def test_cli_version():
    res = runner.invoke(app, ["--version"])
    assert res.exit_code == 0
    assert "DataGuard" in res.output


def test_cli_init_template(tmp_path):
    out_file = str(tmp_path / "test_rules.yaml")
    res = runner.invoke(app, ["init", "--output", out_file, "--template", "customer"])
    assert res.exit_code == 0
    assert "Created starter rules config" in res.output


def test_cli_check_rules(tmp_path):
    out_file = str(tmp_path / "test_rules.yaml")
    runner.invoke(app, ["init", "--output", out_file, "--template", "customer"])

    res = runner.invoke(app, ["check-rules", out_file])
    assert res.exit_code == 0
    assert "Configuration valid" in res.output


def test_cli_validate_clean_data(temp_csv_file, tmp_path):
    rules_file = str(tmp_path / "rules.yaml")
    runner.invoke(app, ["init", "--output", rules_file, "--template", "customer"])

    res = runner.invoke(app, ["validate", temp_csv_file, "--config", rules_file])
    assert res.exit_code == 0
    assert "QUALITY SCORE:" in res.output


def test_cli_profile_command(temp_csv_file):
    res = runner.invoke(app, ["profile", temp_csv_file])
    assert res.exit_code == 0
    assert "Dataset Profile" in res.output
