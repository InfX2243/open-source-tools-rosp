"""Security rules registry for ContainerSec."""

from typing import List, Type

from containersec.rules.base import BaseRule
from containersec.rules.cis_rules import (
    RuleNoRootUser,
    RuleMutableTag,
    RuleNoHealthcheck,
    RuleUseAddInsteadOfCopy,
    RuleExposeSSH,
    RuleRunAptGetNoCache,
    RulePipNoCache,
    RuleNoWorkdir,
    RuleMaintainerDeprecated,
)
from containersec.rules.secrets_rules import (
    RuleHardcodedSecretEnv,
    RuleSecretInRunCommand,
    RuleCopyPrivateKey,
)
from containersec.rules.best_practices import (
    RuleUseSlimImage,
    RuleDangerousPackages,
    RuleMultipleFromWithoutMultiStage,
    RuleTooManyLayers,
    RuleCurlPipeBash,
    RuleExposeTooManyPorts,
)

ALL_RULES: List[Type[BaseRule]] = [
    # CIS Benchmarks
    RuleNoRootUser,
    RuleMutableTag,
    RuleNoHealthcheck,
    RuleUseAddInsteadOfCopy,
    RuleExposeSSH,
    RuleRunAptGetNoCache,
    RulePipNoCache,
    RuleNoWorkdir,
    RuleMaintainerDeprecated,
    # Leaked Secrets & Credentials
    RuleHardcodedSecretEnv,
    RuleSecretInRunCommand,
    RuleCopyPrivateKey,
    # Best Practices
    RuleUseSlimImage,
    RuleDangerousPackages,
    RuleMultipleFromWithoutMultiStage,
    RuleTooManyLayers,
    RuleCurlPipeBash,
    RuleExposeTooManyPorts,
]

__all__ = [
    "BaseRule",
    "ALL_RULES",
    "RuleNoRootUser",
    "RuleMutableTag",
    "RuleNoHealthcheck",
    "RuleUseAddInsteadOfCopy",
    "RuleExposeSSH",
    "RuleRunAptGetNoCache",
    "RulePipNoCache",
    "RuleNoWorkdir",
    "RuleMaintainerDeprecated",
    "RuleHardcodedSecretEnv",
    "RuleSecretInRunCommand",
    "RuleCopyPrivateKey",
    "RuleUseSlimImage",
    "RuleDangerousPackages",
    "RuleMultipleFromWithoutMultiStage",
    "RuleTooManyLayers",
    "RuleCurlPipeBash",
    "RuleExposeTooManyPorts",
]
