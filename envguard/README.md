# 🛡️ EnvGuard — Environment & Secret Governance Suite

> **Developer-first CLI tool and Python library for environment variable drift prevention, `.env` schema validation, automated `.env.example` generation from codebase scanning, safe redacted environment diffing, and secret leakage prevention.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Pre-commit Hook](https://img.shields.io/badge/Pre--commit-Supported-brightgreen?logo=pre-commit)](.pre-commit-hooks.yaml)
[![ROSP Tools](https://img.shields.io/badge/Suite-ROSP%20Tools-orange)](../README.md)

---

## 📌 Why EnvGuard?

Almost every software engineering team encounters subtle configuration bugs and security liabilities:
- **`.env` Drift**: A developer introduces a new environment variable in code without updating `.env.example`. Teammates pull the branch and the application crashes mysteriously at runtime.
- **Accidental Secret Commits**: Production API keys, Stripe tokens, or AWS credentials get committed in staging files or `.env` templates.
- **Type Errors**: Port numbers are strings, boolean flags are misinterpreted, and database URLs have malformed schemas.
- **Unsafe Environment Diffing**: Comparing staging and production `.env` files exposes plaintext production credentials in console logs or shared screen sessions.

**EnvGuard fixes all of this with zero external servers and 100% client-side/local execution.**

---

## 🚀 Key Capabilities

1. **`check` — Drift & Schema Validation**
   - Validates `.env` against `.env.example` or declarative YAML schemas (`.env.schema.yaml`).
   - Flags missing variables, undocumented extra variables, empty keys, and semantic type mismatches (`port`, `boolean`, `url`, `email`, `integer`, `float`, `json`).
   - Flags unmasked live credentials and placeholder values (`your_key_here`, `changeme`).

2. **`generate` — Smart Codebase Scanner & Generator**
   - Scans your codebase across **Python**, **JavaScript/TypeScript**, **Go**, **PHP**, **Ruby**, and **Shell scripts**.
   - Extracts all referenced environment variables (e.g. `process.env.PORT`, `os.environ["DATABASE_URL"]`, `os.getenv(...)`).
   - Automatically generates a clean, sanitized `.env.example` with realistic placeholder values and file reference comments.

3. **`diff` — Safe Redacted Environment Comparison**
   - Compares two environment files (e.g., `staging.env` vs `prod.env`).
   - **Values are automatically redacted**: Displays key status (`MATCH`, `ADDED`, `REMOVED`, `MODIFIED`), byte length, and Shannon entropy without ever printing plaintext secrets.

4. **`scan-secrets` — Pre-Commit Secret Scanner**
   - Scans files or directories for unmasked live API credentials (AWS Access Keys, GitHub PATs, OpenAI Keys, Stripe Live Keys, Slack Tokens, Private Keys).
   - Designed for Git pre-commit hooks and CI/CD quality gates.

---

## 📦 Installation

```bash
cd envguard
pip install -e .
```

Or install with dev dependencies:
```bash
pip install -e ".[dev]"
```

---

## ⚡ Quickstart & CLI Commands

### 1. Check for Drift and Validation Issues
```bash
# Validate local .env against .env.example
envguard check

# Strict mode: fail build on undocumented extra keys or empty variables
envguard check --strict

# Export report to JSON or standalone HTML
envguard check --format html --output report.html
envguard check --format json --output report.json
```

### 2. Generate `.env.example` by Scanning Codebase
```bash
# Scan current project and write to .env.example
envguard generate

# Scan a specific directory and print to terminal
envguard generate --codebase ./src --print-only

# Sanitize an existing real .env into an .env.example template
envguard generate --source-env .env --output .env.example
```

### 3. Safely Compare Environments (Diff)
```bash
envguard diff staging.env prod.env
```

### 4. Scan Files for Secret Leaks
```bash
envguard scan-secrets .env
envguard scan-secrets ./src
```

---

## 🌐 Interactive Web Dashboard

EnvGuard includes a modern, glassmorphic dark-theme Web Dashboard served via FastAPI — no `npm install` or frontend build step required.

```bash
# Launch the dashboard (auto-opens browser)
envguard ui

# Custom port and no auto-open
envguard ui --port 9000 --no-open
```

Open **http://127.0.0.1:8765** in your browser. The dashboard features:

| Tab | Feature |
| :--- | :--- |
| 🛡️ **Drift & Audit** | Paste `.env` and `.env.example`, toggle strict mode, view severity tables and stat cards |
| 🔍 **Safe Redacted Diff** | Side-by-side environment comparison with entropy badges and masked previews |
| ⚡ **Codebase Generator** | Paste source code, auto-discover variables, generate sanitized `.env.example` |
| 🚨 **Secret Scanner** | Detect AWS, Stripe, OpenAI, GitHub tokens, and private keys with remediation advice |

Click **"⚡ Load Demo Data"** in the header bar to instantly populate all tabs with sample data.

**REST API endpoints** are also available at `/api/check`, `/api/diff`, `/api/generate`, `/api/scan-secrets`, and `/api/health`.

---

## 🚦 Pre-commit Integration

Add EnvGuard to your `.pre-commit-config.yaml` to ensure zero broken builds or credential leaks reach your Git repository:

```yaml
repos:
  - repo: https://github.com/your-org/open-source-tools-rosp
    rev: v1.0.0
    hooks:
      - id: envguard-check
      - id: envguard-secrets
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📄 License

MIT License. Part of the [ROSP Open-Source Tools Suite](../README.md).
