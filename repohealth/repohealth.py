#!/usr/bin/env python3
"""
RepoHealth 🏥 - Repository Health, Readiness & Open-Source Checklist Auditor
============================================================================
A developer-first, zero-dependency tool that audits local and GitHub repositories
against open-source industry best practices, awards an A-to-F health grade,
and provides an interactive Web Dashboard and 1-click fix templates.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# Domain Models & Rules Definition
# ==============================================================================

@dataclass
class AuditCheck:
    id: str
    category: str  # Documentation, Legal, Git Hygiene, CI/CD
    title: str
    description: str
    points: int
    passed: bool = False
    warning: bool = False
    details: str = ""
    fix_suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuditResult:
    target_path: str
    timestamp: str
    total_score: int
    max_score: int
    percentage: float
    grade: str
    status: str
    category_scores: Dict[str, Tuple[int, int]]  # cat: (score, max)
    checks: List[AuditCheck] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["checks"] = [c.to_dict() for c in self.checks]
        return data


# Standard SPDX Licenses
SPDX_LICENSES = {
    "MIT": "MIT License",
    "APACHE-2.0": "Apache License 2.0",
    "GPL-3.0": "GNU General Public License v3.0",
    "BSD-2-CLAUSE": "BSD 2-Clause Simplified License",
    "BSD-3-CLAUSE": "BSD 3-Clause Revised License",
    "ISC": "ISC License",
    "MPL-2.0": "Mozilla Public License 2.0",
    "UNLICENSE": "The Unlicense",
}


# ==============================================================================
# Repository Audit Engine
# ==============================================================================

class RepoHealthAuditor:
    """Scans local filesystem or structures against open-source health standards."""

    def __init__(self, root_path: Path):
        self.root = root_path.resolve()

    def file_exists(self, *candidates: str) -> Optional[Path]:
        for candidate in candidates:
            p = self.root / candidate
            if p.exists() and p.is_file():
                return p
        return None

    def dir_exists(self, *candidates: str) -> Optional[Path]:
        for candidate in candidates:
            p = self.root / candidate
            if p.exists() and p.is_dir():
                return p
        return None

    def audit(self) -> AuditResult:
        checks: List[AuditCheck] = []

        # ----------------------------------------------------------------------
        # 1. Documentation Category (Total: 30 pts)
        # ----------------------------------------------------------------------
        readme_file = self.file_exists("README.md", "README", "readme.md", "README.rst")
        readme_check = AuditCheck(
            id="DOC_README",
            category="Documentation",
            title="README.md File",
            description="The front page and primary guide for your repository.",
            points=10,
        )
        if readme_file:
            readme_check.passed = True
            readme_check.details = f"Found: {readme_file.name}"
        else:
            readme_check.details = "No README.md found in repository root."
            readme_check.fix_suggestion = "Create a README.md file explaining the project's purpose, setup, and usage."
        checks.append(readme_check)

        readme_content_check = AuditCheck(
            id="DOC_README_CONTENT",
            category="Documentation",
            title="README Depth & Quality",
            description="Checks if README contains comprehensive documentation (> 150 words).",
            points=5,
        )
        if readme_file:
            try:
                text = readme_file.read_text(encoding="utf-8", errors="replace")
                words = len(text.split())
                if words >= 150:
                    readme_content_check.passed = True
                    readme_content_check.details = f"Extensive documentation ({words} words)."
                else:
                    readme_content_check.warning = True
                    readme_content_check.details = f"README is quite brief ({words} words). Consider adding more details."
                    readme_content_check.fix_suggestion = "Expand README with background context, architecture diagrams, and usage examples."
            except Exception:
                readme_content_check.details = "Could not parse README content."
        else:
            readme_content_check.details = "README missing."
        checks.append(readme_content_check)

        readme_sections_check = AuditCheck(
            id="DOC_README_SECTIONS",
            category="Documentation",
            title="Essential README Sections",
            description="Checks for Installation, Usage, and License sections.",
            points=5,
        )
        if readme_file:
            try:
                text = readme_file.read_text(encoding="utf-8", errors="replace").lower()
                has_install = any(k in text for k in ["install", "setup", "getting started", "prerequisites"])
                has_usage = any(k in text for k in ["usage", "example", "quick start", "commands", "how to"])
                has_license = "license" in text

                found = []
                if has_install: found.append("Installation")
                if has_usage: found.append("Usage")
                if has_license: found.append("License")

                if len(found) >= 2:
                    readme_sections_check.passed = True
                    readme_sections_check.details = f"Found key sections: {', '.join(found)}."
                else:
                    readme_sections_check.warning = True
                    readme_sections_check.details = f"Only found: {', '.join(found) if found else 'None'}."
                    readme_sections_check.fix_suggestion = "Add dedicated 'Installation', 'Usage', and 'License' headings."
            except Exception:
                readme_sections_check.details = "Could not inspect sections."
        else:
            readme_sections_check.details = "README missing."
        checks.append(readme_sections_check)

        contrib_file = self.file_exists("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "contributing.md")
        contrib_check = AuditCheck(
            id="DOC_CONTRIBUTING",
            category="Documentation",
            title="Contributing Guidelines",
            description="Guides external developers on PRs, local setups, and code style.",
            points=5,
        )
        if contrib_file:
            contrib_check.passed = True
            contrib_check.details = f"Found: {contrib_file.relative_to(self.root)}"
        else:
            contrib_check.details = "No CONTRIBUTING.md found."
            contrib_check.fix_suggestion = "Add a CONTRIBUTING.md file with contribution steps, PR rules, and test instructions."
        checks.append(contrib_check)

        coc_file = self.file_exists("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md", "code_of_conduct.md")
        coc_check = AuditCheck(
            id="DOC_CODE_OF_CONDUCT",
            category="Documentation",
            title="Code of Conduct",
            description="Fosters a welcoming, safe open-source community.",
            points=5,
        )
        if coc_file:
            coc_check.passed = True
            coc_check.details = f"Found: {coc_file.relative_to(self.root)}"
        else:
            coc_check.details = "No CODE_OF_CONDUCT.md found."
            coc_check.fix_suggestion = "Adopt the standard Contributor Covenant (Contributor-Covenant.org)."
        checks.append(coc_check)

        # ----------------------------------------------------------------------
        # 2. Legal & Licensing Category (Total: 25 pts)
        # ----------------------------------------------------------------------
        license_file = self.file_exists("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
        license_check = AuditCheck(
            id="LEGAL_LICENSE",
            category="Legal & Community",
            title="Open Source License File",
            description="Grants legal permission for others to use, modify, and distribute code.",
            points=15,
        )
        detected_license = None
        if license_file:
            license_check.passed = True
            license_check.details = f"Found: {license_file.name}"
            try:
                l_text = license_file.read_text(encoding="utf-8", errors="replace").upper()
                for spdx, name in SPDX_LICENSES.items():
                    if spdx in l_text or name.upper() in l_text:
                        detected_license = spdx
                        break
            except Exception:
                pass
        else:
            license_check.details = "No LICENSE file found. Unlicensed code is copyrighted by default."
            license_check.fix_suggestion = "Add an approved open-source license (e.g. MIT, Apache 2.0, or GPL-3.0)."
        checks.append(license_check)

        spdx_check = AuditCheck(
            id="LEGAL_SPDX",
            category="Legal & Community",
            title="Standard SPDX Recognized License",
            description="Ensures the license text is recognized and compatible with package ecosystems.",
            points=5,
        )
        if detected_license:
            spdx_check.passed = True
            spdx_check.details = f"Recognized SPDX License: {detected_license} ({SPDX_LICENSES[detected_license]})"
        elif license_file:
            spdx_check.warning = True
            spdx_check.details = "License file present, but could not detect standard SPDX identifier."
            spdx_check.fix_suggestion = "Ensure license contains standard header (e.g. 'MIT License' or 'Apache License 2.0')."
        else:
            spdx_check.details = "No license found."
        checks.append(spdx_check)

        sec_file = self.file_exists("SECURITY.md", ".github/SECURITY.md", "security.md")
        sec_check = AuditCheck(
            id="LEGAL_SECURITY",
            category="Legal & Community",
            title="Security Vulnerability Policy (SECURITY.md)",
            description="Specifies how to privately report security vulnerabilities.",
            points=5,
        )
        if sec_file:
            sec_check.passed = True
            sec_check.details = f"Found: {sec_file.relative_to(self.root)}"
        else:
            sec_check.details = "No SECURITY.md policy found."
            sec_check.fix_suggestion = "Add a SECURITY.md file explaining contact emails for private disclosure."
        checks.append(sec_check)

        # ----------------------------------------------------------------------
        # 3. Git Hygiene & Configuration (Total: 25 pts)
        # ----------------------------------------------------------------------
        gitignore_file = self.file_exists(".gitignore")
        gitignore_check = AuditCheck(
            id="GIT_GITIGNORE",
            category="Git Hygiene",
            title=".gitignore Configuration",
            description="Prevents temporary files, dependencies, and OS clutter from being committed.",
            points=10,
        )
        if gitignore_file:
            gitignore_check.passed = True
            gitignore_check.details = "Found: .gitignore"
        else:
            gitignore_check.details = "Missing .gitignore file."
            gitignore_check.fix_suggestion = "Add a .gitignore tailored to your project languages."
        checks.append(gitignore_check)

        gitignore_hygiene_check = AuditCheck(
            id="GIT_HYGIENE",
            category="Git Hygiene",
            title="Environment & Cache Exclusion Rules",
            description="Checks if .gitignore blocks .env files, node_modules, and cache files.",
            points=5,
        )
        if gitignore_file:
            try:
                g_text = gitignore_file.read_text(encoding="utf-8", errors="replace")
                rules_found = []
                if ".env" in g_text: rules_found.append(".env")
                if "node_modules" in g_text or "__pycache__" in g_text: rules_found.append("dependencies/cache")
                if "*.pyc" in g_text or "*.log" in g_text or ".DS_Store" in g_text: rules_found.append("build/system logs")

                if len(rules_found) >= 2:
                    gitignore_hygiene_check.passed = True
                    gitignore_hygiene_check.details = f"Properly blocks: {', '.join(rules_found)}."
                else:
                    gitignore_hygiene_check.warning = True
                    gitignore_hygiene_check.details = "Missing key exclusions (.env, node_modules, or cache)."
                    gitignore_hygiene_check.fix_suggestion = "Ensure .env, dependencies, and caches are listed in .gitignore."
            except Exception:
                gitignore_hygiene_check.details = "Could not parse .gitignore."
        else:
            gitignore_hygiene_check.details = ".gitignore missing."
        checks.append(gitignore_hygiene_check)

        secrets_check = AuditCheck(
            id="GIT_NO_SECRETS",
            category="Git Hygiene",
            title="No Tracked Secret / Key Files",
            description="Verifies that no live .env or credential keys (.pem, .key) exist in the repository.",
            points=10,
        )
        leaked = []
        for bad_pattern in [".env", ".env.local", "id_rsa", "server.key", "credentials.json"]:
            if (self.root / bad_pattern).exists():
                leaked.append(bad_pattern)

        if not leaked:
            secrets_check.passed = True
            secrets_check.details = "Clean! No unmasked credential files found."
        else:
            secrets_check.details = f"⚠️ Danger: Sensitive files detected on disk: {', '.join(leaked)}!"
            secrets_check.fix_suggestion = f"Remove {', '.join(leaked)} and add them to .gitignore immediately."
        checks.append(secrets_check)

        # ----------------------------------------------------------------------
        # 4. CI/CD & Automation (Total: 20 pts)
        # ----------------------------------------------------------------------
        workflows_dir = self.dir_exists(".github/workflows")
        has_ci_yaml = False
        workflow_count = 0

        if workflows_dir:
            yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            workflow_count = len(yaml_files)
            has_ci_yaml = workflow_count > 0

        gitlab_ci = self.file_exists(".gitlab-ci.yml")
        if gitlab_ci:
            has_ci_yaml = True
            workflow_count += 1

        cicd_check = AuditCheck(
            id="CICD_WORKFLOWS",
            category="CI/CD & Automation",
            title="Automated CI/CD Workflows",
            description="Automates building, testing, or publishing via GitHub Actions / GitLab CI.",
            points=15,
        )
        if has_ci_yaml:
            cicd_check.passed = True
            cicd_check.details = f"Found {workflow_count} active workflow(s) in CI directory."
        else:
            cicd_check.details = "No automated CI/CD workflows detected."
            cicd_check.fix_suggestion = "Add a GitHub Actions workflow in .github/workflows/ to automate tests."
        checks.append(cicd_check)

        issue_tmpl_dir = self.dir_exists(".github/ISSUE_TEMPLATE")
        issue_tmpl_file = self.file_exists(".github/issue_template.md", "ISSUE_TEMPLATE.md")
        tmpl_check = AuditCheck(
            id="CICD_TEMPLATES",
            category="CI/CD & Automation",
            title="Issue & PR Templates",
            description="Standardizes bug reports, feature requests, and pull requests.",
            points=5,
        )
        if issue_tmpl_dir or issue_tmpl_file:
            tmpl_check.passed = True
            tmpl_check.details = "Issue / PR template(s) configured."
        else:
            tmpl_check.details = "No issue/PR templates found."
            tmpl_check.fix_suggestion = "Create .github/ISSUE_TEMPLATE/ for bug reports and feature requests."
        checks.append(tmpl_check)

        # ----------------------------------------------------------------------
        # Calculate Total Scores & Grade
        # ----------------------------------------------------------------------
        total_score = sum(c.points for c in checks if c.passed)
        # Half points for warnings
        for c in checks:
            if c.warning and not c.passed:
                total_score += c.points // 2

        max_score = sum(c.points for c in checks)
        percentage = round((total_score / max_score) * 100, 1)

        # Assign Grade
        if percentage >= 95:
            grade = "A+"
            status = "🟢 Exceptional Open-Source Quality"
        elif percentage >= 85:
            grade = "A"
            status = "🟢 Healthy & Production-Ready"
        elif percentage >= 75:
            grade = "B"
            status = "🟡 Good — Minor Gaps Identified"
        elif percentage >= 60:
            grade = "C"
            status = "🟠 Needs Improvement"
        else:
            grade = "F"
            status = "🔴 Critical Gaps Present"

        # Calculate category scores
        category_scores: Dict[str, Tuple[int, int]] = {}
        for c in checks:
            earned = c.points if c.passed else (c.points // 2 if c.warning else 0)
            cur_earned, cur_max = category_scores.get(c.category, (0, 0))
            category_scores[c.category] = (cur_earned + earned, cur_max + c.points)

        return AuditResult(
            target_path=str(self.root),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            grade=grade,
            status=status,
            category_scores=category_scores,
            checks=checks,
        )


# ==============================================================================
# Markdown & Terminal Reporting Engine
# ==============================================================================

class HealthReporter:
    """Renders audit findings into terminal tables and Markdown reports."""

    @staticmethod
    def render_markdown(result: AuditResult) -> str:
        lines: List[str] = []
        lines.append(f"# 🏥 Repository Health Report: `{Path(result.target_path).name}`")
        lines.append("")
        lines.append(f"> 📅 **Audit Date:** `{result.timestamp}` &nbsp;•&nbsp; "
                     f"🎯 **Score:** `{result.total_score} / {result.max_score}` ({result.percentage}%) &nbsp;•&nbsp; "
                     f"🏷️ **Grade:** `{result.grade}` ({result.status})")
        lines.append("")

        # Badge
        color = "brightgreen" if result.grade in ["A+", "A"] else ("yellow" if result.grade == "B" else "red")
        clean_grade = result.grade.replace("+", "%2B")
        badge_md = f"[![RepoHealth](https://img.shields.io/badge/RepoHealth-{clean_grade}%20({result.percentage}%25)-{color})](#)"
        lines.append(f"### 🛡️ Repository Badge")
        lines.append(f"Add this to your `README.md`:")
        lines.append(f"```markdown\n{badge_md}\n```")
        lines.append("")

        # Category Breakdown Table
        lines.append("### 📊 Category Breakdown")
        lines.append("")
        lines.append("| Category | Score | Percentage | Status |")
        lines.append("| :--- | :---: | :---: | :--- |")
        for cat, (earned, max_p) in result.category_scores.items():
            pct = round((earned / max_p) * 100, 1)
            cat_status = "🟢 Pass" if pct >= 80 else ("🟡 Warning" if pct >= 50 else "🔴 Action Needed")
            lines.append(f"| {cat} | {earned} / {max_p} | {pct}% | {cat_status} |")
        lines.append("")

        # Detailed Checklist
        lines.append("### 📋 Audit Checklist & Recommendations")
        lines.append("")
        lines.append("| Rule | Status | Points | Details / Recommendation |")
        lines.append("| :--- | :---: | :---: | :--- |")

        for c in result.checks:
            badge = "✅ Passed" if c.passed else ("⚠️ Warning" if c.warning else "❌ Missing")
            recommendation = c.details
            if c.fix_suggestion:
                recommendation += f"<br>↳ **Fix:** *{c.fix_suggestion}*"
            clean_rec = recommendation.replace("|", "\\|")
            lines.append(f"| **{c.title}** ({c.category}) | {badge} | +{c.points} | {clean_rec} |")

        lines.append("")
        lines.append("---")
        lines.append("*Report generated by [RepoHealth](repohealth/) — Open-Source Repository Readiness Auditor.*")
        return "\n".join(lines)

    @staticmethod
    def print_terminal_summary(result: AuditResult) -> None:
        print("\n" + "=" * 65)
        print(f"🏥  RepoHealth Audit Report: {Path(result.target_path).name}")
        print("=" * 65)
        print(f"🎯  Overall Health Score : {result.total_score} / {result.max_score} ({result.percentage}%)")
        print(f"🏷️  Overall Grade        : {result.grade}")
        print(f"📋  Status               : {result.status}")
        print("-" * 65)
        print("CATEGORY SUMMARY:")
        for cat, (earned, max_p) in result.category_scores.items():
            pct = round((earned / max_p) * 100, 1)
            icon = "✅" if pct >= 80 else ("⚠️" if pct >= 50 else "❌")
            print(f"  {icon} {cat.ljust(22)} : {earned}/{max_p} pts ({pct}%)")
        print("-" * 65)

        failures = [c for c in result.checks if not c.passed]
        if failures:
            print("RECOMMENDED FIXES:")
            for c in failures:
                prefix = "⚠️" if c.warning else "❌"
                print(f"  {prefix} {c.title}: {c.fix_suggestion or c.details}")
        else:
            print("🎉 Perfect score! No critical gaps found.")
        print("=" * 65 + "\n")


# ==============================================================================
# Web Studio Dashboard Launcher
# ==============================================================================

def launch_web_ui(port: int = 8899) -> int:
    """Launches the RepoHealth Studio Web Dashboard in the user's browser."""
    import http.server
    import socketserver
    import webbrowser

    web_dir = Path(__file__).resolve().parent / "web"
    if not web_dir.exists():
        sys.stderr.write(f"❌ Error: Web dashboard directory not found at {web_dir}\n")
        return 1

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(web_dir), **kwargs)

        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print("=" * 65)
            print(f"🏥  RepoHealth Studio Web Dashboard is LIVE!")
            print(f"🌐  Open in your browser: {url}")
            print("=" * 65)
            print("💡 Press Ctrl+C in this terminal to stop the web dashboard.\n")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except OSError:
        port += 1
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print(f"🏥  RepoHealth Studio running at {url}")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 RepoHealth Studio stopped.")
    return 0


# ==============================================================================
# CLI Entrypoint & Runner
# ==============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repohealth",
        description="🏥 RepoHealth: Repository Health & Open-Source Checklist Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  repohealth .                                 # Audit current repository
  repohealth /path/to/project                  # Audit specific repository folder
  repohealth --ui                              # Launch interactive Web Studio Dashboard
  repohealth -o REPO_HEALTH.md                 # Save markdown audit report
  repohealth --badge                           # Output Markdown badge for README.md
  repohealth --json                            # Machine-readable JSON for CI/CD gates
        """,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to repository folder to audit (default: current directory).",
    )
    parser.add_argument(
        "--ui", "--dashboard",
        action="store_true",
        help="Launch the interactive RepoHealth Web Dashboard in your browser.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8899,
        help="Port number for the Web Dashboard (default: 8899).",
    )
    parser.add_argument(
        "-o", "--output",
        help="File path to save Markdown audit report (e.g. REPO_HEALTH.md).",
    )
    parser.add_argument(
        "--badge",
        action="store_true",
        help="Print only the Markdown badge snippet for README.md.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON result.",
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=0,
        help="Exit with non-zero status if health percentage is under this threshold (e.g. 80). Great for CI/CD gates.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # 1. Handle Web Dashboard
    if args.ui:
        return launch_web_ui(port=args.port)

    # 2. Run Local Audit
    target_path = Path(args.target).resolve()
    if not target_path.exists() or not target_path.is_dir():
        sys.stderr.write(f"❌ Error: Target path '{args.target}' does not exist or is not a directory.\n")
        return 1

    auditor = RepoHealthAuditor(target_path)
    result = auditor.audit()

    # 3. Output formats
    if args.badge:
        clean_grade = result.grade.replace("+", "%2B")
        color = "brightgreen" if result.grade in ["A+", "A"] else ("yellow" if result.grade == "B" else "red")
        print(f"[![RepoHealth](https://img.shields.io/badge/RepoHealth-{clean_grade}%20({result.percentage}%25)-{color})](#)")
        return 0

    if args.json:
        payload = result.to_dict()
        json_str = json.dumps(payload, indent=2)
        if args.output:
            Path(args.output).write_text(json_str, encoding="utf-8")
            print(f"✅ Saved JSON health audit to {args.output}")
        else:
            print(json_str)
        return 0

    # Terminal output
    HealthReporter.print_terminal_summary(result)

    if args.output:
        md_content = HealthReporter.render_markdown(result)
        Path(args.output).write_text(md_content, encoding="utf-8", newline="\n")
        print(f"✨ Saved Markdown report to {args.output}")

    # 4. Check CI/CD failure threshold
    if args.fail_under > 0 and result.percentage < args.fail_under:
        sys.stderr.write(f"❌ CI Gate Failed: Health score {result.percentage}% is below required threshold of {args.fail_under}%.\n")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
