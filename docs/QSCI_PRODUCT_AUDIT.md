# QSCI Product Audit

Status: **COMPLETE** (planning artifact — no source files modified to produce this)
Date: 2026-08-20
Scope: full-repository inspection as of commit `3a48e9b` (phase-6 vertical slice). Classifies every major capability as **EXISTS+VERIFIED**, **EXISTS+INCOMPLETE**, **MISSING**, **RESEARCH ONLY**, or **PENDING**.

---

## 1. Current Product

QSCI today is two things at once: (a) a rigorously audited, six-phase quantum-vs-classical supply-chain research engine (`qsci_core`, Phases 0–5, 176 passing tests), and (b) the first real vertical slice of a decision-intelligence application (FastAPI backend + Next.js frontend, Phase 6, 38 passing API tests) that exposes a *narrow* but *real* end of that engine: LightGBM-based inventory recommendations, human approval, and a read-only research viewer. It is not yet the full "Decision Center + Research Lab" product described in the planning prompt. The research engine substantially outruns the product surface.

## 2. Current Backend

**EXISTS+VERIFIED**: `backend/app/main.py` (FastAPI, CORS via regex for local dev ports), service-layer separation (`routes → services → qsci_core → DB`), Alembic migrations (`backend/migrations/`, baseline `7ee0940aea90`, no silent `create_all()` on app startup). Endpoints, all real (no mocked data): `GET /health`, `POST /data/ingest`, `GET /data/sources`, `POST /forecast`, `GET /forecast/{id}`, `POST /optimize`, `GET /optimization/{id}`, `POST /recommend`, `GET /recommendations`, `GET /recommendations/{id}`, `POST /recommendations/{id}/approve|reject|modify`, `GET /audit`, `GET /research/benchmarks|experiments|scalability|noise`. Slow solvers (QAOA, VQR) dispatch as real non-blocking `BackgroundTasks` with their own DB session. 38/38 backend tests pass against real qsci_core execution.

**EXISTS+INCOMPLETE**: routing optimization is wired (`or_tools`, `simulated_annealing`, `qaoa` methods on `POST /optimize`) but has no frontend page consuming it yet. `research_service.py` reads static JSON files directly from `experiments/results/` on every request — correct and simple, but doesn't yet use the `ExperimentResultRecord` DB table that exists in the schema (defined, migrated, never populated — a mirror table with no writer).

**MISSING**: authentication/authorization (disclosed gap — `approver` is an unverified free-text field, see `docs/PHASE_6_PREIMPLEMENTATION_AUDIT.md` §10); rate limiting; structured logging/observability; outcome-recording endpoint (the `OutcomeRecord` model and `record_outcome()` persistence function exist in `qsci_core`, but no API route calls it); scenario-simulation endpoints; copilot/chat endpoint; supplier/risk-specific endpoints beyond stockout risk.

## 3. Current Frontend

**EXISTS+VERIFIED**: Next.js 16 App Router, TypeScript, Tailwind v4, production build passes. Design tokens (dark-first navy/slate, cyan accent, violet-for-research, semantic LIVE/RESEARCH/ILLUSTRATIVE/PENDING status pills) in `app/globals.css`. Typed API client (`lib/api.ts`) with honest error propagation (no fabricated fallback data — verified live: a backend outage rendered "Backend unavailable," not fake numbers). Reusable `DecisionChain` and `WhyPanel` components built from real API responses. Pages: `/` (landing), `/dashboard` (Decision Center — generate/approve/reject a real LightGBM-backed recommendation), `/demand` (run/compare Seasonal Naive, LightGBM, VQR), `/inventory` (recommendation table), `/research` (live Phase 4/5 JSON).

**EXISTS+INCOMPLETE**: `/demand` and `/inventory` were built and unit/API-tested but not re-verified live in-browser after the Phase 6 reorder-point bugfix (see `docs/BUTTON_INTERACTION_MATRIX.md`). The Decision Center only offers a LightGBM "generate" action — no UI path to trigger routing/inventory-optimization or view a VQR-backed recommendation's confidence gap.

**MISSING**: `/risk`, `/optimization`, `/scenarios`, `/copilot`, `/models`, `/data`, `/settings`, `/operations` pages (all named in the planning prompt's navigation, none built). Mobile-specific layout (drawers/bottom sheets — only generic Tailwind responsive utilities exist, untested at breakpoints). Loading-state choreography beyond a plain "Generating…" button label. Any animation/motion system. A Stitch-derived (or otherwise deliberate) design system beyond the token set in §2 above — current UI is functional, not yet "premium enterprise SaaS" per the visual-design bar in the planning prompt.

## 4. Current Research Engine (`qsci_core`)

**EXISTS+VERIFIED**, all with real data and passing tests:
- `data/` — M5, CVRPLIB, Amazon Last-Mile loaders + quality assessment (LIVE-labeled).
- `forecasting/classical/` — LightGBM quantile forecaster (p10/p50/p90, quantile-crossing-fixed), seasonal-naive baseline.
- `forecasting/quantum/` — VQR forecaster, leakage-safe PCA feature reduction (4/8/12/16 qubits).
- `optimization/classical/` — OR-Tools native CVRP solver.
- `optimization/quantum/` — QUBO formulator (with a documented, fixed formulation bug from Phase 3), decoder (hard independent feasibility check), simulated-annealing solver, QAOA solver (now with `noise_preset` support from Phase 4), experiment/instance-builder scaffolding.
- `risk/` — stockout risk from forecast quantiles, demand volatility.
- `financial/` — EOQ, safety stock, reorder point (always `CostAssumptions.status="ILLUSTRATIVE"`).
- `confidence/` — 4-factor decomposition (data quality, forecast stability, model consensus, backtest performance), real weights, documented formulas.
- `recommendation/` — `build_recommendation()`, ties the above into one auditable object.
- `persistence/` — SQLAlchemy models + write helpers, every write auto-generates a paired audit event.
- `evaluation/` — rmse/mae/wmape/bias/fva/pinball_loss, Diebold-Mariano test, rolling-origin backtest.

**RESEARCH ONLY** (by design, not a gap): VQR forecasting, QAOA/annealing routing — all correctly labeled RESEARCH throughout, per CLAUDE.md's honesty rules.

This layer is the strongest part of the repository — six phases, each independently audited (`docs/PHASE_*_REPORT.md`, `docs/*_AUDIT.md`), zero fabricated claims found across four separate claim audits.

## 5. Current Database

SQLite (`experiments/qsci_dev.db`, gitignored), Alembic-migrated. Tables: `datasets`, `forecast_runs`, `optimization_runs`, `experiment_results` (all added in Phase 6, `experiment_results` currently unused — no writer), `recommendations` (now with a `status` enum + duplicate-approval/invalid-transition guard), `approvals`, `audit_events`, `outcomes` (defined, unused — no API writes to it yet). **EXISTS+INCOMPLETE**: no seed data pipeline for `experiment_results`; `outcomes` has no producer; no migration beyond the single baseline (expected at this stage, not a gap yet).

## 6. Current API

REST, versioned under `/api/v1`. No API versioning strategy beyond the `v1` prefix (fine for now — **PENDING** for later). No OpenAPI customization beyond FastAPI's default schema (usable, unpolished). No pagination on `GET /recommendations` or `GET /audit` (the latter is `.limit(200)`-capped, not paginated) — **EXISTS+INCOMPLETE**, will matter once data volume grows.

## 7. Current UX

Golden Path (generate → inspect DecisionChain/WhyPanel → approve) is real and was manually verified end-to-end in a browser this session — the strongest UX evidence in the repo. Everything past that single path (routing decisions, risk exceptions, scenario simulation, research drill-down beyond three JSON dumps, mobile, Copilot) is **MISSING** or **EXISTS+INCOMPLETE**. The Research Lab page currently renders raw JSON in `<pre>` blocks for two of its four sections — functional evidence, not yet a designed research experience.

## 8. Current Security

**EXISTS+VERIFIED**: CORS scoped to localhost dev origins (regex, not `*`); no secrets in the codebase (nothing to leak); `NEXT_PUBLIC_API_BASE_URL` is non-sensitive by design.
**MISSING**: authentication, authorization, rate limiting, input size limits, HTTPS/production CORS config, CSRF consideration for the approve/reject/modify mutations (currently plain POST from any origin the CORS regex allows), audit-log tamper-evidence (no hash chaining — `docs/PHASE_6_PREIMPLEMENTATION_AUDIT.md` flagged this as future work, still true).
**PENDING**: a documented security model appropriate for "no real auth yet, dev/demo scale" — exists informally in audit docs, not as a single security doc yet (this plan produces one, §46 target).

## 9. Current Testing

Root `qsci_core` suite: 176 passed, 1 xfailed (documented pre-existing xfail). Backend: 38/38 API tests, real qsci_core execution, covering valid/invalid/missing/malformed input, invalid IDs, duplicate approval, invalid state transitions. **MISSING**: frontend unit/component tests (zero); Playwright/E2E automation (zero — the one full Golden Path pass that exists was manual, evidenced in `docs/BUTTON_INTERACTION_MATRIX.md`, not a regression test); persona-based testing; accessibility testing; load/performance testing; security testing beyond manual reasoning.

## 10. Current Research Exposure (Product-Facing)

`/research` surfaces: master benchmark table (Phase 5), QAOA depth tradeoff (Phase 4), noise sensitivity with its honesty caveat (Phase 4), a static limitations list. **MISSING** from the product surface entirely: Phase 2/2.1 forecasting-leakage story (the single most important research narrative — a real bug found and fixed, changing the paper's conclusion), Phase 3's QUBO-validation bug-and-fix story, statistical test results (DM test, Mann-Whitney) beyond what's baked into the master-scorecard table, resource-scaling charts (qubits/depth/gates vs. N — exist as PDFs in `paper/figures/`, not surfaced in the app at all), reproducibility metadata, dataset lineage.

## 11. Current Gaps — Summary Table

| Area | Status |
|---|---|
| Golden Path (inventory recommendation → approval) | EXISTS+VERIFIED |
| Routing optimization in the product | EXISTS+INCOMPLETE (backend real, no frontend) |
| Risk page | MISSING |
| Scenario simulator | MISSING |
| Copilot | MISSING |
| Models registry page | MISSING |
| Data lineage page | MISSING |
| Settings | MISSING |
| Outcome recording (RQ2/H2 loop) | EXISTS+INCOMPLETE (model + persistence function exist, no API/UI) |
| Auth | MISSING |
| Frontend tests | MISSING |
| E2E/Playwright | MISSING |
| Accessibility | MISSING |
| Mobile-specific design | MISSING |
| Design system beyond tokens | EXISTS+INCOMPLETE |
| Research Lab depth (leakage story, QUBO-bug story, stats, resource charts) | EXISTS+INCOMPLETE |

---

## 12. User Journeys

### Executive
- **Goal**: understand supply-chain state in seconds, approve/reject high-impact decisions.
- **Entry**: `/dashboard`.
- **Steps**: scan pending decisions → open highest-impact one → read WhyPanel's one-paragraph rationale → approve/reject.
- **Info required**: financial impact, confidence, risk level — all present today for inventory recs.
- **Success**: decision made in under 2 minutes without needing to understand the underlying model.
- **Failure modes today**: no severity/impact sorting on the pending list (currently unordered by anything but recency); no routing/risk decisions to approve, only inventory.

### Demand Planner
- **Goal**: validate/override a demand forecast before it drives inventory.
- **Entry**: `/demand`.
- **Steps**: run LightGBM forecast for a SKU → compare against seasonal-naive → (optionally) run VQR to see the research comparison → note forecast_stability is unavailable for VQR → proceed to `/dashboard` to generate the recommendation.
- **Success**: understands why LightGBM, not VQR, drives production recommendations today.
- **Failure modes today**: no SKU picker (hardcoded to `FOODS_3_090_CA_1_evaluation`); no historical-actuals chart; can't jump directly from a forecast run to a recommendation for that exact run without leaving the page.

### Inventory Manager
- **Goal**: decide what to reorder, how much, and why.
- **Entry**: `/inventory`.
- **Steps**: scan the recommendation table → click a SKU → land on `/dashboard`'s DecisionChain for that item → approve/reject/modify.
- **Success**: EXISTS+VERIFIED for the single-SKU flow.
- **Failure modes today**: no multi-SKU bulk view/action; no "modify" UI (backend supports it, frontend doesn't expose a quantity-editing control).

### Operations Manager
- **Goal**: decide which routing method to trust for a given shipment batch.
- **Entry**: intended `/optimization` — **does not exist**.
- **Journey today**: dead end at the product layer; only reachable via direct API calls or `/research`'s master-benchmark table.

### Data Scientist / Quantum Researcher
- **Goal**: reproduce and extend the classical-vs-quantum comparison.
- **Entry**: `/research`.
- **Steps today**: read three research-JSON dumps → for real depth, must leave the product and open `notebooks/QSCI_Research_Report.ipynb` or the `docs/PHASE_*_REPORT.md` files directly.
- **Success**: fully achievable outside the product (the research artifacts are excellent); not yet achievable inside it.

### Professor / Reviewer
- **Goal**: audit the claims for rigor — "how do you know?"
- **Entry**: `docs/PHASE_*_REPORT.md` and `docs/*_AUDIT.md` (not the product UI).
- **Success**: fully achievable today via the docs; the product UI does not yet carry this burden, and per CLAUDE.md's own standard, it should eventually be able to.

### First-Time User
- **Goal**: understand what QSCI is within 10 seconds of landing.
- **Entry**: `/`.
- **Steps**: read hero + pipeline visual → click into Decision Center or Research Lab.
- **Success**: EXISTS+VERIFIED — the landing page states the FORECAST≠DECISION thesis and frames quantum as a research layer, matching the planning prompt's requirement not to lead with "Quantum AI."

---

## 13. Page Map (Current + Planned)

| Route | Status | User | Purpose | Backend | Data Source |
|---|---|---|---|---|---|
| `/` | EXISTS+VERIFIED | All | Thesis, entry point | none (static) | none |
| `/dashboard` | EXISTS+VERIFIED (inventory only) | Exec, Inv. Mgr | Decision Center | `/forecast`, `/recommend`, `/recommendations/*`, `/audit` | M5 (live) |
| `/demand` | EXISTS+VERIFIED | Demand Planner | Forecast comparison | `/forecast` | M5 (live) |
| `/inventory` | EXISTS+VERIFIED | Inv. Mgr | Recommendation table | `/recommendations` | M5-derived |
| `/research` | EXISTS+INCOMPLETE | Researcher | Evidence viewer | `/research/*` | `experiments/results/*.json` |
| `/risk` | MISSING | Ops Mgr | Exception-driven risk | none yet | — |
| `/optimization` | MISSING | Ops Mgr | Routing/allocation decisions | `/optimize` (backend ready) | CVRPLIB |
| `/scenarios` | MISSING | Planner/Exec | What-if simulation | none yet | — |
| `/copilot` | MISSING | All | Grounded Q&A | none yet | — |
| `/models` | MISSING | Researcher | Model evidence registry | `ExperimentResultRecord` (unused) | `experiments/results/*` |
| `/data` | MISSING | Researcher | Dataset lineage | `/data/sources` (backend ready) | `DatasetRecord` |
| `/settings` | MISSING | All | Config, (future) auth | none yet | — |

Empty/loading/error states, mobile behavior, and accessibility requirements per page are detailed in `docs/QSCI_UI_UX_MASTER_PLAN.md` §6.
