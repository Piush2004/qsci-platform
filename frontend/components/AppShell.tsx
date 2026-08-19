"use client";

import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

/** Owns the mobile nav-toggle state shared between TopBar (hamburger
 * button) and Sidebar (hidden by default below `lg`, shown as an overlay
 * when toggled). This is a minimal fix to stop the fixed-width sidebar
 * from overflowing small viewports -- the full drawer/bottom-sheet
 * treatment is Milestone 9's scope (docs/QSCI_PHASE_6_MASTER_PLAN.md),
 * not redone here. */
export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full">
      <div className={`${mobileNavOpen ? "fixed inset-0 z-40 flex" : "hidden"} lg:static lg:z-auto lg:flex`}>
        {mobileNavOpen && (
          <button
            aria-label="Close navigation"
            onClick={() => setMobileNavOpen(false)}
            className="fixed inset-0 bg-black/50 lg:hidden"
          />
        )}
        <div className="relative z-10">
          <Sidebar onNavigate={() => setMobileNavOpen(false)} />
        </div>
      </div>
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar onMenuClick={() => setMobileNavOpen((v) => !v)} />
        <main className="min-w-0 flex-1 overflow-x-auto">{children}</main>
      </div>
    </div>
  );
}
