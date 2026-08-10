from pydantic import BaseModel
from typing import Optional

class AuditEntryCreate(BaseModel):
    user: str
    recommendation_summary: str
    action: str
    final_decision: str
    reason: str
    expected_business_impact: str
    risk_level: str
    timestamp: Optional[str] = None

class AuditEntry(AuditEntryCreate):
    id: int
