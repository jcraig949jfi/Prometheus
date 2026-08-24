# CYCLE 148-L — TRANSFER FAILS. 147-K's positive was memorisation, and is superseded.

**The falsifier 147-K named has fired.** The 14-cell structure does not transfer to an unseen
relation. Reported as the major result it is, not softened.

## Design, and why M4 was excluded by construction

147-K's positive used cells keyed on (parent_invariant, relation), fit and evaluated on the same 14
cells. This pass holds out **relations**, leave-one-out across all four.

M4 = P(holds | parent, relation, invariant) has **no cell** for an unseen relation. Testing it on
held-out relations would measure a tautology, so it is excluded by design. The model that *can*
transfer is M2 = P(holds | parent, invariant), which pools across relations. The transfer question
is therefore exact: fitted on three relations, does parent-conditioning still beat the context-free
invariant marginal on a fourth never seen?

## Result — and it is worse than "no transfer"

    held-out abs_diff_le_3  n= 88,143  chance .4929 | M1 .3381  M2 .1770  delta -.1611
    held-out divides        n= 56,809  chance .4707 | M1 .1508  M2 .2976  delta +.1468
    held-out equal          n=  7,707  chance .3750 | M1 .4661  M2 .8516  delta +.3855
    held-out equal_mod_2    n=109,225  chance .5355 | M1 .4067  M2 .4067  delta +.0000

    M1 context-free   acc .3298  per-cell delta -.1725  clustered SE .0444  (14 cells)
    M2 parent-cond    acc .3188  per-cell delta -.1836  clustered SE .0592  (14 cells)
    NULL shuffled     acc  ----  per-cell delta -.1803  clustered SE .0587  (14 cells)

    HEADLINE  D = M2 - M1 = -0.01103 | clustered SE 0.07398 | t(13)=2.16 | bar 0.15980
    transfers? NO

Three things, in order of importance:

1. **D is negative and nowhere near its bar.** Parent-conditioning buys nothing on an unseen
   relation.
2. **Both models land exactly on the shuffled null** (−0.1725, −0.1836, −0.1803). A model trained on
   three real relations performs indistinguishably from one trained on noise. That is the cleanest
   possible statement of zero transferred information.
3. **Both score below chance** (0.33 and 0.32 against ~0.49). This is *anti*-transfer: the invariant
   rankings partially **reverse** across relations, so confidently applying what worked elsewhere is
   worse than picking at random. `abs_diff_le_3` is the extreme case — M2 scores 0.1770 against
   0.4929 chance.

## The preregistered branch fired VACUOUS, and why the substantive reading still stands

C3 required the shuffled null to sit within 3 clustered SE of **zero**. It sits at −0.1803 against a
3·SE of 0.1760 — outside by 0.004, so C = 4 of 5 and B1_VACUOUS fired.

**C3 was mis-specified for a transfer design.** In 147-K's within-relation setting a null belongs at
zero. In a transfer setting, *any* fixed ranking carried from elsewhere scores below chance when
rankings reverse — so the null's correct expectation is negative, and demanding zero tests something
that cannot hold. That is my design error, the same class as 146-J's C4.

The substantive reading survives it on independent grounds: **the headline is a paired difference**
(M2 − M1) between two models sharing the identical "fixed ranking from elsewhere" handicap, so the
null's absolute level cancels. And the models sitting *at* the null rather than above it is the
opposite of a leak signature — a leak inflates models above the null; here there is nothing to
inflate.

Applying the 145-I precedent: the branch condition is not the finding when the control underneath it
is mis-specified. **Terminal: NO_TRANSFER.**

## What this retracts

**147-K's ADVANCE is superseded.** Its +0.24395 at 3.9 clustered SE was real *within* the cells it
was fit to, and this pass shows those cells carry nothing beyond themselves. The gain lived entirely
in relation-specific constants. Fourteen numbers, memorised.

Stated without hedging: **the recorded coordinates do not carry transferable navigational
knowledge.** They carry a lookup table that works where it was fit and is actively misleading
elsewhere. That is the operator's hypothesis, confirmed on real data.

## The finding that is not just a negative

The anti-transfer is itself structure worth recording: **which invariant is most extensible depends
on the relation, and the dependence partially inverts.** `rank` is the best extension target under
some relations and among the worst under others. A navigation coordinate system would have to
represent the relation as a first-class axis rather than as context to be pooled over — which is
exactly what the corpus does *not* do, since relation is constant within a sibling set and therefore
invisible to any within-set ranking.

## Self-identified weaknesses

- Four folds and 14 cells. The `equal` fold has only 7,707 sets and the largest delta (+0.3855), so
  one fold carries much of the variance — disclosed as a risk before the run, and it materialised.
- C3's misspecification means this pass has no clean null of its own. The paired-difference argument
  is sound but a purpose-built transfer null (permute *relation labels* across sets, preserving
  parent and outcome structure) would be better and is the obvious repair.
- The four relations are not exchangeable — `equal` has a 0.123 base rate against 0.41–0.62 for the
  others — so leave-one-out treats visibly heterogeneous folds as equivalent.
- 12 of 165 batches, ~7% of the corpus.
- Scope unchanged: h4 only, feature selection over four invariants, not mathematical transformation.

## Falsifier

A purpose-built relation-permutation null that lands at the models' level, confirming this reading;
or a richer transfer model (one that represents relations by *features* rather than identity) that
beats the context-free baseline on held-out relations — which would show the failure is
representational rather than fundamental.

## Terminal

**CYCLE 148-L: NO_TRANSFER.** 147-K is superseded. The only positive this line produced was
memorisation of fourteen constants, and applying them outside their cells is worse than guessing.
