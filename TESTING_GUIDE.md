# OpenForge Master Functional Testing & Screenshot Guide

This guide walks you through executing each of the 12 tools using the dedicated test fixtures located in [`sample_testing_suite/`](./sample_testing_suite). 

Drop your captured screenshots into the [`screenshots/`](./screenshots) directory. When you re-run `python generate_report_docx.py`, your images will automatically be embedded under **Section 4.3 (Figure 4.1 to Figure 4.12)** in the Word report!


---

## Tool 1: ContainerSec
* **Test Focus:** Static Dockerfile CIS Linter, Secret Detection & AST Fixer
* **Sample File:** [`sample_testing_suite/containersec_test/Dockerfile.test`](./sample_testing_suite/containersec_test/Dockerfile.test)
* **Execution Commands:**
  ```powershell
  cd containersec
  pip install -e .
  containersec scan ../sample_testing_suite/containersec_test/Dockerfile.test --fail-on HIGH
  containersec fix ../sample_testing_suite/containersec_test/Dockerfile.test -o Dockerfile.hardened
  ```
* **Screenshot Action:** Take a screenshot of the terminal showing the red/yellow CIS violations, secret key warning, and the auto-generated `Dockerfile.hardened`.
* **Save As:** `screenshots/test_containersec.png` (or `.jpg`)

---

## Tool 2: CurlCraft
* **Test Focus:** cURL Command Tokenization & Multi-Target Code Generation
* **Sample File:** [`sample_testing_suite/curlcraft_test/curl_sample.txt`](./sample_testing_suite/curlcraft_test/curl_sample.txt)
* **Execution Action:**
  1. Start CurlCraft:
     ```powershell
     cd curlcraft
     npm install
     npm run dev
     ```
  2. Open `http://localhost:5173` in your browser.
  3. Copy the cURL command from `sample_testing_suite/curlcraft_test/curl_sample.txt` and paste it into the editor.
* **Screenshot Action:** Take a screenshot of the browser showing the input cURL command and the generated Python Requests / Axios / Go code with the parameter inspector.
* **Save As:** `screenshots/test_curlcraft.png` (or `.jpg`)

---

## Tool 3: DataDiff
* **Test Focus:** Semantic Tabular Dataset Comparison & Distribution Drift
* **Sample Files:** [`sample_testing_suite/datadiff_test/baseline.csv`](./sample_testing_suite/datadiff_test/baseline.csv) & [`current.csv`](./sample_testing_suite/datadiff_test/current.csv)
* **Execution Command:**
  ```powershell
  cd datadiff
  pip install -e .
  datadiff compare ../sample_testing_suite/datadiff_test/baseline.csv ../sample_testing_suite/datadiff_test/current.csv --key id
  ```
* **Screenshot Action:** Take a screenshot of the Rich terminal table highlighting the row additions, deletions, modified salary cells, and status changes.
* **Save As:** `screenshots/test_datadiff.png` (or `.jpg`)

---

## Tool 4: DataGuard
* **Test Focus:** Polars SIMD Data Validation & Quality Profiling
* **Sample Files:** [`sample_testing_suite/dataguard_test/dirty_data.csv`](./sample_testing_suite/dataguard_test/dirty_data.csv) & [`rules.yaml`](./sample_testing_suite/dataguard_test/rules.yaml)
* **Execution Command:**
  ```powershell
  cd dataguard
  pip install -e .
  dataguard validate ../sample_testing_suite/dataguard_test/dirty_data.csv --rules ../sample_testing_suite/dataguard_test/rules.yaml
  ```
* **Screenshot Action:** Capture the terminal table showing rule violation checks (invalid email, age out of bounds, duplicate ID) and the overall dataset health score.
* **Save As:** `screenshots/test_dataguard.png` (or `.jpg`)

---

## Tool 5: JSON Formatter & Visualizer
* **Test Focus:** Heuristic Syntax Auto-Repair & Collapsible Tree Inspector
* **Sample File:** [`sample_testing_suite/json_formatter_test/broken_sample.json`](./sample_testing_suite/json_formatter_test/broken_sample.json)
* **Execution Action:**
  1. Start the JSON Formatter:
     ```powershell
     cd json-formatter
     npm install
     npm run dev
     ```
  2. Open the web interface at `http://localhost:5173`.
  3. Paste the contents of `broken_sample.json` into the left editor pane and click **"Auto-Fix"** or view the interactive tree on the right.
* **Screenshot Action:** Capture the dual-pane UI showing the auto-repaired JSON and the expanded tree viewer with colored data type chips.
* **Save As:** `screenshots/test_jsonformatter.png` (or `.jpg`)

---

## Tool 6: ScaffoldTree
* **Test Focus:** Filesystem Hierarchy Generation from ASCII Trees
* **Sample File:** [`sample_testing_suite/scaffoldtree_test/sample_tree.txt`](./sample_testing_suite/scaffoldtree_test/sample_tree.txt)
* **Execution Command:**
  ```powershell
  cd ScaffoldTree
  python structure_generator.py ../sample_testing_suite/scaffoldtree_test/sample_tree.txt -o ./output-scaffold-test
  dir output-scaffold-test
  ```
* **Screenshot Action:** Capture the terminal output showing the parsing confirmation and the generated directories and boilerplate files on disk.
* **Save As:** `screenshots/test_scaffoldtree.png` (or `.jpg`)

---

## Tool 7: SVG2JSX Studio
* **Test Focus:** Vector SVG Sanitization, React Component Generation & CSS Data-URIs
* **Sample File:** [`sample_testing_suite/svg2jsx_test/sample_icon.svg`](./sample_testing_suite/svg2jsx_test/sample_icon.svg)
* **Execution Action:**
  1. Start SVG2JSX:
     ```powershell
     cd svg2jsx
     npm install
     npm run dev
     ```
  2. Open the browser and paste/upload `sample_icon.svg`.
* **Screenshot Action:** Capture the live preview canvas, the color/size sliders, and the clean generated React TSX component code.
* **Save As:** `screenshots/test_svg2jsx.png` (or `.jpg`)

---

## Tool 8: TokenCost Studio
* **Test Focus:** BPE Token Estimation, Dynamic Variable Templating & Multi-Model Price Matrix
* **Sample File:** [`sample_testing_suite/tokencost_test/prompt_sample.txt`](./sample_testing_suite/tokencost_test/prompt_sample.txt)
* **Execution Action:**
  1. Start TokenCost:
     ```powershell
     cd tokencost
     npm install
     npm run dev
     ```
  2. Paste the prompt template into the playground and fill in sample values for `{{language}}`, `{{file_path}}`, and `{{compliance_standard}}`.
* **Screenshot Action:** Capture the TokenCost dashboard showing real-time token metrics and the multi-model pricing comparison table (GPT-4o, Claude 3.5, Gemini, DeepSeek).
* **Save As:** `screenshots/test_tokencost.png` (or `.jpg`)

---

## Tool 9: TreeSnapshot
* **Test Focus:** Recursive Directory Traversal with .treeignore Filtering
* **Execution Command:**
  ```powershell
  cd TreeSnapshot
  python tree_snapshot.py ../sample_testing_suite --ignore "*.csv,*.json"
  ```
* **Screenshot Action:** Capture the terminal showing the clean Markdown tree generated without the ignored CSV/JSON files.
* **Save As:** `screenshots/test_treesnapshot.png` (or `.jpg`)

---

## Tool 10: EnvGuard
* **Test Focus:** Schema Drift Auditing, Secret Leak Scanning & Redacted Diffing
* **Sample Files:** [`sample_testing_suite/envguard_test/.env.test`](./sample_testing_suite/envguard_test/.env.test) & [`.env.example.test`](./sample_testing_suite/envguard_test/.env.example.test)
* **Execution Command:**
  ```powershell
  cd envguard
  pip install -e .
  envguard check --env ../sample_testing_suite/envguard_test/.env.test --example ../sample_testing_suite/envguard_test/.env.example.test
  envguard scan-secrets ../sample_testing_suite/envguard_test
  ```
* **Screenshot Action:** Capture the Rich terminal tables showing the schema drift errors (invalid port type, missing keys) and detected AWS secret keys with entropy metrics.
* **Save As:** `screenshots/test_envguard.png` (or `.jpg`)

---

## Tool 11: RepoHealth
* **Test Focus:** 360-Degree Open-Source Repository Readiness, Health Grading (A+ to F), and Web Studio Audit
* **Sample Files:** [`sample_testing_suite/repohealth_test/`](./sample_testing_suite/repohealth_test)
* **Execution Commands:**
  1. **CLI Quality Audit & Gate:**
     ```powershell
     cd repohealth
     python repohealth.py ../sample_testing_suite/repohealth_test
     # Enforce Quality Gate (fails if score < 80%)
     python repohealth.py ../sample_testing_suite/repohealth_test --fail-under 80
     ```
  2. **Interactive Web Studio Dashboard:**
     ```powershell
     python repohealth.py --ui
     ```
     *(Or double-click `repohealth/web/index.html` directly in your browser)*
* **Screenshot Action:** Capture the terminal showing the RepoHealth score calculation (Grade, category breakdowns, and recommended template fixes) or the interactive Web Studio gauge showing real-time repository health and 1-click template fixes.
* **Save As:** `screenshots/test_repohealth.png` (or `.jpg`)

---

## Tool 12: GitScribe
* **Test Focus:** Conventional Commits Extraction, Markdown Table Generation, Git Hooks & Release Notes Studio
* **Sample Files:** [`sample_testing_suite/gitscribe_test/sample_commits.txt`](./sample_testing_suite/gitscribe_test/sample_commits.txt)
* **Execution Commands:**
  1. **CLI Changelog Generation:**
     ```powershell
     cd gitscribe
     # Generate clean Markdown Table Changelog
     python gitscribe.py --version v1.0.0 -o CHANGELOG_TEST.md
     # Test Git Hook zero-command automation
     python gitscribe.py --install-hook
     ```
  2. **Interactive Web Studio Dashboard:**
     ```powershell
     python gitscribe.py --ui
     ```
     *(Or double-click `gitscribe/web/index.html` directly in your browser)*
* **Screenshot Action:** Capture the terminal confirming generated table-formatted changelog with categorized commits, or the Web Studio dashboard showing real-time commit metrics (Features, Fixes, Contributors) and one-click PDF / Markdown export buttons.
* **Save As:** `screenshots/test_gitscribe.png` (or `.jpg`)

---

## Compiling Your Final Report with Screenshots
Whenever you add or update screenshots in `screenshots/`, run:
```powershell
python generate_report_docx.py
```
Your images will be automatically placed into the Word document under each corresponding tool test case!

