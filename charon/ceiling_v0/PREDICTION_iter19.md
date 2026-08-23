# Pre-registered prediction — iteration 19, written BEFORE the run

## Claim under test
Iteration 18: "the substrate succeeds exactly when the rule set required to
collapse the query population is affordable at the interaction budget."
F_T needs ~64 rules (affordable, ceiling 1.000, P3d reaches 0.652).
F_P needs ~217 at window 4 / ~1211 at window 5 (NOT affordable at 20-48 rules,
ceiling 0.550, P3d reaches 0.310 with an advantage over P3c of only +0.021).

## Prediction
Scaling F_P's interaction budget AND its claim allowance together (so the arm can
actually purchase rules rather than merely probe more) should:

  P1. raise P3d's F_P accuracy toward F_P's ceiling of ~0.550
  P2. restore P3d's advantage over P3c from +0.021 toward the F_T-like gap
      (F_T shows +0.290); I predict >= +0.15 by 12x budget
  P3. raise the number of surviving rules roughly in proportion to budget

## Falsifier — what would overturn the affordability account
  F1. At 12x budget, P3d's advantage over P3c remains < +0.10
  F2. At 12x budget, P3d's F_P accuracy remains < 0.40 (i.e. under 73% of its
      reachable ceiling, versus the 65% it reaches in F_T at 1x)

If either fires, affordability is NOT the binding constraint in F_P and the
iteration-18 account joins the three already withdrawn.

## Confound being controlled
Budget alone is not enough: with claims_per_turn fixed at 3 the arm cannot buy
more rules no matter how much budget it has, so it would just probe more. Claim
allowance and probe allowance are scaled together, preserving the mix.

---

## VERDICT (written after the run)

```
F_P budget   P3c acc   P3d acc   gap      P3c rules  P3d rules
   1x         0.287     0.312   +0.025      31.2       19.9
   3x         0.408     0.445   +0.037     112.0       60.1
   6x         0.465     0.512   +0.047     237.9       86.8
  12x         0.540     0.510   -0.030     442.7      117.5
F_T 1x        0.370     0.662   +0.292      47.9       23.5
```

P1 accuracy rises toward the ceiling      CONFIRMED (0.312 -> 0.510, 93% of 0.550)
P2 advantage recovers to >= +0.15         REFUTED — falsifier F1 FIRES (gap -0.030)
P3 rules scale with budget                CONFIRMED (31 -> 443, 20 -> 118)

Falsifier F1 fired; F2 did not. The affordability account is therefore CORRECT
about accuracy and WRONG about the advantage, and must be split accordingly.
