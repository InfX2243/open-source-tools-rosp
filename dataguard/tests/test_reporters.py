"""Unit tests for report renderers."""

import pytest
import polars as pl
from dataguard.core.engine import ValidationEngine
from dataguard.core.models import RuleConfig, ColumnRule
from dataguard.reporters.console import ConsoleReporter
from dataguard.reporters.json import JSONReporter
from dataguard.reporters.html import HTMLReporter
from dataguard.reporters.markdown import MarkdownReporter


@pytest.fixture
def sample_summary(sample_valid_df):
    config = RuleConfig(
        dataset="test_customers.csv",
        columns={
            "customer_id": ColumnRule(required=True, unique=True),
            "email": ColumnRule(format="email"),
        },
    )
    engine = ValidationEngine(config)
    return engine.validate_dataframe(sample_valid_df, config=config)


def test_console_reporter(sample_summary):
    rep = ConsoleReporter()
    text = rep.render(sample_summary)
    assert "DATAGUARD QUALITY REPORT" in text
    assert "QUALITY SCORE:" in text


def test_json_reporter(sample_summary):
    rep = JSONReporter()
    json_str = rep.render(sample_summary)
    assert '"dataset_name": "test_customers.csv"' in json_str
    assert '"quality_score":' in json_str


def test_html_reporter(sample_summary):
    rep = HTMLReporter()
    html_str = rep.render(sample_summary)
    assert "<!DOCTYPE html>" in html_str
    assert "DataGuard Report" in html_str
    assert "Quality Score" in html_str


def test_markdown_reporter(sample_summary):
    rep = MarkdownReporter()
    md_str = rep.render(sample_summary)
    assert "# 🛡️ DataGuard Quality Report" in md_str
    assert "| Status | Rule / Check |" in md_str
