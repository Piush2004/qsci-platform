const CLASS_BY_LABEL: Record<string, string> = {
  LIVE: "label-live",
  RESEARCH: "label-research",
  ILLUSTRATIVE: "label-illustrative",
  PENDING: "label-pending",
  "NOT AVAILABLE FOR THIS MODEL": "label-pending",
};

/** Renders CLAUDE.md's mandatory LIVE/RESEARCH/ILLUSTRATIVE/PENDING
 * classification. Never omit this on any number sourced from qsci_core. */
export function StatusPill({ label }: { label: string }) {
  const normalized = label.toUpperCase();
  const cls = CLASS_BY_LABEL[normalized] ?? "label-pending";
  return <span className={`label-pill ${cls}`}>{label}</span>;
}
