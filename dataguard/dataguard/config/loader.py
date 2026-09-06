"""Configuration loader and validator for YAML and JSON rule files."""

import os
import yaml
import json
from typing import Dict, Any, Optional
from dataguard.core.models import RuleConfig


class ConfigLoader:
    """Loads and validates DataGuard rule configuration files."""

    @classmethod
    def load_from_file(cls, path: str) -> RuleConfig:
        """Load and validate a rule config from a YAML or JSON file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return cls.load_from_string(content, filename=path)

    @classmethod
    def load_from_string(cls, content: str, filename: str = "config.yaml") -> RuleConfig:
        """Parse string content as YAML/JSON and validate into RuleConfig."""
        try:
            raw_data = yaml.safe_load(content)
        except Exception as e:
            raise ValueError(f"Failed to parse configuration file '{filename}': {e}")

        if not isinstance(raw_data, dict):
            raise ValueError(f"Invalid rule configuration format in '{filename}'. Expected a YAML/JSON dictionary.")

        try:
            return RuleConfig(**raw_data)
        except Exception as e:
            raise ValueError(f"Configuration schema validation error in '{filename}':\n{e}")

    @classmethod
    def get_template(cls, template_name: str = "basic") -> str:
        """Return a boilerplate starter YAML configuration string."""
        templates: Dict[str, str] = {
            "customer": """# DataGuard Validation Rules: Customer Data
dataset: customers.csv
version: "1.0"
description: "Quality rules and constraints for customer records"

thresholds:
  fail_on: high
  min_quality_score: 85.0

dataset_checks:
  min_rows: 10
  required_columns:
    - customer_id
    - email
    - age
    - status

columns:
  customer_id:
    type: integer
    required: true
    unique: true
    min: 1
    severity: critical
    description: "Unique integer customer identifier"

  email:
    type: string
    required: true
    format: email
    severity: high
    description: "Valid RFC-compliant email address"

  age:
    type: integer
    min: 18
    max: 120
    severity: medium
    description: "Customer age between 18 and 120"

  status:
    type: string
    required: true
    allowed:
      - active
      - inactive
      - pending
      - suspended
    severity: high

  signup_date:
    type: date
    required: false
    severity: low
""",
            "ecommerce": """# DataGuard Validation Rules: E-Commerce Transactions
dataset: transactions.csv
version: "1.0"
description: "Transaction and order validation rules"

thresholds:
  fail_on: high
  min_quality_score: 90.0

columns:
  order_id:
    type: string
    required: true
    unique: true
    regex: "^ORD-[0-9]{6}$"
    severity: critical

  amount:
    type: float
    required: true
    min: 0.01
    max: 100000.00
    severity: critical

  currency:
    type: string
    required: true
    allowed: [USD, EUR, GBP, CAD, AUD, JPY]
    severity: high

  customer_id:
    type: integer
    required: true
    min: 1
    severity: high

  discount_pct:
    type: float
    min: 0.0
    max: 100.0
    severity: medium
""",
            "basic": """# DataGuard Validation Rules
dataset: dataset.csv
version: "1.0"
description: "Basic tabular data validation rules"

thresholds:
  fail_on: high
  min_quality_score: 80.0

columns:
  id:
    type: integer
    required: true
    unique: true
    severity: critical

  name:
    type: string
    required: true
    severity: high

  created_at:
    type: datetime
    required: false
    severity: low
""",
        }
        return templates.get(template_name.lower(), templates["basic"])
