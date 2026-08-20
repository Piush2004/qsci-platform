import type { BaselineComparison, BaselineSide } from "@/lib/api";
import { StatusPill } from "./StatusPill";
import { Card } from "./Card";

function fmt(n: number | null, digits = 1) {
  if (n === null || n === undefined) return "N/A";
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

type MetricKey = "forecast_metric" | "operational_metric" | "financial_metric";

function Row({ label, baseline, decision }: { label: MetricKey; baseline: BaselineSide; decision: BaselineSide }) {
  const b = baseline[label];
  const d = decision[label];
  return (
    <tr className="border-b border-border/50">
      <td className="py-2 pr-4 text-muted">{b.name}</td>
      <td className="py-2 pr-4">
        {fmt(b.value)} {b.status && <StatusPill label={b.status} />}
      </td>
      <td className="py-2 pr-4">
        {fmt(d.value)} {d.status && <StatusPill label={d.status} />}
      </td>
    </tr>
  );
}

/** Step 3: baseline (seasonal-naive) vs. QSCI's actual decision, on the
 * identical series+horizon. Renders only what the backend computed --
 * PENDING is a legitimate, expected state when no baseline run exists yet. */
export function BaselineComparisonCard({ comparison }: { comparison: BaselineComparison | null }) {
  if (comparison === null) {
    return (
      <Card>
        <h3 className="text-sm font-semibold text-muted">Baseline vs. decision</h3>
        <p className="mt-2 text-sm text-muted">Loading…</p>
      </Card>
    );
  }

  if (comparison.status === "PENDING" || !comparison.baseline || !comparison.decision) {
    return (
      <Card>
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-muted">Baseline vs. decision</h3>
          <StatusPill label="PENDING" />
        </div>
        <p className="mt-2 text-sm text-muted">{comparison.note}</p>
      </Card>
    );
  }

  const { baseline, decision } = comparison;

  return (
    <Card className="overflow-x-auto">
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-semibold text-muted">Baseline vs. decision</h3>
        <StatusPill label="LIVE" />
      </div>
      <p className="mt-1 text-xs text-muted">{comparison.note}</p>
      <table className="mt-3 w-full min-w-[420px] text-sm">
        <thead>
          <tr className="border-b border-border text-left text-caption uppercase">
            <th className="py-2 pr-4">Metric</th>
            <th className="py-2 pr-4">{baseline.model} (baseline)</th>
            <th className="py-2 pr-4">{decision.model} (QSCI decision)</th>
          </tr>
        </thead>
        <tbody>
          <Row label="forecast_metric" baseline={baseline} decision={decision} />
          <Row label="operational_metric" baseline={baseline} decision={decision} />
          <Row label="financial_metric" baseline={baseline} decision={decision} />
        </tbody>
      </table>
    </Card>
  );
}
