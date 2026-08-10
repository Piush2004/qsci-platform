import pandas as pd
import numpy as np

class TFTForecaster:
    """
    Mock Temporal Fusion Transformer (TFT) Forecaster.
    In production, this would wrap pytorch-forecasting or darts.
    TFT is the deep learning SOTA for multi-horizon time series forecasting.
    """
    def __init__(self, prediction_length: int = 14, **kwargs):
        self.prediction_length = prediction_length
        self.params = kwargs
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame, target_col: str = 'demand'):
        """
        Mock training for TFT.
        """
        self.is_fitted = True
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        TFT outputs probabilistic forecasts (quantiles).
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
            
        n_samples = len(df)
        
        # Base prediction
        p50 = np.random.uniform(80, 120, size=n_samples)
        
        # Quantiles for uncertainty
        p10 = p50 * np.random.uniform(0.7, 0.9, size=n_samples)
        p90 = p50 * np.random.uniform(1.1, 1.3, size=n_samples)
        
        results = pd.DataFrame({
            'date': df.get('date', pd.date_range(start='2026-01-01', periods=n_samples)),
            'sku': df.get('sku', 'UNKNOWN'),
            'location': df.get('location', 'UNKNOWN'),
            'p10': p10,
            'p50': p50,
            'p90': p90
        })
        
        return results
        
    def get_attention_weights(self) -> dict:
        """
        Mock attention weights for interpretability (Variable Selection Network).
        """
        return {
            'demand_lag_1': 0.35,
            'demand_lag_7': 0.25,
            'is_weekend': 0.15,
            'month': 0.10,
            'demand_rolling_mean_7': 0.15
        }
