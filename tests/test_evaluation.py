import numpy as np
import pandas as pd
import pytest

from qsci_core.evaluation import metrics
from qsci_core.evaluation.backtest import rolling_origin_splits, run_backtest


def test_metrics_basic():
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([12.0, 18.0, 33.0])
    m = metrics.summarize(y_true, y_pred)
    assert m["rmse"] == pytest.approx(2.3805, abs=1e-3)
    assert m["mae"] == pytest.approx(2.333, abs=1e-2)
    assert m["bias"] == pytest.approx(1.0, abs=1e-2)  # mean(y_pred - y_true) = mean([2, -2, 3])


def test_metrics_empty_raises():
    with pytest.raises(ValueError):
        metrics.rmse(np.array([]), np.array([]))


def test_metrics_shape_mismatch_raises():
    with pytest.raises(ValueError):
        metrics.rmse(np.array([1, 2]), np.array([1, 2, 3]))


def test_wmape_zero_denominator_raises():
    with pytest.raises(ValueError):
        metrics.wmape(np.array([0.0, 0.0]), np.array([1.0, 1.0]))


def test_fva_zero_actuals_raises():
    # wMAPE (and therefore FVA) is weighted by |y_true| — an all-zero actual
    # series makes the denominator zero regardless of predictions.
    with pytest.raises(ValueError):
        metrics.fva(np.array([0.0, 0.0]), np.array([1.0, 2.0]), np.array([3.0, 4.0]))


def test_fva_positive_when_model_beats_baseline():
    y_true = np.array([10.0, 10.0, 10.0])
    y_pred = np.array([10.0, 10.0, 10.0])  # perfect
    y_baseline = np.array([5.0, 5.0, 5.0])  # bad baseline
    assert metrics.fva(y_true, y_pred, y_baseline) == pytest.approx(1.0)


def test_pinball_loss_rejects_bad_quantile():
    with pytest.raises(ValueError):
        metrics.pinball_loss(np.array([1.0]), np.array([1.0]), quantile=1.5)


def test_rolling_origin_splits_never_leaks_future():
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    splits = rolling_origin_splits(dates, horizon=7, n_splits=3, min_train_size=60)
    assert len(splits) == 3
    for train_idx, test_idx in splits:
        assert train_idx.max() < test_idx.min()
        assert len(test_idx) == 7


def test_rolling_origin_splits_insufficient_history_raises():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    with pytest.raises(ValueError):
        rolling_origin_splits(dates, horizon=7, n_splits=3, min_train_size=60)


def test_rolling_origin_splits_rejects_unsorted_dates():
    dates = pd.Series(pd.to_datetime(["2024-01-05", "2024-01-01", "2024-01-03"]))
    with pytest.raises(ValueError):
        rolling_origin_splits(dates, horizon=1, n_splits=1, min_train_size=1)


def test_run_backtest_rejects_nan_target():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=80, freq="D"),
        "y": [1.0] * 79 + [np.nan],
    })

    def fit_predict(train_df, test_df):
        return np.zeros(len(test_df))

    with pytest.raises(ValueError):
        run_backtest(df, "date", "y", fit_predict, horizon=5, n_splits=2, min_train_size=60)


def test_run_backtest_rejects_empty_df():
    df = pd.DataFrame({"date": [], "y": []})

    def fit_predict(train_df, test_df):
        return np.zeros(len(test_df))

    with pytest.raises(ValueError):
        run_backtest(df, "date", "y", fit_predict, horizon=5, n_splits=2, min_train_size=60)


def test_run_backtest_rejects_missing_column():
    df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=80, freq="D")})

    def fit_predict(train_df, test_df):
        return np.zeros(len(test_df))

    with pytest.raises(ValueError):
        run_backtest(df, "date", "y", fit_predict, horizon=5, n_splits=2, min_train_size=60)


def test_run_backtest_produces_fold_metrics():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=100, freq="D"),
        "y": 50 + rng.normal(0, 1, 100),
    })

    def fit_predict(train_df, test_df):
        return np.full(len(test_df), train_df["y"].mean())

    result = run_backtest(df, "date", "y", fit_predict, horizon=7, n_splits=3, min_train_size=60)
    assert len(result.folds) == 3
    assert "rmse" in result.mean_metrics
    assert result.to_dataframe().shape[0] == 3
