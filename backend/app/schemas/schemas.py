"""Pydantic request/response schemas. Deliberately thin -- these mirror
qsci_core/persistence record shapes, they never redefine business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    qsci_core_importable: bool


class DatasetResponse(BaseModel):
    id: int
    name: str
    source: str
    version: str
    record_count: int
    date_range_start: str | None
    date_range_end: str | None
    quality_status: str
    quality_report: dict
    ingested_at: datetime

    model_config = {"from_attributes": True}


class DataIngestRequest(BaseModel):
    dataset: str = Field(description="'m5' | 'cvrplib' | 'last_mile'")
    cvrplib_instance: str | None = "A-n32-k5"


class ForecastRequest(BaseModel):
    series_id: str = "FOODS_3_090_CA_1_evaluation"
    model: str = Field(description="'seasonal_naive' | 'lightgbm' | 'vqr'")
    horizon: int = Field(default=14, gt=0, le=90)

    @field_validator("model")
    @classmethod
    def _validate_model(cls, v: str) -> str:
        if v not in {"seasonal_naive", "lightgbm", "vqr"}:
            raise ValueError(f"model must be one of seasonal_naive/lightgbm/vqr, got '{v}'")
        return v


class ForecastRunResponse(BaseModel):
    id: int
    dataset: str
    series_id: str
    model: str
    horizon: int
    run_status: str
    label: str
    predictions: dict | None
    metrics: dict | None
    runtime_seconds: float | None
    model_metadata: dict | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}

    @field_validator("run_status", mode="before")
    @classmethod
    def _enum_to_str(cls, v: Any) -> str:
        return v.value if hasattr(v, "value") else v


class OptimizeRequest(BaseModel):
    problem_type: str = Field(description="'inventory' | 'routing'")
    method: str = Field(description="'eoq' | 'or_tools' | 'simulated_annealing' | 'qaoa'")
    params: dict[str, Any] = Field(default_factory=dict)


class OptimizationRunResponse(BaseModel):
    id: int
    problem_type: str
    method: str
    run_status: str
    label: str
    input_params: dict
    objective: float | None
    solution: dict | None
    feasible: bool | None
    optimality_gap_pct: float | None
    resource_metrics: dict | None
    runtime_seconds: float | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}

    @field_validator("run_status", mode="before")
    @classmethod
    def _enum_to_str(cls, v: Any) -> str:
        return v.value if hasattr(v, "value") else v


class RecommendRequest(BaseModel):
    forecast_run_id: int
    lead_time_days: float = 3.0


class RecommendationResponse(BaseModel):
    id: int
    sku_id: str
    status: str
    created_at: datetime
    forecast_p10: float
    forecast_p50: float
    forecast_p90: float
    suggested_order_qty: float
    reorder_point: float
    risk_probability: float
    risk_level: str
    confidence_overall: float
    confidence_breakdown: dict
    financial_impact: dict
    rationale: str

    model_config = {"from_attributes": True}

    @field_validator("status", mode="before")
    @classmethod
    def _enum_to_str(cls, v: Any) -> str:
        return v.value if hasattr(v, "value") else v


class ApprovalActionRequest(BaseModel):
    approver: str = Field(min_length=1, description="Placeholder identity field -- NOT cryptographically verified (no auth system exists yet, disclosed in docs/PHASE_6_PREIMPLEMENTATION_AUDIT.md sec.10)")
    modified_qty: float | None = None
    notes: str | None = None


class AuditEventResponse(BaseModel):
    id: int
    recommendation_id: int
    event_type: str
    event_payload: dict
    created_at: datetime

    model_config = {"from_attributes": True}
