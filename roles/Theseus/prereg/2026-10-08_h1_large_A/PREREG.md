# THESEUS-24 preregistration -- H1 with a larger LLM arm (n no longer capped at 51)

Currency: 2026-10-08. Committed before the v1 LLM genomes are evaluated (they
are being written now by five fresh agents that see only SPEC.md and
TUPLES.json in theseus/controls/llm_arm_v1/; SPEC text identical to v0 except
the tuple counts). Code: theseus/synth/h1_rescore.py (blob id in CODE_SHA256.txt).

## Why

v0 and v0_1 H1 verdicts flipped (FAIL / INDETERMINATE) at equal n = 51, the cap
set by the 60-genome LLM arm. With A at ~310 genomes the cap moves to the next
smallest arm (R, 175 viable), so H1 is re-decided at ~3x the n.

## Design

- D, B, C, R: committed rows of v0_1 (no new ecology run). A = 60 v0 + 250 v1
  LLM genomes; the v1 genomes are evaluated under the FROZEN v0_1 calibration.
- The H1 rule is theseus.synth.analysis.hard_test unchanged (grids, metrics,
  permutation null, bootstrap, PASS/FAIL/INDETERMINATE clauses).
- Secondary 1: H1 without A (D vs B, C, R), same rule.
- Secondary 2: hard_test re-drawn with only the v0 A genomes (a check that
  the larger-A result is not a sampling artefact of the new subsample).
- Not a new campaign: v0_1's verdict stays recorded as INDETERMINATE; this is
  H1 at larger n on the same D, B, C, R rows.

## Predictions

N1 H1 at large n is FAIL.                                    p = 0.55
N2 H1 at large n is not PASS.                                p = 0.9
N3 H1 without A is not PASS.                                 p = 0.85
N4 v1 LLM genomes have a viable fraction >= 0.75.            p = 0.6

Compute: 250 evaluations x ~1 s / 4 CPUs ~ 2 min + hard tests; < 0.5 CPU-hour.
COI: the A arm is written by the same model family as the builder.
