import type { Recommendation } from "@/lib/api";
import { StatusPill } from "./StatusPill";

function fmt(n: number, digits = 0) {
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

const RISK_COLOR: Record<string, string> = {
  LOW: "text-live",
  MEDIUM: "text-illustrative",
  HIGH: "text-danger",
};

/** Compact per-recommendation summary for the Decision Center's list --
 * every value comes straight off the real Recommendation the backend
 * returned. No "winner" framing, no invented number. */
export function DecisionCard({
  rec,
  selected,
  onClick,
}: {
  rec: Recommendation;
  selected: boolean;
  onClick: () => void;
}) {
  const impact = rec.financial_impact.total_cost as number | undefined;
  const impactStatus = (rec.financial_impact.status as string) ?? "ILLUSTRATIVE";

  return (
    <button
      onClick={onClick}
      className={`block w-full rounded-md border px-3 py-2.5 text-left text-sm transition-colors duration-[var(--duration-fast)] ${
        selected ? "border-accent bg-accent/10" : "border-border hover:bg-border/30"
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium">{rec.sku_id}</span>
        <StatusPill label={rec.status} />
      </div>
      <p className="mt-1 text-xs text-muted">
        Forecast <strong className="text-foreground">{fmt(rec.forecast_p50)}</strong> · Order{" "}
        <strong className="text-foreground">{fmt(rec.suggested_order_qty)}</strong> units
      </p>
      <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
        <span className={RISK_COLOR[rec.risk_level] ?? "text-muted"}>Risk {rec.risk_level}</span>
        <span className="text-muted">Confidence {(rec.confidence_overall * 100).toFixed(0)}%</span>
        {impact !== undefined && (
          <span className="flex items-center gap-1 text-muted">
            Impact ${fmt(impact)}
            <StatusPill label={impactStatus} />
          </span>
        )}
      </div>
    </button>
  );
}
