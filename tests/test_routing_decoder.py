import numpy as np
import pytest

from qsci_core.optimization.quantum.decoder import decode_qubo_sample

DEPOT = np.array([50.0, 50.0])
COORDS = np.array([[10, 10], [15, 15], [90, 90], [85, 85]], dtype=float)
DEMANDS = np.array([30, 30, 30, 30], dtype=float)
CAPACITY = 70


def _sample(assignments):
    """assignments: dict customer_idx -> vehicle_idx (single assignment each)."""
    s = {}
    for i in range(4):
        for k in range(2):
            s[f"x_{i}_{k}"] = 1 if assignments.get(i) == k else 0
    return s


def test_valid_solution_is_feasible():
    sample = _sample({0: 1, 1: 1, 2: 0, 3: 0})
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert d.feasible
    assert d.total_cost is not None
    assert set(d.routes[0]) == {2, 3}
    assert set(d.routes[1]) == {0, 1}


def test_all_customers_visited_check():
    # customer 2 never assigned to any vehicle
    sample = _sample({0: 1, 1: 1, 3: 0})
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert not d.feasible
    assert "never assigned" in d.feasibility_reason
    assert "[2]" in d.feasibility_reason


def test_no_duplicate_visits_check():
    sample = _sample({0: 1, 1: 1, 2: 0, 3: 0})
    sample["x_0_0"] = 1  # customer 0 now assigned to BOTH vehicle 0 and vehicle 1
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert not d.feasible
    assert "multiple vehicles" in d.feasibility_reason


def test_capacity_respected_check():
    # overload vehicle 0 with all four 30-demand customers (120 > 70)
    sample = _sample({0: 0, 1: 0, 2: 0, 3: 0})
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert not d.feasible
    assert "capacity exceeded" in d.feasibility_reason
    assert d.vehicle_loads[0] == 120.0


def test_route_continuity_cost_includes_depot_legs():
    sample = _sample({0: 0, 1: 0, 2: 1, 3: 1})
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    # single-customer-equivalent sanity: cost must be strictly positive (depot legs included)
    assert d.route_costs[0] > 0
    assert d.route_costs[1] > 0


def test_cost_calculation_matches_manual_computation():
    sample = _sample({0: 1, 1: 1, 2: 0, 3: 0})
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    # manual: depot->2->3->depot and depot->0->1->depot (or reverse orders, same cost by symmetry here)
    depot_dist = np.sqrt(((COORDS - DEPOT) ** 2).sum(axis=1))
    dist = np.sqrt(((COORDS[:, None, :] - COORDS[None, :, :]) ** 2).sum(axis=-1))
    manual_v0 = depot_dist[2] + dist[2, 3] + depot_dist[3]
    manual_v1 = depot_dist[0] + dist[0, 1] + depot_dist[1]
    assert d.route_costs[0] == pytest.approx(manual_v0)
    assert d.route_costs[1] == pytest.approx(manual_v1)
    assert d.total_cost == pytest.approx(manual_v0 + manual_v1)


def test_malformed_input_missing_variables_treated_as_unassigned():
    d = decode_qubo_sample({}, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert not d.feasible
    assert "never assigned" in d.feasibility_reason


def test_empty_instance_raises_via_zero_customers():
    d = decode_qubo_sample({}, 0, 2, np.empty((0, 2)), np.empty(0), CAPACITY, DEPOT)
    assert d.feasible  # vacuously feasible: no customers to visit
    assert d.total_cost == 0.0


# --- Adversarial cases from CLAUDE.md Phase 3 spec §29 ---

def test_adversarial_all_zero_bitstring_is_infeasible():
    sample = {f"x_{i}_{k}": 0 for i in range(4) for k in range(2)}
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert not d.feasible
    assert "never assigned" in d.feasibility_reason


def test_adversarial_multiple_assignments_bitstring_is_infeasible():
    sample = {f"x_{i}_{k}": 1 for i in range(4) for k in range(2)}  # every customer assigned to every vehicle
    d = decode_qubo_sample(sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert not d.feasible
    assert "multiple vehicles" in d.feasibility_reason


def test_adversarial_single_customer_instance():
    coords = np.array([[10.0, 10.0]])
    demands = np.array([5.0])
    sample = {"x_0_0": 1}
    d = decode_qubo_sample(sample, 1, 1, coords, demands, 10, DEPOT)
    assert d.feasible
    assert d.routes[0] == [0]
    depot_dist = float(np.sqrt(((coords[0] - DEPOT) ** 2).sum()))
    assert d.total_cost == pytest.approx(2 * depot_dist)


def test_adversarial_more_vehicles_than_customers():
    # 4 customers, 4 vehicles (one each) -- extra vehicle capacity is fine, unused slots simply get empty routes
    n_vehicles = 4
    sample = {f"x_{i}_{k}": 1 if k == i else 0 for i in range(4) for k in range(n_vehicles)}
    d = decode_qubo_sample(sample, 4, n_vehicles, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert d.feasible
    assert len(d.routes) == n_vehicles
    assert all(len(d.routes[k]) == 1 for k in range(4))


def test_adversarial_zero_demand_customer_is_valid():
    coords = np.array([[10.0, 10.0], [20.0, 20.0]])
    demands = np.array([0.0, 0.0])
    sample = {"x_0_0": 1, "x_1_0": 1}
    d = decode_qubo_sample(sample, 2, 1, coords, demands, 10, DEPOT)
    assert d.feasible
    assert d.vehicle_loads[0] == 0.0


def test_adversarial_cluster_too_large_for_exact_decode_reported_not_approximated():
    n = 10
    coords = np.random.default_rng(0).uniform(0, 100, (n, 2))
    demands = np.ones(n)
    sample = {f"x_{i}_0": 1 for i in range(n)}
    d = decode_qubo_sample(sample, n, 1, coords, demands, 1000, DEPOT, max_exact_cluster_size=8)
    assert not d.feasible
    assert "intractable" in d.feasibility_reason
