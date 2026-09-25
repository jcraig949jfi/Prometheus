+==============================================================================+
|  APHRODITE ENGINE REVIEW 11 -- THE S1-S4 CHAIN                              |
|  Whole-program identity -> fair meta-selection -> endogenous abstraction ->  |
|  abstraction transplant                                                      |
|                                                                              |
|  Author : Aphrodite (RSI science seat), host harry1 / M4                     |
|  Date   : 2026-09-24 (work 2026-09-23 .. 2026-09-24)                         |
|  For    : James (HITL operator) and external reviewers                       |
|  Status : S4 COMPLETE -- returned to operator per the S1 ruling              |
|  Self-contained: every load-bearing number is inline; no repo access needed. |
+==============================================================================+

------------------------------------------------------------------------------
0. SUMMARY AND VERDICTS
------------------------------------------------------------------------------

The open question at the start (operator, 2026-09-22): "Aphrodite has
demonstrated transferable local search leverage and ... that a reusable schema
can generalize across unseen families, but has not yet demonstrated that the
improver can discover that abstraction itself."

The operator ordered a causal chain, each step frozen in a dated amendment
BEFORE its code was written or anything was measured:

  S1 whole-program identity   GLOBAL_BEHAVIOR_IDENTITY   = FAIL (3 runs)
                              CAMPAIGN_RELEVANT_IDENTITY = PASS (class certs)
  S2 fair meta-selection      S2_PASS
  S3 endogenous abstraction   ENDOGENOUS_ABSTRACTION     = YES
  S4 abstraction transplant   ABSTRACTION_TRANSPLANT     = YES (all 8 conditions)

Headline. The donor derived the hole-bearing schema (acc + {H}) mechanically,
from its own certified successes, by anti-unification. It selected that schema
by a paired rule, on validation families it had never observed. The derived
library then took fresh recipients from 0-1/16 to 16/16 on five unseen-body
families under a hostile tribunal. It beat PRISTINE and the preregistered sham
distribution, with 0.39% false-positive hits. The break-even is 41.2
descendants against a horizon of 64.

Ceiling (section 7): one bounded meta-generation, on a synthetic integer DSL
and a catalog the seat designed. The derived library is content-identical to
the known positive control; the claim is DERIVATION, not a new mechanism.
Campaign 1 remains frozen and unrun; nothing here is Campaign 1 evidence.

------------------------------------------------------------------------------
1. WHAT WAS BUILT, AND WHAT WAS FROZEN FIRST (commit order)
------------------------------------------------------------------------------

  287d208ea  AMENDMENT 12     S1 design: three identities (source / structure
                              / behavior), safe rewrites only, a behavior
                              battery B1, an independent audit battery B2,
                              gates G-S1.1..7
  d72595bb0  run-1 report + ADDENDUM 1 (coverage repair, emitter v2, fresh
                              audit) -- frozen before the repairs were coded
  4a6bbf55d  AMENDMENTS 13 + 14 (S2; S3 + S4 with S5-S7) -- frozen BEFORE any
                              S2-S4 code and while S1 was still running, so the
                              S4 families, arms and criterion could not be
                              chosen after seeing a derived schema
  18ab82c50  ADDENDUM 2       identity over the valid task domain (op ruling)
  a2ba379aa  ADDENDUM 3       global FAIL recorded; campaign-local class
                              certificates, including the adversarial
                              generator, frozen before the certifier existed
  52dad4db7  S1-local PASS, S2 PASS, S3 artifact (frozen before S4)
  65edc1251  S4 results
  (branch aphrodite/engine-2026-09-21; pushed)

Code: identity.py (three identities), s1_fixtures.py and s1_gate.py, cert.py
(class certificates), s1_local_gate.py, fair.py (keyed common random numbers),
s2_gate.py, tier3d.py (catalog, member enumeration, least general
generalisation (LGG)), run_s3s4.py.

------------------------------------------------------------------------------
2. THE DSL AND WHY S1 WAS NEEDED
------------------------------------------------------------------------------

Programs are integer folds: ('fold', init, body, final). acc = init; for v in
the sequence: acc = body(acc, v, first, last); return final(acc, first, last).
Primitives: add, sub, mul, floor-div, mod, gcd(|a|,|b|), and pow guarded to
exponents in [0, 32]. Division or modulo by zero fails. A 10^40 ceiling is
checked on the accumulator after every step and on the output; crossing it
fails.

Tier 3C (prior) failed to abstract because its donor observed body `acc - v*v`
with final `first - acc`: the same program as `acc + v*v` / `acc + first`,
factorised differently. Body-level anti-unification found nothing. S1's job
was to make identity a property of the WHOLE program, so that compensating
factorisations collapse before abstraction is attempted.

------------------------------------------------------------------------------
3. S1 -- THREE FAILED GLOBAL RUNS, THEN CAMPAIGN-LOCAL CERTIFICATION
------------------------------------------------------------------------------

behavior_id = the whole-program value vector (FAIL included) over a frozen
battery, computed by the SAME evaluator the search uses. structure_id uses
only rewrites that preserve value AND failure (for example, x - x -> 0 only
when x cannot fail; x // x -> 1 is refused).

RUN 1 (domain: all non-negative integers)
  PASS  collapse 163/163. The Tier-3C pair shares a behavior_id but NOT a
        structure_id, so no rewrite rule did the collapsing.
  PASS  refinement, no-target static audit, old AMENDMENT-10 fixtures.
  FAIL  separation: 1/1,155 single-point mutants merged by B1 but separated by
        B2.
  FAIL  audit: 403 false merges / 6,304 classes.
  FAIL  conformance: 4,501 mismatches. A REAL ENGINE DEFECT: the emitted
        artifact never applied the ceiling to the OUTPUT. It was the fifth
        instance of the "implementation diverges from declared semantics"
        family. The standing 21,600-comparison sweep never produced an overflow
        in the final expression alone, so it had stayed green.
  Also found: AMENDMENT 10's body identity probed only non-negative
  accumulators, so it merged `v + |acc|` with `v + acc`.

RUN 2 (ADDENDUM 1: exhaustive short-input ceiling cross; emitter v2; fresh
audit)
  All gates PASS except audit: 179 false merges / 7,338 classes. Every one was
  FAIL-vs-value on a value more than 1 above the ceiling, while the band held
  only C+1. The seat did NOT repair a second time (pre-committed); it returned.

RUN 3 (operator ruling: identity over the VALID task domain -- sequence length
in {2..60, 80, 150, 200}, values in [2, 30], query in [1, 97]; the ceiling
stays execution semantics, so internal overflow on a valid input still counts
as behavior)
  PASS  collapse 199/199; separation 0/1,628 mutants plus 7 in-domain
        near-neighbours (two of them cross the ceiling INTERNALLY on valid
        inputs); refinement; conformance 21,600 + 7,833,930, 0 mismatches.
  FAIL  audit: 13 false merges / 3,445 classes. All genuine in-domain
        differences: fast-growing accumulators (last*(acc+1) vs acc*last,
        nested pow, v + acc*acc from different inits) cross 10^40 one step
        apart, on 1-6 of 10,000 valid inputs.
  Diagnostic over the donor's member space (151,920 programs): 74 / 7,808
  classes false-merged, but all 8 meta-development families' classes were
  audit-clean.

FAILURE SHAPE. A finite battery cannot certify the equivalence of programs
that differ only in the step at which a fast-growing accumulator crosses a
fixed ceiling, because that step depends on the exact input values. Each
fresh audit finds a few more.

DISPOSITION (operator, recorded): GLOBAL_BEHAVIOR_IDENTITY = FAIL, permanently.
behavior_id becomes a provisional bucket. Every class that can affect science
needs a CLASS CERTIFICATE: all members agree on B1 u B_CERT (20,000 fresh
valid inputs) u A(S). A(S) is a threshold-adversarial battery that brackets
EACH member's own smallest failing length over 109 base sequences x 8 queries,
plus last-element and query variants. It was frozen before any class was seen.
Certifier power (reported, not gated): it split 13/13 of the run-3 false
merges and 15/20 of the recorded member-space examples. Those records held
only the first 6 members of each class, so the splitting member may be absent.

S1-LOCAL GATE: 16/16 Tier-3D witness classes and member sets certified, 0
splits; conformance 21,600 + 321,392, 0 mismatches.
CAMPAIGN_RELEVANT_IDENTITY = PASS.

------------------------------------------------------------------------------
4. S2 -- FAIR META-SELECTION (AMENDMENT 13)
------------------------------------------------------------------------------

Defect repaired. Tier 3C scored two byte-identical libraries at 13,479 and
51,018 charges, because the search RNG was seeded with the library's NAME.

Fix. Every list the search walks is sorted by
sha256(seed / slot / item). The key never sees the library or the arm. Cells
(family, replicate) are shared across all candidates. Selection: pick the
largest mean paired saving vs PRISTINE whose one-sided 95% lower bound is > 0;
otherwise select PRISTINE.

  G-S2.1  identical-content libraries score identically      PASS
  G-S2.2  permuting an entry's lists changes nothing           PASS
  G-S2.3  arm label invariance                                 PASS
  G-S2.4  charges = position of the first acceptance (direct)  PASS
  G-S2.5  variance of paired vs unpaired differences:
          9.44e8 vs 1.55e9 (39% lower)                         reported
  G-S2.6  conformance, identity unchanged                      PASS

------------------------------------------------------------------------------
5. S3 -- ENDOGENOUS ABSTRACTION (AMENDMENT 14)
------------------------------------------------------------------------------

Catalog (frozen). Eight meta-development families, split lexicographically:
OBSERVE = md_a (acc+v, acc*last), md_b (acc+v*v, acc+first), md_c (acc*v,
acc-first); VALIDATE = md_d..md_h. Composition by shape: 4 add/sub, 2 mul,
2 gcd; 3 of the 5 validate bodies lie outside the pristine hole grammar, one of
each shape.

Generator qualification (the Tier-3C rule, unchanged) rejected all three
gcd-shaped families (md_d, md_h, tc_new_gcdshift). The survivors are OBSERVE
3/3 and VALIDATE 3/5 (md_e acc-v, md_f acc+(v-1), md_g acc*(v+1)). The
required minimum of 3 validate families was met exactly.

Donor procedure.
  D1  observe with PRISTINE (3 cells per OBSERVE family);
  D2  group into provisional buckets;
  D3  enumerate every member of each bucket in the donor's own search space
      (H1 x H2 x FINAL, 151,920 programs) and certify it;
  D4  LGG over every member pair of distinct classes, keeping results with
      exactly one non-root hole;
  D5  candidate libraries UNCHANGED / MEMORISE / SCHEMA_k;
  D6  S2 paired selection, 24 cells, escrow 250,000.

Results.
  Three certified classes: sum*last (8 members), prod-first (4), sumsq+first
  (3 members, including the compensating `acc - v*v` form).
  D4 candidate schemas: exactly one, (acc + {H}).
  D6 mean costs:
    UNCHANGED  116,364
    MEMORISE   119,064   saving   -2,700
    SCHEMA_0    22,291   saving   94,073   lower95 64,604
  ENDOGENOUS_ABSTRACTION = YES. Selected library sha 4fed9489d956...

HOSTILE NOTES ON S3
  (a) Under keyed ordering, the donor happened to observe the ADDITIVE
      sum-of-squares form directly. A counterfactual LGG over the observed
      bodies alone ALSO yields (acc + {H}). S1's compensating-factorisation
      collapse was present (the member set contains `acc - v*v`) but was NOT
      load-bearing in this run. This run does not show that S1 was necessary.
  (b) The derived library's content is IDENTICAL to the positive control's.
      What is established is that the donor DERIVED it, not that it found a
      different abstraction.

------------------------------------------------------------------------------
6. S4 -- TRANSPLANT (AMENDMENT 14)
------------------------------------------------------------------------------

Arms: DERIVED (the treatment), PRISTINE, SHAM_0..7 (6 random H2 classes plus 1
random one-hole schema each, hashed before the donor ran), and two
sensitivity-only arms, POSITIVE_CONTROL (acc + {H}) and MEMORISE.
N = 16 recipients per arm per family; escrow 250,000; up to 5 hits, each judged
by the hostile tribunal on held-out, stress-length-200, counterexample and
metamorphic tests.

Difficulty control S7 (DERIVED excluded): the admitted families were 5
unseen-body (negmod, sumdiv, sumgcdlast, summod, sumscaled) and 2 related.

  family (Q = qualified/16, E = censored effort)   DERIVED     PRISTINE
  tc_new_negmod_plus_first   acc-(v%last)          16 / 34,180   1 / 249,680
  tc_new_sumdiv_plus_first   acc+(v//last)         16 / 29,189   1 / 247,872
  tc_new_sumgcdlast_minus_first                    16 / 24,049   0 / 250,000
  tc_new_summod_times_first                        16 / 29,792   0 / 250,000
  tc_new_sumscaled_minus_last acc+(v*last)         16 / 36,074   0 / 250,000
  tc_rel_sum_minus_last                            16 / 26,157  16 /  61,584
  tc_rel_sumsq_times_first                         16 / 27,899  16 /  72,933

Pooled paired saving vs PRISTINE: 167,818 charges per recipient
(SE 7,887; lower95 154,844; 112 cells). False-positive hits: 0.39%.

Shams. Seven shams scored 0/16 on every unseen-body family. SHAM_7 drew
(acc - {H}) and solved negmod 16/16 at 34,294 and sumdiv 16/16 at 32,688.
DERIVED beat it on both, the first narrowly (34,180 vs 34,294).

Criterion.
  1 expressive equivalence                          PASS
  2 improves vs PRISTINE                            PASS
  3 beats the sham distribution                     PASS
  4 hostile evaluation (tribunal-qualified only)    PASS
  5 false-positive acceleration <= 25%              PASS (0.39%)
  6 multiple families                               PASS (7)
  7 >= 2 families whose mechanism is absent from
    the observed classes                            PASS (see caveat)
  8 no donor state crosses                          PASS
  ABSTRACTION_TRANSPLANT = YES.

Economics: meta-cost 6,916,141 charges; break-even 41.2 descendants, against a
preregistered horizon of 64. Economically positive.

OBSERVATIONS
  - negmod, a NON-additive body, was solved by the additive schema through
    negation conjugation: (0, acc + (v % last), first - acc). This is exactly
    the equivalence S1 formalised, found by the recipient's own search.
  - On related families MEMORISE is far cheaper (1,452 vs 26,157), and it fails
    every unseen-body family. The memorise-vs-generalise trade-off, measured.
  - CONDITION 7 CAVEAT: the frozen test compares whole-program classes, so even
    the two RELATED families counted as "unobserved" (their finals differ).
    That test is weaker than intended. The substantive version -- unseen-body
    families alone -- holds with 5 of 5.

INCIDENT. The first S4 attempt crashed in the pilot: Recipient.fresh() wipes a
GLOBAL marker directory, and parallel workers deleted each other's
workspaces. No result was written. The fix gives each worker its own marker
directory. S4 was then resumed from the FROZEN S3 artifact with every library
hash re-verified; nothing was re-derived.

DISCLOSURE. After all designs were frozen, two single "smoke" recipients were
run for plumbing. They are not observations.

------------------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

DOES: in this engine, an improver mechanically derived a reusable abstraction
from its own certified successes and selected it by a fair paired rule on data
it never observed. Inherited through a clean membrane, that abstraction
transferred to five unseen-body families under hostile evaluation, beating
PRISTINE and a preregistered sham distribution, with positive economics.
This answers the operator's open clause for this engine.

DOES NOT:
  - establish recursion: this is one bounded meta-generation, and the derived
    abstraction was never used to derive the next one;
  - establish that S1 was necessary (see 5a);
  - generalise beyond a synthetic DSL of integer folds with one schema grammar;
  - escape designer influence: the seat designed the catalog. Validation
    included an out-of-grammar additive family (md_f), and additive families
    dominate the transfer set (4/6 unseen-body; the 2 non-additive ones were
    admitted only because negmod proved solvable and gcdshift was rejected);
  - avoid positive-control influence on admission: the positive control
    certified family admission (declared; the bias acts on every arm alike);
  - provide a globally sound semantic quotient -- GLOBAL identity FAILED;
  - count as Campaign 1 evidence, or say anything about LLM substrates.

------------------------------------------------------------------------------
8. DECISION FOR THE OPERATOR (seat's lean in brackets)
------------------------------------------------------------------------------

  D1 Accept S4 = YES under the caveats above.              [lean: accept]
  D2 A second meta-generation: can the derived schema, once inherited, help
     derive a NEW abstraction (e.g. a mul- or sub-shaped one) on a catalog
     where (acc + {H}) is insufficient? That is the recursion question this
     run does not touch.                                    [lean: yes, under a
                                                             new amendment]
  D3 A necessity test for S1: replay the donor with the observed factorisation
     forced to the compensating form (a preregistered adversarial observation
     set), with and without member enumeration.            [lean: yes, cheap]
  D4 Acceleration: both backends reproduce the M4 reference exactly on M4
     (Azure: pool, 480/480 rows; RunPod fasteval: 1,157,192 evaluations,
     ~12x end to end). The cloud canaries await credentials (RunPod key;
     az login), expected cost about $0.15 and $0.20. If they pass,
     certification sweeps would be the first accelerated workload.
  D5 Or stop here: the engine line has answered its question.

------------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------------------------

  Q1 The derived schema equals the positive control, and the catalog was
     designed by someone who knew that schema works. Is "derived" meaningful,
     or is the catalog a funnel toward (acc + {H})? What catalog would
     distinguish the two?
  Q2 OBSERVE contained two additive families. Would ANY LGG procedure fail to
     produce (acc + {H}) from sum and sum-of-squares? If not, is S3 a test of
     the donor or of the observation set?
  Q3 Condition 7 turned out weaker than intended. Does passing it on
     unseen-body families alone suffice, or should the whole criterion be
     re-declared before any further use?
  Q4 Global identity failed three times. Is campaign-local certification a
     principled narrowing or a retreat that hides unsoundness? Name a
     certificate failure that would have mattered here.
  Q5 Is the S7 admission rule (the positive control may certify solvability) a
     bias toward the treatment? Would you reverse any verdict because of it?

------------------------------------------------------------------------------
10. ARTIFACTS (branch aphrodite/engine-2026-09-21, roles/Aphrodite/engine/)
------------------------------------------------------------------------------

  AMENDMENT_12_2026-09-23.md (+ ADDENDUM_1, _2, _3)   287d208ea .. a2ba379aa
  AMENDMENT_13_2026-09-23.md, AMENDMENT_14_2026-09-23.md        4a6bbf55d
  S1_GATE_RUN1_2026-09-23.json, _RUN2_, S1_GATE_RUN3_2026-09-24.json
  diagnostics/S1_MEMBER_SPACE_AUDIT_2026-09-24.json               390727442
  S1_LOCAL_GATE_2026-09-24.json, S2_GATE_2026-09-23.json          52dad4db7
  T3D_QUALIFICATION_2026-09-23.json, T3D_SHAMS_2026-09-23.json,
  S3_ARTIFACT_2026-09-23.json                                     52dad4db7
  S4_RESULTS_2026-09-23.json, S4_RUN_2026-09-24.log               65edc1251
  journal/2026-09-23.md (09-23 and 09-24, every error in full)
  Acceleration: aphrodite/accel-azure-cpu-2026-09-23 @ 96503f81a,
                aphrodite/accel-runpod-2026-09-23 @ bfbc5859e

+==============================================================================+
|  END OF REVIEW 11. "Not worth continuing" is a first-class answer: the       |
|  engine line may have answered its question, and a reviewer who thinks the   |
|  catalog funnels the result should say so plainly.                           |
+==============================================================================+
