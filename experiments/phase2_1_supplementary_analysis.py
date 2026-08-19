"""Phase 2.1 supplementary validity analysis — NOT part of the committed
Phase 2 experiment. Run once, output captured into
docs/PHASE_2_1_VALIDITY_AUDIT.md. Does not modify qsci_core, notebook 03,
or the Phase 2 results already committed at 6b1b28a.

Two things are computed here:
1. A leakage-free re-evaluation of VQR — the original Phase 2 notebook
   built test-set lag/rolling features from `build_features(windowed, ...)`
   where `windowed` includes the real test-period actuals, so lag_1/lag_7/
   rollmean/rollstd for test days 2+ leak real future values a genuine
   forecast wouldn't have. This recomputes VQR predictions recursively,
   using only real training history and the model's own prior predictions
   for each step's features -- exactly how the classical LightGBM baseline
   in the same notebook already worked.
2. A repeated-run non-determinism check at N=4 (cheap enough to repeat).
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qsci_core.data import loaders
from qsci_core.evaluation import metrics as metrics_mod
from qsci_core.forecasting.classical.features import DEFAULT_LAGS, DEFAULT_ROLLING_WINDOWS, feature_columns
from qsci_core.forecasting.quantum.vqr_forecaster import QuantumVQRForecaster

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERIES_ID = "FOODS_3_090_CA_1_evaluation"
TEST_START, TEST_END = pd.Timestamp("2016-05-09"), pd.Timestamp("2016-05-22")
HORIZON = 14
SEED = 42
N_TRAIN = 18
WARMUP = 28


def load_series():
    m5 = loaders.load_m5(PROJECT_ROOT / "data" / "raw" / "m5")
    sales, calendar = m5["sales"], m5["calendar"]
    day_cols = [c for c in sales.columns if c.startswith("d_")]
    row = sales[sales["id"] == SERIES_ID].iloc[0]
    day_to_date = calendar.set_index("d")["date"]
    return pd.DataFrame({
        "date": pd.to_datetime(day_to_date.reindex(day_cols).values),
        "sales": row[day_cols].astype(float).values,
    }).sort_values("date").reset_index(drop=True)


def next_step_features(history_dates, history_vals, next_date):
    """Same logic as LightGBMQuantileForecaster._next_step_features, but
    standalone -- computes the classical 12-column feature row for the
    period immediately after `history_vals`, using ONLY those real/prior-
    predicted values, never a real future actual."""
    row = {}
    for lag in DEFAULT_LAGS:
        row[f"lag_{lag}"] = history_vals[-lag] if len(history_vals) >= lag else np.nan
    for window in DEFAULT_ROLLING_WINDOWS:
        tail = history_vals[-window:] if len(history_vals) >= window else history_vals
        row[f"rollmean_{window}"] = float(np.mean(tail)) if len(tail) else np.nan
        row[f"rollstd_{window}"] = float(np.std(tail, ddof=1)) if len(tail) > 1 else 0.0
    row["dow"] = next_date.dayofweek
    row["day"] = next_date.day
    row["month"] = next_date.month
    row["is_weekend"] = int(next_date.dayofweek >= 5)
    return row


def build_train_features(series_df):
    """Build the N_TRAIN leakage-free training rows exactly as notebook 03
    did (train rows only ever reference real history strictly before
    themselves -- this part of the original notebook was NOT leaky)."""
    from qsci_core.forecasting.classical.features import build_features

    train_end_idx = series_df.index[series_df["date"] < TEST_START][-1]
    window_start_idx = max(0, train_end_idx - (N_TRAIN + WARMUP) + 1)
    train_window = series_df.iloc[window_start_idx:train_end_idx + 1]
    feat = build_features(train_window, "date", "sales")
    return feat.tail(N_TRAIN)


def leakage_free_vqr_predict(n_qubits, X_train_raw, y_train, series_df, optimizer_maxiter=10, seed=SEED):
    """Fits VQR exactly as notebook 03 did (train side was never leaky),
    then predicts the 14-day horizon RECURSIVELY -- each step's classical
    features come from real training history plus the model's own prior
    predictions, then the SAME fitted scaler+PCA (refit here on the
    identical X_train_raw, deterministic given random_state=0) reduces
    them to n_qubits dimensions, exactly mirroring the leakage-safety rule
    already enforced for training in feature_reduction.py.
    """
    scaler = StandardScaler().fit(X_train_raw)
    pca = PCA(n_components=n_qubits, random_state=0).fit(scaler.transform(X_train_raw))
    X_train_reduced = pca.transform(scaler.transform(X_train_raw))

    model = QuantumVQRForecaster(n_qubits=n_qubits, optimizer_maxiter=optimizer_maxiter, seed=seed)
    t0 = time.perf_counter()
    model.fit(X_train_reduced, y_train)
    train_time = time.perf_counter() - t0

    train_end_idx = series_df.index[series_df["date"] < TEST_START][-1]
    history_dates = list(series_df["date"].iloc[:train_end_idx + 1])
    history_vals = list(series_df["sales"].iloc[:train_end_idx + 1])

    future_dates = pd.date_range(TEST_START, TEST_END, freq="D")
    preds = []
    t0 = time.perf_counter()
    for next_date in future_dates:
        row = next_step_features(history_dates, np.array(history_vals), next_date)
        raw_row = np.array([[row[c] for c in feature_columns()]])
        reduced_row = pca.transform(scaler.transform(raw_row))
        pred = model.predict(reduced_row)[0]
        preds.append(pred)
        history_dates.append(next_date)
        history_vals.append(pred)  # feed back the PREDICTION, never the real actual
    predict_time = time.perf_counter() - t0

    return np.array(preds), model, train_time, predict_time


def main():
    series_df = load_series()
    train_feat = build_train_features(series_df)
    cols = feature_columns()
    X_train_raw = train_feat[cols].to_numpy()
    y_train = train_feat["sales"].to_numpy()

    y_test = series_df[(series_df["date"] >= TEST_START) & (series_df["date"] <= TEST_END)]["sales"].to_numpy()

    print("=== 1. Leakage-free VQR re-evaluation ===")
    for n in (4, 8, 12):
        preds, model, train_time, predict_time = leakage_free_vqr_predict(n, X_train_raw, y_train, series_df)
        m = metrics_mod.summarize(y_test, preds)
        print(f"N={n}: train={train_time:.1f}s predict={predict_time:.2f}s metrics={m}")

    print("\n=== 2. Non-determinism check: N=4, 5 repeated runs, same seed ===")
    for run_i in range(5):
        preds, model, train_time, predict_time = leakage_free_vqr_predict(4, X_train_raw, y_train, series_df, seed=SEED)
        m = metrics_mod.summarize(y_test, preds)
        pred_hash = hashlib.sha256(np.round(preds, 6).tobytes()).hexdigest()[:12]
        print(f"run={run_i} seed={SEED} rmse={m['rmse']:.4f} mae={m['mae']:.4f} runtime={train_time:.2f}s hash={pred_hash}")


if __name__ == "__main__":
    main()
