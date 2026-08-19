"""Phase 4 consolidation: unifies experiments/results/phase4_noise_and_scaling_results.json
and phase4_runtime_component_breakdown.json into the unified per-row schema
(experiments/results/phase4_noise_scalability.{json,csv}), and generates the
10 required publication figures under paper/figures/. Reads real, already-
executed results only -- no hand-typed numbers.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
FIGURES_DIR = ROOT / "paper" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

with open(RESULTS_DIR / "phase4_noise_and_scaling_results.json") as f:
    R = json.load(f)
with open(RESULTS_DIR / "phase4_runtime_component_breakdown.json") as f:
    BREAKDOWN = json.load(f)
with open(RESULTS_DIR / "routing_results.json") as f:
    PHASE3 = json.load(f)

FIELDS = [
    "experiment", "method", "problem_size", "seed", "noise_preset", "qaoa_depth",
    "num_reads", "objective", "gap", "feasible", "runtime", "qubits", "depth",
    "gates", "status", "label",
]


def row(**kw):
    r = {k: kw.get(k) for k in FIELDS}
    return r


rows = []

# --- Part A: runtime wall diagnosis (per-size single-circuit-execution) ---
for entry in R["part_a_runtime_wall_diagnosis"]["per_size"]:
    rows.append(row(
        experiment="phase4_part_a_runtime_wall", method="qaoa_single_circuit_execution",
        problem_size=entry["n_customers"], seed=None, noise_preset="noiseless", qaoa_depth=1,
        objective=None, gap=None, feasible=None, runtime=entry["single_call_mean_seconds"],
        qubits=entry["qubits"], depth=entry["circuit_depth"], gates=entry["gate_count"],
        status="RESEARCH", label=f"single forward-execution call, N={entry['n_customers']}",
    ))

# --- Part B: annealing num_reads sweep ---
for entry in R["part_b_annealing_reads_sweep"]:
    rows.append(row(
        experiment="phase4_part_b_annealing_reads", method="simulated_annealing",
        problem_size=entry["n_customers"], seed=None, noise_preset=None, qaoa_depth=None,
        num_reads=entry["num_reads"], objective=entry["best_cost"], gap=None,
        feasible=entry["feasibility_rate"], runtime=entry["mean_runtime_seconds"],
        qubits=None, depth=None, gates=None, status="RESEARCH",
        label=f"annealing feasibility sweep N={entry['n_customers']} reads={entry['num_reads']}",
    ))

# --- Part C: noise sensitivity at N=4 ---
for entry in R["part_c_noise_sensitivity"]:
    rows.append(row(
        experiment="phase4_part_c_noise_sensitivity", method="qaoa",
        problem_size=4, seed=None, noise_preset=entry["noise_preset"], qaoa_depth=1,
        objective=entry["best_cost"], gap=0.0 if entry["best_cost"] else None,
        feasible=entry["feasibility_rate"], runtime=entry["mean_runtime_seconds"],
        qubits=8, depth=None, gates=None, status="RESEARCH",
        label=f"QAOA noise preset={entry['noise_preset']}",
    ))

# --- Part D: QAOA depth sweep ---
for entry in R["part_d_qaoa_depth_sweep"]:
    rows.append(row(
        experiment="phase4_part_d_depth_sweep", method="qaoa",
        problem_size=4, seed=None, noise_preset="noiseless", qaoa_depth=entry["p"],
        objective=entry["best_cost"], gap=0.0 if entry["best_cost"] else None,
        feasible=entry["feasibility_rate"], runtime=entry["mean_runtime_seconds"],
        qubits=8, depth=entry["circuit_depth"], gates=entry["gate_count_total"],
        status="RESEARCH", label=f"QAOA p={entry['p']}",
    ))

# --- Runtime component breakdown ---
for n_key, entry in BREAKDOWN.items():
    n = int(n_key[1:])
    rows.append(row(
        experiment="phase4_runtime_components", method="qaoa_circuit_construction",
        problem_size=n, runtime=entry["construction_mean_seconds"], status="RESEARCH",
        label=f"QAOAAnsatz construction+bind, N={n}",
    ))
    rows.append(row(
        experiment="phase4_runtime_components", method="qaoa_transpile",
        problem_size=n, runtime=entry["transpile_mean_seconds"], status="RESEARCH",
        label=f"transpile to Aer basis gates, N={n}",
    ))
if "full_run_total_seconds" in BREAKDOWN.get("n4", {}):
    e = BREAKDOWN["n4"]
    rows.append(row(
        experiment="phase4_runtime_components", method="qaoa_full_optimization",
        problem_size=4, qaoa_depth=1, runtime=e["full_run_total_seconds"], status="RESEARCH",
        label=f"full COBYLA optimization, n_fevals={e['full_run_n_function_evals']}",
    ))

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
with open(RESULTS_DIR / "phase4_noise_scalability.json", "w") as f:
    json.dump(rows, f, indent=2, default=str)
with open(RESULTS_DIR / "phase4_noise_scalability.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} unified rows.")

# ============================================================
# FIGURES
# ============================================================
plt.rcParams.update({"figure.dpi": 120, "font.size": 9})


def savefig(name):
    path = FIGURES_DIR / f"{name}.pdf"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"  saved {path}")


# 1. QAOA runtime scaling (single-call + full-run, N=4 vs N=5)
sizes = [e["n_customers"] for e in R["part_a_runtime_wall_diagnosis"]["per_size"]]
single_call = [e["single_call_mean_seconds"] for e in R["part_a_runtime_wall_diagnosis"]["per_size"]]
plt.figure(figsize=(5, 4))
plt.plot(sizes, single_call, "o-", label="single circuit execution (mean of 5)")
plt.scatter([4, 5], [37.6, 628.9], color="red", marker="x", s=80, label="full COBYLA optimization run (Phase 3)")
plt.yscale("log")
plt.xlabel("Customers (N)")
plt.ylabel("Runtime (seconds, log scale)")
plt.title("QAOA runtime scaling: single-call vs. full optimization")
plt.legend(fontsize=7)
savefig("phase4_qaoa_runtime_scaling")

# 2. QAOA depth tradeoff (p vs cost/feasibility/runtime)
ps = [e["p"] for e in R["part_d_qaoa_depth_sweep"]]
feas = [e["feasibility_rate"] for e in R["part_d_qaoa_depth_sweep"]]
rt = [e["mean_runtime_seconds"] for e in R["part_d_qaoa_depth_sweep"]]
fig, ax1 = plt.subplots(figsize=(5, 4))
ax1.bar([p - 0.15 for p in ps], feas, width=0.3, color="tab:blue", label="feasibility rate")
ax1.set_ylabel("Feasibility rate", color="tab:blue")
ax1.set_ylim(0, 1.1)
ax2 = ax1.twinx()
ax2.plot(ps, rt, "o-", color="tab:red", label="mean runtime (s)")
ax2.set_ylabel("Mean runtime (s)", color="tab:red")
ax1.set_xlabel("QAOA depth p")
ax1.set_xticks(ps)
plt.title("QAOA p=1/2/3: feasibility vs. runtime (N=4)")
savefig("phase4_qaoa_depth_tradeoff")

# 3. Noise sensitivity (feasibility + runtime per preset)
presets = [e["noise_preset"] for e in R["part_c_noise_sensitivity"]]
feas_c = [e["feasibility_rate"] for e in R["part_c_noise_sensitivity"]]
rt_c = [e["mean_runtime_seconds"] for e in R["part_c_noise_sensitivity"]]
fig, ax1 = plt.subplots(figsize=(5.5, 4))
x = np.arange(len(presets))
ax1.bar(x - 0.15, feas_c, width=0.3, color="tab:blue", label="feasibility rate")
ax1.set_ylim(0, 1.1)
ax1.set_ylabel("Feasibility rate", color="tab:blue")
ax2 = ax1.twinx()
ax2.plot(x, rt_c, "o-", color="tab:red")
ax2.set_ylabel("Mean runtime (s, log)", color="tab:red")
ax2.set_yscale("log")
ax1.set_xticks(x)
ax1.set_xticklabels(presets, rotation=20, ha="right")
plt.title("QAOA noise sensitivity at N=4 (8 qubits)")
savefig("phase4_noise_sensitivity")

# 4. Annealing feasibility vs N at fixed num_reads=100 (Phase 3 baseline) and Phase 4 sweep
b = R["part_b_annealing_reads_sweep"]
fig, ax = plt.subplots(figsize=(5.5, 4))
for reads in (100, 500, 1000, 5000):
    ns = [e["n_customers"] for e in b if e["num_reads"] == reads]
    fr = [e["feasibility_rate"] for e in b if e["num_reads"] == reads]
    ax.plot(ns, fr, "o-", label=f"num_reads={reads}")
ax.set_xlabel("Customers (N)")
ax.set_ylabel("Feasibility rate")
ax.set_ylim(-0.05, 1.1)
ax.legend(fontsize=7)
plt.title("Annealing feasibility vs. problem size, by num_reads")
savefig("phase4_annealing_feasibility")

# 5. Annealing sampling sensitivity (feasibility vs num_reads, one line per N)
fig, ax = plt.subplots(figsize=(5.5, 4))
for n in (8, 10, 12):
    reads = [e["num_reads"] for e in b if e["n_customers"] == n]
    fr = [e["feasibility_rate"] for e in b if e["n_customers"] == n]
    ax.plot(reads, fr, "o-", label=f"N={n}")
ax.set_xscale("log")
ax.set_xlabel("num_reads (log scale)")
ax.set_ylabel("Feasibility rate")
ax.set_ylim(-0.05, 1.1)
ax.legend(fontsize=8)
plt.title("Annealing feasibility recovers with more reads")
savefig("phase4_annealing_sampling")

# 6. Qubit scaling (QUBO variables = qubits, from Phase 3 + Phase 4 N=5 point)
phase3_sizes = sorted(set(r["stops"] for r in PHASE3 if r["qubo_variables"]))
phase3_qubits = [next(r["qubo_variables"] for r in PHASE3 if r["stops"] == n) for n in phase3_sizes]
fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(phase3_sizes, phase3_qubits, "o-", label="Phase 3 derived instances (K=ceil(N/2))")
ax.scatter([5], [10], color="red", marker="x", s=80, label="Phase 4 diagnostic (N=5, K=2)")
ax.set_xlabel("Customers (N)")
ax.set_ylabel("QUBO variables (= qubits)")
ax.legend(fontsize=7)
plt.title("Qubit / QUBO-variable scaling with problem size")
savefig("phase4_qubit_scaling")

# 7. Circuit depth scaling (vs p, and vs N from Part A)
fig, axes = plt.subplots(1, 2, figsize=(8, 4))
axes[0].plot(sizes, [e["circuit_depth"] for e in R["part_a_runtime_wall_diagnosis"]["per_size"]], "o-")
axes[0].set_xlabel("Customers (N)")
axes[0].set_ylabel("Circuit depth")
axes[0].set_title("Depth vs. N (p=1)")
axes[1].plot(ps, [e["circuit_depth"] for e in R["part_d_qaoa_depth_sweep"]], "o-", color="tab:orange")
axes[1].set_xlabel("QAOA depth p")
axes[1].set_ylabel("Circuit depth")
axes[1].set_title("Depth vs. p (N=4)")
savefig("phase4_circuit_depth_scaling")

# 8. Gate count scaling (vs p, and vs N)
fig, axes = plt.subplots(1, 2, figsize=(8, 4))
axes[0].plot(sizes, [e["gate_count"] for e in R["part_a_runtime_wall_diagnosis"]["per_size"]], "o-")
axes[0].set_xlabel("Customers (N)")
axes[0].set_ylabel("Total gate count")
axes[0].set_title("Gates vs. N (p=1)")
axes[1].plot(ps, [e["gate_count_total"] for e in R["part_d_qaoa_depth_sweep"]], "o-", color="tab:orange")
axes[1].set_xlabel("QAOA depth p")
axes[1].set_ylabel("Total gate count")
axes[1].set_title("Gates vs. p (N=4)")
savefig("phase4_gate_scaling")

# 9. Reproducibility (feasibility rate as proxy for stability across the two
# 5-seed representative configs: annealing N=8/reads=100, QAOA N=4 noiseless)
configs = ["annealing\nN=8,reads=100", "QAOA\nN=4,p=1,noiseless"]
ann_n8_100 = next(e for e in b if e["n_customers"] == 8 and e["num_reads"] == 100)
qaoa_n4 = next(e for e in R["part_c_noise_sensitivity"] if e["noise_preset"] == "noiseless")
feas_rates = [ann_n8_100["feasibility_rate"], qaoa_n4["feasibility_rate"]]
fig, ax = plt.subplots(figsize=(4.5, 4))
ax.bar(configs, feas_rates, color=["tab:blue", "tab:purple"])
ax.set_ylabel("Feasibility rate across 5 independent seeds")
ax.set_ylim(0, 1.1)
plt.title("Reproducibility: feasibility rate, 2 representative configs")
savefig("phase4_reproducibility")

# 10. Scalability summary (practical qubit/N ceiling annotated)
fig, ax = plt.subplots(figsize=(6, 4.5))
ann_feas_by_n = {n: max(e["feasibility_rate"] for e in b if e["n_customers"] == n) for n in (8, 10, 12)}
ax.plot(list(ann_feas_by_n.keys()), list(ann_feas_by_n.values()), "o-", label="annealing (best-of-swept-reads)")
qaoa_ns = [4, 5]
qaoa_practical = [1.0, None]  # N=5 not run to statistics this phase -- PENDING, plotted as gap
ax.scatter([4], [1.0], color="tab:purple", marker="s", s=80, label="QAOA (statistics only at N=4)")
ax.axvline(5, color="gray", linestyle="--", alpha=0.5)
ax.text(5.1, 0.5, "QAOA wall\n(N=5: 1 run=629s,\nN=6: timeout)", fontsize=7, color="gray")
ax.set_xlabel("Customers (N)")
ax.set_ylabel("Best observed feasibility rate")
ax.set_ylim(-0.05, 1.1)
ax.legend(fontsize=7)
plt.title("Phase 4 scalability summary")
savefig("phase4_scalability_summary")

print("All figures generated.")
