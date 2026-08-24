# CYCLE 147-K — TERMINAL: ADVANCE. The effect is real, and it is 14 constants.

**Two things happened this pass.** My 146-J leak diagnosis was falsified, the actual defect turned
out to be a variance error rather than a leak, and once corrected the headline **survives**. This is
the first positive result this line has produced, and per the pass instruction it is stated plainly
rather than hedged.

## First: 146-J's diagnosis was wrong, and verifying it was the right first move

146-J claimed the shuffled-label null leaked through availability structure, with ties breaking
alphabetically toward `conductor`. Three checks, before implementing the specified repair:

1. **Alphabetical tie-breaking is not what happens.** The shuffled model picks `rank` most often
   (48,612 of 132,009), not `conductor`, and within-set score spread is nonzero (median 0.006).
2. **The shuffle worked correctly.** Shuffled marginal rates land at 0.4846–0.5150 and within-group
   spreads at 0.0053–0.0083 — sampling noise, exactly as a working shuffle should produce.
3. **So where did +0.087 come from?** Per group: the shuffled model picks **one invariant for every
   set in a group, in 14 of 14 groups**, with large bidirectional deltas —
   `(torsion, abs_diff_le_3)` picks rank and scores 0.9601 against 0.4635 chance;
   `(rank, abs_diff_le_3)` picks conductor and scores **0.0000** against 0.4668.

Had I implemented the prescribed stratified permutation without checking, I would have "fixed" a
defect that did not exist.

## The actual defect: the wrong unit of analysis

**Every model here emits a constant ranking per cell.** M1 emits 4 distinct orderings (one per
availability subset); M4 emits 14. So the number of *independent decisions* is the cell count, not
the test-set count. Scoring 132,009 sets and computing a binomial SE as though they were independent
trials inflates apparent precision:

    naive per-set SE   0.00109
    clustered SE       0.06228        inflation factor 57x

That is the same error class as measuring over the wrong population, applied to the variance instead
of the mean. 146-J's "seventy-fold clearance" was an artifact of that inflation.

## Corrected result — and it survives

    C1 one ranking per cell : M4 14 cells | M1 4 cells                  PASS
    C2 cell count > 3       : 14                                        PASS
    C3 null at zero under the correct unit : |+0.0873| vs 3*SE 0.2452   PASS
    C4 loud parse accounting: 0 dropped of 469,513                      PASS

    M4 state-conditioned  acc 0.8056  chance 0.5029  per-cell delta +0.3027 (SE 0.0417, 14 cells)
    M1 context-free       acc 0.5617  chance 0.5029  per-cell delta +0.0588 (SE 0.0462,  4 cells)
    NULL shuffled         acc 0.5903  chance 0.5029  per-cell delta +0.0873 (SE 0.0817, 14 cells)

    D = M4 - M1 = +0.24395 | clustered SE 0.06228 | bar 2*SEc = 0.12456 | CLEARS at 3.9 SE

**C3 is the vindication of the correction.** Under the correct unit the null sits comfortably within
3 clustered SE of zero — so 146-J's 0.5903 was never a leak, it was 14 coin flips landing unevenly.
The harness was sound; the statistics were not.

## What this positive actually says, stated at its true size

**Conditioning on state reorders the available actions, and the reordering is real.** It survives a
clustered SE and a null that lands at zero. That is the navigation hypothesis confirmed — in its
weakest form.

And the form matters:

- The "representation" is a **14-entry lookup table**: (parent_invariant × relation) → which
  invariant to try next. Going from 4 constants to 14 buys +0.244.
- The action is **feature selection** — which invariant to measure next — over a 4-element space.
  Not a mathematical transformation. Nothing here says the substrate can navigate transformation
  space.
- 14 clusters is a small denominator. The effect is at 3.9 SE, solid but not overwhelming, and with
  13 degrees of freedom a t-reference is more honest than a normal one (p ≈ 0.002).

So: **state-dependent navigational information exists in this corpus, and it amounts to fourteen
constants over a four-way measurement choice.** Both halves of that sentence are the result.

## Self-identified weaknesses

- The clustered SE combines M4 and M1 as `sqrt(se4² + se1²)`, treating them as independent when they
  share test data. A properly paired cluster analysis would be tighter and is the right next step;
  the current form is conservative in the numerator but not principled.
- 14 clusters. Cluster-robust SEs are known to be unreliable below roughly 30–50 clusters, so the SE
  is itself noisy and the 3.9 figure should not be quoted to two decimals.
- M1 has 4 cells and M4 has 14, so the two deltas are estimated on different cluster counts. That
  asymmetry is not handled by the simple combination used here.
- 12 of 165 batches, ~7% of the corpus.
- The discriminative restriction excluded 207,629 of 469,513 sets. Directional information in the
  all-hold and all-fail extremes remains untested.
- Nothing establishes that this transfers. The cells were both fit and evaluated on the same 14
  (parent, relation) combinations; held-out *relations* were never tested, and that is the first
  thing that could kill this.

## Falsifier

A paired cluster analysis that drops D below 2 SE; a held-out-relation split showing the 14 cells do
not transfer to unseen relations; or evidence that the (parent, relation) cell is itself an artifact
of how h4 was generated rather than a property of the mathematics.

## Terminal

**CYCLE 147-K: ADVANCE.** The first positive on this line. Conditioning on state usefully reorders
actions, at a scale of fourteen constants, for a measurement-selection action space. The next cycle
must test whether it **transfers** — hold out relations rather than parents — because a lookup table
that only works on the cells it was fit to is not navigation.
