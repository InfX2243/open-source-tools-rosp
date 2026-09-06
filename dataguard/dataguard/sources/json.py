"""JSON and NDJSON (JSON Lines) source adapter."""

import os
import json
from typing import Any
from dataguard.sources.base import SourceAdapter

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class JSONAdapter(SourceAdapter):
    """Loads JSON arrays or newline-delimited JSON (NDJSON/JSONL) files."""

    def supports(self, source: str) -> bool:
        src_lower = source.lower()
        return src_lower.endswith(".json") or src_lower.endswith(".jsonl") or src_lower.endswith(".ndjson")

    def load(self, source: str, **kwargs: Any) -> Any:
        if not os.path.exists(source):
            raise FileNotFoundError(f"JSON file not found: {source}")

        is_ndjson = source.lower().endswith(".jsonl") or source.lower().endswith(".ndjson")

        if POLARS_AVAILABLE:
            if is_ndjson:
                return pl.read_ndjson(source)
            try:
                return pl.read_json(source)
            except Exception:
                # If read_json fails because of format, fallback to python json and pl.from_dicts
                with open(source, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return pl.from_dicts(data)
                elif isinstance(data, dict):
                    # Find first array key or single record
                    for v in data.values():
                        if isinstance(v, list):
                            return pl.from_dicts(v)
                    return pl.from_dicts([data])

        with open(source, "r", encoding="utf-8") as f:
            if is_ndjson:
                return [json.loads(line) for line in f if line.strip()]
            data = json.load(f)
            if isinstance(data, list):
                return data
            return [data]
