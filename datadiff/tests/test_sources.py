"""Tests for data source adapters."""

from pathlib import Path
import tempfile
import polars as pl
from datadiff.sources.csv import CSVSourceAdapter
from datadiff.sources.json import JSONSourceAdapter
from datadiff.sources.parquet import ParquetSourceAdapter


def test_csv_adapter():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_file = Path(tmp_dir) / "test.csv"
        csv_file.write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8")

        adapter = CSVSourceAdapter(csv_file)
        df = adapter.load()
        assert len(df) == 2
        assert "name" in df.columns
        schema = adapter.get_schema()
        assert "id" in schema


def test_json_adapter():
    with tempfile.TemporaryDirectory() as tmp_dir:
        json_file = Path(tmp_dir) / "test.json"
        json_file.write_text('[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]', encoding="utf-8")

        adapter = JSONSourceAdapter(json_file)
        df = adapter.load()
        assert len(df) == 2
        assert "id" in df.columns


def test_parquet_adapter():
    with tempfile.TemporaryDirectory() as tmp_dir:
        pq_file = Path(tmp_dir) / "test.parquet"
        orig_df = pl.DataFrame({"id": [1, 2], "val": [10.5, 20.5]})
        orig_df.write_parquet(pq_file)

        adapter = ParquetSourceAdapter(pq_file)
        df = adapter.load()
        assert len(df) == 2
        assert "val" in df.columns
