# Phase 1 Report — Classical Golden Path

Status: **COMPLETE — DEMONSTRATED WITH REAL EVIDENCE, NOT YET COMMITTED**
Date: 2026-08-18
Branch: `main`

## 1. Phase Objective

Prove that QSCI is a genuinely useful supply-chain decision-intelligence
system **without quantum computing** — the full classical chain: DATA →
QUALITY → FORECAST → RISK → OPTIMIZATION → FINANCIAL IMPACT → CONFIDENCE →
RECOMMENDATION → HUMAN APPROVAL → AUDIT, on the real datasets verified in
Phase 0. No quantum functionality and no production frontend were built in
this phase, per instruction.

## 2. Modules Delivered

| Module | Path | Purpose |
|---|---|---|
| Forecasting | `qsci_core/forecasting/classical/{lightgbm_forecaster,seasonal_naive,features}.py` | LightGBM quantile (p10/p50/p90) forecaster with recursive multi-step prediction + quantile-crossing rectification; seasonal-naive baseline |
| Evaluation | `qsci_core/evaluation/{metrics,backtest}.py` | RMSE, MAE, wMAPE, Bias, FVA, pinball loss; rolling-origin backtesting (never random splits) |
| Experiment tracking | `qsci_core/mlflow_utils.py` | Wraps mlflow (sqlite backend) — every run logs dataset version, seed, params, metrics, runtime, git commit |
| Optimization | `qsci_core/optimization/classical/or_tools_vrp.py` | OR-Tools CVRP solver, supports Euclidean or precomputed (real travel-time) distance matrices |
| Financial | `qsci_core/financial/eoq.py` | EOQ, safety stock, reorder point, holding/ordering/stockout cost — `CostAssumptions` explicitly typed ILLUSTRATIVE |
| Risk | `qsci_core/risk/stockout_risk.py` | Stockout probability from forecast quantiles (documented normal approximation), demand volatility (CV) |
| Confidence | `qsci_core/confidence/decomposition.py` | 4-component weighted decomposition (data quality, forecast stability, model consensus, backtest performance) — documented formula, not an invented number |
| Recommendation | `qsci_core/recommendation/builder.py` | Assembles forecast + risk + confidence + financial into a `Recommendation` with a generated rationale |
| Persistence | `qsci_core/persistence/{models,db}.py` | SQLAlchemy: `RecommendationRecord`, `ApprovalRecord` (APPROVE/REJECT/MODIFY), `AuditRecord`, `OutcomeRecord` |

**New dependency added:** `ortools` — required by the roadmap but absent
from the original Phase 0 install list (a gap in that list, not a scope
change). Verified importable before use.

## 3. Real Bugs Found and Fixed During This Phase

1. **Quantile crossing**: independently-trained LightGBM quantile models
   could produce p10 > p90 at some forecast steps — a documented limitation
   of the approach, not a coding bug. Fixed with the standard sort-based
   rectification, verified with a monotonicity test.
2. **Reorder-point / forecast-quantile scale mismatch** (found while
   building notebook 02, not by a reviewer): the first draft compared a
   3-day-lead-time reorder point against *single-day* forecast quantiles
   for stockout risk — mathematically guaranteed near-zero risk regardless
   of real risk, since the reorder point was ~4x the demand quantiles by
   construction. Fixed by fixing lead time at 1 day so both are on the same
   basis, with an explicit note that a real multi-day lead time needs the
   *cumulative* demand distribution, not `quantile × days` (statistically
   wrong for quantiles, unlike the mean).
3. **mlflow 3.x deprecation**: the plain filesystem tracking store used in
   the original design is deprecated; switched to a local sqlite backend
   (`experiments/mlruns/tracking.db`).

None of these were caught by a second reviewer — they surfaced from
actually running the code and checking whether the numbers made sense,
which is the entire point of CLAUDE.md §1.

## 4. Tests

75/75 passing, covering the required edge cases:

| File | Edge cases covered |
|---|---|
| `test_evaluation.py` | empty arrays, shape mismatch, zero-denominator wMAPE/FVA, insufficient history, unsorted dates, NaN target |
| `test_forecasting_classical.py` | missing target column, insufficient history, predict-before-fit, horizon mismatch, quantile monotonicity |
| `test_optimization_classical.py` | empty instance, negative demand, demand > capacity (infeasible-by-construction), invalid capacity/vehicle count, out-of-range depot, coords/demands length mismatch |
| `test_financial.py` | negative cost inputs, zero demand/holding cost (EOQ undefined), known-value check against the textbook EOQ formula |
| `test_risk.py` | out-of-order quantiles, degenerate zero-spread, empty/single-value/zero-mean volatility input |
| `test_confidence.py` | out-of-range components, weights not summing to 1, custom weighting |
| `test_recommendation_persistence.py` | out-of-order quantiles, negative order qty, MODIFY-without-qty, APPROVE-with-qty, unknown recommendation id, full chain ordering |

```
75 passed, 23 warnings in 19.53s
```

Known warning (not a failure): a `DeprecationWarning` from `pd.Timedelta(days=1)`
originating inside pandas 2.3.3 / numpy 2.x's internal interaction on this
environment — verified to come from pandas' own `Timedelta` constructor
path, not from incorrect usage in `qsci_core`. Left as-is rather than
working around correct, idiomatic code to silence an upstream warning.

## 5. Notebook Execution — 02_classical_forecasting.ipynb

Series: `FOODS_3_090_CA_1_evaluation` — selected by a disclosed rule (highest
total-volume item in store CA_1), not cherry-picked for a good result.
1,941 days, 24.16% zero-sales days (real, intermittent retail demand).

Rolling-origin backtest, 5 folds, 14-day horizon, `min_train_size=400`:

| Model | RMSE | MAE | wMAPE | Bias |
|---|---|---|---|---|
| LightGBM (p50) | 16.68 | 12.99 | **24.20%** | 3.86 |
| Seasonal-naive | 23.31 | 18.20 | **33.49%** | 2.83 |

**FVA = +28.1%** — LightGBM beat the naive baseline on this real series.
This is a single-series result, not a claim about M5-wide performance;
RQ1/H1 at scale is Phase 2's job against this same baseline.

Forward 14-day quantile forecast produced, monotonic p10≤p50≤p90 at every
step. Confidence decomposition: overall **81.0%** (data quality 1.00,
forecast stability 0.60, model consensus 0.88, backtest performance 0.76).
Recommendation built (LOW stockout risk, reorder point on the same 1-day
basis as the forecast quantiles), persisted, and approved
(`APPROVAL_APPROVE`) — full audit trail: `RECOMMENDATION_CREATED` →
`APPROVAL_APPROVE`. `Outcome` recording intentionally skipped — the
forecasted period hasn't happened yet, so there's no real actual-demand to
record.

## 6. Notebook Execution — 04_classical_optimization.ipynb

**CVRPLIB** — all 4 instances solved feasibly:

| Instance | OR-Tools | Best-known | Gap |
|---|---|---|---|
| A-n32-k5 | 787.1 | 784 | +0.39% |
| A-n33-k5 | 662.1 | 661 | +0.17% |
| A-n37-k5 | 672.5 | 669 | +0.52% |
| B-n31-k5 | 676.1 | 672 | +0.61% |

Max gap across all 4: **0.61%** — this is the classical baseline Phase 3's
quantum routing has to be measured against.

**Amazon Last-Mile** — real route `RouteID_64cb7ba5-342d-46db-9e04-962248c6f667`
(station DCH1, 2018-07-19, smallest route in the training set by stop
count: 33 incl. depot). Real travel-time matrix, real historical driver
sequence (`actual_sequences.json`), modeled as an open route (zero-cost
dummy end node, not a round trip):

- Actual driver: 3,660.9s (61.0 min)
- OR-Tools: 2,561.2s (42.7 min)
- **+30.0%** faster (pure travel-time comparison)

Caveat stated explicitly in the notebook: real drivers optimize more than
travel time (delivery windows, package load order, personal routine) — this
is not a claim that routing software categorically beats human drivers.

## 7. mlflow Verification

Backend: `experiments/mlruns/tracking.db` (sqlite; the filesystem backend
mlflow 3.x deprecated). Two experiments created, all runs tagged with the
real git commit and logging dataset version, seed, params, metrics, and
runtime:

- `m5_classical_forecasting`: `lightgbm_FOODS_3_090_CA_1_evaluation`, `seasonal_naive_FOODS_3_090_CA_1_evaluation`
- `classical_routing`: `or_tools_cvrplib`, `or_tools_lastmile_RouteID_64cb7ba5-...`

## 8. Persistence Verification

`experiments/qsci_dev.db` (real sqlite file, 36KB after this phase's runs):

```
recommendations: 2
approvals: 2
audit events: 4
 - FOODS_3_090_CA_1_evaluation  LOW  0.81
 - FOODS_3_090_CA_1_evaluation  LOW  0.81
```

Two rows, not one — notebook 02 was executed twice during this phase (once
before, once after fixing the reorder-point/quantile scale-mismatch bug in
§3). Left as-is rather than reset, since it's an honest reflection of the
actual development process and demonstrates the persistence layer
correctly accumulating across runs without collision — exactly what an
audit trail is for.

## 9. Recommendation → Approval → Audit Chain

Verified end to end, both via `tests/test_recommendation_persistence.py`
and live in notebook 02: `RECOMMENDATION_CREATED` → `APPROVAL_{APPROVE
| REJECT | MODIFY}` → (`OUTCOME_RECORDED` when real outcome data exists).
`MODIFY` without a quantity, and non-`MODIFY` decisions with a quantity,
are both rejected at the point of creation (`qsci_core/persistence/db.py`).

## 10. Status Classification Summary

| Component | Status |
|---|---|
| Forecast metrics, backtest, mlflow records | LIVE |
| OR-Tools routing results (CVRPLIB + Last-Mile) | LIVE |
| Confidence decomposition | LIVE (documented formula) |
| Stockout risk | LIVE (documented normal approximation, not exact) |
| Financial cost figures ($ holding/ordering/stockout) | ILLUSTRATIVE — no public per-unit cost data exists for M5 or Last-Mile |
| Persistence chain (Recommendation/Approval/Audit) | LIVE |
| Outcome comparison (predicted vs. actual) | PENDING — requires real future data QSCI doesn't have yet |

## 11. Acceptance Criteria (per CLAUDE.md §12 and the Phase 1 spec)

| Criterion | Result |
|---|---|
| Full classical golden path executes | ✅ both notebooks, top to bottom, real output |
| Rolling-origin backtesting, never random split | ✅ enforced in `backtest.py`, tested |
| RMSE/MAE/wMAPE/Bias/FVA reported | ✅ |
| mlflow logs dataset version/seed/params/metrics/runtime/git commit | ✅ verified via `mlflow.search_runs` |
| OR-Tools routing against real data | ✅ CVRPLIB (published ground truth) + Last-Mile (real driver comparison) |
| EOQ/safety stock/reorder/holding/ordering/stockout, ILLUSTRATIVE where appropriate | ✅ `CostAssumptions.status == "ILLUSTRATIVE"` enforced in code |
| Confidence decomposition documented mathematically | ✅ formula in module docstring, not an invented percentage |
| Recommendation → Approval (APPROVE/REJECT/MODIFY) → Audit | ✅ persisted, tested, demonstrated live |
| Outcome representation for future predicted-vs-actual | ✅ `OutcomeRecord` + `record_outcome`, tested; not fabricated in the notebook |
| Edge-case tests: NaN, empty, missing columns, duplicates, negative demand, malformed input, insufficient history, invalid optimization constraints | ✅ 75/75 passing |
| Report contradicts a hypothesis if that's what happened | N/A this phase — H1 (classical vs. quantum) isn't testable until Phase 2 exists |

## 12. Known Limitations

- Notebook 02 evaluates one real M5 series (by a disclosed selection rule),
  not the full 30,490-series panel — a scoping decision for Phase 1
  tractability, not a hidden cap. Multi-series evaluation is Phase 2/5
  scope once quantum needs the same comparison baseline anyway.
- The Last-Mile open-route trick (zero-cost dummy end node) is a modeling
  choice specific to this notebook's single-route demonstration, not yet a
  general capability of `or_tools_vrp.py` for multi-vehicle open routes.
- Stockout risk uses a normal approximation from the p10/p90 spread — it
  degrades for heavily skewed real demand distributions (M5 series are
  frequently zero-inflated, which is not normal). Documented in the
  function's docstring; a heavier-tailed model is future work, not claimed
  as solved.
- `experiments/qsci_dev.db` and `experiments/mlruns/` are gitignored dev
  artifacts, not committed — they're reproducible by re-running the
  notebooks, not treated as source of truth.
- This report and the underlying commits have **not been committed to git**
  — Phase 1 instructions didn't request a commit (unlike Phase 0's explicit
  instruction); awaiting confirmation before committing.
