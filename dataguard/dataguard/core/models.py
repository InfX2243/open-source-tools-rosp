"""Pydantic data models for DataGuard rules, execution results, and dataset profiles."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    """Rule violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def rank(cls, severity: "Severity") -> int:
        ranks = {cls.LOW: 1, cls.MEDIUM: 2, cls.HIGH: 3, cls.CRITICAL: 4}
        return ranks.get(severity, 1)


class RuleStatus(str, Enum):
    """Outcome status of an evaluated rule."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    ERROR = "error"
    SKIPPED = "skipped"


class ColumnRule(BaseModel):
    """Validation constraints defined for a specific dataset column."""
    type: Optional[str] = Field(None, description="Expected data type: string, integer, float, boolean, datetime, date")
    required: Optional[bool] = Field(None, description="If True, null or empty values are disallowed")
    unique: Optional[bool] = Field(None, description="If True, duplicate values are disallowed")
    min: Optional[Union[float, int, str]] = Field(None, description="Minimum acceptable value")
    max: Optional[Union[float, int, str]] = Field(None, description="Maximum acceptable value")
    between: Optional[List[Union[float, int, str]]] = Field(None, description="Inclusive [min, max] range")
    regex: Optional[str] = Field(None, description="Regex pattern the values must match")
    format: Optional[str] = Field(None, description="Standard format: email, url, uuid, ipv4, phone, iso_date")
    allowed: Optional[List[Any]] = Field(None, description="Allowed whitelist of discrete values")
    disallowed: Optional[List[Any]] = Field(None, description="Blacklist of forbidden values")
    max_null_rate: Optional[float] = Field(None, description="Maximum allowed null proportion [0.0 - 1.0]")
    max_duplicate_rate: Optional[float] = Field(None, description="Maximum allowed duplicate proportion [0.0 - 1.0]")
    custom_expr: Optional[str] = Field(None, description="Custom Python validation expression on 'val'")
    severity: Severity = Field(default=Severity.HIGH, description="Violation severity")
    weight: float = Field(default=1.0, ge=0.1, le=10.0, description="Weight in quality score calculation")
    description: Optional[str] = Field(None, description="Human readable description")

    @field_validator("between")
    @classmethod
    def validate_between(cls, v: Optional[List[Any]]) -> Optional[List[Any]]:
        if v is not None and len(v) != 2:
            raise ValueError("'between' range must contain exactly 2 elements [min, max]")
        return v


class DatasetRule(BaseModel):
    """Validation rules evaluated across the entire dataset."""
    min_rows: Optional[int] = Field(None, description="Minimum required row count")
    max_rows: Optional[int] = Field(None, description="Maximum allowed row count")
    required_columns: Optional[List[str]] = Field(None, description="Columns that must exist")
    disallowed_columns: Optional[List[str]] = Field(None, description="Columns that must NOT exist")
    custom_expr: Optional[str] = Field(None, description="Custom dataset-level Python expression on 'df'")
    severity: Severity = Field(default=Severity.HIGH)
    weight: float = Field(default=1.0, ge=0.1, le=10.0)
    description: Optional[str] = None


class ThresholdsConfig(BaseModel):
    """Quality gate threshold settings."""
    fail_on: Severity = Field(default=Severity.HIGH, description="Minimum severity failure that triggers non-zero exit")
    min_quality_score: float = Field(default=80.0, ge=0.0, le=100.0, description="Minimum required overall quality score")


class RuleConfig(BaseModel):
    """Top-level configuration schema for DataGuard rule files."""
    dataset: Optional[str] = Field(None, description="Dataset name or matching filename pattern")
    version: str = Field(default="1.0", description="Configuration schema version")
    description: Optional[str] = Field(None, description="Project or dataset description")
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    dataset_rules: Optional[DatasetRule] = Field(default=None, alias="dataset_checks")
    columns: Dict[str, ColumnRule] = Field(default_factory=dict, description="Per-column validation rules")

    model_config = {"populate_by_name": True}


class FailedSample(BaseModel):
    """Sample record illustrating a rule failure."""
    row_index: int
    column: Optional[str] = None
    value: Any = None
    reason: str


class ValidationResult(BaseModel):
    """Result of an individual rule execution."""
    rule_name: str
    column: Optional[str] = None
    status: RuleStatus
    severity: Severity = Severity.HIGH
    checked_count: int = 0
    failed_count: int = 0
    failure_rate: float = 0.0
    weight: float = 1.0
    message: str = ""
    samples: List[FailedSample] = Field(default_factory=list)
    duration_ms: float = 0.0


class ColumnProfile(BaseModel):
    """Statistical summary and distribution metrics for a single column."""
    column_name: str
    detected_type: str
    total_count: int
    null_count: int
    null_percentage: float
    distinct_count: int
    unique_percentage: float
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_value: Optional[float] = None
    top_values: List[Dict[str, Any]] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    """Complete statistical profile of a dataset."""
    source_name: str
    row_count: int
    column_count: int
    estimated_memory_kb: float
    columns: Dict[str, ColumnProfile]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnomalyItem(BaseModel):
    """A detected anomaly or drift item."""
    metric: str
    column: Optional[str] = None
    baseline_value: Any
    current_value: Any
    percentage_change: float
    severity: Severity
    description: str


class AnomalyReport(BaseModel):
    """Comparison result of a dataset profile against a historical baseline."""
    has_anomalies: bool
    anomalies: List[AnomalyItem] = Field(default_factory=list)
    summary_text: str = ""


class ValidationSummary(BaseModel):
    """Comprehensive aggregation of a complete validation run."""
    dataset_name: str
    source_path: str
    quality_score: float = 100.0
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    warned_rules: int = 0
    errored_rules: int = 0
    results: List[ValidationResult] = Field(default_factory=list)
    profile: Optional[DatasetProfile] = None
    anomalies: Optional[AnomalyReport] = None
    passed_gate: bool = True
    gate_reason: Optional[str] = None
    total_duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
