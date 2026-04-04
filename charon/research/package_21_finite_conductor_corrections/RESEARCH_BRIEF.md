# Research Package 21: Finite-Conductor Corrections to Katz-Sarnak Universality
## For: Google AI Deep Research
## Priority: HIGH — determines whether the RMT gap is structural or transient

---

## Context

We ran an RMT simulation: GUE with 2 pinned zeros at origin (modeling rank-2 curves)
vs unpinned (rank-0). K-means on simulated zeros 5-19 gives ARI = 0.44. Our empirical
data gives ARI = 0.49 within SO(even). Gap = 0.05 (~2 sigma).

Separately, we measured the spectral tail ARI across conductor bins:
- Conductor 1K-2K: ARI = 0.590 (SO(even), few strata)
- Conductor 2K-3K: ARI = 0.527
- Conductor 3K-5K: ARI = 0.461

The signal weakens at higher conductor. This raises a critical question: is the 0.05
RMT gap a FINITE-CONDUCTOR CORRECTION that will vanish as N -> infinity? If so, the
residual is not "new arithmetic" — it's a pre-asymptotic effect that happens to be
detectable at conductor <= 5000.

## Specific Questions

1. **What are the known finite-conductor correction terms to Katz-Sarnak 1-level densities?**
   The asymptotic limit is well-understood. What are the O(1/log N) or O(1/N) corrections?
   Are they computed explicitly for elliptic curve families?

2. **Rate of convergence to RMT universality.** How fast do zero statistics of L-function
   families converge to their predicted RMT distributions as conductor grows?
   - Is there a theorem bounding the convergence rate?
   - Are there numerical studies measuring convergence for elliptic curves specifically?
   - At conductor 5000 (log N ≈ 8.5), how far are we from the asymptotic regime?

3. **The "excised ensemble" model.** Keating, Snaith, and others developed models where
   random matrices are conditioned on their characteristic polynomial exceeding a cutoff
   at the central point. This models the fact that L(1/2) for rank-0 curves can't be
   too small. Does this excised model predict different clustering properties for
   zeros 5-19 compared to pure GUE? Could it explain our 0.05 gap?

4. **Lower-order terms in the explicit formula.** The explicit formula connecting zeros
   to primes has a main term (from conductor/degree) and lower-order terms (from
   Gamma factors, root number, etc.). At conductor 5000, how large are these lower-order
   terms relative to the main term? Could they produce systematic shifts in zeros 5-19
   that pure RMT doesn't capture?

5. **Conductor-dependent clustering.** Has anyone studied how the distinguishability of
   L-function families changes with conductor? E.g., at conductor 100 vs 1000 vs 10000,
   does the ability to separate SO(even) from SO(odd) by their zeros change? What about
   within-family rank discrimination?

6. **Arithmetic conductor vs analytic conductor.** For elliptic curves, the arithmetic
   conductor N and the analytic conductor q = N / (2*pi)^2 differ by a constant factor.
   But the Gamma factors in the functional equation also contribute to the analytic
   conductor. At conductor 5000, are there meaningful differences between normalizing
   by N vs q? Could this explain systematic deviations from pure RMT?

7. **The Sha/Tamagawa modulation at finite conductor.** Murmuration studies show that
   Sha >= 4 curves have systematically displaced first zeros. At conductor 5000, what
   fraction of curves have non-trivial Sha? Is the "BSD wall" at zero 2 potentially
   a finite-conductor artifact that would weaken at conductor 50,000?

## Key Papers to Start From

- Keating, Snaith — "Random matrix theory and L-functions at s=1/2" (2000)
- Conrey, Farmer, Keating, Rubinstein, Snaith — "Integral moments of L-functions" (2005)
- Miller — finite-conductor corrections in low-lying zeros studies (2004, 2006)
- Rubinstein — "Low-lying zeros of L-functions and random matrix theory" (2001)
- Any paper measuring convergence rate to RMT for specific conductor ranges

## What Outcome Helps Us

- If finite-conductor corrections at N=5000 are O(0.05): the RMT gap is explained.
  The finding becomes "we measured a known finite-conductor correction." Still useful,
  not deep.
- If corrections are O(0.01) or smaller: the 0.05 gap exceeds known corrections.
  Something structural beyond RMT + finite-conductor effects is present.
- If the convergence rate is known and predicts our conductor-dependent ARI trend
  (0.59 -> 0.46): strong evidence the gap is pre-asymptotic, nothing more.
