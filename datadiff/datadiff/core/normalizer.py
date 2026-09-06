"""Value normalization and tolerance comparator."""

from __future__ import annotations

import math
from typing import Any
from datadiff.core.models import NormalizationRules


class ValueNormalizer:
    """Normalizes and compares values according to configurable rules."""

    def __init__(self, rules: NormalizationRules):
        self.rules = rules

    def are_equal(self, a: Any, b: Any) -> bool:
        """Check if two cell values are semantically equal under given rules."""
        # Null / NaN check
        a_is_null = a is None or (isinstance(a, float) and math.isnan(a))
        b_is_null = b is None or (isinstance(b, float) and math.isnan(b))

        if a_is_null and b_is_null:
            return True
        if a_is_null or b_is_null:
            return False

        # Numeric tolerance comparison
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if self.rules.numeric_tolerance > 0:
                return abs(float(a) - float(b)) <= self.rules.numeric_tolerance
            return a == b

        # String comparison with case and trim options
        if isinstance(a, str) or isinstance(b, str):
            str_a = str(a)
            str_b = str(b)
            if self.rules.trim_whitespace:
                str_a = str_a.strip()
                str_b = str_b.strip()
            if not self.rules.case_sensitive:
                str_a = str_a.lower()
                str_b = str_b.lower()
            return str_a == str_b

        return a == b
