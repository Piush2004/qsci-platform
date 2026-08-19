"""Experiment manifest and results schema for Phase 3 quantum-routing
comparisons. Every solver (OR-Tools, annealing, QAOA) consumes the exact
same manifest -- same instance, same constraints, same objective -- per
CLAUDE.md Phase 3 spec's fairness requirement."""

from __future__ import annotations

import csv
import json
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2], text=True
        ).strip()
    except Exception:
        return "unknown"


def _package_versions() -> dict:
    import importlib
    import importlib.metadata

    versions = {}
    for pkg, dist_name in (
        ("qiskit", "qiskit"), ("qiskit_optimization", "qiskit-optimization"),
        ("qiskit_algorithms", "qiskit-algorithms"), ("dimod", "dimod"),
        ("dwave.samplers", "dwave-samplers"), ("ortools", "ortools"), ("numpy", "numpy"),
    ):
        try:
            mod = importlib.import_module(pkg)
            versions[pkg] = getattr(mod, "__version__", None) or importlib.metadata.version(dist_name)
        except ImportError:
            versions[pkg] = "not installed"
    return versions


@dataclass
class RoutingManifest:
    dataset: str
    dataset_version: str
    instance_id: str
    instance_status: str  # "LIVE" or "RESEARCH - DERIVED / SYNTHETIC EXTENSION"
    num_stops: int
    num_vehicles: int
    vehicle_capacity: float
    seed: int
    objective: str
    constraints: list[str]
    penalty_multiplier: float
    time_limit_seconds: float
    classical_solver: str
    annealing_backend: str
    qaoa_backend: str
    source_hash: str
    software_versions: dict = field(default_factory=_package_versions)
    hardware: str = field(default_factory=lambda: f"{platform.system()} {platform.machine()}, {platform.processor()}")
    git_commit: str = field(default_factory=_git_commit)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RoutingResult:
    """One row of the Phase 3 experiment matrix."""
    experiment_id: str
    dataset: str
    instance: str
    stops: int
    vehicles: int
    capacity: float
    seed: int
    solver: str  # "or_tools_native" | "or_tools_qubo" | "simulated_annealing" | "qaoa" | "brute_force"
    algorithm: str
    qaoa_depth: int | None
    qubits: int | None
    qubo_variables: int | None
    circuit_depth: int | None
    gate_count: int | None
    shots: int | None
    runtime_solver_seconds: float
    runtime_end_to_end_seconds: float
    objective_cost: float | None
    reference_cost: float | None
    reference_type: str  # "BKS" | "BRUTE_FORCE_OPTIMUM" | "BEST_FOUND" | "UNKNOWN"
    optimality_gap_pct: float | None
    feasible: bool
    feasibility_reason: str
    repair_used: bool
    status: str  # "LIVE" | "RESEARCH" | "ILLUSTRATIVE" | "PENDING"
    classification: str  # "OPTIMAL" | "FEASIBLE" | "INFEASIBLE" | "TIMEOUT" | "UNKNOWN"

    def to_dict(self) -> dict:
        return asdict(self)


def save_results(results: list[RoutingResult], json_path: Path | str, csv_path: Path | str) -> None:
    json_path, csv_path = Path(json_path), Path(csv_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [r.to_dict() for r in results]
    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2, default=str)

    if rows:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
