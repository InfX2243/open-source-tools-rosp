"""Statistical comparison and data drift comparator."""

from __future__ import annotations

from typing import Dict, List, Optional
import polars as pl
from datadiff.core.models import ColumnStatDiff, StatsDiff, StatsDiffConfig


class StatsComparator:
    """Calculates column-level statistical changes and flags data drift."""

    @classmethod
    def compare(
        cls,
        df_a: pl.DataFrame,
        df_b: pl.DataFrame,
        stats_config: Optional[StatsDiffConfig] = None,
    ) -> StatsDiff:
        cfg = stats_config or StatsDiffConfig()
        columns_stat: Dict[str, ColumnStatDiff] = {}
        drift_warnings: List[str] = []

        all_cols = sorted(set(df_a.columns).union(df_b.columns))

        len_a = len(df_a)
        len_b = len(df_b)

        for col in all_cols:
            # Source stats
            null_a = df_a[col].null_count() if col in df_a.columns else 0
            null_rate_a = (null_a / len_a * 100.0) if len_a > 0 else 0.0
            distinct_a = df_a[col].n_unique() if col in df_a.columns else 0

            # Target stats
            null_b = df_b[col].null_count() if col in df_b.columns else 0
            null_rate_b = (null_b / len_b * 100.0) if len_b > 0 else 0.0
            distinct_b = df_b[col].n_unique() if col in df_b.columns else 0

            # Mean if numeric
            mean_a = None
            mean_b = None
            if col in df_a.columns and df_a[col].dtype.is_numeric():
                mean_a = df_a[col].mean()
            if col in df_b.columns and df_b[col].dtype.is_numeric():
                mean_b = df_b[col].mean()

            # Drift checks
            drift_detected = False
            drift_msg = None

            delta_null = null_rate_b - null_rate_a
            if cfg.track_null_rates and delta_null > cfg.drift_alert_pct:
                drift_detected = True
                drift_msg = f"Column '{col}' NULL rate increased by {delta_null:.1f}% ({null_rate_a:.1f}% -> {null_rate_b:.1f}%)"
                drift_warnings.append(drift_msg)

            columns_stat[col] = ColumnStatDiff(
                column=col,
                source_null_count=null_a,
                target_null_count=null_b,
                source_null_rate_pct=null_rate_a,
                target_null_rate_pct=null_rate_b,
                source_distinct_count=distinct_a,
                target_distinct_count=distinct_b,
                source_mean=mean_a,
                target_mean=mean_b,
                drift_detected=drift_detected,
                drift_message=drift_msg,
            )

        return StatsDiff(columns=columns_stat, drift_warnings=drift_warnings)
