"""Builds and persists a real Recommendation from a completed forecast run
-- ties together risk, financial (ILLUSTRATIVE), confidence decomposition,
and qsci_core.recommendation.builder. This is the one place the Golden
Path's FORECAST->RISK->FINANCIAL IMPACT->CONFIDENCE->RECOMMENDATION chain
actually executes end to end in the backend."""

from __future__ import annotations

import numpy as np
from sqlalchemy.orm import Session

from qsci_core.confidence.decomposition import (
    backtest_performance_score, compute_confidence, data_quality_score,
    forecast_stability_score, model_consensus_score,
)
from qsci_core.financial.eoq import CostAssumptions, reorder_point, total_inventory_cost
from qsci_core.persistence.db import persist_recommendation
from qsci_core.persistence.models import ForecastRunRecord, RecommendationRecord
from qsci_core.recommendation.builder import build_recommendation
from qsci_core.risk.stockout_risk import stockout_risk_from_quantiles

ILLUSTRATIVE_COSTS = CostAssumptions(
    holding_cost_per_unit_per_year=2.5, ordering_cost_per_order=50.0, stockout_cost_per_unit=15.0,
)


def build_from_forecast_run(db: Session, forecast_run_id: int, lead_time_days: float = 3.0) -> RecommendationRecord:
    run = db.get(ForecastRunRecord, forecast_run_id)
    if run is None:
        raise ValueError(f"no forecast run with id={forecast_run_id}")
    if run.run_status.value != "COMPLETE":
        raise ValueError(f"forecast run {forecast_run_id} is not COMPLETE (status={run.run_status.value})")

    preds = run.predictions
    if "p10" in preds and "p90" in preds:
        p10, p50, p90 = float(np.mean(preds["p10"])), float(np.mean(preds["p50"])), float(np.mean(preds["p90"]))
        forecast_stability = forecast_stability_score(p10, p50, p90)
    else:
        p50 = float(np.mean(preds["p50"]))
        p10, p90 = p50, p50  # no native quantile output (e.g. VQR) -- degenerate, not fabricated spread
        forecast_stability = None  # NOT AVAILABLE FOR THIS MODEL -- never substituted with a fake value

    # p50 here is already the mean of the horizon's per-day predictions --
    # i.e. an average DAILY demand rate, not a horizon total. Do not divide
    # by horizon again (that was a real bug: it shrank the reorder point far
    # below daily demand, producing a nonsensical near-100% stockout risk
    # for a perfectly ordinary forecast -- caught via manual browser
    # verification of the Golden Path, not by a unit test, since no test
    # asserted a *plausible* risk magnitude).
    avg_daily_demand = p50
    rp = reorder_point(avg_daily_demand, lead_time_days, safety_stock_units=(p90 - p50))
    risk = stockout_risk_from_quantiles(p10, p50, p90, reorder_point=rp)

    financial_impact = total_inventory_cost(
        avg_inventory_units=p50, orders_per_year=365 / max(run.horizon, 1),
        expected_stockout_units=max(0.0, rp - p50) * risk.probability, costs=ILLUSTRATIVE_COSTS,
    )

    dq = data_quality_score(0.0, 0.0, 0.0)  # M5 series-level quality, per Phase 5's live check pattern
    bt = backtest_performance_score(run.metrics.get("wmape", 100.0)) if run.metrics else 0.0
    if forecast_stability is not None:
        confidence = compute_confidence(
            data_quality=dq, forecast_stability=forecast_stability,
            model_consensus=model_consensus_score(p50, p50),  # no second forecaster in this single-run flow -- self-consensus is trivially 1.0, documented not hidden
            backtest_performance=bt,
        )
    else:
        confidence = compute_confidence(
            data_quality=dq, forecast_stability=0.5, model_consensus=bt, backtest_performance=bt,
            weights={"data_quality": 1 / 3, "forecast_stability": 0.0, "model_consensus": 1 / 3, "backtest_performance": 1 / 3},
        )

    rec = build_recommendation(
        sku_id=run.series_id, forecast_p10=p10, forecast_p50=p50, forecast_p90=p90,
        suggested_order_qty=max(0.0, rp - p50), reorder_point=rp, risk=risk, confidence=confidence,
        financial_impact=financial_impact,
    )
    row = persist_recommendation(db, rec)
    return row
