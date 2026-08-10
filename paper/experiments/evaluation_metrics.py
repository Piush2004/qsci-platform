import pandas as pd
import numpy as np
import hashlib
from datetime import datetime

def run_inventory_optimization(forecast_df):
    """
    (R,s,S) Policy Optimization.
    Calculates Inventory Savings and Financial Impact against the Naive baseline.
    """
    print("  -> Calculating Safety Stock and Expected Savings...")
    
    # Simple (R,s,S) proxy
    unit_holding_cost = 2.50
    unit_stockout_cost = 50.00
    
    metrics = []
    
    for sku in forecast_df['sku'].unique():
        sku_df = forecast_df[forecast_df['sku'] == sku]
        
        # Get Naive RMSE as baseline error
        naive_rmse = sku_df[sku_df['model'] == 'Naive']['rmse'].values[0]
        naive_safety_stock = 1.65 * naive_rmse # 95% service level
        naive_holding_cost = naive_safety_stock * unit_holding_cost
        
        for _, row in sku_df.iterrows():
            model_rmse = row['rmse']
            safety_stock = 1.65 * model_rmse
            holding_cost = safety_stock * unit_holding_cost
            savings = naive_holding_cost - holding_cost
            
            metrics.append({
                "sku": sku,
                "model": row['model'],
                "safety_stock": float(safety_stock),
                "holding_cost": float(holding_cost),
                "expected_savings_vs_naive": float(savings)
            })
            
    return pd.DataFrame(metrics)

def calculate_confidence(rmse, data_quality_score=0.95):
    """
    4-Factor Confidence Decomposition
    """
    # Inverse proportional to RMSE
    uncertainty_score = max(0.1, 1.0 - (rmse / 1000.0))
    consensus_score = 0.85
    backtest_score = max(0.1, 1.0 - (rmse / 800.0))
    
    final_confidence = (data_quality_score * 0.2) + (uncertainty_score * 0.4) + (consensus_score * 0.2) + (backtest_score * 0.2)
    return float(min(1.0, max(0.0, final_confidence)))

def simulate_hitl_approval(model_name, confidence_score):
    """
    Simulates the Human-In-The-Loop Workflow and writes to Audit Log.
    """
    action = "APPROVE" if confidence_score > 0.8 else "MODIFY"
    user = "SIMULATED_PLANNER_DECISION"
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    log_entry = f'{{"model": "{model_name}", "confidence": {confidence_score:.3f}, "action": "{action}", "user": "{user}", "timestamp": "{timestamp}"}}'
    audit_hash = hashlib.sha256(log_entry.encode()).hexdigest()
    
    return {
        "log_entry": log_entry,
        "audit_hash": audit_hash,
        "action": action
    }
