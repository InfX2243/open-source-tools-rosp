# DataGuard REST API Reference

The DataGuard REST API is built on FastAPI and exposes endpoints for automated quality evaluation, profiling, rule management, and historical run tracking.

---

## 🔌 API Endpoints

### Validation Endpoints

- `POST /api/v1/validations/run`: Execute validation on a file path or database source and persist run metadata.
- `POST /api/v1/validations/upload`: Upload a CSV, JSON, or Parquet file directly via multipart form and validate against rules.
- `GET /api/v1/validations/history`: Retrieve recent validation runs, quality scores, durations, and pass/fail gate statuses.
- `GET /api/v1/validations/{run_id}`: Retrieve detailed summary, column profile, and sample violation records for a specific run.

### Rules & Profiling

- `GET /api/v1/rules/templates`: Fetch starter YAML configuration templates (`customer`, `ecommerce`, `basic`).
- `POST /api/v1/profiles/run`: Compute statistical column profiling metrics for an uploaded file.

### Projects

- `GET /api/v1/projects`: List configured project workspaces.
- `POST /api/v1/projects`: Create a new project workspace.

### System & Health

- `GET /health`: Health check endpoint returning version and service status.
- `GET /docs`: Interactive Swagger OpenAPI documentation.
- `GET /`: Interactive DataGuard Web Dashboard.
