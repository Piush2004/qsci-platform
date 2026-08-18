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


class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
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
