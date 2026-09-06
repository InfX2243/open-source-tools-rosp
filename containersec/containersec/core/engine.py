"""Core security engine that drives Dockerfile scans."""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional, Union

from containersec.core.models import (
    DockerInstruction,
    Finding,
    PolicyReport,
    ScanConfig,
    ScanResult,
    Severity,
)
from containersec.core.parser import DockerfileParser
from containersec.core.scorer import calculate_score
from containersec.rules import ALL_RULES
from containersec.rules.base import BaseRule


class SecurityEngine:
    """Orchestrates parsing, rule evaluation, scoring, and policy enforcement."""

    def __init__(self, config: Optional[ScanConfig] = None):
        self.config = config or ScanConfig()
        self.rules: List[BaseRule] = [rule_cls() for rule_cls in ALL_RULES]

    def scan_content(self, content: str, file_path: str = "Dockerfile") -> ScanResult:
        """Scan Dockerfile content directly from string."""
        start_time = time.perf_counter()

        # Parse Dockerfile
        parser = DockerfileParser()
        instructions: List[DockerInstruction] = parser.parse_content(content)

        findings: List[Finding] = []
        passed_rules: List[str] = []

        # Run rules
        for rule in self.rules:
            rule_def = rule.definition()
            # Check ignore list
            if rule_def.rule_id in self.config.ignore_rules:
                continue

            rule_findings = rule.check(instructions)
            if rule_findings:
                for f in rule_findings:
                    if self._severity_allowed(f.severity):
                        findings.append(f)
            else:
                passed_rules.append(rule_def.rule_id)

        # Sort findings by severity: CRITICAL -> HIGH -> MEDIUM -> LOW -> INFO
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        findings.sort(key=lambda x: (severity_order.get(x.severity, 5), x.line_number or 0))

        # Calculate security score
        score = calculate_score(findings)

        elapsed = (time.perf_counter() - start_time) * 1000.0

        result = ScanResult(
            file_path=file_path,
            file_type="Dockerfile",
            total_lines=len(content.splitlines()),
            total_instructions=len([i for i in instructions if not i.is_comment]),
            findings=findings,
            score=score,
            passed_rules=passed_rules,
            execution_time_ms=round(elapsed, 2),
        )
        result.compute_counts()
        return result

    def scan_file(self, file_path: Union[str, Path]) -> ScanResult:
        """Scan a Dockerfile located on the filesystem."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8", errors="replace")
        return self.scan_content(content, file_path=str(path))

    def evaluate_policy(self, result: ScanResult) -> PolicyReport:
        """Evaluate CI/CD quality gate policy against a scan result."""
        policy = self.config.policy
        report = PolicyReport(passed=True, failures=[], warnings=[])

        if result.critical_count > policy.max_critical:
            report.passed = False
            report.failures.append(
                f"Critical findings ({result.critical_count}) exceed policy limit ({policy.max_critical})"
            )

        if result.high_count > policy.max_high:
            report.passed = False
            report.failures.append(
                f"High findings ({result.high_count}) exceed policy limit ({policy.max_high})"
            )

        if policy.max_medium is not None and result.medium_count > policy.max_medium:
            report.passed = False
            report.failures.append(
                f"Medium findings ({result.medium_count}) exceed policy limit ({policy.max_medium})"
            )

        if result.score.points < policy.min_score:
            report.passed = False
            report.failures.append(
                f"Security score ({result.score.points}/100) is below minimum required ({policy.min_score})"
            )

        if policy.fail_on_secrets:
            secret_findings = [f for f in result.findings if f.category == "secrets"]
            if secret_findings:
                report.passed = False
                report.failures.append(
                    f"Found {len(secret_findings)} hardcoded secrets/credentials (policy forbids secrets in images)"
                )

        return report

    def _severity_allowed(self, finding_severity: Severity) -> bool:
        threshold = self.config.severity_threshold
        levels = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        try:
            return levels.index(finding_severity) >= levels.index(threshold)
        except ValueError:
            return True
