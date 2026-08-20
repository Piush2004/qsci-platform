# Milestone 2 Pre-Implementation Audit — Optimization Intelligence

Status: **COMPLETE** (read-only audit, no code modified to produce this)
Date: 2026-08-20

## 1. Current OR-Tools Implementation

`qsci_core/optimization/classical/or_tools_vrp.py::solve_cvrp()` — native CVRP solver (real sequencing, not the QUBO-assignment proxy), Euclidean distance matrix, returns `VRPSolution(status, routes, total_distance, vehicles_used)`. Backed by `backend/app/services/optimization_service.py::_run_or_tools()`, exposed via `POST /optimize {problem_type: "routing", method: "or_tools"}`. Synchronous (fast). Verified against real CVRPLIB instances in Phase 1/3 (0.61% max gap vs. published BKS across all 4 real instances).

## 2. Current QUBO Implementation

`qsci_core/optimization/quantum/qubo_formulator.py::build_cvrp_qubo()` — cluster-first assignment QUBO (`n*K` binary variables), penalty-derivation bug found and fixed in Phase 3 (see `docs/PHASE_3_REPORT.md` §9). `instance_builder.py::build_derived_instance()` truncates a real CVRPLIB instance to N customers (deterministic, first-N by file order — labeled `RESEARCH - DERIVED / SYNTHETIC EXTENSION`). `decoder.py::decode_qubo_sample()` independently validates feasibility regardless of solver output. All three QUBO-track solvers (OR-Tools-on-QUBO, annealing, QAOA) consume the identical `QUBOInstance`.

## 3. Current Simulated Annealing Implementation

`qsci_core/optimization/quantum/annealing_solver.py::solve_qubo_with_annealing()` — `dwave.samplers.SimulatedAnnealingSampler`, classical CPU, honestly labeled (never "hardware" — no D-Wave credentials exist in this environment, verified in Phase 3). Backed by `_run_qubo_track()` in the optimization service, exposed via `POST /optimize {method: "simulated_annealing"}`. Synchronous (fast, sub-second even at `num_reads=5000`).

## 4. Current QAOA Implementation

`qsci_core/optimization/quantum/qaoa_solver.py::solve_qubo_with_qaoa()` — `StatevectorSampler` (noiseless default) or Aer `SamplerV2` (via `noise_preset`, added Phase 4). Real resource metadata (qubits, circuit depth, gate count, shots, simulator label). Backed by `_run_qubo_track()`, exposed via `POST /optimize {method: "qaoa"}`. **Async** — dispatched as a `BackgroundTasks` job (documented up to ~630s at 10 qubits).

## 5. Existing APIs

- `POST /optimize` — creates a run, executes sync (eoq/or_tools/simulated_annealing) or async (qaoa). Real, tested (`backend/tests/test_api.py`).
- `GET /optimization/{run_id}` — fetch one run.
- **Gap**: no `GET /optimization` (list) — exists for recommendations (`GET /recommendations`) but not optimization runs. Needed for a history view.
- **Gap**: no endpoint returning raw CVRPLIB instance data (coordinates, demands, capacity, depot) for problem-context display or route visualization — `GET /data/sources` only returns dataset-level metadata (record counts), not per-instance geometry.
- **Gap**: `optimization_service._run_or_tools`/`_run_qubo_track`'s `solution` dict returns routes as **customer index lists**, not coordinates — insufficient for a frontend route visualization without a second lookup.

## 6. Existing Experiment Results (Reusable, Do Not Re-run)

- `experiments/results/routing_results.json` — 76 rows, Phase 3's full N∈{4,6,8,10,12,16} sweep across or_tools_qubo/simulated_annealing/qaoa, real schema (objective_cost, feasible, runtime_solver_seconds, qubits, circuit_depth, gate_count, etc. — confirmed by direct read this audit).
- `experiments/results/routing_ground_truth.json` — real CVRPLIB metadata (4 instances, verified BKS: A-n32-k5=784, A-n33-k5=661, A-n37-k5=669, B-n31-k5=672) + Amazon Last-Mile re-verification (6,112 routes, 904,527 stops).
- `experiments/results/routing_penalty_sensitivity.json` — Phase 3's 4-point penalty sweep.
- `experiments/results/phase4_noise_and_scaling_results.json` / `phase4_noise_scalability.json` — Phase 4's QAOA runtime-wall diagnosis, annealing num_reads sweep, noise sensitivity, QAOA depth tradeoff.
- All already exposed read-only via `GET /research/scalability` and `GET /research/noise` (`research_service.py`) — Milestone 2 should reuse this pattern for a new `GET /research/routing` (or extend existing) rather than duplicate the read logic.

## 7. Datasets Available

CVRPLIB (4 real instances, `data/raw/cvrplib/`) — primary. Amazon Last-Mile (`data/raw/last_mile/`) — verified counts only; no per-route coordinate/sequencing data has been wired into any solver (Phase 3 explicitly scoped it to "scale context," not a direct routing-solve input). Milestone 2 will use CVRPLIB as the primary interactive dataset, consistent with all prior phases.

## 8. Metrics Available vs. Missing

**Available** (real, per solver): objective_cost, feasible, runtime (solver + end-to-end), qubo_variables, qubits/circuit_depth/gate_count/shots (QAOA only), num_reads (annealing only), classification (OR-Tools only). **Missing/PENDING**: `optimality_gap_pct` is present in the schema but is `null`/`"UNKNOWN"` throughout the real data (Phase 3 never computed it against an external BKS for the QUBO sub-problem, since truncation invalidates the original CVRPLIB BKS — documented in `docs/PHASE_3_REPORT.md` §16). Milestone 2 must preserve this honesty — display gap as `N/A` against the QUBO-track's own OR-Tools-on-QUBO reference (which the data does support, per-N), never against the original CVRPLIB BKS for truncated instances.

## 9. Limitations (Inherited, Not Introduced)

- Cluster-first-route-second QUBO is not the same problem as OR-Tools' native CVRP solve — the two are **not directly comparable** (Phase 3 fairness audit's explicit finding). Milestone 2's UI must keep these two comparisons visually and textually separate, exactly as the research phases did.
- QAOA statistics exist with real 5/10-seed samples only at N=4 (8 qubits); N=5 is single-run; N≥6 untested (Phase 3) or timed out (Phase 4 diagnostics).
- No real D-Wave QPU was ever used — annealing is always classical-CPU simulated annealing.

## 10. Frontend Gaps

No `/optimization` page exists. `lib/api.ts` already has `createOptimization()`/`getOptimization()` (built in Phase 6, unused by any page). No route-visualization component. No scalability-chart component (no charting library is installed — Milestone 6's plan already flagged this as a deferred decision; Milestone 2 will use inline SVG for the specific, bounded charts this milestone needs rather than adding a dependency).

## 11. Backend Gaps (To Be Filled This Milestone)

1. `GET /optimization` — list runs (mirrors `GET /recommendations`).
2. `GET /optimize/instances/{name}` — real CVRPLIB coordinates/demands/capacity/depot + ground-truth BKS, for problem-context display and route visualization.
3. `_run_or_tools`/`_run_qubo_track` extended to include `coords`/`depot_coord`/`demands` in the `solution` dict, so a live-triggered run's route can be visualized without a second round-trip.
4. `GET /research/routing` — read-only exposure of `routing_results.json` + `routing_penalty_sensitivity.json` + the routing-relevant slice of Phase 4 data, for the pre-computed Comparison table and Scalability view (matches the existing `research_service.py` pattern exactly — read from disk, never recompute).

## 12. Plan

Backend: items 1-4 above, each a small, additive, real change (no duplicated business logic — routes stay thin, `qsci_core`/existing services remain the source of truth). Frontend: `/optimization` page per the milestone's suggested hierarchy, an SVG route-visualization component, an SVG scalability-chart component, a solver-comparison table component (reusing `Card`/`StatusPill`/design tokens from Milestones 0-1). Live-verify `/demand` and `/inventory` per Step 19 before declaring the milestone complete.

## 13. Implementation Verification (post-build)

All 4 backend gaps from §11 were filled as planned, plus one addition found necessary during implementation: `POST /optimize {method: "or_tools_qubo"}` (calls `qsci_core.optimization.quantum.classical_qubo_solver.solve_qubo_with_ortools`) — added because native `or_tools` solves a genuinely different, non-comparable problem per §9's fairness finding, so a fourth, classical-and-fair reference point was needed for the live 3-way QUBO-track comparison. Verified this reproduces Phase 3's exact recorded N=4 result: `test_optimize_or_tools_qubo_is_live_and_fair_reference` asserts `objective == pytest.approx(380.00755017228636, abs=1e-4)`.

**Backend tests**: `backend/tests/test_api.py`, 50/50 passed (`844.53s`), including 8 new Milestone 2 tests covering coords-in-solution, run listing (+ filter), real-CVRPLIB-instance endpoint, unknown-instance 404, and the `/research/routing` fairness-note payload.

**Browser-verified against the real backend** (port 8010) at 1440×900:
- Instance selector: switching A-n32-k5 → A-n37-k5 live-updates Customers (31→36) and Published BKS (784→669) from `GET /optimize/instances/{name}`.
- Live run, OR-Tools (on QUBO): cost 380.01, feasible, LIVE label, route rendered with real coordinates.
- Live run, Simulated Annealing: cost 380.01, feasible, RESEARCH label, "1000 reads" resource string — both runs agree with the pre-computed Phase 3 N=4 table.
- `GET /optimize/instances/NOT-REAL` → 404 with a clear message (error-state check).
- No console errors during any of the above.

**Mobile bug found and fixed during this verification**: `SolverComparisonTable`'s `<table className="w-full ...">` let the table compress to viewport width on narrow screens instead of triggering the wrapper's `overflow-x-auto`, clipping the QAOA column's text. Fixed by giving the table a `min-w-[560px]` floor so it overflows (and scrolls) instead of squeezing. Re-verified at a 516px-wide viewport (see Environment Note below) — both comparison tables now show a visible horizontal scrollbar with all columns fully legible.

**Environment note — mobile emulation floor**: neither `mcp__plugin_chrome-devtools-mcp_chrome-devtools__resize_page` nor `...emulate({viewport: "390x844..."})` could get `window.innerWidth` below 516px in this session, regardless of requested width (confirmed via repeated `evaluate_script` checks after fresh page loads). This is a tooling/environment ceiling, not a page bug — the true-390px method documented as working in Milestone 1 did not reproduce this session. All "mobile" testing in Milestone 2 was therefore done at the achievable ~516px floor (still well below the `lg` breakpoint, so sidebar-to-drawer and stacked-layout behavior is exercised), not true 390×844. Flagged honestly per §1 rather than reported as verified at 390px.

Step 19 live-verification: `/demand`'s three forecast buttons (Seasonal Naive, LightGBM, VQR) and `/inventory` were exercised against the real backend — see the Milestone 2 final report for results.
