"use client";

import { usePathname } from "next/navigation";

const ROUTE_META: Record<string, { group: string; label: string }> = {
  "/dashboard": { group: "Decide", label: "Decision Center" },
  "/demand": { group: "Decide", label: "Demand" },
  "/inventory": { group: "Decide", label: "Inventory" },
  "/research": { group: "Understand", label: "Research Lab" },
};

/** Thin context bar above every app page: which section of the product
 * you're in, and which page. Below `lg`, also carries the nav toggle
 * (the sidebar is hidden by default at that width -- see AppShell). */
export function TopBar({ onMenuClick }: { onMenuClick?: () => void } = {}) {
  const pathname = usePathname();
  const meta = ROUTE_META[pathname];

  return (
    <div className="flex h-12 shrink-0 items-center gap-2 border-b border-border px-4 text-caption sm:px-6">
      {onMenuClick && (
        <button
          onClick={onMenuClick}
          aria-label="Toggle navigation"
          className="mr-1 rounded p-1 text-foreground/80 hover:bg-border/40 lg:hidden"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
            <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      )}
      <span>QSCI</span>
      {meta && (
        <>
          <span className="text-border">/</span>
          <span>{meta.group}</span>
          <span className="text-border">/</span>
          <span className="text-foreground">{meta.label}</span>
        </>
      )}
    </div>
  );
}
