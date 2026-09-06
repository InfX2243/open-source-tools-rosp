# 🛠️ ROSP Open-Source Tools Suite (`open-source-tools-rosp`)

> **A curated collection of developer-first, high-performance open-source tools designed for Cloud Security, Data Engineering, Scaffolding, Developer Utilities, and Web Productivity.**

[![License: Apache 2.0 / MIT](https://img.shields.io/badge/License-Open%20Source-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Polars Engine](https://img.shields.io/badge/Data%20Engine-Polars-orange)](https://pola.rs)
[![React & Vite](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?logo=react&logoColor=black)](https://vitejs.dev)
[![Docker & Cloud Native](https://img.shields.io/badge/Cloud%20Native-Docker%20%7C%20CIS-2496ED?logo=docker&logoColor=white)](https://docker.com)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Suite Tool Matrix](#-suite-tool-matrix)
- [Detailed Tool Breakdown](#-detailed-tool-breakdown)
  - [1. 🛡️ ContainerSec — Container Security & CIS Linter](#1-️-containersec--container-security--cis-linter)
  - [2. 🔍 DataDiff — Semantic Dataset & Schema Comparison](#2--datadiff--semantic-dataset--schema-comparison)
  - [3. 🚀 DataGuard — Data Quality, Validation & Profiling](#3--dataguard--data-quality-validation--profiling)
  - [4. ✨ JSON Formatter & Visualizer — Web Utility & Tree Inspector](#4--json-formatter--visualizer--web-utility--tree-inspector)
  - [5. 🏗️ ScaffoldTree — Tree-to-Filesystem Scaffolding Generator](#5-️-scaffoldtree--tree-to-filesystem-scaffolding-generator)
  - [6. 📸 TreeSnapshot — Filesystem-to-Tree Markdown Documentation](#6--treesnapshot--filesystem-to-tree-markdown-documentation)
- [ScaffoldTree + TreeSnapshot Workflow](#-the-scaffoldtree--treesnapshot-duo)
- [Repository Structure](#-repository-structure)
- [Local Setup & Testing Guide](#-local-setup--testing-guide)
- [CI/CD & Production Integration](#-cicd--production-integration)
- [Contributing & Community](#-contributing--community)

---

## 🌟 Overview

The **ROSP Open-Source Tools Suite** solves real-world pain points across modern software development, security auditing, data pipelines, and project management. Instead of relying on bloated, heavyweight enterprise software or unsafe third-party web utilities, this repository provides **modular, lightweight, zero-bloat utilities** that run via:
- 💻 **Command Line Interfaces (CLI)** for immediate developer feedback
- 📦 **Python Libraries & SDKs** for programmatic integration
- 🌐 **Interactive Web Interfaces & Dashboards**
- 🚦 **Automated CI/CD Quality Gates** (GitHub Actions, GitLab CI)

---

## 📊 Suite Tool Matrix

| Tool | Primary Domain | Core Tech Stack | Primary Value & Use Case | Folder |
| :--- | :--- | :--- | :--- | :--- |
| **[ContainerSec](./containersec)** | Cloud & Container Security | Python, Rich, SARIF, Jinja2 | Audits Dockerfiles against CIS benchmarks, detects exposed secrets, and auto-remediates security flaws. | [`/containersec`](./containersec) |
| **[DataDiff](./datadiff)** | Data Engineering & ETL | Python, DuckDB / Polars, Rich | Semantic Git-diff for datasets; pinpoints row additions, removals, field modifications, schema migrations, and statistical drift. | [`/datadiff`](./datadiff) |
| **[DataGuard](./dataguard)** | Data Quality & Governance | Python, Polars, FastAPI, HTML5 | Ultra-fast data profiling & rule validation with interactive HTML reports and REST API microservice. | [`/dataguard`](./dataguard) |
| **[JSON Formatter](./json-formatter)** | Developer Utilities & Web | React 18, Vite, Lucide Icons | 100% client-side privacy-first JSON formatter, syntax repair engine, converter, and collapsible tree viewer. | [`/json-formatter`](./json-formatter) |
| **[ScaffoldTree](./ScaffoldTree)** | Scaffolding & Project Setup | Python 3.8+ (Zero Deps) | Generates entire folder and file structures on disk directly from text/ASCII tree diagrams. | [`/ScaffoldTree`](./ScaffoldTree) |
| **[TreeSnapshot](./TreeSnapshot)** | Documentation & Tooling | Python 3.8+ (Zero Deps) | Traverses any directory and captures an accurate, clean Markdown-friendly tree with `.treeignore` support. | [`/TreeSnapshot`](./TreeSnapshot) |

---

## 🔍 Detailed Tool Breakdown

### 1. 🛡️ ContainerSec — Container Security & CIS Linter
> *Static security scanner and automated remediator for Dockerfiles and container configurations.*

#### 💡 Why It Is Useful
More than 60% of container images in production contain critical misconfigurations—such as running as `root`, using mutable `:latest` tags, leaving SSH ports open, or embedding plain-text API credentials. ContainerSec acts as a static security guardian before code is ever built or pushed to a container registry.

#### 🚀 Key Capabilities
- **CIS Benchmark Enforcement**: Validates rules against CIS Docker Benchmark v1.6.0 (Non-root user, pinned tags, healthchecks, `COPY` over `ADD`, package cache hygiene).
- **Secret & Key Detection**: Catches leaked AWS tokens, private keys, database passwords, and environment secrets in `ENV` / `ARG` / `RUN` instructions.
- **Automated Remediation (`containersec fix`)**: Can automatically rewrite Dockerfiles to insert non-root users, substitute secure commands, and inject healthchecks.
- **Multi-Format Export**: Terminal tables, machine-readable JSON, interactive HTML reports, and **SARIF v2.1.0** for direct integration with GitHub's Security Tab.
- **Web UI & Scanner**: Comes with an interactive web dashboard for real-time rule inspection and visual scanning.

#### ⚡ Quick Command
```bash
cd containersec
pip install -e .

# Scan a Dockerfile with strict severity check
containersec scan Dockerfile --fail-on HIGH

# Automatically fix common violations
containersec fix Dockerfile --output Dockerfile.hardened
```

---

### 2. 🔍 DataDiff — Semantic Dataset & Schema Comparison
> *Semantic Git-diff for tabular data, schemas, and statistical distributions.*

#### 💡 Why It Is Useful
Standard text diff tools (`diff`, `git diff`) fail on tabular data because record order can shift, float numbers have rounding differences, and columns reorder. DataDiff understands data semantically: it maps primary keys, compares row values, detects column data-type changes, and alerts you when null percentages shift unexpectedly.

#### 🚀 Key Capabilities
- **Row-Level & Field-Level Reconciliation**: Distinguishes between newly added rows, deleted rows, and modified values with precise cell-level diffs (`status: PENDING -> ACTIVE`).
- **Schema Migration Analysis**: Flags column additions, removals, renamings, and type widening/narrowing (e.g. `int32` to `string`).
- **Statistical Drift & Null Tracking**: Monitors changes in mean, median, standard deviation, and spikes in missing data.
- **CI/CD Quality Gate**: Returns distinct exit codes to fail automated data pipeline builds if critical drift or row discrepancies exceed tolerances.
- **Supported Formats**: CSV, Parquet, JSON, and SQL database connections.

#### ⚡ Quick Command
```bash
cd datadiff
pip install -e .

# Compare two dataset versions by primary key
datadiff compare baseline.csv current.csv --key id

# Generate an interactive HTML report
datadiff compare old.parquet new.parquet --key user_id --format html -o diff_report.html
```

---

### 3. 🚀 DataGuard — Data Quality, Validation & Profiling
> *Lightning-fast, Polars-powered data validation and statistical profiling engine.*

#### 💡 Why It Is Useful
Enterprise data validation tools (such as Great Expectations) can be complex to configure, heavy on dependencies, and slow on large files. DataGuard provides a lightweight, instant alternative: write a simple YAML rule file, validate gigabytes of data in seconds, and get interactive HTML reports or machine-readable JSON outputs.

#### 🚀 Key Capabilities
- **Polars Core Engine**: Multi-threaded, memory-efficient data processing handling millions of rows with minimal RAM overhead.
- **Declarative YAML Rules**: Define column expectations (uniqueness, null bounds, value ranges, regex patterns, enum sets) in concise YAML configs.
- **Automated Profiler**: Automatically profiles any dataset to calculate distributions, cardinality, quantiles, and anomalies without writing any code.
- **FastAPI Microservice & Dashboard**: Includes an integrated REST API for remote validation requests and a live web dashboard.
- **Pipeline Integration**: Drop-in step for Airflow, Prefect, dbt post-hooks, or GitHub Actions.

#### ⚡ Quick Command
```bash
cd dataguard
pip install -e .

# Profile a dataset automatically
dataguard profile dataset.csv --output profile.html

# Validate data against custom quality rules
dataguard validate dataset.csv --rules rules.yaml --fail-on high
```

---

### 4. ✨ JSON Formatter & Visualizer — Web Utility & Tree Inspector
> *Modern, 100% client-side JSON formatting, broken syntax repair, and tree visualization tool.*

#### 💡 Why It Is Useful
Developers constantly paste configuration files, API payloads, and database dumps into random online formatters, inadvertently exposing confidential customer tokens, credentials, or internal payload structures to third-party servers. The ROSP JSON Formatter runs completely client-side in the browser with zero external server calls, ensuring total data privacy.

#### 🚀 Key Capabilities
- **100% Client-Side Privacy**: No network requests; your sensitive payloads never leave your browser memory.
- **Dual-Pane Interactive UI**:
  - **Code Editor**: Real-time syntax validation, exact line/column error pointers, indent configuration (2 spaces, 4 spaces, tabs), and minification.
  - **Interactive Tree Visualizer**: Collapsible nested structures, datatype chips, key/value search filter, and path-copying (`payload.users[0].email`).
- **Auto-Fix Broken JSON**: Heuristically fixes trailing commas, unquoted property keys, and single-quoted strings with one click.
- **Format Converters**: Convert JSON payloads directly into **YAML, CSV, XML, or JavaScript objects**.
- **Iframe & Platform Embed Ready**: Supports `?embed=true` mode and `window.postMessage` communication for seamless embedding into parent dashboard portals.

#### ⚡ Quick Command
```bash
cd json-formatter
npm install
npm run dev
# Open http://localhost:5173 in your browser
```

---

### 5. 🏗️ ScaffoldTree — Tree-to-Filesystem Scaffolding Generator
> *Generates real directories and boilerplate files instantly from visual ASCII / text tree definitions.*

#### 💡 Why It Is Useful
When starting a new project, setting up architecture, or following design documentation, developers waste time executing repetitive `mkdir` and `touch` commands. ScaffoldTree lets you paste an ASCII file tree from documentation, LLM responses, or architecture plans and turns it into real directories and files on disk in milliseconds.

#### 🚀 Key Capabilities
- **Intuitive Convention**: Ends with `/` → creates a Directory. No trailing `/` → creates a File.
- **Zero External Dependencies**: Pure Python standard library (`os`, `sys`, `pathlib`).
- **Handles Nested & Indented Trees**: Understands Unicode box drawing characters (`├──`, `│`, `└──`) and simple indentation.
- **Safe & Non-Destructive**: Creates missing folders and files without wiping existing file content.

#### ⚡ Quick Command
```bash
cd ScaffoldTree

# Generate project structure from tree definition file
python structure_generator.py examples/web_app_structure.txt ./my-new-project
```

---

### 6. 📸 TreeSnapshot — Filesystem-to-Tree Markdown Documentation
> *Captures clean, formatted ASCII directory trees from existing folders for documentation and READMEs.*

#### 💡 Why It Is Useful
Documenting repository structure in READMEs and technical specifications is often manual and quickly falls out of sync. Traditional OS commands (`tree`) dump massive un-filtered outputs filled with `.git`, `node_modules`, `__pycache__`, and temporary caches. TreeSnapshot traverses directories, applies `.treeignore` filter patterns, and outputs clean Markdown compatible with documentation and ScaffoldTree.

#### 🚀 Key Capabilities
- **Markdown Ready**: Automatically outputs trees formatted in clean Markdown code blocks.
- **`.treeignore` & Wildcard Support**: Ignores junk folders (`.git`, `node_modules`, `dist`, `__pycache__`, `*.pyc`, `*.log`).
- **Bidirectional Compatibility**: Output format matches the exact syntax consumed by **ScaffoldTree**.
- **Zero Dependencies**: Pure Python standard library.

#### ⚡ Quick Command
```bash
cd TreeSnapshot

# Capture directory structure to directory_structure.md
python tree_snapshot.py ../my-web-app

# Exclude custom directories
python tree_snapshot.py ./project --ignore "temp/*,*.log"
```

---

## 🔄 The ScaffoldTree + TreeSnapshot Duo

Together, **TreeSnapshot** and **ScaffoldTree** form a complete, bi-directional project templating and documentation loop:

```text
               ┌───────────────────────┐
               │  Existing Filesystem  │
               └───────────┬───────────┘
                           │
                           ▼  (TreeSnapshot)
               ┌───────────────────────┐
               │   Markdown ASCII Tree │
               └───────────┬───────────┘
                           │
                           ▼  (ScaffoldTree)
               ┌───────────────────────┐
               │    New Filesystem     │
               └───────────────────────┘
```

1. **Capture**: Run `TreeSnapshot` on your reference project to capture its structure into Markdown.
2. **Share / Document**: Include the snapshot in documentation, architectural RFCs, or share with teammates.
3. **Scaffold**: Teammates run `ScaffoldTree` with that tree definition to replicate the project skeleton instantly.

---

## 📁 Repository Structure

```text
open-source-tools-rosp/
├── containersec/              # 🛡️ Dockerfile & Container Security Linter
│   ├── containersec/          # Core Python scanner, rules, fixers & reporters
│   ├── tests/                 # Unit & integration test suites
│   ├── examples/              # Sample vulnerable & hardened Dockerfiles
│   └── pyproject.toml         # Package build & dependency metadata
│
├── datadiff/                  # 🔍 Semantic Dataset Comparison Tool
│   ├── datadiff/              # Comparison algorithms, schema diff & engines
│   ├── tests/                 # Test suites for CSV, Parquet & JSON diffs
│   ├── examples/              # Sample dataset versions for demo comparisons
│   └── pyproject.toml         # Package build & dependency metadata
│
├── dataguard/                 # 🚀 Data Quality & Profiling Platform
│   ├── dataguard/             # Polars validation engine, rules & profiling
│   ├── api/                   # FastAPI microservice endpoints
│   ├── dashboard/             # Static dashboard assets
│   ├── tests/                 # Unit tests & rule verification tests
│   └── pyproject.toml         # Package build & dependency metadata
│
├── json-formatter/            # ✨ React + Vite JSON Web Application
│   ├── src/                   # React components (Tree, Editor, Converters)
│   ├── public/                # Static web assets
│   ├── package.json           # Dependencies & build scripts
│   └── vite.config.js         # Vite bundler configuration
│
├── ScaffoldTree/              # 🏗️ Tree-to-Filesystem Generator
│   ├── structure_generator.py # Core scaffolding engine (zero dependencies)
│   ├── examples/              # Sample tree definitions (.txt)
│   └── README.md              # ScaffoldTree documentation
│
├── TreeSnapshot/              # 📸 Filesystem-to-Tree Markdown Capture
│   ├── tree_snapshot.py       # Core snapshot engine (zero dependencies)
│   ├── .treeignore            # Default ignore rules
│   ├── directory_structure.md # Generated snapshot output
│   └── README.md              # TreeSnapshot documentation
│
└── README.md                  # Unified suite documentation (this file)
```

---

## 🧪 Local Setup & Testing Guide

### Prerequisites
- **Python**: Version 3.8 or newer
- **Node.js**: Version 18 or newer (with `npm`)

### 1. Python Data & Security Tools (`containersec`, `datadiff`, `dataguard`)

```bash
# Create and activate a virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Test ContainerSec
cd containersec && pip install -e . pytest && pytest && cd ..

# Test DataDiff
cd datadiff && pip install -e . pytest && pytest && cd ..

# Test DataGuard
cd dataguard && pip install -e . pytest && pytest && cd ..
```

### 2. Standalone Zero-Dependency Python Utilities (`ScaffoldTree`, `TreeSnapshot`)

```bash
# Test ScaffoldTree
cd ScaffoldTree
python structure_generator.py examples/web_app_structure.txt ./test-scaffold
cd ..

# Test TreeSnapshot
cd TreeSnapshot
python tree_snapshot.py ./my-web-app
cd ..
```

### 3. Frontend Tool (`json-formatter`)

```bash
cd json-formatter
npm install
npm run build   # Validates production compilation without errors
npm run dev     # Launches local development server at http://localhost:5173
```

---

## 🚀 CI/CD & Production Integration

All tools are engineered with strict exit codes, standard output formatting, and zero-interaction flags suitable for CI/CD automation:

```yaml
# Example GitHub Actions Workflow snippet
name: Quality & Security Gate
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      # 1. Audit Dockerfiles
      - name: Scan Dockerfile with ContainerSec
        run: |
          pip install ./containersec
          containersec scan Dockerfile --format sarif -o results.sarif --fail-on HIGH

      # 2. Check Data Quality
      - name: Validate Datasets with DataGuard
        run: |
          pip install ./dataguard
          dataguard validate data/production.csv --rules .dataguard.yaml --fail-on high
```

---

## 🤝 Contributing & Community

Contributions are welcomed across all tools in the suite:
- Add new CIS rules or remediations to **ContainerSec**
- Add SQL or columnar engines to **DataDiff**
- Expand validation rules in **DataGuard**
- Add converter options or visual themes to **JSON Formatter**
- Enhance tree parser syntax in **ScaffoldTree** & **TreeSnapshot**

### Contribution Steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add new capability'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Each sub-tool within this suite is distributed under recognized open-source licenses (Apache 2.0 / MIT). Please refer to the individual `LICENSE` files inside each tool directory for specific terms.
