"""
Pydantic v2 Domain Schemas for QSCI API.

Separated into Create / Update / Response schemas for clean API contracts.
All response models use ConfigDict(from_attributes=True) for ORM bridging.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ─── Confidence Decomposition (PRD §9.1) ─────────────────────────────

class ConfidenceComponent(BaseModel):
    """A single factor in the 4-factor confidence decomposition."""
    name: str = Field(..., description="Factor name")
    score: float = Field(..., ge=0.0, le=1.0, description="Score 0-1")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight in composite")
    detail: str = Field("", description="Human-readable explanation")


class ConfidenceDecomposition(BaseModel):
    """Full multi-factor confidence breakdown for a recommendation."""
    composite_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: str = Field(..., description="HIGH / MODERATE / REVIEW_REQUIRED")
    components: List[ConfidenceComponent]
    auto_approval_eligible: bool = False


# ─── Forecast Schemas ─────────────────────────────────────────────────

class ForecastResponse(BaseModel):
    id: str
    tenant_id: str
    sku_id: str
    location_id: str
    predicted_demand: float
    p10: Optional[float] = None
    p50: Optional[float] = None
    p90: Optional[float] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


# ─── Recommendation Schemas ──────────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: str
    tenant_id: str
    forecast_id: str
    action_type: str
    status: str
    confidence: ConfidenceDecomposition
    sku_id: str = ""
    location_id: str = ""
    recommended_quantity: float = 0.0
    revenue_at_risk: float = 0.0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecommendationListResponse(BaseModel):
    total: int
    items: List[RecommendationResponse]


class ApproveRequest(BaseModel):
    reasoning: str = Field("", description="Optional reasoning for approving")


class OverrideRequest(BaseModel):
    reasoning: str = Field(..., min_length=10, description="Mandatory reasoning when overriding AI")
    override_quantity: Optional[float] = Field(None, description="Planner's revised quantity")


# ─── Approval Schemas ────────────────────────────────────────────────

class ApprovalResponse(BaseModel):
    id: str
    recommendation_id: str
    user_id: str
    decision: str
    reasoning: Optional[str] = None
    is_override: bool
    decided_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─── SHAP / Driver Attribution ────────────────────────────────────────

class DriverAttribution(BaseModel):
    """A single SHAP-style feature attribution."""
    feature: str
    impact: float = Field(..., description="Positive=demand driver, Negative=suppressor")
    direction: str = Field(..., description="positive or negative")


class RecommendationDetail(BaseModel):
    """Full detail view for a single recommendation — includes SHAP drivers."""
    recommendation: RecommendationResponse
    drivers: List[DriverAttribution]
    forecast_history: List[ForecastResponse] = []
