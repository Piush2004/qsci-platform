"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type Recommendation } from "@/lib/api";
import { StatusPill } from "@/components/StatusPill";
import { PageHeader } from "@/components/PageHeader";
import { Card } from "@/components/Card";

export default function InventoryPage() {
  const [recs, setRecs] = useState<Recommendation[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listRecommendations()
      .then(setRecs)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Backend unavailable"));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <PageHeader
        title="Inventory"
        description="SKU-level reorder recommendations — forecast, safety stock, reorder point, and stockout risk from qsci_core."
      />

      {error && (
        <div className="mb-6 rounded-md border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
      )}

      {recs !== null && recs.length === 0 && (
        <p className="text-sm text-muted">
          No recommendations yet — generate one from the{" "}
          <a href="/dashboard" className="text-accent underline">
            Decision Center
          </a>
          .
        </p>
      )}

      {recs && recs.length > 0 && (
        <Card padded={false} className="motion-fade-in overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface text-left text-caption uppercase">
              <tr>
                <th className="px-3 py-2">SKU</th>
                <th className="px-3 py-2">Forecast (p50)</th>
                <th className="px-3 py-2">Reorder Point</th>
                <th className="px-3 py-2">Suggested Order</th>
                <th className="px-3 py-2">Stockout Risk</th>
                <th className="px-3 py-2">Confidence</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {recs.map((r) => (
                <tr key={r.id} className="border-t border-border transition-colors duration-[var(--duration-fast)] hover:bg-border/20">
                  <td className="px-3 py-2">
                    <a href="/dashboard" className="text-accent hover:underline">
                      {r.sku_id}
                    </a>
                  </td>
                  <td className="text-data px-3 py-2">{r.forecast_p50.toFixed(1)}</td>
                  <td className="text-data px-3 py-2">{r.reorder_point.toFixed(1)}</td>
                  <td className="text-data px-3 py-2">{r.suggested_order_qty.toFixed(1)}</td>
                  <td className="text-data px-3 py-2">
                    {(r.risk_probability * 100).toFixed(1)}% ({r.risk_level})
                  </td>
                  <td className="text-data px-3 py-2">{(r.confidence_overall * 100).toFixed(0)}%</td>
                  <td className="px-3 py-2">
                    <StatusPill label={r.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
