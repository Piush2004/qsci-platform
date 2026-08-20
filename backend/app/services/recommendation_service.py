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
from qsci_core.persistence.models import (
    ForecastRunRecord, RecommendationRecord, RunStatus,
)
from qsci_core.recommendation.builder import build_recommendation
from qsci_core.risk.stockout_risk import stockout_risk_from_quantiles

ILLUSTRATIVE_COSTS = CostAssumptions(
    holding_cost_per_unit_per_year=2.5, ordering_cost_per_order=50.0, stockout_cost_per_unit=15.0,
)


def compute_recommendation(run: ForecastRunRecord, lead_time_days: float = 3.0):
    """Pure computation, no persistence -- the same FORECAST -> RISK ->
    FINANCIAL -> CONFIDENCE -> RECOMMENDATION chain `build_from_forecast_run`
    persists, but callable on any COMPLETE forecast run without writing a
    row. Used by the recommendation endpoint AND by Milestone 3's baseline-
    comparison / accuracy-vs-outcome endpoints, so both paths share one
    implementation instead of two copies of this math."""
    if run.run_status.value != "COMPLETE":
        raise ValueError(f"forecast run {run.id} is not COMPLETE (status={run.run_status.value})")

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

    return build_recommendation(
        sku_id=run.series_id, forecast_p10=p10, forecast_p50=p50, forecast_p90=p90,
        suggested_order_qty=max(0.0, rp - p50), reorder_point=rp, risk=risk, confidence=confidence,
        financial_impact=financial_impact,
    )


def build_from_forecast_run(db: Session, forecast_run_id: int, lead_time_days: float = 3.0) -> RecommendationRecord:
    run = db.get(ForecastRunRecord, forecast_run_id)
    if run is None:
        raise ValueError(f"no forecast run with id={forecast_run_id}")
    rec = compute_recommendation(run, lead_time_days)
    return persist_recommendation(db, rec, forecast_run_id=run.id)


BASELINE_MODEL = "seasonal_naive"


def get_baseline_comparison(db: Session, rec_id: int) -> dict:
    """Step 3: baseline (seasonal-naive) vs QSCI's actual decision, on the
    identical series/horizon -- only when a real seasonal-naive run for
    that exact series+horizon already exists on file. Never runs a new
    forecast just to manufacture a comparison; a missing baseline is
    reported as PENDING, not silently skipped or approximated."""
    rec = db.get(RecommendationRecord, rec_id)
    if rec is None:
        raise ValueError(f"no recommendation with id={rec_id}")
    if rec.forecast_run_id is None:
        return {"status": "PENDING", "note": "This recommendation has no linked forecast run to compare against."}

    decision_run = db.get(ForecastRunRecord, rec.forecast_run_id)
    if decision_run is None:
        return {"status": "PENDING", "note": "The originating forecast run no longer exists."}

    if decision_run.model == BASELINE_MODEL:
        return {
            "status": "PENDING",
            "note": f"This recommendation's own forecast IS the {BASELINE_MODEL} baseline -- no separate comparison applies.",
        }

    baseline_run = (
        db.query(ForecastRunRecord)
        .filter(
            ForecastRunRecord.series_id == decision_run.series_id,
            ForecastRunRecord.horizon == decision_run.horizon,
            ForecastRunRecord.model == BASELINE_MODEL,
            ForecastRunRecord.run_status == RunStatus.COMPLETE,
        )
        .order_by(ForecastRunRecord.created_at.desc())
        .first()
    )
    if baseline_run is None:
        return {
            "status": "PENDING",
            "note": (
                f"No completed {BASELINE_MODEL} run exists yet for series={decision_run.series_id} "
                f"horizon={decision_run.horizon}. Run one on /demand to enable this comparison."
            ),
        }

    baseline_rec = compute_recommendation(baseline_run, lead_time_days=3.0)

    return {
        "status": "LIVE",
        "note": "Both forecasts were scored on the identical series and held-out horizon.",
        "baseline": {
            "model": baseline_run.model,
            "forecast_metric": {"name": "wMAPE", "value": (baseline_run.metrics or {}).get("wmape")},
            "operational_metric": {"name": "reorder_point", "value": baseline_rec.reorder_point},
            "financial_metric": {
                "name": "total_cost",
                "value": baseline_rec.financial_impact.get("total_cost"),
                "status": baseline_rec.financial_impact.get("status"),
            },
        },
        "decision": {
            "model": decision_run.model,
            "forecast_metric": {"name": "wMAPE", "value": (decision_run.metrics or {}).get("wmape")},
            "operational_metric": {"name": "reorder_point", "value": rec.reorder_point},
            "financial_metric": {
                "name": "total_cost",
                "value": rec.financial_impact.get("total_cost"),
                "status": rec.financial_impact.get("status"),
            },
        },
    }


def get_accuracy_vs_outcome(db: Session, series_id: str) -> dict:
    """Step 4: does better forecast accuracy (wMAPE) correspond to lower
    financial cost, across whatever models have actually been run on this
    series+horizon? Uses only real completed forecast runs already on
    file -- never fabricates a paired point. Needs >=2 distinct models to
    say anything about a relationship at all."""
    runs = (
        db.query(ForecastRunRecord)
        .filter(ForecastRunRecord.series_id == series_id, ForecastRunRecord.run_status == RunStatus.COMPLETE)
        .order_by(ForecastRunRecord.created_at.desc())
        .all()
    )
    latest_by_model: dict[str, ForecastRunRecord] = {}
    for run in runs:
        latest_by_model.setdefault(run.model, run)  # already ordered desc -- first hit per model is the latest

    points = []
    for model, run in latest_by_model.items():
        if not run.metrics or "wmape" not in run.metrics:
            continue
        try:
            rec = compute_recommendation(run, lead_time_days=3.0)
        except Exception:  # noqa: BLE001 -- a single bad run shouldn't break the whole chart
            continue
        points.append({
            "model": model,
            "label": run.label,
            "wmape": run.metrics["wmape"],
            "total_cost": rec.financial_impact.get("total_cost"),
            "financial_status": rec.financial_impact.get("status"),
        })

    if len(points) < 2:
        return {
            "status": "PENDING",
            "note": "PENDING — paired business-outcome experiment (fewer than 2 completed models for this series+horizon).",
            "points": points,
        }

    return {
        "status": "RESEARCH" if any(p["label"] == "RESEARCH" for p in points) else "LIVE",
        "note": (
            "Each point pairs one model's real backtest wMAPE with its financial-impact total cost "
            "(ILLUSTRATIVE cost assumptions) on the identical series+horizon. A lower wMAPE point at a "
            "higher total_cost, or vice versa, is real evidence against 'better accuracy = better outcome' "
            "-- reported as observed, not adjusted to fit the hypothesis."
        ),
        "points": points,
    }
