# Aporia Frontier Hypotheses — 30 Cross-Domain Challenges
## Date: 2026-04-17
## Source: Gemini 2.5 Pro (browser) + Claude, prompted with Prometheus data inventory + frontier research
## Context: Aporia's Five Barriers framework, Fingerprint Program, and 20-frontier map

---

# SET A: 10 Spectral-Arithmetic Bridge Hypotheses

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

## B-1. ADE Singularity Signatures in Finite-N GUE Deviations

**Hypothesis:** The 14% GUE variance reduction depends on ADE classification of curve singularities. Multiplicative reduction (A_n) matches Wigner; additive (D_n, E_n) carries the deviation.

**Tables:** `lmfdb.bsd_joined`, `prometheus_fire.zeros.object_zeros`

**Computation:** Classify by bad_primes into multiplicative vs additive, compute spacing variance independently.

**Falsification:** Variance difference < 2.5%, or A_n deviation > 5%.

**Connection:** ADE universality / RH operator approaches. **Confidence:** Medium.

---

## B-2. Assembly Index Bounding of Modular Form Traces

**Hypothesis:** Hecke eigenvalue sequences for weight-2 MF have Assembly Index that undergoes phase transition to bounded complexity at level > 1000.

**Tables:** `lmfdb.mf_newforms`

**Computation:** Decode trace_hash, compute Assembly Index, compare to Shannon entropy.

**Falsification:** Assembly Index linear with N (r > 0.95).

**Connection:** Assembly theory / black hole microstates. **Confidence:** High.

---

## B-3. Knot Silence Breaking via Galois Correspondence

**Hypothesis:** Knot determinant perfectly divides class_number of degree-2 NF whose disc_abs depends on crossing_number.

**Tables:** `prometheus_sci.topology.knots`, `lmfdb.nf_fields`

**Computation:** Join on disc_abs ≤ f(crossing_number), test class_number mod determinant == 0.

**Falsification:** Hit rate indistinguishable from random (p > 0.05).

**Connection:** BQP-completeness of topological invariants. **Confidence:** Low.

---

## B-4. Black Hole Entropy and Genus-2 Automorphism Asymptotics

**Hypothesis:** Analytic SHA growth in genus-2 curves, stratified by aut_grp, matches Rademacher sub-leading terms for black hole microstates.

**Tables:** `lmfdb.g2c_curves`

**Computation:** Growth of analytic_sha vs log(abs_disc) per aut_grp_label group.

**Falsification:** Growth coefficients differ from Rademacher by > 0.05.

**Connection:** Black hole entropy via modular forms. **Confidence:** Low.

---

## B-5. Autocatalytic Phase Transitions in EC Ranks

**Hypothesis:** EC ranks undergo discontinuous phase transition at critical conductor/szpiro_ratio threshold.

**Tables:** `lmfdb.ec_curvedata`

**Computation:** Plot rank≥2 density vs C = conductor/szpiro_ratio, test for discontinuity.

**Falsification:** No spikes > 4σ above moving average.

**Connection:** Autocatalytic sets / abc conjecture. **Confidence:** Medium.

---

## B-6. Berry-Keating Dynamics in Dirichlet Zeros

**Hypothesis:** Skewness and kurtosis of Dirichlet zero spacings scale as O(1/log N) per Yakaboylu 2024.

**Tables:** `prometheus_fire.zeros.dirichlet_zeros`, `lmfdb.lfunc_lfunctions`

**Computation:** Compute moments at conductor > 10^5, regress against 1/log(conductor).

**Falsification:** Skewness < 0.01 or regression R² < 0.5.

**Connection:** RH operator approaches. **Confidence:** Medium.

---

## B-7. She-Leveque in Artin Representation Dimensions

**Hypothesis:** Even Artin rep dimension gaps obey She-Leveque hierarchy formula.

**Tables:** `lmfdb.artin_reps`

**Computation:** Max conductor per Dim, fit ζ_p to p/3 + C(1 − β^(p/3)).

**Falsification:** Residuals > 10% or β unstable.

**Connection:** Turbulence anomalous exponents. **Confidence:** Low.

---

## B-8. Faltings Height Separates Artin Frontier

**Hypothesis:** Unproven Artin reps map to motives with faltings_height above a threshold H_crit.

**Tables:** `lmfdb.artin_reps`, `lmfdb.bsd_joined`

**Computation:** Join via Conductor, compare faltings_height distributions.

**Falsification:** > 10 frontier motives in lowest 5th percentile.

**Connection:** Artin frontier. **Confidence:** High.

---

## B-9. NF Discriminant Bounds Knot Crossing Number

**Hypothesis:** disc_abs/degree limits crossing number of knots with matching Alexander polynomial coefficients.

**Tables:** `lmfdb.nf_fields`, `prometheus_sci.topology.knots`

**Computation:** Match coeffs to Alexander polys, compute max crossing per disc/degree bin.

**Falsification:** Any match exceeding 10 × ln(disc_abs/degree).

**Connection:** Knotted proteins / knot silence. **Confidence:** Medium.

---

## B-10. OEIS Core Sequences Are L-function Coefficients

**Hypothesis:** OEIS sequences with polynomial growth and low Assembly Index match L-function leading_terms.

**Tables:** `prometheus_sci.analysis.oeis`, `lmfdb.lfunc_lfunctions`

**Computation:** Generate pseudo-L-series from OEIS, cross-match to 24M L-function leading_terms.

**Falsification:** Zero matches at < 10^-6 precision.

**Connection:** Assembly theory / ADE universality. **Confidence:** High.

---

# SET C: 10 Precision Frontier Hypotheses

---

## C-1. Selmer Shadow in Zero Spacing

**Hypothesis:** For rank ≥ 2 EC, normalized gap (z2−z1) anti-correlates with log(Sha), Spearman ρ < −0.15.

**Tables:** `lmfdb.bsd_joined`

**Computation:** Filter rank≥2, sha>1, compute (z2−z1)×log(conductor) vs log(sha), stratify by conductor.

**Falsification:** |ρ| < 0.05 or sign reversal across strata.

**Connection:** BSD conjecture. **Confidence:** Low (0.15).

---

## C-2. ADE Gatekeeping in Number Field Discriminants

**Hypothesis:** NF with Dynkin-type Galois groups have lower disc_abs/degree! ratios (Cohen's d > 0.3).

**Tables:** `lmfdb.nf_fields`

**Computation:** Map galois_label to Dynkin/non-Dynkin, Mann-Whitney test on log(disc_abs/degree!).

**Falsification:** d < 0.1 or p > 0.01 after Bonferroni.

**Connection:** ADE universality. **Confidence:** Medium (0.35).

---

## C-3. Weight-1 MF Density Tracks Artin Dimension Transitions

**Hypothesis:** Cumulative weight-1 MF count C(N) ~ N^α has α jumps (Δα > 0.1) at even dim-2 Artin transition conductors.

**Tables:** `lmfdb.mf_newforms`, `lmfdb.artin_reps`

**Computation:** Piecewise power law between Galois-type transitions, permutation test (10K shuffles).

**Falsification:** Δα < 0.05 or permutation p > 0.05.

**Connection:** Langlands program. **Confidence:** Medium (0.30).

---

## C-4. GUE Convergence Rate Depends on L-function Degree

**Hypothesis:** KS distance from GUE decays as conductor^(−β) with β(degree=1) ≠ β(degree=2) by ≥ 20%.

**Tables:** `prometheus_fire.zeros.object_zeros`, `prometheus_fire.zeros.dirichlet_zeros`, `lmfdb.lfunc_lfunctions`

**Computation:** Per-degree conductor-binned KS distance, fit power law, bootstrap CIs.

**Falsification:** CI overlap > 50% or R² < 0.5.

**Connection:** GUE universality / RH. **Confidence:** Medium-High (0.50).

---

## C-5. Torsion Predicts z1 Distribution

**Hypothesis:** KS distance between z1 distributions for torsion=T vs torsion=1 grows monotonically with T.

**Tables:** `lmfdb.bsd_joined`

**Computation:** Propensity match by conductor, compute D(T) per torsion group.

**Falsification:** ρ(T, D) < 0.5 or non-monotone with > 2 violations.

**Connection:** BSD bridge transmits more than rank. **Confidence:** Medium (0.40).

---

## C-6. Knot Determinant Residues Mirror Class Numbers

**Hypothesis:** Entropy ratio H_knot(p)/H_nf(p) converges to constant C across primes p ≤ 19.

**Tables:** `prometheus_sci.topology.knots`, `lmfdb.nf_fields`

**Computation:** Mod-p histograms of determinant and class_number, Shannon entropy, test Var(R) < 0.01.

**Falsification:** Var(R) > 0.05.

**Connection:** Knot silence boundary. **Confidence:** Low (0.15).

---

## C-7. Genus-2 Aut Group Predicts Sha Magnitude

**Hypothesis:** Geometric mean of analytic_sha scales as |Aut|^γ with γ > 0.

**Tables:** `lmfdb.g2c_curves`

**Computation:** Parse aut_grp_label for |Aut|, group, fit log-log.

**Falsification:** γ ≤ 0 or CI includes 0.

**Connection:** BSD for genus-2. **Confidence:** Medium (0.35).

---

## C-8. OEIS Growth Rates Cluster by L-function Conductor mod 12

**Hypothesis:** Number-theoretic OEIS sequences have growth exponent α correlated with leading_term by conductor mod 12.

**Tables:** `prometheus_sci.analysis.oeis`, `lmfdb.lfunc_lfunctions`

**Computation:** Fit a(n) ~ Cn^α, bin lfunc leading_term by conductor mod 12, test correlation.

**Falsification:** Permutation p > 0.05 or |r| < 0.1.

**Connection:** Langlands universality. **Confidence:** Low (0.10).

---

## C-9. Faltings Heights Show She-Leveque Anomalous Scaling

**Hypothesis:** Semistable EC: ⟨|faltings_height|^q⟩ ~ conductor^ζ(q) with |ζ(3) − 3ζ(1)| > 0.05.

**Tables:** `lmfdb.bsd_joined`

**Computation:** Filter semistable, bin by conductor decade, fit moments, test linearity of ζ(q)/q.

**Falsification:** |ζ(3) − 3ζ(1)| < 0.02 or R² < 0.8.

**Connection:** Turbulence intermittency in arithmetic. **Confidence:** Low-Medium (0.20).

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
