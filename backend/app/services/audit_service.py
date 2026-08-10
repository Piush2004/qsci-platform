from backend.app.repositories.audit_repository import AuditRepository
from backend.app.schemas.audit import AuditEntryCreate

class AuditService:
    def __init__(self):
        self.repo = AuditRepository()

    def record_decision(self, entry: AuditEntryCreate):
        if not entry.reason:
            raise ValueError("Reason is MANDATORY")
        return self.repo.create_entry(entry)

    def get_all_entries(self):
        return self.repo.get_all()
