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

`bcaacf4` — phase-6 milestone-0: design system + global visual foundation (plus `e1fc34a` for the preceding planning-docs baseline).

### Not Done This Milestone (Explicitly Deferred, Not Silently Dropped)

Full mobile drawer/bottom-sheet redesign (Milestone 9). Landing-page multi-section redesign per the expanded brief in the Phase 6 implementation prompt (hero/gap/pipeline/evidence/decision-intelligence-explanation/classical-vs-quantum/financial-impact/explainability/research-credibility sections) — the existing single-section landing page already satisfies the core thesis requirement (FORECAST≠DECISION, pipeline visual, quantum-as-research-layer framing) and a full redesign is disproportionate scope for "Milestone 0: design system foundation," risking exactly the "uncontrolled pass" the prompt explicitly forbids; flagged as a candidate for a dedicated later milestone rather than attempted here. Stitch MCP exploration — not available in this environment (checked via `ToolSearch`; only `DesignSync`, a different Claude Design tool, is present).

---

## Milestone 1 — Close the Golden Path + Harden the Decision Center

Status: **COMPLETE**
Date: 2026-08-20

### Pre-implementation audit (done live in-browser before any code change, per the milestone's own instruction)

- **CURRENTLY WORKING**: Generate, DecisionChain render, WhyPanel render, Approve (backend-confirmed status transition).
- **CURRENTLY BROKEN** (found during the audit, fixed this milestone): the Audit stage panel didn't refresh after approve/reject — showed only `RECOMMENDATION_CREATED`, missing the just-created `APPROVAL_APPROVE` event, because only a `selectedId` change triggered a refetch and deciding on the currently-selected item doesn't change it.
- **CURRENTLY MISSING**: the entire Modify workflow (backend `POST /recommendations/{id}/modify` existed and was tested; zero frontend UI called it).
- **CURRENTLY ONLY API-TESTED**: duplicate-approval/invalid-state-transition handling, `/demand`'s three forecast buttons, backend-unavailable handling.

### Implemented

- **`ModifyPanel` component** (new): quantity + mandatory reason, client-side validated (numeric/finite/non-negative/plausible-magnitude for quantity; non-empty/max-length for reason), ARIA-wired (`aria-invalid`, `aria-describedby`, `role="alert"`), review-before-submit line, uses the Milestone 0 design system (`Card`, existing motion/typography tokens) throughout.
- **Dashboard wiring**: Approve/Modify/Reject action bar, `actionBusy` flag preventing duplicate submission during any in-flight action, audit-refresh fix (both the recommendation list and audit trail now refetch after every decide/modify success), empty-state `Card` ("No active decisions").
- **Backend hardening**: `ApprovalActionRequest.modified_qty` now validated server-side too (`ge=0`, a custom finite-check validator) — defense in depth, not relying on client-side validation alone for a value that's persisted to the audit trail. A custom `RequestValidationError` exception handler in `main.py` sanitizes non-finite floats before serializing the error response (fixes a real 500-crash-on-error-response bug, see below).
- **6 new backend tests**: negative/infinite/valid `modified_qty`, audit-event reason recording.

### Real bugs found and fixed (in the order discovered)

1. **Audit panel staleness** (found during the pre-implementation live audit, before writing any Modify code) — see above. Fixed by refetching audit alongside the recommendation list on every decide/modify success.
2. **Backend 500 on non-finite input** — sending `modified_qty: Infinity` crashed the *validation-error response itself* (Starlette's `JSONResponse` enforces `allow_nan=False`, but FastAPI's default handler tries to echo the rejected value back). Fixed with a custom exception handler. Found by a newly-written adversarial test, not manual testing — exactly the kind of bug Section 20's "run pytest, not just claim success" mandate exists to catch.
3. **`ModifyPanel` raw floating-point display** ("152.99897648241702 units") — found via manual browser testing. Fixed with a `fmt()` rounding helper.
4. **Tooling correction**: Milestone 0's mobile testing tool (`chrome-devtools__resize_page`) turned out to floor at ~500px in this environment, not the requested 390px — discovered when re-testing Modify at "mobile" width looked suspiciously roomy. Switched to true CDP device emulation (`emulate` with a `viewport` string), which surfaced two real bugs invisible at 500px:
5. **Missing base `grid-cols-1`** on `/dashboard`'s and `/demand`'s responsive grids — CSS grid's implicit auto-placement compressed/clipped content instead of stacking it below `lg`/`md`. Fixed on both pages.
6. **Action-bar input squeeze** — the approver-name input was compressed to near-zero width beside three buttons in a single flex row at 390px. Fixed: `flex-col sm:flex-row`, input gets its own row below `sm`.

### Tested

- `npx tsc --noEmit`: 0 errors. `npm run lint`: 0 errors. `npm run build`: succeeds, all 5 routes.
- `backend/tests/`: 42/42 passed (36 prior + 6 new).
- Root `qsci_core` suite: 176 passed, 1 xfailed — unchanged from the pre-milestone baseline, 0 regressions.

### Browser Verified

Full Tests A-K from the milestone prompt — see `docs/QSCI_E2E_TEST_REPORT.md` Milestone 1 section for the complete table. Highlights: real backend-confirmed Approve and Modify (not optimistic UI), validation blocking on invalid quantity/missing reason with correct ARIA wiring, honest "Backend unavailable" on a real backend outage, and a full generate→select→approve flow re-verified working at *true* 390px after the two mobile fixes above.

### Visual QA

See `docs/QSCI_VISUAL_QA_REPORT.md` Milestone 1 section — desktop, true-768px tablet, and true-390px mobile all re-screenshotted after fixes.

### Accessibility

Spot-checked (not a full WCAG 2.2 AA pass): `ModifyPanel`'s quantity/reason fields both have real `<label>`s (not placeholder-as-label), `aria-invalid`/`aria-describedby` wired to `role="alert"` error messages, confirmed present in the live accessibility tree (not just written in source) via `chrome-devtools__take_snapshot`.

### Regression Protection

No changes to `qsci_core`, `DecisionChain`, or `WhyPanel`'s core rendering logic (only wrapped in `Card`, unchanged this milestone). Existing Golden Path data (from Phase 6 and Milestone 0's sessions) rendered identically throughout this milestone's testing, confirming no regression.

### Commit

Pending — see final report.
