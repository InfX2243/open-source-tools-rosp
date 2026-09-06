"""Automated remediation engine for Dockerfile security findings."""

from __future__ import annotations

import re
from typing import List, Tuple
from containersec.core.models import ScanResult


class DockerfileFixer:
    """Automatically applies safe security fixes to Dockerfile contents."""

    def __init__(self, content: str, scan_result: ScanResult):
        self.original_content = content
        self.scan_result = scan_result
        self.applied_fixes: List[str] = []

    def fix(self) -> Tuple[str, List[str]]:
        """Apply automated fixes and return the modified content along with a change log."""
        lines = self.original_content.splitlines()
        fixes_log: List[str] = []

        # 1. Replace ADD with COPY when not extracting tar or URL
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("ADD ") and not (
                ".tar" in stripped or ".gz" in stripped or "http://" in stripped or "https://" in stripped
            ):
                replaced = re.sub(r"^(\s*)ADD\s+", r"\1COPY ", line)
                new_lines.append(replaced)
                fixes_log.append("Replaced insecure ADD with COPY")
            else:
                new_lines.append(line)
        lines = new_lines

        # 2. Add --no-install-recommends and rm -rf /var/lib/apt/lists/* to apt-get install
        new_lines = []
        for line in lines:
            if "apt-get install" in line:
                mod_line = line
                if "--no-install-recommends" not in mod_line:
                    mod_line = mod_line.replace("apt-get install", "apt-get install --no-install-recommends")
                    fixes_log.append("Added --no-install-recommends to apt-get install")
                if "rm -rf /var/lib/apt/lists/*" not in mod_line and not mod_line.rstrip().endswith("\\"):
                    mod_line = mod_line.rstrip() + " && rm -rf /var/lib/apt/lists/*"
                    fixes_log.append("Added cache cleanup (rm -rf /var/lib/apt/lists/*)")
                new_lines.append(mod_line)
            else:
                new_lines.append(line)
        lines = new_lines

        # 3. Add --no-cache-dir to pip install
        new_lines = []
        for line in lines:
            if "pip install" in line and "--no-cache-dir" not in line:
                new_lines.append(line.replace("pip install", "pip install --no-cache-dir"))
                fixes_log.append("Added --no-cache-dir to pip install")
            else:
                new_lines.append(line)
        lines = new_lines

        # 4. Check if USER is present; if not, inject a non-root user creation before CMD/ENTRYPOINT
        has_user = any(l.strip().startswith("USER ") for l in lines)
        if not has_user:
            insert_idx = len(lines)
            for idx, l in enumerate(lines):
                stripped = l.strip()
                if stripped.startswith("CMD ") or stripped.startswith("ENTRYPOINT "):
                    insert_idx = idx
                    break

            user_block = [
                "",
                "# CIS-4.1: Switch to non-root user for principle of least privilege",
                "RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser",
                "USER appuser",
                "",
            ]
            lines = lines[:insert_idx] + user_block + lines[insert_idx:]
            fixes_log.append("Injected non-root user definition (RUN groupadd/useradd & USER appuser)")

        # 5. Check if HEALTHCHECK is present; if not, inject default template
        has_healthcheck = any(l.strip().startswith("HEALTHCHECK ") for l in lines)
        if not has_healthcheck:
            insert_idx = len(lines)
            for idx, l in enumerate(lines):
                stripped = l.strip()
                if stripped.startswith("CMD ") or stripped.startswith("ENTRYPOINT "):
                    insert_idx = idx
                    break

            healthcheck_block = [
                "# CIS-4.6: Add container healthcheck",
                "HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\",
                '  CMD curl -f http://localhost:8080/health || exit 1',
                "",
            ]
            lines = lines[:insert_idx] + healthcheck_block + lines[insert_idx:]
            fixes_log.append("Added HEALTHCHECK instruction skeleton")

        # 6. Replace deprecated MAINTAINER with LABEL maintainer=...
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("MAINTAINER "):
                val = stripped[len("MAINTAINER "):].strip()
                new_lines.append(f'LABEL maintainer="{val}"')
                fixes_log.append("Replaced deprecated MAINTAINER with LABEL maintainer=...")
            else:
                new_lines.append(line)
        lines = new_lines

        self.applied_fixes = fixes_log
        return "\n".join(lines) + "\n", fixes_log
