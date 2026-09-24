# c2x -- complete the 2x2 and replicate C2 -- PREREGISTRATION (2026-09-23 ~15:52Z, before running)

Arms (both new configs in campaign0.py; no sealed universe is used -- none remains):
  c2none  seed 20260929 (the C2/c2abl seed), NO cost lines, NO location-aware selection (LOLO pick as
          in C0b/C1), location gate ON. Completes the lines x selection 2x2 on one seed.
  c2rep   C2 exactly, fresh seed 20260931. Replication: positive results are provisional.
Predictions: c2none -> no law survives the location gate (conf 0.6). c2rep -> a law survives with
worst per-family offset <= 0.10 log2 and a G exp(-N)-product ceiling (conf 0.5).
Scope: one seed per cell; the 2x2 is descriptive, not a significance test.

## c2none RESULT (2026-09-23T16:04Z)
NO lines, NO location-aware selection, location gate ON, seed 20260929: round 0 law FAILED by the
location gate (ring +.134, ca +.063); revised law ce54e6dd6f (v4)
  (exp(-N) - C/G) >= 0.1454  AND  ((C - log Q) K) >= 0.16
SURVIVED round 1 (1/111; offsets ca .000 regs -.033 ring +.055). Prediction LOST.
On seed 20260929 all three arms run (both / selection only / neither) produced a surviving, well-
located law; C1 (lines, no selection) failed on seed 20260928. The lines x selection attribution is
confounded with seed. Added arm (written before it runs):
  c1s29   C1 exactly (lines, no selection, location gate) on seed 20260929 -- completes the 2x2 on one
          seed. Prediction (conf 0.5): it produces a survivor too (i.e. C1's failure was the seed).

## c2rep RESULT (2026-09-23T16:25Z) -- C2 replication on fresh seed 20260931
Law e654764319 (v4): (Q - C K) <= 0.8385 AND C - G exp(-N) <= -0.0945
SURVIVED round 0 (0/106; offsets ca -.027 regs -.021 ring -.016). Prediction HELD (worst offset
<= .10 and a G exp(-N) product ceiling).
Convergence across the three location-gated survivors on two seeds: ceiling G exp(-N) - C >= 0.102
(C2), 0.0945 (c2rep), 0.145 G (c2none); the task economics give 0.10.

## c1s29 RESULT (2026-09-23T16:29Z)
Lines, NO selection, seed 20260929: law ce2c66c36f (v4) (Q - C K) <= 0.8415 AND C - G exp(-N) <= -0.1026
SURVIVED round 0 (0/107; offsets ca -.024 regs -.044 ring +.002). Prediction HELD.
Seed-29 2x2 is complete: all four cells (lines x selection) produced a surviving, well-located law.
This law is exactly C2's top LOLO candidate; C2's location-aware selection had instead picked a
different candidate that FAILED round 0 (selection-time location noise made selection WORSE than the
plain LOLO pick on this seed). C1's failure (seed 20260928) is therefore attributed provisionally to
the seed/data, not to the method.
FINAL discriminating arm (written before it runs; then no more method arms):
  c2none28  NO lines, NO selection, location gate, seed 20260928 (C1's seed).
  If it FAILS: seed 28's data defeats the method regardless of lines -> seed variance dominates.
  If it SURVIVES: lines-without-selection hurt on seed 28 specifically.
  Prediction (conf 0.55): it FAILS.

## c2none28 RESULT (2026-09-23T16:46Z) -- the final method arm
NO lines, NO selection, seed 20260928: round-0 law FAILED by the location gate (regs -.089 biased,
ring -.100); revised law c1b5a2630c (v4) (exp(-N) - C/G) >= 0.1605 AND (log Q - C K) <= -0.16
SURVIVED round 1 (2/107; offsets ca +.026 regs +.024 ring +.097 -- ring just under the .10 kill line).
Prediction (it fails) LOST.

## ATTRIBUTION MATRIX (survival within 3 rounds; one run per cell-seed; DESCRIPTIVE ONLY)
                 no cost lines            cost lines
  no selection   s28 SURV   s29 SURV      s28 FAIL (C1)   s29 SURV (c1s29)
  selection      s29 SURV (c2abl)         s29 SURV (C2)   s31 SURV (c2rep)
6 of 7 runs produced a surviving law; the only failure is lines-without-selection on seed 28.
CONCLUDED (search-method qualification): UNRESOLVED. Location-aware selection is NOT shown to be
necessary (both no-selection/no-lines runs survived). Weak single-seed evidence that cost lines
without selection can hurt (consistent with eta2's budget-matched loss to random). The apparent
C1 -> C2 improvement was mostly seed. What survives robustly across arms is the LOCATION GATE's
effect: in every arm it killed at least one otherwise-passing law or passed only well-located ones.
Method arms stop here (operator direction 2026-09-23 16:27Z).
