# Button / Interaction Matrix

Status: **PARTIAL** — covers the Golden Path surface built so far (dashboard, demand, inventory, research, landing). Every row below was manually exercised in a real browser against the real backend (Chrome, this session) unless noted PENDING. This is not yet the full persona/E2E sweep CLAUDE.md's Phase 6 spec calls for — see `docs/PHASE_6_PROGRESS_REPORT.md` for what remains.

**Correction (Milestone 1)**: Milestone 0's "mobile (390×844) verified" claims were tested using a browser-window-resize tool that, on inspection this milestone, actually floors at ~500px in this environment (`window.innerWidth` measured 500, not 390, despite the tool reporting success at the requested size) — not caught at the time because 500px still looked plausibly "mobile" in the screenshot. Milestone 1 re-verified using true CDP device-emulation (`emulate` tool's `viewport` param, confirmed `window.innerWidth === 390` before trusting any screenshot) and found two real bugs invisible at 500px — see below. All Milestone 1 mobile rows use verified-true-390px evidence; Milestone 0's original mobile screenshots are superseded, not retracted (the fixes described there were still real, just under-tested).

| Location | Element | Action | Expected | Actual | API | Status | Evidence |
|---|---|---|---|---|---|---|---|
| `/` | "Open Decision Center" link | Navigate | Goes to `/dashboard` | Works | — | PASS | Manual click, this session |
| TopBar (all app pages, `<lg` widths) | Hamburger menu button | Click | Opens mobile sidebar overlay with backdrop | Works — verified at true 390px (Milestone 1) | — (client-side) | PASS | `docs/QSCI_VISUAL_QA_REPORT.md` Milestone 1 |
| Mobile nav overlay | Backdrop click | Click | Closes the overlay | Works | — (client-side) | PASS | `docs/QSCI_VISUAL_QA_REPORT.md` Milestone 0 |
| `/` | "Research Lab" link | Navigate | Goes to `/research` | Works | — | PASS | Manual click, this session |
| Sidebar (all pages) | "Decision Center"/"Demand"/"Inventory"/"Research Lab" links | Navigate | Highlights active route, loads page | Works | — | PASS | Manual click, this session |
| `/dashboard` | "Generate recommendation (LightGBM)" | Click | Runs `POST /forecast` (lightgbm) then `POST /recommend`, adds a PENDING recommendation to the list, auto-selects it | Works — verified real reorder-point/risk numbers computed from live M5 data | `/forecast`, `/recommend` | PASS (Phase 6 reorder-point unit bug fixed prior to this milestone) | Screenshot + backend log |
| `/dashboard` | Recommendation list item | Click | Selects it, loads its DecisionChain + WhyPanel + audit events | Works | `/audit?recommendation_id=` | PASS | Manual click, this session |
| `/dashboard` | DecisionChain stage buttons (Data/Forecast/.../Audit) | Click | Toggles that stage's detail panel open/closed | Works | — (client-side) | PASS | Manual click, this session |
| `/dashboard` | Approver name field | Type | Enables Approve/Modify/Reject once non-empty | Works | — | PASS | Manual click, this session |
| `/dashboard` | "Approve" button | Click | `POST /recommendations/{id}/approve`, status flips to APPROVED, buttons disappear, Human Decision stage turns LIVE | Works | `/recommendations/{id}/approve` | PASS | Screenshot, this session |
| `/dashboard` | Audit stage panel | Click, after Approve/Modify | Shows the just-created `APPROVAL_*` event immediately | **Was BROKEN** (stale — only refreshed on `selectedId` change, not after a decide/modify action) — **FIXED this milestone**, refetches audit alongside the recommendation list on every decide/modify success | `/audit?recommendation_id=` | PASS (after fix) | Screenshot before/after, this session |
| `/dashboard` | "Modify" button | Click | Opens `ModifyPanel` with the current quantity prefilled | Works | — (client-side) | PASS | Screenshot, this session |
| `ModifyPanel` | Quantity field | Type invalid (negative) | Shows "Quantity cannot be negative.", disables Confirm, `aria-invalid`/`aria-describedby`/`role="alert"` wired | Works | — (client-side validation) | PASS | Screenshot + a11y-tree snapshot, this session |
| `ModifyPanel` | Reason field | Leave empty | Shows "A reason is required for every modification.", disables Confirm | Works | — (client-side validation) | PASS | Screenshot + a11y-tree snapshot, this session |
| `ModifyPanel` | Quantity + Reason valid | Fill both, click Confirm | `POST /recommendations/{id}/modify`, status flips to MODIFIED, panel closes, audit shows `APPROVAL_MODIFY` with the reason recorded | Works | `/recommendations/{id}/modify` | PASS | Screenshot, this session |
| `ModifyPanel` | "Cancel" | Click | Closes panel without submitting | Works | — | PASS | Manual click, this session |
| `/dashboard` | Duplicate approve/reject/modify on a decided recommendation | (attempted) | Backend 409 if reached | **Prevented at the UI layer** — action buttons only render when `status === "PENDING"`, so a decided recommendation offers no way to re-trigger the action from a single session/tab. Backend's 409 guard (`test_duplicate_approval_rejected`, `test_invalid_state_transition_reject_after_approve`) remains the defense for races (e.g. two tabs) | `/recommendations/{id}/approve\|reject\|modify` | PASS (prevention, not just error-handling) | Backend tests + UI inspection |
| `/dashboard` | Backend stopped, page reloaded | Reload | Honest "Backend unavailable" message, 0 fabricated recommendations | Works | — | PASS | Screenshot, this session |
| `/dashboard` mobile (true 390px) | Full Golden Path: select → fill approver → Approve | Tap | Works identically to desktop | **Was BROKEN twice** (see below) — **FIXED**, now works end-to-end | `/recommendations/{id}/approve` | PASS (after 2 fixes) | Screenshots before/after, this session |
| `/demand` | "Run forecast" (Seasonal Naive) | Click | Runs synchronously, shows wMAPE/RMSE/bias/runtime | PENDING — API-tested (`test_forecast_seasonal_naive_synchronous_and_real`), not re-verified in browser this session | `/forecast` | PASS (API-test evidence) | `backend/tests/test_api.py` |
| `/demand` | "Run forecast" (LightGBM) | Click | Same, plus quantile-crossing-fixed p10/p50/p90 | PENDING — API-tested, not re-verified in browser this session | `/forecast` | PASS (API-test evidence) | `backend/tests/test_api.py` |
| `/demand` | "Run forecast" (VQR) | Click | Dispatches async, polls until COMPLETE/FAILED, shows "forecast_stability: NOT AVAILABLE FOR THIS MODEL" | PENDING — API-tested (~5-8 min per real run), not re-verified in browser this session | `/forecast`, `/forecast/{id}` | PASS (API-test evidence) | `backend/tests/test_api.py::test_recommend_vqr_forecast_has_no_forecast_stability` |
| `/demand` mobile (true 390px) | Page load, card layout | — | Cards stack full-width, no overflow | Works — was previously untested at true mobile width; the same missing-base-`grid-cols-1` bug as `/dashboard` was found and fixed here too | — | PASS (after fix) | Screenshot, this session |
| `/inventory` | SKU link | Click | Navigates to `/dashboard` | Works by construction (plain link) — not manually clicked this session | — | PENDING (untested in browser) | — |
| `/inventory` mobile (true 390px) | Table | — | Contained horizontal scroll within the table's own Card, no page-level overflow | Works as designed (documented `overflow-x-auto` stopgap, not a bug) | — | PASS | Screenshot, this session |
| `/research` | (read-only page, no interactive elements beyond nav) | — | Loads real Phase 4/5 JSON from `/research/*` | Works | `/research/benchmarks`, `/scalability`, `/noise` | PASS | Screenshot, this session |

## Real bugs found and fixed this milestone

1. **Audit panel went stale after approve/reject/modify.** Only `selectedId` changing triggered a refetch; deciding on the currently-selected recommendation didn't change `selectedId`, so the audit trail silently failed to show the just-created event until the user navigated away and back. Fixed: `decide()`/`submitModify()` now refetch both the recommendation list and the audit trail on success.
2. **Backend 500 crash on non-finite `modified_qty`.** Sending `Infinity` for a quantity should have produced a clean 422, but FastAPI's default validation-error handler tries to echo the rejected value back in the response body, and Starlette's `JSONResponse` enforces strict JSON (`allow_nan=False`) — so validating an invalid input crashed the *error response itself*. Fixed with a custom `RequestValidationError` handler that sanitizes non-finite floats before serializing. Caught by a new adversarial test, not manual browser testing.
3. **`ModifyPanel` showed raw floating-point precision** ("152.99897648241702 units") instead of a rounded, human-readable number — found via manual browser testing, not a unit test (no test asserted display *formatting*). Fixed with a `fmt()` helper, consistent with `WhyPanel`'s existing pattern.
4. **True mobile bug #1** (390px, not caught in Milestone 0 due to the tooling issue above): the dashboard's `grid lg:grid-cols-[320px_1fr]` had no base `grid-cols-1` for below-`lg` widths — CSS grid's implicit auto-placement compressed/clipped the recommendation list and WhyPanel text instead of stacking them. Same bug independently present on `/demand`. Fixed on both pages.
5. **True mobile bug #2** (390px): the approve/modify/reject action bar's approver-name input was squeezed to near-zero width next to three buttons in a single flex row. Fixed: the row now stacks (`flex-col sm:flex-row`) — input gets its own full-width row below `sm`, buttons wrap below it.

## Not yet covered (disclosed, not silently skipped)

- No Playwright test suite exists yet — all "PASS" verdicts above are either manual Chrome-driven verification (this session) or backend API-test evidence, not automated browser regression tests.
- No persona-based testing (executive/planner/analyst/researcher/adversarial/mobile/etc.) has been run.
- No formal accessibility (a11y) audit has been run — ARIA wiring on `ModifyPanel`'s validation was spot-checked (`aria-invalid`, `aria-describedby`, `role="alert"` all confirmed present in the a11y tree) but not a full WCAG 2.2 AA pass.
- No 10-round adversarial E2E sweep has been run.
- Marketing page beyond the single landing hero, `/settings`, `/scenarios`, `/copilot`, `/models`, `/data`, `/risk` pages do not exist yet.
- Tablet (768px) re-verification not repeated in Milestone 2 (see the tooling-floor note below).

## Milestone 2 — Optimization Intelligence

**Step 19 note**: Milestone 1 left `/demand`'s and `/inventory`'s actual interactive elements as "API-test evidence only, not browser-verified." Both are live-verified below, closing that gap.

| Location | Element | Action | Expected | Actual | API | Status | Evidence |
|---|---|---|---|---|---|---|---|
| `/demand` | "Run forecast" (Seasonal Naive) | Click | Runs `POST /forecast` (seasonal_naive), shows COMPLETE with real wMAPE/RMSE/Bias/Runtime | wMAPE 37.15%, RMSE 24.50, Bias 15.50, Runtime 0.000s | `/forecast` | PASS | Snapshot, this session |
| `/demand` | "Run forecast" (LightGBM) | Click | Runs `POST /forecast` (lightgbm), completes with real p10/p50/p90-derived metrics, beats naive | wMAPE 25.56%, RMSE 18.08, Bias 10.37, Runtime 4.116s — beats Seasonal Naive as expected | `/forecast` | PASS | Snapshot, this session |
| `/demand` | "Run forecast" (VQR) | Click | Runs `POST /forecast` (vqr), async job polls to COMPLETE, real metrics, honest "forecast stability: NOT AVAILABLE" disclosure | wMAPE 390.34%, RMSE 217.61, Bias 209.39, Runtime 731.684s (~12.2 min) — dramatically worse than both classical models, consistent with H1's default expectation; no fabricated confidence shown | `/forecast`, polled `/forecast/{id}` | PASS | `curl /forecast/7` + snapshot, this session |
| `/inventory` | Table row | Render | Real qsci_core-computed forecast/reorder-point/suggested-order/stockout-risk/confidence/status per SKU | Real values shown (e.g. reorder point 217.0, stockout risk 0.0%/LOW, confidence 83%, status APPROVED) | `/inventory` (backing data) | PASS | Snapshot, this session |
| `/inventory` | SKU name link | Click | Navigates to `/dashboard`, selects that recommendation | Navigates correctly; Decision Center shows an honest "Loading…" / "PENDING DECISIONS (0)" state rather than fabricated data while it fetches | — | PASS | Screenshot, this session |
| `/optimization` | Instance selector | Change (A-n32-k5 → A-n37-k5) | Live-updates Customers/Vehicles/Capacity/BKS from `GET /optimize/instances/{name}` | Customers 31→36, BKS 784→669 | `/optimize/instances/{name}` | PASS | Snapshot, this session |
| `/optimization` | "Run OR-Tools (on QUBO)" | Click | `POST /optimize` (or_tools_qubo), synchronous, comparison table updates from N/A to real values, LIVE badge, route renders | Cost 380.01, feasible, runtime 0.175s, "CP-SAT (quadratic objective, identical QUBO)", route SVG + textual table rendered | `/optimize` | PASS | Snapshot + screenshot, this session |
| `/optimization` | "Run Simulated Annealing" | Click | `POST /optimize` (simulated_annealing), synchronous, comparison table's 2nd column updates | Cost 380.01, feasible, runtime 0.166s, "1000 reads", RESEARCH badge — agrees with the OR-Tools-on-QUBO result | `/optimize` | PASS | Snapshot, this session |
| `/optimize/instances/{name}` | (error path) | `GET` an unknown instance name | 404 with a clear error message | `{"detail":"unknown CVRPLIB instance 'NOT-REAL', must be one of [...]"}`, HTTP 404 | `/optimize/instances/NOT-REAL` | PASS | `curl`, this session |

### Real bugs found and fixed this milestone

1. **Mobile table clipping** — `SolverComparisonTable`'s `<table className="w-full ...">` compressed columns to fit the narrow viewport instead of triggering horizontal scroll, clipping the QAOA column's text. Fixed with `min-w-[560px]`; re-verified with a visible scrollbar and fully legible columns.
2. **VQR runtime label inaccurate** — "~1-5 min to train" undersold the real measured 731.7s (~12.2 min) runtime observed during this milestone's live Step 19 verification. Corrected to "~10-15 min."

### Environment note (mobile tooling)

Neither `resize_page` nor `emulate({viewport: "390x844..."})` produced a true 390px `window.innerWidth` in this session (floored at ~516px regardless of requested size) — this did not reproduce Milestone 1's documented true-390px method. All Milestone 2 "mobile" verification above was done at the achievable ~516px width and is reported as such, not claimed at 390px.

## Milestone 3 — Outcome & Financial Decision Intelligence

| Location | Element | Action | Expected | Actual | API | Status | Evidence |
|---|---|---|---|---|---|---|---|
| `/dashboard` | `DecisionCard` (list) | Click | Selects the recommendation, loads full detail pane | Works — real SKU/forecast/order/risk/confidence/impact shown on the card itself | `/recommendations` | PASS | Snapshot, this session |
| `/dashboard` | `GET /recommendations/{id}/outcome` on select | Auto-fetch | Real backtest actual for a linked run, honest PENDING otherwise | LIVE: predicted 64.0 vs. actual 53.6 (M5 real held-out sales), error −10.4 (−19.3%); PENDING for pre-Milestone-3 recs (no `forecast_run_id`) | `/recommendations/{id}/outcome` | PASS | `curl` + snapshot, this session |
| `/dashboard` | `POST /recommendations/{id}/outcome` (manual entry) | POST | Overrides the backtest-derived figure, `kind:"manual"` | `{"actual_demand_observed":999.0}` → returned `kind:"manual"`, `error:934.99` | `/recommendations/{id}/outcome` | PASS | `curl`, this session |
| `/dashboard` | `POST /recommendations/{id}/outcome`, negative value | POST | 422 | `{"detail":[{"type":"greater_than_equal", ...}]}`, HTTP 422 | `/recommendations/{id}/outcome` | PASS | `curl`, this session |
| `/dashboard` | `GET /recommendations/{id}/baseline` on select | Auto-fetch | LIVE comparison when a same-series/horizon seasonal_naive run exists, PENDING otherwise | LIVE: seasonal_naive wMAPE 37.2/reorder_point 207.4/cost 3,550.7 vs. lightgbm wMAPE 25.6/reorder_point 217/cost 1,463.6, both ILLUSTRATIVE-labeled | `/recommendations/{id}/baseline` | PASS | `curl` + snapshot, this session |
| `/dashboard` | Approve (recommendation with real outcome/baseline attached) | Click | Backend-confirmed status change, DecisionChain's Human Decision stage LIVE, Outcome/Baseline persist through refetch | Works — status PENDING→APPROVED, list re-sorts, action buttons disappear | `/recommendations/{id}/approve` | PASS | Snapshot, this session |
| `/research` | Accuracy-vs-outcome scatter | Render | Real per-model (wMAPE, total_cost) points, PENDING below 2 models | 3 real points (seasonal_naive/lightgbm/vqr) from `GET /research/accuracy-vs-outcome` | `/research/accuracy-vs-outcome` | PASS (after 1 fix — see below) | Screenshot, this session |
| `/research/accuracy-vs-outcome` | unknown series_id | `GET` | PENDING, empty points | `{"status":"PENDING","points":[]}` | `/research/accuracy-vs-outcome?series_id=BOGUS_SERIES` | PASS | `curl`, this session |
| `/recommendations/{id}/outcome`, `/baseline` | invalid recommendation id | `GET` | 404 | `{"detail":"no recommendation with id=999999"}`, HTTP 404 (both endpoints) | — | PASS | `curl`, this session |

### Real bugs found and fixed this milestone

1. **Accuracy-vs-outcome scatter label clipped** — the point with the largest wMAPE (VQR, 390%) placed its text label past the SVG's right edge, rendering it invisible. Fixed: labels within 60px of the right edge flip to render left of their point with `text-anchor="end"`.

### Environment note (mobile tooling) — resolved this milestone

Unlike Milestone 2, `emulate({viewport: "390x844x2,mobile,touch"})` produced a genuine `window.innerWidth === 390` this session (confirmed before every mobile screenshot) — the ~516px floor observed in Milestone 2 did not reproduce. All Milestone 3 mobile rows above (see `docs/QSCI_VISUAL_QA_REPORT.md`'s Milestone 3 section) are true 390px, not a fallback width.

## Presentation-Readiness Pass — Golden Path + Adversarial

| Location | Element | Action | Expected | Actual | API | Status | Evidence |
|---|---|---|---|---|---|---|---|
| Golden Path | Forecast → Recommend → Outcome → Baseline → Approve → Audit, one continuous run | `curl` sequence | Every stage real, backend-confirmed | forecast run 10 → recommendation 7 (wMAPE-backed reorder point 217.0) → outcome LIVE (predicted 64.0 vs. real M5 actual 53.6) → baseline LIVE (seasonal_naive $3,550.7 vs. lightgbm $1,463.6) → approve → APPROVED → audit shows both RECOMMENDATION_CREATED and APPROVAL_APPROVE events | `/forecast`, `/recommend`, `/recommendations/{id}/{outcome,baseline,approve}`, `/audit` | PASS | `curl` transcript, this session |
| `/recommendations/{id}/approve` | duplicate approval | POST twice | 2nd call 409 | `{"detail":"recommendation 7 already decided (status=APPROVED)..."}`, HTTP 409 | — | PASS | `curl`, this session |
| `/recommendations/{id}/reject` | reject an already-approved recommendation | POST | 409 (invalid state transition) | same 409 as above | — | PASS | `curl`, this session |
| `/recommendations/{id}/modify` | no `modified_qty` | POST | 422 | `{"detail":"modified_qty is required for a MODIFY decision"}` | — | PASS | `curl`, this session |
| `/recommendations/{id}/modify` | negative `modified_qty` | POST `-5` | 422 | Pydantic `greater_than_equal` error | — | PASS | `curl`, this session |
| `/recommendations/{id}/modify` | huge `modified_qty` (999999999) | POST | 200, persisted as a real human override | `status:"MODIFIED"`, qty persisted verbatim — no artificial cap (a human is entitled to override with any non-negative finite quantity) | — | PASS | `curl`, this session |
| `/recommendations/{id}/modify` | infinite `modified_qty` | POST `Infinity` | 422, no 500 crash | `{"detail":[{"type":"value_error","msg":"modified_qty must be finite, got inf"}]}` — confirms Milestone 1's non-finite-float exception handler still works | — | PASS | `curl`, this session |
| `/recommendations/999999` | invalid id | GET | 404 | `{"detail":"no recommendation with id=999999"}` | — | PASS | `curl`, this session |
| `/recommend` | invalid `forecast_run_id` | POST `999999` | 422 | `{"detail":"no forecast run with id=999999"}` | — | PASS | `curl`, this session |
| `/optimize/instances/BOGUS` | invalid instance | GET | 404 | `{"detail":"unknown CVRPLIB instance 'BOGUS'..."}` | — | PASS | `curl`, this session |
| `/forecast` | malformed JSON body | POST `not json` | 422 | `{"detail":[{"type":"json_invalid",...}]}` | — | PASS | `curl`, this session |
| `/dashboard` | backend killed, page reloaded | reload | Honest "Backend unavailable" alert, 0 pending, no fabricated data | Confirmed via accessibility snapshot: `alert` role with text "Backend unavailable", "DECISIONS REQUIRING ATTENTION (0 PENDING)" | — | PASS | Snapshot, this session |
| `/dashboard` | backend restarted, page reloaded | reload | Recovers automatically, no stuck error state | `document.body.innerText` no longer contains "Backend unavailable" | — | PASS | `evaluate_script`, this session |
| `/` (new landing page) | "Open Decision Center" (hero + header + CTA, 3 instances) | Click | Navigates to `/dashboard` | All 3 confirmed as real `<a href="/dashboard">` in the accessibility tree | — | PASS | Snapshot, this session |
| `/` | "See the Research Evidence" / "Research Lab" (2 instances) | Click | Navigates to `/research` | Confirmed as real links in the accessibility tree | — | PASS | Snapshot, this session |
| `/optimization` | live "Run OR-Tools (on QUBO)" at 390px | Click | Route section appears with a rendered SVG map + textual table, no page overflow | Cost 380.01, feasible, Route section rendered, `docScrollWidth === innerWidth === 390` | `/optimize` | PASS | Snapshot + `evaluate_script`, this session |

### Real bug found and fixed

See `docs/QSCI_VISUAL_QA_REPORT.md`'s Presentation-Readiness Pass section — `sr-only` applied directly to a `<table>` inflated `document.documentElement.scrollWidth` past the viewport on `/optimization` at 768px (799 vs. 768), even though nothing was visually clipped. Fixed in `ScalabilityChart.tsx`, `RouteVisualization.tsx`, and `AccuracyOutcomeScatter.tsx` by moving `sr-only` to a wrapping `<div>`.

### Automated tests (final regression, this pass)

- `npx tsc --noEmit`: 0 errors. `npm run lint`: 0 errors. `npm run build`: succeeds, all 6 routes.
- `backend/tests/`: 60/60 passed (1766.1s / 29m 26s — VQR-heavy tests dominate runtime).
- Root `tests/` (qsci_core): 176 passed, 1 xfailed — unchanged baseline, zero regressions.
