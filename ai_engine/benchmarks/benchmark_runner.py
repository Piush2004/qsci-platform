import json
import os
from datetime import datetime
from ai_engine.benchmarks.fairness import QuantumFairnessFramework
from ai_engine.benchmarks.metrics import BenchmarkMetrics

class BenchmarkRunner:
    """
    Executes and records benchmarks comparing Classical vs Quantum models.
    """
    def __init__(self, results_dir: str = "benchmarks/results"):
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
        
    def run_routing_benchmark(self, vrp_solver, qaoa_solver, distance_matrix, demands, capacities):
        """
        Compare Classical VRP (OR-Tools) vs QAOA.
        """
        print("Running VRP Benchmark: OR-Tools vs QAOA...")
        
        # 1. Run Classical
        import time
        start = time.time()
        classical_result = vrp_solver.solve(distance_matrix, demands, capacities)
        classical_time = (time.time() - start) * 1000
        
        # 2. Run Quantum
        start = time.time()
        quantum_result = qaoa_solver.solve(distance_matrix, len(capacities))
        quantum_wall_time = (time.time() - start) * 1000
        
        # 3. Apply Fairness Framework
        qpu_time = quantum_result.get("metrics", {}).get("qpu_time_ms", quantum_wall_time)
        effective_quantum_time = QuantumFairnessFramework.calculate_effective_quantum_time(
            qpu_time, len(distance_matrix), 1024
        )
        
        # 4. Compare
        classical_score = classical_result.get("total_distance", float('inf'))
        quantum_score = quantum_result.get("total_distance", float('inf'))
        
        # Note: Lower distance is better, so we invert the quality diff for the framework
        advantage = QuantumFairnessFramework.evaluate_advantage(
            classical_time, effective_quantum_time, quantum_score, classical_score
        )
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "problem": "CVRP",
            "size": len(distance_matrix),
            "classical": {
                "solver": "OR-Tools",
                "time_ms": classical_time,
                "score": classical_score
            },
            "quantum": {
                "solver": "QAOA",
                "wall_time_ms": quantum_wall_time,
                "effective_time_ms": effective_quantum_time,
                "score": quantum_score,
                "metrics": quantum_result.get("metrics", {})
            },
            "advantage": advantage
        }
        
        self._save_report("routing_benchmark", report)
        return report
        
    def _save_report(self, name: str, report: dict):
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"Benchmark report saved to {filepath}")
