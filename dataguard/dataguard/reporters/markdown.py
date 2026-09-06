"""Markdown summary reporter for GitHub PR comments and CI pipeline logs."""

from dataguard.core.models import ValidationSummary, RuleStatus, Severity
from dataguard.reporters.base import BaseReporter


class MarkdownReporter(BaseReporter):
    """Renders GitHub Flavored Markdown summary."""

    def render(self, summary: ValidationSummary) -> str:
        lines = []
        score = summary.quality_score
        gate_emoji = "✅" if summary.passed_gate else "❌"
        gate_status = "PASSED" if summary.passed_gate else "FAILED"

        lines.append(f"# 🛡️ DataGuard Quality Report: `{summary.dataset_name}`")
        lines.append("")
        lines.append(f"**Quality Score:** `{score:.1f}%` | **Gate Status:** {gate_emoji} **{gate_status}**")
        lines.append(f"**Records Checked:** `{summary.profile.row_count if summary.profile else 'N/A':,}` | **Rules Evaluated:** `{summary.total_rules}` | **Duration:** `{summary.total_duration_ms:.1f}ms`")
        lines.append("")
        lines.append("## 📊 Validation Summary")
        lines.append("")
        lines.append("| Status | Rule / Check | Column | Severity | Checked | Failed | Failure Rate | Message |")
        lines.append("| :---: | :--- | :--- | :---: | ---: | ---: | ---: | :--- |")

        status_emojis = {
            RuleStatus.PASS: "✅ Pass",
            RuleStatus.FAIL: "❌ Fail",
            RuleStatus.WARN: "⚠️ Warn",
            RuleStatus.ERROR: "💥 Error",
            RuleStatus.SKIPPED: "⚪ Skip",
        }

        for res in summary.results:
            st = status_emojis.get(res.status, res.status.value)
            col = f"`{res.column}`" if res.column else "*dataset*"
            rate = f"{res.failure_rate:.1%}" if res.failed_count > 0 else "0.0%"
            lines.append(
                f"| {st} | `{res.rule_name}` | {col} | `{res.severity.value.upper()}` | {res.checked_count:,} | {res.failed_count:,} | {rate} | {res.message} |"
            )

        failed_results = [r for r in summary.results if r.status in (RuleStatus.FAIL, RuleStatus.ERROR) and r.samples]
        if failed_results:
            lines.append("")
            lines.append("## 🔍 Sample Violations")
            lines.append("")
            for r in failed_results:
                col_text = f" on column `{r.column}`" if r.column else ""
                lines.append(f"### `{r.rule_name}`{col_text} - **{r.severity.value.upper()}**")
                lines.append(f"- **Message:** {r.message}")
                lines.append("| Row # | Value | Reason |")
                lines.append("| ---: | :--- | :--- |")
                for s in r.samples[:5]:
                    lines.append(f"| {s.row_index} | `{s.value}` | {s.reason} |")
                lines.append("")

        if summary.anomalies and summary.anomalies.has_anomalies:
            lines.append("")
            lines.append("## ⚠️ Baseline Anomalies")
            for a in summary.anomalies.anomalies:
                lines.append(f"- **[{a.severity.value.upper()}]** {a.description}")

        lines.append("")
        lines.append("---")
        lines.append("*Generated automatically by [DataGuard](https://github.com/dataguard/dataguard)*")

        return "\n".join(lines)
