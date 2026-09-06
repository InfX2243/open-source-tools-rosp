"""Abstract base class for DataGuard data source adapters."""

from abc import ABC, abstractmethod
from typing import Any


class SourceAdapter(ABC):
    """Abstract interface for loading data into a unified DataFrame."""

    @abstractmethod
    def load(self, source: str, **kwargs: Any) -> Any:
        """
        Load dataset from file path, connection URI, or query.
        
        Returns:
            Polars DataFrame (or fallback DataFrame/dict representation).
        """
        pass

    @abstractmethod
    def supports(self, source: str) -> bool:
        """Check if this adapter supports the given source identifier."""
        pass
