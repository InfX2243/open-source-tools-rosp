"""Unit tests for CIS and security rules."""

from containersec.core.parser import DockerfileParser
from containersec.rules.cis_rules import (
    RuleNoRootUser,
    RuleMutableTag,
    RuleUseAddInsteadOfCopy,
    RuleExposeSSH,
)
from containersec.rules.secrets_rules import RuleHardcodedSecretEnv


def test_rule_no_root_user_triggers_when_no_user():
    content = "FROM python:3.11\nCMD ['python']"
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    rule = RuleNoRootUser()
    findings = rule.check(instructions)
    assert len(findings) == 1
    assert findings[0].rule_id == "CIS-4.1"


def test_rule_no_root_user_passes_when_user_present():
    content = "FROM python:3.11\nUSER appuser\nCMD ['python']"
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    rule = RuleNoRootUser()
    findings = rule.check(instructions)
    assert len(findings) == 0


def test_rule_mutable_tag():
    content = "FROM node:latest"
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    rule = RuleMutableTag()
    findings = rule.check(instructions)
    assert len(findings) == 1
    assert findings[0].rule_id == "CIS-4.6"


def test_rule_add_instead_of_copy():
    content = "FROM alpine\nADD file.txt /app/"
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    rule = RuleUseAddInsteadOfCopy()
    findings = rule.check(instructions)
    assert len(findings) == 1
    assert findings[0].rule_id == "CIS-4.9"


def test_rule_expose_ssh():
    content = "FROM ubuntu\nEXPOSE 22"
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    rule = RuleExposeSSH()
    findings = rule.check(instructions)
    assert len(findings) == 1
    assert findings[0].rule_id == "CIS-4.5"


def test_rule_secrets_env():
    content = 'FROM alpine\nENV AWS_SECRET_ACCESS_KEY="AKIA1234567890EXAMPLE"'
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    rule = RuleHardcodedSecretEnv()
    findings = rule.check(instructions)
    assert len(findings) == 1
    assert findings[0].rule_id == "SEC-001"
