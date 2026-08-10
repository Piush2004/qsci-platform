from typing import Dict, Any

class ExecutiveAgent:
    """Generates holistic recommendations, summarizes business impact, and formats for Human-in-the-Loop review."""
    
    def generate_review_payload(self, forecast: Dict[str, Any], optimization: Dict[str, Any], 
                                rules: Dict[str, Any], financial: Dict[str, Any]) -> Dict[str, Any]:
        """Compiles the pipeline outputs into a single payload for the planner's dashboard."""
        
        # Determine suggested action
        action_required = rules.get("Prescriptive_Action", "Maintain Normal Operations")
        
        # Build the Human-in-the-Loop structure
        hitl_payload = {
            "status": "PENDING_REVIEW",
            "summary": f"Recommendation: {action_required}. Expected Savings: ${financial.get('Expected_Savings', 0)}",
            "confidence_score": financial.get("Recommendation_Confidence", "0%"),
            "risk_level": financial.get("Risk_Level", "Unknown"),
            "forecast_reliability": financial.get("Forecast_Reliability", "Unknown"),
            "data_context": {
                "forecasted_demand": forecast.get("avg_demand", 0),
                "suggested_eoq": optimization.get("Optimal_Order_Quantity_EOQ", 0),
                "safety_stock": optimization.get("Recommended_Safety_Stock", 0)
            },
            "actions_available": ["APPROVE", "REJECT", "MODIFY"]
        }
        
        return hitl_payload
