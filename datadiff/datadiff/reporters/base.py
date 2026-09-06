"""Base reporter interface for DataDiff."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from datadiff.core.models import DiffSummary


class BaseReporter(ABC):
    """Abstract base class for all DataDiff output formatters."""

    @abstractmethod
    def render(self, diff: DiffSummary) -> Any:
        """Render the diff summary to output (string, print, or file)."""
        pass
