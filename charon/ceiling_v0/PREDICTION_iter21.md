# Pre-registered prediction — iteration 21, written BEFORE running any arm on F_M

## Claim under test
Iteration 20: "selectivity wins when a compact sufficient rule set EXISTS and can
be found." This is the fourth account of P3d's advantage and the first to subsume
its predecessors, so it needs an OUT-OF-SAMPLE test rather than another sweep over
the data that shaped it.

## Method
A new intermediate family F_M was built (exactly one action carries a permutation,
so the monoid is "mostly abelian"). Its STRUCTURE was measured first, with no arm
run on it. The account must then predict the P3d advantage before any arm touches
F_M.

## Structure measured first (arms not yet run, 5 seeds, rule window 3)
  family   noncommuting pairs   oracle rules   ceiling   observed P3d gap
  F_T                     0.0             64     1.000             +0.292
  F_M                     4.0             52     0.560            UNKNOWN
  F_P                    11.2             22     0.310             +0.025

## Disclosure: the account does not uniquely determine the predictor
Two structural quantities are candidates and they DISAGREE. Registering both
rather than picking one after seeing the answer.

  Predictor A — log oracle rule count:  predicted gap +0.240
  Predictor B — oracle ceiling:         predicted gap +0.122

Note predictor A is suspect on its face: F_P has FEWER window-3 rules than F_T
(22 vs 64) because there is little to find there, so rule count at a fixed window
measures scarcity of equivalences rather than compactness. I expect B to do
better and am recording that expectation now.

## Falsifiers
  F1. The measured F_M gap falls outside BOTH bands
      A: +0.140..+0.340   B: +0.022..+0.222
      Then compressibility does not quantitatively predict the advantage and the
      account is descriptive, not predictive.
  F2. The measured gap is not between +0.025 and +0.292 at all. Then even the
      ORDERING fails and the account is wrong, not merely imprecise.

---

## VERDICT (written after running the arms)

```
family   noncommuting  oracle rules  ceiling   P3d gap
F_T               0.0            64    1.000    +0.292   (known before)
F_M               4.0            52    0.560    +0.152   (PREDICTED, then measured)
F_P              11.2            22    0.310    +0.027   (known before)
```

  measured F_M gap                                     +0.152
  predictor A, log rule count   +0.240  band +0.140..+0.340   IN (by 0.012)
  predictor B, ceiling          +0.122  band +0.022..+0.222   IN (error 0.030)
  F2 ordering between +0.025 and +0.292                       HOLDS

Neither falsifier fires. Predictor B was the more accurate, as recorded in
advance. The ordering is monotone in exactly the predicted direction on a family
that did not exist when the account was formed.
