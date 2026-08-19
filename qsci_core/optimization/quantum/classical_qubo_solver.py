"""Solves the EXACT SAME QUBO (qubo_formulator.build_cvrp_qubo) with
OR-Tools CP-SAT -- not the native VRP routing solver used in Phase 1.

This exists specifically for fairness (CLAUDE.md Phase 3 spec §8): a
comparison between quantum/annealing and OR-Tools' full native VRP solver
would be comparing two different problem formulations. This module makes
OR-Tools solve the identical binary-quadratic objective and constraints
the quantum/annealing tracks solve, so all three methods are compared on
one problem definition. Phase 1's OR-Tools VRP baseline remains a
separate, differently-labeled reference (see docs/PHASE_3_REPORT.md).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from ortools.sat.python import cp_model

from qsci_core.optimization.quantum.qubo_formulator import QUBOInstance


@dataclass
class ClassicalQUBOResult:
    sample: dict
    energy: float
    status: str
    solve_time_seconds: float


def solve_qubo_with_ortools(qi: QUBOInstance, time_limit_seconds: float = 30.0) -> ClassicalQUBOResult:
    model = cp_model.CpModel()
    bool_vars = {name: model.NewBoolVar(name) for name in qi.bqm.variables}

    # CP-SAT works with integer objectives -- scale float coefficients to
    # integers via a fixed-point multiplier, matching common CP-SAT practice.
    SCALE = 10_000
    linear_terms = []
    for var, bias in qi.bqm.linear.items():
        linear_terms.append(round(bias * SCALE) * bool_vars[var])

    quadratic_terms = []
    for (u, v), bias in qi.bqm.quadratic.items():
        prod = model.NewBoolVar(f"prod_{u}_{v}")
        model.AddMultiplicationEquality(prod, [bool_vars[u], bool_vars[v]])
        quadratic_terms.append(round(bias * SCALE) * prod)

    model.Minimize(sum(linear_terms) + sum(quadratic_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.random_seed = 42

    t0 = time.perf_counter()
    status = solver.Solve(model)
    solve_time = time.perf_counter() - t0

    status_name = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return ClassicalQUBOResult(sample={}, energy=float("nan"), status=status_name, solve_time_seconds=solve_time)

    sample = {name: solver.Value(v) for name, v in bool_vars.items()}
    energy = qi.bqm.energy(sample)
    return ClassicalQUBOResult(sample=sample, energy=float(energy), status=status_name, solve_time_seconds=solve_time)
