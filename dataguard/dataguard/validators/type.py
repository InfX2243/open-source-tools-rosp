"""Data type conformance validator."""

import time
from typing import Any, List
from datetime import datetime
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class TypeValidator(Validator):
    """Validates that values conform to expected data types."""

    name = "type"

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()

        if column not in df.columns:
            return self.create_result(
                rule_name="type_check",
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

        expected_type = (rule.type or "").lower().strip()
        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows == 0 or not expected_type:
            return self.create_result(
                rule_name="type_check",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=total_rows,
                failed_count=0,
                weight=rule.weight,
                message="No type check applied",
                samples=[],
                start_time=start_time,
            )

        samples: List[FailedSample] = []
        failed_count = 0

        if POLARS_AVAILABLE and isinstance(df, pl.DataFrame):
            series = df[column]
            non_null_mask = series.is_not_null()
            checked_count = int(non_null_mask.sum())

            if checked_count == 0:
                return self.create_result(
                    rule_name="type_check",
                    column=column,
                    status=RuleStatus.PASS,
                    severity=rule.severity,
                    checked_count=0,
                    failed_count=0,
                    weight=rule.weight,
                    message="All records are null",
                    samples=[],
                    start_time=start_time,
                )

            # Perform parsing checks based on expected type
            bad_mask = pl.Series(name="bad", values=[False] * total_rows)

            if expected_type in ("integer", "int", "int64", "int32"):
                if series.dtype.is_integer():
                    bad_mask = pl.Series(values=[False] * total_rows)
                else:
                    # Try cast to Int64, invalid become null
                    cast_res = series.cast(pl.Utf8).str.strip_chars()
                    # Check regex integer or try cast
                    parsed = cast_res.cast(pl.Int64, strict=False)
                    bad_mask = non_null_mask & parsed.is_null()

            elif expected_type in ("float", "double", "numeric", "number"):
                if series.dtype.is_numeric():
                    bad_mask = pl.Series(values=[False] * total_rows)
                else:
                    cast_res = series.cast(pl.Utf8).str.strip_chars()
                    parsed = cast_res.cast(pl.Float64, strict=False)
                    bad_mask = non_null_mask & parsed.is_null()

            elif expected_type in ("boolean", "bool"):
                if series.dtype == pl.Boolean:
                    bad_mask = pl.Series(values=[False] * total_rows)
                else:
                    s_str = series.cast(pl.Utf8).str.to_lowercase().str.strip_chars()
                    valid_bools = ["true", "false", "1", "0", "yes", "no", "t", "f", "y", "n"]
                    bad_mask = non_null_mask & (~s_str.is_in(valid_bools))

            elif expected_type in ("date", "datetime", "timestamp"):
                if series.dtype in (pl.Date, pl.Datetime):
                    bad_mask = pl.Series(values=[False] * total_rows)
                else:
                    # Check date parsing
                    bad_indices = []
                    s_list = series.to_list()
                    for idx, val in enumerate(s_list):
                        if val is not None and str(val).strip():
                            if not self._is_valid_date(str(val)):
                                bad_indices.append(idx)
                                if len(samples) < 10:
                                    samples.append(
                                        FailedSample(
                                            row_index=idx,
                                            column=column,
                                            value=val,
                                            reason=f"Cannot parse as {expected_type}",
                                        )
                                    )
                    failed_count = len(bad_indices)
                    return self._build_result(column, expected_type, checked_count, failed_count, samples, rule, start_time)

            elif expected_type in ("string", "str", "text"):
                bad_mask = pl.Series(values=[False] * total_rows)
            else:
                # Unsupported type name
                pass

            failed_count = int(bad_mask.sum())
            if failed_count > 0:
                indices = df.with_row_index("row_idx").filter(bad_mask).head(10)
                for row in indices.iter_rows(named=True):
                    samples.append(
                        FailedSample(
                            row_index=row["row_idx"],
                            column=column,
                            value=row[column],
                            reason=f"Value '{row[column]}' does not conform to expected type '{expected_type}'",
                        )
                    )

            return self._build_result(column, expected_type, checked_count, failed_count, samples, rule, start_time)

        return self.create_result(
            rule_name="type_check",
            column=column,
            status=RuleStatus.PASS,
            severity=rule.severity,
            checked_count=total_rows,
            failed_count=0,
            weight=rule.weight,
            message=f"Type check passed ({expected_type})",
            samples=[],
            start_time=start_time,
        )

    def _is_valid_date(self, val_str: str) -> bool:
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        for fmt in formats:
            try:
                datetime.strptime(val_str.strip(), fmt)
                return True
            except ValueError:
                continue
        return False

    def _build_result(
        self,
        column: str,
        expected_type: str,
        checked_count: int,
        failed_count: int,
        samples: List[FailedSample],
        rule: ColumnRule,
        start_time: float,
    ) -> ValidationResult:
        if failed_count == 0:
            status = RuleStatus.PASS
            msg = f"All {checked_count:,} checked values match type '{expected_type}'"
        else:
            status = RuleStatus.FAIL
            rate = (failed_count / checked_count) if checked_count > 0 else 0.0
            msg = f"{failed_count:,} value(s) failed type check '{expected_type}' ({rate:.1%})"

        return self.create_result(
            rule_name=f"type_check[{expected_type}]",
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


ValidatorRegistry.register("type", TypeValidator)
