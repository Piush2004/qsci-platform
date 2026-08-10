"""
Recommendations API — Core HITL Decision Intelligence Endpoints.

Exposes the Planner Workspace API:
- GET /recommendations — list pending AI recommendations
- GET /recommendations/{id} — detail view with SHAP drivers
- POST /recommendations/{id}/approve — planner approves
- POST /recommendations/{id}/override — planner overrides (mandatory reasoning)
"""
from fastapi import APIRouter, Depends
from typing import Optional

from backend.app.schemas.domain import (
    RecommendationListResponse,
    RecommendationDetail,
    ApproveRequest,
    OverrideRequest,
)
from backend.app.core.errors import not_found, conflict
from backend.app.core.events import event_bus, DomainEvents
from backend.app.api.dependencies import get_current_user, CurrentUser
from backend.app.services.ai_engine import ai_engine

router = APIRouter()

# In-memory store for Phase 2 (replaces DB queries until SQLAlchemy wiring is complete)
_recommendations_cache = None


def _get_recommendations():
    global _recommendations_cache
    if _recommendations_cache is None:
        _recommendations_cache = ai_engine.generate_recommendations(count=8)
    return _recommendations_cache


@router.get("/recommendations", response_model=RecommendationListResponse)
async def list_recommendations(
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    List all AI-generated recommendations for the planner's tenant.
    Optionally filter by status (pending, approved, overridden).
    """
    recs = _get_recommendations()
    if status:
        recs = [r for r in recs if r["status"] == status]
    return {"total": len(recs), "items": recs}


@router.get("/recommendations/{rec_id}")
async def get_recommendation_detail(
    rec_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get the full detail view for a single recommendation,
    including SHAP driver attribution and forecast history.
    """
    recs = _get_recommendations()
    rec = next((r for r in recs if r["id"] == rec_id), None)
    if not rec:
        raise not_found("Recommendation", rec_id)

    drivers = ai_engine.generate_shap_drivers(top_n=5)
    return {
        "recommendation": rec,
        "drivers": [d.model_dump() for d in drivers],
        "forecast_history": [],
    }


@router.post("/recommendations/{rec_id}/approve")
async def approve_recommendation(
    rec_id: str,
    body: ApproveRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Approve an AI recommendation. Emits RecommendationApproved domain event.
    """
    recs = _get_recommendations()
    rec = next((r for r in recs if r["id"] == rec_id), None)
    if not rec:
        raise not_found("Recommendation", rec_id)
    if rec["status"] != "pending":
        raise conflict(f"Recommendation is already '{rec['status']}'. Cannot approve.")

    rec["status"] = "approved"

    # Emit domain event
    await event_bus.publish(DomainEvents.RECOMMENDATION_APPROVED, {
        "recommendation_id": rec_id,
        "user_id": current_user.id,
        "reasoning": body.reasoning,
    })

    return {"status": "approved", "recommendation_id": rec_id}


@router.post("/recommendations/{rec_id}/override")
async def override_recommendation(
    rec_id: str,
    body: OverrideRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Override an AI recommendation with planner judgment.
    Mandatory reasoning is captured as training data for the Human Feedback Loop (PRD §9.2).
    Emits RecommendationOverridden domain event.
    """
    recs = _get_recommendations()
    rec = next((r for r in recs if r["id"] == rec_id), None)
    if not rec:
        raise not_found("Recommendation", rec_id)
    if rec["status"] != "pending":
        raise conflict(f"Recommendation is already '{rec['status']}'. Cannot override.")

    rec["status"] = "overridden"
    if body.override_quantity is not None:
        rec["recommended_quantity"] = body.override_quantity

    # Emit domain event — this feeds the Human Feedback Loop
    await event_bus.publish(DomainEvents.RECOMMENDATION_OVERRIDDEN, {
        "recommendation_id": rec_id,
        "user_id": current_user.id,
        "reasoning": body.reasoning,
        "override_quantity": body.override_quantity,
        "original_quantity": rec.get("recommended_quantity"),
    })

    return {
        "status": "overridden",
        "recommendation_id": rec_id,
        "feedback_captured": True,
    }
