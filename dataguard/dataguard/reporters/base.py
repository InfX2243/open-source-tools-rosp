"""Abstract Base Class for DataGuard validation reporters."""

from abc import ABC, abstractmethod
from typing import Optional
from dataguard.core.models import ValidationSummary


class BaseReporter(ABC):
    """Abstract interface for formatting and outputting validation results."""

    @abstractmethod
    def render(self, summary: ValidationSummary) -> str:
        """Format the ValidationSummary into the target representation."""
        pass

    def save(self, summary: ValidationSummary, output_path: str) -> None:
        """Render and persist to an output file path."""
        content = self.render(summary)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
