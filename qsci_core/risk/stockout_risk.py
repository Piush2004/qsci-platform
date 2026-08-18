"""Risk layer: stockout probability and demand volatility from real forecast
quantiles and history — no distributional assumption beyond what the
quantile spread itself supports.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StockoutRiskEstimate:
    probability: float
    method: str
    status: str = "LIVE"


def stockout_risk_from_quantiles(p10: float, p50: float, p90: float, reorder_point: float) -> StockoutRiskEstimate:
    """Approximate P(demand > reorder_point) from the p10/p50/p90 forecast
    quantiles by fitting a normal distribution to the p10-p90 spread
    (sigma ~= (p90 - p10) / (2 * 1.2816), since 1.2816 is the z-score for
    the 90th percentile of a standard normal). This is a documented
    approximation, not an exact fit to the true (unknown) demand
    distribution — it degrades if the real distribution is heavily skewed.
    """
    if not (p10 <= p50 <= p90):
        raise ValueError(f"quantiles must satisfy p10 <= p50 <= p90, got p10={p10}, p50={p50}, p90={p90}")

    spread = p90 - p10
    if spread == 0:
        # Degenerate forecast (identical quantiles) - deterministic risk.
        probability = 1.0 if p50 < reorder_point else 0.0
        return StockoutRiskEstimate(probability=probability, method="degenerate_zero_spread")

    z90 = 1.2816
    sigma = spread / (2 * z90)
    z = (reorder_point - p50) / sigma
    probability = 1 - _standard_normal_cdf(z)
    return StockoutRiskEstimate(probability=float(np.clip(probability, 0.0, 1.0)), method="normal_approx_from_quantile_spread")


def _standard_normal_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def demand_volatility(history: np.ndarray) -> float:
    """Coefficient of variation (std / mean) of historical demand — a
    unit-free volatility measure usable across SKUs with different scales.
    """
    history = np.asarray(history, dtype=float)
    if history.size == 0:
        raise ValueError("history is empty")
    if history.size < 2:
        raise ValueError("need at least 2 observations to compute volatility")
    mean = float(np.mean(history))
    if mean == 0:
        raise ValueError("mean demand is zero — coefficient of variation undefined")
    return float(np.std(history, ddof=1) / mean)
