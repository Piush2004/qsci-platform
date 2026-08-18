"""Variational Quantum Regressor (VQR) forecaster — Qiskit Machine Learning,
Aer statevector simulation.

Architecture (per CLAUDE.md §6): classical features -> feature reduction
(qsci_core.forecasting.quantum.feature_reduction) -> quantum encoding
(ZZFeatureMap/PauliFeatureMap) -> parameterized ansatz -> EstimatorQNN
(wrapped by qiskit_machine_learning's VQR) -> forecast.

Installed-API note (qiskit 2.5.2 / qiskit-machine-learning 0.9.0): the
class-based `ZZFeatureMap`/`RealAmplitudes` from `qiskit.circuit.library`
are deprecated in favor of the function-based `zz_feature_map`/
`real_amplitudes`, and Aer's `EstimatorV2` requires circuits pre-transpiled
to its basis gates (raises `AerError: unknown instruction` on raw
blueprint-circuit output otherwise) — VQR's `pass_manager` argument handles
this. Both were verified against the actually-installed versions before
writing this module, per CLAUDE.md's "no silent API replacement" rule.

Known limitation (diagnosed, not fixed): qiskit-aer 0.17.2's `EstimatorV2`,
when executing multiple pubs in one batched job (which is what
`EstimatorQNN.forward` does over a training/prediction set), returns
run-to-run varying expectation values -- even with every documented RNG
seeded (`algorithm_globals.random_seed`, `AerSimulator(seed_simulator=...)`,
`seed_transpiler`) and `default_precision=0.0` (nominally exact statevector,
no shot sampling). This was isolated to the batched forward pass itself:
repeated `.predict()` calls on the SAME already-fitted model (no
optimizer/training involved) still differ, while single-pub raw
`estimator.run()` calls and COBYLA itself were separately verified fully
deterministic. See `tests/test_quantum_vqr_forecaster.py` (xfail with the
same diagnosis) and `docs/PHASE_2_REPORT.md` Known Issues. Practical
consequence: exact numeric results in the Phase 2 experiment matrix should
be read as one representative run, not a bit-exact reproducible value.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from qiskit.circuit.library import pauli_feature_map, real_amplitudes, zz_feature_map
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import EstimatorV2
from qiskit_machine_learning.algorithms import VQR
from qiskit_machine_learning.optimizers import COBYLA, SPSA
from qiskit_machine_learning.utils import algorithm_globals
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from sklearn.preprocessing import MinMaxScaler

VALID_FEATURE_MAPS = ("zz", "pauli")
VALID_OPTIMIZERS = ("cobyla", "spsa")


@dataclass
class CircuitMetadata:
    n_qubits: int
    feature_map_type: str
    ansatz_type: str
    optimizer_type: str
    optimizer_maxiter: int
    circuit_depth: int
    gate_count: int
    num_parameters: int
    shots: str  # "N/A (exact statevector expectation)" for the noiseless config used in Phase 2
    simulator: str
    train_time_seconds: float | None = None
    predict_time_seconds: float | None = None
    optimizer_n_function_evals: int | None = None
    optimizer_n_iterations: int | None = None
    final_objective_value: float | None = None


class QuantumVQRForecaster:
    """Fits a VQR to (already dimensionality-reduced) features. Feature and
    target scaling are handled internally, fit on the training data only —
    the caller is responsible for leakage-safe feature reduction upstream
    (see feature_reduction.py); this class only owns encoding-range scaling.
    """

    def __init__(
        self,
        n_qubits: int,
        feature_map_type: str = "zz",
        feature_map_reps: int = 1,
        ansatz_reps: int = 1,
        optimizer_type: str = "cobyla",
        optimizer_maxiter: int = 50,
        seed: int = 42,
    ):
        if feature_map_type not in VALID_FEATURE_MAPS:
            raise ValueError(f"feature_map_type must be one of {VALID_FEATURE_MAPS}, got {feature_map_type!r}")
        if optimizer_type not in VALID_OPTIMIZERS:
            raise ValueError(f"optimizer_type must be one of {VALID_OPTIMIZERS}, got {optimizer_type!r}")
        if n_qubits < 1:
            raise ValueError(f"n_qubits must be positive, got {n_qubits}")

        self.n_qubits = n_qubits
        self.feature_map_type = feature_map_type
        self.feature_map_reps = feature_map_reps
        self.ansatz_reps = ansatz_reps
        self.optimizer_type = optimizer_type
        self.optimizer_maxiter = optimizer_maxiter
        self.seed = seed

        self._x_scaler = MinMaxScaler(feature_range=(0, np.pi))
        self._y_scaler = MinMaxScaler(feature_range=(-1, 1))
        self._vqr: VQR | None = None
        self.metadata: CircuitMetadata | None = None

    def _build_circuits(self):
        if self.feature_map_type == "zz":
            feature_map = zz_feature_map(feature_dimension=self.n_qubits, reps=self.feature_map_reps)
        else:
            feature_map = pauli_feature_map(feature_dimension=self.n_qubits, reps=self.feature_map_reps)
        ansatz = real_amplitudes(num_qubits=self.n_qubits, reps=self.ansatz_reps)
        return feature_map, ansatz

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "QuantumVQRForecaster":
        X_train = np.asarray(X_train, dtype=float)
        y_train = np.asarray(y_train, dtype=float)

        if X_train.size == 0 or y_train.size == 0:
            raise ValueError("X_train/y_train must not be empty")
        if np.isnan(X_train).any() or np.isnan(y_train).any():
            raise ValueError("X_train/y_train contain NaN values")
        if X_train.shape[1] != self.n_qubits:
            raise ValueError(f"X_train has {X_train.shape[1]} features but forecaster is configured for {self.n_qubits} qubits")
        if len(X_train) != len(y_train):
            raise ValueError(f"X_train has {len(X_train)} rows but y_train has {len(y_train)}")

        X_scaled = self._x_scaler.fit_transform(X_train)
        y_scaled = self._y_scaler.fit_transform(y_train.reshape(-1, 1)).ravel()

        # VQR draws its random initial point from this global RNG (not from
        # AerSimulator's seed_simulator, which only controls shot sampling) --
        # without setting it, two runs with the same `self.seed` would still
        # start from different random points and diverge.
        algorithm_globals.random_seed = self.seed

        feature_map, ansatz = self._build_circuits()
        backend = AerSimulator(method="statevector", seed_simulator=self.seed)
        pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
        estimator = EstimatorV2()  # default_precision=0.0 -> exact statevector expectation, no shot noise

        optimizer = COBYLA(maxiter=self.optimizer_maxiter) if self.optimizer_type == "cobyla" else SPSA(maxiter=self.optimizer_maxiter)

        combined = feature_map.compose(ansatz)
        transpiled = pass_manager.run(combined)

        t0 = time.perf_counter()
        self._vqr = VQR(feature_map=feature_map, ansatz=ansatz, optimizer=optimizer, estimator=estimator, pass_manager=pass_manager)
        self._vqr.fit(X_scaled, y_scaled)
        train_time = time.perf_counter() - t0

        fit_result = self._vqr.fit_result
        self.metadata = CircuitMetadata(
            n_qubits=self.n_qubits,
            feature_map_type=self.feature_map_type,
            ansatz_type="real_amplitudes",
            optimizer_type=self.optimizer_type,
            optimizer_maxiter=self.optimizer_maxiter,
            circuit_depth=transpiled.depth(),
            gate_count=sum(transpiled.count_ops().values()),
            num_parameters=ansatz.num_parameters,
            shots="N/A (exact statevector expectation, default_precision=0.0)",
            simulator="qiskit_aer.AerSimulator(method=statevector)",
            train_time_seconds=train_time,
            optimizer_n_function_evals=int(fit_result.nfev) if hasattr(fit_result, "nfev") and fit_result.nfev is not None else None,
            optimizer_n_iterations=int(fit_result.nit) if hasattr(fit_result, "nit") and fit_result.nit is not None else None,
            final_objective_value=float(fit_result.fun) if hasattr(fit_result, "fun") else None,
        )
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._vqr is None:
            raise RuntimeError("forecaster not fit yet")
        X = np.asarray(X, dtype=float)
        if X.size == 0:
            raise ValueError("X must not be empty")
        if np.isnan(X).any():
            raise ValueError("X contains NaN values")
        if X.shape[1] != self.n_qubits:
            raise ValueError(f"X has {X.shape[1]} features but forecaster is configured for {self.n_qubits} qubits")

        X_scaled = self._x_scaler.transform(X)
        t0 = time.perf_counter()
        preds_scaled = self._vqr.predict(X_scaled)
        predict_time = time.perf_counter() - t0
        if self.metadata is not None:
            self.metadata.predict_time_seconds = predict_time

        preds = self._y_scaler.inverse_transform(np.asarray(preds_scaled).reshape(-1, 1)).ravel()
        return preds
