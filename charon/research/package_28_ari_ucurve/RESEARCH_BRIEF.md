# Research Package 28: Non-Monotonic ARI vs Conductor (U-Curve Anomaly)
## Priority: HIGH
## Date: 2026-04-04

---

## Context

We measure the Adjusted Rand Index (ARI) for rank clustering using zeros 5-19 within conductor strata. The ARI measures how well K-means on the spectral tail separates rank-0 from rank-1 curves. We expected ARI to decay monotonically as conductor increases (convergence toward Katz-Sarnak universality). Instead, we see a U-curve:

| Conductor Bin | N objects | ARI (tail 5-19) |
|--------------|----------|-----------------|
| 301-500      | 428      | 0.638           |
| 501-800      | 861      | 0.571           |
| 801-1200     | 1,307    | 0.541           |
| 1201-1800    | 2,030    | 0.529           |
| 1801-2500    | 2,507    | 0.525           |
| 2501-3500    | 3,687    | 0.552 (uptick!) |
| 3501-5000    | 3,925    | 0.584 (uptick!) |

Linear fit: R^2 = 0.315 (poor). The ARI *decreases* from N=300-2500 then *increases* from N=2500-5000.

## Research Questions

1. **Is there a known population shift in LMFDB elliptic curves at conductor > 2500?** Does the rank distribution, torsion structure, Tamagawa product, or CM proportion change systematically at higher conductor? Is there a selection bias in how LMFDB catalogues high-conductor curves?

2. **Do finite-conductor corrections to the Katz-Sarnak density exhibit non-monotonic behavior?** The lower-order terms in the 1-level density (Huynh-Keating-Snaith, Miller) include oscillatory corrections. Could these produce a U-curve in a clustering metric?

3. **Has anyone observed non-monotonic convergence to universality in L-function families?** As conductor grows, symmetry type statistics should converge to the Katz-Sarnak prediction. Is this convergence always monotonic, or can there be transient effects (analogous to the Mertens conjecture oscillation)?

4. **Could this be a strata-count artifact?** At low conductor, few curves share exact conductor, so strata are small and ARI is volatile. At high conductor, strata are larger. Could the U-curve be a statistical artifact of stratum size variation?

5. **Is the uptick related to the density of primes?** Conductor = product of bad primes (roughly). High-conductor curves may have more bad primes, changing the analytic properties of the L-function. Does the number of distinct prime factors of the conductor correlate with ARI?

6. **Does the rank-2 fraction change across the conductor range?** Our dataset has 458 rank-2 curves. If they cluster disproportionately in the 2500-5000 range, they could drive the ARI uptick by providing a more separable third cluster.

## Key Papers

- Huynh, Keating, Snaith (2009) -- "Lower order terms and the 1-level density"
- Miller (2004) -- "One- and two-level densities for rational families of elliptic curves"
- Cremona's tables documentation -- any notes on completeness boundaries
- Brumer, McGuinness (1990) -- "The behavior of the Mordell-Weil group of elliptic curves"
- Park, Poonen, Voight, Wood (2019) -- "A heuristic for boundedness of ranks of elliptic curves"
