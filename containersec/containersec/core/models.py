"""Pydantic data models for ContainerSec scan results, rules, and configuration."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Security finding severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class DockerInstruction(BaseModel):
    """Parsed representation of a single Dockerfile instruction."""
    line_number: int
    instruction: str          # FROM, RUN, COPY, ENV, EXPOSE, etc.
    arguments: str            # The raw argument string after the instruction
    original_line: str        # Complete original line text
    is_comment: bool = False


class RuleDefinition(BaseModel):
    """Metadata definition for a security rule."""
    rule_id: str = Field(description="Unique rule identifier e.g. CIS-4.1, SEC-003")
    title: str = Field(description="Short human-readable rule title")
    description: str = Field(description="Detailed explanation of the security concern")
    severity: Severity = Field(default=Severity.MEDIUM)
    category: str = Field(default="general", description="Rule category: cis, secrets, best-practice")
    cis_benchmark: Optional[str] = Field(default=None, description="CIS Benchmark reference ID")
    fix_suggestion: str = Field(default="", description="Recommended remediation")
    references: List[str] = Field(default_factory=list, description="External reference URLs")


class Finding(BaseModel):
    """A single security issue discovered during a scan."""
    rule_id: str
    title: str
    severity: Severity
    category: str
    line_number: Optional[int] = None
    line_content: Optional[str] = None
    description: str = ""
    fix_suggestion: str = ""
    fixed_line: Optional[str] = None


class ScoreGrade(str, Enum):
    """Security score letter grades."""
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class SecurityScore(BaseModel):
    """Calculated security score and letter grade."""
    points: int = Field(default=100, description="Numeric score 0-100")
    grade: ScoreGrade = Field(default=ScoreGrade.A_PLUS)
    max_points: int = 100


class ScanResult(BaseModel):
    """Complete scan result for a Dockerfile or container configuration."""
    file_path: str
    file_type: str = "Dockerfile"
    total_lines: int = 0
    total_instructions: int = 0
    findings: List[Finding] = Field(default_factory=list)
    score: SecurityScore = Field(default_factory=SecurityScore)

    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0

    passed_rules: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0

    def compute_counts(self):
        """Recompute severity counts from findings list."""
        self.critical_count = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        self.high_count = sum(1 for f in self.findings if f.severity == Severity.HIGH)
        self.medium_count = sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
        self.low_count = sum(1 for f in self.findings if f.severity == Severity.LOW)
        self.info_count = sum(1 for f in self.findings if f.severity == Severity.INFO)


class ScanPolicy(BaseModel):
    """CI/CD quality gate policy for container scans."""
    max_critical: int = Field(default=0, description="Max allowed critical findings")
    max_high: int = Field(default=0, description="Max allowed high findings")
    max_medium: Optional[int] = Field(default=None, description="Max allowed medium findings")
    min_score: int = Field(default=60, description="Minimum security score to pass gate")
    fail_on_secrets: bool = Field(default=True, description="Fail if any hardcoded secrets found")


class PolicyReport(BaseModel):
    """CI/CD quality gate evaluation result."""
    passed: bool = True
    failures: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ScanConfig(BaseModel):
    """Root configuration for a ContainerSec scan."""
    target_path: Optional[str] = None
    policy: ScanPolicy = Field(default_factory=ScanPolicy)
    ignore_rules: List[str] = Field(default_factory=list, description="Rule IDs to skip")
    severity_threshold: Severity = Field(default=Severity.INFO, description="Minimum severity to report")
