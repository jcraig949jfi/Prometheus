# RB-2 -- QUALIFICATION STRICTNESS SWEEP AND TASK-WORLD AUDIT (threads T04, T05, T09)

Cheap, autonomous, read-only on frozen artifacts. Estimated 4-8 hours. Read RB-00 first.

WHY
  K1 showed the qualification regime admits almost only commutative, bounded-growth,
  non-degenerate folds, i.e. G1's own span:
    - mul dies of overflow at stress length 200;
    - fdiv/mod/powr die of degenerate 0/1 dynamics with init in {0, 1};
    - gcd dies at Q2 discriminability, and its survivors are mostly |acc + v|.
  Genuinely non-additive qualified tasks: 7 per 10,500 draws (K7). The minimal-criterion
  literature (Soros et al. 2016; PRIOR_ART_C s8 E8) says both extremes of strictness
  stagnate. Measure where we are.

GOAL
  A table: tribunal variant x stratum ->
    - admissible count;
    - genuinely non-G1 count (extensional, per K7);
    - Q2 pass rate;
    - PRISTINE and L1 solvability;
    - the distinct non-G1 schema families present (by RB-1 ruler if available, else K7
      extensional test).

VARIANTS (at least; add others with a reason)
  V0  the current tribunal (baseline; must reproduce K1's numbers).
  V1  drop the metamorphic permutation test.
  V2  replace it with an order-sensitive metamorphic relation valid for ALL folds:
      prefix-extension consistency (answer on xs+[y] equals the fold continued from the
      answer state). This needs the witness, so it is a generator-side check.
  V3  stress length 60 instead of 200.
  V4  modular arithmetic ceiling (values mod a large prime) instead of None at CEIL.
  V5  widened init space: {0, 1, 2, first, last}.
  V6  V1+V3+V5 combined.
  For each, state what junk the variant would now admit, e.g. leaky or constant tasks.
  A variant that admits junk is not a fix.

STEPS
  1. Copy spikes/k1_supply_census.py to rb2/. Parameterise the tribunal preconditions.
     Reproduce V0 exactly.
  2. Run the variants at N = 1,500 per stratum (about 40 s each).
  3. For admissible non-G1 survivors, run Q2 (a17.qualify) and the K7 extensional test.
  4. For the best 1-2 variants, run K2-style solvability.
  5. Also compute the p(1-p) learnability window (T09): the fraction of survivors with
     PRISTINE solve rate in (0, 1).

DELIVERABLES
  science/frontier/rb2/ (scripts, RB2_RESULTS.json, TASK_WORLD_AUDIT.md), ending with a
  recommendation of which task world (if any) is worth a preregistered campaign.
  Replacing the tribunal is an OPERATOR decision (synthesis s14), so recommend and do not
  adopt.
