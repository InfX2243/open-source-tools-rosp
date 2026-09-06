"""Tests for schema, row, and statistical comparators."""

import polars as pl
from datadiff.comparators.rows import RowComparator
from datadiff.comparators.schema import SchemaComparator
from datadiff.comparators.statistics import StatsComparator
from datadiff.core.models import NormalizationRules, StatsDiffConfig


def test_schema_comparator_identical(sample_df_a):
    """Test schema comparison with identical schemas."""
    diff = SchemaComparator.compare(sample_df_a, sample_df_a)
    assert not diff.has_changes
    assert len(diff.added_columns) == 0
    assert len(diff.removed_columns) == 0
    assert len(diff.type_migrations) == 0


def test_schema_comparator_differences(sample_df_a, sample_df_b):
    """Test schema comparison detecting added column."""
    diff = SchemaComparator.compare(sample_df_a, sample_df_b)
    assert diff.has_changes
    assert len(diff.added_columns) == 1
    assert diff.added_columns[0].name == "tier"
    assert len(diff.removed_columns) == 0


def test_row_comparator_add_remove_modify(sample_df_a, sample_df_b):
    """Test row comparator identifying added, removed, and modified rows."""
    rules = NormalizationRules(numeric_tolerance=0.0)
    diff = RowComparator.compare(
        df_a=sample_df_a,
        df_b=sample_df_b,
        keys=["id"],
        rules=rules,
    )

    assert diff.source_row_count == 4
    assert diff.target_row_count == 4
    assert diff.added_count == 1      # id 105
    assert diff.removed_count == 1    # id 103
    assert diff.modified_count == 2   # id 101 (age, score, email), id 104 (email)
    assert diff.unchanged_count == 1  # id 102


def test_row_comparator_with_tolerance(sample_df_a, sample_df_b):
    """Test row comparator where score difference 95.5 vs 95.505 is within tolerance 0.01."""
    rules = NormalizationRules(numeric_tolerance=0.01)
    diff = RowComparator.compare(
        df_a=sample_df_a,
        df_b=sample_df_b,
        keys=["id"],
        rules=rules,
        ignore_columns=["email", "age"],
    )

    # With email and age ignored, and score within tolerance, id 101 and id 104 should have no changes!
    assert diff.modified_count == 0
    assert diff.unchanged_count == 3


def test_stats_comparator(sample_df_a, sample_df_b):
    """Test statistical comparison calculation."""
    cfg = StatsDiffConfig(track_null_rates=True, drift_alert_pct=10.0)
    stats_diff = StatsComparator.compare(sample_df_a, sample_df_b, stats_config=cfg)

    assert "email" in stats_diff.columns
    email_stat = stats_diff.columns["email"]
    assert email_stat.source_null_count == 1
    assert email_stat.target_null_count == 0
    assert email_stat.source_null_rate_pct == 25.0
    assert email_stat.target_null_rate_pct == 0.0
