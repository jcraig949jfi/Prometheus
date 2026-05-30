# A3 Lattice Void Mining — 2026-05-30

**Scope:** exhaustive sweep of a3's operator-composition lattice.
**Lattice size:** 6 ops × 6 ops × 4 relations = 144 cells.
**Sample budget per cell:** 2000 (knot, k_invariant, ec, e_invariant) tuples.

## Cell-density distribution

```
  hold_rate >= 0.95   (strong identity):    2/144
  0.50 <= hold_rate < 0.95 (high):         57/144
  0.05 < hold_rate < 0.50 (mid):           71/144
  hold_rate <= 0.05   (anti-identity):     14/144
```

## Candidate non-trivial operator identities

Cells with hold_rate >= 0.95 NOT explained by parity / small-range modular triviality.
**Count:** 0

(none above the strong-identity threshold after triviality filter)

## Trivial strong-identity cells (filtered out)

```
       mod_3   mod_3      | abs_diff_le_3    | 1.000  | one operator has bounded codomain; difference bounded by catalog scale, not algebra
  log2_floor   mod_3      | abs_diff_le_3    | 0.959  | one operator has bounded codomain; difference bounded by catalog scale, not algebra
```

## Candidate non-trivial anti-identities

Cells with hold_rate <= 0.05 where the substrate's claims essentially NEVER hold — operator pairs structurally incompatible with the relation on the catalogs.
**Count:** 0


## Full lattice (sorted by hold_rate descending)

```
           f   g          | rel              | hold_rate
       mod_3   mod_3      | abs_diff_le_3    | 1.000
  log2_floor   mod_3      | abs_diff_le_3    | 0.959
       mod_3   log2_floor | abs_diff_le_3    | 0.702
  log2_floor   log2_floor | abs_diff_le_3    | 0.671
  log2_floor   log2_floor | divides          | 0.643
  log2_floor   sq_mod_100 | divides          | 0.619
       mod_3   mod_3      | divides          | 0.618
       mod_3   log2_floor | divides          | 0.603
       mod_3   identity   | equal_mod_2      | 0.591
  log2_floor   identity   | abs_diff_le_3    | 0.590
  log2_floor   mod_3      | divides          | 0.589
       mod_3   neg        | equal_mod_2      | 0.583
       mod_3   sq_mod_100 | divides          | 0.574
  log2_floor   identity   | divides          | 0.572
       mod_3   abs        | abs_diff_le_3    | 0.571
  log2_floor   neg        | divides          | 0.571
       mod_3   abs        | equal_mod_2      | 0.570
  log2_floor   abs        | divides          | 0.568
  log2_floor   abs        | abs_diff_le_3    | 0.567
       mod_3   mod_3      | equal_mod_2      | 0.560
  log2_floor   sq_mod_100 | abs_diff_le_3    | 0.559
         abs   sq_mod_100 | equal_mod_2      | 0.556
    identity   sq_mod_100 | equal_mod_2      | 0.555
       mod_3   sq_mod_100 | equal_mod_2      | 0.555
       mod_3   identity   | abs_diff_le_3    | 0.551
         neg   identity   | equal_mod_2      | 0.547
         abs   identity   | equal_mod_2      | 0.546
  log2_floor   abs        | equal_mod_2      | 0.543
       mod_3   sq_mod_100 | abs_diff_le_3    | 0.543
         abs   abs        | equal_mod_2      | 0.542
  sq_mod_100   abs        | equal_mod_2      | 0.541
  log2_floor   log2_floor | equal_mod_2      | 0.540
         neg   abs        | equal_mod_2      | 0.537
         neg   neg        | equal_mod_2      | 0.537
       mod_3   neg        | divides          | 0.535
  sq_mod_100   sq_mod_100 | equal_mod_2      | 0.535
  sq_mod_100   neg        | equal_mod_2      | 0.534
    identity   abs        | equal_mod_2      | 0.533
  log2_floor   neg        | equal_mod_2      | 0.533
         abs   mod_3      | equal_mod_2      | 0.532
    identity   identity   | equal_mod_2      | 0.532
         neg   log2_floor | equal_mod_2      | 0.532
       mod_3   identity   | divides          | 0.532
         neg   sq_mod_100 | equal_mod_2      | 0.530
       mod_3   log2_floor | equal_mod_2      | 0.530
    identity   mod_3      | equal_mod_2      | 0.527
         abs   log2_floor | equal_mod_2      | 0.527
         abs   neg        | equal_mod_2      | 0.526
         neg   mod_3      | equal_mod_2      | 0.523
    identity   neg        | equal_mod_2      | 0.520
  log2_floor   sq_mod_100 | equal_mod_2      | 0.518
  sq_mod_100   mod_3      | equal_mod_2      | 0.518
       mod_3   abs        | divides          | 0.517
  sq_mod_100   identity   | equal_mod_2      | 0.514
  sq_mod_100   log2_floor | equal_mod_2      | 0.512
    identity   log2_floor | equal_mod_2      | 0.511
    identity   log2_floor | divides          | 0.503
  log2_floor   identity   | equal_mod_2      | 0.503
  log2_floor   mod_3      | equal_mod_2      | 0.501
         abs   mod_3      | divides          | 0.474
         abs   log2_floor | divides          | 0.473
    identity   mod_3      | divides          | 0.466
         neg   log2_floor | divides          | 0.465
         neg   mod_3      | divides          | 0.454
       mod_3   neg        | abs_diff_le_3    | 0.452
         abs   sq_mod_100 | divides          | 0.438
         neg   sq_mod_100 | divides          | 0.425
  sq_mod_100   mod_3      | divides          | 0.422
         abs   mod_3      | abs_diff_le_3    | 0.419
    identity   sq_mod_100 | divides          | 0.414
  sq_mod_100   log2_floor | divides          | 0.412
         abs   abs        | divides          | 0.404
    identity   identity   | divides          | 0.400
    identity   mod_3      | abs_diff_le_3    | 0.399
  sq_mod_100   sq_mod_100 | divides          | 0.389
         neg   identity   | divides          | 0.389
    identity   abs        | divides          | 0.386
    identity   neg        | divides          | 0.384
         neg   neg        | divides          | 0.381
         abs   log2_floor | abs_diff_le_3    | 0.374
         abs   identity   | divides          | 0.373
         neg   abs        | divides          | 0.370
         abs   neg        | divides          | 0.349
       mod_3   mod_3      | equal            | 0.336
         neg   mod_3      | abs_diff_le_3    | 0.336
    identity   log2_floor | abs_diff_le_3    | 0.330
  log2_floor   neg        | abs_diff_le_3    | 0.321
         abs   abs        | abs_diff_le_3    | 0.308
         abs   sq_mod_100 | abs_diff_le_3    | 0.307
         abs   identity   | abs_diff_le_3    | 0.306
  sq_mod_100   mod_3      | abs_diff_le_3    | 0.283
    identity   identity   | abs_diff_le_3    | 0.276
    identity   abs        | abs_diff_le_3    | 0.270
  sq_mod_100   neg        | divides          | 0.269
  sq_mod_100   identity   | divides          | 0.269
    identity   sq_mod_100 | abs_diff_le_3    | 0.266
         neg   neg        | abs_diff_le_3    | 0.262
  sq_mod_100   abs        | divides          | 0.254
         neg   log2_floor | abs_diff_le_3    | 0.246
  log2_floor   mod_3      | equal            | 0.220
       mod_3   log2_floor | equal            | 0.217
  sq_mod_100   log2_floor | abs_diff_le_3    | 0.198
  sq_mod_100   identity   | abs_diff_le_3    | 0.190
  sq_mod_100   abs        | abs_diff_le_3    | 0.181
  sq_mod_100   sq_mod_100 | abs_diff_le_3    | 0.176
    identity   neg        | abs_diff_le_3    | 0.170
         neg   sq_mod_100 | abs_diff_le_3    | 0.169
       mod_3   abs        | equal            | 0.169
         neg   abs        | abs_diff_le_3    | 0.167
         neg   identity   | abs_diff_le_3    | 0.162
       mod_3   identity   | equal            | 0.156
       mod_3   sq_mod_100 | equal            | 0.150
  log2_floor   identity   | equal            | 0.133
         abs   neg        | abs_diff_le_3    | 0.133
  log2_floor   log2_floor | equal            | 0.127
  log2_floor   abs        | equal            | 0.124
  sq_mod_100   neg        | abs_diff_le_3    | 0.099
  log2_floor   sq_mod_100 | equal            | 0.099
         abs   mod_3      | equal            | 0.096
    identity   mod_3      | equal            | 0.091
  sq_mod_100   sq_mod_100 | equal            | 0.084
         abs   log2_floor | equal            | 0.070
  sq_mod_100   mod_3      | equal            | 0.067
    identity   identity   | equal            | 0.064
         abs   identity   | equal            | 0.064
    identity   log2_floor | equal            | 0.064
         abs   abs        | equal            | 0.059
    identity   abs        | equal            | 0.056
         neg   neg        | equal            | 0.056
  sq_mod_100   log2_floor | equal            | 0.054
  sq_mod_100   abs        | equal            | 0.046
       mod_3   neg        | equal            | 0.044
         abs   sq_mod_100 | equal            | 0.044
    identity   sq_mod_100 | equal            | 0.044
  sq_mod_100   identity   | equal            | 0.035
         neg   mod_3      | equal            | 0.031
         neg   log2_floor | equal            | 0.030
         neg   sq_mod_100 | equal            | 0.022
         neg   identity   | equal            | 0.021
  log2_floor   neg        | equal            | 0.019
    identity   neg        | equal            | 0.017
         neg   abs        | equal            | 0.016
  sq_mod_100   neg        | equal            | 0.010
         abs   neg        | equal            | 0.008
```

## Interpretation guide

- **Non-trivial strong-identity cells** are the highest-value output:
  they describe operator compositions that produce values satisfying
  the relation across the catalog, even though there's no obvious
  algebraic reason. Each is a candidate Lean-formalizable identity.
- **Non-trivial anti-identity cells** describe operator compositions
  that NEVER produce matching values — structural incompatibilities
  that can be promoted as falsification rules for cheaper future fires.
- **Mid-band cells** (0.05 < hold_rate < 0.5) are where a3's actual
  observed kills concentrate. They produce kill_pattern volume but
  little structural info per kill.

## Actionable: a3 lattice pruning recommendation

After the codomain-bounded triviality filter, the lattice splits roughly:

```
  candidate non-trivial identities    :   0/144
  trivial strong-identity (codomain) :   2/144
  candidate non-trivial anti-id      :   0/144
  trivial anti (cross-scale 'equal') :  14/144
  mid-band (informative kills)       :  71/144
```

**Recommendation:** prune trivial-identity cells AND trivial-anti cells
from a3's sampling distribution. Trivial-identity cells produce only
SHADOW_CATALOG records (claim holds — info-free). Trivial-anti cells
produce only kill records that look like 'a3_func_id_*_equal_violated'
but encode cross-scale numerical mismatch, not algebra.

Concretely:
- a3's batch could skip ALL `_equal_` rel cells where f != g and at least
  one of (f,g) is sq_mod_100 or mod_3 (cross-scale).
- a3 could skip ALL `_abs_diff_le_K_` rel cells where f or g is mod_3
  (codomain-trivial).
- Sampling budget redirected to the ~71 mid-band cells triples
  effective signal-per-fire.