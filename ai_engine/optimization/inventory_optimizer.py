import numpy as np
import pandas as pd
from typing import Dict, Any

class InventoryOptimizer:
    """
    Calculates safety stock and (R, s, S) inventory policies.
    Utilizes probabilistic forecasts (p10, p50, p90) from TFT or similar models.
    """
    def __init__(self, holding_cost_rate: float = 0.2, stockout_cost_rate: float = 0.8):
        self.holding_cost_rate = holding_cost_rate
        self.stockout_cost_rate = stockout_cost_rate

    def calculate_policy(self, forecast_df: pd.DataFrame, current_inventory: float, 
                         lead_time_days: int = 7, review_period_days: int = 7,
                         target_service_level: float = 0.95) -> Dict[str, Any]:
        """
        Calculate continuous review (s, S) or periodic review (R, s, S) policy.
        """
        if len(forecast_df) == 0:
            return {}

        # The protection interval is Lead Time (L) + Review Period (R)
        protection_interval = lead_time_days + review_period_days
        
        # Get demand forecast for the protection interval
        future_demand = forecast_df.head(protection_interval)
        
        # Mean expected demand over interval
        expected_demand = future_demand['p50'].sum()
        
        # Demand uncertainty (simplified assumption: normally distributed errors based on quantiles)
        # Approximate standard deviation from p90 and p50 (Z = 1.28 for 90th percentile)
        sigma_demand = (future_demand['p90'].sum() - expected_demand) / 1.28 if 'p90' in future_demand.columns else expected_demand * 0.2
        
        # Service factor (Z-score for target service level)
        from scipy.stats import norm
        try:
            z_score = norm.ppf(target_service_level)
        except ImportError:
            z_score = 1.645 # 95% default
            
        # Safety Stock
        safety_stock = z_score * sigma_demand
        
        # Reorder Point (s)
        reorder_point = expected_demand + safety_stock
        
        # Order-up-to Level (S) - simplified approach
        # S = s + Q (Economic Order Quantity proxy)
        order_up_to_level = reorder_point + (expected_demand * (review_period_days / protection_interval))
        
        # Recommended action
        recommended_order_quantity = 0
        if current_inventory <= reorder_point:
            recommended_order_quantity = max(0, order_up_to_level - current_inventory)
            
        return {
            "current_inventory": current_inventory,
            "expected_demand_L_R": expected_demand,
            "safety_stock": safety_stock,
            "reorder_point_s": reorder_point,
            "order_up_to_level_S": order_up_to_level,
            "recommended_order_quantity": recommended_order_quantity,
            "stockout_risk": "HIGH" if current_inventory < safety_stock else "LOW"
        }
