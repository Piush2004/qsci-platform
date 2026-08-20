"""Session management + write helpers for the Recommendation/Approval/Audit/
Outcome chain. Validation that spans multiple fields (e.g. MODIFY requiring
a quantity) lives here, at the point of creation, rather than in the ORM
model itself."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from qsci_core.persistence.models import (
    ApprovalDecision, ApprovalRecord, AuditRecord, Base, OutcomeRecord,
    RecommendationRecord, RecommendationStatus,
)
from qsci_core.recommendation.builder import Recommendation

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "experiments" / "qsci_dev.db"


def get_engine(db_path: Path | str = DEFAULT_DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(engine)
    return engine


def get_session(engine) -> Session:
    return sessionmaker(bind=engine)()


def persist_recommendation(session: Session, rec: Recommendation, forecast_run_id: int | None = None) -> RecommendationRecord:
    row = RecommendationRecord(
        sku_id=rec.sku_id,
        forecast_p10=rec.forecast_p10,
        forecast_p50=rec.forecast_p50,
        forecast_p90=rec.forecast_p90,
        suggested_order_qty=rec.suggested_order_qty,
        reorder_point=rec.reorder_point,
        risk_probability=rec.risk.probability,
        risk_level=rec.risk_level,
        confidence_overall=rec.confidence.overall,
        confidence_breakdown=rec.confidence.to_dict(),
        financial_impact=rec.financial_impact,
        rationale=rec.rationale,
        forecast_run_id=forecast_run_id,
    )
    session.add(row)
    session.flush()
    session.add(AuditRecord(recommendation_id=row.id, event_type="RECOMMENDATION_CREATED", event_payload=rec.to_dict()))
    session.commit()
    return row


def record_approval(
    session: Session,
    recommendation_id: int,
    decision: ApprovalDecision,
    approver: str,
    modified_qty: float | None = None,
    notes: str | None = None,
) -> ApprovalRecord:
    if decision == ApprovalDecision.MODIFY and modified_qty is None:
        raise ValueError("MODIFY decisions must include modified_qty")
    if decision != ApprovalDecision.MODIFY and modified_qty is not None:
        raise ValueError(f"modified_qty is only valid for MODIFY decisions, got decision={decision}")

    rec = session.get(RecommendationRecord, recommendation_id)
    if rec is None:
        raise ValueError(f"no recommendation with id={recommendation_id}")
    if rec.status != RecommendationStatus.PENDING:
        raise ValueError(
            f"recommendation {recommendation_id} already decided (status={rec.status.value}) -- "
            f"a recommendation can only be approved/rejected/modified once, not re-decided"
        )

    previous_status = rec.status
    approval = ApprovalRecord(
        recommendation_id=recommendation_id, decision=decision, approver=approver,
        modified_qty=modified_qty, notes=notes,
    )
    session.add(approval)
    rec.status = {
        ApprovalDecision.APPROVE: RecommendationStatus.APPROVED,
        ApprovalDecision.REJECT: RecommendationStatus.REJECTED,
        ApprovalDecision.MODIFY: RecommendationStatus.MODIFIED,
    }[decision]
    session.flush()
    session.add(AuditRecord(
        recommendation_id=recommendation_id,
        event_type=f"APPROVAL_{decision.value}",
        event_payload={
            "approver": approver, "modified_qty": modified_qty, "notes": notes,
            "previous_status": previous_status.value, "new_status": rec.status.value,
        },
    ))
    session.commit()
    return approval


def record_outcome(
    session: Session,
    recommendation_id: int,
    actual_qty_ordered: float | None = None,
    actual_demand_observed: float | None = None,
    notes: str | None = None,
) -> OutcomeRecord:
    rec = session.get(RecommendationRecord, recommendation_id)
    if rec is None:
        raise ValueError(f"no recommendation with id={recommendation_id}")

    outcome = OutcomeRecord(
        recommendation_id=recommendation_id, actual_qty_ordered=actual_qty_ordered,
        actual_demand_observed=actual_demand_observed, notes=notes,
    )
    session.add(outcome)
    session.flush()
    session.add(AuditRecord(
        recommendation_id=recommendation_id,
        event_type="OUTCOME_RECORDED",
        event_payload={"actual_qty_ordered": actual_qty_ordered, "actual_demand_observed": actual_demand_observed},
    ))
    session.commit()
    return outcome
