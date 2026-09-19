"""
Data models for EnvGuard.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IssueType(str, Enum):
    MISSING_KEY = "MISSING_KEY"
    EXTRA_KEY = "EXTRA_KEY"
    EMPTY_VALUE = "EMPTY_VALUE"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    UNMASKED_SECRET = "UNMASKED_SECRET"
    SUSPICIOUS_VALUE = "SUSPICIOUS_VALUE"
    SYNTAX_ERROR = "SYNTAX_ERROR"


class EnvVar(BaseModel):
    key: str
    value: str
    line_number: int
    comment: Optional[str] = None
    is_exported: bool = False
    inferred_type: str = "string"


class EnvFile(BaseModel):
    path: str
    variables: Dict[str, EnvVar] = Field(default_factory=dict)
    raw_lines: List[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    key: str
    severity: Severity
    issue_type: IssueType
    message: str
    line_number: Optional[int] = None
    expected: Optional[str] = None
    actual: Optional[str] = None


class CheckResult(BaseModel):
    env_path: str
    example_path: Optional[str] = None
    passed: bool
    total_checked: int
    issues: List[ValidationIssue] = Field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.LOW)


class DiffType(str, Enum):
    MATCH = "MATCH"
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"


class DiffField(BaseModel):
    key: str
    diff_type: DiffType
    file1_present: bool
    file2_present: bool
    file1_len: Optional[int] = None
    file2_len: Optional[int] = None
    file1_entropy: Optional[float] = None
    file2_entropy: Optional[float] = None
    masked_preview1: Optional[str] = None
    masked_preview2: Optional[str] = None


class DiffResult(BaseModel):
    file1_path: str
    file2_path: str
    fields: List[DiffField] = Field(default_factory=list)
    total_keys: int = 0
    matched: int = 0
    added: int = 0
    removed: int = 0
    modified: int = 0


class SecretFinding(BaseModel):
    file_path: str
    line_number: int
    key_name: str
    secret_type: str
    masked_preview: str
    severity: Severity
    description: str


class CodeReference(BaseModel):
    file_path: str
    line_number: int
    line_content: str
    language: str


class ScanCodebaseResult(BaseModel):
    variables: Dict[str, List[CodeReference]] = Field(default_factory=dict)
    files_scanned: int = 0
    total_references: int = 0
