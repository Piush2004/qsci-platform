import pytest

from qsci_core.financial.eoq import (
    CostAssumptions, annual_holding_cost, annual_ordering_cost,
    economic_order_quantity, expected_stockout_cost, reorder_point,
    safety_stock, total_inventory_cost,
)


def _costs():
    return CostAssumptions(holding_cost_per_unit_per_year=2.0, ordering_cost_per_order=50.0, stockout_cost_per_unit=10.0)


def test_cost_assumptions_status_is_illustrative():
    assert _costs().status == "ILLUSTRATIVE"


def test_cost_assumptions_rejects_negative_inputs():
    with pytest.raises(ValueError):
        CostAssumptions(holding_cost_per_unit_per_year=-1.0, ordering_cost_per_order=1.0, stockout_cost_per_unit=1.0)


def test_eoq_zero_demand_raises():
    with pytest.raises(ValueError):
        economic_order_quantity(annual_demand=0, costs=_costs())


def test_eoq_zero_holding_cost_raises():
    costs = CostAssumptions(holding_cost_per_unit_per_year=0.0, ordering_cost_per_order=50.0, stockout_cost_per_unit=10.0)
    with pytest.raises(ValueError):
        economic_order_quantity(annual_demand=1000, costs=costs)


def test_eoq_known_value():
    # classic textbook check: D=1000, S=50, H=2 -> sqrt(2*1000*50/2) = sqrt(50000) = 223.6
    eoq = economic_order_quantity(annual_demand=1000, costs=_costs())
    assert eoq == pytest.approx(223.6, abs=0.1)


def test_safety_stock_negative_std_raises():
    with pytest.raises(ValueError):
        safety_stock(demand_std=-1, lead_time_days=7, service_z=1.645)


def test_reorder_point_negative_demand_raises():
    with pytest.raises(ValueError):
        reorder_point(avg_daily_demand=-5, lead_time_days=7, safety_stock_units=10)


def test_annual_holding_cost_negative_inventory_raises():
    with pytest.raises(ValueError):
        annual_holding_cost(avg_inventory_units=-1, costs=_costs())


def test_annual_ordering_cost_negative_orders_raises():
    with pytest.raises(ValueError):
        annual_ordering_cost(orders_per_year=-1, costs=_costs())


def test_expected_stockout_cost_negative_units_raises():
    with pytest.raises(ValueError):
        expected_stockout_cost(expected_stockout_units=-1, costs=_costs())


def test_total_inventory_cost_is_illustrative_and_sums_correctly():
    result = total_inventory_cost(avg_inventory_units=100, orders_per_year=12, expected_stockout_units=5, costs=_costs())
    assert result["status"] == "ILLUSTRATIVE"
    assert result["total_cost"] == pytest.approx(result["holding_cost"] + result["ordering_cost"] + result["stockout_cost"])
