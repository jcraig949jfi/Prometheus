# THESEUS-33 preregistration -- is the depth advantage on the task DEGENERACY?

Currency: 2026-10-08. Committed before any run of theseus/synth/task_degen.py.

## Why

31b (225576cb3) replicated the task advantage off the ceiling and found, post hoc, that
capable deep descendants are mostly carrier-size-0: no single rule knockout breaks recall
(D 24/40, E 28/40 vs one-shot 23/115, R 16/40). Candidate: degeneracy (redundant carriers).

## Design

Population: the 31b knockout set's carrier-size-0 genomes (rebuilt by the identical 31a/31b
construction; ids from theseus/runs/task_hard_2026-10-08/ROWS.jsonl). All pairwise knockouts,
J at V 8, k 8, task seed 0. DEGENERATE = no single drop >= .2 and some pair drop >= .2;
DISTRIBUTED = no single and no pair drop >= .2.
Gate (20 each, seed 33): redundant_relay (two separate relays into ch1 and ch2) and
single_relay (one relay into ch1).

## Decision rule

GATE: redundant_relay degenerate >= 80% AND single_relay carrier size 1 in >= 80% with
degenerate <= 5%. Else INSTRUMENT FAILED.
H-DEGEN: per arm, share of the arm's CAPABLE knockout set (31b) that is degenerate OR
distributed ("no single point of failure"); D share > pooled one-shot (P+B+C) share AND > R
share, one-sided Fisher p < .05 each -> SUPPORTED; else NOT SUPPORTED / INDETERMINATE as in
earlier items. Reported separately: degenerate vs distributed counts per arm.
Note: the "no single point of failure" share is already measured in 31b (it is carrier size
0); H-DEGEN re-tests it under its own preregistration and adds the pair structure. The
pair structure is the new information.

## Predictions

Z1 gate passes.                                                        p = 0.75
Z2 H-DEGEN is SUPPORTED.                                               p = 0.6
Z3 most D carrier-size-0 genomes are DISTRIBUTED (no critical pair).   p = 0.5

Compute: ~110 genomes x ~70 pairs x ~1.3 s + 40 controls; ~3 CPU-hours; checkpointed.
