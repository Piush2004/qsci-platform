# QSCI Visual QA Report

Running log, one section per milestone. Every entry below reflects an actual screenshot taken this session (Chrome DevTools MCP / claude-in-chrome), not a description of intended appearance.

---

## Milestone 0 — Design System + Global Visual Foundation

Date: 2026-08-20

### Desktop (1440×900)

| Page | Result |
|---|---|
| `/` | Typography scale applied (`text-display` hero, `text-caption` footnote), pipeline chips have a subtle hover border transition, motion-rise-in on load. No overflow, no console errors. |
| `/demand` | Three model cards render with consistent `Card` styling, `StatusPill` labels correct (LIVE/LIVE/RESEARCH per model), monospace tabular numbers via `.text-data` once a metric appears. |
| `/research` | `Card`-wrapped sections, breadcrumb reads "QSCI / Understand / Research Lab", violet active-state indicator on the sidebar link (distinct from cyan "Decide" section), real Phase 4/5 data loaded (master benchmark table, QAOA depth JSON, noise sensitivity JSON) with 0 console errors. |
| `/inventory` | Table renders both the old (pre-Milestone-1-fix, 93.1% risk) and would-be-new recommendation rows side by side — real historical data, not fabricated; `.text-data` gives the numeric columns clean tabular alignment. |
| `/dashboard` | TopBar breadcrumb, sidebar active-indicator bar, DecisionChain (10-stage horizontal chain, `Card`-wrapped) and WhyPanel (confidence decomposition grid) all verified rendering with real recommendation data from the existing dev DB. |

### Tablet (768×1024)

| Page | Result |
|---|---|
| `/dashboard` | Sidebar correctly collapses to a hamburger-triggered overlay below the `lg` (1024px) breakpoint — deliberate choice, since the 224px fixed sidebar would otherwise consume ~30% of a 768px-wide tablet screen. No overflow, no content cut off. |

### Mobile (390×844)

| Page | Result |
|---|---|
| `/dashboard` (before fix) | **FAIL** — sidebar's fixed `w-56` (224px) width was not responsive; page content and the "APPROVED"/"PENDING" status pills were cut off at the right edge, horizontal scrollbar appeared. Screenshotted as evidence before fixing. |
| `/dashboard` (after fix) | **PASS** — hamburger icon in TopBar, full-width single-column content, no overflow. Clicking the hamburger opens a working overlay nav with dimmed backdrop; clicking a link or the backdrop closes it (verified: overlay nav screenshotted mid-open, showing Decide/Understand groups correctly). |

### Known Visual Gaps (Not Regressions — Pre-Existing or Explicitly Deferred)

- `/inventory`'s table uses `overflow-x-auto` as a mobile stopgap, not a card-list redesign — acceptable for Milestone 0's scope, flagged for Milestone 9.
- `/research`'s two JSON sections (`<pre>{JSON.stringify(...)}</pre>`) are functional but not designed — explicitly scoped to Milestone 6 (Research Lab Depth Pass) in `docs/QSCI_PHASE_6_MASTER_PLAN.md`, not addressed this milestone.
- Landing page (`/`) is single-section; the expanded multi-section brief (hero/research-gap/pipeline/evidence/financial-impact/etc.) was not attempted this milestone — see `docs/QSCI_IMPLEMENTATION_LOG.md`'s Milestone 0 entry for the scoping rationale.
