"""Builds real-data-derived routing sub-instances for the Phase 3 scaling
study. Coordinates and demands are taken directly from a real CVRPLIB
instance (verified in Phase 0/3); truncating to N customers means the
sub-instance no longer matches the original published best-known solution,
so every instance built here is labeled RESEARCH - DERIVED / SYNTHETIC
EXTENSION, never LIVE, per CLAUDE.md Phase 3 spec §3.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from qsci_core.data import loaders

STATUS_LABEL = "RESEARCH - DERIVED / SYNTHETIC EXTENSION"


@dataclass(frozen=True)
class DerivedInstance:
    instance_id: str
    source_instance: str
    n_customers: int
    coords: np.ndarray  # customers only, depot excluded
    demands: np.ndarray  # customers only
    depot_coord: np.ndarray
    capacity: float
    n_vehicles: int
    status: str = STATUS_LABEL


def build_derived_instance(
    source_instance: str, n_customers: int, n_vehicles: int | None = None, seed: int = 42,
) -> DerivedInstance:
    """Take the first N customers (by CVRPLIB file order -- deterministic,
    not cherry-picked) from a real CVRPLIB instance, and a capacity scaled
    down proportionally so the sub-instance genuinely needs multiple
    vehicles (using the original per-vehicle capacity would usually let
    one vehicle serve all N customers for small N, making the CVRP trivial
    and uninteresting for a routing study).
    """
    instance, _solution = loaders.load_cvrplib_instance(source_instance)
    coords_full = np.asarray(instance["node_coord"], dtype=float)
    demands_full = np.asarray(instance["demand"], dtype=float)
    depot_idx = 0  # CVRPLIB convention: node 1 (index 0) is the depot

    if n_customers >= len(coords_full) - 1:
        raise ValueError(f"n_customers={n_customers} too large for source instance with {len(coords_full)-1} customers")

    depot_coord = coords_full[depot_idx]
    non_depot_idx = [i for i in range(len(coords_full)) if i != depot_idx][:n_customers]
    coords = coords_full[non_depot_idx]
    demands = demands_full[non_depot_idx]

    total_demand = float(demands.sum())
    if n_vehicles is None:
        n_vehicles = max(2, math.ceil(n_customers / 2))  # small clusters per vehicle, keeps QUBO variable count modest
    capacity = math.ceil(total_demand / n_vehicles * 1.15)  # 15% slack above the perfectly-balanced minimum

    return DerivedInstance(
        instance_id=f"{source_instance}-derived-n{n_customers}",
        source_instance=source_instance, n_customers=n_customers, coords=coords, demands=demands,
        depot_coord=depot_coord, capacity=float(capacity), n_vehicles=n_vehicles,
    )
