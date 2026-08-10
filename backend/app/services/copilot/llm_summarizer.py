import json

class LLMSummarizer:
    """
    Wraps deterministic results from the AI/Optimization engines into natural language.
    Crucially: The LLM NEVER invents numbers or predictions. It only formats the context.
    """
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        self.model_name = model_name
        
    def summarize_forecast(self, sku: str, location: str, forecast_data: dict, confidence: dict) -> str:
        """
        Summarize a demand forecast.
        """
        # In production, this would call the Vertex AI / Gemini API with strict system prompts
        # "You are a Supply Chain Copilot. Do NOT hallucinate data. Summarize the provided JSON."
        
        expected_demand = forecast_data.get('expected_demand', 0)
        p10 = forecast_data.get('p10', 0)
        p90 = forecast_data.get('p90', 0)
        
        conf_score = confidence.get('score_0_to_100', 0)
        
        return (f"The forecasted demand for {sku} at {location} is **{expected_demand:,.0f} units** "
                f"(ranging between {p10:,.0f} and {p90:,.0f}). "
                f"The model confidence is **{conf_score}%**.")
                
    def summarize_graph_impact(self, graph_data: dict) -> str:
        """
        Summarize a knowledge graph impact analysis.
        """
        source = graph_data.get("source_node", {}).get("id", "Unknown")
        revenue_risk = graph_data.get("impacted_revenue_at_risk", 0)
        alts = graph_data.get("alternative_suppliers", [])
        
        response = (f"A disruption at {source} puts **${revenue_risk:,.2f}** of revenue at risk. "
                    f"It impacts {len(graph_data.get('impacted_products', []))} products. ")
                    
        if alts:
            response += f"Recommended alternative suppliers to mitigate this risk: {', '.join(alts)}."
            
        return response
