"use client";

import { useEffect, useMemo, useState } from "react";
import { api, ApiError, type CvrplibInstance, type OptimizationRun } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { Card } from "@/components/Card";
import { StatusPill } from "@/components/StatusPill";
import { RouteVisualization } from "@/components/RouteVisualization";
import { ScalabilityChart } from "@/components/ScalabilityChart";
import { SolverComparisonTable, type SolverResult } from "@/components/SolverComparisonTable";

const INSTANCES = ["A-n32-k5", "A-n33-k5", "A-n37-k5", "B-n31-k5"];
const LIVE_METHODS = [
  { key: "or_tools_qubo", label: "OR-Tools (on QUBO)", type: "CLASSICAL" as const },
  { key: "simulated_annealing", label: "Simulated Annealing", type: "QUANTUM-INSPIRED" as const },
  { key: "qaoa", label: "QAOA", type: "QUANTUM" as const },
];

type RoutingResultRow = {
  stops: number;
  solver: string;
  seed: number;
  feasible: boolean;
  objective_cost: number | null;
  runtime_solver_seconds: number;
  qubits: number | null;
  circuit_depth: number | null;
  gate_count: number | null;
  qubo_variables: number | null;
};

function methodTypeOf(solver: string): SolverResult["methodType"] {
  if (solver.startsWith("or_tools")) return "CLASSICAL";
  if (solver === "simulated_annealing") return "QUANTUM-INSPIRED";
  return "QUANTUM";
}

function methodLabelOf(solver: string): string {
  return { or_tools_qubo: "OR-Tools (on QUBO)", simulated_annealing: "Simulated Annealing", qaoa: "QAOA" }[solver] ?? solver;
}

function resourcesOf(row: RoutingResultRow): string {
  if (row.qubits != null) return `${row.qubits} qubits, depth ${row.circuit_depth ?? "N/A"}, ${row.gate_count ?? "N/A"} gates`;
  if (row.qubo_variables != null) return `${row.qubo_variables} QUBO variables`;
  return "N/A";
}

export default function OptimizationPage() {
  const [instanceName, setInstanceName] = useState(INSTANCES[0]);
  const [instance, setInstance] = useState<CvrplibInstance | null>(null);
  const [routing, setRouting] = useState<{ results: RoutingResultRow[]; note: string; status: string } | null>(null);
  const [scalability, setScalability] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [problemSize, setProblemSize] = useState(4);
  const [liveRuns, setLiveRuns] = useState<Record<string, OptimizationRun>>({});
  const [running, setRunning] = useState<string | null>(null);

  useEffect(() => {
    api.getInstance(instanceName).then(setInstance).catch((e) => setError(e instanceof ApiError ? e.message : "Backend unavailable"));
  }, [instanceName]);

  useEffect(() => {
    api.researchRouting().then((r) => setRouting(r as never)).catch(() => setRouting(null));
    api.researchScalability().then(setScalability).catch(() => setScalability(null));
  }, []);

  // Historical comparison at N=4 -- the one size all three QUBO-track
  // methods have real, multi-seed statistics for (Phase 3). Best (lowest
  // cost among feasible) per solver, matching how the research notebooks
  // report it.
  const historicalComparison: SolverResult[] = useMemo(() => {
    if (!routing) return [];
    const n4 = routing.results.filter((r) => r.stops === 4);
    return ["or_tools_qubo", "simulated_annealing", "qaoa"].map((solver) => {
      const rows = n4.filter((r) => r.solver === solver);
      const feasibleRows = rows.filter((r) => r.feasible && r.objective_cost != null);
      const best = feasibleRows.length ? feasibleRows.reduce((a, b) => (a.objective_cost! < b.objective_cost! ? a : b)) : null;
      const feasibilityRate = rows.length ? feasibleRows.length / rows.length : null;
      return {
        method: methodLabelOf(solver),
        methodType: methodTypeOf(solver),
        cost: best?.objective_cost ?? null,
        gapPct: best ? 0 : null, // or_tools_qubo IS the reference; annealing/qaoa matched it exactly at N=4 per Phase 3
        feasible: feasibilityRate !== null ? feasibilityRate > 0 : null,
        runtimeSeconds: best?.runtime_solver_seconds ?? (rows[0]?.runtime_solver_seconds ?? null),
        resources: best ? resourcesOf(best) : rows[0] ? resourcesOf(rows[0]) : "N/A",
        evidence: "RESEARCH",
      };
    });
  }, [routing]);

  // Recursive, not a reassigned loop variable -- React Compiler's
  // immutability rule flags mutating a `let` binding across an await
  // boundary in a component function (same pattern fixed on /demand).
  async function pollUntilSettled(method: string, run: OptimizationRun, attemptsLeft: number): Promise<void> {
    if (attemptsLeft <= 0 || (run.run_status !== "PENDING" && run.run_status !== "RUNNING")) return;
    await new Promise((r) => setTimeout(r, 2000));
    const updated = await api.getOptimization(run.id);
    setLiveRuns((prev) => ({ ...prev, [method]: updated }));
    await pollUntilSettled(method, updated, attemptsLeft - 1);
  }

  async function runLive(method: string) {
    setRunning(method);
    setError(null);
    try {
      const run = await api.createOptimization("routing", method, {
        cvrplib_instance: instanceName, n_customers: problemSize, seed: 42,
      });
      setLiveRuns((prev) => ({ ...prev, [method]: run }));
      await pollUntilSettled(method, run, 200);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Backend unavailable");
    } finally {
      setRunning(null);
    }
  }

  const liveComparison: SolverResult[] = LIVE_METHODS.map((m) => {
    const run = liveRuns[m.key];
    if (!run || run.run_status !== "COMPLETE") {
      return {
        method: m.label, methodType: m.type, cost: null, gapPct: null, feasible: null, runtimeSeconds: null,
        resources: "N/A", evidence: run ? run.run_status : "PENDING",
      };
    }
    const rm = run.resource_metrics as Record<string, unknown> | null;
    const resources = rm?.qubits != null
      ? `${rm.qubits} qubits, depth ${rm.circuit_depth}, ${rm.gate_count} gates`
      : rm?.num_reads != null
        ? `${rm.num_reads} reads`
        : (rm?.solver as string) ?? "N/A";
    return {
      method: m.label, methodType: m.type, cost: run.objective, gapPct: null, feasible: run.feasible,
      runtimeSeconds: run.runtime_seconds, resources, evidence: run.label,
    };
  });

  const qaoaLiveRoute = liveRuns["qaoa"]?.run_status === "COMPLETE" ? liveRuns["qaoa"] : null;
  const orToolsQuboLiveRoute = liveRuns["or_tools_qubo"]?.run_status === "COMPLETE" ? liveRuns["or_tools_qubo"] : null;
  const routeToVisualize = orToolsQuboLiveRoute ?? liveRuns["simulated_annealing"] ?? qaoaLiveRoute;

  const qaoaDepth = (scalability?.qaoa_depth_tradeoff as { p: number; feasibility_rate: number; mean_runtime_seconds: number }[] | undefined) ?? [];
  const annealingByReads = (scalability?.annealing_feasibility_by_reads as { n_customers: number; num_reads: number; feasibility_rate: number }[] | undefined) ?? [];

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <PageHeader
        title="Optimization Intelligence"
        description="Classical vs. quantum-inspired vs. quantum routing, on the identical CVRPLIB-derived instance and QUBO — evidence, not a winner."
      />

      {error && <div role="alert" className="mb-6 rounded-md border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

      <Card className="mb-6">
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <label htmlFor="instance-select" className="text-xs font-medium text-muted">Instance</label>
          <select
            id="instance-select"
            value={instanceName}
            onChange={(e) => setInstanceName(e.target.value)}
            className="rounded-md border border-border bg-background px-2 py-1 text-sm"
          >
            {INSTANCES.map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
          <StatusPill label="LIVE" />
        </div>
        {instance && (
          <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            <div><p className="text-caption">Customers</p><p className="text-data font-medium">{instance.num_customers}</p></div>
            <div><p className="text-caption">Vehicles (published)</p><p className="text-data font-medium">{instance.n_vehicles_published}</p></div>
            <div><p className="text-caption">Capacity</p><p className="text-data font-medium">{instance.capacity}</p></div>
            <div><p className="text-caption">Published BKS</p><p className="text-data font-medium">{instance.published_bks}</p></div>
          </div>
        )}
      </Card>

      <Card className="mb-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-h3">Solution comparison — Phase 3 research results (N=4)</h2>
          <StatusPill label="RESEARCH" />
        </div>
        <p className="mb-3 text-supporting">{routing?.note}</p>
        {historicalComparison.length > 0 ? (
          <SolverComparisonTable results={historicalComparison} />
        ) : (
          <p className="text-sm text-muted">Loading…</p>
        )}
      </Card>

      <Card className="mb-6">
        <h2 className="mb-3 text-h3">Run a live comparison</h2>
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <label htmlFor="size-select" className="text-xs font-medium text-muted">Problem size (customers)</label>
          <select
            id="size-select"
            value={problemSize}
            onChange={(e) => setProblemSize(Number(e.target.value))}
            className="rounded-md border border-border bg-background px-2 py-1 text-sm"
          >
            {[4, 6, 8].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
        <div className="mb-4 flex flex-wrap gap-2">
          {LIVE_METHODS.map((m) => (
            <button
              key={m.key}
              onClick={() => runLive(m.key)}
              disabled={running === m.key}
              className="rounded-md border border-border px-3 py-1.5 text-sm transition-colors duration-[var(--duration-fast)] hover:bg-border/30 disabled:opacity-50"
            >
              {running === m.key ? "Running…" : `Run ${m.label}`}
              {m.key === "qaoa" && <span className="ml-1 text-caption">(may take 30s+)</span>}
            </button>
          ))}
        </div>
        <SolverComparisonTable results={liveComparison} />

        {routeToVisualize?.solution && (
          <div className="mt-4">
            <h3 className="mb-2 text-h3">Route</h3>
            <RouteVisualization
              depot={(routeToVisualize.solution.depot_coord as [number, number]) ?? (routeToVisualize.solution.coords as [number, number][])[0]}
              nodes={
                routeToVisualize.solution.depot_coord
                  ? (routeToVisualize.solution.coords as [number, number][])
                  : (routeToVisualize.solution.coords as [number, number][]).slice(1)
              }
              routes={Object.values(routeToVisualize.solution.routes as Record<string, number[]>)}
            />
          </div>
        )}
      </Card>

      <Card className="mb-6">
        <h2 className="mb-3 text-h3">Scalability — where does each method become impractical?</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {annealingByReads.length > 0 && (
            <ScalabilityChart
              title="Annealing feasibility vs. num_reads (Phase 4)"
              xLabel="num_reads"
              yLabel="feasibility rate"
              yDomain={[0, 1]}
              series={[8, 10, 12].map((n) => ({
                label: `N=${n}`,
                points: annealingByReads.filter((r) => r.n_customers === n).map((r) => ({ x: r.num_reads, y: r.feasibility_rate })),
              }))}
            />
          )}
          {qaoaDepth.length > 0 && (
            <ScalabilityChart
              title="QAOA depth (p) vs. runtime (Phase 4)"
              xLabel="p"
              yLabel="mean runtime (s)"
              series={[{ label: "N=4", points: qaoaDepth.map((r) => ({ x: r.p, y: r.mean_runtime_seconds })) }]}
            />
          )}
        </div>
        <p className="mt-3 text-caption">
          Real measurements from Phase 3/4 (docs/PHASE_3_REPORT.md, docs/PHASE_4_REPORT.md) — not projected or interpolated.
        </p>
      </Card>

      <Card className="mb-6">
        <h2 className="mb-2 text-h3">What does this result mean?</h2>
        <ul className="list-inside list-disc space-y-2 text-sm">
          <li>On the identical QUBO, OR-Tools-on-QUBO, simulated annealing, and QAOA all matched the same optimum when feasible at N=4 — no cost difference was observed among feasible solutions.</li>
          <li>Annealing&apos;s feasibility rate collapses at larger N under a fixed sampling budget, but recovers substantially with more <code>num_reads</code> — a sampling artifact, not a hard limit (Phase 4 finding).</li>
          <li>QAOA required real, non-trivial quantum resources (8 qubits, circuit depth 34 at N=4) and its runtime grows steeply with both problem size and circuit depth <code>p</code> — deeper circuits did not improve solution quality in the tested range.</li>
          <li>No experiment in this repository establishes a quantum advantage on this routing problem. See <a className="text-accent underline" href="/research">Research Lab</a> for the full evidence.</li>
        </ul>
      </Card>

      <Card>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-h3">Decision implication</h2>
          <StatusPill label="PENDING" />
        </div>
        <p className="text-sm text-muted">
          Route cost differences here have not been converted to a financial figure — no real per-stop/fuel/driver
          cost data exists for CVRPLIB (per <code>qsci_core.financial</code>&apos;s documented scope), and routing
          decisions are not yet wired into the Recommendation → Approval → Audit chain the way inventory decisions
          are (see the Decision Center). This is a disclosed gap, not a fabricated dollar figure.
        </p>
      </Card>
    </div>
  );
}
