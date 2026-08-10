import sys
import os
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ai_engine.data.dataset_loaders import DatasetManager
from ai_engine.data.ai_preparation import AIDataPreparation
from ai_engine.models.model_selection import AdaptiveModelSelectionEngine
from ai_engine.mlflow_utils import setup_mlflow

def run_benchmark():
    print("=== QSCI Benchmarking Pipeline ===")
    setup_mlflow()

    print("1. Loading Dataset...")
    dm = DatasetManager()
    # Let's use Walmart for regression task (Weekly_Sales)
    df = dm.load_walmart()
    
    # Optional: downsample for speed in this prototype
    if len(df) > 500:
        df = df.sample(500, random_state=42)

    print("2. Preparing Data...")
    prep = AIDataPreparation(df, target_col='Weekly_Sales', date_col='Date')
    df_prepared = prep.prepare_pipeline()

    print("3. Splitting Data...")
    # Sort by date for time-series split
    df_prepared = df_prepared.sort_values(by='Date')
    
    # Drop non-numeric for simple modeling
    features = df_prepared.drop(columns=['Weekly_Sales', 'Date', 'Store', 'Dept'])
    target = df_prepared['Weekly_Sales']
    
    # We need arrays for the models
    X = features.values
    y = target.values

    # Train/Test Split (80/20)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")

    print("4. Running Model Selection Engine...")
    mse = AdaptiveModelSelectionEngine(task_type='regression')
    results = mse.evaluate_models(X_train, y_train, X_test, y_test)
    
    print("\n=== Benchmark Results ===")
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    run_benchmark()
