"""Unit tests for configuration loader and templates."""

import pytest
from dataguard.config.loader import ConfigLoader
from dataguard.core.models import Severity


def test_load_from_string_valid_yaml():
    yaml_text = """
dataset: users.csv
version: "1.0"
thresholds:
  fail_on: critical
  min_quality_score: 90.0
columns:
  id:
    type: integer
    required: true
    unique: true
  email:
    type: string
    format: email
"""
    cfg = ConfigLoader.load_from_string(yaml_text)
    assert cfg.dataset == "users.csv"
    assert cfg.thresholds.fail_on == Severity.CRITICAL
    assert cfg.thresholds.min_quality_score == 90.0
    assert "id" in cfg.columns
    assert cfg.columns["id"].unique is True


def test_invalid_yaml_raises_value_error():
    bad_yaml = "invalid: yaml: : text"
    with pytest.raises(ValueError):
        ConfigLoader.load_from_string(bad_yaml)


def test_template_generation():
    tmpl_cust = ConfigLoader.get_template("customer")
    assert "customer_id" in tmpl_cust
    cfg = ConfigLoader.load_from_string(tmpl_cust)
    assert "email" in cfg.columns
