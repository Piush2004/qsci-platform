import numpy as np
from typing import Dict, Any

class BusinessOptimizationEngine:
    """Applies Operations Research to predict optimal constraints (EOQ, Safety Stock)."""
    
    def calculate_eoq(self, annual_demand: float, order_cost: float, holding_cost_rate: float, unit_cost: float) -> float:
        """Economic Order Quantity (EOQ) = sqrt((2 * D * S) / H)"""
        holding_cost = holding_cost_rate * unit_cost
        if holding_cost == 0:
            return 0.0
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)
        return round(eoq, 2)
        
    def calculate_safety_stock(self, max_daily_demand: float, max_lead_time: float, avg_daily_demand: float, avg_lead_time: float) -> float:
        """Safety Stock = (Max Daily Demand * Max Lead Time) - (Avg Daily Demand * Avg Lead Time)"""
        safety_stock = (max_daily_demand * max_lead_time) - (avg_daily_demand * avg_lead_time)
        return max(0.0, round(safety_stock, 2))
        
    def optimize(self, forecast_data: Dict[str, Any], costs: Dict[str, float]) -> Dict[str, Any]:
        """Runs Prescriptive Analytics on forecasted demand."""
        avg_demand = forecast_data.get("avg_demand", 100)
        max_demand = avg_demand * 1.5
        
        eoq = self.calculate_eoq(
            annual_demand=avg_demand * 365,
            order_cost=costs.get("order_cost", 50),
            holding_cost_rate=costs.get("holding_cost_rate", 0.2),
            unit_cost=costs.get("unit_cost", 10)
        )
        
        safety_stock = self.calculate_safety_stock(
            max_daily_demand=max_demand,
            max_lead_time=costs.get("max_lead_time", 14),
            avg_daily_demand=avg_demand,
            avg_lead_time=costs.get("avg_lead_time", 7)
        )
        
        return {
            "Optimal_Order_Quantity_EOQ": eoq,
            "Recommended_Safety_Stock": safety_stock,
            "Reorder_Point": (avg_demand * costs.get("avg_lead_time", 7)) + safety_stock
        }
