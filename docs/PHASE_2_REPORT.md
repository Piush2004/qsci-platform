# Phase 2 Report — Quantum Forecasting

Status: **COMPLETE — RESEARCH RESULT, NOT YET COMMITTED**
Date: 2026-08-19
Branch: `main`

## 1. Research Question

**RQ1**: Under identical data, feature, split, horizon, and evaluation conditions, does a NISQ-era variational quantum regressor (VQR) provide useful forecasting performance compared with the classical LightGBM baseline established in Phase 1?

## 2. Hypothesis

**H1**: Classical production-grade models are expected to outperform current QML approaches on this data under realistic computational constraints. Classical winning is the expected, acceptable outcome — this phase does not optimize the experiment to make quantum look better, and does not tune until quantum wins if it doesn't.

## 3. Experimental Design

Both tracks share: series (`FOODS_3_090_CA_1_evaluation`), test window (2016-05-09 to 2016-05-22, 14 days — identical to Phase 1 notebook 02's last backtest fold), feature engineering (`qsci_core.forecasting.classical.features.build_features` — 12 lag/rolling/calendar columns), seed (42), and evaluation metrics (RMSE, MAE, wMAPE, bias).

**Documented, unavoidable deviation from Phase 1**: Phase 1's classical backtest trained on the full multi-year history available before each fold. VQR training via COBYLA on a statevector simulator cannot tractably consume that much data — see §7 for the measured cost. Both tracks in Phase 2 therefore use the **same bounded 18-row training window** (2016-04-21 to 2016-05-08) instead. This keeps the comparison fair between the two tracks (identical data), while being a much smaller-scale evaluation than Phase 1's — disclosed here, not hidden.

## 4. Dataset

M5 Forecasting – Accuracy, series `FOODS_3_090_CA_1_evaluation` (same series Phase 1 used). Real data, verified in Phase 0.

## 5. Classical Baseline (re-run under Phase 2's bounded-window conditions)

| Model | RMSE | MAE | wMAPE | Bias |
|---|---|---|---|---|
| Seasonal-naive | 24.50 | 19.93 | **37.15%** | 15.50 |
| LightGBM (p50) | 28.78 | 24.36 | **45.41%** | 22.85 |

Note: LightGBM underperforms seasonal-naive here — a real, honest finding, not an error. LightGBM is a data-hungry model; 18 training rows (bounded for quantum comparability, see §3) is far below what it needs, and its high positive bias (+22.85) indicates systematic over-forecasting from an undertrained model. Phase 1's full-history LightGBM result (wMAPE 24.20%, beating seasonal-naive) stands on its own and is not contradicted by this — they are different, disclosed experimental conditions.

## 6. Quantum Architecture

Per CLAUDE.md §6: `zz_feature_map` (ZZFeatureMap, reps=1) encoding → `real_amplitudes` (reps=1) variational ansatz → `EstimatorQNN` (wrapped by `qiskit_machine_learning.algorithms.VQR`) → forecast. Optimizer: COBYLA. Simulator: `qiskit_aer.AerSimulator(method="statevector")`, noiseless — exact expectation value (`default_precision=0.0`, no shot sampling; shot-based/noisy simulation is Phase 4's job, not mixed in here).

**Installed-API adaptation** (qiskit 2.5.2 / qiskit-machine-learning 0.9.0, verified against actually-installed versions, not assumed):
- Class-based `ZZFeatureMap`/`RealAmplitudes` are deprecated in favor of function-based `zz_feature_map`/`real_amplitudes`.
- Aer's `EstimatorV2` raises `AerError: unknown instruction` on raw blueprint-circuit output — requires a `pass_manager` (built via `generate_preset_pass_manager`) for pre-transpilation. `VQR`'s `pass_manager` argument, and `EstimatorQNN`'s own `pass_manager` argument, both need it (a partial fix — passing it only to one still leaves the other non-deterministic, see §9).

## 7. Feature Reduction

`qsci_core/forecasting/quantum/feature_reduction.py`: `StandardScaler` + `PCA`, both fit on `X_train` only. Leakage-safety is enforced structurally (raises if `n_components > n_samples`) and tested (`test_reduce_features_fit_only_on_train_not_test` asserts perturbing the test set never changes the fitted train transform).

Explained variance captured at each N (real, measured):

| N | Explained variance (cumulative) |
|---|---|
| 4 | 88.2% |
| 8 | 98.7% |
| 12 | 100.0% |

## 8. Experimental Configurations & Results

| Model | N | Qubits | Circuit depth | Gates | Params | Optimizer nfev | Train time | Predict time | RMSE | MAE | wMAPE | Bias |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Seasonal-naive | — | — | — | — | — | — | ~0s | ~0s | 24.50 | 19.93 | 37.15% | 15.50 |
| LightGBM (p50) | 12 (raw features) | — | — | — | — | — | 5.9s | 0.13s | 28.78 | 24.36 | 45.41% | 22.85 |
| VQR | 4 | 4 | 22 | 37 | 8 | 10 | 1.6s | 0.15s | 20.51 | 16.89 | **31.49%** | 10.57 |
| VQR | 8 | 8 | 50 | 123 | 16 | 18 | 17.3s | 0.79s | 23.24 | 19.46 | 36.27% | 15.60 |
| VQR | 12 | 12 | 78 | 257 | 24 | 26 | **502.2s** | 12.4s | 21.77 | 17.92 | 33.41% | 14.58 |
| VQR | 16 | 16 | — | — | 32 | — | **PENDING** | — | — | — | — | — |

Shots for all VQR runs: `N/A (exact statevector expectation, default_precision=0.0)` — genuinely not applicable, not an omitted measurement.

Full machine-readable results: `experiments/results/quantum_forecasting_results.json` / `.csv`. Manifest: `experiments/results/quantum_forecasting_manifest.json`.

## 9. Statistical Analysis — Diebold-Mariano

All 10 pairwise comparisons (naive, LightGBM, VQR-4, VQR-8, VQR-12) computed for real (`qsci_core/evaluation/dm_test.py`), Harvey-Leybourne-Newbold small-sample correction applied. **None were significant at α=0.05** — with only 14 test observations, this is expected and reported honestly rather than overstated:

| Comparison | DM statistic | p-value | Significant? |
|---|---|---|---|
| LightGBM vs. best quantum (N=4) | 1.281 | 0.2227 | No |
| Seasonal-naive vs. LightGBM | -1.809 | 0.0936 | No |
| Seasonal-naive vs. VQR-4 | 0.597 | 0.5606 | No |
| Seasonal-naive vs. VQR-8 | 0.216 | 0.8320 | No |
| Seasonal-naive vs. VQR-12 | 0.478 | 0.6403 | No |
| LightGBM vs. VQR-8 | 1.034 | 0.3198 | No |
| LightGBM vs. VQR-12 | 1.315 | 0.2112 | No |
| VQR-4 vs. VQR-8 | -0.794 | 0.4413 | No |
| VQR-4 vs. VQR-12 | -0.426 | 0.6773 | No |
| VQR-8 vs. VQR-12 | 1.750 | 0.1037 | No |

**None of the accuracy differences observed in this run are statistically distinguishable from noise at n=14.** This is the single most important caveat on every number in §8 — see §14.

## 10. Runtime Analysis

Training time scales worse than linearly with qubit/parameter count on this environment (Python 3.14, qiskit-aer 0.17.2):

| N (qubits) | Parameters | Train time | Ratio vs. N=4 |
|---|---|---|---|
| 4 | 8 | 1.6s | 1.0x |
| 8 | 16 | 17.3s | 10.8x |
| 12 | 24 | 502.2s | 313x |
| 16 | 32 | PENDING (exceeded a 10-minute isolated diagnostic budget across 4 independent attempts) | — |

This is a real, measured finding, distinguishing three components:
- **Classical preprocessing** (feature engineering, PCA): milliseconds, negligible.
- **Quantum simulation** (Aer statevector execution): fast in isolation — a single fixed-parameter circuit evaluation at N=16 measured 0.148s.
- **Algorithmic/optimizer execution**: this is where the cost concentrates. COBYLA's initial simplex construction alone requires `num_parameters + 2` function evaluations (confirmed via a `UserWarning: COBYLA: Invalid MAXFUN` at every N), and each evaluation costs a full batched forward pass over all training samples. This explains *some* superlinear growth, but not all of it — see §13's diagnosis of N=16 specifically.

Simulator runtime is never reported as "quantum hardware runtime" — every result in §8 explicitly labels its simulator (`qiskit_aer.AerSimulator(method=statevector)`).

## 11. Circuit Complexity

Circuit depth and gate count both scale as expected with N for this architecture (ZZFeatureMap's O(N²) pairwise entangling terms dominate):

| N | Depth | Gates | Gates/qubit |
|---|---|---|---|
| 4 | 22 | 37 | 9.25 |
| 8 | 50 | 123 | 15.4 |
| 12 | 78 | 257 | 21.4 |

## 12. N=16: Diagnosed, Not Faked

Per CLAUDE.md §14 ("If VQR/EstimatorQNN cannot execute correctly: STOP and diagnose it. Do not replace it with a fake quantum calculation"), N=16 was investigated in depth before being excluded from the notebook's live run:

1. **Isolated circuit construction/transpilation**: fast (<0.2s) at N=16 — not the bottleneck.
2. **Isolated a single fixed-parameter Aer evaluation**: fast (0.148s) at N=16 — not the bottleneck.
3. **Isolated COBYLA itself** on a pure-Python deterministic objective: fast, deterministic — not the bottleneck.
4. **Full `VQR.fit()` at N=16**: four independent attempts (COBYLA maxiter=5, COBYLA maxiter=15 with `ansatz_reps=0`, SPSA maxiter=15, and a live-callback-instrumented trace) — none completed within budgets ranging from 3 to 10 minutes, despite N=12 (fewer parameters: 24 vs. 32) completing in 148–502s.
5. **A live-callback trace** confirmed all setup steps (data prep, circuit construction, pass-manager transpilation, VQR object construction) complete in under 0.2s — the stall is entirely inside the optimization loop, before the first callback fires.

This scaling (N=12 tractable in minutes, N=16 not completing in 10+ minutes despite only 8 more parameters) is worse than the `num_parameters`-driven explanation in §10 alone predicts, and was not fully resolved. It is reported as **PENDING**, with the diagnostic trail above, rather than silently dropped or faked with placeholder numbers.

## 13. Additional Diagnosed Issue: Batched Execution Non-Determinism

While diagnosing reproducibility (`tests/test_quantum_vqr_forecaster.py`), a separate, real issue was found and isolated: `qiskit_aer.primitives.EstimatorV2`, when executing a **batch** of pubs (which is what `EstimatorQNN.forward` does over a training/prediction set), returns run-to-run varying expectation values — even with `algorithm_globals.random_seed`, `AerSimulator(seed_simulator=...)`, and `seed_transpiler` all fixed, and `default_precision=0.0` (nominally exact statevector, no shot sampling). Isolated down to repeated `.predict()` calls on the **same already-fitted model** (no training/optimizer involvement at all) — single-pub raw `estimator.run()` calls and COBYLA itself were separately verified fully deterministic. This is documented in the module docstring and captured as a strict `xfail` test (`test_reproducibility_predictions_same_seed_same_predictions`) rather than deleted or hidden.

**Practical consequence**: every number in §8 should be read as one representative run of the quantum track, not a bit-exact reproducible value. Structural properties (circuit depth, gate count, parameter count) ARE fully reproducible — verified in `test_reproducibility_circuit_structure_is_deterministic`.

## 14. Limitations

- Single series, single train/test split — not a claim about performance across the M5 panel or across multiple resamples.
- 18 training rows / 14 test rows — small by both classical and quantum-research standards, necessitated by quantum tractability.
- 10 COBYLA iterations — small; higher-N configs' initial simplex alone consumes most or all of this budget (N=12's `nfev=26` exceeds the requested `maxiter=10`, since scipy auto-raises `maxfun` to at least `num_vars + 2`).
- No statistically significant result in either direction (§9) — the numeric ranking in §8 should not be read as a proven effect.
- Run-to-run instability (§13) means a repeat of this exact notebook would likely produce somewhat different numbers, though the same qualitative pattern (no significant difference at n=14) is expected to hold.
- N=16 incomplete (§12) — a real gap against the full N∈{4,8,12,16} spec, honestly reported rather than backfilled with a fabricated number.

## 15. Was H1 Supported?

**Not on this run** — the best quantum configuration (N=4, wMAPE 31.49%) numerically outperformed classical LightGBM (wMAPE 45.41%) under these bounded-window conditions. However:

1. The DM test found this difference **not statistically significant** (p=0.22, n=14) — H1 is not *rejected* with confidence either; the honest conclusion is **inconclusive at this sample size**.
2. LightGBM's poor showing here is very plausibly a **confound of the small training window** (18 rows) forced by quantum tractability, not evidence that LightGBM is a worse model in general — Phase 1's same LightGBM architecture, given its normal full-history training data, beat seasonal-naive by a wide margin (wMAPE 24.20% vs. 33.49%, FVA +28.1%).
3. Per CLAUDE.md §1, this contradiction-to-expectation is reported as-is, not adjusted to protect H1. It is also not overstated as "quantum wins" — the correct, evidence-supported statement is: *under the evaluated NISQ simulation conditions, at this very small sample size, no statistically significant difference between classical and quantum forecasting was established; the classical model's baseline was itself constrained in a way that likely disadvantaged it.*

## 16. What This Means for QSCI

This result does not establish quantum forecasting as viable or non-viable for QSCI — the sample size, training-window constraint, and unresolved N=16/reproducibility issues mean this is a preliminary RESEARCH data point, not a production signal. What it does establish, concretely:
- The VQR architecture from CLAUDE.md §6 is implemented correctly and runs on real M5 data end to end (N=4, 8, 12).
- A real, fair, leakage-safe, statistically-tested comparison methodology now exists in `qsci_core` (feature reduction, DM test, experiment manifest/results schema) that Phase 5's business-impact benchmark can reuse directly.
- Two concrete, diagnosed engineering findings (N=16 runtime wall, batched-execution non-determinism) are exactly the kind of "where quantum stops being practical" evidence CLAUDE.md §6 asks for — surfaced honestly rather than hidden, and directly relevant to Phase 4's noise/scalability study.

## 17. Reproducibility Information

- Manifest: `experiments/results/quantum_forecasting_manifest.json` (dataset, series, split, seed, feature columns, software versions, hardware, simulator, git commit).
- Software versions (real, captured by the manifest, not hand-typed): qiskit 2.5.2, qiskit-machine-learning 0.9.0, qiskit-aer 0.17.2, lightgbm 4.7.0, scikit-learn 1.9.0, numpy 2.5.2, pandas 2.3.3.
- Hardware: Windows AMD64, AMD64 Family 25 Model 117 Stepping 2 (AuthenticAMD).
- Caveat: exact numeric reproducibility is NOT guaranteed given §13's diagnosed batched-execution instability — re-running will very likely produce different exact numbers with the same qualitative pattern.

## 18. Known Issues (summary)

1. N=16 does not complete within a practical (10+ minute) runtime budget on this environment — diagnosed, not resolved (§12).
2. `EstimatorV2` batched execution is non-deterministic run-to-run despite full RNG seeding — diagnosed, not resolved (§13).
3. `pd.Timedelta(days=1)` deprecation warning from pandas 2.3.3/numpy 2.x internals (same as Phase 1, unrelated to quantum code) — cosmetic, not a correctness issue.
4. LightGBM's bounded-window result (§5) should not be confused with or cited against Phase 1's full-history result — different, disclosed conditions.

## 19. Acceptance Criteria

| Criterion | Result |
|---|---|
| Quantum forecasting implementation exists | ✅ `qsci_core/forecasting/quantum/` |
| Qiskit circuit executes | ✅ N=4, 8, 12 real executions |
| Feature reduction is leakage-safe | ✅ enforced + tested |
| Same temporal split as classical baseline | ✅ identical test window to Phase 1's last fold |
| Seasonal-naive baseline included | ✅ |
| LightGBM baseline included | ✅ |
| Quantum VQR included | ✅ |
| RMSE/MAE/wMAPE/Bias calculated | ✅ |
| Runtime measured | ✅ training/inference split out |
| Qubit count / circuit depth / gate count recorded | ✅ |
| Shots recorded where applicable | ✅ (`N/A`, genuinely not applicable) |
| Statistical comparison performed where valid | ✅ 10 DM tests, all correctly reported as non-significant |
| Experiment manifest created | ✅ |
| Results saved to machine-readable files | ✅ JSON + CSV |
| Notebook executes top-to-bottom | ✅ |
| Quantum tests pass | ✅ 41/42 (1 documented, diagnosed `xfail`) |
| Phase 1 tests still pass | ✅ |
| No fabricated metrics | ✅ N=16 reported PENDING, not fabricated |
| No quantum advantage claim without evidence | ✅ §15 explicitly avoids this |
