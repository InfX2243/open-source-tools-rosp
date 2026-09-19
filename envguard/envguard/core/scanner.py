"""
Codebase AST and regex scanner to discover environment variable usages across languages.
"""

import os
import re
from typing import Dict, List, Set
from envguard.core.models import CodeReference, ScanCodebaseResult

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "site-packages",
}

# Regex patterns per file extension
PATTERNS = {
    "python": [
        re.compile(r"""(?:os\.environ|environ)\[['"]([A-Z0-9_]+)['"]\]"""),
        re.compile(r"""(?:os\.environ|environ)\.get\(['"]([A-Z0-9_]+)['"]"""),
        re.compile(r"""os\.getenv\(['"]([A-Z0-9_]+)['"]"""),
        re.compile(r"""(?:config|env)\(['"]([A-Z0-9_]+)['"]"""),
    ],
    "javascript": [
        re.compile(r"""process\.env\.([A-Z0-9_]+)\b"""),
        re.compile(r"""process\.env\[['"]([A-Z0-9_]+)['"]\]"""),
        re.compile(r"""import\.meta\.env\.([A-Z0-9_]+)\b"""),
    ],
    "go": [
        re.compile(r"""os\.(?:Getenv|LookupEnv)\(['"]([A-Z0-9_]+)['"]"""),
    ],
    "php": [
        re.compile(r"""(?:getenv|\$_ENV|\$_SERVER)\[?['"]([A-Z0-9_]+)['"]"""),
    ],
    "ruby": [
        re.compile(r"""ENV\[['"]([A-Z0-9_]+)['"]\]"""),
        re.compile(r"""ENV\.fetch\(['"]([A-Z0-9_]+)['"]"""),
    ],
    "shell": [
        re.compile(r"""\$\{?([A-Z0-9_]+)\}?"""),
    ],
}

EXT_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
    ".php": "php",
    ".rb": "ruby",
    ".sh": "shell",
    ".bash": "shell",
}


def scan_codebase(root_path: str) -> ScanCodebaseResult:
    """Scan all source code files under root_path for environment variable lookups."""
    discovered: Dict[str, List[CodeReference]] = {}
    files_scanned = 0
    total_refs = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        # In-place filtering of ignored dirs
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXT_MAP:
                continue

            file_path = os.path.join(dirpath, fname)
            lang = EXT_MAP[ext]
            patterns = PATTERNS.get(lang, [])

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                files_scanned += 1
            except Exception:
                continue

            for line_idx, line in enumerate(lines, start=1):
                clean_line = line.strip()
                # Skip comments
                if clean_line.startswith(("#", "//", "/*", "*")):
                    continue

                for pat in patterns:
                    for match in pat.finditer(line):
                        var_name = match.group(1)
                        # Filter out common shell noise or false positives
                        if len(var_name) < 2 or var_name in ("0", "1", "PATH", "HOME", "USER", "PWD", "SHELL"):
                            continue

                        ref = CodeReference(
                            file_path=os.path.relpath(file_path, root_path),
                            line_number=line_idx,
                            line_content=clean_line[:120],
                            language=lang,
                        )
                        if var_name not in discovered:
                            discovered[var_name] = []
                        discovered[var_name].append(ref)
                        total_refs += 1

    return ScanCodebaseResult(
        variables=discovered,
        files_scanned=files_scanned,
        total_references=total_refs,
    )
