# C4 gate S0 -- trivial rules and baselines (PREREGISTERED before any successor law search)

Campaign C4 (successor to C3; new preregistration, not a repaired C3). Thread T-C4 thr-cac8c079f216.
Authority: operator 2026-09-30 (roles/Cosmos/prompts/2026-09-30_operator_c3_disposition/), gate S0.
Written 2026-09-30, before any C4 coordinate exists and before any S0 baseline number is computed. It is
frozen as FREEZES F-0001, and any change needs a new freeze that names this one in `supersedes`.
It reads no D/D2 material and is not designed around D2.

## 1. The phenomenon label (unchanged from C3; the LABEL only)
Per world, the certificate class NONE / PASSIVE / FUNCTIONAL (INDETERMINATE and INCOHERENT are reported,
never relabelled, and excluded from fitting). The primary S0 target is binary: FUNCTIONAL vs not.
Certificate A is the C3 v3 P1/P2 certificate (prometheus/cosmos/c3/certify.py). Certificate B is the
gate-S3 certificate (DESIGN_C4.md s4). S0 is scored under Certificate A, and S3 repeats it under B.

## 2. Evaluation
- PRIMARY: leave-one-family-out (LOFO). Every rule with any fitted part is refit on the training
  families only.
- Primary score: balanced accuracy (BA) on the held-out family, pooled over all held-out predictions.
  Also reported: worst-family BA and per-family BA.
- Pooled (within-family) cross-validation is reported ONLY as a leakage reference, never as evidence.

## 3. The trivial rules (all computed for every evaluation set; none may be dropped)
T0 MAJORITY. Predict the training folds' majority class. Reported with its accuracy. Its BA is .5 by
   construction.
T1 FAMILY-ID. Under LOFO a held-out family has no ID, so T1 has two parts:
   T1a (LOFO): identical to T0.
   T1b (leakage reference): predict each family's own majority class, scored by within-family
   leave-one-out. This gives the score of "knowing the family and nothing else".
T2 SIMPLE NATIVE FEATURES.
   T2a (LOFO): logistic regression on the task parameters every family shares (delay k, alphabet V).
   T2b (within-family ceiling): per family, logistic regression and 5-NN on that family's own declared
   native parameters plus k and V, scored by within-family leave-one-out, taking the better of the two.
   T2b is NOT a cross-substrate rule. It shows what family-specific knowledge alone achieves.
T3 ZERO-PARAMETER CERTIFICATE RULE (the definition rung; no fitted value, no threshold)
   T3-DOWN, the C3 definition rung: the P1/P2 preconditions evaluated with the certificate's own
   paired common-random-number construction at query time q = k+1:
     NONE        if the cue-paired full-state distance at q is exactly 0
     PASSIVE     if it is > 0 and the cue-paired readout-feature distance at q is exactly 0
     FUNCTIONAL  if the cue-paired readout-feature distance at q is > 0
   The reference implementation is zero_rule() in the withheld C3 autopsy (c9f8aff17). A public
   re-implementation is written for C4 from this text, not copied.
   It has zero parameters and needs no training folds, so its LOFO score is its plain score.
   BINDING (operator gate S0): any C4 representation must beat T3-DOWN.

## 4. "Materially better" (fixed now)
A candidate C4 representation passes S0 only if ALL of the following hold:
(a) Pooled LOFO BA margin >= 0.05 over EACH of T0, T1a, T2a and T3-DOWN, with the lower bound of a 95%
    paired bootstrap interval > 0. The bootstrap resamples worlds within family, 2000 resamples,
    seed 20260930.
(b) Exact McNemar test vs T3-DOWN on the determinate rows: p < 0.05, AND more rows where only the
    candidate is right than rows where only T3-DOWN is right.
(c) Worst-family LOFO BA >= the worst-family BA of T3-DOWN.
(d) T1b and T2b are reported next to the candidate. If the candidate's LOFO BA does not exceed T1b, the
    report must say "the representation carries no more than family identity" (a WARNING, and an S2
    trigger).
Failing (a), (b) or (c) is a STOP (directive: "stop"). It is reported as "no successor law earned at
S0". It is not repaired on the same worlds.

## 5. Hard exclusions
- The C3 preliminary law (GRAVEYARD G-0006) is NOT a candidate, is NOT refit, and none of its
  coordinates is used. It is also not used as a baseline, so that nothing in C4 consumes it.
- No threshold in s4 moves after any C4 number is seen.
- T3-DOWN is computed with the certificate's machinery. That is allowed because it is a BASELINE.
  C4 candidate coordinates may not use that machinery (gate S1).
