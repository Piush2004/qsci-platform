"""Lag/calendar feature engineering shared by classical forecasters."""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_LAGS = (1, 7, 14, 28)
DEFAULT_ROLLING_WINDOWS = (7, 28)


def build_features(df: pd.DataFrame, date_col: str, target_col: str,
                    lags: tuple[int, ...] = DEFAULT_LAGS,
                    rolling_windows: tuple[int, ...] = DEFAULT_ROLLING_WINDOWS) -> pd.DataFrame:
    """Add lag, rolling-statistic, and calendar features to a single-series
    dataframe sorted by date. Rows whose lag/rolling features can't be
    computed (start of history) are dropped, not imputed — imputing them
    would fabricate signal that wasn't there.
    """
    if target_col not in df.columns:
        raise ValueError(f"missing target column: {target_col}")
    if date_col not in df.columns:
        raise ValueError(f"missing date column: {date_col}")

    out = df.sort_values(date_col).reset_index(drop=True).copy()
    out[date_col] = pd.to_datetime(out[date_col])

    for lag in lags:
        out[f"lag_{lag}"] = out[target_col].shift(lag)
    for window in rolling_windows:
        shifted = out[target_col].shift(1)
        out[f"rollmean_{window}"] = shifted.rolling(window).mean()
        out[f"rollstd_{window}"] = shifted.rolling(window).std()

    out["dow"] = out[date_col].dt.dayofweek
    out["day"] = out[date_col].dt.day
    out["month"] = out[date_col].dt.month
    out["is_weekend"] = (out["dow"] >= 5).astype(int)

    max_lag = max(max(lags), max(rolling_windows))
    out = out.iloc[max_lag:].reset_index(drop=True)
    return out


def feature_columns(lags: tuple[int, ...] = DEFAULT_LAGS,
                     rolling_windows: tuple[int, ...] = DEFAULT_ROLLING_WINDOWS) -> list[str]:
    cols = [f"lag_{l}" for l in lags]
    for w in rolling_windows:
        cols += [f"rollmean_{w}", f"rollstd_{w}"]
    cols += ["dow", "day", "month", "is_weekend"]
    return cols
