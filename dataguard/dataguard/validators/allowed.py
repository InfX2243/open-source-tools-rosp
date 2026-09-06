"""Allowed / Whitelist and Disallowed / Blacklist value validator."""

import time
from typing import Any, List
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class AllowedValuesValidator(Validator):
    """Validates that column values belong to an allowed set or avoid a disallowed set."""

    name = "allowed"

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()

        if column not in df.columns:
            return self.create_result(
                rule_name="allowed_check",
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

        allowed_list = rule.allowed
        disallowed_list = rule.disallowed

        if allowed_list is None and disallowed_list is None:
            return self.create_result(
                rule_name="allowed_check",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message="No allowed/disallowed list configured",
                samples=[],
                start_time=start_time,
            )

        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows == 0:
            return self.create_result(
                rule_name="allowed_check",
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
            # Convert series and allowed values to uniform strings for safe comparison
            str_series = series.cast(pl.Utf8).str.strip_chars()
            non_null_mask = series.is_not_null() & (str_series.str.len_bytes() > 0)
            checked_count = int(non_null_mask.sum())

            if checked_count == 0:
                return self.create_result(
                    rule_name="allowed_check",
                    column=column,
                    status=RuleStatus.PASS,
                    severity=rule.severity,
                    checked_count=0,
                    failed_count=0,
                    weight=rule.weight,
                    message="No non-null values to check",
                    samples=[],
                    start_time=start_time,
                )

            bad_mask = pl.Series(values=[False] * total_rows)

            if allowed_list is not None:
                str_allowed = [str(x).strip() for x in allowed_list]
                is_in_allowed = str_series.is_in(str_allowed)
                bad_mask = non_null_mask & (~is_in_allowed)

            if disallowed_list is not None:
                str_disallowed = [str(x).strip() for x in disallowed_list]
                is_in_disallowed = str_series.is_in(str_disallowed)
                bad_mask = bad_mask | (non_null_mask & is_in_disallowed)

            failed_count = int(bad_mask.sum())
            if failed_count > 0:
                indices = df.with_row_index("row_idx").filter(bad_mask).head(10)
                for row in indices.iter_rows(named=True):
                    val = row[column]
                    samples.append(
                        FailedSample(
                            row_index=row["row_idx"],
                            column=column,
                            value=val,
                            reason=f"Value '{val}' is not permitted by allowed/disallowed rule",
                        )
                    )
        else:
            checked_count = 0
            str_allowed_set = set(str(x).strip() for x in allowed_list) if allowed_list is not None else None
            str_disallowed_set = set(str(x).strip() for x in disallowed_list) if disallowed_list is not None else None

            for idx, val in enumerate(df[column]):
                if val is not None and str(val).strip() != "":
                    checked_count += 1
                    s_val = str(val).strip()
                    is_bad = False
                    if str_allowed_set is not None and s_val not in str_allowed_set:
                        is_bad = True
                    if str_disallowed_set is not None and s_val in str_disallowed_set:
                        is_bad = True

                    if is_bad:
                        failed_count += 1
                        if len(samples) < 10:
                            samples.append(
                                FailedSample(
                                    row_index=idx,
                                    column=column,
                                    value=val,
                                    reason="Value not in permitted set",
                                )
                            )

        rule_label = f"allowed_check[{allowed_list}]" if allowed_list is not None else f"disallowed_check[{disallowed_list}]"
        if failed_count == 0:
            status = RuleStatus.PASS
            msg = f"All {checked_count:,} checked values match permitted set"
        else:
            status = RuleStatus.FAIL
            rate = (failed_count / checked_count) if checked_count > 0 else 0.0
            msg = f"{failed_count:,} value(s) violate permitted set ({rate:.1%})"

        return self.create_result(
            rule_name=rule_label,
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


ValidatorRegistry.register("allowed", AllowedValuesValidator)
ValidatorRegistry.register("disallowed", AllowedValuesValidator)
