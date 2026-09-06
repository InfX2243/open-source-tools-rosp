"""Parquet file source adapter."""

import os
from typing import Any
from dataguard.sources.base import SourceAdapter

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class ParquetAdapter(SourceAdapter):
    """Loads Apache Parquet files."""

    def supports(self, source: str) -> bool:
        src_lower = source.lower()
        return src_lower.endswith(".parquet") or src_lower.endswith(".pq")

    def load(self, source: str, **kwargs: Any) -> Any:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Parquet file not found: {source}")

        if POLARS_AVAILABLE:
            return pl.read_parquet(source)

        import pyarrow.parquet as pq
        table = pq.read_table(source)
        return table.to_pylist()
