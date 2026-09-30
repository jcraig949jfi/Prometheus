# T-INS-20 PLAN (frozen by commit before any T-INS-20 run)

Thread thr-8c7342a7d513 (carrier-swap instrument line), experiment
E-ANANKE-W-Y (delegated worker; must NOT edit this file; post-freeze
deviations go in its own PLAN_ADDENDUM.md written before the affected run).
Authority: CWO 2026-09-30 ANANKE (queue) + MWO-0004 R2. Cap: 3 CPU core-hours.

## 1 Question
In MAJ champion 4781b0a1 (sync update_period 2), W-P found the "neither" (N)
pattern is a joint carrier; W-V found the readout's own S1 never differs
between mirror partners, the readout's Kp differs in 78-98% of pairs, and its
raw readout is S0 = IN0_1 - 3 + Kp[7] (decompiled). Is the readout's Kp[7]
the readout-side half of the joint carrier at o10-o14 (the offsets where
readout-bound traffic matters)?

## 2 Arms (SINGLE-trial swaps, W-R fork runner / lens_swap semantics)
At offsets o10, o12, o14, both update-clock phases:
- KP7: swap only the readout site's Kp[7] between mirror partners.
- KPALL: swap the readout site's whole Kp vector.
- FLA: swap all in-flight packets addressed to the readout (W-S flight_a).
- KP7+FLA: both together.
- SITE_R: the readout site's full site arrays (W-S site_a), reference.
- NORMAL.

## 3 Measures and frozen decision
Follow effect e_X = fraction of eligible pair-trials whose readout follows the
partner (both partners normal-correct, scored); 99% pair bootstrap (2000);
M = 128 worlds, assays.world_seeds(0x670, 128); trials 1..11.
Per (offset, phase) stratum with SITE_R or FLA effect >= .50 ("informative"):
- KP7 IS THE READOUT HALF iff e_KP7 lo99 > .20 AND e_(KP7+FLA) >= max(e_KP7,
  e_FLA) + .10 (lo99 of the difference > 0) -- i.e. Kp[7] carries bit and
  combines with the in-flight payload.
- KP7 REDUNDANT iff e_KP7 lo99 > .20 AND the joint arm adds nothing
  (difference CI contains 0).
- KP7 NOT A CARRIER iff e_KP7 hi99 < .05.
- Otherwise UNRESOLVED.
Report KPALL vs KP7 (does another Kp slot matter?).

## 4 Known answers (build before touching the champion)
- Plant A: readout S0 := IN + Kp[j] with the cue written into Kp[j] by the
  readout's own program and into the in-flight payload (both halves carry):
  must read KP7-analogue IS THE READOUT HALF.
- Plant B: same plant with Kp[j] constant (cue-free): must read NOT A CARRIER.
Must-fail: swapping a cue-free Kp slot in Plant A reads NOT A CARRIER; the
classifier fed shuffled pair labels reads UNRESOLVED or NOT A CARRIER.

## 5 Failure interpretations
- KP7 NOT A CARRIER at all informative strata: the readout-side half is not
  Kp[7]; W-V's decompilation reading is wrong or Kp[7] is cue-constant at
  readout time; next candidate is the readout's inbox (Acc_sum) at o14-o15.
- UNRESOLVED everywhere: report effect sizes; do not expand the design here.

## 6 Resources
<= 3 CPU core-hours, Fabric lease skullport:cpu8 for > 2 threads (else <= 2
threads unleased), no GPU, outputs <= 2 MB.
