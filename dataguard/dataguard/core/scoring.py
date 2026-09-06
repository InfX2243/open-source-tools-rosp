"""Data quality scoring engine.

Calculates weighted quality scores and evaluates quality gates
based on rule statuses, violation severities, and failure rates.
"""

from typing import List, Tuple
from dataguard.core.models import (
    ValidationResult,
    RuleStatus,
    Severity,
    ThresholdsConfig,
)

# Severity penalty multipliers
SEVERITY_MULTIPLIERS = {
    Severity.LOW: 0.5,
    Severity.MEDIUM: 1.0,
    Severity.HIGH: 2.0,
    Severity.CRITICAL: 4.0,
}


def calculate_quality_score(results: List[ValidationResult]) -> float:
    """
    Calculate an overall data quality score between 0.0 and 100.0%.
    
    The score is weighted by each rule's configured weight and severity.
    If a rule checks rows, the failure rate (failed_count / checked_count)
    is accounted for rather than treating a single row failure identically
    to a 100% failure, while still penalizing failures.
    """
    if not results:
        return 100.0

    total_weight = 0.0
    weighted_score_sum = 0.0

    for result in results:
        if result.status == RuleStatus.SKIPPED:
            continue

        base_weight = result.weight
        sev_multiplier = SEVERITY_MULTIPLIERS.get(result.severity, 1.0)
        effective_weight = base_weight * sev_multiplier
        total_weight += effective_weight

        if result.status == RuleStatus.PASS:
            rule_score = 100.0
        elif result.status == RuleStatus.WARN:
            rule_score = 80.0
        elif result.status == RuleStatus.ERROR:
            rule_score = 0.0
        elif result.status == RuleStatus.FAIL:
            # If we know the failure rate, calculate granular score with penalty
            if result.checked_count > 0:
                pass_rate = max(0.0, 1.0 - result.failure_rate)
                # Apply a curve: even 1% failure reduces score to max 70% for high sev
                rule_score = pass_rate * 75.0
            else:
                rule_score = 0.0
        else:
            rule_score = 100.0

        weighted_score_sum += rule_score * effective_weight

    if total_weight == 0.0:
        return 100.0

    final_score = weighted_score_sum / total_weight
    return round(max(0.0, min(100.0, final_score)), 2)


def evaluate_quality_gate(
    results: List[ValidationResult],
    quality_score: float,
    thresholds: ThresholdsConfig,
) -> Tuple[bool, str]:
    """
    Evaluate whether the validation run passed configured quality gates.
    
    Returns:
        (passed, reason_message)
    """
    min_rank = Severity.rank(thresholds.fail_on)
    blocking_failures = []

    for res in results:
        if res.status in (RuleStatus.FAIL, RuleStatus.ERROR):
            res_rank = Severity.rank(res.severity)
            if res_rank >= min_rank:
                col_info = f" on column '{res.column}'" if res.column else ""
                blocking_failures.append(
                    f"[{res.severity.value.upper()}] {res.rule_name}{col_info}: {res.message}"
                )

    if quality_score < thresholds.min_quality_score:
        return False, (
            f"Quality score {quality_score:.1f}% is below required threshold "
            f"of {thresholds.min_quality_score:.1f}%"
        )

    if blocking_failures:
        count = len(blocking_failures)
        return False, f"{count} rule(s) failed with severity >= {thresholds.fail_on.value.upper()}"

    return True, "All quality gates satisfied"
