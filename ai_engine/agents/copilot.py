class SupplyChainCopilot:
    """Chat interface powered by LLM (Gemini 2.5 Pro / Ollama) for supply chain queries."""
    
    def __init__(self, use_local_ollama=False):
        self.use_local_ollama = use_local_ollama
        self.provider = "Ollama (Local)" if use_local_ollama else "Gemini 2.5 Pro (Cloud)"
        print(f"Initialized Supply Chain Copilot using {self.provider}")
        
    def ask(self, query: str, context: dict) -> str:
        """
        Simulates an LLM query using the context (Knowledge Graph + current pipeline state).
        In a real deployment, this would format a prompt and call the Gemini API or local Ollama instance.
        """
        prompt = f"Given the current supply chain state: {context}, answer the user's query: {query}"
        
        # Mock LLM Response logic based on keyword matching for the prototype
        query_lower = query.lower()
        if "warehouse" in query_lower and "inventory" in query_lower:
            return "Based on the recent risk analysis, Warehouse B in California is projected to drop below safety stock in 4 days due to a supplier delay. I recommend reallocating 500 units from the Texas Distribution Center."
        elif "quantum" in query_lower:
            return "The Qiskit Variational Quantum Regressor (VQR) achieved a 5% improvement in MAPE over the XGBoost baseline during the last high-volatility event. However, classical models are still faster for inference."
        elif "cost" in query_lower or "savings" in query_lower:
            return f"Implementing the current EOQ optimization plan will save an estimated ${context.get('Expected_Savings', '12,500')} in holding costs this quarter."
        else:
            return "I have analyzed the supply chain parameters. Please review the Executive Dashboard for the latest Human-in-the-Loop pending actions."
