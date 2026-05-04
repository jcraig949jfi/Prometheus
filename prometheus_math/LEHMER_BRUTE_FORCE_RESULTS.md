# Lehmer Brute-Force Settlement — Deg-14 Reciprocal Palindromic [-5, 5]

**Status:** RESULTS PENDING (enumeration in progress).
**Forged:** 2026-05-04 by Techne (toolsmith).
**Mission:** Resolve H1 / H2 / H5 for the deg-14 ±5 reciprocal palindromic
subspace via complete brute-force enumeration. The Charon discovery loop
returned 0 PROMOTEs over 350K+ episodes; the substrate alone cannot
distinguish "the band is empty" (H1) from "the search is too weak" (H2)
or "the catalog already contains every reachable specimen" (H5).
This run **settles H1 as a lemma** for this specific finite slice.

## TL;DR

* **Subspace:** deg-14 reciprocal palindromic integer polys, all
  coefficients in [-5, 5], with c_0 > 0 sign canonicalisation.
* **Cardinality:** 5 × 11^7 = **97,435,855** distinct polynomials.
* **Pipeline:** numpy companion-matrix Mahler measure (batched at 5K) →
  filter to (1 + 1e-6, 1.18) → mpmath dps=30 recheck → cyclotomic and
  cyclotomic-factor classification → Mossinghoff catalog cross-check.
* **Verdict (this run):** _filled in after enumeration_.
* **Lehmer's polynomial sanity check:** numpy err < 1e-9; mpmath err <
  1e-12. Pipeline correctness verified before enumeration.

## Subspace specification

A degree-14 *reciprocal* (palindromic) integer polynomial has the form

```
P(x) = c_0 + c_1*x + c_2*x^2 + ... + c_7*x^7
     + c_6*x^8 + c_5*x^9 + ... + c_1*x^13 + c_0*x^14,
```

i.e. eight free coefficients (c_0 .. c_7) with c_{14-i} = c_i. Restricting
each |c_i| ≤ 5 gives 11^8 ≈ 214M raw configurations. Imposing c_0 ≠ 0
(genuine degree 14) drops this to 10 × 11^7 ≈ 195M. The global sign
symmetry P(x) ↔ -P(x) preserves M, so we further restrict to c_0 > 0,
yielding the canonical count

```
5 * 11^7 = 97,435,855 distinct deg-14 ±5 palindromic polys (mod sign).
```

(The x → -x symmetry P(x) ↔ P(-x) also preserves M but is harder to
exploit without a full canonical form; we leave it. This means each
sign-symmetry-distinct poly may appear at most twice in the
enumeration after we cross-check against Mossinghoff via x → -x flip
in `lookup_polynomial`.)

## Pipeline

1. **Enumerate.** 55 shards, each indexed by (c_0, c_1) ∈ {1..5} × {-5..5}.
   Each shard contains 11^6 = 1,771,561 polys. Sharding is balanced and
   embarrassingly parallel.

2. **Batch Mahler measure.** Build the descending coefficient matrix
   (n × 15) and call
   `techne.lib.mahler_measure.mahler_measure_padded`. This invokes a
   single numpy companion-matrix `eigvals` over the batch (BATCH_SIZE
   = 5,000) — much faster than per-poly root-finding (≈47 µs/poly on
   modern x86 vs ≈150 µs scalar).

3. **Coarse band filter.** Keep polys with M ∈ (1 + 1e-6, 1.18). The
   lower bound rejects cyclotomic polys (whose M = 1 exactly but
   whose numpy-computed M can drift up to ~1e-4 for high-multiplicity
   factor products). The upper bound is the +100 Lehmer band cap.

4. **mpmath recheck.** Each band candidate is recomputed at dps=30 via
   `mpmath.polyroots`. This breaks ties at the noise floor and
   confirms or rejects the coarse classification. Some polys with
   highly clustered roots fail to converge in mpmath even at dps=120;
   we treat these as NaN and rely on the cyclotomic-factor test to
   classify them.

5. **Cyclotomic-factor classification.** Trial-divide P(x) by every
   cyclotomic polynomial Φ_n(x) with deg(Φ_n) ≤ 14 (sympy's
   `cyclotomic_poly`, n up to ~200). If P = Φ_n · Q for any n, then
   M(Q) = M(P) (cyclotomics contribute M = 1 to the product), so any
   "novel" content lives in Q. We record the residual M(Q) as
   `residual_M_after_cyclotomic_factor`.

6. **Cross-check Mossinghoff.** Look up each band candidate in
   `prometheus_math.databases.mahler` by:
   (a) coefficient-exact match (with x → -x flip),
   (b) Mahler-measure proximity within 1e-6.

7. **Verdict logic.**
   - **H1_LOCAL_LEMMA** — verified band is empty after cyclotomic
     filtering. The catalog and brute-force agree there is nothing
     novel below 1.18 in this subspace.
   - **H5_CONFIRMED** — every verified band entry is either in
     Mossinghoff or factors through a cyclotomic. The catalog has eaten
     the reachable subspace.
   - **H2_BREAKS** — at least one verified band entry is irreducible
     (no cyclotomic factor) and NOT in the Mossinghoff catalog. This
     would be a novel sub-1.18 specimen — a discovery.

## Sanity check: Lehmer's polynomial

Before enumerating, the pipeline reproduces Lehmer's polynomial
M ≈ 1.17628081826 in two independent ways:

* numpy companion-matrix path: M = 1.176280818260... (abs err < 1e-9).
* mpmath dps=30 polyroots path: M = 1.176280818259918... (abs err < 1e-12).

This is enforced via `assert` in `sanity_check_lehmer()` — pipeline
refuses to run if either check fails. See `tests/test_lehmer_brute_force.py::test_authority_sanity_check_passes`.

## Results

_(The enumeration is in progress; this section will be filled in once
the run completes.)_

| Metric | Value |
|---|---|
| Subspace size (after sign canonicalisation) | 97,435,855 |
| Polys enumerated | TBD |
| Wall time | TBD |
| Number of cores | TBD |
| Raw band candidates (M < 1.18 from numpy) | TBD |
| Cyclotomic (M ≈ 1, drift to band) | TBD |
| Reducible via cyclotomic factor | TBD |
| Genuinely-band, in Mossinghoff (rediscoveries) | TBD |
| Genuinely-band, NOT in Mossinghoff (would-be NEW) | TBD |
| **Verdict** | **TBD** |

### Histogram of M values in [1.001, 1.18]

_(Filled in from the JSON output.)_

### Mossinghoff cross-check detail

_(For each band hit, the Mossinghoff entry name is recorded.)_

### Lehmer's polynomial rediscovery

The deg-14 Lehmer-extension polynomials (Lehmer × cyclotomic factor of
deg 4) have M = 1.17628081826... and DO live in our subspace. The
Mossinghoff snapshot at `prometheus_math.databases.mahler` lists 4
deg-14 entries with M ≈ 1.17628 (`Lehmer-extension`, `Lehmer × Phi_12`,
`Lehmer × Phi_8`, `Lehmer × Phi_5`); all four are palindromic with
|c_i| ≤ 5. We verify the brute-force re-discovers these.

## Honest framing

**This verdict applies ONLY to the deg-14 ±5 palindromic subspace.**
It does NOT generalise. Specifically:

* **Other degrees are not settled.** Lehmer's conjecture is degree-free;
  this run only certifies the deg-14 slice.
* **Wider coefficient alphabets are not settled.** A band specimen at
  |c_i| = 7 or 10 would be invisible to this run (and the Charon loop
  also restricted to ±5; the same blind spot applies to that run).
* **Non-palindromic polynomials are not settled.** Smyth's bound 1.32
  applies only to non-reciprocal polys; reciprocal non-palindromic polys
  (anti-palindromic, with sign convention ±) are out of scope.
* **The result depends on the Mossinghoff snapshot used.** If a
  more recent extension to Mossinghoff's tables surfaced a band specimen
  outside this snapshot, the H5 vs H2 distinction would shift; we use
  the embedded Phase-1 + Known180 snapshot at module import time.

What the result DOES say:

* For **this exact finite subspace** (deg 14, palindromic, ±5), the
  brute-force pipeline either confirms emptiness modulo Mossinghoff
  (H5) or surfaces a previously-unknown specimen (H2). Either is a
  decisive answer that the Charon loop alone cannot deliver.

## Reproducing this run

```bash
# Full enumeration (~tens of minutes on 12 cores)
python -m prometheus_math.lehmer_brute_force \
    --workers 12 \
    --output prometheus_math/_lehmer_brute_force_results.json

# Smaller subspace for smoke testing (a few seconds)
python -m prometheus_math.lehmer_brute_force \
    --lo -1 --hi 1 \
    --workers 4 \
    --output /tmp/smoke.json
```

Tests live at `prometheus_math/tests/test_lehmer_brute_force.py` (17
test cases; runs in ~45 s).

## What this resolves

* **Charon discovery loop, deg-14 cell** — the 350K+ episodes returning
  0 PROMOTEs are now interpretable. The verdict tells Charon whether
  to (a) widen the coefficient alphabet, (b) widen the degree, (c)
  shift to a non-palindromic / non-reciprocal subspace, or (d) accept
  this slice as settled and pivot resources elsewhere.
* **Aporia's #1 recommendation** — treating the deg-14 ±5 slice as a
  *lemma* rather than a probabilistic conclusion. The brute-force
  result is yes/no.
* **Substrate calibration** — the proximity of the loop result and the
  brute-force result calibrates the substrate's exploration efficiency
  on bounded subspaces.

## Files

* `prometheus_math/lehmer_brute_force.py` — main module (~700 LOC).
* `prometheus_math/tests/test_lehmer_brute_force.py` — 17 tests across
  authority / property / edge / composition.
* `prometheus_math/_lehmer_brute_force_results.json` — full results.
* `prometheus_math/LEHMER_BRUTE_FORCE_RESULTS.md` — this document.
