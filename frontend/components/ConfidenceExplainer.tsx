import type { Recommendation } from "@/lib/api";
import { Card } from "./Card";

/** RQ5/H4: "confidence is a better reliability signal than accuracy
 * alone." Grounds the explanation in THIS recommendation's own real
 * decomposition (never a generic canned example) so the abstract claim is
 * tied to an actual number the reader can check against the WhyPanel
 * above it. */
export function ConfidenceExplainer({ rec }: { rec: Recommendation }) {
  const fs = rec.confidence_breakdown.forecast_stability;
  const fsAvailable = typeof fs === "number";
  const components = [
    { name: "data quality", value: rec.confidence_breakdown.data_quality, meaning: "how complete and clean the underlying M5 series is" },
    {
      name: "forecast stability",
      value: fsAvailable ? (fs as number) : null,
      meaning: "how tight the p10-p90 forecast spread is (a wide spread is a low-confidence forecast even if the median looks accurate)",
    },
    { name: "model consensus", value: rec.confidence_breakdown.model_consensus, meaning: "how much independent forecasters agree" },
    { name: "backtest performance", value: rec.confidence_breakdown.backtest_performance, meaning: "how the model actually scored on held-out data" },
  ];
  const spread = Math.max(...components.map((c) => c.value ?? 0)) - Math.min(...components.filter((c) => c.value !== null).map((c) => c.value as number));

  return (
    <Card>
      <h3 className="text-sm font-semibold text-muted">Why confidence is multi-factor</h3>
      <p className="mt-2 text-sm text-foreground/90">
        A single accuracy number (e.g. backtest wMAPE) can&rsquo;t tell you whether{" "}
        <em>this specific forecast</em> is reliable — a model can score well on average while still producing an
        unstable prediction for one series, on dirty data, or in disagreement with a second model. QSCI decomposes
        confidence into four independent signals rather than reporting accuracy alone:
      </p>
      <ul className="mt-2 space-y-1 text-sm">
        {components.map((c) => (
          <li key={c.name} className="text-foreground/90">
            <strong>{c.name}</strong> ({c.value !== null ? `${(c.value * 100).toFixed(0)}%` : "NOT AVAILABLE"}) —{" "}
            <span className="text-muted">{c.meaning}</span>
          </li>
        ))}
      </ul>
      {!fsAvailable && (
        <p className="mt-2 text-xs text-pending">
          This recommendation&rsquo;s forecast stability is NOT AVAILABLE — its model is a point forecaster with no native
          quantile output (documented Phase 5 finding). The overall confidence score below is computed from the
          remaining three components with forecast stability weighted to zero, not silently assigned a guessed value.
        </p>
      )}
      <p className="mt-2 text-sm text-foreground/90">
        For this recommendation, the four components span a{" "}
        <strong>{(spread * 100).toFixed(0)} percentage-point</strong> range — direct, real evidence that these
        signals do not move together, which is exactly why a single &ldquo;backtest performance&rdquo; number would be an
        incomplete reliability signal on its own.
      </p>
    </Card>
  );
}
