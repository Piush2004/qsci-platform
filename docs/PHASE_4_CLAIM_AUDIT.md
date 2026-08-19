# Phase 4 Adversarial Claim Audit

Status: **COMPLETE**
Date: 2026-08-19
Scope: independently re-verifies Phase 4's key claims against raw evidence before they are accepted into `docs/PHASE_4_REPORT.md`. Performed single-threaded by the main session (not spawned subagents), per CLAUDE.md §11's explicit instruction to hold off on multi-agent setups until Phase 6 — this overrides the takeover prompt's suggestion of dedicated audit agents for this phase.

| TEST | INPUT | EXPECTED | ACTUAL | STATUS | EVIDENCE |
|---|---|---|---|---|---|
| Default noiseless QAOA path unchanged from Phase 3 | `solve_qubo_with_qaoa(qi, p=1, maxiter=20, shots=1024, seed=42)` with and without explicit `noise_preset="noiseless"` | Identical sample/energy, `StatevectorSampler` label | Identical — `tests/test_qaoa_noise.py::test_qaoa_noiseless_default_unchanged` passes | PASS | pytest run: 176 passed, 1 xfailed (was 168 passed pre-Phase-4; +8 new tests, 0 regressions) |
| No D-Wave hardware credentials present in this environment | `env \| grep -i DWAVE`, check `~/.config/dwave` | No token, no config file | No `DWAVE_API_TOKEN`/`DWAVE_API_KEY`, no config file found | CONFIRMED | Shell output, this audit |
| Noise-model labels never claim "hardware" | `result.metadata.simulator` string for every noise preset | "hardware" substring absent | Absent — `assert "hardware" not in result.metadata.simulator.lower()` | PASS | `tests/test_qaoa_noise.py::test_qaoa_with_depolarizing_noise_runs_and_labels_honestly` |
| Report's QAOA p=1/2/3 table matches raw JSON exactly | `experiments/results/phase4_noise_and_scaling_results.json`'s `part_d_qaoa_depth_sweep` vs. `docs/PHASE_4_REPORT.md` §5 table | Byte-for-byte matching feasible counts, costs, runtimes | p=1: 5/5, 380.008, 38.00s; p=2: 3/5, 380.008, 70.35s; p=3: 4/5, 380.008, 101.14s — all match | CONFIRMED | Direct JSON read, this audit |
| Unified results file (Step 12 schema) has no missing/duplicate rows | `experiments/results/phase4_noise_scalability.{json,csv}` | JSON/CSV row counts match; all 16 required fields present | 26 rows in both; all fields present: experiment, method, problem_size, seed, noise_preset, qaoa_depth, num_reads, objective, gap, feasible, runtime, qubits, depth, gates, status, label | CONFIRMED | Direct file read, this audit |
| All 10 required figures generated, non-trivial size | `paper/figures/phase4_*.pdf` | 10 files, each >0 bytes | 10 files present, 14.2KB–18.0KB each (real rendered PDFs, not empty placeholders) | CONFIRMED | `ls -la`, this audit |
| Banned-claim scan across all Phase 4 artifacts | grep for "quantum advantage/supremacy/faster/scalable/wins/competitive" across report, notebook, code, tests | Zero unqualified positive claims | 3 occurrences of "quantum advantage" found, all negations ("No quantum advantage is claimed", "does not establish", "Neither refinement establishes") | PASS | grep output, this audit |
| Notebook executes top-to-bottom with 0 errors | `jupyter nbconvert --execute` on `notebooks/06_noise_and_scalability.ipynb` | 0 cells with `output_type == 'error'` | 0 errors across 19 code cells (40 total cells) | CONFIRMED | nbconvert run + programmatic error-cell scan, this session |
| Existing QAOA/annealing/routing tests unaffected by Phase 4 changes | Full `pytest -q` | All previously-passing tests still pass | 176 passed, 1 xfailed, 0 failed (same 1 xfail as pre-Phase-4) | CONFIRMED | pytest run, this session |
| Noise-sensitivity "0% degradation" claim is honestly caveated, not overclaimed | `docs/PHASE_4_REPORT.md` §6 and notebook §07 | Explicit disclosure that best-of-1024-shots metric can mask distributional degradation | Present in both report and notebook, plus marked PENDING for the un-run success-probability measurement | CONFIRMED | Direct text read, this audit |

## Verdict

**PASS.** No fabricated result, no hidden classical repair (Phase 4 introduces no repair logic at all), no unqualified quantum-advantage claim, and no silent extrapolation found. The one genuinely surprising number (Aer ~38x faster than StatevectorSampler) is reported as a simulator-implementation artifact, not oversold as a quantum-performance finding. Sample-size reductions (5 seeds vs. Phase 3's 10) are documented at every point they occur, with explicit "too small to call this significant" language where relevant (QAOA depth-vs-feasibility trend, §5).
