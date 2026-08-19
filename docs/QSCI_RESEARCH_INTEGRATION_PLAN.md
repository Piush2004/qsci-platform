# QSCI Research Integration Plan

Status: **COMPLETE** (planning artifact)
Date: 2026-08-20

Maps each research phase to exactly how its results appear (or should appear) in the product, so no research finding stays trapped in a notebook or markdown report that a product user would never see.

## Phase 1 → Product (Golden Path)

**What it produced**: LightGBM quantile forecasting, OR-Tools routing, EOQ/safety-stock math, confidence decomposition, recommendation/approval/audit persistence — the entire classical backbone.
**Where it lives in the product today**: directly — this *is* `/dashboard`, `/demand` (LightGBM/Seasonal Naive cards), `/inventory`. EXISTS+VERIFIED, no gap.
**Remaining integration work**: routing (OR-Tools was Phase 1's other half) has a real backend endpoint (`POST /optimize`, method `or_tools`) but no frontend page — this is the `/optimization` page from the feature matrix, P1.

## Phase 2 / 2.1 → Research (with a Product Obligation)

**What it produced**: VQR forecasting; then a real discovered-and-fixed data-leakage bug that changed the paper's conclusion (original VQR N=4 wMAPE ~32%, looked competitive; corrected wMAPE ~34-36%, classical LightGBM's full-history wMAPE of 25.56% clearly stronger).
**Where it lives in the product today**: `/demand`'s VQR card shows RESEARCH-labeled results and the `forecast_stability: NOT AVAILABLE FOR THIS MODEL` finding from Phase 5. The leakage story itself — arguably the single most important piece of scientific honesty in this entire project — is **not surfaced in the product at all**, only in `docs/PHASE_2_1_VALIDITY_AUDIT.md` and the notebooks.
**Integration work** (P2, feature matrix "Research Lab — leakage story"): a `/research` section (or a `/models` detail view) that shows the original (FLAWED) vs. corrected VQR numbers side by side, exactly as `notebooks/07_classical_vs_quantum_comparison.ipynb` §5 already does — the data (`experiments/results/quantum_forecasting_results.json` labeled `FLAWED`, `phase2_1_leakage_free_results.json` corrected) already exists; this is a display task, not new research.

## Phase 3 → Research (with a Product Obligation)

**What it produced**: QUBO-based routing (OR-Tools-on-QUBO, simulated annealing, QAOA), a real formulation bug found via the mandated brute-force validation gate and fixed, a full fairness audit.
**Where it lives in the product today**: the backend (`POST /optimize`, methods `simulated_annealing`/`qaoa`) is real and tested; nothing in the frontend surfaces it yet.
**Integration work**: primary — the `/optimization` page (P1, shared with Phase 1's OR-Tools). Secondary (P3) — the QUBO-bug story (`docs/PHASE_3_REPORT.md` §9), similar treatment to the Phase 2.1 leakage story: show the failing case and the fix, not just final numbers, reusing `experiments/results/routing_penalty_sensitivity.json`.

## Phase 4 → Research

**What it produced**: QAOA runtime-wall root cause (execution-cost-dominated), annealing feasibility-collapse recovery via sampling, QAOA depth (p=1/2/3) showing no benefit, noise sensitivity with an honestly-disclosed metric caveat.
**Where it lives in the product today**: `/research` already surfaces the QAOA depth tradeoff and noise sensitivity (with its caveat) directly from `experiments/results/phase4_noise_and_scaling_results.json`. This is the best-integrated research phase in the current product. **Remaining gap** (P3): the resource-scaling story (qubits/depth/gates/runtime vs. N) exists only as PDFs in `paper/figures/`, not as interactive product charts — the `EvidenceChart` component from the UI/UX plan should eventually render this from the same JSON the PDFs were built from.

## Phase 5 → Business Decision Intelligence (the Bridge Phase)

**What it produced**: confidence-decomposition applied to both forecasting tracks for the first time, surfacing that VQR cannot produce `forecast_stability` at all; Phase 4's findings folded into the master synthesis; the consolidated research report.
**Where it lives in the product today**: this is the most product-relevant research phase, and it's already reflected — `WhyPanel`'s confidence breakdown is literally `qsci_core.confidence.decomposition`, the same module Phase 5 exercised. The master-scorecard table on `/research` is Phase 5's output directly.
**Remaining gap** (P2): the confidence-decomposition *comparison* (LightGBM's real 4-factor score vs. VQR's 3-factor-renormalized, non-comparable score, with the explicit "don't compare these two numbers directly" caveat from `docs/PHASE_5_REPORT.md` §3) is not shown anywhere in the product — only the classical side's confidence shows up today, since only LightGBM drives real recommendations. Worth adding once a VQR-backed recommendation path exists (currently, `/recommend` only accepts a COMPLETE forecast run, which VQR runs can satisfy — the recommendation *would* show the degraded/partial confidence breakdown if generated; this is more a UI-completeness gap than a backend one).

## Phase 6 → The Product Itself

Phase 6 is not "research feeding the product" — it *is* the product, in its first real form. Its own findings (two real bugs caught via manual verification, not unit tests) are documented in `docs/PHASE_6_PROGRESS_REPORT.md` and `docs/BUTTON_INTERACTION_MATRIX.md`, which should be treated as living documents, updated as the product surface grows, not archived like the numbered research-phase reports.

## Cross-Cutting Principle

Every research-phase JSON file under `experiments/results/` is already the authoritative source for its corresponding product display — the integration work throughout this plan is consistently a *display* task (build a component, wire it to an existing endpoint or a new thin read-only one), never a *recompute* task. No new experiments are implied by this plan. Where a product page would need a number qsci_core doesn't currently compute (e.g. supplier risk, capacity risk — see `/risk` in the feature matrix), the honest move is to label that dimension PENDING in the UI, not to approximate it with a fabricated placeholder.
