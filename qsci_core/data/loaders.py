"""Raw dataset loaders for QSCI. Every function here reads real files from disk —
none of it fabricates or samples synthetic data."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

DEFAULT_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def load_m5(raw_dir: Path | str = DEFAULT_RAW_DIR / "m5") -> dict[str, pd.DataFrame]:
    """Load the M5 Forecasting - Accuracy competition files.

    Expects sales_train_validation.csv (or sales_train_evaluation.csv),
    calendar.csv, and sell_prices.csv in `raw_dir`.
    """
    raw_dir = Path(raw_dir)

    sales_path = raw_dir / "sales_train_evaluation.csv"
    if not sales_path.exists():
        sales_path = raw_dir / "sales_train_validation.csv"
    calendar_path = raw_dir / "calendar.csv"
    prices_path = raw_dir / "sell_prices.csv"

    missing = [p for p in (sales_path, calendar_path, prices_path) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            f"M5 files missing under {raw_dir}: {[str(p) for p in missing]}. "
            "Download via `kaggle competitions download -c m5-forecasting-accuracy`."
        )

    return {
        "sales": pd.read_csv(sales_path),
        "calendar": pd.read_csv(calendar_path, parse_dates=["date"]),
        "prices": pd.read_csv(prices_path),
    }


def load_cvrplib_instance(name: str, raw_dir: Path | str = DEFAULT_RAW_DIR / "cvrplib"):
    """Load a single CVRPLIB instance by name (e.g. 'A-n32-k5') via the vrplib package."""
    import vrplib

    raw_dir = Path(raw_dir)
    instance_path = raw_dir / f"{name}.vrp"
    solution_path = raw_dir / f"{name}.sol"
    if not instance_path.exists():
        raise FileNotFoundError(
            f"CVRPLIB instance not found: {instance_path}. Fetch it first "
            f"(vrplib.download_instance('{name}', '{raw_dir}'))."
        )
    instance = vrplib.read_instance(str(instance_path))
    solution = vrplib.read_solution(str(solution_path)) if solution_path.exists() else None
    return instance, solution


def load_last_mile(raw_dir: Path | str = DEFAULT_RAW_DIR / "last_mile") -> dict:
    """Load the Amazon Last-Mile Routing Research Challenge model_build_inputs.

    Returns the raw JSON dicts for route_data, package_data, travel_times,
    actual_sequences, and invalid_sequence_scores (whichever files are
    present under raw_dir).
    """
    raw_dir = Path(raw_dir)
    candidates = {
        "route_data": "route_data.json",
        "package_data": "package_data.json",
        "travel_times": "travel_times.json",
        "actual_sequences": "actual_sequences.json",
        "invalid_sequence_scores": "invalid_sequence_scores.json",
    }
    result = {}
    for key, filename in candidates.items():
        matches = list(raw_dir.rglob(filename))
        if not matches:
            continue
        with open(matches[0], "r") as f:
            result[key] = json.load(f)

    if not result:
        raise FileNotFoundError(
            f"No Last-Mile files found under {raw_dir}. Sync via "
            "`aws s3 sync --no-sign-request s3://amazon-last-mile-challenges/almrrc2021/ ./data/raw/last_mile/`."
        )
    return result
