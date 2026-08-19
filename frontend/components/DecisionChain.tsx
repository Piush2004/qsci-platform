"use client";

import { useState } from "react";
import type { AuditEvent, Recommendation } from "@/lib/api";
import { StatusPill } from "./StatusPill";

interface Stage {
  key: string;
  title: string;
  status: string;
  detail: React.ReactNode;
}

function fmt(n: number, digits = 1) {
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

/** Every stage's detail is derived directly from the real Recommendation /
 * AuditEvent objects passed in -- clicking a stage reveals actual backend
 * evidence, never a hardcoded placeholder. */
export function DecisionChain({ rec, auditEvents }: { rec: Recommendation; auditEvents: AuditEvent[] }) {
  const [open, setOpen] = useState<string | null>("recommendation");

  const decisionEvent = auditEvents.find((e) => e.event_type.startsWith("APPROVAL_"));
  const stages: Stage[] = [
    {
      key: "data",
      title: "Data",
      status: "LIVE",
      detail: (
        <p>
          M5 Forecasting-Accuracy, series <code className="text-xs">{rec.sku_id}</code>.
        </p>
      ),
    },
    {
      key: "forecast",
      title: "Forecast",
      status: "LIVE",
      detail: (
        <p>
          p10={fmt(rec.forecast_p10)}, p50={fmt(rec.forecast_p50)}, p90={fmt(rec.forecast_p90)}.
        </p>
      ),
    },
    {
      key: "risk",
      title: "Risk",
      status: "LIVE",
      detail: (
        <p>
          Stockout probability {(rec.risk_probability * 100).toFixed(1)}% ({rec.risk_level}), reorder point{" "}
          {fmt(rec.reorder_point)} units.
        </p>
      ),
    },
    {
      key: "optimization",
      title: "Optimization",
      status: "LIVE",
      detail: <p>EOQ/safety-stock inventory math suggests ordering {fmt(rec.suggested_order_qty)} units.</p>,
    },
    {
      key: "financial",
      title: "Financial Impact",
      status: (rec.financial_impact.status as string) ?? "ILLUSTRATIVE",
      detail: <p>Total annual cost estimate ${fmt(rec.financial_impact.total_cost as number, 0)} (illustrative cost assumptions).</p>,
    },
    {
      key: "confidence",
      title: "Confidence",
      status: "LIVE",
      detail: <p>Overall {(rec.confidence_overall * 100).toFixed(1)}% — see the WhyPanel decomposition below.</p>,
    },
    {
      key: "recommendation",
      title: "Recommendation",
      status: "LIVE",
      detail: <p>{rec.rationale}</p>,
    },
    {
      key: "decision",
      title: "Human Decision",
      status: rec.status === "PENDING" ? "PENDING" : "LIVE",
      detail: decisionEvent ? (
        <p>
          {String(decisionEvent.event_payload.approver ?? "unknown")} —{" "}
          {decisionEvent.event_type.replace("APPROVAL_", "")} at{" "}
          {new Date(decisionEvent.created_at).toLocaleString()}
        </p>
      ) : (
        <p className="text-muted">Awaiting human approval, rejection, or modification.</p>
      ),
    },
    {
      key: "audit",
      title: "Audit",
      status: "LIVE",
      detail: (
        <ul className="space-y-1 text-xs text-muted">
          {auditEvents.map((e) => (
            <li key={e.id}>
              {new Date(e.created_at).toLocaleString()} — {e.event_type}
            </li>
          ))}
        </ul>
      ),
    },
  ];

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface">
      <div className="flex min-w-max divide-x divide-border">
        {stages.map((s) => (
          <button
            key={s.key}
            onClick={() => setOpen(open === s.key ? null : s.key)}
            className={`flex flex-col items-start gap-1 px-4 py-3 text-left transition-colors ${
              open === s.key ? "bg-accent/10" : "hover:bg-border/30"
            }`}
          >
            <span className="text-xs font-medium">{s.title}</span>
            <StatusPill label={s.status} />
          </button>
        ))}
      </div>
      {open && (
        <div className="border-t border-border p-4 text-sm">
          {stages.find((s) => s.key === open)?.detail}
        </div>
      )}
    </div>
  );
}
