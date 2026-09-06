"""Statistical anomaly and metric drift detection engine."""

from typing import Optional, List
from dataguard.core.models import DatasetProfile, AnomalyReport, AnomalyItem, Severity


class AnomalyDetector:
    """Detects schema drift and distribution shifts against a baseline profile."""

    @classmethod
    def detect(
        cls,
        current: DatasetProfile,
        baseline: Optional[DatasetProfile],
        row_count_threshold_pct: float = 20.0,
        null_rate_threshold_pct: float = 10.0,
        uniqueness_threshold_pct: float = 15.0,
    ) -> AnomalyReport:
        """
        Compare current dataset profile against a baseline profile.
        
        Args:
            current: Profile of the current dataset run.
            baseline: Historical reference profile.
            row_count_threshold_pct: Allowed % shift in row count before flagging.
            null_rate_threshold_pct: Allowed absolute change in null % before flagging.
            uniqueness_threshold_pct: Allowed absolute change in uniqueness % before flagging.
        """
        if baseline is None:
            return AnomalyReport(
                has_anomalies=False,
                anomalies=[],
                summary_text="No historical baseline provided for comparison.",
            )

        anomalies: List[AnomalyItem] = []

        # 1. Row count drift
        if baseline.row_count > 0:
            diff = current.row_count - baseline.row_count
            pct_change = (diff / baseline.row_count) * 100.0
            if abs(pct_change) >= row_count_threshold_pct:
                sev = Severity.HIGH if abs(pct_change) >= 50.0 else Severity.MEDIUM
                direction = "increase" if pct_change > 0 else "decrease"
                anomalies.append(
                    AnomalyItem(
                        metric="row_count",
                        column=None,
                        baseline_value=baseline.row_count,
                        current_value=current.row_count,
                        percentage_change=round(pct_change, 2),
                        severity=sev,
                        description=(
                            f"Significant row count {direction}: "
                            f"{baseline.row_count:,} -> {current.row_count:,} ({pct_change:+.1f}%)"
                        ),
                    )
                )

        # 2. Schema check (missing/added columns)
        base_cols = set(baseline.columns.keys())
        curr_cols = set(current.columns.keys())
        missing = base_cols - curr_cols
        if missing:
            anomalies.append(
                AnomalyItem(
                    metric="missing_columns",
                    column=", ".join(sorted(missing)),
                    baseline_value=list(base_cols),
                    current_value=list(curr_cols),
                    percentage_change=100.0,
                    severity=Severity.CRITICAL,
                    description=f"Missing expected columns from baseline: {sorted(missing)}",
                )
            )

        # 3. Column-level drifts
        for col_name, curr_col in current.columns.items():
            if col_name not in baseline.columns:
                continue
            base_col = baseline.columns[col_name]

            # Null percentage drift
            null_diff = curr_col.null_percentage - base_col.null_percentage
            if abs(null_diff) >= null_rate_threshold_pct:
                sev = Severity.HIGH if null_diff > 25.0 else Severity.MEDIUM
                anomalies.append(
                    AnomalyItem(
                        metric="null_rate_drift",
                        column=col_name,
                        baseline_value=f"{base_col.null_percentage:.1f}%",
                        current_value=f"{curr_col.null_percentage:.1f}%",
                        percentage_change=round(null_diff, 2),
                        severity=sev,
                        description=(
                            f"Column '{col_name}' null rate shifted from "
                            f"{base_col.null_percentage:.1f}% to {curr_col.null_percentage:.1f}% ({null_diff:+.1f}%)"
                        ),
                    )
                )

            # Uniqueness drift
            uniq_diff = curr_col.unique_percentage - base_col.unique_percentage
            if abs(uniq_diff) >= uniqueness_threshold_pct:
                anomalies.append(
                    AnomalyItem(
                        metric="uniqueness_drift",
                        column=col_name,
                        baseline_value=f"{base_col.unique_percentage:.1f}%",
                        current_value=f"{curr_col.unique_percentage:.1f}%",
                        percentage_change=round(uniq_diff, 2),
                        severity=Severity.LOW if abs(uniq_diff) < 25.0 else Severity.MEDIUM,
                        description=(
                            f"Column '{col_name}' uniqueness ratio shifted from "
                            f"{base_col.unique_percentage:.1f}% to {curr_col.unique_percentage:.1f}% ({uniq_diff:+.1f}%)"
                        ),
                    )
                )

        has_anomalies = len(anomalies) > 0
        summary = (
            f"Detected {len(anomalies)} metric drift anomaly(ies) compared to baseline."
            if has_anomalies
            else "Dataset metrics are within normal baseline thresholds."
        )

        return AnomalyReport(
            has_anomalies=has_anomalies,
            anomalies=anomalies,
            summary_text=summary,
        )
