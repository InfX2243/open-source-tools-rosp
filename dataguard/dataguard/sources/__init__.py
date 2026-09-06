"""Source adapter registry and loader factory."""

from typing import Any, List
from dataguard.sources.base import SourceAdapter
from dataguard.sources.csv import CSVAdapter
from dataguard.sources.json import JSONAdapter
from dataguard.sources.parquet import ParquetAdapter
from dataguard.sources.sql import SQLAdapter

ADAPTERS: List[SourceAdapter] = [
    CSVAdapter(),
    JSONAdapter(),
    ParquetAdapter(),
    SQLAdapter(),
]


def get_adapter_for_source(source: str) -> SourceAdapter:
    """Find the appropriate source adapter for a given path or connection URI."""
    for adapter in ADAPTERS:
        if adapter.supports(source):
            return adapter
    # Default to CSV adapter if unknown
    return CSVAdapter()


def load_dataset(source: str, **kwargs: Any) -> Any:
    """Convenience function to load a dataset from any supported source."""
    adapter = get_adapter_for_source(source)
    return adapter.load(source, **kwargs)


__all__ = [
    "SourceAdapter",
    "CSVAdapter",
    "JSONAdapter",
    "ParquetAdapter",
    "SQLAdapter",
    "get_adapter_for_source",
    "load_dataset",
]
