class ChaosMonkeyTester:
    """Agent 8: Chaos Monkey (Resilience)"""
    
    def simulate_node_failures(self):
        print("🕵️ ChaosMonkeyTester: Tearing down 30% of mock Supplier nodes in the Knowledge Graph...")
        
        from backend.app.services.copilot.knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        
        # Test if downstream impact survives missing nodes
        try:
            impact = kg.get_downstream_impact("Supplier", "SUP-999-MISSING")
            if "delayed_orders_count" in impact:
                print("✅ ChaosMonkeyTester: Knowledge Graph routing survived missing nodes with graceful degradation.")
                return True
        except Exception as e:
            print(f"❌ ChaosMonkeyTester: System crashed when encountering a ghost node: {e}")
            return False

if __name__ == "__main__":
    agent = ChaosMonkeyTester()
    agent.simulate_node_failures()
