import pandas as pd
import numpy as np

class DataQualityIntelligence:
    """
    Evaluates dataset quality before allowing AI pipeline processing.
    Generates Data Quality and Forecast Readiness Scores.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def detect_schema(self):
        """Identifies columns, data types, and primary keys."""
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        
    def check_missing_values(self):
        """Calculates percentage of missing values per column."""
        missing = self.df.isnull().mean() * 100
        return missing.to_dict()
        
    def detect_outliers(self, numerical_cols=None):
        """Uses Z-score to detect outliers in numerical columns."""
        if not numerical_cols:
            numerical_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
        outliers = {}
        for col in numerical_cols:
            z_scores = np.abs((self.df[col] - self.df[col].mean()) / (self.df[col].std() + 1e-9))
            outlier_pct = (z_scores > 3).mean() * 100
            outliers[col] = outlier_pct
        return outliers
        
    def generate_readiness_score(self):
        """Aggregates metrics into an overall Dataset Health Score."""
        missing = self.check_missing_values()
        outliers = self.detect_outliers()
        
        # Penalize for missing values and high outliers
        avg_missing = np.mean(list(missing.values())) if missing else 0
        avg_outliers = np.mean(list(outliers.values())) if outliers else 0
        
        health_score = 100 - (avg_missing * 1.5) - (avg_outliers * 1.0)
        health_score = max(0, min(100, health_score))
        
        is_ready = health_score >= 85.0
        
        return {
            "Dataset Health Score": round(health_score, 2),
            "Forecast Ready": "YES" if is_ready else "NO",
            "Avg Missing Values (%)": round(avg_missing, 2),
            "Recommendation": "Proceed to AI Pipeline" if is_ready else "Data Imputation Required"
        }
