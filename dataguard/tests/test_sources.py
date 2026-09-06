"""Unit tests for data source adapters."""

import pytest
import os
import polars as pl
from dataguard.sources.csv import CSVAdapter
from dataguard.sources.json import JSONAdapter
from dataguard.sources.parquet import ParquetAdapter
from dataguard.sources.sql import SQLAdapter
from dataguard.sources import get_adapter_for_source, load_dataset


def test_csv_adapter(temp_csv_file):
    adapter = CSVAdapter()
    assert adapter.supports("test.csv")
    assert adapter.supports("path/to/data.tsv")
    df = adapter.load(temp_csv_file)
    assert len(df) == 10
    assert "customer_id" in df.columns


def test_json_adapter(temp_json_file):
    adapter = JSONAdapter()
    assert adapter.supports("records.json")
    assert adapter.supports("stream.jsonl")
    df = adapter.load(temp_json_file)
    assert len(df) == 2


def test_parquet_adapter(sample_valid_df, tmp_path):
    pq_path = str(tmp_path / "test.parquet")
    sample_valid_df.write_parquet(pq_path)

    adapter = ParquetAdapter()
    assert adapter.supports("dataset.parquet")
    df = adapter.load(pq_path)
    assert len(df) == 10


def test_sql_adapter(sample_valid_df, tmp_path):
    db_path = str(tmp_path / "test.db")
    import sqlite3
    conn = sqlite3.connect(db_path)
    # Write sample table
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
    cursor.execute("INSERT INTO users VALUES (2, 'Bob')")
    conn.commit()
    conn.close()

    adapter = SQLAdapter()
    assert adapter.supports(db_path)
    assert adapter.supports("sqlite:///test.db")
    df = adapter.load(db_path, table="users")
    assert len(df) == 2


def test_load_dataset_helper(temp_csv_file):
    df = load_dataset(temp_csv_file)
    assert len(df) == 10
