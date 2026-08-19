# Phase 6 Pre-Implementation Audit

Status: **COMPLETE**
Date: 2026-08-20
Scope: read-only inspection of the repository before any Phase 6 backend/frontend code is written. No files modified during this audit.

## 1. Current Backend State

`backend/` exists as an empty directory — **zero files**. No FastAPI app, no routes, no service layer, no schemas. This is a greenfield build, not a repair job, despite `backend/app` being referenced in CLAUDE.md's target architecture.

## 2. Current Frontend State

`frontend/` exists as an empty directory — **zero files**. No `package.json`, no Next.js scaffold. Also greenfield. (Note: CLAUDE.md's own repo-history section mentions a prior commit `6202ae6 feat: integrate Next.js frontend into monorepo and add 8 new hubs` — that work is not present in the current tree; either it was on a different branch/was removed, or the commit message doesn't reflect what's actually there. Verified by direct inspection, not assumed from git log text.)

## 3. Existing API Routes

None. Nothing to audit.

## 4. Existing Database Models

`qsci_core/persistence/models.py` (SQLAlchemy 2.0 declarative, unit-tested in `tests/test_recommendation_persistence.py`) already has: `RecommendationRecord`, `ApprovalRecord` (with `ApprovalDecision` enum: APPROVE/REJECT/MODIFY), `AuditRecord`, `OutcomeRecord`. `qsci_core/persistence/db.py` provides `get_engine()` (SQLite at `experiments/qsci_dev.db`, `Base.metadata.create_all()` — no migration framework), `persist_recommendation()`, `record_approval()`, `record_outcome()` — every write already auto-generates a paired `AuditRecord` server-side.

**Gap vs. CLAUDE.md's Phase 6 model list** (`Dataset`, `ForecastRun`, `OptimizationRun`, `Recommendation`, `Approval`, `AuditEntry`, `ExperimentResult`): `Dataset`, `ForecastRun`, `OptimizationRun`, and `ExperimentResult` do not exist as persisted tables — forecasting/optimization runs currently live only as JSON files under `experiments/results/`, never written to the DB. These need new models.

**Migration gap**: `create_all()` on startup is exactly the anti-pattern CLAUDE.md's Phase 6 spec calls out ("Do not silently recreate tables on startup... Use migrations"). Alembic is installed (`.venv/Scripts/alembic.exe` present) but never initialized in this repo.

## 5. Existing qsci_core Entry Points (the real backend service layer will wrap these)

- **Data**: `qsci_core.data.loaders.load_m5(raw_dir)`, `.load_cvrplib_instance(name, raw_dir)`, `.load_last_mile(raw_dir)`; `qsci_core.data.quality.assess_m5/.assess_cvrplib_instance/.assess_dataframe(...)`.
- **Forecasting (classical)**: `LightGBMQuantileForecaster` (class, `.fit()/.predict()`), `lightgbm_p50_point_forecast()`, `seasonal_naive_predict()`, `feature_columns()`/`build_features()`.
- **Forecasting (quantum)**: `qsci_core.forecasting.quantum.vqr_forecaster` (VQR class), `.feature_reduction` (PCA/top-N to 4/8/12/16 qubits) — **slow** (documented non-trivial train times, up to minutes at N≥12); any API endpoint wrapping this needs an async/background-job pattern, not a synchronous request/response, or it will time out.
- **Optimization (classical)**: `qsci_core.optimization.classical` (OR-Tools VRP, from Phase 1) + `qsci_core.optimization.quantum.classical_qubo_solver` (OR-Tools-on-QUBO, from Phase 3).
- **Optimization (quantum)**: `qsci_core.optimization.quantum.annealing_solver.solve_qubo_with_annealing()`, `.qaoa_solver.solve_qubo_with_qaoa()` (now with `noise_preset`, Phase 4) — QAOA is **very slow** (seconds to hundreds of seconds per call, per Phase 3/4 measurements); must be a background job, never a synchronous API call.
- **Risk**: `qsci_core.risk.stockout_risk.stockout_risk_from_quantiles()`, `.demand_volatility()`.
- **Financial**: `qsci_core.financial.eoq` (EOQ, safety stock, reorder point, `CostAssumptions` — always `status="ILLUSTRATIVE"`).
- **Confidence**: `qsci_core.confidence.decomposition.compute_confidence()` and the four component-score functions (`data_quality_score`, `forecast_stability_score`, `model_consensus_score`, `backtest_performance_score`) — validated in Phase 5 to have a real gap for point-forecast models (no `forecast_stability` for VQR).
- **Recommendation**: `qsci_core.recommendation.builder.build_recommendation()` → `Recommendation` dataclass with `.to_dict()`.
- **Persistence**: as above.
- **Evaluation**: `qsci_core.evaluation.metrics` (rmse/mae/wmape/bias/fva/pinball_loss/summarize), `.dm_test.diebold_mariano_test()`, `.backtest` (rolling-origin).

All of the above are real, already unit-tested (`tests/` — 176 passing tests cover these modules directly). The backend's job is to expose them, not reimplement them.

## 6. Existing Research Results Available to the Research API (static, file-backed)

`experiments/results/*.json` and `*.csv` (19+ files: forecasting, routing, Phase 4 noise/scalability, Phase 5 confidence/synthesis tables) plus 20 PDF figures in `paper/figures/`. These are the ground truth for `/api/v1/research/*` endpoints — read from disk (or a `ExperimentResult` DB table seeded from them), never recomputed live and never hand-typed into frontend code.

## 7. pyproject.toml / Environment

No `[project.dependencies]` block exists — dependencies were installed ad hoc into `.venv` across Phases 0-4 without being pinned in `pyproject.toml` (an existing, pre-Phase-6 gap, not introduced here). Verified installed and usable: `fastapi==0.141.1`, `uvicorn`, `sqlalchemy==2.0.52`, `alembic` (binary present, unconfigured), `httpx` (useful for API tests). No `package.json` anywhere in the repo — Node toolchain (`node v24.16.0`, `npm 11.13.0`) is available in this environment but nothing has been scaffolded with it yet.

## 8. Git History

Working tree clean as of commit `d23c4cb` (Phase 5). No backend/frontend commits exist in the reachable history that left files in the current tree — confirmed by direct file listing (§1-2), not inferred from commit messages alone (CLAUDE.md's own historical note about a prior Next.js integration commit does not match the current file state — flagged, not silently trusted).

## 9. Frontend/Backend Gaps (Everything, Enumerated)

Nothing exists. Every route, every schema, every component, every test in the Phase 6 spec is net-new work.

## 10. Security Risks (Anticipatory — Nothing to Audit Yet, But Design Constraints Going In)

- No auth system exists yet. `approver` in `ApprovalRecord` is currently a free-text string field with no identity verification behind it — a real gap the Phase 6 API must not paper over: `POST /recommendations/{id}/approve` cannot trust a client-supplied "approver" identity as authoritative without a real auth layer. Given no auth provider is specified anywhere in CLAUDE.md and none is installed, the honest Phase 6 scope is: implement the endpoint with a clearly documented placeholder identity mechanism (e.g., a required non-empty string field, explicitly NOT cryptographically verified), and flag real authentication as a disclosed gap rather than fabricating a fake "logged in" experience.
- No secrets exist yet (no API keys, no external services) — nothing to leak via `NEXT_PUBLIC_` today, but this must stay true as Phase 6 code is added (no DB connection strings or future secrets in client bundles).
- QAOA/VQR endpoints are genuinely slow (documented in §5) — a naive synchronous endpoint is also a denial-of-service risk (a client can trivially trigger a multi-minute server-side computation). Must be async/job-queued with a status-polling pattern, not fire-and-block.

## 11. Architecture Risks

- **Sync vs. async compute**: QAOA (up to ~630s/run) and full VQR training (up to ~290s at N=12) cannot be synchronous HTTP handlers. Recommended: a simple in-process background-task pattern (FastAPI `BackgroundTasks` + a `status` column on the run record: `PENDING → RUNNING → COMPLETE/FAILED`) is sufficient for this project's scale — no need for Celery/Redis given the actual usage pattern (a research/demo app, not a production multi-tenant service).
- **SQLite concurrency**: fine for this project's actual scale (single dev/demo instance); CLAUDE.md's "don't introduce SQLite if a more appropriate DB exists" caveat doesn't apply — SQLite is already the existing, working choice from Phase 1, reused, not newly introduced.
- **Scope mismatch, stated plainly**: this Phase 6 spec (14 recommended subagents, Stitch MCP design exploration, 10 independent E2E rounds × 10 personas, full accessibility + security + performance audits, production build) describes multiple weeks of a real product team's work. It will be built **incrementally across this and following turns**, in the priority order CLAUDE.md itself mandates (§8: "application correctness > Golden Path > backend/frontend integration > UX/UI > browser/E2E testing"). This audit does not pretend otherwise — each milestone below will be reported with real evidence (tests run, endpoints verified, pages loaded), not claimed complete in bulk.

## 12. Recommended Implementation Order

1. **Backend scaffold + DB models** (`Dataset`, `ForecastRun`, `OptimizationRun`, `ExperimentResult` added alongside the existing Recommendation/Approval/Audit/Outcome models; Alembic initialized).
2. **Core read-only APIs first** (health, data sources, research/* — all fast, synchronous, directly unblock frontend work) — these are also the lowest-risk, highest-value endpoints since they're pure reads from already-computed, already-audited results.
3. **Golden Path write APIs** (forecast, optimize with the async job pattern, recommend, approve/reject/modify, audit) with real qsci_core wiring and tests.
4. **Frontend scaffold** (Next.js, design tokens, layout shell) once the API contract is stable enough not to churn.
5. **Golden Path pages** (dashboard, demand, inventory — the pages CLAUDE.md's own priority order puts before marketing/research polish).
6. **Research pages** (research/models/data — read-only, lower integration risk, high evidentiary value).
7. **Marketing/landing** last among page work (CLAUDE.md: "Golden Path pages first, then marketing/research/models/data pages").
8. **Testing** (API tests alongside each endpoint as it's built, not deferred to the end; browser/E2E testing after the Golden Path is functionally real).

No implementation has started as of this document. The next step is §12 item 1.
