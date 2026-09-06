"""Markdown reporter for CI/CD and Pull Request change reviews."""

from __future__ import annotations

from datadiff.core.models import DiffSummary
from datadiff.reporters.base import BaseReporter


class MarkdownReporter(BaseReporter):
    """Formats comparison results into clean GitHub-flavored Markdown."""

    def render(self, diff: DiffSummary) -> str:
        r = diff.row_diff
        s = diff.schema_diff
        pol = diff.policy_report

        status_badge = ":white_check_mark: **PASSED**" if pol.passed else ":x: **FAILED**"

        lines = [
            f"# DataDiff Comparison Report",
            f"",
            f"**Source:** `{diff.source_name}` &rarr; **Target:** `{diff.target_name}`  ",
            f"**Status:** {status_badge} | **Execution Time:** `{diff.execution_time_ms:.1f}ms`",
            f"",
            f"## Summary Metrics",
            f"",
            f"| Metric | Source | Target | Change |",
            f"| :--- | :---: | :---: | :---: |",
            f"| **Total Rows** | `{r.source_row_count:,}` | `{r.target_row_count:,}` | `{r.target_row_count - r.source_row_count:+d}` |",
            f"| **Added Rows** | - | `{r.added_count:,}` | :heavy_plus_sign: `+{r.added_count:,}` |",
            f"| **Removed Rows** | `{r.removed_count:,}` | - | :heavy_minus_sign: `-{r.removed_count:,}` |",
            f"| **Modified Rows** | - | - | :pencil2: `{r.modified_count:,}` |",
            f"| **Unchanged Rows** | - | - | :white_circle: `{r.unchanged_count:,}` |",
            f"",
        ]

        # Schema Diff
        lines.append("## Schema Changes")
        if not s.has_changes:
            lines.append(":white_check_mark: No schema differences detected.")
        else:
            lines.append("| Type | Column | Source Type | Target Type |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for col in s.added_columns:
                lines.append(f"| :heavy_plus_sign: ADD | `{col.name}` | - | `{col.dtype}` |")
            for col in s.removed_columns:
                lines.append(f"| :heavy_minus_sign: REMOVE | `{col.name}` | `{col.dtype}` | - |")
            for mig in s.type_migrations:
                lines.append(f"| :arrows_counterclockwise: TYPE | `{mig.column}` | `{mig.source_dtype}` | `{mig.target_dtype}` |")
        lines.append("")

        # Sample Modified Records
        if r.sample_modified:
            lines.append("## Sample Modified Records")
            lines.append("<details><summary>Click to view modified records diff</summary>")
            lines.append("")
            for mod in r.sample_modified[:10]:
                keys_str = ", ".join(f"`{k}={v}`" for k, v in mod.key_values.items())
                lines.append(f"- **Key ({keys_str})**:")
                for fc in mod.field_changes:
                    lines.append(f"  - `{fc.column}`: `{fc.source_value}` &rarr; **`{fc.target_value}`**")
            lines.append("</details>")
            lines.append("")

        # Policy Failures
        if not pol.passed:
            lines.append("## Quality Gate Violations")
            for f in pol.failures:
                lines.append(f"- :x: {f}")
            lines.append("")

        return "\n".join(lines)
