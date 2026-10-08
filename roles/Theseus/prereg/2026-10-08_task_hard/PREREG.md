# THESEUS-31b preregistration -- harder task replication and knockout attribution

Currency: 2026-10-08. Committed before any run of theseus/synth/task_hard.py.

## Why

31a (b7932dcb9) is the campaign's first preregistered positive: deep descendants carry a cue
through 4 distractors better than one-shot (p 6e-10) and complexity-matched random (p .004).
It is ceiling-limited (medians 1.0) and says nothing about mechanism.

## Design

Part 1: J_hard = mean J over task seeds 0, 1 at V = 8, k = 8 (chance .125); identical arm
construction to 31a (seed 20261008, 100 per arm: D, E, B, C, P, R, A, G0) and 31a controls.
Part 2: genomes with J_hard >= .5, up to 40 per arm (seed 7): single-rule knockouts at task
seed 0; a rule is ESSENTIAL if J drops by >= .2; carrier size = number of essential rules.

## Decision rule

GATE: noop mean J_hard <= .175 AND max(relay mean, memcomp mean) >= .30. Else INSTRUMENT
FAILED (descriptive only).
H-TASK-HARD: D median J_hard > pooled one-shot (P+B+C) AND > R, one-sided Mann-Whitney
p < .05 each -> SUPPORTED (31a replicates at the harder setting); D <= both -> NOT
SUPPORTED; else INDETERMINATE.
Attribution (descriptive, reported per arm): carrier-size distribution; share of capable
genomes whose carrier has >= 2 essential rules; the essential ops.
H-CARRIER (secondary): D's share of multi-part carriers (>= 2) > R's share, one-sided Fisher
p < .05 -> SUPPORTED, else NOT SUPPORTED.

## Predictions

H1h gate passes.                                                   p = 0.8
H2h H-TASK-HARD is SUPPORTED.                                      p = 0.55
H3h most capable D genomes have carrier size 1 (one-part relays).  p = 0.55
H4h H-CARRIER is NOT SUPPORTED.                                    p = 0.7

Compute: ~860 genomes x 2 seeds x ~1.5 s + knockouts (~300 genomes x ~12 rules x 1.5 s);
~3 CPU-hours.
