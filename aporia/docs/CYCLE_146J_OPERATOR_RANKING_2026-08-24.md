# CYCLE 146-J — TERMINAL: REDESIGN. The controls caught my harness before it published a huge false result.

**Question:** given a parent relation and the invariants it could be extended to, does the recorded
representation rank the extensions that HOLD above those that FAIL — better than chance and better
than embarrassing baselines? First direct measurement of I(Z; next useful action) this loop has run.

## The contamination check reshaped the question, and that is the pass's first real output

Run before anything else, over 1,408,539 extension attempts:

    holds rate by extended invariant : conductor .4454 | tamagawa .5694 | torsion .5559 | rank .6352
    holds rate by parent invariant   : rank .4665 | torsion .5617 | tamagawa .5887 | conductor .6096
    holds rate by relation           : equal_mod_2 .6249 | divides .6121 | abs_diff_le_3 .4122 | equal .1230

No invariant dominates to triviality, so the test is informative. But the check surfaced something
that changes what must be measured: **within a sibling set, `relation`, `parent_invariant`,
`knot_invariant` and both objects are CONSTANT — only the extended invariant varies.** Relation is
the strongest predictor in the corpus (a 0.50 spread) and it *cannot affect ranking at all*.

So a context-free model that memorises the global per-invariant hold rate emits **the same ranking
for every state in the corpus**. It can score well on outcome prediction while carrying zero
navigational information. The question that separates a taxonomy from a navigation coordinate
system is therefore not I(Z; outcome) but:

> Does conditioning on the state *reorder* the available actions, and does that reordering improve
> which action you would pick?

The headline was preregistered as **M4 − M1** (state-conditioned minus context-free), never M4 − chance.

## What the action actually is — stated so it scopes every claim

h4's "operation" is *which ec_invariant to test this relation against next*. That is **feature
selection** — choosing a different projection of the same object — **not** a mathematical
transformation of it. The edge is a genuine (state, action, outcome) triple, but the action space is
a 4-element choice of measurement. Nothing here tests ranking over mathematical transformations, and
"edge" is not permitted to do rhetorical work the data does not support.

## The number I am not reporting as a result

    matched chance on test sets : 0.5029  (n = 132,009)
    M1 context-free   0.5617    M2 parent  0.6457    M3 relation  0.7971
    M4 full-cell      0.8056    M5 +knot   0.8465
    D = M4 - M1 = +0.24395 | paired McNemar SE 0.00178 | 2*SE 0.00356

D clears its materiality bar by seventy-fold. Reported naively this reads as *the substrate has
powerful state-dependent navigational information*. **Two of four controls failed, so it is not
reportable.**

## Control C3 failed: the shuffled-label null scored 0.5903 against chance 0.5029

A model trained on shuffled labels must land at matched chance. It landed 0.087 above it — more than
twenty SE. The harness leaks, and the channel is now isolated:

    every set has k = 3, and the available invariants are exactly "all except the parent"
    => AVAILABILITY IS IDENTICAL TO THE PARENT INVARIANT

    availability set                                  n         mean hold fraction
    (conductor, tamagawa, torsion)   [parent=rank]     146,918   0.4665
    (conductor, rank, tamagawa)      [parent=torsion]  116,567   0.5617
    (conductor, rank, torsion)       [parent=tamagawa] 113,906   0.5887
    (rank, tamagawa, torsion)        [parent=conductor] 92,122   0.6096

A **within-set** shuffle preserves each set's hold *count*. So cell rates still encode "sets with
this parent have more holds," and because availability is determined by the parent, each invariant's
shuffled rate still reflects the hold fraction of the contexts it co-occurs with. The null did not
perturb the axis the statistic varies on — which is the loop's own standing doctrine on nulls, and I
violated it.

**The correct null:** permute labels *across* sets within the same (parent, relation, n_holding)
stratum, breaking the invariant↔outcome association while preserving availability and hold-count
structure. Until that null lands at chance, no accuracy figure from this harness means anything.

## Control C4 was mis-specified by me

C4 required the context-free model to emit exactly one ordering. It emitted four. That is **not**
state-dependence — it is the same global order restricted to four different available subsets, since
the parent invariant is always excluded. The control should have verified that M1's ordering is a
*restriction of a single global order*, not that it is literally identical. As written it cannot
pass on this data, which makes it theatre of the kind the external reviews flagged.

## Verdict

**VACUOUS** on the preregistered branch (C = 2 of 4), terminal **REDESIGN**.

The apparatus did exactly what it was built for. A +0.244 effect at seventy times its own SE, with
M5 at 0.846 against chance 0.503, was sitting there as the most impressive-looking result this line
has produced — and two controls stopped it. That is the third consecutive pass where a control, not
inspection, caught the defect.

## What must change before the question can be answered

1. **Stratified conditional permutation** as the null, as specified above.
2. **Restate C4** as "M1's ordering is a restriction of one global order across all availability
   subsets," which is the property actually intended.
3. **Add a confound control**: since availability ≡ parent, any apparent state-conditioning may be
   availability structure rather than knowledge. Compare M4 against a model given *only* the
   availability set — if they tie, the extra state buys nothing.
4. Only then read M4 − M1.

## Self-identified weaknesses

- 12 of 165 batches. Wider than 145-I's 6, still 7% of the corpus.
- The action space is 4 invariants and every set is k=3, so the ranking problem is a 3-way choice —
  small, and the chance baseline sits near 0.50 by construction.
- The discriminative restriction dropped 207,629 of 469,513 sets (125,653 all-hold, 81,976 all-fail).
  That is 44% of the data excluded for a principled reason, but it selects toward the ambiguous
  middle, and whether directional information lives disproportionately in the excluded extremes was
  not tested.
- Parse accounting was clean (0 drops of 469,513), so the 145-I silent-exclusion failure did not
  recur — but that is one pass of evidence, not a fixed process.
- No claim whatever is made about whether the substrate has navigational information. The pass
  establishes only that the harness cannot currently answer it.

## Falsifier

A stratified conditional null that lands at chance while M4 − M1 survives, which would restore the
headline; or evidence that the leak channel is not availability-driven, which would move the
diagnosis elsewhere.

## Terminal

**CYCLE 146-J: REDESIGN.** The measurement is well-posed, the data supports it, and the harness is
not yet trustworthy enough to read. No accuracy figure from this pass should be cited.
