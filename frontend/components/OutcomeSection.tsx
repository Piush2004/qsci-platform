import type { OutcomeResult } from "@/lib/api";
import { StatusPill } from "./StatusPill";
import { Card } from "./Card";

function fmt(n: number, digits = 1) {
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

/** Predicted vs. actual demand -- RQ2/H2's "does better accuracy guarantee
 * better outcomes" foundation. Renders exactly what the backend returned;
 * never fabricates an actual when the backend says PENDING. */
export function OutcomeSection({ outcome }: { outcome: OutcomeResult | null }) {
  if (outcome === null) {
    return (
      <Card>
        <h3 className="text-sm font-semibold text-muted">Outcome</h3>
        <p className="mt-2 text-sm text-muted">Loading…</p>
      </Card>
    );
  }

  if (outcome.status === "PENDING") {
    return (
      <Card>
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-muted">Outcome</h3>
          <StatusPill label="PENDING" />
        </div>
        <p className="mt-2 text-sm text-muted">{outcome.note}</p>
      </Card>
    );
  }

  const predicted = outcome.predicted_demand;
  const actual = outcome.kind === "manual" ? outcome.actual_demand_observed : outcome.actual_demand;
  const error = outcome.error;

  return (
    <Card>
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-semibold text-muted">Outcome</h3>
        <StatusPill label="LIVE" />
      </div>
      <p className="mt-1 text-xs text-muted">{outcome.note}</p>
      {predicted !== undefined && actual !== undefined && actual !== null && (
        <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
          <div>
            <p className="text-xs text-muted">Predicted demand</p>
            <p className="text-data font-medium">{fmt(predicted)}</p>
          </div>
          <div>
            <p className="text-xs text-muted">Actual demand</p>
            <p className="text-data font-medium">{fmt(actual)}</p>
          </div>
          <div>
            <p className="text-xs text-muted">Error</p>
            <p className={`text-data font-medium ${error !== null && error !== undefined && error < 0 ? "text-danger" : "text-live"}`}>
              {error !== null && error !== undefined ? (error >= 0 ? "+" : "") + fmt(error) : "N/A"}
              {outcome.pct_error != null && <span className="ml-1 text-xs text-muted">({fmt(outcome.pct_error)}%)</span>}
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}
