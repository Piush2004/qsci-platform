# Phase 3 — Quantum Routing

Status: **COMPLETE — RESEARCH RESULT, NOT YET COMMITTED**
Date: 2026-08-19
Branch: `main`

## 1. Objective

Investigate whether quantum or quantum-inspired optimization provides measurable value for supply-chain vehicle routing under realistic constraints and fair comparison against a strong classical baseline. Quantum superiority, classical superiority, and quantum advantage are all treated as open questions, not assumed.

## 2. Research Questions

**RQ6 (primary)**: Can quantum/quantum-inspired optimization produce competitive feasible vehicle-routing solutions compared with a strong OR-Tools baseline when both solve exactly the same constrained routing instances?

Secondary: solution-quality scaling, computational-cost scaling, quantum-encoding-overhead scaling, qubit requirements, QUBO size growth, QAOA circuit-depth growth, quantum-annealing behavior as problem size grows, the point at which the quantum formulation becomes impractical, whether a quantum method produces feasible solutions without classical repair, why classical wins if it does, and whether any quantum win survives statistical testing.

## 3. Hypotheses

**H5**: Quantum and quantum-inspired methods may become increasingly relevant for selected constrained optimization problems as hardware and algorithms mature / as problem size grows. Tested as a real hypothesis — see §26 for whether the evidence supports it (it does not, on this formulation).

## 4. Dataset

Real CVRPLIB data (`A-n32-k5`, 31 customers, verified in Phase 0 and re-verified directly from raw files this phase — see §5). Amazon Last-Mile data (6,112 routes, 904,527 stops) also re-verified, used for scale context (§22) rather than as a direct routing-solve input this phase.

## 5. Ground Truth — Re-Verified, Not Trusted From Phase 0

Read directly from raw files on disk, not copied from the Phase 0 report:

| Instance | Customers | Vehicles | Capacity | Published BKS | Source | Status |
|---|---|---|---|---|---|---|
| A-n32-k5 | 31 | 5 | 100 | 784 | raw `.sol` file | MATCHES_PRIOR_REPORT |
| A-n33-k5 | 32 | 5 | 100 | 661 | raw `.sol` file | MATCHES_PRIOR_REPORT |
| A-n37-k5 | 36 | 5 | 100 | 669 | raw `.sol` file | MATCHES_PRIOR_REPORT |
| B-n31-k5 | 30 | 5 | 100 | 672 | raw `.sol` file | MATCHES_PRIOR_REPORT |

No discrepancies found — all four match the previously reported values exactly. Machine-readable: `experiments/results/routing_ground_truth.json`.

Amazon Last-Mile, re-verified directly from raw JSON (not trusted from Phase 0):

| Field | Value | Type |
|---|---|---|
| Route count | 6,112 | directly observed |
| Total stops (incl. depot per route) | 904,527 | directly observed |
| Avg. stops per route | 147.99 | derived |
| Unique station codes | 17 | directly observed |
| Route score categories | High, Medium, Low | directly observed |
| Total packages | 1,457,175 | directly observed |
| Monetary/cost data | none present | explicitly noted — nothing assumed or fabricated |

Matches Phase 0's reported 6,112 routes / 904,527 stops exactly.

## 6. Routing Formulation

**Cluster-first, route-second decomposition.** Decision variables: `x_{i,k} ∈ {0,1}` — customer `i` assigned to vehicle `k`, for `i` in 0..n-1, `k` in 0..K-1. No depot variable (implicit start/end of every route). `n*K` binary variables total, no slack bits.

Objective (pairwise-distance clustering proxy — a documented simplification, not the exact TSP cost, see §9):
```
minimize  sum_k sum_{i<j} c_ij * x_ik * x_jk
```
Constraints (as QUBO penalty terms):
```
1. Visit-once:  lambda1 * sum_i (sum_k x_ik - 1)^2
2. Capacity:    lambda2 * sum_k (sum_i d_i*x_ik - Q)^2   (soft, no slack)
```
Within-vehicle visitation **order** is decided classically, post-hoc, by exact enumeration over each vehicle's (small) assigned cluster — this is the explicit, disclosed trade-off that keeps the QUBO to `n*K` variables instead of the `O(n²*K)` a full position-indexed encoding would need (which would make even N=4 QAOA-intractable). Feasibility (all constraints) is independently re-checked at decode time regardless of what the QUBO's soft penalties encouraged — see `qsci_core/optimization/quantum/decoder.py`.

Where real data doesn't supply a needed parameter: vehicle count `K` and capacity `Q` for the truncated scaling instances are **derived, not real CVRPLIB values** (the original instance's `K=5`, `Q=100` are sized for 31 customers, not a 4-16 customer sub-instance) — `K = max(2, ceil(N/2))`, `Q = ceil(total_demand/K * 1.15)`. Documented in `instance_builder.py`; every derived instance is labeled `RESEARCH — DERIVED / SYNTHETIC EXTENSION`, never LIVE.

## 7. Classical Baseline

Two baselines, kept explicitly separate (CLAUDE.md §8 fairness requirement):

1. **OR-Tools native VRP solver** (Phase 1, unchanged) — solves the *full* CVRP with real sequencing. 0.61% max gap vs. published BKS across all 4 real CVRPLIB instances (30-37 customers). Kept as outside context, not compared directly against quantum/annealing.
2. **OR-Tools-on-QUBO** (this phase) — CP-SAT solving the *identical* binary-quadratic objective/constraints the annealing and QAOA tracks solve. Config: `random_seed=42`, `max_time_in_seconds=30`, default search strategy — not weakened. This is the fair, same-problem classical reference for §14-17.

## 8. QUBO Formulation

See §6. Implemented in `qsci_core/optimization/quantum/qubo_formulator.py`.

## 9. QUBO Validation — A Real Bug Was Found and Fixed

Per CLAUDE.md §11/§40's mandatory stop condition, the QUBO's true optimum (via `dimod.ExactSolver`, exhaustive enumeration — not a heuristic) is checked against an independent manual brute-force enumeration before any quantum solver runs.

**This failed on the first attempt** with real data. Instance: 4 customers from `A-n32-k5` (demands 19, 21, 6, 19; capacity 38; 2 vehicles). The QUBO's true global optimum was:
```
customer 0 -> vehicle 0 AND vehicle 1 (both)
customer 3 -> vehicle 0 AND vehicle 1 (both)
customers 1, 2 -> unassigned to any vehicle
```
Decoded: **INFEASIBLE** — "customers never assigned to any vehicle: [1, 2]".

**Root cause**: the original `penalty_visit` derivation (`m * n * max(c_ij)`) was sized only against the *objective's* scale. It failed to account for the capacity penalty's *own* potential magnitude. Duplicating customers 0 and 3 onto both vehicles happened to push each vehicle's load to *exactly* 38 (=capacity), zeroing the symmetric squared-deviation capacity penalty `(load - Q)²` — while any *actually* feasible partition (the only one exists: {21,6}=27 and {19,19}=38) leaves one vehicle under capacity, incurring a real, nonzero, and — critically — *larger* capacity penalty than the visit-once violation cost. The exploit was cheaper than correctness.

**Fix**: `penalty_visit` is now derived to dominate BOTH the objective's scale AND the capacity penalty's own maximum magnitude:
```
penalty_capacity = m * n * max(c_ij)
penalty_visit     = m * (n * max(c_ij) + K * penalty_capacity * capacity^2)
```
Re-validated on the failing instance: true optimum is now the correct partition, decodes feasible, cost 380.00755017228636, matching an independent manual brute-force enumeration exactly. The original hand-crafted validation instance (used before any real data was involved) was re-checked and still passes unchanged. A penalty-multiplier sensitivity sweep (1x/2x/5x/10x, §20) confirms the fix is robust across an order of magnitude, not a narrow escape at one specific value.

**This is exactly the class of bug Phase 2.1 warned about** (a leakage/formulation bug that changes the interpretation of results) — caught here at the mandated validation gate, before any quantum solver ran on the buggy formulation, per the "STOP and diagnose" discipline.

## 10. Quantum Annealing

Backend: `dwave.samplers.SimulatedAnnealingSampler` (dwave-samplers 1.8.0, part of dwave-ocean-sdk 9.4.0). **The standalone `neal` package the original architecture spec named does not exist in this environment** — verified directly (`ModuleNotFoundError`), not assumed; its functionality moved into `dwave.samplers` in newer Ocean SDK releases. Documented in `annealing_solver.py`, same "no silent API replacement" discipline as Phase 2.

**No D-Wave Leap hardware was available or used** — verified directly: no `DWAVE_API_TOKEN`/`DWAVE_API_KEY` environment variables, no `~/.config/dwave` file, and `dwave.cloud.Client.from_config()` raises `ValueError: API token not defined`. Every annealing result in this report is **SIMULATED ANNEALING** on classical CPU — labeled as such everywhere, never "quantum hardware."

Config: `num_reads=100` per run, 10 independent seeds per instance size.

## 11. QAOA

Pipeline: QUBO → `QuadraticProgram` (via `qiskit_optimization.converters.QuadraticProgramToQubo`) → Ising Hamiltonian (`.to_ising()`) → `qiskit_algorithms.minimum_eigensolvers.QAOA` → `qiskit.primitives.StatevectorSampler` (noiseless, shot-sampled) → bitstring → `qsci_core`'s own `decode_qubo_sample` (route decoding + independent feasibility validation).

**Installed-API note**: `qiskit_algorithms` (providing the `QAOA` class) is not part of core `qiskit` 2.5.2 — it is a separate package (`qiskit-algorithms==0.4.0`), not in the original Phase 0 dependency list. Installed for Phase 3, same pattern as `ortools` in Phase 1. Verified against the actually-installed version before writing `qaoa_solver.py`.

Config: `p=1`, COBYLA `maxiter=20`, `shots=1024`, 10 independent seeds at N=4.

**Contrast with Phase 2's VQR pathology**: unlike Phase 2's `EstimatorQNN`-based forecaster (which suffered catastrophic runtime from an unconditionally-constructed analytic gradient), this QAOA path uses a `StatevectorSampler` — samples bitstrings, not expectation-value gradients — and was empirically verified NOT to reproduce that specific pathology. It has its own, different scaling wall — see §18.

## 12. Experimental Conditions

Manifest schema: `qsci_core/optimization/quantum/experiment.py`'s `RoutingManifest` — dataset, instance ID, status label, stops, vehicles, capacity, seed, objective, constraints, penalty multiplier, time limit, solver identities, software versions, hardware, git commit. Every solver call in `experiments/phase3_scaling_experiment.py` consumes the identical `QUBOInstance` for a given size — verified by construction (one `qi` object, passed to all three solvers).

## 13. Fairness Audit

Full 15-point audit: `docs/PHASE_3_FAIRNESS_AUDIT.md`. Summary verdict: **fully fair within the Phase 3 QUBO-based comparison** (identical data, features, constraints, objective, reference, preprocessing, postprocessing across all three solvers). **Explicitly not fair, and not presented as such,** between Phase 1's native-VRP OR-Tools and the QUBO-based tracks — different problem formulations, reported separately.

## 14. Feasibility Results

| Solver | N=4 | N=6 | N=8 | N=10 | N=12 | N=16 |
|---|---|---|---|---|---|---|
| OR-Tools-on-QUBO | 1/1 OPTIMAL | 1/1 OPTIMAL | 1/1 OPTIMAL | 1/1 OPTIMAL | 1/1 FEASIBLE (30s limit) | 1/1 FEASIBLE (30s limit) |
| Simulated annealing | 10/10 | 10/10 | 9/10 | 1/10 | 0/10 | 0/10 |
| QAOA | 8/10 | PENDING | PENDING | PENDING | PENDING | PENDING |

`repair_used` is `False` on all 76 results (verified directly, not assumed) — no hidden classical repair anywhere in this phase.

## 15. Objective Results

| N | OR-Tools-on-QUBO cost | Annealing best (of feasible) | Annealing mean | QAOA cost (of feasible) |
|---|---|---|---|---|
| 4 | 380.01 | 380.01 | 380.01 | 380.01 (all 8 feasible runs) |
| 6 | 519.63 | 519.63 | 521.07 (std 3.04) | PENDING |
| 8 | 643.50 | 643.50 | 695.96 (std 35.87) | PENDING |
| 10 | 853.88 | 859.01 | 859.01 (n=1) | PENDING |
| 12 | 1117.46 | — (0 feasible) | — | PENDING |
| 16 | 1386.38 | — (0 feasible) | — | PENDING |

## 16. Optimality Gap

Reference = OR-Tools-on-QUBO's result on the identical problem (`reference_type` recorded per-row in `routing_results.json`; for the QUBO sub-problem there is no external BKS, since truncation invalidates the original CVRPLIB BKS — documented, not silently substituted).

| N | Annealing best-case gap | QAOA gap (when feasible) |
|---|---|---|
| 4 | 0.000% | 0.000% |
| 6 | -0.000% (matches to float precision) | PENDING |
| 8 | -0.000% (matches to float precision) | PENDING |
| 10 | 0.601% | PENDING |
| 12 | undefined (0 feasible) | PENDING |
| 16 | undefined (0 feasible) | PENDING |

**QAOA found the exact true optimum in every feasible run at N=4 (8/8) — 0.000% gap.**

## 17. Runtime

Solver-only vs. end-to-end are distinguished in every result row (`runtime_solver_seconds` vs. `runtime_end_to_end_seconds`, which additionally includes QUBO construction time — itself sub-millisecond even at N=16's 128 variables).

| Solver | N=4 solver time | N=16 solver time |
|---|---|---|
| OR-Tools-on-QUBO | 0.16s | 30.18s (hit time limit) |
| Simulated annealing (per run) | ~0.013s | 0/10 feasible, still returns a (infeasible) result in comparable time |
| QAOA (per run) | ~37.6s mean | not attempted |

QAOA's per-run cost (~37.6s at 8 qubits) is three orders of magnitude higher than OR-Tools' (~0.16s) or annealing's (~0.013s) for the *same* problem at the *same* size — reported plainly, not glossed over. This is simulator wall-clock, never described as hardware runtime.

## 18. Quantum Resources

| N | Qubits | QUBO vars | Circuit depth | Gates (1Q/2Q/total) | Shots | QAOA p |
|---|---|---|---|---|---|---|
| 4 | 8 | 8 | 34 | 49/32/81 | 1024 | 1 |
| 5* | 10 | 10 | not captured (single timing-only run) | — | — | 1 |
| 6 (K=2, exploratory)* | 12 | 12 | — | — | — | 1 |

\*N=5 and the exploratory N=6 (K=2, not the real N=6 derived instance which needs K=3/18 qubits) were isolated diagnostics outside the main experiment, run specifically to find QAOA's practical ceiling — not part of the 10-seed statistical sweep.

**Measured QAOA scaling wall**: 8 qubits (N=4) → ~35-50s/run, reliable. 10 qubits (N=5) → 628.9s for a single run (12-18x slower for 2 more qubits — steeper than the 4x that pure state-space doubling would predict). 12 qubits (N=6, K=2 exploratory) → exceeded a 15+ minute budget across 4 independent attempts (COBYLA maxiter=5 and maxiter=15, SPSA maxiter=15, a live-callback-instrumented trace confirming the stall is inside the optimization loop, not circuit construction/transpilation which both measured under 0.2s) — killed, **TIMEOUT**, not fabricated as a result. The real N=6 derived instance (K=3 vehicles, 18 qubits) is worse than the already-timed-out case and was not attempted — **PENDING**, honestly labeled, not silently dropped.

Annealing has no qubit ceiling (classical CPU) — its scaling wall (§14, feasibility collapsing 100%→0% between N=8 and N=12) is a solution-quality/tuning limitation of the fixed 100-reads configuration, not a hardware constraint.

## 19. Scaling

QUBO variable count grows as `N * K` where `K = max(2, ceil(N/2))` — empirically: N=4→8 vars, N=6→18, N=8→32, N=10→50, N=12→72, N=16→128. Consistent with the documented O(n²)-ish growth (since K itself grows with N in this scheme).

The scaling boundary that matters most, measured directly: **annealing's feasibility rate collapses from 90% (N=8) to 10% (N=10) to 0% (N=12) well before OR-Tools' own 30-second time limit is exhausted at the same sizes** (OR-Tools still returns FEASIBLE, if not always proven-OPTIMAL, through N=16). QAOA's wall (§18) is far more severe, arriving by N=6.

## 20. Penalty Sensitivity

4-point sweep at N=4 (`m` = 1, 2, 5, 10), with the corrected derivation:

| Multiplier | penalty_visit | Feasible | Cost | Loads |
|---|---|---|---|---|
| 1.0 | 1,050,134.6 | Yes | 380.01 | {0: 38.0, 1: 27.0} |
| 2.0 | 4,199,811.5 | Yes | 380.01 | {0: 27.0, 1: 38.0} |
| 5.0 | 26,246,095.4 | Yes | 380.01 | {0: 27.0, 1: 38.0} |
| 10.0 | 104,980,746.6 | Yes | 380.01 | {0: 38.0, 1: 27.0} |

**Finding**: with the fixed derivation, cost and feasibility are completely stable across a 10x multiplier range — the fix is robust, not a narrow escape from the bug at one specific value. (Vehicle labels 0/1 swap between runs — expected, since vehicles are interchangeable; the partition itself, {27, 38}, is identical every time.)

## 21. Statistical Analysis

10 independent seeds per feasible (solver, N) configuration. At N∈{4,6,8}, annealing's best-of-10 matches OR-Tools' proven optimum with **zero variance among the feasible-run costs that achieve the optimum** — no formal significance test was applied to these, since there is no meaningful distribution to test (best case = the known optimum, exactly, every feasible time). At N=10, only 1/10 annealing runs were feasible at all — too small a sample for any test. QAOA statistics (N=4 only): 8/10 feasible, and all 8 feasible runs found the identical optimal cost — again no variance to test statistically, but the *feasibility rate itself* (80%) is a real, reportable metric on its own.

This differs from Phase 2's DM-test-based approach because the underlying comparison here is discrete (feasible/infeasible, and cost when feasible) rather than a continuous forecast-error series — a paired statistical test on cost would be appropriate for a case with genuine cost variance; here, feasibility rate is the more informative statistic, matching CLAUDE.md §16's explicit instruction to treat feasibility as first-class.

## 22. Business Interpretation

Route distances reported above are real (Euclidean, CVRPLIB coordinate units) — **RESEARCH** math over **LIVE** distances. No monetary translation is computed: the Amazon Last-Mile ground-truth re-verification (§5) confirms no fuel, driver-cost, or per-stop-cost data exists in any dataset QSCI uses, so none is fabricated, per CLAUDE.md §25. At N=4, quantum and quantum-inspired methods lose zero distance vs. classical when they return a feasible answer, at a large runtime cost and a non-trivial infeasibility rate. Neither track's demonstrated operating range (N≤4 reliably, N≤10 for annealing at reduced confidence) approaches either Phase 1's native-solver capability (30-37 real customers, 0.61% gap) or the real-world scale QSCI targets (Amazon Last-Mile: ~148 stops/route, verified directly this phase).

## 23. Failure Cases

Comprehensive adversarial test suite (`tests/test_routing_adversarial.py`, 9 tests) covering: duplicate coordinates, extreme demand (raises cleanly), single-customer and single-vehicle instances, NaN/infinite coordinates (propagate visibly as non-finite QUBO terms, never silently absorbed), malformed/empty samples, penalty too small (decoder still independently catches infeasibility regardless of QUBO's own soft-penalty verdict), penalty excessively large (no overflow), degenerate zero-distance instances. All 9 pass with controlled, correct results — no hanging processes, no silent misbehavior.

## 24. Limitations

- **Cluster-first-route-second**, not the full joint CVRP — sequencing decided classically post-hoc. Not directly comparable to Phase 1's native OR-Tools VRP result (hence reported separately, §7).
- **Soft, not hard, capacity constraint** (no slack variables) — the §9 bug is direct proof this trade-off has real teeth; the decoder's independent hard check is what makes it safe, not the QUBO's own penalty.
- **QAOA statistics exist only at N=4.** N=5 is a single expensive data point; N≥6 is PENDING, not attempted at scale, for measured (not assumed) reasons.
- **Annealing's feasibility collapse (N=10-16) is a tuning limitation** of the fixed 100-reads configuration used here — untested whether more reads or a different schedule would do meaningfully better; not concluded to be a hard limit of simulated annealing in general.
- **Single source instance**, deterministic (non-random) truncation — not a claim about CVRP instances broadly.
- **No real D-Wave QPU** was available or used.
- **No classical-repair hybrid experiment** was run this phase (CLAUDE.md §24 optional) — noted as Phase 4/5 candidate work, not silently skipped.

## 25. Research Findings

1. A real QUBO-formulation bug was found and fixed via the mandated brute-force validation gate — before it could reach any quantum solver (§9).
2. On the identical QUBO problem, simulated annealing matches classical optimally at small scale (N≤8, 0% gap) but its *feasibility rate*, not solution quality, degrades sharply and fails completely by N=12 — well before any hardware/qubit constraint, since annealing has none.
3. QAOA matched the true optimum in 100% of its feasible runs at N=4 (8/8) — a genuinely positive quantum result at this specific tiny scale — but its own measured runtime wall arrives even sooner than annealing's feasibility wall (unusable by N=6, vs. annealing's N=12).
4. The QAOA runtime wall is real and steep (12-18x slower for a 2-qubit increase, worse than pure exponential state-space scaling would predict) but was not root-caused to the same specific mechanism as Phase 2's gradient pathology — this QAOA path avoids that specific bug (verified) but still hits a comparably severe, distinctly-measured wall of its own.

## 26. RQ6 Conclusion

**Neither quantum-inspired (simulated annealing) nor gate-model (QAOA) optimization demonstrated a quantum advantage on this real-data-derived CVRP QUBO.** Both matched classical exactly when feasible at small scale; both became *less*, not more, competitive as problem size grew — annealing's feasibility collapsing by N=12, QAOA's runtime wall arriving even earlier at N~6. **H5 is not supported by this evidence.** If anything, the measured pattern is the reverse of H5's expectation: competitiveness (here, feasibility) decreased with scale for both quantum and quantum-inspired methods, on this formulation, in this environment. This is reported as a valid, negative research result, per CLAUDE.md's explicit instruction not to tune until quantum wins.

## 27. What Phase 4 Must Investigate

Phase 4 (Noise & Scalability) should use these Phase 3-discovered bottlenecks, not an invented plan:

- **QAOA's runtime wall** (§18): whether it is dominated by gradient-adjacent optimizer overhead (as Phase 2's VQR was) or purely by state-space/shot-sampling cost — this phase's diagnostics ruled out the *exact* Phase 2 mechanism but did not fully isolate the real one; Phase 4's noise/scalability study is the natural place to finish this.
- **Annealing's feasibility collapse** (N=8→12): whether more `num_reads`, a different annealing schedule, or reverse annealing recovers feasibility at the sizes where the fixed 100-reads configuration failed — untested here.
- **Shot-count and noise sensitivity** at QAOA's one reliable size (N=4, 8 qubits) — this phase only ran noiseless `StatevectorSampler`; Aer noise models (depolarizing, readout) are explicitly Phase 4's job, not mixed in here.
- **Circuit-depth vs. QAOA-p trade-off**: `p=1` only was used this phase (CLAUDE.md §14's p=2/p=3 study was not reached given the p=1, N=4 runtime already at ~37s/run and the N≥6 wall) — worth revisiting at N=4 specifically, where repeated runs are still tractable.
