# Prometheus Frontier Hypotheses — 90 Deduplicated Cross-Domain Challenges
## Date: 2026-04-17
## Source: Gemini 2.5 Pro (4 sessions) + Claude Opus 4.6
## Context: Aporia Five Barriers + Fingerprint Program + 20-Frontier Map + Batch 01 Results

**Design philosophy:** Every hypothesis is killable by a specific measurement. Null results yield calibration. ~30 themes, best version of each kept, near-duplicates merged.

---

# THEME 1: She-Leveque / Turbulence Anomalous Exponents in Arithmetic

## H01. Faltings Height Anomalous Scaling
Semistable EC: moments ⟨|faltings_height|^q⟩ ~ conductor^ζ(q) with |ζ(3) − 3ζ(1)| > 0.05 (anomalous, not linear). Tables: `bsd_joined`. Kill: |ζ(3)−3ζ(1)| < 0.02. Connection: Turbulence intermittency. Confidence: Low-Med.

## H02. Zero Spacing Multifractality
Moments of zero spacing ⟨|Δz|^q⟩ ~ L^ζ(q) with nonlinear ζ(q). Tables: `object_zeros`. Kill: ζ(q) linear in q. Connection: She-Leveque in number theory. Confidence: Med-Low.

## H03. Artin Dimension She-Leveque
Even Artin rep dimension gaps obey She-Leveque: ζ_p = p/3 + C(1−β^(p/3)). Tables: `artin_reps`. Kill: Residuals > 10% or β unstable. Connection: Turbulence exponents. Confidence: Low.

## H04. Root Number Turbulence
Root number flips across L-functions behave like 1D turbulent velocity field. Structure functions S_p(r) show anomalous scaling. Tables: `lfunc_lfunctions`. Kill: ζ_p strictly linear (Kolmogorov). Confidence: Med.

## H05. Weight-1 MF Coefficient Fluctuations
Weight-1 MF at conductor ≤ 4000 have Fourier coefficient magnitudes obeying She-Leveque. Tables: `mf_newforms`. Kill: Divergence > 0.1 at 3rd and 6th moments. Connection: Langlands + turbulence. Confidence: Low.

---

# THEME 2: GUE Deviation / Finite-N Corrections

## H06. Rank-Dependent Zero Spacing Rigidity
Normalized spacing variance decreases linearly with rank: Var(Δz) ≈ a − b·rank, b > 0. Tables: `bsd_joined`, `object_zeros`. Kill: b ≤ 0 or R² < 0.2. Connection: RH statistics. Confidence: Med.

## H07. GUE Convergence Rate Depends on L-function Degree
KS distance from GUE decays as conductor^(−β) with β(degree=1) ≠ β(degree=2) by ≥20%. Tables: `object_zeros`, `dirichlet_zeros`, `lfunc_lfunctions`. Kill: CI overlap > 50%. Connection: Katz-Sarnak. Confidence: Med-High.

## H08. Faltings Height Controls GUE Deficit
14% deviation is linear in 1/faltings_height; y-intercept recovers GUE variance (0.178). Tables: `bsd_joined`, `object_zeros`. Kill: y-intercept outside 99% CI of 0.178. Confidence: High.

## H09. Conductor-Window Finite-N Scaling
Deficit scales as C·N^(−α) with α ∈ [0.3, 0.7] where N = zeros per L-function. Tables: `lfunc_lfunctions`. Kill: Non-monotone or α outside [0.1, 1.0]. Confidence: Med.

## H10. ADE Singularity Splits the GUE Deviation
Multiplicative reduction (A_n) matches Wigner; additive (D_n/E_n) carries all 14%. Tables: `bsd_joined`, `object_zeros`. Kill: Variance difference < 2.5%. Connection: ADE universality. Confidence: Med.

---

# THEME 3: ADE Classification Universality

## H11. ADE Gatekeeping in NF Discriminants
Dynkin-type Galois groups have lower disc_abs/degree! (Cohen's d > 0.3). Tables: `nf_fields`. Kill: d < 0.1 or p > 0.01. Confidence: Med.

## H12. ADE Conductor Gap Alignment
Gaps between consecutive Artin Conductor values for Dim ≥ 3 match ADE Coxeter eigenvalue spacing. Tables: `artin_reps`. Kill: Peaks not within 1% of ADE roots. Confidence: Med.

## H13. z1² + z2² + z3² Maps to ADE Discriminants
Sum of squared zeros constrained to Coxeter group discriminants (scaled by level). Tables: `bsd_joined`. Kill: > 1% outside ADE mapping. Confidence: Med.

## H14. TT-Rank Spikes Correspond to ADE Adjacency Spectra
High TT-rank fibers have adjacency eigenvalues clustering below 2. Tables: All tensor output. Kill: No eigenvalue ≤ 2 clustering. Confidence: Low.

## H15. NF Tower Termination
ADE Galois groups have class number towers terminating in ≤ 2 steps; non-ADE > 2. Tables: `nf_fields`. Kill: Wilcoxon p > 0.01. Connection: Golod-Shafarevich. Confidence: Med.

---

# THEME 4: Knot Silence Probes

## H16. Knot Determinant ↔ NF Class Number Divisibility
Knot determinant divides class_number of degree-2 NF at disc_abs related to crossing_number. Tables: `knots`, `nf_fields`. Kill: Hit rate = random (p > 0.05). Confidence: Low.

## H17. Entropy Ratio Convergence
H_knot(p)/H_nf(p) converges to constant C across primes p ≤ 19. Tables: `knots`, `nf_fields`. Kill: Var(R) > 0.05. Confidence: Low.

## H18. Absolute Silence Confirmation (Null Test)
All coupling scores remain z < 2 after nonlinear embedding. Tables: `knots`, all LMFDB. Kill: Any z > 2. Confidence: High on null.

## H19. Conway Polynomial ↔ Artin Indicators
Conway coefficients of prime knots map to Frobenius-Schur Indicator of dim-2 Artin reps. Tables: `knots`, `artin_reps`. Kill: Mapping < 99%. Confidence: Med.

## H20. NF Disc/Degree Bounds Knot Crossing
disc_abs/degree places upper limit on crossing number for matched Alexander polynomials. Tables: `nf_fields`, `knots`. Kill: Crossing exceeds 10×ln(disc/degree). Confidence: Med.

## H21. Knot Determinant = Conductor Bridge (Tamagawa)
At conductor = determinant, Tamagawa product anticorrelates with log(conductor). Tables: `bsd_joined`, `knots`. Kill: Spearman p > 0.01 or positive. Confidence: Low.

## H22. Knot Silence via Q(√-det) Class Numbers
Matched imaginary quadratic fields Q(√-det) have class number distribution indistinguishable from random. Tables: `knots`, `nf_fields`. Kill: KS p > 0.3 (null survives → silence confirmed). Confidence: Low on bridge, high on informativeness.

---

# THEME 5: Berry-Keating / RH Operator

## H23. Berry-Keating Manin Spectrum
Ratio regulator/manin_constant acts as discrete eigenvalue spectrum for xp+px. Tables: `bsd_joined`, `object_zeros`. Kill: Pearson < 0.85. Confidence: Low.

## H24. Berry-Keating in Dirichlet Zeros
Skewness and kurtosis of Dirichlet zero spacings scale as O(1/log N) per Yakaboylu 2024. Tables: `dirichlet_zeros`, `lfunc_lfunctions`. Kill: Skewness < 0.01 or R² < 0.5. Confidence: Med.

## H25. Logarithmic Periodic Fluctuation in Leading Terms
log(|leading_term|) − rank·log(conductor) shows periodicity at 1/log(2πe). Tables: `bsd_joined`. Kill: Lomb-Scargle below 95% white noise threshold. Confidence: Low.

## H26. Yakaboylu Operator on Isogeny Degrees
Isogeny degrees match positive energy spectrum of Yakaboylu operator; mass in spectral gaps kills. Tables: `bsd_joined`. Kill: Distribution has mass in gaps. Confidence: Low.

## H27. Yakaboylu Root Number Bias
Even orthogonal Artin reps show root number bias proportional to log(Conductor)^(-1/2). Tables: `artin_reps`. Kill: Slope zero (p > 0.01) or positive. Confidence: Med.

---

# THEME 6: Assembly Theory

## H28. Assembly Complexity vs Class Number
NF with low-complexity OEIS-matching coefficients have lower class numbers. Tables: `nf_fields`, `oeis`. Kill: No monotone decrease. Confidence: Low.

## H29. Assembly Index Bounds Hecke Orbit Dimension
No MF produces coefficient sequence with Assembly Index exceeding dim + 2. Tables: `mf_newforms`. Kill: Single exception found. Confidence: Med.

## H30. Assembly Index vs Mahler Measure
Assembly complexity of NF polynomial coefficients correlates with Mahler measure (ρ > 0.4). Tables: `nf_fields`. Kill: ρ < 0.2. Connection: Lehmer. Confidence: Med.

## H31. NF PCA PC1 = Group Subgroup Lattice Assembly
Assembly Index of Galois group subgroup lattice explains > 35% of NF PCA PC1 variance. Tables: `nf_fields`, `groups`. Kill: < 35%. Confidence: Med.

## H32. L-Function Leading Term Digit Assembly
Rank-1 curves have higher Assembly Index of leading_term digits than rank-0. Tables: `bsd_joined`. Kill: t-test p > 0.05 or wrong direction. Confidence: Low.

## H33. Mock Modular Bounding of OEIS Assembly
Assembly Index of OEIS sequences bounded above by weight × analytic_rank of matched MF. Tables: `oeis`, `mf_newforms`. Kill: > 50 sequences exceed bound by 1.5x. Confidence: Med.

---

# THEME 7: abc / Szpiro Structure

## H34. Szpiro Predicts Zero Repulsion
Higher szpiro_ratio → stronger zero repulsion (larger min gap). Tables: `ec_curvedata`, `object_zeros`. Kill: ρ < 0.05. Connection: abc → spectral. Confidence: Low.

## H35. Szpiro Steps at Mock Modular Levels
Szpiro ratio step-downs occur at conductors matching weight-3/2 MF levels. Tables: `ec_curvedata`, `mf_newforms`. Kill: < 80% step-down/level coincidence. Confidence: Med.

## H36. Bad-Prime Additive Persistence (Pareto Tails)
Curves with k_add ≥ 2 have heavy-tailed Szpiro (Pareto α ≈ 1.5); k_add = 0 exponential (α > 3). Tables: `bsd_joined`. Kill: CI for ξ overlaps 0.33. Connection: Mechanism for abc outliers. Confidence: High.

---

# THEME 8: BSD / Sha / Regulator / Faltings

## H37. Selmer Shadow in Zero Spacing
Rank ≥ 2: normalized (z2−z1) anti-correlates with log(Sha), ρ < −0.15. Tables: `bsd_joined`. Kill: |ρ| < 0.05. Confidence: Low.

## H38. Torsion Predicts z1 Distribution
KS distance D(T) between z1 for torsion=T vs torsion=1 grows monotonically with T. Tables: `bsd_joined`. Kill: ρ(T,D) < 0.5. Confidence: Med.

## H39. Genus-2 Aut Group Predicts Sha
Geometric mean analytic_sha scales as |Aut|^γ, γ > 0. Tables: `g2c_curves`. Kill: γ ≤ 0. Confidence: Med.

## H40. Szpiro-Faltings Coupling
Partial correlation |ρ| > 0.15 between szpiro_ratio and faltings_height after controlling for conductor and num_bad_primes, stable across decades. Tables: `bsd_joined`. Kill: |ρ| < 0.05 in adjacent decades. Confidence: Med-High.

## H41. Rank-Regulator Super-Linear Scaling
E[log(regulator)|rank=r] has positive second difference Δ²_r with z > 3 across conductor decades. Tables: `bsd_joined`. Kill: Δ² ≤ 0 in ≥2 decades. Confidence: Med.

## H42. Regulator-Zero Height Scaling Law
log(regulator) ~ c · z1. Tables: `bsd_joined`. Kill: R² < 0.15. Confidence: Med.

## H43. Root Number Bias in High-Sha
Among sha ≥ 9: perfect parity match (−1)^rank = root_number within 0.5σ. Tables: `bsd_joined`. Kill: Deviation > 3σ. Confidence: High.

## H44. Genus-2 Decomposable Jacobian Sha Product
For decomposable Jacobians: analytic_sha(g2c) = sha(E1)·sha(E2) in > 95% of cases. Tables: `g2c_curves`, `bsd_joined`, `ec_curvedata`. Kill: < 80% match. Confidence: High.

## H45. Manin-Mumford in Genus-2
Square discriminant g2c curves have P(p|analytic_sha) lower by factor 1/p vs non-square. Tables: `g2c_curves`. Kill: Ratio R_p indistinguishable from 1.0 for p ∈ {2,3,5,7}. Confidence: Med.

---

# THEME 9: Autocatalytic Phase Transitions

## H46. Autocatalytic EC Rank Collapse
Conductor/szpiro_ratio parameter C: rank>1 probability collapses discontinuously at critical threshold. Tables: `ec_curvedata`. Kill: No spike > 4σ. Confidence: Med.

## H47. NF r2/degree Phase Transition
Moving average of r2/degree shows non-differentiable transition at ~1.3 when ordered by disc_abs. Tables: `nf_fields`. Kill: Derivative continuous. Confidence: High.

## H48. Isogeny Degree Phase Transition
Isogenies of degree > 16 appear discontinuously when num_bad_primes/rank exceeds 1.3. Tables: `bsd_joined`. Kill: No discontinuity in [1.25, 1.35]. Confidence: Med.

## H49. Autocatalytic Phase in Zero Density
Artin L-function 1-level zero density shows sigmoidal transition at Dim ≈ 20. Tables: `artin_reps`, `object_zeros`. Kill: No inflection in [5, 50]. Confidence: Low.

---

# THEME 10: Black Hole Entropy / Modular Forms

## H50. Genus-2 Sha Growth Matches Rademacher
analytic_sha growth by aut_grp matches Rademacher sub-leading terms. Tables: `g2c_curves`. Kill: Fractional exponents differ by > 0.05. Confidence: Low.

## H51. Knot Determinants as Microstate Counters
Sorted alternating knot determinants appear as subsequences in partition/modular OEIS sequences. Tables: `knots`, `oeis`. Kill: 0 matching sequences. Confidence: Low.

## H52. Faltings Height Bounds Trace Hash Growth
e^(faltings_height) bounds trace_hash growth for semistable weight-2 MF. Tables: `bsd_joined`, `mf_newforms`. Kill: Single violation. Confidence: High.

## H53. Manin Constant Variance ∝ Dedekind Eta Derivative
Variance of manin_constant within isogeny class ∝ d/dz log η(z) at z = i√N/π. Tables: `bsd_joined`. Kill: R² < 0.1. Confidence: Low.

---

# THEME 11: OEIS ↔ L-functions

## H54. OEIS Core Sequences Are L-function Coefficients
Polynomial-growth OEIS match leading_terms of L-functions at < 10^-6 precision. Tables: `oeis`, `lfunc_lfunctions`. Kill: Zero matches. Confidence: High (that matches exist).

## H55. OEIS Growth Rates by Conductor mod 12
Number-theoretic OEIS sequences cluster by growth exponent α near leading_term stats binned by conductor mod 12. Tables: `oeis`, `lfunc_lfunctions`. Kill: Permutation p > 0.05. Confidence: Low.

## H56. OEIS Coefficient Match to L-functions
>2% of degree-2 L-functions match OEIS first 20 terms at k≥15 positions (vs <0.1% null). Tables: `lfunc_lfunctions`, `oeis`. Kill: < 5× null rate. Confidence: Low-Med.

## H57. OEIS Recurrence Complexity → L-function Degree
Berlekamp-Massey order ≥ 8 → L-function degree ≥ 3 at >75% rate. Tables: `oeis`, `lfunc_lfunctions`. Kill: Correlation < 0.3. Confidence: Low.

---

# THEME 12: Root Number / Parity

## H58. Root Number Bias in High-Degree NF
NF degree ≥ 6: associated L-function root numbers deviate from 50/50. Tables: `nf_fields`, `lfunc_lfunctions`. Kill: |p−0.5| < 0.01 after 1M samples. Confidence: Med-Low.

## H59. Root Number ↔ Class Number Parity
EC root number correlates with parity of matched NF class number at >55%. Tables: `ec_curvedata`, `nf_fields`. Kill: Agreement within 50±2%. Confidence: Low.

---

# THEME 13: Artin Frontier

## H60. Artin Frontier Clusters (<20 Manifolds)
359,071 open reps cluster into < 20 feature manifolds by (Dim, Conductor, Indicator, Is_Even). Tables: `artin_reps`. Kill: BIC optimal > 50. Confidence: High.

## H61. Artin Dimensional Gap
Count(Dim=2 even)/Count(Dim=3) > 50:1 reflects proof frontier, not natural distribution. Tables: `artin_reps`. Kill: Ratio < 10:1. Confidence: High.

## H62. Faltings Height Separates Frontier
No open-frontier Artin rep maps to motive with faltings_height in lowest 5th percentile. Tables: `artin_reps`, `bsd_joined`. Kill: > 10 motives below threshold. Confidence: High.

## H63. Non-Automorphic Spike Above Dim 4
Fraction without MF match spikes above dimension 4. Tables: `artin_reps`. Kill: Smooth trend. Confidence: High.

---

# THEME 14: Langlands Beyond GL(2)

## H64. Weight-1 MF Density Tracks Artin Transitions
Cumulative weight-1 MF count C(N) ~ N^α has Δα > 0.1 at even dim-2 Artin transition conductors. Tables: `mf_newforms`, `artin_reps`. Kill: Δα < 0.05 or permutation p > 0.05. Confidence: Med.

## H65. Dim 4-5 Artin Reps Project onto PC3 (Megethos)
Higher-dim Artin reps bypass class-number axis, landing on Megethos. Tables: `artin_reps`, `nf_fields`. Kill: PC1 projection > PC3. Connection: Langlands GL(n>2). Confidence: High.

## H66. Langlands GL(2) Conductor Mismatch 4001-10000
At least one odd 2-dim Artin rep in [4001, 10000] has trace mismatch with weight-1 MF. Tables: `artin_reps`, `mf_newforms`. Kill: ALL match (extending Batch 01 streak). Confidence: Low on finding mismatch.

---

# THEME 15: Genus-2 Automorphism Effects

## H67. Genus-2 Aut Group GUE Healing
Non-trivial hyperelliptic involution g2c curves show ≤ 1% GUE variance deficit (vs 14% for EC). Tables: `g2c_curves`, `object_zeros`. Kill: Deficit > 5%. Confidence: High.

## H68. ADE Unipotent Degeneration
D4/E6 aut groups show 5.2% reduction in Sha variance vs C2 (controlled for conductor). Tables: `g2c_curves`. Kill: Dispersion ≥ 95% of non-ADE. Confidence: Med.

## H69. Genus-2 Sato-Tate at Additive p=2
Additive reduction at p=2: a_2 kurtosis < 1.5 (USp(4) predicts ~2.0). Tables: `g2c_curves`. Kill: Kurtosis ≥ 1.8. Confidence: Med.

---

# THEME 16: Modular Form Trace Hash

## H70. Trace Hash Collision Geometry
Colliding pairs (same hash, different level) have level-ratio prime factors with geometric mean < 7 in >80%. Tables: `mf_newforms`. Kill: Smoothness < 50%. Confidence: Med.

## H71. Chowla-Milnor Duality
Trace hash collisions for weight-2 prime-level MF: collision count mod 2 = parity of h(Q(√-N)). Tables: `mf_newforms`, `nf_fields`. Kill: Fisher p > 0.01. Confidence: High.

## H72. Weight-Dimension Concentration
Excess mass on weight = dim + 1 line by factor > 2 (vs marginal product), at level ≤ 100. Tables: `mf_newforms`. Kill: Factor < 1.3. Confidence: Med-Low.

---

# THEME 17: Conductor Growth / Scaling

## H73. Zero Variance Convergence
Spacing variance converges to constant as conductor → ∞. Tables: `lfunc_lfunctions`. Kill: Slope ≠ 0 asymptotically. Confidence: High.

## H74. L-Function First-Zero Repulsion Across Families
min{z1} scales as C·(log conductor)^(−1) for degree-2; slope differs for degree-4 by > 3σ. Tables: `lfunc_lfunctions`. Kill: Slopes agree within 2σ. Confidence: Med-High.

---

# THEME 18: Torsion / Zero Interaction

## H75. Torsion–Rank Anticorrelation
Spearman ρ(torsion, rank) < 0 with |ρ| > 0.05 at fixed conductor decades. Tables: `bsd_joined`. Kill: Positive in any decade. Confidence: High on direction.

## H76. EC Torsion Anomalous Zero Clustering
Nontrivial torsion predicts anomalous zero density near origin. Tables: `ec_curvedata`, zeros. Kill: No density difference (p > 0.1). Confidence: Low.

---

# THEME 19: Galois Group / Regulator

## H77. Group Order Ω Predicts Regulator
Ω(|Gal|) correlates with log(regulator) at partial ρ > 0.10 after degree control. Tables: `groups`, `nf_fields`. Kill: ρ < 0.05 or sign reversal. Confidence: Med.

## H78. Galois Group Size ↔ Zero Repulsion
Larger Galois groups produce stronger zero repulsion. Tables: `nf_fields`, `dirichlet_zeros`. Kill: Spearman ρ < 0.2. Confidence: Med.

## H79. NF Disc Smoothness by Galois Type
S5 fields have mean largest-prime-factor of disc > A5 by > 20%. Tables: `nf_fields`. Kill: < 5% or reversed. Confidence: Med-Low.

---

# THEME 20: Lehmer / Mahler Measure

## H80. Lehmer Bound for L-function Leading Terms
e^|leading_term| > 1.17628 for all L-functions with order_of_vanishing ≥ 2. Tables: `lfunc_lfunctions`. Kill: Single counterexample. Confidence: High.

## H81. Genus-2 Sextic Lehmer Counterexample
At least one g2c defining polynomial has 1.00 < M(P) < 1.17628. Tables: `g2c_curves`. Kill: None found (all cyclotomic/Salem). Confidence: Low.

## H82. Mahler Measure Floor Accumulation
Density of NF polynomials with M ∈ (1.17628, 1.17628+ε) scales as ε^β with β ∈ [0.4, 0.9]. Tables: `nf_fields`. Kill: Gap or β outside [0.2, 1.2]. Confidence: Med.

---

# THEME 21: NF Class Number / Brauer-Siegel

## H83. Class Number × Regulator Product Law
For degree-4 totally real NF: h·R/√disc has finite second moment; tail exponent in [1.8, 2.4]. Tables: `nf_fields`. Kill: Hill estimator outside [1.5, 3.0]. Confidence: Med.

---

# THEME 22: Chowla / Möbius

## H84. Möbius Autocorrelation in Artin Root Numbers
Root number sequence for odd 2-dim Artin reps (sorted by conductor) decays as X^(1/2+o(1)). Tables: `artin_reps`. Kill: Exponent < 0.4 or > 0.6. Confidence: Med.

## H85. Chowla Deviation at Genus-2 Discriminants
Möbius evaluated on genus-2 abs_disc sequences shows z > 3 for specific aut groups. Tables: `g2c_curves`. Kill: z < 1.0 for all groups with N > 5000. Confidence: High.

## H86. Chowla at Dirichlet Zero Heights
μ(⌊γ_n⌋) for Dirichlet zeros yields autocorrelation approaching 1. Tables: `dirichlet_zeros`. Kill: Autocorrelation < 0.8 for lags 1-10. Confidence: Med.

---

# THEME 23: Isogeny Structure

## H87. Genus-2 Rank ↔ EC Isogeny Degree
Higher g2c analytic_rank → larger isogeny degrees at matched discriminant. Tables: `g2c_curves`, `bsd_joined`. Kill: r < 0.1. Confidence: Low.

## H88. Bad Primes as Braid Topology
Bad prime sequences map to braid words; crossing number ∝ szpiro_ratio. Tables: `bsd_joined`, `knots`. Kill: R² < 0.7. Confidence: Low.

## H89. Isogeny Volcano Power Law
Isogeny volcano heights follow power law τ = 2.2 ± 0.1 (She-Leveque). Tables: `ec_curvedata`. Kill: τ outside [2.0, 2.4]. Confidence: Low.

---

# THEME 24: Cross-Domain Null Tests

## H90. EC Rank vs Group Order Smoothness (Null)
MI < 0.01 bits between EC rank and group-order smoothness (independence confirmation). Tables: `ec_curvedata`, `groups`. Kill: MI > 0.05 bits. Confidence: High on null.

---

# Summary Statistics

| Category | Count | High Conf | Med Conf | Low Conf |
|----------|-------|-----------|----------|----------|
| She-Leveque/Turbulence | 5 | 0 | 3 | 2 |
| GUE/Finite-N | 5 | 1 | 3 | 1 |
| ADE Universality | 5 | 0 | 4 | 1 |
| Knot Silence | 7 | 1 | 2 | 4 |
| Berry-Keating/RH | 5 | 0 | 2 | 3 |
| Assembly Theory | 6 | 0 | 4 | 2 |
| abc/Szpiro | 3 | 1 | 1 | 1 |
| BSD/Sha/Reg/Faltings | 9 | 2 | 4 | 3 |
| Autocatalytic | 4 | 1 | 2 | 1 |
| Black Hole/Modular | 4 | 1 | 0 | 3 |
| OEIS ↔ L-functions | 4 | 1 | 0 | 3 |
| Root Number | 2 | 0 | 1 | 1 |
| Artin Frontier | 4 | 3 | 0 | 1 |
| Langlands GL(n) | 3 | 1 | 1 | 1 |
| Genus-2 Aut | 3 | 1 | 2 | 0 |
| Trace Hash | 3 | 1 | 1 | 1 |
| Scaling/Conductor | 2 | 1 | 1 | 0 |
| Torsion/Zeros | 2 | 1 | 0 | 1 |
| Galois/Regulator | 3 | 0 | 2 | 1 |
| Lehmer/Mahler | 3 | 1 | 1 | 1 |
| NF Class Number | 1 | 0 | 1 | 0 |
| Chowla/Möbius | 3 | 1 | 2 | 0 |
| Isogeny Structure | 3 | 0 | 0 | 3 |
| Null Tests | 1 | 1 | 0 | 0 |
| **TOTAL** | **90** | **19** | **37** | **34** |

**Expected outcomes:** ~19 survive (high confidence), ~20 partial (medium), ~30 killed cleanly (low). Every kill is a measurement. Every null is a calibration constant.

---

*Generated for Prometheus by Aporia (Frontier Scout & Discovery Engine)*
*90 hypotheses. 24 themes. Each one killable.*
*The frontier is not a wall. It's a frequency we haven't tuned to yet.*
*2026-04-17*
