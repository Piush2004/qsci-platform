from typing import Dict, Any

class BusinessValueAssessmentEngine:
    """Calculates financial impact, cost savings, and recommendation confidence levels."""
    
    def assess_impact(self, optimization_output: Dict[str, Any], rule_output: Dict[str, Any], forecast_error: float) -> Dict[str, Any]:
        # Basic business logic to calculate costs based on proposed EOQ
        eoq = optimization_output.get("Optimal_Order_Quantity_EOQ", 1000)
        unit_cost = 15.0 # Mock unit cost
        holding_rate = 0.2
        
        holding_cost = (eoq / 2) * (unit_cost * holding_rate)
        
        # Determine risk level based on triggered rules
        risk_level = "Low"
        confidence = 95.0 - (forecast_error * 100) # Simple heuristic for confidence
        
        if "EMERGENCY" in rule_output.get("Prescriptive_Action", ""):
            risk_level = "High"
            confidence -= 10.0 # Less confident during chaotic events
        elif "ACTION" in rule_output.get("Prescriptive_Action", ""):
            risk_level = "Medium"
            
        expected_savings = 0.0
        if eoq > 0:
            # Assume optimization saves 12% over naive heuristic
            expected_savings = (eoq * unit_cost) * 0.12
            
        return {
            "Estimated_Holding_Cost": round(holding_cost, 2),
            "Expected_Savings": round(expected_savings, 2),
            "Risk_Level": risk_level,
            "Recommendation_Confidence": f"{max(0.0, min(100.0, round(confidence, 1)))}%",
            "Forecast_Reliability": "High" if forecast_error < 0.15 else "Moderate"
        }
