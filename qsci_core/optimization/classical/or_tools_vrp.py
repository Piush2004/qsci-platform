"""Classical CVRP solver via OR-Tools routing — the baseline every quantum
routing result in Phase 3 is measured against."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


@dataclass
class VRPSolution:
    status: str  # "OPTIMAL_OR_FEASIBLE" | "INFEASIBLE"
    routes: list[list[int]] = field(default_factory=list)  # node indices per vehicle, depot excluded
    total_distance: float | None = None
    vehicles_used: int = 0


def _euclidean_distance_matrix(coords: np.ndarray) -> np.ndarray:
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def solve_cvrp(
    coords: np.ndarray,
    demands: np.ndarray,
    capacity: float,
    n_vehicles: int,
    depot: int = 0,
    distance_matrix: np.ndarray | None = None,
    time_limit_seconds: int = 10,
) -> VRPSolution:
    """Solve a Capacitated VRP instance with OR-Tools.

    `coords` is used for Euclidean distances unless `distance_matrix` is
    supplied directly (e.g. real travel times from the Last-Mile dataset).
    Demand and capacity are integers internally — OR-Tools' CP solver
    requires integral capacity constraints, so both are rounded.
    """
    coords = np.asarray(coords, dtype=float)
    demands = np.asarray(demands, dtype=float)
    n = len(demands)

    if n == 0:
        raise ValueError("empty instance: no nodes/demands given")
    if len(coords) != n and distance_matrix is None:
        raise ValueError(f"coords length {len(coords)} != demands length {n}")
    if not (0 <= depot < n):
        raise ValueError(f"depot index {depot} out of range for {n} nodes")
    if capacity <= 0:
        raise ValueError(f"capacity must be positive, got {capacity}")
    if n_vehicles <= 0:
        raise ValueError(f"n_vehicles must be positive, got {n_vehicles}")
    if np.any(demands < 0):
        raise ValueError("negative demand present")
    if np.any(demands[np.arange(n) != depot] > capacity):
        raise ValueError("at least one node's demand exceeds vehicle capacity — instance is infeasible by construction")

    dist_matrix = distance_matrix if distance_matrix is not None else _euclidean_distance_matrix(coords)
    dist_matrix_int = (dist_matrix * 1000).round().astype(int)  # OR-Tools wants integer costs
    demands_int = demands.round().astype(int)
    capacity_int = int(round(capacity))

    manager = pywrapcp.RoutingIndexManager(n, n_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return int(dist_matrix_int[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        return int(demands_int[manager.IndexToNode(from_index)])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, [capacity_int] * n_vehicles, True, "Capacity")

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_params.time_limit.FromSeconds(time_limit_seconds)

    solution = routing.SolveWithParameters(search_params)
    if solution is None:
        return VRPSolution(status="INFEASIBLE")

    routes = []
    total_distance = 0
    for vehicle_id in range(n_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_distance = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != depot:
                route.append(node)
            prev_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(prev_index, index, vehicle_id)
        if route:
            routes.append(route)
        total_distance += route_distance

    return VRPSolution(
        status="OPTIMAL_OR_FEASIBLE",
        routes=routes,
        total_distance=total_distance / 1000,  # undo the integer scaling
        vehicles_used=len(routes),
    )
