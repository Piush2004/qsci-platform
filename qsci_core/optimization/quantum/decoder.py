"""Decodes a QUBO sample (bitstring/assignment) into real vehicle routes,
independently validates feasibility, and computes the real route cost via
exact per-vehicle sequencing.

The QUBO's soft capacity penalty (qubo_formulator.py) only *discourages*
overload -- it does not guarantee it. This module is the one place that
makes a hard feasibility determination, regardless of what the QUBO
solver returned. A solution that violates capacity, double-assigns, or
drops a customer is reported INFEASIBLE here -- never silently repaired.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np


@dataclass
class DecodedSolution:
    feasible: bool
    feasibility_reason: str
    assignment: dict  # vehicle_idx -> list of customer indices (unordered, as assigned)
    routes: dict  # vehicle_idx -> list of customer indices IN VISIT ORDER (depot implicit at both ends)
    route_costs: dict  # vehicle_idx -> float
    total_cost: float | None
    vehicle_loads: dict  # vehicle_idx -> float


def _exact_route_cost(customers: list[int], depot_dist: np.ndarray, dist: np.ndarray) -> tuple[list[int], float]:
    """Exact optimal visiting order for a small customer set via full
    permutation enumeration (brute force) -- tractable only because
    per-vehicle clusters from the QUBO's small instances are small
    (typically <= 6-8 customers after clustering)."""
    if not customers:
        return [], 0.0
    if len(customers) == 1:
        c = customers[0]
        return [c], float(depot_dist[c] + depot_dist[c])

    best_order, best_cost = None, float("inf")
    for perm in itertools.permutations(customers):
        cost = depot_dist[perm[0]]
        for a, b in zip(perm[:-1], perm[1:]):
            cost += dist[a, b]
        cost += depot_dist[perm[-1]]
        if cost < best_cost:
            best_cost, best_order = cost, list(perm)
    return best_order, best_cost


def decode_qubo_sample(
    sample: dict,
    n_customers: int,
    n_vehicles: int,
    coords: np.ndarray,
    demands: np.ndarray,
    capacity: float,
    depot_coord: np.ndarray,
    max_exact_cluster_size: int = 8,
) -> DecodedSolution:
    """`sample` maps variable names "x_{i}_{k}" (as produced by
    qubo_formulator.build_cvrp_qubo) to 0/1. Returns a fully validated,
    costed solution -- or an explicit INFEASIBLE verdict."""

    assignment: dict[int, list[int]] = {k: [] for k in range(n_vehicles)}
    visit_counts = {i: 0 for i in range(n_customers)}

    for i in range(n_customers):
        for k in range(n_vehicles):
            var = f"x_{i}_{k}"
            if sample.get(var, 0) == 1:
                assignment[k].append(i)
                visit_counts[i] += 1

    unvisited = [i for i, c in visit_counts.items() if c == 0]
    duplicated = [i for i, c in visit_counts.items() if c > 1]

    if unvisited:
        return DecodedSolution(
            feasible=False, feasibility_reason=f"customers never assigned to any vehicle: {unvisited}",
            assignment=assignment, routes={}, route_costs={}, total_cost=None, vehicle_loads={},
        )
    if duplicated:
        return DecodedSolution(
            feasible=False, feasibility_reason=f"customers assigned to multiple vehicles: {duplicated}",
            assignment=assignment, routes={}, route_costs={}, total_cost=None, vehicle_loads={},
        )

    vehicle_loads = {k: float(sum(demands[i] for i in custs)) for k, custs in assignment.items()}
    overloaded = {k: load for k, load in vehicle_loads.items() if load > capacity + 1e-9}
    if overloaded:
        return DecodedSolution(
            feasible=False, feasibility_reason=f"vehicle capacity exceeded: {overloaded} (capacity={capacity})",
            assignment=assignment, routes={}, route_costs={}, total_cost=None, vehicle_loads=vehicle_loads,
        )

    for k, custs in assignment.items():
        if len(custs) > max_exact_cluster_size:
            return DecodedSolution(
                feasible=False,
                feasibility_reason=(
                    f"vehicle {k} assigned {len(custs)} customers, exceeding max_exact_cluster_size="
                    f"{max_exact_cluster_size} -- exact sequencing would be computationally intractable "
                    f"(brute force decode is O(n!)); reported as infeasible-to-decode, not silently approximated"
                ),
                assignment=assignment, routes={}, route_costs={}, total_cost=None, vehicle_loads=vehicle_loads,
            )

    coords = np.asarray(coords, dtype=float)
    diff = coords[:, None, :] - coords[None, :, :]
    dist = np.sqrt((diff ** 2).sum(axis=-1))
    depot_dist = np.sqrt(((coords - depot_coord) ** 2).sum(axis=1))

    routes, route_costs = {}, {}
    for k, custs in assignment.items():
        order, cost = _exact_route_cost(custs, depot_dist, dist)
        routes[k] = order
        route_costs[k] = cost

    total_cost = float(sum(route_costs.values()))

    return DecodedSolution(
        feasible=True, feasibility_reason="all customers visited exactly once, all vehicles within capacity",
        assignment=assignment, routes=routes, route_costs=route_costs, total_cost=total_cost,
        vehicle_loads=vehicle_loads,
    )
