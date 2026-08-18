"""Seasonal-naive baseline — the honesty check every other forecaster is
measured against via FVA."""

from __future__ import annotations

import numpy as np
import pandas as pd


def seasonal_naive_predict(train_df: pd.DataFrame, test_df: pd.DataFrame, target_col: str, season_length: int = 7) -> np.ndarray:
    """Predict each test period as the value observed `season_length` periods
    before it, walking forward through the combined train+test history so
    later test periods can reference earlier *predicted* test periods'
    actual antecedents once available, exactly like a real deployed naive
    forecaster would.
    """
    if len(train_df) < season_length:
        raise ValueError(f"insufficient history: need >= {season_length} periods, got {len(train_df)}")

    history = list(train_df[target_col].to_numpy())
    preds = []
    for _ in range(len(test_df)):
        preds.append(history[-season_length])
        history.append(history[-season_length])  # naive forecast becomes next season's reference
    return np.asarray(preds)
