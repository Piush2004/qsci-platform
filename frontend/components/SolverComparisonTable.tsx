import { StatusPill } from "./StatusPill";

export interface SolverResult {
  method: string;
  methodType: "CLASSICAL" | "QUANTUM-INSPIRED" | "QUANTUM";
  cost: number | null;
  gapPct: number | null;
  feasible: boolean | null;
  runtimeSeconds: number | null;
  resources: string; // e.g. "8 qubits, depth 34" or "1000 reads" or "CP-SAT"
  evidence: string; // LIVE | RESEARCH | ILLUSTRATIVE | PENDING
}

const TYPE_COLOR: Record<SolverResult["methodType"], string> = {
  CLASSICAL: "text-live",
  "QUANTUM-INSPIRED": "text-accent",
  QUANTUM: "text-research",
};

/** Every solver in this table must have solved the identical instance,
 * same constraints, same objective (Milestone 2's "fair comparison"
 * requirement) -- enforced by the caller passing results from a single
 * shared QUBOInstance/CVRPLIB instance, not by this component. No
 * "quantum winner" badge is ever rendered here. */
export function SolverComparisonTable({ results }: { results: SolverResult[] }) {
  const rows: { label: string; render: (r: SolverResult) => React.ReactNode }[] = [
    { label: "Cost", render: (r) => (r.cost !== null ? <span className="text-data">{r.cost.toFixed(2)}</span> : "N/A") },
    { label: "Optimality gap", render: (r) => (r.gapPct !== null ? <span className="text-data">{r.gapPct.toFixed(2)}%</span> : "N/A") },
    {
      label: "Feasible",
      render: (r) =>
        r.feasible === null ? "N/A" : (
          <span className={r.feasible ? "text-live" : "text-danger"}>{r.feasible ? "Yes" : "No"}</span>
        ),
    },
    { label: "Runtime", render: (r) => (r.runtimeSeconds !== null ? <span className="text-data">{r.runtimeSeconds.toFixed(3)}s</span> : "N/A") },
    { label: "Resources", render: (r) => <span className="text-xs">{r.resources}</span> },
    { label: "Evidence", render: (r) => <StatusPill label={r.evidence} /> },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[560px] text-sm">
        <thead>
          <tr className="border-b border-border text-left">
            <th className="py-2 pr-4 text-caption uppercase">Metric</th>
            {results.map((r) => (
              <th key={r.method} className="py-2 pr-4">
                <div className="font-medium">{r.method}</div>
                <div className={`text-caption ${TYPE_COLOR[r.methodType]}`}>{r.methodType}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-b border-border/50">
              <td className="py-2 pr-4 text-muted">{row.label}</td>
              {results.map((r) => (
                <td key={r.method} className="py-2 pr-4">
                  {row.render(r)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
