"""Unit tests for statistical profiler and anomaly detection."""

import pytest
import polars as pl
from dataguard.core.profiler import DataProfiler
from dataguard.core.anomaly import AnomalyDetector


def test_profiler_metrics(sample_valid_df):
    profile = DataProfiler.profile_dataframe(sample_valid_df, source_name="test_dataset")
    assert profile.row_count == 10
    assert profile.column_count == 6
    assert "age" in profile.columns

    age_col = profile.columns["age"]
    assert age_col.null_count == 0
    assert age_col.min_value == 19.0
    assert age_col.max_value == 61.0
    assert age_col.mean_value is not None


def test_anomaly_detection():
    # Base profile
    df1 = pl.DataFrame({"id": list(range(100)), "email": ["a@b.com"] * 100})
    base_profile = DataProfiler.profile_dataframe(df1, "baseline")

    # Current profile with sudden 50% null spike in email
    emails = ["a@b.com"] * 50 + [None] * 50
    df2 = pl.DataFrame({"id": list(range(100)), "email": emails})
    curr_profile = DataProfiler.profile_dataframe(df2, "current")

    report = AnomalyDetector.detect(curr_profile, base_profile)
    assert report.has_anomalies is True
    assert len(report.anomalies) >= 1
    assert any(a.metric == "null_rate_drift" for a in report.anomalies)
