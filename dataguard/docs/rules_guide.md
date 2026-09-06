# DataGuard Quality Rules Guide

DataGuard rules are configured using declarative YAML or JSON format.

---

## 📋 Rule File Structure

```yaml
# Top-level dataset metadata
dataset: customers.csv
version: "1.0"
description: "Customer data quality constraints"

# Quality Gate Enforcement Settings
thresholds:
  fail_on: high             # Minimum severity that triggers non-zero exit: low, medium, high, critical
  min_quality_score: 85.0   # Minimum overall score required (0 - 100)

# Dataset-Wide Checks
dataset_checks:
  min_rows: 100
  max_rows: 1000000
  required_columns:
    - customer_id
    - email
    - signup_date

# Column-Specific Rules
columns:
  customer_id:
    type: integer           # integer, float, string, boolean, date, datetime
    required: true          # Disallows null or empty strings
    unique: true            # Disallows duplicate values
    min: 1                  # Minimum boundary
    severity: critical      # Violation severity: low, medium, high, critical
    weight: 2.0             # Scoring weight multiplier (0.1 to 10.0)

  email:
    type: string
    required: true
    format: email           # email, url, uuid, ipv4, phone, iso_date, alphanumeric
    severity: high

  age:
    type: integer
    between: [18, 120]      # Inclusive numeric range
    severity: medium

  status:
    type: string
    required: true
    allowed:                # Whitelist of permitted values
      - active
      - inactive
      - pending
      - suspended
    severity: high

  custom_code:
    type: string
    regex: "^CUST-[0-9]{5}$" # Custom regex pattern
    severity: high

  formula_check:
    custom_expr: "val > 0 and val % 2 == 0"  # Safe Python expression on 'val'
    severity: low
```

---

## 🎯 Built-in Validators Reference

| Validator Key | Property | Description | Example |
| :--- | :--- | :--- | :--- |
| `required` | `required: bool` | Checks that values are not null/None/empty | `required: true` |
| `max_null_rate` | `max_null_rate: float` | Maximum allowed proportion of nulls | `max_null_rate: 0.05` |
| `unique` | `unique: bool` | Checks that all values are distinct | `unique: true` |
| `type` | `type: string` | Checks data type conformance | `type: integer` |
| `range` | `min`, `max`, `between` | Numeric or date boundary bounds | `between: [0, 100]` |
| `format` | `format: string` | Standard format validation | `format: email` |
| `regex` | `regex: string` | Custom regular expression pattern | `regex: "^[A-Z]{3}$"` |
| `allowed` | `allowed: list` | Whitelist of permitted values | `allowed: [USD, EUR]` |
| `disallowed` | `disallowed: list`| Blacklist of forbidden values | `disallowed: [TEST, N/A]` |
| `custom` | `custom_expr: string` | Python boolean expression on `val` | `custom_expr: "len(val) == 8"` |
