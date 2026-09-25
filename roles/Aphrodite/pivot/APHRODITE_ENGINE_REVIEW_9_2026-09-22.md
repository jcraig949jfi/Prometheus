+==============================================================================+
| APHRODITE LOCAL ENGINE -- TIER 3B: SEMANTIC IDENTITY, EVALUATOR POWER,       |
| AND THE REPLACEMENT TEST                                                     |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-22                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO                             |
|          Conditions 4 and 5 fail. Condition 7 PASSES, which matters.         |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. VERDICT
------------------------------------------------------------------------------

    BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO

The evolved library produced one large, clean, sham-beating advantage on one
family and essentially nothing on the other four. The criterion requires the
advantage to hold across more than one independent family (condition 4) and
to include evidence on more than one structurally novel unseen-body family
(condition 5). It does not.

This is NOT a repeat of Tier 3A. The control is valid this time, the
comparison is against a preregistered distribution of eight shams, and the
result is a real measurement rather than an invalidated one.

------------------------------------------------------------------------------
1. RESULTS (primary = censored mean effort over ALL 16 recipients)
------------------------------------------------------------------------------

  family                      EVOLVED    PRISTINE   SHAM med   sham range
  mt_gcd_plus_first   [T]     235,017    218,860    239,458    187,687-239,970
  mt_gcdsq_plus_last  [U]     250,000    250,000    250,000    218,776-250,000
  mt_sum_minus_last   [T]         989     46,105     58,497     26,847- 75,776
  mt_sumdivlast_...   [U]     250,000    250,000    250,000    247,823-250,000
  mt_summodlast_...   [U]     245,306    250,000    250,000    250,000-250,000
  [T] = transfer family (body kind seen by the donor)
  [U] = structurally novel, unseen body kind

  qualified / 16              EVOLVED    PRISTINE   SHAM median
  mt_gcd_plus_first              1/16       2/16       1
  mt_gcdsq_plus_last             0/16       0/16       0
  mt_sum_minus_last             16/16      16/16      16
  mt_sumdivlast_...              0/16       0/16       0
  mt_summodlast_...              1/16       0/16       0

------------------------------------------------------------------------------
2. THE ONE REAL RESULT
------------------------------------------------------------------------------

On mt_sum_minus_last the evolved library reaches a tribunal-qualified
solution in 989 charges against PRISTINE's 46,105 -- a 47x reduction -- and
it beats EVERY member of the sham distribution, including the best sham at
26,847. All 16 recipients qualify in every arm, so this is a pure search-cost
effect at identical discovery probability, with ZERO false positives in any
arm on that family.

That is a clean demonstration of transferable search-representation value at
certified equal expressive power. It is also, precisely, the family whose
body class the library contains: `(v + acc)` is one of the five semantic
classes the donor abstracted. The advantage appears where the structure
matches and nowhere else.

------------------------------------------------------------------------------
3. WHY IT FAILS CONDITIONS 4 AND 5
------------------------------------------------------------------------------

The library's five semantic classes are:
    (acc * v), (acc - (v * v)), (v + (v * acc)), (v + acc),
    (v + math.gcd(abs(v), abs(v)))          [ = v + v, ignores the accumulator ]

There is NO gcd-accumulating body among them, and no body of the
`acc + (v % last)` or `acc + (v // last)` shape. So:

  - on the OTHER transfer family, mt_gcd_plus_first, the evolved library is
    WORSE than pristine (235,017 vs 218,860) and worse on discovery
    probability (1/16 vs 2/16). It pays for scanning 2,520 specialised
    candidates that cannot express the target. The donor's "gcd success" was
    recorded as `(v + math.gcd(abs(acc), abs(acc)))` -- which is v + acc, a
    SUM body. The donor never actually abstracted gcd machinery.
  - on two of the three unseen-body families, nothing solves anything: 0/16
    in every arm, all at the 250,000 ceiling. The families are genuinely
    hard for this grammar and the comparison is uninformative there.
  - on the third, mt_summodlast_times_first, EVOLVED qualifies 1/16 against
    PRISTINE's 0/16 and beats all shams. ONE recipient out of sixteen is a
    fossil, not evidence, and I am not counting it as a second family.

Condition 4 (advantage across more than one independent family): FAILS.
Condition 5 (evidence on more than one unseen-body family): FAILS.

------------------------------------------------------------------------------
4. CONDITION 7 PASSES -- THE TIER-3A WORRY DID NOT MATERIALISE
------------------------------------------------------------------------------

FALSE_POSITIVE_ACCELERATION, false positives per recipient before the first
qualified solution:

  family                      EVOLVED   PRISTINE   ratio   limit
  mt_gcd_plus_first             4.688      4.562    1.03    1.25
  mt_gcdsq_plus_last            5.000      5.000    1.00    1.25
  mt_sum_minus_last             0.000      0.000     n/a    1.25
  mt_sumdivlast_...             1.688      1.500    1.13    1.25
  mt_summodlast_...             0.625      0.625    1.00    1.25

No family exceeds the declared 25% threshold. The evolved machinery does NOT
buy its (small) advantage by reaching wrong programs faster. Tier 3A's
headline worry -- improved search accelerating false confidence -- is
measured here and is absent.

BUT THE ABSOLUTE NUMBERS ARE THE STORY. On mt_gcd_plus_first BOTH arms burn
~4.6 false positives per recipient out of a cap of 5. The development
batteries still admit false programs in bulk, for both arms equally.

------------------------------------------------------------------------------
5. THE DISCRIMINATION GUARANTEE DID NOT TRANSFER, EXACTLY AS DISCLOSED
------------------------------------------------------------------------------

Before the run I qualified every family's false-positive basin to ZERO and
stated plainly that the guarantee was nominal: it was established on ONE
greedy-selected instance set, while recipients draw fresh instances of the
qualified SIZE, because the ruling requires independent development entropy
per recipient.

Section 4 shows what that concession cost. Basin zero on the qualified set,
4.688 false positives per recipient on fresh draws of the same size. The
qualification procedure sized the battery correctly and did NOT make an
arbitrary draw discriminating.

A future run wanting a real guarantee must either qualify the basin for the
DRAW RULE rather than one draw -- e.g. by requiring basin zero across many
independent draws of a candidate size -- or accept identical batteries across
recipients and give up independent development entropy. That is a genuine
design tension the ruling's two requirements create, and it should be
resolved explicitly rather than by my choosing one side quietly.

------------------------------------------------------------------------------
6. ECONOMICS (separate from the causal result, as required)
------------------------------------------------------------------------------

    meta-search cost                    503,914 charges
    mean saved per recipient/family       6,730 charges
        (mt_sum_minus_last +45,116; mt_summodlast +4,694;
         mt_gcd_plus_first -16,158; the two dead families 0)
    BREAK-EVEN DESCENDANTS                   74.9
    PREREGISTERED HORIZON                      64

    ECONOMIC VERDICT AT THE DECLARED HORIZON: NEGATIVE.

The library does not repay its own meta-search within the horizon declared
before the run. Economic negativity does not invalidate the causal result and
this mechanism is NOT called self-amplifying.

------------------------------------------------------------------------------
7. FOUR APPARATUS DEFECTS FOUND DURING THIS SLICE
------------------------------------------------------------------------------

D1 SEMANTIC IDENTITY (fixed, and it worked). The donor's eight raw successes
   collapsed to FIVE semantic classes -- `(v * math.gcd(abs(acc), abs(acc)))`
   and `(acc * v)` merged. Tier 3A would have carried both as distinct
   discoveries. All five Tier-3A equivalences pass as regression fixtures,
   including gcd(acc, v+acc) == gcd(acc, v), whose canonical ASTs differ.
D2 REPRESENTATIVE SELECTION, found by the new fixtures: the picker preferred
   `(acc + math.gcd(abs(v), abs(v)))` over `(acc + v)` because it sorted by
   canonical form then source string. The library would have carried baroque
   spellings again.
D3 UNBOUNDED COMPILE CACHE, introduced by my own slice-4 "pure performance"
   optimisation: the G4 fallback mints a distinct expression string per
   candidate, so the cache grew without limit (1.65 GB observed). Bounded now.
   Cost wall-clock only; charges count candidates, not evals.
D4 SEARCH/ARTIFACT CONFORMANCE DIVERGENCE -- the one that actually mattered.
   `run_program` returns None past the declared 10^40 ceiling; the EMITTED
   artifact had no such guard, so a pow-bodied program grew its accumulator
   across 200 tribunal elements into unbounded big-int arithmetic and HUNG
   the run: 1,829 s of CPU with no output. This is the fourth instance in
   this program of the same failure family -- implementation not matching
   declared semantics. Repaired so the artifact returns "overflow" exactly
   where the searcher returns None; the pathological case went from a hang to
   0.04 s, and mt_gcd_plus_first reproduced its pre-repair numbers to one
   decimal place, so no measurement moved.

PROCESS FAILURES, disclosed: TaskStop does not kill the detached Python
child. Two orphans survived earlier stops, one running 18 hours at 3.8 GB.
I twice reported runs as stopped when they were not, and once attributed a
speed-up to killing them when the real cause was D4. Every wall-clock figure
I reported for slice 4 and Tier 3A is contaminated; every charge-based
endpoint is not, and those are the primary endpoints in both amendments.

------------------------------------------------------------------------------
8. WHAT THIS ESTABLISHES
------------------------------------------------------------------------------

ESTABLISHED:
  - a transplanted proposal library can cut search cost 47x on a family whose
    structure it contains, beating all eight preregistered shams, at
    certified equal expressive power and with zero false positives
  - the advantage does NOT come from false-positive acceleration (condition 7)
  - semantic identity is implementable and immediately caught two defects
  - the Tier-3A control failure cannot recur: shams are drawn as semantic
    classes under frozen seeds before the artifact exists

NOT ESTABLISHED:
  - bounded recursive self-improvement. Conditions 4 and 5 fail.
  - any generalisation to structure the donor did not abstract. The evolved
    library helps where it matches and hurts where it does not.
  - economic viability at the declared horizon.

------------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is a 47x effect on one family plus a 1/16 fossil on another genuinely a
    NO, or am I over-applying a criterion written to prevent exactly the
    opposite error?
Q2. Two of three unseen-body families were solved by NOBODY (0/16 in ten
    arms). Should a family that no arm can solve count as evidence against
    condition 5, or as a family that should have been excluded by a
    difficulty control before the run?
Q3. The donor abstracted `v + gcd(acc, acc)` -- a sum body -- as its gcd-family
    success. Its own development battery could not tell the difference. Is
    that a defect, or the honest behaviour of a system whose evaluator is
    weaker than its search?
Q4. Section 5: the ruling requires both basin-zero discrimination and
    independent per-recipient development entropy, and those two conflict.
    Which should give way?
Q5. Four defects in one slice, all found by the apparatus rather than by
    review. Is that evidence the apparatus is working, or that it is too
    complex to trust?

------------------------------------------------------------------------------
10. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  169dc6c67  AMENDMENT 10, frozen before every step
  38bf8f7a4  semantic-identity layer + regression fixtures
  roles/Aphrodite/engine/TIER3B_QUALIFICATION_2026-09-22.json
  roles/Aphrodite/engine/TIER3B_ARTIFACT_2026-09-22.json  (1bbbd985ab05...)
  roles/Aphrodite/engine/TIER3B_RESULTS_2026-09-22.json
  roles/Aphrodite/engine/{semantics.py, tier3b.py, qualify_tier3b.py,
                          run_tier3b.py, meta_tribunal.py}
  Tier 3A: NOT POOLED, retained as exploratory fossils

+==============================================================================+
| END. "One family is a fossil, exactly as your own criterion says" is the     |
| correct summary. "The unseen families were too hard to be informative --     |
| your design could not have passed condition 5" is a first-class answer.      |
+==============================================================================+
