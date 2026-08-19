# QSCI Phase 6 Master Implementation Roadmap

Status: **APPROVED, IMPLEMENTATION IN PROGRESS** (Milestone 0 complete)
Date: 2026-08-20

Per CLAUDE.md's priority order (correctness > Golden Path > backend/frontend integration > UX/UI > browser/E2E testing) and the planning prompt's explicit instruction not to create one enormous "build everything" task, this roadmap is broken into milestones, each independently shippable and testable. Priorities: P0 = core/broken workflow, P1 = Golden Path, P2 = major product capability, P3 = UX/research improvement, P4 = polish.

---

## Milestone 0 (P1) — Design System + Global Visual Foundation

**Status: COMPLETE** (2026-08-20) — see `docs/QSCI_IMPLEMENTATION_LOG.md` for full evidence.

Added after the original 10-milestone plan, per the Phase 6 implementation prompt's explicit instruction to start with a design-system foundation before touching individual pages. Delivered: typography scale, motion tokens (with `prefers-reduced-motion` support), `PageHeader`/`Card`/`TopBar`/`AppShell` shared components, applied consistently across all 5 existing pages. Two real bugs found and fixed during this milestone's mandated testing: a mobile sidebar-overflow layout bug (found via the mandated mobile screenshot, not by `npm run build`) and two pre-existing ESLint errors (found by running `npm run lint`, which apparently hadn't been run as part of Phase 6's own verification). Stitch MCP was checked for and confirmed unavailable in this environment — noted honestly rather than skipped silently.

---

## Milestone 1 (P1) — Close the Golden Path's Known Gaps

**Objective**: fix the incompleteness flagged in `docs/PHASE_6_PROGRESS_REPORT.md` before adding new surface area — verify `/demand` and `/inventory` live in-browser post-bugfix, add the "modify quantity" UI the backend already supports.
**Files/modules**: `frontend/app/(app)/dashboard/page.tsx` (add modify UI + quantity input), manual browser verification pass (no new files).
**Dependencies**: none — everything needed already exists.
**Implementation**: add a quantity-edit control + reason field to the dashboard's decision panel, wired to `api.modify()` (already in `lib/api.ts`); re-run the manual Golden Path walkthrough for `/demand` and `/inventory` specifically.
**Tests**: extend `docs/BUTTON_INTERACTION_MATRIX.md` with the newly-verified rows; no new backend tests needed (the `modify` endpoint is already tested).
**Acceptance criteria**: every row in the button matrix reads PASS with live evidence, not "API-test evidence only."
**Risks**: low — UI-only change against an already-tested endpoint.
**Rollback**: revert the single component change; no schema/API impact.

## Milestone 2 (P1) — Outcome Recording (Close the RQ2/H2 Loop)

**Objective**: wire `qsci_core.persistence.db.record_outcome` (exists, unused) to a real endpoint and a UI affordance, closing DATA→...→OUTCOME.
**Files/modules**: `backend/app/api/routes/recommend.py` (new route), `backend/app/schemas/schemas.py` (new schema), `frontend/components/WhyPanel.tsx` or a new `OutcomePanel` (only for APPROVED recommendations).
**Dependencies**: Milestone 1 not required but logically sequenced first (both touch the dashboard).
**Implementation**: `POST /recommendations/{id}/outcome` calling `record_outcome`; guard against recording an outcome on a non-APPROVED recommendation (mirrors the existing duplicate-approval guard pattern).
**Tests**: backend tests mirroring `test_duplicate_approval_rejected`'s pattern for outcome-on-non-approved; one happy-path test.
**Acceptance criteria**: an approved recommendation can have an outcome recorded, visible in its audit trail.
**Risks**: low. **Rollback**: new route + new UI element, trivially revertible.

## Milestone 3 (P1) — Routing / Optimization Page

**Objective**: build `/optimization`, the single largest EXISTS+INCOMPLETE gap (real backend, zero frontend) — surfaces Phase 1 and Phase 3's routing research as a real product decision.
**Files/modules**: `frontend/app/(app)/optimization/page.tsx` (new), extends `Sidebar.tsx`'s link list, new `backend/app/api/routes/optimize.py::list_optimizations` (`GET /optimization`, mirroring `GET /recommendations`).
**Dependencies**: none new — `POST /optimize`, `GET /optimization/{id}` already work.
**Implementation**: page lets a user trigger OR-Tools/annealing/QAOA against a CVRPLIB instance, shows objective/feasibility/gap/runtime side by side per the UI/UX plan's explicit "no quantum winner" framing; QAOA runs use the `LoadingSequence` component (Milestone 6) or, if built first, a simple polling spinner with an honest "this may take several minutes" notice.
**Tests**: one Playwright-style manual walkthrough (or automated if Milestone 8 lands first) triggering all three methods; backend `list_optimizations` gets the same test pattern as `list_recommendations`.
**Acceptance criteria**: a real QAOA run, triggered from the UI, completes and displays real resource metrics (qubits/depth/gates), matching what `/research` already shows for historical runs.
**Risks**: QAOA's genuine multi-minute runtime could read as "broken" without clear loading feedback — mitigate with an explicit runtime-expectation notice sourced from Phase 3/4's measured numbers, not a generic spinner.
**Rollback**: new page + one new list endpoint; no schema change.

## Milestone 4 (P2) — Data Lineage Page

**Objective**: build `/data`, exposing `GET /data/sources` (already real) as a real page.
**Files/modules**: `frontend/app/(app)/data/page.tsx` (new).
**Dependencies**: none.
**Implementation**: table of ingested datasets (name, source, version, record count, date range, quality status, ingested_at), with a "re-ingest" action calling `POST /data/ingest`.
**Tests**: manual browser verification; backend already tested.
**Acceptance criteria**: shows real M5/CVRPLIB/Last-Mile metadata, matching Phase 0's verified numbers.
**Risks**: none significant. **Rollback**: trivial.

## Milestone 5 (P2) — Model Evidence Registry

**Objective**: build `/models`, populate the currently-unused `experiment_results` table, expose it.
**Files/modules**: new `backend/app/services/model_registry_service.py` + a one-off seed script (`backend/scripts/seed_experiment_results.py`) reading `experiments/results/*.json`, new `GET /models` route, `frontend/app/(app)/models/page.tsx`.
**Dependencies**: none.
**Implementation**: seed script parses each phase's result files into `ExperimentResultRecord` rows (model, problem, dataset, metrics, runtime, resources, status, experiment ID — per the feature matrix's exact column spec); the page is a sortable/filterable `DataTable` (new shared component, first real use).
**Tests**: seed-script idempotency test (re-running doesn't duplicate rows); route test.
**Acceptance criteria**: every row traces to a real `experiments/results/*.json` file, clickable through to it.
**Risks**: seed-script scope creep (parsing 6 phases' worth of heterogeneous JSON shapes) — mitigate by starting with Phase 3/4/5's already-uniform `RoutingResult`/unified-schema files, deferring Phase 2's less-uniform shape to a follow-up.
**Rollback**: new table already exists and is empty by default; seed script is additive, safely re-runnable.

## Milestone 6 (P2) — Research Lab Depth Pass

**Objective**: address the Research Integration Plan's flagged gaps — leakage story, QUBO-bug story, statistical tests, resource-scaling charts, and fix `/research`'s current raw-JSON-in-`<pre>` presentation.
**Files/modules**: `frontend/app/(app)/research/page.tsx` (substantial rework), new `EvidenceChart` component, `backend/app/services/research_service.py` (add `get_leakage_story()`, `get_qubo_validation_story()`, extend `get_benchmarks()` to include DM-test/Mann-Whitney results already present in `classical_vs_quantum_results.json`).
**Dependencies**: a charting library decision (recommend `recharts`, React-native, minimal bundle impact) — the one new external dependency this whole plan introduces.
**Implementation**: replace `<pre>{JSON.stringify(...)}</pre>` sections with real components (tables, before/after comparisons, charts) per section; new backend read-only endpoints follow the existing `research_service.py` pattern exactly (read from disk, never recompute).
**Tests**: manual verification per section; no backend logic changes beyond new read-only functions (low regression risk).
**Acceptance criteria**: a reviewer/professor persona (per the user journeys) can understand the leakage story and QUBO-bug story without leaving the product.
**Risks**: charting library integration is the only genuinely new technical surface in this plan — budget extra time for it, and confirm bundle-size impact before committing to it.
**Rollback**: additive; the existing three sections keep working throughout.

## Milestone 7 (P2) — Risk Exception Feed

**Objective**: build `/risk`, honestly scoped to what qsci_core actually computes today (stockout risk only — no supplier/capacity/routing risk models exist).
**Files/modules**: new `backend/app/services/risk_service.py` (aggregates stockout risk across recommendations, sorted by severity), `GET /risk` route, `frontend/app/(app)/risk/page.tsx`.
**Dependencies**: Milestone 4's `DataTable`/card patterns if built first (not required).
**Implementation**: explicitly do NOT fabricate supplier/capacity/routing risk cards — the page should show only stockout-risk exceptions and, wherever a risk type is asked for in the planning brief but not computed, an honest "not yet computed by qsci_core" note rather than a placeholder number.
**Tests**: one new backend test for the aggregation service.
**Acceptance criteria**: matches the planning brief's "do not show fake risk scores" instruction, verified by inspection.
**Risks**: scope pressure to "fill out" the page with fabricated risk types — explicitly resist this per CLAUDE.md's honesty rules.
**Rollback**: trivial, additive.

## Milestone 8 (P1) — Testing Infrastructure

**Objective**: stop relying on manual verification for regression safety. Automate the Golden Path walkthrough already done manually this session.
**Files/modules**: `frontend/playwright.config.ts` (new), `frontend/e2e/golden-path.spec.ts` (new, encodes the exact manual walkthrough from `docs/BUTTON_INTERACTION_MATRIX.md`), minimal frontend component tests for `DecisionChain`/`WhyPanel` (Vitest + React Testing Library, or Playwright component testing — pick one, don't run two frameworks).
**Dependencies**: none — can start immediately, ideally in parallel with Milestones 3-7 rather than after them.
**Implementation**: one Playwright spec per milestone as it ships, not a single giant spec written at the end — this keeps the "no dead buttons" property continuously verified rather than checked once.
**Tests**: this milestone *is* tests.
**Acceptance criteria**: the Golden Path (generate → inspect → approve) runs unattended in CI-equivalent conditions and fails loudly if broken.
**Risks**: test flakiness against real (slow, non-deterministic) qsci_core execution — mitigate by mocking the backend at the HTTP layer for frontend-only tests, while keeping the existing real-execution backend tests as the source of truth for computational correctness (don't mock qsci_core in `backend/tests/`, only mock the backend API in `frontend/e2e/`).
**Rollback**: N/A, additive only.

## Milestone 9 (P3) — Accessibility & Mobile Pass

**Objective**: WCAG 2.2 AA first pass on existing pages, real mobile layout (drawers/bottom sheets) for DecisionChain/WhyPanel.
**Files/modules**: `frontend/components/Drawer.tsx` (new), audits/fixes across existing pages (contrast, focus states, ARIA, form labels — e.g. the approver-name field's `placeholder`-as-label gap flagged in the UI/UX plan).
**Dependencies**: Milestone 8 ideally in place first, so fixes are guarded by tests.
**Implementation**: incremental, page by page, starting with `/dashboard` (highest-traffic page).
**Tests**: axe-core (or equivalent) automated a11y checks added to the Playwright suite.
**Acceptance criteria**: zero critical a11y violations on `/dashboard`, `/demand`, `/inventory`.
**Risks**: low, but easy to under-scope — budget real time, don't treat as a checkbox.
**Rollback**: N/A, additive/fix-only.

## Milestone 10 (P2/P3) — Scenario Simulator, Copilot (Sequenced Last, Deliberately)

**Objective**: the two most product-exciting but highest-fabrication-risk features, built only once everything they'd cite is real and stable.
**Files/modules**: `backend/app/services/scenario_service.py`, `POST /scenarios`, `frontend/app/(app)/scenarios/page.tsx`; then `backend/app/services/copilot_service.py`, `POST /copilot/query`, `frontend/app/(app)/copilot/page.tsx`.
**Dependencies**: Milestones 1-7 (Copilot in particular needs a stable, complete set of read endpoints to ground itself in — building it earlier risks exactly the hallucination CLAUDE.md explicitly forbids).
**Implementation**: Scenarios reuse `forecast_service`/`optimization_service`/`financial` with perturbed inputs, never a separate fabricated-delta calculation. Copilot maps questions to existing REST endpoints only; any question it can't ground in a real response gets "I don't have that information," not a plausible-sounding guess.
**Tests**: scenario correctness tests (perturbed input produces a real, re-computed output, not an interpolated guess); Copilot grounding tests (every canned test question's answer must cite a real API call).
**Acceptance criteria**: matches the planning brief's explicit Copilot examples ("Which warehouses are at risk?", "Why isn't quantum being used for this recommendation?") with real, evidence-backed answers.
**Risks**: highest in this entire roadmap — LLM integration choice (which model, which framework) is out of scope for this plan and needs a separate decision before implementation starts.
**Rollback**: entirely new, isolated routes/pages; zero impact on the rest of the product if descoped or delayed.

---

## Recommended Implementation Order

1. Milestone 1 (close known gaps) — fast, de-risks everything after it.
2. Milestone 8 (testing infrastructure) — start in parallel with 1, so every subsequent milestone ships with regression coverage instead of adding a testing debt.
3. Milestone 3 (Optimization page) — highest-value gap: real backend, zero frontend, directly serves the "quantum as evidence, not marketing" product principle.
4. Milestone 2 (Outcome recording) — small, closes a real research-relevant gap (RQ2/H2).
5. Milestones 4-5 (Data lineage, Model registry) — both read-only, low-risk, high research value.
6. Milestone 6 (Research Lab depth) — the biggest single UX win for the Researcher/Reviewer personas.
7. Milestone 7 (Risk feed) — scoped honestly to avoid fabrication pressure.
8. Milestone 9 (Accessibility/mobile) — once there's enough surface area to make a real audit worthwhile.
9. Milestone 10 (Scenarios, Copilot) — last, deliberately, per the dependency reasoning above.

Do not begin implementation until this plan (and the five documents it accompanies: `QSCI_PRODUCT_AUDIT.md`, `QSCI_FEATURE_MATRIX.md`, `QSCI_UI_UX_MASTER_PLAN.md`, `QSCI_BACKEND_MASTER_PLAN.md`, `QSCI_RESEARCH_INTEGRATION_PLAN.md`) has been reviewed and a milestone or subset is explicitly approved.
