"""Confidence decomposition: a documented mathematical formulation, not an
invented percentage.

Overall confidence is a weighted average of four components, each mapped to
[0, 1] by an explicit, stated formula:

  data_quality        = 1 - (data quality report's problem rate)
  forecast_stability   = 1 / (1 + relative quantile spread), spread = (p90-p10)/max(p50, eps)
  model_consensus       = 1 - normalized disagreement between two independent
                          forecasters (e.g. LightGBM vs. seasonal-naive)
  backtest_performance  = max(0, 1 - backtest_wmape / 100)

  overall = w_dq*data_quality + w_fs*forecast_stability + w_mc*model_consensus + w_bp*backtest_performance

Default weights are equal (0.25 each) unless the caller has evidence to
justify otherwise — equal weighting is itself a documented, overridable
assumption, not a tuned result.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_WEIGHTS = {
    "data_quality": 0.25,
    "forecast_stability": 0.25,
    "model_consensus": 0.25,
    "backtest_performance": 0.25,
}


@dataclass(frozen=True)
class ConfidenceBreakdown:
    data_quality: float
    forecast_stability: float
    model_consensus: float
    backtest_performance: float
    weights: dict = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    status: str = "LIVE"

    @property
    def overall(self) -> float:
        return (
            self.weights["data_quality"] * self.data_quality
            + self.weights["forecast_stability"] * self.forecast_stability
            + self.weights["model_consensus"] * self.model_consensus
            + self.weights["backtest_performance"] * self.backtest_performance
        )

    def to_dict(self) -> dict:
        return {
            "data_quality": self.data_quality,
            "forecast_stability": self.forecast_stability,
            "model_consensus": self.model_consensus,
            "backtest_performance": self.backtest_performance,
            "overall": self.overall,
            "weights": self.weights,
            "status": self.status,
        }


def _validate_unit_interval(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value}")


def data_quality_score(missing_pct: float, negative_value_rate: float, duplicate_rate: float) -> float:
    """1 minus the average of three problem rates (all expressed as
    fractions in [0, 1], not percentages)."""
    for name, val in [("missing_pct", missing_pct), ("negative_value_rate", negative_value_rate), ("duplicate_rate", duplicate_rate)]:
        _validate_unit_interval(name, val)
    return 1.0 - (missing_pct + negative_value_rate + duplicate_rate) / 3.0


def forecast_stability_score(p10: float, p50: float, p90: float, eps: float = 1e-6) -> float:
    if not (p10 <= p50 <= p90):
        raise ValueError(f"quantiles must satisfy p10 <= p50 <= p90, got p10={p10}, p50={p50}, p90={p90}")
    relative_spread = (p90 - p10) / max(p50, eps)
    return 1.0 / (1.0 + relative_spread)


def model_consensus_score(forecast_a: float, forecast_b: float, eps: float = 1e-6) -> float:
    """1 minus normalized disagreement between two independent forecasts of
    the same target (e.g. LightGBM p50 vs. seasonal-naive)."""
    denom = max(abs(forecast_a), abs(forecast_b), eps)
    disagreement = abs(forecast_a - forecast_b) / denom
    return float(max(0.0, 1.0 - disagreement))


def backtest_performance_score(backtest_wmape: float) -> float:
    if backtest_wmape < 0:
        raise ValueError(f"backtest_wmape must be non-negative, got {backtest_wmape}")
    return max(0.0, 1.0 - backtest_wmape / 100.0)


def compute_confidence(
    data_quality: float,
    forecast_stability: float,
    model_consensus: float,
    backtest_performance: float,
    weights: dict | None = None,
) -> ConfidenceBreakdown:
    weights = weights or dict(DEFAULT_WEIGHTS)
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError(f"weights must sum to 1.0, got {sum(weights.values())}")
    for name, val in [
        ("data_quality", data_quality),
        ("forecast_stability", forecast_stability),
        ("model_consensus", model_consensus),
        ("backtest_performance", backtest_performance),
    ]:
        _validate_unit_interval(name, val)
    return ConfidenceBreakdown(
        data_quality=data_quality,
        forecast_stability=forecast_stability,
        model_consensus=model_consensus,
        backtest_performance=backtest_performance,
        weights=weights,
    )
