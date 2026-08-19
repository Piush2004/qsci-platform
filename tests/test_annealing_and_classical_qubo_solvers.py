import numpy as np
import pytest

from qsci_core.optimization.quantum.annealing_solver import BACKEND_LABEL, solve_qubo_with_annealing
from qsci_core.optimization.quantum.classical_qubo_solver import solve_qubo_with_ortools
from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo

DEPOT = np.array([50.0, 50.0])
COORDS = np.array([[10, 10], [15, 15], [90, 90], [85, 85]], dtype=float)
DEMANDS = np.array([30, 30, 30, 30], dtype=float)
CAPACITY = 70

KNOWN_OPTIMAL_COST = 226.27416997969522  # verified against dimod.ExactSolver + manual brute force


def _tiny_qubo():
    return build_cvrp_qubo(COORDS, DEMANDS, CAPACITY, n_vehicles=2, penalty_multiplier=2.0)


def test_annealing_label_is_honest_not_hardware():
    assert "SIMULATED ANNEALING" in BACKEND_LABEL
    assert "hardware" not in BACKEND_LABEL.lower()


def test_annealing_finds_known_optimum_on_tiny_instance():
    qi = _tiny_qubo()
    result = solve_qubo_with_annealing(qi, num_reads=100, seed=42)
    decoded = decode_qubo_sample(result.sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert decoded.feasible
    assert decoded.total_cost == pytest.approx(KNOWN_OPTIMAL_COST, abs=1e-6)


def test_annealing_seeded_reproducibility():
    qi = _tiny_qubo()
    r1 = solve_qubo_with_annealing(qi, num_reads=50, seed=123)
    r2 = solve_qubo_with_annealing(qi, num_reads=50, seed=123)
    assert r1.sample == r2.sample
    assert r1.energy == pytest.approx(r2.energy)


def test_annealing_records_seed_and_num_reads():
    qi = _tiny_qubo()
    result = solve_qubo_with_annealing(qi, num_reads=17, seed=7)
    assert result.num_reads == 17
    assert result.seed == 7


def test_ortools_qubo_solver_finds_known_optimum_on_tiny_instance():
    qi = _tiny_qubo()
    result = solve_qubo_with_ortools(qi, time_limit_seconds=10)
    assert result.status in ("OPTIMAL", "FEASIBLE")
    decoded = decode_qubo_sample(result.sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert decoded.feasible
    assert decoded.total_cost == pytest.approx(KNOWN_OPTIMAL_COST, abs=1e-6)


def test_ortools_qubo_solver_records_solve_time():
    qi = _tiny_qubo()
    result = solve_qubo_with_ortools(qi, time_limit_seconds=5)
    assert result.solve_time_seconds > 0
    assert result.solve_time_seconds < 10  # should not exceed the time limit by much
