"""CIS Docker Benchmark security rules for ContainerSec."""

from __future__ import annotations

import re
from typing import List

from containersec.core.models import DockerInstruction, Finding, RuleDefinition, Severity
from containersec.rules.base import BaseRule


class RuleNoRootUser(BaseRule):
    """CIS 4.1 - Ensure a non-root user is configured for the container."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.1",
            title="Container runs as root (no USER directive)",
            description="No USER instruction found. The container will run as root by default, giving an attacker full control if compromised.",
            severity=Severity.CRITICAL,
            category="cis",
            cis_benchmark="4.1",
            fix_suggestion="Add 'USER 1001' or 'USER nonroot' before CMD/ENTRYPOINT.",
            references=["https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user"],
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        has_user = any(i.instruction == "USER" and i.arguments.strip() not in ("0", "root") for i in instructions)
        if not has_user:
            defn = self.definition()
            return [self._make_finding(defn, fixed_line="USER 1001")]
        return []


class RuleMutableTag(BaseRule):
    """CIS 4.6 - Ensure images use fixed version tags, not :latest."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.6",
            title="Mutable base image tag (:latest or no tag)",
            description="Using ':latest' or an untagged base image is dangerous because the image content can change unpredictably between builds.",
            severity=Severity.HIGH,
            category="cis",
            cis_benchmark="4.6",
            fix_suggestion="Pin to a specific version tag or SHA256 digest (e.g. 'FROM python:3.11-slim@sha256:...').",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "FROM":
                continue
            image_ref = instr.arguments.split()[0] if instr.arguments else ""
            # Skip scratch and build stage references
            if image_ref.lower() in ("scratch",):
                continue
            # Check for :latest or no tag
            if ":latest" in image_ref or (":" not in image_ref and "@" not in image_ref):
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                    description=f"Base image '{image_ref}' uses a mutable tag. The image pulled today may differ from tomorrow.",
                ))
        return findings


class RuleNoHealthcheck(BaseRule):
    """CIS 4.7 - Ensure HEALTHCHECK instruction is defined."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.7",
            title="No HEALTHCHECK instruction defined",
            description="Without a HEALTHCHECK, Docker cannot detect if the application inside the container has crashed or become unresponsive.",
            severity=Severity.LOW,
            category="cis",
            cis_benchmark="4.7",
            fix_suggestion="Add 'HEALTHCHECK CMD curl -f http://localhost/ || exit 1' or an equivalent health probe.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        has_healthcheck = any(i.instruction == "HEALTHCHECK" for i in instructions)
        if not has_healthcheck:
            defn = self.definition()
            return [self._make_finding(defn, fixed_line='HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost/ || exit 1')]
        return []


class RuleUseAddInsteadOfCopy(BaseRule):
    """CIS 4.9 - Ensure COPY is used instead of ADD."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.9",
            title="ADD instruction used instead of COPY",
            description="ADD can fetch remote URLs and auto-extract archives, introducing unexpected content. COPY is explicit and safer.",
            severity=Severity.MEDIUM,
            category="cis",
            cis_benchmark="4.9",
            fix_suggestion="Replace 'ADD' with 'COPY' unless you specifically need URL fetching or tar extraction.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction == "ADD":
                fixed = instr.original_line.replace("ADD", "COPY", 1)
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                    fixed_line=fixed,
                ))
        return findings


class RuleExposeSSH(BaseRule):
    """CIS 4.5 - Ensure SSH is not exposed in the container."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.5",
            title="SSH port (22) is exposed",
            description="Exposing port 22 in a container enables SSH access, which is an unnecessary attack vector. Containers should be managed through orchestration tools.",
            severity=Severity.HIGH,
            category="cis",
            cis_benchmark="4.5",
            fix_suggestion="Remove port 22 from EXPOSE. Use 'docker exec' or orchestrator tooling for container access.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction == "EXPOSE":
                ports = re.findall(r"\b22\b", instr.arguments)
                if ports:
                    findings.append(self._make_finding(
                        defn,
                        line_number=instr.line_number,
                        line_content=instr.original_line,
                    ))
        return findings


class RuleRunAptGetNoCache(BaseRule):
    """CIS 4.3 - Ensure apt-get install cleans up cache."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.3",
            title="apt-get install without cache cleanup",
            description="Running 'apt-get install' without removing the package cache creates bloated image layers with unnecessary cached files.",
            severity=Severity.MEDIUM,
            category="cis",
            cis_benchmark="4.3",
            fix_suggestion="Add '&& rm -rf /var/lib/apt/lists/*' after apt-get install commands.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "RUN":
                continue
            if "apt-get install" in instr.arguments and "rm -rf /var/lib/apt/lists" not in instr.arguments:
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                ))
        return findings


class RulePipNoCache(BaseRule):
    """Ensure pip install uses --no-cache-dir."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.3b",
            title="pip install without --no-cache-dir",
            description="Running 'pip install' without '--no-cache-dir' leaves cached wheel files in the image, increasing its size unnecessarily.",
            severity=Severity.LOW,
            category="cis",
            fix_suggestion="Add '--no-cache-dir' flag to pip install commands.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "RUN":
                continue
            if "pip install" in instr.arguments and "--no-cache-dir" not in instr.arguments:
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                ))
        return findings


class RuleNoWorkdir(BaseRule):
    """Ensure WORKDIR is set explicitly."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.8",
            title="No WORKDIR instruction defined",
            description="Without an explicit WORKDIR, files are copied to and commands run from the root '/' directory, which is poor practice and can cause confusion.",
            severity=Severity.LOW,
            category="cis",
            cis_benchmark="4.8",
            fix_suggestion="Add 'WORKDIR /app' (or an appropriate directory) early in the Dockerfile.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        has_workdir = any(i.instruction == "WORKDIR" for i in instructions)
        if not has_workdir:
            defn = self.definition()
            return [self._make_finding(defn, fixed_line="WORKDIR /app")]
        return []


class RuleMaintainerDeprecated(BaseRule):
    """MAINTAINER instruction is deprecated."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="CIS-4.10",
            title="Deprecated MAINTAINER instruction used",
            description="The MAINTAINER instruction is deprecated. Use LABEL maintainer='...' instead.",
            severity=Severity.INFO,
            category="cis",
            cis_benchmark="4.10",
            fix_suggestion="Replace 'MAINTAINER name' with 'LABEL maintainer=\"name\"'.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction == "MAINTAINER":
                fixed = f'LABEL maintainer="{instr.arguments.strip()}"'
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                    fixed_line=fixed,
                ))
        return findings


# Convenient list of all CIS rules
CIS_RULES = [
    RuleNoRootUser(),
    RuleMutableTag(),
    RuleNoHealthcheck(),
    RuleUseAddInsteadOfCopy(),
    RuleExposeSSH(),
    RuleRunAptGetNoCache(),
    RulePipNoCache(),
    RuleNoWorkdir(),
    RuleMaintainerDeprecated(),
]
