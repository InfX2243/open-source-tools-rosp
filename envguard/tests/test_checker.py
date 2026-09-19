from envguard.core.checker import check_env
from envguard.core.models import IssueType


def test_check_missing_key(tmp_path):
    env_file = tmp_path / ".env"
    example_file = tmp_path / ".env.example"

    example_file.write_text("PORT=8000\nDATABASE_URL=postgresql://localhost/db\n", encoding="utf-8")
    env_file.write_text("PORT=8000\n", encoding="utf-8")

    result = check_env(str(env_file), str(example_file))
    assert not result.passed
    assert any(i.issue_type == IssueType.MISSING_KEY and i.key == "DATABASE_URL" for i in result.issues)


def test_check_extra_key(tmp_path):
    env_file = tmp_path / ".env"
    example_file = tmp_path / ".env.example"

    example_file.write_text("PORT=8000\n", encoding="utf-8")
    env_file.write_text("PORT=8000\nEXTRA_UNDOCUMENTED=123\n", encoding="utf-8")

    result = check_env(str(env_file), str(example_file), strict=True)
    assert any(i.issue_type == IssueType.EXTRA_KEY and i.key == "EXTRA_UNDOCUMENTED" for i in result.issues)


def test_check_type_mismatch(tmp_path):
    env_file = tmp_path / ".env"
    example_file = tmp_path / ".env.example"

    example_file.write_text("PORT=8000\nDEBUG=true\n", encoding="utf-8")
    env_file.write_text("PORT=not_a_port\nDEBUG=maybe\n", encoding="utf-8")

    result = check_env(str(env_file), str(example_file))
    assert any(i.issue_type == IssueType.TYPE_MISMATCH and i.key == "PORT" for i in result.issues)
