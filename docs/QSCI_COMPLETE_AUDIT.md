# QSCI Complete Audit — Presentation-Readiness Pass

Date: 2026-08-20. Scope: this pass targets Track 1 (polish + harden what exists), per
explicit user direction — no new pages (`/risk`, `/scenarios`, `/copilot`, `/models`,
`/data`, `/settings` remain PENDING, not built tonight).

## Working (real backend, real data, tested, committed)

| Area | State | Evidence |
|---|---|---|
| `/` (landing) | Minimal single-hero page — functional, not presentation-quality | `frontend/app/page.tsx`, 55 lines |
| `/dashboard` | Decision Center — DecisionCard list, DecisionChain (10 stages incl. Outcome), WhyPanel, BaselineComparisonCard, ConfidenceExplainer, RiskExplainer, Approve/Modify/Reject, OutcomeSection | Milestones 1 & 3, commits `1a72c8b`, `f75c743` |
| `/demand` | Seasonal Naive / LightGBM / VQR, real RMSE/MAE/wMAPE/Bias/Runtime, LIVE/RESEARCH labels | Milestone 1, live-verified Milestone 2 Step 19 |
| `/inventory` | Real qsci_core reorder-point table, SKU→Dashboard navigation | Milestone 1 |
| `/optimization` | OR-Tools/OR-Tools-on-QUBO/annealing/QAOA, fair-comparison separation preserved, route viz, scalability charts | Milestone 2, commit `e5a51e1` |
| `/research` | Benchmarks, scalability, noise, routing, accuracy-vs-outcome scatter — RESEARCH-labeled throughout | Milestone 2 & 3 |
| Backend | `/forecast`, `/optimize`, `/optimization`, `/recommend`, `/recommendations/{id}/{approve,reject,modify,outcome,baseline}`, `/audit`, `/research/*`, `/data/*` | 60/60 backend tests passing |
| qsci_core | forecasting (classical+quantum), optimization (classical+quantum), risk, financial, confidence, recommendation, persistence | 176 passed/1 xfailed, unchanged baseline |

## Broken / Incomplete

- Nothing currently broken in the 5 existing app routes — last full regression (backend 60/60, qsci_core 176/1xfail) was clean as of commit `f75c743`.
- Landing page does not yet communicate the research story (§10-11 of the prompt) — this is tonight's primary work item.
- No dedicated "presentation mode" / rehearsed demo script exists yet.

## Disconnected / Duplicated / Mocked

- None found. Frontend has never independently recreated a formula (verified in Milestones 0-3 audits) — all math stays in `qsci_core`, surfaced via typed API responses.

## Explicitly Out of Scope Tonight (remain PENDING, disclosed)

`/risk`, `/scenarios`, `/copilot`, `/models`, `/data`, `/settings` — per user direction, not built. Their absence from the sidebar is intentional, not a bug.

## Tonight's Plan (sequence, per user's Hard Stop Rule)

1. Landing page redesign (`/`) — the 12-section presentation-quality experience.
2. Design-consistency pass across existing pages.
3. Dashboard / Demand / Inventory / Optimization / Research polish (presentation clarity, not new features).
4. Golden Path integration test (real backend, one continuous run).
5. Browser test (every existing route, every interactive element) → `docs/BUTTON_INTERACTION_MATRIX.md` update.
6. Responsive test (390/768/1280/1440) → `docs/QSCI_VISUAL_QA_REPORT.md` update.
7. Accessibility spot-check.
8. Adversarial pass (invalid states, missing data, backend-down).
9. Full regression suite (pytest × 2, lint, tsc, build).
10. `docs/PRESENTATION_READINESS_REPORT.md` + final report.

Each step stops on any P0/P1/P2 before proceeding, per the Hard Stop Rule.
