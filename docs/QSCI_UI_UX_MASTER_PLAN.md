# QSCI UI/UX Master Plan

Status: **COMPLETE** (planning artifact)
Date: 2026-08-20

## 1. Design Direction

Current implementation already establishes the correct direction (`frontend/app/globals.css`): dark-first navy/slate background, cyan accent, violet reserved for research surfaces, semantic status-pill colors for LIVE/RESEARCH/ILLUSTRATIVE/PENDING. This plan extends that system rather than replacing it — the tokens are sound; what's missing is a component library, motion system, and page-level composition discipline applied consistently.

Target aesthetic (unchanged from the brief): modern enterprise SaaS + scientific research platform + supply-chain control tower. Explicitly avoid: gradients-as-decoration, glowing "quantum" visual effects, generic AI robot imagery, animation for its own sake, empty KPI walls, decorative charts that don't map to a real number.

## 2. Information Architecture

```
/                     Marketing/landing (exists)
/dashboard            Decision Center (exists, inventory-only — extend to routing)
/demand               Forecast comparison (exists)
/inventory            Recommendation table (exists)
/risk                 Exception feed (new)
/optimization         Routing/allocation decisions (new — backend already real)
/scenarios            What-if simulator (new — backend work required first)
/copilot              Grounded assistant (new — last, depends on everything else)
/research             Evidence viewer (exists — deepen, don't rebuild)
/models               Model evidence registry (new)
/data                 Dataset lineage (new — backend already real)
/settings             Config (new, low priority)
```

Sidebar groups (extends the existing `Sidebar.tsx` two-group pattern): **Decide** (Dashboard, Demand, Inventory, Risk, Optimization, Scenarios, Copilot), **Understand** (Research Lab, Models, Data). Settings lives in a header/footer utility slot, not the main nav.

## 3. Navigation

Keep the existing route-group pattern (`app/(app)/layout.tsx` wraps all authenticated/app pages with the sidebar; `/` stays outside it). No change to this mechanism — it works and is idiomatic Next.js App Router.

## 4. Visual System

- **Color**: extend `globals.css` tokens, don't introduce new ad hoc colors per page. Every new page must use `--color-accent`/`--color-research`/`--color-live`/etc., never a hardcoded hex.
- **Typography**: current stack (Geist Sans/Mono via `next/font`) is adequate; no change needed. Establish a type scale (currently ad hoc `text-xl`/`text-sm` per component) — define `text-display`, `text-heading`, `text-body`, `text-caption` as Tailwind theme extensions before building new pages, so `/risk`, `/optimization`, etc. don't reinvent sizes.
- **Spacing**: standardize on Tailwind's default scale; no custom spacing tokens needed at this size.

## 5. Components (existing + planned)

**Existing, reusable, keep as the foundation**: `StatusPill`, `Sidebar`, `DecisionChain`, `WhyPanel`.

**Planned, in build order**:
1. `DataTable` — sortable/filterable table (needed by `/inventory` at scale, `/models`, `/data`, `/optimization`'s method-comparison view). Currently `/inventory` hand-rolls a `<table>`; extract once a second table-heavy page is built, not before (avoid premature abstraction).
2. `EvidenceChart` — a thin wrapper around a real charting library (recommend `recharts` or `visx`, both React-native, avoid heavier options) for prediction intervals, resource-scaling curves, confidence intervals. No chart ships without a real data source wired in from day one — never scaffold with placeholder data.
3. `ScenarioComparisonPanel` — baseline vs. scenario side-by-side, built only once the scenario backend endpoint exists (§ dependencies in the feature matrix).
4. `Drawer`/`BottomSheet` — mobile evidence panels (WhyPanel/DecisionChain collapse into these below a breakpoint, not just via CSS shrink).
5. `LoadingSequence` — the DATA→QUALITY→FORECAST→...→RECOMMENDATION step indicator for `/dashboard`'s "Generate recommendation" action. Must reflect real backend progress (poll `run_status`), never a canned animation that outpaces or lags the actual computation — this directly follows CLAUDE.md's "never show 'Running quantum circuit...' unless it's actually running" rule.

## 6. Page-by-Page Design Strategy

For each existing and planned page: empty state, loading state, error state, mobile behavior, and one accessibility note.

- **`/dashboard`**: Empty = "No recommendations yet, generate one" (exists). Loading = `LoadingSequence` replacing the bare "Generating…" label. Error = "Backend unavailable" banner (exists, keep). Mobile = recommendation list becomes a full-screen list; selecting one pushes DecisionChain+WhyPanel into a drawer rather than a side-by-side grid. A11y = approve/reject buttons need `aria-label`s beyond visible text once icons are introduced; today's text-only buttons are already screen-reader-adequate.
- **`/demand`**: Empty = three model cards, no run yet (exists). Loading = per-card status text (exists) — extend with the `LoadingSequence` for VQR specifically, since it's genuinely multi-minute. Error = per-card error text (exists). Mobile = 3-column grid → stacked cards (Tailwind `md:grid-cols-3` already degrades correctly, verify at 375px width). A11y = ensure `<button>` disabled states have sufficient contrast (current cyan-on-navy passes AA at full opacity; verify the 50%-opacity disabled state separately).
- **`/inventory`**: Empty = link to Decision Center (exists). Loading = skeleton rows, not a blank table (currently just "Loading…" text — minor P4 gap). Mobile = table → card list (a raw `<table>` with `overflow-x-auto` is a P3 stopgap, not the final mobile design).
- **`/research`**: Empty = N/A (always has data once qsci_core results exist). Loading = per-section skeletons (currently the whole page waits on `Promise.all`, meaning one slow endpoint blocks all four sections — fix to per-section loading). Mobile = JSON `<pre>` blocks need a real component (raw JSON dumps are not mobile-usable at any width) — this is the single most important `/research` fix, more urgent than adding new sections.
- **`/risk` (new)**: Empty = "No active risk exceptions" (a real, honest empty state — do not invent risk if `qsci_core.risk` finds none). Mobile = card list, severity-sorted.
- **`/optimization` (new)**: Loading = per-method status (OR-Tools/annealing fast, QAOA slow — the `LoadingSequence` must show QAOA as genuinely still running, not fake-complete early). Never a "quantum winner" badge — display objective/feasibility/gap/runtime as parallel columns, framed as evidence per the planning brief's explicit instruction.
- **`/scenarios` (new)**: Do not build until a real backend scenario endpoint exists — building the UI first invites fabricated deltas, which CLAUDE.md's honesty rules forbid outright.
- **`/copilot` (new)**: Build last. Every response must cite which API call(s) backed it; "I don't have that information" is a valid, expected response, not a failure state to hide.
- **`/models`, `/data` (new)**: Read-only, low interaction risk, good candidates for early Playwright coverage once built.

## 7. Animation & Motion

Motion budget: state transitions only. Concretely: DecisionChain stage expand/collapse (exists, CSS-only, keep), a scenario before/after comparison, the LoadingSequence step progression, drawer open/close on mobile, approve/reject confirmation (a brief success flash, not a modal). Nothing else. No page-load hero animations, no hover-glow effects, no particle/circuit-board decoration implying quantum computation that isn't happening. Respect `prefers-reduced-motion` — currently untested, must be added when the motion system is built (not deferred to a later polish pass, since it's an accessibility requirement, not a nice-to-have).

## 8. Loading States (Detail)

The `LoadingSequence` component's step list must be generated from the actual pipeline stages a given action touches — a LightGBM forecast shows DATA→FORECAST only (fast, might not even need a multi-step display); a QAOA optimization shows the real stages including a "this may take several minutes" notice sourced from Phase 3/4's actual measured runtimes, not a generic spinner. This is the direct product-level expression of CLAUDE.md's "loading state must reflect reality" rule.

## 9. Responsive Design

Three explicit breakpoints to design and test at: 375px (mobile), 768px (tablet), 1280px+ (desktop). Current pages rely entirely on Tailwind's default responsive utilities without breakpoint-specific verification — every new page in this plan must be screenshotted at all three widths before being marked done (Playwright's viewport-resize capability, once E2E is set up, should automate this).

## 10. Accessibility

Target WCAG 2.2 AA, applied incrementally: **first pass** (P2, before new pages) — audit the four existing pages for keyboard navigation, focus-visible states, color contrast (the design tokens should be checked with a contrast checker, not assumed), and semantic heading structure. **Second pass** (P3, alongside new pages) — ARIA roles for DecisionChain's stage buttons (currently plain `<button>`s with visible text, likely already adequate, but unverified with a screen reader), reduced-motion support once motion exists, form labels for the approver-name input (currently a `placeholder`, not a `<label>` — a real, fixable gap).

## 11. Stitch Workflow

Not available/not invoked in this session. Recommended workflow when it is: generate design explorations for exactly five surfaces (Landing, Decision Center, Research Lab, Demand, Inventory — matching the planning brief), pick one winning direction, derive the reusable component set from it, then apply that system to every subsequent page rather than re-exploring per page. Do not let Stitch generate the `/optimization`, `/risk`, `/scenarios`, `/copilot` pages independently — they should inherit the system, not diverge from it.

## 12. Explicit Non-Goals

No dark/light toggle beyond `prefers-color-scheme` (already implemented) unless a user explicitly asks for a manual toggle. No custom illustration/iconography system beyond what's needed for the status pills and nav — commission or select one only when a specific page genuinely needs it, not preemptively.
