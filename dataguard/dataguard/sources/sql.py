"""Relational database SQL source adapter (SQLite, PostgreSQL, MySQL via SQLAlchemy)."""

from typing import Any
from dataguard.sources.base import SourceAdapter

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class SQLAdapter(SourceAdapter):
    """Loads records from SQL databases using SQLAlchemy."""

    def supports(self, source: str) -> bool:
        src_lower = source.lower()
        return (
            src_lower.startswith("sqlite:")
            or src_lower.startswith("postgresql:")
            or src_lower.startswith("postgres:")
            or src_lower.startswith("mysql:")
            or src_lower.endswith(".db")
            or src_lower.endswith(".sqlite")
            or src_lower.endswith(".sqlite3")
        )

    def load(self, source: str, **kwargs: Any) -> Any:
        try:
            from sqlalchemy import create_engine, text
        except ImportError:
            raise ImportError("SQLAlchemy is required for database sources. Install with `pip install sqlalchemy`.")

        # Normalize SQLite file paths
        conn_uri = source
        if source.endswith((".db", ".sqlite", ".sqlite3")) and not source.startswith("sqlite:"):
            conn_uri = f"sqlite:///{source}"

        engine = create_engine(conn_uri)
        table_name = kwargs.get("table")
        query = kwargs.get("query")
        limit = kwargs.get("limit")

        if query:
            sql_stmt = query
        elif table_name:
            sql_stmt = f"SELECT * FROM {table_name}"
            if limit:
                sql_stmt += f" LIMIT {int(limit)}"
        else:
            raise ValueError("Must specify either 'table' or 'query' when loading from SQL source.")

        if POLARS_AVAILABLE:
            try:
                # Read directly via Polars SQL connector
                return pl.read_database_uri(query=sql_stmt, uri=conn_uri)
            except Exception:
                pass

        # Fallback using SQLAlchemy connection
        with engine.connect() as conn:
            result = conn.execute(text(sql_stmt))
            keys = list(result.keys())
            rows = [dict(zip(keys, row)) for row in result.fetchall()]

        if POLARS_AVAILABLE:
            return pl.from_dicts(rows) if rows else pl.DataFrame()
        return rows
