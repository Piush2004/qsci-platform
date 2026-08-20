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

---

## Milestone 1 — Close the Golden Path

Date: 2026-08-20

### Tooling correction (read this before trusting Milestone 0's mobile row above)

Milestone 0's "mobile (390×844)" testing used `chrome-devtools__resize_page(390, 844)`, which — discovered this milestone — silently floors at `window.innerWidth === 500` in this environment (confirmed via `evaluate_script`; the tool reports success at the requested size but the page never actually renders at less than ~500px). Milestone 0's "PASS" verdict was real evidence, just at ~500px, not true 390px. Milestone 1 switched to `chrome-devtools__emulate({viewport: "390x844x2,mobile,touch"})`, which does deliver a true `window.innerWidth === 390` (verified before every mobile screenshot below), and found two additional real bugs invisible at 500px.

### Desktop (1440×900)

| Page | Result |
|---|---|
| `/dashboard` | `ModifyPanel` renders correctly below the WhyPanel, `Card`-styled, consistent with the rest of the design system. Validation error states (`role="alert"`, red text) render inline under each field. Review-before-submit line renders correctly. |

### Tablet (768×1024, re-verified with true device emulation this time)

| Page | Result |
|---|---|
| `/dashboard` | Re-confirmed clean at *true* 768px (not just the ~500px-floor tool used in Milestone 0) — hamburger nav, single-column stacking, no overflow. |

### Mobile (true 390×844, device-emulated)

| Page | Result |
|---|---|
| `/dashboard` (initial load) | PASS — list and header render cleanly. |
| `/dashboard` (recommendation selected, before fix) | **FAIL** — two real bugs found at true 390px that the ~500px Milestone-0 testing missed: (1) the `grid lg:grid-cols-[320px_1fr]` container had no base `grid-cols-1`, so the recommendation list and WhyPanel text were compressed/cut off rather than stacked; (2) the approve/modify/reject action bar's approver-name input was squeezed to near-zero width beside three buttons in one flex row. Screenshotted as evidence before fixing. |
| `/dashboard` (after both fixes) | **PASS** — WhyPanel text wraps fully, confidence-decomposition grid renders as a clean 2×2, approver input gets its own full-width row with buttons wrapping below it. Full interaction verified: filled approver name, tapped Approve, confirmed real backend-driven status change (PENDING→APPROVED) at true 390px. |
| `/demand` | **FAIL before fix** (same missing-`grid-cols-1` bug as dashboard, on the `md:grid-cols-3` model-card grid) → **PASS after fix** — three cards stack full-width, no overflow. |
| `/inventory` | PASS — table's `overflow-x-auto` is correctly contained to the table's own Card; no page-level horizontal overflow (confirmed via `document.documentElement.scrollWidth === window.innerWidth`). |

### Adversarial (backend down)

| Scenario | Result |
|---|---|
| `/dashboard`, backend killed mid-session, page reloaded | Honest "Backend unavailable" banner, "PENDING DECISIONS (0)", no fabricated cached data, no fake success state. |
| `/dashboard`, an orphaned unrelated process answering on the same port with 404 | Honest "Backend error: Not Found" banner — the error banner surfaces whatever the real HTTP response actually was, never papered over. (This was an accidental real-world case of "backend returns an unexpected response," not a staged test — documented because it's genuine evidence the error path is not hardcoded to one specific failure mode.) |

### Known Visual Gaps (Unchanged From Milestone 0, Still Deferred)

- `/research`'s two JSON sections — still Milestone 6 scope.
- Landing page multi-section redesign — still out of scope, per Milestone 0's rationale.
- DecisionChain's own stage-button row still uses `overflow-x-auto` at narrow widths (swipeable, not lost, not fixed this milestone) — full mobile redesign remains Milestone 9 scope.

## Milestone 2 — Optimization Intelligence

### Desktop (1440×900)

| Page/State | Result |
|---|---|
| `/optimization`, initial load | PASS — instance selector, problem-context card, Phase 3 N=4 comparison table (RESEARCH label, real 380.01/0.00%/Yes/runtime/resources values), all render with real data from `GET /optimize/instances/A-n32-k5`. |
| `/optimization`, live `or_tools_qubo` run | PASS — comparison table updates from all-`N/A` to real cost/feasible/runtime/resources with a LIVE badge; a "Route" section appears with an SVG map (real coordinates) plus a `sr-only` textual route table. |
| `/optimization`, live `simulated_annealing` run | PASS — second column populates (cost 380.01, feasible, RESEARCH badge, "1000 reads"), agrees with the OR-Tools-on-QUBO result and the Phase 3 pre-computed table. |
| `/optimization`, instance switch (A-n32-k5 → A-n37-k5) | PASS — Customers (31→36) and Published BKS (784→669) live-update from the real endpoint; no stale data. |
| `/optimization`, scalability charts | PASS — both SVG charts (annealing feasibility vs. num_reads; QAOA depth vs. runtime) render real Phase 4 data points with legends and `sr-only` textual-table equivalents. |

### Mobile (environment-limited — see note)

**Environment note**: neither `resize_page` nor `emulate({viewport: "390x844..."})` produced a true `window.innerWidth` of 390 in this session — both floored at ~516px regardless of the requested size, confirmed via repeated `evaluate_script` checks across fresh page loads. This did not reproduce Milestone 1's documented true-390px method. All mobile findings below are reported at the actually-achieved ~516px width, not claimed at 390px.

| Page/State | Result |
|---|---|
| `/optimization` at ~516px, before fix | **FAIL** — `SolverComparisonTable`'s `<table className="w-full ...">` compressed to fit the viewport instead of overflowing, clipping the QAOA column's text (e.g. "QAC", "0.0", "40.") rather than making it scrollable. Both the Phase 3 pre-computed table and the live-run table were affected. Screenshotted as evidence before fixing. |
| `/optimization` at ~516px, after fix | **PASS** — `min-w-[560px]` added to the table; both comparison tables now show a visible horizontal scrollbar and all columns (including QAOA) are fully legible when scrolled. Sidebar collapses to a hamburger menu correctly; buttons stack full-width; scalability charts and the "what does this mean" findings section render cleanly with no overflow. |
| `/optimization` at ~516px, no live run yet | PASS — "Route" section correctly does not render (no fabricated route shown before a live run completes). |

### Known Visual Gaps (Carried Forward)

- True 390×844 mobile testing could not be performed this milestone due to the tooling floor described above — flagged for follow-up if resolved in a future session.
- Tablet (768×1024) re-verification not repeated this milestone (same tooling floor prevented an exact 768px target; the desktop pass already covers the `lg` breakpoint transition).
