"""DataDiff: Open-Source Semantic Data Comparison & Change Detection Platform."""

__version__ = "1.0.0"
__author__ = "DataDiff Community"

from datadiff.core.engine import DataDiffEngine
from datadiff.core.models import (
    ComparisonPolicy,
    DiffConfig,
    DiffSummary,
    NormalizationRules,
    RowDiffSummary,
    SchemaDiff,
    StatsDiff,
)

__all__ = [
    "DataDiffEngine",
    "DiffConfig",
    "DiffSummary",
    "SchemaDiff",
    "RowDiffSummary",
    "StatsDiff",
    "ComparisonPolicy",
    "NormalizationRules",
]
