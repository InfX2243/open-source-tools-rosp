# 🛡️ ContainerSec

> **Open-Source Container & Dockerfile Security Linter — CIS Benchmark Enforcement & Automated Remediation**

[![CI](https://github.com/open-source-tools/containersec/actions/workflows/ci.yml/badge.svg)](https://github.com/open-source-tools/containersec/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Docker: CIS Benchmark](https://img.shields.io/badge/CIS%20Benchmark-v1.6.0-green.svg)](https://www.cisecurity.org/)

---

## 🌟 Why ContainerSec?

Containers are the backbone of modern cloud deployments, but **over 60% of Dockerfiles in production contain dangerous misconfigurations**:
- Running containers as `root` (privilege escalation)
- Hardcoded API keys, database passwords, and private SSH keys
- Mutable tags like `:latest` causing unpredictable builds
- Insecure instructions like `ADD` downloading remote artifacts without integrity checks
- Missing `HEALTHCHECK` and cache cleanups leaving container images bloated and brittle

**ContainerSec** is an enterprise-grade static security scanner and auto-remediator for Dockerfiles. It audits your container builds against the **CIS Docker Benchmark**, scans for leaked secrets, assigns a letter grade (`A+` to `F`), and can **automatically fix** violations.

---

## 🚀 Key Features

- **🏛️ CIS Docker Benchmark Enforcement:** Out-of-the-box checks for CIS 4.1 (Non-root user), CIS 4.2 (Pinned tags), CIS 4.6 (Healthchecks), CIS 4.9 (COPY over ADD), CIS 4.11 (No SSH), and more.
- **🔑 Secret & Credential Detection:** Detects exposed AWS keys, tokens, database passwords, and private keys in `ENV`, `ARG`, `RUN`, and `COPY`.
- **🛠️ Automated Remediation (`containersec fix`):** Automatically injects non-root users, replaces `ADD` with `COPY`, prunes package caches, and inserts healthcheck templates.
- **📊 Multiple Report Formats:** Rich terminal tables, machine-readable JSON, HTML report, and **SARIF v2.1.0** for seamless GitHub Code Scanning integration.
- **🌐 Interactive Web Dashboard:** Clean, responsive Web UI with real Lucide icons, live scanner, auto-fix preview, and rule explorer.
- **🚦 CI/CD Quality Gates:** Define policies in `.containersec.yaml` and break builds on critical security regressions.

---

## 📦 Quickstart

### Installation

```bash
cd containersec
pip install -e .
```

### 1. Scan a Dockerfile

```bash
# Scan with rich terminal output
containersec scan Dockerfile

# Scan with SARIF output for GitHub Security Tab
containersec scan --format sarif -o report.sarif

# Enforce quality gate (fail if HIGH or CRITICAL issues exist)
containersec scan --fail-on HIGH
```

### 2. Auto-Fix Common Issues

```bash
# Dry run: view proposed remediations
containersec fix Dockerfile

# Apply fixes directly to file
containersec fix Dockerfile --write
```

### 3. Rule Catalog

```bash
containersec rules
```

### 4. Launch Web Dashboard

```bash
containersec serve --port 8002
```
Visit `http://localhost:8002` to use the interactive dashboard.

---

## 📋 Rules Reference

| Rule ID | Severity | Category | CIS Ref | Description |
| :--- | :---: | :---: | :---: | :--- |
| `CIS-4.1` | **HIGH** | CIS | CIS 4.1 | Ensure a non-root user is specified (`USER <user>`) |
| `CIS-4.2` | **MEDIUM** | CIS | CIS 4.2 | Avoid unpinned or `:latest` image tags |
| `CIS-4.6` | **LOW** | CIS | CIS 4.6 | Add `HEALTHCHECK` instruction to container image |
| `CIS-4.9` | **MEDIUM** | CIS | CIS 4.9 | Use `COPY` instead of `ADD` for files and directories |
| `CIS-4.11` | **CRITICAL** | CIS | CIS 4.11 | Do not expose SSH port 22 or install `openssh-server` |
| `CIS-4.12` | **LOW** | CIS | CIS 4.12 | Clean package manager cache (`/var/lib/apt/lists/*`) |
| `SEC-001` | **CRITICAL** | Secrets | CWE-798 | Hardcoded secret or credential detected in `ENV` / `ARG` |
| `SEC-002` | **CRITICAL** | Secrets | CWE-798 | Potential secret token leaked in `RUN` command |
| `SEC-003` | **CRITICAL** | Secrets | CWE-312 | Private SSH / RSA / PEM key copied into image |
| `SEC-BP-001` | **LOW** | Best Practice | - | Use minimal/slim base images (`-slim`, `-alpine`) |
| `SEC-BP-002` | **HIGH** | Best Practice | - | Avoid dangerous diagnostic tools in production (`netcat`, `gdb`) |
| `SEC-BP-005` | **HIGH** | Best Practice | CWE-78 | Dangerous remote script execution via `curl \| bash` |

---

## ⚙️ Configuration (`.containersec.yaml`)

```yaml
target_path: "Dockerfile"
severity_threshold: "LOW"

policy:
  max_critical: 0
  max_high: 0
  max_medium: 3
  min_score: 75
  fail_on_secrets: true

ignore_rules:
  # - CIS-4.6
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📄 License

ContainerSec is open source under the **Apache 2.0 License**. See [LICENSE](LICENSE) for details.
