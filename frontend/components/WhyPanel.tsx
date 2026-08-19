import type { Recommendation } from "@/lib/api";
import { StatusPill } from "./StatusPill";
import { Card } from "./Card";

function fmt(n: number, digits = 1) {
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

/** Every field here comes directly from a real Recommendation returned by
 * the backend (qsci_core.recommendation.builder). Never invents a number,
 * never shows a bare confidence percentage without its decomposition. */
export function WhyPanel({ rec }: { rec: Recommendation }) {
  const fs = rec.confidence_breakdown.forecast_stability;
  const fsIsNumber = typeof fs === "number";

  return (
    <Card className="space-y-5">
      <div>
        <h3 className="text-sm font-semibold text-muted">Forecast evidence</h3>
        <p className="mt-1 text-sm">
          Median demand forecast is <strong>{fmt(rec.forecast_p50)}</strong> units
          (p10={fmt(rec.forecast_p10)}, p90={fmt(rec.forecast_p90)}) for SKU{" "}
          <code className="text-xs">{rec.sku_id}</code>.
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-muted">Risk evidence</h3>
        <p className="mt-1 text-sm">
          Estimated stockout risk is <strong>{(rec.risk_probability * 100).toFixed(1)}%</strong> (
          {rec.risk_level}), reorder point {fmt(rec.reorder_point)} units.
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-muted">Financial impact</h3>
        <div className="mt-1 flex items-center gap-2">
          <StatusPill label={(rec.financial_impact.status as string) ?? "ILLUSTRATIVE"} />
          <span className="text-sm">
            total cost ${fmt(rec.financial_impact.total_cost as number, 0)}/yr (holding + ordering + stockout, documented cost
            assumptions, not real per-unit data)
          </span>
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-muted">Confidence decomposition</h3>
        <div className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
          <ConfidenceCell label="Data quality" value={rec.confidence_breakdown.data_quality} />
          <ConfidenceCell
            label="Forecast stability"
            value={fsIsNumber ? (fs as number) : null}
            unavailableNote={fsIsNumber ? undefined : String(fs)}
          />
          <ConfidenceCell label="Model consensus" value={rec.confidence_breakdown.model_consensus} />
          <ConfidenceCell label="Backtest performance" value={rec.confidence_breakdown.backtest_performance} />
        </div>
        <p className="mt-2 text-sm">
          Overall confidence: <strong>{(rec.confidence_overall * 100).toFixed(1)}%</strong>{" "}
          <span className="text-xs text-muted">
            (weighted average of the four components above — never shown without this breakdown)
          </span>
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-muted">Rationale</h3>
        <p className="mt-1 text-sm text-foreground/90">{rec.rationale}</p>
      </div>
    </Card>
  );
}

function ConfidenceCell({
  label,
  value,
  unavailableNote,
}: {
  label: string;
  value: number | null;
  unavailableNote?: string;
}) {
  return (
    <div className="rounded-md border border-border bg-background/40 p-2">
      <p className="text-xs text-muted">{label}</p>
      {value === null ? (
        <p className="mt-1 text-xs font-medium text-pending" title={unavailableNote}>
          NOT AVAILABLE
        </p>
      ) : (
        <p className="mt-1 text-sm font-semibold">{(value * 100).toFixed(0)}%</p>
      )}
    </div>
  );
}
