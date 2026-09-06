"""JSON reporter for DataDiff."""

from __future__ import annotations

import json
from typing import Optional
from pathlib import Path
from datadiff.core.models import DiffSummary
from datadiff.reporters.base import BaseReporter


class JSONReporter(BaseReporter):
    """Serializes dataset comparison results into standard formatted JSON."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def render(self, diff: DiffSummary) -> str:
        """Render diff summary to a formatted JSON string."""
        return diff.model_dump_json(indent=self.indent)

    def write_to_file(self, diff: DiffSummary, path: Path | str) -> None:
        """Save JSON diff report to a file."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.render(diff), encoding="utf-8")
