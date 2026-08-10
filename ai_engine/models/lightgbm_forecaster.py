import pandas as pd
import numpy as np
try:
    import lightgbm as lgb
except ImportError:
    print("LightGBM not installed. Mocking lgb.")
    lgb = None

class LightGBMForecaster:
    """
    LightGBM-based demand forecaster (Classical SOTA for tabular time-series).
    Used as the classical baseline against Quantum algorithms.
    """
    def __init__(self, **kwargs):
        self.params = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'learning_rate': 0.05,
            'num_leaves': 31,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        self.params.update(kwargs)
        self.model = None
        self.features = None

    def fit(self, df: pd.DataFrame, target_col: str = 'demand', categorical_features: list = None):
        """
        Train the LightGBM model.
        """
        if lgb is None:
            print("LightGBM missing, skipping fit.")
            return

        self.features = [col for col in df.columns if col not in ['date', 'sku', 'location', target_col]]
        
        X = df[self.features]
        y = df[target_col]
        
        train_data = lgb.Dataset(X, label=y, categorical_feature=categorical_features if categorical_features else 'auto')
        
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=100
        )
        
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict demand.
        """
        if lgb is None:
            return np.random.uniform(50, 150, size=len(df))
            
        if self.model is None:
            raise ValueError("Model is not trained yet.")
            
        X = df[self.features]
        return self.model.predict(X)
        
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Return global feature importance (split and gain).
        """
        if self.model is None or lgb is None:
            return pd.DataFrame()
            
        importance_split = self.model.feature_importance(importance_type='split')
        importance_gain = self.model.feature_importance(importance_type='gain')
        
        df = pd.DataFrame({
            'feature': self.features,
            'importance_split': importance_split,
            'importance_gain': importance_gain
        }).sort_values('importance_gain', ascending=False)
        
        return df
