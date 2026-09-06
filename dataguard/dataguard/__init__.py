"""
DataGuard: Open-Source Data Quality & Validation Platform.

A lightweight, developer-friendly, rule-driven data validation,
profiling, and quality scoring engine for files and databases.
"""

__version__ = "0.1.0"
__author__ = "DataGuard Contributors"

from dataguard.core.models import (
    RuleConfig,
    ColumnRule,
    ValidationResult,
    ValidationSummary,
    DatasetProfile,
    ColumnProfile,
    Severity,
    RuleStatus,
)
from dataguard.core.engine import ValidationEngine
from dataguard.core.profiler import DataProfiler

__all__ = [
    "__version__",
    "RuleConfig",
    "ColumnRule",
    "ValidationResult",
    "ValidationSummary",
    "DatasetProfile",
    "ColumnProfile",
    "Severity",
    "RuleStatus",
    "ValidationEngine",
    "DataProfiler",
]
