from fastapi import APIRouter, HTTPException
from backend.app.schemas.audit import AuditEntryCreate, AuditEntry
from backend.app.services.audit_service import AuditService
from typing import List

router = APIRouter()
audit_service = AuditService()

@router.get("/audit", response_model=List[AuditEntry])
def get_all_audits():
    return audit_service.get_all_entries()

@router.post("/audit", response_model=AuditEntry)
def create_audit_entry(entry: AuditEntryCreate):
    try:
        return audit_service.record_decision(entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
