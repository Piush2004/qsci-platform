from typing import Dict, Any

class ScenarioEngine:
    """
    Executes what-if scenarios by overriding base assumptions (demand, capacity, lead times)
    and re-running the optimization engines.
    """
    def __init__(self, ai_engine, optimization_engine):
        self.ai_engine = ai_engine
        self.optimization_engine = optimization_engine
        
    def simulate(self, base_state: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a scenario simulation.
        """
        # 1. Apply overrides to base state
        scenario_state = self._apply_overrides(base_state, parameters)
        
        # 2. Re-run forecasting (Mocked for speed in simulation)
        demand_uplift = parameters.get("demand_multiplier", 1.0)
        scenario_demand = scenario_state["expected_demand"] * demand_uplift
        
        # 3. Re-run optimization
        # E.g., re-run inventory optimizer with new demand
        stockout_cost = parameters.get("stockout_cost_multiplier", 1.0) * scenario_state.get("base_stockout_cost", 100)
        
        # We mock the optimization result for the simulation
        new_safety_stock = scenario_demand * 1.5 if demand_uplift > 1.2 else scenario_demand * 1.2
        
        # 4. Compare and return delta
        return {
            "scenario_name": parameters.get("name", "Custom Scenario"),
            "baseline": {
                "demand": base_state["expected_demand"],
                "safety_stock": base_state.get("safety_stock", 0),
                "total_cost": base_state.get("total_cost", 0)
            },
            "scenario_results": {
                "demand": scenario_demand,
                "safety_stock": new_safety_stock,
                "total_cost": scenario_state.get("total_cost", 0) * demand_uplift * 1.1
            },
            "deltas": {
                "demand_pct": (scenario_demand - base_state["expected_demand"]) / base_state["expected_demand"] * 100,
                "safety_stock_diff": new_safety_stock - base_state.get("safety_stock", 0)
            }
        }
        
    def _apply_overrides(self, base: dict, params: dict) -> dict:
        state = base.copy()
        if "supplier_capacity_reduction" in params:
            state["supplier_capacities"] = [c * (1 - params["supplier_capacity_reduction"]) for c in state.get("supplier_capacities", [])]
        return state
