import os
import json
from datetime import datetime
import pandas as pd
from ai_engine.pipeline.feature_store import FeatureStore
from ai_engine.models.lightgbm_forecaster import LightGBMForecaster
from ai_engine.models.tft_forecaster import TFTForecaster
from ai_engine.pipeline.evaluate import EvaluationMetrics

class TrainingOrchestrator:
    """
    Orchestrates the training of classical AI models and tracks experiments.
    In production, this would use MLflow or similar for experiment tracking.
    """
    def __init__(self, data_path: str = None, experiment_dir: str = "experiments"):
        self.feature_store = FeatureStore(data_path=data_path)
        self.experiment_dir = experiment_dir
        os.makedirs(self.experiment_dir, exist_ok=True)
        
    def train_baseline_models(self, sku: str, location: str, start_date: str, end_date: str):
        """
        Train LightGBM and TFT baselines for a given SKU and location.
        """
        print(f"Fetching historical demand for {sku} at {location}...")
        df = self.feature_store.get_historical_demand(sku, location, start_date, end_date)
        
        # Train-Test Split (last 30 days for testing)
        train_df = df[:-30]
        test_df = df[-30:]
        
        results = {}
        
        # 1. Train LightGBM
        print("Training LightGBM Forecaster...")
        lgb = LightGBMForecaster()
        try:
            lgb.fit(train_df)
            lgb_preds = lgb.predict(test_df)
            lgb_metrics = EvaluationMetrics.evaluate_all(test_df['demand'].values, lgb_preds)
            results['LightGBM'] = lgb_metrics
            print(f"LightGBM metrics: {lgb_metrics}")
        except Exception as e:
            print(f"LightGBM training failed: {e}")
            
        # 2. Train TFT
        print("Training TFT Forecaster...")
        tft = TFTForecaster()
        try:
            tft.fit(train_df)
            tft_preds_df = tft.predict(test_df)
            tft_metrics = EvaluationMetrics.evaluate_all(test_df['demand'].values, tft_preds_df['p50'].values)
            results['TFT'] = tft_metrics
            print(f"TFT metrics: {tft_metrics}")
        except Exception as e:
            print(f"TFT training failed: {e}")
            
        # 3. Naive Baseline (Mean of train data)
        naive_pred = np.full(len(test_df), train_df['demand'].mean())
        naive_metrics = EvaluationMetrics.evaluate_all(test_df['demand'].values, naive_pred)
        results['Naive'] = naive_metrics
        
        # Calculate FVA against Naive
        if 'LightGBM' in results:
            results['LightGBM']['FVA'] = EvaluationMetrics.forecast_value_added(naive_metrics['RMSE'], results['LightGBM']['RMSE'])
        if 'TFT' in results:
            results['TFT']['FVA'] = EvaluationMetrics.forecast_value_added(naive_metrics['RMSE'], results['TFT']['RMSE'])
            
        # Save experiment
        self._save_experiment(sku, location, results)
        
        return results
        
    def _save_experiment(self, sku: str, location: str, results: dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_id = f"{sku}_{location}_{timestamp}"
        exp_file = os.path.join(self.experiment_dir, f"{exp_id}.json")
        
        with open(exp_file, 'w') as f:
            json.dump({
                "sku": sku,
                "location": location,
                "timestamp": timestamp,
                "metrics": results
            }, f, indent=4)
        print(f"Experiment saved to {exp_file}")
