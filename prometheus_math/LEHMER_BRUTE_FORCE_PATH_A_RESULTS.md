# Lehmer Brute-Force — Path A Results (high-precision re-verification)

**Date:** 2026-05-04
**Forged by:** Techne (toolsmith)
**Subspace:** deg-14 reciprocal palindromic, coefficients in [-5, 5], `c_0` positive (~97.4M polys after sign canonicalisation)
**Source:** `prometheus_math/_lehmer_brute_force_results.json` (verdict: `INCONCLUSIVE`)
**Output:** `prometheus_math/_lehmer_brute_force_path_a_results.json`

## Mission

The full brute-force F at deg-14 ±5 palindromic completed earlier today and
returned 43 verified band hits. Of those, 26 were in the Mossinghoff catalog
and 17 were NOT — but every one of those 17 had `verification_failed=True`
because `mpmath.polyroots` at dps=30 returned NaN. The brute-force run
declared `INCONCLUSIVE` because we cannot safely call H5 vs H2 with that
many entries unverified at high precision.

Path A is the cheapest of three resolution strategies. It re-verifies the 17
entries at higher precision. **Crucially, it factors the polynomial first**
via `sympy.factor_list` and computes Mahler measures factor-by-factor with
`Poly.nroots(n=80)`, which dodges the convergence failure that defeated bare
`mpmath.polyroots` (the failure was caused by clustered repeated unit-circle
roots from cyclotomic factors — once factored, each irreducible piece has
only simple roots and the eigenvalue-based root-finder converges instantly).

Path A does **not** do symbolic interpretation of the residual factors —
that's Path B. It only re-verifies M to high precision, classifies each
entry, and re-runs the Mossinghoff cross-check with the corrected M.

## Headline result

**Substrate verdict:** `H5_CONFIRMED`
**Path A lifts the brute-force `INCONCLUSIVE` to `H5_CONFIRMED` for the deg-14 palindromic ±5 subspace.**

Every one of the 17 unverified entries resolved at the lowest precision
tried (`dps=60`, ~13ms per entry). 15 were cyclotomic-noise (true `M = 1`
exactly; numpy companion-matrix routine drifted into the band by ~1e-3 due
to repeated unit-circle eigenvalues). 2 were in-band Lehmer-extension
variants whose M was exactly Lehmer's measure to better than 1e-15; both
match the catalog `Lehmer-extension (deg 14)` entry via M-proximity.

**Zero novel candidates** flagged for Path B/C cross-check.

## Aggregate counts

| Metric | Count |
| --- | --- |
| Unverified entries loaded | 17 |
| Converged at `dps=60` | 17 |
| Converged at `dps=100` (only) | 0 |
| Converged at `dps=200` (only) | 0 |
| **Did not converge (A4)** | **0** |

| Classification | Count | Meaning |
| --- | --- | --- |
| **A1** (cyclotomic_only) | 15 | M ≤ 1 + 1e-8; entry is purely cyclotomic, numpy noise |
| **A2** (cyclotomic × small Salem) | 0 | M in (1+1e-8, 1.001]; small residual |
| **A3** (confirmed in-band) | 2 | M in (1.001, 1.18); genuine band candidate |
| **A4** (still failed) | 0 | High-precision factor + nroots failed |

| Per-entry verdict | Count |
| --- | --- |
| cyclotomic_noise (A1+A2) | 15 |
| **rediscovery (A3 + Mossinghoff match)** | **2** |
| candidate (A3 with no Mossinghoff match) | **0** |
| still_unverified (A4) | 0 |

## Per-entry table

`half_coeffs` is the 8-element half-vector `(c_0, ..., c_7)`. `M_numpy` is
the original brute-force eigenvalue-based estimate; `M_path_a` is Path A's
factor-then-nroots result at the precision in `dps`.

| # | half_coeffs | M_numpy | M_path_a | dps | class | verdict | Mossinghoff |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  0 | `[1, -4, 5, 0, -5, 4, -1, 0]` | 1.003143 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  1 | `[1, -3, 1, 5, -5, -1, 3, -2]` | 1.004371 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  2 | `[1, -3, 2, 1, 0, -2, 1, 0]` | 1.176533 | **1.176280818259918** | 60 | **A3** | **rediscovery** | Lehmer-extension (deg 14) |
|  3 | `[1, -3, 2, 2, -4, 3, 1, -4]` | 1.002844 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  4 | `[1, -3, 3, -2, 1, 3, -5, 4]` | 1.004297 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  5 | `[1, -2, -1, 3, 1, -2, -1, 2]` | 1.002707 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  6 | `[1, -2, 0, 0, 2, 2, -3, 0]` | 1.003249 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  7 | `[1, -1, -3, 2, 3, 1, -1, -4]` | 1.003989 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  8 | `[1, 0, 3, 0, 1, 0, -5, 0]` | 1.001180 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
|  9 | `[1, 1, -3, -2, 3, -1, -1, 4]` | 1.003944 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
| 10 | `[1, 2, -1, -3, 1, 2, -1, -2]` | 1.002707 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
| 11 | `[1, 2, 0, 0, 2, -2, -3, 0]` | 1.003249 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
| 12 | `[1, 3, 1, -5, -5, 1, 3, 2]` | 1.004371 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
| 13 | `[1, 3, 2, -2, -4, -3, 1, 4]` | 1.002842 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
| 14 | `[1, 3, 2, -1, 0, 2, 1, 0]` | 1.176533 | **1.176280818259918** | 60 | **A3** | **rediscovery** | Lehmer-extension (deg 14) |
| 15 | `[1, 3, 3, 2, 1, -3, -5, -4]` | 1.004297 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |
| 16 | `[1, 4, 5, 0, -5, -4, -1, 0]` | 1.003141 | 1.000000000000000 | 60 | A1 | cyclotomic_noise | — |

### A3 entries — factor structure

Both A3 entries factor as a cyclotomic factor times Lehmer's deg-10
polynomial, recovering Lehmer's measure exactly:

| # | factorisation | M(factor) per piece |
| --- | --- | --- |
|  2 | `(x - 1)^4 * Lehmer_10(x)` | 1 × 1.17628081826 = 1.17628081826 |
| 14 | `(x + 1)^4 * Lehmer_10(-x)` | 1 × 1.17628081826 = 1.17628081826 |

Entries #2 and #14 are related by the involution `x -> -x`, which preserves
M. Both are well-known Lehmer extensions in the deg-14 palindromic family.

## Why mpmath dps=30 originally failed and dps=60 (after factoring) works

The `mpmath.polyroots` Durand-Kerner iteration cannot converge on the
unfactored deg-14 polynomial — verified empirically up to `dps=400`,
`maxsteps=4000`. The reason is the cluster of repeated unit-circle roots
contributed by the cyclotomic factors: e.g. entry #0 factors as
`(x-1)^6 (x+1)^2 (x^2+1) (x^4+1)`, putting six roots at +1 and two at -1.
Durand-Kerner's quadratic convergence degrades to linear (or worse) when
roots cluster within a distance ~ε of each other, and clustered repeated
roots make the iteration oscillate without ever satisfying the residual
tolerance.

`sympy.factor_list` factors the polynomial **exactly** over Z, breaking it
into irreducible pieces each with simple roots only. Then `Poly.nroots(n=80)`
on each factor uses the eigenvalue-based root-finder of mpmath underneath,
which does not have the clustering pathology. Each factor has degree ≤ 10
and converges in microseconds.

This is the right tool for the job: factoring is cheap (sub-millisecond at
deg 14), and once factored, every irreducible piece is well-conditioned for
high-precision root-finding.

## Path A's verdict on the substrate question

**Path A lifts INCONCLUSIVE → H5_CONFIRMED.**

Specifically:

* The 26 in-Mossinghoff entries from the brute-force run were already verified.
* The 17 not-in-Mossinghoff + verification_failed entries are now all classified:
  * 15 are cyclotomic-noise (true M = 1, not actually in the band — they were
    numerical false positives from the deg-14 companion-matrix path).
  * 2 are deg-14 Lehmer extensions, both matching the Mossinghoff catalog
    `Lehmer-extension (deg 14)` entry via M-proximity at the corrected M.
* **Zero entries remain unverified or unmatched.**
* No A3 entry lacks a Mossinghoff match, so no candidate is flagged for Path
  B/C cross-check.

The deg-14 palindromic ±5 subspace contains no novel sub-1.18 specimens that
the Mossinghoff catalog has missed. **H5 holds: Mossinghoff ate the
reachable subspace.**

## Caveats & honest framing

* H5 holds **only for this specific subspace** (deg-14, palindromic,
  coefficients in [-5, 5], sign-canonicalised on `c_0 > 0`). It says nothing
  about deg-16+ extensions, wider coefficient ranges, or non-palindromic
  Salem polynomials. The brute-force run is a *local lemma*, and Path A
  upgrades it from "probably true given the substrate" to "verified to
  high precision".

* The cyclotomic-noise filter that the brute-force ran upstream of these 17
  entries is now corroborated post-hoc: every A1 entry truly has M = 1
  exactly, validating the cyclotomic-residual heuristic that already drained
  hundreds of similar polynomials in the brute-force pipeline.

* Path A has no opinion on what makes a polynomial "Salem" or "Lehmer" —
  it just computes M and matches against catalog. The structural / symbolic
  characterisation of the residuals is Path B's territory and has not been
  done here. (For these 17 entries it would be wasteful: every residual is
  either trivial (cyclotomic only) or Lehmer's polynomial.)

* Path A confirms the catalog's coverage *as a numerical claim*. It does
  not constitute a proof of Lehmer's conjecture in this subspace — that
  would require ruling out *all* deg-14 reciprocal integer polynomials with
  M ∈ (1, 1.17628), and the coefficient-range cutoff at ±5 is the load-
  bearing limitation. The brute-force file already records this caveat.

## Files

* `prometheus_math/lehmer_path_a.py` — Path A module (~530 LOC)
* `prometheus_math/tests/test_lehmer_path_a.py` — 17 tests (3 authority, 4
  property, 4 edge, 6 composition); all pass.
* `prometheus_math/_lehmer_brute_force_path_a_results.json` — full per-entry
  results document (loaded by tests + report).
* `prometheus_math/_lehmer_brute_force_results.json` — **unmodified** source
  data from the original brute-force run.

## Wall time

End-to-end Path A: **~0.2 seconds** (17 entries × ~13ms factor+nroots each).
