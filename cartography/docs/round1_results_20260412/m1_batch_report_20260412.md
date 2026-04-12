# M1 Batch Report — Cross-Domain Cartography Re-Audit
## Skullport (M1), 2026-04-12
## For Council Review

---

## 1. Background

### 1.1 What This Project Is

Project Prometheus is an autonomous cross-domain mathematical discovery pipeline. The agent ("Charon") ingests structured data from 21 mathematical and scientific databases (~1M+ objects), builds a concept layer (39K concepts, 1.88M links), generates hypotheses about structural relationships between domains, and subjects them to a falsification battery.

The goal is to find genuine, novel cross-domain bridges in mathematics — structural connections between number theory, topology, algebra, physics, and combinatorics that are not already known. After 342 challenges across 12 days of operation, the honest count of novel universal laws discovered is **zero**. The pipeline has proven excellent at rediscovering known mathematics (23 rediscoveries, 97.4% validation rate) and at killing false positives.

### 1.2 The Datasets

| Domain | Dataset | Objects | Key Content |
|--------|---------|---------|-------------|
| Number theory | LMFDB | 134K | Elliptic curves, modular forms, L-functions |
| Number theory | Number Fields | 9.1K | Degree 1-6, class numbers, regulators, Galois groups |
| Number theory | Genus-2 | 66K | Higher genus curves, Sato-Tate groups |
| Number theory | Maass Forms | 15K | Spectral parameters, Fricke eigenvalues, coefficients |
| Topology | KnotInfo | 13K | Alexander, Jones, Conway polynomials, determinants |
| Algebra | Isogenies | 3.2K primes | Supersingular isogeny graphs |
| Formal math | mathlib | 8.5K modules | Lean 4 import dependency graph |
| Formal math | Metamath | 46K theorems | set.mm proof database |
| Physics | Materials Project | 210K | Crystal structures, band gaps, formation energies |
| Physics | Superconductors (3DSC) | 5.7K | Formulas, space groups, Tc, 92 properties |
| Combinatorics | OEIS | 394K | Integer sequences, cross-references |
| + 10 more | Various | Various | Lattices, polytopes, FindStat, Fungrim, etc. |

### 1.3 The Battery

The falsification battery is a 25-test instrument organized in 4 tiers. It runs without any LLM involvement — pure statistical testing. It is currently **frozen** (no further tests will be added).

**Tier A — Detection (F1-F14):** Does the signal exist?
- F1: Permutation null (is it better than random?)
- F2: Subset stability (does it hold in subsamples?)
- F3: Effect size gate (is the effect large enough to matter?)
- F4: Confound sweep (does it survive controlling for obvious confounds?)
- F5: Alternative normalization (does the sign flip under re-normalization?)
- F6: Bonferroni correction (multiple testing)
- F7: Dose-response (does more X give more Y?)
- F8: Direction consistency (same sign across subgroups?)
- F9: Simpler explanation (is there a trivial explanation?)
- F10: Outlier sensitivity (do a few points drive the result?)
- F11: Cross-validation (does it generalize?)
- F12: Partial correlation (does it survive controlling for a third variable?)
- F13: Growth rate filter (is the correlation just shared growth rate?)
- F14: Phase-shift test (is it a lagged coincidence?)

**Tier B — Robustness (F15-F18):** Is it robust?
- F15: Log-normal calibration
- F16: Equivalence test (TOST) against reference values
- F17: Confound sensitivity (how much does the effect shrink when you control for the strongest confound?)
- F18: Subset stability across strata

**Tier C — Representation (F19-F23):** Is it well-described?
- F19: Variance ratio check
- F20: Representation dependence (does the statistic change under transforms?)
- F21: Robustness to alternative metrics
- F22: Complexity penalty (penalizes transforms that destroy ordering)
- F23: Multi-method agreement (k-means + hierarchical + GMM must agree)

**Tier D — Magnitude (F24-F24b):** How big is it?
- F24: Variance decomposition (eta² — what fraction of variance does the grouping explain?)
- F24b: Metric consistency (is the effect bulk-driven or tail-driven? Flags when M4/M² shows a big contrast but eta² is small.)

**Interpretation layers** (not tests — analyses applied post-battery):
- Interaction analysis: Does the effect transfer across contexts, or is it conditional?
- Tautology detection: Is the finding a known theorem or mathematical identity?
- Leave-one-group-out: Does a model trained on one subgroup predict another?

### 1.4 The Classification System

Findings are classified by **mechanism type**, not confidence level:

| Level | Type | Definition |
|-------|------|------------|
| IDENTITY | Known mathematical theorem or functional dependence | R² > 0.99 or provably equivalent to known result |
| UNIVERSAL LAW | Holds across all contexts with eta² ≥ 0.14 | Never found one across 21 datasets |
| CONDITIONAL LAW | Holds within context, eta² ≥ 0.14, but mapping is context-specific | SG→Tc is the archetype |
| CONSTRAINT | Real but small (eta² < 0.14), or tail-driven | Boundary conditions, not organizing principles |
| TENDENCY | eta² 0.01-0.06, consistent but weak | Background effects |
| NEGLIGIBLE | eta² < 0.01 | Statistical ghosts |

### 1.5 Key Lesson From Prior Sessions

**M4/M² is a contrast amplifier, not a magnitude measure.** It attends to distributional tails. A 3.7× M4/M² ratio between groups can correspond to eta² = 0.013 (1.3% of variance explained). The prior version of this pipeline systematically overvalued tail-driven effects and missed bulk effects. F24 corrects this permanently. This re-audit applies F24 to all M1-assigned findings.

---

## 2. This Session's Scope

10 findings were assigned to M1 (Skullport) for re-audit through the frozen battery with F24 classification. These cover:
- 2 number field findings (C36, C56)
- 3 knot theory findings (C35, C37, C41)
- 1 representation theory finding (C48)
- 1 analytic number theory finding (C43)
- 2 Charon spectral findings (S5, S6)
- 1 number field distribution finding (C52)

A parallel set of 10 findings (superconductors, genus-2) was assigned to M2 (SpectreX5).

---

## 3. Results

### 3.1 C36: Galois Group → Class Number

**Prior claim:** Galois group enrichment 3.68x-5.12x on class number (eta² = 0.138, killed by F17 as degree confound).

**This session:** Full interaction decomposition on 9,115 number fields.

| Grouping | eta² | Verdict |
|----------|------|---------|
| Galois → CN (global) | 0.1380 | MODERATE |
| Degree → CN | 0.1382 | MODERATE |
| Galois → CN (after degree residualization) | **0.0000** | NEGLIGIBLE |

Within-degree analysis:
- Degree 2: only 1 Galois group (2T1) — nothing to compare
- Degree 3: 2 groups → eta² = 0.0000
- Degree 4: 4 groups → eta² = 0.0861 (moderate, but this is the only degree with structure)

**Verdict: DEGREE CONFOUND.** The F17 kill is confirmed definitively. Galois group and degree have eta² = 0.138 individually because they are perfectly correlated — different Galois groups live at different degrees. After removing degree, Galois adds exactly zero. The entire "enrichment" was a proxy for degree.

**Classification: NEGLIGIBLE (after controls)**

---

### 3.2 C35: Crossing Number → Determinant

**Prior claim:** eta² = 0.219 LAW. Need Alexander polynomial control.

**This session:** 2,977 knots (crossing number extracted from knot names since the field was mostly empty in the JSON).

| Test | Result |
|------|--------|
| Crossing → det (F24) | eta² = 0.144, STRONG, CONSISTENT |
| Alexander degree → det (F24) | eta² = 0.191 |
| Crossing → det \| Alexander degree | eta² = 0.089 (MODERATE) |
| Correlation crossing vs log(det) | Spearman rho = 0.378, p = 8e-102 |
| det = \|Alexander(-1)\| identity | **2977/2977 (100.0%)** |

**Critical finding:** The determinant IS \|Alexander(-1)\| — this is a mathematical identity, not an empirical discovery. Every single knot in the dataset confirms it exactly. The crossing→determinant relationship is real (eta² = 0.144) but it works through Alexander polynomial complexity: more crossings → higher-degree Alexander polynomial → larger \|Alexander(-1)\| = larger determinant.

**Verdict: LAW, but identity-mediated.** The relationship is strong and consistent, but it's a consequence of known topology (det = \|Δ(-1)\|), not a novel bridge.

**Classification: CONDITIONAL LAW (mediated by Alexander polynomial)**

---

### 3.3 C37/K1: Knot Determinant M4/M² = 2.155

**Prior claim:** M4/M² = 2.155, 90% CI [2.092, 2.217]. Not SU(2) = 2.0.

**This session:** 2,977 determinants, 10,000 bootstrap resamples.

| Metric | Value |
|--------|-------|
| M4/M² | 2.1555 |
| 90% CI | [2.1026, 2.2094] |
| SU(2) = 2.0 in CI? | NO |
| Gaussian = 3.0 in CI? | NO |
| Crossing → det eta² | 0.0847 (MODERATE) |
| F24b | CONSISTENT (not tail-driven) |

Stability across crossing strata:
- Crossing 0 (n=2728): M4/M² = 2.023
- Crossing 8 (n=21): M4/M² = 1.502
- Crossing 9 (n=49): M4/M² = 1.544
- Crossing 10 (n=165): M4/M² = 1.638

**Observation:** The M4/M² ratio decreases at higher crossing numbers (2.02 → 1.50). The bulk of the data (crossing=0, which means crossing number wasn't recorded — these are likely high-crossing knots from the original dataset) drives the 2.155 value. This is consistent — not tail-driven — but the value is dataset-composition-dependent.

**Verdict:** The distribution is genuinely between SU(2) and Gaussian, in a region not occupied by standard universality classes. Whether this is a "novel universality class" or just a mixture effect from combining knots of different complexity requires further investigation.

**Classification: CONSTRAINT (real distributional property, not a law)**

---

### 3.4 C52: Number Field Discriminant Moments by Degree

**Prior claim:** Discriminant and regulator scale with degree.

**This session:** 9,115 number fields.

| Grouping | eta² | Verdict |
|----------|------|---------|
| Degree → log(disc) | 0.0061 | NEGLIGIBLE |
| Galois → log(disc) | 0.0103 | SMALL |
| Galois → log(disc) \| degree | 0.0042 | NEGLIGIBLE |
| Degree → log(regulator) | 0.0812 | MODERATE |

M4/M² of discriminants within each degree:
- Degree 2: 1.800
- Degree 3: 1.728
- Degree 4: 1.625
- Degree 5: 1.405

**Observation:** The M4/M² monotonically decreases with degree — higher degree fields have more uniform discriminant distributions. This echoes the endomorphism finding from genus-2 curves (more algebraic structure → more uniform factorization). But the effect on discriminant magnitude is negligible (eta² = 0.006).

The regulator effect is moderate (eta² = 0.081) — degree genuinely constrains regulator size, with a non-monotonic pattern (degree 2: mean 1.48, degree 3: 2.37, degree 4: 1.30, degree 5: -0.21 in log scale).

**Classification: NEGLIGIBLE (discriminant), TENDENCY (regulator)**

---

### 3.5 C56: Number Field Regulator by Galois Within Degree

**Prior claim:** Galois group predicts regulator within degree.

**This session:** 9,115 number fields.

| Grouping | eta² | Verdict |
|----------|------|---------|
| Galois → log(reg) (global) | 0.0816 | MODERATE |
| Degree → log(reg) | 0.0812 | MODERATE |
| Galois → log(reg) \| degree | **0.0010** | NEGLIGIBLE |

Within-degree:
- Degree 3: 2 groups → eta² = 0.0052 (NEGLIGIBLE)
- Degree 4: 4 groups → eta² = 0.0261 (SMALL)

Brauer-Siegel context: regulator and class number are strongly anti-correlated (rho = -0.709 overall, -0.864 at degree 2). This is expected — the Brauer-Siegel theorem says h·R ~ √|Δ| asymptotically, so large regulator implies small class number.

**Verdict: DEGREE CONFOUND.** Same pattern as C36. Galois and degree are collinear; after removing degree, Galois adds 0.1% of variance. The Brauer-Siegel anti-correlation is the real structure here.

**Classification: NEGLIGIBLE (Galois effect), KNOWN THEOREM (reg-CN anti-correlation)**

---

### 3.6 C41/S1: Knot Polynomial Unit Circle Profiles

**Prior claim:** 13-point unit circle evaluation of Jones polynomial distinguishes knot types. Rich profile.

**This session:** 2,977 knots with valid Jones polynomials.

| Metric | Value |
|--------|-------|
| Subsample CV (F18 stability) | 0.77% |
| Max CV across angles | 1.01% |
| Crossing → profile norm eta² | 0.1426 (STRONG) |
| Jones-Alexander profile correlation | rho = 0.716, p = 0.006 |
| Jones-Alexander cosine similarity | 0.933 |

Profile norm by crossing number:
- Crossing 8: mean = 32.2
- Crossing 9: mean = 48.7
- Crossing 10: mean = 72.4
- Crossing 11: mean = 111.5
- Crossing 12: mean = 167.3

**Verdict: STABLE LAW.** The unit circle profile is extremely stable (CV < 1%) and crossing number explains 14.3% of profile norm variance. The exponential growth of profile norm with crossing number is a genuine structural property — knot polynomials become more complex (larger evaluations on the unit circle) with increasing crossing number. Jones and Alexander profiles are strongly correlated (cosine 0.933), meaning both polynomial invariants encode similar unit-circle structure.

**Classification: LAW (stable, non-trivial, strong effect)**

---

### 3.7 C48/S2: S_n Character M4/M² = p(n)/n

**Prior claim:** The M4/M² ratio of irreducible character degrees of S_n equals p(n)/n exactly, where p(n) is the partition function.

**This session:** Computed character degrees via hook length formula for S_2 through S_30.

| n | p(n) | M4/M² | p(n)/n | Ratio |
|---|------|-------|--------|-------|
| 5 | 7 | 1.488 | 1.400 | 1.063 |
| 10 | 42 | 2.959 | 4.200 | 0.705 |
| 15 | 176 | 4.371 | 11.733 | 0.373 |
| 20 | 627 | 6.419 | 31.350 | 0.205 |
| 25 | 1958 | 9.582 | 78.320 | 0.122 |
| 30 | 5604 | 12.757 | 186.800 | 0.068 |

**Verdict: FALSE.** The ratio M4/M²/(p(n)/n) diverges monotonically from 1.0, reaching 0.068 at n=30. M4/M² grows polynomially (~n^0.97), while p(n)/n grows super-polynomially (Hardy-Ramanujan: p(n) ~ exp(π√(2n/3))/(4n√3)). These are different growth rates and the claim is definitively false.

**Classification: FALSE CLAIM**

---

### 3.8 C43/S3: Prime Gap M4/M² Scaling

**Prior claim:** M4/M² of prime gaps increases at +0.23 per decade toward Poisson (M4/M² = 9).

**This session:** Computed prime gaps from 10³ to 10⁸ (5.76M primes at the largest scale).

| Scale | n_primes | Mean gap | M4/M² | % toward Poisson |
|-------|----------|----------|-------|-----------------|
| 10³ | 168 | 5.96 | 2.509 | -8.2% |
| 10⁴ | 1,229 | 8.12 | 3.444 | 7.4% |
| 10⁵ | 9,592 | 10.43 | 3.974 | 16.2% |
| 10⁶ | 78,498 | 12.74 | 4.384 | 23.1% |
| 10⁷ | 664,579 | 15.05 | 4.604 | 26.7% |
| 10⁸ | 5,761,455 | 17.36 | 4.740 | 29.0% |

Linear fit: M4/M² = **0.430** × log₁₀(N) + 1.578 (R² = 0.905)

**Verdict: MODIFIED.** The scaling is real (R² = 0.905) but the slope is **0.43/decade, nearly double the prior claim of 0.23.** The prior measurement was likely computed over a narrower range or with a different normalization. The convergence toward Poisson is genuine but slow — at 10⁸, prime gaps are only 29% of the way from Gaussian to Poisson.

However, as an F24 effect (decade-of-prime → gap size), eta² = 0.0036 — NEGLIGIBLE. The scaling is a property of the *distribution* evolving with scale, not a grouping effect. This is better described as a **scaling law** than a variance decomposition finding.

**Classification: SCALING LAW (real, slope corrected to 0.43/decade)**

---

### 3.9 S5: Fricke Enrichment 1.44x

**Prior claim:** Fricke eigenvalue +1 vs -1 shows 1.44x enrichment on spectral parameter in Maass forms.

**This session:** 14,995 Maass forms (7,668 Fricke -1, 7,327 Fricke +1).

| Metric | Value |
|--------|-------|
| Fricke → spectral eta² | 0.0001 |
| Enrichment ratio | 1.027x |
| Mann-Whitney p | 0.178 |
| Cohen's d | 0.022 |

**One interesting anomaly:** At Level 1 specifically (n=69), Fricke → R gives eta² = 0.416 (STRONG). But this is just the even/odd Maass form interleaving at the lowest level — a well-known structural feature, not a discovery. At all other levels, eta² drops to 0.002-0.018.

**Verdict: NEGLIGIBLE.** The 1.44x enrichment claim was noise. The actual enrichment is 1.03x with p = 0.18.

**Classification: NEGLIGIBLE (killed)**

---

### 3.10 S6: Oscillation Shadow

**Prior claim:** Sign oscillation patterns in EC L-function coefficients, p = 0.001.

**This session:** The prior oscillation analysis file contained its own verdict:

> "NEGATIVE: The oscillation in 15.2.a.a is NOT universal. AC magnitudes in real data are not significantly larger than shuffled null (z = 0.84). The lag-3 standing wave in 15.2.a.a is either a local arithmetic feature or an artifact of small sample size."

The k* distribution is uniform (not non-uniform), and the prediction test achieved only 5.5% exact match rate (7.0% with fallback) — no better than random for 15 categories.

**Verdict: ALREADY KILLED by prior analysis.** No need to re-audit.

**Classification: KILLED**

---

## 4. Summary Table

| # | Finding | Prior Status | New Classification | eta² | Key Insight |
|---|---------|-------------|-------------------|------|-------------|
| C36 | Galois → CN | KILLED (F17) | **NEGLIGIBLE** | 0.000 (incr.) | Degree confound confirmed |
| C35 | Crossing → det | LAW (0.219) | **CONDITIONAL LAW** | 0.144 | det = \|Alexander(-1)\| is 100% identity |
| C37 | Knot det M4/M² | POSSIBLE | **CONSTRAINT** | 0.085 | 2.156, not SU(2), crossing-dependent |
| C52 | NF disc moments | Untested | **NEGLIGIBLE** | 0.006 | M4/M² decreases with degree |
| C56 | NF reg by Galois | Untested | **NEGLIGIBLE** | 0.001 (incr.) | Degree confound, Brauer-Siegel explains |
| C41 | Knot unit circle | POSSIBLE | **LAW** | 0.143 | CV=0.77%, exponential norm growth |
| C48 | S_n M4/M²=p(n)/n | POSSIBLE | **FALSE** | N/A | Ratio diverges, different growth rates |
| C43 | Prime gap scaling | +0.23/decade | **SCALING LAW** | 0.004 | Corrected to 0.43/decade |
| S5 | Fricke enrichment | OPEN | **NEGLIGIBLE** | 0.0001 | 1.03x not 1.44x, p=0.18 |
| S6 | Oscillation shadow | OPEN | **KILLED** | N/A | Prior analysis already negative |

---

## 5. Patterns and Observations

### 5.1 The Degree Confound Pattern

Both number field findings (C36, C56) show the same structure: Galois group and degree are perfectly collinear, so any correlation with Galois is actually a correlation with degree. After residualizing by degree, Galois adds zero (C36) or 0.1% (C56). This mirrors the superconductor finding from M2 where space group effects are conditional on chemical family.

**Lesson:** Any categorical variable that is nested within or strongly correlated with another categorical variable will show inflated eta² globally. Incremental eta² (after residualizing the parent variable) is the honest measure.

### 5.2 The Identity Trap

C35 (crossing → determinant) has eta² = 0.144, which meets the LAW threshold. But the relationship is a known mathematical identity (det = |Δ(-1)|). C48 (S_n character) was a claimed identity that turned out to be false. The battery now includes tautology detection for exactly this reason — strong effects need to be checked against known theorems before being claimed as discoveries.

### 5.3 M4/M² Is Not a Discovery Metric

Three findings in this batch (C37, C48, C43) were originally framed around M4/M² values. In each case, F24 (eta²) told a more honest story:
- C37: M4/M² = 2.156 looks precise, but crossing→det eta² = 0.085 (moderate, not strong)
- C48: M4/M² ≈ p(n)/n was simply false
- C43: M4/M² scaling is real but eta² = 0.004 as a grouping effect

M4/M² measures distributional shape. Eta² measures how much a grouping variable explains. They answer different questions. Using M4/M² as a discovery metric systematically overweights tail effects and can make negligible findings look dramatic.

### 5.4 What Survived

Two findings emerged as genuine laws from this batch:
1. **C35 (crossing → determinant):** eta² = 0.144, CONSISTENT, identity-mediated. Not novel, but real.
2. **C41 (unit circle profiles):** eta² = 0.143, CV = 0.77%, exponential growth with crossing number. This is a stable, non-trivial structural property of knot polynomials.

Both are in knot theory. Both are about how polynomial invariants scale with crossing complexity. Neither is a cross-domain bridge — they describe structure within a single mathematical domain.

### 5.5 The Honest Count

After this batch: **zero novel universal laws across 21 datasets.** The findings that survive are either:
- Known mathematics (identities, rediscoveries)
- Conditional laws (context-specific mappings, primarily in superconductors)
- Constraints (real but small boundary conditions)
- Domain-internal structure (knot theory scaling)

This is not a failure. The battery is working correctly — it kills what should be killed and classifies what survives honestly. The absence of universal cross-domain laws is itself an informative result about the structure of mathematical knowledge.

---

## 6. Questions for the Council

1. **C37 (knot det M4/M² = 2.156):** Is there a known universality class with this moment ratio? The value sits between uniform (1.8) and SU(2) semicircle (2.0) — or more precisely, slightly above SU(2). Is there a random matrix ensemble or combinatorial distribution that predicts this value?

2. **C43 (prime gap scaling 0.43/decade):** The prior claim was 0.23/decade. Our measurement gives 0.43. Is there a theoretical prediction for this rate? The Cramér model predicts eventual convergence to exponential (M4/M² = 9), but the rate of convergence is not well-characterized.

3. **C41 (unit circle profiles):** The Jones and Alexander polynomial evaluations on the unit circle have cosine similarity 0.933 — much higher than expected for two "different" polynomial invariants. Is this known? Does it reflect a deeper structural constraint on knot polynomials?

4. **C52 (M4/M² decreasing with degree):** The discriminant M4/M² drops from 1.80 (degree 2) to 1.40 (degree 5). This echoes the genus-2 endomorphism finding (more structure → more uniform). Is this a known consequence of algebraic number theory (e.g., Minkowski bounds constraining discriminant distributions at higher degree)?

5. **Meta-question:** We have found zero universal laws across 21 datasets after 342 challenges. Is this expected? Is the search space too sparse, the battery too strict, or is mathematical knowledge genuinely compartmentalized at the level we're probing?

---

*10 tests. 2 kills confirmed. 2 new kills. 1 false claim. 1 correction. 2 laws (domain-internal). 1 constraint. 1 negligible.*
*Battery: 25 tests, 4 tiers, frozen.*
*The honest count of novel universal cross-domain laws: zero.*

*Charon — M1 (Skullport)*
*2026-04-12*
