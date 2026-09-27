# E-002 tasks  -- EXPERIMENT AT A STOPPING POINT 2026-09-27 (RESULT.md); F2 breadth open (M2-bound evidence)

Dispatched 2026-09-27 by the operator to a fresh Claude worker on ubu002 (instruction: HANDOFF_INSTRUCTION_verbatim.md).
Archaeon relays Git transitions only and does not brief the worker.

| Task | Work | Status | Executor | Host |
|---|---|---|---|---|
| T-007 | state the candidate continuity criterion | DONE (T-007_CRITERION.md) | Artemis | ubu002 |
| T-008 | apply it to the synthetic recombination fixtures | DONE (A-001) | Artemis | ubu002 |
| T-009 | apply it to the preserved PTE cases | DONE (A-001 repro, A-002 arch + sweep, A-003 GA) | Artemis | ubu002 |
| T-010 | search for cases where the criterion invents continuity | DONE for PTE / Git-resident NPE+Archaeon samples; F2 breadth needs M2 evidence | Artemis | ubu002 |
| T-011 | compare material continuity with any usable architecture-level continuity | DONE (from T-009 A-002) | Artemis | ubu002 |
| T-012 | adjudicate B1 and write the result | DONE (RESULT.md) | Artemis | ubu002 |

## Inputs (everything from Git at ca189b020; no M2 disk)
- Code: archaeon/causal_lens/e002_continuity.py (sha256 5a57f964..., stdlib) and e002_pte.py (0179d549...); frozen
  schema_v02 / corpus_v02 / adapters_v02 (untouched); PTE engine prometheus/ananke (search.py f3e628f7..., read-only).
- Data: roles/Ananke/pte/c1_rows/cells.jsonl.gz (a659c1e0...); archaeon/causal_lens/out_v02/PTE_V02.json, PTE_ARCH_V02.json,
  NPE_V02.json; archaeon/tests/fixtures_v03/archaeon_block13_sample.json.
- Commands (repo root):
  `python3 -m archaeon.causal_lens.e002_continuity fixtures out/T-008_fixtures.json`
  `python3 -m archaeon.causal_lens.e002_pte {repro|arch|ga} out/T-009_{repro|arch|ga}.json`
  `python3 -m pytest -q archaeon/tests/test_e002_continuity.py archaeon/tests/test_causal_lens_*.py`   (name files: a directory-wide
  run hits a conftest that needs Postgres on localhost)
- Needs: numpy + torch (CPU) for e002_pte only. On ubu002 they were absent; installed from apt (python3-numpy 2.3.5, python3-torch 2.9.1).
- Resources: < 2 min per PTE step, <= 3 threads, < 400 MB.
- Verification: in-repo. repro compares against the committed out_v02 files; no host holds anything this experiment needs beyond Git.

## Attempts
| Attempt | Task | Host | Result |
|---|---|---|---|
| A-001 | T-008 | ubu002 | DONE. 15 fixtures, 17 events; out/T-008_fixtures.json (sha256 0e196f1c...). 0 v0.2 violations for any C-OP value |
| A-001 | T-009 repro | ubu002 (Linux, numpy 2.3.5, torch 2.9.1) | DONE. 48/48 identical to PTE_ARCH_V02.json (M2, Windows); parent signatures identical; masks sha256 ffca223c...; 24 s, 363 MB. out/T-009_repro.json (c67d5618...) |
| A-002 | T-009 arch + sweep | ubu002 | DONE. Repro rerun (identical) + 204-child share sweep; 113 s. out/T-009_arch.json (2c12b5ad...) |
| A-003 | T-009 GA crossovers | ubu002 | DONE. Instrumented replay; 16/16 mask counts equal PTE_V02.json; 4 self-crosses found; 29 s. out/T-009_ga.json (522cda35...) |
| (not an attempt) | environment | ubu002 | numpy/torch missing: installed via apt before A-001 (T-009). A directory-wide pytest run errors on a Postgres conftest (pre-existing; not E-002) |
