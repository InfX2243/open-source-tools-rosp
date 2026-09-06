"""ContainerSec: Open-Source Container & Dockerfile Security Linter — CIS Benchmark Enforcement.

Detect security misconfigurations, enforce CIS Docker Benchmarks, catch leaked secrets,
and auto-fix vulnerabilities before containers hit production.
"""

__version__ = "1.0.0"
__author__ = "Antigravity Team & Contributors"

from containersec.core.models import (
    DockerInstruction,
    Finding,
    RuleDefinition,
    ScanConfig,
    ScanPolicy,
    ScanResult,
    SecurityScore,
    Severity,
    ScoreGrade,
    PolicyReport,
)
from containersec.core.engine import SecurityEngine
from containersec.core.parser import DockerfileParser

__all__ = [
    "__version__",
    "SecurityEngine",
    "DockerfileParser",
    "ScanResult",
    "Finding",
    "Severity",
    "ScoreGrade",
    "SecurityScore",
    "ScanPolicy",
    "ScanConfig",
    "RuleDefinition",
    "PolicyReport",
]
