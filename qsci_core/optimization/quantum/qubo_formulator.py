"""CVRP QUBO formulation — cluster-first, route-second decomposition.

Mathematical formulation
-------------------------
Given n customers (indices 0..n-1), a depot, K vehicles, capacity Q,
demands d_i, and a distance matrix c_ij:

Decision variables: x_{i,k} in {0,1} for customer i, vehicle k -- 1 if
customer i is assigned to vehicle k. n*K binary variables, no slack bits.

Objective (pairwise-distance clustering proxy for route length):
    sum_k sum_{i<j} c_ij * x_{i,k} * x_{j,k}
Two customers sharing a vehicle contribute their pairwise distance to the
objective -- a standard cluster-first-route-second proxy: routes formed
from mutually-close customers tend to be shorter than routes formed from
scattered ones. This QUBO does NOT decide visitation order within a
vehicle (that would need O(n^2*K) position variables -- intractable for
QAOA even at n=4, see docs/PHASE_3_REPORT.md). Order is decided
classically post-hoc by exact enumeration over each (small) assigned
cluster -- see decoder.py.

Constraints, as penalty terms:
    1. Each customer assigned to exactly one vehicle:
       lambda1 * sum_i (sum_k x_{i,k} - 1)^2
    2. Vehicle capacity (soft, no slack variables -- see below):
       lambda2 * sum_k (sum_i d_i * x_{i,k} - Q)^2

Capacity is a SOFT squared-deviation penalty targeting the capacity
ceiling, not a hard inequality via slack bits. An exact inequality
encoding needs ceil(log2(Q+1)) extra binary variables PER VEHICLE (e.g.
~7 qubits/vehicle for Q=100) -- this would dominate qubit count for even
n=4 and make QAOA intractable before the customer-assignment problem
itself does. The soft penalty keeps the QUBO to exactly n*K variables.
This is a documented, deliberate trade-off, not a hidden shortcut: the
QUBO's penalty only *discourages* overload; capacity feasibility is
checked as a HARD, independent condition at decode time
(qsci_core/optimization/quantum/decoder.py) regardless of what the QUBO's
soft penalty produced. A QUBO solution can still be reported INFEASIBLE.

Penalty derivation (not arbitrary, per CLAUDE.md Phase 3 spec):
    lambda2 = m * n * max(c_ij)
    lambda1 = m * (n * max(c_ij) + K * lambda2 * Q^2)
where m is `penalty_multiplier`. lambda2 is sized against the objective's
own scale, same reasoning as before. lambda1 must dominate not just the
objective's maximum possible improvement, but ALSO the maximum possible
saving in capacity-penalty achievable by violating the visit-once
constraint -- e.g. assigning one customer to every vehicle so each
vehicle's load lands on exactly Q (zeroing the symmetric capacity
penalty), while leaving other customers unassigned entirely. That second
term (K * lambda2 * Q^2) was MISSING from an earlier version of this
derivation, which only bounded lambda1 against the objective. The bug was
real: dimod.ExactSolver's true brute-force optimum on a live CVRPLIB-
derived 4-customer instance assigned 2 of 4 customers to BOTH vehicles and
left the other 2 unassigned entirely, because that degenerate assignment
hit each vehicle's capacity target exactly (zero capacity penalty) while
the constraint-1 violation cost was smaller than the capacity-penalty
"savings" -- see docs/PHASE_3_REPORT.md section 9 for the specific
numbers and the fix. A penalty sensitivity study (varying `m`) is in
notebooks/05_routing_qubo.ipynb and docs/PHASE_3_REPORT.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import dimod
import numpy as np


@dataclass(frozen=True)
class QUBOInstance:
    bqm: dimod.BinaryQuadraticModel
    n_customers: int
    n_vehicles: int
    variable_map: dict  # (customer_idx, vehicle_idx) -> variable name
    penalty_visit: float
    penalty_capacity: float
    n_variables: int
    n_quadratic_terms: int
    density: float  # fraction of possible pairwise terms actually present
    construction_time_seconds: float


def _distance_matrix(coords: np.ndarray) -> np.ndarray:
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def build_cvrp_qubo(
    coords: np.ndarray,
    demands: np.ndarray,
    capacity: float,
    n_vehicles: int,
    penalty_multiplier: float = 2.0,
) -> QUBOInstance:
    """Build the CVRP assignment QUBO for customers only (no depot variable
    -- the depot is implicit start/end of every vehicle's route).

    `coords`/`demands` must exclude the depot (index 0 of the original
    instance) -- pass customer-only arrays.
    """
    import time
    t0 = time.perf_counter()

    coords = np.asarray(coords, dtype=float)
    demands = np.asarray(demands, dtype=float)
    n = len(demands)

    if n == 0:
        raise ValueError("empty instance: no customers given")
    if len(coords) != n:
        raise ValueError(f"coords length {len(coords)} != demands length {n}")
    if n_vehicles <= 0:
        raise ValueError(f"n_vehicles must be positive, got {n_vehicles}")
    if capacity <= 0:
        raise ValueError(f"capacity must be positive, got {capacity}")
    if np.any(demands < 0):
        raise ValueError("negative demand present")
    if np.any(demands > capacity):
        raise ValueError("at least one customer's demand exceeds vehicle capacity -- infeasible by construction")
    if np.sum(demands) > capacity * n_vehicles:
        raise ValueError(
            f"total demand {demands.sum()} exceeds total fleet capacity {capacity * n_vehicles} "
            f"({n_vehicles} vehicles x {capacity}) -- infeasible by construction, add more vehicles"
        )

    dist = _distance_matrix(coords)
    c_max = float(dist[dist > 0].max()) if np.any(dist > 0) else 1.0

    # penalty_capacity first: it must dominate the objective's own scale.
    penalty_capacity = penalty_multiplier * n * c_max
    # penalty_visit must dominate BOTH the objective's scale AND the maximum
    # possible saving in capacity-penalty achievable by violating the
    # visit-once constraint (e.g. assigning one customer to every vehicle to
    # push each vehicle's load to exactly `capacity`, which zeroes the
    # capacity penalty while leaving other customers unassigned). That
    # second term was missing from the original derivation -- found via the
    # brute-force validation this module's docstring requires; see
    # docs/PHASE_3_REPORT.md section 9 for the failing case and fix.
    penalty_visit = penalty_multiplier * (n * c_max + n_vehicles * penalty_capacity * capacity ** 2)

    var = lambda i, k: f"x_{i}_{k}"
    variable_map = {(i, k): var(i, k) for i in range(n) for k in range(n_vehicles)}

    bqm = dimod.BinaryQuadraticModel(vartype=dimod.BINARY)

    # Objective: pairwise distance within the same vehicle
    for k in range(n_vehicles):
        for i in range(n):
            for j in range(i + 1, n):
                bqm.add_quadratic(var(i, k), var(j, k), float(dist[i, j]))

    # Constraint 1: each customer assigned to exactly one vehicle
    # lambda1 * (sum_k x_ik - 1)^2 = lambda1 * (sum_k x_ik^2 + 2*sum_{k<k'} x_ik*x_ik' - 2*sum_k x_ik + 1)
    # x_ik^2 = x_ik for binary variables.
    for i in range(n):
        for k in range(n_vehicles):
            bqm.add_linear(var(i, k), penalty_visit * (1 - 2))
        for k1 in range(n_vehicles):
            for k2 in range(k1 + 1, n_vehicles):
                bqm.add_quadratic(var(i, k1), var(i, k2), 2 * penalty_visit)
        bqm.offset += penalty_visit

    # Constraint 2: soft capacity penalty per vehicle
    # lambda2 * (sum_i d_i*x_ik - Q)^2
    for k in range(n_vehicles):
        for i in range(n):
            bqm.add_linear(var(i, k), penalty_capacity * (demands[i] ** 2 - 2 * capacity * demands[i]))
        for i in range(n):
            for j in range(i + 1, n):
                bqm.add_quadratic(var(i, k), var(j, k), 2 * penalty_capacity * demands[i] * demands[j])
        bqm.offset += penalty_capacity * capacity ** 2

    n_variables = n * n_vehicles
    n_possible_quadratic = n_variables * (n_variables - 1) / 2
    n_quadratic_terms = len(bqm.quadratic)
    density = n_quadratic_terms / n_possible_quadratic if n_possible_quadratic > 0 else 0.0

    construction_time = time.perf_counter() - t0

    return QUBOInstance(
        bqm=bqm, n_customers=n, n_vehicles=n_vehicles, variable_map=variable_map,
        penalty_visit=penalty_visit, penalty_capacity=penalty_capacity,
        n_variables=n_variables, n_quadratic_terms=n_quadratic_terms, density=density,
        construction_time_seconds=construction_time,
    )
