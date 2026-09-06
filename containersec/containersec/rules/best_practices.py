"""General best-practice security rules for Dockerfiles."""

from __future__ import annotations

import re
from typing import List

from containersec.core.models import DockerInstruction, Finding, RuleDefinition, Severity
from containersec.rules.base import BaseRule


class RuleUseSlimImage(BaseRule):
    """BP-001 - Prefer slim or distroless base images."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="BP-001",
            title="Full OS base image used instead of slim/alpine variant",
            description="Full images (e.g. python:3.11, ubuntu:22.04) ship with hundreds of unnecessary packages that increase attack surface and image size.",
            severity=Severity.MEDIUM,
            category="best-practice",
            fix_suggestion="Use '-slim', '-alpine', or distroless variants (e.g. 'python:3.11-slim').",
        )

    FULL_IMAGE_PATTERNS = [
        r"^(python|node|ruby|golang|java|openjdk|php|rust|dotnet):\d",
        r"^(ubuntu|debian|centos|fedora|amazonlinux):\d",
    ]

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "FROM":
                continue
            image_ref = instr.arguments.split()[0].lower()
            if any(re.match(p, image_ref) for p in self.FULL_IMAGE_PATTERNS):
                if "slim" not in image_ref and "alpine" not in image_ref and "distroless" not in image_ref:
                    findings.append(self._make_finding(
                        defn,
                        line_number=instr.line_number,
                        line_content=instr.original_line,
                    ))
        return findings


class RuleDangerousPackages(BaseRule):
    """BP-002 - Detect installation of unnecessary attack-surface packages."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="BP-002",
            title="Dangerous packages installed (ssh, netcat, telnet, nmap)",
            description="Installing network utilities like ssh, netcat, telnet, or nmap gives attackers ready-made tools for lateral movement and data exfiltration.",
            severity=Severity.HIGH,
            category="best-practice",
            fix_suggestion="Remove these packages or use a multi-stage build that excludes them from the final image.",
        )

    DANGEROUS_PACKAGES = [
        "openssh-server", "openssh-client", "ssh", "sshd",
        "netcat", "ncat", "nc", "nmap", "telnet",
        "tcpdump", "wireshark", "strace", "gdb",
    ]

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "RUN":
                continue
            lower_args = instr.arguments.lower()
            for pkg in self.DANGEROUS_PACKAGES:
                if re.search(rf"\b{re.escape(pkg)}\b", lower_args):
                    findings.append(self._make_finding(
                        defn,
                        line_number=instr.line_number,
                        line_content=instr.original_line,
                        description_override=f"Dangerous package '{pkg}' is being installed. This increases attack surface.",
                    ))
                    break
        return findings


class RuleMultipleFromWithoutMultiStage(BaseRule):
    """BP-003 - Detect multiple FROM without AS (not multi-stage)."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="BP-003",
            title="Multiple FROM instructions without multi-stage build naming",
            description="Multiple FROM instructions without 'AS builder' naming may indicate accidental overwrites instead of intentional multi-stage builds.",
            severity=Severity.INFO,
            category="best-practice",
            fix_suggestion="Use named build stages: 'FROM python:3.11-slim AS builder'.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        from_instructions = [i for i in instructions if i.instruction == "FROM"]
        if len(from_instructions) > 1:
            unnamed = [i for i in from_instructions if " as " not in i.arguments.lower() and " AS " not in i.arguments]
            if len(unnamed) > 1:
                defn = self.definition()
                return [self._make_finding(
                    defn,
                    line_number=unnamed[1].line_number,
                    line_content=unnamed[1].original_line,
                )]
        return []


class RuleTooManyLayers(BaseRule):
    """BP-004 - Warn if too many individual RUN commands create excessive layers."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="BP-004",
            title="Excessive number of RUN instructions (layer bloat)",
            description="Each RUN instruction creates a new image layer. Combining related commands reduces image size and build time.",
            severity=Severity.LOW,
            category="best-practice",
            fix_suggestion="Consolidate related RUN commands using '&&' chaining.",
        )

    MAX_RUN_COUNT = 10

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        run_count = sum(1 for i in instructions if i.instruction == "RUN")
        if run_count > self.MAX_RUN_COUNT:
            defn = self.definition()
            return [self._make_finding(
                defn,
                description_override=f"Found {run_count} RUN instructions (threshold: {self.MAX_RUN_COUNT}). Consolidate to reduce image layers.",
            )]
        return []


class RuleCurlPipeBash(BaseRule):
    """BP-005 - Detect curl-pipe-bash anti-pattern."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="BP-005",
            title="curl | bash anti-pattern detected",
            description="Piping curl output directly to bash is dangerous. A compromised or changed URL can execute arbitrary code during build.",
            severity=Severity.HIGH,
            category="best-practice",
            fix_suggestion="Download the script first, verify its checksum, then execute it.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        findings = []
        defn = self.definition()
        for instr in instructions:
            if instr.instruction != "RUN":
                continue
            if re.search(r"curl\s.*\|\s*(ba)?sh", instr.arguments):
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                ))
            elif re.search(r"wget\s.*\|\s*(ba)?sh", instr.arguments):
                findings.append(self._make_finding(
                    defn,
                    line_number=instr.line_number,
                    line_content=instr.original_line,
                ))
        return findings


class RuleExposeTooManyPorts(BaseRule):
    """BP-006 - Warn if more than 3 ports are exposed."""

    def definition(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id="BP-006",
            title="Excessive ports exposed",
            description="Exposing many ports increases the network attack surface. Only expose the ports your application actively needs.",
            severity=Severity.MEDIUM,
            category="best-practice",
            fix_suggestion="Reduce EXPOSE directives to only the necessary application ports.",
        )

    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        all_ports = []
        for instr in instructions:
            if instr.instruction == "EXPOSE":
                ports = re.findall(r"\d+", instr.arguments)
                all_ports.extend(ports)
        if len(all_ports) > 3:
            defn = self.definition()
            return [self._make_finding(
                defn,
                description_override=f"Found {len(all_ports)} exposed ports ({', '.join(all_ports)}). Minimize to reduce attack surface.",
            )]
        return []


BEST_PRACTICE_RULES = [
    RuleUseSlimImage(),
    RuleDangerousPackages(),
    RuleMultipleFromWithoutMultiStage(),
    RuleTooManyLayers(),
    RuleCurlPipeBash(),
    RuleExposeTooManyPorts(),
]
