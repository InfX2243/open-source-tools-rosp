"""Database storage for DataDiff comparison run history."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///datadiff_history.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ComparisonRunRecord(Base):
    """Stores metadata and full result of a dataset comparison run."""

    __tablename__ = "comparison_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name = Column(String(255), nullable=False)
    target_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    execution_time_ms = Column(Float, default=0.0)
    passed = Column(Integer, default=1)  # 1 = True, 0 = False

    source_rows = Column(Integer, default=0)
    target_rows = Column(Integer, default=0)
    added_rows = Column(Integer, default=0)
    removed_rows = Column(Integer, default=0)
    modified_rows = Column(Integer, default=0)
    unchanged_rows = Column(Integer, default=0)

    schema_changes_count = Column(Integer, default=0)
    diff_summary_json = Column(Text, nullable=False)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def save_run(
    source_name: str,
    target_name: str,
    passed: bool,
    source_rows: int,
    target_rows: int,
    added_rows: int,
    removed_rows: int,
    modified_rows: int,
    unchanged_rows: int,
    schema_changes: int,
    execution_time_ms: float,
    summary_data: Dict[str, Any],
) -> ComparisonRunRecord:
    """Save a comparison run result to sqlite database."""
    init_db()
    session = SessionLocal()
    try:
        record = ComparisonRunRecord(
            source_name=source_name,
            target_name=target_name,
            passed=1 if passed else 0,
            source_rows=source_rows,
            target_rows=target_rows,
            added_rows=added_rows,
            removed_rows=removed_rows,
            modified_rows=modified_rows,
            unchanged_rows=unchanged_rows,
            schema_changes_count=schema_changes,
            execution_time_ms=execution_time_ms,
            diff_summary_json=json.dumps(summary_data),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    finally:
        session.close()


def get_history(limit: int = 50) -> List[ComparisonRunRecord]:
    """Retrieve historical comparison runs."""
    init_db()
    session = SessionLocal()
    try:
        return session.query(ComparisonRunRecord).order_by(ComparisonRunRecord.id.desc()).limit(limit).all()
    finally:
        session.close()
