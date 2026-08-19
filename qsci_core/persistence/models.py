"""SQLAlchemy models for the human-in-the-loop chain:
Recommendation -> Approval -> Audit, plus Outcome for later
predicted-vs-actual comparison (RQ2/H2)."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ApprovalDecision(enum.Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY = "MODIFY"


class RecommendationStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class RunStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[RecommendationStatus] = mapped_column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    forecast_p10: Mapped[float] = mapped_column(Float)
    forecast_p50: Mapped[float] = mapped_column(Float)
    forecast_p90: Mapped[float] = mapped_column(Float)
    suggested_order_qty: Mapped[float] = mapped_column(Float)
    reorder_point: Mapped[float] = mapped_column(Float)

    risk_probability: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(16))

    confidence_overall: Mapped[float] = mapped_column(Float)
    confidence_breakdown: Mapped[dict] = mapped_column(JSON)

    financial_impact: Mapped[dict] = mapped_column(JSON)
    rationale: Mapped[str] = mapped_column(Text)

    approvals: Mapped[list["ApprovalRecord"]] = relationship(back_populates="recommendation", cascade="all, delete-orphan")
    audit_events: Mapped[list["AuditRecord"]] = relationship(back_populates="recommendation", cascade="all, delete-orphan")
    outcomes: Mapped[list["OutcomeRecord"]] = relationship(back_populates="recommendation", cascade="all, delete-orphan")


class ApprovalRecord(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), index=True)
    decision: Mapped[ApprovalDecision] = mapped_column(Enum(ApprovalDecision))
    modified_qty: Mapped[float | None] = mapped_column(Float, nullable=True)
    approver: Mapped[str] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    recommendation: Mapped["RecommendationRecord"] = relationship(back_populates="approvals")


class AuditRecord(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    event_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    recommendation: Mapped["RecommendationRecord"] = relationship(back_populates="audit_events")


class OutcomeRecord(Base):
    __tablename__ = "outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), index=True)
    actual_qty_ordered: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_demand_observed: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    recommendation: Mapped["RecommendationRecord"] = relationship(back_populates="outcomes")


class DatasetRecord(Base):
    """Metadata for a real, loaded dataset -- never a placeholder row.
    Populated by the data-ingest service reading actual files on disk
    (qsci_core.data.loaders / .quality), not hand-typed values."""
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(256))
    version: Mapped[str] = mapped_column(String(64))
    record_count: Mapped[int] = mapped_column(Integer)
    date_range_start: Mapped[str | None] = mapped_column(String(32), nullable=True)
    date_range_end: Mapped[str | None] = mapped_column(String(32), nullable=True)
    quality_status: Mapped[str] = mapped_column(String(16))  # "LIVE" per qsci_core.data.quality
    quality_report: Mapped[dict] = mapped_column(JSON)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ForecastRunRecord(Base):
    """One forecasting run's inputs/outputs -- classical or quantum. The
    quantum track's runs are always status='RESEARCH', never 'LIVE',
    per CLAUDE.md sec.1 -- this module never overrides that label."""
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset: Mapped[str] = mapped_column(String(128))
    series_id: Mapped[str] = mapped_column(String(128))
    model: Mapped[str] = mapped_column(String(64))  # "seasonal_naive" | "lightgbm" | "vqr"
    horizon: Mapped[int] = mapped_column(Integer)
    run_status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.PENDING)
    label: Mapped[str] = mapped_column(String(16))  # LIVE | RESEARCH
    predictions: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"p10": [...], "p50": [...], "p90": [...]} where available
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # rmse/mae/wmape/bias/fva
    runtime_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # e.g. n_qubits, circuit depth
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OptimizationRunRecord(Base):
    """One optimization run -- inventory (EOQ) or routing (OR-Tools /
    annealing / QAOA). Quantum solver runs can be long (QAOA up to ~10
    minutes, Phase 3/4-measured) -- run_status tracks async progress; the
    API layer must never block a request on solver completion."""
    __tablename__ = "optimization_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_type: Mapped[str] = mapped_column(String(32))  # "inventory" | "routing"
    method: Mapped[str] = mapped_column(String(64))  # "eoq" | "or_tools" | "simulated_annealing" | "qaoa"
    run_status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.PENDING)
    label: Mapped[str] = mapped_column(String(16))  # LIVE | RESEARCH | ILLUSTRATIVE
    input_params: Mapped[dict] = mapped_column(JSON)
    objective: Mapped[float | None] = mapped_column(Float, nullable=True)
    solution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feasible: Mapped[bool | None] = mapped_column(nullable=True)
    optimality_gap_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    resource_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # qubits/depth/gates/shots where applicable
    runtime_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ExperimentResultRecord(Base):
    """Read-mostly index over experiments/results/*.json -- backs the
    /api/v1/research/* endpoints. Seeded from real files on disk (see
    backend/app/db/seed_experiments.py); this table is never the source
    of truth for a number, only a queryable mirror of one."""
    __tablename__ = "experiment_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phase: Mapped[str] = mapped_column(String(32), index=True)  # "phase2" | "phase3" | "phase4" | "phase5"
    experiment: Mapped[str] = mapped_column(String(128), index=True)
    source_file: Mapped[str] = mapped_column(String(256))
    label: Mapped[str] = mapped_column(String(16))  # LIVE | RESEARCH | ILLUSTRATIVE | PENDING
    summary: Mapped[dict] = mapped_column(JSON)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
