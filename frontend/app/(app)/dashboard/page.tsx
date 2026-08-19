"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type AuditEvent, type Recommendation } from "@/lib/api";
import { DecisionChain } from "@/components/DecisionChain";
import { WhyPanel } from "@/components/WhyPanel";
import { StatusPill } from "@/components/StatusPill";

export default function DashboardPage() {
  const [recs, setRecs] = useState<Recommendation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [generating, setGenerating] = useState(false);
  const [actionApprover, setActionApprover] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await api.listRecommendations();
      setRecs(data);
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? `Backend error: ${e.message}` : "Backend unavailable");
      setRecs(null);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (selectedId == null) return;
    api.audit(selectedId).then(setAuditEvents).catch(() => setAuditEvents([]));
  }, [selectedId]);

  const selected = recs?.find((r) => r.id === selectedId) ?? null;
  const pending = recs?.filter((r) => r.status === "PENDING") ?? [];

  async function generateNew() {
    setGenerating(true);
    try {
      const fc = await api.createForecast("lightgbm");
      const rec = await api.createRecommendation(fc.id);
      await load();
      setSelectedId(rec.id);
    } catch (e) {
      setError(e instanceof ApiError ? `Could not generate recommendation: ${e.message}` : "Backend unavailable");
    } finally {
      setGenerating(false);
    }
  }

  async function decide(action: "approve" | "reject") {
    if (!selected || !actionApprover.trim()) return;
    try {
      if (action === "approve") await api.approve(selected.id, actionApprover);
      else await api.reject(selected.id, actionApprover);
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Backend unavailable");
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Decision Center</h1>
          <p className="text-sm text-muted">What requires your attention — not a KPI wall.</p>
        </div>
        <button
          onClick={generateNew}
          disabled={generating}
          className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-black disabled:opacity-50"
        >
          {generating ? "Generating…" : "Generate recommendation (LightGBM)"}
        </button>
      </header>

      {error && (
        <div className="mb-6 rounded-md border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">
          {error} — is the backend running (`uvicorn app.main:app` in `backend/`)?
        </div>
      )}

      {recs === null && !error && <p className="text-sm text-muted">Loading…</p>}

      {recs !== null && recs.length === 0 && (
        <p className="text-sm text-muted">No recommendations yet. Generate one to see the Golden Path in action.</p>
      )}

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <div className="space-y-2">
          <h2 className="text-xs font-medium uppercase tracking-wider text-muted">
            Pending decisions ({pending.length})
          </h2>
          {recs?.map((r) => (
            <button
              key={r.id}
              onClick={() => setSelectedId(r.id)}
              className={`block w-full rounded-md border px-3 py-2 text-left text-sm ${
                selectedId === r.id ? "border-accent bg-accent/10" : "border-border hover:bg-border/30"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{r.sku_id}</span>
                <StatusPill label={r.status} />
              </div>
              <p className="mt-1 text-xs text-muted">
                Order {r.suggested_order_qty.toFixed(0)} units · confidence {(r.confidence_overall * 100).toFixed(0)}%
              </p>
            </button>
          ))}
        </div>

        <div className="space-y-4">
          {selected ? (
            <>
              <DecisionChain rec={selected} auditEvents={auditEvents} />
              <WhyPanel rec={selected} />
              {selected.status === "PENDING" && (
                <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-4">
                  <input
                    value={actionApprover}
                    onChange={(e) => setActionApprover(e.target.value)}
                    placeholder="Your name (approver — no auth system yet, see docs)"
                    className="flex-1 rounded-md border border-border bg-background px-3 py-1.5 text-sm"
                  />
                  <button
                    onClick={() => decide("approve")}
                    disabled={!actionApprover.trim()}
                    className="rounded-md bg-live/20 px-3 py-1.5 text-sm font-medium text-live disabled:opacity-40"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => decide("reject")}
                    disabled={!actionApprover.trim()}
                    className="rounded-md bg-danger/20 px-3 py-1.5 text-sm font-medium text-danger disabled:opacity-40"
                  >
                    Reject
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="text-sm text-muted">Select a recommendation to inspect its evidence chain.</p>
          )}
        </div>
      </div>
    </div>
  );
}
