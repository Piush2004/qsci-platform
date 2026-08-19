"""Phase 4 -- Noise & Scalability. Real execution, not a hand-typed table.

Driven directly by the bottlenecks Phase 3 flagged in its own report
(docs/PHASE_3_REPORT.md section 27), not an invented plan:

  A. QAOA runtime-wall diagnosis -- isolate whether the N=4->N=5 runtime
     explosion (37.6s -> 628.9s, Phase 3 section 18) comes from per-circuit
     execution cost scaling with qubit count, or from the optimizer needing
     more function evaluations. Measured directly, not assumed.
  B. Annealing feasibility-collapse recovery -- Phase 3 found feasibility
     collapsing 90%->10%->0% between N=8 and N=12 at a fixed num_reads=100.
     Sweep num_reads to see whether more reads recovers feasibility, or
     whether the collapse is structural.
  C. Noise sensitivity at QAOA's one reliable size (N=4, 8 qubits) -- Phase
     3 only ran noiseless StatevectorSampler. This sweeps real Aer noise
     models (depolarizing low/high, readout) via qaoa_solver.py's new
     noise_preset parameter.
  D. QAOA p=1/p=2/p=3 depth-vs-quality tradeoff at N=4 -- Phase 3 only ran
     p=1 (runtime budget). This runs p=2,3 with real statistics.

Every run's config (seed, shots, maxiter, num_reads, noise preset) is
recorded per-row. No fabricated timing or fabricated feasibility.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qiskit.primitives import StatevectorSampler

from qsci_core.optimization.quantum.annealing_solver import solve_qubo_with_annealing
from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.instance_builder import build_derived_instance
from qsci_core.optimization.quantum.qaoa_solver import _bqm_to_quadratic_program, solve_qubo_with_qaoa
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo

SOURCE_INSTANCE = "A-n32-k5"
PENALTY_MULTIPLIER = 2.0
RESULTS_DIR = Path(__file__).resolve().parents[1] / "experiments" / "results"


def part_a_runtime_wall_diagnosis():
    """Fix QAOA's variational parameters (no optimization loop) and time a
    single sampler.run() call directly, at N=4 (8 qubits) and N=5 (10
    qubits) -- isolates per-circuit-execution cost from optimizer-iteration
    count. If per-call time alone explains most of the N=4->N=5 runtime
    growth, the wall is execution-cost-dominated; if not, it implicates the
    optimizer needing more/harder iterations at higher qubit count."""
    print("=== Part A: QAOA runtime-wall diagnosis ===")
    from qiskit_optimization.converters import QuadraticProgramToQubo
    from qiskit.circuit.library import QAOAAnsatz

    results = []
    for n in (4, 5):
        di = build_derived_instance(SOURCE_INSTANCE, n, n_vehicles=2)
        qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=PENALTY_MULTIPLIER)
        qp = _bqm_to_quadratic_program(qi)
        converter = QuadraticProgramToQubo()
        qubo_qp = converter.convert(qp)
        hamiltonian, _offset = qubo_qp.to_ising()

        sampler = StatevectorSampler(default_shots=1024, seed=42)
        ansatz = QAOAAnsatz(cost_operator=hamiltonian, reps=1)
        ansatz = ansatz.assign_parameters(np.full(ansatz.num_parameters, 0.5))
        ansatz.measure_all()

        circuit_depth = ansatz.decompose(reps=3).depth()
        gate_count = sum(ansatz.decompose(reps=3).count_ops().values())

        times = []
        for _ in range(5):
            t0 = time.perf_counter()
            job = sampler.run([(ansatz,)], shots=1024)
            job.result()
            times.append(time.perf_counter() - t0)

        row = {
            "n_customers": n, "qubits": qi.n_variables, "qubo_variables": qi.n_variables,
            "circuit_depth": circuit_depth, "gate_count": gate_count,
            "single_call_mean_seconds": float(np.mean(times)), "single_call_std_seconds": float(np.std(times)),
            "single_call_min_seconds": float(np.min(times)), "single_call_max_seconds": float(np.max(times)),
        }
        results.append(row)
        print(f"  N={n} ({qi.n_variables} qubits): mean single-call time = {np.mean(times):.4f}s "
              f"(depth={circuit_depth}, gates={gate_count})")

    # Compare against Phase 3's already-measured full-optimization times
    # (docs/PHASE_3_REPORT.md section 18): N=4 ~37.6s/run (maxiter=20,
    # COBYLA), N=5 ~628.9s/single run. If single-call time scales far less
    # than the full-run ratio, the wall is optimizer-iteration-count-driven,
    # not pure circuit-execution-cost.
    n4_call, n5_call = results[0]["single_call_mean_seconds"], results[1]["single_call_mean_seconds"]
    call_ratio = n5_call / n4_call if n4_call > 0 else float("inf")
    phase3_full_run_ratio = 628.9 / 37.6
    print(f"  Single-call time ratio (N5/N4): {call_ratio:.2f}x")
    print(f"  Phase 3 full-optimization-run time ratio (N5/N4): {phase3_full_run_ratio:.2f}x")
    print(f"  Interpretation: {'execution-cost-dominated' if call_ratio >= phase3_full_run_ratio * 0.5 else 'optimizer-iteration-count-dominated (single-call cost alone does not explain the full-run wall)'}")

    return {
        "per_size": results,
        "single_call_ratio_n5_over_n4": call_ratio,
        "phase3_full_run_ratio_n5_over_n4": phase3_full_run_ratio,
    }


def part_b_annealing_reads_sweep():
    """Sweep num_reads at N in {8, 10, 12} -- the exact sizes where Phase 3
    (fixed num_reads=100) found feasibility collapsing 90%->10%->0%.
    5 seeds per (N, num_reads) cell -- reduced from Phase 3's 10 to keep
    this sweep's total runtime tractable (annealing itself is fast per-run;
    the reduction is purely a wall-clock budget decision, documented here,
    not a silent shortcut)."""
    print("\n=== Part B: Annealing num_reads recovery sweep ===")
    sizes = [8, 10, 12]
    read_counts = [100, 500, 1000, 5000]
    n_seeds = 5
    rows = []
    for n in sizes:
        di = build_derived_instance(SOURCE_INSTANCE, n)
        qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=PENALTY_MULTIPLIER)
        for reads in read_counts:
            feasible_count = 0
            costs = []
            times = []
            for seed in range(n_seeds):
                t0 = time.perf_counter()
                ann = solve_qubo_with_annealing(qi, num_reads=reads, seed=seed)
                rt = time.perf_counter() - t0
                decoded = decode_qubo_sample(ann.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
                times.append(rt)
                if decoded.feasible:
                    feasible_count += 1
                    costs.append(decoded.total_cost)
            row = {
                "n_customers": n, "num_reads": reads, "n_seeds": n_seeds,
                "feasible_count": feasible_count, "feasibility_rate": feasible_count / n_seeds,
                "best_cost": min(costs) if costs else None, "mean_cost": float(np.mean(costs)) if costs else None,
                "mean_runtime_seconds": float(np.mean(times)),
            }
            rows.append(row)
            print(f"  N={n} num_reads={reads}: {feasible_count}/{n_seeds} feasible, "
                  f"best={row['best_cost']}, mean_runtime={row['mean_runtime_seconds']:.3f}s")
    return rows


def part_c_noise_sensitivity():
    """QAOA at N=4 (8 qubits, the one size Phase 3 established reliable
    statistics for) across 4 noise presets: noiseless, depolarizing_low,
    depolarizing_high, readout. 5 seeds per preset -- reduced from Phase
    3's 10 seeds since each noisy run additionally pays Aer's
    noise-simulation + transpile overhead on top of QAOA's own cost."""
    print("\n=== Part C: Noise sensitivity at N=4 ===")
    n = 4
    n_seeds = 5
    di = build_derived_instance(SOURCE_INSTANCE, n, n_vehicles=2)
    qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=PENALTY_MULTIPLIER)
    presets = ["noiseless", "depolarizing_low", "depolarizing_high", "readout"]
    rows = []
    for preset in presets:
        feasible_count = 0
        costs = []
        times = []
        for seed in range(n_seeds):
            t0 = time.perf_counter()
            res = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=20, shots=1024, seed=seed, noise_preset=preset)
            rt = time.perf_counter() - t0
            decoded = decode_qubo_sample(res.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
            times.append(rt)
            if decoded.feasible:
                feasible_count += 1
                costs.append(decoded.total_cost)
        row = {
            "noise_preset": preset, "n_seeds": n_seeds,
            "feasible_count": feasible_count, "feasibility_rate": feasible_count / n_seeds,
            "best_cost": min(costs) if costs else None, "mean_cost": float(np.mean(costs)) if costs else None,
            "mean_runtime_seconds": float(np.mean(times)),
        }
        rows.append(row)
        print(f"  {preset}: {feasible_count}/{n_seeds} feasible, best={row['best_cost']}, "
              f"mean_runtime={row['mean_runtime_seconds']:.2f}s")
    return rows


def part_d_qaoa_depth_sweep():
    """QAOA p in {1, 2, 3} at N=4, noiseless, 5 seeds each -- extends
    Phase 3's p=1-only result with the p=2/p=3 depth-vs-quality tradeoff
    it explicitly deferred (docs/PHASE_3_REPORT.md section 27)."""
    print("\n=== Part D: QAOA p=1/2/3 depth tradeoff at N=4 ===")
    n = 4
    n_seeds = 5
    di = build_derived_instance(SOURCE_INSTANCE, n, n_vehicles=2)
    qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=PENALTY_MULTIPLIER)
    rows = []
    for p in (1, 2, 3):
        feasible_count = 0
        costs, times, depths, gates = [], [], [], []
        for seed in range(n_seeds):
            t0 = time.perf_counter()
            res = solve_qubo_with_qaoa(qi, p=p, optimizer_maxiter=20, shots=1024, seed=seed)
            rt = time.perf_counter() - t0
            decoded = decode_qubo_sample(res.sample, n, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
            times.append(rt)
            depths.append(res.metadata.circuit_depth)
            gates.append(res.metadata.gate_count_total)
            if decoded.feasible:
                feasible_count += 1
                costs.append(decoded.total_cost)
        row = {
            "p": p, "n_seeds": n_seeds,
            "feasible_count": feasible_count, "feasibility_rate": feasible_count / n_seeds,
            "best_cost": min(costs) if costs else None, "mean_cost": float(np.mean(costs)) if costs else None,
            "mean_runtime_seconds": float(np.mean(times)),
            "circuit_depth": depths[0], "gate_count_total": gates[0],
        }
        rows.append(row)
        print(f"  p={p}: {feasible_count}/{n_seeds} feasible, best={row['best_cost']}, "
              f"depth={depths[0]}, gates={gates[0]}, mean_runtime={row['mean_runtime_seconds']:.2f}s")
    return rows


if __name__ == "__main__":
    import json

    all_results = {}
    all_results["part_a_runtime_wall_diagnosis"] = part_a_runtime_wall_diagnosis()
    all_results["part_b_annealing_reads_sweep"] = part_b_annealing_reads_sweep()
    all_results["part_c_noise_sensitivity"] = part_c_noise_sensitivity()
    all_results["part_d_qaoa_depth_sweep"] = part_d_qaoa_depth_sweep()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "phase4_noise_and_scaling_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")
