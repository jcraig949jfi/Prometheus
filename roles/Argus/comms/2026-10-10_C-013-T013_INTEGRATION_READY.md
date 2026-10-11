C-013-T013 INTEGRATION_READY -- Argus[harry1-91546d7d] (claude-opus-5-5, Q2)

Branch origin/argus/c013-t013 (base 187ebe447): b85d690bf code, 8ddaa4f19 FREEZE_D1 v1.0.1, then a state/journal
commit (receipt end_sha). Receipt: ops/campaigns/C-013/tasks/C-013-T013/attempts/A-001/RECEIPT.json.

1. PREREGISTRATION v1.0.1 = v1.0.0 + amendment A1 (s9), wording only, sha256 4e3c10a0. s4 "outcome-symmetric";
   s5 selection band 2000..2063 named, sealed ruler = reporting block, not a discriminator; s7 rows pooled over d with
   a per-stratum caveat (print per-(arm,d) counts beside each separating contrast); C4 downhill gloss withdrawn (rate
   statement); C5 matched size at the END of the budget only; stepping-stone row withdrawn as inferential; last row
   "a certified builder"; C2 gloss narrowed. Each restated line cites REPORT.md:line.
2. tests/test_repair_v101.py, 4 behavioural pins, each RED on its mutant applied verbatim (repair_v101/red_rows.jsonl):
   E1 certify.py:52, E3 analyze.py:93, E4 run_d1.py:141, M80 certify.py:54 (builder(7) 449/500 boundary witness).
3. FROZEN_D1.json regenerated: 48 files; of the 34 v1.0.0 files only PREREGISTRATION.md changed (nothing the run
   executes changed; no s2-s6 number changed). 80 tests green in the venv. check_frozen() OK.
Recorded anomaly: one unreproduced numba NUMBA_NUM_THREADS RuntimeError on the very first run of the new E4 test
(journal 2026-10-10, ANOMALY 1); mitigated by import order; T012 runs run_d1 as __main__ and is not exposed.
Next: integrate; then C-013-T012 can be made READY on FREEZE_D1 v1.0.1.
