+==============================================================================+
| APHRODITE LOCAL ENGINE -- TIER 3C: SEMANTIC ABSTRACTION AS IMPROVER HEREDITY |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-22                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO                             |
|          The donor never formed an abstraction. Two SHAMS did, and they      |
|          solved both unseen-body families 16/16. Read section 3.             |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. VERDICT AND THE SHAPE OF THE RESULT
------------------------------------------------------------------------------

    BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO
    (conditions 2, 3, 6 and 7 fail; conditions 1, 4, 5, 8 pass)

The evolved library produced the largest local effect this program has
measured -- 345x on the related family, beating all eight shams -- and did
nothing whatever on the two unseen-body families. It failed for a reason that
is now identified precisely, and the control distribution accidentally
demonstrated the mechanism it failed to build.

------------------------------------------------------------------------------
1. RESULTS
------------------------------------------------------------------------------

  family                          EVOLVED   PRISTINE  SHAM med   best sham
  tc_rel_sum_minus_first  [REL]     167.6    57,923    51,489     21,258
  tc_new_sumgcdlast_...   [NEW]   249,431   245,890   250,000     30,634
  tc_new_summod_times_... [NEW]   250,000   250,000   250,000     46,661

  qualified / 16                  EVOLVED   PRISTINE  SHAM_0   SHAM_5  others
  tc_rel_sum_minus_first            16/16     16/16    16/16    16/16   16/16
  tc_new_sumgcdlast_...              1/16      2/16    16/16    16/16    0/16
  tc_new_summod_times_...            0/16      0/16    16/16    16/16    0/16

  FALSE POSITIVES PER RECIPIENT: 0 vs 0 vs 0, ON EVERY FAMILY, EVERY ARM.

------------------------------------------------------------------------------
2. THE APPARATUS FINALLY WORKS
------------------------------------------------------------------------------

Two numbers deserve more attention than the verdict.

ZERO FALSE POSITIVES, everywhere. Tier 3A burned 14 of 16 recipients on
tribunal-rejected programs; Tier 3B averaged 4.688 per recipient on its gcd
family. Tier 3C records ZERO across three families and ten arms. The
difference is the GENERATOR qualification: instead of qualifying one sample
and hoping, each family's generator was calibrated over 200 independent draws
per candidate size, and the development battery was sized until the 95% upper
bound on surviving wrong semantic classes fell below 0.05. It then REJECTED
THREE OF NINE FAMILIES -- including both gcd-final families, which are exactly
the ones that poisoned Tier 3B. The qualifier refused the families that had
previously produced the false positives, and the false positives disappeared.

THE CONFORMANCE GATE WAS GREEN BEFORE THE RUN: 900 program shapes x 24 input
configurations = 21,600 differential comparisons between the search evaluator
and the emitted artifact evaluator, zero mismatches, covering overflow,
division by zero, modulo zero, out-of-range exponents and sequence lengths 1
to 200. This is the first slice in this program that began from a verified
agreement between its two evaluators. Nothing hung, nothing diverged, and
memory stayed at 45 MB against 1.65 GB in the previous slice.

------------------------------------------------------------------------------
3. THE SHAMS PERFORMED THE EXPERIMENT THE DONOR COULD NOT
------------------------------------------------------------------------------

Each sham carries six random semantic classes plus ONE randomly drawn schema.
What they drew decided everything:

    SHAM_0   schema (acc + {H})   covers all three unseen bodies   16/16, 16/16
    SHAM_5   schema (acc + {H})   covers all three unseen bodies   16/16, 16/16
    SHAM_1   schema (acc - {H})   covers none                       0/16,  0/16
    SHAM_2   schema (acc * {H})   covers none                       0/16,  0/16
    EVOLVED  no schema at all     covers none                       1/16,  0/16
    PRISTINE no schema at all     covers none                       2/16,  0/16

This is a natural experiment I did not design and could not have faked: the
hole-bearing schema is the causal ingredient. A library carrying (acc + {H})
solves families whose bodies NOBODY had ever seen, at 16/16, while every
library without it fails. The abstraction hypothesis Tier 3C was built to
test is strongly supported -- by the control distribution, because the
treatment arm never constructed a schema.

------------------------------------------------------------------------------
4. WHY THE DONOR FORMED NO ABSTRACTION
------------------------------------------------------------------------------

Its two observed semantic classes were:

    (acc - (v * v))        and        (v + acc)

Anti-unification of those yields nothing: different operator AND different
arguments. So no schema, and `abstract` degenerated into `memorise`.

The reason it observed `acc - v^2` is the interesting part. For the
sum-of-squares family the donor did NOT find body `acc + v*v`. It found body
`acc - v*v` paired with final `first - acc`: it accumulated the NEGATIVE sum
of squares and negated at the end. Semantically the identical program, a
different factorisation.

  THE BODY IS NOT AN INVARIANT UNIT. A program decomposes into body x final
  in many equivalent ways, and the body can absorb a sign, a scale or an
  offset that its final compensates. Abstracting over one component is
  unreliable when that component's form is contingent on its partner.

That is a real limitation of abstraction-from-self-observation, and no
improvement to the anti-unification procedure fixes it. The fix is to
abstract over the WHOLE PROGRAM's semantic class and then factor, or to
canonicalise the body/final split before abstraction -- neither of which this
apparatus does.

------------------------------------------------------------------------------
5. A DESIGN ERROR THAT MADE THE DONOR'S CHOICE MEANINGLESS
------------------------------------------------------------------------------

Candidate libraries were scored: unchanged 46,646, memorise 13,479, abstract
51,018. The donor selected `memorise`.

That selection carries NO information. With no schema formed, `memorise` and
`abstract` have IDENTICAL CONTENT -- yet they scored 13,479 and 51,018, a 3.8x
spread, because I seeded each arm's search with a string containing the
library's NAME. Different names, different shuffles, different costs.

Compounding it, the VALIDATE set had collapsed to ONE family
(md_d_gcd_plus_last failed generator qualification), so three repetitions on a
single family had to overcome that noise. They could not.

The cross-validation introduced in AMENDMENT 11 s4a -- the entire mechanism by
which an abstraction could out-score memorisation -- was therefore never
functional. I predicted this collapse in writing before the results arrived,
which is worth exactly as much as it sounds: I saw it and ran anyway rather
than re-designing mid-slice.

------------------------------------------------------------------------------
6. WHAT EVOLVED DID ACHIEVE
------------------------------------------------------------------------------

On tc_rel_sum_minus_first: 167.6 charges against PRISTINE's 57,923 -- a 345x
reduction, larger than Tier 3B's 47x -- and it beats every sham, the best of
which needs 21,258. 16/16 qualified, zero false positives, solution class
add(acc, v), which is exactly the class the donor memorised.

This replicates TRANSFERABLE_SEARCH_LEVERAGE = YES_LOCAL with a bigger effect
and a cleaner apparatus. It remains local: the advantage appears where the
memorised class matches and nowhere else.

------------------------------------------------------------------------------
7. CONDITION-BY-CONDITION
------------------------------------------------------------------------------

  1 expressive equivalence                  PASS (all arms desugar to G4,
                                                  all retain G4 fallback)
  2 improves qualified discovery vs PRISTINE PARTIAL -- 345x on one family,
                                                  tie or worse on two
  3 beats the sham distribution             FAIL on both unseen families
                                                  (SHAM_0/5 at 16/16 vs 1/16,
                                                  0/16); PASS on the related
                                                  family
  4 survives hostile evaluation             PASS
  5 no false-positive acceleration          PASS -- zero everywhere
  6 useful across multiple families         FAIL -- one family
  7 >= 2 families not memorised             FAIL -- the single success is
                                                  exactly the memorised class
  8 no donor state or evaluator information PASS

------------------------------------------------------------------------------
8. ECONOMICS -- POSITIVE, FOR THE FIRST TIME, AND IT CHANGES NOTHING
------------------------------------------------------------------------------

    meta-search cost                620,709 charges
    mean saved per recipient/family  18,072 charges
        (+57,756 related; -3,541 one unseen; 0 the other)
    BREAK-EVEN DESCENDANTS             34.3
    PREREGISTERED HORIZON                64

The horizon EXCEEDS break-even, so the mechanism pays for itself within the
declared descendant budget -- the first time in this program. Per AMENDMENT 11
s9 that permits the economics to be called positive, and it does NOT permit
the process to be called self-amplifying, because the causal criterion failed.
An economically positive mechanism that does not generalise is a cheap
memory, not an improving improver.

------------------------------------------------------------------------------
9. WHAT A CORRECTED RUN NEEDS (specified, not performed)
------------------------------------------------------------------------------

  R1 PAIRED SEEDS across candidate libraries and across arms. Identical
     content must produce identical cost; that it did not here invalidated
     the donor's selection.
  R2 ABSTRACT OVER WHOLE-PROGRAM SEMANTIC CLASSES, or canonicalise the
     body/final factorisation before anti-unifying. Section 4 shows the body
     alone is not a stable unit.
  R3 A VALIDATE SET THAT SURVIVES QUALIFICATION. Declare more validate
     families than needed, so that exclusions leave enough to measure with.
  R4 SCHEMA-BEARING LIBRARIES SHOULD BE AN ARM, not only a sham draw. The
     strongest evidence in this slice came from controls; that should be a
     treatment next time.
  R5 UNSEEN-BODY FAMILIES THAT SOME ARM CAN SOLVE. Two of three were solved
     only by the two lucky shams; a difficulty control would have caught that
     before the run.

------------------------------------------------------------------------------
10. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Section 3: is evidence from a randomly-drawn control legitimate support
    for the abstraction hypothesis, or does it only license a new experiment
    in which the schema is the treatment?
Q2. The donor found `acc - v^2 / first - acc` instead of `acc + v^2 /
    acc + first`. Is the body/final factorisation problem specific to this
    grammar, or does every attempt to abstract a component of a program hit
    it?
Q3. I foresaw the VALIDATE collapse and the likely outcome, wrote it down,
    and ran anyway. Was that discipline (no mid-slice redesign) or waste
    (a run whose result I had already predicted)?
Q4. Zero false positives across three families and ten arms, after two slices
    where they dominated. Is generator qualification the right general fix,
    or did I merely exclude the hard families?
Q5. Economics is positive and the causal claim fails. Which of those does a
    reader remember, and how should a report be written so it is the second?

------------------------------------------------------------------------------
11. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  13fd1d9b9  AMENDMENT 11 + conformance gate GREEN
  roles/Aphrodite/engine/CONFORMANCE_GATE_2026-09-22.json
  roles/Aphrodite/engine/TIER3C_ARTIFACT_2026-09-22.json  (2849244e1637...)
  roles/Aphrodite/engine/TIER3C_RESULTS_2026-09-22.json
  roles/Aphrodite/engine/{semantics.py, tier3c.py, conformance.py,
                          run_tier3c.py}
  Tier 3A and 3B: NOT POOLED. Slice-4 and Tier-3A wall-clock: CONTAMINATED.

+==============================================================================+
| END. "Your shams ran the experiment and your treatment did not" is the       |
| correct summary. "Make the schema an arm and run it properly" is a           |
| first-class answer, as is "stop -- the body/final problem means this         |
| abstraction target was never well-defined."                                  |
+==============================================================================+
