"""Phase 3 core scaling experiment -- real execution, not a hand-typed
table. Run once; output captured into notebooks/05_routing_qubo.ipynb and
docs/PHASE_3_REPORT.md. Produces experiments/results/routing_results.json
and .csv.

Scope decisions made from REAL measured evidence (documented in
docs/PHASE_3_REPORT.md, not invented in advance):
- OR-Tools-on-QUBO and simulated annealing run the full N in
  {4,6,8,10,12,16} sweep -- neither has a qubit ceiling.
- QAOA runs reliably (statistics, 10 seeds) only at N=4 (8 qubits).
  Isolated diagnostics (outside this script, see docs/PHASE_3_REPORT.md
  section 19) measured N=5 (10 qubits) at 628.9s for a single run and
  N=6-with-K=2 (12 qubits) exceeding a 15+ minute budget without
  completing. This script's real N=6 derived instance needs 18 qubits
  (K=3 vehicles) -- worse than the already-timed-out 12-qubit case -- so
  QAOA is not attempted there; it is recorded PENDING with this reasoning,
  not silently skipped.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qsci_core.optimization.quantum.annealing_solver import BACKEND_LABEL as ANNEALING_LABEL
from qsci_core.optimization.quantum.annealing_solver import solve_qubo_with_annealing
from qsci_core.optimization.quantum.classical_qubo_solver import solve_qubo_with_ortools
from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.experiment import RoutingResult, save_results
from qsci_core.optimization.quantum.instance_builder import build_derived_instance
from qsci_core.optimization.quantum.qaoa_solver import solve_qubo_with_qaoa
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo

SIZES = [4, 6, 8, 10, 12, 16]
SOURCE_INSTANCE = "A-n32-k5"
PENALTY_MULTIPLIER = 2.0
N_STATISTICAL_SEEDS = 10


def run_ortools_and_annealing_sweep():
    results = []
    for n in SIZES:
        di = build_derived_instance(SOURCE_INSTANCE, n)
        t0 = time.perf_counter()
        qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=PENALTY_MULTIPLIER)
        qubo_time = time.perf_counter() - t0

        # OR-Tools on the QUBO
        t_start = time.perf_counter()
        ort = solve_qubo_with_ortools(qi, time_limit_seconds=30)
        decoded = decode_qubo_sample(ort.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord) if ort.sample else None
        e2e = time.perf_counter() - t_start
        results.append(RoutingResult(
            experiment_id=f"ortools_qubo_n{n}", dataset="cvrplib-derived", instance=di.instance_id,
            stops=n, vehicles=di.n_vehicles, capacity=di.capacity, seed=42, solver="or_tools_qubo",
            algorithm="CP-SAT (quadratic objective)", qaoa_depth=None, qubits=None, qubo_variables=qi.n_variables,
            circuit_depth=None, gate_count=None, shots=None, runtime_solver_seconds=ort.solve_time_seconds,
            runtime_end_to_end_seconds=qubo_time + e2e, objective_cost=decoded.total_cost if decoded and decoded.feasible else None,
            reference_cost=None, reference_type="UNKNOWN", optimality_gap_pct=None,
            feasible=decoded.feasible if decoded else False,
            feasibility_reason=decoded.feasibility_reason if decoded else "solver returned no sample",
            repair_used=False, status="LIVE", classification=ort.status,
        ))
        print(f"N={n} OR-Tools-QUBO: status={ort.status} feasible={decoded.feasible if decoded else False} cost={decoded.total_cost if decoded and decoded.feasible else None} time={ort.solve_time_seconds:.2f}s")

        # Simulated annealing -- statistical runs
        for seed in range(N_STATISTICAL_SEEDS):
            t_start = time.perf_counter()
            ann = solve_qubo_with_annealing(qi, num_reads=100, seed=seed)
            decoded = decode_qubo_sample(ann.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
            e2e = time.perf_counter() - t_start
            results.append(RoutingResult(
                experiment_id=f"annealing_n{n}_seed{seed}", dataset="cvrplib-derived", instance=di.instance_id,
                stops=n, vehicles=di.n_vehicles, capacity=di.capacity, seed=seed, solver="simulated_annealing",
                algorithm=ANNEALING_LABEL, qaoa_depth=None, qubits=None, qubo_variables=qi.n_variables,
                circuit_depth=None, gate_count=None, shots=None, runtime_solver_seconds=ann.solve_time_seconds,
                runtime_end_to_end_seconds=qubo_time + e2e, objective_cost=decoded.total_cost if decoded.feasible else None,
                reference_cost=None, reference_type="UNKNOWN", optimality_gap_pct=None,
                feasible=decoded.feasible, feasibility_reason=decoded.feasibility_reason,
                repair_used=False, status="RESEARCH", classification="FEASIBLE" if decoded.feasible else "INFEASIBLE",
            ))
        ann_costs = [r.objective_cost for r in results if r.experiment_id.startswith(f"annealing_n{n}_") and r.feasible]
        ann_feas = sum(1 for r in results if r.experiment_id.startswith(f"annealing_n{n}_") and r.feasible)
        print(f"N={n} Annealing: {ann_feas}/{N_STATISTICAL_SEEDS} feasible, "
              f"best={min(ann_costs) if ann_costs else None}, mean={np.mean(ann_costs) if ann_costs else None}")

    return results


def run_qaoa_at_n4():
    results = []
    n = 4
    di = build_derived_instance(SOURCE_INSTANCE, n)
    qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=PENALTY_MULTIPLIER)
    print(f"QAOA N={n}: qubo_variables={qi.n_variables}")

    for seed in range(N_STATISTICAL_SEEDS):
        t_start = time.perf_counter()
        res = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=20, shots=1024, seed=seed)
        decoded = decode_qubo_sample(res.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
        e2e = time.perf_counter() - t_start
        results.append(RoutingResult(
            experiment_id=f"qaoa_n{n}_seed{seed}", dataset="cvrplib-derived", instance=di.instance_id,
            stops=n, vehicles=di.n_vehicles, capacity=di.capacity, seed=seed, solver="qaoa",
            algorithm="QAOA p=1, COBYLA", qaoa_depth=1, qubits=res.metadata.n_qubits, qubo_variables=qi.n_variables,
            circuit_depth=res.metadata.circuit_depth, gate_count=res.metadata.gate_count_total, shots=res.metadata.shots,
            runtime_solver_seconds=res.solve_time_seconds, runtime_end_to_end_seconds=e2e,
            objective_cost=decoded.total_cost if decoded.feasible else None, reference_cost=None,
            reference_type="UNKNOWN", optimality_gap_pct=None, feasible=decoded.feasible,
            feasibility_reason=decoded.feasibility_reason, repair_used=False, status="RESEARCH",
            classification="FEASIBLE" if decoded.feasible else "INFEASIBLE",
        ))
        print(f"  seed={seed}: feasible={decoded.feasible} cost={decoded.total_cost if decoded.feasible else None} time={res.solve_time_seconds:.2f}s")

    return results


def run_penalty_sensitivity():
    results = []
    n = 4
    di = build_derived_instance(SOURCE_INSTANCE, n)
    print(f"Penalty sensitivity study, N={n}:")
    for mult in (1.0, 2.0, 5.0, 10.0):
        qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=mult)
        ann = solve_qubo_with_annealing(qi, num_reads=100, seed=42)
        decoded = decode_qubo_sample(ann.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
        print(f"  multiplier={mult}: penalty_visit={qi.penalty_visit:.1f} feasible={decoded.feasible} "
              f"cost={decoded.total_cost if decoded.feasible else None} loads={decoded.vehicle_loads}")
        results.append({
            "multiplier": mult, "penalty_visit": qi.penalty_visit, "penalty_capacity": qi.penalty_capacity,
            "feasible": decoded.feasible, "cost": decoded.total_cost, "feasibility_reason": decoded.feasibility_reason,
        })
    return results


if __name__ == "__main__":
    print("=== 1. OR-Tools-QUBO + Simulated Annealing scaling sweep ===")
    sweep_results = run_ortools_and_annealing_sweep()

    print("\n=== 2. QAOA at N=4 (10 seeds) ===")
    qaoa_results = run_qaoa_at_n4()

    print("\n=== 3. Penalty sensitivity study (N=4) ===")
    penalty_results = run_penalty_sensitivity()

    all_results = sweep_results + qaoa_results
    results_dir = Path(__file__).resolve().parents[1] / "experiments" / "results"
    save_results(all_results, results_dir / "routing_results.json", results_dir / "routing_results.csv")
    print(f"\nSaved {len(all_results)} results to {results_dir}")

    import json
    with open(results_dir / "routing_penalty_sensitivity.json", "w") as f:
        json.dump(penalty_results, f, indent=2, default=str)
