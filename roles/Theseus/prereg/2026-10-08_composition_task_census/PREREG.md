# THESEUS-36b preregistration -- composition-necessary task on UNSELECTED arms

Currency: 2026-10-08. Committed before the census runs (no J on this task has been computed
for any arm genome; only the hand-built controls in comp_task_2026-10-08/CONTROLS.json).

## Why

36 asks whether task selection makes recursion build a store+release composition. 36b gives
the no-selection baseline across ALL arms of the aligned split-reader substrate (run
v0_2a_2026-10-08, full run with one-shot and random arms): how often does each arm already
solve a task that, by construction, only a composition of parts worthless alone can solve?

## Design

python -m theseus.synth.task_comp_census --tag comp_task_census_v0_2a_2026-10-08
--ref v0_2a_2026-10-08 --workers 2. 100 viable genomes per arm (D, R, P, B, C); J = V 4, k 8,
sensor-only readout, 400/400 episodes; SOLVER = J >= .6.

## Decision rule

H-UNSEL: D solver share > pooled one-shot share AND > R share, one-sided Fisher p < .05 each
-> SUPPORTED (recursion alone, unselected, builds composition-necessary mechanisms more
often); D <= both -> NOT SUPPORTED; all arms 0 -> NONE-WITHOUT-SELECTION; else INDETERMINATE.

## Predictions

W1 every arm has <= 5% solvers.            p = 0.6
W2 H-UNSEL SUPPORTED.                      p = 0.2

Compute: 500 J evaluations x ~1.5 s / 2 workers, ~10 min.
