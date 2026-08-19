# Classical vs. Quantum Comparison Audit — Notebook 07

Status: **COMPLETE**
Date: 2026-08-19
Scope: audits `notebooks/07_classical_vs_quantum_comparison.ipynb` before its results are accepted as this repo's synthesis conclusion, per CLAUDE.md's non-negotiable rules (§1) and the explicit instruction that this notebook must not be marketing theater.

## 1. Provenance check — does every number trace to a real source?

Every quantitative claim in the notebook loads from one of four files, all produced by prior, already-audited phases:

- `experiments/results/phase2_1_leakage_free_results.json` — regenerated live in this task by re-running `experiments/phase2_1_supplementary_analysis.py` (added JSON output as part of this task), not hand-typed. Fresh values differ slightly from the numbers originally printed in the Phase 2.1 audit doc due to VQR's documented non-determinism (COBYLA + statevector sampling) — same qualitative pattern, real re-execution, not stale citation.
- `experiments/results/quantum_forecasting_results.json` — Phase 2's original, committed, leakage-affected run. Used exactly once, explicitly labeled `"FLAWED - DO NOT USE FOR CONCLUSIONS"` / `status="FLAWED"` in every table it appears in.
- `experiments/results/routing_results.json` — Phase 3's committed 76-row scaling experiment, already fairness-audited (`docs/PHASE_3_FAIRNESS_AUDIT.md`).
- `experiments/results/routing_penalty_sensitivity.json` — Phase 3's penalty-multiplier sweep.

No result in Sections 5-30 is a hardcoded literal copied from a prior report — every printed number is either loaded from these JSON files or computed live, in-notebook, from them (DM test, gap%, feasibility rates, scorecard, complexity LOC counts). Verified by inspecting every code cell's source for bare numeric literals used as *results* (as opposed to configuration constants like `GLOBAL_SEED = 42`, penalty multipliers being swept, or plotting cosmetics) — none found.

## 2. Leakage-correction discipline (the Phase 2.1 lesson, applied)

The notebook's own text states the rule at the top (cell `db1fce50`) and follows it: Section 5 (`992a456b`) loads both the original and corrected VQR numbers side by side, with the original rows carrying `status="FLAWED - DO NOT USE FOR CONCLUSIONS"`. Every downstream computation that treats VQR as "quantum's forecasting result" — Section 6 metrics, Section 7 DM test, Section 8 figures, Section 10 speedup analysis, Section 23 scorecard, Section 24 advantage table, Section 30 conclusion — reads from `leakage_free["leakage_free_vqr"]`, never from `phase2_original`. Verified by grep: `phase2_original` is referenced only in the Section 5 display table and the Section 9 resource-metadata join (circuit depth/gate count, which are unaffected by the leakage bug since it only affected test-time feature construction, not the trained circuit).

## 3. Banned-claim scan

Grepped the notebook's full extracted source (`nbconvert`-independent, direct cell-source concatenation) for: "quantum advantage", "quantum is better/faster/more accurate", "production ready", "quantum speedup", "all tests pass", "fake"/"placeholder"/"dummy"/"mock_", "real quantum hardware" (as an unqualified positive claim). Matches found were all legitimate, neutral section headers ("Section 24 — Quantum Advantage *Analysis*", "Section 25-27 — Where Quantum *Is* Better...") or explicit disclaimers ("this is Aer STATEVECTOR SIMULATOR runtime, **not** real quantum hardware execution time") — no unqualified advantage claim exists anywhere in the notebook.

## 4. Statistical honesty

- Forecasting: Diebold-Mariano test (Section 7) run live against a freshly-recomputed classical baseline (not re-cited). Result: **not significant** at n=14 for all 3 VQR configurations (p=0.14–0.20). The notebook states this plainly and does not use "wMAPE is numerically lower/higher" language to imply significance it didn't measure.
- Routing: Section 20 attempts a Mann-Whitney U test between QAOA and annealing feasible-cost distributions at N=4; where a distribution turned out degenerate (annealing's feasible costs are a single value, zero variance), the notebook states this directly instead of forcing a test onto a constant, matching the Phase 3 fairness audit's own finding.
- The master scorecard (Section 23) assigns `"Classical (not statistically distinguishable)"` rather than a bare `"Classical"` win where the DM test found no significance — the low-power caveat survives into the scorecard rather than being silently dropped a layer up.

## 5. Fairness contract adherence

Section 4's `fairness_contract` dict documents the actual shared conditions (dataset, split, seeds, config) for both forecasting and routing, sourced from the already-audited Phase 2/2.1/3 code — not aspirational. It explicitly flags the one known confound (Phase 2's bounded 18-row training window applied to both classical and quantum for tractability, not Phase 1's full-history window) rather than hiding it. The forecasting scorecard entry compares corrected VQR against **full-history** LightGBM (the strongest fair classical reference), and the notebook shows the bounded-window classical number too, so a reader can see both framings.

## 6. Disclosed gaps (not silently omitted)

- QAOA has zero data at N∈{6,8,10,12,16} — stated explicitly wherever QAOA scaling is discussed (Sections 12, 16, 24, 29), not extrapolated or interpolated.
- QAOA circuit depth is measured only at p=1 — p=2,3 explicitly marked not run (Section 20's `qaoa_depth_analysis.pdf` figure caption states this directly on the chart itself).
- Business-impact dollar figures (Section 22) are explicitly labeled ILLUSTRATIVE throughout, per CLAUDE.md §5 — no public per-unit cost data exists for either dataset.
- The QUBO-based routing comparison and Phase 1's native-VRP OR-Tools baseline are never merged into one number — Section 4 states this is "documented as a difference, not presented as a fair head-to-head," inherited directly from the Phase 3 fairness audit's own finding.

## 7. Reproducibility

- `GLOBAL_SEED = 42` set once in Section 0 and reused everywhere seeding is under this notebook's control (the live LightGBM/DM-test recomputation). VQR/QAOA/annealing seeds are the ones already recorded per-run in the source JSON files (not re-seeded here).
- Section 0 prints exact package versions, git commit, and hardware. Section 34 additionally persists this to `experiments/results/classical_vs_quantum_repro_metadata.json`.
- The notebook was executed top-to-bottom via `nbconvert --execute` three separate times during construction (after each major block) and once fully at the end — **0 errors** across all runs, verified programmatically (`output_type == 'error'` scan across all cells), not by eyeballing.

## 8. Test suite

Full `pytest` run (168 tests): **168 passed, 1 xfailed** (the pre-existing, documented xfail from earlier phases), 0 failures, in 157.05s. No test was modified to force a pass as part of this task.

## 9. Artifacts produced

- `experiments/results/classical_vs_quantum_results.{json,csv}` — unified per-row schema (experiment/dataset/instance/method/algorithm/seed/problem_size/metric/value/unit/runtime/qubits/depth/gates/shots/feasible/reference/gap/status/label) covering every forecasting and routing result used in the notebook.
- `experiments/results/table1_forecast_comparison.csv` through `table8_master_scorecard.csv` — 8 publication tables, saved verbatim from the notebook's own dataframes.
- `experiments/results/classical_vs_quantum_repro_metadata.json` — consolidated reproducibility record.
- 10 PDF figures in `paper/figures/`: `forecast_accuracy_comparison`, `forecast_runtime_comparison`, `quantum_resource_scaling`, `routing_cost_comparison`, `routing_gap_comparison`, `routing_runtime_scaling`, `qubit_scaling`, `qaoa_depth_analysis`, `feasibility_comparison`, `classical_vs_quantum_summary` — all confirmed present on disk by the notebook's own Section 32 assertion (not just "the code that saves them ran").

## 10. Overall audit verdict

**PASS.** No fabricated claim, no silent extrapolation, no stale-number reuse, and no reframing of a negative result as a partial win was found. The notebook's own Section 30 conclusion — that classical outperforms or ties quantum on every measured dimension except one narrow routing-runtime case at the smallest tested problem size (N=4, where simulated annealing's `num_reads=100` sampler happened to run faster than OR-Tools' CP-SAT solve) — is consistent with the underlying data traced above and is not softened or oversold anywhere in the surrounding prose.
