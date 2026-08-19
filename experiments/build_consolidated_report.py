"""Rebuilds notebooks/QSCI_Research_Report.ipynb by concatenating the
numbered working notebooks in research order, now including 06 (added in
Phase 4, absent from the previous consolidation which predates it).
Mirrors the structure of the existing consolidated report exactly (title
cell, then one '# Part N -- Title' marker + that notebook's cells,
per notebook), then the whole thing is executed top-to-bottom in one
kernel session, per CLAUDE.md sec.3."""

import nbformat as nbf

PARTS = [
    ("01_data_and_quality.ipynb", "Data & Quality"),
    ("02_classical_forecasting.ipynb", "Classical Forecasting"),
    ("03_quantum_forecasting.ipynb", "Quantum Forecasting"),
    ("04_classical_optimization.ipynb", "Classical Optimization"),
    ("05_routing_qubo.ipynb", "Quantum Routing (QUBO)"),
    ("06_noise_and_scalability.ipynb", "Noise & Scalability"),
    ("07_classical_vs_quantum_comparison.ipynb", "Classical vs. Quantum: Synthesis Comparison"),
]

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3 (QSCI .venv)", "language": "python", "name": "qsci"},
    "language_info": {"name": "python"},
}

title = r"""# QSCI Research Report — Consolidated Notebook

**Quantum SupplyChain Intelligence** — this notebook merges the numbered working notebooks (`01`-`07`) into a single, top-to-bottom executable research narrative, per `CLAUDE.md` §3 (`QSCI_Research_Report.ipynb <- consolidated: imports qsci_core, reruns key experiments, narrates results. This is the submission/portfolio deliverable.`).

The numbered working notebooks are kept as-is alongside this one — they remain the dev/debug trail that makes every claim below independently checkable, per the same section: *"Keep the numbered working notebooks after consolidating."*

**Structure**:
1. Data & Quality — real M5, CVRPLIB, and Amazon Last-Mile datasets, quality-audited.
2. Classical Forecasting — LightGBM vs. seasonal-naive, rolling-origin backtest, full Golden Path (risk, financial, confidence, recommendation, persistence).
3. Quantum Forecasting — Variational Quantum Regressor (VQR) vs. the same classical baseline under matched conditions.
4. Classical Optimization — OR-Tools CVRP against real CVRPLIB ground truth and an actual historical Amazon Last-Mile route.
5. Quantum Routing (QUBO) — simulated annealing and QAOA vs. OR-Tools on an identical QUBO, including the brute-force validation that caught and fixed a real formulation bug.
6. Noise & Scalability — QAOA runtime-wall root cause, annealing feasibility recovery via sampling, noise sensitivity, and the p=1/2/3 depth tradeoff (Phase 4).
7. Classical vs. Quantum: Synthesis Comparison — the rigorous, publication-quality head-to-head across forecasting, routing, and the confidence-decomposition layer, statistically tested, with a programmatically-derived research conclusion (Phase 5).

**A note on notebook-local state**: each part below is deliberately self-contained — it reloads its own data and redefines its own working variables (`PROJECT_ROOT`, `series_df`, `results_df`, etc.) exactly as its original standalone notebook did. Later parts intentionally overwrite same-named variables from earlier parts (e.g. Part 3's `series_df` replaces Part 2's) — this is safe because no part reads a stale variable from an earlier part; every part's outputs are produced immediately after its own inputs are (re)loaded, so results are identical to running the seven notebooks separately in order.

Every result below is labeled **LIVE** / **RESEARCH** / **ILLUSTRATIVE** / **PENDING** per `CLAUDE.md` §1 — inherited unchanged from each source notebook."""

cells = [nbf.v4.new_markdown_cell(title)]

for i, (fname, part_title) in enumerate(PARTS, start=1):
    marker = f"---\n\n# Part {i} — {part_title}\n\n*(source: `notebooks/{fname}`)*"
    cells.append(nbf.v4.new_markdown_cell(marker))
    src_nb = nbf.read(f"notebooks/{fname}", as_version=4)
    cells.extend(src_nb["cells"])

nb["cells"] = cells
nbf.write(nb, "notebooks/QSCI_Research_Report.ipynb")
print(f"Wrote consolidated report with {len(cells)} cells.")
