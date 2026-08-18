import numpy as np
import pytest

from qsci_core.optimization.classical.or_tools_vrp import solve_cvrp


def _square_instance():
    coords = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [2, 0], [2, 1]], dtype=float)
    demands = np.array([0, 5, 5, 5, 5, 5], dtype=float)
    return coords, demands


def test_solve_cvrp_empty_instance_raises():
    with pytest.raises(ValueError):
        solve_cvrp(np.empty((0, 2)), np.array([]), capacity=10, n_vehicles=1)


def test_solve_cvrp_negative_demand_raises():
    coords, demands = _square_instance()
    demands[1] = -5
    with pytest.raises(ValueError):
        solve_cvrp(coords, demands, capacity=10, n_vehicles=2)


def test_solve_cvrp_demand_exceeds_capacity_raises():
    coords, demands = _square_instance()
    with pytest.raises(ValueError):
        solve_cvrp(coords, demands, capacity=3, n_vehicles=2)  # every node demands 5 > capacity 3


def test_solve_cvrp_invalid_capacity_raises():
    coords, demands = _square_instance()
    with pytest.raises(ValueError):
        solve_cvrp(coords, demands, capacity=0, n_vehicles=2)


def test_solve_cvrp_invalid_vehicle_count_raises():
    coords, demands = _square_instance()
    with pytest.raises(ValueError):
        solve_cvrp(coords, demands, capacity=20, n_vehicles=0)


def test_solve_cvrp_depot_out_of_range_raises():
    coords, demands = _square_instance()
    with pytest.raises(ValueError):
        solve_cvrp(coords, demands, capacity=20, n_vehicles=2, depot=99)


def test_solve_cvrp_coords_demands_length_mismatch_raises():
    coords, demands = _square_instance()
    with pytest.raises(ValueError):
        solve_cvrp(coords[:-1], demands, capacity=20, n_vehicles=2)


def test_solve_cvrp_solves_small_feasible_instance():
    coords, demands = _square_instance()
    result = solve_cvrp(coords, demands, capacity=20, n_vehicles=2, time_limit_seconds=5)
    assert result.status == "OPTIMAL_OR_FEASIBLE"
    assert result.total_distance is not None
    all_visited = sorted(node for route in result.routes for node in route)
    assert all_visited == [1, 2, 3, 4, 5]  # every non-depot node visited exactly once


def test_solve_cvrp_accepts_precomputed_distance_matrix():
    coords, demands = _square_instance()
    n = len(demands)
    dist_matrix = np.ones((n, n)) - np.eye(n)  # trivial uniform distances
    result = solve_cvrp(coords, demands, capacity=20, n_vehicles=2, distance_matrix=dist_matrix, time_limit_seconds=5)
    assert result.status == "OPTIMAL_OR_FEASIBLE"
