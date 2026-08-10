from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ForecastPoint(BaseModel):
    date: str
    point_estimate: float
    lower_bound: float
    upper_bound: float
    business_risk: str

class ForecastResponse(BaseModel):
    horizon: str
    confidence_interval: float
    prediction_interval: float
    forecast_points: List[ForecastPoint]
    
class ForecastRunRequest(BaseModel):
    dataset_id: Optional[int] = None
    horizon_days: int = 30
