"""FastAPI REST Application for DataDiff."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import polars as pl
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import datadiff
from datadiff.api import database
from datadiff.api.schemas import CompareRequest
from datadiff.core.engine import DataDiffEngine
from datadiff.core.models import DiffConfig, DiffSummary, NormalizationRules
from datadiff.reporters.html import HTMLReporter

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(
    title="DataDiff REST API",
    description="Semantic Data Comparison & Change Detection Platform API",
    version=datadiff.__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "datadiff",
        "version": datadiff.__version__,
    }


@app.post("/api/v1/compare")
def compare_datasets_endpoint(payload: CompareRequest):
    """Compare datasets supplied as in-memory record lists or local file paths."""
    try:
        cfg = DiffConfig(
            key=payload.key,
            ignore_columns=payload.ignore_columns or [],
            rules=NormalizationRules(
                numeric_tolerance=payload.numeric_tolerance or 0.0,
                case_sensitive=payload.case_sensitive,
                trim_whitespace=payload.trim_whitespace,
            ),
        )

        df_a: pl.DataFrame
        df_b: pl.DataFrame
        source_name = "source"
        target_name = "target"

        if payload.source_records is not None and payload.target_records is not None:
            df_a = pl.DataFrame(payload.source_records)
            df_b = pl.DataFrame(payload.target_records)
            source_name = "payload_source.json"
            target_name = "payload_target.json"
        elif payload.source_path and payload.target_path:
            df_a = DataDiffEngine.load_adapter(payload.source_path).load()
            df_b = DataDiffEngine.load_adapter(payload.target_path).load()
            source_name = Path(payload.source_path).name
            target_name = Path(payload.target_path).name
        else:
            raise HTTPException(
                status_code=400,
                detail="Either (source_records, target_records) or (source_path, target_path) must be provided.",
            )

        diff = DataDiffEngine.compare_sources(
            source=df_a,
            target=df_b,
            config=cfg,
            source_name=source_name,
            target_name=target_name,
        )

        # Save to database
        database.save_run(
            source_name=diff.source_name,
            target_name=diff.target_name,
            passed=diff.policy_report.passed,
            source_rows=diff.row_diff.source_row_count,
            target_rows=diff.row_diff.target_row_count,
            added_rows=diff.row_diff.added_count,
            removed_rows=diff.row_diff.removed_count,
            modified_rows=diff.row_diff.modified_count,
            unchanged_rows=diff.row_diff.unchanged_count,
            schema_changes=len(diff.schema_diff.added_columns) + len(diff.schema_diff.removed_columns) + len(diff.schema_diff.type_migrations),
            execution_time_ms=diff.execution_time_ms,
            summary_data=diff.model_dump(),
        )

        return diff.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/compare/upload")
async def compare_upload(
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...),
    key: Optional[str] = Form(None),
    ignore_columns: Optional[str] = Form(None),
    numeric_tolerance: float = Form(0.0),
    case_sensitive: bool = Form(True),
    trim_whitespace: bool = Form(True),
):
    """Handle multipart file upload for two datasets and return comparison diff."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        src_path = Path(tmp_dir) / source_file.filename
        tgt_path = Path(tmp_dir) / target_file.filename

        src_path.write_bytes(await source_file.read())
        tgt_path.write_bytes(await target_file.read())

        keys_list = [k.strip() for k in key.split(",")] if key else None
        ignore_list = [i.strip() for i in ignore_columns.split(",")] if ignore_columns else []

        cfg = DiffConfig(
            key=keys_list,
            ignore_columns=ignore_list,
            rules=NormalizationRules(
                numeric_tolerance=numeric_tolerance,
                case_sensitive=case_sensitive,
                trim_whitespace=trim_whitespace,
            ),
        )

        diff = DataDiffEngine.compare_sources(
            source=src_path,
            target=tgt_path,
            config=cfg,
            source_name=source_file.filename,
            target_name=target_file.filename,
        )

        # Save to database
        database.save_run(
            source_name=diff.source_name,
            target_name=diff.target_name,
            passed=diff.policy_report.passed,
            source_rows=diff.row_diff.source_row_count,
            target_rows=diff.row_diff.target_row_count,
            added_rows=diff.row_diff.added_count,
            removed_rows=diff.row_diff.removed_count,
            modified_rows=diff.row_diff.modified_count,
            unchanged_rows=diff.row_diff.unchanged_count,
            schema_changes=len(diff.schema_diff.added_columns) + len(diff.schema_diff.removed_columns) + len(diff.schema_diff.type_migrations),
            execution_time_ms=diff.execution_time_ms,
            summary_data=diff.model_dump(),
        )

        return diff.model_dump()


@app.get("/api/v1/compare/sample/{sample_id}")
def compare_sample(sample_id: str):
    """Run predefined sample dataset comparisons."""
    samples = {
        "customers": {
            "source": [
                {"id": 101, "name": "Rahul Sharma", "email": "rahul@example.com", "age": 22, "balance": 1500.0, "status": "active"},
                {"id": 102, "name": "Aisha Khan", "email": "aisha@example.com", "age": 24, "balance": 3200.5, "status": "active"},
                {"id": 103, "name": "John Doe", "email": "john@example.com", "age": 21, "balance": 450.0, "status": "inactive"},
                {"id": 104, "name": "Elena Rostova", "email": "elena@example.com", "age": 29, "balance": 9800.0, "status": "active"},
            ],
            "target": [
                {"id": 101, "name": "Rahul Sharma", "email": "rahul.sharma@newcorp.com", "age": 23, "balance": 1500.005, "status": "active", "tier": "gold"},
                {"id": 102, "name": "Aisha Khan", "email": "aisha@example.com", "age": 24, "balance": 3200.5, "status": "active", "tier": "silver"},
                {"id": 104, "name": "Elena Rostova", "email": "elena@example.com", "age": 29, "balance": 10200.0, "status": "active", "tier": "platinum"},
                {"id": 105, "name": "Sara Chen", "email": "sara@example.com", "age": 25, "balance": 2400.0, "status": "active", "tier": "bronze"},
            ],
            "key": ["id"],
            "ignore": [],
            "source_name": "customers_v1.csv",
            "target_name": "customers_v2.csv",
        },
        "orders_etl": {
            "source": [
                {"order_id": "ORD-001", "customer_id": 101, "amount": 120.50, "status": "PENDING", "created_at": "2026-09-01"},
                {"order_id": "ORD-002", "customer_id": 102, "amount": 45.00, "status": "COMPLETED", "created_at": "2026-09-01"},
                {"order_id": "ORD-003", "customer_id": 103, "amount": 990.00, "status": "CANCELLED", "created_at": "2026-09-02"},
            ],
            "target": [
                {"order_id": "ORD-001", "customer_id": 101, "amount": 120.50, "status": "COMPLETED", "created_at": "2026-09-01"},
                {"order_id": "ORD-002", "customer_id": 102, "amount": 45.00, "status": "COMPLETED", "created_at": "2026-09-01"},
                {"order_id": "ORD-004", "customer_id": 105, "amount": 310.00, "status": "SHIPPED", "created_at": "2026-09-03"},
            ],
            "key": ["order_id"],
            "ignore": [],
            "source_name": "raw_orders.json",
            "target_name": "processed_orders.parquet",
        },
    }

    if sample_id not in samples:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found. Available: {list(samples.keys())}")

    s = samples[sample_id]
    df_a = pl.DataFrame(s["source"])
    df_b = pl.DataFrame(s["target"])

    cfg = DiffConfig(key=s["key"], ignore_columns=s["ignore"])
    diff = DataDiffEngine.compare_sources(
        source=df_a,
        target=df_b,
        config=cfg,
        source_name=s["source_name"],
        target_name=s["target_name"],
    )

    database.save_run(
        source_name=diff.source_name,
        target_name=diff.target_name,
        passed=diff.policy_report.passed,
        source_rows=diff.row_diff.source_row_count,
        target_rows=diff.row_diff.target_row_count,
        added_rows=diff.row_diff.added_count,
        removed_rows=diff.row_diff.removed_count,
        modified_rows=diff.row_diff.modified_count,
        unchanged_rows=diff.row_diff.unchanged_count,
        schema_changes=len(diff.schema_diff.added_columns) + len(diff.schema_diff.removed_columns) + len(diff.schema_diff.type_migrations),
        execution_time_ms=diff.execution_time_ms,
        summary_data=diff.model_dump(),
    )

    return diff.model_dump()


@app.get("/api/v1/history")
def get_runs_history(limit: int = 20):
    """Get history of comparison runs."""
    records = database.get_history(limit=limit)
    return [
        {
            "id": r.id,
            "source_name": r.source_name,
            "target_name": r.target_name,
            "timestamp": r.timestamp.isoformat() if r.timestamp else "",
            "passed": bool(r.passed),
            "execution_time_ms": r.execution_time_ms,
            "source_rows": r.source_rows,
            "target_rows": r.target_rows,
            "added_rows": r.added_rows,
            "removed_rows": r.removed_rows,
            "modified_rows": r.modified_rows,
            "unchanged_rows": r.unchanged_rows,
            "schema_changes_count": r.schema_changes_count,
            "summary": json.loads(r.diff_summary_json) if r.diff_summary_json else None,
        }
        for r in records
    ]


# Mount Dashboard static files if directory exists
dashboard_dir = Path(__file__).resolve().parent.parent / "dashboard"
if dashboard_dir.exists():
    app.mount("/", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")
