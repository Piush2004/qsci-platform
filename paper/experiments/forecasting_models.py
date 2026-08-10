import time
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def wmape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true))

def bias(y_true, y_pred):
    return np.mean(y_pred - y_true)

def train_eval_classical(df, target_col='demand', forecast_horizon=14):
    """
    Trains Naive, Moving Average, and LightGBM models.
    (Chronos and TFT are skipped due to local compute constraints as per experimental parameters).
    """
    results = []
    
    for sku in df['sku'].unique():
        sku_df = df[df['sku'] == sku].copy()
        
        # Train/Test Split
        train = sku_df.iloc[:-forecast_horizon]
        test = sku_df.iloc[-forecast_horizon:]
        
        y_train = train[target_col].values
        y_test = test[target_col].values
        
        features = [col for col in sku_df.columns if col not in ['date', 'sku', 'demand']]
        X_train = train[features].values
        X_test = test[features].values
        
        # 1. Naive Baseline (Last observed value)
        start_time = time.time()
        naive_pred = np.full(len(y_test), y_train[-1])
        naive_time = time.time() - start_time
        
        results.append(compile_metrics(sku, "Naive", y_test, naive_pred, naive_time, 0))
        
        # 2. Moving Average (Window=3)
        start_time = time.time()
        ma_pred = np.full(len(y_test), np.mean(y_train[-3:]))
        ma_time = time.time() - start_time
        
        results.append(compile_metrics(sku, "MovingAverage", y_test, ma_pred, ma_time, 0))
        
        # 3. LightGBM
        train_start = time.time()
        lgbm = LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
        lgbm.fit(X_train, y_train)
        train_time = time.time() - train_start
        
        inf_start = time.time()
        lgbm_pred = lgbm.predict(X_test)
        inf_time = time.time() - inf_start
        
        results.append(compile_metrics(sku, "LightGBM", y_test, lgbm_pred, train_time, inf_time))
        
    return pd.DataFrame(results)

def compile_metrics(sku, model_name, y_true, y_pred, train_time, inf_time, quantum_overhead=0.0):
    return {
        "sku": sku,
        "model": model_name,
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "wmape": float(wmape(y_true, y_pred)),
        "bias": float(bias(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
        "train_time_sec": train_time,
        "inference_time_sec": inf_time,
        "quantum_overhead_sec": quantum_overhead,
        "total_time_sec": train_time + inf_time + quantum_overhead
    }
