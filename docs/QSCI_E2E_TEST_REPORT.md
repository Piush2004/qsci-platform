# QSCI E2E Test Report

Status: no automated E2E suite exists yet — Playwright setup is Milestone 8 in `docs/QSCI_PHASE_6_MASTER_PLAN.md`, sequenced deliberately early (in parallel with Milestone 3) but not yet reached. This report currently records **manual** browser-driven verification only, with real evidence (screenshots, console-message checks, HTTP status checks) per milestone. It will convert to automated Playwright results once Milestone 8 lands.

---

## Milestone 0 — Design System + Global Visual Foundation

Date: 2026-08-20

| Test | Input | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|
| All 5 routes load | GET `/`, `/dashboard`, `/demand`, `/inventory`, `/research` | HTTP 200 | HTTP 200 on all 5 | PASS | `curl` status checks, this session |
| No console errors on load | Visit each of the 5 routes | 0 console errors | 0 console errors on all 5 (checked via `list_console_messages` after each navigation) | PASS | This session |
| Golden Path data survives the visual rework | Load `/dashboard`, inspect existing (Phase 6) recommendation | DecisionChain + WhyPanel render identically to Phase 6's verified output, now via `Card`/`PageHeader` | Confirmed — same real data, same 10-stage chain, same confidence breakdown, now consistently styled | PASS | Screenshot, this session |
| Mobile nav toggle | Click hamburger icon at 390px width | Sidebar overlay opens with backdrop; click again or click backdrop closes it | Opens correctly with dimmed backdrop, Decide/Understand groups visible | PASS | Screenshot, this session |
| Sidebar overflow at mobile width | Load `/dashboard` at 390px, before the fix | (adversarial — expected to reveal a bug) | Content cut off, horizontal scroll appeared | CONFIRMED BUG, then FIXED | Before/after screenshots, this session |
| `prefers-reduced-motion` rule present | Inspect `document.styleSheets` for a `prefers-reduced-motion` media rule | Rule present | Rule present, confirmed via `evaluate_script` | PASS | This session |
| Static validation | `tsc --noEmit`, `eslint`, `next build` | 0 errors, build succeeds | 0 errors on all three (2 pre-existing lint errors found and fixed as part of this pass) | PASS | This session |

No adversarial-input testing (malformed data, backend-unavailable, slow backend, etc.) was performed this milestone — Milestone 0 touched only presentation components with no new data-fetching logic, so the existing Phase 6 adversarial coverage (duplicate approval, invalid state transition, invalid IDs — see `backend/tests/test_api.py`) remains the relevant evidence and was not re-run since nothing it covers changed.
