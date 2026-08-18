import numpy as np
import pytest

from qsci_core.forecasting.quantum.vqr_forecaster import QuantumVQRForecaster

# VQR training is genuinely slow (real circuit simulation) -- these tests use
# the smallest qubit count and iteration budget that still exercises real
# behavior, per CLAUDE.md's "reduce experiment size, document it" allowance.
FAST_MAXITER = 5


def _tiny_data(n=12, n_features=4, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 1, (n, n_features))
    y = X.sum(axis=1) * 10
    return X, y


def test_invalid_feature_map_type_raises():
    with pytest.raises(ValueError):
        QuantumVQRForecaster(n_qubits=4, feature_map_type="not_a_real_map")


def test_invalid_optimizer_type_raises():
    with pytest.raises(ValueError):
        QuantumVQRForecaster(n_qubits=4, optimizer_type="not_a_real_optimizer")


def test_invalid_n_qubits_raises():
    with pytest.raises(ValueError):
        QuantumVQRForecaster(n_qubits=0)


def test_predict_before_fit_raises():
    model = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER)
    X, _ = _tiny_data()
    with pytest.raises(RuntimeError):
        model.predict(X)


def test_fit_empty_data_raises():
    model = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER)
    with pytest.raises(ValueError):
        model.fit(np.empty((0, 4)), np.empty(0))


def test_fit_nan_data_raises():
    model = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER)
    X, y = _tiny_data()
    X[0, 0] = np.nan
    with pytest.raises(ValueError):
        model.fit(X, y)


def test_fit_feature_dimension_mismatch_raises():
    model = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER)
    X, y = _tiny_data(n_features=6)  # model expects 4 qubits/features
    with pytest.raises(ValueError):
        model.fit(X, y)


def test_fit_length_mismatch_raises():
    model = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER)
    X, y = _tiny_data()
    with pytest.raises(ValueError):
        model.fit(X, y[:-1])


@pytest.fixture(scope="module")
def fitted_model():
    X, y = _tiny_data(n=12, n_features=4, seed=0)
    model = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER, seed=42).fit(X, y)
    return model, X, y


def test_predict_feature_dimension_mismatch_raises(fitted_model):
    model, X, y = fitted_model
    with pytest.raises(ValueError):
        model.predict(X[:, :2])


def test_predict_nan_raises(fitted_model):
    model, X, y = fitted_model
    X_bad = X.copy()
    X_bad[0, 0] = np.nan
    with pytest.raises(ValueError):
        model.predict(X_bad)


def test_predict_empty_raises(fitted_model):
    model, X, y = fitted_model
    with pytest.raises(ValueError):
        model.predict(np.empty((0, 4)))


def test_predict_output_shape_matches_input(fitted_model):
    model, X, y = fitted_model
    preds = model.predict(X)
    assert preds.shape == (len(X),)
    assert np.all(np.isfinite(preds))


def test_circuit_metadata_matches_configured_qubits(fitted_model):
    model, X, y = fitted_model
    meta = model.metadata
    assert meta.n_qubits == 4
    assert meta.circuit_depth > 0
    assert meta.gate_count > 0
    assert meta.num_parameters > 0
    assert meta.train_time_seconds > 0
    assert meta.shots.startswith("N/A")


def test_circuit_num_parameters_scales_with_qubits():
    # real_amplitudes(N, reps=1) has N*(reps+1) parameters -- verify this
    # matches what the forecaster actually builds, not an assumption.
    X4, y4 = _tiny_data(n=10, n_features=4, seed=1)
    X8, y8 = _tiny_data(n=10, n_features=8, seed=1)
    model4 = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER).fit(X4, y4)
    model8 = QuantumVQRForecaster(n_qubits=8, optimizer_maxiter=FAST_MAXITER).fit(X8, y8)
    assert model8.metadata.num_parameters > model4.metadata.num_parameters
    assert model8.metadata.n_qubits == 8


def test_reproducibility_circuit_structure_is_deterministic():
    # Circuit structure (depth/gate count/param count) depends only on the
    # configuration, not on execution -- this part IS fully reproducible.
    X, y = _tiny_data(n=10, n_features=4, seed=2)
    model_a = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER, seed=42).fit(X, y)
    model_b = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER, seed=42).fit(X, y)
    assert model_a.metadata.circuit_depth == model_b.metadata.circuit_depth
    assert model_a.metadata.gate_count == model_b.metadata.gate_count
    assert model_a.metadata.num_parameters == model_b.metadata.num_parameters


@pytest.mark.xfail(
    reason=(
        "Diagnosed, not a test bug: qiskit-aer 0.17.2's EstimatorV2 batched "
        "execution (multiple pubs in one job) returns run-to-run varying "
        "expectation values even with every documented RNG seeded "
        "(algorithm_globals.random_seed, AerSimulator seed_simulator, "
        "seed_transpiler) and default_precision=0.0 (nominally exact "
        "statevector, no shot sampling). Isolated down to repeated "
        ".predict() calls on the SAME already-fitted model (no training/"
        "optimizer/initial-point involvement at all) -- see docs/PHASE_2_REPORT.md "
        "Known Issues. COBYLA and raw single-pub Aer calls were separately "
        "verified deterministic; the instability is specific to EstimatorQNN's "
        "multi-pub batched forward pass on this Aer version."
    ),
    strict=True,
)
def test_reproducibility_predictions_same_seed_same_predictions():
    X, y = _tiny_data(n=10, n_features=4, seed=2)
    model_a = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER, seed=42).fit(X, y)
    model_b = QuantumVQRForecaster(n_qubits=4, optimizer_maxiter=FAST_MAXITER, seed=42).fit(X, y)
    preds_a = model_a.predict(X)
    preds_b = model_b.predict(X)
    np.testing.assert_allclose(preds_a, preds_b, rtol=1e-6)
