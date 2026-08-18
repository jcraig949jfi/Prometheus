# Deep Research Report #151: Sum of Three Squares — Linnik Equidistribution Rate

**Target Agent:** Ergon
**Date:** 2026-04-25
**Front:** Analytic NT (Linnik / Iwaniec-Kowalski)

## 1. Problem Statement

For square-free n with n ≡ 1, 2, 3, 5, 6 (mod 8) — the Legendre-Gauss representable residues — the integer solutions to x² + y² + z² = n form a set R(n) ⊂ Z³ of size r₃(n). Projecting each solution to the unit sphere via v = (x, y, z)/√n produces r₃(n) points on S². Linnik's theorem (1968) asserts that as n → ∞ along the representable residues, the empirical measure (1/r₃(n)) Σ δ_{v} converges weak-* to the uniform Lebesgue measure σ on S².

Iwaniec-Kowalski ("Analytic Number Theory" 2004, Ch. 24) quantify the rate via subconvex bounds on Hecke L-functions of imaginary quadratic fields Q(√−n): the discrepancy D(n) between the empirical measure and σ satisfies D(n) = O(n^{−1/28}). Duke's 1988 sharpening of Iwaniec's 1987 theta-series bound corresponds to a conjectural rate of n^{−1/8} under GRH.

The empirical question: does the measured discrepancy on a 10K-sample of representable n up to 10⁶ scale as n^{−α} with α matching the Iwaniec-Kowalski exponent 1/28, the Duke-conjectural 1/8, or something else?

## 2. Literature

- **Linnik 1968** (*Ergodic Properties of Algebraic Number Fields*): qualitative equidistribution via ergodic action of class group on representations.
- **Iwaniec 1987** (*Invent. Math.* 87): theta-series bound, first quantitative rate via half-integral weight Hecke bounds.
- **Duke 1988** (*Invent. Math.* 92): sharpened spectral bound, subconvex L-function estimate giving the strongest unconditional rate.
- **Iwaniec-Kowalski 2004**, Ch. 24: textbook synthesis, n^{−1/28} explicit constant.
- **Michel-Venkatesh 2006** (*ICM*): subconvexity ⇒ equidistribution program, generalizes to Heegner points.
- **Status:** equidistribution proved unconditionally; the sharp rate n^{−1/8} is conjectural, requires Lindelöf for Hecke L-functions over Q(√−n).

## 3. LMFDB Data

- `mf_newforms`: weight-3/2 modular forms — the theta-series θ_Q(z) = Σ exp(2πi Q(x)z) for ternary quadratic forms Q live here; coefficients give r_Q(n).
- `lfunc_lfunctions`: Hecke L-functions on Q(√−n); subconvex bounds tested empirically via central-value distribution.
- `nf_fields`: imaginary quadratic NF data (disc < 0, degree 2) for class-group orders h(−n); Linnik bound h(−n) ≪ |d|^{1/2+ε}.
- Direct enumeration: Sage `IntegerListsLex` or PARI `qfminim(matid(3), n, n, 2)` returns all integer points on the sphere of radius √n; trivial up to n = 10⁶.

## 4. Test Design

**Step 1.** Enumerate 10K square-free n ≤ 10⁶ with n ≡ 1, 2, 3, 5, 6 (mod 8). Use `numbthy.is_squarefree` filter; stratify into 20 logarithmic bins of n.

**Step 2.** For each n, call `qfminim` to enumerate R(n); project to S² via v_i = (x_i, y_i, z_i)/√n. Confirm |R(n)| = r₃(n) via class-number formula (Gauss: r₃(n) = 12 h(−n) for n ≡ 1, 2 mod 4 etc.) — sanity check against `nf_fields` h.

**Step 3.** Bin S² into K ≈ 200 spherical caps of equal Lebesgue measure (HEALPix pixelization at N_side=4 gives 192 cells). Compute χ²(n) = Σ_k (observed_k − expected_k)² / expected_k, and the spherical KS-distance D_KS(n) per Cui-Freeden 2D test.

**Step 4.** Bin-aggregate D_KS(n) over the 20 log-bins of n; least-squares fit log D_KS = −α log n + c. Bootstrap 95% CI on α via 1000 resamples within bins.

**Step 5.** Compare α̂ to the analytical exponents 1/28 ≈ 0.0357 and 1/8 = 0.125. Null model: replace R(n) by r₃(n) i.i.d. uniform draws on S²; recompute D_KS; expect α_null = 1/2 (CLT for empirical discrepancy).

## 5. Falsification

- **Confirms Iwaniec-Kowalski:** α̂ ∈ [0.025, 0.045], i.e. within 0.01 of 1/28 → bound is empirically tight.
- **Indicates subconvex improvement:** α̂ ∈ (0.045, 0.125) → real rate beats Iwaniec-Kowalski but lies below Duke conjectural; flag as evidence for partial Lindelöf in this family.
- **Contradicts theorem (bug check):** α̂ > 0.125 + 0.01 → exceeds Duke conjectural; either binning artifact, qfminim miscount, or square-free filter bug. Not a mathematical kill — a pipeline kill.
- **Stratification surprise:** if α̂ averaged is normal but specific n with h(−n) anomalously large (Linnik-bound saturators) deviate by >3σ, those are anomaly cells.
- **Null sanity:** uniform-S² null must give α ≈ 0.5; if not, KS estimator is broken.

## 6. Budget

~6 hours. Sage `qfminim` over 10K n: ~30 min. HEALPix binning + KS via `astropy.healpix` and `scipy.stats`: ~1h. Fit, bootstrap, plotting: ~2h. Class-group cross-check against `nf_fields`: ~30 min. Writeup: ~2h.

## 7. Expected Outcome

Prior: α̂ ≈ 0.04–0.06, comfortably above Iwaniec-Kowalski's 1/28 lower bound, below Duke's 1/8. The value is **calibration**: a measured equidistribution exponent on a clean classical-NT testbed before the same machinery is pointed at speculative bridges (Heegner-point distribution on Shimura curves, ternary forms over real quadratic K). Anomaly cells — n where α̂ is significantly worse than the global fit — point either to class-group concentration (h(−n) saturating Linnik bound, fewer orbits to spread mass) or to Heegner-style structure analogous to `project_charon_two_channels.md`'s rank/regulator separability. For Aporia void-detection: a clean baseline calibrates the void-detector — once we know the expected discrepancy floor for this family, true voids (under-represented spherical regions across many n) become statistically isolable.

**Word count: 798**
