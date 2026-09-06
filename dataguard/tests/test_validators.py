"""Unit tests for all DataGuard validators."""

import pytest
import polars as pl
from dataguard.core.models import ColumnRule, RuleStatus, Severity
from dataguard.validators.required import RequiredValidator
from dataguard.validators.type import TypeValidator
from dataguard.validators.unique import UniqueValidator
from dataguard.validators.range import RangeValidator
from dataguard.validators.regex import RegexValidator
from dataguard.validators.allowed import AllowedValuesValidator
from dataguard.validators.custom import CustomValidator


class TestRequiredValidator:
    def test_required_passes_clean_data(self, sample_valid_df):
        v = RequiredValidator()
        rule = ColumnRule(required=True)
        res = v.validate(sample_valid_df, "email", rule)
        assert res.status == RuleStatus.PASS
        assert res.failed_count == 0

    def test_required_fails_with_nulls_and_empty_strings(self, sample_dirty_df):
        v = RequiredValidator()
        rule = ColumnRule(required=True)
        res = v.validate(sample_dirty_df, "name", rule)
        assert res.status == RuleStatus.FAIL
        assert res.failed_count == 1
        assert len(res.samples) == 1

    def test_max_null_rate_threshold(self, sample_dirty_df):
        v = RequiredValidator()
        # 1 out of 5 rows is null (20%) -> 30% max threshold should pass
        rule = ColumnRule(max_null_rate=0.30)
        res = v.validate(sample_dirty_df, "name", rule)
        assert res.status == RuleStatus.PASS

        # 10% max threshold should fail
        rule_strict = ColumnRule(max_null_rate=0.10)
        res_strict = v.validate(sample_dirty_df, "name", rule_strict)
        assert res_strict.status == RuleStatus.FAIL


class TestUniqueValidator:
    def test_unique_passes_distinct(self, sample_valid_df):
        v = UniqueValidator()
        rule = ColumnRule(unique=True)
        res = v.validate(sample_valid_df, "customer_id", rule)
        assert res.status == RuleStatus.PASS
        assert res.failed_count == 0

    def test_unique_fails_on_duplicates(self, sample_dirty_df):
        v = UniqueValidator()
        rule = ColumnRule(unique=True)
        res = v.validate(sample_dirty_df, "customer_id", rule)
        assert res.status == RuleStatus.FAIL
        assert res.failed_count > 0


class TestTypeValidator:
    def test_type_integer(self, sample_valid_df):
        v = TypeValidator()
        rule = ColumnRule(type="integer")
        res = v.validate(sample_valid_df, "customer_id", rule)
        assert res.status == RuleStatus.PASS

    def test_type_float(self, sample_valid_df):
        v = TypeValidator()
        rule = ColumnRule(type="float")
        res = v.validate(sample_valid_df, "score", rule)
        assert res.status == RuleStatus.PASS


class TestRangeValidator:
    def test_range_bounds_pass(self, sample_valid_df):
        v = RangeValidator()
        rule = ColumnRule(min=18, max=100)
        res = v.validate(sample_valid_df, "age", rule)
        assert res.status == RuleStatus.PASS

    def test_range_bounds_fail(self, sample_dirty_df):
        v = RangeValidator()
        rule = ColumnRule(min=18, max=100)
        res = v.validate(sample_dirty_df, "age", rule)
        assert res.status == RuleStatus.FAIL
        assert res.failed_count == 2  # -5 and 150


class TestRegexValidator:
    def test_email_format_pass(self, sample_valid_df):
        v = RegexValidator()
        rule = ColumnRule(format="email")
        res = v.validate(sample_valid_df, "email", rule)
        assert res.status == RuleStatus.PASS

    def test_email_format_fail(self, sample_dirty_df):
        v = RegexValidator()
        rule = ColumnRule(format="email")
        res = v.validate(sample_dirty_df, "email", rule)
        assert res.status == RuleStatus.FAIL
        assert res.failed_count >= 1

    def test_custom_regex(self, sample_valid_df):
        v = RegexValidator()
        rule = ColumnRule(regex="^[A-Z][a-z]+$")
        res = v.validate(sample_valid_df, "name", rule)
        assert res.status == RuleStatus.PASS


class TestAllowedValuesValidator:
    def test_allowed_whitelist(self, sample_valid_df):
        v = AllowedValuesValidator()
        rule = ColumnRule(allowed=["active", "inactive", "pending", "suspended"])
        res = v.validate(sample_valid_df, "status", rule)
        assert res.status == RuleStatus.PASS

    def test_allowed_whitelist_fails_on_unknown(self, sample_dirty_df):
        v = AllowedValuesValidator()
        rule = ColumnRule(allowed=["active", "inactive", "pending"])
        res = v.validate(sample_dirty_df, "status", rule)
        assert res.status == RuleStatus.FAIL


class TestCustomValidator:
    def test_custom_expression_pass(self, sample_valid_df):
        v = CustomValidator()
        rule = ColumnRule(custom_expr="val > 0")
        res = v.validate(sample_valid_df, "customer_id", rule)
        assert res.status == RuleStatus.PASS

    def test_custom_expression_fail(self, sample_dirty_df):
        v = CustomValidator()
        rule = ColumnRule(custom_expr="val > 0")
        res = v.validate(sample_dirty_df, "age", rule)
        assert res.status == RuleStatus.FAIL
