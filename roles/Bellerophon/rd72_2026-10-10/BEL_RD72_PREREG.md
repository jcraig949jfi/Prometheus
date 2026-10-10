# BEL-RD-72 PREREGISTRATION -- Bellerophon, campaign BEL-RD-72 (Reachability deserts, composition, accumulation)

Directive: roles/Bellerophon/prompts/2026-10-10_rd72/ (verbatim + MANIFEST). Clock 2026-10-10T09:50:44Z ->
2026-10-13T09:50Z. Host ubu005 (8 cores; prometheus-worker service inactive). Branch bellerophon/rd72-2026-10-10 from
main d0eba60f5. Prior evidence: BEL-48H (roles/Bellerophon/bel48h_2026-10-08/). Append-only; amendments dated;
timestamps from the shell clock only.

## 1. Standing rules (carried from the BEL-48H calibration ledger)

- Unit of independence = distinct initial population (distinct seed). Seeds are distinct per run unless a pairing is
  the stated design; pooled claims are reported per seed.
- Every analysis script is committed before its data AND exercised on synthetic rows that drive every predicate to both
  branches (BEL-48H W4-P5 rule).
- A mechanism read from a trace gets an automated falsifiable test before it is written into a report.
- Before freezing a mechanism test, check that the mechanism can operate in the window the endpoint measures (U3 rule).
- Completion markers are matched anchored; processes are selected by exact command line.
- Classes: CAUSALLY_CONFIRMED / REPRODUCED / PROVISIONAL / DETECTOR_ONLY / CONFOUNDED / FALSIFIED / INSTRUMENT_FAILURE.
- Origin (Q1) / Composition (Q2) / Accumulation (Q3) evidence is reported separately; a Q1 result is never cited as Q2/Q3.

## 2. D1 -- functional loss/gain ratio as a frozen prediction of the uptake effect (frozen 2026-10-10T09:53:56Z, before any run)

Plan tools/plan_d1.py: 1,900 runs, sha256 d632cb30180724f6dc0ef8d886c411e41e1906016d3b489940ec3d339cdfdf70. Substrates
NOT used in BEL-48H: S_LOCAL (PARTIAL, GRID LOCAL, budget 256) and S_PAIR320 (PAIR_EXECUTION, GRID WELL_MIXED, budget
320). Per substrate: 150 UF worlds (R = FUNC_LOSS / FUNC_GAIN over uptake events) and 400 seed-pairs normal vs uptake-
blocked (first-origin endpoint, as BEL-48H U). Analysis tools/analyze_d1.py (committed; branch-exercised on synthetic
rows -- which caught and fixed a NO_PREDICTION handling bug before this freeze).
Rule: R >= 1.25 predicts INCREASE (blocked > normal, one-sided sign test p < 0.05); R <= 0.8 predicts NO_INCREASE;
otherwise NO_PREDICTION.
- D1-P1: in every testable substrate the predicted and observed outcomes match.
