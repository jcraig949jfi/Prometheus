# Gap Compression in the Spectral Tail of Elliptic Curve L-Functions: A Sign Inversion Beyond Random Matrix Theory

## Target: Experimental Mathematics

---

## Abstract

We report a qualitative failure of the SO(2N) random matrix model for
predicting zero spacing in elliptic curve L-functions: rank-1 curves exhibit
uniformly tighter gaps in zeros 5-19, opposite to the prediction of
finite-matrix simulation. We strip 15 candidate mechanisms -- including BSD
invariants under nonlinear modeling, Tamagawa numbers, Galois image, and
torsion structure -- and find that none explains more than 1.1% of the effect.
The compression is strongest at low conductor (mean Cohen's d = -0.09 at
N < 500) and decays logarithmically (d = -0.002 at N ~ 4000, slope +0.035
vs log N, R^2 = 0.85), consistent with a finite-conductor correction that has
not yet reached the Katz-Sarnak universal limit at conductor 5000. As
secondary findings, we observe that BSD invariants carry monotonically decaying
predictive information through the zero spectrum (random forest R^2 from +0.52
at zero 1 to -0.50 at zero 20), and that Tamagawa numbers exhibit a
previously unreported two-hump partial correlation pattern orthogonal to rank.

---

## 1. Introduction

### 1.1 The Katz-Sarnak Philosophy and Its Finite-Conductor Regime

The Katz-Sarnak philosophy posits that the distribution of low-lying zeros
of families of L-functions is governed by the symmetry type of the family,
with statistics matching eigenvalues from classical compact groups. For
elliptic curves over Q, rank-0 curves correspond to SO(even) and rank-1
curves to SO(odd), distinguished by a forced zero at s = 1/2 for rank-1.

The Iwaniec-Luo-Sarnak (ILS) test function support theorem [ILS00]
establishes that the 1-level densities for SO(even) and SO(odd) are
indistinguishable for test functions with Fourier support in [-1, 1].
Distinguishing rank families requires information from higher zeros.

Crucially, the Katz-Sarnak predictions are asymptotic: they describe the
limit as conductor grows. At finite conductor, lower-order terms
[HKS09, Mil04] introduce corrections that may differ between rank classes.
The regime N <= 5000 that we study has an effective spectral density of
approximately log(N)/(2*pi) ~ 1.0-1.4 zeros per unit height -- far from
any asymptotic regime.

### 1.2 The RMT Prediction and What We Find

In the standard SO(2N) model, rank-1 curves have one fewer free eigenangle
(the forced zero consumes one degree of freedom). Fewer degrees of freedom
should produce wider gaps in the remaining eigenangle spectrum.

We find the opposite: rank-1 curves have uniformly *tighter* zero spacing
in zeros 5-19. This sign inversion is strongest at low conductor and decays
logarithmically toward zero at higher conductor, consistent with a
finite-conductor effect. It contradicts the SO(2N) prediction not just
quantitatively but qualitatively.

### 1.3 Summary of Results

1. Rank-1 curves have tighter zero spacing than rank-0 in zeros 5-19,
   contradicting the sign of the SO(2N) prediction. The effect decays
   logarithmically with conductor.
2. Fifteen candidate mechanisms stripped; none explains more than 1.1%.
3. BSD invariants carry monotonically decaying information through the
   zero spectrum, with negative out-of-sample R^2 by zero 7.
4. Tamagawa numbers show a two-hump spectral fingerprint orthogonal to rank.

---

## 2. Data and Methods

### 2.1 Dataset

14,751 elliptic curves from LMFDB [LMFDB], deduplicated by isogeny class
(curves within an isogeny class share the same L-function by definition).
Conductor <= 5,000. Each curve has 20 low-lying zeros, normalized as
gamma_n / log(N) following the Katz-Sarnak convention. Rank distribution:
6,817 rank-0, 7,476 rank-1, 458 rank-2.

**Deduplication sensitivity.** Without deduplication, ARI = 0.476 on 26,147
curves. With deduplication, ARI = 0.555 on 14,751 curves. Deduplication
is mathematically correct (isogeny siblings contribute identical zero
vectors, inflating strata without adding information), but we report both
values for transparency. All subsequent analyses use the deduplicated set.

### 2.2 Primary Metric: Gap Cohen's d

For each consecutive gap z_{k+1} - z_k in zeros 5-19 (15 gaps), we compute
Cohen's d between the rank-0 and rank-1 gap distributions. Negative d means
rank-1 has tighter spacing. We report the full 15-dimensional d-vector and
its aggregate statistics (mean, norm, sign pattern).

### 2.3 Discovery Metric: Adjusted Rand Index

K-means clustering (k = min(n/2, 5), n_init=10) within conductor strata
(min 5 objects per stratum, at least 2 rank classes), scored against rank
labels via ARI. This metric discovered the spectral tail signal but is
secondary to the gap analysis.

**Stratum size sensitivity.** ARI varies with the minimum stratum size
threshold: 0.672 (min=3), 0.555 (min=5), 0.383 (min=10), 0.415 (min=20).
Small strata inflate ARI due to easier clustering of fewer objects. The
gap Cohen's d vector is stable across all thresholds (mean d negative at
every setting, pattern correlation > 0.76 with the global d-vector).

### 2.4 Pre-Registration

Clustering thresholds (ARI_min = 0.30, improvement_min = 0.08, and others)
were set before zero ingestion on 2026-04-01 and documented in a structured
audit. All code and data are reproducible from the LMFDB PostgreSQL mirror.

---

## 3. The Sign Inversion

### 3.1 Global Gap Structure

Across all 15 gaps in zeros 5-19, rank-1 curves show tighter spacing than
rank-0 curves. The global d-vector (unstratified, 6,817 rank-0 vs 7,476
rank-1) has:
- Mean d = -0.045
- ||d|| = 0.251
- 13/15 gaps negative (exceptions: z9-z10 at d = +0.0004, z17-z18 at
  d = +0.065)
- 8/15 gaps surviving Bonferroni correction (p < 0.0033)
- Permutation test on ||d||: p = 0.001 (0/1000 permuted d-vectors exceeded)

After removing 2% outliers (per-zero top/bottom tails), all d-values become
negative and approximately double in magnitude, with the z17-z18 anomaly
vanishing (d: +0.065 -> +0.007). The core pattern is uniform compression,
robust to outlier influence.

### 3.2 RMT Simulation

We simulate 20 trials of 7,000 rank-0 objects sampled from SO(120) and
7,000 rank-1 objects from SO(118) with one eigenvalue pinned at zero.
Positive eigenangles are normalized to unit mean spacing.

We use N_matrix = 60 (SO(120)) as a comparison point. We note that the
effective spectral density at conductor N is approximately log(N)/(2*pi),
giving 1.0-1.4 zeros per unit height for our conductor range -- far smaller
than the matrix dimension. The simulation therefore tests the *qualitative*
sign prediction (does rank-1 have wider or tighter gaps?) rather than the
quantitative d-values.

**Results.** The simulation predicts positive d (wider gaps for rank-1) at
every gap position, with mean d ~ +0.04. The empirical pattern correlates
with the simulated pattern at r = 0.15 (effectively uncorrelated). Only
1/15 gaps falls within 2-sigma of the RMT prediction. The discrepancy is
qualitative: RMT predicts the wrong sign.

### 3.3 Conductor Dependence

The gap compression decays logarithmically with conductor:

| Conductor Range | N curves | Mean d | Negative gaps |
|----------------|---------|--------|---------------|
| 200-500 | 431 | -0.091 | 10/15 |
| 501-1000 | 1,477 | -0.033 | 10/15 |
| 1000-2000 | 3,312 | -0.034 | 9/15 |
| 2000-3000 | 3,515 | -0.014 | 9/15 |
| 3000-5000 | 5,558 | -0.002 | 7/15 |

Linear fit of mean d vs log(conductor): slope = +0.035, R^2 = 0.85,
p = 0.027. The compression weakens at higher conductor but has not changed
sign at N = 5000.

This is consistent with a finite-conductor correction to the Katz-Sarnak
limit. Whether the compression vanishes in the asymptotic regime (N >> 5000)
is an open question.

### 3.4 Robustness

The sign inversion (negative mean d) is:
- **Stratum-stable:** Negative at all stratum size thresholds (min=3,5,10,20)
- **Normalization-independent:** r = 0.994 correlation between normalized
  and raw (unnormalized) zero d-vectors; 13/15 same-sign gaps
- **Method-independent:** K-Means ARI = 0.555, GMM ARI = 0.531
- **Split-stable:** Train ARI = 0.592, Test ARI = 0.626 (50/50 random split)
- **Outlier-robust:** Effect doubles after removing 2% tails

---

## 4. Fifteen Mechanisms Stripped

We systematically test 15 candidate explanations for the gap compression.
None explains more than 1.1% of the ARI-measured effect.

### 4.1 Classical Invariants (Kills 1-9)

| # | Mechanism | Method | Result |
|---|-----------|--------|--------|
| 1 | Central vanishing (z1) | Ablation | Removing z1 *improves* clustering |
| 2 | Conductor | Ridge regression residual | Signal survives |
| 3 | Sha order | Rank-stratified comparison | Orthogonal to tail |
| 4 | Faltings height | Variance decomposition | < 1% explained |
| 5 | Modular degree | Variance decomposition | < 1% |
| 6 | Symmetry type | Root number conditioning | ARI = 0.49 within SO(even) |
| 7 | Pre-asymptotic effects | Conductor scaling | ARI flat; gap d decays (see 3.3) |
| 8 | Truncation (20 vs 25+) | Extended zeros from LMFDB | Signal plateaus at z5-19 |
| 9 | Inner twists (CM) | Enrichment analysis | CM = 0.87x (depleted) |

**Note on Kill 7.** The ARI is approximately flat across conductor bins
(slope = -0.014). However, the gap Cohen's d decays logarithmically (Section
3.3). We report both: the rank-clustering signal is stable, but the
gap-level effect weakens at higher conductor. These are not contradictory --
the ARI aggregates across gaps and strata, smoothing the per-gap decay.

### 4.2 Normalization and Methodology (Kills 10-12)

| # | Mechanism | Method | Result |
|---|-----------|--------|--------|
| 10 | KS normalization | Exact Gamma unfolding (mpmath) | ARI +0.003 |
| 11 | Analytic conductor | Re-normalize by q = N/(4*pi^2) | ARI delta = 0.000 |
| 12 | Sha leaking into tail | Hotelling T^2, conductor-matched | p = 0.109 |

### 4.3 Arithmetic Fingerprints (Kills 13-15)

Three arithmetic invariants show a consistent pattern: they influence zero
positions but are orthogonal to rank discrimination (ARI delta < 0.002).

| # | Mechanism | Touches zeros? | ARI delta |
|---|-----------|---------------|-----------|
| 13 | Tamagawa product | Yes (6/16 sig, conductor-matched) | -0.001 (1.1%) |
| 14 | Galois image (mod-2) | Yes (6/16 sig, conductor-matched) | -0.0003 (0.4%) |
| 15 | Torsion subgroup | Yes (16/16 sig, Hotelling p=1e-5) | +0.0001 (0.0%) |

### 4.4 Nonlinear BSD Confirmation

Random forest regression (100 trees, max_depth=8, 5-fold cross-validation)
trained on [log(N), rank, log1p(Sha), Faltings height, log1p(degree),
regulator] to predict each zero position:

- Zero 1: R^2 = +0.524
- Zero 4: R^2 = +0.143
- Zero 6: R^2 = +0.013
- Zeros 7-20: all R^2 < 0 (worse than predicting the mean)

Even nonlinear models find no BSD content in the spectral tail.

---

## 5. BSD Information Decay

The influence of BSD invariants on zero positions decays monotonically from
zero 1 to approximately zero 7, after which BSD invariants carry no
predictive information (negative out-of-sample R^2).

This decay is confirmed by three independent methods:
1. **Linear partial correlation** (controlling for conductor + rank):
   |r| ~ 0.04 at z1, decaying to |r| < 0.02 by z7
2. **Sliding-window partial correlation** (3-zero windows): mean |r| =
   0.025 at z1-z3, decaying to 0.009 by z13-z15
3. **Random forest R^2** (nonlinear, out-of-sample): +0.52 at z1,
   crossing zero at z6-z7, reaching -0.50 at z20

Zero 1 and the spectral tail carry complementary, non-redundant information
about an elliptic curve's arithmetic.

---

## 6. Tamagawa Two-Hump Spectral Fingerprint

After controlling for conductor and rank, the Tamagawa product shows a
partial correlation with zero positions in two distinct regions:

- **Region 1 (z1-z3):** r = 0.249, 0.106, 0.043 (expected: Tamagawa
  enters the BSD formula, which governs L(1,E))
- **Dead zone (z4-z9):** r ~ 0.00
- **Region 2 (z10-z16):** r = 0.053 to 0.102 (unexpected)
- **Decay (z17-z20):** r returning to zero

The second hump survives conductor matching (Fisher combined test: 6/16
zeros significant). The mechanism is unknown. We note that the Tamagawa
fingerprint is entirely orthogonal to rank discrimination (ARI
delta = -0.001), meaning Tamagawa shifts zeros of all ranks equally.

---

## 7. Discussion

### 7.1 Conductor Dependence and the Pre-Asymptotic Regime

The gap compression decays logarithmically with conductor (R^2 = 0.85),
consistent with a lower-order correction to the Katz-Sarnak universal limit.
At conductor 5000, the mean Cohen's d has decayed to -0.002 but has not
changed sign. Whether it vanishes at larger conductor is an open empirical
question requiring data at N > 10^5.

We note that our entire dataset lies in the pre-asymptotic regime: the
effective spectral density (log(N)/(2*pi)) is approximately 1.0-1.4
for our conductor range, meaning the "higher zeros" we study (indices 5-19)
are not far into the bulk spectrum. The lower-order terms studied by
Huynh-Keating-Snaith [HKS09] and the finite-conductor corrections to ILS
[Mil04] are expected to be significant in this regime. Our finding
quantifies a specific manifestation: the correction has a definite sign
(compressive for rank-1) that current theoretical formulas do not predict.

### 7.2 Limitations

1. **Conductor range.** Our data covers N <= 5000. The logarithmic
   decay suggests the effect may vanish at sufficiently high conductor.
   This limits claims about the asymptotic regime.
2. **Single family.** We study only elliptic curve L-functions. Whether
   analogous compression occurs in other families is unknown.
3. **No theoretical model.** We do not propose a mechanism. The finding
   is purely empirical.
4. **Stratum sensitivity.** ARI depends on stratum construction, though
   the gap d-vector sign is stable (Section 3.4).

### 7.3 Relation to Prior Work

- **He, Lee, Oliver, Pozdnyakov (2022) [HLOP22]:** Murmurations demonstrated
  unexpected oscillatory patterns in a_p averages. Our finding is in the
  complementary domain of zero spacing.
- **arXiv:2502.10360 (2025):** Machine learning the vanishing order
  of L-functions. Confirms the spectral tail carries rank information.
  Our work adds that the mechanism contradicts standard RMT.
- **Miller (2004) [Mil04]:** One- and two-level densities for elliptic
  curve families. Our gap-by-gap analysis operates at finer resolution.
- **Huynh, Keating, Snaith (2009) [HKS09]:** Lower-order terms in
  the 1-level density. The conductor dependence we observe is qualitatively
  consistent with their framework, though the specific sign of the
  correction is not predicted by their formulas.

---

## 8. Conclusion

The spectral tail (zeros 5-19) of elliptic curve L-functions exhibits
rank-dependent gap compression that contradicts the sign prediction of the
standard SO(2N) model. The compression is strongest at low conductor and
decays logarithmically, consistent with a finite-conductor correction whose
specific character (compressive for rank-1, not expansive) is not predicted
by current random matrix or analytic number theory models.

Fifteen candidate mechanisms have been tested and excluded. The pattern is
stable across normalization schemes, clustering methods, train/test splits,
and stratum constructions. BSD invariants carry no predictive information
about tail zeros even under nonlinear modeling.

The finding invites two lines of follow-up: empirical confirmation at
conductor N > 10^5, and theoretical derivation of the sign of
finite-conductor corrections to the SO(2N) gap prediction for rank-1
families.

---

## Data Availability

All data reproducible from LMFDB PostgreSQL mirror (devmirror.lmfdb.xyz).
Analysis code archived at [repository URL]. Pre-registered thresholds
documented before data ingestion (2026-04-01).

## References

- [ILS00] Iwaniec, Luo, Sarnak -- "Low lying zeros of families of L-functions" (2000)
- [KS99] Katz, Sarnak -- "Zeroes of zeta functions and symmetry" (1999)
- [Mil04] Miller -- "One- and two-level densities for rational families of elliptic curves" (2004)
- [HLOP22] He, Lee, Oliver, Pozdnyakov -- "Murmurations of elliptic curves" (2022)
- [HM07] Hughes, Miller -- "Low-lying zeros with orthogonal symmetry" (2007)
- [HKS09] Huynh, Keating, Snaith -- "Lower order terms and the 1-level density" (2009)
- [LMFDB] The L-functions and modular forms database, https://www.lmfdb.org
- [SS25] Sawin, Sutherland -- Murmuration density formula (2025)
- [2502.10360] "Machine learning the vanishing order of rational L-functions" (2025)
