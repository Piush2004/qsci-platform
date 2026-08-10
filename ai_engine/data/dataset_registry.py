import json
import os
import hashlib
from datetime import datetime
import pandas as pd

class DatasetRegistry:
    """Tracks dataset versions for reproducibility."""
    
    REGISTRY_PATH = "d:/Projects/QML project/data/dataset_registry.json"
    
    def __init__(self):
        os.makedirs(os.path.dirname(self.REGISTRY_PATH), exist_ok=True)
        if not os.path.exists(self.REGISTRY_PATH):
            with open(self.REGISTRY_PATH, 'w') as f:
                json.dump({}, f)

    def register(self, name: str, df: pd.DataFrame, file_path: str) -> dict:
        """Register a dataset with version, hash, row count, column count, timestamp."""
        with open(self.REGISTRY_PATH, 'r') as f:
            registry = json.load(f)
            
        if name not in registry:
            registry[name] = []
            
        version = len(registry[name]) + 1
        
        entry = {
            "version": version,
            "hash": self._compute_hash(df),
            "rows": len(df),
            "columns": len(df.columns),
            "created_at": datetime.now().isoformat(),
            "file_path": file_path
        }
        
        registry[name].append(entry)
        
        with open(self.REGISTRY_PATH, 'w') as f:
            json.dump(registry, f, indent=4)
            
        return entry
    
    def get_latest_version(self, name: str) -> dict:
        """Get metadata for the latest version of a named dataset."""
        with open(self.REGISTRY_PATH, 'r') as f:
            registry = json.load(f)
            
        if name in registry and registry[name]:
            return registry[name][-1]
        return {}
    
    def get_all(self) -> list:
        """Get all registered datasets."""
        with open(self.REGISTRY_PATH, 'r') as f:
            registry = json.load(f)
        return registry
    
    def _compute_hash(self, df: pd.DataFrame) -> str:
        """SHA-256 hash of the DataFrame for integrity checking."""
        return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
