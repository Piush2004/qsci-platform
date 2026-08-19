"""Wraps qsci_core.forecasting for the /api/v1/forecast routes.

seasonal_naive and lightgbm are fast (sub-second to a few seconds) --
run synchronously. vqr is slow (documented: up to ~5 minutes at N=12
qubits, Phase 2/2.1/4 measurements) -- always dispatched as a background
task; the endpoint returns immediately with run_status=PENDING/RUNNING
and the client polls GET /forecast/{run_id}."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from qsci_core.data import loaders
from qsci_core.evaluation.metrics import summarize
from qsci_core.forecasting.classical.features import build_features, feature_columns
from qsci_core.forecasting.classical.lightgbm_forecaster import LightGBMQuantileForecaster
from qsci_core.forecasting.classical.seasonal_naive import seasonal_naive_predict
from qsci_core.persistence.models import ForecastRunRecord, RunStatus

DEFAULT_SERIES_ID = "FOODS_3_090_CA_1_evaluation"
SUPPORTED_MODELS = {"seasonal_naive", "lightgbm", "vqr"}


def _load_series(series_id: str) -> pd.DataFrame:
    m5 = loaders.load_m5()
    day_cols = [c for c in m5["sales"].columns if c.startswith("d_")]
    row = m5["sales"][m5["sales"]["id"] == series_id]
    if row.empty:
        raise ValueError(f"series_id '{series_id}' not found in M5 sales_train_evaluation")
    row = row.iloc[0]
    day_to_date = m5["calendar"].set_index("d")["date"]
    return pd.DataFrame({
        "date": pd.to_datetime(day_to_date.reindex(day_cols).values),
        "sales": row[day_cols].astype(float).values,
    }).sort_values("date").reset_index(drop=True)


def create_run(db: Session, series_id: str, model: str, horizon: int) -> ForecastRunRecord:
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"unsupported model '{model}', must be one of {sorted(SUPPORTED_MODELS)}")
    run = ForecastRunRecord(
        dataset="m5", series_id=series_id, model=model, horizon=horizon,
        run_status=RunStatus.PENDING, label="LIVE" if model in ("seasonal_naive", "lightgbm") else "RESEARCH",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def execute_run(db: Session, run_id: int) -> None:
    """Runs synchronously in the calling context -- called directly for
    fast models, or via FastAPI BackgroundTasks for vqr."""
    run = db.get(ForecastRunRecord, run_id)
    if run is None:
        return
    run.run_status = RunStatus.RUNNING
    db.commit()

    try:
        series_df = _load_series(run.series_id)
        split_idx = len(series_df) - run.horizon
        train_df, test_df = series_df.iloc[:split_idx], series_df.iloc[split_idx:]
        t0 = time.perf_counter()

        if run.model == "seasonal_naive":
            p50 = seasonal_naive_predict(train_df, test_df, "sales", season_length=7)
            predictions = {"p50": p50.tolist()}
            metadata = {}
        elif run.model == "lightgbm":
            fc = LightGBMQuantileForecaster().fit(train_df, "date", "sales")
            future_dates = pd.to_datetime(test_df["date"]).reset_index(drop=True)
            preds = fc.predict(train_df, horizon=run.horizon, future_dates=future_dates)
            predictions = {f"p{int(q*100)}": v.tolist() for q, v in preds.items()}
            metadata = {"feature_columns": fc._feature_cols}
        elif run.model == "vqr":
            predictions, metadata = _run_vqr(train_df, test_df, run.horizon)
        else:
            raise ValueError(f"unsupported model '{run.model}'")

        runtime = time.perf_counter() - t0
        y_true = test_df["sales"].to_numpy()
        p50_key = "p50" if "p50" in predictions else sorted(predictions)[len(predictions) // 2]
        metrics = summarize(y_true, np.asarray(predictions[p50_key]))

        run.predictions = predictions
        run.metrics = metrics
        run.runtime_seconds = runtime
        run.model_metadata = metadata
        run.run_status = RunStatus.COMPLETE
        run.completed_at = datetime.now(timezone.utc)
    except Exception as exc:  # noqa: BLE001 -- must record failure, not crash the background task silently
        run.run_status = RunStatus.FAILED
        run.error = f"{type(exc).__name__}: {exc}"
        run.completed_at = datetime.now(timezone.utc)
    db.commit()


def _run_vqr(train_df: pd.DataFrame, test_df: pd.DataFrame, horizon: int, n_qubits: int = 4) -> tuple[dict, dict]:
    """RESEARCH only -- point forecaster, no native quantile output
    (Phase 5 finding: forecast_stability is N/A for this model). Uses the
    same leakage-safe PCA-reduction pipeline as notebooks 03/07."""
    from qsci_core.forecasting.quantum.feature_reduction import reduce_features_pca
    from qsci_core.forecasting.quantum.vqr_forecaster import QuantumVQRForecaster

    full_df = pd.concat([train_df, test_df], ignore_index=True)
    feat_df = build_features(full_df, "date", "sales")
    cols = feature_columns()
    split_idx = len(feat_df) - horizon
    if split_idx <= 0:
        raise ValueError("not enough history after feature engineering for the requested horizon")

    X_train, X_test = feat_df[cols].iloc[:split_idx].to_numpy(), feat_df[cols].iloc[split_idx:].to_numpy()
    y_train = feat_df["sales"].iloc[:split_idx].to_numpy()

    reduced = reduce_features_pca(X_train, X_test, n_components=n_qubits)
    forecaster = QuantumVQRForecaster(n_qubits=n_qubits).fit(reduced.X_train_reduced, y_train)
    preds = forecaster.predict(reduced.X_test_reduced)

    predictions = {"p50": preds[-horizon:].tolist()}
    meta = forecaster.metadata
    metadata = {
        "n_qubits": meta.n_qubits, "circuit_depth": meta.circuit_depth, "gate_count": meta.gate_count,
        "train_time_seconds": meta.train_time_seconds, "predict_time_seconds": meta.predict_time_seconds,
        "forecast_stability": "NOT AVAILABLE FOR THIS MODEL (point forecaster, no native quantile output -- Phase 5 finding)",
    }
    return predictions, metadata


def get_run(db: Session, run_id: int) -> ForecastRunRecord | None:
    return db.get(ForecastRunRecord, run_id)
