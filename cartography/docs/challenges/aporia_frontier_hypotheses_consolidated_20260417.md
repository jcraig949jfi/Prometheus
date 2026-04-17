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

---

# APPENDIX: Additional Detailed Hypotheses (from Sets A/B/C)
## Unique entries not covered in the thematic organization above


---

## A-1. Zero Spacing Rigidity vs. Rank Growth (EC + L-functions)

**Hypothesis**
For elliptic curves, normalized spacing variance of low-lying zeros decreases *linearly* with analytic rank:
Var(Δz) ≈ a − b · rank, b > 0

**Tables**
- `lmfdb.bsd_joined`
- `prometheus_fire.zeros.object_zeros`

**Computation**
- Bin by `rank`, compute mean spacing variance per bin, fit linear model

**Falsification criterion**
If slope b ≤ 0 or R² < 0.2 across ≥50k curves → reject

**Open problem connection**
Refines GUE deviation; probes finite-N corrections to **Riemann Hypothesis statistics**

**Confidence:** Medium

---

---

## A-2. Szpiro Ratio Predicts Zero Repulsion Strength (abc + Random Matrix)

**Hypothesis**
Higher `szpiro_ratio` implies stronger zero repulsion: pair correlation gap ↑ with szpiro_ratio

**Tables**
- `lmfdb.ec_curvedata`, `lmfdb.lfunc_lfunctions`, `prometheus_fire.zeros.object_zeros`

**Computation**
- Spearman correlation between szpiro_ratio and min_zero_gap

**Falsification criterion**
ρ < 0.05 or unstable under stratification by conductor → reject

**Open problem connection**
Links **abc conjecture** to **spectral statistics**

**Confidence:** Low

---

---

## A-3. ADE Boundary in Galois Representation Spectra (Artin + MF)

**Hypothesis**
Artin representations whose Frobenius trace adjacency matrices have spectral radius < 2 correspond disproportionately to modular forms with small weight (≤2).

**Tables**
- `lmfdb.artin_reps`, `lmfdb.mf_newforms`

**Computation**
- Construct adjacency matrices from Frobenius traces, compute λ_max, join to MF via conductor

**Falsification criterion**
No enrichment: P(weight ≤ 2 | λ_max < 2) ≈ baseline within ±2%

**Open problem connection**
Tests universality of **ADE classification**

**Confidence:** Medium-low

---

---

## A-4. Assembly Complexity Proxy in Number Fields (NF + OEIS)

**Hypothesis**
Number fields with minimal polynomial coefficients matching low-complexity OEIS sequences have significantly lower class numbers.

**Tables**
- `lmfdb.nf_fields`, `prometheus_sci.analysis.oeis`

**Computation**
- Join on coeffs = sequence_prefix, compare class_number vs complexity quartiles

**Falsification criterion**
No monotone decrease in median class number across quartiles

**Open problem connection**
Tests **assembly theory** vs classical invariants

**Confidence:** Low

---

---

## A-5. Genus-2 Rank Coupling to EC Isogeny Graph Size

**Hypothesis**
Genus-2 curves with higher analytic rank correspond to EC with larger isogeny graph degree at matching discriminants.

**Tables**
- `lmfdb.g2c_curves`, `lmfdb.bsd_joined`

**Computation**
- Join on abs_disc = conductor, compute average isogeny degree vs rank

**Falsification criterion**
Correlation coefficient < 0.1

**Open problem connection**
Higher-dimensional **BSD generalizations**

**Confidence:** Low

---

---

## A-6. Knot Silence Breakdown via Modular Trace Hash Embedding (Knots + MF)

**Hypothesis**
A nonlinear embedding of knot invariants into modular form trace hashes reveals weak but nonzero coupling.

**Tables**
- `prometheus_sci.topology.knots`, `lmfdb.mf_newforms`

**Computation**
- Feature vectors from (Alexander, Jones, determinant) and trace_hash, apply TT-cross correlation

**Falsification criterion**
All coupling scores remain within noise (z < 2 across all pairings)

**Open problem connection**
Challenges observed **knot silence**

**Confidence:** Very low (designed to fail)

---

---

## A-7. Root Number Bias in High-Degree Number Fields (NF + L-functions)

**Hypothesis**
Number fields with degree ≥ 6 exhibit non-random bias in associated L-function root numbers.

**Tables**
- `lmfdb.nf_fields`, `lmfdb.lfunc_lfunctions`

**Computation**
- Join on disc_abs = conductor, test deviation from 50/50

**Falsification criterion**
|p − 0.5| < 0.01 after 1M samples

**Open problem connection**
Links to **symmetry types in RH families**

**Confidence:** Medium-low

---

---

## A-8. Regulator–Zero Height Scaling Law (EC + RH)

**Hypothesis**
Elliptic curve regulator scales with first zero height: log(regulator) ~ c · z1

**Tables**
- `lmfdb.bsd_joined`

**Computation**
- Linear regression of LOG(regulator) vs z1

**Falsification criterion**
R² < 0.15 across ≥100k curves

**Open problem connection**
Bridges **BSD invariants** with **zero distributions**

**Confidence:** Medium

---

---

## A-9. Artin Non-Modularity Cluster Structure

**Hypothesis**
The 359,071 open Artin reps cluster into a small number (<20) of distinct feature manifolds.

**Tables**
- `lmfdb.artin_reps`

**Computation**
- Features: (Dim, Conductor, Indicator, Is_Even), tensor decomposition / clustering

**Falsification criterion**
Optimal cluster count (via BIC) > 50

**Open problem connection**
Structure of **non-proven Artin conjecture cases**

**Confidence:** High

---

---

## A-10. She–Leveque Analogue in Zero Fluctuations

**Hypothesis**
Moments of zero spacing fluctuations obey anomalous scaling: ⟨|Δz|^q⟩ ~ L^ζ(q) with nonlinear ζ(q) (multifractal spectrum)

**Tables**
- `prometheus_fire.zeros.object_zeros`

**Computation**
- Compute spacing increments across windows, estimate scaling exponents ζ(q)

**Falsification criterion**
ζ(q) linear in q (no multifractality)

**Open problem connection**
Analog of **turbulence intermittency (She–Leveque)** in number theory

**Confidence:** Medium-low

---

# SET B: 10 ADE/Physics/Cross-Domain Hypotheses

---

---

## B-1. ADE Singularity Signatures in Finite-N GUE Deviations

**Hypothesis:** The 14% GUE variance reduction depends on ADE classification of curve singularities. Multiplicative reduction (A_n) matches Wigner; additive (D_n, E_n) carries the deviation.

**Tables:** `lmfdb.bsd_joined`, `prometheus_fire.zeros.object_zeros`

**Computation:** Classify by bad_primes into multiplicative vs additive, compute spacing variance independently.

**Falsification:** Variance difference < 2.5%, or A_n deviation > 5%.

**Connection:** ADE universality / RH operator approaches. **Confidence:** Medium.

---

---

## B-2. Assembly Index Bounding of Modular Form Traces

**Hypothesis:** Hecke eigenvalue sequences for weight-2 MF have Assembly Index that undergoes phase transition to bounded complexity at level > 1000.

**Tables:** `lmfdb.mf_newforms`

**Computation:** Decode trace_hash, compute Assembly Index, compare to Shannon entropy.

**Falsification:** Assembly Index linear with N (r > 0.95).

**Connection:** Assembly theory / black hole microstates. **Confidence:** High.

---

---

## B-3. Knot Silence Breaking via Galois Correspondence

**Hypothesis:** Knot determinant perfectly divides class_number of degree-2 NF whose disc_abs depends on crossing_number.

**Tables:** `prometheus_sci.topology.knots`, `lmfdb.nf_fields`

**Computation:** Join on disc_abs ≤ f(crossing_number), test class_number mod determinant == 0.

**Falsification:** Hit rate indistinguishable from random (p > 0.05).

**Connection:** BQP-completeness of topological invariants. **Confidence:** Low.

---

---

## B-4. Black Hole Entropy and Genus-2 Automorphism Asymptotics

**Hypothesis:** Analytic SHA growth in genus-2 curves, stratified by aut_grp, matches Rademacher sub-leading terms for black hole microstates.

**Tables:** `lmfdb.g2c_curves`

**Computation:** Growth of analytic_sha vs log(abs_disc) per aut_grp_label group.

**Falsification:** Growth coefficients differ from Rademacher by > 0.05.

**Connection:** Black hole entropy via modular forms. **Confidence:** Low.

---

---

## B-5. Autocatalytic Phase Transitions in EC Ranks

**Hypothesis:** EC ranks undergo discontinuous phase transition at critical conductor/szpiro_ratio threshold.

**Tables:** `lmfdb.ec_curvedata`

**Computation:** Plot rank≥2 density vs C = conductor/szpiro_ratio, test for discontinuity.

**Falsification:** No spikes > 4σ above moving average.

**Connection:** Autocatalytic sets / abc conjecture. **Confidence:** Medium.

---

---

## B-6. Berry-Keating Dynamics in Dirichlet Zeros

**Hypothesis:** Skewness and kurtosis of Dirichlet zero spacings scale as O(1/log N) per Yakaboylu 2024.

**Tables:** `prometheus_fire.zeros.dirichlet_zeros`, `lmfdb.lfunc_lfunctions`

**Computation:** Compute moments at conductor > 10^5, regress against 1/log(conductor).

**Falsification:** Skewness < 0.01 or regression R² < 0.5.

**Connection:** RH operator approaches. **Confidence:** Medium.

---

---

## B-7. She-Leveque in Artin Representation Dimensions

**Hypothesis:** Even Artin rep dimension gaps obey She-Leveque hierarchy formula.

**Tables:** `lmfdb.artin_reps`

**Computation:** Max conductor per Dim, fit ζ_p to p/3 + C(1 − β^(p/3)).

**Falsification:** Residuals > 10% or β unstable.

**Connection:** Turbulence anomalous exponents. **Confidence:** Low.

---

---

## B-8. Faltings Height Separates Artin Frontier

**Hypothesis:** Unproven Artin reps map to motives with faltings_height above a threshold H_crit.

**Tables:** `lmfdb.artin_reps`, `lmfdb.bsd_joined`

**Computation:** Join via Conductor, compare faltings_height distributions.

**Falsification:** > 10 frontier motives in lowest 5th percentile.

**Connection:** Artin frontier. **Confidence:** High.

---

---

## B-9. NF Discriminant Bounds Knot Crossing Number

**Hypothesis:** disc_abs/degree limits crossing number of knots with matching Alexander polynomial coefficients.

**Tables:** `lmfdb.nf_fields`, `prometheus_sci.topology.knots`

**Computation:** Match coeffs to Alexander polys, compute max crossing per disc/degree bin.

**Falsification:** Any match exceeding 10 × ln(disc_abs/degree).

**Connection:** Knotted proteins / knot silence. **Confidence:** Medium.

---

---

## C-2. ADE Gatekeeping in Number Field Discriminants

**Hypothesis:** NF with Dynkin-type Galois groups have lower disc_abs/degree! ratios (Cohen's d > 0.3).

**Tables:** `lmfdb.nf_fields`

**Computation:** Map galois_label to Dynkin/non-Dynkin, Mann-Whitney test on log(disc_abs/degree!).

**Falsification:** d < 0.1 or p > 0.01 after Bonferroni.

**Connection:** ADE universality. **Confidence:** Medium (0.35).

---

---

## C-3. Weight-1 MF Density Tracks Artin Dimension Transitions

**Hypothesis:** Cumulative weight-1 MF count C(N) ~ N^α has α jumps (Δα > 0.1) at even dim-2 Artin transition conductors.

**Tables:** `lmfdb.mf_newforms`, `lmfdb.artin_reps`

**Computation:** Piecewise power law between Galois-type transitions, permutation test (10K shuffles).

**Falsification:** Δα < 0.05 or permutation p > 0.05.

**Connection:** Langlands program. **Confidence:** Medium (0.30).

---

---

## C-6. Knot Determinant Residues Mirror Class Numbers

**Hypothesis:** Entropy ratio H_knot(p)/H_nf(p) converges to constant C across primes p ≤ 19.

**Tables:** `prometheus_sci.topology.knots`, `lmfdb.nf_fields`

**Computation:** Mod-p histograms of determinant and class_number, Shannon entropy, test Var(R) < 0.01.

**Falsification:** Var(R) > 0.05.

**Connection:** Knot silence boundary. **Confidence:** Low (0.15).

---

---

## C-8. OEIS Growth Rates Cluster by L-function Conductor mod 12

**Hypothesis:** Number-theoretic OEIS sequences have growth exponent α correlated with leading_term by conductor mod 12.

**Tables:** `prometheus_sci.analysis.oeis`, `lmfdb.lfunc_lfunctions`

**Computation:** Fit a(n) ~ Cn^α, bin lfunc leading_term by conductor mod 12, test correlation.

**Falsification:** Permutation p > 0.05 or |r| < 0.1.

**Connection:** Langlands universality. **Confidence:** Low (0.10).

---

---

## C-9. Faltings Heights Show She-Leveque Anomalous Scaling

**Hypothesis:** Semistable EC: ⟨|faltings_height|^q⟩ ~ conductor^ζ(q) with |ζ(3) − 3ζ(1)| > 0.05.

**Tables:** `lmfdb.bsd_joined`

**Computation:** Filter semistable, bin by conductor decade, fit moments, test linearity of ζ(q)/q.

**Falsification:** |ζ(3) − 3ζ(1)| < 0.02 or R² < 0.8.

**Connection:** Turbulence intermittency in arithmetic. **Confidence:** Low-Medium (0.20).

---

---

## C-10. Group Order Factorization Predicts Regulator

**Hypothesis:** Ω(|Gal|) correlates with log(regulator) at partial ρ > 0.10 after degree control.

**Tables:** `prometheus_sci.algebra.groups`, `lmfdb.nf_fields`

**Computation:** Parse galois_label for order, compute Ω, partial Spearman controlling for degree.

**Falsification:** Partial ρ < 0.05 or sign reversal in > 2 strata.

**Connection:** Class number formula / regulator structure. **Confidence:** Medium (0.30).

---

# Summary Table

| Set | # | Domains Crossed | Confidence | Kill Criterion |
|-----|---|----------------|------------|----------------|
| A | 1 | Zeros × Rank | Medium | b ≤ 0 or R² < 0.2 |
| A | 2 | abc × RMT | Low | ρ < 0.05 |
| A | 3 | ADE × Langlands | Medium-low | No enrichment ±2% |
| A | 4 | Assembly × NF | Low | No monotone decrease |
| A | 5 | Genus-2 × EC isogeny | Low | r < 0.1 |
| A | 6 | Knots × MF (null test) | Very low | z < 2 |
| A | 7 | NF × root numbers | Medium-low | |p−0.5| < 0.01 |
| A | 8 | Regulator × zero height | Medium | R² < 0.15 |
| A | 9 | Artin frontier clustering | High | BIC clusters > 50 |
| A | 10 | She-Leveque × zeros | Medium-low | ζ(q) linear |
| B | 1 | ADE × GUE deviation | Medium | Δvariance < 2.5% |
| B | 2 | Assembly × MF traces | High | Assembly linear |
| B | 3 | Knots × NF class numbers | Low | Hit rate = random |
| B | 4 | Black hole × genus-2 Sha | Low | Coeff Δ > 0.05 |
| B | 5 | Autocatalytic × EC ranks | Medium | No discontinuity |
| B | 6 | Berry-Keating × Dirichlet | Medium | Skewness < 0.01 |
| B | 7 | She-Leveque × Artin dims | Low | Residuals > 10% |
| B | 8 | Faltings × Artin frontier | High | >10 below H_crit |
| B | 9 | NF disc × knot crossing | Medium | Exceeds bound |
| B | 10 | OEIS → L-functions | High | Zero matches |
| C | 1 | Sha × zero spacing | Low (0.15) | |ρ| < 0.05 |
| C | 2 | ADE × NF discriminants | Medium (0.35) | d < 0.1 |
| C | 3 | MF density × Artin transitions | Medium (0.30) | Δα < 0.05 |
| C | 4 | GUE convergence × degree | Med-High (0.50) | CI overlap > 50% |
| C | 5 | Torsion × z1 | Medium (0.40) | ρ(T,D) < 0.5 |
| C | 6 | Knot det × class numbers | Low (0.15) | Var(R) > 0.05 |
| C | 7 | Aut × genus-2 Sha | Medium (0.35) | γ ≤ 0 |
| C | 8 | OEIS × L-func conductor | Low (0.10) | p > 0.05 |
| C | 9 | Faltings × She-Leveque | Low-Med (0.20) | |ζ(3)−3ζ(1)| < 0.02 |
| C | 10 | Group Ω × regulator | Medium (0.30) | partial ρ < 0.05 |

**Total: 30 hypotheses across 3 sets. Each one killable. Null results are still measurements.**

---

*Generated for Prometheus by Aporia (Frontier Scout & Discovery Engine)*
*The frontier is not a wall. It's a frequency we haven't tuned to yet.*
*2026-04-17*

---

### Hypothesis 1: BSD Phase 2 via L-function Derivatives and Regulator Ratio

*   **Hypothesis Statement:** For elliptic curves with analytic rank $r \ge 1$, the ratio of the leading term of the L-function (derived from `z1`, `z2`, `z3`) to the `regulator` is statistically correlated with the order of the Tate-Shafarevich group (`sha`) divided by a factor related to the `torsion` subgroup order squared, suggesting a measurable manifestation of the BSD Phase 2 conjecture. Specifically, we hypothesize that for curves with `analytic_rank = 1`, the quantity `(-1)^rank * z1 / regulator` will be strongly correlated with `sha / (torsion^2)`.
*   **Mathematical Domains:** Number Theory (Elliptic Curves, L-functions, p-adic analysis implicit)
*   **Database Tables to Query:** `lmfdb.bsd_joined`
*   **Specific Computation to Run:**
    1.  Filter `lmfdb.bsd_joined` for `rank = 1` and `analytic_rank = 1`.
    2.  Calculate the ratio `RHS = sha / (torsion * torsion)` for each curve.
    3.  Calculate the "L-value term" `L_val = ABS(z1) / regulator`. (Note: `z1` is the first non-zero derivative coefficient, so for rank 1, it's `L'(1)`).
    4.  Perform a Pearson correlation analysis between `L_val` and `RHS`.
    5.  Additionally, compare the distributions of `log(L_val)` and `log(RHS)` for statistical similarity (e.g., using a Kolmogorov-Smirnov test).
*   **Falsification Criterion:** If the Pearson correlation coefficient between `L_val` and `RHS` is less than 0.7, or if the two distributions are statistically distinct (p-value < 0.01 for KS test), the hypothesis is falsified.
*   **Open Problem Connection:** Directly addresses **BSD Phase 2 (Sha formula)**.
*   **Confidence Estimate:** Medium. While BSD is hard, the perfect rank and parity agreement for Prometheus suggests robust data for exploring `sha` and `leading_term` relationships. The challenge is the precise form of the relation and the exact interpretation of `z1, z2, z3`.

---

---

### Hypothesis 2: Artin Representation Conductors and Number Field Galois Signatures

*   **Hypothesis Statement:** There is a statistically significant correlation between the `Conductor` and `Is_Even` property of Artin representations and the `degree`, `disc_abs`, and `galois_label` of number fields. Specifically, for number fields with abelian Galois groups (`galois_label` matching known abelian groups, e.g., 'C_n'), the distribution of `Conductor` values for 1-dimensional Artin representations whose `GaloisLabel` is a subgroup of the number field's Galois group will be distinct and predictable based on `disc_abs`.
*   **Mathematical Domains:** Number Theory (Artin Representations, Number Fields), Group Theory
*   **Database Tables to Query:** `lmfdb.artin_reps`, `lmfdb.nf_fields`
*   **Specific Computation to Run:**
    1.  Identify number fields in `lmfdb.nf_fields` with `galois_label` corresponding to abelian groups (e.g., 'C3', 'C4', 'C5', 'C2xC2', up to degree 5-6 for manageable labels).
    2.  For each such number field, identify 1-dimensional Artin representations in `lmfdb.artin_reps` whose `GaloisLabel` is isomorphic to a subgroup of the number field's Galois group. This requires a lookup table for Galois group isomorphisms.
    3.  For each pair, calculate the ratio `Conductor / disc_abs` (or `Conductor / sqrt(disc_abs)` depending on representation theory normalizations).
    4.  Compare the distribution of these ratios for different `galois_label` types of number fields. Specifically, test if the mean and variance of `log(Conductor / disc_abs)` are significantly different (e.g., t-test, F-test) between fields with abelian vs. non-abelian Galois groups.
*   **Falsification Criterion:** If the distribution of `log(Conductor / disc_abs)` for abelian `nf_fields` is not statistically distinct from a baseline distribution (e.g., for non-abelian `nf_fields` of similar `degree`), or if no clear pattern emerges linking `Conductor` to `disc_abs` within abelian groups (e.g., correlation coefficient < 0.3), the hypothesis is falsified.
*   **Open Problem Connection:** Connects to **Artin entireness**, as the conductor is a key invariant in the functional equation for Artin L-functions, and this explores its arithmetic origins.
*   **Confidence Estimate:** Low-Medium. Identifying 'subgroup' relationships via `GaloisLabel` can be complex, and the precise form of the correlation (e.g., `Conductor / disc_abs`) needs to be robust.

---

---

### Hypothesis 3: Knot Invariant Complexity and Modular Form Hecke Eigenvalue Variance

*   **Hypothesis Statement:** Despite the "silent islands" finding, there exists a subtle, statistically significant inverse correlation between the "complexity" of knots (quantified by the variance of coefficients of their `Jones_polynomial` and `crossing_number`) and the variance of `Hecke_eigenvalues` for specific families of modular forms, particularly those with `weight` 1/2 or 3/2 (often associated with mock modular forms). More complex knots are associated with "simpler" (lower variance) Hecke eigenvalue patterns for these specific modular forms.
*   **Mathematical Domains:** Topology (Knots), Number Theory (Modular Forms), Theoretical Physics (Implicit: Black Hole Entropy, Mock Modular Forms)
*   **Database Tables to Query:** `prometheus_sci.topology.knots`, `lmfdb.mf_newforms`
*   **Specific Computation to Run:**
    1.  For each knot in `prometheus_sci.topology.knots`, calculate its "complexity score": `K_comp = crossing_number * VAR(Jones_polynomial_coeffs)`. (Coefficients need to be parsed from the string.)
    2.  Filter `lmfdb.mf_newforms` for `weight` = 0.5 or 1.5 (or other weights related to mock modular forms, if identifiable).
    3.  For each filtered modular form, calculate the variance of its `Hecke_eigenvalues` (e.g., the first 20 eigenvalues): `MF_var = VAR(Hecke_eigenvalues[1:20])`.
    4.  Bin knots by `crossing_number`. Within each bin, compute the average `K_comp`.
    5.  Perform a cross-domain tensor decomposition (TT-Cross) relating the binned `K_comp` to `MF_var` for `mf_newforms` with specific `level` ranges and `weight` values, looking for strong anti-correlations (negative tensor components).
    6.  As a simpler check, correlate `K_comp` against `MF_var` for forms with small `level` (e.g., level < 100) and specific `weight`.
*   **Falsification Criterion:** If the strongest tensor components show a positive or near-zero correlation (magnitudes < 0.2) or if direct correlation analysis yields a Pearson coefficient greater than -0.3, the hypothesis is falsified.
*   **Open Problem Connection:** Directly attempts to address the **"Silent islands"** finding by finding a subtle link, and connects to **Black hole entropy** via mock modular forms.
*   **Confidence Estimate:** Low. The "silent islands"

---

Here are hypotheses 4 through 10 for the Prometheus mathematical research system, incorporating the specified format and leveraging key findings and frontiers:

---

**Hypothesis 4: Assembly Index of L-functions and Number Fields Correlates with Topological Complexity of Related Knots.**

*   **Statement:** There exists an "assembly index" for L-functions and number fields, analogous to that for chemical networks, that quantifies the minimum number of "irreducible components" required for their construction. This index will correlate positively with the topological complexity (e.g., crossing number, Jones polynomial degree) of knots from the `knots` table that are associated with these L-functions or number fields (e.g., via their complements or invariants).
*   **Database tables:** `lfunc_lfunctions`, `nf_fields`, `knots`, `oeis` (for combinatorial patterns), `groups` (for Galois group structure).
*   **Computation:**
    *   Define "irreducible components" for `lfunc_lfunctions` (e.g., primitive L-functions, prime factors of `lfunc_lfunctions.conductor`) and `nf_fields` (e.g., prime factors of `nf_fields.discriminant`, simple constituents of `nf_fields.galois_group_id` from `groups`).
    *   Develop an algorithm to compute an "assembly index" (A(O)) for objects O based on these components.
    *   For L-functions or number fields known to relate to knots, retrieve their corresponding `knots.crossing_number` and analyze the degree of `knots.jones_polynomial`.
    *   Calculate the correlation between A(O) and `knots.crossing_number` / `jones_polynomial_degree` for associated objects.
*   **Falsification criterion:** A statistically insignificant or negative correlation (e.g., Pearson R < 0.1) between the assembly index and topological complexity across a significant sample of linked objects. Alternatively, if no consistent, non-trivial definition of "irreducible component" can be established for mathematical objects that yields a meaningful assembly index.
*   **Open problem connection:** Assembly theory as new complexity measure, Knotted proteins, knots are silent islands. This bridges the abstract notion of assembly with the concrete complexity of topological objects.
*   **Confidence estimate:** Low-Medium. Defining "irreducible components" universally across abstract mathematical objects is a challenge, and the precise mathematical link between specific L-functions/number fields and knots is not always direct.

---

**Hypothesis 5: The GUE Deviation for L-functions is Reduced by Twisting with Specific Artin Characters.**

*   **Statement:** The observed 14% deviation from GUE statistics in the nearest-neighbor spacing distribution of zeros from `object_zeros` is significantly attenuated (e.g., reduced to <5%) for L-functions from `lfunc_lfunctions` when twisted by specific, non-trivial characters derived from `artin_reps`. This suggests these twists either filter out non-automorphic components or reveal a deeper, more fundamental symmetry of the underlying arithmetic object.
*   **Database tables:** `lfunc_lfunctions`, `object_zeros`, `artin_reps`.
*   **Computation:**
    *   For a large sample of L-functions from `lfunc_lfunctions` (especially those with `lfunc_lfunctions.degree` > 1), retrieve their `object_zeros`.
    *   Select a diverse set of characters from `artin_reps` (e.g., varying `artin_reps.degree`, `artin_reps.conductor`).
    *   Generate (or simulate zeros for) L-functions twisted by these characters.
    *   Compute the nearest-neighbor spacing distribution (NNSD) for both original and twisted L-functions.
    *   Quantify the GUE deviation for each (e.g., using a statistical fit to the GUE distribution, such as Kolmogorov-Smirnov test p-value or a specific distance metric).
    *   Compare the average deviation of the twisted L-functions against the original ones.
*   **Falsification criterion:** The average GUE deviation for twisted L-functions does not show a statistically significant reduction (e.g., remains above 10%) compared to the original L-functions across a broad range of twists. Or, if the deviation *increases* for a significant number of twists.
*   **Open problem connection:** RH operator hunt, GUE deviation 14%. This directly probes the nature of the GUE deviation and hints at mechanisms for finding the RH operator.
*   **Confidence estimate:** Medium. Twisting L-functions is a standard technique, and the GUE deviation is a well-established observation. The hypothesis proposes a testable mechanism for its reduction.

---

**Hypothesis 6: ADE Universality in Singular Fiber Types of Genus-2 Curves.**

*   **Statement:** The types of singular fibers arising from the degeneration of genus-2 curves in `g2c_curves`, particularly when analyzed over local fields or at bad primes, exhibit an underlying ADE classification. The frequency distribution of these ADE types will align with statistical predictions from theoretical physics models, such as those related to string theory compactifications or conformal field theories.
*   **Database tables:** `g2c_curves`, `nf_fields` (for base field information).
*   **Computation:**
    *   For a large sample of `g2c_curves`, obtain their equations and compute their reductions modulo various primes.
    *   Analyze the local geometry of these reduced curves to determine the types of singular fibers (e.g., using Kodaira's classification or other standard methods). This likely requires external computational algebraic geometry tools.
    *   Map the identified singular fiber types (e.g., `I_n`, `II`, `III`, `IV`, `I_n^*`, `II^*`, `III^*`, `IV^*`) to the corresponding ADE Dynkin diagrams (e.g., `I_n` to `A_{n-1}`, `IV` to `D_4`).
    *   Compute the frequency of each ADE type.
    *   Compare these observed frequencies with theoretical predictions from specific physical models (e.g., using statistical tests like chi-squared).
*   **Falsification criterion:** No consistent mapping from singular fiber types to ADE classification can be established, or the observed frequency distribution of ADE types from `g2c_curves` does not statistically match theoretical predictions from physics.
*   **Open problem connection:** ADE universality, Black hole entropy = modular forms (indirectly, as geometric degenerations are often related to such phenomena). This directly tests a frontier by linking algebraic geometry to fundamental symmetries in physics.
*   **Confidence estimate:** Low-Medium. Requires sophisticated algebraic geometry computation and a precise framework for mapping fiber types to ADE, which might itself be a research problem.

---

**Hypothesis 7: Modular Forms as Encoders of Black Hole Microstates.**

*   **Statement:** For physically consistent parameterizations of black holes (e.g., mass, charge, angular momentum in specific supergravity theories), there exists a corresponding modular form (or a finite set thereof) from `mf_newforms` whose Fourier coefficients (`mf_newforms.fourier_coefficients`), when interpreted combinatorially, accurately enumerate the microstates of the black hole, especially for extremal or near-extremal black holes.
*   **Database tables:** `mf_newforms`, `oeis` (for combinatorial sequences).
*   **Computation:**
    *   Identify specific black hole configurations for which microstate counts are theoretically known or computable (e.g., using string theory or M-theory results).
    *   Develop a mapping from black hole parameters (e.g., quantum numbers, charge vectors) to properties of modular forms (e.g., `mf_newforms.weight`, `mf_newforms.level`, `mf_newforms.character`).
    *   Query `mf_newforms` for candidate modular forms based on these properties.
    *   Extract and analyze `mf_newforms.fourier_coefficients` for these candidates.
    *   Attempt to match these coefficients to known microstate counting functions or sequences in `oeis` (e.g., partition functions, mock theta functions).
    *   Verify the accuracy of the enumeration against the theoretical microstate counts.
*   **Falsification criterion:** No consistent mapping can be found between physically relevant black hole parameters and modular form properties that yields Fourier coefficients accurately matching known microstate counts for a significant number of black hole examples. Or, if the combinatorial interpretation requires *ad hoc* adjustments for each case rather than a universal rule.
*   **Open problem connection:** Black hole entropy = modular forms. This directly tests a major frontier at the intersection of physics and number theory.
*   **Confidence estimate:** Medium. There are known examples and strong theoretical motivations for this connection, but a general, systematic correspondence across all black hole types is still an open challenge.

---

**Hypothesis 8: The GUE Deviation is a Signature of Non-Langlands L-functions.**

*   **Statement:** The observed 14% deviation from GUE statistics in `object_zeros` primarily originates from L-functions in `lfunc_lfunctions` that are *not* known to correspond to automorphic forms (i.e., those not yet proven to satisfy the Langlands correspondence). Conversely, L-functions explicitly known to be Langlands-satisfying (e.g., those linked to `mf_newforms` via `bsd_joined` or implied by the "Langlands GL(2) perfect" finding) will exhibit near-perfect GUE statistics (e.g., <2% deviation).
*   **Database tables:** `lfunc_lfunctions`, `object_zeros`, `mf_newforms`, `bsd_joined`.
*   **Computation:**
    *   Partition `lfunc_lfunctions` into two sets:
        1.  "Langlands-Confirmed": L-functions explicitly linked to `mf_newforms` (e.g., via `bsd_joined.lfunction_id` and `bsd_joined.newform_id`), or those contributing to the "Langlands GL(2) perfect (10,880)" finding.
        2.  "Langlands-Unconfirmed": All other L-functions in `lfunc_lfunctions`.
    *   For both sets, retrieve their associated `object_zeros`.
    *   Compute the nearest-neighbor spacing distribution (NNSD) for the zeros of each L-function in both groups.
    *   Quantify the GUE deviation for each L-function.
    *   Compare the average GUE deviation between the "Langlands-Confirmed" and "Langlands-Unconfirmed" groups using statistical significance tests.
*   **Falsification criterion:** The average GUE deviation for the "Langlands-Confirmed" L-functions is not significantly lower (e.g., remains above 5-10%) than for the "Langlands-Unconfirmed" L-functions. Or, if the difference in deviations is statistically insignificant.
*   **Open problem connection:** GUE deviation 14%, Langlands GL(2) perfect, RH operator hunt. This hypothesis provides a specific, testable explanation for the observed GUE deviation, linking it directly to the scope of the Langlands program.
*   **Confidence estimate:** Medium-High. This is a very direct and testable hypothesis given the existing key findings and database structure.

---

**Hypothesis 9: Class Number Domination Reflects Knotted Protein Stability.**

*   **Statement:** The "class-number-dominated" nature of the `nf_fields` backbone extends to a biological context: number fields mathematically derived from (or associated with) amino acid sequences or protein folding landscapes will exhibit unusually small `nf_fields.class_number` when those proteins adopt stable, functional, and particularly, knotted conformations. This small class number reflects a fundamental "arithmetic simplicity" or "stability" that correlates with the observed `knots.crossing_number` or other topological invariants of knotted proteins.
*   **Database tables:** `nf_fields`, `knots`, `oeis` (for potential sequence patterns).
*   **Computation:**
    *   Develop or utilize a theoretical framework to associate specific number fields (e.g., via their defining polynomials, discriminants, or Galois groups) with known protein sequences or structural motifs. This is a highly interdisciplinary and speculative step.
    *   For proteins known to form specific knots (e.g., 3_1, 4_1, etc.), identify the corresponding entries in `knots` (e.g., based on `knots.name`, `knots.crossing_number`).
    *   For the associated number fields, retrieve their `nf_fields.class_number`.
    *   Compare the distribution of `class_number` for protein-associated number fields (especially those linked to knotted proteins) against a baseline distribution of general number fields, looking for a statistically significant bias towards smaller values.
    *   Correlate small class numbers with simple knot types (low `knots.crossing_number`).
*   **Falsification criterion:** No consistent or statistically significant association can be established between protein structures (especially knotted ones) and specific number fields. Alternatively, if number fields associated with stable, knotted proteins do not exhibit a statistically significant bias towards smaller `nf_fields.class_number` compared to a control group.
*   **Open problem connection:** NF backbone is class-number-dominated, Knotted proteins, knots are silent islands. This is a highly cross-domain and speculative hypothesis attempting to link abstract number theory with biological complexity.
*   **Confidence estimate:** Low. The fundamental mapping between biological protein structures and specific number fields is not established and would require significant novel research.

---

**Hypothesis 10: Assembly Theory as a Universal Measure of Mathematical Object Complexity.**

*   **Statement:** A unified "assembly index" can be defined and computed for a diverse range of mathematical objects across the Prometheus database, including L-functions (`lfunc_lfunctions`), number fields (`nf_fields`), groups (`groups`), knots (`knots`), and modular forms (`mf_newforms`). This assembly index will universally correlate positively with other measures of computational complexity (e.g., `knots.crossing_number`, `lfunc_lfunctions.conductor`, `nf_fields.discriminant`, `groups.order`, `mf_newforms.level`) and inversely with their frequency of occurrence within their respective databases.
*   **Database tables:** `ec_curvedata`, `lfunc_lfunctions`, `mf_newforms`, `nf_fields`, `groups`, `knots`, `oeis`.
*   **Computation:**
    *   Develop a generalized "irreducible component" definition applicable across diverse mathematical structures (e.g., prime factors of conductors/discriminants/orders, simple groups, prime knot components).
    *   Implement a universal algorithm to compute an "assembly index" for objects from `lfunc_lfunctions`, `nf_fields`, `groups`, `knots`, `mf_newforms`.
    *   For each object, compute its assembly index and various measures of complexity (e.g., `lfunc_lfunctions.conductor`, `nf_fields.discriminant`, `groups.order`, `knots.crossing_number`, `mf_newforms.level`).
    *   Calculate the correlation between the assembly index and these complexity measures.
    *   Calculate the inverse correlation between the assembly index and the observed frequency of specific objects or object classes (e.g., counts of distinct `conductor` values, `discriminant` values, `group_id` occurrences) in the databases.
*   **Falsification criterion:** The proposed universal assembly index does not consistently exhibit a positive correlation with diverse computational complexity measures and a negative correlation with frequency of occurrence across multiple distinct mathematical object types. Or, if a meaningful and non-trivial definition of "irreducible component" cannot be generalized across these disparate domains.
*   **Open problem connection:** Assembly theory as new complexity measure, Jones polynomial BQP-complete. This is a grand unifying hypothesis for assembly theory, proposing it as a fundamental measure of complexity across mathematics.
*   **Confidence estimate:** Low. This is a highly ambitious hypothesis requiring a novel, foundational definition of "assembly" that transcends traditional mathematical boundaries, and its applicability across such diverse structures is unproven.

---
