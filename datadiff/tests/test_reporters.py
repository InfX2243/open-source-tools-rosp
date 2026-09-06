"""Tests for reporters (JSON, Markdown, HTML, Console)."""

from datadiff.core.engine import DataDiffEngine
from datadiff.core.models import DiffConfig
from datadiff.reporters.console import ConsoleReporter
from datadiff.reporters.html import HTMLReporter
from datadiff.reporters.json import JSONReporter
from datadiff.reporters.markdown import MarkdownReporter


def test_reporters(sample_df_a, sample_df_b):
    diff = DataDiffEngine.compare_sources(
        source=sample_df_a,
        target=sample_df_b,
        config=DiffConfig(key=["id"]),
    )

    # JSON Reporter
    json_out = JSONReporter().render(diff)
    assert '"source_row_count": 4' in json_out
    assert '"added_count": 1' in json_out

    # Markdown Reporter
    md_out = MarkdownReporter().render(diff)
    assert "# DataDiff Comparison Report" in md_out
    assert "| **Added Rows** |" in md_out

    # HTML Reporter
    html_out = HTMLReporter().render(diff)
    assert "<!DOCTYPE html>" in html_out
    assert "DataDiff Semantic Report" in html_out
    assert "Rahul Sharma" not in html_out or "MODIFIED" in html_out

    # Console Reporter
    console_rep = ConsoleReporter()
    console_rep.render(diff)  # Should render cleanly without exception
