# THESEUS-35 preregistration -- fresh-seed replication: task advantage and DISTRIBUTED carriers

Currency: 2026-10-08. Committed before the fresh-seed run exists.

## Why

31a/31b found deep descendants carry a cue through distractors better than one-shot and
complexity-matched random programs. 33 found, POST HOC, that capable deep descendants often
hold the cue DISTRIBUTED over >= 3 overlapping paths (no single rule and no pair of rules is
essential): D 14/40 vs R 2/40 vs one-shot 3/115. A post-hoc pattern needs a fresh sample.

## Design

Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_1s2_2026-10-08
--master-seed 20261009 --workers 4 (v0_1 configuration, fresh master seed; G0 and
calibration are seed-independent, the ecology/arms/known library are not).
Then: python -m theseus.synth.task_replicate --tag replicate_s2_2026-10-08
--ref v0_1s2_2026-10-08 --workers 4 (stages S1-S3, checkpointed; arms D, R, P, B, C only --
the lens lane is excluded as not needed for the hypothesis and slow).
Measures as 31b/33: J at V 8, k 8 (mean of task seeds 0, 1); capable = J >= .5; up to 40
capable per arm for knockouts; essential = J drop >= .2.

## Decision rule

GATE: noop mean J <= .175; max(relay, memcomp) mean J >= .30; redundant_relay degenerate
>= 80%; single_relay one-point >= 80%. Else INSTRUMENT FAILED.
PRIMARY H-DIST: share of the arm's capable knockout set that is DISTRIBUTED, D > R AND D >
pooled one-shot (P+B+C), one-sided Fisher p < .05 each -> REPLICATED; D <= both ->
NOT REPLICATED; else INDETERMINATE.
SECONDARY H-TASK-HARD (fresh seed): D J > pooled one-shot and > R, one-sided Mann-Whitney
p < .05 each -> REPLICATED, else not.

## Predictions

R1 gate passes.                                  p = 0.8
R2 H-DIST REPLICATED.                            p = 0.45
R3 H-TASK-HARD REPLICATED.                       p = 0.65

Compute: run ~55 min wall; S1-S3 ~5-6 CPU-hours, checkpointed (resumable across 2 h kills).
