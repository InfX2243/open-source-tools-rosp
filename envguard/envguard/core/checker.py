"""
Drift detection, schema validation, and sanity checker for .env files.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from envguard.core.models import (
    CheckResult,
    EnvFile,
    IssueType,
    Severity,
    ValidationIssue,
)
from envguard.core.parser import parse_env_file, infer_variable_type
from envguard.core.secrets import scan_text_for_secrets

PLACEHOLDER_SUBSTRINGS = [
    "changeme",
    "replace_me",
    "your_key_here",
    "your_secret_here",
    "todo",
    "xxx",
    "dummy_value",
    "insert_",
    "your-api-key",
]


def is_suspicious_placeholder(val: str) -> bool:
    """Check if value looks like an unfilled boilerplate placeholder."""
    v = val.strip().lower()
    return any(p in v for p in PLACEHOLDER_SUBSTRINGS)


def validate_type(key: str, val: str, expected_type: str) -> bool:
    """Validate if value satisfies expected type."""
    exp = expected_type.lower().strip()
    inferred = infer_variable_type(key, val)

    if exp in ("string", "str"):
        return True
    if exp in ("int", "integer"):
        return inferred == "integer"
    if exp in ("float", "number"):
        return inferred in ("integer", "float")
    if exp in ("bool", "boolean"):
        return inferred == "boolean"
    if exp == "port":
        return inferred == "port"
    if exp == "url":
        return inferred == "url"
    if exp == "email":
        return inferred == "email"
    if exp == "json":
        return inferred == "json"
    return True


def check_env(
    env_path: str,
    example_path: Optional[str] = None,
    schema_path: Optional[str] = None,
    strict: bool = False,
) -> CheckResult:
    """
    Validate target .env against .env.example or declarative schema.
    """
    env_file = parse_env_file(env_path)
    issues: List[ValidationIssue] = []

    # 1. Secret scanning on the .env file
    with open(env_path, "r", encoding="utf-8", errors="replace") as f:
        env_content = f.read()
    secret_findings = scan_text_for_secrets(env_content, file_path=env_path)
    for finding in secret_findings:
        issues.append(
            ValidationIssue(
                key=finding.key_name,
                severity=finding.severity,
                issue_type=IssueType.UNMASKED_SECRET,
                message=f"Live secret detected: {finding.description} (preview: {finding.masked_preview})",
                line_number=finding.line_number,
            )
        )

    # 2. Check for suspicious placeholders or empty values
    for var in env_file.variables.values():
        if not var.value.strip():
            issues.append(
                ValidationIssue(
                    key=var.key,
                    severity=Severity.MEDIUM if not strict else Severity.HIGH,
                    issue_type=IssueType.EMPTY_VALUE,
                    message=f"Environment variable '{var.key}' is defined but has an empty value.",
                    line_number=var.line_number,
                )
            )
        elif is_suspicious_placeholder(var.value):
            issues.append(
                ValidationIssue(
                    key=var.key,
                    severity=Severity.HIGH,
                    issue_type=IssueType.SUSPICIOUS_VALUE,
                    message=f"Variable '{var.key}' contains placeholder text ('{var.value[:15]}...').",
                    line_number=var.line_number,
                )
            )

    # 3. Check against .env.example (if provided)
    if example_path and os.path.exists(example_path):
        example_file = parse_env_file(example_path)

        # Missing keys: in example but not in env
        for ex_key, ex_var in example_file.variables.items():
            if ex_key not in env_file.variables:
                issues.append(
                    ValidationIssue(
                        key=ex_key,
                        severity=Severity.CRITICAL if strict else Severity.HIGH,
                        issue_type=IssueType.MISSING_KEY,
                        message=f"Missing variable '{ex_key}' required by {os.path.basename(example_path)}.",
                        line_number=ex_var.line_number,
                        expected=f"Type: {ex_var.inferred_type}",
                        actual="<not present>",
                    )
                )
            else:
                # Type drift between example and env
                actual_var = env_file.variables[ex_key]
                if ex_var.inferred_type not in ("string", "empty"):
                    if not validate_type(ex_key, actual_var.value, ex_var.inferred_type):
                        issues.append(
                            ValidationIssue(
                                key=ex_key,
                                severity=Severity.HIGH,
                                issue_type=IssueType.TYPE_MISMATCH,
                                message=(
                                    f"Type mismatch for '{ex_key}': expected {ex_var.inferred_type}, "
                                    f"got '{actual_var.value}' ({actual_var.inferred_type})."
                                ),
                                line_number=actual_var.line_number,
                                expected=ex_var.inferred_type,
                                actual=actual_var.inferred_type,
                            )
                        )

        # Extra keys: in env but not in example
        for env_key, env_var in env_file.variables.items():
            if env_key not in example_file.variables:
                issues.append(
                    ValidationIssue(
                        key=env_key,
                        severity=Severity.LOW if not strict else Severity.MEDIUM,
                        issue_type=IssueType.EXTRA_KEY,
                        message=f"Undocumented variable '{env_key}' found in .env (not present in {os.path.basename(example_path)}).",
                        line_number=env_var.line_number,
                    )
                )

    # 4. Check against declarative schema (if provided)
    if schema_path and os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_data = yaml.safe_load(f) or {}

        rules: Dict[str, Any] = schema_data.get("variables", {})
        for req_key, rule in rules.items():
            is_required = rule.get("required", True)
            expected_type = rule.get("type", "string")

            if req_key not in env_file.variables:
                if is_required:
                    issues.append(
                        ValidationIssue(
                            key=req_key,
                            severity=Severity.CRITICAL,
                            issue_type=IssueType.MISSING_KEY,
                            message=f"Missing required variable '{req_key}' specified in schema.",
                            expected=expected_type,
                            actual="<missing>",
                        )
                    )
            else:
                val = env_file.variables[req_key].value
                if not validate_type(req_key, val, expected_type):
                    issues.append(
                        ValidationIssue(
                            key=req_key,
                            severity=Severity.HIGH,
                            issue_type=IssueType.TYPE_MISMATCH,
                            message=f"Schema violation for '{req_key}': expected {expected_type}, got '{val}'.",
                            line_number=env_file.variables[req_key].line_number,
                            expected=expected_type,
                            actual=env_file.variables[req_key].inferred_type,
                        )
                    )

    passed = not any(i.severity in (Severity.CRITICAL, Severity.HIGH) for i in issues)
    return CheckResult(
        env_path=os.path.abspath(env_path),
        example_path=os.path.abspath(example_path) if example_path else None,
        passed=passed,
        total_checked=len(env_file.variables),
        issues=issues,
    )
