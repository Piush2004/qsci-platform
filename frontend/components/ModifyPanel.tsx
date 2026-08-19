"use client";

import { useState } from "react";
import { Card } from "./Card";

const MAX_REASON_LENGTH = 500;

interface ModifyPanelProps {
  currentQty: number;
  approver: string;
  submitting: boolean;
  onCancel: () => void;
  onSubmit: (qty: number, reason: string) => void;
}

/** The complete MODIFY workflow: quantity + mandatory reason, both
 * validated client-side before the request is even sent (the backend
 * validates independently too -- see backend/app/schemas/schemas.py's
 * ApprovalActionRequest -- this is a UX improvement, not the only
 * defense). The backend remains the source of truth: submitting does not
 * optimistically change any displayed status, it only fires the real
 * request and lets the caller refetch confirmed state. */
function fmt(n: number) {
  return n.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

export function ModifyPanel({ currentQty, approver, submitting, onCancel, onSubmit }: ModifyPanelProps) {
  // Round the prefilled value for display/editing -- the backend's raw
  // computed quantity carries full floating-point precision
  // (152.99897648241702), which is real but not human-meaningful at that
  // resolution; found via manual testing, not by a unit test.
  const [qtyInput, setQtyInput] = useState(() => (Math.round(currentQty * 10) / 10).toString());
  const [reason, setReason] = useState("");
  const [touched, setTouched] = useState(false);

  const qty = Number(qtyInput);
  const qtyError = !qtyInput.trim()
    ? "Quantity is required."
    : !Number.isFinite(qty)
      ? "Quantity must be a finite number."
      : qty < 0
        ? "Quantity cannot be negative."
        : qty > 1_000_000
          ? "Quantity looks implausibly large — double-check before submitting."
          : null;

  const trimmedReason = reason.trim();
  const reasonError = !trimmedReason
    ? "A reason is required for every modification."
    : trimmedReason.length > MAX_REASON_LENGTH
      ? `Reason must be ${MAX_REASON_LENGTH} characters or fewer (currently ${trimmedReason.length}).`
      : null;

  const canSubmit = !qtyError && !reasonError && !submitting;

  return (
    <Card className="motion-fade-in space-y-4">
      <div>
        <h3 className="text-h3">Modify recommendation</h3>
        <p className="text-supporting">
          System-suggested quantity was <strong className="text-data">{fmt(currentQty)}</strong> units. The backend
          records this change and the reason in the audit trail — it is never a local-only edit.
        </p>
      </div>

      <div>
        <label htmlFor="modify-qty" className="mb-1 block text-xs font-medium text-muted">
          New quantity
        </label>
        <input
          id="modify-qty"
          type="number"
          min={0}
          step="any"
          inputMode="decimal"
          value={qtyInput}
          onChange={(e) => setQtyInput(e.target.value)}
          onBlur={() => setTouched(true)}
          aria-invalid={touched && !!qtyError}
          aria-describedby="modify-qty-error"
          className="w-40 rounded-md border border-border bg-background px-3 py-1.5 text-sm"
        />
        {touched && qtyError && (
          <p id="modify-qty-error" role="alert" className="mt-1 text-xs text-danger">
            {qtyError}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="modify-reason" className="mb-1 block text-xs font-medium text-muted">
          Reason (required)
        </label>
        <textarea
          id="modify-reason"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          onBlur={() => setTouched(true)}
          rows={2}
          maxLength={MAX_REASON_LENGTH + 100}
          aria-invalid={touched && !!reasonError}
          aria-describedby="modify-reason-error"
          placeholder="e.g. Adjusted for a known upcoming promotion not reflected in the forecast"
          className="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm"
        />
        <div className="mt-1 flex items-center justify-between">
          {touched && reasonError ? (
            <p id="modify-reason-error" role="alert" className="text-xs text-danger">
              {reasonError}
            </p>
          ) : (
            <span />
          )}
          <span className="text-xs text-muted">
            {trimmedReason.length}/{MAX_REASON_LENGTH}
          </span>
        </div>
      </div>

      {trimmedReason && !reasonError && !qtyError && (
        <div className="rounded-md border border-border bg-background/40 p-3 text-xs text-muted">
          Review: change order quantity from <strong className="text-data text-foreground">{fmt(currentQty)}</strong> to{" "}
          <strong className="text-data text-foreground">{qty}</strong> units, recorded as {approver || "(no approver set)"}.
        </div>
      )}

      <div className="flex items-center gap-2">
        <button
          onClick={() => {
            setTouched(true);
            if (canSubmit) onSubmit(qty, trimmedReason);
          }}
          disabled={!canSubmit || !approver.trim()}
          className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-black transition-opacity duration-[var(--duration-fast)] disabled:opacity-40"
        >
          {submitting ? "Submitting…" : "Confirm modification"}
        </button>
        <button
          onClick={onCancel}
          disabled={submitting}
          className="rounded-md border border-border px-3 py-1.5 text-sm transition-colors duration-[var(--duration-fast)] hover:bg-border/30 disabled:opacity-40"
        >
          Cancel
        </button>
      </div>
    </Card>
  );
}
