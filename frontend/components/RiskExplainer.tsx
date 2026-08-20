import type { Recommendation } from "@/lib/api";
import { Card } from "./Card";

function fmt(n: number, digits = 1) {
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

const LEVEL_COLOR: Record<string, string> = { LOW: "text-live", MEDIUM: "text-illustrative", HIGH: "text-danger" };

/** Step 7: never a bare "High Risk" pill -- always the driver behind it,
 * built from this recommendation's own real fields (forecast spread vs.
 * reorder point), not a canned sentence. */
export function RiskExplainer({ rec }: { rec: Recommendation }) {
  const spread = rec.forecast_p90 - rec.forecast_p10;
  const gap = rec.reorder_point - rec.forecast_p50;

  return (
    <Card>
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-semibold text-muted">Risk intelligence</h3>
        <span className={`text-sm font-semibold ${LEVEL_COLOR[rec.risk_level] ?? ""}`}>{rec.risk_level}</span>
      </div>
      <dl className="mt-2 space-y-1.5 text-sm">
        <div className="flex justify-between gap-2">
          <dt className="text-muted">Affected SKU</dt>
          <dd className="text-data">{rec.sku_id}</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt className="text-muted">Constraint</dt>
          <dd className="text-data">reorder point {fmt(rec.reorder_point)} units</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt className="text-muted">Forecast spread (p10-p90)</dt>
          <dd className="text-data">{fmt(spread)} units</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt className="text-muted">Gap to reorder point</dt>
          <dd className="text-data">{gap >= 0 ? "+" : ""}{fmt(gap)} units vs. median forecast</dd>
        </div>
      </dl>
      <p className="mt-2 text-sm text-foreground/90">
        Estimated stockout probability is <strong>{(rec.risk_probability * 100).toFixed(1)}%</strong>, computed by
        fitting a normal approximation to the p10-p90 forecast spread and evaluating P(demand &gt; reorder point).
        This forecast is {rec.risk_level.toLowerCase()} risk because {rec.risk_level === "HIGH"
          ? "the reorder point sits close to (or below) the upper end of the forecast spread — a plausible demand outcome would exceed it."
          : rec.risk_level === "MEDIUM"
            ? "the reorder point has some but not generous headroom above the median forecast, given the spread."
            : "the reorder point sits comfortably above the median forecast relative to the spread."}
      </p>
    </Card>
  );
}
