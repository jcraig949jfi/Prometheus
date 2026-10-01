# RB-1 -- A DOMAIN-GROUNDED, CONJUGATE-CLOSED NOVELTY RULER (threads T01, T02)

Prerequisite for any future NEW verdict. Cheap, autonomous. Estimated 3-6 hours.
Read RB-00 first.

WHY
  The current ruler (tier3e.semantically_new) has two false-positive channels:
    R-a  (acc - {H}) is NEW on 7/161 floor-div/mod sign edge cases. It is the schema-level
         conjugate of G1, which the operator's definition excludes. K5: 2/18 PRISTINE
         donors "discovered" it.
    R-b  the key grid uses negative acc, so abs() variants (v + gcd(0, acc)) look novel.
         K7: 24/31 "non-G1" qualified families are extensionally G1 on the task domain.
  It also has no COMPOUNDING verdict: 11/18 K5 G1 donors selected G1-built schemas that
  it (correctly) calls NOT NEW.

GOAL
  A frozen, testable ruler family:
    NEW_DOMAIN(S, ref)   S has instantiations whose WHOLE-PROGRAM behaviour on the task
                         domain (values 2..30, lengths 2..200, query 1..97; the tribunal
                         shapes included) is not matched by ANY program in ref's
                         coverage, AND S is not in the schema-level conjugate/renaming
                         closure of ref.
    COMPOUNDS(S, ref)    S's instantiations are a proper subset of, or refine, ref's span,
                         and S is selected over ref.
    PANEL_ABLATION(S)    the vector of per-family paired savings of [S] + base on a fixed
                         task panel (Ananke PTE idea). Two schemas are the same iff their
                         vectors match within noise.
  and a validation report showing each variant's behaviour on known cases.

STEPS
  1. Implement extensional equality over task-domain inputs (reuse spikes/k7_domain_novelty.py:
     fasteval + early exit). Build a schema-level conjugation map: H -> (0 - H) inside
     +/-, and argument swaps for commutative ops. Prove or check the closure on G1.
  2. Score, under old and new rulers: the 467 K3 NEW schemas (K3_DERIVABLE_UNIVERSE.json),
     every K5 candidate (K5_SUPPLY_VS_MECHANISM.json), 100 random junk single-hole schemas
     (seeded), and G1 itself (must be NOT NEW, and COMPOUNDS(G1, G1) = False).
  3. Tabulate agreement/disagreement. Every disagreement is a case study.
  4. Write RULER_V2_DRAFT.md with definitions, the table and recommendations. Do NOT
     freeze it into an AMENDMENT yourself unless your seat is Aphrodite. Otherwise hand it
     to Aphrodite.

DELIVERABLES
  science/frontier/rb1/ruler_v2.py, RB1_RESULTS.json, RULER_V2_DRAFT.md.
STOP CONDITIONS
  If extensional equality needs more than 10 min per schema, subsample coverage and say so.
  If the conjugation closure is not decidable syntactically, fall back to extensional
  equality only, and say so.
