# ✒️ GitScribe — Automated Git Changelog & Release Notes Generator

> **Transform messy Git commit histories into structured, easy-to-read Markdown changelogs, PDF release notes, and machine-readable JSON.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python)-brightgreen)](https://python.org)
[![Web Studio](https://img.shields.io/badge/Web%20Studio-HTML5%20%7C%20Fast%20Preview-purple)](./web/index.html)
[![PDF Export](https://img.shields.io/badge/Export-Markdown%20%7C%20PDF%20%7C%20JSON-orange)](./web/index.html)

---

## 📌 Overview

Writing release notes and keeping `CHANGELOG.md` updated before every release or Git tag is repetitive, manual, and often forgotten. **GitScribe** automates this entirely with **zero external dependencies**—running directly via the standard Python runtime or through an interactive Web Studio.

It inspects local or remote GitHub commit history, understands [Conventional Commits](https://www.conventionalcommits.org/), extracts breaking changes, links issues and PRs, and outputs clean, scannable **Markdown Tables** and **PDF release documents**.

---

## 🌟 Key Capabilities

* **🌐 Interactive Web Studio Dashboard (`--ui`)**:
  * Paste any GitHub repository link (e.g. `facebook/react`, `fastapi/fastapi`, or your own projects).
  * Fetches commits directly via GitHub's public REST API.
  * Live visual metrics: Commits count, Features, Bug Fixes, and Contributors.
  * **One-Click Downloads**: Download `CHANGELOG.md` or export directly as a styled **PDF document**!
* **⚡ Zero Dependencies**: Pure Python 3.8+ using standard library modules (`subprocess`, `argparse`, `http.server`, `re`, `json`). No external pip dependencies required.
* **🪝 Zero-Command Git Hook (`--install-hook`)**:
  * One-time setup connects GitScribe to Git's `post-commit` lifecycle.
  * Every time you run `git commit`, `CHANGELOG.md` **automatically updates itself** in the background!
* **👀 Real-Time Watcher (`--watch`)**:
  * Background daemon that detects new commits in real time and refreshes changelogs immediately.
* **📊 Easy-to-Read Markdown Tables**:
  * Formats categories into clean, readable tables with component scopes, descriptions, short commit links, and author attribution.
* **Conventional Commits Engine**:
  * Automatically categorizes: `feat`, `fix`, `perf`, `security`, `docs`, `refactor`, `style`, `test`, `build`, `ci`, and `chore`.
  * Detects **Breaking Changes** (`feat!:`, `BREAKING CHANGE:`) and pins them at the top.
* **Intelligent Prepend (`-p` / `--prepend`)**:
  * Inserts the new release block right under the title of an existing `CHANGELOG.md`, preserving past version history.
* **GitHub Release Drafts (`--release-notes`)**:
  * Outputs only the current release block for direct pasting into GitHub Releases or CI/CD pipelines.

---

## 🌐 Interactive Web Studio Dashboard (UI)

GitScribe includes a modern, glassmorphic **Web Studio Dashboard** that lets you fetch commits from any GitHub repository, preview changelogs in real time, and export directly as Markdown or PDF documents—all with **zero external dependencies**.

### 🚀 Steps to Launch and Use the Web UI:

#### Method 1: Using the CLI Launcher (Recommended)

1. **Run the UI command in your terminal:**
   ```bash
   python gitscribe/gitscribe.py --ui
   ```
   *(Or specify a custom port: `python gitscribe/gitscribe.py --ui --port 9000`)*

2. **Open in your browser:**
   GitScribe will automatically launch your default browser to:
   ```text
   http://localhost:8787
   ```

3. **Generate your changelog:**
   * **Step A:** Paste any GitHub repository link (e.g. `facebook/react`, `fastapi/fastapi`, or your own repo URL) or click one of the quick preset chips.
   * **Step B:** Choose your release version (e.g., `v1.0.0`) and layout (**Clean Table** or **Bulleted List**).
   * **Step C:** Click **"⚡ Fetch Commits & Generate Changelog"**.

4. **Export & Download:**
   * 📥 Click **"Download .md"** to save the formatted `CHANGELOG.md` file.
   * 🖨️ Click **"Export PDF"** to generate an executive-ready PDF release report.
   * 📋 Click **"Copy"** to copy raw Markdown to your clipboard.

5. **To stop the web server:**
   Press **`Ctrl + C`** in your terminal.

---

#### Method 2: Direct In-Browser (No Terminal / No Python Needed!)

Because the dashboard is built with pure web standards (HTML5/CSS/Vanilla JS):
1. Open your file manager and navigate to the `gitscribe/web/` folder.
2. **Double-click [`gitscribe/web/index.html`](./web/index.html)** (or drag and drop it into Chrome, Edge, Firefox, or Safari).
3. The dashboard will load instantly and connect directly to GitHub's REST API!

---

```text
┌────────────────────────────────────────────────────────────────────────┐
│  ✒️ GitScribe Studio                                          [v1.0.0]  │
├────────────────────────────────────────────────────────────────────────┤
│  🔗 Enter GitHub Repository Link:                                      │
│  [ https://github.com/owner/repository                              ]  │
│                                                                        │
│  Presets: [ ⚛️ React ]  [ 🚀 FastAPI ]  [ ⚡ Vite ]  [ 💻 VS Code ]     │
│                                                                        │
│  [ ⚡ Fetch Commits & Generate Changelog ]                             │
├────────────────────────────────────────────────────────────────────────┤
│  📊 Stats:  12 Commits  •  8 Features  •  1 Fix  •  3 Contributors     │
│                                                                        │
│  [👁️ Preview] [📄 Raw Markdown]  │  [📥 Download .md]  [🖨️ Export PDF]│
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start & CLI Usage

If you prefer using the command line instead of the Web UI:

### 1. Launch the Web Studio
```bash
python gitscribe/gitscribe.py --ui
```

### 2. Generate Table-Formatted Changelog via CLI
```bash
# Generate changelog from unreleased commits directly into CHANGELOG.md
python gitscribe/gitscribe.py --version v1.0.0 --output CHANGELOG.md
```

### 3. Auto-Update on Every Git Commit (Zero-Command Automation)
```bash
# Install Git post-commit hook (one-time command)
python gitscribe/gitscribe.py --install-hook

# Now make your normal commit:
git commit -m "feat(ui): add dark mode toggle"
# ✨ CHANGELOG.md updates automatically in the background without typing any commands!
```

### 4. Run Real-Time Background Watcher
```bash
python gitscribe/gitscribe.py --watch
```

---

## 🛠️ How to Add GitScribe to ANY Local Project / Idle Folder

Follow these 3 simple steps to add automated changelogs to any repository on your computer:

### Step 1: Copy `gitscribe` into Your Project
Copy the `gitscribe/` directory directly into the root of your project:
```bash
cp -r /path/to/gitscribe ./gitscribe
```

### Step 2: Enable the Auto-Updating Git Hook
Inside your project terminal, run:
```bash
python gitscribe/gitscribe.py --install-hook
```
*Done! Every commit you make from now on will automatically update `CHANGELOG.md`.*

### Step 3: Access GitScribe Anytime
* **Generate a new release:** `python gitscribe/gitscribe.py --version v2.0.0 -p`
* **Open the Web Studio:** `python gitscribe/gitscribe.py --ui`
* **Watch in real-time:** `python gitscribe/gitscribe.py --watch`

---

## 📖 CLI Flags & Options Reference

```text
usage: gitscribe [-h] [--ui] [--port PORT] [--install-hook] [--uninstall-hook]
                 [-w] [-q] [-v VERSION] [--style {table,list}]
                 [--since SINCE] [--until UNTIL] [-o OUTPUT] [-p]
                 [--release-notes] [--repo REPO] [--include-merges]
                 [--hide-authors] [--json] [--all]
```

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--ui` | `--dashboard` | `False` | Launch the interactive Web Studio in your browser. |
| `--port` | | `8787` | Port for the Web Studio server. |
| `--install-hook` | | `False` | Installs Git post-commit hook for zero-command automatic changelog updates. |
| `--uninstall-hook` | | `False` | Removes the Git post-commit hook. |
| `--watch` | `-w` | `False` | Runs real-time background watcher that refreshes changelogs on new commits. |
| `--version` | `-v` | `1.0.0` | Release version tag (e.g. `v1.2.0`). |
| `--style` | | `table` | Layout format: `table` (clean Markdown tables, default) or `list` (bullet points). |
| `--output` | `-o` | `CHANGELOG.md`| Path to write output markdown. |
| `--prepend` | `-p` | `False` | Prepend new release block to existing changelog without overwriting history. |
| `--release-notes`| | `False` | Output only the release notes section (for GitHub Releases or CI/CD). |
| `--since` | | Latest Tag | Starting Git tag/commit. If omitted, uses the latest tag. |
| `--until` | | `HEAD` | Ending Git tag/commit. |
| `--repo` | | Auto-detected| Custom repo URL for commit/PR links (e.g. `https://github.com/org/repo`). |
| `--include-merges`| | `False` | Include merge commits in output. |
| `--hide-authors` | | `False` | Omit `@author` attribution from commit entries. |
| `--json` | | `False` | Output machine-readable JSON object. |
| `--quiet` | `-q` | `False` | Suppress console output (used by background hooks). |
| `--all` | | `False` | Parse all commits in the repository history. |

---

## 📊 Example Generated Table Output

Here is what the table-formatted `CHANGELOG.md` looks like:

```markdown
# 📜 Project Changelog

> All notable changes and version milestones for this repository are documented here.

---

## 🏷️ [v1.0.0] — 2026-10-18

> 📦 **Release:** `v1.0.0` • 📅 **Date:** `2026-10-18` • 🔨 **Commits:** `12` • 👥 **Contributors:** `3`

### 🚀 New Features & Tools

| Component | Description | Commit | Author |
| :--- | :--- | :---: | :--- |
| `envguard` | Add EnvGuard tool and integrate with suite documentation | [`2116146`](https://github.com/...) | [@yashfeenraavi09](https://github.com/...) |
| `curlcraft, svg2jsx` | Add curlcraft and svg2jsx tools | [`34f4fe4`](https://github.com/...) | [@Zainab-013](https://github.com/...) |
| `TreeSnapshot` | Add directory structure generator | [`f1d0657`](https://github.com/...) | [@InfX2243](https://github.com/...) |

### 🐛 Bug Fixes & Stability

| Component | Description | Commit | Author |
| :--- | :--- | :---: | :--- |
| `ScaffoldTree` | Fix directory nesting problem | [`bc40e97`](https://github.com/...) | [@InfX2243](https://github.com/...) |

### 👥 Contributors

Thank you to our contributors for this release: [@InfX2243](https://github.com/InfX2243), [@yashfeenraavi09](https://github.com/yashfeenraavi09), [@Zainab-013](https://github.com/Zainab-013)!
```

---

## 🤖 GitHub Actions Automated Cloud Sync

To automatically update `CHANGELOG.md` on GitHub every time you push, add this workflow file to `.github/workflows/auto-changelog.yml`:

```yaml
name: 📜 Auto Update Changelog

on:
  push:
    branches:
      - main
    paths-ignore:
      - 'CHANGELOG.md'
      - '.gitignore'

jobs:
  update-changelog:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run GitScribe
        run: |
          python gitscribe/gitscribe.py --output CHANGELOG.md

      - name: Auto-Commit & Push Updated Changelog
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "docs(changelog): auto-update CHANGELOG.md [skip ci]"
          file_pattern: 'CHANGELOG.md'
```

---

## 🧪 Running Tests

GitScribe includes a self-contained unit test suite testing commit parsing, breaking changes, table rendering, and prepend mode:

```bash
python gitscribe/tests/test_gitscribe.py
```
