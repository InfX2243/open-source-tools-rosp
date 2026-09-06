"""Tests for CI/CD comparison policy evaluation."""

import polars as pl
from datadiff.comparators.rows import RowComparator
from datadiff.comparators.schema import SchemaComparator
from datadiff.comparators.statistics import StatsComparator
from datadiff.core.models import ComparisonPolicy
from datadiff.core.policies import PolicyEvaluator


def test_policy_evaluator_pass(sample_df_a):
    """Test policy passes when comparing identical dataset."""
    s_diff = SchemaComparator.compare(sample_df_a, sample_df_a)
    r_diff = RowComparator.compare(sample_df_a, sample_df_a, keys=["id"])
    st_diff = StatsComparator.compare(sample_df_a, sample_df_a)

    policy = ComparisonPolicy(
        allow_schema_changes=False,
        max_removed_rows=0,
        max_modified_pct=0.0,
    )

    report = PolicyEvaluator.evaluate(s_diff, r_diff, st_diff, policy)
    assert report.passed
    assert len(report.failures) == 0


def test_policy_evaluator_fail(sample_df_a, sample_df_b):
    """Test policy fails when schema changes and removals exist."""
    s_diff = SchemaComparator.compare(sample_df_a, sample_df_b)
    r_diff = RowComparator.compare(sample_df_a, sample_df_b, keys=["id"])
    st_diff = StatsComparator.compare(sample_df_a, sample_df_b)

    policy = ComparisonPolicy(
        allow_schema_changes=False,
        max_removed_rows=0,
    )

    report = PolicyEvaluator.evaluate(s_diff, r_diff, st_diff, policy)
    assert not report.passed
    assert len(report.failures) >= 2
