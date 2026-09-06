"""Custom expression and Python formula validator."""

import time
from typing import Any, List
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, FailedSample
from dataguard.validators.base import Validator, ValidatorRegistry

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class CustomValidator(Validator):
    """Validates records against custom Python boolean expressions on 'val'."""

    name = "custom"

    # Safe builtins exposed to expressions
    SAFE_GLOBALS = {
        "__builtins__": {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "isinstance": isinstance,
        }
    }

    def validate(self, df: Any, column: str, rule: ColumnRule) -> ValidationResult:
        start_time = time.perf_counter()

        if column not in df.columns:
            return self.create_result(
                rule_name="custom_expr",
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

        expr_str = (rule.custom_expr or "").strip()
        if not expr_str:
            return self.create_result(
                rule_name="custom_expr",
                column=column,
                status=RuleStatus.PASS,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message="No custom expression provided",
                samples=[],
                start_time=start_time,
            )

        try:
            compiled_code = compile(expr_str, "<custom_rule>", "eval")
        except SyntaxError as e:
            return self.create_result(
                rule_name=f"custom_expr[{expr_str}]",
                column=column,
                status=RuleStatus.ERROR,
                severity=rule.severity,
                checked_count=0,
                failed_count=0,
                weight=rule.weight,
                message=f"Syntax error in expression: {e}",
                samples=[],
                start_time=start_time,
            )

        total_rows = df.height if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else len(df)
        if total_rows == 0:
            return self.create_result(
                rule_name=f"custom_expr[{expr_str}]",
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
        checked_count = 0

        # Iterate over records safely
        series_vals = df[column].to_list() if POLARS_AVAILABLE and isinstance(df, pl.DataFrame) else df[column]

        for idx, val in enumerate(series_vals):
            if val is not None:
                checked_count += 1
                try:
                    result = eval(compiled_code, self.SAFE_GLOBALS, {"val": val, "x": val})
                    if not bool(result):
                        failed_count += 1
                        if len(samples) < 10:
                            samples.append(
                                FailedSample(
                                    row_index=idx,
                                    column=column,
                                    value=val,
                                    reason=f"Expression '{expr_str}' evaluated to False for val={val}",
                                )
                            )
                except Exception as e:
                    failed_count += 1
                    if len(samples) < 10:
                        samples.append(
                            FailedSample(
                                row_index=idx,
                                column=column,
                                value=val,
                                reason=f"Expression evaluation error: {e}",
                            )
                        )

        if failed_count == 0:
            status = RuleStatus.PASS
            msg = f"All {checked_count:,} records satisfied expression '{expr_str}'"
        else:
            status = RuleStatus.FAIL
            rate = (failed_count / checked_count) if checked_count > 0 else 0.0
            msg = f"{failed_count:,} record(s) failed expression '{expr_str}' ({rate:.1%})"

        return self.create_result(
            rule_name=f"custom_expr[{expr_str}]",
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


ValidatorRegistry.register("custom", CustomValidator)
