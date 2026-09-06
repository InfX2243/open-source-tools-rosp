"""Uniqueness and Duplicate validator."""

import time
from typing import Any, List
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class UniqueValidator(Validator):
    """Validates that a column contains only distinct / unique values."""

    name = "unique"

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()

        if column not in df.columns:
            return self.create_result(
                rule_name="unique_check",
                column=column,
                status=RuleStatus.ERROR,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message=f"Column '{column}' does not exist",
                samples=[],
                start_time=start_time,
            )

        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows <= 1:
            return self.create_result(
                rule_name="unique_check",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=total_rows,
                failed_count=0,
                weight=rule.weight,
                message="Dataset has <= 1 rows",
                samples=[],
                start_time=start_time,
            )

        samples: List[FailedSample] = []
        failed_count = 0

        if POLARS_AVAILABLE and isinstance(df, pl.DataFrame):
            # Only consider non-null values for uniqueness check
            series = df[column]
            non_null_mask = series.is_not_null()
            checked_count = int(non_null_mask.sum())

            if checked_count <= 1:
                return self.create_result(
                    rule_name="unique_check",
                    column=column,
                    status=RuleStatus.PASS,
                    severity=rule.severity,
                    checked_count=checked_count,
                    failed_count=0,
                    weight=rule.weight,
                    message="<= 1 non-null records to check",
                    samples=[],
                    start_time=start_time,
                )

            # Find duplicates using is_duplicated mask
            dup_mask = series.is_duplicated() & non_null_mask
            # Total duplicate instances
            duplicate_rows_count = int(dup_mask.sum())
            # Failed count can be measured as duplicate rows
            failed_count = duplicate_rows_count

            if failed_count > 0:
                dup_sample_df = df.with_row_index("row_idx").filter(dup_mask).head(10)
                for row in dup_sample_df.iter_rows(named=True):
                    samples.append(
                        FailedSample(
                            row_index=row["row_idx"],
                            column=column,
                            value=row[column],
                            reason=f"Duplicate value '{row[column]}' found",
                        )
                    )
        else:
            checked_count = total_rows
            seen = set()
            dup_set = set()
            for idx, val in enumerate(df[column]):
                if val is not None:
                    if val in seen:
                        dup_set.add(val)
                        if len(samples) < 10:
                            samples.append(
                                FailedSample(
                                    row_index=idx,
                                    column=column,
                                    value=val,
                                    reason=f"Duplicate value '{val}'",
                                )
                            )
                    else:
                        seen.add(val)
            failed_count = len(dup_set)

        dup_rate = (failed_count / checked_count) if checked_count > 0 else 0.0
        max_allowed_rate = rule.max_duplicate_rate if rule.max_duplicate_rate is not None else 0.0

        if failed_count == 0 or dup_rate <= max_allowed_rate:
            status = RuleStatus.PASS
            msg = f"All {checked_count:,} checked values are unique"
        else:
            status = RuleStatus.FAIL
            msg = f"{failed_count:,} duplicate occurrence(s) found ({dup_rate:.1%})"

        return self.create_result(
            rule_name="unique_check",
            column=column,
            status=status,
            severity=rule.severity,
            checked_count=checked_count,
            failed_count=failed_count,
            weight=rule.weight,
            message=msg,
            samples=samples,
            start_time=start_time,
        )


ValidatorRegistry.register("unique", UniqueValidator)
