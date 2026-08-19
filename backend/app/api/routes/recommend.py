from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import (
    ApprovalActionRequest, AuditEventResponse, RecommendationResponse, RecommendRequest,
)
from app.services import recommendation_service
from qsci_core.persistence.db import record_approval
from qsci_core.persistence.models import ApprovalDecision, AuditRecord, RecommendationRecord

router = APIRouter(tags=["recommend"])


@router.post("/recommend", response_model=RecommendationResponse)
def create_recommendation(req: RecommendRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    try:
        row = recommendation_service.build_from_forecast_run(db, req.forecast_run_id, req.lead_time_days)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RecommendationResponse.model_validate(row)


@router.get("/recommendations", response_model=list[RecommendationResponse])
def list_recommendations(db: Session = Depends(get_db)) -> list[RecommendationResponse]:
    rows = db.query(RecommendationRecord).order_by(RecommendationRecord.created_at.desc()).all()
    return [RecommendationResponse.model_validate(r) for r in rows]


@router.get("/recommendations/{rec_id}", response_model=RecommendationResponse)
def get_recommendation(rec_id: int, db: Session = Depends(get_db)) -> RecommendationResponse:
    row = db.get(RecommendationRecord, rec_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"no recommendation with id={rec_id}")
    return RecommendationResponse.model_validate(row)


def _decide(rec_id: int, decision: ApprovalDecision, req: ApprovalActionRequest, db: Session) -> RecommendationResponse:
    row = db.get(RecommendationRecord, rec_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"no recommendation with id={rec_id}")
    try:
        record_approval(db, rec_id, decision, req.approver, req.modified_qty, req.notes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.refresh(row)
    return RecommendationResponse.model_validate(row)


@router.post("/recommendations/{rec_id}/approve", response_model=RecommendationResponse)
def approve(rec_id: int, req: ApprovalActionRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    return _decide(rec_id, ApprovalDecision.APPROVE, req, db)


@router.post("/recommendations/{rec_id}/reject", response_model=RecommendationResponse)
def reject(rec_id: int, req: ApprovalActionRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    return _decide(rec_id, ApprovalDecision.REJECT, req, db)


@router.post("/recommendations/{rec_id}/modify", response_model=RecommendationResponse)
def modify(rec_id: int, req: ApprovalActionRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    if req.modified_qty is None:
        raise HTTPException(status_code=422, detail="modified_qty is required for a MODIFY decision")
    return _decide(rec_id, ApprovalDecision.MODIFY, req, db)


@router.get("/audit", response_model=list[AuditEventResponse])
def audit(recommendation_id: int | None = None, db: Session = Depends(get_db)) -> list[AuditEventResponse]:
    q = db.query(AuditRecord).order_by(AuditRecord.created_at.desc())
    if recommendation_id is not None:
        q = q.filter(AuditRecord.recommendation_id == recommendation_id)
    return [AuditEventResponse.model_validate(r) for r in q.limit(200).all()]
