"""Sources package for DataDiff."""

from datadiff.sources.base import BaseSourceAdapter
from datadiff.sources.csv import CSVSourceAdapter
from datadiff.sources.json import JSONSourceAdapter
from datadiff.sources.parquet import ParquetSourceAdapter
from datadiff.sources.sql import SQLSourceAdapter

__all__ = [
    "BaseSourceAdapter",
    "CSVSourceAdapter",
    "JSONSourceAdapter",
    "ParquetSourceAdapter",
    "SQLSourceAdapter",
]
