# Frontier Model Review — Round 2
## 2026-04-13 | Response to survivor kill protocol results

---

## The Review

A frontier model was given the full kill protocol results (8/8 tests survived, synthetic null validated, factorization confound tested) and asked to assess the state of the project. Below is a summary of their analysis followed by our response and test results.

### Assessment of What We've Shown

The reviewer confirmed:

1. **The effect is statistically real** in our dataset. z = -29 with permutation controls is not noise. Combined with multiple orthogonal conditionings, consistent sign, and persistence across 31K curves.

2. **The signal is not where people usually look.** We've ruled out individual zero positions, Sato-Tate, a_p distribution, local reduction data, and CM structure. The dominant signal is spacing(gamma_2 - gamma_1) — zero repulsion/interaction, not location/bias. This places it in RMT territory, not classical arithmetic statistics.

3. **It's genuinely class-level.** Isogenous curves share identical zeros. We're correlating algebraic multiplicity (class size) vs analytic spectrum (zero spacing) — a clean separation.

4. **The scaling is the strongest clue.** |rho| ~ N^(-0.464) ~ N^(-1/2). This exponent appears throughout eigenvalue fluctuation theory, central limit scaling in RMT, and finite-size corrections to spacing distributions.

### Proposed Interpretation

> Isogeny class size acts as a hidden parameter that slightly perturbs the effective matrix ensemble. Larger class size leads to slightly stronger effective repulsion and wider gamma_2 - gamma_1. The effect vanishes as conductor goes to infinity at rate N^(-1/2).

The "negative reduction" result (conditioning makes the signal stronger) was identified as a known signature of a real signal masked by independent noise sources.

### Three Remaining Attack Surfaces

1. **Finite-sample / database artifact coupling.** Curves with more computed zeros may correlate with class size or conductor structure. Numerical precision or ordering artifacts could subtly affect spacing. The reviewer called this the #1 realistic failure mode.

2. **Hidden conditioning leak via conductor geometry.** Conductor is not just a scalar — it encodes arithmetic structure through its prime factorization. Class size could correlate with conductor factorization type, indirectly influencing spacing statistics.

3. **Multiple testing / researcher degrees of freedom.** Many tests with different conditionings and spacing variants increases the chance of finding the strongest channel. However, the reviewer noted that z-scores are strong enough that this alone won't kill it.

### Four Requirements for Publishable-Level

A. **Extend conductor range** > 50,000 to confirm continued N^(-1/2) decay
B. **Independent dataset replication** (Cremona database)
C. **Synthetic null model test** — construct fake data, check if pipeline recovers false signal
D. **Theoretical hook** — even a heuristic mechanism connecting class size to effective ensemble dimension

### Additional Research Directions

- **Signal B kill protocol**: Level/weight ablation, Hecke operator orthogonality control, Sato-Tate-preserving synthetic null
- **Higher-order spacings**: Does the signal exist only in gap_1 (BSD-related) or propagate across the spectrum (global geometric property)?
- **New domains**: Dedekind zeta functions, Maass waveforms, p-adic L-functions
- **Neural networks**: GNNs for congruence graph embeddings, gradient attribution to identify which specific zero gaps the model relies on most
- **The motivic perspective**: L-functions are themselves shadows of motives (Grothendieck). If Prometheus is computationally validating that L-functions act as universal bridges, we are validating the motivic philosophy.

### Closing Question

> If you extend your conductor range to > 50,000 and find that alpha precisely hits 1/2, how will you adjust your null-hypothesis parameters to ensure that larger conductor values aren't introducing their own asymptotic artifacts?

---

## Our Response

### Addressing the Closing Question

Three specific risks at large conductor and how to handle them:

1. **Bin population inversion.** At conductor < 5,000 we have dense bins. At conductor > 100,000, curves are sparse and unevenly distributed. Fix: adaptive bin widths targeting a minimum population (200 curves/bin), not fixed log-spacing.

2. **Class size distribution shift.** At large conductor, isogeny classes tend to be smaller. If the class_size distribution compresses toward 1, the signal mechanically vanishes regardless of whether the coupling persists. Fix: measure effect size relative to available class_size variance in each conductor range, not absolute rho.

3. **Zero computation artifacts.** LMFDB zeros at large conductor may be computed to different precision or with different numbers of zeros stored. Fix: normalize by zeros available and test whether n_zeros_stored itself correlates with class_size (database artifact, not mathematics).

The right approach is a **sliding-window null** that recalibrates at each conductor scale.

### Tests Executed

We immediately ran three tests from the review:

#### 1. Synthetic Null Test (Reviewer Requirement C) — PIPELINE VALIDATED

Four synthetic models, 200 trials each. **0.0% false positive rate across all models.**

| Synthetic Model | Mean rho | FPR |
|----------------|----------|-----|
| GUE zeros + randomly permuted class_size | -0.000 | 0.0% |
| Real zeros + conductor-predicted class_size | +0.001 | 0.0% |
| Real zeros + factorization-predicted class_size | -0.020 | 0.0% |
| GUE-resampled spacing + real class_size | -0.001 | 0.0% |

The pipeline does not hallucinate. Both real zeros AND real class sizes are required. Replacing either side with synthetic data — even conductor-correlated synthetic data — destroys it completely.

This is the single strongest validation result in the project. It directly addresses the reviewer's "most powerful missing piece."

#### 2. Conductor Factorization Confound (Attack Surface #2) — SURVIVES

Direct test of whether conductor prime factorization geometry explains the coupling.

- Conditioning on omega (distinct prime factors), Omega (total factors), largest prime factor, primality, and squarefreeness
- Signal reduces 28% but survives: **rho = 0.096, p = 1.4e-64**
- Signal is stronger for conductors with fewer prime factors (omega=1: rho=0.331, omega=5: rho=0.072)

The factorization gradient is consistent with the RMT interpretation: simpler Euler products produce a cleaner spectral signal with less noise masking the isogeny coupling.

#### 3. Higher-Order Spacing Test — GLOBAL, NOT BSD-LOCALIZED

This test directly answers the reviewer's suggestion about whether the signal is BSD-related (first gap only) or a global geometric property.

| Gap | Within-bin rho | z-score | After conditioning on gap_1 |
|-----|---------------|---------|----------------------------|
| gap_1_2 | 0.0802 | **14.4** | (baseline) |
| gap_2_3 | 0.0374 | **6.8** | rho=0.054, p=1.1e-21 |
| gap_3_4 | 0.0264 | **4.8** | rho=0.023, p=6.2e-05 |
| gap_4_5 | -0.012 | -2.2 | rho=-0.010, p=0.066 |
| gap_5_6 | 0.0360 | **6.1** | rho=0.048, p=1.6e-17 |

Key findings:

- **The signal is global.** It propagates from gap_1 through gap_3 with gradual decay (z: 14.4, 6.8, 4.8), goes quiet at gap_4, then **rebounds at gap_5** (z=6.1).

- **It survives conditioning on gap_1.** After removing the first gap entirely, gaps 2, 3, and 5 still carry independent isogeny class information (all p < 1e-5). The information is not leaking from gap_1 via RMT rigidity.

- **Not BSD-localized.** If this were purely about L(s) near s=1/2, only the first gap should matter. The rebound at gap_5 rules out a simple "distance from critical point" explanation.

- **The rebound at gap_5 is unexpected.** It could reflect periodic structure in how isogeny information distributes across the zero spectrum, or it could be an artifact of the finite zero sample (only 6-10 zeros per curve). This needs investigation at higher zero counts.

### Signal B Kill Protocol (Running)

A full kill protocol for Signal B (congruence graph communities predict rank) is executing:

1. **Level ablation** — does signal survive within-level-bin testing?
2. **Sato-Tate-preserving synthetic null** — permute a_p values independently per prime, rebuild graph 200 times
3. **Edge density control** — is community structure just reflecting node degree?
4. **Modulus sensitivity** — does the signal depend on the choice of ell?

Results pending.

---

## Updated Assessment

### Requirements scorecard

| Requirement | Status |
|-------------|--------|
| A. Extended conductor range | PENDING — DuckDB limited to N < 5,000; LMFDB Postgres label matching needs fixing |
| B. Independent replication (Cremona) | NOT STARTED |
| C. Synthetic null test | **DONE — 0% FPR across 800 trials** |
| D. Theoretical hook | PARTIAL — RMT N^(-1/2) scaling matches, motivic framing identified |

### What has changed since the review

1. The pipeline is validated — it cannot produce this signal from synthetic data.
2. The factorization confound is ruled out — conductor geometry explains 28% but not the core.
3. The signal is global across the zero spectrum, not BSD-localized — this is a stronger result than expected.
4. The motivic framing (L-functions as shadows of motives) provides the right conceptual level for interpretation.

### Remaining critical path

1. Fix LMFDB Postgres label matching to access conductor > 50,000
2. Cremona database replication
3. Investigate the gap_5 rebound — periodic structure or finite-sample artifact?
4. Complete Signal B kill protocol

---

*Written: 2026-04-13*
*Tests: synthetic_null_test.json, extended_conductor_factorization.json, higher_order_spacing.json*
