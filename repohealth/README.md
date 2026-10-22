# 🏥 RepoHealth — Repository Health & Open-Source Checklist Auditor

> **Audit any local or GitHub repository against open-source industry best practices. Award A-to-F health grades, interactive checklists, and 1-click template fixes.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python)-brightgreen)](https://python.org)
[![Web Studio](https://img.shields.io/badge/Web%20Studio-Live%20GitHub%20Audit-emerald)](./web/index.html)
[![Grading](https://img.shields.io/badge/Grade-A%2B%20to%20F-blueviolet)](./web/index.html)

---

## 📌 Overview

Open-source repositories often suffer from missing licenses, uninformative READMEs, neglected security reporting policies, or exposed configuration files. **RepoHealth** acts as a 360-degree quality auditor for any software project—evaluating documentation depth, legal licensing, Git hygiene, and CI/CD automation.

It runs as a **zero-dependency Python CLI** or through an interactive **Web Studio Dashboard** that can audit live GitHub repositories or local folders.

---

## 🌟 Key Capabilities

* **🌐 Interactive Web Studio Dashboard (`--ui`)**:
  * Enter any GitHub repository URL (e.g. `facebook/react`, `fastapi/fastapi`, or your own repos).
  * Queries GitHub's REST API and community profile to evaluate compliance.
  * Animated A-to-F Grade Gauge and category progress bars.
  * **1-Click Template Fixes**: Directly copy ready-to-use templates for `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.gitignore`, and issue templates!
  * **Export Options**: Download `REPO_HEALTH.md`, export as clean PDF, or copy badge Markdown for your README.
* **⚡ Zero External Dependencies**: Built with pure Python 3.8+ standard libraries (`argparse`, `pathlib`, `json`, `http.server`).
* **🎯 Comprehensive 100-Point Audit Engine**:
  * 📚 **Documentation (30 pts)**: README existence, depth (> 150 words), essential sections, contributing guide, code of conduct.
  * ⚖️ **Legal & Licensing (25 pts)**: Open-source license file, recognized SPDX identifier, `SECURITY.md` vulnerability reporting policy.
  * 🧼 **Git Hygiene (25 pts)**: Clean `.gitignore`, cache exclusion rules, zero exposed secret keys/credentials.
  * 🚀 **CI/CD & Automation (20 pts)**: Automated workflows (`.github/workflows/`), issue/PR templates.
* **🚦 CI/CD Quality Gates (`--fail-under`)**:
  * Enforce repository health in your pipelines: fail builds if the health score falls below your team's threshold (e.g. `--fail-under 85`).

---

## 🌐 Interactive Web Studio Dashboard (UI)

RepoHealth includes a modern dark-theme browser dashboard:

### 🚀 Steps to Run the Web Dashboard:

#### Method 1: Using the CLI Launcher
1. **Run the UI command in your terminal:**
   ```bash
   python repohealth/repohealth.py --ui
   ```
   *(Or specify a custom port: `python repohealth/repohealth.py --ui --port 9000`)*

2. **Open in your browser:**
   The dashboard will automatically open at:
   ```text
   http://localhost:8899
   ```

3. **Audit any repository:**
   * Enter any GitHub repository link (e.g. `facebook/react`) or click a preset chip.
   * Click **"⚡ Audit Repository Health"**.
   * Review your letter grade (`A+` to `F`), category bars, and 1-click template fixes.
   * Download the `REPO_HEALTH.md` report or export to PDF!

---

#### Method 2: Direct In-Browser (No Terminal / No Python Needed!)
Because the dashboard is built with pure web standards:
1. Open your file manager and navigate to `repohealth/web/`.
2. **Double-click [`repohealth/web/index.html`](./web/index.html)** in Chrome, Edge, or Firefox.
3. The dashboard loads instantly and connects directly to GitHub's REST API!

---

## ⚡ CLI Usage & Commands

### 1. Audit Current Repository
```bash
python repohealth/repohealth.py .
```

### 2. Generate Markdown Audit Report
```bash
python repohealth/repohealth.py . --output REPO_HEALTH.md
```

### 3. Generate README Badge Markdown
```bash
python repohealth/repohealth.py . --badge
```
*Output:*
```markdown
[![RepoHealth](https://img.shields.io/badge/RepoHealth-A%2B%20(95.0%25)-brightgreen)](#)
```

### 4. Machine-Readable JSON Export
```bash
python repohealth/repohealth.py . --json -o health.json
```

---

## 📖 CLI Flags & Options

```text
usage: repohealth [-h] [--ui] [--port PORT] [-o OUTPUT]
                  [--badge] [--json] [--fail-under FAIL_UNDER]
                  [target]
```

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `target` | | `.` | Directory path of the repository to audit. |
| `--ui` | `--dashboard` | `False` | Launch interactive Web Studio Dashboard in browser. |
| `--port` | | `8899` | Port number for the Web Dashboard server. |
| `--output` | `-o` | *stdout* | Save Markdown report to file (e.g. `REPO_HEALTH.md`). |
| `--badge` | | `False` | Print only the Markdown badge snippet for README.md. |
| `--json` | | `False` | Output audit results as machine-readable JSON. |
| `--fail-under` | | `0` | Exit with code 2 if score is under threshold (e.g. 80). |

---

## 🤖 CI/CD Quality Gate Example

Add this step to your GitHub Actions workflow to ensure your repository stays healthy:

```yaml
name: 🏥 Repository Health Check

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run RepoHealth Audit
        run: |
          python repohealth/repohealth.py . --fail-under 80 --output REPO_HEALTH.md
```

---

## 🧪 Running Unit Tests

RepoHealth includes a self-contained unit test suite testing audit checks, scoring, and report rendering:

```bash
python repohealth/tests/test_repohealth.py
```
