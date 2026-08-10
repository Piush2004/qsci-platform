class CopilotAdversary:
    """Agent 11: Copilot Adversary (LLM Hallucinations)"""
    
    def test_hallucination_guardrails(self):
        print("🕵️ CopilotAdversary: Prompting the LLM Summarizer to invent demand numbers...")
        
        from backend.app.services.copilot.llm_summarizer import LLMSummarizer
        summarizer = LLMSummarizer()
        
        # Mock forecast data without any numbers
        forecast = {"status": "success"}
        confidence = {"score_0_to_100": 85}
        
        summary = summarizer.summarize_forecast("SKU-999", "WH-01", forecast, confidence)
        
        # The LLM summarizer is hardcoded/prompted to only use provided data.
        # If expected_demand is 0 because it's missing, it should say 0, not invent "5000"
        if "0 units" in summary:
            print("✅ CopilotAdversary: LLM Summarizer properly passed through deterministic zero, refused to hallucinate.")
            return True
        else:
            print(f"❌ CopilotAdversary: LLM hallucinated data! Output: {summary}")
            return False

if __name__ == "__main__":
    agent = CopilotAdversary()
    agent.test_hallucination_guardrails()
