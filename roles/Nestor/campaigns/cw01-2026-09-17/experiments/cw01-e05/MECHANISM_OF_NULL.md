# cw01-e05 — mechanism of the NULL

Descriptive reading of committed results only. **No criterion is changed here.** The
verdict contract `c80b5bfd…` was frozen before the first organism was evaluated, and
the freeze rule stands: any criterion change would void the attempt and open a new
`attempt_id`. This document explains a NULL; it does not relitigate it.

## What failed

    beats_best_single             4/4   PASS
    m3_interaction_positive       4/4   PASS    DiD mean +30.89 pp
    superadditivity_clears_null   2/4   FAIL
    ablation_all_load_bearing     2/4   FAIL
    replication                         FAIL  -> NULL

## Finding 1 — the two failures are one fact, not two

Superadditivity and full load-bearing fail in **exactly the same two replicates**:

    attempt          sa_pct   clears   load   did_points
    cw01-e05-a01   +12.7863     True    3/3     +19.4280
    cw01-e05-r02   +28.1670     True    3/3     +65.1260
    cw01-e05-r03    -4.8236    False    2/3     +21.4111
    cw01-e05-r04    +0.0747    False    1/3     +17.6031

This is not two independent misses that happened to land together. Both quantities
measure the same underlying property from different directions: superadditivity asks
whether the mixture exceeds the sum of its parts, targeted ablation asks whether
removing a member costs more than that member is worth alone. Where the best set does
not compose, neither appears. The correlation is perfect across the four replicates
and should be read as one result.

## Finding 2 — the failure is the drawn world, not a noisier measurement

    null band widths : 15.638, 17.546, 13.454, 13.407   (spread 4.14)
    effect sizes     : +12.786, +28.167, -4.824, +0.075  (spread 32.99)

The null bands are comparable across replicates; the effects are not. The failing
replicates did not fail because their measurement was noisy enough to swallow a real
effect — they failed because the effect is absent or negative in those worlds. In
r03 and r04 the best three-component set is measurably **sub-additive**: mixture
information 150.00 vs additive prediction 156.32, and 116.09 vs 118.23.

That outcome was deliberately kept reachable. `WORLD.json` records it as the honest
null: *"a set of weak specialists that each handle their own share independently is a
PARTITION, and its value is the sum of its members."* Carrying one component, none,
or all are all inside the search space. Engineering the partition away would have
rigged the experiment. In half the drawn worlds, the partition is what evolution found.

## Finding 3 — why the interaction survived when superadditivity did not

BEST-set normalised superadditivity, by composition law:

    attempt        conjunctive   disjunctive
    cw01-e05-a01        +8.433       -22.351
    cw01-e05-r02       +29.586       -23.904
    cw01-e05-r03        -4.046       -26.559
    cw01-e05-r04        -1.817       -23.177

The disjunctive term is **stable across every world** (−22.4 to −26.6, spread 4.2)
because it is dominated by coverage overlap, which is an arithmetic property of the
capability structure rather than of composition. The conjunctive term swings by more
than 33 points across worlds.

So a *within-set, across-law* contrast is robust to the world draw, while a *raw
magnitude* is not. That is why the difference-in-differences held 4/4 while raw
superadditivity held 2/4 — and it is retrospective vindication of the D040/D041
corrections, which replaced two across-law magnitude criteria with the DiD for
reasons that were then purely methodological.

**Design lesson for e06–e10:** prefer statistics that difference out the world draw.
A quantity measured within one drawn world and compared across a controlled
intervention replicates; the same quantity compared across independently drawn worlds
inherits their variance.

## What survives the NULL

Two claims hold in **every** replicate and must not be buried by the disposition:

1. **Mixtures beat the best single component, 4/4**, by large margins (1.881 vs 0.795;
   1.599 vs 0.682; 2.166 vs 0.972; 1.675 vs 0.735).
2. **The composition law benefits a well-chosen set more than a poor one, 4/4**
   (+19.43, +65.13, +21.41, +17.60 points).

What fails is the strictly stronger claim that the mixture exceeds the **sum of its
parts**. Carrying a good set is worth far more than carrying the best single
component — but in half these worlds that value is *accumulation*, not *composition*.
Those are different claims and the distinction is the result.

## Supplementary evidence from the independent replication lane

**Outside the frozen verdict.** The contract binds four replicates and the disposition
is NULL on those four. Everything in this section is additional evidence gathered by
an independent executor under the *unchanged* contract (branch
`nestor/e05-replica-2026-09-18`). It does not alter the disposition and was not
allowed to.

**Exact reconstruction.** An executor working from committed artifacts alone
reproduced the canonical run across **381 leaf comparisons with 0 divergences** —
every statistic, null bound, seed block, cell and disposition field, bit-for-bit. The
experimental object is genuinely portable and self-describing in place.

**Finding 1 strengthens.** With eight further seeds (r05–r12), `superadditivity_clears_null`
and `ablation_all_load_bearing` agree in **12 of 12 replicates, without a single
exception** — they pass together in a01, r02, r06, r07, r08, r09, r12 and fail
together in r03, r04, r05, r10, r11. The claim that these are one fact rather than two
now rests on twelve worlds, not four.

**Finding 3 is corrected, and this correction matters.** The M3 interaction held 4/4
in the canonical lane, and I described it as holding in every replicate. Across all
twelve it holds **11/12**: r10 returns `did_points` **−14.45**. The composition law
does not benefit a well-chosen set more than a poor one in *every* world — only in
almost all of them. The canonical 4/4 was a small-sample accident, and stating it as
universal would have been an overclaim that four replicates could not have caught.

Combined tallies across all twelve replicates:

    beats_best_single             12/12
    m3_interaction_positive       11/12   (r10: -14.45)
    superadditivity_clears_null    7/12
    ablation_all_load_bearing      7/12

The 7/12 split does not change the disposition, and it is still too small a sample to
be a rate. It does say the partition outcome is common rather than exceptional.

**One anomaly, not investigated.** r11 records `n_load_bearing = 0` of 3 carried, while
its targeted ablation cost is 57.94 against a random-removal sham of 36.53 — a large
targeted effect with no component individually clearing its own solo value. The
threshold is contract-frozen, so this is recorded and left alone rather than probed.

## Limitations

- An 8-gene real-valued inclusion vector, not a rich program.
- Four replicates. The 2/4 split is a small-sample statement about how often these
  worlds compose; it is not an estimate of that rate.
- Per-replicate BEST/WORST sets differ ([0,2,4], [1,2,6], [0,4,5], [0,3,7]) because
  each `attempt_id` draws its own latent world. Independent replicates are independent
  worlds. The contract's BEST/WORST bind a01 only.
- `conjunctive_fraction` was not swept in this attempt. WORLD.json declares it a swept
  parameter; the sweep is expansion, not part of the minimal form.
- Whether a world composes may be predictable from its capability structure before
  running it. That is a hypothesis this attempt did not test, and testing it would
  require a new pre-registration rather than an amendment.
