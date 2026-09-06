"""CSV file source adapter."""

import os
from typing import Any
from dataguard.sources.base import SourceAdapter

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class CSVAdapter(SourceAdapter):
    """Loads CSV and TSV formatted files."""

    def supports(self, source: str) -> bool:
        src_lower = source.lower()
        return src_lower.endswith(".csv") or src_lower.endswith(".tsv") or src_lower.endswith(".txt")

    def load(self, source: str, **kwargs: Any) -> Any:
        if not os.path.exists(source):
            raise FileNotFoundError(f"CSV file not found: {source}")

        separator = kwargs.get("separator", "," if not source.lower().endswith(".tsv") else "\t")
        ignore_errors = kwargs.get("ignore_errors", True)

        if POLARS_AVAILABLE:
            try:
                # Polars fast CSV reader with schema inference and error tolerance
                return pl.read_csv(
                    source,
                    separator=separator,
                    ignore_errors=ignore_errors,
                    infer_schema_length=kwargs.get("infer_schema_length", 10000),
                    truncate_ragged_lines=True,
                )
            except Exception as e:
                # Fallback to loose string casting if strictly typed parsing fails
                return pl.read_csv(
                    source,
                    separator=separator,
                    schema_overrides={col: pl.Utf8 for col in []},
                    infer_schema_length=0,
                    truncate_ragged_lines=True,
                )

        import csv
        with open(source, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter=separator)
            return list(reader)
