# Project Prometheus — Full Council Review
## Cross-Domain Mathematical Discovery Pipeline: Complete Results + Battery Critique Request
### 2026-04-12 | 3 Rounds | 2 Machines | ~65 tests completed | Battery v6 (F1-F27)

---

## To the Council

We are submitting the complete results of 3 rounds of testing across 21 mathematical and scientific datasets. We request hostile review on four specific axes:

1. **Interpretation** — Are we reading the results correctly? Where are we over- or under-claiming?
2. **Battery design** — Is our 27-test instrument sound? Where are the blind spots, over-fitted thresholds, or domain-specific traps that will fail on new domains?
3. **Overfitting concerns** — Have we tuned the battery to the quirks of these specific datasets? Will it generalize?
4. **Recommendations** — Give us 5 specific tests that would smoke out any concerns you have, and tell us what tests to run after making adjustments.

---

## 1. The Instrument (Battery v6)

### Architecture

The battery has 27 tests across 5 tiers, plus 2 interpretation layers. It runs without LLM involvement — pure statistical computation.

**Tier A — Detection (F1-F14): Is the signal real?**
- F1: Permutation null (2,000-10,000 shuffles). Signal must exceed random at p < 0.01.
- F2: Subset stability (5 random 50% splits). Must hold in subsamples.
- F3: Effect size gate (Cohen's d > 0.2 or r > 0.1).
- F4: Confound sweep — test all available covariates as confounds.
- F5: Alternative normalization — log, rank, z-score. If sign flips, it's scale not structure.
- F6: Bonferroni correction for multiple testing within a single test.
- F7: Monotonic dose-response (is there a gradient, not just a jump?).
- F8: Direction consistency — same sign across all subgroups.
- F9: Simpler explanation — does a trivial baseline (mean, random) explain equally well?
- F10: Outlier sensitivity — remove top/bottom 5%, retest.
- F11: Cross-validation — train/test split.
- F12: Partial correlation — control for the most obvious third variable.
- F13: Growth rate filter — is the correlation just shared scale growth?
- F14: Phase-shift test — does the effect survive index permutation?

**Tier B — Robustness (F15-F18): Does it survive perturbation?**
- F15: Log-normal calibration — is M4/M² explained by log-normality?
- F16: Equivalence test (TOST) — is the value indistinguishable from a reference?
- F17: Confound sensitivity — quantify how much the effect shrinks when stratified by the strongest confound. Reports the sensitivity coefficient.
- F18: Subset stability (statistical) — CV of the statistic across bootstrap resamples.

**Tier C — Representation (F19-F23): Is the description well-posed?**
- F19: Generative replay — does a domain-matched null model (e.g., log-normal per group) reproduce the statistic? Reports z-score vs synthetic.
- F20: Representation invariance — does the statistic change under transforms (log, rank, sqrt, z-score)? Reports CV across transforms.
- F21: Trend robustness — does correlation survive detrending?
- F22: Representation alignment — which transform gives the best residuals (normality, homoscedasticity, CV stability)? Penalizes ordering-destroying transforms.
- F23: Latent confound discovery — k-means + hierarchical + GMM clustering. Gate 4 (effect reduction) must pass FIRST; then validates with stability, separation, and multi-method agreement. Prevents hallucinated confounds from stable-but-irrelevant clusters.

**Tier D — Magnitude (F24-F24b): How big is it?**
- F24: Variance decomposition — ANOVA eta² (between-group SS / total SS). Groups must have ≥ 5 members. Reports STRONG (≥ 0.14), MODERATE (≥ 0.06), SMALL (≥ 0.01), NEGLIGIBLE (< 0.01).
- F24b: Metric consistency — compares M4/M² contrast between groups against eta². Flags TAIL_DRIVEN when M4/M² ratio > 1.5 but eta² < 0.06. Reports tail contribution (% of total deviation from top 10% of values).

**Tier E — Context (F25-F27): Is it universal or conditional?**
- F25: Transportability — leave-one-group-out OOS R². Trains group means on all partitions except one, predicts held-out. Reports UNIVERSAL (OOS > 0.15), WEAKLY_TRANSFERABLE (> 0), CONTEXT_DEPENDENT (~ 0), CONDITIONAL (< 0).
- F26: Benjamini-Hochberg FDR — family-wise correction across hypothesis suites. Adjusts p-values for multiple testing.
- F27: Domain consequence checker — lookup table of 7 known mathematical consequences (e.g., "E_6 → root_number: CM by Q(√-3) forces it via parity conjecture"). Catches tautologies the statistical tests miss.

**Interpretation layers (not tests — applied post-battery):**
- Interaction analysis: variance decomposition into main effects + interaction terms
- Tautology detection: functional dependence + known theorem matching

### Calibration

- **Known truth battery:** 218/218 mathematical identities pass (100%). Covers arithmetic, algebraic NT, EC/MF, analytic NT, geometry, and formal proofs.
- **Rediscoveries:** 25 independent rediscoveries across testing (modularity theorem z=72, Deuring mass z=93, Euler relation z=33, paramodular conjecture 7/7, Kauffman-Murasugi-Thistlethwaite, etc.).
- **Calibration limitation (acknowledged):** Known truths are all deterministic (zero noise). We lack a "noisy physics ground truth" benchmark. eta² calibration on empirical data has not been independently validated.

### Key Design Decision: M4/M² Correction

Our largest methodological error was treating M4/M² (excess kurtosis ratio) as a magnitude measure. It is a contrast amplifier — it attends to distributional tails. A 3.7× M4/M² ratio between groups can correspond to eta² = 0.013 (1.3% of variance). F24 corrects this permanently. Every finding originally framed around M4/M² either died (C48 S_n formula), shrank (ST→conductor, C37 knot det), or needed correction (C43 prime gap slope). This single correction changed the project's finding landscape more than any other instrument improvement.

### Classification System

| Level | Type | Criteria |
|-------|------|----------|
| IDENTITY | Deterministic/known theorem | R² > 0.99 or known mathematical consequence |
| UNIVERSAL LAW | Transfers across contexts | eta² ≥ 0.14, F25 OOS R² > 0.15 |
| CONDITIONAL LAW | Strong within context | eta² ≥ 0.14, F25 OOS R² < 0 |
| CONSTRAINT | Real but small | eta² 0.01-0.14, survives F19 generative null |
| TENDENCY | Weak but consistent | eta² 0.01-0.06 |
| NEGLIGIBLE | Below noise floor | eta² < 0.01 |

---

## 2. Complete Results (3 Rounds, ~65 Tests, 2 Machines)

### CONDITIONAL LAWS (strong within context, interaction-dominated)

| # | Finding | eta² | Key evidence | Domain |
|---|---------|------|-------------|--------|
| 1 | SC_class → Tc | 0.570 | z>100, CV=3.2%, replicated on COD (0.41) | Superconductors |
| 2 | (SG × SC_class) → Tc | 0.457 global, 14.1% incr, 11% interaction | Balanced interaction survives; within-class 0.22-0.60; rank rho=-0.04 across classes | Superconductors |
| 3 | C21 NF class# by degree | 0.280 | F25 CONDITIONAL | Number fields |
| 4 | C09 Moonshine class → coeff scale | 0.601 | 26 classes, F27 NOT_TAUTOLOGY | Moonshine/OEIS |
| 5 | Crossing → determinant | 0.144 | 249/249 det=\|Alexander(-1)\|; partial r=0.39 after Alexander degree | Knots |

### LAWS (domain-internal, likely known or structural)

| # | Finding | eta² / R² | Evidence | Domain |
|---|---------|-----------|---------|--------|
| 6 | C86 Isogeny diameter scaling | R²=0.94 | diam=0.97·log(p)-1.22, 3240 primes, F27 NOT_TAUTOLOGY | Isogeny graphs |
| 7 | C05 Maass level → spectral param | 0.824 | 14,995 forms, 237 levels, F27 NOT_TAUTOLOGY | Maass forms |
| 8 | C08 EC traces non-recurrent | 0.139 | EC 0.01% vs OEIS 48% recurrence rate | EC / OEIS |
| 9 | C41 Unit circle profiles | 0.143 | CV=0.77%, exponential growth with crossing | Knots |
| 10 | C27 Dimension → f-vector sum | 0.914 | 980 polytopes, 7 dimensions | Polytopes |
| 11 | C88 SG → nsites | 0.531 | 3,921 crystals, 77 space groups | Crystals |
| 12 | C88 SG → volume | 0.394 | Same dataset | Crystals |
| 13 | C88 SG → density | 0.190 | Same dataset | Crystals |
| 14 | Fungrim module → n_symbols | 0.186 | 3,127 formulas, 59 modules | Fungrim |
| 15 | C05-deep Maass spacing: 100% Poisson | — | 174/174 levels fit Poisson > GUE | Maass forms |

### CONSTRAINTS (small but structurally real)

| # | Finding | eta² | Evidence | Domain |
|---|---------|------|---------|--------|
| 16 | ST → conductor | 0.013 | z=172 vs null, log-normal replay z=24.9, CV=0.061 | Genus-2 |
| 17 | Endomorphism → uniformity | 0.110 | F24 CONSISTENT, M4/M² monotonic 5.01→1.32 | Genus-2 |
| 18 | C5 Composition curvature | partial r=0.42 | Stable across Jaccard thresholds 0.2-0.8 (CV=0.23) | Superconductors |
| 19 | C68 Selmer-root number parity | 0.013 | 73.1% match (48,392/66,158) | Genus-2 |
| 20 | R5.iso-knot overlap | 0.047 | Primes that are knot dets have different isogeny node counts | Cross-domain |
| 21 | R6.iso-MF correlation | 0.309 | r=-0.556, isogeny nodes ~ MF count at level p | Cross-domain |

### SCALING LAWS

| # | Finding | Slope | Evidence |
|---|---------|-------|---------|
| 22 | C43 Prime gap M4/M² | 0.37/decade | R²=0.88, 10³ to 10⁸ |

### TENDENCIES (weak, consistent)

| # | Finding | eta² | Domain |
|---|---------|------|--------|
| 23 | N_elements → Tc | 0.018 after controls | Superconductors |
| 24 | C87 ST → torsion order | 0.084 | Genus-2 |
| 25 | C02 Mod-p starvation | 5.9% at p=3 | Modular forms |
| 26 | C04 HMF congruences | 1.21-1.30x enrichment | Hilbert modular forms |
| 27 | Fungrim type → n_symbols | 0.047 | Fungrim |
| 28 | R5.nfsg PG order / NF degree overlap | 5 shared values | Cross-domain |
| 29 | C53 Level → coeff M4/M² | 0.071 | Maass forms |
| 30 | Maass.coeff AC(1) | 0.019 | Maass forms |

### IDENTITIES and REDISCOVERIES

| # | Finding | Type |
|---|---------|------|
| 31 | C01 Paramodular conjecture (7/7 matched) | Rediscovery |
| 32 | EC~MF count (modularity theorem) | Rediscovery |
| 33 | Polytope Euler characteristic (980/980) | Rediscovery |
| 34 | det = \|Alexander(-1)\| (100% verified) | Mathematical identity |
| 35 | max Jones ~ det (R²=0.995) | Near-identity |
| 36 | Jones length ~ crossing (KMT theorem) | Known theorem |
| 37 | C41-deep Jones ≈ Alexander (cosine=0.919) | Structural identity |
| 38 | C8 Logistic map phase coherence | Dynamical identity |
| 39 | 23 genocide rediscoveries (Deuring, Euler, BSD, etc.) | Calibration |

### KILLED

| # | Finding | Kill mechanism |
|---|---------|---------------|
| 40 | E_6 root number = +1 | Tautology (CM forces it) |
| 41 | C48 S_n M4/M²=p(n)/n | False (ratio diverges to 0.068) |
| 42 | C11 3-prime fingerprint | Artifact (any hash gives same eta²) |
| 43 | S5 Fricke enrichment | Null (1.03x, p=0.18) |
| 44 | S6 Oscillation shadow | Already killed (z=0.84) |
| 45 | C36 Galois → class number | Degree confound (partial eta²=0.000) |
| 46 | C56 NF regulator by Galois | Degree confound (partial eta²=0.001) |
| 47 | C59 Crystal system → Tc | Absorbed by SG (partial eta²=0.000) |
| 48 | C60 Formation energy C3 | Second moment kills (M6≠C4) |
| 49 | Maass.fricke → coeff shape | Negligible (eta²=0.0003) |
| 50 | C78 Root number → conductor | Negligible (eta²=0.0006) |

---

## 3. Variance Decomposition of Tc (the flagship result)

```
Total Tc variance = 100%

  SC_class (chemical family):           57.0%
  SG (space group, after SC_class):     14.1%
  SC_class × SG (interaction):          11.0% (balanced)
  N_elements (after SC + SG):            1.8%
  Continuous properties (vol/den/FE):    0.6%
  Residual:                             15.5%

  Total model R²:                       0.845 (with interaction)
```

Replicated externally: eta²(SG→Tc) = 0.41 on 70 independent COD-sourced curves.

Within-class SG→Tc: Cuprate 0.60, Other 0.50, Oxide 0.46, Chevrel 0.39, Heavy fermion 0.22, Ferrite 0.08.

Rank correlation of SG rankings across classes: rho = -0.04 (independent).

---

## 4. The Meta-Result

**Most empirical "laws" in mathematical and scientific databases are conditional mappings, not universal ones.**

Evidence:
- Every categorical→continuous finding with a testable secondary grouping shows negative leave-one-group-out OOS R² (SG→Tc: -15.7, SC_class→Tc: -1.6, Galois→CN: -107, N_elem→Tc: -3.6)
- Within-context eta² values remain high (0.22-0.60)
- The same confound/nesting pattern appears independently in superconductors (SG/SC_class), number fields (Galois/degree), and knots (crossing/Alexander)
- Zero universal laws found across 21 datasets under this battery and these representations

---

## 5. Questions for the Council

### Q1: Interpretation

We classify findings as CONDITIONAL LAW when eta² ≥ 0.14 but F25 OOS R² < 0. We interpret negative OOS R² as "the conditional expectation changes across contexts" rather than "the signal is fake."

- Is this interpretation correct, or could negative OOS R² indicate something else (catastrophic overfitting, distribution shift artifact, small-group instability)?
- Are we overclaiming by calling these "laws" at all? Would "conditional association" or "context-specific regularity" be more appropriate?
- The 0.14 eta² threshold (Cohen's "large effect") was inherited from social science. Is this appropriate for mathematical/physical data where effects are often much stronger or weaker?

### Q2: Battery Design

- F24 uses one-way ANOVA eta². This assumes groups are categorical with no ordering. For ordinal predictors (crossing number, degree, n_elements), should we use a different test?
- F25 (transportability) trains group means on one context and predicts another. This is a very simple model — it can't capture interaction effects. Is there a better transportability test that accounts for interaction structure?
- F27 (consequence checker) is a lookup table of 7 known consequences. This is fragile — it misses anything not in the table. What would a more robust tautology detector look like?
- F23 (latent confound) uses k-means clustering, which hallucinates structure on isotropic noise. We gated it with effect-reduction-first (Gate 4), but is this sufficient?

### Q3: Overfitting and Domain Traps

- The battery was developed iteratively against superconductor and genus-2 data over 12 days. We froze it after Round 1, but the thresholds (eta² = 0.14, F25 OOS > 0.15, F24b M4/M² ratio > 1.5) were tuned on these datasets. Will they generalize to new domains (e.g., graph theory, combinatorics, algebraic geometry)?
- SG→Tc dominates the superconductor findings. Could the battery have a blind spot for non-categorical structure (continuous→continuous, network topology, sequential patterns)?
- The 218 known-truth calibration set is all deterministic identities. Does this create a false sense of precision for noisy empirical findings?

### Q4: Five Tests to Smoke Out Concerns

Please propose 5 specific, concrete tests (with datasets and expected outcomes) that would expose the battery's weaknesses. These should be designed to:
- Break the battery if it's over-tuned to the superconductor domain
- Reveal if the conditional law classification is an artifact of the testing procedure
- Test whether F24 eta² is sensitive to group structure artifacts (unequal group sizes, hierarchical nesting)
- Verify that F25 transportability actually detects universal laws when they exist
- Check whether F27 misses tautologies outside the lookup table

### Q5: What Tests Should We Run Next?

After incorporating your feedback and making any battery adjustments, what should our next round of testing focus on? We have ~80 untested hypotheses remaining, 60 frontier model proposals (mostly blocked on infrastructure), and 21 datasets spanning number theory, topology, algebra, physics, and combinatorics.

---

## 6. Appendix: Reproducibility

All scripts in `cartography/shared/scripts/`. Key entry points:

| Round | Machine | Scripts |
|-------|---------|---------|
| R1 | M2 | `reaudit_20_findings.py`, `law_independence.py`, `interaction_analysis.py`, `stanev_replication.py`, `stress_test_*.py`, `final_classification.py` |
| R1 | M1 | `m1_c35_*.py` through `m1_s6_*.py` (10 scripts) |
| R2 | M2 | `m2_r2_followups.py`, `m2_r2_genus2.py` |
| R2 | M1 | `m1_r2_c01_*.py` through `m1_r2_c43_ext.py` (8 scripts) |
| R3 | M2 | `m2_r3_sc_crystal.py`, `m2_r3_genus2_iso.py`, `m2_r3_maass.py`, `m2_r3_lattice_cross.py`, `m2_r3_unblocked.py` |

Battery: `battery_v2.py` (F15-F27), `falsification_battery.py` (F1-F14).

Datasets: 21 databases, ~1M+ objects. Superconductors (3,995), genus-2 (66,158), EC (31,073), MF (102K), Maass (14,995), knots (12,965), number fields (9,116), isogenies (3,240 primes), OEIS (394K), polytopes (980), lattices (21), space groups (230), Fungrim (3,130), and 8 more.

Total runtime: ~30 minutes across both machines for all 3 rounds.

---

## Council Submission Prompt

*Submit the above report to each council member (ChatGPT, Gemini, Claude, DeepSeek, Grok, Perplexity) with this prompt:*

---

**PROMPT FOR COUNCIL:**

You are reviewing a computational mathematics discovery pipeline that has run 65 tests across 21 datasets. The full report is attached.

Please provide:

1. **Interpretation critique** — Where are we over-claiming or under-claiming? Is our "conditional law" framework sound, or are we dressing up associations as laws?

2. **Battery critique** — Identify the 3 most serious blind spots in our 27-test battery (F1-F27). For each, explain what kind of finding it would miss or falsely validate, and suggest a fix.

3. **Overfitting assessment** — Do you see evidence that the battery is tuned to superconductor/genus-2 data? What would happen if we applied it unchanged to graph theory, combinatorics, or algebraic geometry data?

4. **5 smoke tests** — Propose 5 specific, concrete tests (state the hypothesis, dataset, expected outcome, and what it would prove) that would expose weaknesses in the battery or our interpretation. At least 2 should use data we already have. At least 1 should be a "universal law" that the battery should detect but might miss.

5. **Next round recommendations** — Given 80 remaining hypotheses and 21 datasets, what should we prioritize? What kind of finding should we be hunting for that we're currently missing?

Be adversarial. Attack every claim. Do not flatter. The goal is to find what we're doing wrong before publication.

---

*Report compiled: 2026-04-12*
*Machines: M1 (Skullport), M2 (SpectreX5)*
*Battery: v6 (F1-F27)*
*Total tests: ~65 across 3 rounds*
*Findings: 5 conditional laws, 10 domain-internal laws, 6 constraints, 1 scaling law, 8 tendencies, 9 identities/rediscoveries, 11 killed*
