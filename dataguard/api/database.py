"""Database models and SQLite/PostgreSQL persistence layer using SQLAlchemy."""

import os
from datetime import datetime
from typing import Generator
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DB_URL = os.getenv("DATAGUARD_DB_URL", "sqlite:///dataguard.db")

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("ValidationRunRecord", back_populates="project", cascade="all, delete-orphan")


class ValidationRunRecord(Base):
    __tablename__ = "validation_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    dataset_name = Column(String(255), index=True, nullable=False)
    source_path = Column(String(500), nullable=True)
    quality_score = Column(Float, nullable=False)
    passed_gate = Column(Boolean, nullable=False)
    gate_reason = Column(String(255), nullable=True)
    total_rules = Column(Integer, default=0)
    passed_rules = Column(Integer, default=0)
    failed_rules = Column(Integer, default=0)
    warned_rules = Column(Integer, default=0)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    duration_ms = Column(Float, default=0.0)
    summary_json = Column(Text, nullable=False)  # Full JSON payload
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    project = relationship("Project", back_populates="runs")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
