# QSCI Implementation Log

Running log, one entry per milestone, per `docs/QSCI_PHASE_6_MASTER_PLAN.md`'s execution protocol. Each entry records what was implemented, tested, browser-verified, and any failures found and fixed — not just a completion claim.

---

## Milestone 0 — Design System + Global Visual Foundation

Status: **COMPLETE**
Date: 2026-08-20

### Implemented

- Typography scale (`.text-display/.text-h1/.text-h2/.text-h3/.text-body/.text-supporting/.text-caption/.text-data`) and motion tokens (`--duration-fast/base/slow`, `--ease-standard`) in `frontend/app/globals.css`, with a `prefers-reduced-motion` guard that disables all `.motion-*` animations and clamps transition/animation durations globally.
- New shared components: `PageHeader.tsx`, `Card.tsx`, `TopBar.tsx` (breadcrumb context bar), `AppShell.tsx` (owns mobile-nav-toggle state).
- `Sidebar.tsx` reworked: fixed a real Tailwind bug in the plan (dynamic `bg-${accent}/15` class interpolation, which Tailwind's compiler cannot detect — replaced with an explicit static-class lookup table before it ever shipped); added an active-route indicator bar.
- Applied `PageHeader`/`Card` consistently across `/`, `/dashboard`, `/demand`, `/inventory`, `/research`; `DecisionChain` and `WhyPanel` now use `Card` internally.
- Fixed a real, found-via-testing mobile layout bug: the fixed-width (`w-56`) sidebar overflowed the viewport below `lg` (1024px), cutting off page content. Sidebar now hides by default below `lg` with a hamburger toggle in `TopBar` (`AppShell.tsx`). This is a bounded fix, not the full drawer/bottom-sheet system scoped to Milestone 9 — noted explicitly, not silently expanded.
- Fixed two pre-existing (Phase 6, not this milestone's) ESLint errors surfaced by `npm run lint`: a `react-hooks/set-state-in-effect` violation in `dashboard/page.tsx` (restructured the mount-effect to a direct `.then()` chain, matching the pattern already used successfully elsewhere on the same page) and a `react-hooks/immutability` violation in `demand/page.tsx` (converted a reassigned-`let` polling loop to non-mutating recursion).

### Tested

- `npx tsc --noEmit`: 0 errors.
- `npm run lint`: 0 errors (2 pre-existing errors found and fixed as part of this milestone's static-validation step).
- `npm run build`: succeeds, all 5 routes prerender as static content.
- No backend changes this milestone — backend test suite not re-run (nothing to regress).

### Browser Verified

- Real backend (`uvicorn app.main:app`, port 8000) + real frontend (`next dev`, port 3001) — not mocked.
- `/`, `/dashboard`, `/demand`, `/inventory`, `/research` all visited; 0 console errors on any page.
- Dashboard's existing Golden Path data (from Phase 6's manual approval) still renders correctly through the new `Card`/`PageHeader` components — confirms the visual rework didn't regress the already-verified approve/reject flow.

### Visual QA

- **Desktop (1440×900)**: `/`, `/demand`, `/research`, `/inventory` all screenshotted — correct hierarchy, no overflow, `text-data` monospace tabular numbers render cleanly in the inventory table.
- **Tablet (768×1024)**: dashboard screenshotted — sidebar correctly collapsed (hamburger shown), no overflow.
- **Mobile (390×844)**: dashboard screenshotted before and after the fix. **Before**: sidebar overflowed the viewport, page content cut off (real bug, screenshotted as evidence). **After**: full-width content, no overflow, hamburger toggle opens a working overlay nav (screenshotted mid-interaction, confirmed functional).

### Adversarial Test

- `prefers-reduced-motion` CSS rule presence verified via `document.styleSheets` inspection in the live page — confirmed compiled into the stylesheet.
- Backend-unavailable error-banner styling untouched by this milestone's changes (verified by inspection, not re-triggered live — no regression risk since the underlying `error &&` logic wasn't touched).

### Failures Found and Fixed (This Milestone)

1. Dynamic Tailwind class interpolation in `Sidebar.tsx`'s original draft (`bg-${accent}/15`) — would have silently failed to generate CSS. Caught before commit via review, not via a build failure (Tailwind doesn't error on this, it just omits the class).
2. Two pre-existing ESLint errors (see above) — caught by this milestone's static-validation step, since `npm run lint` had apparently not been run as part of Phase 6's own verification.
3. Mobile sidebar overflow — caught via this milestone's mandated mobile screenshot, not by `npm run build` (which doesn't catch layout issues).

### Commit

Pending — see final report.

### Not Done This Milestone (Explicitly Deferred, Not Silently Dropped)

Full mobile drawer/bottom-sheet redesign (Milestone 9). Landing-page multi-section redesign per the expanded brief in the Phase 6 implementation prompt (hero/gap/pipeline/evidence/decision-intelligence-explanation/classical-vs-quantum/financial-impact/explainability/research-credibility sections) — the existing single-section landing page already satisfies the core thesis requirement (FORECAST≠DECISION, pipeline visual, quantum-as-research-layer framing) and a full redesign is disproportionate scope for "Milestone 0: design system foundation," risking exactly the "uncontrolled pass" the prompt explicitly forbids; flagged as a candidate for a dedicated later milestone rather than attempted here. Stitch MCP exploration — not available in this environment (checked via `ToolSearch`; only `DesignSync`, a different Claude Design tool, is present).
