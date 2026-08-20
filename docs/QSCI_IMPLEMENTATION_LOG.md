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

`1a72c8b`

## Milestone 2 — Optimization Intelligence + Classical vs Quantum Routing

### Implemented

- **`docs/MILESTONE_2_OPTIMIZATION_AUDIT.md`** (new): read-only pre-implementation audit of the existing OR-Tools/QUBO/annealing/QAOA stack, APIs, reusable Phase 3-5 experiment results, and the 4 backend gaps this milestone needed to fill — written before any code changed, per the milestone's mandate.
- **Backend**: `GET /optimization` (list runs, optional `problem_type` filter), `GET /optimize/instances/{name}` (real CVRPLIB coordinates/demands/capacity/BKS for problem-context and route visualization, 404 on unknown instance), `GET /research/routing` (read-only exposure of `routing_results.json`/`routing_penalty_sensitivity.json`/ground truth with the Phase 3 fairness note attached), and a new live-triggerable method `or_tools_qubo` (`solve_qubo_with_ortools` — CP-SAT on the identical QUBO) added as the classical, genuinely-fair reference point for the 3-way QUBO-track comparison, since native OR-Tools solves a different, non-comparable problem. `_run_or_tools`/`_run_qubo_track` extended to return real coordinates in their `solution` dict so a live run's route can be visualized without a second round-trip.
- **Frontend `/optimization` page** (new): instance selector (4 real CVRPLIB instances) → problem context → Phase 3's pre-computed N=4 solution comparison (RESEARCH) → a live 3-way comparison the user can trigger against the real backend → route visualization → scalability charts (real Phase 4 annealing-feasibility-vs-num_reads and QAOA-depth-vs-runtime data) → a real, structured "what does this mean" section → a disclosed-PENDING decision-implication section (no fabricated dollar figure — routing isn't wired into the Recommendation/Approval/Audit chain yet).
- **New components**: `SolverComparisonTable` (Cost/Gap/Feasible/Runtime/Resources/Evidence rows, never a "winner" badge), `RouteVisualization` (SVG map from real Euclidean CVRPLIB coordinates, click-to-highlight, `sr-only` textual-table equivalent), `ScalabilityChart` (dependency-free SVG line chart, `sr-only` textual-table equivalent).
- **8 new backend tests** covering coords-in-solution, run listing (+ filter), the real-instance endpoint (+ 404), the fairness-noted research payload, and an exact-value regression check (`objective == pytest.approx(380.00755017228636)`) that the new `or_tools_qubo` live endpoint reproduces Phase 3's recorded N=4 result.
- **Copy fix**: VQR's "~1-5 min to train" label understated its real measured runtime (731.7s / ~12.2 min, live-verified this milestone) — corrected to "~10-15 min."

### Real bugs found and fixed

1. **Mobile table clipping** — `SolverComparisonTable`'s `<table className="w-full ...">` compressed columns to fit the viewport instead of triggering the wrapper's `overflow-x-auto`, clipping the QAOA column's text at narrow widths. Fixed with a `min-w-[560px]` floor so the table overflows (and scrolls) instead of squeezing. Found via live narrow-viewport testing, not desktop review.
2. **VQR runtime label inaccurate** — see Copy fix above; a real "PENDING"-adjacent honesty gap (claim didn't match the live-measured value) rather than a rendering bug.
3. **React Compiler lint** (`react-hooks/immutability`) on the live-run polling loop — same reassignment-across-`await` pattern as Milestone 1's `/demand` fix; resolved identically with a recursive `pollUntilSettled(method, run, attemptsLeft)` helper instead of a mutated `let`.

### Tested

- `npx tsc --noEmit`: 0 errors. `npm run lint`: 0 errors. `npm run build`: succeeds, all 6 routes (`/`, `/dashboard`, `/demand`, `/inventory`, `/optimization`, `/research`).
- `backend/tests/`: 50/50 passed (844.5s), including all 8 new Milestone 2 tests.
- Root `qsci_core` suite: 176 passed, 1 xfailed — unchanged from the pre-milestone baseline, 0 regressions.

### Browser Verified

Real backend (port 8010), 1440×900: instance switch (A-n32-k5 → A-n37-k5) live-updates Customers/BKS from the real endpoint; live `or_tools_qubo` run returns cost 380.01/feasible/LIVE with a rendered route from real coordinates; live `simulated_annealing` run returns the same cost/feasible with a RESEARCH label and real `num_reads` resource string — both agree with the pre-computed Phase 3 N=4 table. `GET /optimize/instances/NOT-REAL` correctly 404s with a clear message. No console errors across any of the above.

**Step 19 (non-deferrable per the milestone prompt)**: `/demand`'s three forecast buttons live-verified against the real backend — Seasonal Naive (wMAPE 37.15%, RMSE 24.50, instant), LightGBM (wMAPE 25.56%, RMSE 18.08, 4.1s — beats naive as expected), VQR (wMAPE 390.34%, RMSE 217.61, 731.7s — dramatically worse than both classical models, consistent with H1's default expectation; honest "forecast stability: NOT AVAILABLE FOR THIS MODEL" disclosure rendered correctly, no fabricated confidence). `/inventory` live-verified: real qsci_core-computed reorder points/stockout risk/status per row, SKU link correctly navigates into the Decision Center, which renders an honest loading state rather than fabricated data.

### Visual QA

Desktop (1440×900) fully verified — see screenshots taken during this session. **Environment note**: neither `resize_page` nor `emulate({viewport: "390x844..."})` could get `window.innerWidth` below ~516px in this session regardless of requested width (a tooling/environment ceiling that did not reproduce Milestone 1's documented true-390px method) — all "mobile" testing this milestone was done at the achievable ~516px floor, not true 390×844, and is reported as such rather than claimed at 390px.

### Accessibility

`RouteVisualization` and `ScalabilityChart` both ship `sr-only` textual-table equivalents of their SVG content (verified present in the live accessibility snapshot, not just in source) plus `<title>` tooltips on interactive SVG elements. Route/scalability images carry descriptive `aria-label`s.

### Regression Protection

No changes to `DecisionChain`, `WhyPanel`, or the Approve/Modify/Reject flow's logic. `/dashboard`'s recommendation → approval → audit path re-verified working (SKU link from `/inventory` navigates in and renders an honest loading state) with no regressions.

### Commit

`phase-6: build optimization intelligence` — see final report.

## Milestone 3 — Outcome & Financial Decision Intelligence

### Implemented

- **Schema**: `RecommendationRecord.forecast_run_id` (nullable FK to `forecast_runs.id`), added via a real Alembic migration (`a513201f3233_add_forecast_run_id_to_recommendations.py`, batch mode for SQLite's ALTER TABLE limitation), applied to the dev DB — all 4 pre-existing rows preserved with `forecast_run_id=NULL`.
- **`backend/app/services/outcome_service.py`** (new): `get_outcome` — real M5 held-out test-window sales as the "backtest actual" for any recommendation with a linked forecast run, honestly distinguished (`kind: "backtest_actual"`) from a live post-decision outcome (`kind: "manual"`, via the pre-existing-but-unwired `qsci_core.persistence.db.record_outcome`). Manual entries take precedence when present.
- **`recommendation_service.py` additions**: `compute_recommendation` extracted as a pure (non-persisting) function shared by the recommend endpoint, `get_baseline_comparison`, and `get_accuracy_vs_outcome` — one implementation of the FORECAST→RISK→FINANCIAL→CONFIDENCE math, not three. `get_baseline_comparison` (Step 3) pairs a recommendation's model against a same-series/horizon `seasonal_naive` run when one exists on file, PENDING otherwise. `get_accuracy_vs_outcome` (Step 4) pairs each distinct model's real wMAPE against its financial total cost, PENDING below 2 models.
- **New endpoints**: `GET`/`POST /recommendations/{id}/outcome`, `GET /recommendations/{id}/baseline`, `GET /research/accuracy-vs-outcome`.
- **New frontend components**: `DecisionCard` (Step 9 — compact list card), `OutcomeSection`, `BaselineComparisonCard`, `ConfidenceExplainer` (Step 6, grounded in the selected recommendation's own real decomposition, not a canned example), `RiskExplainer` (Step 7, built entirely from already-returned fields — no new backend needed), `AccuracyOutcomeScatter` (Step 4, a scatter not a line — connecting points would imply an ordering the models don't have).
- **`DecisionChain`** gained a 9th stage, **Outcome**, driven by the same `OutcomeResult` object the dashboard fetches for the `OutcomeSection`.
- **`/dashboard`** restructured into Step 8's exact hierarchy: Decisions requiring attention → Why this decision → Business impact → Confidence → Human decision → Outcome.
- **`/research`** gained a "Forecast accuracy vs. business outcome (RQ2/H2)" section with the new scatter chart.
- **Scope decision** (disclosed, not silent): no separate recommendation-detail route was added for Step 13 — `/dashboard`'s existing list+detail-pane layout already satisfies the "rich detail view" requirement and was enriched in place rather than duplicated into a second route. See `docs/MILESTONE_3_OUTCOME_AUDIT.md` §9.

### Real bugs found and fixed

1. **Accuracy-vs-outcome scatter label clipped off-canvas** — VQR's real wMAPE (390%, dramatically worse than the classical models) placed its point at the far right of the plot, and its text label ran past the SVG's `viewBox` boundary, rendering invisible. Fixed: labels within 60px of the right edge flip to render left of their point (`text-anchor="end"`), verified with a reload + screenshot.

### Tested

- `npx tsc --noEmit`: 0 errors. `npm run lint`: 0 errors. `npm run build`: succeeds, all 6 routes unchanged.
- `backend/tests/`: 60/60 passed (851.8s), including all 11 new Milestone 3 tests (outcome LIVE/manual/negative-rejected/404, baseline PENDING/LIVE/own-model-is-baseline, accuracy-vs-outcome PENDING/LIVE, `forecast_run_id` round-trip).
- Root `tests/` (qsci_core) suite: unchanged pass count from the Milestone 2 baseline (176 passed, 1 xfailed) — this milestone touched only `qsci_core/persistence/models.py` (additive column) and `qsci_core/persistence/db.py` (additive `forecast_run_id` parameter, default `None`), no qsci_core test depends on either.

### Browser Verified

Real backend (port 8010) at 1440×900: created a fresh LightGBM recommendation end-to-end and confirmed `forecast_run_id` populated; outcome LIVE with real predicted-vs-actual (64.0 vs. 53.6, M5 held-out sales); baseline LIVE comparing seasonal_naive (wMAPE 37.2, cost $3,550.7) against the lightgbm decision (wMAPE 25.6, cost $1,463.6) — both real, both ILLUSTRATIVE-labeled where appropriate; full Approve flow (fill approver → click Approve → backend-confirmed status change → DecisionChain's Human Decision stage LIVE → Outcome section persists). Adversarial: invalid recommendation id 404s on both new endpoints, negative outcome value 422s, unknown series_id on accuracy-vs-outcome returns PENDING with an empty point list — no fabricated fallback anywhere. Pre-Milestone-3 recommendations (`forecast_run_id=null`) correctly show PENDING outcome/baseline with a specific, honest explanation.

### Mobile

True 390×844 this time (`emulate` produced a genuine `window.innerWidth===390`, unlike Milestone 2's ~516px floor) — `DecisionCard` list, confidence decomposition grid, `RiskExplainer`'s `<dl>` (wraps instead of clipping), and `BaselineComparisonCard`'s table (`min-w-[420px]` inside `overflow-x-auto`, visible scrollbar) all verified clean at true mobile width. See `docs/QSCI_VISUAL_QA_REPORT.md`'s Milestone 3 section.

### Accessibility

`AccuracyOutcomeScatter` ships an `sr-only` textual-table equivalent (model/wMAPE/total_cost/evidence) and per-point `<title>` tooltips, consistent with Milestone 2's chart components. Confidence/risk/baseline/outcome cards use real `<dl>`/`<table>`/heading structure, not div soup.

### Regression Protection

`/inventory`, `/optimization`, and `/demand` unchanged this milestone except the VQR-runtime copy fix already shipped in Milestone 2 — spot-verified at 390px with no new issues. The Approve/Modify/Reject flow's underlying logic (`decide`/`submitModify`) is unchanged; only its data-refresh set grew to include `refreshOutcome`.

### Commit

`phase-6: connect financial impact confidence and outcomes` — see final report.
