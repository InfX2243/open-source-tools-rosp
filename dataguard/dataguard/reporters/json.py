"""JSON reporter for automation and CI/CD pipelines."""

import json
from typing import Any
from dataguard.core.models import ValidationSummary
from dataguard.reporters.base import BaseReporter


class JSONReporter(BaseReporter):
    """Outputs machine-readable JSON representation of validation results."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def render(self, summary: ValidationSummary) -> str:
        # Use Pydantic's model_dump_json
        return summary.model_dump_json(indent=self.indent)
