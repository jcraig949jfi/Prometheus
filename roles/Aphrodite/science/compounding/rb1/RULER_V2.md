# RULER v2 -- TASK-GROUNDED NOVELTY + STRUCTURAL RELATIONS (RB-1 result, 2026-09-27)

Status: validated forensic instrument, proposed for freezing in AMENDMENT 18 (the next
compounding assay). The old ruler (tier3e.semantically_new) is NOT changed. It remains
the instrument of record for AMENDMENTs 12-17 and every historical label.
Code: rb1/ruler_v2.py. Validation: rb1/rb1_validate.py -> RB1_RESULTS.json.

1. DEFINITIONS (all relative to a reference schema R; for the compounding program R = G1)

  ACCUMULATING(b)  the body depends on acc AND on v somewhere on the task-grounded state
                   grid (acc >= 0, v 2..30, first 2..30, last 1..97).
  SPAN(R)          grid vectors of R's instantiations, and of its schema-level
                   RE-EXPRESSIONS (argument swap at a commutative root; additive sign
                   flip (a + {H}) <-> (a - {H})), each closed under the conjugate
                   b -> -b(-acc).
  NEW_V2           >= 2 accumulating instantiations, and >= 10% of them, fall outside
                   SPAN(R) and outside R's defining functional class (for G1: the
                   ADDITIVE class, i.e. any acc + f(v, first, last), however deep f is).
  NEW_TRAJ         the same proportion floor, judged on FOLDED TRAJECTORIES. Run
                   ('fold', init in {0,1}, b, acc) over 80 task-domain lists; the
                   trajectory must be non-degenerate (no None, >= 5 distinct values) and
                   differ from every reference trajectory.
  STRUCTURE        EQUAL; REFINES (S = R[t] with the hole inside t, modulo commutativity,
                   or R's operands a sub-multiset of S's at an associative root);
                   COMPOSES (S = C[R[t]] with a non-empty context C).
  NEW_FINAL        NEW_V2 and NEW_TRAJ and not EQUAL and not REFINES.

  Separate verdicts, never merged into one label:
    NOVELTY     NEW_FINAL
    COMPOUNDING REFINES or COMPOSES, and selected over R (scored downstream, by selection
                and payoff, not by the ruler)
    REACH       EXTENDS_REACH: accumulating instances outside the reference library's
                coverage

2. VALIDATION (old ruler vs v2 final; v2 never adds a NEW the old ruler missed)

  set               n    old-only (removed)  both  neither
  K3 PRISTINE univ  554        414            53     87
  K5 candidates       9          1             1      7   ((acc - {H}) removed; the 6
                                                           G1-built K5 winners =
                                                           REFINES, not NEW)
  K8 fresh          134         90            22     22
  random junk       100         66            16     18
  named              10          3             4      3
  Removal causes: 432 schemas with < 2 accumulating instantiations; 142 in-span, edge-only
  or trajectory-degenerate.

3. WHAT THE RULER NOW SAYS ABOUT THE EARLIER RECORD (forensic, no label changes)
  - E1 (AMENDMENT 17): unaffected (0 NEW under both rulers).
  - K5: G1 donors' 11/18 selections are COMPOUNDING (REFINES G1), not novelty. PRISTINE's
    2/18 (acc - {H}) "NEW" selections were false positives.
  - Of 467 old-ruler NEW schemas derivable from PRISTINE coverage, 53 survive (11%).

4. KNOWN LIMITS
  - The 10% floor and the >= 5-distinct-value trajectory criterion are conventions.
    Their sensitivity has NOT been measured yet. RB1_RESULTS rows carry the raw counts
    (accumulating, novel, novel_traj), so any floor can be re-applied offline.
  - Base rate: 16% of RANDOM single-hole schemas are NEW_FINAL. Novelty is common by
    chance, so any claim must pair NOVELTY with selection plus payoff against a sham
    baseline. The ruler measures difference, not value.
  - The trajectory battery is lists of length 2-40. Families whose novelty only appears
    at length 200 are not seen.
  - The panel-ablation (Ananke PTE) variant was not built. It stays open in T01 as an
    independent cross-check.
