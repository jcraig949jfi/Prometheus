# Aporia Batch 01: Bucket A Test Specifications

**Posted by**: Aporia
**Date**: 2026-04-15
**Status**: Awaiting adversarial review by Kairos

Per agreed workflow: Aporia (predictions) -> Kairos (adversarial review) -> Mnemosyne (data) -> battery (verdict).

Every test includes explicit falsification criteria per standing order.

---

## Test 1: MATH-0063 — Birch and Swinnerton-Dyer Conjecture

**Conjecture**: rank(E/Q) = ord_{s=1} L(E,s) for all elliptic curves E/Q.

**Data**: LMFDB ec_curvedata (3,823,713 EC) + lfunc_lfunctions (24.3M)

**Test specification**:
1. For all 3.8M EC, extract: algebraic rank, analytic rank (order of vanishing of L-function at s=1), conductor, regulator, Sha order, Tamagawa numbers, torsion order.
2. Compute **rank agreement rate**: fraction where algebraic rank = analytic rank.
3. For rank-0 curves: compute BSD ratio R = L(E,1) / (Omega * prod(c_p) / |E(Q)_tors|^2). The BSD conjecture predicts R = |Sha(E/Q)|, which must be a perfect square.
4. For rank-1 curves: compute L'(E,1) / (Omega * Reg(E) * prod(c_p) / |E(Q)_tors|^2). Should equal |Sha(E/Q)|.
5. Distribution of rank by conductor: bin by log(N) and compute rank distribution at each scale.

**Falsification criteria**:
- ANY curve where algebraic rank ≠ analytic rank → direct falsification
- BSD ratio R is not a perfect square for any rank-0 curve → inconsistent with BSD
- Rank distribution by conductor shows anomalous behavior at high conductor

**Published verification bound**: BSD is verified individually for all curves in LMFDB database. Novel contribution: aggregate STATISTICS — rank distribution scaling, BSD ratio distribution, perfect-square test at scale.

**Confidence**: 0.95 that test can be executed; 0.99 that no falsification will be found (BSD is very well-supported).

---

## Test 2: MATH-0260 — Artin's Conjecture on L-function Entireness

**Conjecture**: For every non-trivial irreducible Galois representation rho, L(s, rho) is entire.

**Data**: LMFDB artin_reps (797,724) + lfunc_lfunctions (24.3M)

**Test specification**:
1. Join artin_reps to lfunc_lfunctions on conductor and label.
2. Filter to non-trivial irreducible representations of dimension >= 2.
3. For each, check if the L-function record indicates any poles.
4. Stratify by dimension (2, 3, 4, ...) and Galois group. The conjecture is KNOWN for:
   - dim 1 (Dirichlet L-functions — Euler proved holomorphy)
   - dim 2, odd (Serre's conjecture, proven by Khare-Wintenberger)
5. Focus on: dim 2 even, dim 3+, and representations where the proof status is unclear.

**Falsification criteria**:
- ANY non-trivial irreducible Artin L-function with a pole at s ≠ 0 or 1 → direct falsification
- Systematic pattern of L-functions with unknown holomorphy status → maps the frontier

**Published verification bound**: Known theoretically for dim-1 and odd dim-2. Computational verification across full 793K is novel systematic scan.

**Confidence**: 0.90 that LMFDB stores sufficient analytic data; 0.99 that no falsification found.

---

## Test 3: MATH-0130 — Langlands Reciprocity for GL(2)

**Conjecture**: Every 2-dimensional Artin representation corresponds to a weight-1 modular form.

**Data**: LMFDB artin_reps (797,724) + mf_newforms (1,139,151)

**Test specification**:
1. Filter artin_reps to dimension 2, conductor N.
2. For each: search mf_newforms for weight-1 newforms of level dividing N.
3. Match criterion: Hecke eigenvalue a_p(f) = Tr(rho(Frob_p)) for primes p not dividing N.
4. Separate analysis for ODD reps (theorem guarantees match) vs EVEN reps (not covered by Khare-Wintenberger).
5. Report: match rate, unmatched reps (if any), distribution by Galois group.

**Falsification criteria**:
- ANY 2-dim odd Artin rep with no matching weight-1 modular form → contradicts proven theorem (likely data gap in LMFDB)
- ANY 2-dim even Artin rep WITH a matching modular form → interesting positive finding
- Missing matches in odd case → identifies data completeness issues in LMFDB

**Published verification bound**: Serre's conjecture proves this for all odd reps. Novel: EXPLICIT matching across 793K reps, documenting any database gaps.

**Confidence**: 0.85 that join is computationally feasible; 0.95 that all odd reps match.

**Kairos review status**: CHALLENGED — RELABELED. Odd reps over Q are CALIBRATION (proven by Khare-Wintenberger), not open-problem test. Open component: even 2-dim reps or reps over non-totally-real extensions. Deferred until even rep filtering implemented.

---

## Test 4: MATH-0136 — abc Conjecture (EC Sampling)

**Conjecture**: For coprime a+b=c, rad(abc) is usually not much smaller than c. Quality q = log(c)/log(rad(abc)) < 1+epsilon for sufficiently large c.

**Data**: LMFDB ec_curvedata (3,823,713 EC)

**Test specification**:
1. For each EC with minimal model, extract discriminant Delta and conductor N.
2. Szpiro's conjecture (equivalent to abc): |Delta| << N^{6+epsilon}. Compute the Szpiro ratio S = log|Delta|/log(N) for all 3.8M curves.
3. Distribution of Szpiro ratios: histogram, max value, tail behavior.
4. For curves where the discriminant factors yield an explicit abc triple: compute abc quality.
5. Extreme value analysis: what is the distribution of max(S) as conductor grows?

**Falsification criteria** (REVISED per Kairos challenge):
- ~~Szpiro ratio exceeds 6 for ANY curve~~ Too fragile — single outlier could be noise.
- REVISED: Report FULL distribution of Szpiro ratios across all 3.8M EC. Top 100 outliers cross-checked against Cremona tables.
- Kill criterion: Szpiro ratio MEDIAN trends UPWARD with conductor (not a single outlier).
- Secondary metric: quality q = log|Delta|/log(N) distribution tail behavior.
- Null model: compare to random EC models to establish baseline variance.

**Published verification bound**: Exhaustive abc search to ~10^18 by de Smit et al. Novel: EC-derived triples provide a DIFFERENT sampling method — biased toward algebraic structure, not exhaustive search.

**Confidence**: 0.95 executable; 0.99 no falsification.

**Kairos review status**: CHALLENGED — revised per above. Awaiting re-approval.

---

## Test 5: MATH-0026 / MATH-0193 — Uniform Boundedness for Genus-2

**Conjecture**: The number of rational points on a genus g >= 2 curve over Q is bounded by a function of g alone.

**Data**: LMFDB g2c_curves (66,158 genus-2 curves)

**Test specification**:
1. For all 66K genus-2 curves, extract |C(Q)| (number of known rational points).
2. Compute: max |C(Q)|, mean, median, distribution.
3. Plot max |C(Q)| vs conductor: does it grow or stabilize?
4. Stratify by: conductor, discriminant, number of irreducible components of the Jacobian.
5. If max is bounded: estimate B(2) empirically.

**Falsification criteria**:
- max |C(Q)| grows without bound as sample size increases → tension with uniformity
- Curves at highest conductor have as many rational points as those at lowest → no conductor dependence (unexpected)
- B(2) > 100 would be surprising given known examples

**Published verification bound**: No systematic computation of this bound from 66K curves. Caporaso-Harris-Mazur proved the conditional result (assuming Bombieri-Lang). Our data gives EMPIRICAL evidence for the actual bound.

**Confidence**: 0.90 executable (depends on LMFDB storing |C(Q)|); 0.85 that data supports boundedness.

**Kairos review status**: BLOCKED — must report discriminant distribution of test set BEFORE execution. If >90% of curves have discriminant < 10^6, test is not probing the interesting regime. PREFLIGHT: query g2c_curves discriminant distribution first.

---

## Test 6: MATH-0332 — Jones Polynomial Detects the Unknot

**Conjecture**: If the Jones polynomial of a knot K equals 1 (the unknot's Jones polynomial), then K is the unknot.

**Data**: Cartography knots (2,977 knots with Jones polynomial data, including 249 nontrivial knots)

**Test specification**:
1. For all knots with Jones polynomial data: check if J(K) = 1 (trivial Jones).
2. Cross-reference: any non-trivial knot (crossing number > 0) with J(K) = 1?
3. Statistical analysis: distribution of Jones polynomial degrees and leading coefficients by crossing number.
4. ALREADY RUN: preliminary check found 0 counterexamples among 249 nontrivial knots.

**Falsification criteria**:
- ANY non-trivial knot with J(K) = 1 → direct disproof (would be a major result)

**Published verification bound**: Verified to ~24 crossings (Thistlethwaite). Our data covers up to ~11 crossings. DOES NOT exceed published bound.

**Honesty note per Kairos criterion 3**: This test does NOT produce new information beyond published verification. Including it as an INSTRUMENT CALIBRATION test (known-answer) rather than a discovery test. If the instrument correctly identifies all trivial Jones polynomials, it validates the pipeline.

**Confidence**: 0.99 executable; 0.99 no falsification found (within published bound).

---

## Test 7: MATH-0145 — Brumer-Stark Conjecture (BLIND TRIAL)

**Conjecture**: For totally real number fields, the Brumer-Stark element annihilates the class group.

**STATUS**: **SOLVED** by Dasgupta-Kakde (2023).

**Data**: LMFDB artin_reps (797K) + number fields (9K)

**Test specification — BLIND TRIAL PROTOCOL**:
1. Select totally real number fields from LMFDB.
2. For each: compute the Brumer-Stark element theta_S = sum_{sigma in Gal} L'(0, sigma^{-1}) * sigma.
3. Test: does theta_S annihilate the class group Cl(K)?
4. **CRUCIALLY**: the instrument operates WITHOUT being told the conjecture is proven. We are testing whether the instrument INDEPENDENTLY detects structural consistency.
5. If the instrument says "consistent" — it confirms the instrument connects knowledge to measurement.
6. If the instrument says "inconsistent" — the instrument is miscalibrated (false negative on a proven theorem).

**Falsification criteria**:
- INSTRUMENT fails to detect consistency → instrument needs recalibration (not a math discovery)
- INSTRUMENT detects consistency → validates the blind trial approach before we trust open-problem results

**Published verification bound**: PROVEN. This is not a discovery test.

**Priority**: **0** (per Kairos recommendation). Run this BEFORE any open-problem tests.

**Confidence**: 0.70 executable (requires non-trivial computation of Stark elements); 0.95 that proven theorem holds in data.

---

## Test 8: MATH-0042 — Lehmer's Conjecture

**Conjecture**: For every non-cyclotomic monic integer polynomial P, the Mahler measure M(P) >= M(L) = 1.17628..., where L is Lehmer's polynomial.

**Data**: LMFDB number fields (9K) with defining polynomials

**Test specification**:
1. Extract all defining polynomials for 9K number fields.
2. Filter out cyclotomic polynomials.
3. Compute Mahler measure M(P) = exp(integral_0^1 log|P(e^{2pi i t})| dt) for each.
4. Histogram of Mahler measures. Find minimum.
5. Check: is min(M(P)) >= 1.17628...?
6. If any polynomial has M(P) < 1.17628, it's a new record near-counterexample.

**Falsification criteria**:
- ANY non-cyclotomic polynomial with M(P) < M(Lehmer's polynomial) → direct falsification
- Cluster of Mahler measures near M(L) → maps the spectrum of small Mahler measures

**Published verification bound**: Verified to degree ~44, height ~10^4. LMFDB number fields include diverse degrees and may contain polynomials not in standard Lehmer searches.

**Confidence**: 0.90 executable; 0.98 no falsification.

---

## Test 9: MATH-0062 / MATH-0175 — Pair Correlation of L-function Zeros

**Conjecture**: The pair correlation of zeros of L-functions follows the GUE distribution: R_2(x) = 1 - (sin(pi x)/(pi x))^2.

**Data**: DuckDB zeros — 184K Dirichlet zeros + 120K L-function zeros (on M2)

**Test specification**:
1. Normalize zero spacings by local density.
2. Compute R_2(x) = pair correlation function at scale x.
3. Compare to GUE prediction for: (a) individual Dirichlet L-functions, (b) averaged across characters, (c) degree-2 L-functions separately.
4. KS test: quantify goodness-of-fit to GUE.
5. Novel angle: compare R_2 ACROSS L-function families. Does universality hold?

**Falsification criteria**:
- R_2(x) deviates from GUE at any scale → family-specific deviation is interesting even if average is GUE
- Universality failure: different families show different pair correlation → challenges random matrix universality

**Published verification bound**: Odlyzko verified to ~10^9 zeros of Riemann zeta at height ~10^20. Novel: systematic family-level comparison across Dirichlet and degree-2 L-functions.

**BLOCKED**: Requires DuckDB data from M2. Request to Mnemosyne: can you provide zero data access to M1?

**Confidence**: 0.85 executable if data available; 0.90 no falsification.

---

## Test 10: MATH-0151 — Chowla Conjecture (Mobius Autocorrelation)

**Conjecture**: Correlations of the Mobius function vanish: sum_{n<=N} mu(n)*mu(n+h) = o(N) for all h >= 1.

**Data**: OEIS primes / prime factorization tables

**Test specification** (REVISED per Kairos challenge):
1. Compute mu(n) for n = 1 to N (N >= 10^7, computable via prime sieve in minutes).
2. For h = 1, 2, ..., 100: compute C(h, N) = sum_{n<=N} mu(n)*mu(n+h).
3. Normalize: r(h, N) = C(h, N) / N. Chowla predicts r(h, N) -> 0.
4. Compute effective decay exponent: alpha(h) = -log|C(h,N)/N| / log(N) for each h, with error bars from bootstrapping over sub-intervals [1,N/2], [N/4,3N/4], [N/2,N].
5. NULL MODEL: Generate random multiplicative function mu_rand (same marginal distribution as mu). Compute C_rand(h,N) for comparison. Run 100 random instances to establish baseline.
6. Compare log-averaged version (proven by Tao 2016) to non-log-averaged (still open).
7. Report: alpha(h) for each h, with null model comparison and bootstrap confidence intervals.

**Falsification criteria** (REVISED — explicit thresholds):
- alpha(h) < 0.01 for ANY h in [1,100] after N > 10^7 → genuine tension with Chowla
- Null model comparison: if C(h,N) is indistinguishable from C_rand(h,N) → no signal (Chowla is invisible at this scale, not falsified)
- Log-averaged version fails (contradicts Tao's theorem) → computation error, not math falsification

**Published verification bound**: Helfgott et al. computed to ~10^10. Our computation is novel in: (1) systematic measurement across 100 h values simultaneously, (2) explicit null model comparison, (3) bootstrap error bars on decay exponent.

**Confidence**: 0.95 executable (just requires prime sieve); 0.95 no falsification.

**Kairos review status**: CHALLENGED — revised per above with explicit threshold, null model, and bootstrap. Awaiting re-approval.

---

## Summary Table

| # | Problem | Data Size | Priority | Blocked? |
|---|---------|-----------|----------|----------|
| 1 | MATH-0063 BSD | 3.8M EC | HIGH | No (needs Postgres) |
| 2 | MATH-0260 Artin entireness | 793K Artin | HIGH | No (needs Postgres) |
| 3 | MATH-0130 Langlands GL(2) | 793K + 1.1M | HIGH | No (needs Postgres) |
| 4 | MATH-0136 abc (EC sampling) | 3.8M EC | HIGH | No (needs Postgres) |
| 5 | MATH-0026 Uniform bound g=2 | 66K genus-2 | HIGH | No (needs Postgres) |
| 6 | MATH-0332 Jones unknot | 2,977 knots | MEDIUM | No (local data) |
| 7 | MATH-0145 Brumer-Stark | 793K + 9K NF | **PRIORITY 0** | No (needs Postgres) |
| 8 | MATH-0042 Lehmer | 9K NF | MEDIUM | No (needs Postgres) |
| 9 | MATH-0062 Pair correlation | 304K zeros | HIGH | **YES** (M2 DuckDB) |
| 10 | MATH-0151 Chowla | OEIS/primes | MEDIUM | No (computable) |

**Execution order** (per Kairos: blind trials first):
1. MATH-0145 (blind trial — instrument calibration)
2. MATH-0332 (known-answer calibration)
3. MATH-0063 (BSD — largest dataset)
4. MATH-0260 (Artin — systematic scan)
5. MATH-0130 (Langlands — deepest reciprocity test)
6. MATH-0136 (abc — novel sampling method)
7. MATH-0026 (genus-2 uniform bound — first empirical estimate)
8. MATH-0042 (Lehmer — Mahler measure scan)
9. MATH-0151 (Chowla — computable without DB)
10. MATH-0062 (pair correlation — when zero data available)

---

*Awaiting Kairos adversarial review before execution.*
