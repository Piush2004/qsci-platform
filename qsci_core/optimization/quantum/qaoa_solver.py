"""Gate-model QAOA solver for the CVRP QUBO.

Pipeline: QUBO (qubo_formulator.py) -> QuadraticProgram -> Ising Hamiltonian
(handled internally by qiskit_optimization's MinimumEigenOptimizer) -> QAOA
-> StatevectorSampler -> bitstring -> qsci_core's own decoder
(decode_qubo_sample) for route decoding + independent feasibility
validation.

Installed-API note: `qiskit_algorithms` (providing the `QAOA` class) is not
part of core `qiskit` 2.5.2 -- it was a separate package
(`qiskit-algorithms==0.4.0`) not in the original Phase 0 dependency list,
installed for Phase 3 (same pattern as `ortools` in Phase 1 and
`qiskit-machine-learning`'s function-based feature maps in Phase 2).
Verified against the actually-installed version before writing this
module.

Unlike Phase 2's `EstimatorQNN`-based VQR (which suffered catastrophic
runtime from an unconditionally-constructed analytic gradient, diagnosed
in Phase 2.1), this QAOA path uses a `StatevectorSampler` (samples
bitstrings, not expectation-value gradients) and was empirically verified
NOT to reproduce that pathology -- see docs/PHASE_3_REPORT.md's QAOA
timing section for the actual measured scaling.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from qiskit.primitives import StatevectorSampler
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.converters import QuadraticProgramToQubo

from qsci_core.optimization.quantum.qubo_formulator import QUBOInstance


@dataclass
class QAOAResourceMetadata:
    n_qubits: int
    qaoa_depth_p: int
    circuit_depth: int
    gate_count_1q: int
    gate_count_2q: int
    gate_count_total: int
    optimizer_type: str
    optimizer_maxiter: int
    optimizer_n_function_evals: int | None
    shots: int | None
    simulator: str


@dataclass
class QAOAResult:
    sample: dict
    energy: float
    metadata: QAOAResourceMetadata
    solve_time_seconds: float


def _bqm_to_quadratic_program(qi: QUBOInstance) -> QuadraticProgram:
    qp = QuadraticProgram()
    for v in qi.bqm.variables:
        qp.binary_var(name=v)
    linear = {v: float(b) for v, b in qi.bqm.linear.items()}
    quadratic = {(u, v): float(b) for (u, v), b in qi.bqm.quadratic.items()}
    qp.minimize(linear=linear, quadratic=quadratic, constant=float(qi.bqm.offset))
    return qp


def solve_qubo_with_qaoa(
    qi: QUBOInstance,
    p: int = 1,
    optimizer_maxiter: int = 20,
    shots: int = 1024,
    seed: int = 42,
) -> QAOAResult:
    if p < 1:
        raise ValueError(f"p (QAOA depth) must be >= 1, got {p}")
    if optimizer_maxiter < 1:
        raise ValueError(f"optimizer_maxiter must be >= 1, got {optimizer_maxiter}")

    qp = _bqm_to_quadratic_program(qi)

    # Build the Ising Hamiltonian explicitly (documented pipeline step,
    # not hidden inside MinimumEigenOptimizer) so circuit metadata below
    # reflects the actual operator QAOA runs against.
    converter = QuadraticProgramToQubo()
    qubo_qp = converter.convert(qp)
    hamiltonian, _offset = qubo_qp.to_ising()

    sampler = StatevectorSampler(default_shots=shots, seed=seed)
    optimizer = COBYLA(maxiter=optimizer_maxiter)

    n_fevals = {"count": 0}

    def _callback(eval_count, params, mean, metadata):
        n_fevals["count"] = eval_count

    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=p, callback=_callback)

    t0 = time.perf_counter()
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    solve_time = time.perf_counter() - t0

    sample = {v.name: int(round(result.x[i])) for i, v in enumerate(qp.variables)}

    circuit = qaoa.ansatz.decompose(reps=3)
    ops = circuit.count_ops()
    gate_count_2q = sum(v for k, v in ops.items() if k in ("cx", "cz", "rzz", "ecr", "cp"))
    gate_count_total = sum(ops.values())

    metadata = QAOAResourceMetadata(
        n_qubits=circuit.num_qubits,
        qaoa_depth_p=p,
        circuit_depth=circuit.depth(),
        gate_count_1q=gate_count_total - gate_count_2q,
        gate_count_2q=gate_count_2q,
        gate_count_total=gate_count_total,
        optimizer_type="cobyla",
        optimizer_maxiter=optimizer_maxiter,
        optimizer_n_function_evals=n_fevals["count"] or None,
        shots=shots,
        simulator="qiskit.primitives.StatevectorSampler (noiseless, shot-sampled)",
    )

    return QAOAResult(sample=sample, energy=float(result.fval), metadata=metadata, solve_time_seconds=solve_time)
