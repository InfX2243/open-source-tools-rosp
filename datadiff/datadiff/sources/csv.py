"""CSV source adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union
import polars as pl
from datadiff.sources.base import BaseSourceAdapter


class CSVSourceAdapter(BaseSourceAdapter):
    """Loads CSV / TSV datasets using Polars fast scanner."""

    def __init__(self, file_path: Union[str, Path], separator: str = ","):
        self.file_path = Path(file_path)
        self.separator = separator

    def load(self) -> pl.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        return pl.read_csv(self.file_path, separator=self.separator, infer_schema_length=10000)

    def get_schema(self) -> Dict[str, str]:
        df = self.load()
        return {col: str(dtype) for col, dtype in df.schema.items()}
