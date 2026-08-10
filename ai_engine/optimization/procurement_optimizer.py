import numpy as np

class ProcurementOptimizer:
    """
    Solves the Procurement Portfolio Optimization problem.
    (Markowitz Mean-Variance inspired formulation for supply chain).
    Classical SOTA baseline using Gurobi (mocked if not installed).
    """
    def __init__(self, risk_aversion: float = 1.0):
        self.risk_aversion = risk_aversion
        
    def solve(self, expected_costs: np.ndarray, risk_covariance: np.ndarray, 
              capacities: np.ndarray, total_demand: float):
        """
        Minimize: expected_costs^T * w + risk_aversion * w^T * risk_covariance * w
        Subject to: sum(w) == total_demand, 0 <= w <= capacities
        """
        # In a real enterprise system, this would use gurobipy or scipy.optimize.
        # Here we mock the result for the baseline.
        
        n_suppliers = len(expected_costs)
        
        try:
            from scipy.optimize import minimize
            
            def objective(w):
                return expected_costs.dot(w) + self.risk_aversion * w.dot(risk_covariance).dot(w)
                
            def constraint(w):
                return np.sum(w) - total_demand
                
            bounds = [(0, cap) for cap in capacities]
            cons = {'type': 'eq', 'fun': constraint}
            
            # Initial guess: evenly distribute
            w0 = np.full(n_suppliers, total_demand / n_suppliers)
            
            result = minimize(objective, w0, method='SLSQP', bounds=bounds, constraints=cons)
            
            if result.success:
                return {
                    "status": "Optimal",
                    "allocations": result.x.tolist(),
                    "total_cost": float(expected_costs.dot(result.x)),
                    "total_risk": float(result.x.dot(risk_covariance).dot(result.x))
                }
            else:
                return {"status": "Failed to converge"}
                
        except ImportError:
            # Simple fallback if scipy is not available
            w = np.zeros(n_suppliers)
            remaining_demand = total_demand
            
            # Greedy allocation by lowest cost
            sorted_indices = np.argsort(expected_costs)
            for idx in sorted_indices:
                alloc = min(remaining_demand, capacities[idx])
                w[idx] = alloc
                remaining_demand -= alloc
                if remaining_demand <= 0:
                    break
                    
            return {
                "status": "Heuristic (Scipy missing)",
                "allocations": w.tolist(),
                "total_cost": float(expected_costs.dot(w)),
                "total_risk": float(w.dot(risk_covariance).dot(w))
            }
