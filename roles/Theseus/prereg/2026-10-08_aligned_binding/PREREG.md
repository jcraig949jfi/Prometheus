# THESEUS-34 preregistration -- assembly with channel-identity-preserving binding

Currency: 2026-10-08. Committed before the run.

## Why

30e (a512ae012): with writers and readers available in different G0 lineages, in-context
compositions stayed rare (D 1/120, one-shot 1/360, R 3/120; INDETERMINATE). Failure shape:
only 4/30 viable ecology genomes holding both parts had them on the same memory channel,
because collisions remap channels by parent position ((c + j) mod C). 34 removes that remap.

## Design

Identical to 30e except --aligned-binding (collide(..., aligned=True): parent channels keep
their indices; every RNG draw unchanged; default behaviour verified unchanged, 125/125
entities identical to the THESEUS-25 reference). Run: PYTHONHASHSEED=0 python -m
theseus.synth.run_v0 --tag v0_2a_2026-10-08 --g0-readers --cond-ops --aligned-binding
--workers 4; scan composition_v3 --ref v0_2a_2026-10-08 (gate inside).

## Decision rule

MANIPULATION CHECK: among viable ecology genomes holding both parts, the share with writer
and reader on the same memory channel exceeds 30e's (4/30) by a one-sided Fisher p < .05;
else the manipulation failed and the composition result is descriptive only.
GATE as 30c. Then the 30e rule unchanged: H-ASSEMBLE SUPPORTED iff D share > one-shot share
AND > R share (one-sided Fisher p < .05 each); RANDOM-BEATS-RECURSION iff R > D (p < .05);
every arm 0 -> WALL-WITH-ALIGNED-PARTS; else INDETERMINATE. Note: R is unaffected by binding
(random programs), one-shot arms ARE affected (they collide too).

## Predictions

A1 manipulation check passes.                                    p = 0.7
A2 D composition share is higher than in 30e (point estimate).   p = 0.6
A3 H-ASSEMBLE is SUPPORTED.                                      p = 0.3

Compute: full run ~60 min + scan ~40 min; ~6 CPU-hours; scan is short enough for the limit.
