import pandas as pd
import numpy as np
from ai_engine.models.classical_baselines import (
    XGBoostWrapper, RandomForestWrapper, ARIMAWrapper, ProphetWrapper, LSTMWrapper
)
from ai_engine.quantum.qml_models import QuantumRegressionModels, QuantumClassificationModels
from ai_engine.mlflow_utils import log_experiment, recommend_promotion

class AdaptiveModelSelectionEngine:
    def __init__(self, task_type='regression'):
        self.task_type = task_type
        
    def evaluate_models(self, X_train, y_train, X_test, y_test):
        results = {}
        best_metric = float('inf') if self.task_type == 'regression' else -float('inf')
        best_model_name = None
        best_run_id = None
        
        models_to_test = {}
        
        if self.task_type == 'regression':
            models_to_test = {
                'XGBoost': XGBoostWrapper(task_type='regression'),
                'RandomForest': RandomForestWrapper(task_type='regression'),
                'ARIMA': ARIMAWrapper(),
                'Prophet': ProphetWrapper(),
                'LSTM': LSTMWrapper()
            }
            metric_to_optimize = 'RMSE'
        else:
            models_to_test = {
                'XGBoost': XGBoostWrapper(task_type='classification'),
                'RandomForest': RandomForestWrapper(task_type='classification')
            }
            metric_to_optimize = 'Accuracy'

        for name, model in models_to_test.items():
            print(f"Evaluating {name}...")
            metrics = model.evaluate(X_train, y_train, X_test, y_test)
            results[name] = metrics
            
            run_id = log_experiment(name, params={'task_type': self.task_type}, metrics=metrics, tags={'model_type': 'classical'})
            
            if self.task_type == 'regression':
                if metrics[metric_to_optimize] < best_metric:
                    best_metric = metrics[metric_to_optimize]
                    best_model_name = name
                    best_run_id = run_id
            else:
                if metrics[metric_to_optimize] > best_metric:
                    best_metric = metrics[metric_to_optimize]
                    best_model_name = name
                    best_run_id = run_id

        # Evaluate Quantum Models
        print("Evaluating Quantum Models...")
        if self.task_type == 'regression':
            q_models = QuantumRegressionModels()
            q_metrics = q_models.train_and_evaluate(X_train, y_train, X_test, y_test)
            if q_metrics:
                results['VQR'] = q_metrics
                q_run_id = log_experiment('VQR', params={'task_type': 'regression', 'backend': 'aer_simulator'}, metrics=q_metrics, tags={'model_type': 'quantum'})
                
                if q_metrics['RMSE'] < best_metric:
                    best_metric = q_metrics['RMSE']
                    best_model_name = 'VQR'
                    best_run_id = q_run_id
        else:
            q_models = QuantumClassificationModels()
            
            # VQC
            q_metrics_vqc = q_models.train_and_evaluate(X_train, y_train, X_test, y_test, use_vqc=True)
            if q_metrics_vqc:
                results['VQC'] = q_metrics_vqc
                q_run_id_vqc = log_experiment('VQC', params={'task_type': 'classification'}, metrics=q_metrics_vqc, tags={'model_type': 'quantum'})
                if q_metrics_vqc['Accuracy'] > best_metric:
                    best_metric = q_metrics_vqc['Accuracy']
                    best_model_name = 'VQC'
                    best_run_id = q_run_id_vqc
                    
            # QSVC
            q_metrics_qsvc = q_models.train_and_evaluate(X_train, y_train, X_test, y_test, use_vqc=False)
            if q_metrics_qsvc:
                results['QSVC'] = q_metrics_qsvc
                q_run_id_qsvc = log_experiment('QSVC', params={'task_type': 'classification'}, metrics=q_metrics_qsvc, tags={'model_type': 'quantum'})
                if q_metrics_qsvc['Accuracy'] > best_metric:
                    best_metric = q_metrics_qsvc['Accuracy']
                    best_model_name = 'QSVC'
                    best_run_id = q_run_id_qsvc
        
        if best_run_id:
            print(f"Recommending {best_model_name} for Candidate stage.")
            recommend_promotion(best_run_id, 'Candidate')
            
        return results
