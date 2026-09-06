"""CI/CD Comparison policy evaluator."""

from __future__ import annotations

from typing import List
from datadiff.core.models import (
    ComparisonPolicy,
    PolicyReport,
    RowDiffSummary,
    SchemaDiff,
    StatsDiff,
)


class PolicyEvaluator:
    """Evaluates comparison diff against configured CI/CD quality gate policies."""

    @staticmethod
    def evaluate(
        schema_diff: SchemaDiff,
        row_diff: RowDiffSummary,
        stats_diff: StatsDiff,
        policy: ComparisonPolicy,
    ) -> PolicyReport:
        failures: List[str] = []
        warnings: List[str] = []

        # 1. Schema change checks
        if not policy.allow_schema_changes and schema_diff.has_changes:
            failures.append(
                f"Schema changes are prohibited by policy. Detected: {len(schema_diff.added_columns)} added, {len(schema_diff.removed_columns)} removed, {len(schema_diff.type_migrations)} migrated."
            )

        if not policy.allow_column_removal and schema_diff.removed_columns:
            rem_names = ", ".join(c.name for c in schema_diff.removed_columns)
            failures.append(f"Column removal is prohibited by policy. Removed columns: {rem_names}")

        # 2. Row deletion limit
        if policy.max_removed_rows is not None and row_diff.removed_count > policy.max_removed_rows:
            failures.append(
                f"Removed rows ({row_diff.removed_count}) exceeded policy threshold ({policy.max_removed_rows})."
            )

        # 3. Row modification percentage limit
        if policy.max_modified_pct is not None and row_diff.source_row_count > 0:
            mod_pct = (row_diff.modified_count / row_diff.source_row_count) * 100.0
            if mod_pct > policy.max_modified_pct:
                failures.append(
                    f"Modified rows percentage ({mod_pct:.1f}%) exceeded policy threshold ({policy.max_modified_pct:.1f}%)."
                )

        # 4. Null rate increase limit
        if policy.max_null_rate_increase is not None:
            for col, col_stat in stats_diff.columns.items():
                delta = col_stat.target_null_rate_pct - col_stat.source_null_rate_pct
                if delta > policy.max_null_rate_increase:
                    failures.append(
                        f"Column '{col}' null rate increased by {delta:.1f} percentage points (allowed: {policy.max_null_rate_increase:.1f}%)."
                    )

        # Collect any warnings from drift
        for w in stats_diff.drift_warnings:
            warnings.append(w)

        passed = len(failures) == 0
        return PolicyReport(passed=passed, failures=failures, warnings=warnings)
