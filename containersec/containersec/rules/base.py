"""Abstract base class for all ContainerSec security rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from containersec.core.models import DockerInstruction, Finding, RuleDefinition


class BaseRule(ABC):
    """Every security rule must inherit from this base class."""

    @abstractmethod
    def definition(self) -> RuleDefinition:
        """Return the static metadata for this rule."""
        pass

    @abstractmethod
    def check(self, instructions: List[DockerInstruction]) -> List[Finding]:
        """Run the rule against parsed Dockerfile instructions and return findings."""
        pass

    def _make_finding(
        self,
        defn: RuleDefinition,
        line_number: Optional[int] = None,
        line_content: Optional[str] = None,
        fixed_line: Optional[str] = None,
        description: Optional[str] = None,
        description_override: Optional[str] = None,
        **kwargs,
    ) -> Finding:
        """Helper to construct a Finding from a RuleDefinition."""
        desc = description or description_override or defn.description
        return Finding(
            rule_id=defn.rule_id,
            title=defn.title,
            severity=defn.severity,
            category=defn.category,
            line_number=line_number,
            line_content=line_content,
            description=desc,
            fix_suggestion=defn.fix_suggestion,
            fixed_line=fixed_line,
        )
