from envguard.core.scanner import scan_codebase


def test_scan_codebase_python_and_ts(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text(
        """
import os
port = os.getenv("APP_PORT")
db = os.environ["DATABASE_URL"]
""",
        encoding="utf-8",
    )

    ts_file = tmp_path / "main.ts"
    ts_file.write_text(
        """
const apiKey = process.env.API_KEY;
const viteMode = import.meta.env.VITE_APP_MODE;
""",
        encoding="utf-8",
    )

    res = scan_codebase(str(tmp_path))

    assert "APP_PORT" in res.variables
    assert "DATABASE_URL" in res.variables
    assert "API_KEY" in res.variables
    assert "VITE_APP_MODE" in res.variables
    assert res.files_scanned == 2
