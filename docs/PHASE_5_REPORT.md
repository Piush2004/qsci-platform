# Phase 5 — Business-Impact Benchmark & Consolidation

Status: **COMPLETE**
Date: 2026-08-20

## 1. Objective

Per CLAUDE.md §8 ("Phase 5 — Business-impact benchmark: classical vs. quantum vs. quantum-inspired under identical conditions, statistical significance testing. Consolidate into `QSCI_Research_Report.ipynb`."). The forecast/routing/business-impact/statistical-significance benchmark itself was already substantially built as `notebooks/07_classical_vs_quantum_comparison.ipynb` (committed `3ce92bd`, audited `docs/CLASSICAL_VS_QUANTUM_COMPARISON_AUDIT.md`, verdict PASS) — re-deriving it here would be redundant. Phase 5's genuine, non-redundant contribution is therefore scoped to two real gaps identified by inspecting the existing work before writing anything:

1. **The CONFIDENCE layer** (CLAUDE.md's DATA→...→FINANCIAL IMPACT→**CONFIDENCE**→RECOMMENDATION pipeline) had never been applied to the classical-vs-quantum comparison — Phase 1's confidence-decomposition module (`qsci_core/confidence/decomposition.py`) was validated standalone and against classical forecasts (`notebooks/02_classical_forecasting.ipynb`), but never against the quantum forecasting track.
2. **Phase 4's findings were not yet folded into the master synthesis** — `notebooks/07` and the consolidated report predate Phase 4 by commit order.

## 2. What Was NOT Redone

Forecasting accuracy/runtime/resource comparison (Sections 5-11), routing feasibility/cost/gap/runtime/resource comparison (Sections 12-21), business-impact dollar translation (Section 22, ILLUSTRATIVE), the master scorecard (Section 23), and the statistical tests (DM test §7, Mann-Whitney §20) — all pre-existing, all already audited, unchanged in this phase except for their numbers refreshing under VQR's already-documented non-determinism when the notebook was re-executed (§6 below).

## 3. Confidence-Layer Synthesis (New — `notebooks/07` §35)

Applied `qsci_core.confidence.decomposition` (unmodified, Phase 1 code) to both forecasting tracks on the identical 14-day bounded-window test period:

| Component | LightGBM | VQR (N=4/8/12) |
|---|---|---|
| `data_quality` | 1.0000 (0 missing, 0 duplicates, live M5 series check) | 1.0000 (same — dataset property, not model-dependent) |
| `forecast_stability` | 0.6043 (mean over 14 days, real p10/p50/p90) | **N/A — structurally undefined** (VQR is a point forecaster) |
| `model_consensus` (vs. seasonal-naive for LightGBM; vs. LightGBM-p50 for VQR) | 0.8831 | 0.7525 / 0.7574 / 0.7645 |
| `backtest_performance` | 0.5459 (from bounded-window wMAPE) | 0.6511 / 0.6894 / 0.6792 |
| **Overall** | **0.7583** (real 4-factor weighted average) | 3-factor renormalized only (0.80–0.82) — **not directly comparable**, different weight scheme |

**Key finding**: the confidence framework itself exposes a real, previously undocumented architectural gap — **VQR cannot produce the `forecast_stability` signal at all** in its current design (no native quantile/uncertainty output). This is disclosed explicitly rather than papered over with an invented proxy value (the module's weight for the missing component is set to 0, not silently defaulted). A quantum forecast could not currently feed the same recommendation pipeline (`qsci_core/recommendation/builder.py`) a classical forecast already can without this gap being addressed — a concrete, actionable finding beyond "VQR has higher wMAPE."

The two "overall" numbers are **not comparable** (different weight denominators) — the notebook states this explicitly; only the shared three components should be compared directly.

## 4. Phase 4 Integration (New — `notebooks/07` §36)

Loaded `experiments/results/phase4_noise_and_scaling_results.json` live and added `experiments/results/table9_phase5_phase4_refinements.csv`, reframing two of Phase 3's apparent walls:

| Dimension | Phase 3 framing | Phase 4 refinement |
|---|---|---|
| Routing feasibility collapse | Structural-looking (90%→10%→0%, N=8→12) | Sampling artifact — recovers to 100%/100%/60% with more `num_reads`, near-zero cost |
| QAOA depth | Untested past p=1 | p=2/p=3: no cost improvement, feasibility not monotonic, 1.85-2.66x more runtime |
| QAOA runtime wall | Mechanism undetermined | Execution-cost-dominated; Aer backend measured ~38x faster than `StatevectorSampler` at the same size — partly a simulator-choice artifact |

## 5. Consolidation (`QSCI_Research_Report.ipynb`)

Rebuilt to include `notebooks/06_noise_and_scalability.ipynb` as Part 6 (research order: data quality → classical forecasting → quantum forecasting → classical routing → quantum routing QUBO → **noise & scalability** → classical-vs-quantum synthesis), which the previous consolidation (commit `0ba9e3f`) predates. 184 cells total (was 134), 88 code cells, executed top-to-bottom in one kernel session, **0 errors**. Build script: `experiments/build_consolidated_report.py`.

## 6. Non-Determinism (Expected, Documented, Not a Bug)

Re-executing the consolidated report re-ran notebook 03's live VQR training, which regenerated `quantum_forecasting_results.{json,csv}` and cascaded into `classical_vs_quantum_results.*` and 10 PDF figures with fresh, non-deterministic VQR numbers (same mechanism Phase 2.1 documented: COBYLA + statevector-sampling non-determinism). Spot-checked: the qualitative pattern is unchanged — classical still wins forecasting accuracy by a wide margin (e.g. VQR N=4 leakage-corrected wMAPE moved from 34.89% to a re-run value within the same range; master scorecard `experiments/results/table8_master_scorecard.csv` unchanged in every "winner" column). This exact regeneration pattern was already precedented and disclosed in commit `0ba9e3f`'s own message.

## 7. Claim Audit

Grepped both modified notebooks for banned phrases ("quantum advantage/supremacy/faster/scalable/wins/competitive"). Every hit is a section header ("Quantum Advantage Analysis") or an explicit negation ("No claim of quantum advantage is made anywhere in this section", "None of this establishes a quantum advantage on any dimension"). No unqualified positive claim found.

## 8. Test Suite

`pytest -q`: **176 passed, 1 xfailed** (unchanged from Phase 4's post-change count — Phase 5 added no new `qsci_core` code, only notebook cells and a small confidence-application script, so no new tests were needed; existing `test_confidence.py` already covers the module used).

## 9. What Remains PENDING (Disclosed, Not Silently Skipped)

Per CLAUDE.md's full pipeline (DATA→QUALITY→FORECAST→RISK→OPTIMIZATION→FINANCIAL IMPACT→CONFIDENCE→RECOMMENDATION→**HUMAN APPROVAL→AUDIT→OUTCOME**): the last three stages require a live UI/backend loop (`qsci_core/persistence`, `qsci_core/recommendation` exist and are unit-tested, but nothing wires them to an actual human-in-the-loop approval flow yet) — this is explicitly **Phase 6**, not attempted here.

## 10. Files Changed/Added

- `docs/PHASE_5_REPORT.md` (this file)
- `notebooks/07_classical_vs_quantum_comparison.ipynb` — +12 cells (Sections 35-37), re-executed, 66 cells total, 0 errors
- `notebooks/QSCI_Research_Report.ipynb` — rebuilt with Part 6 (notebook 06) inserted, 184 cells, 0 errors
- `experiments/build_consolidated_report.py`, `experiments/phase5_append_notebook07.py` — build scripts
- `experiments/results/table9_phase5_phase4_refinements.csv` — new
- `experiments/results/quantum_forecasting_*`, `classical_vs_quantum_*`, `table1_forecast_comparison.csv`, `table5_implementation_complexity.csv`, `table8_master_scorecard.csv`, and 10 `paper/figures/*.pdf` — regenerated by the live re-execution (expected VQR non-determinism, §6), qualitative conclusions unchanged

## 11. Research Conclusion (Unchanged, Refined)

RQ6/H5 remains unsupported (Phase 3's conclusion stands). Phase 5 adds: (a) a concrete production-readiness gap for quantum forecasting (no native uncertainty quantification, surfaced by the confidence framework), and (b) confirmation that two of Phase 3's routing "walls" are partly configuration/implementation artifacts rather than fundamental limits (Phase 4's findings, now folded into the synthesis). No quantum advantage is claimed on any dimension.
