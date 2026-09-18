+=====================================================================+
|  C5-08 -- ROBUSTNESS MECHANISM TEST: PREREGISTRATION                  |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Campaign 5, Phase B (written while C5-05 runs, before it reports)   |
+=====================================================================+

CAMPAIGN 4's CLAIM (fact 5 of the directive): robustness to single edits
(the neutral share D5) is neutrality plus length -- dead and unreachable
code absorbing edits -- not insulation. Under representation B the
question becomes: does the boundary add a robustness component of its
own (FIZZLE skipping executed faults), and is the old component still
dead code?

DESIGN. Two parent sets, one census each, three interpreters.
  P_full     the 57 canonical parents (C5-05's rows are reused: grammar
             B arm, 8 draws x 12 operators)
  P_ablated  the same parents with statically unreachable instructions
             removed (proteus grammar.static_reachable on the canonical
             genome; the reachable instructions kept in order; length
             falls; behaviour under OLD must be UNCHANGED on the parent
             environment -- checked, and a parent whose behaviour changes
             is excluded and counted). A fresh single-edit census on
             P_ablated: grammar B, 8 draws x 12 operators, the three
             interpreters, C5 seeds (a NEW measurement).
  length bins  1-8, 9-16, 17-32 instructions (canonical length);
             comparisons are made within bins and pooled.

QUANTITIES (per parent set x interpreter; Wilson bands)
  R_old   D5 share under OLD                      (C4's robustness)
  R_fail  D5 share under B_FAIL
  R_fizz  D5 + DF/D5 share under B_FIZZLE         (skips count as neutral)
  GAP     R_fizz - R_fail                          (the boundary's own
                                                    contribution)
  DEAD    unreachable share of the parent's instructions

PREREGISTERED TESTS (all at the band 1/16)
  M1 dead code carries robustness: R_old(P_full) - R_old(P_ablated) >
     band pooled and in >= 2 of 3 length bins.
  M2 the boundary's contribution is not dead code: GAP(P_full) and
     GAP(P_ablated) within a band of each other.
  M3 GAP is the executed-crossing rate: GAP within a band of the share
     of grammar-B children that cross AND execute the fault (C5-05 T1
     numerator over all children) on the same parent set.
  M4 length-matched: within each length bin, R_fail(P_full) <
     R_old(P_full) by no more than the executed-crossing share of that
     bin plus a band (the boundary removes only the crossing children's
     neutrality, nothing else).
  READINGS: NEUTRALITY_PLUS_LENGTH_CONFIRMED_UNDER_B iff M1, M2 and M4
  hold (M3 reported); BOUNDARY_ADDS_ROBUSTNESS iff M2 fails with
  GAP(P_ablated) > GAP(P_full) + band; otherwise MIXED.
  Prediction written to be lost: M1, M2, M4 hold; M3 holds.

CONTROLS: ablation preserves OLD behaviour on the parent environment for
every included parent (reward and answer vector equal); identity edits
100%; determinism on one parent.
