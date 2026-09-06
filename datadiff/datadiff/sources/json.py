"""JSON / NDJSON source adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union
import polars as pl
from datadiff.sources.base import BaseSourceAdapter


class JSONSourceAdapter(BaseSourceAdapter):
    """Loads standard JSON arrays and line-delimited JSON datasets."""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)

    def load(self) -> pl.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")

        ext = self.file_path.suffix.lower()
        if ext in (".jsonl", ".ndjson"):
            return pl.read_ndjson(self.file_path)
        return pl.read_json(self.file_path)

    def get_schema(self) -> Dict[str, str]:
        df = self.load()
        return {col: str(dtype) for col, dtype in df.schema.items()}
