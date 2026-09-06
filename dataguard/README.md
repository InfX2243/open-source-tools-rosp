<div align="center">

# 🛡️ DataGuard
### Open-Source Data Quality, Validation & Profiling Platform

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Polars](https://img.shields.io/badge/Powered%20By-Polars-CD792C.svg)](https://pola.rs)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![CI Tests](https://img.shields.io/badge/Tests-42%20Passed-10B981.svg)]()

*A lightweight, developer-first, open-source alternative to heavyweight data-quality platforms for teams that want fast validation, statistical profiling, rich reporting, and CI/CD quality gates without excessive infrastructure.*

</div>

---

## 📖 Table of Contents

- [Why DataGuard?](#-why-dataguard)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
  - [Installation](#1-installation)
  - [CLI Validation](#2-cli-validation)
  - [Interactive HTML Reports](#3-interactive-html-reports)
  - [Statistical Profiling](#4-statistical-profiling)
  - [Python SDK Usage](#5-python-sdk-usage)
- [Rule Configuration Guide](#-rule-configuration-guide)
- [Web Dashboard & REST API](#-web-dashboard--rest-api)
- [CI/CD Quality Gate Integration](#-cicd-quality-gate-integration)
- [Docker Deployment](#-docker-deployment)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing & License](#-contributing--license)

---

## 💡 Why DataGuard?

Data problems are frequently discovered only after corrupt or ill-formatted records reach downstream production warehouses, dashboards, or ML models. Developers often write ad-hoc scripts or struggle with complex, heavyweight enterprise frameworks.

**DataGuard provides:**
- **Lightning Speed**: Built on **Polars** for multi-threaded, memory-efficient data processing.
- **Developer Experience**: One CLI command, rich terminal panels, readable issue logs, and human-friendly exit codes.
- **Multi-Format Reporting**: Rich Console, Interactive Standalone HTML, JSON, and PR Markdown.
- **CI/CD Quality Gates**: Enforce validation rules with `--fail-on high` to prevent bad data deployments.
- **Zero Overhead**: Run as a simple Python CLI, import as a library, or deploy as a lightweight FastAPI microservice with Docker.

---

## 🏛️ Architecture

```
                         ┌────────────────────────┐
                         │   Developer / Pipeline │
                         └───────────┬────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
               CLI (Typer + Rich)              REST API (FastAPI)
                     │                               │
                     └───────────────┬───────────────┘
                                     ▼
                         ┌────────────────────────┐
                         │    DataGuard Core      │
                         │   Validation Engine    │
                         └───────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        Source Adapters         Rule Engine             Profiler
       CSV / Parquet / JSON    Validators & Custom      Distributions &
       PostgreSQL / MySQL      Pydantic v2 Models       Anomaly Detection
              └──────────────────────┼──────────────────────┘
                                     ▼
                         ┌────────────────────────┐
                         │    Scoring & Gates     │
                         └───────────┬────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ▼               ▼               ▼
                 Rich CLI      HTML Dashboard     Metadata DB
                  Report        (Standalone)       (History)
```

---

## ✨ Key Features

- **10+ Built-In Validators**: Non-Null / Required, Type Conformance (Int, Float, Bool, Date, DateTime), Uniqueness & Duplicate Rates, Min/Max/Between Ranges, Regex & Format Validation (Email, URL, UUID, IPv4, Phone, ISO Date), Allowed Whitelists, Disallowed Blacklists, and Custom Python Expressions.
- **Statistical Profiling**: Automatically calculates row counts, column types, null percentages, distinct counts, distributions, quartiles, and min/max/mean metrics.
- **Historical Drift & Anomaly Detection**: Compares runs against stored baseline profiles to flag sudden null rate spikes or row count shifts.
- **Weighted Quality Scoring**: Configurable rule weights and penalty curves produce transparent 0–100% scores.
- **Multi-Source Support**: Ingests CSV, TSV, JSON, NDJSON/JSONL, Parquet, SQLite, PostgreSQL, and MySQL.

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install from local package or PyPI
cd dataguard
pip install -e .
```

### 2. CLI Validation

Generate a starter rules configuration file:
```bash
dataguard init --output rules.yaml --template customer
```

Validate a dataset against the rules:
```bash
dataguard validate examples/data/customers.csv --config examples/rules/customer_rules.yaml
```

Output:
```
🛡️  DATAGUARD DATA QUALITY REPORT
Dataset: customers.csv   Rows: 10   Cols: 7   Duration: 8.2ms

QUALITY SCORE: 100.0%  [PASS]
Quality Gate: [PASSED] - All quality gates satisfied

Validation Rules Summary:
✓ PASS  min_rows[5]            <dataset>  HIGH  10  0  0.0%  Dataset row count 10 satisfies minimum 5
✓ PASS  required_columns_check <dataset>  HIGH   5  0  0.0%  All required columns are present
✓ PASS  required_check         customer_id CRIT 10  0  0.0%  All 10 records non-null
✓ PASS  type_check[integer]    customer_id CRIT 10  0  0.0%  All 10 checked values match type 'integer'
✓ PASS  unique_check           customer_id CRIT 10  0  0.0%  All 10 checked values are unique
✓ PASS  format_check[email]    email       HIGH 10  0  0.0%  All 10 checked values match pattern
✓ PASS  range_check            age         MED  10  0  0.0%  All 10 checked values within range [18, 120]
✓ PASS  allowed_check          status      HIGH 10  0  0.0%  All 10 checked values match permitted set
```

### 3. Interactive HTML Reports

Generate a standalone HTML dashboard report with charts, dark mode, and sample violation drill-downs:
```bash
dataguard validate examples/data/dirty_users.csv --config examples/rules/customer_rules.yaml --format html --output report.html
```

### 4. Statistical Profiling

Profile any dataset to inspect cardinality, null ratios, and column ranges:
```bash
dataguard profile examples/data/customers.csv
```

### 5. Python SDK Usage

```python
from dataguard import ValidationEngine, RuleConfig, ColumnRule

# Define rules programmatically
config = RuleConfig(
    dataset="customers.csv",
    columns={
        "customer_id": ColumnRule(type="integer", required=True, unique=True),
        "email": ColumnRule(required=True, format="email"),
        "age": ColumnRule(min=18, max=120),
        "status": ColumnRule(allowed=["active", "inactive", "pending"]),
    }
)

# Run validation
engine = ValidationEngine(config)
summary = engine.validate_source("examples/data/customers.csv")

print(f"Quality Score: {summary.quality_score}%")
print(f"Passed Gate: {summary.passed_gate}")
```

---

## 📝 Rule Configuration Guide

Rules are written in clean, declarative YAML:

```yaml
dataset: customers.csv
version: "1.0"
description: "Customer data quality constraints"

thresholds:
  fail_on: high             # Options: low, medium, high, critical
  min_quality_score: 85.0   # 0.0 - 100.0

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
    weight: 2.0

  email:
    type: string
    required: true
    format: email
    severity: high

  age:
    type: integer
    between: [18, 120]
    severity: medium

  status:
    type: string
    required: true
    allowed: [active, inactive, pending, suspended]
    severity: high
```

---

## 🌐 Web Dashboard & REST API

DataGuard comes with an embedded FastAPI REST service and single-page Web Dashboard:

```bash
dataguard serve --port 8000
```

- **Web Dashboard**: Visit `http://localhost:8000` to upload files, test rules live, and inspect historical runs.
- **OpenAPI Docs**: Visit `http://localhost:8000/docs` for interactive API testing.

---

## 🔄 CI/CD Quality Gate Integration

Prevent bad data from breaking production pipelines by adding DataGuard to GitHub Actions:

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Gate

on: [push, pull_request]

jobs:
  validate-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install DataGuard
        run: pip install dataguard

      - name: Enforce Data Quality Gate
        run: |
          dataguard validate data/customers.parquet \
            --config rules.yaml \
            --fail-on high \
            --min-score 90
```

If any rule with severity `>= high` fails or the overall score falls below 90%, DataGuard exits with non-zero code `1`, halting the CI workflow.

---

## 🐳 Docker Deployment

Run DataGuard and PostgreSQL with Docker Compose:

```bash
docker compose up -d
```

---

## 🧪 Testing

Run the full automated test suite (42 tests covering validators, source adapters, CLI, profiler, and API):

```bash
pytest tests/ -v
```

---

## 🗺️ Roadmap

- [x] **Phase 1: Core Engine** (Polars ingestion, Pydantic v2 schemas, 8 core validators)
- [x] **Phase 2: Reporters** (Rich Console, Standalone HTML, JSON, Markdown)
- [x] **Phase 3: Multi-Format Adapters** (CSV, Parquet, JSON, NDJSON, SQLite, PostgreSQL, MySQL)
- [x] **Phase 4: Profiling & Anomaly Detection** (Distributions, null tracking, baseline drift)
- [x] **Phase 5: REST API & Web Dashboard** (FastAPI, SQLite/PostgreSQL history store, Web Studio)
- [x] **Phase 6: CI/CD Quality Gates & Docker** (Exit code gates, GitHub Actions, Docker Compose)
- [ ] **Phase 7: Cloud Storage Connectors** (Amazon S3, Google Cloud Storage, Azure Blob)
- [ ] **Phase 8: Snowflake & BigQuery Connectors**
- [ ] **Phase 9: Slack & Webhook Alert Notifications**

---

## 📄 Contributing & License

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and development setup.

DataGuard is open-source software licensed under the **Apache-2.0 License**. See [LICENSE](LICENSE) for details.
