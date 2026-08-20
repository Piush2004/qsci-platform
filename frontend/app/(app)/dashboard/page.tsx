"use client";

import { useCallback, useEffect, useState } from "react";
import {
  api, ApiError, type AuditEvent, type BaselineComparison, type OutcomeResult, type Recommendation,
} from "@/lib/api";
import { DecisionChain } from "@/components/DecisionChain";
import { WhyPanel } from "@/components/WhyPanel";
import { PageHeader } from "@/components/PageHeader";
import { Card } from "@/components/Card";
import { ModifyPanel } from "@/components/ModifyPanel";
import { DecisionCard } from "@/components/DecisionCard";
import { OutcomeSection } from "@/components/OutcomeSection";
import { BaselineComparisonCard } from "@/components/BaselineComparisonCard";
import { ConfidenceExplainer } from "@/components/ConfidenceExplainer";
import { RiskExplainer } from "@/components/RiskExplainer";

export default function DashboardPage() {
  const [recs, setRecs] = useState<Recommendation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [outcome, setOutcome] = useState<OutcomeResult | null>(null);
  const [baseline, setBaseline] = useState<BaselineComparison | null>(null);
  const [generating, setGenerating] = useState(false);
  const [actionApprover, setActionApprover] = useState("");
  const [actionBusy, setActionBusy] = useState(false);
  const [modifyOpen, setModifyOpen] = useState(false);
  // Reset the modify panel when the selected recommendation changes --
  // done during render (React's documented pattern for "adjust state when
  // a prop changes"), not in an effect, to avoid a cascading-render lint
  // violation from calling setState synchronously inside useEffect.
  const [modifyOpenForId, setModifyOpenForId] = useState<number | null>(null);
  if (selectedId !== modifyOpenForId) {
    setModifyOpenForId(selectedId);
    setModifyOpen(false);
  }

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

  const refreshAudit = useCallback(async (id: number) => {
    try {
      setAuditEvents(await api.audit(id));
    } catch {
      setAuditEvents([]);
    }
  }, []);

  const refreshOutcome = useCallback(async (id: number) => {
    try {
      setOutcome(await api.getOutcome(id));
    } catch {
      setOutcome(null);
    }
  }, []);

  useEffect(() => {
    api
      .listRecommendations()
      .then((data) => {
        setRecs(data);
        setError(null);
      })
      .catch((e) => {
        setError(e instanceof ApiError ? `Backend error: ${e.message}` : "Backend unavailable");
        setRecs(null);
      });
  }, []);

  useEffect(() => {
    if (selectedId == null) return;
    api
      .audit(selectedId)
      .then(setAuditEvents)
      .catch(() => setAuditEvents([]));
    api
      .getOutcome(selectedId)
      .then(setOutcome)
      .catch(() => setOutcome(null));
    api
      .getBaseline(selectedId)
      .then(setBaseline)
      .catch(() => setBaseline(null));
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
    if (!selected || !actionApprover.trim() || actionBusy) return;
    setActionBusy(true);
    setError(null);
    try {
      if (action === "approve") await api.approve(selected.id, actionApprover);
      else await api.reject(selected.id, actionApprover);
      // The backend, not this optimistic client state, is the source of
      // truth for the new status -- refetch both the recommendation list
      // and this recommendation's audit trail (a real, found-via-manual-
      // testing bug: the audit panel previously went stale after
      // approve/reject because only `selectedId` changes triggered a
      // refetch, and it doesn't change here).
      await Promise.all([load(), refreshAudit(selected.id), refreshOutcome(selected.id)]);
    } catch (e) {
      // A 409 here is the backend's real invalid-state-transition guard
      // (e.g. double-approval) -- its message is shown verbatim, not
      // swallowed or replaced with a generic string.
      setError(e instanceof ApiError ? e.message : "Backend unavailable");
    } finally {
      setActionBusy(false);
    }
  }

  async function submitModify(qty: number, reason: string) {
    if (!selected || !actionApprover.trim() || actionBusy) return;
    setActionBusy(true);
    setError(null);
    try {
      await api.modify(selected.id, actionApprover, qty, reason);
      await Promise.all([load(), refreshAudit(selected.id), refreshOutcome(selected.id)]);
      setModifyOpen(false);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Backend unavailable");
    } finally {
      setActionBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <PageHeader
        title="Decision Center"
        description="What requires your attention — not a KPI wall."
        action={
          <button
            onClick={generateNew}
            disabled={generating}
            className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-black transition-opacity duration-[var(--duration-fast)] disabled:opacity-50"
          >
            {generating ? "Generating…" : "Generate recommendation (LightGBM)"}
          </button>
        }
      />

      {error && (
        <div role="alert" className="mb-6 rounded-md border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {recs === null && !error && <p className="text-sm text-muted">Loading…</p>}

      {recs !== null && recs.length === 0 && (
        <Card className="text-center">
          <p className="text-h3">No active decisions</p>
          <p className="mt-1 text-supporting">Generate a recommendation to begin.</p>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[320px_1fr]">
        <div className="space-y-2">
          <h2 className="text-caption uppercase">Decisions requiring attention ({pending.length} pending)</h2>
          {recs?.map((r) => (
            <DecisionCard key={r.id} rec={r} selected={selectedId === r.id} onClick={() => setSelectedId(r.id)} />
          ))}
        </div>

        <div className="motion-fade-in space-y-4" key={selected?.id ?? "none"}>
          {selected ? (
            <>
              <h2 className="text-caption uppercase text-muted">Why this decision</h2>
              <DecisionChain rec={selected} auditEvents={auditEvents} outcome={outcome} />
              <WhyPanel rec={selected} />

              <h2 className="text-caption uppercase text-muted">Business impact</h2>
              <BaselineComparisonCard comparison={baseline} />

              <h2 className="text-caption uppercase text-muted">Confidence</h2>
              <ConfidenceExplainer rec={selected} />
              <RiskExplainer rec={selected} />

              <h2 className="text-caption uppercase text-muted">Human decision</h2>
              {selected.status === "PENDING" && !modifyOpen && (
                <Card className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <label htmlFor="approver-name" className="sr-only">
                    Your name (approver)
                  </label>
                  <input
                    id="approver-name"
                    value={actionApprover}
                    onChange={(e) => setActionApprover(e.target.value)}
                    placeholder="Your name (approver — no auth system yet, see docs)"
                    className="min-w-0 rounded-md border border-border bg-background px-3 py-1.5 text-sm sm:flex-1"
                  />
                  <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => decide("approve")}
                    disabled={!actionApprover.trim() || actionBusy}
                    className="rounded-md bg-live/20 px-3 py-1.5 text-sm font-medium text-live transition-opacity duration-[var(--duration-fast)] disabled:opacity-40"
                  >
                    {actionBusy ? "Working…" : "Approve"}
                  </button>
                  <button
                    onClick={() => setModifyOpen(true)}
                    disabled={!actionApprover.trim() || actionBusy}
                    className="rounded-md bg-accent/20 px-3 py-1.5 text-sm font-medium text-accent transition-opacity duration-[var(--duration-fast)] disabled:opacity-40"
                  >
                    Modify
                  </button>
                  <button
                    onClick={() => decide("reject")}
                    disabled={!actionApprover.trim() || actionBusy}
                    className="rounded-md bg-danger/20 px-3 py-1.5 text-sm font-medium text-danger transition-opacity duration-[var(--duration-fast)] disabled:opacity-40"
                  >
                    {actionBusy ? "Working…" : "Reject"}
                  </button>
                  </div>
                </Card>
              )}

              {selected.status === "PENDING" && modifyOpen && (
                <ModifyPanel
                  currentQty={selected.suggested_order_qty}
                  approver={actionApprover}
                  submitting={actionBusy}
                  onCancel={() => setModifyOpen(false)}
                  onSubmit={submitModify}
                />
              )}

              <h2 className="text-caption uppercase text-muted">Outcome</h2>
              <OutcomeSection outcome={outcome} />
            </>
          ) : (
            <p className="text-sm text-muted">Select a recommendation to inspect its evidence chain.</p>
          )}
        </div>
      </div>
    </div>
  );
}
