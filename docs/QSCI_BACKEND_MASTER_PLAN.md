# QSCI Backend Master Plan

Status: **COMPLETE** (planning artifact)
Date: 2026-08-20

## 1. Architecture (Current, Confirmed Sound — Extend, Don't Replace)

```
Next.js  →  FastAPI  →  service layer  →  qsci_core  →  DB / experiment results
```

`backend/app/main.py` → `app/api/routes/*` → `app/services/*` → `qsci_core.*` / `qsci_core.persistence`. This separation is already correctly enforced (verified by reading every route file — none contain business logic beyond request validation and calling a service function). Continue this pattern for every new endpoint; the biggest architectural risk is a future contributor putting qsci_core calls directly in a route to save time.

## 2. API (Current + Planned)

Current (all real, Phase 6): health, data ingest/sources, forecast (+async VQR), optimize (+async QAOA), recommend, approve/reject/modify, audit, research/*.

**Planned additions**, in priority order:
- **P1** `POST /recommendations/{id}/outcome` — wraps `qsci_core.persistence.db.record_outcome` (exists, unused). Closes the RQ2/H2 loop.
- **P1** `GET /optimization` (list, mirrors `GET /recommendations`) — needed once `/optimization` frontend page exists.
- **P2** `POST /scenarios` — takes a baseline forecast/optimization run ID plus a perturbation (e.g. `{"type": "demand_spike", "magnitude_pct": 20}`), re-runs the real forecast/optimization/financial chain with the perturbed input, returns baseline vs. scenario. Must reuse `forecast_service`/`optimization_service`/`recommendation_service`, not a new parallel computation path.
- **P2** `GET /models` — seeds/reads `ExperimentResultRecord` from `experiments/results/*` (the table exists, unused — needs a seed script, not new schema).
- **P3** `POST /copilot/query` — thin layer that maps a natural-language question to one or more existing read endpoints and composes an answer; explicitly does not call an LLM with unconstrained tool access to qsci_core internals (scope the tool surface to the existing REST endpoints).
- **P4** pagination on `GET /recommendations` and `GET /audit` (currently unpaginated / hard-capped at 200).

## 3. Services

Current: `data_service`, `forecast_service`, `optimization_service`, `recommendation_service`, `research_service` — all thin, all real. Planned: `scenario_service` (new), `outcome_service` (thin wrapper, could live in `recommendation_service`), `model_registry_service` (seeds/reads `ExperimentResultRecord`).

## 4. Database

Current schema (Alembic-migrated, `backend/migrations/`): `datasets`, `forecast_runs`, `optimization_runs`, `experiment_results`, `recommendations` (+ `status`), `approvals`, `audit_events`, `outcomes`. **Next migration** (P1): none required for `outcomes`/`experiment_results` — schema already supports the planned endpoints above; only a *seed script* is needed for `experiment_results`, not a schema change. **Future migration** (P2, only when auth is built): an `approvers`/`users` table, foreign-keyed from `approvals.approver` (currently a free string).

## 5. Authentication

**Current**: none. `approver` is free text, explicitly disclosed as unverified (`docs/PHASE_6_PREIMPLEMENTATION_AUDIT.md` §10).
**Recommendation**: do not build a custom auth system. When this becomes a real requirement (before any non-local deployment), use a standard provider (e.g. NextAuth.js on the frontend + a verified-identity header/JWT passed to FastAPI, validated server-side). This is explicitly **P2 for continued local/demo use, P0 before any real deployment** — flagging the distinction rather than either building it prematurely or ignoring it.

## 6. Authorization

Not yet relevant (no distinct roles exist). When built, keep it simple: a small enum (`viewer`, `planner`, `approver`, `admin`) checked in the service layer (not scattered across routes), consistent with the existing routes→services separation.

## 7. Audit

**Current**: every write (recommendation creation, approval/rejection/modification) auto-generates a paired `AuditRecord`, verified in Phase 1 and re-verified in Phase 6's manual walkthrough. Server-authoritative (client never supplies `created_at` or the event payload's derived fields).
**Gap**: no tamper-evidence (no hash chaining between audit rows). **Recommendation**: add a `previous_hash`/`hash` pair to `AuditRecord` only if/when the product needs to defend against a compromised DB, not preemptively — note it as a documented, deferred hardening step, matching the "no auth yet" honesty pattern already established elsewhere.

## 8. Error Handling

**Current**: consistent pattern — `ValueError` from a service → `HTTPException(422)`; not-found → `HTTPException(404)`; invalid state transition (duplicate approval) → `HTTPException(409)`. Background-task failures are caught and recorded as `run_status=FAILED` with an `error` string, never crash silently or leave a run stuck. This pattern is sound; extend it verbatim to every new endpoint rather than inventing a new error convention.

## 9. Observability

**Current**: none beyond uvicorn's default request logging.
**Recommendation** (P3, not urgent at current scale): structured logging (Python's `logging` module, JSON formatter) for request/response and background-task lifecycle events; a `/metrics` endpoint only if/when the product has real usage to measure. Do not add a full observability stack (Prometheus/Grafana/etc.) prematurely — CLAUDE.md's priority order puts this well below Golden Path correctness.

## 10. Testing

**Current**: 38/38 backend API tests, real qsci_core execution (no mocking), isolated temp SQLite DB per test session, covering valid/invalid/missing/malformed requests, invalid IDs, duplicate approval, invalid state transitions, async-dispatch behavior. This is a strong foundation — extend the same real-execution-no-mocking philosophy to every new endpoint. **Gap**: no load/concurrency testing (background-task + SQLite concurrency has not been stress-tested — worth a dedicated test once `/scenarios` or `/models` add more concurrent read load).

## 11. Security

Covered in depth as its own section (§46 of the original numbering) — see the security posture already documented in `docs/PHASE_6_PREIMPLEMENTATION_AUDIT.md` §10 (auth gap, CORS scoping, no secrets in repo). This backend plan's contribution: keep the CORS origin-regex dev-only pattern out of any production config (flagged as a `# Production must replace this` comment already in `backend/app/main.py` — honor that comment when the time comes, don't let it silently ship).

## 12. Non-Goals For Now

No GraphQL layer (REST is adequate at this scale and matches the existing, working pattern). No microservice split (`qsci_core` + one FastAPI app is the right granularity for a research/decision-intelligence app of this size — splitting further would add operational overhead with no corresponding benefit). No Celery/Redis job queue (FastAPI `BackgroundTasks` + a `run_status` column is sufficient for this project's actual concurrency needs, per the reasoning already in `docs/PHASE_6_PREIMPLEMENTATION_AUDIT.md` §11).
