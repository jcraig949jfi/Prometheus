# WTP-LM01 v0.3.2 DRAFT rev b (b1e1aae59): confirmation check of R1-R4

Reviewer: the same independent reviewer, 2026-09-28. This is a focused check, not a new review.
Constraints kept: read-only; one dev world (seed 9_700_040); no campaign seed derived; launch.py not run.
Analysis known-answer tests: 20/20 passed (test_lm01_analysis.py, -p no:cacheprovider).

VERDICT: NOT YET CONFIRMED. R1-R4 are applied correctly in the code. One text blocker remains (B1 below). It is a
one-sentence prose fix. Once it is corrected, this counts as CONFIRMED and needs no further review round.

## R1-R4 status

- R1: APPLIED.
  - analysis.py headline(): pays now requires _win(diffs[g]) AND above_floor[g] for every g in WIN_RUNGS.
  - The fixture was rerun at a declared SD 0.3, 8 worlds per level. The positive control is now NON-degenerate: every
    WIN rung is above N1 (90% CI lower bound of rung - N1):
    - L2: c/8 .08, c/4 .22, c/2 .42, c .94
    - L3: c/8 .13, c/4 .36, c/2 .75, c 1.06
  - It still fires LOSSLESS_TRANSIENT_CONTRACTION at L2 and L3 (L-R - c lower bound .73 / .52). L1 is still
    TOO_FEW_WORLDS, which is disclosed.
  - I cannot verify from the repo that "SD 0.3 declared before running" happened in that order. The SD 1.0 run is
    disclosed, which is the important part.
- R2: APPLIED.
  - LTC is rescoped in s1, 6.1, 6.7 and s11, and the sufficient-statistic identity is stated.
  - SuffStatR is report-only: it is excluded from eviction candidate detection, and only suffstat_minus_LR is
    reported.
  - Probe (F2-L2-cp, dev seed 9_700_040): L-R AC 2.524, SUFFSTAT AC 2.519, max |dpred| .009.
- R3: APPLIED. The dev projection is disclosed in 6.1 and in diff row 19. v031_set_label is emitted as a descriptive
  column.
- R4: APPLIED.
  - freeze.py FILES now includes fixtures_v032.json, FIXTURE_RERUN_v032.json and the diff.
  - analyse() raises FileNotFoundError when the fixtures file is missing.
  - The status word is DRAFT.
  - FREEZE.json still records v0.3.1. This is expected: it must be regenerated in the freeze commit.
- Recommended items: APPLIED and correct in code.
  - RECENCY_LOSES is not a falsifier (only HEURISTIC_EQUIVALENT_TO_RANDOM and RANDOM_BEATS_HEURISTIC fire F-C).
  - Live-only multiplicity, GENERATOR_DEPENDENT and CROSSOVER.
  - The wider 6.2 note.
  - The L-K strata are declared.
  - The clamp is flagged at both ends.

## Remaining blocker

B1. The prose contradicts the frozen fixture file.
- Prereg s11 (PREREG_WTP_LM01.md:251-253) says: "The 2c comparison ... cannot carry a verdict: no dev stratum, and not
  even the planted control, had CI.lo(L-R - 2c) > .30."
- In the rerun SD 0.3 control (dev/fixtures_v032.json), L2 has L-R - 2c = .491 [.344, .638]. Its lower bound is above
  .30. So v0.3.1's rule, 2c included, WOULD fire at L2. It would not at L3 (.157 [.113, .201]).
- The sentence was true only of the degenerate SD 1.0 run. Diff row #16 still justifies itself with the SD 1.0 numbers
  (L2 2c lo .25, L3 .13).
- Fix:
  - reword s11: "under the declared SD 0.3 control, the v0.3.1 rule (incl. 2c) fires at L2 but not at L3; no
    campaign-scale dev stratum had CI.lo(L-R - 2c) > .30";
  - update row #16's evidence to the SD 0.3 numbers, and state that #16 now rests on the design argument (2c holds
    37-73% of the history) plus the L3 control.
- This does not change any rule.

## Non-blocking notes (fix if convenient; they affect no label)

- N-a. SUFFSTAT rows carry misleading meters.
  - It inherits LosslessR, so peak_persistent is the full store (140,800 B in the probe), not the table (loci
    hypothesis_bytes 36,564 B).
  - Its _fit charges store_read with the table's bytes, which trips the R1d cheat counter: full_read_violations = 1.
  - A reader or an automated fixture scan could take the SUFFSTAT row for a flagged cheat. Annotate the row, or override
    must_read_bytes / persistent for this report-only readout.
- N-b. FIXTURE_RERUN_v032.json kept its old timestamp "t": 2026-09-28T09:10:06Z, although its contents (pytest count,
  headline_pc_noise) changed in the rerun. The file is now a frozen artefact, so its receipt time should be real.
