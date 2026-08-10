from typing import Dict, Any

class BusinessRulesEngine:
    """Evaluates non-ML business logic overrides and constraints."""
    
    def evaluate(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        inventory = current_state.get("current_inventory", 0)
        safety_stock = current_state.get("safety_stock", 0)
        supplier_delay = current_state.get("supplier_delay_days", 0)
        warehouse_capacity = current_state.get("warehouse_capacity_pct", 0)
        demand_spike = current_state.get("demand_spike_predicted", False)
        
        rules_triggered = []
        action = "Maintain Normal Operations"
        
        # Rule 1: High Risk Supplier Delay
        if inventory < safety_stock and supplier_delay > 5:
            rules_triggered.append("RULE_1: Critical Shortage & Supplier Delay")
            action = "EMERGENCY: Increase Reorder Quantity by 20% & Expedite Shipping"
            
        # Rule 2: Warehouse Capacity Overflow
        elif demand_spike and warehouse_capacity >= 95.0:
            rules_triggered.append("RULE_2: Demand Spike + Warehouse Full")
            action = "ACTION: Recommend Temporary 3PL Warehouse Allocation"
            
        # Rule 3: Excess Inventory
        elif inventory > (safety_stock * 3) and not demand_spike:
            rules_triggered.append("RULE_3: Excess Inventory Trapped")
            action = "ACTION: Halt Replenishment & Initiate Promotional Discount"
            
        return {
            "Rules_Triggered": rules_triggered,
            "Prescriptive_Action": action
        }
