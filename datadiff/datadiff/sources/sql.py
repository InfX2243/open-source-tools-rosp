"""SQL database source adapter."""

from __future__ import annotations

from typing import Dict, Optional
import polars as pl
from datadiff.sources.base import BaseSourceAdapter


class SQLSourceAdapter(BaseSourceAdapter):
    """Loads database tables or query results via SQLAlchemy connection string."""

    def __init__(self, connection_string: str, table: Optional[str] = None, query: Optional[str] = None):
        self.connection_string = connection_string
        self.table = table
        self.query = query

    def load(self) -> pl.DataFrame:
        sql_query = self.query or f"SELECT * FROM {self.table}"
        return pl.read_database_uri(query=sql_query, uri=self.connection_string)

    def get_schema(self) -> Dict[str, str]:
        df = self.load()
        return {col: str(dtype) for col, dtype in df.schema.items()}
