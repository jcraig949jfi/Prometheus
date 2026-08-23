# CAMPAIGN W — TERMINAL: **KILL** (branch W3). The X-line closes on a measurement.

Frozen read exactly once (1,000 pairs, 800 four-real-operator). **The reserve split was never
opened** and remains clean. Branches applied exactly as preregistered with the original MDE of
0.0306, despite pass 2 having shown that bar to be ~3x the achievable resolution — moving it would
have voided the campaign.

## G-pos holds

`mean |V|` computed on frozen = 2.5900 → adjusted chance 0.000976, threshold 0.002929. Per-draw
granularity at n = 800 is 0.001250, below the threshold, so single draws are informative here.

    fixed     permuted mean 0.001563   (min 0.000000, max 0.005000)
    windowed  permuted mean 0.001125   (min 0.000000, max 0.003750)   -> HOLDS in both variants

Sanity: recorded target absent from its own answer set, **0 of 1,000**.

## The measurement

    arm         variant     hits          rate      Wilson 95% CI
    combined    fixed       68/800      0.0850     [0.0676, 0.1064]
    combined    windowed    73/800      0.0912     [0.0732, 0.1132]
      W = +0.0063   paired 95% CI [-0.0011, 0.0136]   b=7, c=2, discordance 0.0112
      shift control: fixed 32/200, windowed 32/200

    v2_only     fixed       66/800      0.0825
    v2_only     windowed    66/800      0.0825
      W = +0.0000   paired 95% CI [-0.0069, 0.0069]   b=4, c=4 — exactly balanced

**Development's effect did not replicate.** Dev W was +0.0175 with CI [0.0029, 0.0321], which
excluded zero; frozen is +0.0063 with CI [-0.0011, 0.0136], which contains it. The V2-only arm
moves by exactly nothing.

## The verdict is robust to my own threshold error

    CI upper bound 0.0136  vs  preregistered threshold 0.0306   ->  W3 KILL
    CI upper bound 0.0136  vs  counterfactual 2x measured MDE 0.0150  ->  W3 KILL

Pass 2 found the preregistered bar sat at roughly three times the achievable resolution and warned
that a real effect could fire the wrong branch. **It did not happen.** The counterfactual — what the
verdict would have been had the threshold been preregistered as a multiple of the measured MDE — is
reported for the record and gives the *same* branch. The miscalibration was real and, here,
immaterial.

## Seventh firing of the wrong-population lesson

Development within-arm discordance was 0.0225; frozen came in at **0.0112**, roughly halved. The
frozen MDE from the observed value is 0.0075. Once again a variance measured on one split did not
transfer — the seventh instance, and this time it made the frozen test *sharper* than expected.

## What W3 KILL kills, and what it does not

Pass 1 established that the window is **oracle information** a real query cannot have, which makes
this branch decisive:

- **The overlap artifact does not explain the X-line's negative results.** Even with oracle knowledge
  of the guaranteed window, correcting it buys at most 0.0136 top-10 recall, with a point estimate of
  +0.0063 and zero inside the interval. Five campaigns of negatives are **robust** to it.
- **The named deployable variant is ruled out by domination.** Per-candidate length matching over
  `min(len(A), len(B))` is strictly weaker than the oracle window. The oracle bought nothing, so the
  deployable variant cannot buy anything either. It does not need to be built and tested.
- **It does not kill** the possibility that some other representation beats raw terms. It kills the
  last live *explanation* for why the ones tried did not.

## The X-line, closed

    campaigns                    6   X, X-2, X-3, X-4, X-5, W
    terminal states                  REDESIGN, PARK, REDESIGN, PARK, PARK, KILL
    frozen splits burned         6   3,275 held-out pairs
    reserve remaining            1   1,000 pairs / 800 four-real-operator, never opened
    frozen-validated positives   1   relations ARE recoverable from term vectors (156x chance)
    frozen-validated nulls       3   hand-designed signature; learned linear metric; window correction
    doctrine rules produced      5   gate design · branches partition · verdict rules are instruments ·
                                     thresholds fail both ways · oracle scoping

**Campaign W cost 3 passes and 1,000 frozen pairs, and produced the one thing the line still
needed:** the last live explanation for its negatives, tested and killed. The line now has a coherent
ending rather than an unresolved doubt — structural relations are recoverable from plain term
vectors at ~156x chance, and across a hand-designed 125-feature signature, a learned linear metric,
and an oracle-windowed correction, **nothing beat a 20-term log-magnitude vector.**

**Recommendation: close the X-line.** Not park — close. Every named successor is either falsified
(window correction) or dominated by something falsified (length matching). Reopening would require a
genuinely new idea, not a variation, and none is currently on the table.

The reserve split (1,000 pairs, 800 four-real-operator, disjoint from all six campaigns) stays clean
and is handed to whatever asks the next question of this benchmark.

## Campaign W TERMINAL: KILL
