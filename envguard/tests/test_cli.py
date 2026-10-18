from typer.testing import CliRunner
from envguard.cli.commands import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "EnvGuard" in result.stdout


def test_cli_check_clean(tmp_path):
    env_file = tmp_path / ".env"
    ex_file = tmp_path / ".env.example"

    env_file.write_text("PORT=8000\nDATABASE_URL=https://example.com\n", encoding="utf-8")
    ex_file.write_text("PORT=8000\nDATABASE_URL=https://example.com\n", encoding="utf-8")

    result = runner.invoke(app, ["check", "--env", str(env_file), "--example", str(ex_file)])
    assert result.exit_code == 0
    assert "Zero drift detected" in result.stdout or "Status: PASSED" in result.stdout


def test_cli_check_missing_fails(tmp_path):
    env_file = tmp_path / ".env"
    ex_file = tmp_path / ".env.example"

    env_file.write_text("PORT=8000\n", encoding="utf-8")
    ex_file.write_text("PORT=8000\nSECRET_KEY=dummy\n", encoding="utf-8")

    result = runner.invoke(app, ["check", "--env", str(env_file), "--example", str(ex_file)])
    assert result.exit_code != 0
    assert "MISSING_KEY" in result.stdout


def test_cli_diff(tmp_path):
    f1 = tmp_path / "env1"
    f2 = tmp_path / "env2"

    f1.write_text("A=1\nB=2\n", encoding="utf-8")
    f2.write_text("A=1\nB=999\n", encoding="utf-8")

    result = runner.invoke(app, ["diff", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "matched" in result.stdout
    assert "modified" in result.stdout


def test_cli_scan_secrets_clean(tmp_path):
    clean_file = tmp_path / "clean.py"
    clean_file.write_text("port = 8000\nprint(port)\n", encoding="utf-8")

    result = runner.invoke(app, ["scan-secrets", str(clean_file)])
    assert result.exit_code == 0
    assert "No secret leaks" in result.stdout
