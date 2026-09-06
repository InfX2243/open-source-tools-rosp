"""Validator modules registration."""

from dataguard.validators.base import Validator, ValidatorRegistry
from dataguard.validators.required import RequiredValidator
from dataguard.validators.type import TypeValidator
from dataguard.validators.unique import UniqueValidator
from dataguard.validators.range import RangeValidator
from dataguard.validators.regex import RegexValidator
from dataguard.validators.allowed import AllowedValuesValidator
from dataguard.validators.custom import CustomValidator

__all__ = [
    "Validator",
    "ValidatorRegistry",
    "RequiredValidator",
    "TypeValidator",
    "UniqueValidator",
    "RangeValidator",
    "RegexValidator",
    "AllowedValuesValidator",
    "CustomValidator",
]
