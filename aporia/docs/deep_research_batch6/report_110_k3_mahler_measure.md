# Deep Research Report #110: Mahler Measure of K3 Surfaces

**Target Agent:** Charon
**Topic:** Deninger-Boyd empirics extending Lehmer saturation to dim-2 motives (Batch 3 F014:P040)
**Date:** 2026-04-23

## 1. Problem Statement

Mahler measure m(P) of Laurent polynomial P(x_1,...,x_n) is integral of log|P| over unit torus. For n=1, Lehmer's 1933 conjecture: m(P) ≥ log(1.17628...) for non-cyclotomic P, saturated at Lehmer's x^10 + x^9 − x^7 − x^6 − x^5 − x^4 − x^3 + x + 1. For n=2, Boyd-Deninger connects m(P) to L-values of elliptic curves. For n=3, natural target is K3 surfaces (dim-2 motives):

**Does m(P) for 3-variable polynomials whose Newton polytope defines a K3 admit a Lehmer-type lower bound, and what saturates it?**

Clean test: L-function independent of prime-density effects; claim is geometric, not statistical.

## 2. Literature

- **Boyd (1981)** *Speculations concerning the range of Mahler measure* — catalogued n=2 measures, proposed L'(E,0) identities.
- **Deninger (1997)** J. AMS 10: m(P) to regulators of motivic cohomology; first principled K3 framework.
- **Boyd (1998)** Experimental Math 7: 50+ identities m(P) =? c · L'(E, 0), mostly conjectural.
- **Rodriguez-Villegas (1999)** *Modular Mahler measures I*: tempered polynomial measures to Eisenstein-Kronecker series.
- **Brunault (2016), Brunault-Zudilin (2020)** *Many Variables Mahler Measures* (Cambridge): Ch. 8 K3 families including Apery (1+x)(1+y)(1+z) − txyz.
- **Bertin (2004, 2008)** — m for K3 one-parameter families; matched L(f, 3) for weight-3 newforms.
- **Samart (2015, 2020)** — families with m = L'(E/K, 0) for K3 of Picard rank 19-20.

## 3. LMFDB Data

K3 coverage sparse. No dedicated `k3_surfaces` table. Workaround:
1. OEIS reciprocal-polynomial sequences (A231896, A318626, A338336 family).
2. `cmf_newforms` weight=3 — candidate L-functions.
3. Apery-like families from Almkvist-Zudilin (~350 entries).
4. Narumiya-Shiga classification: 95 K3 families via anticanonical hypersurfaces in toric 3-folds — explicit Newton polytopes.

## 4. Test Design

**Scan:** 10^4 candidate 3-var Laurent polynomials.
- 95 Narumiya-Shiga polytopes × 100 coefficient tweaks = 9,500 seeds.
- 500 OEIS-derived reciprocal triples.

**Mahler measure:** Jensen iterated: fix (x,y) on torus, integrate log|P(x,y,e^{iθ})| analytically via root-tracking on univariate reduction. 6-digit accuracy. Ship `techne/tools/mahler3.py`: Jensen + Kahan summation; unit test against Smyth m((1+x)(1+y)+z) = 7ζ(3)/(2π²).

**Identification:** for 50 smallest non-trivial m, LLL against basis {L'(f,0), L(f,3), ζ(3), log primes} at 40-digit precision.

**Null battery:**
- Permutation: shuffle coefficients within Newton polytope, re-scan.
- Detrending: subtract mean over Picard-rank strata.
- 5 RNG seeds.

## 5. Falsification

- **Primary:** permutation null bottom-50 indistinguishable (KS p > 0.1) from real K3 → "K3 Lehmer bound" is polynomial-degree artifact.
- **Secondary:** min m(P) across K3 < classical Lehmer (log 1.17628) → n=3 bound doesn't extend n=1. Genuine discovery, inverts the conjecture.
- **Tertiary:** LLL concentrates on log(primes) not L-values → cyclotomic contamination (prime-atmosphere lesson).

## 6. Budget

~8 CPU-hr on SpectreX5 (M2):
- 2h polynomial generation + canonical form.
- 4h Mahler integration (10^4 × ~1.5s, 8-core parallel).
- 1h permutation null (10× subsampled).
- 1h LLL + report.
Rhea batch; no babysitting.

## 7. Expected Outcome

Prior against clean Lehmer-K3 bound surviving Charon battery — Mahler minima crowd near cyclotomic limits; Deninger-Boyd identities are dim-1 (elliptic), not K3. Realistic win: **2-3 new candidate L-value identities** for weight-3 newforms (beyond Boyd's 1998 table), entered as Aporia verifiable conjectures. Bound itself: weak pass (z ∈ [1,3]), not the z=5 threshold.

**Word count: 786**
