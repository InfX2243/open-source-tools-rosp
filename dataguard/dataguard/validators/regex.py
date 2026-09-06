"""Regex pattern and standard format validator."""

import re
import time
from typing import Any, Dict, List, Optional
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

# Standard built-in regex format definitions
BUILTIN_FORMATS: Dict[str, str] = {
    "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
    "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
    "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    "phone": r"^\+?[0-9]{1,4}?[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}$",
    "iso_date": r"^\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?$",
    "alphanumeric": r"^[a-zA-Z0-9]+$",
    "alphabetic": r"^[a-zA-Z]+$",
    "numeric_string": r"^[0-9]+$",
}


class RegexValidator(Validator):
    """Validates string values against regex patterns or standard formats."""

    name = "regex"

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()

        if column not in df.columns:
            return self.create_result(
                rule_name="regex_check",
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

        pattern_str: Optional[str] = None
        format_name: Optional[str] = None

        if rule.format:
            format_name = rule.format.lower().strip()
            if format_name in BUILTIN_FORMATS:
                pattern_str = BUILTIN_FORMATS[format_name]
            else:
                return self.create_result(
                    rule_name=f"format_check[{format_name}]",
                    column=column,
                    status=RuleStatus.ERROR,
                    severity=rule.severity,
                    checked_count=0,
                    failed_count=0,
                    weight=rule.weight,
                    message=f"Unknown format '{format_name}'. Supported: {list(BUILTIN_FORMATS.keys())}",
                    samples=[],
                    start_time=start_time,
                )
        elif rule.regex:
            pattern_str = rule.regex

        if not pattern_str:
            return self.create_result(
                rule_name="regex_check",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message="No pattern configured",
                samples=[],
                start_time=start_time,
            )

        try:
            compiled_regex = re.compile(pattern_str)
        except re.error as e:
            return self.create_result(
                rule_name="regex_check",
                column=column,
                status=RuleStatus.ERROR,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message=f"Invalid regular expression: {e}",
                samples=[],
                start_time=start_time,
            )

        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows == 0:
            return self.create_result(
                rule_name="regex_check",
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
            # Convert series to string
            str_series = series.cast(pl.Utf8)
            non_null_mask = series.is_not_null() & (str_series.str.strip_chars().str.len_bytes() > 0)
            checked_count = int(non_null_mask.sum())

            if checked_count == 0:
                return self.create_result(
                    rule_name="regex_check",
                    column=column,
                    status=RuleStatus.PASS,
                    severity=rule.severity,
                    checked_count=0,
                    failed_count=0,
                    weight=rule.weight,
                    message="No non-null text values to check",
                    samples=[],
                    start_time=start_time,
                )

            # Polars regex matching
            matches_mask = str_series.str.contains(pattern_str)
            bad_mask = non_null_mask & (~matches_mask)
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
                            reason=f"Value '{val}' does not match pattern '{format_name or pattern_str}'",
                        )
                    )
        else:
            checked_count = 0
            for idx, val in enumerate(df[column]):
                if val is not None and str(val).strip() != "":
                    checked_count += 1
                    s_val = str(val).strip()
                    if not compiled_regex.search(s_val):
                        failed_count += 1
                        if len(samples) < 10:
                            samples.append(
                                FailedSample(
                                    row_index=idx,
                                    column=column,
                                    value=val,
                                    reason=f"Value '{val}' does not match pattern",
                                )
                            )

        display_name = f"format_check[{format_name}]" if format_name else f"regex_check[{pattern_str}]"
        if failed_count == 0:
            status = RuleStatus.PASS
            msg = f"All {checked_count:,} checked values match pattern"
        else:
            status = RuleStatus.FAIL
            rate = (failed_count / checked_count) if checked_count > 0 else 0.0
            msg = f"{failed_count:,} value(s) failed pattern check ({rate:.1%})"

        return self.create_result(
            rule_name=display_name,
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


ValidatorRegistry.register("regex", RegexValidator)
ValidatorRegistry.register("format", RegexValidator)
