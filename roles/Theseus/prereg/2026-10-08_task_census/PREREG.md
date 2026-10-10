# THESEUS-31a preregistration -- task census: do Theseus programs carry a cue through distractors?

Currency: 2026-10-08. Committed before any task_J value of any genome was read (one timing
call, 0.7 s on one arm genome, value not printed).

## Why

Hestia #1897 (s2, s4.19) diagnoses Theseus as EXPRESS + REWARD: programs have zero input
channels, so no task can be posed and a mechanism can only be counted, never selected for.
theseus/synth/task_system.py gives a genome an input: channel 0 becomes a TRANSIENT sensor
overwritten each step with a one-hot pulse at site(x) = 5x mod 32 (an additive input was
rejected before any run because "do nothing" would then keep every pulse). The adapter is
bit-identical to substrate.run without input (test_task_system_matches_substrate_...).

## Design

Task: prometheus.cosmos.c3.task cue recall (public), V = 4, k = 4, 400 train / 400 test
episodes, seed 0; J = held-out accuracy of a ridge readout on the state at the query.
Groups: gate controls (20 each: noop, relay, memcomp -- see module docstring) and 100
viable genomes per arm from committed v0_1 rows: D, E, B, C, P, R, A, G0 (seed 20261008).

## Decision rule

GATE: noop mean J <= .30 AND relay mean J >= .45 AND memcomp mean J >= .35. Gate fails ->
INSTRUMENT FAILED (arms descriptive only).
Gate passes:
  H-TASK: median J of D > median J of pooled one-shot (P+B+C) AND > median J of R, each by
  one-sided Mann-Whitney p < .05 -> SUPPORTED; D <= both -> NOT SUPPORTED; else INDETERMINATE.
  Descriptive: share of each arm with J > .35; max J per arm.

## Predictions

Q1 gate passes.                                               p = 0.7
Q2 at least 20% of some arm's genomes have J > .35.           p = 0.6
Q3 H-TASK is not SUPPORTED.                                   p = 0.75

Compute: ~860 task evaluations x ~1 s / 4 CPUs, ~5-10 min.
