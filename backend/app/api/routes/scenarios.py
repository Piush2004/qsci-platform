from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ScenarioParameter(BaseModel):
    name: str
    value: float

class ScenarioRequest(BaseModel):
    base_demand: float
    scenarios: List[List[ScenarioParameter]]

class ScenarioResult(BaseModel):
    revenue: float
    cost: float
    service_level: float
    inventory_impact: float
    carbon_score: float
    recommendation: str

@router.post("/scenarios", response_model=List[ScenarioResult])
def run_scenarios(req: ScenarioRequest):
    results = []
    for idx, _ in enumerate(req.scenarios):
        # Mock calculation
        results.append({
            "revenue": req.base_demand * 1.5 * (1 + idx*0.1),
            "cost": req.base_demand * 0.8 * (1 + idx*0.05),
            "service_level": 0.95 - (idx * 0.02),
            "inventory_impact": 1000 + (idx * 200),
            "carbon_score": 85 - (idx * 5),
            "recommendation": "Optimal balance of cost and service" if idx == 0 else "High cost variation"
        })
    return results
