"""Base validator interface and registry."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
import time
from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus, Severity, FailedSample

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class Validator(ABC):
    """Abstract base class for all DataGuard validators."""

    name: str = "base"

    @abstractmethod
    def validate(
        self,
        df: Any,
        column: str,
        rule: ColumnRule,
    ) -> ValidationResult:
        """
        Execute the validation check against a dataframe for the specified column.
        
        Args:
            df: Polars DataFrame or generic records.
            column: Name of the column being evaluated.
            rule: Configured ColumnRule.
            
        Returns:
            ValidationResult with detailed metrics and sample failures.
        """
        pass

    def create_result(
        self,
        rule_name: str,
        column: str,
        status: RuleStatus,
        severity: Severity,
        checked_count: int,
        failed_count: int,
        weight: float,
        message: str,
        samples: List[FailedSample],
        start_time: float,
    ) -> ValidationResult:
        """Helper to construct a standardized ValidationResult."""
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        failure_rate = (failed_count / checked_count) if checked_count > 0 else 0.0
        return ValidationResult(
            rule_name=rule_name,
            column=column,
            status=status,
            severity=severity,
            checked_count=checked_count,
            failed_count=failed_count,
            failure_rate=round(failure_rate, 4),
            weight=weight,
            message=message,
            samples=samples[:10],  # Keep top 10 samples
            duration_ms=duration_ms,
        )


class ValidatorRegistry:
    """Registry mapping rule keys to validator implementations."""

    _validators: Dict[str, Type[Validator]] = {}

    @classmethod
    def register(cls, name: str, validator_cls: Type[Validator]) -> None:
        cls._validators[name] = validator_cls

    @classmethod
    def get(cls, name: str) -> Type[Validator]:
        if name not in cls._validators:
            raise KeyError(f"No validator registered for '{name}'")
        return cls._validators[name]

    @classmethod
    def all_registered(cls) -> Dict[str, Type[Validator]]:
        return dict(cls._validators)
