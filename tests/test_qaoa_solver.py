import numpy as np
import pytest

from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.qaoa_solver import solve_qubo_with_qaoa
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo

DEPOT = np.array([50.0, 50.0])
COORDS = np.array([[10, 10], [15, 15], [90, 90], [85, 85]], dtype=float)
DEMANDS = np.array([30, 30, 30, 30], dtype=float)
CAPACITY = 70
KNOWN_OPTIMAL_COST = 226.27416997969522


def _tiny_qubo():
    return build_cvrp_qubo(COORDS, DEMANDS, CAPACITY, n_vehicles=2, penalty_multiplier=2.0)


def test_invalid_p_raises():
    qi = _tiny_qubo()
    with pytest.raises(ValueError):
        solve_qubo_with_qaoa(qi, p=0)


def test_invalid_maxiter_raises():
    qi = _tiny_qubo()
    with pytest.raises(ValueError):
        solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=0)


@pytest.mark.slow
def test_qaoa_finds_known_optimum_on_tiny_instance():
    """The core validation requirement, mirroring the annealing/OR-Tools
    tests: QAOA's result, decoded, must match the independently-verified
    optimum (dimod.ExactSolver + manual brute force, tests/test_qubo_formulator.py)."""
    qi = _tiny_qubo()
    result = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=20, shots=1024, seed=42)
    decoded = decode_qubo_sample(result.sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert decoded.feasible
    assert decoded.total_cost == pytest.approx(KNOWN_OPTIMAL_COST, abs=1e-6)


@pytest.mark.slow
def test_qaoa_resource_metadata_is_real_not_estimated():
    qi = _tiny_qubo()
    result = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=10, shots=512, seed=42)
    meta = result.metadata
    assert meta.n_qubits == 8
    assert meta.qaoa_depth_p == 1
    assert meta.circuit_depth > 0
    assert meta.gate_count_total == meta.gate_count_1q + meta.gate_count_2q
    assert meta.gate_count_2q > 0  # QAOA's cost-Hamiltonian layer needs 2-qubit interactions
    assert meta.shots == 512
    assert "StatevectorSampler" in meta.simulator
    assert result.solve_time_seconds > 0


@pytest.mark.slow
def test_qaoa_circuit_depth_grows_with_p():
    qi = _tiny_qubo()
    r_p1 = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=5, shots=256, seed=42)
    r_p2 = solve_qubo_with_qaoa(qi, p=2, optimizer_maxiter=5, shots=256, seed=42)
    assert r_p2.metadata.circuit_depth > r_p1.metadata.circuit_depth
    assert r_p2.metadata.gate_count_total > r_p1.metadata.gate_count_total
