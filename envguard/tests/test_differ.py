from envguard.core.differ import diff_environments
from envguard.core.models import DiffType


def test_diff_environments(tmp_path):
    f1 = tmp_path / "staging.env"
    f2 = tmp_path / "prod.env"

    f1.write_text("PORT=8000\nAPI_KEY=stg_secret_12345\nDEBUG=true\n", encoding="utf-8")
    f2.write_text("PORT=8000\nAPI_KEY=prod_ultra_secret_67890\nPROD_ONLY=true\n", encoding="utf-8")

    diff = diff_environments(str(f1), str(f2))

    assert diff.total_keys == 4
    assert diff.matched == 1  # PORT matches
    assert diff.modified == 1  # API_KEY modified

    types = {f.key: f.diff_type for f in diff.fields}
    assert types["PORT"] == DiffType.MATCH
    assert types["DEBUG"] == DiffType.REMOVED
    assert types["PROD_ONLY"] == DiffType.ADDED
    assert types["API_KEY"] == DiffType.MODIFIED
