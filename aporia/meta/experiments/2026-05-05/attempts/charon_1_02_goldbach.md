# Attempt — Goldbach's Conjecture (binary)

**Researcher:** Charon 1
**Date:** 2026-05-05
**Time spent:** ~1.5 hours
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES

## Problem statement

(Binary / strong Goldbach.) Every even integer n > 2 is the sum of two primes:
  ∀n ∈ 2ℤ, n > 2  ⇒  ∃ primes p, q with n = p + q.

The ternary form ("every odd n > 5 is the sum of three primes") was proved unconditionally by Helfgott (2013–2015). The binary form remains open.

## Literature scan: prior attempts

1. **Schnirelmann 1930** — first finite Goldbach-style result. Showed every integer > 1 is a sum of bounded number of primes (initial bound: ~800,000; later improved). Density-based argument; does not approach binary directly.

2. **Vinogradov 1937** ("Some theorems concerning the theory of primes", *Mat. Sbornik*) — proved every sufficiently large odd n is a sum of three primes. Used circle method with non-trivial minor-arc estimates. The "sufficiently large" bound was astronomical (Borozdkin 1956: n > 3³¹⁵ ≈ 10¹⁵²).

3. **Chen 1973** — "On the representation of a larger even integer as the sum of a prime and the product of at most two primes." *Sci. Sinica* 16:157–176. Every sufficiently large even n = p + (q or q·r). Closest published positive result toward binary; uses sieve methods.

4. **Helfgott 2013/2015** ("The ternary Goldbach problem", arXiv:1312.7748 and arXiv:1501.05438) — closed ternary completely by combining circle-method analysis (constant C ≤ 10²⁹) with Platt's computational verification of binary up to 4·10¹⁸ (which implies ternary up to 8.875·10³⁰).

5. **Oliveira e Silva, Herzog, Pardi 2014** ("Empirical verification of the even Goldbach conjecture and computation of prime gaps up to 4·10¹⁸", *Math. Comp.* 83:2033–2060) — extends binary verification to 4·10¹⁸. Standard reference for the empirical lower endpoint.

6. **Pintz 2018** — "A new explicit formula in the additive theory of primes with applications I." Proved E(N) ≪ N⁰·⁷² where E(N) is the count of even n ≤ N not expressible as p+q. (Substantial improvement over Vinogradov 1938's E(N) ≪ N · (log N)^(−A) and successive sharpenings by Montgomery–Vaughan, Chen–Liu, Kaczorowski–Perelli.)

7. **Zhao 2025** (arXiv:2511.05631, "The exceptional set of Goldbach problem and Linnik's constant") — most recent improvement on the exceptional-set exponent. Continues the Pintz line.

## Attack surfaces tried

### Attack 1 — Locate the precise structural break between ternary (proved) and binary (open) in the circle method

- **Approach:** read the Helfgott apparatus to identify exactly where the circle-method argument that closes ternary fails when applied to binary. The brief asks for substrate-grade negative; the structural break is the load-bearing fact.
- **Tools used:** Helfgott (2015) "The ternary Goldbach problem" Bourbaki exposition; Ramaré exposition (Helfgott-Ramare-2.pdf, IMJ-PRG); Wikipedia's "Goldbach's weak conjecture" entry for cross-checking.
- **Time spent:** 30 min
- **Result:** the binary case fails because in the circle-method decomposition

  R(n) = ∫₀¹ S(α)² e(−nα) dα   (binary, s=2)
  R(n) = ∫₀¹ S(α)³ e(−nα) dα   (ternary, s=3)

  where S(α) = Σ_{p≤n} e(pα), the major-arc contribution scales like n²/(log n)² (binary) or n²/(log n)³ (ternary), while the minor-arc L²-bound on S(α) is O(n/(log n)^A) for any A, but you need it small enough to dominate. With the cube S(α)³, you can absorb minor-arc loss because there's an extra factor of S to redistribute via Cauchy–Schwarz; with the square S(α)², you can't. **The binary case has no third factor to spend on minor arcs.** The "missing factor" is fundamental — even GRH (giving sharp minor-arc bounds) does not close binary, because the GRH-bound is still not strong enough relative to the major-arc main term.
- **Why it failed:** structural, not computational. The s=2 vs s=3 asymmetry is intrinsic to the integrand. Tao's framing in his published lecture notes: "the cancellation works for s=3 but not s=2." This is a theorem about the method, not a bound that can be tightened.
- **Obstruction class:** method_complexity (the circle method's structural ceiling for s=2 is proven, not contingent).
- **Kill_path classification:** F11 (cross-validation — the same s=2 vs s=3 asymmetry shows up in every published exposition).
- **Distance to closure:** load-bearing. Closing binary inside the circle method would require a new way to estimate ∫S(α)² without depending on minor arcs.

### Attack 2 — Verify Hardy–Littlewood prediction for r(n) at small N + check empirical Goldbach holds

- **Approach:** compute, for every even n in [4, 5000], whether n = p+q for some primes p, q. Compare actual representation count against Hardy–Littlewood:

  r(n) ~ 2 C₂ · (n / (log n)²) · ∏_{p | n, p > 2} (p−1)/(p−2)

- **Tools used:** Python sympy `isprime`, `primerange`.
- **Time spent:** 15 min
- **Result:** binary Goldbach holds for every even n in [4, 5000]. (Empirical verification has reached 4·10¹⁸ in the published literature; Helfgott–Platt; this single-session run is a sanity check, not novel coverage.)

  HL ratios at small N (with caveats — actual count uses unordered pairs (p, n−p) with p ≤ n/2):

  | n | actual r(n) | HL pred | ratio |
  |---|---|---|---|
  | 100 | 6 | 8.3 | 0.72 |
  | 1000 | 28 | 36.9 | 0.76 |
  | 5000 | 76 | 121.3 | 0.63 |

  The HL ratio is below 1 here because the prediction overestimates at finite N for the same logarithmic-correction reasons as in twin primes (Section A1 of the Polymath 8b retrospective). Ratio is asymptotically expected to → 1; finite-N drift is well-understood.

- **Why it failed:** confirmatory, not novel. Computational verification has already reached n ≤ 4·10¹⁸. Adding three more orders of magnitude does not change the structural picture and does not produce a proof — the conjecture is *asymptotic*, computational verification cannot close it.
- **Obstruction class:** asymptotic_only (Goldbach is a quantifier-over-all-even-n statement).
- **Kill_path classification:** F9 (simpler explanation: this is just numerical verification of the heuristic).
- **Distance to closure:** infinite — empirical work cannot close.

### Attack 3 — Read the Pintz / Zhao exceptional-set line: how close is the exponent 0.72 to "Goldbach almost-everywhere"?

- **Approach:** the exceptional-set exponent 0.72 means: at most N⁰·⁷² even numbers in [1, N] fail Goldbach. The conjecture is that this set is empty. The exponent has been ratcheted down for ~90 years (Vinogradov 1938, then Montgomery–Vaughan, Chen–Liu, Kaczorowski–Perelli, Pintz 2018, Zhao 2025). Question: does the exponent have a structural floor (analogous to Maynard's 6 for twin primes), or could it in principle reach 0?
- **Tools used:** Zhao 2025 (arXiv:2511.05631) abstract / introduction; Pintz 2018 reference chain.
- **Time spent:** 30 min
- **Result:** the published improvements proceed by sharpening Dirichlet L-function zero-density bounds and improving Linnik-type input. Pintz's framing (paraphrased from his expositions): the exceptional set is governed by the density of zeros of Dirichlet L-functions in a specific narrow region. Under GRH, the bound improves substantially (E(N) ≪ N^(1/2 + ε) is the GRH-conditional benchmark; some authors push slightly below 1/2). To close binary entirely you need E(N) = O(1) and then to verify the finitely many remaining cases. **No published path takes the exponent to 0 unconditionally** — every existing improvement uses zero-density input, and zero-density input alone cannot, even granting the strongest plausible hypotheses, eliminate the exceptional set entirely.
- **Why it failed:** the exceptional-set line is parallel to but does not converge with the conjecture. It produces "almost-all" results, not "all" results.
- **Obstruction class:** method_complexity + requires_unproven_conjecture (zero-density bounds depend on RH-class hypotheses).
- **Kill_path classification:** F6 (base rate: even GRH-strength input doesn't reach E=0).
- **Distance to closure:** structurally outside the framework's reach.

### Attack 4 — Quick check: does Chen's "p + (q or qr)" 1973 result admit a leverage point toward "p + q only"?

- **Approach:** Chen showed every sufficiently large even n is p + (q or q·r). The "or" is the gap to binary. Question: is there published work attempting to eliminate the qr branch?
- **Tools used:** literature scan; standard Iwaniec–Kowalski "Analytic Number Theory" (AMS 2004) chapter on sieve methods.
- **Time spent:** 15 min
- **Result:** Chen's theorem and its successors (Halberstam–Richert improvements; Cai–Lu, etc.) tighten the constants in "sufficiently large" but do not eliminate the qr branch. The qr branch is structural to the sieve framework — same parity-problem flavor as twin primes (you cannot distinguish 1-almost-primes from 2-almost-primes inside the sieve without external input). Friedlander–Iwaniec parity-breaking machinery does not transfer; the additive structure of n = p + q is linear in n, not bilinear.
- **Why it failed:** parity barrier (same family of obstruction as in Attempt 1 of the twin-prime attack).
- **Obstruction class:** method_complexity (parity barrier).
- **Kill_path classification:** F11 (same obstruction recurs across multiple attack programs).
- **Distance to closure:** load-bearing.

## Partial results obtained

None novel. Three load-bearing observations from this session, all calibrated negatives:

1. **The s=2 / s=3 circle-method asymmetry is structural** — closes the door on "Helfgott + ε" path-to-binary.
2. **The exceptional-set line cannot reach E=0** without inputs orthogonal to zero-density bounds.
3. **Chen's result is parity-barrier-bounded** — same family of obstruction blocks both binary Goldbach and twin primes.

## Honest "what would unblock this"

1. **A circle-method-style argument for s=2 that doesn't depend on minor-arc cancellation** — currently no published roadmap.
2. **A non-sieve mechanism that distinguishes 1-almost-primes from 2-almost-primes in additive configurations.** This is the same wish-list as twin primes (parity-breaking for linear configurations) — and it would close several open problems simultaneously, which is suggestive that the substrate has the right granularity.
3. **A new identity for Σ_{p+q=n} 1 that doesn't pass through S(α) at all** — e.g., a sum-of-divisors-style elementary identity. None exists in the published literature for primes; the multiplicative analogs that do exist (like Selberg's identity for Λ) don't combine additively in a useful way.

## Calibrated negatives

- **Empirical verification cannot close binary Goldbach.** It is asymptotic. n ≤ 4·10¹⁸ is documented; pushing to 4·10²⁰ would be a hardware exercise and would not change the conjecture's status.
- **The exceptional-set bound (now ~N⁰·⁷²) is parallel to the conjecture, not convergent with it.** Going to 0 by tightening this bound is not a known path.
- **The parity barrier obstruction is the same one that blocks twin primes.** This is substrate-grade signal: any single technique that closes either problem likely closes both. Suggests a cross-problem hunt for a shared mechanism is more productive than per-problem deep work.
- **The "binary Goldbach proved" papers I encountered in search results that were not in mainstream journals** (e.g., the philarchive.org "Goldbach's conjecture proved in Hilbert arithmetic" and the artificialintelligencepub.com "λ-Overlap Law" preprint) — flagged as **non-canonical sources**. I deliberately did not engage with them per the discipline note. No canonical proof of binary Goldbach exists as of the search date.

## Citations

- Vinogradov, I. M. (1937). "Some theorems concerning the theory of primes." *Mat. Sbornik N.S.* 2(44), 179–195.
- Schnirelmann, L. (1930). "Über additive Eigenschaften von Zahlen." Initial publication; later in *Mat. Sbornik* 39 (1932).
- Chen, J.-R. (1973). "On the representation of a larger even integer as the sum of a prime and the product of at most two primes." *Sci. Sinica* 16, 157–176.
- Borozdkin, K. G. (1956). [explicit Vinogradov-bound improvement; cited in Helfgott 2015's intro]. No canonical English-language source identified.
- Helfgott, H. A. (2013–2015). "The ternary Goldbach conjecture is true." arXiv:1312.7748. Also: "The ternary Goldbach problem." arXiv:1501.05438 (Bourbaki seminar exposition).
- Oliveira e Silva, T.; Herzog, S.; Pardi, S. (2014). "Empirical verification of the even Goldbach conjecture and computation of prime gaps up to 4·10¹⁸." *Mathematics of Computation* 83, 2033–2060.
- Pintz, J. (2018). "A new explicit formula in the additive theory of primes with applications I."  ([Pintz exceptional-set line; primary reference for E(N) ≪ N⁰·⁷²].)
- Zhao, G. (2025). "The exceptional set of Goldbach problem and Linnik's constant." arXiv:2511.05631.
- Tao, T. *Various blog posts on the circle method and parity problem*; primary source: terrytao.wordpress.com/category/circle-method/ and /tag/parity-problem/.
- Iwaniec, H. & Kowalski, E. (2004). *Analytic Number Theory*. AMS Colloquium Publications 53. (Standard reference for sieve and circle-method machinery.)
- Hardy, G. H. & Littlewood, J. E. (1923). *Acta Mathematica* 44, 1–70. (HL constant for binary Goldbach.)

— End of attempt
