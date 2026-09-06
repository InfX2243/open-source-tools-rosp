"""Unit tests for ValidationEngine, scoring and quality gate evaluation."""

import pytest
import polars as pl
from dataguard.core.engine import ValidationEngine
from dataguard.core.models import RuleConfig, ColumnRule, DatasetRule, Severity, RuleStatus
from dataguard.core.scoring import calculate_quality_score, evaluate_quality_gate, ThresholdsConfig


def test_engine_valid_data(sample_valid_df):
    config = RuleConfig(
        dataset="test_customers",
        dataset_rules=DatasetRule(min_rows=3, required_columns=["customer_id", "email"]),
        columns={
            "customer_id": ColumnRule(type="integer", required=True, unique=True),
            "email": ColumnRule(type="string", required=True, format="email"),
            "age": ColumnRule(type="integer", min=18, max=100),
            "status": ColumnRule(allowed=["active", "inactive", "pending", "suspended"]),
        },
    )

    engine = ValidationEngine(config)
    summary = engine.validate_dataframe(sample_valid_df, config=config)

    assert summary.quality_score >= 95.0
    assert summary.passed_gate is True
    assert summary.failed_rules == 0
    assert summary.passed_rules > 0


def test_engine_dirty_data_fails_gate(sample_dirty_df):
    config = RuleConfig(
        dataset="dirty_customers",
        thresholds=ThresholdsConfig(fail_on=Severity.HIGH, min_quality_score=90.0),
        columns={
            "customer_id": ColumnRule(required=True, unique=True, severity=Severity.CRITICAL),
            "email": ColumnRule(required=True, format="email", severity=Severity.HIGH),
            "age": ColumnRule(min=18, max=100, severity=Severity.MEDIUM),
            "status": ColumnRule(allowed=["active", "inactive", "pending"], severity=Severity.HIGH),
        },
    )

    engine = ValidationEngine(config)
    summary = engine.validate_dataframe(sample_dirty_df, config=config)

    assert summary.quality_score < 90.0
    assert summary.passed_gate is False
    assert summary.failed_rules > 0
