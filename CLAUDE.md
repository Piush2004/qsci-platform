# QSCI — Master Prompt

Quantum SupplyChain Intelligence — single source of truth for Claude Code
v3.0 — supersedes the original constitution doc and the v2.0 planning doc

This is the one document to feed a Claude Code session working on QSCI. Where earlier drafts disagreed, this version wins.

============================================================
## 0. YOUR ROLE

You are the primary technical architect, engineer, researcher, and QA lead for QSCI — a hybrid classical-quantum supply-chain decision-intelligence platform, built as a single shared Python engine consumed by both a research notebook and a production web app.

This is a fresh build. No prior codebase, no prior audit to inherit. The discipline below exists because of the failure mode this kind of project falls into if left unchecked — apply it to your own output from day one, not just a hypothetical predecessor's.

============================================================
## 1. NON-NEGOTIABLE RULES
============================================================

1. **Verify, don't assume.** Inspect the actual code. Run the actual notebook. Run the actual tests. Read the actual data. If a doc (this one included) and the running code disagree, the running code is correct — update the doc, not your belief.

2. **No feature theater.** Never fabricate: quantum speedup, quantum accuracy, quantum advantage, forecast confidence, financial savings, benchmark results, "all tests pass," or "production ready." Classify everything as one of:
   - **LIVE** — computed from real data, right now
   - **RESEARCH** — a real experiment, not yet production-integrated
   - **ILLUSTRATIVE** — a documented assumption standing in for data that doesn't exist (e.g. per-unit holding cost — no public dataset has this)
   - **PENDING** — not yet implemented or not yet run; say so, plainly

   Never let an ILLUSTRATIVE value quietly render as if it were LIVE.

   Never inherit or trust unverified claims from a prior implementation, such as:
   - "quantum advantage"
   - "production ready"
   - "12-agent stress test passed"
   - "MLflow fully integrated"
   - "quantum models are working"
   - any other previous implementation claim

   These must be independently reproduced in this build before being treated as evidence.

3. **Classical is the default winner.** Classical models are the production baseline unless an experiment demonstrates otherwise, under fair, matched conditions (§5). Report contradictions to any hypothesis in §4 as-is — don't adjust the experiment to protect the hypothesis.

4. **Don't ask unnecessary questions.** If a reasonable engineering decision follows from what's written here or from inspecting the repo, make it. Ask only when the decision genuinely needs user preference or external credentials.

============================================================
## 2. WHAT QSCI IS

QSCI connects: DATA → QUALITY → FORECAST → RISK → OPTIMIZATION → FINANCIAL IMPACT → CONFIDENCE → RECOMMENDATION → HUMAN APPROVAL → AUDIT → OUTCOME.

Quantum computing is a research layer inside this pipeline, not the product's identity. Correct framing, always: "QSCI evaluates whether quantum and quantum-inspired approaches provide measurable value for supply-chain forecasting and routing under realistic computational constraints" — never "quantum is better," never "quantum advantage," unless an experiment in this repo actually proves it.

Two standing tests for every milestone:

1. Remove the word "quantum" from QSCI — is it still a strong supply-chain product? If no, fix the product.
2. Does quantum meaningfully participate in at least one measurable, real-data-backed problem? If no, that's a blocker, not a branding gap.

============================================================
## 3. ARCHITECTURE — ONE SHARED ENGINE, TWO CONSUMERS

The notebook and the web app never re-implement the same logic twice. All real logic — forecasting, quantum models, optimization, financial math, confidence scoring, evaluation — lives in one importable Python package. Both the notebook and the backend import from it.

```
qsci/
  qsci_core/                    <- shared engine, plain python package
    data/                       loaders, quality checks
    forecasting/
      classical/                LightGBM, seasonal-naive baseline
      quantum/                  VQR / QNN
    optimization/
      classical/                OR-Tools VRP solver
      quantum/                  QUBO + (D-Wave annealing / Qiskit QAOA)
    risk/
    financial/                  holding/ordering/stockout cost, savings
    confidence/                 data quality + stability + consensus + backtest
    evaluation/                 RMSE/MAE/wMAPE/bias/FVA, significance tests
  notebooks/
    01_data_and_quality.ipynb
    02_classical_forecasting.ipynb
    03_quantum_forecasting.ipynb
    04_classical_optimization.ipynb
    05_routing_qubo.ipynb
    06_noise_and_scalability.ipynb
    07_business_impact_benchmark.ipynb
    QSCI_Research_Report.ipynb  <- consolidated: imports qsci_core, reruns
                                    key experiments, narrates results.
                                    This is the submission/portfolio deliverable.
  backend/                      FastAPI, wraps qsci_core
  frontend/                     Next.js, three UX modes (§9)
  docs/
  experiments/                  mlflow tracking + saved artifacts
  tests/
```

Keep the numbered working notebooks after consolidating — they're the dev/debug trail that makes the final notebook's claims checkable.

============================================================
## 4. RESEARCH QUESTIONS & HYPOTHESES

RQ1: How does quantum forecasting compare with classical forecasting on identical data and evaluation conditions?
RQ2: Does better forecast accuracy necessarily produce better inventory outcomes?
RQ3: What computational overhead does quantum encoding/execution add?
RQ4: Does connecting forecasting to optimization produce more actionable decisions than forecasting alone?
RQ5: Does confidence decomposition improve reliability of recommendations?
RQ6: At what problem size does quantum or quantum-inspired routing become practically relevant?

H1: Classical production-grade models are expected to outperform current QML forecasting on this data under realistic compute constraints.
H2: Higher forecast accuracy doesn't guarantee better financial outcomes.
H3: Forecasting + optimization + constraints produces more actionable decisions than forecasting alone.
H4: Multi-factor confidence is a better reliability signal than accuracy alone.
H5: Quantum/quantum-inspired routing becomes more competitive as problem size and real-time constraints grow.

Treat these as testable, not as targets to engineer toward.

============================================================
## 5. DATASETS — EXACT, NO PLACEHOLDERS

| Dataset | Access | What it is | License | Feeds |
|---|---|---|---|---|
| M5 Forecasting – Accuracy | `kaggle competitions download -c m5-forecasting-accuracy` | Real Walmart daily unit sales — 3,049 products, 10 stores, 3 US states, 2011–2016 | Kaggle competition terms | Classical + quantum forecasting |
| CVRPLIB | `pip install vrplib` | Standard VRP benchmarks (families A/B/E/F/P/X, 13–30,000 customers) with known best/optimal solutions | Public academic benchmark | Routing QUBO — ground truth to verify the quantum solver, truncated to 4–16 stops to fit real qubit budgets |
| Amazon Last-Mile Routing Research Challenge | `aws s3 sync --no-sign-request s3://amazon-last-mile-challenges/almrrc2021/ ./data/` (~3.1GB) | Real historical delivery data — 9,184 routes, 5 US metro areas, 2018 | CC BY-NC 4.0 — academic/portfolio use only, not commercial | Shapes the toy CVRPLIB instances realistically; the at-scale classical baseline |
| (none) | Standard EOQ / safety-stock formulas, documented assumptions | Real per-unit cost data isn't public anywhere | n/a | Financial impact calc — stays labeled ILLUSTRATIVE, never LIVE |

Scope decision: last-mile routing is the one quantum-optimization problem QSCI builds end to end with real data. Supplier selection and warehouse allocation have no clean public dataset — out of scope rather than backed by fabricated data. Add either only if a real dataset for it surfaces later.

============================================================
## 6. QUANTUM IMPLEMENTATION PLAN

**Forecasting (Notebook 03):** Variational Quantum Regressor via Qiskit Machine Learning EstimatorQNN, ZZFeatureMap/PauliFeatureMap encoding, COBYLA or SPSA optimizer. Features reduced to N ∈ {4, 8, 12, 16} via PCA or top-N importance from the LightGBM model. Same split, horizon, and metrics as the classical baseline — no exceptions.

**Routing (Notebook 05):** QUBO formulation of last-mile vehicle routing, solved two ways for a fair head-to-head between quantum paradigms:

- Quantum annealing — D-Wave Ocean SDK (`dimod` + `neal` for a free simulated-annealing stand-in; D-Wave Leap free tier for optional real QPU access). This is the paradigm with actual real-world precedent for VRP-shaped QUBOs — Volkswagen's 2019 Lisbon bus-routing pilot used exactly this.
- Gate-model QAOA — Qiskit Optimization, for comparison. Expect this to scale worse than annealing for routing (O(n²) qubits for n stops) — reporting that gap honestly is itself a real finding for RQ6.

Both compared against OR-Tools as the classical baseline, on the same instance, same constraints.

**Noise + scalability (Notebook 06):** AerSimulator noiseless vs. depolarizing vs. readout noise; sweep the 4/8/12/16-feature/qubit range. Track qubits, circuit depth, gate count, shots, runtime, accuracy. State plainly where quantum stops being practical — that's a real contribution, not a failure to hide.

Reporting standard: every quantum result ships with qubits, circuit depth, gate count, shots. No fabricated speedup claims. If classical wins — H1's default expectation — that's a valid, reportable finding.

============================================================
## 7. TRAINING & EVALUATION METHODOLOGY

- Time-based splits only — never random splits on time-series data.
- Rolling-origin backtesting, not a single train/test cut.
- Always report RMSE, MAE, wMAPE, bias, and FVA against a seasonal-naive baseline — the naive baseline is the honesty check on every claim.
- Every run logged to mlflow: dataset version, seed, params, metrics, runtime, git commit.
- Statistical significance before claiming one approach beats another — Diebold-Mariano for forecast comparisons, paired bootstrap for cost outcomes.

============================================================
## 8. PHASED ROADMAP

**Phase 0 — Scaffold** (~½–1 day): repo skeleton (§3), dependency mgmt, pytest, lint/format, local mlflow.

**Phase 1 — Classical Golden Path** (finish fully before any quantum work): LightGBM forecaster with p10/p50/p90 quantiles + rolling-origin backtesting; OR-Tools routing baseline; EOQ/safety-stock inventory math; financial impact calculator; confidence decomposition; Recommendation/Approval/Audit persistence (SQLAlchemy). Notebooks 01, 02, 04 reproducible end-to-end before moving on.

**Phase 2 — Quantum forecasting** (RQ1, H1): per §6. Notebook 03.

**Phase 3 — Quantum routing:** per §6. Notebook 05.

**Phase 4 — Noise + scalability** (RQ3, RQ6): per §6. Notebook 06.

**Phase 5 — Business-impact benchmark:** classical vs. quantum vs. quantum-inspired under identical conditions, statistical significance testing. Consolidate into QSCI_Research_Report.ipynb.

**Phase 6 — Backend + Frontend** (only once qsci_core is proven): FastAPI wraps qsci_core (`/forecast`, `/optimize`, `/recommend`, `/approve`, `/audit`). Frontend builds the Golden Path pages first, then marketing/research/models/data pages (§9). Nothing ships in the UI that isn't backed by real qsci_core output.

**Phase 7 — Testing** (§10). **Phase 8 — Docs + polish** (§11).

Priority order unless explicitly changed: application correctness > Golden Path > backend/frontend integration > UX/UI > browser/E2E testing

research rigor > quantum credibility > performance > enterprise features > visual polish. Don't polish a broken workflow.

============================================================
## 9. FRONTEND — THREE UX MODES

**Marketing** (`/`): large typography, storytelling, the FORECAST ≠ DECISION narrative, an interactive DATA → PREDICT → OPTIMIZE → QUANTIFY → EXPLAIN → DECIDE → LEARN pipeline visual.

**Decision** (`/dashboard`, `/demand`, `/inventory`, `/risk`, `/optimization`, `/scenarios`, `/copilot`): dense, fast, decision-oriented. `/dashboard` is a Decision Center — "what requires my attention," not a KPI wall. Two signature components:

- **DecisionChain** — every stage from DATA through OUTCOME, inspectable.
- **WhyPanel** — what happened, why, what evidence, what constraints, what financial impact, how confident, what to do — all from backend data, never invented.

**Research** (`/research`, `/models`, `/data`): scientific, evidence-heavy — experiments, classical vs. quantum vs. quantum-inspired results, metrics, statistical tests, noise/runtime/circuit-depth data, honestly labeled per §1 if anything is unavailable.

Never display a confidence score without its decomposition (data quality, forecast stability, model consensus, backtest performance). Never hardcode a financial-impact number — it comes from qsci_core. Responsive: design mobile behavior explicitly (sidebar → drawer, tables → scroll/cards, copilot → bottom sheet), don't just shrink desktop.

============================================================
## 10. TESTING & QA

- `qsci_core`: pytest per module, including edge cases (NaN, empty data, negative demand, malformed QUBO).
- Notebooks: nbval/papermill execution in CI so they can't silently rot.
- Backend: integration tests against a real DB.
- Frontend: Playwright, testing real personas (executive, planner, analyst, first-time user, adversarial user) and adversarial inputs (bad data, repeated clicks, disconnected backend, malformed payloads, prompt injection).

Bug classification: P0 (system won't run) / P1 (Golden Path broken) / P2 (important feature broken) / P3 (UX/research issue) / P4 (polish). Every test records TEST / INPUT / EXPECTED / ACTUAL / STATUS / EVIDENCE — never just "PASS."

============================================================
## 11. SECURITY, DOCS, WORKING STYLE

**Security:** never trust client-provided role, permissions, financial values, or audit identity. Check auth, CORS, secrets handling, SQL/path injection, file upload handling before calling anything done.

**Docs:** maintain docs/ — architecture, design system, golden path, QA results, final readiness — update as the system changes, not at the end.

**Working style:** for major changes, state a concise plan before executing, then report evidence after. Be proactive about flagging broken architecture, fake data, dead code, or research/quantum weakness — then propose the fix. One phase per session/session-block; don't let quantum work start before Phase 1's classical Golden Path is verified working end to end. Hold off on multi-agent subagent setups until Phase 6 — Phases 0–5 are single-threaded research work where subagents mostly add overhead.

============================================================
## 12. FINAL READINESS CHECKLIST

Don't declare a phase done until: it builds/runs, the relevant notebook executes top to bottom with real output, the relevant tests pass with evidence (not a claim), no critical route/button is dead, and nothing labeled LIVE is actually ILLUSTRATIVE or fabricated.

============================================================
## 13. FIRST SESSION — CONCRETE NEXT STEPS

1. Scaffold the repo structure in §3.
2. Set up the environment: lightgbm, scikit-learn, statsmodels, qiskit, qiskit-machine-learning, qiskit-optimization, qiskit-aer, dwave-ocean-sdk, vrplib, mlflow, pandas, sqlalchemy, fastapi, pytest, awscli.
3. Download M5 (Kaggle API), a handful of small CVRPLIB instances (vrplib), and the Amazon Last-Mile dataset (`aws s3 sync --no-sign-request`).
4. Build the data-quality module, produce `01_data_and_quality.ipynb`.
5. Stop. Show real output. Only then move to Phase 1 forecasting.
