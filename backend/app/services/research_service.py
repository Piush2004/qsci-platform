"""Serves /api/v1/research/* directly from experiments/results/*.json --
read fresh from disk on every request, never mirrored into the DB and
left to drift. These are the same files the audited notebooks/reports
(Phase 2-5) already cite -- this module adds zero new computation, only
exposure."""

from __future__ import annotations

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parents[3] / "experiments" / "results"


def _load(name: str):
    path = RESULTS_DIR / name
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def get_benchmarks() -> dict:
    """Master scorecard + business-impact comparison (Phase 5)."""
    scorecard = _load("classical_vs_quantum_results.json")
    return {
        "status": "RESEARCH" if scorecard else "PENDING",
        "source_files": ["classical_vs_quantum_results.json", "table8_master_scorecard.csv"],
        "results": scorecard,
        "note": "Classical vs. quantum benchmark across forecasting and routing, Phase 5 (docs/PHASE_5_REPORT.md). "
                "No quantum advantage established on any dimension.",
    }


def get_experiments() -> dict:
    """Index of every phase's real experiment result files."""
    files = {
        "phase2_forecasting": "quantum_forecasting_results.json",
        "phase2_1_leakage_corrected": "phase2_1_leakage_free_results.json",
        "phase3_routing": "routing_results.json",
        "phase3_penalty_sensitivity": "routing_penalty_sensitivity.json",
        "phase4_noise_and_scaling": "phase4_noise_and_scaling_results.json",
        "phase4_unified": "phase4_noise_scalability.json",
    }
    return {
        "status": "RESEARCH",
        "experiments": {
            key: {"source_file": fname, "available": (RESULTS_DIR / fname).exists()}
            for key, fname in files.items()
        },
    }


def get_scalability() -> dict:
    data = _load("phase4_noise_and_scaling_results.json")
    if data is None:
        return {"status": "PENDING", "note": "Phase 4 results not found on disk."}
    return {
        "status": "RESEARCH",
        "source_file": "phase4_noise_and_scaling_results.json",
        "qaoa_runtime_wall": data.get("part_a_runtime_wall_diagnosis"),
        "annealing_feasibility_by_reads": data.get("part_b_annealing_reads_sweep"),
        "qaoa_depth_tradeoff": data.get("part_d_qaoa_depth_sweep"),
    }


def get_noise() -> dict:
    data = _load("phase4_noise_and_scaling_results.json")
    if data is None:
        return {"status": "PENDING", "note": "Phase 4 results not found on disk."}
    return {
        "status": "RESEARCH",
        "source_file": "phase4_noise_and_scaling_results.json",
        "noise_sensitivity": data.get("part_c_noise_sensitivity"),
        "caveat": (
            "No quality/feasibility degradation was measured at these noise magnitudes, but the metric "
            "used (best-of-1024-shots) can mask distributional degradation -- a direct success-probability "
            "measurement was not run (PENDING). See docs/PHASE_4_REPORT.md sec.6."
        ),
    }
