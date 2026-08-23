# Pre-registered prediction — iteration 25, written BEFORE running arms on F_MT

## The weakness being addressed
RESULTS.md (iteration 24) showed the low end of the compressibility curve is noise:
F_M2 +0.019 (1.3 SE) and F_P +0.021 (1.5 SE) are not distinguishable from zero.
So the F_M2 "prediction success" of iteration 22 landed in a band spanning zero,
which is not a real test. The account therefore rests on ONE genuine out-of-sample
hit (F_M) plus one solid anchor (F_T, +0.284, 6.8 SE).

This iteration adds the discriminating test proposed in iteration 22 and never run:
a family at the HIGH end of the curve, where the predicted gap is large enough that
its noise-justified band excludes zero.

## F_MT
One permuting action, restricted to a TRANSPOSITION (order 2) rather than any
permutation. Less disruption per application, so it should be more compressible
than F_M and sit between it and abelian F_T.

Structure measured first, arms not run:
  ceiling 0.630   noncommuting pairs 3.6/16
  ordering: F_T 1.000 > F_MT 0.630 > F_M 0.560 > F_M2 0.360 > F_P 0.310

## Prediction (predictor B: interpolate the gap on oracle ceiling, 20-seed anchors)
  PREDICTED gap +0.143   band +0.061 .. +0.225
  Band excludes zero: YES — so this IS a discriminating test.

## Falsifiers
  F1. Measured 20-seed gap falls outside +0.061..+0.225.
  F2. Measured gap not ordered between F_T (+0.284) and F_M (+0.107), given
      F_MT's ceiling lies between theirs.

---

## VERDICT
  PREDICTED +0.143   band +0.061..+0.225 (excludes zero)
  MEASURED  +0.142   SE 0.025, 20 seeds, 5.7 SE from zero
  F1 outside band  -> does not fire (error 0.001)
  F2 ordering      -> HOLDS (+0.107 < +0.142 < +0.284)

The error of 0.001 against an SE of 0.025 is fortuitous. The defensible claim is
that a discriminating out-of-sample prediction landed well inside noise, not that
the predictor is accurate to a thousandth.
