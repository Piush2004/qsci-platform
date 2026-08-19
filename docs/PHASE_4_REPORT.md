# Phase 4 — Noise & Scalability

Status: **COMPLETE**
Date: 2026-08-19

## 1. Executive Summary

Phase 4 investigated *why* quantum and quantum-inspired routing methods hit the walls Phase 3 measured, using four bottleneck-driven diagnostics: QAOA's runtime-wall root cause, annealing's feasibility-collapse recovery, noise sensitivity at QAOA's one reliable size, and the QAOA `p=1/2/3` depth-vs-quality tradeoff. No quantum advantage is claimed anywhere in this phase. Key results: the QAOA runtime wall is execution-cost-dominated (not optimizer-dominated); annealing's feasibility collapse is a sampling artifact that substantially recovers with more `num_reads`, not a structural or hardware limitation; no noise-induced quality degradation was measured at realistic NISQ noise magnitudes on this shallow circuit (with an explicit caveat about the metric's blind spot); and deeper QAOA circuits (`p=2`, `p=3`) did not improve solution quality over `p=1` while costing substantially more runtime.

## 2. Research Question

"Where does quantum become impractical, and why?" — decomposed into: runtime scaling, quantum resource scaling, noise sensitivity, annealing feasibility, QAOA depth tradeoffs, problem-size scalability, noise-induced degradation, reproducibility, and the practical computational boundary.

## 3. Experimental Design

All four investigations reuse Phase 3's already-audited, unchanged infrastructure (`qubo_formulator.py`, `instance_builder.py`, `decoder.py`, `annealing_solver.py`) plus one real extension: `qaoa_solver.py` gained an optional `noise_preset` parameter (default `"noiseless"`, verified byte-identical to the pre-Phase-4 path — see §11) that routes through a new `qsci_core/optimization/quantum/noise_models.py` module of real `qiskit_aer.noise.NoiseModel` presets, executed via a `_TranspilingAerSampler` wrapper (Aer's compiler needs circuits pre-transpiled to its basis gates; `qiskit.primitives.StatevectorSampler` does not).

Sample sizes were reduced from Phase 3's 10 seeds to 5 for the noise-sensitivity and depth-sweep configurations — a documented wall-clock budget decision (each noisy/deep-circuit QAOA run costs tens of seconds to minutes), not a silent reduction in rigor; flagged explicitly wherever a 5-seed sample is too small to call a pattern significant.

Source: `experiments/phase4_noise_and_scaling.py` (main sweep), `experiments/phase4_consolidate_and_figures.py` (unification + figures), a small supplementary runtime-component measurement saved to `experiments/results/phase4_runtime_component_breakdown.json`.

## 4. Runtime Scaling

| N | Qubits | Circuit depth | Gates | Construction | Transpile | Single-call (mean of 5) |
|---|---|---|---|---|---|---|
| 4 | 8 | 34 | 81 | 5.1 ms | 11.6 ms | 1.53 s |
| 5 | 10 | 43 | 116 | 4.2 ms | 9.9 ms | 17.91 s |

Single-call time ratio (N5/N4): **11.71x**. Phase 3's full-optimization-run ratio (same N5/N4 comparison, 37.6s→628.9s): **16.73x**. Circuit construction and transpile are both under 15ms — negligible. A full N=4 COBYLA run (`maxiter=20`) took 36.1s over 20 function evaluations, implying ~1.81s/eval — within ~25% of the directly measured 1.53s single-call time (the remainder is `MinimumEigenOptimizer`/COBYLA bookkeeping, not a separate dominant cost).

**Conclusion: the runtime wall is execution-cost-dominated.** The single-circuit-execution-time ratio alone explains most (70%) of the full-run ratio; optimizer iteration count (fixed at `maxiter=20` regardless of N) contributes only its constant multiplicative factor, not an independent scaling problem.

## 5. QAOA Depth

| p | Feasible (of 5) | Best cost | Circuit depth | Gates | Mean runtime |
|---|---|---|---|---|---|
| 1 | 5/5 | 380.008 | 34 | 81 | 38.00s |
| 2 | 3/5 | 380.008 | 51 | 145 | 70.35s |
| 3 | 4/5 | 380.008 | 68 | 209 | 101.14s |

Every feasible run at every `p` found the identical optimum. Feasibility did not increase monotonically with depth. Runtime grew 1.85x (`p=2`) and 2.66x (`p=3`) vs. `p=1`. **"Deeper is better" is not supported by this evidence** — increasing `p` past 1 bought no measured quality improvement at substantial, monotonically growing runtime cost, on this formulation at this size.

## 6. Noise Sensitivity

| Preset | Feasible (of 5) | Best cost | Mean runtime | Quality degradation vs. noiseless |
|---|---|---|---|---|
| noiseless | 5/5 | 380.008 | 39.01s | — |
| depolarizing_low (1e-3/1e-2) | 5/5 | 380.008 | 1.04s | 0% |
| depolarizing_high (1e-2/5e-2) | 5/5 | 380.008 | 1.06s | 0% |
| readout (2%) | 5/5 | 380.008 | 1.07s | 0% |

No quality or feasibility degradation was measured. **Disclosed caveat, not glossed over**: `MinimumEigenOptimizer.solve()` reports the single best-objective sample out of 1024 shots; simple fidelity arithmetic suggests ~19% of shots survive `depolarizing_high` noise-free-equivalent on this circuit — plenty for the optimum to still appear at least once. This metric can mask real degradation of the full output *distribution* (success probability) while the reported best sample stays unaffected. A direct success-probability measurement was **not** run this phase — **PENDING**.

A separate, real, measured finding: the noisy Aer `SamplerV2` path ran **~38x faster** than the noiseless `StatevectorSampler` path for the identical circuit and shot count — a simulator-implementation artifact of this environment (Aer's compiled backend vs. Qiskit's pure-Python one), not a claim that noise itself speeds up computation.

## 7. Annealing Feasibility

| N | reads=100 | reads=500 | reads=1000 | reads=5000 |
|---|---|---|---|---|
| 8 | 80% | 100% | 100% | 100% |
| 10 | 20% | 80% | 100% | 100% |
| 12 | 0% | 20% | 20% | 60% |

Phase 3's feasibility collapse (fixed `num_reads=100`) is **sampling-related, not structural** — feasibility recovers substantially at every size with more reads, at negligible runtime cost (≤6.3s even at `num_reads=5000`, N=12). N=12's recovery is partial (60% at 5000 reads, not yet 100%) — genuinely still incomplete, not silently rounded up. No D-Wave hardware was used anywhere in this repository (verified directly in Phase 3, unchanged here) — this is entirely classical simulated annealing.

## 8. Sampling

See §7's table — same data, framed as the direct answer to "does feasibility improve with sampling": yes, monotonically (with one non-monotonic step at N=10 reads=500→1000 staying flat at 100%, expected once ceiling is reached) at every tested size.

## 9. Penalty Sensitivity

Not re-derived this phase. Phase 3 already ran a 4-point penalty-multiplier sweep (1x/2x/5x/10x) at N=4 and found cost/feasibility completely stable across the range (`experiments/results/routing_penalty_sensitivity.json`). Phase 4's findings (annealing collapse being sampling-, not penalty-, related; noise not measurably affecting the best-of-shots result) do not surface a new penalty question this formulation didn't already answer.

## 10. Resource Scaling

QUBO variables (=qubits) grow as `N*K`, `K=ceil(N/2)`: N=4→8, N=5→10 (K=2 diagnostic, not the default K=3), N=6→18, N=8→32, N=10→50, N=12→72, N=16→128 (unchanged from Phase 3). Circuit depth/gate count grew ~1.26x/1.43x from N=4→N=5 (34→43 depth, 81→116 gates) — far more modestly than the 11.71x single-call runtime growth over the same step. **Observed runtime grew approximately 11.7-fold over this one-customer increment** — steeper than the ~1.3x depth/gate growth, consistent with (not formally proven as) state-space-size scaling (`O(2^qubits)`) dominating over circuit-structure growth. This is an empirical observation over 2 measured points, not a formally derived complexity claim.

## 11. Reproducibility

Two representative 5-seed configurations (annealing N=8/`reads=100`; QAOA N=4/`p=1`/noiseless) both show **zero cost variance among feasible runs** — every feasible run found the identical optimal cost, cross-checked against Phase 3's original 10-seed runs at the same configs (same pattern: annealing 9/10 feasible in Phase 3 vs. 4/5 here, QAOA 8/10 vs. 5/5 here — both differences consistent with ordinary sampling variance at a reduced-reads/small-sample regime, not a regression). **Feasibility is the unstable quantity; solution quality, when feasible, is stable.**

Default noiseless-path regression check: `solve_qubo_with_qaoa(..., noise_preset="noiseless")` produces byte-identical sample/energy to the pre-Phase-4 call signature (no `noise_preset` kwarg at all) — verified in `tests/test_qaoa_noise.py::test_qaoa_noiseless_default_unchanged`. All 5 pre-existing `tests/test_qaoa_solver.py` tests still pass unmodified.

## 12. Practical Scalability Boundary

QAOA (this environment, `StatevectorSampler` path): statistically reliable only at N=4 (8 qubits). N=5 (10 qubits) costs ~629s for a *single* run (Phase 3); this phase's diagnostic shows a single circuit execution alone already costs ~17.9s at N=5. The Aer-backed noisy path was ~38x faster per-call at the *same* N=4 size — suggesting part of this boundary is a simulator-choice artifact of the `StatevectorSampler` path specifically, not an inherent property of QAOA at 8-10 qubits in general. Not re-tested at N≥5 with the Aer path this phase — **PENDING**, a natural Phase 5 candidate.

Simulated annealing: no qubit ceiling (classical CPU). With adequate `num_reads`, practically solvable through N=10 (100% feasible) and partially N=12 (60% feasible) — all under 10 seconds/run. The hard boundary past N=12, if one exists, is uncharacterized (untested at higher `num_reads`).

## 13. Key Findings

1. QAOA's runtime wall is execution-cost-dominated (§4).
2. Annealing's feasibility collapse is sampling-related and substantially recoverable (§7).
3. Increasing QAOA depth (p=2, p=3) does not improve solution quality over p=1 on this formulation (§5).
4. The Aer-vs-StatevectorSampler ~38x runtime gap suggests QAOA's measured impracticality is partly a simulator-implementation artifact, not solely an algorithmic property (§6, §12).

## 14. Negative Findings

- Deeper QAOA circuits did not produce better solutions and did not monotonically improve feasibility (§5) — a negative result for the "more expressive ansatz helps" intuition, reported as such.
- No noise-robustness claim survives scrutiny of the best-of-shots metric used (§6) — the headline "0% degradation" number is disclosed as likely an artifact of the metric, not evidence QAOA tolerates noise well.
- Annealing's N=12 recovery remains incomplete (60%, not 100%) even at 5000 reads (§7) — a real, unresolved limitation, not silently omitted.

## 15. Limitations

See notebook §14 (`notebooks/06_noise_and_scalability.ipynb`) for the full list: reduced 5-seed samples throughout; noise-sensitivity metric blind spot (§6); QAOA statistics still exist only at N=4; annealing N=12 recovery is partial; no real D-Wave QPU or real quantum hardware was used anywhere in this phase.

## 16. RQ6 Implications

Phase 4 does not overturn Phase 3's RQ6 conclusion (H5 unsupported) — it refines *why* the walls appear where they do. Some of what looked like a hard quantum/quantum-inspired ceiling in Phase 3 (annealing's feasibility collapse) is shown here to be a fixable configuration artifact rather than a structural limit; other walls (QAOA's per-shot execution cost) are shown to be real and substantial, though partly simulator-implementation-dependent rather than purely algorithmic. Neither refinement establishes a quantum advantage on any measured dimension.

## 17. Phase 5 Recommendation

Phase 5 (Business-Impact Benchmark) should treat as open, testable candidates rather than settled facts: (a) whether the Aer noisy/noiseless path materially changes QAOA's practical qubit ceiling if re-run at N≥5, (b) whether annealing's N=12 feasibility gap closes with `num_reads > 5000`, and (c) whether a direct success-probability measurement (not just best-of-shots) reveals real noise-induced degradation this phase's metric missed. None of these block Phase 5 from proceeding — they are refinements a reviewer would ask about, not blockers.
