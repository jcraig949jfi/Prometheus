# Kill-Topography — Real Findings
**Date:** 2026-05-29
**Predecessor:** pivot/kill_topography_2026-05-29.md (raw scan)
**Scope:** 200K kills across 7 recent batches, 5 attribution axes.

## Headline

The kill-topography pass produced three substantive findings and one
methodological correction. The corpus's killing is mostly
catalog-uniform statistical failure (low directional information),
with one notable exception (a3) that encodes a real operator-lattice
artifact.

## Finding 1 — EC conductor topography is flat (negative)

Kill rate across EC conductor bands exactly mirrors the catalog's
volume distribution.

```
band      kills%   cat%   kills/cat
<50        0.19    0.20      0.95
<100       0.17    0.20      0.85
<500       2.90    2.90      1.00
<1K        4.86    4.80      1.01
<5K       40.36   40.40      1.00
<10K      51.50   51.50      1.00
```

Where the substrate seems to "concentrate kills at high conductor" is
just catalog volume. No structural concentration. The earlier raw
report flagged `('equal', 'cond<10K')` as +231 std-residuals
overrepresented — but the expected-value used uniform-cell expectation,
not catalog-weighted. After correction: zero anomaly.

**Implication:** EC conductor is NOT a useful coordinate for finding
where substrate hypotheses structurally break. Substrate killing here
is volume-driven, not curvature-driven.

## Finding 2 — a3 emits a real operator-composition lattice

Of the substrate's gens, a3 is the only one with a true
multi-coordinate kill-pattern structure. It tests
`(op_A ∘ op_B → relation)` and emits 143 distinct kill_patterns
across a `~9 operators × ~9 operators × 4 relations` lattice
(~324 possible cells, ~143 observed, ~44% lattice coverage).

Operators in lattice: identity, abs, neg, log2_floor, sq_mod_100, mod_3
Relations: equal, abs_diff_le_3, divides, equal_mod_2

Kills per cell are remarkably uniform (~70-100 each), suggesting
systematic exhaustive probing rather than random failure.

**The voids in a3's lattice ARE the math.** Empty cells = operator
pairs that DO satisfy the relation across the catalog =
candidate invariants. Per feedback_failure_signal_vector_field,
voids in the kill-lattice encode hidden algebraic structure.

This is the single richest substrate-internal artifact in the
corpus. It deserves an explicit downstream pass — extract the
empty cells, verify they're actually consistent (not just unsampled),
promote consistent ones as candidate invariants.

## Finding 3 — h2 is an opaque-kill black hole (substrate bug)

h2 emits 43.68% of all kills (87K records), and ALL of them have
the same kill_pattern: `h2_method_triangulated_reject`. Zero
internal differentiation. h2 is a "rejected by triangulation"
oracle — it tells you the kill happened but nothing about WHERE
in the claim-space the failure points.

This is the largest information-loss hole in the substrate. Until
h2 breaks its kill into subclasses (which method triangulated
which way), 44% of the corpus's kill volume is opaque to the
Learner. h2 should be refactored to emit named-witness kill_patterns
matching the structure already present in f2/g4/a3.

## Finding 4 — methodological correction to the topography script

My initial mechanism classifier had a regex gap that lumped 62.85%
of kills into "other". The actual situation was:

- f2_anti_freq_*_violated → relation_violated (regex was correct but I misread the per-gen result)
- f4_frontier_*_violated → relation_violated (same)
- a3_func_id_*_<rel>_violated → new mechanism class needed: functional_identity_violated
- a4_polyfit_r2_below_X → polyfit_r2_below_threshold
- d1_neighborhood_prediction_wrong → neighborhood_prediction_wrong
- g4_reflection_asymmetric_X → reflection_asymmetric
- g5_scale_kN_breaks_X → scale_breaks
- h2_method_triangulated_reject → method_triangulated_reject

**Update needed:** kill_topography.py MECHANISM_RULES should be
extended; re-run gives the true distribution. Pattern list above.

## What this means for direction

Going into this analysis I expected to find "anomalous concentrations"
and "anomalous voids" at the (mechanism × object) level. What I
found instead:

- 99% of the high-volume kill production carries low directional
  information (catalog-uniform statistical failures). The Learner
  won't extract much signal from teaching it "this EC has high
  conductor and 17 things fail at it" because EVERY high-conductor
  EC has roughly the same.
- The one place real directional signal exists is **a3's lattice
  voids** — operator pairs that consistently DON'T fail, encoding
  candidate algebraic identities.
- h2's 87K opaque kills are a substrate bug. Fixing h2 to emit
  structured kill_patterns would unlock substantially more
  Learner-usable data than building more gens.

## Recommendations

1. **Mine a3's lattice voids** — script that enumerates the
   full op×op×rel lattice, marks observed cells, identifies cells
   with anomalously low kill density. These are candidate operator
   identities. Worth a Lean autoformalization pass on the most
   robust ones.

2. **Refactor h2** to emit kill_pattern subclasses — minimum
   `h2_<method>_rejected_at_<witness>`. This single change
   converts 44% of kill volume from opaque to named.

3. **Stop adding new gens** until 1+2 are done. The Learner
   benefits more from differentiating the existing volume than
   from adding more low-volume specialized gens.

4. **Drop EC conductor as a structural axis** in future
   reports. It tracks catalog volume, not substrate behavior.
