"""Inventory economics: EOQ, safety stock, reorder point, and cost
calculators.

The FORMULAS below are standard, real operations-research math — computing
them from given inputs is LIVE. The $ COST INPUTS (holding cost/unit,
ordering cost/order, stockout cost/unit) are a different matter: no public
dataset gives QSCI real per-unit cost data for M5 or the Last-Mile items.
`CostAssumptions` exists specifically so those inputs are never silently
mistaken for real numbers — every function that consumes it is documented
as producing an ILLUSTRATIVE financial output, not a LIVE one.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CostAssumptions:
    """ILLUSTRATIVE cost inputs — documented assumptions standing in for
    real per-unit cost data that doesn't exist in any public dataset QSCI
    uses. Never treat values computed from this as LIVE."""
    holding_cost_per_unit_per_year: float
    ordering_cost_per_order: float
    stockout_cost_per_unit: float
    status: str = "ILLUSTRATIVE"

    def __post_init__(self):
        for name in ("holding_cost_per_unit_per_year", "ordering_cost_per_order", "stockout_cost_per_unit"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative, got {getattr(self, name)}")


def economic_order_quantity(annual_demand: float, costs: CostAssumptions) -> float:
    """EOQ = sqrt(2 * D * S / H). Requires positive annual demand and
    holding cost — division by zero is a real error, not silently 0."""
    if annual_demand <= 0:
        raise ValueError(f"annual_demand must be positive, got {annual_demand}")
    if costs.holding_cost_per_unit_per_year <= 0:
        raise ValueError("holding_cost_per_unit_per_year must be positive for EOQ to be defined")
    return math.sqrt(2 * annual_demand * costs.ordering_cost_per_order / costs.holding_cost_per_unit_per_year)


def safety_stock(demand_std: float, lead_time_days: float, service_z: float) -> float:
    """Safety stock = z * sigma_demand * sqrt(lead_time).
    `service_z` is the standard-normal z-score for the target service level
    (e.g. 1.645 for 95%, 2.33 for 99%) — pass it explicitly, don't hardcode
    a service level inside this function.
    """
    if demand_std < 0:
        raise ValueError(f"demand_std must be non-negative, got {demand_std}")
    if lead_time_days < 0:
        raise ValueError(f"lead_time_days must be non-negative, got {lead_time_days}")
    return service_z * demand_std * math.sqrt(lead_time_days)


def reorder_point(avg_daily_demand: float, lead_time_days: float, safety_stock_units: float) -> float:
    if avg_daily_demand < 0:
        raise ValueError(f"avg_daily_demand must be non-negative, got {avg_daily_demand}")
    if safety_stock_units < 0:
        raise ValueError(f"safety_stock_units must be non-negative, got {safety_stock_units}")
    return avg_daily_demand * lead_time_days + safety_stock_units


def annual_holding_cost(avg_inventory_units: float, costs: CostAssumptions) -> float:
    if avg_inventory_units < 0:
        raise ValueError(f"avg_inventory_units must be non-negative, got {avg_inventory_units}")
    return avg_inventory_units * costs.holding_cost_per_unit_per_year


def annual_ordering_cost(orders_per_year: float, costs: CostAssumptions) -> float:
    if orders_per_year < 0:
        raise ValueError(f"orders_per_year must be non-negative, got {orders_per_year}")
    return orders_per_year * costs.ordering_cost_per_order


def expected_stockout_cost(expected_stockout_units: float, costs: CostAssumptions) -> float:
    if expected_stockout_units < 0:
        raise ValueError(f"expected_stockout_units must be non-negative, got {expected_stockout_units}")
    return expected_stockout_units * costs.stockout_cost_per_unit


def total_inventory_cost(avg_inventory_units: float, orders_per_year: float, expected_stockout_units: float, costs: CostAssumptions) -> dict:
    """Bundle the three cost components. Result is ILLUSTRATIVE end to end —
    inherited from `costs`."""
    holding = annual_holding_cost(avg_inventory_units, costs)
    ordering = annual_ordering_cost(orders_per_year, costs)
    stockout = expected_stockout_cost(expected_stockout_units, costs)
    return {
        "holding_cost": holding,
        "ordering_cost": ordering,
        "stockout_cost": stockout,
        "total_cost": holding + ordering + stockout,
        "status": "ILLUSTRATIVE",
    }
