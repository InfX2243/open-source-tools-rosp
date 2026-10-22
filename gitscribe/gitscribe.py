#!/usr/bin/env python3
"""
GitScribe ✒️ - Automated Git Changelog & Release Notes Generator
===============================================================
A developer-first, zero-dependency tool that transforms Git commit history
into structured, beautiful Markdown changelogs, GitHub release drafts,
and machine-readable JSON.

Includes automatic commit detection via Git Hooks and Real-Time Watch mode!
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



# ==============================================================================
# Domain Models & Conventional Commit Rules
# ==============================================================================

CATEGORY_MAPPING: Dict[str, Tuple[str, str, int]] = {
    # type: (Section Title, Emoji, Priority Ordering)
    "breaking": ("Breaking Changes", "💥", 0),
    "feat": ("New Features & Tools", "🚀", 1),
    "fix": ("Bug Fixes & Stability", "🐛", 2),
    "perf": ("Performance Improvements", "⚡", 3),
    "security": ("Security Hardening", "🛡️", 4),
    "docs": ("Documentation", "📚", 5),
    "refactor": ("Refactoring & Code Quality", "♻️", 6),
    "style": ("Code Style & UI", "🎨", 7),
    "test": ("Tests & QA", "🧪", 8),
    "build": ("Build & Dependencies", "📦", 9),
    "ci": ("CI/CD & Automation", "🏗️", 10),
    "chore": ("Maintenance & Configuration", "🔧", 11),
    "revert": ("Reverted Changes", "⏪", 12),
    "other": ("Other Improvements", "✨", 13),
}

KNOWN_PROJECT_TOOLS = [
    "containersec",
    "curlcraft",
    "datadiff",
    "dataguard",
    "envguard",
    "gitscribe",
    "json-formatter",
    "ScaffoldTree",
    "svg2jsx",
    "tokencost",
    "TreeSnapshot",
]

CONVENTIONAL_REGEX = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$"
)
ISSUE_REGEX = re.compile(r"(?:^|[\s(,])(#\d+|[A-Z]+-\d+)")


@dataclass
class CommitInfo:
    hash: str
    short_hash: str
    author: str
    date: str
    raw_subject: str
    body: str = ""
    commit_type: str = "other"
    scope: Optional[str] = None
    subject: str = ""
    is_breaking: bool = False
    breaking_reason: str = ""
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ==============================================================================
# Git Repository Interaction Engine
# ==============================================================================

class GitEngine:
    """Zero-dependency wrapper over local git commands."""

    @staticmethod
    def run_git(args: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=cwd or Path.cwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return (
                res.returncode,
                res.stdout.replace("\r\n", "\n").replace("\r", "").strip(),
                res.stderr.replace("\r\n", "\n").replace("\r", "").strip(),
            )
        except FileNotFoundError:
            return -1, "", "Git executable not found in system PATH."

    @classmethod
    def is_git_repo(cls, cwd: Optional[Path] = None) -> bool:
        code, out, _ = cls.run_git(["rev-parse", "--is-inside-work-tree"], cwd)
        return code == 0 and out == "true"

    @classmethod
    def get_repo_remote_url(cls, cwd: Optional[Path] = None) -> Optional[str]:
        code, out, _ = cls.run_git(["config", "--get", "remote.origin.url"], cwd)
        if code != 0 or not out:
            return None

        url = out.strip()
        if url.startswith("git@"):
            url = re.sub(r"^git@([^:]+):", r"https://\1/", url)
        if url.endswith(".git"):
            url = url[:-4]
        return url

    @classmethod
    def get_tags(cls, cwd: Optional[Path] = None) -> List[str]:
        code, out, _ = cls.run_git(["tag", "--sort=-creatordate"], cwd)
        if code != 0 or not out:
            return []
        return [t.strip() for t in out.splitlines() if t.strip()]

    @classmethod
    def get_latest_tag(cls, cwd: Optional[Path] = None) -> Optional[str]:
        tags = cls.get_tags(cwd)
        return tags[0] if tags else None

    @classmethod
    def fetch_commits(
        cls,
        revision_range: Optional[str] = None,
        exclude_merges: bool = True,
        cwd: Optional[Path] = None,
    ) -> List[CommitInfo]:
        git_args = [
            "log",
            "--pretty=format:%H%x1f%h%x1f%an%x1f%ad%x1f%s%x1f%b%x1e",
            "--date=short",
        ]
        if exclude_merges:
            git_args.append("--no-merges")

        if revision_range:
            git_args.append(revision_range)

        code, stdout, stderr = cls.run_git(git_args, cwd)
        if code != 0:
            if "unknown revision" in stderr or "bad revision" in stderr:
                code, stdout, _ = cls.run_git(
                    ["log", "--pretty=format:%H%x1f%h%x1f%an%x1f%ad%x1f%s%x1f%b%x1e", "--date=short", "--no-merges"],
                    cwd,
                )
            if code != 0:
                return []

        if not stdout:
            return []

        raw_records = stdout.split("\x1e")
        commits: List[CommitInfo] = []

        for record in raw_records:
            clean_record = record.replace("\r", "").strip()
            if not clean_record:
                continue

            parts = clean_record.split("\x1f")
            if len(parts) < 5:
                continue

            full_hash = parts[0].strip()
            short_hash = parts[1].strip()
            author = parts[2].strip()
            date = parts[3].strip()
            subject = parts[4].strip()
            body = parts[5].strip() if len(parts) > 5 else ""

            parsed = parse_commit_message(full_hash, short_hash, author, date, subject, body)
            commits.append(parsed)

        return commits


# ==============================================================================
# Commit Message Parsing & Smart Formatting Logic
# ==============================================================================

def clean_subject_and_infer_scope(
    raw_subject: str,
    explicit_scope: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    subject = raw_subject.replace("\r", "").strip()
    scope = explicit_scope

    if not scope:
        matched_tools = []
        for tool in KNOWN_PROJECT_TOOLS:
            pattern = re.compile(rf"\b{re.escape(tool)}\b", re.IGNORECASE)
            if pattern.search(subject):
                matched_tools.append(tool)

        if matched_tools:
            scope = ", ".join(matched_tools)
        elif re.search(r"\b(readme|docs|documentation)\b", subject, re.IGNORECASE):
            scope = "docs"
        elif re.search(r"\b(gitignore|\.gitignore|config|settings)\b", subject, re.IGNORECASE):
            scope = "config"
        elif re.search(r"\b(ci|workflow|action|pipeline)\b", subject, re.IGNORECASE):
            scope = "ci"
        elif re.search(r"\b(test|tests|pytest)\b", subject, re.IGNORECASE):
            scope = "test"

    if scope:
        clean_pattern = rf"^(?:fix|feat|add|update)?\s*{re.escape(scope)}:\s*"
        subject = re.sub(clean_pattern, "", subject, flags=re.IGNORECASE).strip()

    if re.match(r"^curlcraft done$", subject, re.IGNORECASE):
        subject = "Complete curlcraft implementation"
    elif re.match(r"^done tokencost$", subject, re.IGNORECASE):
        subject = "Complete tokencost implementation"
    elif re.match(r"^gitignore updated$", subject, re.IGNORECASE):
        subject = "Update .gitignore rules"
    elif re.match(r"^add (.*)$", subject, re.IGNORECASE):
        subject = re.sub(r"^add\s+", "Add ", subject, flags=re.IGNORECASE)
    elif re.match(r"^fix (.*)$", subject, re.IGNORECASE):
        subject = re.sub(r"^fix\s+", "Fix ", subject, flags=re.IGNORECASE)

    subject = subject.replace("|", "\\|")

    if subject and len(subject) > 1:
        subject = subject[0].upper() + subject[1:]

    return subject, scope


def parse_commit_message(
    full_hash: str,
    short_hash: str,
    author: str,
    date: str,
    raw_subject: str,
    body: str = "",
) -> CommitInfo:
    raw_subject = raw_subject.replace("\r", "").strip()
    body = body.replace("\r", "").strip()

    commit = CommitInfo(
        hash=full_hash,
        short_hash=short_hash,
        author=author,
        date=date,
        raw_subject=raw_subject,
        body=body,
        subject=raw_subject,
    )

    is_breaking = False
    breaking_reason = ""

    if "BREAKING CHANGE:" in raw_subject or "BREAKING CHANGE:" in body:
        is_breaking = True
        match = re.search(r"BREAKING CHANGE:\s*(.+)", raw_subject + "\n" + body)
        if match:
            breaking_reason = match.group(1).strip()
    elif "BREAKING-CHANGE:" in raw_subject or "BREAKING-CHANGE:" in body:
        is_breaking = True
        match = re.search(r"BREAKING-CHANGE:\s*(.+)", raw_subject + "\n" + body)
        if match:
            breaking_reason = match.group(1).strip()

    match = CONVENTIONAL_REGEX.match(raw_subject)
    if match:
        c_type = match.group("type").lower()
        explicit_scope = match.group("scope")
        bang = match.group("breaking")
        clean_sub = match.group("subject").strip()

        if bang:
            is_breaking = True

        commit.commit_type = c_type if c_type in CATEGORY_MAPPING else "other"
        cleaned_subj, final_scope = clean_subject_and_infer_scope(clean_sub, explicit_scope)
        commit.scope = final_scope
        commit.subject = cleaned_subj
    else:
        sub_lower = raw_subject.lower()
        if sub_lower.startswith(("fix", "patch", "bug", "resolve")):
            commit.commit_type = "fix"
        elif sub_lower.startswith(("feat", "add", "create", "new")):
            commit.commit_type = "feat"
        elif sub_lower.startswith(("doc", "readme")):
            commit.commit_type = "docs"
        elif sub_lower.startswith(("refactor", "clean", "rewrite")):
            commit.commit_type = "refactor"
        elif sub_lower.startswith(("test", "spec")):
            commit.commit_type = "test"
        elif sub_lower.startswith(("perf", "speed", "optimi")):
            commit.commit_type = "perf"
        elif sub_lower.startswith(("bump", "upgrade", "deps")):
            commit.commit_type = "build"
        elif "gitignore" in sub_lower or "config" in sub_lower:
            commit.commit_type = "chore"
        else:
            commit.commit_type = "other"

        cleaned_subj, final_scope = clean_subject_and_infer_scope(raw_subject)
        commit.scope = final_scope
        commit.subject = cleaned_subj

    commit.is_breaking = is_breaking
    commit.breaking_reason = breaking_reason

    found_issues = ISSUE_REGEX.findall(raw_subject + " " + body)
    if found_issues:
        commit.issues = sorted(list(set(issue.strip() for issue in found_issues)))

    return commit


# ==============================================================================
# Markdown Table Rendering Engine
# ==============================================================================

class ChangelogRenderer:
    """Transforms parsed commits into a modern, beautifully formatted Markdown Table changelog."""

    def __init__(
        self,
        repo_url: Optional[str] = None,
        show_authors: bool = True,
        style: str = "table",
    ):
        self.repo_url = repo_url
        self.show_authors = show_authors
        self.style = style

    def format_commit_link(self, commit: CommitInfo) -> str:
        if self.repo_url:
            return f"[`{commit.short_hash}`]({self.repo_url}/commit/{commit.short_hash})"
        return f"`{commit.short_hash}`"

    def format_issue_links(self, issues: List[str]) -> str:
        if not issues:
            return ""
        rendered = []
        for issue in issues:
            clean_issue = issue.lstrip("#")
            if self.repo_url and clean_issue.isdigit():
                rendered.append(f"[{issue}]({self.repo_url}/issues/{clean_issue})")
            else:
                rendered.append(issue)
        return " (" + ", ".join(rendered) + ")"

    def format_author_link(self, author: str) -> str:
        if not self.show_authors or not author:
            return "—"
        if self.repo_url and "github.com" in self.repo_url:
            return f"[@{author}](https://github.com/{author})"
        return f"@{author}"

    def linkify_issues(self, text: str, issues: List[str]) -> str:
        """Replaces issue numbers like #15 in text with markdown links without duplicating."""
        if not self.repo_url or not issues:
            return text
        res = text
        for issue in issues:
            clean_issue = issue.lstrip("#")
            if clean_issue.isdigit():
                link = f"[{issue}]({self.repo_url}/issues/{clean_issue})"
                res = re.sub(rf"(?<!\[){re.escape(issue)}(?!\])", link, res)
        return res

    def render_category_table(self, commits: List[CommitInfo]) -> str:
        """Renders commits into an ultra-clean, readable Markdown table."""
        lines = []
        lines.append("| Component | Description | Commit | Author |")
        lines.append("| :--- | :--- | :---: | :--- |")

        for c in commits:
            component = f"`{c.scope}`" if c.scope else "*core*"
            desc = self.linkify_issues(c.subject, c.issues)
            extra_issues = [i for i in c.issues if i not in c.subject]
            if extra_issues:
                desc += " " + self.format_issue_links(extra_issues)
            if c.is_breaking and c.breaking_reason:
                desc += f" <br>↳ **Breaking:** *{c.breaking_reason}*"

            commit_link = self.format_commit_link(c)
            author_link = self.format_author_link(c.author)

            lines.append(f"| {component} | {desc} | {commit_link} | {author_link} |")

        return "\n".join(lines)

    def render_commit_line(self, commit: CommitInfo) -> str:
        """Bullet list fallback."""
        scope_badge = f"**`{commit.scope}`** " if commit.scope else ""
        desc = self.linkify_issues(commit.subject, commit.issues)
        extra_issues = [i for i in commit.issues if i not in commit.subject]
        issues_str = " " + self.format_issue_links(extra_issues) if extra_issues else ""
        link_str = self.format_commit_link(commit)
        author_str = f" ({self.format_author_link(commit.author)})" if commit.author else ""
        return f"- {scope_badge}{desc}{issues_str} • {link_str}{author_str}"

    def render_release_section(
        self,
        version: str,
        date_str: str,
        commits: List[CommitInfo],
        include_chores: bool = True,
    ) -> str:
        """Renders an aesthetically pleasing release section with clean tables."""
        if not commits:
            return f"## 🏷️ [{version}] — {date_str}\n\n*No changes recorded in this revision range.*"

        contributors: Set[str] = set()
        for c in commits:
            if c.author:
                contributors.add(c.author)
        sorted_contributors = sorted(list(contributors))

        breaking_commits = [c for c in commits if c.is_breaking]

        grouped: Dict[str, List[CommitInfo]] = {}
        for c in commits:
            if not include_chores and c.commit_type in ("chore", "style"):
                continue
            grouped.setdefault(c.commit_type, []).append(c)

        lines: List[str] = []

        clean_ver = version if version.startswith("v") else f"v{version}"
        lines.append(f"## 🏷️ [{clean_ver}] — {date_str}")
        lines.append("")

        lines.append(
            f"> 📦 **Release:** `{clean_ver}` &nbsp;•&nbsp; "
            f"📅 **Date:** `{date_str}` &nbsp;•&nbsp; "
            f"🔨 **Commits:** `{len(commits)}` &nbsp;•&nbsp; "
            f"👥 **Contributors:** `{len(sorted_contributors)}`"
        )
        lines.append("")

        # 1. Breaking Changes
        if breaking_commits:
            lines.append("### 💥 Breaking Changes")
            lines.append("")
            if self.style == "table":
                lines.append(self.render_category_table(breaking_commits))
            else:
                for c in breaking_commits:
                    reason = f" *(Note: {c.breaking_reason})*" if c.breaking_reason else ""
                    lines.append(f"{self.render_commit_line(c)}{reason}")
            lines.append("")

        # 2. Categorized tables
        sorted_categories = sorted(
            CATEGORY_MAPPING.items(), key=lambda item: item[1][2]
        )

        for cat_key, (title, emoji, _) in sorted_categories:
            if cat_key == "breaking":
                continue
            cat_commits = grouped.get(cat_key, [])
            if not cat_commits:
                continue

            lines.append(f"### {emoji} {title}")
            lines.append("")
            if self.style == "table":
                lines.append(self.render_category_table(cat_commits))
            else:
                for c in cat_commits:
                    lines.append(self.render_commit_line(c))
            lines.append("")

        # 3. Contributors Spotlight
        if sorted_contributors:
            lines.append("### 👥 Contributors")
            lines.append("")
            rendered_authors = []
            for author in sorted_contributors:
                if self.repo_url and "github.com" in self.repo_url:
                    rendered_authors.append(f"[@{author}](https://github.com/{author})")
                else:
                    rendered_authors.append(f"@{author}")
            lines.append(f"Thank you to our contributors for this release: {', '.join(rendered_authors)}!")
            lines.append("")

        return "\n".join(lines).strip()

    def generate_full_changelog(
        self,
        version: str,
        date_str: str,
        commits: List[CommitInfo],
        include_chores: bool = True,
    ) -> str:
        """Renders standard full CHANGELOG.md file format."""
        header = (
            "# 📜 Project Changelog\n\n"
            "> All notable changes and version milestones for this repository are documented here.\n"
            "> Built with [GitScribe](gitscribe/) • Adheres to [Keep a Changelog](https://keepachangelog.com/) & [Semantic Versioning](https://semver.org/).\n\n"
            "---\n\n"
        )
        release_block = self.render_release_section(
            version, date_str, commits, include_chores=include_chores
        )
        return header + release_block + "\n"

    def prepend_to_existing(
        self,
        existing_content: str,
        new_release_markdown: str,
    ) -> str:
        """Inserts the new release block right under the top Changelog title."""
        pattern = re.compile(r"^(#\s+.*?Changelog.*?\n(?:.*\n)*?---\s*\n\n?)", re.MULTILINE)
        match = pattern.search(existing_content)

        if match:
            prefix = match.group(1)
            suffix = existing_content[match.end():]
            return prefix + new_release_markdown + "\n\n---\n\n" + suffix.lstrip()

        return new_release_markdown + "\n\n---\n\n" + existing_content.lstrip()


# ==============================================================================
# Automation Engines: Git Hooks & Real-Time Watch Mode
# ==============================================================================

def generate_and_save(
    output_path: str = "CHANGELOG.md",
    version: str = "1.0.0",
    style: str = "table",
    quiet: bool = False,
) -> int:
    """Core function to fetch all commits and save to output file."""
    commits = GitEngine.fetch_commits(exclude_merges=True)
    date_today = datetime.date.today().isoformat()
    repo_url = GitEngine.get_repo_remote_url()

    renderer = ChangelogRenderer(repo_url=repo_url, style=style)
    content = renderer.generate_full_changelog(
        version=version, date_str=date_today, commits=commits
    )
    Path(output_path).write_text(content, encoding="utf-8", newline="\n")

    if not quiet:
        print(f"✨ GitScribe: Auto-updated {output_path} ({len(commits)} commits)")
    return 0


def install_git_hook(output_file: str = "CHANGELOG.md") -> int:
    """Installs a Git post-commit hook so CHANGELOG.md auto-updates on every commit."""
    code, git_dir, _ = GitEngine.run_git(["rev-parse", "--git-dir"])
    if code != 0:
        sys.stderr.write("❌ Error: Not a git repository.\n")
        return 1

    hooks_dir = Path(git_dir) / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    hook_file = hooks_dir / "post-commit"
    py_exec = sys.executable.replace("\\", "/")

    hook_script = f"""#!/bin/sh
# GitScribe Auto-Changelog Hook
# Automatically refreshes {output_file} on every single git commit!
"{py_exec}" gitscribe/gitscribe.py --output "{output_file}" --quiet 2>/dev/null || python gitscribe/gitscribe.py --output "{output_file}" --quiet 2>/dev/null || true
"""
    hook_file.write_text(hook_script, encoding="utf-8", newline="\n")

    try:
        os.chmod(hook_file, 0o755)
    except Exception:
        pass

    print(f"🎉 GitScribe Git Hook successfully installed to:\n   {hook_file}")
    print(f"\n🚀 From now on, whenever you run 'git commit', '{output_file}' will automatically update itself without typing any commands!")
    return 0


def uninstall_git_hook() -> int:
    """Removes the Git post-commit hook."""
    code, git_dir, _ = GitEngine.run_git(["rev-parse", "--git-dir"])
    if code != 0:
        return 1

    hook_file = Path(git_dir) / "hooks" / "post-commit"
    if hook_file.exists():
        hook_file.unlink()
        print(f"✅ GitScribe Git Hook removed from {hook_file}.")
    else:
        print("ℹ️ No GitScribe hook found.")
    return 0


def run_watch_mode(output: str = "CHANGELOG.md", interval: float = 2.0) -> None:
    """Watches git repository for new commits in real time and updates CHANGELOG.md immediately."""
    print("👀 GitScribe Watcher is ACTIVE!")
    print(f"📁 Monitoring Git history for new commits... Auto-updating '{output}'")
    print("💡 Press Ctrl+C at any time to stop watching.\n")

    last_head = ""
    code, out, _ = GitEngine.run_git(["rev-parse", "HEAD"])
    if code == 0:
        last_head = out.strip()
        generate_and_save(output_path=output, quiet=False)

    try:
        while True:
            time.sleep(interval)
            code, current_head, _ = GitEngine.run_git(["rev-parse", "HEAD"])
            if code == 0 and current_head.strip() != last_head:
                last_head = current_head.strip()
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"⚡ [{now_str}] New commit detected ({last_head[:7]})! Auto-updating {output}...")
                generate_and_save(output_path=output, quiet=False)
                print(f"✅ [{now_str}] {output} refreshed successfully!\n")
    except KeyboardInterrupt:
        print("\n🛑 GitScribe Watcher stopped.")


def launch_web_ui(port: int = 8787) -> int:
    """Launches the GitScribe Studio Web Dashboard using Python's built-in HTTP server."""
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
            print(f"✒️  GitScribe Studio Web Dashboard is LIVE!")
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
            print(f"✒️  GitScribe Studio running at {url}")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 GitScribe Studio stopped.")
    return 0


# ==============================================================================
# CLI Entrypoint & Runner
# ==============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitscribe",
        description="✒️ GitScribe: Automated Git Changelog & Release Notes Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Zero-Command Automation:
  gitscribe --install-hook                     # Auto-updates CHANGELOG.md on every git commit!
  gitscribe --watch                            # Real-time background watcher for commits

Manual Commands:
  gitscribe                                    # Preview clean table changelog
  gitscribe --version v1.0.0 -o CHANGELOG.md   # Generate easy-to-read table CHANGELOG.md
  gitscribe --style list                       # Switch to classic bullet list format
  gitscribe --version v1.1.0 -o CHANGELOG.md -p # Prepend new release to existing changelog
  gitscribe --release-notes                    # Output release section only (for GitHub Releases)
  gitscribe --json                             # Machine-readable JSON summary
        """,
    )
    parser.add_argument(
        "--ui", "--dashboard",
        action="store_true",
        help="Launch the interactive GitScribe Studio Web Dashboard in your browser.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8787,
        help="Port number for the Web Dashboard (default: 8787).",
    )
    parser.add_argument(
        "--install-hook",
        action="store_true",
        help="Install Git post-commit hook to auto-update CHANGELOG.md on every commit without running commands.",
    )
    parser.add_argument(
        "--uninstall-hook",
        action="store_true",
        help="Uninstall the Git post-commit hook.",
    )
    parser.add_argument(
        "-w", "--watch",
        action="store_true",
        help="Run real-time background watcher that auto-updates CHANGELOG.md whenever new commits are made.",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress console output (used in background hooks).",
    )
    parser.add_argument(
        "-v", "--version",
        default="1.0.0",
        help="Release version tag (e.g., v1.0.0, 1.2.0). Defaults to '1.0.0'.",
    )
    parser.add_argument(
        "--style",
        choices=["table", "list"],
        default="table",
        help="Formatting style: 'table' (clean Markdown tables, default) or 'list' (bullet points).",
    )
    parser.add_argument(
        "--since",
        help="Starting git ref / tag. Defaults to latest tag or initial commit.",
    )
    parser.add_argument(
        "--until",
        default="HEAD",
        help="Ending git ref / tag (default: HEAD).",
    )
    parser.add_argument(
        "-o", "--output",
        default="CHANGELOG.md",
        help="Path to write output markdown (default: CHANGELOG.md).",
    )
    parser.add_argument(
        "-p", "--prepend",
        action="store_true",
        help="Prepend release notes into existing changelog file instead of overwriting.",
    )
    parser.add_argument(
        "--release-notes",
        action="store_true",
        help="Output only the release section (omits full top header). Perfect for GitHub Releases.",
    )
    parser.add_argument(
        "--repo",
        help="Custom GitHub/GitLab repository URL for auto-linking commits & PRs.",
    )
    parser.add_argument(
        "--include-merges",
        action="store_true",
        help="Include merge commits (excluded by default).",
    )
    parser.add_argument(
        "--hide-authors",
        action="store_true",
        help="Omit author names from commit entries.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as machine-readable JSON.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Parse entire repository commit history.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # 0. Handle Web Dashboard (can run anywhere, even outside git)
    if args.ui:
        return launch_web_ui(port=args.port)

    if not GitEngine.is_git_repo():
        sys.stderr.write("❌ Error: Current directory is not a Git repository.\n")
        return 1

    # 1. Handle Hook Installation / Uninstallation
    if args.install_hook:
        return install_git_hook(output_file=args.output)
    if args.uninstall_hook:
        return uninstall_git_hook()

    # 2. Handle Real-Time Watcher
    if args.watch:
        run_watch_mode(output=args.output)
        return 0

    # 3. Standard Execution
    latest_tag = GitEngine.get_latest_tag()
    if args.all:
        rev_range = None
    elif args.since:
        rev_range = f"{args.since}..{args.until}"
    elif latest_tag:
        rev_range = f"{latest_tag}..{args.until}"
    else:
        rev_range = None

    repo_url = args.repo or GitEngine.get_repo_remote_url()

    commits = GitEngine.fetch_commits(
        revision_range=rev_range,
        exclude_merges=not args.include_merges,
    )

    date_today = datetime.date.today().isoformat()

    if args.json:
        payload = {
            "version": args.version,
            "date": date_today,
            "range": rev_range or "all",
            "repo_url": repo_url,
            "total_commits": len(commits),
            "breaking_count": sum(1 for c in commits if c.is_breaking),
            "commits": [c.to_dict() for c in commits],
        }
        json_str = json.dumps(payload, indent=2)
        if args.output:
            Path(args.output).write_text(json_str, encoding="utf-8")
            if not args.quiet:
                print(f"✅ Scribed JSON summary to {args.output}")
        else:
            print(json_str)
        return 0

    renderer = ChangelogRenderer(
        repo_url=repo_url,
        show_authors=not args.hide_authors,
        style=args.style,
    )

    if args.release_notes:
        content = renderer.render_release_section(
            version=args.version,
            date_str=date_today,
            commits=commits,
        )
    else:
        content = renderer.generate_full_changelog(
            version=args.version,
            date_str=date_today,
            commits=commits,
        )

    if args.output:
        out_path = Path(args.output)
        if args.prepend and out_path.exists():
            existing = out_path.read_text(encoding="utf-8")
            release_block = renderer.render_release_section(
                version=args.version,
                date_str=date_today,
                commits=commits,
            )
            final_content = renderer.prepend_to_existing(existing, release_block)
            out_path.write_text(final_content, encoding="utf-8", newline="\n")
            if not args.quiet:
                print(f"✨ GitScribe: Prepended [{args.version}] into {args.output} ({len(commits)} commits)")
        else:
            out_path.write_text(content, encoding="utf-8", newline="\n")
            if not args.quiet:
                print(f"✨ GitScribe: Generated table-formatted {args.output} ({len(commits)} commits scribed)")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
