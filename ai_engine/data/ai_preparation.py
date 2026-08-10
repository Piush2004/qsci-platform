import pandas as pd
from sklearn.preprocessing import StandardScaler

class AIDataPreparation:
    """
    Automatic preprocessing, scaling, time-series lag features, 
    and seasonality extraction for predictive models.
    """
    def __init__(self, df: pd.DataFrame, target_col: str, date_col: str = None):
        self.df = df.copy()
        self.target_col = target_col
        self.date_col = date_col
        self.scaler = StandardScaler()
        
    def create_lag_features(self, lags=[1, 7, 14, 28]):
        """Generates historical lag features for time-series forecasting."""
        for lag in lags:
            self.df[f"lag_{lag}"] = self.df[self.target_col].shift(lag)
        self.df.dropna(inplace=True)
        return self.df
        
    def extract_seasonality(self):
        """Extracts day, month, year, and weekday features if date_col exists."""
        if self.date_col and pd.api.types.is_datetime64_any_dtype(self.df[self.date_col]):
            self.df['day'] = self.df[self.date_col].dt.day
            self.df['month'] = self.df[self.date_col].dt.month
            self.df['year'] = self.df[self.date_col].dt.year
            self.df['dayofweek'] = self.df[self.date_col].dt.dayofweek
            self.df['is_weekend'] = self.df['dayofweek'].isin([5, 6]).astype(int)
        return self.df
        
    def scale_numerical_features(self, exclude_cols=None):
        """Standardizes numerical features for model ingestion (especially important for Quantum & Neural Nets)."""
        exclude_cols = exclude_cols or []
        exclude_cols.append(self.target_col)
        
        num_cols = self.df.select_dtypes(include=['number']).columns
        cols_to_scale = [c for c in num_cols if c not in exclude_cols]
        
        if cols_to_scale:
            self.df[cols_to_scale] = self.scaler.fit_transform(self.df[cols_to_scale])
            
        return self.df

    def prepare_pipeline(self):
        """Runs the full preparation pipeline."""
        if self.date_col and not pd.api.types.is_datetime64_any_dtype(self.df[self.date_col]):
             self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        
        self.extract_seasonality()
        self.create_lag_features()
        self.scale_numerical_features(exclude_cols=['day', 'month', 'year', 'dayofweek', 'is_weekend'])
        
        return self.df
