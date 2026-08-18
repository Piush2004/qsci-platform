"""Experiment manifest and results schema for Phase 2 quantum-vs-classical
forecasting comparisons. Both tracks must be reproducible from the manifest
this module builds — dataset, split, seed, and every configuration are
captured explicitly rather than left implicit in notebook code."""

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
    versions = {}
    for pkg in ("qiskit", "qiskit_machine_learning", "qiskit_aer", "lightgbm", "sklearn", "numpy", "pandas"):
        try:
            mod = __import__(pkg)
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not installed"
    return versions


@dataclass
class ExperimentManifest:
    dataset: str
    dataset_version: str
    series_id: str
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    forecast_horizon: int
    seed: int
    classical_feature_columns: list[str]
    software_versions: dict = field(default_factory=_package_versions)
    hardware: str = field(default_factory=lambda: f"{platform.system()} {platform.machine()}, {platform.processor()}")
    simulator: str = "qiskit_aer.AerSimulator(method=statevector)"
    git_commit: str = field(default_factory=_git_commit)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExperimentConfigResult:
    """One row of the Phase 2 experiment matrix — every field CLAUDE.md's
    Phase 2 spec requires per configuration. `None` means genuinely
    unavailable for this model type (e.g. classical models have no qubit
    count), never a placeholder for a number that wasn't measured."""
    model: str
    feature_count: int | None
    qubit_count: int | None
    feature_map: str | None
    ansatz: str | None
    optimizer: str | None
    optimizer_iterations: int | None
    circuit_depth: int | None
    gate_count: int | None
    shots: str | None
    simulator: str | None
    execution_time_seconds: float
    training_time_seconds: float | None
    inference_time_seconds: float | None
    rmse: float
    mae: float
    wmape: float
    bias: float

    def to_dict(self) -> dict:
        return asdict(self)


def save_results(results: list[ExperimentConfigResult], json_path: Path | str, csv_path: Path | str) -> None:
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
