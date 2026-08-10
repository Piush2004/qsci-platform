import os
from mlflow import set_tracking_uri, set_experiment, autolog

def configure_mlflow(experiment_name: str = "qsci-demand-forecasting"):
    """
    Configures MLflow tracking server for QSCI production models.
    """
    # In production, this would point to a managed MLflow server (e.g., Databricks or GCP)
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    
    set_tracking_uri(tracking_uri)
    set_experiment(experiment_name)
    
    # Auto-log parameters, metrics, and models for LightGBM/XGBoost/Sklearn
    autolog()
    
    print(f"MLflow initialized. Tracking URI: {tracking_uri}, Experiment: {experiment_name}")

if __name__ == "__main__":
    configure_mlflow()
