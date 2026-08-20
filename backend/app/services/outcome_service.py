"""Predicted-vs-actual outcome comparison (RQ2/H2: does better forecast
accuracy guarantee better inventory outcomes?).

M5 is a real, already-collected historical dataset -- the "test" window
`forecast_service.execute_run` holds out for scoring (`test_df["sales"]`)
is genuine historical demand, not a placeholder. So for any recommendation
whose forecast run is still on file, the actual demand for that forecast's
horizon is real data, available immediately -- not something that has to
be "waited for."

This is NOT the same claim as "a live, post-decision, real-world outcome."
No recommendation built in this system has ever led to a real purchase
order being placed and observed -- QSCI does not execute real-world
actions. The distinction is disclosed in every response this module
returns (see `kind` field) rather than left for the reader to infer.

`qsci_core.persistence.db.record_outcome` (manual entry, e.g. a real
purchase order's actual result once QSCI is wired into a live ordering
system) remains available for that future, genuinely-live case and is
preferred over the backtest-derived figure when both exist.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.forecast_service import _load_series
from qsci_core.persistence.models import (
    ForecastRunRecord, OutcomeRecord, RecommendationRecord,
)


def get_outcome(db: Session, rec_id: int) -> dict:
    rec = db.get(RecommendationRecord, rec_id)
    if rec is None:
        raise ValueError(f"no recommendation with id={rec_id}")

    manual = (
        db.query(OutcomeRecord)
        .filter(OutcomeRecord.recommendation_id == rec_id)
        .order_by(OutcomeRecord.recorded_at.desc())
        .first()
    )
    if manual is not None:
        return {
            "status": "LIVE",
            "kind": "manual",
            "note": "Manually recorded outcome (e.g. a real observed result), not derived from a backtest.",
            "predicted_demand": rec.forecast_p50,
            "actual_qty_ordered": manual.actual_qty_ordered,
            "actual_demand_observed": manual.actual_demand_observed,
            "error": (
                manual.actual_demand_observed - rec.forecast_p50
                if manual.actual_demand_observed is not None else None
            ),
            "recorded_at": manual.recorded_at.isoformat(),
            "notes": manual.notes,
        }

    if rec.forecast_run_id is None:
        return {
            "status": "PENDING",
            "kind": None,
            "note": (
                "This recommendation was created before Milestone 3 linked recommendations to their "
                "originating forecast run -- no outcome can be derived. Awaiting outcome data."
            ),
        }

    run = db.get(ForecastRunRecord, rec.forecast_run_id)
    if run is None or run.run_status.value != "COMPLETE":
        return {
            "status": "PENDING",
            "kind": None,
            "note": "Awaiting outcome data -- the originating forecast run is missing or incomplete.",
        }

    try:
        series_df = _load_series(run.series_id)
    except ValueError as exc:
        return {"status": "PENDING", "kind": None, "note": f"Awaiting outcome data -- {exc}"}

    split_idx = len(series_df) - run.horizon
    test_df = series_df.iloc[split_idx:]
    if test_df.empty:
        return {"status": "PENDING", "kind": None, "note": "Awaiting outcome data -- no held-out window available."}

    actual_avg_daily_demand = float(test_df["sales"].mean())
    predicted = rec.forecast_p50
    error = actual_avg_daily_demand - predicted
    pct_error = (error / actual_avg_daily_demand * 100.0) if actual_avg_daily_demand != 0 else None

    return {
        "status": "LIVE",
        "kind": "backtest_actual",
        "note": (
            "Real M5 held-out test-window sales for this forecast's horizon (average daily demand) -- "
            "genuine historical data, not fabricated. This is a BACKTEST actual, not a live post-decision "
            "outcome: no real-world order was placed or observed as a result of this recommendation."
        ),
        "predicted_demand": predicted,
        "actual_demand": actual_avg_daily_demand,
        "error": error,
        "pct_error": pct_error,
        "horizon_days": run.horizon,
        "series_id": run.series_id,
    }
