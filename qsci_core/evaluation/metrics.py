"""Forecast accuracy metrics. All functions operate on real (or test) arrays —
no synthetic fallback for empty/invalid input; they raise instead."""

from __future__ import annotations

import numpy as np


def _validate(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.shape != y_pred.shape:
        raise ValueError(f"shape mismatch: y_true {y_true.shape} vs y_pred {y_pred.shape}")
    if y_true.size == 0:
        raise ValueError("y_true/y_pred are empty")
    return y_true, y_pred


def rmse(y_true, y_pred) -> float:
    y_true, y_pred = _validate(y_true, y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true, y_pred) -> float:
    y_true, y_pred = _validate(y_true, y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def wmape(y_true, y_pred) -> float:
    """Weighted MAPE: sum|error| / sum|actual|, as a percentage. Robust to
    zero-valued individual observations (unlike plain MAPE)."""
    y_true, y_pred = _validate(y_true, y_pred)
    denom = np.sum(np.abs(y_true))
    if denom == 0:
        raise ValueError("wMAPE undefined: sum of |y_true| is zero")
    return float(np.sum(np.abs(y_true - y_pred)) / denom * 100)


def bias(y_true, y_pred) -> float:
    """Mean signed error. Positive = systematic over-forecasting."""
    y_true, y_pred = _validate(y_true, y_pred)
    return float(np.mean(y_pred - y_true))


def fva(y_true, y_pred, y_baseline) -> float:
    """Forecast Value Add: relative wMAPE improvement over a baseline
    (e.g. seasonal-naive). Positive = model beats the baseline.
    FVA = 1 - (wmape(model) / wmape(baseline))."""
    y_true = np.asarray(y_true, dtype=float)
    y_baseline = np.asarray(y_baseline, dtype=float)
    baseline_wmape = wmape(y_true, y_baseline)
    if baseline_wmape == 0:
        raise ValueError("FVA undefined: baseline wMAPE is zero")
    model_wmape = wmape(y_true, y_pred)
    return float(1 - (model_wmape / baseline_wmape))


def pinball_loss(y_true, y_pred, quantile: float) -> float:
    """Quantile (pinball) loss — the metric quantile regressors are trained
    against. Lower is better; used to validate p10/p50/p90 calibration."""
    y_true, y_pred = _validate(y_true, y_pred)
    if not 0 < quantile < 1:
        raise ValueError(f"quantile must be in (0, 1), got {quantile}")
    diff = y_true - y_pred
    return float(np.mean(np.maximum(quantile * diff, (quantile - 1) * diff)))


def summarize(y_true, y_pred, y_baseline=None) -> dict:
    """Bundle the standard metric set into one dict."""
    out = {
        "rmse": rmse(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "wmape": wmape(y_true, y_pred),
        "bias": bias(y_true, y_pred),
    }
    if y_baseline is not None:
        out["fva"] = fva(y_true, y_pred, y_baseline)
    return out
