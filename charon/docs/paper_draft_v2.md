# Anomalous Gap Compression in Elliptic Curve L-Function Zeros: A Sign Inversion Beyond Random Matrix Theory

## Working Title Options
1. "Gap Compression in the Spectral Tail: Rank-1 Elliptic Curves Have Tighter Higher Zeros Than Random Matrix Theory Predicts"
2. "A Sign Inversion in L-Function Zero Spacing: Empirical Evidence Against the SO(2N) Model for Rank"
3. "Fifteen Mechanisms Stripped: The Arithmetic Residual in Elliptic Curve Zero Geometry"

## Target: Experimental Mathematics

---

## Abstract (Draft)

We study the nearest-neighbor gap structure of zeros 5-19 in 14,751 elliptic
curve L-functions (conductor <= 5000, deduplicated by isogeny class). We find
that rank-1 curves exhibit uniformly tighter zero spacing than rank-0 curves
across all 15 consecutive gaps, with Cohen's d ranging from -0.03 to -0.11
(8/15 surviving Bonferroni correction, permutation p = 0.001). This contradicts
the sign prediction of finite-matrix random matrix theory: simulation of SO(120)
ensembles with one pinned eigenvalue predicts that rank-1 curves should have
*wider* gaps (positive d), not tighter (negative d). The empirical pattern
correlates with the RMT prediction at r = 0.15 (effectively uncorrelated), with
only 1/15 gaps falling within 2-sigma of the simulation.

We strip 15 candidate mechanisms for this discrepancy — including BSD invariants
(linear and nonlinear), Tamagawa numbers, Galois image, torsion structure,
normalization artifacts, and symmetry type — and find that none explains more
than 1.1% of the effect. The pattern is stable across clustering methods
(K-Means vs GMM), train/test splits, stratum size thresholds, and
normalization schemes (r = 0.994 correlation between normalized and raw zeros).

Additionally, we observe that BSD invariants carry monotonically decaying
predictive information from zero 1 (out-of-sample R^2 = 0.52) to zero 7
(R^2 < 0), with all tail zeros (5-20) having negative R^2 under random forest
regression. Tamagawa numbers exhibit a novel two-hump partial correlation
pattern (r = 0.25 at z1, dead zone z4-z9, second hump r ~ 0.10 at z10-z16)
that is orthogonal to rank discrimination.

---

## 1. Introduction

### 1.1 The Katz-Sarnak Philosophy and Its Limits

The Katz-Sarnak philosophy posits that the distribution of low-lying zeros of
families of L-functions is governed by the symmetry type of the family, with
statistics matching those of eigenvalues from classical compact groups (SO, Sp, U).
For elliptic curves over Q, rank-0 curves correspond to SO(even) and rank-1
curves to SO(odd), with the key difference being a forced zero at the central
point s = 1/2 for rank-1 curves.

The Iwaniec-Luo-Sarnak (ILS) test function support theorem (2000) establishes
that the 1-level densities for SO(even) and SO(odd) are indistinguishable for
test functions with Fourier support in [-1, 1]. Distinguishing rank families
requires test functions with wider support, which by the uncertainty principle
requires information from higher zeros.

### 1.2 What We Test

We ask a simple empirical question: what does the gap structure of higher zeros
(indices 5-19) look like for rank-0 vs rank-1 elliptic curves, and does it
match the prediction of finite-matrix RMT?

The naive RMT prediction is clear: rank-1 curves have one fewer free eigenangle
in the SO(2N) model (the forced zero at the origin consumes one degree of
freedom). Fewer degrees of freedom means more room for the remaining eigenangles,
predicting wider gaps for rank-1 curves.

We find the opposite.

### 1.3 Summary of Results

1. Rank-1 curves have uniformly tighter zero spacing in the spectral tail,
   contradicting the sign prediction of SO(2N) simulation.
2. The gap compression survives 15 stripping attempts against known arithmetic
   and analytic confounds.
3. BSD invariants carry zero predictive information about tail zeros, even
   under nonlinear (random forest) modeling.
4. Tamagawa numbers exhibit a previously unreported two-hump spectral fingerprint
   that is orthogonal to rank discrimination.

---

## 2. Data and Methods

### 2.1 Dataset

14,751 elliptic curves from LMFDB, deduplicated by isogeny class. Conductor
<= 5,000. Each curve has 20 low-lying zeros, Katz-Sarnak normalized
(gamma_n / log(N)). Rank distribution: 6,817 rank-0, 7,476 rank-1, 458 rank-2.

### 2.2 Metrics

**Gap Cohen's d:** For each consecutive gap z_{k+1} - z_k in zeros 5-19 (15
gaps), compute Cohen's d between the rank-0 and rank-1 distributions.
Negative d means rank-1 has tighter spacing.

**Adjusted Rand Index (ARI):** K-means clustering within conductor strata,
scored against rank labels. Used as a discovery tool; the gap analysis is the
primary finding.

### 2.3 Pre-Registration and Audit

Clustering thresholds were set before zero ingestion (2026-04-01). Full audit
trail documented in structured journal. All code and data reproducible from
LMFDB PostgreSQL mirror.

---

## 3. The Sign Inversion

### 3.1 Empirical Gap Structure

Across all 15 gaps in zeros 5-19, rank-1 curves show tighter spacing than
rank-0 curves. After removing 2% outliers, the effect is uniform and stronger:

| Gap Region | Mean Cohen's d | N gaps significant (Bonferroni) |
|-----------|---------------|------|
| z5-z9 (near central) | -0.14 | 3/4 |
| z9-z13 (mid-tail) | -0.14 | 3/4 |
| z13-z17 (far tail) | -0.09 | 1/4 |
| z17-z20 (edge) | -0.11 | 2/3 |

Aggregate: permutation test on the d-vector norm, p = 0.001 (0/1000 exceeded).

### 3.2 RMT Prediction

We simulate 20 trials of 7,000 rank-0 objects from SO(120) and 7,000 rank-1
objects from SO(118) + 1 pinned eigenvalue. The simulation predicts positive d
(wider gaps for rank-1) at every gap position, with mean d ~ +0.04.

The empirical pattern correlates with the RMT pattern at r = 0.15. Only 1/15
gaps falls within 2-sigma of the simulation. The discrepancy is qualitative
(sign error), not merely quantitative.

### 3.3 Robustness

The sign inversion is:
- Stable across stratum sizes (min_n = 3, 5, 10, 20): mean d is negative at all settings
- Identical on raw (unnormalized) zeros: pattern correlation r = 0.994
- Stable across clustering methods: K-Means ARI = 0.555, GMM ARI = 0.531
- Stable under train/test split: Train ARI = 0.592, Test ARI = 0.626
- Strengthened by outlier removal: d-values approximately double

---

## 4. Fifteen Mechanisms Stripped

We systematically test 15 candidate explanations for the gap compression.
None explains more than 1.1% of the effect.

### 4.1 Classical Invariants (Kills 1-9)

| Mechanism | Method | Result |
|-----------|--------|--------|
| Central vanishing (z1) | Ablation | Removing z1 *improves* clustering |
| Conductor | Ridge regression residual | Signal survives |
| Sha order | Rank-stratified comparison | Orthogonal to tail |
| Faltings height | Variance decomposition | < 1% variance explained |
| Modular degree | Variance decomposition | < 1% |
| Symmetry type (root number) | Conditioning | ARI = 0.49 within SO(even) |
| Pre-asymptotic effects | Conductor scaling | Flat across conductor range |
| Zero truncation (20 vs 25+) | Extended zeros from LMFDB | Signal plateaus at z5-19 |
| Inner twists (CM) | Enrichment analysis | CM = 0.87x (depleted, not enriched) |

### 4.2 Normalization and Methodology (Kills 10-12)

| Mechanism | Method | Result |
|-----------|--------|--------|
| KS normalization | Exact Gamma unfolding (mpmath) | ARI changes by +0.003 |
| Analytic conductor | Re-normalize by q = N/(4pi^2) | ARI delta = 0.000 |
| Sha leaking into tail | Hotelling T^2, conductor-matched | p = 0.109 |

### 4.3 Arithmetic Fingerprints (Kills 13-15)

Three arithmetic invariants (Tamagawa, Galois image, torsion) show a consistent
pattern: they influence zero positions (significant KS/Hotelling tests) but are
**orthogonal to rank discrimination** (ARI delta < 0.002 in all cases).

| Mechanism | Touches zeros? | Explains rank signal? | ARI delta |
|-----------|---------------|----------------------|-----------|
| Tamagawa product | Yes (6/16 sig, conductor-matched) | No | -0.001 (1.1%) |
| Galois image (mod-2) | Yes (6/16 sig, conductor-matched) | No | -0.0003 (0.4%) |
| Torsion subgroup | Yes (16/16 sig, Hotelling p=1e-5) | No | +0.0001 (0.0%) |

### 4.4 Nonlinear BSD Test (Kill Confirmation)

Random forest regression (100 trees, 5-fold CV) trained on BSD invariants
(log(conductor), rank, log1p(Sha), Faltings height, log1p(degree), regulator)
to predict each zero position. Out-of-sample R^2:
- Zero 1: +0.524 (strong)
- Zero 4: +0.143
- Zero 6: +0.013
- Zeros 7-20: all negative (worse than predicting the mean)

Even nonlinear models find no BSD content in the spectral tail.

---

## 5. BSD Information Decay

The influence of BSD invariants on zero positions decays monotonically from
zero 1 to approximately zero 12, then stabilizes near zero. This is not a
sharp "wall" but a smooth decay, visualized via sliding-window partial
correlations and confirmed by the random forest R^2 profile.

The decay structure is:
- **Zero 1:** Strong BSD dependence (r ~ 0.04 for Sha, Faltings, regulator)
- **Zeros 2-6:** Transitional (r decaying)
- **Zeros 7-20:** BSD-independent (RF R^2 < 0)

This separation means zero 1 and the spectral tail carry complementary,
non-redundant information about an elliptic curve's arithmetic.

---

## 6. Tamagawa Two-Hump Spectral Fingerprint

After controlling for conductor and rank, the Tamagawa product shows a
partial correlation with zero positions that has two distinct humps:

- **Hump 1 (z1-z3):** r = 0.249, 0.106, 0.043 (decaying)
- **Dead zone (z4-z9):** r ~ 0.00
- **Hump 2 (z10-z16):** r = 0.053 to 0.102 (bell-shaped)
- **Decay (z17-z20):** r returning to zero

This two-hump structure survives conductor matching (Fisher combined test:
6/16 zeros significant). The mechanism is unknown. We note that the second
hump (z10-z16) aligns roughly with the region where the gap compression
effect is strongest, but the Tamagawa fingerprint is orthogonal to rank
discrimination (ARI delta = -0.001).

---

## 7. Discussion

### 7.1 What Produces the Sign Inversion?

The standard SO(2N) model with a pinned eigenvalue predicts wider gaps for
rank-1. The data shows tighter. This suggests the modeling of rank via a
simple pinned eigenvalue is insufficient for zeros 5-19 at conductor <= 5000.

Possible explanations (speculative):
- **Arithmetic corrections to GUE repulsion:** The forced zero at the central
  point may exert a longer-range compressive effect than pure RMT predicts,
  through the explicit formula's arithmetic terms.
- **Non-universal lower-order terms:** The zeros we study (indices 5-19 at
  conductor <= 5000) are still in a pre-asymptotic regime where
  conductor-dependent corrections to the Katz-Sarnak density may dominate.
- **Rank-dependent conductor effects:** Even after conductor stratification,
  the functional relationship between conductor and zero positions may differ
  between rank classes in ways not captured by linear regression.

We do not resolve this question. We report the empirical observation and its
robustness.

### 7.2 Limitations

1. **Dataset size and range:** 14,751 curves at conductor <= 5000.
   Confirmation at higher conductor would strengthen the result.
2. **Stratum size sensitivity:** ARI varies with minimum stratum size
   threshold, though the gap d-vector sign is stable.
3. **Single L-function family:** We study only elliptic curve L-functions.
   Whether the sign inversion extends to other families is unknown.
4. **No theoretical model:** We do not propose a theoretical explanation
   for the gap compression. The finding is purely empirical.

### 7.3 Relation to Prior Work

- **He, Lee, Oliver, Pozdnyakov (2022):** Murmurations of elliptic curves
  demonstrated unexpected oscillatory patterns in a_p averages. Our finding
  is in a complementary domain (zero spacing rather than coefficient
  statistics).
- **arXiv:2502.10360 (2025):** Machine learning the vanishing order of
  L-functions. Our work confirms and extends: the spectral tail carries rank
  information, but through a mechanism that contradicts the standard RMT model.
- **Miller (2004):** One- and two-level densities for elliptic curve families.
  Our gap-by-gap analysis operates at a finer resolution than density tests.

---

## 8. Conclusion

The spectral tail (zeros 5-19) of elliptic curve L-functions exhibits
rank-dependent gap compression that contradicts the sign prediction of
finite-matrix SO(2N) random matrix theory. Rank-1 curves have uniformly
tighter zero spacing than rank-0 curves, opposite to the naive expectation
from the forced-zero model. This effect survives 15 mechanism-stripping
tests, is stable across methodological variations, and is not a normalization
artifact (r = 0.994 correlation between normalized and raw zeros).

The finding opens two questions: what arithmetic mechanism produces the
compression, and whether it persists at higher conductor (the asymptotic
regime where Katz-Sarnak universality should hold). A theoretical model
predicting gap compression from the explicit formula's arithmetic terms
would transform this empirical observation into a structural result.

---

## Data Availability

All data reproducible from LMFDB PostgreSQL mirror (devmirror.lmfdb.xyz).
Analysis code at [repository URL]. Pre-registered thresholds documented
before data ingestion.

## Key References

- Iwaniec, Luo, Sarnak (2000) — "Low lying zeros of families of L-functions"
- Katz, Sarnak (1999) — "Zeroes of zeta functions and symmetry"
- Miller (2004) — "One- and two-level densities for rational families"
- He, Lee, Oliver, Pozdnyakov (2022) — "Murmurations of elliptic curves"
- Hughes, Miller (2007) — "Low-lying zeros with orthogonal symmetry"
- Huynh, Keating, Snaith (2009) — "Lower order terms and the 1-level density"
- arXiv:2502.10360 (2025) — "Machine learning the vanishing order"
