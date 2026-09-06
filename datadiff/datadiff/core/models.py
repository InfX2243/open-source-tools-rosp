"""Pydantic data models for DataDiff configurations, schemas, and comparison results."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    """Configuration for a comparison dataset source."""

    path: Optional[str] = Field(default=None, description="Local file path or cloud URI")
    format: Optional[str] = Field(default=None, description="Data format: csv, json, parquet, sql")
    connection_string: Optional[str] = Field(default=None, description="Database connection URI")
    table: Optional[str] = Field(default=None, description="Database table name")
    query: Optional[str] = Field(default=None, description="Custom SQL query for source data")


class NormalizationRules(BaseModel):
    """Value normalization and tolerance rules for comparisons."""

    numeric_tolerance: float = Field(default=0.0, description="Absolute tolerance for float diffs")
    case_sensitive: bool = Field(default=True, description="Whether string comparison is case sensitive")
    trim_whitespace: bool = Field(default=True, description="Strip leading/trailing whitespace")
    ignore_nan_vs_null: bool = Field(default=True, description="Treat NaN and null as equivalent")


class ComparisonPolicy(BaseModel):
    """CI/CD Quality Gate policies to enforce data-change constraints."""

    allow_schema_changes: bool = Field(default=True, description="Fail CI if columns are added/removed/migrated")
    allow_column_removal: bool = Field(default=False, description="Fail CI if any column is deleted")
    max_removed_rows: Optional[int] = Field(default=None, description="Max allowed deleted records")
    max_modified_pct: Optional[float] = Field(default=None, description="Max allowed percentage of modified records")
    max_null_rate_increase: Optional[float] = Field(default=None, description="Max percentage points increase in nulls")
    max_critical_discrepancies: int = Field(default=0, description="Max allowed critical anomalies")


class StatsDiffConfig(BaseModel):
    """Configuration for statistical diffing and drift detection."""

    track_null_rates: bool = Field(default=True)
    track_distinct_counts: bool = Field(default=True)
    track_numerical_drift: bool = Field(default=True)
    drift_alert_pct: float = Field(default=10.0, description="Threshold percentage change for drift alert")


class DiffConfig(BaseModel):
    """Root configuration object for a DataDiff comparison task."""

    source: Optional[SourceConfig] = Field(default=None)
    target: Optional[SourceConfig] = Field(default=None)
    key: Optional[List[str]] = Field(default=None, description="Primary key column(s) to match records")
    ignore_columns: List[str] = Field(default_factory=list, description="Columns to exclude from diff")
    rules: NormalizationRules = Field(default_factory=NormalizationRules)
    policies: ComparisonPolicy = Field(default_factory=ComparisonPolicy)
    stats_config: StatsDiffConfig = Field(default_factory=StatsDiffConfig)


class ColumnMigration(BaseModel):
    """Represents a column data-type change."""

    column: str
    source_dtype: str
    target_dtype: str


class ColumnMeta(BaseModel):
    """Metadata for a column in schema."""

    name: str
    dtype: str
    nullable: bool = True


class SchemaDiff(BaseModel):
    """Differences between source and target schemas."""

    added_columns: List[ColumnMeta] = Field(default_factory=list)
    removed_columns: List[ColumnMeta] = Field(default_factory=list)
    type_migrations: List[ColumnMigration] = Field(default_factory=list)
    unchanged_columns: List[str] = Field(default_factory=list)
    has_changes: bool = False


class FieldChange(BaseModel):
    """Field-level change within a modified record."""

    column: str
    source_value: Any
    target_value: Any


class RowChange(BaseModel):
    """Details of a single row modification, addition, or removal."""

    change_type: str  # 'added', 'removed', 'modified'
    key_values: Dict[str, Any]
    field_changes: List[FieldChange] = Field(default_factory=list)
    row_data: Dict[str, Any] = Field(default_factory=dict)


class RowDiffSummary(BaseModel):
    """Aggregated row-level difference counts and samples."""

    keys: List[str] = Field(default_factory=list)
    source_row_count: int = 0
    target_row_count: int = 0
    added_count: int = 0
    removed_count: int = 0
    modified_count: int = 0
    unchanged_count: int = 0
    duplicate_keys_count: int = 0
    sample_added: List[RowChange] = Field(default_factory=list)
    sample_removed: List[RowChange] = Field(default_factory=list)
    sample_modified: List[RowChange] = Field(default_factory=list)


class ColumnStatDiff(BaseModel):
    """Statistical summary and drift for a single column."""

    column: str
    source_null_count: int = 0
    target_null_count: int = 0
    source_null_rate_pct: float = 0.0
    target_null_rate_pct: float = 0.0
    source_distinct_count: int = 0
    target_distinct_count: int = 0
    source_mean: Optional[float] = None
    target_mean: Optional[float] = None
    drift_detected: bool = False
    drift_message: Optional[str] = None


class StatsDiff(BaseModel):
    """Dataset-wide statistical diff and drift results."""

    columns: Dict[str, ColumnStatDiff] = Field(default_factory=dict)
    drift_warnings: List[str] = Field(default_factory=list)


class PolicyReport(BaseModel):
    """CI/CD Quality Gate evaluation results."""

    passed: bool = True
    failures: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class DiffSummary(BaseModel):
    """Complete structured comparison result model."""

    source_name: str
    target_name: str
    schema_diff: SchemaDiff
    row_diff: RowDiffSummary
    stats_diff: StatsDiff
    policy_report: PolicyReport
    execution_time_ms: float = 0.0
