# QSCI — Presentation Readiness Report

Date: 2026-08-20. Track: **Polish + harden what exists** (user-directed — no new pages built).

## 1. What Was Implemented

- **Landing page (`/`) full rewrite** — 12 sections per the presentation spec: Hero, Problem, Decision Chain,
  Real Data Evidence (M5/CVRPLIB/Amazon Last-Mile), Classical vs. Quantum forecasting (real wMAPE numbers),
  Classical vs. quantum-inspired routing (real cost/runtime numbers), Financial Impact, Explainability,
  Research Questions (all 6 RQ/H pairs), Architecture, Evidence Standard legend, CTA. Sticky header with
  `QSCI` brand link + "Open Decision Center". Proper `<main>`/`<header>` landmarks.
- **Real bug fixed**: `sr-only` applied directly to a `<table>` inflated `document.documentElement.scrollWidth`
  past the viewport (799px vs. 768px on `/optimization` at tablet width) even though nothing was visually
  clipped — a table's intrinsic layout width doesn't reliably respect `sr-only`'s clip/1px constraints in all
  browsers. Fixed in all 3 affected components (`ScalabilityChart`, `RouteVisualization`, `AccuracyOutcomeScatter`)
  by moving `sr-only` to a wrapping `<div>`.
- No changes to `qsci_core`, backend routes, or existing page logic — this pass was frontend-presentation and
  one cross-cutting layout fix only, per the user's explicit "protect existing research" directive.

## 2. What Was Tested

- `npx tsc --noEmit`: 0 errors.
- `npm run lint`: 0 errors.
- `npm run build`: succeeds, all 6 routes (`/`, `/dashboard`, `/demand`, `/inventory`, `/optimization`, `/research`).
- `backend/tests/`: **60/60 passed** (1766.1s — VQR-heavy tests dominate runtime; no test infrastructure change).
- Root `tests/` (qsci_core): **176 passed, 1 xfailed** — unchanged from every prior milestone's baseline, zero regressions.
- Full Golden Path integration test against the real running backend (not the test client): Forecast → Risk →
  Financial → Confidence → Recommendation → Outcome → Baseline → Approve → Audit, one continuous `curl` sequence,
  every stage real (see §10 below for the actual values).
- Adversarial pass: duplicate approval, reject-after-approve, modify without qty, negative qty, huge qty,
  infinite qty, invalid recommendation id, invalid forecast_run_id, invalid CVRPLIB instance, malformed JSON,
  backend killed mid-session and restarted. All produced honest, correct responses — no crash, no fabricated data.

## 3. Browser Routes Tested

`/`, `/dashboard`, `/demand`, `/inventory`, `/optimization`, `/research` — all reloaded and checked for console
errors after both changes (landing rewrite + sr-only fix). None found on any page.

## 4. Buttons/Interactions Tested

See `docs/BUTTON_INTERACTION_MATRIX.md`'s "Presentation-Readiness Pass" section for the full PAGE/ELEMENT/ACTION/
EXPECTED/ACTUAL/STATUS/EVIDENCE table (18 rows, this pass).

## 5. Responsive Sizes Tested

| Size | Result |
|---|---|
| 390×844 (true, confirmed via `window.innerWidth`) | PASS on all 6 routes, before and after the sr-only fix comparison |
| 768×1024 | PASS on all 6 routes (one real bug found and fixed on `/optimization`, see §1) |
| 1280×800 | Covered by the 1440×900 pass — no breakpoint between them in this design system |
| 1440×900 | PASS on all 6 routes |

## 6. Accessibility Checks

- Landmark structure: landing page now has a `banner` (header) and `main` region, confirmed via the accessibility
  tree snapshot (previously no explicit landmarks).
- Heading hierarchy: h1 (hero) → h2 (every section) throughout the landing page, verified via snapshot — no
  skipped levels.
- Keyboard focus: links retain the browser's native `:focus-visible` outline (not suppressed by CSS) — confirmed
  by programmatically focusing a link and reading `getComputedStyle().outlineStyle === "auto"`.
- Existing `sr-only` textual-table equivalents (route maps, scalability charts, accuracy scatter) remain present
  and correctly hidden visually while readable to assistive tech — the fix in §1 corrected a *layout* side effect,
  not the accessibility semantics, which were already correct.
- Not a full WCAG 2.2 AA audit — spot-checked, consistent with every prior milestone's disclosed scope.

## 7. Bugs Discovered

1. `sr-only` on a `<table>` element (not a wrapping `<div>`) inflates document scroll width — real, cross-cutting, found via a deliberate 768px overflow sweep (`docScrollWidth` vs. `innerWidth`), not a screenshot.

## 8. Bugs Fixed

1. Fixed in all 3 affected components — re-verified at 390px and 768px, before and after a live optimization run (so the affected table element is actually present in the DOM), on both `/optimization` and `/research`.

## 9. Remaining PENDING Features (disclosed, not built this session)

`/risk`, `/scenarios`, `/copilot`, `/models`, `/data`, `/settings` — explicitly out of scope per user direction
("do not overbuild... a smaller application with a flawless Golden Path is much better for tomorrow's presentation
than a larger application with half-working pages"). Their absence from the sidebar is intentional.

## 10. Golden Path Result — Real Values From This Session

```
1. POST /forecast {model: lightgbm, horizon: 14}        → run_id=10
2. POST /recommend {forecast_run_id: 10}                → recommendation id=7
     forecast: p10=45.1, p50=64.0, p90=89.0
     reorder_point=217.0, suggested_order_qty=153.0
     risk: 0.0% (LOW)
     confidence: 83.4% (data_quality=1.00, forecast_stability=0.59, model_consensus=1.00, backtest_performance=0.74)
     financial: total_cost=$1,463.60/yr (ILLUSTRATIVE)
3. GET /recommendations/7/outcome                        → LIVE, kind=backtest_actual
     predicted=64.0 vs. actual=53.6 (real M5 held-out sales), error=-10.4 (-19.3%)
4. GET /recommendations/7/baseline                        → LIVE
     seasonal_naive: wMAPE=37.2%, reorder_point=207.4, total_cost=$3,550.7
     lightgbm (this decision): wMAPE=25.6%, reorder_point=217.0, total_cost=$1,463.6
5. POST /recommendations/7/approve {approver: "Golden Path Test"} → status=APPROVED
6. GET /audit?recommendation_id=7                          → [APPROVAL_APPROVE, RECOMMENDATION_CREATED]
```

**RESULT: PASS.** Every stage produced a real, backend-computed value. No stage was skipped, mocked, or fabricated.

## 11. LIVE / RESEARCH / ILLUSTRATIVE / PENDING Inventory (what you'll be asked to explain)

| Item | Label | Why |
|---|---|---|
| M5/CVRPLIB/Amazon Last-Mile dataset facts | LIVE | Real, verified, previously ingested datasets |
| Seasonal Naive, LightGBM forecasts | LIVE | Computed from real M5 data, right now |
| VQR forecast | RESEARCH | Real experiment, not production-integrated (Phase 2/2.1's documented finding: classical wins) |
| Risk (stockout probability) | LIVE | Real computation from forecast quantiles |
| OR-Tools / OR-Tools-on-QUBO / Simulated Annealing | LIVE / LIVE / RESEARCH | Real solves; annealing is RESEARCH per its classical-simulator-not-hardware status |
| QAOA | RESEARCH | Real quantum circuit execution (simulator), documented runtime wall |
| Financial impact ($ figures) | ILLUSTRATIVE | Real formulas, documented (not measured) per-unit cost assumptions |
| Confidence decomposition | LIVE | Real 4-factor computation; VQR's forecast_stability is explicitly NOT AVAILABLE, never guessed |
| Outcome (predicted vs. actual) | LIVE (`backtest_actual`) | Real M5 held-out sales — explicitly disclosed as a backtest actual, not a live post-decision outcome |
| Routing → dollar savings | PENDING | Explicitly disclosed gap — no real per-stop cost data exists, not wired into the approval chain |
| `/risk`, `/scenarios`, `/copilot`, `/models`, `/data`, `/settings` | PENDING | Not built this session, by design |

## 12. Known Limitations

- No real D-Wave QPU or quantum hardware was used anywhere in this project — annealing is always classical-CPU
  simulated annealing, QAOA always runs on a statevector or Aer simulator.
- VQR's statistical comparison against classical (Phase 2.1) was not significant at n=14 — disclosed as
  insufficient statistical power, not claimed as either a win or a loss beyond what the data supports.
- QAOA has a measured runtime wall — real numbers on the landing page and `/optimization` (40.9s at N=4, growing
  steeply with problem size).
- Financial dollar figures are illustrative throughout the product — no public dataset provides real per-unit
  holding/ordering/stockout costs for M5 or Last-Mile items.
- `/risk`, `/scenarios`, `/copilot`, `/models`, `/data`, `/settings` do not exist — PENDING, disclosed, not hidden.
- Presentation-mode caching: VQR training takes minutes in this environment — do not re-trigger it live during
  the demo unless you have time to wait; the already-persisted VQR run on `/demand` and the Research Lab's
  pre-computed benchmark numbers are sufficient evidence without a live re-run.

## Demo Sequence (rehearsed)

1. Open `/` — "QSCI is not another forecasting dashboard." Scroll through the Decision Chain and Research
   Questions sections.
2. Open `/dashboard` — show the DecisionCard list, select a recommendation, walk the DecisionChain's 10 stages.
3. Open the WhyPanel + ConfidenceExplainer — explain the 4-factor confidence decomposition and why VQR can't
   produce forecast stability.
4. Open `/demand` — run (or point to already-run) Seasonal Naive vs. LightGBM vs. VQR; explain that classical
   wins, per H1's expectation.
5. Open `/optimization` — point to the pre-computed Phase 3 comparison table (fast, no live wait needed);
   optionally trigger a live OR-Tools-on-QUBO run (sub-second) to show the route visualization.
6. Return to `/dashboard`, approve the selected recommendation, show the audit trail update and the Outcome
   section's real predicted-vs-actual comparison.
7. Return to `/` or `/research` — close on "the question isn't whether quantum looks impressive, it's where it
   actually earns its place," pointing at the honest RESEARCH/PENDING labels throughout.
