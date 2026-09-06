# DataDiff

> **Semantic Git-Diff for Data, Schemas & Statistics**  
> Fast, explainable dataset comparisons across CSV, JSON, Parquet, and SQL databases.

[![CI](https://github.com/InfX2243/open-source-tools-rosp/actions/workflows/ci.yml/badge.svg)](https://github.com/InfX2243/open-source-tools-rosp/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://pypi.org/project/datadiff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Overview

**DataDiff** is an open-source Data Engineering and developer tool designed to compare datasets and explain precisely **what changed** between two versions.

Traditional text diff tools fail on tabular data because row orders change, numbers have slight floating point variations, and schemas evolve. DataDiff treats tabular data semantically:
- **Row-Level Diff**: Identifies exact records added, removed, and modified.
- **Field-Level Diff**: Pinpoints specific changed values (e.g. `age: 22 -> 23`).
- **Schema Migration Detection**: Tracks added/removed columns and data-type changes (e.g. `int32 -> int64`).
- **Statistical Drift & Null Rates**: Alerts when NULL counts surge or numeric averages drift.
- **CI/CD Quality Gates**: Enforces strict deployment policies to break builds on unexpected data breaking changes.

---

## 2. Quick Start (2 Minutes)

### Installation
```bash
pip install datadiff
```

### CLI Usage

#### Compare Two Datasets
```bash
# Compare CSV datasets by primary key
datadiff compare old.csv new.csv --key id

# Compare Parquet datasets with numeric float tolerance
datadiff compare baseline.parquet current.parquet --key customer_id --tolerance 0.001

# Output as Interactive HTML Report
datadiff compare old.csv new.csv --key id --format html --output report.html

# Output as JSON or Markdown (for GitHub PR comments)
datadiff compare old.csv new.csv --key id --format json
datadiff compare old.csv new.csv --key id --format markdown
```

#### Schema & Profile Commands
```bash
# Inspect only schema column differences
datadiff schema old.csv new.csv

# Analyze statistical drift & NULL percentage shifts
datadiff profile old.csv new.csv

# Generate a starter YAML config
datadiff init
```

---

## 3. Web Dashboard & REST API

Launch the interactive local Web UI and FastAPI server with one command:
```bash
datadiff serve --port 8001
```
Open **http://127.0.0.1:8001** in your browser to access:
- **Interactive Side-by-Side Visual Diff Viewer**
- **1-Click Quick Demo Runners**
- **File Upload Dropzones (CSV / JSON / Parquet)**
- **Schema & Statistics Drift Tabs**
- **Persistent Run History**

---

## 4. CI/CD Pipeline Quality Gate Integration

Prevent silent pipeline corruptions in GitHub Actions or Airflow:

```yaml
# datadiff.yaml
source:
  path: "data/source.csv"

target:
  path: "data/target.csv"

key:
  - customer_id

policies:
  allow_schema_changes: false
  allow_column_removal: false
  max_removed_rows: 0
  max_modified_pct: 10.0
  max_null_rate_increase: 5.0
```

Run in CI:
```bash
datadiff compare source.csv target.csv --config datadiff.yaml
```
*(Returns exit code 0 on pass, exit code 1 on policy violation).*

---

## 5. Python Library API

```python
import polars as pl
from datadiff import DataDiffEngine, DiffConfig

df_old = pl.read_csv("old.csv")
df_new = pl.read_csv("new.csv")

diff = DataDiffEngine.compare_sources(
    source=df_old,
    target=df_new,
    key="customer_id",
)

print(f"Added: {diff.row_diff.added_count}")
print(f"Removed: {diff.row_diff.removed_count}")
print(f"Modified: {diff.row_diff.modified_count}")
```

---

## 6. Architecture & Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Core Engine** | Python + Polars | Vectorized anti-joins & inner joins for row comparison |
| **Models & Config** | Pydantic v2 | Strictly typed configuration and structured diff outputs |
| **CLI** | Typer + Rich | Color-coded terminal panels, git-diff formatting |
| **API** | FastAPI + Uvicorn | High-performance REST service for dataset diffing |
| **Metadata Store** | SQLite + SQLAlchemy | Comparison run history persistence |
| **Web Dashboard** | Vanilla CSS + HTML5 + JS | Fast, lightweight Light Theme dashboard with Lucide vector icons |
| **Testing** | Pytest | Unit and integration test suite |

---

## 7. License

MIT License. See [LICENSE](LICENSE) for details.
