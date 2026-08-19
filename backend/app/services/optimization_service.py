"""Wraps qsci_core.optimization for the /api/v1/optimize routes.

Inventory (EOQ) and routing-via-OR-Tools/annealing are fast -- run
synchronously. QAOA is slow (documented: up to ~630s at 10 qubits, Phase
3/4 measurements) -- always dispatched as a background task."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from qsci_core.data import loaders
from qsci_core.financial.eoq import CostAssumptions, economic_order_quantity, safety_stock
from qsci_core.optimization.classical.or_tools_vrp import solve_cvrp
from qsci_core.optimization.quantum.annealing_solver import solve_qubo_with_annealing
from qsci_core.optimization.quantum.decoder import decode_qubo_sample
from qsci_core.optimization.quantum.instance_builder import build_derived_instance
from qsci_core.optimization.quantum.qaoa_solver import solve_qubo_with_qaoa
from qsci_core.optimization.quantum.qubo_formulator import build_cvrp_qubo
from qsci_core.persistence.models import OptimizationRunRecord, RunStatus

SUPPORTED_METHODS = {"eoq", "or_tools", "simulated_annealing", "qaoa"}


def create_run(db: Session, problem_type: str, method: str, input_params: dict) -> OptimizationRunRecord:
    if method not in SUPPORTED_METHODS:
        raise ValueError(f"unsupported method '{method}', must be one of {sorted(SUPPORTED_METHODS)}")
    label = "ILLUSTRATIVE" if method == "eoq" else ("LIVE" if method in ("or_tools",) else "RESEARCH")
    run = OptimizationRunRecord(
        problem_type=problem_type, method=method, run_status=RunStatus.PENDING,
        label=label, input_params=input_params,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def execute_run(db: Session, run_id: int) -> None:
    run = db.get(OptimizationRunRecord, run_id)
    if run is None:
        return
    run.run_status = RunStatus.RUNNING
    db.commit()

    try:
        t0 = time.perf_counter()
        if run.method == "eoq":
            objective, solution, feasible, resource_metrics = _run_eoq(run.input_params)
        elif run.method == "or_tools":
            objective, solution, feasible, resource_metrics = _run_or_tools(run.input_params)
        elif run.method in ("simulated_annealing", "qaoa"):
            objective, solution, feasible, resource_metrics = _run_qubo_track(run.method, run.input_params)
        else:
            raise ValueError(f"unsupported method '{run.method}'")

        run.objective = objective
        run.solution = solution
        run.feasible = feasible
        run.resource_metrics = resource_metrics
        run.runtime_seconds = time.perf_counter() - t0
        run.run_status = RunStatus.COMPLETE
        run.completed_at = datetime.now(timezone.utc)
    except Exception as exc:  # noqa: BLE001
        run.run_status = RunStatus.FAILED
        run.error = f"{type(exc).__name__}: {exc}"
        run.completed_at = datetime.now(timezone.utc)
    db.commit()


def _run_eoq(params: dict) -> tuple[float, dict, bool, dict]:
    costs = CostAssumptions(
        holding_cost_per_unit_per_year=params["holding_cost_per_unit_per_year"],
        ordering_cost_per_order=params["ordering_cost_per_order"],
        stockout_cost_per_unit=params["stockout_cost_per_unit"],
    )
    eoq = economic_order_quantity(params["annual_demand"], costs)
    ss = safety_stock(params["demand_std"], params["lead_time_days"], params.get("service_z", 1.645))
    return eoq, {"eoq": eoq, "safety_stock": ss, "cost_assumptions": {
        "holding_cost_per_unit_per_year": costs.holding_cost_per_unit_per_year,
        "ordering_cost_per_order": costs.ordering_cost_per_order,
        "stockout_cost_per_unit": costs.stockout_cost_per_unit,
        "status": costs.status,
    }}, True, {}


def _run_or_tools(params: dict) -> tuple[float, dict, bool, dict]:
    instance_name = params.get("cvrplib_instance", "A-n32-k5")
    instance, _sol = loaders.load_cvrplib_instance(instance_name)
    coords = instance["node_coord"]
    demands = instance["demand"]
    result = solve_cvrp(
        coords=coords, demands=demands, capacity=instance["capacity"],
        n_vehicles=params.get("n_vehicles", 5), time_limit_seconds=params.get("time_limit_seconds", 10),
    )
    feasible = result.status != "INFEASIBLE"
    return (result.total_distance or 0.0), {"routes": result.routes, "vehicles_used": result.vehicles_used, "status": result.status}, feasible, {}


def _run_qubo_track(method: str, params: dict) -> tuple[float, dict, bool, dict]:
    n_customers = params.get("n_customers", 4)
    di = build_derived_instance(params.get("cvrplib_instance", "A-n32-k5"), n_customers)
    qi = build_cvrp_qubo(di.coords, di.demands, di.capacity, di.n_vehicles, penalty_multiplier=params.get("penalty_multiplier", 2.0))

    if method == "simulated_annealing":
        res = solve_qubo_with_annealing(qi, num_reads=params.get("num_reads", 1000), seed=params.get("seed", 42))
        resource_metrics = {"num_reads": res.num_reads, "backend": res.backend}
    else:  # qaoa
        res = solve_qubo_with_qaoa(
            qi, p=params.get("p", 1), optimizer_maxiter=params.get("optimizer_maxiter", 20),
            shots=params.get("shots", 1024), seed=params.get("seed", 42), noise_preset=params.get("noise_preset", "noiseless"),
        )
        resource_metrics = {
            "qubits": res.metadata.n_qubits, "circuit_depth": res.metadata.circuit_depth,
            "gate_count": res.metadata.gate_count_total, "shots": res.metadata.shots, "simulator": res.metadata.simulator,
        }

    decoded = decode_qubo_sample(res.sample, n_customers, di.n_vehicles, di.coords, di.demands, di.capacity, di.depot_coord)
    solution = {
        "routes": decoded.routes, "vehicle_loads": decoded.vehicle_loads,
        "feasibility_reason": decoded.feasibility_reason, "instance_status": di.status,
    }
    return (decoded.total_cost if decoded.feasible else 0.0), solution, decoded.feasible, resource_metrics


def get_run(db: Session, run_id: int) -> OptimizationRunRecord | None:
    return db.get(OptimizationRunRecord, run_id)
