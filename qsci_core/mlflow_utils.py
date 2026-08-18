"""mlflow experiment tracking wrapper. Every run logs dataset version, seed,
params, metrics, runtime, and git commit — per CLAUDE.md §7, no run is
comparable to another without this."""

from __future__ import annotations

import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import mlflow

DEFAULT_TRACKING_DIR = Path(__file__).resolve().parents[1] / "experiments" / "mlruns"

# mlflow 3.x deprecated the plain filesystem tracking store in favor of a
# database backend (sqlite here — no external server needed for local runs).


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True
        ).strip()
    except Exception:
        return "unknown"


def set_tracking_uri(path: Path | str = DEFAULT_TRACKING_DIR) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    db_path = path / "tracking.db"
    mlflow.set_tracking_uri(f"sqlite:///{db_path.as_posix()}")


@contextmanager
def tracked_run(experiment_name: str, run_name: str, dataset_version: str, seed: int, params: dict):
    """Context manager: logs dataset_version/seed/params/git-commit on entry,
    metrics + runtime_seconds via the yielded logger on exit.

    Usage:
        with tracked_run("m5_forecasting", "lightgbm_v1", "m5-2020-06-01", 42, {"n_estimators": 200}) as log:
            ...
            log({"rmse": 3.1, "wmape": 5.5})
    """
    mlflow.set_experiment(experiment_name)
    start = time.perf_counter()
    logged_metrics: dict = {}

    def log_metrics(metrics: dict) -> None:
        logged_metrics.update(metrics)

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("dataset_version", dataset_version)
        mlflow.log_param("seed", seed)
        mlflow.log_params(params)
        mlflow.set_tag("git_commit", _git_commit())
        try:
            yield log_metrics
        finally:
            runtime_seconds = time.perf_counter() - start
            if logged_metrics:
                mlflow.log_metrics(logged_metrics)
            mlflow.log_metric("runtime_seconds", runtime_seconds)
