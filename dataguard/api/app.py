"""FastAPI application for DataGuard REST API and Dashboard backend."""

import os
import json
import tempfile
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session

from dataguard import __version__
from dataguard.core.models import ValidationSummary, RuleConfig, DatasetProfile
from dataguard.core.engine import ValidationEngine
from dataguard.core.profiler import DataProfiler
from dataguard.config.loader import ConfigLoader
from dataguard.sources import load_dataset
from dataguard.reporters.html import HTMLReporter
from api.database import init_db, get_db, ValidationRunRecord, Project
from api.schemas import (
    RunValidationRequest,
    DirectDataValidationRequest,
    ValidationRunItem,
    ProjectCreate,
    ProjectResponse,
)

# Initialize database tables
init_db()

app = FastAPI(
    title="DataGuard REST API",
    description="Developer-friendly Data Quality, Validation, Profiling & Observability Engine",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard")
if os.path.exists(DASHBOARD_DIR):
    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")


@app.get("/health", tags=["System"])
def health_check():
    """Service health check endpoint."""
    return {"status": "ok", "service": "DataGuard", "version": __version__}


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def serve_dashboard():
    """Serve the interactive Web Dashboard."""
    index_file = os.path.join(DASHBOARD_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>DataGuard API is running. Visit /docs for OpenAPI documentation.</h1>")


@app.post("/api/v1/validations/run", response_model=ValidationSummary, tags=["Validation"])
def run_validation(
    req: RunValidationRequest,
    db: Session = Depends(get_db),
):
    """Run validation for a file path or database source and persist run history."""
    try:
        config: RuleConfig
        if req.rules_yaml:
            config = ConfigLoader.load_from_string(req.rules_yaml, filename="request.yaml")
        elif req.rules_json:
            config = req.rules_json
        else:
            config = RuleConfig(dataset=req.source)

        engine = ValidationEngine(config)
        summary = engine.validate_source(req.source, config=config)

        # Store in database
        project_id = None
        if req.project_name:
            proj = db.query(Project).filter(Project.name == req.project_name).first()
            if not proj:
                proj = Project(name=req.project_name)
                db.add(proj)
                db.commit()
                db.refresh(proj)
            project_id = proj.id

        run_rec = ValidationRunRecord(
            project_id=project_id,
            dataset_name=summary.dataset_name,
            source_path=summary.source_path,
            quality_score=summary.quality_score,
            passed_gate=summary.passed_gate,
            gate_reason=summary.gate_reason,
            total_rules=summary.total_rules,
            passed_rules=summary.passed_rules,
            failed_rules=summary.failed_rules,
            warned_rules=summary.warned_rules,
            row_count=summary.profile.row_count if summary.profile else 0,
            column_count=summary.profile.column_count if summary.profile else 0,
            duration_ms=summary.total_duration_ms,
            summary_json=summary.model_dump_json(),
        )
        db.add(run_rec)
        db.commit()

        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/validations/upload", response_model=ValidationSummary, tags=["Validation"])
async def upload_and_validate(
    file: UploadFile = File(...),
    rules_yaml: Optional[str] = Form(None),
    project_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a CSV/JSON/Parquet file and run validation against rules."""
    suffix = os.path.splitext(file.filename or "data.csv")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        config: RuleConfig
        if rules_yaml:
            config = ConfigLoader.load_from_string(rules_yaml, filename="upload_rules.yaml")
        else:
            config = RuleConfig(dataset=file.filename)

        engine = ValidationEngine(config)
        summary = engine.validate_source(tmp_path, config=config)
        summary.dataset_name = file.filename or "uploaded_dataset"
        summary.source_path = file.filename or "uploaded_file"

        # Record in DB
        project_id = None
        if project_name:
            proj = db.query(Project).filter(Project.name == project_name).first()
            if not proj:
                proj = Project(name=project_name)
                db.add(proj)
                db.commit()
                db.refresh(proj)
            project_id = proj.id

        run_rec = ValidationRunRecord(
            project_id=project_id,
            dataset_name=summary.dataset_name,
            source_path=summary.source_path,
            quality_score=summary.quality_score,
            passed_gate=summary.passed_gate,
            gate_reason=summary.gate_reason,
            total_rules=summary.total_rules,
            passed_rules=summary.passed_rules,
            failed_rules=summary.failed_rules,
            warned_rules=summary.warned_rules,
            row_count=summary.profile.row_count if summary.profile else 0,
            column_count=summary.profile.column_count if summary.profile else 0,
            duration_ms=summary.total_duration_ms,
            summary_json=summary.model_dump_json(),
        )
        db.add(run_rec)
        db.commit()

        return summary
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@app.get("/api/v1/validations/history", response_model=List[ValidationRunItem], tags=["Validation"])
def get_validation_history(
    limit: int = Query(50, ge=1, le=500),
    project_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List historical validation runs and their quality scores."""
    query = db.query(ValidationRunRecord).order_by(ValidationRunRecord.created_at.desc())
    if project_name:
        query = query.join(Project).filter(Project.name == project_name)
    runs = query.limit(limit).all()

    return [
        ValidationRunItem(
            id=r.id,
            dataset_name=r.dataset_name,
            quality_score=r.quality_score,
            passed_gate=r.passed_gate,
            total_rules=r.total_rules,
            passed_rules=r.passed_rules,
            failed_rules=r.failed_rules,
            row_count=r.row_count,
            duration_ms=r.duration_ms,
            created_at=r.created_at,
        )
        for r in runs
    ]


@app.get("/api/v1/validations/{run_id}", response_model=ValidationSummary, tags=["Validation"])
def get_validation_run_details(run_id: int, db: Session = Depends(get_db)):
    """Retrieve full summary and sample violations for a specific run ID."""
    run_rec = db.query(ValidationRunRecord).filter(ValidationRunRecord.id == run_id).first()
    if not run_rec:
        raise HTTPException(status_code=404, detail="Validation run not found")
    data = json.loads(run_rec.summary_json)
    return ValidationSummary(**data)


@app.get("/api/v1/rules/templates", tags=["Rules"])
def get_rule_templates():
    """Retrieve starter YAML configuration templates."""
    return {
        "customer": ConfigLoader.get_template("customer"),
        "ecommerce": ConfigLoader.get_template("ecommerce"),
        "basic": ConfigLoader.get_template("basic"),
    }


@app.get("/api/v1/projects", response_model=List[ProjectResponse], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)):
    """List all configured projects."""
    projs = db.query(Project).all()
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            created_at=p.created_at,
            run_count=len(p.runs),
        )
        for p in projs
    ]


@app.post("/api/v1/projects", response_model=ProjectResponse, tags=["Projects"])
def create_project(req: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project workspace."""
    existing = db.query(Project).filter(Project.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists")
    proj = Project(name=req.name, description=req.description)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return ProjectResponse(
        id=proj.id,
        name=proj.name,
        description=proj.description,
        created_at=proj.created_at,
        run_count=0,
    )


@app.get("/api/v1/samples", tags=["Samples"])
def list_samples():
    """List available sample datasets for quick testing in the UI."""
    return [
        {
            "id": "customers",
            "name": "Clean Customers (customers.csv)",
            "description": "10 valid customer records with valid emails, ages, and statuses.",
            "file": "examples/data/customers.csv",
            "rule_template": "customer",
            "expected": "100% Quality Score (PASS)",
        },
        {
            "id": "dirty_users",
            "name": "Dirty / Corrupted Data (dirty_users.csv)",
            "description": "Dataset with intentional flaws: duplicate ID, invalid email, negative age, bad status.",
            "file": "examples/data/dirty_users.csv",
            "rule_template": "customer",
            "expected": "~68% Quality Score (FAIL Gate)",
        },
        {
            "id": "orders",
            "name": "E-Commerce Orders (orders.json)",
            "description": "JSON transaction records with currency, order amount, and item counts.",
            "file": "examples/data/orders.json",
            "rule_template": "ecommerce",
            "expected": "100% Quality Score (PASS)",
        },
    ]


@app.post("/api/v1/validations/sample/{sample_id}", response_model=ValidationSummary, tags=["Samples"])
def validate_sample_dataset(sample_id: str, db: Session = Depends(get_db)):
    """Run validation on a pre-packaged sample dataset."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_map = {
        "customers": (
            os.path.join(base_dir, "examples", "data", "customers.csv"),
            os.path.join(base_dir, "examples", "rules", "customer_rules.yaml"),
        ),
        "dirty_users": (
            os.path.join(base_dir, "examples", "data", "dirty_users.csv"),
            os.path.join(base_dir, "examples", "rules", "customer_rules.yaml"),
        ),
        "orders": (
            os.path.join(base_dir, "examples", "data", "orders.json"),
            os.path.join(base_dir, "examples", "rules", "ecommerce_rules.yaml"),
        ),
    }

    if sample_id not in samples_map:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found. Available: {list(samples_map.keys())}")

    data_path, rule_path = samples_map[sample_id]
    if not os.path.exists(data_path) or not os.path.exists(rule_path):
        raise HTTPException(status_code=500, detail="Sample data or rules file missing on server.")

    config = ConfigLoader.load_from_file(rule_path)
    engine = ValidationEngine(config)
    summary = engine.validate_source(data_path, config=config)

    # Record in history
    run_rec = ValidationRunRecord(
        project_id=None,
        dataset_name=summary.dataset_name,
        source_path=summary.source_path,
        quality_score=summary.quality_score,
        passed_gate=summary.passed_gate,
        gate_reason=summary.gate_reason,
        total_rules=summary.total_rules,
        passed_rules=summary.passed_rules,
        failed_rules=summary.failed_rules,
        warned_rules=summary.warned_rules,
        row_count=summary.profile.row_count if summary.profile else 0,
        column_count=summary.profile.column_count if summary.profile else 0,
        duration_ms=summary.total_duration_ms,
        summary_json=summary.model_dump_json(),
    )
    db.add(run_rec)
    db.commit()

    return summary

