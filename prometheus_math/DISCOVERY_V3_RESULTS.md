# Discovery V3 — root-space generator results 2026-05-04

V3 inverts the search coordinate: instead of mutating coefficients (V1 / V2),
the generator samples a polynomial's *root structure* directly, then
expands to coefficients via Vieta's formulas. Reciprocity is automatic by
root + 1/root closure; the "Salem corner" (one off-unit-circle pair plus
unit-circle pairs) is the natural default distribution rather than a
needle in a coefficient haystack.

**Headline:** root-space sampling at degree 14 produced **0
integer-coefficient configurations** in 30,000 samples (15K random-bin
+ 15K cyclotomic-aligned). The integer-poly subspace within
continuous-parameterized root space is effectively measure-zero —
Vieta-of-an-integer-poly requires very specific algebraic conditions on
(r, theta) that random sampling cannot hit. This is a **structural
finding**, not a tuning failure.

## Generator design

For a degree-2k reciprocal polynomial we sample k root pairs:

* **Unit-circle pairs** (default for k-1 of k pairs): r = 1, theta in
  (0, pi). Each contributes ``x^2 - 2*cos(theta)*x + 1`` (a degree-2
  cyclotomic-style factor).
* **Salem pair** (default for 1 of k pairs): r > 1, theta in (0, pi).
  Contributes the degree-4 Salem block ``(x^2 - 2*r*cos(theta)*x + r^2)
  * (x^2 - 2*cos(theta)/r*x + 1/r^2)``.
* **Real root pair** (optional): rho > 0, contributing ``(x - rho)*(x - 1/rho)``.

Discrete bins:
* `n_theta_bins = 16` angles uniformly spaced in (0, pi)
* `n_r_bins = 8` magnitudes log-spaced in (1.0001, 1.5)

After Vieta expansion via `numpy.poly`, we round to integers iff the
rounding error is within `integer_tol = 1e-6`. **By construction**
integer-coefficient roundings are reciprocal (palindromic).

## Pilot configuration

| param | value |
|---|---|
| degree | 14 (k = 7 root pairs) |
| n_theta_bins | 16 |
| n_r_bins | 8 |
| r_min, r_max | 1.0001, 1.5 |
| n_samples | 5K per cell × 3 seeds × 2 variants = 30K |
| variant 1 | random-bin (default) |
| variant 2 | cyclotomic-aligned (theta pinned to 2*pi/n for n in {3..15}) |

Seeds: {0, 1, 2}. Total wall-clock: 3.1 s (numpy is fast when the
configurations don't trigger the kernel-mediated M-evaluation; 99.99% of
samples short-circuited at the integer-rounding gate).

## Results — random-bin variant

| seed | n_integer | n_sub_lehmer | n_signal | best_M | M-distribution |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | inf | — (no integer polys) |
| 1 | 0 | 0 | 0 | inf | — |
| 2 | 0 | 0 | 0 | inf | — |
| **agg** | **0/15000** | **0** | **0** | inf | — |

## Results — cyclotomic-aligned variant

Theta values for the unit-circle pairs are pinned to
``{2*pi/n : n in {3, 4, 5, 6, 7, 8, 9, 10, 12, 15}} ∪ {pi - that}``
(the cyclotomic-friendly subset where `2*cos(theta)` is rational).
The Salem pair's theta and r remain continuous.

| seed | n_integer | n_sub_lehmer | n_signal | best_M | M-distribution |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | inf | — |
| 1 | 0 | 0 | 0 | inf | — |
| 2 | 0 | 0 | 0 | inf | — |
| **agg** | **0/15000** | **0** | **0** | inf | — |

The cyclotomic-aligned variant also produces **0 integer-coefficient
configs**. The reason is structural: even when the unit-circle factors
expand to rational coefficients, the Salem block contributes irrational
terms (``2*r*cos(theta)`` is irrational for generic r, even when
`2*cos(theta)` happens to be rational). The product is irrational
unless the Salem block also independently rounds to integer
coefficients — which requires a measure-zero coincidence of r and theta.

## Comparison with V2 elitist

The V2 elitist baseline at degree 10 (DISCOVERY_V2_RESULTS.md) generated
non-trivial polynomials at every step but funneled them all to
M = 1 exactly (cyclotomic basin). V3 at degree 14 generates polynomials
with M > 1 *by design* (the Salem block forces a root outside the unit
circle), but cannot land on integer coefficients except by accident.

The two failure modes are *complementary*:

* **V2 elitist failure:** integer-coefficient generator (always
  succeeds) + selection collapses to cyclotomic basin (always M=1).
* **V3 root-space failure:** root-space generator (always M>1 at
  source) + integer-coefficient gate (never holds for random
  continuous samples).

Together they characterize the discovery problem: the integer
+ low-M intersection is a *thin* set in either coordinate system.
Coefficient space sees the integers but cannot escape M=1; root space
sees low M but cannot land on integers.

## Catalog hits

0 hits across both variants (no integer polys → no candidates routed to
the catalog cross-check).

## Verdict — does root-space search find polys that coefficient-space search missed?

**No, not in this configuration.** The integer-coefficient subspace
within continuously-parameterized root space is too sparse for random
sampling to find. To make root-space search productive we would need
one of:

1. **Algebraic-number sampling.** Sample r and theta from algebraic
   number fields (e.g., r as a root of a small-degree integer poly,
   theta as 2*pi*k/n for integer n). This is the conventional
   Mossinghoff GA construction — but it collapses V3 back to a
   coefficient-space-equivalent search since algebraic-number
   parameterizations are isomorphic to coefficient-space lattice
   walks for low-degree minimal polynomials.

2. **Integer-coefficient post-processing.** After Vieta expansion,
   round to nearest integer-coefficient poly *regardless* of rounding
   error, then check if the rounded poly's M is close to the original
   continuous-config M. This trades exact algebraic correctness for
   integer-poly yield. Future work.

3. **Resultant-based search.** Sample one Salem pair (r, theta) and
   search for unit-circle pairs that *make* the product integer. This
   is computationally a lattice problem (find theta_i such that
   sum_i 2*cos(theta_i) is rational) and does not yield easily to
   uniform sampling.

## H1 vs H2 update

Recall the framing:

* **H1**: 0-PROMOTE bound is *territorial* — sub-Lehmer integer polys
  are genuinely sparse, regardless of generator.
* **H2**: 0-PROMOTE bound is *generator-bound* — a richer generator
  can reach territory uniform enumeration cannot.

V3's negative result (0 integer-coeff configs in 30K samples)
**partially strengthens H1**: even when the generator's inductive bias
is *correctly aligned* with sub-Lehmer territory (Salem-shape sampling
in root space), the integer-coefficient constraint is a
measure-zero filter that forces the search back into the same
combinatorial sparsity that V1 hit.

Honestly, this is one specific root-space implementation; the
*algebraic-number sampling* variant (option 1 above) is the obvious
next attempt and is closer to what Mossinghoff actually did. Calling H2
fully refuted would be premature — but the simple "sample continuous,
round to integer" path is closed.

## Code references

* `prometheus_math/discovery_env_v3.py` — the env (no V1/V2 modifications)
* `prometheus_math/_run_v3_root_space_pilot.py` — pilot driver
* `prometheus_math/_v3_root_space_pilot.json` — full per-cell results
* `prometheus_math/tests/test_discovery_v3.py` — 17 tests across the
  authority/property/edge/composition rubric

## Test summary

```
prometheus_math/tests/test_discovery_v3.py::test_authority_vieta_phi3_degree_2 PASSED
... 17 tests total — 5 authority, 4 property, 5 edge, 3 composition ...
17 passed in 14.16s
```
