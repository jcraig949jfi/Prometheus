+==============================================================================+
| APHRODITE LOCAL ENGINE -- SLICE 4: REPRESENTATIONAL SEARCH LEVERAGE          |
| Equal expressive power, unequal search cost                                  |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-22                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  STRUCTURAL_SEARCH_LEVERAGE = YES, with one weak family and one      |
|          statistic that points the other way. Read sections 2 and 3.         |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. THE GATE THAT MAKES THIS SLICE DIFFERENT
------------------------------------------------------------------------------

Expressivity equivalence was certified BEFORE any search: 13,824 output
comparisons over macro expansions, ZERO mismatches. The macro expands into
G4, and the ORGAN arm falls back to the full G4 enumeration, so the two arms
can ultimately express EXACTLY the same programs. Capability available only to
ORGAN cannot occur by construction. Every difference below is search cost.

    space sizes    ORGAN coordinate   1,215,360 candidates
                   SCRATCH (G4)     226,381,140 candidates      (186x)
    escrow         1,500,000 charges per recipient, identical across arms
    recipients     16 per arm per family, paired development entropy
    run            1047 s

Families selected mechanically, lexicographically, before any result:
gcd_times_first, prod_minus_first, sum_minus_first. sum_plus_last was
REJECTED by T3 because the organ's own hole completes it.

------------------------------------------------------------------------------
1. RESULTS, PER FAMILY, NOT AGGREGATED
------------------------------------------------------------------------------

M2 = fraction reaching a tribunal-qualified solution within the fixed escrow.
CENSORED MEAN = mean charges with every failure counted at the full escrow
(the honest unconditional effort statistic).
COND. MEDIAN = median charges among successes ONLY (see section 3).

  gcd_times_first     M2      censored mean   cond. median   false pos.
    ORGAN            9/16        890,709         609,303        7/16
    SCRATCH          3/16      1,224,383           3,246        7/16
    SHAM             9/16      1,350,708       1,222,569        5/16

  prod_minus_first    M2      censored mean   cond. median   false pos.
    ORGAN           16/16        281,215         115,493        0/16
    SCRATCH          5/16      1,047,735          37,285        0/16
    SHAM             2/16      1,480,374       1,342,996        0/16

  sum_minus_first     M2      censored mean   cond. median   false pos.
    ORGAN           16/16        432,820         510,704        0/16
    SCRATCH          5/16      1,061,017          85,164        1/16
    SHAM             3/16      1,457,545       1,242,067        1/16

  POSITIVE qualified on all three families.

ORGAN has the higher discovery probability on ALL THREE families and the
lower unconditional search effort on ALL THREE (3.7x, 2.5x, and 1.4x).

------------------------------------------------------------------------------
2. THE ATTRIBUTION IS DECISIVE
------------------------------------------------------------------------------

Where did each arm's successes actually come from?

    ORGAN successes found INSIDE the macro coordinate:  9/9, 16/16, 16/16
    SHAM successes that came from the G4 FALLBACK:      9/9,  2/2,  3/3

EVERY ORGAN success came from the macro. EVERY SHAM success came from the
fallback, after the sham macro had been exhausted for 1,215,360 charges
without producing anything. The sham macro -- the organ with its body's second
argument mechanically rewritten from `v` to `acc`, so the loop ignores the
sequence -- contributes nothing, and its cost shows up directly in SHAM's
censored means (the worst in every family).

So the advantage is attributable to THIS macro's semantics, not to carrying a
macro. That is the comparison the ruling asked for, and it separates cleanly.

------------------------------------------------------------------------------
3. THE STATISTIC THAT POINTS THE OTHER WAY, AND WHY
------------------------------------------------------------------------------

SCRATCH's median charges AMONG ITS SUCCESSES are LOWER than ORGAN's in all
three families -- 3,246 vs 609,303; 37,285 vs 115,493; 85,164 vs 510,704.

Read naively, that says SCRATCH is the cheaper searcher. It is survivorship.
SCRATCH succeeds only when its randomised enumeration happens to strike the
witness early; on the 11 to 13 recipients per family where it does not, it
burns the entire 1.5M escrow and finds nothing. Conditioning on success
selects exactly the lucky runs. The censored means in section 1, which count
those failures at full cost, reverse the ordering in every family.

I report both because the ruling requires heterogeneity to stay visible, and
because "median charges among winners" is the statistic most likely to be
quoted by someone arguing the opposite conclusion.

------------------------------------------------------------------------------
4. THE WEAK FAMILY, NAMED
------------------------------------------------------------------------------

gcd_times_first is the family where the claim is weakest, on three counts:
  - ORGAN reaches only 9/16, against 16/16 on the other two;
  - SHAM TIES ORGAN on M2 (9/16 vs 9/16). It loses on censored effort
    (1,350,708 vs 890,709) and every one of its successes came from the
    fallback, but on the headline discovery-probability number it does not
    separate;
  - false positives dominate: 7/16 for ORGAN and 7/16 for SCRATCH. With four
    development instances, gcd tasks admit spurious exact fits -- a program
    that happens to reproduce four gcd answers and then fails the tribunal.

If the claim rested on this family alone it would be a fossil, not a result.
It rests on three, and the other two separate by 8x and 5x in M2.

------------------------------------------------------------------------------
5. DID SCRATCH REDISCOVER THE FOLD? SOMETIMES.
------------------------------------------------------------------------------

M8, measured mechanically (a loop whose body consumes v and threads acc):

    ORGAN    16/16, 16/16, 16/16      (by construction -- it is the macro)
    SCRATCH   5/16,  5/16,  6/16
    SHAM      9/16,  2/16,  4/16

SCRATCH independently synthesised fold-equivalent structure in roughly a
third of its recipients, and those are precisely the ones that qualified.
The organ is not supplying something unreachable; it is supplying something
findable that is usually not found in budget. That is the definition of a
search coordinate, and it is why the expressivity certificate matters.

------------------------------------------------------------------------------
6. VERDICT
------------------------------------------------------------------------------

    STRUCTURAL_SEARCH_LEVERAGE = YES

Reproducible across three previously unseen families, at certified equal
expressive power, with the sham control failing to reproduce it and all
ORGAN successes traced to the macro coordinate itself.

The supported claim, at exactly the size the ruling permits:

  A structure discovered by evolution was extracted, transplanted into fresh
  recipients, and made subsequent discovery of independently specified
  capabilities more efficient WITHOUT expanding what those recipients could
  ultimately express.

This is transferable improvement of search representation. It is NOT
recursive self-improvement, and I will not describe it as such. The mutation
generator, evaluator, selection algorithm and evolve() were untouched.

QUALIFICATIONS THAT TRAVEL WITH THE CLAIM: one of three families is weak
(section 4); the conditional-median statistic points the other way (section
3); the space ratio is 186x by design, so the magnitude of the effect is a
property of my grammar rather than a natural constant; and the whole thing is
a toy whose "capabilities" are four-line arithmetic programs.

------------------------------------------------------------------------------
7. THE TIER-3 GATE
------------------------------------------------------------------------------

The ruling says recommend Tier 3 ONLY if structural search leverage is
demonstrated. It is. So I recommend it -- narrowly, and with the design
constraint that makes it interpretable stated up front:

The five conditions are already the right ones. The one I would emphasise is
the fifth: the evaluator, tribunal, escrow and harness MUST remain outside the
mutable artifact. Slice 4 is only interpretable because the tribunal could not
be reached by anything the recipients did; a Tier-3 experiment where the
improver can touch its own evaluator measures nothing at all.

I would add one condition of my own, learned here: a Tier-3 claim needs an
EXPRESSIVITY-EQUIVALENCE CERTIFICATE for improvement machinery, exactly as
this slice needed one for programs. Otherwise "the evolved improver is better"
will be indistinguishable from "the evolved improver can do things the
baseline improver could not attempt", which is capability supply again, and
slice 3 already showed how easily that masquerades as leverage.

I am NOT implementing any of it. Tier 3 remains forbidden until authorised.

------------------------------------------------------------------------------
8. DEFECTS AND DISCLOSURES
------------------------------------------------------------------------------

D1 The evaluator recompiled every expression string on every call, which
   would have made the run take hours. Compiled code objects are now cached.
   Pure performance: candidate order, semantics and charge accounting are
   unchanged, because charges count CANDIDATES, not evals. Disclosed because
   the change was made after the amendment was frozen.
D2 DEV_PER_RECIPIENT = 4 was fixed in the run script, not in AMENDMENT 8,
   which specified the entropy rule but not the count. Declared in the script
   before execution; disclosed here because it materially affects the false
   positive rate (section 4).
D3 The deterministic witness ranks reported before the run favour SCRATCH on
   two of three families (14,507 vs 15,947 and 1,597 vs 4,477). The ORGAN
   advantage therefore comes from space density under randomised search, not
   from a conveniently placed witness. I stated this before seeing results.

------------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is the censored mean the right unconditional statistic, or does counting
    failures at exactly the escrow cap flatter ORGAN? What would you use?
Q2. The 186x space ratio is my design choice. Is any leverage result from a
    hand-sized grammar informative about real systems, or does it only show
    that smaller haystacks are easier to search?
Q3. SHAM ties ORGAN on M2 for gcd_times_first while losing on effort and
    attribution. Is one tied family enough to withhold the YES?
Q4. SCRATCH rediscovered fold structure in a third of recipients. Does that
    strengthen the result (the organ is a coordinate, not a capability) or
    weaken it (the thing transplanted was findable anyway)?
Q5. I recommended Tier 3 and added a condition. Am I recommending it because
    the evidence supports it, or because it is the interesting next thing?

------------------------------------------------------------------------------
10. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  026ccc847  AMENDMENT 8, frozen before certificate and search
  roles/Aphrodite/engine/EXPRESSIVITY_CERTIFICATE_2026-09-22.json
  roles/Aphrodite/engine/SLICE4_RESULTS_2026-09-22.json
  roles/Aphrodite/engine/{basis_v4.py, certify_expressivity.py, run_slice4.py}
  organ 5488abb9f6354f02..., unchanged and not re-extracted

+==============================================================================+
| END. "Your winners-only median says SCRATCH is cheaper and you explained     |
| it away" is a first-class answer, as is "a 186x space ratio you chose        |
| yourself is not a discovery about representation."                           |
+==============================================================================+
