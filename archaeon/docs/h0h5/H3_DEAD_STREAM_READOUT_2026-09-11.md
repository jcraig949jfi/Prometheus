# H3 dead-stream control: readout v1 and the pre-registered v2 addendum (ARCH-26)

Archaeon, 2026-09-11. Rows: archaeon/docs/h0h5/H3_DEAD_STREAM_CONTROL_2026-09-11.json
(five seeds, tasks manifest sha256:436f8aea..., predictions committed first at
571f171dd as H3_DEAD_STREAM_PREDICTION_2026-09-11.md).

## v1 result, prediction by prediction (mean of 5 seeds; paired live-dead with its SE)

    policy      coverage live/dead   famA live/dead   famB live/dead/cheat   famB live-dead (SE)
    top_k       0.5375 / 0.5500      6.2 / 6.2        12.0 / 10.2 / 12.0     +1.80 (0.37)
    uniform     0.5750 / 0.5750      4.0 / 4.2        10.2 / 10.2 / 10.2      0.00 (0.00)
    behavioral  0.9500 / 0.9500      8.0 / 8.0        11.8 / 10.2 / 11.8     +1.60 (0.60)
    hybrid      0.7625 / 0.7625      7.0 / 7.0        11.8 / 10.4 / 11.8     +1.40 (0.68)
    stream ceiling for family B: 12/12 on every seed and arm (gate reachable)
    no cap bound on any policy in any arm (count_bound 0, byte_bound 0)

- P1 HELD. Coverage is IDENTICAL between dead and live for behavioral and
  hybrid on every seed (delta 0.0), and within 1/16 for top_k. Occupancy
  does not see whether the stream carries a relation. Apollo's S1 finding
  reproduced on the H3 contract.
- P2 HELD in substance, MIS-STATED in form. The exact-equality clause for
  top_k was written for all eleven family-A queries; it is true of the five
  score-threshold queries (identical on every seed: 3/3/3/1/3 live and dead)
  and false of the six cell queries, which follow WHICH tables the top 16
  scores sit on (4/3/4/4/3 live vs 2/5/4/4/3 dead). The reading stands: a
  score-threshold reuse read-out measures the score marginal, not reuse.
  Behavioral and hybrid: family A identical between arms on every seed;
  the ">= on average" clause held with equality, and the "noise scatters
  high scores" mechanism did not show at this noise level.
- P3 HELD IN DIRECTION, INDETERMINATE AT THE LINE. Task-level direct reuse
  separates live from dead for every score-reading policy (top_k +1.80,
  behavioral +1.60, hybrid +1.40; each more than two SEs above zero). The
  pre-registered line ">= 2 for top_k" sits 0.2 from the observed value
  with SE 0.37: the line was inside measurement error and is not read
  (feedback: a gate must exceed its own SE). Cause, visible in the rows:
  top_k's live arm is at the CEILING (12/12 on every seed) and the uniform
  floor is 10.2/12, so the whole channel has 1.8 tasks of range. The
  sub-clause "top_k on dead within 2 of uniform on dead" held on the mean
  (10.2 vs 10.2) and failed on one seed (9 vs 12).
- P4 HELD. Cheat >= live for every score-reading policy; top_k cheat 12/12.
  Cheat EQUALS live everywhere, which is the ceiling again: at noise 0.05
  the live relation is already saturating a 12-task family a random table
  solves with probability 1/8.
- P5 HELD, structurally. Uniform is bit-identical across arms because it
  never reads the score and the streams share order and failure pattern;
  its SE of 0 is a construction fact, not a measurement.

## Verdict v1

Coverage and score-threshold reuse are UNSAFE as evidence of what a stream
carries: both are flat between a live stream and its score-permuted twin.
Task-level direct reuse is the channel that sees the relation, and it sees
it with a cheat control that reaches the ceiling. What v1 cannot say is HOW
MUCH it sees, because the family was too easy: the floor a random archive
reaches (10.2/12) leaves no room. That is an instrument-range defect,
pre-listed in the prediction file as the branch "rerun before any verdict",
and it is fixed by a harder task family, not by moving the line.

## v2 addendum, PRE-REGISTERED (this file is committed before v2 is run)

Change ONE thing: bits per task 3 -> 5 (a random table solves a task with
probability 1/32 instead of 1/8). Sealed manifest
archaeon/docs/h0h5/H3_DEAD_STREAM_TASKS_v2.json (sha256:343ae72b...), task
seed 20260912, same 200-table streams, caps, edges, reserve, seeds, noise.

Attainable range: for 16 random tables the expected family-B solve is
12 x (1 - (31/32)^16) = 4.8 of 12; the stream ceiling over 188 evaluated
tables is 12 x (1 - (31/32)^188) = 12.0 (reachable). Expected room between
the floor and the ceiling: ~7 tasks.

    P1'  coverage(dead) == coverage(live) for behavioral and hybrid (delta 0).
    P3'  family_b(live) - family_b(dead) >= 3.0 for top_k, with the paired
         SE below 1.0; >= 2.0 for behavioral and hybrid. Line-to-SE ratio
         must exceed 1 or the line is not read.
    P3b' top_k(dead) within 2.0 of uniform(dead) on the mean.
    P4'  family_b(cheat) >= family_b(live) for top_k, behavioral, hybrid;
         top_k(cheat) >= 9 of 12; and top_k(live) <= 11.5 on the mean (off
         the ceiling), or the family is still too easy and v3 uses 6 bits.
    P5'  uniform identical across arms (structural).

Outcomes: all hold -> the direct-reuse channel is certified with a range
and ARCH-26 closes with a reply to Apollo and Nyx; P3' fails while P4'
holds -> the relation at noise 0.05 is weaker than 3 tasks under 16 slots,
report the measured delta with its SE and do not move the line; P4' fails
-> instrument defect, nothing read.
