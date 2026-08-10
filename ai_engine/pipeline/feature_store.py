import pandas as pd
import numpy as np

class FeatureStore:
    """
    Mock feature store for AI engine pipeline.
    In a real-world scenario, this would interface with Feast, Hopsworks, or Tecton.
    """
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path
        self._cache = {}
        
    def get_historical_demand(self, sku: str, location: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical demand data with rolling features and lags.
        """
        # Create mock data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n_days = len(dates)
        
        # Base demand with seasonality and trend
        t = np.arange(n_days)
        base_demand = 100 + 2 * t + 50 * np.sin(2 * np.pi * t / 365) + 20 * np.sin(2 * np.pi * t / 7)
        noise = np.random.normal(0, 10, n_days)
        demand = np.maximum(0, base_demand + noise)
        
        df = pd.DataFrame({
            'date': dates,
            'sku': sku,
            'location': location,
            'demand': demand
        })
        
        return self._add_features(df)
        
    def _add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add standard supply chain features: lags, rolling stats, calendar features.
        """
        df = df.copy()
        df.set_index('date', inplace=True)
        
        # Calendar features
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        df['is_weekend'] = df.index.dayofweek.isin([5, 6]).astype(int)
        
        # Lags
        for lag in [1, 7, 14, 28]:
            df[f'demand_lag_{lag}'] = df['demand'].shift(lag)
            
        # Rolling stats
        for window in [7, 28]:
            df[f'demand_rolling_mean_{window}'] = df['demand'].shift(1).rolling(window=window).mean()
            df[f'demand_rolling_std_{window}'] = df['demand'].shift(1).rolling(window=window).std()
            
        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        return df

    def get_online_features(self, sku: str, location: str) -> dict:
        """
        Fetch low-latency features for online inference.
        """
        return {
            "sku": sku,
            "location": location,
            "demand_lag_1": np.random.uniform(50, 150),
            "demand_lag_7": np.random.uniform(50, 150),
            "demand_rolling_mean_7": np.random.uniform(80, 120),
            "is_weekend": 0
        }
