# QSCI Feature Matrix

Status: **COMPLETE** (planning artifact)
Date: 2026-08-20

Priority key: P0 = core/broken workflow, P1 = Golden Path, P2 = major product capability, P3 = UX/research improvement, P4 = polish.

| Feature | User | Purpose | Backend | qsci_core | Data | Status | Research/Prod | Priority | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|---|---|---|---|
| Inventory recommendation (LightGBM) | Inv. Mgr | Generate a reorder recommendation | `/forecast`, `/recommend` | `forecasting.classical`, `recommendation.builder` | M5 | EXISTS+VERIFIED | Production | P1 | — | Real numbers, LIVE labels, browser-verified |
| Human approval workflow | Exec, Inv. Mgr | Approve/reject/modify | `/recommendations/{id}/*` | `persistence.db` | — | EXISTS+VERIFIED (modify UI missing) | Production | P1 | — | Duplicate-approval blocked, audit event written |
| Audit trail | All | Traceability | `/audit` | `persistence.models.AuditRecord` | — | EXISTS+VERIFIED | Production | P1 | — | Every state change has a paired audit row |
| VQR forecast comparison | Demand Planner, Researcher | Show quantum forecasting research | `/forecast` (async) | `forecasting.quantum` | M5 | EXISTS+VERIFIED | Research | P2 | — | Labeled RESEARCH, forecast_stability shown as NOT AVAILABLE |
| Modify-quantity UI | Inv. Mgr | Adjust suggested order qty before approving | `/recommendations/{id}/modify` (backend ready) | — | — | MISSING (frontend) | Production | P1 | Dashboard rework | Quantity input + reason field, writes MODIFIED status |
| Multi-SKU dashboard | Exec, Inv. Mgr | See more than one series | `/forecast` (series_id param exists) | `data.loaders.load_m5` | M5 (30,490 series) | MISSING | Production | P2 | SKU picker component | User can browse/select from real M5 series list |
| Routing optimization page | Ops Mgr | Compare OR-Tools/annealing/QAOA on a real routing decision | `/optimize` (backend ready) | `optimization.*` | CVRPLIB | MISSING (frontend) | Production+Research | P1 | — | Shows objective/feasibility/gap/runtime per method, no "quantum winner" framing |
| Risk exception feed | Ops Mgr | Prioritized risk exceptions | none yet | `risk.stockout_risk` (stockout only; no supplier/capacity/routing risk models exist) | M5 | MISSING (backend+frontend) | Production | P2 | New risk-aggregation service | Only shows risk types qsci_core actually computes |
| Scenario simulator | Planner, Exec | What-if analysis | none yet | would reuse `forecasting`+`optimization`+`financial` with perturbed inputs | M5/CVRPLIB | MISSING | Production | P2 | Backend scenario endpoint | Every scenario type traces to real backend logic, no fabricated deltas |
| Copilot | All | Grounded Q&A | none yet | would call existing services, not qsci_core directly | all | MISSING | Production | P3 | LLM integration decision (out of qsci_core scope) | Every answer cites a real API response; refuses when evidence absent |
| Research Lab — leakage story | Researcher, Reviewer | Surface Phase 2.1's found-and-fixed leakage bug | new `/research/leakage` endpoint | reads `experiments/results/phase2_1_leakage_free_results.json` | — | MISSING | Research | P2 | — | Shows original (FLAWED) vs. corrected numbers side by side, as the notebooks already do |
| Research Lab — QUBO-bug story | Researcher, Reviewer | Surface Phase 3's found-and-fixed QUBO penalty bug | new `/research/qubo-validation` endpoint | reads `docs/PHASE_3_REPORT.md` §9 data / `routing_penalty_sensitivity.json` | — | MISSING | Research | P3 | — | Shows the failing case and the fix, not just the final numbers |
| Statistical tests display | Researcher | DM test, Mann-Whitney results | new endpoint or extend `/research/benchmarks` | `evaluation.dm_test` (already computed, stored in `classical_vs_quantum_results.json`) | — | MISSING | Research | P3 | — | p-values, significance, sample-size caveats shown, not just point estimates |
| Resource-scaling charts | Researcher | Qubits/depth/gates/runtime vs. N | serve existing PDFs or re-render as SVG/chart | `paper/figures/*.pdf` | — | MISSING | Research | P3 | Chart library decision | Real data points, not illustrative curves |
| Model evidence registry (`/models`) | Researcher | Compare all models at a glance | `ExperimentResultRecord` (schema exists, unused) | reads `experiments/results/*` | — | MISSING | Research | P2 | Seed script for `experiment_results` table | Sortable/filterable table, every row links to its source file |
| Dataset lineage (`/data`) | Researcher | Where did this number come from | `/data/sources` (exists) | `data.loaders`, `data.quality` | M5/CVRPLIB/Last-Mile | EXISTS+INCOMPLETE (backend ready, no page) | Research | P2 | — | Shows real record counts, quality reports, last-validated timestamp |
| Outcome recording | Inv. Mgr, Researcher (RQ2/H2) | Predicted-vs-actual comparison | new `POST /recommendations/{id}/outcome` | `persistence.db.record_outcome` (exists, unused) | — | EXISTS+INCOMPLETE (backend function exists, no API route) | Production+Research | P2 | — | Closes the DATA→...→OUTCOME loop CLAUDE.md's pipeline requires |
| Authentication | All | Real approver identity | none yet | — | — | MISSING | Production | P2 (P0 before any real deployment) | Auth provider decision | `approver` field becomes verified, not free-text |
| Frontend tests | Dev | Regression safety | — | — | — | MISSING | Production | P1 | Testing framework decision | Component tests for DecisionChain/WhyPanel at minimum |
| Playwright E2E | Dev, QA | Automated Golden Path | — | — | — | MISSING | Production | P1 | Playwright setup | Automates the manual walkthrough already evidenced in `docs/BUTTON_INTERACTION_MATRIX.md` |
| Accessibility pass | All | WCAG 2.2 AA | — | — | — | MISSING | Production | P2 | — | Keyboard nav, contrast, ARIA on existing pages first |
| Mobile layout | All | Usable on phone | — | — | — | MISSING | Production | P3 | — | Drawers/bottom sheets, not shrunk desktop |
| Design system (Stitch-derived) | All | Premium, coherent visual identity | — | — | — | EXISTS+INCOMPLETE (tokens only) | Production | P3 | Stitch MCP availability check | Consistent component library across all pages |
| Settings page | All | Config/future auth | none yet | — | — | MISSING | Production | P4 | — | — |
