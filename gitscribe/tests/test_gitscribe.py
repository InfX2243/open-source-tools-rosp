"""
Unit tests for GitScribe
========================
Tests commit parsing, breaking change detection, issue references,
smart scoping, and enhanced Markdown Table rendering.
"""

import sys
from pathlib import Path

# Add parent directory to path so gitscribe can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gitscribe import CommitInfo, ChangelogRenderer, parse_commit_message


def test_conventional_feat_parsing():
    commit = parse_commit_message(
        full_hash="1234567890abcdef1234567890abcdef12345678",
        short_hash="1234567",
        author="Alice",
        date="2026-10-18",
        raw_subject="feat(auth): implement oauth2 login flow",
        body="Supports GitHub and Google providers (#42)",
    )
    assert commit.commit_type == "feat"
    assert commit.scope == "auth"
    assert commit.subject == "Implement oauth2 login flow"
    assert commit.is_breaking is False
    assert "#42" in commit.issues


def test_conventional_fix_parsing():
    commit = parse_commit_message(
        full_hash="abcdef1234567890abcdef1234567890abcdef12",
        short_hash="abcdef1",
        author="Bob",
        date="2026-10-18",
        raw_subject="fix(parser): handle empty strings gracefully",
        body="Resolves crash on blank lines. Fixes #108",
    )
    assert commit.commit_type == "fix"
    assert commit.scope == "parser"
    assert commit.subject == "Handle empty strings gracefully"
    assert "#108" in commit.issues


def test_breaking_change_with_exclamation():
    commit = parse_commit_message(
        full_hash="9999999990abcdef1234567890abcdef12345678",
        short_hash="9999999",
        author="Charlie",
        date="2026-10-18",
        raw_subject="feat(api)!: remove deprecated v1 endpoints",
        body="",
    )
    assert commit.commit_type == "feat"
    assert commit.scope == "api"
    assert commit.is_breaking is True


def test_breaking_change_in_body():
    body_text = "Refactors database client.\n\nBREAKING CHANGE: drop postgres 10 support"
    commit = parse_commit_message(
        full_hash="8888888880abcdef1234567890abcdef12345678",
        short_hash="8888888",
        author="Dana",
        date="2026-10-18",
        raw_subject="refactor(db): rewrite connection pool",
        body=body_text,
    )
    assert commit.is_breaking is True
    assert "drop postgres 10 support" in commit.breaking_reason


def test_smart_scoping_and_heuristics():
    commit1 = parse_commit_message(
        "1111111111111111111111111111111111111111",
        "1111111",
        "Eve",
        "2026-10-18",
        "add README for TreeSnapshot",
    )
    assert commit1.scope == "TreeSnapshot"
    assert commit1.subject == "Add README for TreeSnapshot"

    commit2 = parse_commit_message(
        "2222222222222222222222222222222222222222",
        "2222222",
        "Eve",
        "2026-10-18",
        "gitignore updated",
    )
    assert commit2.commit_type == "chore"
    assert commit2.scope == "config"
    assert commit2.subject == "Update .gitignore rules"


def test_renderer_table_markdown_output():
    renderer = ChangelogRenderer(
        repo_url="https://github.com/test-org/test-repo",
        show_authors=True,
        style="table",
    )
    commits = [
        parse_commit_message(
            "aaa1111111111111111111111111111111111111",
            "aaa1111",
            "Alice",
            "2026-10-18",
            "feat(search): add fuzzy full-text search (#15)",
        ),
        parse_commit_message(
            "bbb2222222222222222222222222222222222222",
            "bbb2222",
            "Bob",
            "2026-10-18",
            "fix(ui): resolve modal flickering on safari",
        ),
    ]

    section = renderer.render_release_section(
        version="v1.0.0",
        date_str="2026-10-18",
        commits=commits,
    )

    assert "## 🏷️ [v1.0.0] — 2026-10-18" in section
    assert "### 🚀 New Features & Tools" in section
    assert "### 🐛 Bug Fixes & Stability" in section
    assert "| Component | Description | Commit | Author |" in section
    assert "| `search` | Add fuzzy full-text search ([#15](https://github.com/test-org/test-repo/issues/15)) | [`aaa1111`](https://github.com/test-org/test-repo/commit/aaa1111) | [@Alice](https://github.com/Alice) |" in section
    assert "### 👥 Contributors" in section


def test_prepend_to_existing_changelog():
    renderer = ChangelogRenderer(style="table")
    existing_changelog = (
        "# 📜 Project Changelog\n\n"
        "> All notable changes and version milestones for this repository are documented here.\n\n"
        "---\n\n"
        "## 🏷️ [v1.0.0] — 2026-10-01\n\n"
        "### 🚀 New Features & Tools\n\n"
        "| Component | Description | Commit | Author |\n"
    )

    new_release = "## 🏷️ [v1.1.0] — 2026-10-18\n\n### 🐛 Bug Fixes & Stability\n\n| Component | Description | Commit | Author |\n"
    prepended = renderer.prepend_to_existing(existing_changelog, new_release)

    assert "# 📜 Project Changelog" in prepended
    assert "## 🏷️ [v1.1.0] — 2026-10-18" in prepended
    assert "## 🏷️ [v1.0.0] — 2026-10-01" in prepended
    assert prepended.index("v1.1.0") < prepended.index("v1.0.0")


if __name__ == "__main__":
    test_conventional_feat_parsing()
    test_conventional_fix_parsing()
    test_breaking_change_with_exclamation()
    test_breaking_change_in_body()
    test_smart_scoping_and_heuristics()
    test_renderer_table_markdown_output()
    test_prepend_to_existing_changelog()
    print("✅ All 7 GitScribe tests passed successfully!")
