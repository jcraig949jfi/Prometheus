# Pre-registered prediction — iteration 27, before the run

## Context
Iteration 26 refuted the compressibility predictor: a family with oracle ceiling
0.870 (nearly as compressible as abelian F_T at 1.000) showed a P3d-P3c gap of
+0.023 against F_T's +0.284. The families that broke it differed in ACTION COUNT
(6 vs 4), which multiplies words of length <=3 from 84 to 258.

External review advised: test candidate-space burden, but NOT as "account #6" —
as a factor-separation experiment that manipulates burden WITHOUT touching the
arena's algebra. If the gap moves, that is causal evidence about the learner
machinery. If it does not, the hypothesis dies cleanly.

## The manipulation
`sig_tags`: a candidate pair is admitted to the proposal pool when its two words
agree on that many tags. All four (the original) is strong evidence; fewer is
weaker, so the pool floods with plausible-but-often-false candidates. This is
purely downstream of the arena. Universe, sensor, algebra, budget and the verifier
are all identical across conditions. Both arms receive the same pool.

Run in F_T with 4 actions, 20 seeds, standard budget, sig_tags in {4, 3, 2}.

## Prediction
If candidate burden is causal, enlarging the pool should make P3d's ranking
problem harder and/or waste P3c's budget on false candidates, and the GAP SHOULD
MOVE. The iteration-26 observation (bigger pool, gap collapses) implies:

  P1. The gap SHRINKS monotonically as sig_tags falls from 4 to 2.
  P2. The shrink from sig_tags=4 to sig_tags=2 exceeds 2 SE of the difference
      (SE per condition ~0.04, so ~0.11 or more).

## Falsifiers
  F1. The gap does not move by more than 2 SE across the full manipulation.
      Then candidate burden alone does not drive the effect and the hypothesis
      is dead — NOT to be replaced by a seventh account.
  F2. The gap moves in the OPPOSITE direction (grows as the pool floods). Then
      burden matters but the iteration-26 reading of it is wrong.

## Binary decision recorded in advance
If F1 fires, mechanism search in ceiling_v0 TERMINATES and mechanism is reported
as unresolved. If the prediction survives, exactly ONE confirmatory experiment is
permitted, then mechanism work stops regardless of outcome.

---

## VERDICT — prediction survives

```
sig_tags  pool size  P3c acc  P3d acc      gap     SE   P3c rules  P3d rules
       4         78    0.364    0.647   +0.284  0.042        46.5       24.1
       3         87    0.346    0.560   +0.214  0.050        40.8       23.5
       2        167    0.285    0.414   +0.129  0.039        26.3       17.6
```
P1 monotone shrink                         HOLDS
change 4 -> 2: -0.155 vs 2*SE_diff 0.114   exceeds threshold (~2.7 SE)
F1 gap does not move                       does not fire
F2 opposite direction                      does not fire

Doubling the candidate pool (78 -> 167) roughly HALVES the advantage
(+0.284 -> +0.129), with the universe, sensor, algebra, budget and verifier all
identical across conditions. Only the proposer's admission criterion changed.

Per the binary decision recorded in advance: exactly ONE confirmatory experiment
is now permitted, then mechanism work stops regardless of its outcome.
