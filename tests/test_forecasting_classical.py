import numpy as np
import pandas as pd
import pytest

from qsci_core.forecasting.classical.features import build_features
from qsci_core.forecasting.classical.lightgbm_forecaster import LightGBMQuantileForecaster
from qsci_core.forecasting.classical.seasonal_naive import seasonal_naive_predict


def _synthetic_series(n=120, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    vals = np.maximum(50 + 10 * np.sin(np.arange(n) * 2 * np.pi / 7) + rng.normal(0, 3, n), 0)
    return pd.DataFrame({"date": dates, "sales": vals})


def test_build_features_missing_target_raises():
    df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=10)})
    with pytest.raises(ValueError):
        build_features(df, "date", "sales")


def test_build_features_drops_warmup_rows_not_impute():
    df = _synthetic_series(n=50)
    feat = build_features(df, "date", "sales", lags=(1, 7), rolling_windows=(7,))
    assert feat.isna().sum().sum() == 0
    assert len(feat) == 50 - 7  # dropped, not filled


def test_seasonal_naive_insufficient_history_raises():
    df = _synthetic_series(n=5)
    train_df, test_df = df.iloc[:3], df.iloc[3:]
    with pytest.raises(ValueError):
        seasonal_naive_predict(train_df, test_df, "sales", season_length=7)


def test_seasonal_naive_predicts_expected_shape():
    df = _synthetic_series(n=30)
    train_df, test_df = df.iloc[:23], df.iloc[23:]
    preds = seasonal_naive_predict(train_df, test_df, "sales", season_length=7)
    assert len(preds) == len(test_df)


def test_lightgbm_forecaster_rejects_empty_train():
    df = _synthetic_series(n=5)
    model = LightGBMQuantileForecaster()
    with pytest.raises(ValueError):
        model.fit(df, "date", "sales")


def test_lightgbm_forecaster_rejects_missing_target_column():
    df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=50)})
    model = LightGBMQuantileForecaster()
    with pytest.raises(ValueError):
        model.fit(df, "date", "sales")


def test_lightgbm_forecaster_predict_before_fit_raises():
    model = LightGBMQuantileForecaster()
    df = _synthetic_series(n=50)
    future_dates = pd.date_range("2024-03-01", periods=5)
    with pytest.raises(RuntimeError):
        model.predict(df, horizon=5, future_dates=future_dates)


def test_lightgbm_forecaster_quantiles_are_monotonic():
    df = _synthetic_series(n=150)
    train_df, test_df = df.iloc[:130], df.iloc[130:]
    model = LightGBMQuantileForecaster().fit(train_df, "date", "sales")
    future_dates = pd.to_datetime(test_df["date"]).reset_index(drop=True)
    preds = model.predict(train_df, horizon=len(test_df), future_dates=future_dates)
    assert np.all(preds[0.1] <= preds[0.5] + 1e-9)
    assert np.all(preds[0.5] <= preds[0.9] + 1e-9)


def test_lightgbm_forecaster_horizon_mismatch_raises():
    df = _synthetic_series(n=150)
    train_df = df.iloc[:130]
    model = LightGBMQuantileForecaster().fit(train_df, "date", "sales")
    future_dates = pd.date_range("2024-06-01", periods=5)
    with pytest.raises(ValueError):
        model.predict(train_df, horizon=10, future_dates=future_dates)
