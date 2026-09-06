"""Required and Non-Null validator."""

import time
from typing import Any, List
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class RequiredValidator(Validator):
    """Validates that a column does not contain null or empty values."""

    name = "required"

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()
        
        if column not in df.columns:
            return self.create_result(
                rule_name="required_check",
                column=column,
                status=RuleStatus.ERROR,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message=f"Column '{column}' does not exist in dataset",
                samples=[],
                start_time=start_time,
            )

        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows == 0:
            return self.create_result(
                rule_name="required_check",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message="Empty dataset",
                samples=[],
                start_time=start_time,
            )

        samples: List[FailedSample] = []
        failed_count = 0

        if POLARS_AVAILABLE and isinstance(df, pl.DataFrame):
            series = df[column]
            # Identify nulls or empty strings
            is_null_mask = series.is_null()
            if series.dtype in (pl.Utf8, pl.String):
                is_empty_mask = series.str.strip_chars().str.len_bytes() == 0
                bad_mask = is_null_mask | is_empty_mask
            else:
                bad_mask = is_null_mask

            failed_count = int(bad_mask.sum())
            if failed_count > 0:
                # Extract sample failures with row index
                indices = df.with_row_index("row_idx").filter(bad_mask).head(10)
                for row in indices.iter_rows(named=True):
                    samples.append(
                        FailedSample(
                            row_index=row["row_idx"],
                            column=column,
                            value=row[column],
                            reason="Value is null or empty string",
                        )
                    )
        else:
            for idx, val in enumerate(df[column]):
                if val is None or str(val).strip() == "":
                    failed_count += 1
                    if len(samples) < 10:
                        samples.append(
                            FailedSample(
                                row_index=idx,
                                column=column,
                                value=val,
                                reason="Value is null or empty",
                            )
                        )

        failure_rate = failed_count / total_rows
        max_allowed_rate = rule.max_null_rate if rule.max_null_rate is not None else 0.0

        if failed_count == 0 or failure_rate <= max_allowed_rate:
            status = RuleStatus.PASS
            msg = f"All {total_rows:,} records non-null"
        elif rule.max_null_rate is not None and failure_rate > max_allowed_rate:
            status = RuleStatus.FAIL
            msg = f"{failed_count:,} missing values ({failure_rate:.1%}) exceeds threshold {max_allowed_rate:.1%}"
        else:
            status = RuleStatus.FAIL
            msg = f"{failed_count:,} missing/null value(s) found ({failure_rate:.1%})"

        return self.create_result(
            rule_name="required_check",
            column=column,
            status=status,
            severity=rule.severity,
            checked_count=total_rows,
            failed_count=failed_count,
            weight=rule.weight,
            message=msg,
            samples=samples,
            start_time=start_time,
        )


ValidatorRegistry.register("required", RequiredValidator)
