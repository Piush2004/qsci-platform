from pydantic import BaseModel
from typing import List, Optional

class BusinessMetrics(BaseModel):
    forecast_confidence: float
    expected_savings: float
    inventory_health: float
    stockout_risk: float
    otif_score: float
    days_of_cover: int
    forecast_bias: float
    inventory_turnover: float
    cash_to_cash_cycle: float
    perfect_order_pct: float
    order_fill_rate: float

class AIMetrics(BaseModel):
    best_model: str
    model_status: str
    rmse: float
    mape: float
    mae: float
    last_training: str
    inference_latency_ms: int

class QuantumMetrics(BaseModel):
    experiment_name: str
    circuit_depth: int
    num_qubits: int
    optimizer: str
    backend: str
    outperforms_classical: bool
    rmse: float

class RecentDecision(BaseModel):
    id: int
    action: str
    timestamp: str
    user: str

class PlannerMetrics(BaseModel):
    pending_approvals: int
    recent_decisions: List[RecentDecision]

class DashboardResponse(BaseModel):
    business: BusinessMetrics
    ai: AIMetrics
    quantum: QuantumMetrics
    planner: PlannerMetrics
