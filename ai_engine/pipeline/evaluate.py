import numpy as np
import pandas as pd
from typing import Dict, Union

class EvaluationMetrics:
    """
    Standard supply chain and ML evaluation metrics.
    Used for comparing Quantum vs Classical models.
    """
    
    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.sqrt(np.mean((y_true - y_pred) ** 2))
        
    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.mean(np.abs(y_true - y_pred))
        
    @staticmethod
    def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        
    @staticmethod
    def wmape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Weighted Mean Absolute Percentage Error.
        Standard metric in supply chain forecasting (handles zero demand better than MAPE).
        """
        sum_actuals = np.sum(np.abs(y_true))
        if sum_actuals == 0:
            return 0.0
        return np.sum(np.abs(y_true - y_pred)) / sum_actuals * 100
        
    @staticmethod
    def bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Forecast Bias: sum(actuals) - sum(forecast)
        Negative means over-forecasting, positive means under-forecasting.
        """
        return np.sum(y_true) - np.sum(y_pred)
        
    @staticmethod
    def forecast_value_added(naive_error: float, model_error: float) -> float:
        """
        FVA: 1 - (Model Error / Naive Error)
        Positive FVA means the model is adding value over a naive baseline.
        """
        if naive_error == 0:
            return 0.0
        return 1.0 - (model_error / naive_error)
        
    @classmethod
    def evaluate_all(cls, y_true: np.ndarray, y_pred: np.ndarray, y_naive: np.ndarray = None) -> Dict[str, float]:
        """
        Compute all metrics for a given forecast.
        """
        metrics = {
            "RMSE": cls.rmse(y_true, y_pred),
            "MAE": cls.mae(y_true, y_pred),
            "MAPE": cls.mape(y_true, y_pred),
            "wMAPE": cls.wmape(y_true, y_pred),
            "Bias": cls.bias(y_true, y_pred)
        }
        
        if y_naive is not None:
            naive_rmse = cls.rmse(y_true, y_naive)
            metrics["FVA (RMSE)"] = cls.forecast_value_added(naive_rmse, metrics["RMSE"])
            
        return metrics
