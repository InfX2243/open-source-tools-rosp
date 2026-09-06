"""Pydantic request and response schemas for DataGuard API."""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from dataguard.core.models import ValidationSummary, RuleConfig, DatasetProfile


class RunValidationRequest(BaseModel):
    source: str = Field(..., description="File path, URL, or database table identifier")
    rules_yaml: Optional[str] = Field(None, description="Raw YAML string of validation rules")
    rules_json: Optional[RuleConfig] = Field(None, description="Structured rule configuration")
    project_name: Optional[str] = Field(None, description="Optional project name to associate with this run")


class DirectDataValidationRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of record dictionaries")
    dataset_name: str = Field(default="in_memory_records")
    rules_yaml: Optional[str] = None
    rules_json: Optional[RuleConfig] = None
    project_name: Optional[str] = None


class ValidationRunItem(BaseModel):
    id: int
    dataset_name: str
    quality_score: float
    passed_gate: bool
    total_rules: int
    passed_rules: int
    failed_rules: int
    row_count: int
    duration_ms: float
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    run_count: int = 0
