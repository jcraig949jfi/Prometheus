# ENSORAIN E2 -- preregistration part 2 (constants; before OUTER and confirmatory)

Currency: 2026-09-23. Part 1 (efbf950af) unchanged in every gate,
threshold, arm, family, seed set and verdict clause.

## 1. Per-family learning constants (dev 500-505, ORACLE_H lives,
## objective median held-out R^2; rows e2_calibrate.jsonl)
  TT  lam 30, sweeps 20 (0.97)    LR  lam 30, sweeps 10 (0.997)
  CP  lam 10, sweeps 20 (0.79)
Used by every arm for the committed memory's in-life consolidation.

## 2. Dev findings and two engineering fixes (declared; mechanism-neutral)
A dev sanity pass (e2_dev_check.jsonl, 3 instances x 10 arms x 4
families) showed near-zero identification for EVERY in-life arm while
ORACLE_H learned. Two defects, both in shared machinery, none in any
mechanism:
 F1. From-scratch discovery fits used E1's PROXIMAL ridge (toward the
     current parameters, here the random initialisation). On the buffer the
     correct rank-1 LR fit DIVERGED (held-out R^2 -1.6 -> -24 over 60
     sweeps). Fix: discovery fits and the committed memory's first fit use
     an ordinary ridge toward 0 (ensorain/e1/mem.py `_ridge(zero=True)`,
     opt-in; E1 default unchanged, regression test added); the proximal
     ridge resumes for in-life consolidation.
 F2. The fit/validation split could put the same cell on both sides (a
     cell observed twice). Fix: split BY CELL (part 1 said "384 fit / 128
     held out"; the split is now ~384/~128 by cell). This is the "honest
     split" part 1 s8 P2 assumed.
Discovery ridge disc_lam calibrated on dev by a MECHANISM-INDEPENDENT
criterion -- the CORRECT hypothesis fitted from scratch on the discovery
buffer, family sweeps, median held-out R^2 (e2_calibrate_disc.json):
  disc_lam  0.01   0.1   1.0   3.0   10
  TT       -4.59  0.73  0.90  0.72  0.00
  MAT      -8.93 -1.88  0.79  0.64  0.04
  CP       -2.04 -0.48  0.44  0.03  0.00
Frozen disc_lam = 1.0. No identification rate was consulted for either
fix or for disc_lam.

## 3. Discovery compute ceiling
Exhaustive evaluation of all 17 hypotheses at the family sweeps costs
~20.7M units on 384 samples; part 1's criterion ("must NOT fit") ->
D = 8.0M units (~40%), 40 energy at kappa 5e-6.

## 4. OUTER
Selected on training seeds 4000-4063 (16 per family, all families mixed)
after this commit; appended below before any confirmatory row.
