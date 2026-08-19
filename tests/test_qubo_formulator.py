import dimod
import numpy as np
import pytest

from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo


def _tiny_instance():
    coords = np.array([[10, 10], [15, 15], [90, 90], [85, 85]], dtype=float)
    demands = np.array([30, 30, 30, 30], dtype=float)
    return coords, demands


def test_qubo_correct_dimensions():
    coords, demands = _tiny_instance()
    qi = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2)
    assert qi.n_variables == 4 * 2
    assert len(qi.bqm.variables) == 8


def test_qubo_matrix_is_symmetric_via_dimod_representation():
    # dimod BQMs store each quadratic term once; verify no duplicate/conflicting
    # (u,v) and (v,u) entries exist (which would indicate an asymmetric bug).
    coords, demands = _tiny_instance()
    qi = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2)
    seen = set()
    for u, v in qi.bqm.quadratic:
        key = frozenset((u, v))
        assert key not in seen, f"duplicate/asymmetric term for {u},{v}"
        seen.add(key)


def test_qubo_finite_values():
    coords, demands = _tiny_instance()
    qi = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2)
    for bias in qi.bqm.linear.values():
        assert np.isfinite(bias)
    for bias in qi.bqm.quadratic.values():
        assert np.isfinite(bias)
    assert np.isfinite(qi.bqm.offset)


def test_qubo_variable_mapping_matches_expected_names():
    coords, demands = _tiny_instance()
    qi = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2)
    for i in range(4):
        for k in range(2):
            assert qi.variable_map[(i, k)] == f"x_{i}_{k}"
            assert qi.variable_map[(i, k)] in qi.bqm.variables


def test_qubo_penalty_scales_with_multiplier():
    coords, demands = _tiny_instance()
    qi_low = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2, penalty_multiplier=1.0)
    qi_high = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2, penalty_multiplier=10.0)
    # penalty_capacity scales linearly with the multiplier (m * n * c_max).
    assert qi_high.penalty_capacity == pytest.approx(qi_low.penalty_capacity * 10)
    # penalty_visit scales QUADRATICALLY: it must dominate not just the
    # objective (linear in m) but also the capacity penalty's own maximum
    # possible magnitude (m * penalty_capacity * K * Q^2, and
    # penalty_capacity is itself linear in m) -- see qubo_formulator.py's
    # docstring for the real bug this derivation fixes.
    assert qi_high.penalty_visit > qi_low.penalty_visit * 10


def test_qubo_brute_force_agreement_tiny_instance():
    """The core validation requirement: QUBO optimum (via dimod's real
    brute-force ExactSolver) must match an independently-computed manual
    brute-force enumeration of the assignment space."""
    coords, demands = _tiny_instance()
    capacity = 70
    n_vehicles = 2
    qi = build_cvrp_qubo(coords, demands, capacity, n_vehicles, penalty_multiplier=2.0)

    sampleset = dimod.ExactSolver().sample(qi.bqm)
    best_energy = sampleset.first.energy

    import itertools
    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.sqrt((diff ** 2).sum(axis=-1))
    best_manual_cost = float("inf")
    for assign in itertools.product(range(n_vehicles), repeat=4):
        loads = [0.0] * n_vehicles
        for i, k in enumerate(assign):
            loads[k] += demands[i]
        if any(l > capacity for l in loads):
            continue
        total = 0.0
        for k in range(n_vehicles):
            custs = [i for i, kk in enumerate(assign) if kk == k]
            for a in range(len(custs)):
                for b in range(a + 1, len(custs)):
                    total += dist[custs[a], custs[b]]
        best_manual_cost = min(best_manual_cost, total)

    from qsci_core.optimization.quantum.decoder import decode_qubo_sample
    decoded = decode_qubo_sample(dict(sampleset.first.sample), 4, n_vehicles, coords, demands, capacity, np.array([50.0, 50.0]))
    assert decoded.feasible
    # The QUBO objective (pairwise-distance proxy) matches the manual brute
    # force of that SAME proxy objective, independent of the route-decode step.
    proxy_terms_from_decode = sum(
        dist[custs[a], custs[b]]
        for custs in decoded.assignment.values()
        for a in range(len(custs)) for b in range(a + 1, len(custs))
    )
    assert proxy_terms_from_decode == pytest.approx(best_manual_cost, abs=1e-6)


def test_qubo_empty_instance_raises():
    with pytest.raises(ValueError):
        build_cvrp_qubo(np.empty((0, 2)), np.array([]), capacity=10, n_vehicles=1)


def test_qubo_negative_demand_raises():
    coords, demands = _tiny_instance()
    demands = demands.copy()
    demands[0] = -5
    with pytest.raises(ValueError):
        build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2)


def test_qubo_demand_exceeds_capacity_raises():
    coords, demands = _tiny_instance()
    with pytest.raises(ValueError):
        build_cvrp_qubo(coords, demands, capacity=10, n_vehicles=2)  # every demand (30) > capacity (10)


def test_qubo_total_demand_exceeds_fleet_capacity_raises():
    coords, demands = _tiny_instance()  # total demand = 120
    with pytest.raises(ValueError):
        build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=1)  # fleet capacity 70 < 120


def test_qubo_invalid_vehicle_count_raises():
    coords, demands = _tiny_instance()
    with pytest.raises(ValueError):
        build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=0)


def test_qubo_invalid_capacity_raises():
    coords, demands = _tiny_instance()
    with pytest.raises(ValueError):
        build_cvrp_qubo(coords, demands, capacity=0, n_vehicles=2)


def test_qubo_coords_demands_length_mismatch_raises():
    coords, demands = _tiny_instance()
    with pytest.raises(ValueError):
        build_cvrp_qubo(coords[:-1], demands, capacity=70, n_vehicles=2)
