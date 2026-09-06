"""Range and boundary bounds validator (min, max, between)."""

import time
from typing import Any, List
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class RangeValidator(Validator):
    """Validates that numeric or date values fall within specified min/max boundaries."""

    name = "range"

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()

        if column not in df.columns:
            return self.create_result(
                rule_name="range_check",
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

        min_val = rule.min
        max_val = rule.max
        if rule.between:
            min_val, max_val = rule.between[0], rule.between[1]

        if min_val is None and max_val is None:
            return self.create_result(
                rule_name="range_check",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message="No range bounds configured",
                samples=[],
                start_time=start_time,
            )

        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows == 0:
            return self.create_result(
                rule_name="range_check",
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
            # Cast to float or keep numeric
            if series.dtype.is_numeric():
                num_series = series.cast(pl.Float64)
            else:
                num_series = series.cast(pl.Utf8).str.strip_chars().cast(pl.Float64, strict=False)

            non_null_mask = num_series.is_not_null()
            checked_count = int(non_null_mask.sum())

            if checked_count == 0:
                return self.create_result(
                    rule_name="range_check",
                    column=column,
                    status=RuleStatus.PASS,
                    severity=rule.severity,
                    checked_count=0,
                    failed_count=0,
                    weight=rule.weight,
                    message="No numeric non-null values to check range",
                    samples=[],
                    start_time=start_time,
                )

            bad_mask = pl.Series(name="bad", values=[False] * total_rows)
            conditions = []

            if min_val is not None:
                conditions.append(num_series < float(min_val))
            if max_val is not None:
                conditions.append(num_series > float(max_val))

            if len(conditions) == 1:
                bad_mask = non_null_mask & conditions[0]
            elif len(conditions) == 2:
                bad_mask = non_null_mask & (conditions[0] | conditions[1])

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
                            reason=f"Value {val} is outside allowed range [{min_val}, {max_val}]",
                        )
                    )
        else:
            checked_count = 0
            for idx, val in enumerate(df[column]):
                if val is not None and str(val).strip() != "":
                    try:
                        n_val = float(val)
                        checked_count += 1
                        if (min_val is not None and n_val < float(min_val)) or (
                            max_val is not None and n_val > float(max_val)
                        ):
                            failed_count += 1
                            if len(samples) < 10:
                                samples.append(
                                    FailedSample(
                                        row_index=idx,
                                        column=column,
                                        value=val,
                                        reason=f"Value {val} outside bounds [{min_val}, {max_val}]",
                                    )
                                )
                    except (ValueError, TypeError):
                        pass

        range_desc = f"[{min_val if min_val is not None else '-inf'}, {max_val if max_val is not None else '+inf'}]"
        if failed_count == 0:
            status = RuleStatus.PASS
            msg = f"All {checked_count:,} checked values within range {range_desc}"
        else:
            status = RuleStatus.FAIL
            rate = (failed_count / checked_count) if checked_count > 0 else 0.0
            msg = f"{failed_count:,} value(s) out of range {range_desc} ({rate:.1%})"

        return self.create_result(
            rule_name="range_check",
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


ValidatorRegistry.register("range", RangeValidator)
