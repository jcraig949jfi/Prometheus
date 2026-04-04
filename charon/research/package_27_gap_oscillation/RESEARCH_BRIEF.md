# Research Package 27: Oscillatory Gap Pattern in Rank-Dependent Zero Spacing
## Priority: HIGHEST
## Date: 2026-04-04

---

## Context

We measured nearest-neighbor zero spacing in the spectral tail (zeros 5-20) of 14,751 elliptic curve L-functions, comparing rank-0 vs rank-1 curves. We found that rank-1 curves have tighter spacing overall (Cohen's d = -0.045, p = 2.3e-26), but the effect is NOT uniform. The gap-by-gap pattern shows:

1. **Strong compression** at z6-z9 (d = -0.08 to -0.11, p < 1e-5)
2. **Dead zones** at z9-z11 and z14-z16 (d ~ 0, not significant)
3. **Anomalous reversal** at z17-z18 (d = +0.065, p = 5.8e-14 -- rank-1 has WIDER gap)

This oscillatory pattern is not predicted by simple GUE repulsion propagation from a pinned zero at the origin, which should produce monotonically decreasing effect with distance.

## Research Questions

1. **Has anyone measured gap-specific rank effects in L-function zeros?** Not just bulk statistics or 1-level density, but gap-by-gap comparisons between arithmetic subpopulations. Does any existing computational study show similar oscillatory patterns?

2. **Is this pattern predicted by the n-level density formulas?** The Katz-Sarnak n-level density for SO(even) vs SO(odd) has explicit formulas involving determinantal point processes. Do these formulas predict oscillatory behavior in the spacing differences between the two symmetry types at specific zero indices?

3. **Could this be a finite-N effect in RMT?** The Tracy-Widom law and Gaudin-Mehta distribution describe spacing statistics of random matrices. At finite matrix size (our zeros come from N ~ 60 eigenvalues), do the spacing distributions of SO(2N) with r pinned zeros show non-monotonic rank sensitivity as a function of eigenvalue index?

4. **Is there a connection to the "pair correlation oscillation" literature?** Montgomery's pair correlation conjecture and the refinements by Hejhal, Rudnick-Sarnak, and others describe oscillatory phenomena in zero correlations. Does the oscillation period in our gap pattern match any known oscillation in the pair correlation function?

5. **What is the theoretical expectation for the z17-z18 reversal?** For random matrices from SO(2N) with 2 pinned eigenvalues at 0 (rank 1) vs 0 pinned (rank 0), at what eigenvalue index does the spacing of the pinned-eigenvalue ensemble EXCEED that of the unpinned ensemble? Is this a known crossover phenomenon?

6. **Does the spacing pattern depend on conductor?** If we stratify by conductor range, does the oscillation shift, shrink, or remain stable? This would distinguish finite-N effects (conductor-dependent) from structural arithmetic effects (conductor-independent).

## Key Papers to Start From

- Iwaniec, Luo, Sarnak (2000) -- "Low-lying zeros of families of L-functions" (the ILS paper)
- Katz, Sarnak (1999) -- "Random Matrices, Frobenius Eigenvalues, and Monodromy"
- Rudnick, Sarnak (1996) -- "Zeros of principal L-functions and random matrix theory"
- Miller (2004) -- "One- and two-level densities for rational families of elliptic curves"
- Hughes, Miller (2007) -- "Low-lying zeros of L-functions with orthogonal symmetry"
- Huynh, Keating, Snaith (2009) -- "Lower order terms and the 1-level density of families"
- Any computational work measuring gap-specific statistics of L-function zeros
