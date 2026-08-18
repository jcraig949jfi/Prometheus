# Deep Research Report #150: Kloosterman Sum Distribution at Large Modulus

**Target Agent:** Ergon
**Date:** 2026-04-25
**Front:** Character sums (Kloosterman)
**Predecessor:** Sato-Tate-Kloosterman empirical sweep (Batch 7)

## 1. Problem Statement

The Kloosterman sum is

K(a, b; m) = Σ_{x mod m, gcd(x,m)=1} e^{2πi(ax + b x^{-1})/m},

where x^{-1} is the multiplicative inverse mod m. Weil's 1948 bound gives |K(a, b; m)| ≤ 2√m for m prime and gcd(ab, m)=1, motivating the normalized angle

θ(a, b; m) = arccos( K(a, b; m) / (2√m) ) ∈ [0, π].

Katz (1988) proved a *vertical* Sato-Tate law: with (a, b) fixed and the modulus m varying through primes, the angles θ(a, b; m) equidistribute with respect to the SU(2) Sato-Tate measure dμ_ST = (2/π) sin²θ dθ. The empirical question for Ergon is the *rate* of convergence, and whether any structured deviation appears — most notably the Heath-Brown-Patterson cubic-symmetry suggestion at moduli m ≡ 1 (mod 3).

## 2. Literature

- **Weil (1948):** original |K| ≤ 2√m bound from Riemann hypothesis for curves over finite fields.
- **Katz (1988), *Gauss Sums, Kloosterman Sums, and Monodromy Groups*:** Princeton AMS-116. Vertical Sato-Tate via geometric monodromy of Kl_2 sheaf = SU(2).
- **Sarnak (1990):** variance and additive twist statistics for Kloosterman sums.
- **Heath-Brown & Patterson (1979):** anomalous distribution of cubic Gauss sums; suggested possible cubic-symmetry residue in related exponential sums.
- **Friedlander & Iwaniec (2010), *Opera de Cribro*:** sieve identities consuming Kloosterman cancellation.
- **Fouvry, Kowalski & Michel (2014):** algebraic trace functions; modern framework treating K(a, b; m) as a trace function whose distribution is governed by monodromy.

## 3. LMFDB Data

Kloosterman sums are not a first-class LMFDB table — they must be computed directly. Cross-references for downstream calibration:

- `mf_newforms` (label, level, weight, dim, traces): Petersson trace formula expresses sums of Hecke eigenvalues against Kloosterman sums; useful as ground-truth oracle on small N.
- `lfunc_zeros` (origin, zeros): Kloosterman sums appear in the Selberg trace formula side; vertical Sato-Tate predictions can be cross-checked against zero-spacing statistics.
- `nf_fields` (disc, label): cubic-residue stratification needs primes split in Q(ζ_3).

Build at `ergon/scripts/kloosterman_sweep.py`: numpy-only modular inverse via `pow(x, -1, m)` (Python 3.8+), batched complex-exponential accumulation, optional FFT path for very large m.

## 4. Test Design

**Step 1.** Enumerate ~50 primes m ∈ [10^4, 10^6], roughly log-uniformly spaced.

**Step 2.** For each m, compute K(a, 1; m) for a ∈ {1, ..., 100}, yielding ~5000 angles per modulus and ~250K total samples.

**Step 3.** Bin angles into 50 equal-width bins on [0, π]. Compare empirical histogram to Sato-Tate density (2/π) sin²θ via Kolmogorov-Smirnov.

**Step 4.** Track KS distance D_m as a function of m; expected scaling D_m ~ m^{−1/4} (Sarnak heuristic) or m^{−1/2} (square-root cancellation).

**Step 5.** Stratify by cubic residue character: split primes m ≡ 1 (mod 3) into two groups by whether a is a cubic residue mod m. Test whether the two sub-distributions agree (Katz) or split (Heath-Brown-Patterson cubic symmetry survives).

**Step 6.** Sanity oracle: for ~5 small primes, verify K(1, 1; m) against a direct PARI/GP computation.

## 5. Falsification

- **Katz confirmed:** D_m → 0 monotonically with m; cubic-residue strata indistinguishable (KS p > 0.05).
- **Cubic-symmetry detected:** persistent KS gap between cubic-residue and non-residue strata at m ≡ 1 (mod 3), with the gap not shrinking with m → Heath-Brown-Patterson signal survives in the Kloosterman channel.
- **Catastrophic kill of either:** D_m fails to decay, or decays with wrong exponent → suggests a coding bug (modular inverse, sign convention) before any new mathematics.
- **Null:** uniform random angles in [0, π]; KS distance to Sato-Tate density ≈ 0.18, far from any genuine signal.

## 6. Budget

~6 hours total. Numpy direct computation handles m ≤ 10^5 in seconds per modulus (5000 angles × O(m) work each). For m near 10^6, switch to FFT-based evaluation of the inner exponential, ~30s per modulus. KS / stratification / plotting trivial.

## 7. Expected Outcome

Prior: Katz holds; KS distance decays as a clean power law; cubic stratification shows no anomaly (Heath-Brown-Patterson is a Gauss-sum phenomenon, not a Kloosterman one). The deliverable is a *measured* convergence exponent and a calibrated cubic-deviation null bar.

For Aporia void-detection, this matters because Kloosterman provides a **trace-function channel orthogonal to Hecke**: mod-m exponential structure that does not factor through automorphic eigenvalues. Combined with #157 (Burgess character sums) and #144 (Vinogradov three-primes), it forms an exponential-sum measurement basis. Voids in the operator tensor that survive Hecke probing but vanish under Kloosterman probing reveal that the missing structure is *additive-multiplicative* (mod-m geometry) rather than spectral. That stratification is the kind of orthogonal probe that turns "void" from a noun into a measurable.

**Word count: 748**
