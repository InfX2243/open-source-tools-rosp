"""Configuration loader for DataDiff."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

import yaml

from datadiff.core.models import DiffConfig


class ConfigLoader:
    """Loads and validates DataDiff YAML and JSON configuration files."""

    @classmethod
    def load_from_file(cls, path: Union[str, Path]) -> DiffConfig:
        """Load configuration from a YAML or JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        text = file_path.read_text(encoding="utf-8")
        if file_path.suffix.lower() in (".yaml", ".yml"):
            raw_data = yaml.safe_load(text) or {}
        elif file_path.suffix.lower() == ".json":
            raw_data = json.loads(text)
        else:
            # Attempt YAML first, fallback to JSON
            try:
                raw_data = yaml.safe_load(text) or {}
            except Exception:
                raw_data = json.loads(text)

        return cls.load_from_dict(raw_data)

    @classmethod
    def load_from_dict(cls, data: Dict[str, Any]) -> DiffConfig:
        """Validate and construct DiffConfig from a dictionary."""
        return DiffConfig.model_validate(data)

    @staticmethod
    def generate_starter_yaml() -> str:
        """Generate a starter YAML template for comparison configuration."""
        return """# DataDiff Comparison Configuration Template
# Version 1.0

source:
  path: "data/source.csv"
  format: "csv"

target:
  path: "data/target.csv"
  format: "csv"

# Primary key column(s) used to match records between source and target
key:
  - id

# Columns to exclude from comparison
ignore_columns:
  - updated_at
  - last_login

# Value normalization rules
rules:
  numeric_tolerance: 0.001
  case_sensitive: false
  trim_whitespace: true
  ignore_nan_vs_null: true

# CI/CD Quality Gate Policies
policies:
  allow_schema_changes: false
  allow_column_removal: false
  max_removed_rows: 0
  max_modified_pct: 15.0
  max_null_rate_increase: 5.0
  max_critical_discrepancies: 0

# Statistical comparison configuration
stats_config:
  track_null_rates: true
  track_distinct_counts: true
  track_numerical_drift: true
  drift_alert_pct: 10.0
"""
