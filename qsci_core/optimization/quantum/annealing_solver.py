"""Simulated-annealing solver for the CVRP QUBO.

Backend: `dwave.samplers.SimulatedAnnealingSampler` (dwave-samplers 1.8.0,
part of dwave-ocean-sdk 9.4.0). The classic standalone `neal` package the
original architecture spec named does not exist in this environment's
installed packages -- its functionality was folded into `dwave.samplers`
in newer Ocean SDK releases. Verified against the actually-installed
package before writing this module, per CLAUDE.md's "no silent API
replacement" rule.

No D-Wave Leap cloud credentials are configured in this environment (no
`DWAVE_API_TOKEN`, no `~/.config/dwave` file -- checked directly, not
assumed). This module therefore ONLY runs classical simulated annealing.
Every result from this module is labeled "SIMULATED ANNEALING" -- never
"quantum hardware" or "quantum annealing hardware". A real D-Wave QPU
backend is not implemented here since it cannot be exercised or verified
in this environment; adding one is future work, not simulated here.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from dwave.samplers import SimulatedAnnealingSampler

from qsci_core.optimization.quantum.qubo_formulator import QUBOInstance

BACKEND_LABEL = "SIMULATED ANNEALING (dwave.samplers.SimulatedAnnealingSampler, classical CPU)"


@dataclass
class AnnealingResult:
    sample: dict
    energy: float
    backend: str
    num_reads: int
    seed: int
    solve_time_seconds: float


def solve_qubo_with_annealing(qi: QUBOInstance, num_reads: int = 100, seed: int = 42) -> AnnealingResult:
    sampler = SimulatedAnnealingSampler()
    t0 = time.perf_counter()
    sampleset = sampler.sample(qi.bqm, num_reads=num_reads, seed=seed)
    solve_time = time.perf_counter() - t0

    best = sampleset.first
    return AnnealingResult(
        sample=dict(best.sample), energy=float(best.energy), backend=BACKEND_LABEL,
        num_reads=num_reads, seed=seed, solve_time_seconds=solve_time,
    )
