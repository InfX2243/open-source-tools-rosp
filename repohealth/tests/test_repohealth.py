"""
Unit tests for RepoHealth
=========================
Tests audit rules, scoring algorithm, grading scale, and markdown reporting.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path so repohealth can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from repohealth import RepoHealthAuditor, HealthReporter


def test_empty_directory_audit():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        auditor = RepoHealthAuditor(tmp_path)
        result = auditor.audit()

        assert result.grade == "F"
        assert result.percentage < 50
        assert any(c.id == "DOC_README" and not c.passed for c in result.checks)
        assert any(c.id == "LEGAL_LICENSE" and not c.passed for c in result.checks)


def test_healthy_repository_audit():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 1. Documentation
        readme_content = "# Test Project\n\n" + ("This is an extensive documentation description. " * 30) + "\n\n## Installation\n\n## Usage\n\n## License\n"
        (tmp_path / "README.md").write_text(readme_content, encoding="utf-8")
        (tmp_path / "CONTRIBUTING.md").write_text("# Contributing Guide", encoding="utf-8")
        (tmp_path / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct", encoding="utf-8")

        # 2. Legal
        (tmp_path / "LICENSE").write_text("MIT License\n\nCopyright (c) 2026 Test", encoding="utf-8")
        (tmp_path / "SECURITY.md").write_text("# Security Policy", encoding="utf-8")

        # 3. Git Hygiene
        (tmp_path / ".gitignore").write_text(".env\nnode_modules/\n__pycache__/\n*.pyc\n", encoding="utf-8")

        # 4. CI/CD
        workflows = tmp_path / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / "test.yml").write_text("name: Test\non: push\n", encoding="utf-8")

        issue_tmpl = tmp_path / ".github" / "ISSUE_TEMPLATE"
        issue_tmpl.mkdir(parents=True)
        (issue_tmpl / "bug.md").write_text("name: Bug", encoding="utf-8")

        auditor = RepoHealthAuditor(tmp_path)
        result = auditor.audit()

        assert result.grade in ["A+", "A"]
        assert result.percentage >= 85
        assert result.total_score >= 85


def test_markdown_report_rendering():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "README.md").write_text("# Readme", encoding="utf-8")
        (tmp_path / "LICENSE").write_text("MIT License", encoding="utf-8")

        auditor = RepoHealthAuditor(tmp_path)
        result = auditor.audit()
        md = HealthReporter.render_markdown(result)

        assert "# 🏥 Repository Health Report" in md
        assert "### 📊 Category Breakdown" in md
        assert "### 📋 Audit Checklist & Recommendations" in md
        assert "README.md File" in md


def test_secret_file_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a leaked .env file on disk
        (tmp_path / ".env").write_text("SECRET_KEY=leaked_value_123", encoding="utf-8")

        auditor = RepoHealthAuditor(tmp_path)
        result = auditor.audit()

        secret_check = next(c for c in result.checks if c.id == "GIT_NO_SECRETS")
        assert not secret_check.passed
        assert "Danger: Sensitive files detected" in secret_check.details


if __name__ == "__main__":
    test_empty_directory_audit()
    test_healthy_repository_audit()
    test_markdown_report_rendering()
    test_secret_file_detection()
    print("✅ All RepoHealth unit tests passed successfully!")
