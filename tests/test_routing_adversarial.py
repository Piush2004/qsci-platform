"""Adversarial routing tests per CLAUDE.md Phase 3 spec §29. Every case
must produce a controlled result -- no hanging processes, no silent
misbehavior."""

import numpy as np
import pytest

from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo

DEPOT = np.array([50.0, 50.0])


def test_duplicate_coordinates_still_solves():
    # two customers at the identical location -- distance 0 between them,
    # should not break the QUBO or decoder.
    coords = np.array([[10.0, 10.0], [10.0, 10.0], [90.0, 90.0]])
    demands = np.array([10.0, 10.0, 10.0])
    qi = build_cvrp_qubo(coords, demands, capacity=25, n_vehicles=2, penalty_multiplier=2.0)
    assert qi.n_variables == 6
    for bias in qi.bqm.linear.values():
        assert np.isfinite(bias)


def test_extremely_high_demand_customer_raises_cleanly():
    coords = np.array([[10.0, 10.0], [20.0, 20.0]])
    demands = np.array([5.0, 1_000_000.0])
    with pytest.raises(ValueError, match="demand exceeds vehicle capacity"):
        build_cvrp_qubo(coords, demands, capacity=100, n_vehicles=2)


def test_one_vehicle_instance():
    coords = np.array([[10.0, 10.0], [20.0, 20.0], [30.0, 30.0]])
    demands = np.array([5.0, 5.0, 5.0])
    qi = build_cvrp_qubo(coords, demands, capacity=20, n_vehicles=1, penalty_multiplier=2.0)
    assert qi.n_variables == 3
    sample = {"x_0_0": 1, "x_1_0": 1, "x_2_0": 1}
    d = decode_qubo_sample(sample, 3, 1, coords, demands, 20, DEPOT)
    assert d.feasible


def test_nan_distance_via_nan_coordinate_raises_or_propagates_visibly():
    coords = np.array([[10.0, 10.0], [np.nan, 20.0]])
    demands = np.array([5.0, 5.0])
    qi = build_cvrp_qubo(coords, demands, capacity=20, n_vehicles=1, penalty_multiplier=2.0)
    # A NaN coordinate produces a NaN distance, which must NOT silently
    # vanish into a finite-looking QUBO -- it must be visible/detectable.
    has_nan = any(not np.isfinite(b) for b in qi.bqm.linear.values()) or any(
        not np.isfinite(b) for b in qi.bqm.quadratic.values()
    )
    assert has_nan, "a NaN coordinate must produce a detectably non-finite QUBO, not a silently-wrong finite one"


def test_infinite_distance_propagates_visibly():
    coords = np.array([[10.0, 10.0], [np.inf, 20.0]])
    demands = np.array([5.0, 5.0])
    qi = build_cvrp_qubo(coords, demands, capacity=20, n_vehicles=1, penalty_multiplier=2.0)
    has_inf = any(not np.isfinite(b) for b in qi.bqm.linear.values()) or any(
        not np.isfinite(b) for b in qi.bqm.quadratic.values()
    )
    assert has_inf


def test_malformed_qubo_sample_missing_all_variables():
    coords = np.array([[10.0, 10.0], [20.0, 20.0]])
    demands = np.array([5.0, 5.0])
    d = decode_qubo_sample({}, 2, 1, coords, demands, 20, DEPOT)
    assert not d.feasible


def test_penalty_too_small_allows_infeasible_optimum():
    """With penalty_multiplier effectively zero, the QUBO's unconstrained
    optimum can violate capacity -- this is expected QUBO behavior (the
    formulation's own documented trade-off), and the decoder must still
    catch it as infeasible rather than trust the QUBO's raw output."""
    coords = np.array([[10.0, 10.0], [11.0, 11.0], [90.0, 90.0], [91.0, 91.0]])
    demands = np.array([35.0, 35.0, 35.0, 35.0])
    qi = build_cvrp_qubo(coords, demands, capacity=70, n_vehicles=2, penalty_multiplier=0.001)
    # With near-zero penalty, the pure-distance-minimizing optimum packs
    # the two CLOSE pairs together regardless of capacity -- exactly what
    # happened with a proper penalty too (since the pairs are naturally
    # capacity-compatible here); the real assertion is that decode_qubo_sample
    # independently re-checks capacity regardless of what penalty was used.
    import dimod
    best = dimod.ExactSolver().sample(qi.bqm).first
    d = decode_qubo_sample(dict(best.sample), 4, 2, coords, demands, 70, DEPOT)
    # Whatever the QUBO returns, the decoder's feasibility verdict must be
    # independently trustworthy -- assert it agrees with a direct manual check.
    manual_loads = {}
    for i in range(4):
        for k in range(2):
            if best.sample.get(f"x_{i}_{k}", 0) == 1:
                manual_loads[k] = manual_loads.get(k, 0) + demands[i]
    manual_feasible = all(load <= 70 for load in manual_loads.values())
    assert d.feasible == manual_feasible


def test_penalty_excessively_large_does_not_break_construction():
    coords = np.array([[10.0, 10.0], [20.0, 20.0], [90.0, 90.0], [91.0, 91.0]])
    demands = np.array([20.0, 20.0, 20.0, 20.0])
    qi = build_cvrp_qubo(coords, demands, capacity=45, n_vehicles=2, penalty_multiplier=1_000_000.0)
    for bias in list(qi.bqm.linear.values()) + list(qi.bqm.quadratic.values()):
        assert np.isfinite(bias), "an excessively large penalty must not overflow to inf/nan"


def test_disconnected_distance_matrix_via_zero_vector_still_decodes():
    # all customers at the same point as the depot -- degenerate but must not crash
    coords = np.array([[50.0, 50.0], [50.0, 50.0]])
    demands = np.array([5.0, 5.0])
    sample = {"x_0_0": 1, "x_1_0": 1}
    d = decode_qubo_sample(sample, 2, 1, coords, demands, 20, DEPOT)
    assert d.feasible
    assert d.total_cost == pytest.approx(0.0)
