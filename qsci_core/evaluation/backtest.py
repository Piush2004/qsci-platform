"""Rolling-origin time-series backtesting. Never a random split — every fold
trains only on data strictly before its test window."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from qsci_core.evaluation import metrics as metrics_mod


@dataclass
class Fold:
    fold_id: int
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    metrics: dict = field(default_factory=dict)


@dataclass
class BacktestResult:
    folds: list[Fold]
    mean_metrics: dict

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for f in self.folds:
            row = {"fold_id": f.fold_id, "train_end": f.train_end, "test_start": f.test_start, "test_end": f.test_end}
            row.update(f.metrics)
            rows.append(row)
        return pd.DataFrame(rows)


def rolling_origin_splits(
    dates: pd.Series,
    horizon: int,
    n_splits: int,
    min_train_size: int,
    step: int | None = None,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Generate (train_idx, test_idx) index arrays for rolling-origin
    backtesting over a sorted, unique date index.

    Each fold trains on everything up to a cutoff and tests on the next
    `horizon` periods immediately after — never on data from the future
    relative to the cutoff, and never a random split.
    """
    dates = pd.Series(pd.to_datetime(dates)).reset_index(drop=True)
    if not dates.is_monotonic_increasing:
        raise ValueError("dates must be sorted ascending")
    n = len(dates)
    if n < min_train_size + horizon:
        raise ValueError(
            f"insufficient history: {n} periods available, need at least "
            f"min_train_size + horizon = {min_train_size + horizon}"
        )
    step = step or horizon

    splits = []
    last_cutoff = n - horizon
    first_cutoff = min_train_size
    cutoffs = list(range(last_cutoff, first_cutoff - 1, -step))[:n_splits]
    cutoffs.reverse()
    if not cutoffs:
        raise ValueError("no valid folds fit the given min_train_size/horizon/n_splits")

    for cutoff in cutoffs:
        train_idx = np.arange(0, cutoff)
        test_idx = np.arange(cutoff, cutoff + horizon)
        splits.append((train_idx, test_idx))
    return splits


def run_backtest(
    df: pd.DataFrame,
    date_col: str,
    target_col: str,
    fit_predict_fn: Callable[[pd.DataFrame, pd.DataFrame], np.ndarray],
    horizon: int,
    n_splits: int,
    min_train_size: int,
    baseline_fn: Callable[[pd.DataFrame, pd.DataFrame], np.ndarray] | None = None,
) -> BacktestResult:
    """Run rolling-origin backtesting for a single series.

    `fit_predict_fn(train_df, test_df) -> np.ndarray` must be trained only on
    `train_df` and return point predictions aligned to `test_df`'s rows.
    """
    if df.empty:
        raise ValueError("df is empty")
    if target_col not in df.columns:
        raise ValueError(f"missing target column: {target_col}")
    if df[target_col].isna().any():
        raise ValueError(f"target column '{target_col}' contains NaN values")

    df = df.sort_values(date_col).reset_index(drop=True)
    splits = rolling_origin_splits(df[date_col], horizon, n_splits, min_train_size)

    folds = []
    for i, (train_idx, test_idx) in enumerate(splits):
        train_df, test_df = df.iloc[train_idx], df.iloc[test_idx]
        y_pred = np.asarray(fit_predict_fn(train_df, test_df))
        y_true = test_df[target_col].to_numpy()

        y_baseline = None
        if baseline_fn is not None:
            y_baseline = np.asarray(baseline_fn(train_df, test_df))

        fold_metrics = metrics_mod.summarize(y_true, y_pred, y_baseline)
        folds.append(Fold(
            fold_id=i,
            train_end=train_df[date_col].max(),
            test_start=test_df[date_col].min(),
            test_end=test_df[date_col].max(),
            metrics=fold_metrics,
        ))

    keys = folds[0].metrics.keys()
    mean_metrics = {k: float(np.mean([f.metrics[k] for f in folds])) for k in keys}
    return BacktestResult(folds=folds, mean_metrics=mean_metrics)
