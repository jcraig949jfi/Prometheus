# Lehmer Brute-Force Path C — Results

**Hypothesis under test (Path C):** the 17 unmatched entries from the
deg-14 ±5 palindromic brute-force are catalog-lookup-fuzziness
artefacts — specifically, (a) cyclotomic-only polynomials whose true
Mahler measure is exactly 1 but whose numpy reading exceeded the
1.0001 filter floor, and/or (b) `Lehmer × Φ_n` products whose specific
Φ-decomposition was missed by the original tolerance match.

**Forged:** 2026-05-04 by Techne (toolsmith) for Charon's H5 settlement.

**Inputs:**
- 17 unmatched brute-force entries from
  `prometheus_math/_lehmer_brute_force_results.json`
  (`verification_failed=True`, `in_mossinghoff=False`).
- Mossinghoff catalog: `prometheus_math/databases/_mahler_data.py`
  (8625 entries, 2026-05-04 refresh).

**Method:**
1. Load 17 unmatched entries and the catalog.
2. Per entry, factor the polynomial via `sympy.factor_list`.
3. Detect cyclotomic factors via the `Φ_n` coefficient table for
   `n ≤ 200`.
4. If the residual (non-cyclotomic) part is empty → classify **C3**
   (all-cyclotomic; numpy noise).
5. If the residual is exactly Lehmer's deg-10 polynomial (or its
   `x → -x` flip) → classify **C2** (Lehmer × Φ_n product).
6. Otherwise, attempt tighter M+Hamming proximity match against the
   catalog → classify **C1**.
7. Otherwise → **C4** (still unmatched; discovery candidate, triggers
   arXiv / OEIS / LMFDB cross-checks).

## Per-class summary

| Class | Count | Meaning |
|-------|------:|---------|
| C1 (catalog match via tighter proximity) | 0 | none needed |
| C2 (Lehmer × Φ_n product, sympy-exact) | 2 | both M ≈ 1.176 entries |
| C3 (all-cyclotomic; M = 1 exactly; float noise) | 15 | all M ≈ 1.001-1.005 entries |
| C4 (still unmatched; discovery candidate) | **0** | no discovery candidates |
| **Total** | **17** | |

## Path C verdict

**`PATH_C_LIFTS_TO_H5_CONFIRMED`**

All 17 originally-unmatched entries resolve to either Lehmer × Φ_n
products (C2) or all-cyclotomic polynomials whose true M = 1 (C3). The
brute-force INCONCLUSIVE verdict was a tooling artefact, not a genuine
H1 break and not a discovery — the catalog plus its implicit
cyclotomic-extension closure already contains the entire reachable
deg-14 ±5 palindromic Lehmer band.

## Per-entry classification

Coefficients are listed in **ascending** order
(`[a_0, a_1, …, a_14]`).

| # | Class | M (numpy) | residual_M | Decomposition |
|---|-------|----------:|-----------:|---------------|
| 1 | C3 | 1.003143 | 1.000957 | Φ₁⁶ · Φ₂² · Φ₄ · Φ₈ |
| 2 | C3 | 1.004371 | 1.000794 | Φ₁⁶ · Φ₂² · Φ₇ |
| 3 | **C2** | 1.176533 | 1.176299 | **Lehmer(x) · Φ₁⁴** (deg-check ✓) |
| 4 | C3 | 1.002844 | 1.000760 | Φ₁⁶ · Φ₂² · Φ₄ · Φ₅ |
| 5 | C3 | 1.004297 | 1.000753 | Φ₁⁶ · Φ₂² · Φ₃ · Φ₄² |
| 6 | C3 | 1.002707 | 1.000904 | Φ₁⁶ · Φ₂² · Φ₃ · Φ₅ |
| 7 | C3 | 1.003249 | 1.000788 | Φ₁⁶ · Φ₂² · Φ₃² · Φ₄ |
| 8 | C3 | 1.003989 | 1.000761 | Φ₁⁶ · Φ₂⁴ · Φ₃ · Φ₄ |
| 9 | C3 | 1.001180 | 1.001595 | Φ₁² · Φ₂² · Φ₄⁵ |
| 10 | C3 | 1.003944 | 1.003336 | Φ₁⁴ · Φ₂⁶ · Φ₄ · Φ₆ |
| 11 | C3 | 1.002707 | 1.003213 | Φ₁² · Φ₂⁶ · Φ₆ · Φ₁₀ |
| 12 | C3 | 1.003249 | 1.004090 | Φ₁² · Φ₂⁶ · Φ₄ · Φ₆² |
| 13 | C3 | 1.004371 | 1.003412 | Φ₁² · Φ₂⁶ · Φ₁₄ |
| 14 | C3 | 1.002842 | 1.004231 | Φ₁² · Φ₂⁶ · Φ₄ · Φ₁₀ |
| 15 | **C2** | 1.176533 | 1.176299 | **Lehmer(-x) · Φ₂⁴** (deg-check ✓) |
| 16 | C3 | 1.004297 | 1.003167 | Φ₁² · Φ₂⁶ · Φ₄² · Φ₆ |
| 17 | C3 | 1.003141 | 1.005305 | Φ₁² · Φ₂⁶ · Φ₄ · Φ₈ |

## C2 entries — explicit Lehmer × Φ_n decomposition

Both Class-2 entries (M ≈ 1.176) decompose into **Lehmer's deg-10
polynomial** times a **deg-4 cyclotomic factor**, confirming the
Class-2 hypothesis exactly.

| Entry # | Coefficients (ascending) | Lehmer orientation | Φ-factor | Total degree |
|---------|--------------------------|--------------------|----------|--------------|
| 3 | `[1, -3, 2, 1, 0, -2, 1, 0, 1, -2, 0, 1, 2, -3, 1]` | `Lehmer(x)` | `Φ₁⁴` (deg 4) | 14 = 10 + 4 ✓ |
| 15 | `[1, 3, 2, -1, 0, 2, 1, 0, 1, 2, 0, -1, 2, 3, 1]` | `Lehmer(-x)` | `Φ₂⁴` (deg 4) | 14 = 10 + 4 ✓ |

Note that entries 3 and 15 are related by `P(x) ↔ P(-x)`, which is
exactly the Mahler-measure preserving symmetry — both encode the same
Lehmer-product up to the global sign reflection.

**Why the catalog missed them.** The 2026-05-04 Mossinghoff snapshot
contains `Lehmer × Φ_5`, `Lehmer × Φ_8`, `Lehmer × Φ_12` and the
generic `Lehmer-extension (deg 14)`, but **not** `Lehmer × Φ_1⁴` or
`Lehmer × Φ_2⁴` as named entries. The original brute-force
`lookup_in_mossinghoff` used (1) coefficient-exact match (failed
because the catalog lacks these specific products as named entries)
and (2) M-proximity match with `tol=1e-6` (failed because the
`verification_failed=True` mpmath path returned NaN, leaving only the
numpy `M_numpy=1.176533` reading, which is `2.4e-4` away from the
catalog's stored `1.17628081826` — outside the 1e-6 tolerance).
Path C's sympy factorisation sidesteps both failure modes.

## C3 entries — all-cyclotomic polynomials

The 15 Class-3 entries factor entirely into products of cyclotomic
polynomials Φ_n, so their **true Mahler measure is exactly 1**. The
M ≈ 1.001-1.005 readings reported by the brute-force pipeline are
purely floating-point noise from `numpy.linalg.eigvals` on companion
matrices with closely-spaced unit-circle roots (a known
ill-conditioning regime when multiple Φ_n share roots, e.g. repeated
Φ₁ or Φ₂ factors).

The original `is_cyclotomic_exact` filter used a `1e-4` threshold on
`|M − 1|`; the noise floor on these specific deg-14 palindromes lands
just above that threshold (typically `1e-3` to `5e-3`), so they
escaped the cyclotomic filter and entered the band. The
mpmath-recheck path returned NaN (due to root-finding convergence
issues on multi-rooted unit-circle polynomials), forcing the
`verification_failed` flag — which is what surfaced these entries as
"unmatched" in the first place.

## C4 entries — discovery candidates

**None.** All 17 entries resolve cleanly. The deg-14 ±5 palindromic
subspace contains zero non-cyclotomic, non-Lehmer-product
polynomials with M < 1.18 — precisely the H5_CONFIRMED prediction.

## Independence and agreement

Path C is independent of Paths A (mpmath dps=50 reverification) and B
(symbolic-only direct factor decomposition), but the three paths
should produce **concordant classifications** (every Path-A C3 should
be a Path-B/C C3, etc.). Concordance across three independent
methods is what lifts the verdict from "we found a story that works"
to "the entries are robustly explainable."

Expected agreement matrix (to be cross-checked against Paths A/B
outputs once they land):

| Path A finding | Path B finding | Path C finding | Agreement |
|----------------|----------------|----------------|-----------|
| mpmath M ≈ 1.0 (cyclotomic-clean) | symbolic factorization fully Φ_n | C3 (15 entries) | exact |
| mpmath M ≈ 1.176 (Lehmer-clean) | symbolic factorization = Lehmer · Φ_n | C2 (2 entries) | exact |

## Output files

- `prometheus_math/_lehmer_brute_force_path_c_results.json` — full
  per-entry classification record + summary + verdict.
- `prometheus_math/lehmer_brute_force_path_c.py` — module: factor +
  classify pipeline, exported helpers, sympy-driven cyclotomic and
  Lehmer-product detection.
- `prometheus_math/tests/test_lehmer_path_c.py` — 13 tests
  (3 authority + 3 property + 3 edge + 4 composition); all pass in
  ~15s.

## Honest framing

The Path C verdict is **`PATH_C_LIFTS_TO_H5_CONFIRMED`** — and that's
the right resolution **for this specific catalog-fuzziness
hypothesis**. But Path C alone does not settle H5 in full: it shows
that the 17 unmatched entries are *all* explainable as cyclotomic
products of catalog members (either Lehmer or the trivial M = 1
polynomial), which means **Mossinghoff's catalog plus its
cyclotomic-multiplication closure** covers the deg-14 ±5 palindromic
Lehmer band exactly. The catalog as **literally stored** is missing
two named entries (`Lehmer × Φ_1⁴` and `Lehmer × Φ_2⁴`) that would
have made the original lookup pass without needing Path C — those are
candidates for the next catalog refresh.
