# Milestone 3 Audit — Outcome & Financial Decision Intelligence

Status: **COMPLETE** (audit + implementation verification)
Date: 2026-08-20

## 1. Existing Financial Calculations

`qsci_core/financial/eoq.py`: `CostAssumptions` (frozen dataclass, `status="ILLUSTRATIVE"` always), `economic_order_quantity`, `safety_stock`, `reorder_point`, `annual_holding_cost`, `annual_ordering_cost`, `expected_stockout_cost`, `total_inventory_cost` (bundles all three, tags the result dict `"status": "ILLUSTRATIVE"`). All formulas are real, standard OR math — the LIVE part is the computation, the ILLUSTRATIVE part is the $ inputs (`holding_cost_per_unit_per_year=2.5, ordering_cost_per_order=50.0, stockout_cost_per_unit=15.0`, hardcoded in `backend/app/services/recommendation_service.py::ILLUSTRATIVE_COSTS` — no public dataset supplies real per-unit costs for M5, documented in CLAUDE.md §5).

## 2. Available Real Data

M5's `sales_train_evaluation` provides genuine historical daily sales. `forecast_service.execute_run` already holds out a real test window (`test_df["sales"]`) to score wMAPE/RMSE/MAE/bias — this held-out actual demand was already being computed and thrown away after scoring; Milestone 3's outcome layer (§7 below) is the first place it's exposed as a "predicted vs. actual" comparison. This is real M5 data, not fabricated, but it is a **backtest** actual (a historical, already-known test split), not a live post-decision outcome — no recommendation in this system has ever led to a real-world order being placed and observed. That distinction is disclosed in every outcome response (`kind: "backtest_actual"` vs. `kind: "manual"`), not left implicit.

## 3. Illustrative Assumptions (Unchanged, Reused As-Is)

`ILLUSTRATIVE_COSTS` in `recommendation_service.py` — same three constants used since Phase 6/Milestone 1, not modified this milestone. Every dict downstream (`financial_impact`) carries `"status": "ILLUSTRATIVE"` and is rendered with a `StatusPill` everywhere it appears (`WhyPanel`, `DecisionChain`, `BaselineComparisonCard`, `AccuracyOutcomeScatter`'s y-axis label).

## 4. Confidence Implementation

`qsci_core/confidence/decomposition.py`: `data_quality_score`, `forecast_stability_score`, `model_consensus_score`, `backtest_performance_score`, `compute_confidence` (weighted average, default equal 0.25 weights, validated to sum to 1.0). `recommendation_service.compute_recommendation` already routes VQR's missing stability into a reweighted call (`forecast_stability` weight forced to 0.0, not silently defaulted) — this was already correct going into Milestone 3; `ConfidenceExplainer.tsx` (new) surfaces this behavior explicitly to the user rather than leaving it implicit in a number.

## 5. Risk Implementation

`qsci_core/risk/stockout_risk.py`: `stockout_risk_from_quantiles` (normal approximation from the p10-p90 spread, documented as an approximation, degrades under real skew), `demand_volatility`. `qsci_core/recommendation/builder.py::_risk_level` buckets probability into LOW/MEDIUM/HIGH (<10%/<30%/else). Pre-Milestone-3, the UI only ever showed the bucket + probability, never *why* — `RiskExplainer.tsx` (new) is the fix, built entirely from fields the API already returns (`reorder_point`, `forecast_p10/50/90`, `risk_probability`, `risk_level`) — no new backend endpoint needed.

## 6. Recommendation / Audit Implementation

`qsci_core/recommendation/builder.py::build_recommendation` assembles the `Recommendation` dataclass and a real narrative `rationale` string. `qsci_core/persistence/db.py::persist_recommendation`/`record_approval` write `RecommendationRecord`/`ApprovalRecord`/`AuditRecord` rows, and (found this audit) an **already-defined but never-wired** `OutcomeRecord` model + `record_outcome()` helper — built in an earlier phase's persistence layer, unused by any service or route until this milestone. `AuditRecord` has no cryptographic integrity field (no hash chain, no signature) — CLAUDE.md §11's "audit mechanism, not certification" framing is preserved; nothing in this milestone claims SOC 2 or similar.

## 7. Missing Outcome Functionality (What This Milestone Built)

- `RecommendationRecord` had **no link back to its originating `ForecastRunRecord`** — without it, the real M5 held-out test-window actual couldn't be recovered for a given recommendation. Added `forecast_run_id` (nullable FK) via a real Alembic migration (`a513201f3233_add_forecast_run_id_to_recommendations.py`, batch-mode for SQLite), applied to the dev DB with `alembic upgrade head` — verified all 4 pre-existing recommendation rows survived with `forecast_run_id=NULL` (correctly PENDING for the outcome endpoint, since they predate this link).
- New `backend/app/services/outcome_service.py::get_outcome` — returns the real backtest actual when `forecast_run_id` is set and a manual `OutcomeRecord` doesn't already exist (manual entry, via the pre-existing `record_outcome`, takes precedence when present).
- New `GET /recommendations/{id}/outcome`, `POST /recommendations/{id}/outcome` (manual entry, reuses `qsci_core.persistence.db.record_outcome`).
- New `recommendation_service.get_baseline_comparison` (Step 3) — finds a same-series/same-horizon `seasonal_naive` run on file and compares it against the recommendation's actual model via the shared `compute_recommendation` helper (refactored out of `build_from_forecast_run` so both paths use identical math, not two copies). PENDING when no baseline run exists, or when the recommendation's own model *is* the baseline.
- New `recommendation_service.get_accuracy_vs_outcome` (Step 4) — pairs each distinct model's real wMAPE against its financial-impact total cost, for whatever COMPLETE forecast runs already exist on a series. PENDING below 2 models; never fabricates a third point.
- New `GET /recommendations/{id}/baseline`, `GET /research/accuracy-vs-outcome`.

## 8. Frontend Gaps Filled

- `DecisionCard` (Step 9) — compact list card (SKU, status, forecast/order, risk, confidence, illustrative impact), replaces the plain button-list rows.
- `OutcomeSection`, `BaselineComparisonCard`, `ConfidenceExplainer`, `RiskExplainer`, `AccuracyOutcomeScatter` — all new, all rendering only backend-returned data (see the file-by-file list in `docs/QSCI_IMPLEMENTATION_LOG.md`'s Milestone 3 entry).
- `DecisionChain` gained a 9th stage, **Outcome**, driven by the same `OutcomeResult` the dashboard fetches.
- `/dashboard` restructured into Step 8's exact hierarchy: Decisions requiring attention → Why this decision (DecisionChain + WhyPanel) → Business impact (baseline) → Confidence (explainer + risk) → Human decision → Outcome.
- `/research` gained a Forecast-accuracy-vs-business-outcome section (Step 4), scatter chart, PENDING-safe.

## 9. Scope Decision — No Separate Recommendation-Detail Route

Step 13 describes a "rich detail view." `/dashboard` already implements exactly this shape (list on the left, full DecisionChain/WhyPanel/etc. detail on the right for the selected recommendation) since Milestone 1 — Milestone 3 enriches that existing detail pane with the new sections in Step 13's stage order rather than introducing a second, parallel route that would duplicate the same data-fetching and re-fragment the "central QSCI experience" CLAUDE.md asks for. Documented here rather than silently deviating from the letter of Step 13.

## 10. Plan (as executed)

Backend: Alembic migration → `outcome_service` → `recommendation_service` additions (`compute_recommendation` extraction, `get_baseline_comparison`, `get_accuracy_vs_outcome`) → routes → schemas → 11 new tests. Frontend: 5 new components → `DecisionChain` Outcome stage → `/dashboard` restructure → `/research` new section. Verification: full backend + qsci_core suites, browser testing at desktop and the environment's mobile-tooling floor, claim audit, docs.
