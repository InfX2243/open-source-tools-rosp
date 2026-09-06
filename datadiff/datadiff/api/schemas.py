"""API Request and Response schemas for DataDiff REST API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    """Payload for comparing datasets with optional JSON records or file paths."""

    source_path: Optional[str] = None
    target_path: Optional[str] = None
    source_records: Optional[List[Dict[str, Any]]] = None
    target_records: Optional[List[Dict[str, Any]]] = None
    key: Optional[List[str]] = Field(default=None, description="Key column(s) to match records")
    ignore_columns: Optional[List[str]] = Field(default_factory=list)
    numeric_tolerance: Optional[float] = 0.0
    case_sensitive: bool = True
    trim_whitespace: bool = True


class HistoryItemResponse(BaseModel):
    """History item metadata."""

    id: int
    source_name: str
    target_name: str
    timestamp: str
    execution_time_ms: float
    passed: bool
    source_rows: int
    target_rows: int
    added_rows: int
    removed_rows: int
    modified_rows: int
    unchanged_rows: int
    schema_changes_count: int
