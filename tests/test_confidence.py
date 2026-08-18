import pytest

from qsci_core.confidence.decomposition import (
    DEFAULT_WEIGHTS, backtest_performance_score, compute_confidence,
    data_quality_score, forecast_stability_score, model_consensus_score,
)


def test_data_quality_score_perfect():
    assert data_quality_score(0.0, 0.0, 0.0) == 1.0


def test_data_quality_score_out_of_range_raises():
    with pytest.raises(ValueError):
        data_quality_score(1.5, 0.0, 0.0)


def test_forecast_stability_score_narrower_interval_is_higher():
    narrow = forecast_stability_score(p10=48, p50=50, p90=52)
    wide = forecast_stability_score(p10=20, p50=50, p90=80)
    assert narrow > wide


def test_forecast_stability_rejects_out_of_order_quantiles():
    with pytest.raises(ValueError):
        forecast_stability_score(p10=60, p50=50, p90=70)


def test_model_consensus_perfect_agreement():
    assert model_consensus_score(50.0, 50.0) == pytest.approx(1.0)


def test_model_consensus_large_disagreement_near_zero():
    score = model_consensus_score(10.0, 1000.0)
    assert score < 0.1


def test_backtest_performance_negative_wmape_raises():
    with pytest.raises(ValueError):
        backtest_performance_score(-1.0)


def test_backtest_performance_clips_at_zero_for_bad_forecasts():
    assert backtest_performance_score(150.0) == 0.0


def test_compute_confidence_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        compute_confidence(0.5, 0.5, 0.5, 0.5, weights={"data_quality": 0.5, "forecast_stability": 0.5, "model_consensus": 0.5, "backtest_performance": 0.5})


def test_compute_confidence_rejects_out_of_range_component():
    with pytest.raises(ValueError):
        compute_confidence(1.5, 0.5, 0.5, 0.5)


def test_compute_confidence_overall_matches_weighted_formula():
    breakdown = compute_confidence(0.8, 0.6, 0.9, 0.7)
    expected = sum(DEFAULT_WEIGHTS[k] * v for k, v in zip(
        ["data_quality", "forecast_stability", "model_consensus", "backtest_performance"], [0.8, 0.6, 0.9, 0.7]
    ))
    assert breakdown.overall == pytest.approx(expected)


def test_compute_confidence_custom_weights():
    weights = {"data_quality": 1.0, "forecast_stability": 0.0, "model_consensus": 0.0, "backtest_performance": 0.0}
    breakdown = compute_confidence(0.5, 0.9, 0.9, 0.9, weights=weights)
    assert breakdown.overall == pytest.approx(0.5)
