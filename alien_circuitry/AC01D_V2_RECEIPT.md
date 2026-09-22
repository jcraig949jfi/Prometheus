# AC-01D-v2 receipt: the orbit / collapse coordinate test (2026-09-13)

## Verdict

**STRONG POSITIVE. The orbit/collapse hypothesis is confirmed in its strongest form, and it retires the C5 result.**

In T_7 with rank-2 targets, after reachability is supplied, shortest generator distance D(f, t) is an exact function
of the orbit of the pair (f, t) under the exact metric symmetry (domain relabelling by S_7). That orbit is the
value-labelled contingency table J[v, b] = number of positions i with f(i) = v and t(i) = b. There are 25,382 such
tables among reachable pairs. A lookup table on them, built from FIT rows only, reproduces D exactly on every held
row, navigates at oracle cost on every held set (HC_D 0.997-0.999, zero failures, excess path 0.00), occupies
34,800 bytes (CR 30.5 against the 1,060,696-byte frozen denominator; 6.5x smaller than C5), is invariant under the
symmetry by construction, and costs 0.11 ms per decision (faster than C5's 0.19 ms; still 200x slower than a raw
transition expansion at 0.56 us).

C5 was therefore not alien circuitry. It was a symbol-bound approximation, learned from raw digits, to the exact
function on this quotient: the canonical table explains 89% of C5's predictions and 77% of what C5 added over CP,
and a depth-16 decision tree over transparent coordinates of the same table explains 96% of C5. CP rank 16 and the
evolved DSL were coarser approximations to the same object (the canonical table explains 78% and 86% of their
predictions).

## What was done, in the ruled order

**Step 1, exact symmetry.** Computed exhaustively: no non-trivial value relabelling preserves the metric (the
generator set {7-cycle, swap(0,1), collapse 0->1} has trivial conjugation stabiliser). The exact symmetry is
relabelling of positions: (f, t) -> (f o sigma, t o sigma), which commutes with left multiplication by every
generator. Verified on the D chart: 0 violations on 176,540 random relabellings; canonical classes never carry
inconsistent D. Canonical representative = columns (f(i), t(i)) sorted lexicographically by (t, f); deterministic,
target-aware only through the joint arrangement, committed before fitting (`ac01d/v2/canonical.py`). Orbit sizes
42..5040 (stabiliser = product of factorials of equal-column multiplicities). This corrects the v1 dissection,
whose "{0,1}-fixing value relabelling" symmetry test tested a non-symmetry; that finding is withdrawn in the v1
receipt.

**Step 2, transparent coordinates.** Rank, rank difference (= minimum collapse count, since each collapse lowers rank
by exactly one and the target has rank 2), count vector, block sizes, target block sizes, the 14-entry joint table
J, per-block distinct-value counts, largest class per block, straddling values and mass, pure-block values, orbit
and stabiliser size, minimal rotation mismatch, presence and counts of values 0 and 1. No D-derived quantity.

**Step 3, explanatory power** (400k FIT rows, 150k HELD_BOTH rows; `results/ac01d/v2/coordinates.json`):

```
model over canonical coordinates    true D R2   exact    | explains C5   CP    C6    C5-CP  C5-C6
linear ridge (all coords)             0.548     0.204    |   0.561      0.810 0.858  0.158  0.105
degree-2 polynomial (13 basic)        0.571     0.192    |   0.589      0.783 0.863  0.217  0.128
table on 10 orbit-summary coords      0.521     0.183    |   0.539      0.724 0.837  0.141  0.069
decision tree depth 6                 0.661     0.260    |   0.672      0.822 0.927  0.334  0.359
decision tree depth 16 (1,531 leaves) 0.989     0.942    |   0.960      0.891 0.983  0.778  0.904
table on the full joint table J       0.9925    0.998    |   0.888      0.778 0.858  0.769  0.909
reference: C5 0.988, CP 0.528, C6 0.584 on true D
```

Additivity was measured, not assumed: linear and additive-summary models reach only R^2 ~0.55, the same level as
the earlier permitted-feature model, so D is NOT additive in collapse depth and orbit summaries. The full joint
table is required; the depth-16 tree over the same coordinates recovers 94% exact-match, showing the function is
piecewise-structured in those coordinates but not low-order.

**Step 4, CP and C6.** Both are explained by the canonical coordinates at R^2 0.78-0.86 (their own R^2 on D is
0.53-0.58), so the ~0.55 shared success is the coarse part of this quotient function. C5's advantage over them is
also explained by the table (0.77 / 0.91). Layers: the backbone (what CP/C6 capture) is roughly the low-order part
that a depth-6 tree reaches; the fine coordinate C5 learned is the remainder of the same table.

**Step 5, residual.** Residual variance of the joint-table model is 0.75% of D's variance and is entirely coverage:
it is exactly zero on every orbit of size >= 420 and nonzero only on rare small orbits absent from the 400k-row fit
sample (with all FIT rows, coverage is 25,363 of 25,382 orbits). C5 explains none of the residual (R^2 -0.66).
The orbit/collapse hypothesis is complete, not merely dominant.

**Navigation** (`results/ac01d/families/V2_orbit_table.json`, frozen harness, 300 problems per set):

```
representation                  bytes    CR    HELD_STATES        HELD_TARGETS       HELD_BOTH          excess  failures
orbit table, FIT rows only     34,800   30.5   0.998 [.996,.999]  0.999 [.998,1.00]  0.998 [.997,.999]   0.00     0
orbit table, all pairs (ref.)  34,868   30.4   0.999              0.999              0.998               0.00     0
C5 medium (v1)                226,956    4.7   0.91               0.91               0.91                0.00     0
CP rank 16 (v1)                 1,708    621   0.61               0.55               0.57                4-5      0
```

Run 1 of this navigation was a bug and is preserved (`V2_orbit_table_BUG_run1_rank2_missing.json`): the table was
built from the rank >= 3 corpus and so lacked the 2,646 reachable rank-2 pairs, which are the last step before every
target; it scored exact D on every corpus row yet navigated at 5,500-7,900 transitions. The fix includes all
reachable pairs of any rank in the fit rows; the coverage rule is now stated in the code. The same corpus restriction
affected the v1 exact-table families (C3/C4, C1) but not their kills, which were on storage.

**Step 6, equivariance.** Not needed as a separate architecture: the orbit table IS the equivariant model, exact
and smaller than C5. An equivariant neural model would only be a compression of the 34.8 KB table; that is a
different question (how far the 25,382-entry function itself compresses) and is not started.

## The discovered object, named

The reachable orbits are the value-labelled 7 x 2 contingency tables of f against t with no value straddling both
target blocks (0 of 25,382 straddle; kernel refinement is exactly the no-straddle condition on this table). D is a
function on these tables. It is not a function of the block-size multisets alone: collapsing to the 80 signatures
(multiset of f-class sizes inside each target block) leaves every signature with several distinct D values, because
the generators act on specific values (the cycle rotates value labels, the swap and collapse touch values 0 and 1),
so which value carries which block matters. In group-theoretic terms the coordinate system is the double-coset
space of the right S_7 action on pairs, and the "collapse depth" of the ruling is rank(f) - 2 = number of
collapses on every shortest path; the rest of D is the cost of moving the right values into place with the cycle
and swap before each collapse, which is not additive in any of the transparent summaries tried.

## Kills checked

Primary kill conditions (transparent coordinates explain little; navigation near baseline; C5 retains unique power):
none fired. Coordinates were not added ad hoc: the joint table was on the Step-2 list before any fit.

## Scope

Same frozen scope as v1: T_7, rank-2 targets. Whether the same quotient suffices at rank-3 targets or n = 8 is a
replication, not a corollary; the no-straddle characterisation of reachability holds for any target rank, the exact
D-on-orbits property holds by the symmetry argument for any n, but the orbit count and its compressibility are
unmeasured elsewhere.

## Provenance

Commits 188306f (steps 1-5), fa4ecf2 (navigation run 1 preserved as bug), this commit (corrected navigation, orbit
identity, receipt). Results: `results/ac01d/v2/{canonical_symmetry,coordinates,orbit_identity}.json`,
`results/ac01d/families/V2_orbit_table.json`, run logs. No model was fitted beyond closed-form tables, ridge and
bounded sklearn trees; C5 was not touched.
