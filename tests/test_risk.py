import numpy as np
import pytest

from qsci_core.risk.stockout_risk import demand_volatility, stockout_risk_from_quantiles


def test_stockout_risk_rejects_out_of_order_quantiles():
    with pytest.raises(ValueError):
        stockout_risk_from_quantiles(p10=50, p50=40, p90=60, reorder_point=45)


def test_stockout_risk_high_when_reorder_point_far_below_demand():
    # Reorder point of 10 is far below the demand distribution (p10=40) —
    # the buffer is inadequate, so demand almost certainly exceeds it:
    # P(demand > reorder_point) is HIGH. This is the standard reorder-point
    # inventory model, not an inverted one.
    est = stockout_risk_from_quantiles(p10=40, p50=50, p90=60, reorder_point=10)
    assert est.probability > 0.95
    assert est.status == "LIVE"


def test_stockout_risk_low_when_reorder_point_far_above_demand():
    # Reorder point of 100 is far above the demand distribution (p90=60) —
    # ample buffer, so demand almost never exceeds it: LOW stockout risk.
    est = stockout_risk_from_quantiles(p10=40, p50=50, p90=60, reorder_point=100)
    assert est.probability < 0.05


def test_stockout_risk_degenerate_zero_spread():
    est = stockout_risk_from_quantiles(p10=50, p50=50, p90=50, reorder_point=60)
    assert est.probability == 1.0
    assert est.method == "degenerate_zero_spread"

    est2 = stockout_risk_from_quantiles(p10=50, p50=50, p90=50, reorder_point=40)
    assert est2.probability == 0.0


def test_demand_volatility_empty_raises():
    with pytest.raises(ValueError):
        demand_volatility(np.array([]))


def test_demand_volatility_single_value_raises():
    with pytest.raises(ValueError):
        demand_volatility(np.array([5.0]))


def test_demand_volatility_zero_mean_raises():
    with pytest.raises(ValueError):
        demand_volatility(np.array([-5.0, 5.0]))


def test_demand_volatility_known_value():
    history = np.array([10.0, 10.0, 10.0, 10.0])  # zero variance
    assert demand_volatility(history) == pytest.approx(0.0)
