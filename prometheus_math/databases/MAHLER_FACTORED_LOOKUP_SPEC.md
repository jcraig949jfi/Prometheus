# Mossinghoff Factored Lookup — Specification

**Date:** 2026-05-04
**Author:** Techne (toolsmith)
**Module:** `prometheus_math.databases.mahler`
**New API:** `mahler_lookup_factored`, `composite_label`
**Companion test:** `prometheus_math/databases/tests/test_mahler_factored.py`

---

## 1. Why factorization-aware lookup is needed

The Mossinghoff small-Mahler-measure catalog stores polynomials by their
*literal coefficient list*. Lehmer's polynomial is in there at intrinsic
degree 10; a handful of named "Lehmer-extension" entries are stored at
degrees 12, 14, etc. — but only specific products like
`Lehmer * Phi_n` for small `n` and multiplicity `k = 1` are catalogued.
Higher-multiplicity products like `Lehmer * Phi_n^k` for `k >= 2` are
**not** enumerated.

The 2026-05-04 brute-force run on the deg-14 reciprocal palindromic
[-5, 5] subspace surfaced 17 `verification_failed` entries that the
original lookup couldn't classify. Two of them (M_numpy ~ 1.17653) were:

* **`Lehmer * Phi_1^4`** — coeffs ascending
  `[1, -3, 2, 1, 0, -2, 1, 0, 1, -2, 0, 1, 2, -3, 1]`
* **`Lehmer * Phi_2^4`** — coeffs ascending
  `[1, 3, 2, -1, 0, 2, 1, 0, 1, 2, 0, -1, 2, 3, 1]`

Both factor cleanly as Lehmer's polynomial (or Lehmer(-x)) times a
degree-4 cyclotomic factor `(x - 1)^4` or `(x + 1)^4`. The Mahler
measure of each is exactly Lehmer's constant 1.17628081826... — they
are *rediscoveries* of Lehmer, not novel candidates. The original
`lookup_polynomial` exact-match logic returned `None`, and the entries
slipped into the verification_failed bucket as if they were sub-1.18
mysteries.

The remaining 15 missed entries were **pure cyclotomic products** with
numerical M-drift just above the 1+1e-6 noise gate. These are also not
genuine band candidates; the new lookup correctly flags them as
`all_cyclotomic_match`.

This is a **catalog-completeness fix**, not a new mathematical finding.
The 2 entries are still rediscoveries (via Lehmer + cyclotomic
structure); we are merely teaching the lookup to recognise the structure.

---

## 2. API specification

### `mahler_lookup_factored(coeffs, max_cyclotomic_n=200)`

Catalog lookup with factorization-aware composite matching.

**Parameters**

| name | type | default | description |
| --- | --- | --- | --- |
| `coeffs` | `list[int]` | required | Ascending integer coefficients. |
| `max_cyclotomic_n` | `int` | `200` | Largest `n` probed when classifying cyclotomic factors. |

**Returns**

A 3-tuple `(label, cyclotomic_structure, match_type)`:

* `label` — `str | None`. Catalog entry name (e.g. `"Lehmer's polynomial"`),
  or a printable summary of pure cyclotomic structure (e.g. `"Phi_1^4 * Phi_2"`),
  or `None` when no match.
* `cyclotomic_structure` — `list[tuple[int, int]]`. List of `(n, multiplicity)`
  tuples in ascending `n` order. Empty for direct or M-proximity matches.
* `match_type` — one of:
  * `"direct_match"` — literal coefficient list (or x → -x flip) is in
    the catalog. No factorization needed.
  * `"composite_match"` — the polynomial factors as
    `Q(x) * prod(Phi_{n_i}^{k_i})` where `Q` matches a catalog entry.
  * `"all_cyclotomic_match"` — every factor is cyclotomic; the polynomial
    is a pure cyclotomic product (M = 1 in exact arithmetic).
  * `"no_match"` — neither direct lookup nor factorization yields a hit.

### `composite_label(label, cyclotomic_structure)`

Reconstruct a human-readable string from a `(label, structure)` pair.

```python
composite_label("Lehmer's polynomial", [(1, 4)])
# -> "Lehmer's polynomial * Phi_1^4"
composite_label(None, [(1, 2), (3, 1)])
# -> "Phi_1^2 * Phi_3"
```

### Backwards compatibility

The pre-existing `lookup_polynomial(coeffs) -> Optional[dict]` is
**unchanged**: same signature, same return type, same exact-match
semantics. All existing callers continue to work.

In `prometheus_math.lehmer_brute_force`:

* `lookup_in_mossinghoff(half_coeffs, M_value, M_tol=1e-6, use_factored=True)`
  now returns a 4-tuple `(in_catalog, label, cyclotomic_structure, match_type)`.
  The factorization branch fires only when both prior checks (direct,
  M-proximity) miss, and only when `use_factored=True` (default).
* `lookup_in_mossinghoff_legacy(half_coeffs, M_value, M_tol=1e-6)` is
  the 2-tuple legacy wrapper for callers that pre-date 2026-05-04.

---

## 3. The 3 match types in detail

### `direct_match`

Cheapest path. The literal coefficient list (or its `x -> -x` reflection)
is in `_mahler_data.MAHLER_TABLE`. No factorization.

### `composite_match`

The polynomial factors over `ZZ` as

```
P(x) = Q(x) * prod_{i} Phi_{n_i}(x)^{k_i}
```

where `Q` is a non-cyclotomic factor whose ascending coefficient list
*is* in the catalog (after `x -> -x` flip allowance). The cyclotomic
factors all sit on the unit circle and contribute `M = 1`, so
`M(P) = M(Q)`.

This is the case the catalog-completeness fix was built for. It catches
`Lehmer * Phi_n^k` for arbitrary `k >= 1`, plus `Smyth * Phi_n^k`,
plus any other catalog poly multiplied by a cyclotomic product.

### `all_cyclotomic_match`

Every irreducible factor over `ZZ` is a cyclotomic polynomial. The
exact Mahler measure is 1; numerical drift in the numpy companion-matrix
path may push `M_numpy` slightly above the `1 + 1e-6` gate during
brute-force enumeration. The label is a printable summary like
`"Phi_1^6 * Phi_2^2 * Phi_4 * Phi_8"`, sorted ascending by `n`.

### `no_match`

Direct lookup misses, factorization yields a non-cyclotomic core, and
the core is not in the catalog. This is the **interesting** case — a
genuine candidate for a novel sub-1.18 specimen. The brute-force
verdict logic should treat these as potential `H2_BREAKS` entries.

---

## 4. Performance

Direct lookup is `O(N)` over the 178-entry snapshot — microseconds.

Factorization via `sympy.factor_list` is moderately expensive — typical
deg-14 polynomial factors in **~5-15 ms**, dominated by the polynomial
GCD steps and Berlekamp/Zassenhaus over `ZZ`.

For brute-force runs at 97M polynomials, factoring every poly is
**not feasible** (would add ~10 days of wall time at single-core
speeds). The pipeline applies `mahler_lookup_factored` only to the
**band candidates that fail direct lookup** — typically a few dozen
to a few hundred polys per run. At that scale the factorization cost
is negligible (<1 second total).

The new `lookup_in_mossinghoff` in `lehmer_brute_force.py` enforces
this ordering: try direct match → try M-proximity → only then factor.

---

## 5. Test coverage

`prometheus_math/databases/tests/test_mahler_factored.py` (14 tests):

* **Authority (4)**: Lehmer direct match; Lehmer × Φ_1 deg-12;
  Lehmer × Φ_1^4 deg-14 composite; Lehmer × Φ_2^4 deg-14 composite.
* **Property (3)**: determinism across calls; Φ_n exact detection for
  n in [1, 30]; composite_label round-trip.
* **Edge (3)**: no-cyclotomic-factor falls back to direct; degenerate
  constant poly handled; cyclotomic n above cap is graceful.
* **Composition (3)**: end-to-end pipeline; the 17 verification_failed
  entries from 2026-05-04 are ALL findable; output structure valid.
* **Backwards-compat (1)**: pre-existing `lookup_polynomial` unchanged.

Plus the existing `test_mahler.py` (47 tests) and
`test_lehmer_brute_force.py` (20 tests) all continue to pass with no
regressions — the brute-force suite was updated in one place to consume
the new 4-tuple return of `lookup_in_mossinghoff`.

---

## 6. Open question — non-cyclotomic factor products

The current implementation handles:

* `Q(x) * prod_i Phi_{n_i}(x)^{k_i}` with at most one non-cyclotomic
  factor `Q`.

What about polynomials that factor as `Q_1 * Q_2 * (cyclotomic stuff)`
where `Q_1` and `Q_2` are *both* non-cyclotomic? E.g.
`Lehmer(x) * Smyth(x)` — this would have M = M(Lehmer) * M(Smyth),
landing well above the 1.18 band cap, but in principle could exist in a
larger Mahler-measure window.

**Out of scope** for this fix. The current implementation collapses all
non-cyclotomic factors into a single `core` polynomial and looks up the
core verbatim; if the catalog doesn't have `Lehmer * Smyth` as a single
entry (it doesn't), the result is `no_match`. A future enhancement
could decompose the core into its irreducible factors and look up each
piece independently — useful for catalog auditing of high-band products
but not load-bearing for the H1/H2/H5 settlement on the Lehmer band.

If/when this matters, the natural extension is to add a
`"multi_factor_match"` match type that returns
`(label_list, cyclotomic_structure, "multi_factor_match")` where
`label_list` is a list of catalog names for each non-cyclotomic
irreducible piece.

---

## 7. Honest framing

The 2 entries flagged today (`Lehmer * Phi_1^4`, `Lehmer * Phi_2^4`)
are **catalog rediscoveries**, not new sub-1.18 polynomials. Their
Mahler measure is exactly Lehmer's constant 1.17628081826... by
construction, and the brute-force run found them simply because
`Phi_n^4` factors are reachable in the [-5, 5] coefficient slice.

The catalog-completeness fix recovers the right *interpretation* of
these polynomials; it does not change the verdict on Lehmer's
conjecture. A future H2_BREAKS would still require a `no_match`
result (no Lehmer-core, no Smyth-core, no other catalog poly inside)
combined with mpmath-verified M strictly below 1.18.
