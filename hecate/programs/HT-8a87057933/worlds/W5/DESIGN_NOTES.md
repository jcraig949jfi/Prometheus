# HT-8a87057933 / W5 -- design notes (Pass 3 v2)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md. Layer: speculation
plus control rows only; there is no treatment code and no treatment statistic.

## What the world tests

M1 (core-guided forgetting), read through L1 (whether deletions concentrate on
the clauses in conflict). A factored plant (8 channels, each an unknown offset
in Z_8) switches ONE channel at a time. Observation clauses are point
constraints on one channel and sit in a FIFO window of 32. When a new clause
contradicts the window, the treatment extracts an MUS and deletes the oldest
clause inside it, repeating until SAT. The claim is that this keeps
observations that are still valid, which age-based forgetting cannot, and so
halves tracking errors (S1, S2) and at least halves valid deletions per repair
(S3) relative to drop-oldest.

## Why it avoids the earlier failures

- The earlier M1 world failed because after a whole-plant switch every stale
  clause was also the oldest, so core-guided == drop-oldest and even the oracle
  reset could not beat drop-oldest (median 3 vs 3 steps). Here a switch changes
  one channel, so stale clauses sit among younger and older valid clauses of the
  other seven channels. On the control rows the oracle repair makes 619 errors
  over 10 seeds vs 3876 for drop-oldest (ratio 0.160); the gap the treatment
  must close is real and wide.
- The earlier probe's positive control could not reach the threshold; here every
  success clause was checked on the control rows before freezing
  (ATTAINABILITY.json).
- No clause compares an arm with the null twin, so the twin's check is not
  self-referential (the earlier "ratio to itself is identically 1.0" defect).
  Every clause references CONTROL_REF (drop-oldest), which is rerun in the same
  code path as the treatment.
- Success and failure regions are disjoint: success needs S1 <= 0.50, failure
  F1 needs >= 0.90; a treatment meeting S1 makes <= 1938 errors, below the null
  twin's 2779, so F2 (ratio to twin >= 1.0) cannot also hold; S3 <= 0.50 vs F3
  >= 0.90.

## Control values (10 seeds per arm, 0.33 CPU core-seconds)

| clause | positive control | null twin | bar |
|---|---|---|---|
| S1 errors ratio to drop-oldest | 0.160 | 0.717 | <= 0.50 |
| S2 seeds with errors <= 0.5 x drop-oldest | 1.0 | 0.0 | >= 0.80 |
| S3 valid-deleted/UNSAT ratio | 0.0 | 0.781 | <= 0.50 |

Cheat (twin run with errors and valid deletions overwritten to 0) meets every
clause, so the evaluator can see success, and is flagged by the error floor
(< 0.5 errors per switch is impossible: the first request of a switched channel
errs with probability >= 7/8 for any policy not told of the switch). Neither the
positive control nor the twin trips the floor.

## Is the bar reachable by a legitimate (non-oracle) policy?

The positive control uses the truth. A legitimate rule that deletes only the
conflicting channel's clauses would lose, per sensor-corruption event (3% of
2400 steps, about 72 per run), the valid clauses of that channel plus one extra
error; that is roughly 1 extra error per corruption on top of the oracle's 62
per run, about 0.3 of drop-oldest, under the 0.50 bar. So the bar is not an
oracle-only bar. This is an argument, not a measurement; no such rule was run.

## Ambiguities resolved

1. "Oldest clause in the MUS": the MUS is extracted by deletion scanning the
   window oldest-first; the treatment deletes the clause with the smallest
   timestamp in that MUS. Stated in spec.mechanism so the implementer has no
   choice to make.
2. Null twin deletion count: the prompt forbids treatment code in controls, so
   the twin cannot be matched to the treatment's deletion count (that would need
   the MUS routine). It is matched in trigger and stop rule instead (random
   single deletions until SAT). Its deletion total (14639) is reported next to
   drop-oldest (16746) and the oracle (1633).
3. Controller with no clause on a channel: uses theta_hat = 0 (smallest allowed
   value), identically in every arm.
4. Sensor noise (3%) is deliberate: it creates the one case where the conflict
   has an ambiguous culprit (old valid clause vs new corrupted clause) and the
   "oldest in core" rule blames the wrong one. Without it the treatment would be
   the oracle by construction; with it the world can fail.
5. Switch value: uniform among the 7 values different from the current one, so
   every switch is a real change. 29 switches per run (t = 80, 160, ..., 2320).

## Revisions before freezing

See revisions.json (copied into ATTAINABILITY.json). Rev 1 had the twin passing
S2 ("beats drop-oldest in >= 80% of seeds") because random deletion beats
drop-oldest here; S1 had a 0.017 margin over the twin. Rev 2 set every clause
to a "halves" bar and added the error floor for the cheat check.

## Stupid explanations the implementer must report on

Listed in spec.json. The strongest: the MUS in a factored world IS the
conflicting channel, so a reset-the-mismatching-channel rule may do as well
without SAT. This world cannot separate those; a SIGNAL here would show
conflict-localised forgetting beats age-based forgetting, not that SAT adds
anything beyond the factorisation. Category theory contributes nothing here.
