# Spectral Encoding of Arithmetic Invariants: Three Independent Channels in L-Function Zeros

**James Craig**
JFI Research | April 2026

---

## Abstract

We report a systematic computational investigation of the relationship between L-function zero statistics and arithmetic invariants of elliptic curves, using 31,073 curves with stored zeros and 3.8 million curves from the LMFDB database. After an adversarial falsification campaign that killed 18 cross-domain statistical claims and established 10 negative dimensions, we find that L-function zeros encode arithmetic invariants through three independent spectral channels: (1) the first zero height gamma\_1 predicts rank with 92.1% accuracy; (2) the gap distribution (mean spacing, variance, skewness) predicts isogeny class size with R^2 = 0.249; and (3) higher-order spacing ratios predict the order of the Shafarevich-Tate group with R^2 = 0.067. The class size signal survives conductor-matched permutation controls (z = -29.3), local reduction conditioning (rho = -0.113, p = 1.89 x 10^-86), and a synthetic null test with 0% false positive rate across 800 trials. It decays as N^(-0.464), consistent with random matrix theory finite-size corrections. The rank->=2 fraction follows a logistic growth law (R^2 = 0.995) with predicted saturation at 13.7%, compatible with the Goldfeld conjecture. All findings are calibrated against seven known theorems verified at 100.000% across 3.8 million curves, and subjected to a 38-test adversarial battery.

---

## 1. Introduction

The Birch and Swinnerton-Dyer (BSD) conjecture posits a deep connection between the algebraic rank of an elliptic curve E/Q and the analytic behavior of its L-function L(E,s) at s = 1. The Generalized Riemann Hypothesis (GRH) places all nontrivial zeros of L(E,s) on the critical line Re(s) = 1/2. Together, these conjectures suggest that the zero spectrum of an L-function encodes the arithmetic of the underlying curve.

We investigate this encoding computationally, asking: *given only the zeros of L(E,s), what arithmetic invariants can be recovered?* Using 31,073 elliptic curves with >=8 stored zeros from the Charon database, and 3.8 million curves from the LMFDB, we construct predictive models from spectral features and subject every finding to an adversarial falsification protocol.

### 1.1 Falsification-first methodology

This work is organized around systematic destruction of false positives. We begin from the assumption that every observed correlation is artifactual, and accept findings only after they survive a battery of adversarial tests. This approach killed 18 initially plausible statistical claims before the surviving signals were identified.

The adversarial battery (F1-F38) includes: permutation nulls with conductor matching, trivial 1D baselines, Megethos-mediated false positive detection, within-bin shuffling, representation stability tests, and raw-data verification. A synthetic null test generates data from GUE spacing distributions and conductor-correlated models to verify that the analysis pipeline cannot produce false signals from structureless data.

### 1.2 Data

- **Charon DuckDB**: 31,073 elliptic curves with >=5 stored L-function zeros, conductor <=50,000, linked to full LMFDB metadata (rank, Sha, torsion, class size, CM status, bad primes, isogeny degrees).
- **LMFDB Postgres**: 3,824,372 elliptic curves with rank, analytic rank, Sha, regulator, torsion, and conductor up to 500,000.
- **Modular forms**: 5,000-10,000 weight-2 dimension-1 newforms with traces and analytic rank.

---

## 2. Instrument Calibration

Before testing novel predictions, we verify that the instrument correctly detects known mathematical structure.

| Theorem | Sample size | Result |
|---------|------------|--------|
| Modularity (Wiles et al.) | 971 pairs | 100.000% |
| Parity conjecture | 3,824,372 | 100.000% |
| Mazur torsion theorem | 3,824,372 | 100.000% |
| Hasse bound | 150,000 | 100.000% |
| Conductor positivity | 3,824,372 | 100.000% |
| rank = analytic_rank | 3,824,372 | 100.000% |
| root_number = (-1)^rank | 31,073 | 100.000% |

These serve as positive controls: the pipeline reads arithmetic structure at full precision. We additionally verify GUE consistency of zero spacings (spacing ratio <r> = 0.554, GUE prediction 0.531, Poisson 0.386) and Katz-Sarnak symmetry type separation (SO(even) vs SO(odd) density profiles match theoretical 1-level densities).

---

## 3. The Negative Space: 18 Kills

Our investigation began as a search for cross-domain mathematical structure across 42 domains and 789,000 objects. The adversarial battery killed every cross-domain claim:

1. **Kills 1-8**: Original adversarial controls (rank-norm, monotonic, slicing).
2. **Kill 9**: "Universal" scaling exponent: representation-dependent (1.57 vs 1.07).
3. **Kill 10**: Physics-math bridge: 6/8 kills, sparse data artifact.
4. **Kill 11**: Phoneme nearest-neighbor transfer: ordinal matching of small integers (F33).
5. **Kill 12**: Curvature-obstructs-transfer: prediction was backwards (r = +0.27).
6. **Kill 13**: Spectral features crack 21% residual: +5.9% only.
7. **Kill 14**: Knot Alexander polynomial GUE: preprocessing artifact (raw: anti-GUE).
8. **Kill 15**: Within-domain splits: feature dimensionality, not semantic structure.
9. **Kill 16**: EC-Artin bond: matches null exactly (z = 0.00).
10. **Kill 17**: Three-way interactions: 0/5 triples show effects beyond pairwise.
11. **Kill 18**: Congruence graph communities predict rank: sample-dependent graph fragmentation.

These kills establish 10 negative dimensions: the primitive mathematical structure is not ordinal matching, not magnitude mediation, not distributional coincidence, not preprocessing artifacts, not hand-crafted features, not group-theoretic tautologies, not prime-mediated confounds, not partial-correlation artifacts, not within-domain splitting, and not TT-Cross bond dimensions on invariant-level features.

**The only surviving signal class**: L-function zero statistics.

---

## 4. Signal A: Zero Spacing Encodes Isogeny Class Size

### 4.1 The signal

The spacing between the first and second zeros of L(E,s) -- specifically gamma\_2 - gamma\_1 -- correlates with the isogeny class size of E, after controlling for conductor, rank, local reduction type, CM status, and semistability.

- Conductor-controlled Spearman correlation: rho = -0.134, p = 3.0 x 10^-159
- Within-bin permutation null (50 bins, 500 trials): z = -29.3, empirical p = 0.000

### 4.2 Kill protocol

Eight tests designed to destroy the signal:

| Test | Result | Key finding |
|------|--------|-------------|
| Prime reindexing (a_p conditioning) | SURVIVES | Signal increases 8% |
| Low-zero ablation | SURVIVES | Distributed across spectrum |
| CM vs non-CM split | PARTIAL | Present in both (rho ~ -0.15) |
| Low-zero coupling | SURVIVES | Signal strengthens 28% |
| Fine conductor bins (50) | SURVIVES | z = -29.3 |
| Local reduction conditioning | SURVIVES | rho = -0.113, p = 1.89 x 10^-86 |
| Twist stability | CONSISTENT | Identical zeros within classes |
| Asymptotic scaling | DECAYS | alpha = 0.464 ~ 1/2 |

### 4.3 Synthetic null validation

Four synthetic models, 200 trials each, with 0% false positive rate:

| Synthetic model | FPR |
|----------------|-----|
| GUE zeros + randomly permuted class size | 0.0% |
| Real zeros + conductor-predicted class size | 0.0% |
| Real zeros + factorization-predicted class size | 0.0% |
| GUE-resampled spacing + real class size | 0.0% |

Both the real zeros *and* the real class sizes are required to produce the signal. Replacing either with synthetic data -- even conductor-correlated synthetic data -- destroys it.

### 4.4 Perturbation robustness

Adding Gaussian noise to zeros at increasing scales:

| Noise (% of mean spacing) | Signal retention |
|---------------------------|-----------------|
| 0.1% | 100.0% |
| 1% | 99.8% |
| 5% | 96.2% |
| 10% | 88.9% |
| 20% | 68.5% |
| 50% | 32.2% |

Smooth, monotonic degradation with no cliff -- the signature of a real signal, not a numerical artifact.

### 4.5 Higher-order spacing

The signal propagates across the zero spectrum, not concentrated in gamma\_2 - gamma\_1 alone:

| Gap | z-score | After conditioning on gap\_1 |
|-----|---------|----------------------------|
| gamma\_2 - gamma\_1 | 14.4 | (baseline) |
| gamma\_3 - gamma\_2 | 6.8 | rho = 0.054, p = 1.1 x 10^-21 |
| gamma\_4 - gamma\_3 | 4.8 | rho = 0.023, p = 6.2 x 10^-5 |
| gamma\_5 - gamma\_4 | -2.2 | n.s. |
| gamma\_6 - gamma\_5 | 6.1 | rho = 0.048, p = 1.6 x 10^-17 |

The signal is not BSD-localized (first gap only) but global, with an unexpected rebound at gap\_5.

### 4.6 Interpretation

The most parsimonious explanation: isogeny class size approximates Hecke orbit multiplicity. Greater multiplicity corresponds to greater symmetry in the underlying automorphic representation, which produces stronger eigenvalue repulsion at finite conductor. The N^(-1/2) decay is consistent with random matrix theory finite-size corrections to an exact symmetry.

### 4.7 Factorization confound

Conditioning on conductor factorization features (number of distinct prime factors omega, total factors Omega, largest prime factor, primality, squarefreeness) reduces the signal by 28% but it survives: rho = 0.096, p = 1.4 x 10^-64. The signal is stronger for conductors with fewer prime factors (omega=1: rho = 0.331; omega=5: rho = 0.072), consistent with simpler Euler products yielding cleaner spectral signals.

---

## 5. Unified Spectral-BSD Model

We extract 25 spectral features from zero positions (gaps, spacing ratios, moments, density statistics) and build cross-validated predictive models for three arithmetic targets.

### 5.1 Rank prediction

| Model | Accuracy |
|-------|----------|
| Majority baseline | 50.2% |
| Conductor only (logistic regression) | 51.4% |
| Spectral only (logistic regression) | 88.3% |
| **Spectral only (gradient boosting)** | **92.1%** |
| Spectral + conductor | 99.99% |

Zeros predict rank with 92.1% accuracy using no conductor information. The dominant feature is gamma\_1 (49% importance), followed by zero variance (24%). This is a direct spectral manifestation of BSD: the order of vanishing at s = 1 determines gamma\_1.

Confusion matrix (spectral gradient boosting, 5-fold CV):

|  | pred 0 | pred 1 | pred 2 |
|--|--------|--------|--------|
| true 0 | 14,467 | 1,132 | 0 |
| true 1 | 838 | 13,835 | 110 |
| true 2 | 0 | 365 | 326 |

Rank-0 and rank-1 are well-separated spectrally. Rank-2 is harder (47% accuracy) due to small sample size (691 curves).

### 5.2 Isogeny class size prediction

| Model | R^2 |
|-------|-----|
| Conductor only | 0.026 |
| Spectral only (Ridge) | 0.069 |
| **Spectral only (gradient boosting)** | **0.249** |
| Spectral + conductor (Ridge) | 0.074 |

Spectral features predict class size at R^2 = 0.249 -- 10x the conductor baseline. The gradient boosting model captures nonlinear relationships that linear regression misses. The dominant features are mean gap (8.5%), zero variance (8.0%), and zero skewness (7.9%): the *shape* of the gap distribution, not any single spacing.

### 5.3 Sha prediction (rank-0 only)

| Model | R^2 |
|-------|-----|
| Conductor only | 0.004 |
| Spectral only (Ridge) | 0.013 |
| **Spectral only (gradient boosting)** | **0.067** |

The weakest channel but nonzero. Critically, the features that predict Sha are *different* from those that predict rank or class size: spacing ratios (ratio\_4: 6.6%), gap\_3 (6.5%), and max gap (6.0%). Sha lives in the higher-order spacing structure.

### 5.4 Three independent spectral channels

| Arithmetic invariant | Spectral channel | Dominant feature |
|---------------------|-----------------|-----------------|
| Rank | First zero position | gamma\_1 |
| Isogeny class size | Gap distribution shape | mean gap, variance, skewness |
| Sha | Higher-order spacing ratios | ratio\_4, gap\_3, max gap |

These channels are approximately independent: removing gamma\_1 from the class size model has negligible effect (< 1% R^2 change), and the features important for Sha prediction (spacing ratios) are unimportant for rank (< 0.1% importance).

---

## 6. Goldfeld Conjecture: Quantitative Constraints

The Goldfeld conjecture predicts that the average rank of elliptic curves over Q tends to 1/2 as conductor approaches infinity, implying that the fraction of curves with rank >= 2 tends to zero.

### 6.1 Observed rank-2 growth

Across 3,064,705 curves with conductor <= 500,000, the rank->=2 fraction grows monotonically:

| Conductor | % rank >= 2 | % rank 0 |
|-----------|------------|----------|
| ~100 | 0.0% | 82.1% |
| ~1,300 | 1.0% | 51.0% |
| ~5,500 | 4.6% | 42.8% |
| ~48,000 | 9.6% | 39.8% |
| ~400,000 | 13.2% | 37.0% |

### 6.2 Logistic saturation

We fit four models to the rank->=2 fraction as a function of conductor:

| Model | R^2 |
|-------|-----|
| Logarithmic: a * log10(N) + b | 0.980 |
| Power law: a * N^b | 0.925 |
| **Logistic: L / (1 + exp(-k(log10(N) - x0)))** | **0.995** |

The logistic model (R^2 = 0.995) predicts saturation at L = 13.7% with midpoint at conductor 10^4.23 ~ 17,000. The growth is already decelerating.

This is **Goldfeld-compatible**: if rank->=2 saturates at 13.7%, the remaining 86.3% are rank 0-1, and their ratio can approach 50/50 asymptotically. The logarithmic model (R^2 = 0.980) predicts unbounded growth and is Goldfeld-incompatible.

### 6.3 Extrapolation

| Conductor | Logistic | Logarithmic |
|-----------|----------|-------------|
| 10^6 | 13.2% | 14.9% |
| 10^7 | 13.6% | 19.3% |
| 10^9 | 13.7% | 28.2% |
| 10^12 | 13.7% | 41.6% |

The models diverge dramatically above N = 10^6, making extended conductor data decisive.

### 6.4 Prime conductor effect

Curves with prime conductor have significantly higher average rank (0.717) than those with composite conductor (0.553), controlling for conductor magnitude. This parallels the spectral signal: fewer prime factors yield both higher rank and stronger spacing-class size coupling.

---

## 7. BSD Spectral Decomposition

### 7.1 First zero and rank

BSD predicts that rank-r curves have L(E,s) vanishing to order r at s = 1/2. The first nontrivial zero height should increase with rank:

| Rank | n | Mean gamma\_1 | Min gamma\_1 |
|------|---|-------------|-------------|
| 0 | 15,599 | 0.1535 | 0.0219 |
| 1 | 14,783 | 0.2193 | 0.0793 |
| 2 | 691 | 0.2573 | 0.1575 |

Rank-1 gamma\_1 is 43% higher than rank-0; rank-2 is 67% higher. The minimum gamma\_1 also increases (0.022 -> 0.079 -> 0.158), consistent with BSD.

### 7.2 Sha concentration

Sha is perfectly square across 3,064,705 curves (100.0000%). Its variation concentrates entirely in rank 0:

| Rank | Mean Sha | % with Sha > 1 |
|------|----------|----------------|
| 0 | 2.56 | 19.0% |
| 1 | 1.05 | 1.3% |
| >= 2 | 1.00 | 0.0% |

This matches BSD structure: for rank >= 1, the regulator dominates variation; for rank 0, the regulator is trivial and Sha absorbs the analytic information.

### 7.3 Delaunay heuristic deviation

The Cohen-Lenstra-Delaunay heuristic predicts Prob(p^2 | Sha) ~ 1/p. We observe 4-50x suppression:

| p | Observed | Predicted (1/p) | Ratio |
|---|----------|-----------------|-------|
| 2 | 13.4% | 50.0% | 0.27 |
| 3 | 4.3% | 33.3% | 0.13 |
| 5 | 0.7% | 20.0% | 0.04 |
| 7 | 0.2% | 14.3% | 0.01 |

The suppression grows with p, indicating that Sha is far more constrained than a random finite abelian group. The Sha-torsion correlation (rho = 0.110) provides the mechanism: BSD ties them together; the heuristic assumes independence.

---

## 8. Katz-Sarnak Symmetry Types

We split curves by root number into SO(even) (rank 0, epsilon = +1) and SO(odd) (rank 1, epsilon = -1) families and measure the scaled first zero height gamma\_1 * log(N) / (2*pi).

| Symmetry | n | Mean scaled gamma\_1 | % below 0.2 |
|----------|---|---------------------|-------------|
| SO(even) | 15,599 | 0.169 | 76.4% |
| SO(odd) | 14,783 | 0.262 | 13.6% |

SO(even) zeros cluster closer to the origin, consistent with the Katz-Sarnak 1-level density W\_SO(even)(x) = 1 + sin(2*pi*x)/(2*pi*x) having enhanced density near x = 0. SO(odd) 1-level density (after the forced zero) is depleted near the origin. The separation is clean and conductor-independent.

---

## 9. Discussion

### 9.1 What the zeros encode

Our results show that L-function zeros carry arithmetic information in structured, separable channels:

1. **First zero position** (gamma\_1) encodes **rank**. This is a direct spectral consequence of BSD: the order of vanishing determines how far the first nontrivial zero sits from the critical point.
2. **Gap distribution shape** (mean spacing, variance, skewness) encodes **isogeny class size**. This is a finite-size spectral effect: greater Hecke orbit multiplicity produces stronger eigenvalue repulsion, decaying as N^(-1/2).
3. **Higher-order spacing ratios** encode **Sha**. This is the weakest channel but uses features orthogonal to the other two, suggesting an independent encoding.

### 9.2 The negative space

Equally important is what the zeros do *not* encode through invariant-level features. Eighteen cross-domain claims were killed, establishing that mathematical structure does not live in ordinal matching, magnitude mediation, distributional coincidence, or hand-crafted feature engineering. The only surviving representation is the zero spectrum itself.

### 9.3 Relation to the Langlands program

Our empirical finding -- that arithmetic invariants perturb an underlying universal spectral system -- is consistent with the Langlands philosophy that automorphic representations provide a unified framework. The three spectral channels may correspond to three aspects of the automorphic representation: the L-value at s = 1 (rank), the Hecke orbit structure (class size), and the arithmetic of the symmetric square L-function (Sha).

### 9.4 Limitations

- **Conductor range**: Our zero data is limited to N <= 50,000, mostly N <= 5,000. The N^(-1/2) scaling needs verification at larger conductor.
- **Independent replication**: All results use LMFDB data. Replication on the Cremona database (independent computation pipeline) is needed.
- **Analytic conductor**: Spectral statistics should be normalized by analytic conductor, not arithmetic conductor, for precise RMT comparison.
- **Family mixing**: Results average over all elliptic curves rather than restricting to fixed families (e.g., quadratic twist families).
- **Effect size**: The class size signal, while statistically overwhelming (z = -29.3), explains only ~1.7% of variance in pairwise correlation. The gradient boosting model captures 24.9%, suggesting significant nonlinearity.
- **LMFDB consistency**: The 100% verification rates for rank = analytic rank and Sha perfectness confirm pipeline correctness, not independent BSD evidence, as LMFDB enforces internal consistency.

---

## 10. Conclusion

L-function zeros encode arithmetic invariants of elliptic curves through three independent spectral channels. This encoding survives aggressive adversarial testing, including 18 kills of alternative explanations, synthetic null validation at 0% false positive rate, and smooth degradation under perturbation.

The rank channel (gamma\_1 predicts rank at 92.1%) is a direct spectral manifestation of BSD. The class size channel (gap distribution predicts class size at R^2 = 0.249) is a finite-size spectral effect consistent with Hecke orbit multiplicity perturbing eigenvalue repulsion. The Sha channel (higher-order ratios predict Sha at R^2 = 0.067) is weaker but spectrally orthogonal to the other two.

The rank->=2 growth law follows a logistic curve (R^2 = 0.995) with predicted saturation at 13.7%, providing quantitative evidence compatible with the Goldfeld conjecture.

These results suggest that the spectral theory of L-functions, particularly the finite-size corrections to random matrix universality, is the correct framework for understanding how arithmetic invariants are encoded in analytic data. The computational instrument developed here -- a falsification-first exploration engine with a 38-test adversarial battery, 3.8 million curves, and systematic synthetic null validation -- may be applicable to other spectral problems in arithmetic geometry.

---

## Acknowledgments

This work uses data from the LMFDB (https://www.lmfdb.org), developed by a large collaborative effort. Computations were performed on two independent machines (M1/Skullport, M2/SpectreX5) with cross-validation. We thank the developers of the LMFDB, SageMath, DuckDB, and scikit-learn.

## Data and Code Availability

All analysis scripts, result files, and adversarial battery specifications are available in the Prometheus repository. The Charon database and LMFDB Postgres mirror were used for all computations.
