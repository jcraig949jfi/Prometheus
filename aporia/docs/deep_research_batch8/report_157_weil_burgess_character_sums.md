# Deep Research Report #157: Weil Bound and Burgess Refinement Empirics

**Target Agent:** Ergon
**Date:** 2026-04-25
**Front:** Analytic NT / character sums

## 1. Problem Statement

For a non-trivial Dirichlet character χ mod p, the partial sum S_χ(M, N) = Σ_{n=M+1}^{M+N} χ(n) is the fundamental object of multiplicative analytic NT. The Pólya–Vinogradov (PV) inequality gives |S_χ(M, N)| ≤ √p log p uniformly in M, N — sharp for full-period sums (N ≈ p) but vacuous when N < √p log p. Weil's Riemann hypothesis for curves over finite fields refines PV by removing the log factor for *complete* sums (N = p − 1), giving |S_χ| ≪ √p. Burgess (1957–1963) attacked the *short* regime: for any integer r ≥ 2,

|S_χ(M, N)| ≪_r N^{1−1/r} p^{(r+1)/(4r²)+ε}.

This breaks the PV barrier whenever N ≥ p^{1/4+ε}, the only known unconditional improvement in the range p^{1/4} ≤ N ≤ √p. The empirical question: at LMFDB scale, do real characters saturate Burgess, or is the true exponent strictly smaller (suggesting room for improvement)?

## 2. Literature

- **Weil (1948), *Sur les courbes algébriques et les variétés qui s'en déduisent*:** RH for curves → √p bound for complete character sums.
- **Burgess (1957, *Mathematika*; 1962, *Proc. LMS*; 1963, *J. LMS*):** original short-sum bound and its iterated form for r ≥ 2.
- **Iwaniec–Kowalski (2004), *Analytic Number Theory*, Ch. 12:** standard reference, derivation of Burgess from Weil + Hölder.
- **Heath-Brown (2013), *Acta Arith.* 162:** hybrid Burgess–PV bounds in mixed regimes.
- **Conrey–Iwaniec (2000), *Annals* 151:** cubic moments of L-functions yielding subconvexity, implicitly Burgess-tight.
- **Polymath (2020+) Burgess survey:** consolidated explicit constants and r-optimization tables.

## 3. LMFDB Data

- `char_dir_values`: Dirichlet character values indexed by (modulus, conductor, label, order); values stored as roots-of-unity exponents.
- `char_dir_orbits`: primitive-character Galois orbits, ~10^7 rows; orbit_label, parity, is_primitive, conductor.
- `lfunc_lfunctions`: Dirichlet L-function central values and low zeros; Euler factors give χ(p) at small primes for cross-check.
- `mf_newforms`: weight-1 forms encoding Galois reps with χ-twist data.

Direct character enumeration via Sage `DirichletGroup(p)`; LMFDB cross-checks the sign of χ(−1) and conductor for primitivity.

## 4. Test Design

**Step 1.** For each prime p ∈ {1009, 10007, 100003}, enumerate all primitive non-trivial χ mod p via `DirichletGroup(p).list()` (filter modulus(χ) = p). Counts: 1007, 10005, 100001 characters respectively.

**Step 2.** For each χ and N ∈ {⌈p^{1/4}⌉, ⌈p^{1/2}⌉, ⌈p^{3/4}⌉, p−1}, compute MaxS(χ, N) = max_{0 ≤ M < p} |S_χ(M, N)|. Use FFT-based circular convolution: pad χ-vector, convolve with indicator of length-N window — O(p log p) per χ-N pair.

**Step 3.** Aggregate over characters. For each (p, N) compute median, 95th percentile, and max of MaxS(χ, N) across χ.

**Step 4.** Fit log MaxS vs log p (fixed N/p ratio) and log N (fixed p) via OLS to extract empirical exponents α (in p) and β (in N). Burgess predicts α = (r+1)/(4r²), β = 1 − 1/r for r ∈ {2, 3, 4}; PV–Weil predicts α = 1/2, β = 0 (with log).

**Step 5.** Stratify by character order (quadratic, cubic, quartic, high-order) to detect order-dependent saturation.

**Metrics:** observed (α, β) with bootstrap CIs; per-r residual against Burgess prediction; identity of extremal χ saturating each bound.

## 5. Falsification

- **Confirmed:** observed α within 0.1 of Burgess (r+1)/(4r²) at r minimizing the bound for given N → Burgess sharp at LMFDB scale.
- **Sub-Burgess:** observed exponent below Burgess across all three p → either finite-size noise (small p^{1/4} regime contaminated by lower-order terms) or genuine improvement; require p = 10^6 confirmation before claiming.
- **Strong kill:** observed α > 1/2 + ε (super-PV–Weil) sustained across p → bug in FFT convolution or character indexing; halt and audit.
- **Null:** randomized χ (uniform ±1 ± i on unit circle, multiplicative property removed) must give √N random-walk scaling; deviation from √N flags implementation error.

## 6. Budget

~6 hours. Sage character enumeration + FFT partial sums: ~1h for p = 1009 (10^6 ops), ~1h for p = 10007 (10^8 ops), ~3h for p = 100003 (10^{10} ops, requires numpy-FFT, not pure-Sage). Fit + writeup ~1h. GPU FFT optional for p = 10^6 stretch goal.

## 7. Expected Outcome

First LMFDB-scale empirical calibration of Burgess exponent saturation across the full primitive-character spectrum mod p for three decadal primes. Identifies the extremal χ (likely quadratic or low-order at primes with small class number) where S_χ saturates, providing concrete targets for the next refinement of Burgess. **Connects Aporia void-detection:** character sums are the underlying technology for Linnik's constant (#151), Kloosterman sum bounds (#150), and the explicit form of the Weil zeta function. Establishing the measurement protocol here calibrates downstream void-detectors — any subsequent claim of "Burgess-tight" or "sub-Burgess" behavior in derived L-function moments must reduce to this primitive measurement, preventing inflated claims at higher levels of the analytic NT stack.

**Word count: 748**
