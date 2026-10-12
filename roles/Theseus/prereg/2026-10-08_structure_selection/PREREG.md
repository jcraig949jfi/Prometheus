# THESEUS-27 preregistration -- does selecting for graded structure make depth productive?

Currency: 2026-10-08. Committed before any run of this configuration.
Code: run_v0.py flags --quality, --elite-grids, --pop-cap, --dark-protect-gens
(defaults reproduce v0_1 exactly); h1_rescore.py --d-ref / --a-v1-rows. Blob ids
in CODE_SHA256.txt.

## Why

Three results so far: (1) H1 FAIL at n = 175 (THESEUS-24, 8e8e612ce); (2) the only
discriminating structure ruler, R5, shows deep descendants LESS structured than
one-shot collisions (THESEUS-23a post-hoc); (3) the v0 ecology applies almost no
selection: the population cap never binds (QD elites on 3 grids + every untried
dark object are protected; active reached 581 > cap 400), and elite quality is
reproducibility, not structure. Before concluding "recursion cannot build", test
the ecology WITH selection.

## Design (two ecology-only runs, identical except the elite quality)

Common: PYTHONHASHSEED=0, master seed as v0_1, law ON, 30 generations,
--pop-cap 300 --elite-grids pca --dark-protect-gens 3 (so the cap binds).
  SEL-REP: --quality rep   (elites = most reproducible per pca cell)
  SEL-R5:  --quality r5    (elites = highest R5 per pca cell)
Tags: v0_1_selrep_2026-10-08, v0_1_selr5_2026-10-08.

Outcomes:
  PRIMARY (independent of R5): H1 by the unchanged rule (analysis.hard_test),
  arm D = the run's DEEP+VERY_DEEP children, arms A (v0+v1 LLM, rows reused from
  h1_large_A_2026-10-08), B, C, R = committed v0_1 rows; equal n.
  SECONDARY: composition rate (THESEUS-23b detector) on up to 120 viable D
  children per run -- run only if 23b's verdict is not INDETERMINATE-by-blindness.
  MANIPULATION CHECK (not evidence): median R5 of viable D children, SEL-R5 vs
  SEL-REP; and that the cap binds (max active <= 300 + one generation's births).

## Decision rule

- If the cap does not bind in either run: the experiment is VOID (no selection
  was applied); fix and rerun.
- If the manipulation check fails (median R5 of D not higher under SEL-R5): the
  selection did not take; report as such, primary outcome descriptive only.
- STRUCTURE-SELECTION-HELPS: H1 PASS for SEL-R5 and not PASS for SEL-REP.
- NO-HELP: H1 not PASS for SEL-R5.
- BOTH-PASS: binding selection itself (any quality) suffices -- reported as such.

## Predictions

S1 the cap binds in both runs.                                     p = 0.85
S2 manipulation check passes (median R5 of D higher under SEL-R5). p = 0.7
S3 H1 is not PASS for SEL-R5.                                      p = 0.75
S4 H1 is not PASS for SEL-REP.                                     p = 0.85

Compute: 2 ecology-only runs ~20-25 min wall each + rescoring; ~3 CPU-hours.

## Note on THESEUS-28 (prereg df2cf1acd)

THESEUS-28 runs at the commit of this preregistration. run_v0.py changed after
the 28 prereg only by adding the flags above, all defaulting to v0_1 behaviour;
28 uses the defaults. The 28 blob ids are superseded by this file's.
