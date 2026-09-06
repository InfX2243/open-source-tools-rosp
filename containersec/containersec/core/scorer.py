"""Security score calculator."""

from __future__ import annotations

from typing import List, Union
from containersec.core.models import Finding, ScanResult, ScoreGrade, SecurityScore, Severity

# Penalty weights per severity
SEVERITY_PENALTIES = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
    Severity.INFO: 0,
}


def calculate_score(target: Union[ScanResult, List[Finding]]) -> SecurityScore:
    """Calculate a 0-100 security score and letter grade from findings or ScanResult."""
    findings = target.findings if isinstance(target, ScanResult) else target

    penalty = 0
    for finding in findings:
        penalty += SEVERITY_PENALTIES.get(finding.severity, 0)

    points = max(0, 100 - penalty)

    if points >= 95:
        grade = ScoreGrade.A_PLUS
    elif points >= 80:
        grade = ScoreGrade.A
    elif points >= 65:
        grade = ScoreGrade.B
    elif points >= 50:
        grade = ScoreGrade.C
    elif points >= 30:
        grade = ScoreGrade.D
    else:
        grade = ScoreGrade.F

    return SecurityScore(points=points, grade=grade)


# Alias for backwards compatibility
compute_score = calculate_score
