"""LightGBM quantile-regression demand forecaster (p10/p50/p90).

Forecasts are produced recursively: each step's lag/rolling features are
built from real history plus the model's own p50 predictions for steps
already forecast (never from future actuals — that would leak information
a real deployed forecaster wouldn't have). p10/p90 are re-predicted at each
step from those same recursively-built features, not simply offset from p50.
"""

from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd

from qsci_core.forecasting.classical.features import (
    DEFAULT_LAGS, DEFAULT_ROLLING_WINDOWS, build_features, feature_columns,
)

DEFAULT_QUANTILES = (0.1, 0.5, 0.9)


class LightGBMQuantileForecaster:
    def __init__(
        self,
        quantiles: tuple[float, ...] = DEFAULT_QUANTILES,
        lags: tuple[int, ...] = DEFAULT_LAGS,
        rolling_windows: tuple[int, ...] = DEFAULT_ROLLING_WINDOWS,
        lgb_params: dict | None = None,
    ):
        self.quantiles = quantiles
        self.lags = lags
        self.rolling_windows = rolling_windows
        self.lgb_params = {
            "n_estimators": 200,
            "num_leaves": 15,
            "learning_rate": 0.05,
            "min_child_samples": 5,
            "verbosity": -1,
            **(lgb_params or {}),
        }
        self.models: dict[float, lgb.LGBMRegressor] = {}
        self._feature_cols = feature_columns(lags, rolling_windows)

    def fit(self, train_df: pd.DataFrame, date_col: str, target_col: str) -> "LightGBMQuantileForecaster":
        feat_df = build_features(train_df, date_col, target_col, self.lags, self.rolling_windows)
        if feat_df.empty:
            raise ValueError("no rows left after feature engineering — insufficient history for the given lags")

        X = feat_df[self._feature_cols]
        y = feat_df[target_col]
        for q in self.quantiles:
            model = lgb.LGBMRegressor(objective="quantile", alpha=q, **self.lgb_params)
            model.fit(X, y)
            self.models[q] = model
        self._date_col = date_col
        self._target_col = target_col
        return self

    def predict(self, train_df: pd.DataFrame, horizon: int, future_dates: pd.DatetimeIndex) -> dict[float, np.ndarray]:
        """Recursively forecast `horizon` steps ahead of train_df's history."""
        if not self.models:
            raise RuntimeError("forecaster not fit yet")
        if len(future_dates) != horizon:
            raise ValueError(f"future_dates length {len(future_dates)} != horizon {horizon}")

        max_window = max(max(self.lags), max(self.rolling_windows)) if self.rolling_windows else max(self.lags)
        history = train_df[[self._date_col, self._target_col]].sort_values(self._date_col).tail(max_window * 3).reset_index(drop=True)

        preds: dict[float, list[float]] = {q: [] for q in self.quantiles}
        running = history.copy()

        for step_date in future_dates:
            # build_features() drops NaN-target rows, which the pending step
            # legitimately has — so the next-step feature row is computed
            # directly from `running` history instead.
            feat_row = self._next_step_features(running)
            step_preds = {q: float(model.predict(feat_row[self._feature_cols])[0]) for q, model in self.models.items()}

            # Independently-trained quantile models can "cross" (e.g. the p10
            # model predicts above the p90 model's prediction at some step) —
            # a documented LightGBM limitation, not a bug here. Rectify by
            # sorting predictions into the same order as the quantiles
            # themselves (standard quantile-crossing fix).
            ordered_q = sorted(self.quantiles)
            ordered_vals = sorted(step_preds[q] for q in ordered_q)
            step_preds = dict(zip(ordered_q, ordered_vals))

            for q in self.quantiles:
                preds[q].append(step_preds[q])

            p50_key = min(self.quantiles, key=lambda q: abs(q - 0.5))
            running = pd.concat(
                [running, pd.DataFrame({self._date_col: [step_date], self._target_col: [step_preds[p50_key]]})],
                ignore_index=True,
            )

        return {q: np.asarray(v) for q, v in preds.items()}

    def _next_step_features(self, history: pd.DataFrame) -> pd.DataFrame:
        """Compute the feature row for the period immediately after `history`."""
        vals = history[self._target_col].to_numpy()
        last_date = pd.to_datetime(history[self._date_col].max())
        next_date = last_date + pd.Timedelta(days=1)

        row = {}
        for lag in self.lags:
            row[f"lag_{lag}"] = vals[-lag] if len(vals) >= lag else np.nan
        for window in self.rolling_windows:
            tail = vals[-window:] if len(vals) >= window else vals
            row[f"rollmean_{window}"] = float(np.mean(tail)) if len(tail) else np.nan
            row[f"rollstd_{window}"] = float(np.std(tail, ddof=1)) if len(tail) > 1 else 0.0
        row["dow"] = next_date.dayofweek
        row["day"] = next_date.day
        row["month"] = next_date.month
        row["is_weekend"] = int(next_date.dayofweek >= 5)
        return pd.DataFrame([row])


def lightgbm_p50_point_forecast(train_df: pd.DataFrame, test_df: pd.DataFrame, date_col: str, target_col: str) -> np.ndarray:
    """Adapter matching qsci_core.evaluation.backtest's fit_predict_fn signature
    — trains fresh on train_df, returns only the p50 point forecast for
    test_df's dates."""
    model = LightGBMQuantileForecaster(quantiles=(0.5,)).fit(train_df, date_col, target_col)
    future_dates = pd.to_datetime(test_df[date_col]).reset_index(drop=True)
    preds = model.predict(train_df, horizon=len(test_df), future_dates=future_dates)
    return preds[0.5]
