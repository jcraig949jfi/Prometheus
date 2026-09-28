# RESULT -- iterated learning through a bottleneck (raid_A kill test IL-1)

Status: EXPLORATORY. 2026-09-28. stdlib, 4 cores, 397 s for the preregistered
run (16 arms x 20 chains x 30 generations) + 67 s + 34 s + 32 s post-hoc.
Pure ASCII.

Order of events: PREREG.md written -> il.py written -> one smoke run (G=6,
2 chains/arm; code check only, printed, nothing saved) -> Mantel null sped up
(algebraically identical statistic, checked to 1e-12; no parameter, arm or
threshold changed) -> preregistered run (result.json) -> analyze.py
(analysis.json) -> THEN post-hoc diagnostics diag.py, diag2.py, diag3.py
(diag*.json), written after seeing the failure. The preregistered verdict
comes only from analysis.json.

## 1. Preregistered verdict

  V1 HOLISTIC null          PASS  median z30 = 0.06
  V2 PLANTED positive       PASS  median z30 = 38.8, LEARN_SAME30 = 0.88
  K1 ratchet vs one step    FAIL  ASSOC B16 F1: LEARN_SAME +0.17 (needed +0.30);
                                  z30 > z1 in 3/20 chains (needed 16)
  K2 bottleneck necessary   PASS  ASSOC B64: median z30 = 0.72, LEARN 0.00
  K3 convention invented    PASS* 9 signatures among 20 chains with z > 3, BUT
                                  12/20 chains have NO position with MI > 0.5
                                  bits ('------'): weak diffuse structure,
                                  not a code. Nominal pass, substantively empty.
  K4 content dependence     FAIL  permuted-sample reader 0.147 vs intact 0.241
                                  (partly degenerate codes are guessable)
  K5 ceiling vs recompute   FAIL  recompute arm 0.00 as predicted, but chain
                                  only 0.24 (needed 0.5)
  E1 expressivity (Kirby15) AS PREDICTED  EXPR30 0.08 without the homonym
                                  filter (collapse to a near-constant code,
                                  trivially "learnable" 0.92) vs 0.36 with it
  E2 minimal bias NNCOPY    NEITHER  LEARN 0.39, EXPR 0.43; structure z falls
                                  from 9.0 (gen 1) to 0.8 (gen 30); stability
                                  0.07 -- a churning, partly degenerate code

PREREG s6 consequence: K1 failed -> for the ASSOC learner the chain adds
nothing beyond one application of the learner's bias. Structure is maximal
right after the first learner (median z 18.3 at gen 1) and DECAYS to ~14
while expressivity falls to 0.36 and the code never stabilises (STAB 0.08).
Translation KILLED AS SUPERFICIAL for the preregistered learner.

## 2. Post-hoc diagnosis (NOT preregistered; decides what the kill means)

diag.py -- CLOSURE vs CONVERGENCE. Start ASSOC chains from a PERFECT
compositional code (each feature -> 2 positions, bijective): a fresh ASSOC
reader recovers only 0.32 of unseen meanings from 16 samples, and chains
started there decay to the same z ~ 15, EXPR ~ 0.4, STAB < 0.2 as chains
from random codes, at B = 16, 32, 48 and mu = 0, 0.01 (only B48 mu0 holds
partly: z 29, STAB 0.69). The failure is CLOSURE: the target code is not a
fixed point of the ASSOC chain. Cause: with ~4 samples per feature value the
naive-Bayes product lets irrelevant features veto the right symbol.
diag2.py -- ADDITIVE voting instead of product: same closure failure
(perfect code read at 0.34; random-start chains z30 > z1 in 5/20).
diag3.py -- SELECT learner: per position, pick the single feature with the
highest MI in the training sample, predict by majority within that feature
value. Installs "each position depends on one feature", NOT which feature.
From RANDOM codes, 20 chains:
    gen   z      EXPR   LEARN_SAME
    0    -0.04   0.995  0.00
    1    23.7    0.82   0.20
    5    34.1    0.83   0.68
    30   36.6    0.95   0.82
  z30 > z1 in 20/20 chains; STAB 0.78; permuted-sample reader 0.005 vs
  intact 0.82; 20 DIFFERENT alignment signatures in 20 chains (each world
  writes its own convention; none is the "planted" 001122). A perfect code
  is closed under SELECT (0.97 -> 0.77 after 30 noisy generations).
  Every preregistered criterion K1-K5 would pass for SELECT (recompute arm
  is 0 by the same argument as for ASSOC: more samples of a random code are
  still a random code) -- but SELECT was chosen after seeing the failure, so
  this is a hypothesis, not a result.

Also seen (unplanned): the codes SELECT and PLANTED build are readable by
their own learner class (0.82, 0.88) but NOT by an ASSOC reader (0.25,
0.29). The value of the accumulated code is READER-RELATIVE.
NNCOPY B64 F1 reached z30 = 5.2 with NO sampling bottleneck: the homonym
filter itself acts as a bottleneck once noise creates collisions.

## 3. What this does to the transplant (feeds RAID.md s2)

1. The Griffiths-Kalish reduction is right in the strong form that matters
   for Prometheus: the chain reaches only codes that are FIXED POINTS of the
   receiver's regrowth rule at that bottleneck. Where the rule cannot hold a
   structured code (ASSOC, ADD, NNCOPY), the bottleneck produces a one-step
   burst of structure and then churn -- not accumulation.
2. Where the rule can hold one (SELECT, PLANTED), there IS a multi-
   generation ratchet (not a one-step effect: learnability 0.20 -> 0.82
   over 30 generations) AND the convention is history-written (20/20
   distinct), which is ACCUMULATION_v0's "invented, not installed" test
   passed for the CONVENTION while the hypothesis CLASS is installed.
3. So the alien content survives in a narrower form: inheritance by
   reconstruction accumulates structure iff the reconstruction rule's
   fixed-point set contains structured codes at the bottleneck width. For a
   Z80 soup this turns the transplant into a precise question: does the
   substrate's regrowth dynamics have structured fixed points (closure),
   testable BEFORE any evolutionary run by seeding a structured pattern and
   applying partial-copy + regrowth (the diag.py test) -- DA-1's closure
   half, applied to IL-1.
4. For ACCUMULATION_v0: (a) add a CLOSURE PRECHECK -- a planted instance of
   the target object must be a fixed point of the consumer's reconstruction
   before an unplanted run can be read; (b) R2 "new consumer" must be scored
   per reader class, because the accumulated object is reader-relative
   (SELECT code: 0.82 own reader, 0.25 ASSOC reader).

Files: PREREG.md, il.py, analyze.py, result.json, analysis.json,
diag.py/diag.json, diag2.py/diag2.json, diag3.py/diag3.json.
