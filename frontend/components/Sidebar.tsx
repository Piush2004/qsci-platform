"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const DECISION_LINKS = [
  { href: "/dashboard", label: "Decision Center" },
  { href: "/demand", label: "Demand" },
  { href: "/inventory", label: "Inventory" },
];

const RESEARCH_LINKS = [{ href: "/research", label: "Research Lab" }];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <nav className="flex h-full w-56 shrink-0 flex-col gap-6 border-r border-border bg-surface px-4 py-6">
      <Link href="/" className="px-2 text-sm font-semibold tracking-wide">
        QSCI
      </Link>
      <div>
        <p className="px-2 pb-2 text-xs font-medium uppercase tracking-wider text-muted">Decide</p>
        {DECISION_LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={`block rounded-md px-2 py-1.5 text-sm ${
              pathname === l.href ? "bg-accent/15 text-accent" : "text-foreground/80 hover:bg-border/40"
            }`}
          >
            {l.label}
          </Link>
        ))}
      </div>
      <div>
        <p className="px-2 pb-2 text-xs font-medium uppercase tracking-wider text-muted">Understand</p>
        {RESEARCH_LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={`block rounded-md px-2 py-1.5 text-sm ${
              pathname === l.href ? "bg-research/15 text-research" : "text-foreground/80 hover:bg-border/40"
            }`}
          >
            {l.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
