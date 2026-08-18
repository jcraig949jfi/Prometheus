# Deep Research Report #137: Arithmetic Progressions in OEIS Prime Sequences

**Target Agent:** Ergon
**Date:** 2026-04-23
**Topic:** Green-Tao-style empirics on OEIS prime-related sequences

## 1. Problem Statement

Green-Tao (2008): primes contain APs of arbitrary length. OEIS hosts hundreds of prime-built/filtered sequences: twin primes (A001097), Sophie Germain (A005384), n²+1 primes (A002496), Mersenne exponents (A000043), Ramanujan primes (A104272), etc. Each subset or transform has its own density profile.

**Q:** does empirical max AP length distribution across OEIS prime-related sequences match Green-Tao density prediction, or do structural filters (quadratic form, twin constraints) systematically suppress AP length below relative-density prediction?

Green-Tao gives existence; silent on *rate*. Positive-density A ⊂ primes with lower density δ should contain k-APs (relative Szemerédi) but first occurrence depends on A's pseudorandomness.

## 2. Literature

- **Green-Tao (2008)** Annals: APs in primes via transference to pseudorandom majorant.
- **Tao-Ziegler (2008)** Acta Math: polynomial progressions; prime-tuples in P(n).
- **Conlon-Fox-Zhao (2015):** simplified transference principle; weakened pseudorandomness.
- **Granville (2008):** quantitative bounds; first k-AP conjecturally near exp(k).
- **Frind-Jobling-Underwood (2004), PrimeGrid AP27 (2019):** longest known AP in primes = 27 terms.
- **Tao (2014) blog:** Green-Tao for Chen primes; transference robustness.

Gap: no systematic empirical survey across OEIS prime-filter taxonomy. Existing record-hunts target primes-only.

## 3. Data Sources

- **OEIS:** primary. Target sequences tagged `keyword:easy`, "prime" in name, ≥ 1000 b-file terms. Preliminary ~800 candidates; top 100 by term count is testable cut.
- **Literature records:** ground-truth calibration (twin-prime 3-AP, Sophie Germain 3-AP from Andersen).

## 4. Test Design

**A — Corpus.** Pull b-files for 100 prime-flavored sequences. Normalize: ascending integer lists, truncated to N = min(length, 10^6).

**B — Max AP detection.** Per S, max k such that AP of length k exists in S[:N]. O(|S|² log|S|) via common-difference hashing. For |S|=10^6, use sparse difference counting with early termination at k=25.

**C — Density normalization.** δ(S) = |S ∩ [1,X]| / π(X). Green-Tao + Szemerédi heuristic: first k-AP near X_k(S) ≈ exp(C·k/δ(S)) for pseudorandom S. Residual r(S, k) = log X_k^observed − log X_k^predicted.

**D — Stratification.**
- Multiplicative (Sophie Germain, safe primes)
- Additive (twin, cousin, sexy)
- Quadratic-form (n²+1, n²+n+41)
- Transcendentally indexed (Ramanujan, Mersenne exponents)

Test whether r(S,k) has zero mean per stratum vs primes baseline.

**E — Null.** Random subsets of primes with matching density; 500 resamples per sequence. Claim is "observed onset diverges from density prediction," not "APs exist" (Green-Tao guarantees).

## 5. Falsification

Pre-registered kills:
1. **Density suffices:** residuals |mean| < 0.3 and KS p > 0.1 against density-matched null across all strata → density alone explains onset.
2. **Strata indistinguishable:** per-stratum ANOVA p > 0.05 after Bonferroni → filter type irrelevant.
3. **Record artifact:** if results driven by top-5 record-heavy sequences, drop them and re-run.
4. **Permutation null:** shuffle sequence-to-stratum 10^4 times; observed stratum variance must exceed 99th percentile.

Charon battery: 8-test; at least 6 must survive for hypothesis to graduate.

## 6. Budget

- OEIS b-file scrape: 0.5 CPU-hr (rate-limited 1 req/sec).
- Max-AP on 100 sequences N ≤ 10^6: ~4 CPU-hr (difference-hashing).
- Density nulls + permutation: 1 CPU-hr.
- Battery + writeup: 0.5 CPU-hr.
- **Total: ~6 CPU-hr.**

## 7. Expected Outcome

**75%:** density-normalized residuals flat within strata — Green-Tao + relative Szemerédi already predicts. Calibration kill confirming density is dominant variable; useful negative control for Aporia Void Detector.

**20%:** quadratic-form-filtered primes (n²+1, Landau sequences) show AP suppression at z ≥ 2 — pseudorandomness deviates from Cramér. Publishable empirical finding bridging OEIS taxonomy and additive combinatorics.

**5%:** Ramanujan-prime or transcendentally-indexed show AP **enrichment** — genuine anomaly warranting deeper investigation.

Prime atmosphere: 96%+ cross-dataset structure is primes; detrending = density normalization, built into Step C.

**Word count: 762**
