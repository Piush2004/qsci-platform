"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const DECISION_LINKS = [
  { href: "/dashboard", label: "Decision Center" },
  { href: "/demand", label: "Demand" },
  { href: "/inventory", label: "Inventory" },
];

const RESEARCH_LINKS = [{ href: "/research", label: "Research Lab" }];

// Tailwind's compiler only picks up literal class strings -- template-
// interpolated classes like `bg-${accent}/15` would silently fail to
// generate. Each accent variant is spelled out explicitly instead.
const ACCENT_STYLES = {
  accent: { active: "bg-accent/15 text-accent", bar: "bg-accent" },
  research: { active: "bg-research/15 text-research", bar: "bg-research" },
} as const;

function NavLink({ href, label, active, accent }: { href: string; label: string; active: boolean; accent: keyof typeof ACCENT_STYLES }) {
  const styles = ACCENT_STYLES[accent];
  return (
    <Link
      href={href}
      className={`relative block rounded-md px-2 py-1.5 text-sm transition-colors duration-[var(--duration-fast)] ${
        active ? styles.active : "text-foreground/80 hover:bg-border/40"
      }`}
    >
      {active && (
        <span className={`absolute -left-4 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full ${styles.bar}`} aria-hidden />
      )}
      {label}
    </Link>
  );
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void } = {}) {
  const pathname = usePathname();
  return (
    <nav
      onClick={onNavigate}
      className="flex h-full w-56 shrink-0 flex-col gap-6 border-r border-border bg-surface px-4 py-6"
    >
      <Link href="/" className="px-2 text-h3 tracking-wide">
        QSCI
      </Link>
      <div>
        <p className="px-2 pb-2 text-caption uppercase">Decide</p>
        <div className="space-y-0.5 pl-4">
          {DECISION_LINKS.map((l) => (
            <NavLink key={l.href} href={l.href} label={l.label} active={pathname === l.href} accent="accent" />
          ))}
        </div>
      </div>
      <div>
        <p className="px-2 pb-2 text-caption uppercase">Understand</p>
        <div className="space-y-0.5 pl-4">
          {RESEARCH_LINKS.map((l) => (
            <NavLink key={l.href} href={l.href} label={l.label} active={pathname === l.href} accent="research" />
          ))}
        </div>
      </div>
    </nav>
  );
}
