# C0s -- post-freeze stress on the frozen law -- PREREGISTRATION

Written 2026-09-23 ~13:03Z. Law f852d782cb (cmap v3), frozen; already HOLDOUT_TESTED on D and E.
Nothing here can change the law. A failure is recorded as a FAILED event on the law (a scar that
stays beside its holdout successes).

## S1 -- stress adversary
4 rounds, rng seeds 20260930 + round, 60 attacks per family per round (band / coordpres /
extreme / errorseek, in the law's v3 coordinates), on fresh pools (1200 per family, seed
20260926; for regs, every second pool world uses the repetition-code mechanism code = 3).
Kill rule unchanged: confirmed (two 4x-episode replicates, > 2 SE from 0.10) / confident > 0.05.
Precommitment: all 4 rounds SURVIVE (conf 0.5). If one fails, I expect the counterexamples at
the high-cost edge (the D/E error shape) (conf 0.5).

## S2 -- the INFERRED cost-ceiling bias (from D/E error shapes)
Law ceiling at N = 0 and Q = 1: C <= G + 1 - 1.055 = G - 0.055.
Task-economics ceiling: G exp(-N) - C >= 0.10 -> C <= G - 0.10.
Scan: regs (q = 0, K = 7, R = 1), ring (lam = 0, K = 5, n = 64), ca (p = 0, K = 8, r = 1,
Lc = 510) for V in {2, 4, 16} (G .5 .75 .9375), cost knob on a geometric ladder, 1600 episodes,
6 replicates; location x0 fitted by boundary._fit; convert to C*.
Prediction: observed C* within 0.02 of G - 0.10 and NOT within 0.02 of G - 0.055 in >= 7 / 9
cells (conf 0.7). If it holds, the frozen law has a known systematic bias of ~0.045 in C at its
cost ceiling; the law is NOT revised (a revision would need a new sealed universe to test).

## S2 RESULT (2026-09-23T13:02Z, S2_ceiling.json) and amendment S2b (written before S2b runs)
S2 as scored: 6/9 cells near G - 0.10 and not near G - 0.055; prediction (>= 7/9) LOST.
Resolution defect (own design): the 15-point geometric ladder spans a factor 6.5 in cost, i.e.
~14% steps; every fitted location sits on a ladder point, so near C ~ 0.85 the resolution is
~0.11 in C -- coarser than the +/- 0.02 criterion. The rule's attainable resolution was not
computed before freezing it (base-role doctrine violated). S2 stays LOST as scored.
S2b: same cells, cost ladder LINEAR in C over [G - 0.20, G + 0.05], 41 points (step 0.00625),
1600 episodes, 6 replicates; C* = fitted location. Same prediction and threshold (>= 7/9 cells
within 0.02 of G - 0.10 and not within 0.02 of G - 0.055). Resolution 0.00625 < 0.02.
