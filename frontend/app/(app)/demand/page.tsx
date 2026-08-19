"use client";

import { useState } from "react";
import { api, ApiError, type ForecastRun } from "@/lib/api";
import { StatusPill } from "@/components/StatusPill";

const MODELS = [
  { key: "seasonal_naive", label: "Seasonal Naive", note: "LIVE baseline — the honesty check on every claim" },
  { key: "lightgbm", label: "LightGBM", note: "LIVE — p10/p50/p90 quantile forecaster" },
  { key: "vqr", label: "VQR (Quantum)", note: "RESEARCH — point forecaster, ~1-5 min to train" },
];

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between border-t border-border/60 pt-1">
      <span className="text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

export default function DemandPage() {
  const [runs, setRuns] = useState<Record<string, ForecastRun>>({});
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runForecast(modelKey: string) {
    setLoading(modelKey);
    setError(null);
    try {
      let fc = await api.createForecast(modelKey);
      setRuns((prev) => ({ ...prev, [modelKey]: fc }));
      for (let i = 0; i < 150 && (fc.run_status === "PENDING" || fc.run_status === "RUNNING"); i++) {
        await new Promise((r) => setTimeout(r, 2000));
        fc = await api.getForecast(fc.id);
        setRuns((prev) => ({ ...prev, [modelKey]: fc }));
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Backend unavailable");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Demand</h1>
        <p className="text-sm text-muted">
          Compare Seasonal Naive, LightGBM, and VQR on the identical series and test window (M5, FOODS_3_090_CA_1).
        </p>
      </header>

      {error && (
        <div className="mb-6 rounded-md border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {MODELS.map((m) => {
          const run = runs[m.key];
          return (
            <div key={m.key} className="rounded-lg border border-border bg-surface p-4">
              <div className="mb-2 flex items-center justify-between">
                <h2 className="text-sm font-semibold">{m.label}</h2>
                {run && <StatusPill label={run.label} />}
              </div>
              <p className="mb-3 text-xs text-muted">{m.note}</p>
              <button
                onClick={() => runForecast(m.key)}
                disabled={loading === m.key}
                className="mb-3 w-full rounded-md border border-border px-3 py-1.5 text-sm hover:bg-border/30 disabled:opacity-50"
              >
                {loading === m.key ? "Running…" : run ? "Re-run" : "Run forecast"}
              </button>

              {run && (
                <div className="space-y-2 text-sm">
                  <p className="text-xs text-muted">Status: {run.run_status}</p>
                  {run.run_status === "COMPLETE" && run.metrics && (
                    <>
                      <Metric label="wMAPE" value={`${run.metrics.wmape?.toFixed(2)}%`} />
                      <Metric label="RMSE" value={run.metrics.rmse?.toFixed(2)} />
                      <Metric label="Bias" value={run.metrics.bias?.toFixed(2)} />
                      <Metric label="Runtime" value={`${run.runtime_seconds?.toFixed(3)}s`} />
                      {run.model_metadata?.forecast_stability !== undefined && (
                        <Metric label="Forecast stability" value={String(run.model_metadata.forecast_stability)} />
                      )}
                    </>
                  )}
                  {run.run_status === "FAILED" && <p className="text-xs text-danger">{run.error}</p>}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
