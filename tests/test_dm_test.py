import numpy as np
import pytest

from qsci_core.evaluation.dm_test import diebold_mariano_test


def test_dm_test_identical_forecasts_no_significant_difference():
    rng = np.random.default_rng(0)
    y_true = rng.normal(50, 5, 30)
    y_pred = y_true + rng.normal(0, 1, 30)
    result = diebold_mariano_test(y_true, y_pred, y_pred.copy())
    assert result.mean_loss_diff == pytest.approx(0.0)
    assert not result.significant


def test_dm_test_detects_clearly_better_forecast():
    rng = np.random.default_rng(1)
    y_true = rng.normal(50, 5, 50)
    y_pred_good = y_true + rng.normal(0, 0.5, 50)
    y_pred_bad = y_true + rng.normal(0, 20, 50)
    result = diebold_mariano_test(y_true, y_pred_good, y_pred_bad)
    assert result.mean_loss_diff < 0  # A (good) has lower loss than B (bad)
    assert result.significant
    assert result.p_value < 0.05


def test_dm_test_shape_mismatch_raises():
    with pytest.raises(ValueError):
        diebold_mariano_test(np.array([1.0, 2.0]), np.array([1.0]), np.array([1.0, 2.0]))


def test_dm_test_empty_raises():
    with pytest.raises(ValueError):
        diebold_mariano_test(np.array([]), np.array([]), np.array([]))


def test_dm_test_invalid_loss_raises():
    y = np.arange(15.0)
    with pytest.raises(ValueError):
        diebold_mariano_test(y, y, y, loss="not_a_real_loss")


def test_dm_test_small_sample_flagged_unreliable():
    y = np.arange(5.0)
    pred_a = y + 1
    pred_b = y + 2
    result = diebold_mariano_test(y, pred_a, pred_b)
    assert not result.reliable
    assert not result.significant  # unreliable results must never report significant=True
    assert "10" in result.reliability_note or "unreliable" in result.reliability_note.lower()


def test_dm_test_identical_predictions_zero_variance_unreliable():
    y = np.arange(15.0)
    result = diebold_mariano_test(y, y + 1, y + 1)  # A and B identical -> zero loss differential variance
    assert not result.reliable


def test_dm_test_interpretation_mentions_reliability_when_unreliable():
    y = np.arange(5.0)
    result = diebold_mariano_test(y, y, y + 1)
    assert "UNRELIABLE" in result.interpretation()
