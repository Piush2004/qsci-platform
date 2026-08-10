import os
import json
import pandas as pd
from data_loader import load_real_data, engineer_features
from forecasting_models import train_eval_classical
from quantum_models import run_quantum_models
from evaluation_metrics import run_inventory_optimization, calculate_confidence, simulate_hitl_approval
from plot_generator import generate_all_figures

EXPERIMENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(EXPERIMENT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_end_to_end_pipeline():
    print("==================================================")
    print("QSCI Phase 8: Final Research Execution Pipeline")
    print("==================================================")
    
    # 1. REAL DATA
    print("[1/14] Loading Real Dataset...")
    df, meta = load_real_data()
    
    config = {
        "git_commit_sha": "local-experiment-run", 
        "python_version": "3.10",
        "random_seeds": [42],
        "hardware": "Local CPU / Qiskit Aer",
        "qiskit_version": "1.0.2",
        "dataset_metadata": meta,
        "forecast_horizon": 14,
        "test_period": 14
    }
    
    with open(os.path.join(RESULTS_DIR, "EXPERIMENT_CONFIG.json"), "w") as f:
        json.dump(config, f, indent=2)
        
    # 2 & 3. DATA QUALITY & FEATURE ENGINEERING
    print("[2/14 & 3/14] Validating Data Quality and Engineering Features...")
    df_feat = engineer_features(df)
    
    # 4. CLASSICAL TRACK
    print("[4/14] Executing Classical Models (Naive, MA, LightGBM)...")
    classical_results = train_eval_classical(df_feat, forecast_horizon=config["forecast_horizon"])
    
    # 5. QUANTUM TRACK
    print("[5/14] Executing Quantum Models (VQR Ideal & Noisy)...")
    quantum_results = run_quantum_models(df_feat, forecast_horizon=config["forecast_horizon"])
    
    # Combine results
    all_results = pd.concat([classical_results, quantum_results], ignore_index=True)
    all_results.to_csv(os.path.join(RESULTS_DIR, "benchmark.csv"), index=False)
    
    # 6 & 7. FAIR BENCHMARK & STATISTICAL EVALUATION
    print("[6/14 & 7/14] Calculating Fair Benchmarks (with QRAM overhead)...")
    # Done via compile_metrics inside models.
    
    # 8 & 9. INVENTORY OPTIMIZATION & FINANCIAL IMPACT
    print("[8/14 & 9/14] Running Inventory Optimization & Calculating Financial Impact...")
    inventory_df = run_inventory_optimization(all_results)
    inventory_df.to_csv(os.path.join(RESULTS_DIR, "business_metrics.csv"), index=False)
    
    # 10, 11, 12. CONFIDENCE, RECOMMENDATION, HITL AUDIT
    print("[10/14 - 12/14] Confidence Decomposition & HITL Workflow...")
    audit_logs = []
    for _, row in all_results.iterrows():
        conf = calculate_confidence(row['rmse'])
        audit = simulate_hitl_approval(row['model'], conf)
        audit_logs.append(audit)
        
    with open(os.path.join(RESULTS_DIR, "audit_results.json"), "w") as f:
        json.dump(audit_logs, f, indent=2)
    
    # 13 & 14. FIGURES & CONCLUSION
    print("[13/14 & 14/14] Generating Publication-Quality Figures & Outputs...")
    generate_all_figures(all_results, inventory_df, RESULTS_DIR)
    
    print("==================================================")
    print("PIPELINE COMPLETE. Results saved to paper/experiments/results/")
    print("==================================================")

if __name__ == "__main__":
    run_end_to_end_pipeline()
