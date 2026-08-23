# Pre-registered check — iteration 23, written BEFORE the re-run

## Why
Iteration 22 found F_M's gap moved 0.045 between 10 and 20 seeds, larger than its
standard error. That makes every 5-12 seed sweep in iterations 15-21 provisional.
The most load-bearing is the iteration-16 HORIZON sweep (12 seeds), which claimed:

  "P3d's advantage GROWS with the probe cap: +0.140 at cap 4 to +0.481 at cap 10"

and from which the scale-invariance account was drawn. If that trend does not
survive 20 seeds with standard errors attached, a major claim falls.

## What is being re-run
Probe cap in {4,6,8,10}, query length always cap+2..cap+6, P3c vs P3d, 20 seeds,
with paired per-seed standard errors.

## Falsifiers
  F1. The gap is NOT monotonically increasing in cap at 20 seeds.
  F2. The cap-4 to cap-10 increase is smaller than 2 standard errors of the
      difference, i.e. the "advantage grows with arena size" claim is within noise.
  F3. Any individual cap's 20-seed gap differs from its 12-seed value by more than
      0.08 (the worst-case 95% half-width measured in iteration 22), indicating the
      original sweep was too noisy to have supported any conclusion.

---

## VERDICT

### Horizon sweep re-run at 20 seeds — SURVIVES
```
cap   P3c     P3d      gap     SE   12-seed gap   shift
  4  0.371  0.546   +0.175  0.047       +0.140   +0.035
  6  0.364  0.647   +0.284  0.042       +0.290   -0.006
  8  0.370  0.675   +0.305  0.040       +0.331   -0.026
 10  0.297  0.751   +0.454  0.052       +0.481   -0.027
```
F1 monotone increasing                        HOLDS
F2 cap4->cap10 rise +0.279 vs 2*SE_diff 0.140 does not fire (~4 SE)
F3 largest shift 0.035 vs 0.08                does not fire
Iteration 16's claim stands, now with error bars. The 12-seed sweep WAS adequate
for that claim, because the effect (0.279) dwarfed the noise (SE ~0.05).

### Iteration-20 verdict — CONCLUSION SURVIVES, TEST DID NOT
  10-seed gap at 12x budget  +0.170
  20-seed gap at 12x budget  +0.101   SE 0.031   95% CI +0.040..+0.162
The iteration-20 falsifier was "P3d keeps >= +0.15 at 12x", and it was recorded as
FIRING. At 20 seeds the 0.15 threshold sits INSIDE the confidence interval, so
that test was decided by noise, not by data.
The substantive conclusion nonetheless holds on other grounds: +0.101 is 3.3 SE
from zero and never negative, so there is still no crossover in F_T and
selectivity is not merely a scarcity technology.
Right conclusion, invalid test. Both halves recorded.
