# DataGuard Documentation

**DataGuard** is a high-performance, developer-friendly open-source data quality, validation, and profiling platform for modern data engineering workflows.

---

## ⚡ Key Capabilities

- **Polars Fast Engine**: Ingest and validate CSV, Parquet, JSON, and SQL datasets at lightning speed.
- **Declarative YAML Rules**: Define constraints for data types, uniqueness, regex formats, range bounds, allowed sets, and custom Python expressions.
- **Weighted Quality Scoring**: Transparent, configurable scoring with penalty curves based on violation severities.
- **Statistical Profiler**: Automatic detection of column distributions, null ratios, cardinality, quantiles, and min/max/mean metrics.
- **Drift & Anomaly Detection**: Compare validation runs against historical baseline profiles to identify sudden volume shifts or null spikes.
- **Multi-Format Reporting**: Rich Terminal Dashboard, Standalone Interactive HTML Reports, Machine-readable JSON, and GitHub PR Markdown summaries.
- **REST API & Dashboard**: FastAPI-powered backend with SQLite/PostgreSQL metadata persistence and an interactive single-page Web UI.
- **CI/CD Quality Gates**: Exit-code driven quality gating (`--fail-on high`) to block bad data in deployment pipelines.
