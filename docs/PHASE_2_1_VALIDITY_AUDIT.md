# Phase 2.1 — Quantum Forecasting Research Validity Audit

Status: **COMPLETE**
Date: 2026-08-19
Branch: `main`
Scope: audits Phase 2 (commit `6b1b28a`). **Does not modify or replace Phase 2's committed results.**

## 1. Purpose

Determine whether the Phase 2 quantum-vs-classical forecasting comparison supports a defensible scientific conclusion, or whether confounds in its design undermine the headline "H1 not supported on this run" reading. Short answer: **a real, previously undiagnosed confound was found (§5) that materially changes the correct interpretation.** The corrected picture is in §10.

## 2. Original Experiment (unchanged, for reference)

Phase 2 (commit `6b1b28a`) compared seasonal-naive, LightGBM, and VQR (N=4/8/12) on `FOODS_3_090_CA_1_evaluation`, test window 2016-05-09→2016-05-22, both classical and quantum retrained on an 18-row bounded window for fairness between the two tracks. Result: VQR-4 (wMAPE 31.49%) numerically beat bounded-window LightGBM (wMAPE 45.41%), but the DM test found this not significant (p=0.22, n=14).

## 3. Training-Window Confound — Supplementary Baseline Analysis

**Real, computed evidence, not re-run of Phase 2** — Phase 1's rolling-origin backtest (`notebooks/02_classical_forecasting.ipynb`, already committed at `442dbf9`) has a fold whose test window is *exactly* 2016-05-09→2016-05-22 — identical to Phase 2's. This gives a clean same-window, different-training-size comparison for free, no new training needed:

| Model | Training data | wMAPE | RMSE | Source |
|---|---|---|---|---|
| **A. LightGBM, full history** | ~1,875 days (all history before 2016-05-09) | **25.56%** | 18.08 | Phase 1, fold 4 (committed) |
| **B. LightGBM, quantum-compatible window** | 18 days | 45.41% | 28.78 | Phase 2 (committed) |
| **C. Seasonal-naive** | last 7 days only (window size irrelevant) | 37.15% | 24.50 | Phase 1 fold 4 *and* Phase 2 — identical numbers, confirming consistency |
| **D. VQR (as originally reported in Phase 2)** | 18 days | 31.49% (N=4) / 36.27% (N=8) / 33.41% (N=12) | 20.51 / 23.24 / 21.77 | Phase 2 (committed) — **see §5, this number is contaminated by feature leakage** |

**Finding**: Full-history LightGBM (A) is the best model on this exact test window by a wide margin — better than seasonal-naive, better than every quantum configuration Phase 2 reported. The Phase 2 narrative that quantum "wasn't beaten by classical" only holds against the artificially data-starved LightGBM (B), not against classical's real capability (A). This alone is enough to substantially qualify Phase 2's conclusion, before even considering §5.

Seasonal-naive's identical numbers in both A/Phase-1 and Phase-2 columns is a useful internal consistency check: seasonal-naive only needs 7 days of history, so the bounded window vs. full history genuinely makes no difference for it — as expected, and confirms the two experiments' test-window/data pipeline are aligned.

## 4. Feature Fairness Audit

Checked against CLAUDE.md's requirements (same target, horizon, temporal boundary, feature information, no leakage, same normalization principles, PCA fit on train only):

| Requirement | LightGBM (Phase 2) | VQR (Phase 2, as committed) |
|---|---|---|
| Same target | ✅ `sales` | ✅ `sales` |
| Same forecast horizon | ✅ 14 days | ✅ 14 days |
| Same temporal boundary (train < test) | ✅ | ✅ for training features |
| Same underlying feature set | ✅ `qsci_core.forecasting.classical.features` (12 columns) | ✅ same 12 columns, PCA-reduced |
| PCA/scaler fit on train only | N/A (LightGBM doesn't reduce dimensions) | ✅ `reduce_features_pca` — enforced, tested (`test_reduce_features_fit_only_on_train_not_test`) |
| Same normalization principle | Raw features (tree model, scale-invariant) | StandardScaler + PCA + MinMax to `[0, π]` — unavoidable, quantum encoding requires bounded ranges; documented in `vqr_forecaster.py` |
| **No future leakage at inference time** | ✅ recursive prediction — each step's lag features come from real history or the model's own prior predictions, never real future actuals (`LightGBMQuantileForecaster.predict()`'s `_next_step_features`) | ❌ **FAILS — see §5** |

## 5. Critical Finding: Test-Set Feature Leakage in the Quantum Track

**This was not identified in Phase 2. It is the single most important finding of this audit.**

Notebook 03 built test-set features like this:

```python
feat_all = build_features(windowed, "date", "sales")   # windowed includes REAL test-period actuals
test_feat = feat_all[(feat_all["date"] >= TEST_START) & (feat_all["date"] <= TEST_END)]
X_test = test_feat[cols].to_numpy()
```

`build_features` computes `lag_1`, `lag_7`, `rollmean_7`, etc. via `.shift()` on the `sales` column of whatever dataframe it's given. Because `windowed` includes the real actual sales for the *entire* test period (not just training), `test_feat`'s lag/rolling features for test day 2 onward are built from **real actual sales of earlier test days** — information a genuine forecast, issued 14 days ahead, would not have.

**Empirically verified** (not just theorized) — real output from `qsci_core.data.loaders` + `build_features`:

```
      date  sales  lag_1  lag_7
2016-05-09   72.0   77.0   59.0   <- lag_1 = 77.0, the last real TRAINING day. Fine, no leakage.
2016-05-10   46.0   72.0   35.0   <- lag_1 = 72.0 = the REAL actual sales value for 2016-05-09 (a TEST day)
2016-05-11   30.0   46.0   47.0   <- lag_1 = 46.0 = the REAL actual sales value for 2016-05-10 (a TEST day)
...
```

From test day 2 onward, `lag_1` is the *real* previous test day's actual value, not a forecast. `lag_7` becomes similarly leaky from test day 8 onward. **This means Phase 2's VQR was evaluated as a partial nowcasting/interpolation task for 13 of its 14 test days, not a true 14-day-ahead forecast.**

Critically, this bug is **specific to the quantum track**. The classical LightGBM baseline in the *same* Phase 2 notebook was not affected — `LightGBMQuantileForecaster.predict()` recursively builds each step's features from real history plus its *own* prior predictions (never real future actuals), exactly as it should. This asymmetry means the original Phase 2 comparison was not apples-to-apples in the quantum track's favor.

### Corrected, leakage-free re-evaluation (supplementary, real, executed)

`experiments/phase2_1_supplementary_analysis.py` reimplements VQR inference recursively — each of the 14 steps builds its classical features from real training history plus the model's own prior predictions, then applies the *same* fitted scaler/PCA, mirroring exactly how the classical baseline already worked. Models were refit (same architecture, same seed=42, same training data) since Phase 2's original fitted model objects were not persisted.

| N | wMAPE **with leakage** (Phase 2, committed) | wMAPE **leakage-free** (this audit) | Change |
|---|---|---|---|
| 4 | 31.49% | **36.03%** | +4.5pp worse (leakage was helping) |
| 8 | 36.27% | **32.40%** | -3.9pp better (leakage was hurting, on this config) |
| 12 | 33.41% | **33.22%** | ~0 (negligible) |

The leakage's effect is not uniformly favorable to quantum (N=8 improved once corrected) — consistent with the diagnosed run-to-run instability (§7) contributing as much noise as the leakage itself at this small sample size. What's unambiguous: **none of the corrected quantum numbers (32.40–36.03%) beat full-history classical LightGBM (25.56%, §3)** — the qualitative conclusion "classical wins under realistic conditions" (H1) is *more*, not less, supported once both the training-window confound and the leakage bug are corrected for.

## 6. N=16 Scalability Investigation — Root Cause

Per instruction, N=16 was **not** repeatedly run to completion again. One bounded (<3 minute), hypothesis-driven diagnostic was run instead, isolating `EstimatorQNN.forward()` (used by COBYLA's objective evaluation) from `EstimatorQNN.backward()` (gradient computation):

| N | Construction | `forward()`, 10 samples | `backward()`/gradient, 10 samples | Ratio (backward/forward) |
|---|---|---|---|---|
| 12 | 0.01s | 0.10s | **10.39s** | 104x |
| 16 | 0.06s | 2.09s | **169.33s** | 81x |

**Root cause established, not invented**: gradient computation (parameter-shift rule, requiring ~2×`num_parameters` circuit evaluations) dominates runtime by 80-100x over the forward pass alone — and `qiskit_machine_learning`'s `VQR`/`ObjectiveFunction` constructs and passes this gradient (`jac=function.gradient`) to the optimizer unconditionally, even for COBYLA, a derivative-free method that doesn't need it (confirmed via the persistent `"No gradient function provided, creating a gradient function"` warning present regardless of optimizer choice, and via the `jac=function.gradient` argument visible in the `trainable_model.py` traceback captured during Phase 2's diagnosis).

The forward-pass cost itself also grew steeply (0.10s→2.09s, ~21x for N=12→16), so both effects compound: more parameters (24→32, requiring more gradient-direction evaluations) **and** each of those evaluations costing far more. This fully explains why N=16 (32 params) was intractable while N=12 (24 params, "only" 1.33x more parameters) completed in under 10 minutes — the practical wall is gradient computation cost, not qubit count or circuit depth in isolation.

This was not tested to see if disabling the auto-gradient construction would fix N=16 (that is itself a new N=16 attempt, and the instruction was to diagnose, not to keep trying configurations) — noted as a concrete recommendation for Phase 4 in §11.

## 7. Non-Determinism Investigation — Reproduced with a Controlled Experiment

5 repeated runs, identical configuration (N=4, seed=42, same training data, same code path as the leakage-free re-evaluation in §5):

| Run | Seed | RMSE | MAE | Runtime | Prediction hash (first 12 hex chars, SHA-256) |
|---|---|---|---|---|---|
| 0 | 42 | 23.5854 | 19.7672 | 1.09s | `8d1f28ff7ea9` |
| 1 | 42 | 23.3481 | 19.7383 | 1.03s | `3a77c53baa02` |
| 2 | 42 | 23.6193 | 21.1280 | 1.01s | `cd1a47cfa627` |
| 3 | 42 | 25.7575 | 20.4571 | 1.16s | `018bb5e87078` |
| 4 | 42 | 24.2769 | 20.5190 | 0.97s | `bd815f1af3e2` |

RMSE: mean=24.117, std=0.980, **CV=4.06%**, range=2.409 (23.35 – 25.76).
MAE: mean=20.322, std=0.582, **CV=2.86%**, range=1.390.

**All 5 prediction hashes differ** — zero exact reproducibility despite identical seed, identical code, identical data.

**Classification: (B) results vary slightly** — not (A) exactly reproducible (confirmed false), and not (C) materially/wildly varying (a ~4% CV is real but modest relative to the ~5-10 percentage-point gaps seen between models in §3/§5). This is consistent with, and reproduces, the Phase 2 finding — now with a controlled 5-run sample rather than a single anecdotal observation. Root cause remains as diagnosed in Phase 2 (`qsci_core/forecasting/quantum/vqr_forecaster.py` docstring): `qiskit-aer` 0.17.2's `EstimatorV2` batched execution is not deterministic even with every documented RNG seeded; this audit did not find or attempt a further fix, consistent with "do not force deterministic output artificially if the backend is non-deterministic."

**Practical implication for Phase 2's numbers**: individual wMAPE values in both Phase 2 and this audit's corrected table (§5) carry roughly ±4% (relative) run-to-run noise on top of whatever real signal exists. This is smaller than, but not negligible next to, the gaps being compared.

## 8. Statistical Power — Real, Computed, Not Asserted

Using `statsmodels.stats.power.TTestPower` (the DM statistic is asymptotically t-distributed, so a t-test power analysis is the standard approximation for this class of test):

- Phase 2's observed effect (LightGBM vs. best-quantum, DM=1.281, n=14) implies a standardized effect size **d≈0.342** (small-to-moderate by Cohen's convention).
- **Achieved power at n=14 for this effect size: 22.1%** — meaning there was roughly a 78% chance of failing to detect a real effect of this size even if one existed. The Phase 2 "not significant" result is barely informative either way.
- **Minimum detectable effect size at n=14, 80% power: d=0.810** (a *large* effect) — only a dramatic difference would have been reliably caught.
- **Sample size needed for 80% power at a moderate effect (d=0.5): n≈33-34.**
- For reference, pooling to n=100 observations would lower the detectable effect to d≈0.283 (small).

**Conclusion: n=14 is genuinely too small for a reliable conclusion in either direction.** This is not a flaw in the DM test implementation (`qsci_core/evaluation/dm_test.py` correctly flags small-sample unreliability below n=10, and n=14 clears that floor) — it's a property of the experimental design's single 14-day window.

## 9. Research Claim Audit

Every substantive comparative claim in `docs/PHASE_2_REPORT.md` and `notebooks/03_quantum_forecasting.ipynb`, reclassified in light of §3–§8:

| Claim (location) | Original framing | Reclassified |
|---|---|---|
| "VQR (N=4, wMAPE 31.49%) outperformed classical LightGBM (wMAPE 45.41%)" (PHASE_2_REPORT.md §15, notebook interpretation cell) | Presented as measured fact | **PARTIALLY SUPPORTED** — the raw numbers are real and correctly computed, but the VQR number is contaminated by test-set leakage (§5) and the LightGBM number is an artificially data-starved baseline (§3). Neither side of this comparison is a fair representation of either approach's real capability. |
| "H1 not supported on this run" (PHASE_2_REPORT.md §15) | Stated as the run's conclusion | **NOT SUPPORTED as stated** — once corrected for leakage (§5) and compared against a properly-resourced classical baseline (§3), H1 (classical wins) is *better* supported, not less. |
| "classical model's baseline was itself constrained in a way that likely disadvantaged it" (PHASE_2_REPORT.md §15) | Hedged speculation | **SUPPORTED** — confirmed directly by §3's fold-4 comparison. |
| "No quantum advantage claim without evidence" (PHASE_2_REPORT.md §19 checklist) | Self-assessed as met | **SUPPORTED** — the report never used the phrase "quantum advantage," "quantum beats classical," or similar; its hedging (§15's "inconclusive," "not overstated") holds up under this audit even though the underlying number was flawed. |
| "N=16 ... training time was measured to scale worse than linearly" (PHASE_2_REPORT.md §10, §12) | Descriptive, root cause not identified | **SUPPORTED**, and now more precisely explained — §6 of this audit identifies the specific mechanism (unconditional gradient computation). |
| "exact numeric results ... should be read as one representative run, not a bit-exact reproducible value" (PHASE_2_REPORT.md §13, vqr_forecaster.py docstring) | Qualitative caveat | **SUPPORTED, now quantified** — §7 gives the actual CV (~3-4%). |
| "Best quantum configuration ... outperformed classical" (notebook 03 result-interpretation cell, printed output) | Auto-generated from real code, correctly reported the *as-run* numbers | **PARTIALLY SUPPORTED** — accurately reflects Phase 2's actual (leakage-affected) run; the printed caveat text in the same cell ("this single run should not be over-interpreted") already hedged correctly, which holds up. |
| No occurrence of "quantum advantage," "quantum faster," "quantum scalable," or "quantum competitive" was found in either document. | — | **N/A** — nothing to audit; these phrases were correctly never used. |

No claim required outright retraction — Phase 2's own hedging language ("RESEARCH," "not over-interpreted," "inconclusive") was already appropriately cautious. What changes is the **substance** underneath the numbers: the specific comparison that was inconclusive-but-slightly-favorable-to-quantum is now understood to be an artifact of two confounds, not a genuine near-tie.

## 10. Final Validity Assessment

**PRIMARY PHASE 2 RESULT** (as committed, unchanged): inconclusive comparison (DM not significant, n=14) between bounded-window LightGBM and VQR, nominally favoring VQR-4 numerically.

**CORRECTED PICTURE** (this audit, supplementary, does not overwrite the above): once (a) compared against a properly-resourced classical baseline instead of an artificially data-starved one, and (b) corrected for test-set feature leakage in the quantum track, **classical forecasting (full-history LightGBM, wMAPE 25.56%) outperforms every quantum configuration tested (wMAPE 32.4–36.0%)** on this series and window — consistent with H1's expectation, not contrary to it. This is still a single series, single window, small-sample result (§8) and should not be over-generalized, but it is a materially more defensible conclusion than Phase 2's original framing.

The Phase 2 experiment's core engineering (VQR architecture, feature-reduction leakage-safety on the *training* side, DM test implementation, experiment manifest/results schema) is sound and reusable — the flaw was specifically in how *test-set inference* features were constructed for the quantum track, not in the underlying `qsci_core` modules used correctly elsewhere (e.g. `LightGBMQuantileForecaster`'s own recursive prediction, which is leakage-free and was the correct pattern to have replicated for VQR).

## 11. Recommended Phase 2 Research Extension (not implemented here)

A statistically defensible version of this experiment needs a much larger pooled sample. Concretely, matching Phase 1's own rolling-origin methodology:

- **Multiple M5 series** (e.g., 5-10 series spanning different volume/volatility profiles, selected by a disclosed rule as Phase 1/2 already do — not cherry-picked).
- **Repeated rolling-origin windows per series** (e.g., 3-5 folds each, as Phase 1's classical backtest already does).
- **Pooled forecast errors** across series × folds × the 14-day horizon — e.g., 8 series × 4 folds × 14 days ≈ 450 pooled observations, comfortably above the n≈100 threshold where a moderate-to-small effect (d≈0.28) becomes detectable (§8).
- **Fix the leakage bug first** — before any larger run, `qsci_core/forecasting/quantum/vqr_forecaster.py` or a new wrapper needs a recursive, leakage-free `predict()` matching `LightGBMQuantileForecaster`'s pattern, promoted from this audit's throwaway script (`experiments/phase2_1_supplementary_analysis.py`) into a tested `qsci_core` module.
- **Address the N=16 gradient cost** (§6) before including it at scale — either by using an optimizer/QNN configuration that skips gradient construction entirely for derivative-free optimizers (an actual code-level fix, not just a bigger runtime budget), or by explicitly scoping N=16 out of large-scale runs and treating N≤12 as this environment's practical ceiling.
- **Report result distributions, not single-run point estimates** given the ~3-4% CV from run-to-run non-determinism (§7) — e.g. median of 3 runs per configuration, or explicitly propagate this as a source of uncertainty in the pooled analysis.

This is scoped as a Phase 5 (business-impact benchmark) candidate or a dedicated Phase 2.2, not something to auto-implement here.

## 12. Testing

Phase 0 + Phase 1 + Phase 2 test suite re-run, unmodified: **116 passed, 1 xfailed** (the same documented non-determinism `xfail` from Phase 2 — this audit's §7 independently reproduces and quantifies exactly what that test flags). No test was changed to make it pass; no genuine new test failure was found, since this audit's new code (`experiments/phase2_1_supplementary_analysis.py`) is a standalone analysis script, not a `qsci_core` module, and has no test suite of its own — it is not production code, only supplementary evidence.
