# Phase 3 Fairness Audit — Quantum Routing

Status: **COMPLETE**
Date: 2026-08-19
Scope: audits the Phase 3 quantum-routing experiment before its results are accepted.

Per CLAUDE.md Phase 3 §30, each dimension is answered YES / NO / UNKNOWN. If any answer is NO or UNKNOWN, the comparison is not declared fully fair on that dimension — stated explicitly below rather than glossed over.

## DATA: same? — **YES**

OR-Tools-on-QUBO, simulated annealing, and QAOA all consume the identical `QUBOInstance` object returned by `build_cvrp_qubo()` — same coordinates, same demands, same capacity, same vehicle count, same penalty weights. No solver receives a modified, truncated, or simplified copy. Verified by construction: `experiments/phase3_scaling_experiment.py` builds one `qi` per instance size and passes the same object to all three solver calls.

## FEATURES: same? — **YES**

There are no "features" in the ML sense here (this is combinatorial optimization, not a learned model) — the equivalent question is whether all solvers see the same objective/constraint structure. Yes: `qi.bqm` (the dimod BinaryQuadraticModel) is the single source of truth. OR-Tools reads its `.linear`/`.quadratic`/`.offset` directly (`classical_qubo_solver.py`); annealing samples the same `bqm` directly (`annealing_solver.py`); QAOA converts the same `bqm` variables into a `QuadraticProgram` with identical linear/quadratic/constant terms (`qaoa_solver.py`'s `_bqm_to_quadratic_program`).

## INSTANCE: same? — **YES, within each experiment; explicitly different by design across the two experiments**

Within the Phase 3 scaling experiment: same instance (same `DerivedInstance`) for a given N across all three solvers. Across experiments: Phase 1's OR-Tools-native baseline and Phase 3's QUBO-based comparison solve genuinely different problem formulations (full joint CVRP vs. cluster-assignment sub-problem) — this is **documented as a difference, not presented as a fair head-to-head**, per CLAUDE.md §8's explicit warning against "Classical: full information / Quantum: simplified information." Both are reported, clearly labeled as separate comparisons (`docs/PHASE_3_REPORT.md` §7).

## CONSTRAINTS: same? — **YES**

Every solver is subject to the same penalty-encoded visit-once and capacity constraints (part of the shared `bqm`). No solver has constraints "relaxed" for it. The decoder (`decode_qubo_sample`) applies the identical hard feasibility check — visit-once, capacity, decodable cluster size — to every solver's output with no solver-specific leniency.

## OBJECTIVE: same? — **YES**

Same `bqm.linear`/`bqm.quadratic`/`bqm.offset` for every solver, as above. Reported `objective_cost` in results is not the raw QUBO energy (which includes penalty terms) but the *decoded route cost* (pairwise-distance proxy summed over the assignment) — computed identically for every solver by the same `decode_qubo_sample` function, so comparisons are on a common, penalty-free cost metric.

## REFERENCE: same? — **YES, and explicitly two-tiered**

For the QUBO-defined sub-problem (annealing, QAOA, OR-Tools-on-QUBO), the reference is OR-Tools-on-QUBO's own result on the identical problem — a true apples-to-apples reference, not an external number computed differently. For the original, untruncated CVRPLIB instances (Phase 1's native OR-Tools baseline), the reference is the published BKS from the `.sol` files, re-verified against raw files in this phase (§4 of `docs/PHASE_3_REPORT.md`) — unchanged, no discrepancy found.

## TIME LIMIT: documented? — **YES**

OR-Tools-on-QUBO: `max_time_in_seconds=30` (`classical_qubo_solver.py`). Annealing: no explicit wall-clock limit, but bounded by `num_reads=100` (deterministic total work). QAOA: bounded by `optimizer_maxiter=20` COBYLA iterations, not wall-clock, but measured wall-clock is reported per run in the results table.

## RANDOM SEEDS: documented? — **YES**

OR-Tools: `random_seed=42` fixed. Annealing: seeds 0-9 (one per statistical run), recorded per-result in `routing_results.json`'s `seed` field. QAOA: seeds 0-9, same. Instance truncation itself is deterministic (first-N-customers by CVRPLIB file order), not seed-dependent — verified by `tests/test_instance_builder.py::test_derived_instance_deterministic_not_random`.

## PREPROCESSING: same? — **YES**

All three solvers receive the already-built `QUBOInstance` with no solver-specific preprocessing (no solver gets pre-clustering, pre-rounding, or a warm start the others don't). QUBO construction time is measured once, shared across all solvers using that instance (`qubo_time` in the experiment script, folded into each solver's `runtime_end_to_end_seconds`).

## POSTPROCESSING: same? — **YES**

Every solver's raw output goes through the identical `decode_qubo_sample()` function — same feasibility checks, same route-cost computation, same exact-enumeration sequencing. No solver-specific post-hoc adjustment exists in this codebase.

## CLASSICAL REPAIR: separated? — **N/A — none used**

No classical repair step was implemented or invoked anywhere in Phase 3. Every reported "feasible" result is the solver's raw output decoding as feasible on its own — never a repaired infeasible solution relabeled feasible. This was verified directly: `repair_used` is `False` on all 76 results in `routing_results.json` (checked, not assumed — see verification command in `docs/PHASE_3_REPORT.md` §14). CLAUDE.md §24's optional hybrid-repair experiment was not attempted this phase (documented as future work in the Phase 3 report, not silently skipped).

## HARDWARE: documented? — **YES**

`platform.system()`/`platform.machine()`/`platform.processor()` captured in every `RoutingManifest` — this environment: Windows AMD64, AMD64 Family 25 Model 117 Stepping 2 (AuthenticAMD). No GPU or specialized hardware used for any solver.

## SIMULATOR: documented? — **YES**

Annealing: `dwave.samplers.SimulatedAnnealingSampler` (classical CPU) — labeled `SIMULATED ANNEALING` everywhere, never "hardware." No D-Wave Leap credentials exist in this environment (verified directly: no `DWAVE_API_TOKEN`/`DWAVE_API_KEY` env vars, no `~/.config/dwave` file, `Client.from_config()` raises "API token not defined"). QAOA: `qiskit.primitives.StatevectorSampler` — noiseless, shot-sampled (1024 shots), explicitly not Aer hardware-noise simulation (that's Phase 4's job) and explicitly not real quantum hardware.

## QUBO PENALTIES: documented? — **YES, including a real correction**

Full mathematical derivation in `qsci_core/optimization/quantum/qubo_formulator.py`'s docstring. The initial derivation (penalty scaled only against the objective) was found wrong via the mandated brute-force validation step — it allowed a degenerate optimum (double-assignment + omission) that decoded as infeasible. Fixed derivation (penalty also dominates the capacity penalty's own maximum magnitude) verified against both the original failing case and the original hand-crafted validation case; a 4-point penalty-multiplier sensitivity study (1x/2x/5x/10x) confirms the fix is stable across a 10x range, not a narrow escape. Full account in `docs/PHASE_3_REPORT.md` §9.

## STATISTICAL PROCEDURE: documented? — **YES**

10 independent seeds per (solver, N) configuration where computationally feasible (all annealing and QAOA-at-N=4 configurations). Reported: feasibility count, best/mean/std of feasible-run costs, gap vs. the OR-Tools-on-QUBO reference. QAOA statistics exist only at N=4 — N≥6 explicitly marked PENDING (not silently omitted) given the measured runtime wall documented in `docs/PHASE_3_REPORT.md` §18. No statistical test (e.g. Wilcoxon) was applied to the cost differences because, at N∈{4,6,8}, annealing's best-of-10 exactly matches OR-Tools' proven optimum with zero variance in the feasible-run costs — there is no distribution to test against.

## Overall fairness verdict

**Fully fair within the Phase 3 scaling experiment** (all three solvers, same problem, same conditions, same postprocessing). **Explicitly NOT a fair comparison, and not presented as one**, between Phase 1's native-VRP OR-Tools baseline and the QUBO-based quantum/annealing/OR-Tools-on-QUBO tracks — these solve different, disclosed problem formulations, reported side by side rather than merged into one misleading number.
