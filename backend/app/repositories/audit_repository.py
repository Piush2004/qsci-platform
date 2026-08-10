import datetime
from backend.app.db.database import get_db_connection
from backend.app.schemas.audit import AuditEntryCreate, AuditEntry
from typing import List

class AuditRepository:
    def create_entry(self, entry: AuditEntryCreate) -> AuditEntry:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = entry.timestamp or datetime.datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO audit_log (timestamp, user, recommendation_summary, action, final_decision, reason, expected_business_impact, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            entry.user,
            entry.recommendation_summary,
            entry.action,
            entry.final_decision,
            entry.reason,
            entry.expected_business_impact,
            entry.risk_level
        ))
        conn.commit()
        
        entry_id = cursor.lastrowid
        conn.close()
        
        return AuditEntry(id=entry_id, timestamp=timestamp, **entry.model_dump(exclude={"timestamp"}))

    def get_all(self) -> List[AuditEntry]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [AuditEntry(**dict(row)) for row in rows]
