import datetime
from backend.app.db.database import get_db_connection
from typing import Dict, Any, List

class DatasetRepository:
    def register_dataset(self, name: str, version: str, rows: int, columns: int, file_hash: str, file_path: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO dataset_registry (name, version, rows, columns, file_hash, created_at, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, version, rows, columns, file_hash, timestamp, file_path))
        conn.commit()
        conn.close()
        
    def get_latest_dataset(self, name: str) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dataset_registry WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return {}
