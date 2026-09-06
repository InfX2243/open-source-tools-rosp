"""Tests for configuration loader."""

from pathlib import Path
import tempfile
from datadiff.config.loader import ConfigLoader


def test_config_loader_yaml():
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg_file = Path(tmp_dir) / "datadiff.yaml"
        cfg_file.write_text("""
key:
  - user_id
ignore_columns:
  - created_at
rules:
  numeric_tolerance: 0.05
  case_sensitive: false
policies:
  allow_schema_changes: false
        """, encoding="utf-8")

        cfg = ConfigLoader.load_from_file(cfg_file)
        assert cfg.key == ["user_id"]
        assert cfg.ignore_columns == ["created_at"]
        assert cfg.rules.numeric_tolerance == 0.05
        assert not cfg.rules.case_sensitive
        assert not cfg.policies.allow_schema_changes


def test_starter_yaml_generation():
    template = ConfigLoader.generate_starter_yaml()
    assert "numeric_tolerance" in template
    assert "policies:" in template
