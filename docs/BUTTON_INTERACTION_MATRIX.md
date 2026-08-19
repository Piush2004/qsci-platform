# Button / Interaction Matrix

Status: **PARTIAL** — covers the Golden Path surface built so far (dashboard, demand, inventory, research, landing). Every row below was manually exercised in a real browser against the real backend (Chrome, this session) unless noted PENDING. This is not yet the full persona/E2E sweep CLAUDE.md's Phase 6 spec calls for — see `docs/PHASE_6_PROGRESS_REPORT.md` for what remains.

| Location | Element | Action | Expected | Actual | API | Status | Evidence |
|---|---|---|---|---|---|---|---|
| `/` | "Open Decision Center" link | Navigate | Goes to `/dashboard` | Works | — | PASS | Manual click, this session |
| TopBar (all app pages, `<lg` widths) | Hamburger menu button | Click | Opens mobile sidebar overlay with backdrop | Works — verified at 390px, screenshotted mid-open (Milestone 0) | — (client-side) | PASS | `docs/QSCI_VISUAL_QA_REPORT.md` Milestone 0 |
| Mobile nav overlay | Backdrop click | Click | Closes the overlay | Works (Milestone 0) | — (client-side) | PASS | `docs/QSCI_VISUAL_QA_REPORT.md` Milestone 0 |
| `/` | "Research Lab" link | Navigate | Goes to `/research` | Works | — | PASS | Manual click, this session |
| Sidebar (all pages) | "Decision Center"/"Demand"/"Inventory"/"Research Lab" links | Navigate | Highlights active route, loads page | Works | — | PASS | Manual click, this session |
| `/dashboard` | "Generate recommendation (LightGBM)" | Click | Runs `POST /forecast` (lightgbm) then `POST /recommend`, adds a PENDING recommendation to the list, auto-selects it | Works — verified real reorder-point/risk numbers computed from live M5 data | `/forecast`, `/recommend` | PASS (after fixing a real reorder-point unit bug found during this verification — see below) | Screenshot + backend log, this session |
| `/dashboard` | Recommendation list item | Click | Selects it, loads its DecisionChain + WhyPanel + audit events | Works | `/audit?recommendation_id=` | PASS | Manual click, this session |
| `/dashboard` | DecisionChain stage buttons (Data/Forecast/.../Audit) | Click | Toggles that stage's detail panel open/closed | Works | — (client-side) | PASS | Manual click, this session |
| `/dashboard` | Approver name field | Type | Enables Approve/Reject once non-empty | Works | — | PASS | Manual click, this session |
| `/dashboard` | "Approve" button | Click | `POST /recommendations/{id}/approve`, status flips to APPROVED, buttons disappear, Human Decision stage turns LIVE | Works | `/recommendations/{id}/approve` | PASS | Screenshot, this session |
| `/dashboard` | "Reject" button | Click | `POST /recommendations/{id}/reject`, status flips to REJECTED | Not manually clicked this session (approve path was exercised instead) — covered by `backend/tests/test_api.py::test_approve_reject_modify_workflow`-adjacent tests | `/recommendations/{id}/reject` | PASS (API-test evidence only) | `backend/tests/test_api.py` |
| `/demand` | "Run forecast" (Seasonal Naive) | Click | Runs synchronously, shows wMAPE/RMSE/bias/runtime | PENDING — API-tested (`test_forecast_seasonal_naive_synchronous_and_real`), not re-verified in browser this session | `/forecast` | PASS (API-test evidence) | `backend/tests/test_api.py` |
| `/demand` | "Run forecast" (LightGBM) | Click | Same, plus quantile-crossing-fixed p10/p50/p90 | PENDING — API-tested, not re-verified in browser this session | `/forecast` | PASS (API-test evidence) | `backend/tests/test_api.py` |
| `/demand` | "Run forecast" (VQR) | Click | Dispatches async, polls until COMPLETE/FAILED, shows "forecast_stability: NOT AVAILABLE FOR THIS MODEL" | PENDING — API-tested (~5-8 min per real run), not re-verified in browser this session | `/forecast`, `/forecast/{id}` | PASS (API-test evidence) | `backend/tests/test_api.py::test_recommend_vqr_forecast_has_no_forecast_stability` |
| `/inventory` | SKU link | Click | Navigates to `/dashboard` | Works by construction (plain link) — not manually clicked this session | — | PENDING (untested in browser) | — |
| `/research` | (read-only page, no interactive elements beyond nav) | — | Loads real Phase 4/5 JSON from `/research/*` | Works | `/research/benchmarks`, `/scalability`, `/noise` | PASS | Screenshot, this session |

## Real bug found and fixed during this verification pass

Manually exercising "Generate recommendation" surfaced a genuine unit-consistency bug in `backend/app/services/recommendation_service.py`: `avg_daily_demand = p50 / horizon` double-divided an already-daily forecast mean, shrinking the reorder point far below actual daily demand and producing a nonsensical ~93% stockout-risk reading for an ordinary forecast. Fixed (removed the redundant division) and covered by a new regression test, `backend/tests/test_api.py::test_recommend_reorder_point_is_plausible_relative_to_daily_demand`. This is exactly the class of bug a11y/E2E testing is meant to catch — no unit test asserted a *plausible* risk magnitude, only that the pipeline ran without raising.

## Not yet covered (disclosed, not silently skipped)

- `/inventory` and `/demand` interactive elements not re-verified live in-browser after the reorder-point fix (only `/dashboard` and `/research` were).
- No Playwright test suite exists yet — all "PASS" verdicts above are either manual Chrome-driven verification (this session) or backend API-test evidence, not automated browser regression tests.
- No persona-based testing (executive/planner/analyst/researcher/adversarial/mobile/etc.) has been run.
- No accessibility (a11y) audit has been run.
- No 10-round adversarial E2E sweep has been run.
- Marketing page beyond the single landing hero, `/settings`, `/scenarios`, `/copilot`, `/models`, `/data`, `/risk`, `/optimization` pages do not exist yet.
