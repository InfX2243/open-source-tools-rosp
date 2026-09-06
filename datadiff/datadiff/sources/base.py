"""Base data source adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict
import polars as pl


class BaseSourceAdapter(ABC):
    """Abstract base class for all DataDiff source loaders."""

    @abstractmethod
    def load(self) -> pl.DataFrame:
        """Load dataset as a Polars DataFrame."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, str]:
        """Return dataset column names and their data types."""
        pass
