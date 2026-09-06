"""Dockerfile instruction parser for ContainerSec."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Union

from containersec.core.models import DockerInstruction


# Standard Dockerfile instructions
DOCKERFILE_INSTRUCTIONS = {
    "FROM", "RUN", "CMD", "LABEL", "MAINTAINER", "EXPOSE", "ENV", "ADD",
    "COPY", "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD",
    "STOPSIGNAL", "HEALTHCHECK", "SHELL",
}


class DockerfileParser:
    """Parses a Dockerfile into a list of structured DockerInstruction objects."""

    @classmethod
    def parse_file(cls, path: Union[str, Path]) -> List[DockerInstruction]:
        """Parse a Dockerfile from disk."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        content = file_path.read_text(encoding="utf-8")
        return cls.parse_content(content)

    @classmethod
    def parse_content(cls, content: str) -> List[DockerInstruction]:
        """Parse Dockerfile content string into instructions."""
        instructions: List[DockerInstruction] = []
        lines = content.splitlines()

        # Handle line continuations (backslash at end of line)
        merged_lines: List[tuple] = []  # (start_line_number, merged_text)
        i = 0
        while i < len(lines):
            line = lines[i]
            start_line = i + 1  # 1-indexed
            merged = line

            # Handle backslash continuations
            while merged.rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1
                merged = merged.rstrip()[:-1] + " " + lines[i].strip()

            merged_lines.append((start_line, merged, lines[start_line - 1]))
            i += 1

        for line_num, merged_text, original_line in merged_lines:
            stripped = merged_text.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Comments
            if stripped.startswith("#"):
                instructions.append(DockerInstruction(
                    line_number=line_num,
                    instruction="COMMENT",
                    arguments=stripped[1:].strip(),
                    original_line=original_line,
                    is_comment=True,
                ))
                continue

            # Parse instruction keyword
            match = re.match(r"^([A-Z]+)\s*(.*)", stripped, re.IGNORECASE)
            if match:
                keyword = match.group(1).upper()
                args = match.group(2).strip()
                if keyword in DOCKERFILE_INSTRUCTIONS:
                    instructions.append(DockerInstruction(
                        line_number=line_num,
                        instruction=keyword,
                        arguments=args,
                        original_line=original_line,
                    ))
                else:
                    # Unknown instruction, treat as content
                    instructions.append(DockerInstruction(
                        line_number=line_num,
                        instruction="UNKNOWN",
                        arguments=stripped,
                        original_line=original_line,
                    ))
            else:
                instructions.append(DockerInstruction(
                    line_number=line_num,
                    instruction="UNKNOWN",
                    arguments=stripped,
                    original_line=original_line,
                ))

        return instructions
