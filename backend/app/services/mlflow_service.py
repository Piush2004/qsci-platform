from ai_engine.mlflow_utils import (
    log_experiment,
    recommend_promotion,
    approve_promotion,
    get_production_model,
    get_all_runs,
    get_leaderboard
)

class MLFlowService:
    def log_experiment(self, name, params, metrics, tags=None):
        return log_experiment(name, params, metrics, tags)

    def recommend_promotion(self, run_id, target_stage):
        recommend_promotion(run_id, target_stage)

    def approve_promotion(self, run_id, approved_by):
        # The frontend defaults to 'Production' when approving
        approve_promotion(run_id, approved_by, "Production")
        
    def get_production_model(self):
        return get_production_model()

    def get_all_runs(self):
        return get_all_runs()

    def get_leaderboard(self):
        return get_leaderboard()
