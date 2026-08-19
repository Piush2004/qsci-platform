import numpy as np
import pytest

from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.noise_models import PRESETS, build_noise_model
from qsci_core.optimization.quantum.qaoa_solver import solve_qubo_with_qaoa
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo

DEPOT = np.array([50.0, 50.0])
COORDS = np.array([[10, 10], [15, 15], [90, 90], [85, 85]], dtype=float)
DEMANDS = np.array([30, 30, 30, 30], dtype=float)
CAPACITY = 70
KNOWN_OPTIMAL_COST = 226.27416997969522


def _tiny_qubo():
    return build_cvrp_qubo(COORDS, DEMANDS, CAPACITY, n_vehicles=2, penalty_multiplier=2.0)


def test_build_noise_model_noiseless_returns_none():
    assert build_noise_model("noiseless") is None


@pytest.mark.parametrize("preset", ["depolarizing_low", "depolarizing_high", "readout"])
def test_build_noise_model_returns_real_noise_model(preset):
    nm = build_noise_model(preset)
    assert nm is not None
    assert len(nm.noise_qubits) > 0 or nm.to_dict()["errors"]


def test_build_noise_model_unknown_preset_raises():
    with pytest.raises(ValueError):
        build_noise_model("not_a_real_preset")


def test_all_presets_are_documented():
    assert set(PRESETS) == {"noiseless", "depolarizing_low", "depolarizing_high", "readout"}


@pytest.mark.slow
def test_qaoa_noiseless_default_unchanged():
    """Default noise_preset='noiseless' must exercise the pre-Phase-4 code
    path identically (no noise_preset kwarg at all) -- verifies the Phase 4
    extension didn't change Phase 3's already-audited noiseless behavior.

    Does NOT assert bitstring-identical samples: COBYLA + statevector
    sampling is documented non-deterministic even at a fixed seed (Phase
    2.1's VQR finding -- "0/5 bit-identical" runs -- applies to this QAOA
    path too; confirmed empirically here, not assumed). The real invariant
    both calls must share is the decoded solution quality and the code
    path taken (simulator label), not the raw bitstring."""
    qi = _tiny_qubo()
    result = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=20, shots=1024, seed=42)
    result_explicit = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=20, shots=1024, seed=42, noise_preset="noiseless")

    assert result.metadata.simulator == result_explicit.metadata.simulator
    assert "StatevectorSampler" in result.metadata.simulator

    decoded = decode_qubo_sample(result.sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    decoded_explicit = decode_qubo_sample(result_explicit.sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert decoded.feasible and decoded_explicit.feasible
    assert decoded.total_cost == pytest.approx(decoded_explicit.total_cost)
    assert decoded.total_cost == pytest.approx(KNOWN_OPTIMAL_COST, abs=1e-6)
    assert "StatevectorSampler" in result_explicit.metadata.simulator


@pytest.mark.slow
def test_qaoa_with_depolarizing_noise_runs_and_labels_honestly():
    qi = _tiny_qubo()
    result = solve_qubo_with_qaoa(qi, p=1, optimizer_maxiter=20, shots=1024, seed=0, noise_preset="depolarizing_low")
    decoded = decode_qubo_sample(result.sample, 4, 2, COORDS, DEMANDS, CAPACITY, DEPOT)
    assert "Aer" in result.metadata.simulator
    assert "depolarizing_low" in result.metadata.simulator
    assert "hardware" not in result.metadata.simulator.lower()
    # feasibility is not asserted here -- noise may or may not degrade the
    # result; this test only checks the pipeline runs and labels correctly.
    assert decoded.feasibility_reason  # decoder ran and produced a real verdict
