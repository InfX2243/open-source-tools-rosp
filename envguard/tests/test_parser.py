import tempfile
import os
from envguard.core.parser import parse_env_line, parse_env_file, infer_variable_type


def test_parse_simple_line():
    line = "PORT=8080"
    res = parse_env_line(line)
    assert res is not None
    key, val, comment, is_exp = res
    assert key == "PORT"
    assert val == "8080"
    assert comment is None
    assert is_exp is False


def test_parse_exported_and_quoted():
    line = 'export DATABASE_URL="postgresql://user:pass@localhost:5432/db" # primary db'
    res = parse_env_line(line)
    assert res is not None
    key, val, comment, is_exp = res
    assert key == "DATABASE_URL"
    assert val == "postgresql://user:pass@localhost:5432/db"
    assert comment == "primary db"
    assert is_exp is True


def test_infer_types():
    assert infer_variable_type("PORT", "3000") == "port"
    assert infer_variable_type("DEBUG", "true") == "boolean"
    assert infer_variable_type("SITE_URL", "https://example.com") == "url"
    assert infer_variable_type("COUNT", "42") == "integer"
    assert infer_variable_type("CONTACT", "user@test.org") == "email"


def test_parse_env_file(tmp_path):
    env_content = """
    # Comments should be skipped
    APP_NAME="My App"
    PORT=9000
    DEBUG=false
    """
    tmp_file = tmp_path / ".env.test"
    tmp_file.write_text(env_content, encoding="utf-8")

    parsed = parse_env_file(str(tmp_file))
    assert len(parsed.variables) == 3
    assert parsed.variables["APP_NAME"].value == "My App"
    assert parsed.variables["PORT"].inferred_type == "port"
    assert parsed.variables["DEBUG"].inferred_type == "boolean"
