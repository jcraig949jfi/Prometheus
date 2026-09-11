# H3 dead-stream control: predictions, written BEFORE the run (ARCH-26)

Archaeon, 2026-09-11, on Apollo's delegation (comms #20) and Nyx's decoy
proposal (comms #45). This file is committed in its own commit before
`python -m archaeon.producer.h3_dead_stream --run` is executed for the
first time; the results land in a later commit as
archaeon/docs/h0h5/H3_DEAD_STREAM_CONTROL_2026-09-11.json.

## The instrument

Module archaeon/producer/h3_dead_stream.py. Three streams of one shape
(200 candidates, 128-bit rule tables, v1 descriptors and edges, one in
seventeen failed, byte cap never binding), replayed through the four
policies of archaeon/producer/h3_replay.py under caps 16 items, reserve 4,
five seeds (1..5):

- live: score = agreement with a hidden target on 12 hidden tasks of 3
  bits each (solve count / 12) plus Gaussian noise sd 0.05.
- dead: the live stream with its score column permuted (seeded). Score
  marginal identical, descriptor marginal identical, ONLY the relation
  organism -> score removed.
- cheat: score = solve count / 12 exactly; the score IS the reuse target.

Sealed future queries: family A (the v1 shape: five score_at_least
thresholds 0.3..0.7 and six occupies_cell queries) and family B (the 12
tasks, sealed in archaeon/docs/h0h5/H3_DEAD_STREAM_TASKS_v1.json in this
same commit, before any archive is examined).

## Attainable range and eligibility (feedback: a gate must be shown reachable)

- coverage: 0..16 cells; behavioral and hybrid can occupy at most 16 and
  12 behavioral cells respectively; top_k and uniform have no grid and
  their coverage is whatever their 16 items happen to span.
- family A solve: 0..11 of 11 per policy; the five threshold queries are
  answered by the best retained score, the six cell queries by occupancy.
- family B solve: 0..12 of 12 per policy; the ceiling attainable by ANY
  policy is the stream ceiling (tasks solved by some evaluated candidate
  in the stream), reported per seed as stream_ceiling_family_b. With 188
  evaluated random tables and a 1/8 chance per task per table, every
  task is solved by ~23 tables, so the ceiling is expected to be 12/12
  on every seed; the gate is reachable.

## Predictions (falsifiable, per policy, mean over five seeds)

P1 COVERAGE DOES NOT SEPARATE DEAD FROM LIVE. For behavioral and hybrid,
|coverage(dead) - coverage(live)| <= 1/16. The descriptors are identical
by construction and the grid fills from the same tables; the score only
decides WHICH item holds a cell, not whether the cell is held. This is
Apollo's S1 finding (12/64 on DEAD_random equals 12/64 on the live
world) reproduced on the H3 stream contract: occupancy is an unsafe
observable.

P2 FAMILY A (score thresholds + cells) DOES NOT SEPARATE DEAD FROM LIVE
FOR top_k: family_a_solved(dead) == family_a_solved(live) exactly on
every seed, because the retained score multiset is the top 16 of the
same multiset. For behavioral and hybrid: family_a_solved(dead) >=
family_a_solved(live) on average (noise scatters the high scores across
cells so more of them survive one-per-cell retention; under live the
high scorers cluster where the target's bits sit and collide in cells).
If P2 holds, a score-threshold reuse read-out is measuring the score
marginal, not reuse.

P3 FAMILY B (tasks) SEPARATES DEAD FROM LIVE FOR EVERY SCORE-RETAINING
POLICY. family_b_solved(live) - family_b_solved(dead) >= 2 (of 12) for
top_k and >= 1 for behavioral and hybrid; on the dead stream top_k's
family_b_solved is within 2 of uniform's (retention by an uninformative
score is a random sample). If P3 fails for top_k the direct-reuse
channel cannot see the organism-task relation at all and the control has
killed the instrument, not the policies.

P4 CHEAT SEES SUCCESS. family_b_solved(cheat) >= family_b_solved(live)
for top_k, behavioral and hybrid, and family_b_solved(cheat, top_k) >=
10 of 12. If the cheat arm does not reach at least the live arm, the
reuse channel is blind and nothing else in this file is interpretable.

P5 UNIFORM IS THE FLOOR AND IS FLAT. uniform's family B solve is within
2 across live / dead / cheat (it never reads the score).

## What each outcome means

- P1..P5 all hold: coverage and score-threshold reuse are certified
  UNSAFE as evidence of stream content on this contract; task-level
  direct reuse is certified as the channel that sees it; every H3
  coverage number from now on is reported beside its dead-stream twin
  (Nyx's decoy D4 is the same instrument from the binning side).
- P3 fails, P4 holds: the live relation is too weak at noise 0.05 for
  16 slots; rerun with noise 0.02 and 0.0 before any verdict (an
  INDETERMINATE branch, not a kill).
- P4 fails: instrument defect in solves()/score_archives; nothing else is
  read.
- P1 fails (coverage separates): the permutation moved occupancy through
  the tie rule; inspect event_counts before believing it.

## Costs

Producer-side only; no engine, no Vivarium, no queue row. The engine is
UNREACHABLE at the time of writing (14:40-15:30 UTC), which is why this
item is being executed now.
