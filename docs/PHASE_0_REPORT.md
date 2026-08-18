# Phase 0 Report — Scaffold

Status: **VERIFIED AND CLOSED**
Date: 2026-08-18
Branch: `main`

## 1. Phase Objective

Stand up the repository skeleton, the Python environment, and the three real
source datasets QSCI's classical and quantum work will run against. Nothing
downstream (Phase 1+) starts until this phase is independently checkable —
running code and executed output, not a claim.

## 2. Environment

| Item | Value |
|---|---|
| Python | 3.14.5 (`.venv`, project-local) |
| Package manager | pip, `qsci_core` installed editable (`pip install -e .`) |
| OS | Windows 11 |
| Kernel (Jupyter) | `qsci` — registered against `.venv`, `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` set explicitly (see §7) |

**Note on Python version:** the original master prompt specified Python 3.12
over concerns that `qiskit-aer` lacks Windows wheels for 3.14. That concern
was tested directly on this machine and did not hold — `qiskit-aer 0.17.2`
installs and imports cleanly on Python 3.14. Per user decision, 3.14 was kept
rather than installing a second Python version. If a future dependency
genuinely fails on 3.14, revisit this decision then, with evidence.

## 3. Dependency Verification

All packages verified by direct `import` in the `.venv`, not assumed from a
successful `pip install`:

```
OK  lightgbm                     4.7.0
OK  sklearn                      1.9.0
OK  statsmodels                  0.14.6
OK  qiskit                       2.5.2
OK  qiskit_machine_learning      0.9.0
OK  qiskit_optimization          0.7.0
OK  qiskit_aer                   0.17.2
OK  dimod                        0.12.22
OK  dwave.system                 1.35.0
OK  vrplib                       2.2.0
OK  mlflow                       3.15.1
OK  pandas                       2.3.3
OK  sqlalchemy                   2.0.52
OK  fastapi                      0.141.1
OK  uvicorn                      0.52.3
OK  pytest                       9.1.1
OK  kaggle                       2.2.4
OK  matplotlib                   3.11.1
FAILS: 0
```

`qsci_core` imports cleanly: `D:\Projects\QML project\qsci_core\__init__.py`.

## 4. Dataset Verification & Statistics

| Dataset | Status | Real numbers |
|---|---|---|
| M5 Forecasting – Accuracy | **LIVE** | sales: 30,490 rows × 1,947 cols; calendar: 1,969 rows × 14 cols; prices: 6,841,121 rows |
| CVRPLIB (Augerat A/B) | **LIVE** | 4 instances loaded; best-known costs match published values |
| Amazon Last-Mile Routing Challenge | **LIVE** | 6,112 routes, 904,527 total stops, 5/5 expected files present |
| Per-unit holding/ordering/stockout cost | **ILLUSTRATIVE** | no public dataset exists for this — stays a documented assumption in Phase 1, never rendered as LIVE |

CVRPLIB instance detail (best-known cost verified against the loaded solution file):

| Instance | Dimension | Best-known cost |
|---|---|---|
| A-n32-k5 | 32 | 784 |
| A-n33-k5 | 33 | 661 |
| A-n37-k5 | 37 | 669 |
| B-n31-k5 | 31 | 672 |

## 5. Dataset Provenance

- **M5**: `kaggle competitions download -c m5-forecasting-accuracy` — required accepting competition rules on kaggle.com first (initial attempt returned `403 Forbidden` until the user accepted them). Auth via `~/.kaggle/kaggle.json`, moved there from the user's Downloads folder without its contents ever being read into this session.
- **CVRPLIB**: the URL pattern in the original master prompt (`vrp.atd-lab.inf.puc-rio.br`) 404s — the site has moved to `galgos.inf.puc-rio.br/cvrplib`. Instance/solution files fetched directly from the live site via its numeric instance IDs (verified by cross-referencing instance names in the page HTML, not guessed).
- **Amazon Last-Mile**: `aws s3 sync --no-sign-request s3://amazon-last-mile-challenges/almrrc2021/`. First sync attempt dropped 9 files to connection resets (including the critical `model_build_inputs/travel_times.json` and `package_data.json`); a second `sync` pass (idempotent — skips already-downloaded files) filled every gap. Final size: 3.2GB.

## 6. Known Dataset Anomalies (real findings, not injected)

- **CVRPLIB B-n31-k5** has 2 duplicate node coordinates — flagged by `qsci_core.data.quality.assess_cvrplib_instance`.
- **M5**: `sales_train_evaluation.csv` has 1,941 day columns (`d_*`) but `calendar.csv` has 1,969 rows — expected, since the evaluation file's forecast horizon extends beyond what the day columns cover; flagged automatically by `assess_m5`.
- **M5**: 68.00% zero-inflation in unit sales, 4.44% IQR-outlier rate in `sell_price` — both real properties of the M5 series, not errors, but relevant for Phase 1 model design (intermittent demand).

## 7. Notebook Execution

`notebooks/01_data_and_quality.ipynb` executes top-to-bottom via
`jupyter nbconvert --execute --inplace` against the `qsci` kernel. All three
dataset sections report **LIVE** with the real numbers above; no cell errors.

A real bug was found and fixed during this phase: the kernel's default
Windows stdout codepage (`cp1252`) was silently corrupting em dashes in
printed output to `�` (U+FFFD). Fixed by setting `PYTHONUTF8=1` and
`PYTHONIOENCODING=utf-8` in the kernelspec's `env`
(`%APPDATA%\jupyter\kernels\qsci\kernel.json`). Verified fixed — 0 cells
contain the replacement character after the fix.

## 8. Tests

```
tests/test_quality.py::test_assess_dataframe_flags_missing_and_negative PASSED
tests/test_quality.py::test_assess_dataframe_empty PASSED
tests/test_quality.py::test_assess_m5_detects_negative_sales_and_date_range PASSED
tests/test_quality.py::test_assess_cvrplib_instance_flags_capacity_violation PASSED

4 passed in 1.04s
```

## 9. Status Classification Terminology

This phase updated the classification vocabulary from
`LIVE / RESEARCH / ILLUSTRATIVE / NOT IMPLEMENTED` to
`LIVE / RESEARCH / ILLUSTRATIVE / PENDING`, applied consistently in
`CLAUDE.md` and `notebooks/01_data_and_quality.ipynb`. No other wording,
architecture, dataset, phase ordering, or hypothesis content changed.

`CLAUDE.md` §1 rule 2 also now names specific unverified claims (e.g.
"quantum advantage," "production ready," "12-agent stress test passed,"
"MLflow fully integrated," "quantum models are working") that must never be
inherited from a prior implementation without independent reproduction in
this build.

## 10. Acceptance Criteria (per CLAUDE.md §12)

| Criterion | Result |
|---|---|
| Builds/runs | ✅ `.venv` installs and imports cleanly |
| Notebook executes top-to-bottom with real output | ✅ |
| Tests pass with evidence | ✅ 4/4, output above |
| No critical route/button dead | N/A — no UI in this phase |
| Nothing labeled LIVE is actually ILLUSTRATIVE/fabricated | ✅ all LIVE claims backed by loader output shown above |

## 11. Known Limitations

- The repo scaffold (`qsci_core`, `notebooks`, `tests`, `CLAUDE.md`,
  `pyproject.toml`) was uncommitted until this phase's closing commit — no
  prior Phase 0 work existed in git history before this session.
- `backend/`, `frontend/`, `docs/`, `experiments/` directories exist but are
  empty scaffolding — git does not track empty directories, so they will not
  appear as tracked paths until Phase 6+ adds real files.
- `data/raw/` (M5, CVRPLIB, Last-Mile) is gitignored by design — real data
  is reproducible from the provenance in §5, not stored in the repo.
- The 165 files deleted from the previous implementation
  (`ai_engine/`, old `backend/`, old `frontend/`, etc.) remain as pending
  deletions in git working tree from before this session; this commit does
  not touch them one way or the other unless explicitly included.
