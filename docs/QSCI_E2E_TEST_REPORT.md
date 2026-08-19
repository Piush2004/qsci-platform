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

---

## Milestone 1 — Close the Golden Path

Date: 2026-08-20

Maps directly to the prompt's Tests A-K.

| Test | Input | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|
| A — Generate | Click "Generate recommendation (LightGBM)" | Real backend result | Real LightGBM forecast + recommendation, backend-computed numbers | PASS | Screenshot, this session |
| B — Inspect | Open DecisionChain stages | Real evidence per stage | All 9 stages show real LIVE/ILLUSTRATIVE/PENDING data from the actual recommendation | PASS | Screenshot, this session |
| C — Why | Open WhyPanel | Real confidence decomposition | 4-factor breakdown (data quality/forecast stability/model consensus/backtest performance), never a bare percentage | PASS | Screenshot, this session |
| D — Approve | Click Approve with approver filled | Backend confirms approval | Status flipped to APPROVED (backend-confirmed, not optimistic), action buttons disappeared, Human Decision stage → LIVE | PASS | Screenshot, this session |
| E — Audit | Open Audit stage after Approve | New audit record exists | **Initially FAILED** — audit panel was stale (only `RECOMMENDATION_CREATED` shown, `APPROVAL_APPROVE` missing) — real bug, fixed this milestone. Re-tested after fix: PASS, both events shown immediately | PASS (after fix) | Before/after screenshots |
| F — Modify | Fill quantity + reason, Confirm | Real backend update | Status → MODIFIED (backend-confirmed), audit shows `APPROVAL_MODIFY` with the exact reason text recorded | PASS | Screenshot, this session |
| G — Invalid Modify | Enter `-10` as quantity | Validation error | "Quantity cannot be negative.", Confirm disabled, `aria-invalid="true"` | PASS | Screenshot + a11y snapshot |
| H — Missing Reason | Leave reason empty | Blocked | "A reason is required for every modification.", Confirm disabled | PASS | Screenshot + a11y snapshot |
| I — Duplicate Approval | Attempt to re-decide an already-decided recommendation | Clear conflict | Prevented at the UI layer (action buttons only render for `status === "PENDING"`) — backend's 409 guard is the underlying defense, covered by `backend/tests/test_api.py::test_duplicate_approval_rejected` and `test_invalid_state_transition_reject_after_approve` (both still passing) | PASS (prevention, stronger than error-handling) | Backend test suite |
| J — Backend Failure | Stop backend, reload | Honest error | "Backend unavailable", 0 fabricated recommendations, no fake success | PASS | Screenshot, this session |
| K — Mobile | Repeat core interactions at true 390px | Usable, no overflow | **Initially FAILED** (2 real bugs — see `docs/QSCI_VISUAL_QA_REPORT.md` Milestone 1) — **FIXED**, then full generate→select→approve flow re-verified working at true 390px | PASS (after 2 fixes) | Before/after screenshots |

### Additional adversarial backend test (new this milestone)

| Test | Input | Expected | Actual | Status |
|---|---|---|---|---|
| Non-finite `modified_qty` | `POST /recommendations/{id}/modify` with `modified_qty: Infinity` | Clean 422 | **Initially a 500** (Starlette's strict-JSON `JSONResponse` crashed trying to echo the rejected `inf` value back in the error detail) — fixed with a custom `RequestValidationError` handler | PASS (after fix) | `backend/tests/test_api.py::test_modify_infinite_quantity_rejected` |

### Static + Backend Test Suites

| Suite | Result |
|---|---|
| `npx tsc --noEmit` | 0 errors |
| `npm run lint` | 0 errors |
| `npm run build` | Succeeds, all 5 routes |
| `backend/tests/` (pytest) | 42/42 passed (36 prior + 6 new: modify negative/infinite/valid quantity, audit-event reason recording, plus the pre-existing modify-requires-qty test) |
| Root `qsci_core` suite (pytest) | 176 passed, 1 xfailed (unchanged from pre-milestone baseline — 0 regressions) |

Still not covered: automated Playwright (Milestone 8), full persona sweep, formal a11y audit beyond the spot-checks noted above.
