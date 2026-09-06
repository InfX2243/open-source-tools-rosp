"""Core Validation Engine for orchestrating dataset checks and quality scoring."""

import time
from typing import Any, Optional, List
from dataguard.core.models import (
    RuleConfig,
    ValidationResult,
    ValidationSummary,
    DatasetProfile,
    RuleStatus,
    Severity,
    FailedSample,
)
from dataguard.core.profiler import DataProfiler
from dataguard.core.scoring import calculate_quality_score, evaluate_quality_gate
from dataguard.core.anomaly import AnomalyDetector
from dataguard.sources import load_dataset
from dataguard.validators.base import ValidatorRegistry
# Ensure all validators are registered
import dataguard.validators  # noqa: F401

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class ValidationEngine:
    """Orchestrator for data ingestion, rule evaluation, profiling, and scoring."""

    def __init__(self, config: Optional[RuleConfig] = None):
        self.config = config or RuleConfig()

    def validate_source(
        self,
        source: str,
        config: Optional[RuleConfig] = None,
        baseline_profile: Optional[DatasetProfile] = None,
        profile_data: bool = True,
        **adapter_kwargs: Any,
    ) -> ValidationSummary:
        """
        Load data from source and run full validation against configuration rules.
        """
        cfg = config or self.config
        df = load_dataset(source, **adapter_kwargs)
        return self.validate_dataframe(
            df=df,
            source_path=source,
            config=cfg,
            baseline_profile=baseline_profile,
            profile_data=profile_data,
        )

    def validate_dataframe(
        self,
        df: Any,
        source_path: str = "in_memory",
        config: Optional[RuleConfig] = None,
        baseline_profile: Optional[DatasetProfile] = None,
        profile_data: bool = True,
    ) -> ValidationSummary:
        """
        Run validation and profiling on an in-memory DataFrame or record collection.
        """
        start_time = time.perf_counter()
        cfg = config or self.config
        dataset_name = cfg.dataset or source_path

        # 1. Profile dataset
        profile: Optional[DatasetProfile] = None
        if profile_data:
            profile = DataProfiler.profile_dataframe(df, source_name=dataset_name)

        # 2. Run dataset-level checks
        results: List[ValidationResult] = []
        if cfg.dataset_rules:
            results.extend(self._evaluate_dataset_rules(df, cfg.dataset_rules))

        # 3. Run column-level checks
        for col_name, col_rule in cfg.columns.items():
            results.extend(self._evaluate_column_rules(df, col_name, col_rule))

        # 4. Score calculation
        quality_score = calculate_quality_score(results)

        # 5. Evaluate quality gate
        passed_gate, gate_reason = evaluate_quality_gate(
            results=results,
            quality_score=quality_score,
            thresholds=cfg.thresholds,
        )

        # 6. Anomaly detection if baseline profile is provided
        anomaly_report = None
        if profile and baseline_profile:
            anomaly_report = AnomalyDetector.detect(profile, baseline_profile)

        # 7. Aggregate counts
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r.status == RuleStatus.PASS)
        failed_rules = sum(1 for r in results if r.status == RuleStatus.FAIL)
        warned_rules = sum(1 for r in results if r.status == RuleStatus.WARN)
        errored_rules = sum(1 for r in results if r.status == RuleStatus.ERROR)

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

        return ValidationSummary(
            dataset_name=dataset_name,
            source_path=source_path,
            quality_score=quality_score,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            warned_rules=warned_rules,
            errored_rules=errored_rules,
            results=results,
            profile=profile,
            anomalies=anomaly_report,
            passed_gate=passed_gate,
            gate_reason=gate_reason,
            total_duration_ms=duration_ms,
        )

    def _evaluate_dataset_rules(self, df: Any, dataset_rule: Any) -> List[ValidationResult]:
        """Evaluate dataset-wide rules."""
        results: List[ValidationResult] = []
        start_time = time.perf_counter()
        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        columns = df.columns if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else (list(df[0].keys()) if total_rows > 0 else [])

        # Row count checks
        if dataset_rule.min_rows is not None:
            passed = total_rows >= dataset_rule.min_rows
            status = RuleStatus.PASS if passed else RuleStatus.FAIL
            msg = f"Dataset row count {total_rows:,} satisfies minimum {dataset_rule.min_rows:,}" if passed else f"Dataset row count {total_rows:,} is below minimum {dataset_rule.min_rows:,}"
            results.append(
                ValidationResult(
                    rule_name=f"min_rows[{dataset_rule.min_rows}]",
                    column=None,
                    status=status,
                    severity=dataset_rule.severity,
                    checked_count=total_rows,
                    failed_count=0 if passed else 1,
                    weight=dataset_rule.weight,
                    message=msg,
                    duration_ms=round((time.perf_counter() - start_time) * 1000.0, 3),
                )
            )

        if dataset_rule.max_rows is not None:
            passed = total_rows <= dataset_rule.max_rows
            status = RuleStatus.PASS if passed else RuleStatus.FAIL
            msg = f"Dataset row count {total_rows:,} is within maximum {dataset_rule.max_rows:,}" if passed else f"Dataset row count {total_rows:,} exceeds maximum {dataset_rule.max_rows:,}"
            results.append(
                ValidationResult(
                    rule_name=f"max_rows[{dataset_rule.max_rows}]",
                    column=None,
                    status=status,
                    severity=dataset_rule.severity,
                    checked_count=total_rows,
                    failed_count=0 if passed else 1,
                    weight=dataset_rule.weight,
                    message=msg,
                    duration_ms=round((time.perf_counter() - start_time) * 1000.0, 3),
                )
            )

        # Required columns check
        if dataset_rule.required_columns:
            missing_cols = [c for c in dataset_rule.required_columns if c not in columns]
            passed = len(missing_cols) == 0
            status = RuleStatus.PASS if passed else RuleStatus.FAIL
            msg = "All required columns are present" if passed else f"Missing required columns: {missing_cols}"
            results.append(
                ValidationResult(
                    rule_name="required_columns_check",
                    column=None,
                    status=status,
                    severity=dataset_rule.severity,
                    checked_count=len(dataset_rule.required_columns),
                    failed_count=len(missing_cols),
                    weight=dataset_rule.weight,
                    message=msg,
                    duration_ms=round((time.perf_counter() - start_time) * 1000.0, 3),
                )
            )

        return results

    def _evaluate_column_rules(self, df: Any, column: str, rule: Any) -> List[ValidationResult]:
        """Evaluate applicable validators for a column definition."""
        results: List[ValidationResult] = []

        # 1. Required / Null check
        if rule.required is not None or rule.max_null_rate is not None:
            val_cls = ValidatorRegistry.get("required")
            results.append(val_cls().validate(df, column, rule))

        # 2. Type check
        if rule.type is not None:
            val_cls = ValidatorRegistry.get("type")
            results.append(val_cls().validate(df, column, rule))

        # 3. Unique check
        if rule.unique is not None or rule.max_duplicate_rate is not None:
            val_cls = ValidatorRegistry.get("unique")
            results.append(val_cls().validate(df, column, rule))

        # 4. Range / Bounds check
        if rule.min is not None or rule.max is not None or rule.between is not None:
            val_cls = ValidatorRegistry.get("range")
            results.append(val_cls().validate(df, column, rule))

        # 5. Regex / Format check
        if rule.regex is not None or rule.format is not None:
            val_cls = ValidatorRegistry.get("regex")
            results.append(val_cls().validate(df, column, rule))

        # 6. Allowed / Disallowed check
        if rule.allowed is not None or rule.disallowed is not None:
            val_cls = ValidatorRegistry.get("allowed")
            results.append(val_cls().validate(df, column, rule))

        # 7. Custom expression
        if rule.custom_expr is not None:
            val_cls = ValidatorRegistry.get("custom")
            results.append(val_cls().validate(df, column, rule))

        return results
