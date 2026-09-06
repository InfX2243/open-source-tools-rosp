"""Secret detection rules for Dockerfiles."""

from __future__ import annotations

import re
from typing import List

from containersec.core.models import DockerInstruction, Finding, RuleDefinition, Severity
from containersec.rules.base import BaseRule


# Common secret patterns
SECRET_PATTERNS = [
    (r"(?i)(password|passwd|pwd)\s*=\s*\S+", "password"),
    (r"(?i)(secret|secret_key|api_secret)\s*=\s*\S+", "secret_key"),
    (r"(?i)(api_key|apikey)\s*=\s*\S+", "api_key"),
    (r"(?i)(access_key|aws_access_key_id)\s*=\s*\S+", "aws_access_key"),
    (r"(?i)(token|auth_token|bearer)\s*=\s*\S+", "token"),
    (r"(?i)(private_key|priv_key)\s*=\s*\S+", "private_key"),
    (r"(?i)(connection_string|conn_str|database_url|db_url)\s*=\s*\S+", "connection_string"),
    (r"AKIA[0-9A-Z]{16}", "aws_access_key_id"),
    (r"(?i)ghp_[A-Za-z0-9_]{36,}", "github_pat"),
    (r"(?i)sk-[A-Za-z0-9]{20,}", "openai_api_key"),
    (r"(?i)xox[baprs]-[A-Za-z0-9-]+", "slack_token"),
]


class RuleHardcodedSecretEnv(BaseRule):
    """SEC-001 - Detect hardcoded secrets in ENV instructions."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="SEC-001",
            title="Hardcoded secret detected in ENV instruction",
            description="Secrets set via ENV are baked into the image layers and can be extracted by anyone with 'docker history'. Use Docker secrets, runtime environment variables, or a vault.",
            severity=Severity.CRITICAL,
            category="secrets",
            fix_suggestion="Remove the secret from ENV. Use runtime '--env' flags, Docker Secrets, or a secrets manager.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction not in ("ENV", "ARG"):
                continue
            for pattern, secret_type in SECRET_PATTERNS:
                if re.search(pattern, instr.arguments):
                    findings.append(self._make_finding(
                        defn,
                        line_number=instr.line_number,
                        line_content=instr.original_line,
                        description_override=f"Potential hardcoded {secret_type} found in {instr.instruction} instruction. Secrets in image layers are publicly extractable.",
                    ))
                    break  # One finding per line
        return findings


class RuleSecretInRunCommand(BaseRule):
    """SEC-002 - Detect inline secrets in RUN commands (e.g. curl with tokens)."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="SEC-002",
            title="Potential secret in RUN command",
            description="Inline secrets in RUN commands (e.g. curl headers with Bearer tokens) are persisted in image history.",
            severity=Severity.HIGH,
            category="secrets",
            fix_suggestion="Use Docker BuildKit secret mounts: RUN --mount=type=secret,id=mytoken ...",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "RUN":
                continue
            for pattern, secret_type in SECRET_PATTERNS:
                if re.search(pattern, instr.arguments):
                    findings.append(self._make_finding(
                        defn,
                        line_number=instr.line_number,
                        line_content=instr.original_line,
                        description_override=f"Potential {secret_type} embedded in RUN command. Use BuildKit --mount=type=secret instead.",
                    ))
                    break
        return findings


class RuleCopyPrivateKey(BaseRule):
    """SEC-003 - Detect COPY of private key files."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="SEC-003",
            title="Private key or certificate file copied into image",
            description="Copying private keys (.pem, .key, .p12, id_rsa) into the image makes them available to anyone who pulls it.",
            severity=Severity.CRITICAL,
            category="secrets",
            fix_suggestion="Use Docker BuildKit secret mounts or runtime volume mounts instead of COPY for sensitive files.",
        )

    PRIVATE_FILE_PATTERNS = [
        r"id_rsa", r"id_ed25519", r"id_dsa", r"\.pem\b", r"\.key\b",
        r"\.p12\b", r"\.pfx\b", r"\.jks\b", r"\.keystore\b",
        r"\.env\b", r"\.htpasswd\b", r"\.npmrc\b", r"\.pypirc\b",
    ]

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction not in ("COPY", "ADD"):
                continue
            for pattern in self.PRIVATE_FILE_PATTERNS:
                if re.search(pattern, instr.arguments, re.IGNORECASE):
                    findings.append(self._make_finding(
                        defn,
                        line_number=instr.line_number,
                        line_content=instr.original_line,
                        description_override=f"Sensitive file matching '{pattern}' is being copied into the image.",
                    ))
                    break
        return findings


SECRET_RULES = [
    RuleHardcodedSecretEnv(),
    RuleSecretInRunCommand(),
    RuleCopyPrivateKey(),
]
