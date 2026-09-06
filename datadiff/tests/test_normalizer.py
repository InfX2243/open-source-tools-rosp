"""Tests for ValueNormalizer."""

import math
from datadiff.core.models import NormalizationRules
from datadiff.core.normalizer import ValueNormalizer


def test_normalizer_equality_numbers():
    norm = ValueNormalizer(NormalizationRules(numeric_tolerance=0.01))
    assert norm.are_equal(10.0, 10.005)
    assert not norm.are_equal(10.0, 10.05)


def test_normalizer_equality_strings():
    norm_case_insensitive = ValueNormalizer(NormalizationRules(case_sensitive=False, trim_whitespace=True))
    assert norm_case_insensitive.are_equal("  HELLO  ", "hello")

    norm_case_sensitive = ValueNormalizer(NormalizationRules(case_sensitive=True, trim_whitespace=False))
    assert not norm_case_sensitive.are_equal("  HELLO  ", "hello")


def test_normalizer_null_handling():
    norm = ValueNormalizer(NormalizationRules(ignore_nan_vs_null=True))
    assert norm.are_equal(None, None)
    assert norm.are_equal(float("nan"), None)
    assert not norm.are_equal(None, "None")
