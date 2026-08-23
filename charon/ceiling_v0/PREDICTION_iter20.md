# Pre-registered prediction — iteration 20, written BEFORE the run

## Claim under test
Iteration 19: "P3d's advantage is sample efficiency, not rule quality. Selectivity
pays under scarcity and becomes a liability under abundance."
Evidence so far is from F_P only, where the P3d-over-P3c gap ran
+0.025 (1x), +0.037 (3x), +0.047 (6x), -0.030 (12x) — a crossover between 6x and 12x.

If that is a general property of selectivity rather than an F_P quirk, the same
crossover must exist in F_T.

## Why the answer matters beyond bookkeeping
The standard arena is F_T at 1x, and I chose that budget during calibration in
iteration 2. If F_T's crossover sits close to 1x, then the headline result
(P3d 0.647 vs P3c 0.364) was obtained at a budget that specifically flatters
selectivity, and a sceptic is entitled to say the arena was tuned to the answer.
If the crossover is far above 1x, P3d's advantage is robust across the plausible
operating range.

## Prediction
F_T needs only ~64 rules for its ceiling, versus F_P's 1211. Arms at 1x already
buy 24-48. So F_T should saturate at a LOWER budget multiple than F_P did.

  P1. F_T shows a crossover (gap goes negative) at some multiple <= 12x
  P2. The F_T crossover occurs at a LOWER multiple than F_P's (which was
      between 6x and 12x) — I predict between 2x and 6x
  P3. P3c's rule count overtakes P3d's well before the accuracy crossover

## Falsifier
  F1. P3d retains an advantage >= +0.15 at 12x in F_T. Then selectivity is not
      merely a scarcity technology and iteration 19's generalisation is too broad,
      drawn from a single family.
  F2. The crossover occurs at or below 2x. Then the standard arena sits right at
      the edge of the regime that flatters selectivity, and the headline
      comparison should be reported as budget-contingent.

---

## VERDICT (written after the run)

```
 x   budget   P3c acc   P3d acc     gap   P3c rules  P3d rules  P3c cov  P3d cov
 1      100     0.370     0.662  +0.292       47.9       23.5    0.135    0.550
 2      200     0.472     0.895  +0.422      103.6       35.2    0.300    0.890
 3      300     0.560     0.918  +0.358      155.7       40.7    0.450    0.963
 6      600     0.670     0.993  +0.323      314.7       50.8    0.600    1.000
12     1200     0.792     0.963  +0.170      633.8       74.2    0.745    1.000
```

P1 crossover at some multiple <= 12x   REFUTED — no crossover exists in F_T
P2 crossover lower than F_P's          REFUTED — there is none
P3 P3c rule count overtakes P3d        CONFIRMED (immediately, at every multiple)

Falsifier F1 FIRES (+0.170 at 12x, threshold 0.15). F2 does not fire.
Iteration 19's "selectivity is a scarcity technology" was generalised from a
single family and is WRONG for F_T. Revised account in the iteration log.
