# Preregistration ADDENDUM: CRUCIBLE-B control repair (frozen 2026-09-14, before any held result)

Amends `PREREG_C_B.md` section B (frozen at d3b9533). Reason: the preregistered random-macro control is infeasible in
this world (see `results/ac01d/nursery/CRUCIBLE_B_INSTRUMENT_FAILURE_run1.md`, commit 9b0a963). No held result from run
1 was written or observed; the only numbers seen after the freeze are (a) the FIT-only mining output and (b) a timing
diagnostic on VAL problems (the steering set), which reports wall time and solve rate only.

## Why the original control cannot run

The frozen mining rule returns six length-2 macros: (1,0) (0,2) (0,1) (0,0) (2,1) (2,0) in generator indices
cycle=0, swap01=1, collapse01=2. With three generators there are exactly nine length-2 sequences; three are not mined.
"Six random sequences of the same lengths, excluding the mined set" needs six and can find only three.

## Replacement control (the only change)

The control becomes the EXACT distribution over every equally privileged alternative: all C(9,6) = 84 six-element sets
of length-2 generator sequences, in `itertools.combinations` order. The mined set is one of the 84. Every set is
evaluated with the unchanged `MacroWorld` (same cost accounting, same ordering rule, same budget, same pruning).

This is strictly stronger than three random draws: no sampling, no seed, no possibility of choosing a favourable draw.

Honest caveat, fixed now: no six-element set is disjoint from the mined set (only three non-mined sequences exist),
so every alternative shares at least three macros with the mined set. The contrast is "the six most frequent
sequences vs a typical six", not "mined vs unrelated". This weakens the control's power to separate mined macros from
arbitrary ones, and a KILL under it is therefore the more informative outcome.

## Unchanged

World, D, targets, reachability, FIT-only mining procedure and seed, harness (`ac01d/evaluate.py` Context, 300
problems per set, budget 40,000), kernel-aware pruning, macro ordering after generators at equal key, transition
accounting (macro charged its length), path length in generator steps, engine verification, bootstrap CI.

## Verdict rule (restated for the exact control; same form and thresholds)

On HELD_TARGETS and HELD_BOTH, separately for DFS and GBFS:

- KILL if the mined set's HC_D does not exceed the mean HC_D of the other 83 sets by more than the mined set's
  bootstrap CI half-width, or if the mined set's HC_D <= 0, or if the mined set has any failure.
- PASS if it exceeds that mean by more than the CI half-width AND reaches HC_D >= 0.20 on both sets.
- WEAK if it exceeds the mean but HC_D < 0.20.

Reported beside the verdict, never changing it: the mined set's rank among all 84; the number of alternative sets
with failures (excluded from the mean); HELD_STATES results; the no-macros reference.

## Runner

`alien_circuitry/nursery/crucibles/crucible_b2.py`, run as
`python -m alien_circuitry.nursery.crucibles.crucible_b2 --sets HELD_STATES,HELD_TARGETS,HELD_BOTH --kinds DFS,GBFS`.
Checkpoints per macro set under `results/ac01d/nursery/crucible_b2_checkpoints/`. Expected cost from the VAL timing
diagnostic: about 1 ms per problem per cell, i.e. a few minutes in total.
