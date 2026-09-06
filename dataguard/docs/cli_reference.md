# DataGuard CLI Reference

The DataGuard CLI is built with `Typer` and `Rich` to provide developer-friendly data quality validation directly from the terminal.

---

## 🚀 Commands

### 1. `dataguard validate`
Validate a data source against quality rules.

```bash
dataguard validate <source> [OPTIONS]
```

**Options:**
- `--config`, `-c`: Path to YAML or JSON validation rules file.
- `--format`, `-f`: Output format: `console` (default), `html`, `json`, `markdown`.
- `--output`, `-o`: File path to save the generated report.
- `--fail-on`: Minimum severity triggering exit code 1 (`low`, `medium`, `high`, `critical`).
- `--min-score`: Minimum overall quality score required to pass gate (0 - 100).
- `--baseline`, `-b`: Baseline profile JSON file for anomaly and drift detection.
- `--table`: SQL table name (for database connections).
- `--query`: Custom SQL query (for database connections).

**Examples:**
```bash
# Validate CSV with terminal report
dataguard validate data.csv --config rules.yaml

# Generate standalone HTML dashboard report
dataguard validate data.parquet --config rules.yaml --format html --output report.html

# Enforce strict CI/CD quality gate
dataguard validate data.csv --config rules.yaml --fail-on high --min-score 90
```

---

### 2. `dataguard profile`
Profile a dataset and generate statistical distributions.

```bash
dataguard profile <source> [OPTIONS]
```

**Options:**
- `--format`, `-f`: `console` (default), `json`, `html`.
- `--output`, `-o`: Save profile metrics to file.

---

### 3. `dataguard init`
Generate a starter rules configuration file.

```bash
dataguard init --output rules.yaml --template customer
```

**Templates:** `customer`, `ecommerce`, `basic`.

---

### 4. `dataguard check-rules`
Validate rule file syntax and schema.

```bash
dataguard check-rules rules.yaml
```

---

### 5. `dataguard serve`
Launch the FastAPI server and Web Dashboard.

```bash
dataguard serve --host 127.0.0.1 --port 8000
```
