# Research Package 13: BSD Invariants in L-Function Zero Space
## Priority: HIGHEST — mechanistic explanation for the spectral tail finding
## Triggered by: Wachs (2026) discovery in Package 3 prior art review

---

## Context

Wachs (2026), "BSD Invariants and Murmurations of Elliptic Curves," demonstrated that
within rank-0 elliptic curves, curves with Tate-Shafarevich order ≥ 4 have systematically
different zero distributions: the first zero is displaced higher, subsequent zeros pack
more tightly. He used Hotelling's T² test to confirm this.

Our spectral tail finding shows that removing the first L-function zero monotonically
improves rank clustering (ARI: 0.5456 → 0.5548). The Wachs result provides a candidate
mechanism: the first zero encodes non-rank BSD invariants (Sha, Tamagawa, real period)
that add variance irrelevant to rank clustering. Removing it strips that confound.

We are now running two experiments on our 31K EC dataset:
1. **Sha Stratification Test**: Does the ablation improvement vanish when Sha is controlled?
2. **BSD Invariant Decomposition**: Do Sha, regulator, Faltings height, and modular degree
   predict position in zeros 5-19 space independently of rank and conductor?

This research package seeks the theoretical and literature context for interpreting results.

## Specific Questions

1. **What is the quantitative relationship between Sha order and first-zero height?**
   Wachs observed displacement — is there a formula? Does the BSD formula
   (L'(1)/Omega = (Sha · Tam · Reg) / |E_tor|²) predict a specific functional
   relationship between Sha and the first zero's position?

2. **Has anyone decomposed L-function zero positions into contributions from
   individual BSD invariants?** Not just showing correlation, but decomposing the
   variance of zero positions into components attributable to Sha, Tamagawa, regulator,
   real period, and torsion.

3. **The Tamagawa product and zero geometry.** Tamagawa numbers encode local reduction
   behavior at bad primes. Is there a known mechanism by which local data at bad primes
   influences the global zero distribution beyond the conductor?

4. **The regulator and higher zeros.** The regulator measures the "size" of the
   Mordell-Weil lattice. For rank-1 curves, does the regulator value predict anything
   about zeros 5-19 (the spectral tail)? Is there a mechanism by which regulator
   information leaks into the bulk zero distribution?

5. **Has anyone used BSD invariants as ML features for elliptic curve classification
   beyond rank prediction?** E.g., predicting isogeny class, Galois image, CM status,
   or torsion structure from combinations of BSD invariants.

6. **The Faltings height and zero geometry.** The Faltings height is an intrinsic
   invariant of the curve measuring arithmetic complexity. Does it correlate with
   zero distribution statistics? Is there a known formula connecting Faltings height
   to L-function zeros?

7. **Non-rank invariants in the spectral tail specifically.** Wachs showed the first
   zero carries Sha information. Do higher zeros also carry BSD invariant information?
   If the spectral tail (zeros 5-19) is independent of all BSD invariants, that's
   strong evidence for a residual geometric signal. If it correlates, it tells us
   which invariant the tail encodes.

## Key Papers to Check
- Wachs (2026) — "BSD Invariants and Murmurations of Elliptic Curves"
- Birch, Swinnerton-Dyer — the BSD formula and its computational consequences
- Watkins — "Computing the modular degree of an elliptic curve" (2002)
- Cremona — tables and BSD verification for conductor ≤ 500,000
- Goldfeld — conjectures on rank distribution and L-function behavior
- Any papers connecting the Faltings height to L-function zero statistics
- Any ML work using BSD invariants (Sha, Tamagawa, regulator) as features

## What Would Kill Our Mechanistic Claim
- If Sha has NO measurable effect on zero positions in our dataset → Wachs mechanism
  doesn't operate at our scale
- If zeros 5-19 correlate strongly with Sha → the spectral tail IS the Sha signal,
  not a residual beyond it

## What Would Strengthen It
- If Sha affects only the first 1-4 zeros and zeros 5-19 are Sha-independent → clean
  separation supports feature-engineering interpretation
- If the BSD formula predicts a quantitative zero displacement that matches our data →
  first-principles mechanistic explanation
