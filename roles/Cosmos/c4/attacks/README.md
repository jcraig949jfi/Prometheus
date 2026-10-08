# C4 reviewer-attack reproductions (Cosmos, ubu003, 2026-10-08)

| file | what | how |
|---|---|---|
| rmech_rerun_ubu003_h0.jsonl | R-MECH sweep1 re-run (F1-F4) | `PYTHONHASHSEED=0 PYTHONPATH=. python <attack_harness.py from 164df3cdd> out 0 2` and part 1 |
| rmech_rerun_ubu003_h0_analysis.json | analyse_sweep1.py (164df3cdd) on the re-run | A classes identical to the review; B agrees 47/48; REL@q BA .923 (review .910); T3 FUNCTIONAL 60/60 |
| f2_matrix_v1.json | first F2 shared-failure matrix (A vs B-linear vs B-rf) | XorCue at V = 4 there is NOT linear-blind (multi-class argmax, .378); superseded by the V = 2 tests |

The R-MECH harness files are NOT copied here (they stay on Bellerophon's branch until the finals). Reproduction
defect in the harness: SYSID and B seeds come from `tuple.__hash__()`, salted per process, so runs are not
bit-reproducible unless PYTHONHASHSEED is fixed.
A1 reproduction: Ananke's snippet with power_s0.py unchanged -> 1.00 (200/200), as reported.
