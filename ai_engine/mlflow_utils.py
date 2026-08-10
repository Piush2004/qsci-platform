import mlflow
import mlflow.sklearn
from datetime import datetime

def setup_mlflow(experiment_name='QSCI_Decision_Intelligence'):
    """Configure MLflow with separate experiments for Demand and Inventory."""
    mlflow.set_experiment(experiment_name)
    print(f"MLflow configured for experiment: {experiment_name}")

import re

def log_experiment(model_name: str, params: dict, metrics: dict, tags: dict = None) -> str:
    """Log a full experiment run. Returns run_id."""
    with mlflow.start_run(run_name=model_name) as run:
        mlflow.log_params(params)
        
        # separate metrics from model_obj
        clean_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                # MLflow only allows alphanumerics, underscores, dashes, periods, spaces, and slashes.
                safe_k = re.sub(r'[^a-zA-Z0-9_\-\.\/ ]', '', k).replace(' ', '_')
                clean_metrics[safe_k] = v
        mlflow.log_metrics(clean_metrics)
        
        default_tags = {'model_stage': 'Experiment', 'date': datetime.now().isoformat()}
        if tags:
            default_tags.update(tags)
        mlflow.set_tags(default_tags)
        
        return run.info.run_id

def recommend_promotion(run_id: str, target_stage: str):
    """Tag a run as recommended for promotion. Does NOT auto-deploy."""
    client = mlflow.tracking.MlflowClient()
    client.set_tag(run_id, "recommended_stage", target_stage)
    print(f"Run {run_id} recommended for promotion to {target_stage}. Awaiting human approval.")

def approve_promotion(run_id: str, approved_by: str, stage: str):
    """Human-approved promotion. Sets model_stage tag."""
    client = mlflow.tracking.MlflowClient()
    client.set_tag(run_id, "model_stage", stage)
    client.set_tag(run_id, "approved_by", approved_by)
    client.set_tag(run_id, "approval_date", datetime.now().isoformat())
    print(f"Run {run_id} promoted to {stage} by {approved_by}.")

def get_production_model() -> dict:
    """Get the current production-stage model info."""
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name('QSCI_Decision_Intelligence')
    if not experiment:
        return {}
        
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="tags.model_stage = 'Production'",
        order_by=["start_time DESC"],
        max_results=1
    )
    if runs:
        return runs[0].to_dictionary()
    return {}

def get_all_runs() -> list:
    """Get all experiment runs with full metrics for the Research Portal."""
    client = mlflow.tracking.MlflowClient()
    experiment = mlflow.get_experiment_by_name('QSCI_Decision_Intelligence')
    if not experiment:
        return []
    
    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    return [run.to_dictionary() for run in runs]

def get_leaderboard(task_type='regression') -> list:
    """Return models sorted by RMSE (regression) or accuracy (classification)."""
    runs = get_all_runs()
    
    if task_type == 'regression':
        sorted_runs = sorted(
            [r for r in runs if 'metrics.RMSE' in r.get('data', {}).get('metrics', {})],
            key=lambda x: x['data']['metrics']['RMSE']
        )
    else:
        sorted_runs = sorted(
            [r for r in runs if 'metrics.Accuracy' in r.get('data', {}).get('metrics', {})],
            key=lambda x: x['data']['metrics']['Accuracy'],
            reverse=True
        )
        
    return sorted_runs
