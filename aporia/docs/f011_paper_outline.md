# F011 Paper — Skeleton Outline

**Working title:** Sato-Tate saturation of L-function zero statistics in CM and rare-torsion subfamilies of rank-0 elliptic curves

**Authors:** Prometheus team (Charon, Ergon, Aporia, Techne, Harmonia)

**Status:** Outline only. For Charon to expand into methods/tables per his tick-33 readiness statement, pending James signal.

---

## Abstract (target 200 words)

We study the local variance of the first four gaps in rank-0 elliptic curve L-function zero sequences, normalized by the local 4-gap mean. Comparing against a matched-GUE null constructed with the same local normalization, we observe a systematic compression: EC rank-0 L-functions sit 20-33% below matched GUE at gap1-gap4, with the deficit deepening with gap index (gap4 > gap1). The compression is structural (z = -48 to -103 at n = 200K) and cannot be explained by finite-N effects. Using a multi-channel Euler-product-simplification framework, we account for ~78% of gap1 and ~68% of gap4 variance via a joint regression on (CM-flag, fundamental CM discriminant, order conductor, torsion rarity, log-conductor). CM curves show ~2× deeper compression than non-CM; rare Mazur torsion (orders 5, 6, 8) shows comparable deepening. The two channels saturate at gap1 (sub-additive, -19 pp residual from additive prediction) but combine additively at gap4. Within CM, the non-maximal orders in Q(√-3) uniquely invert the gap-index gradient — a sixth-roots-of-unity sub-void we identify and confirm. The remaining 22-32% residual suggests per-curve noise and at least one unidentified arithmetic predictor.

---

## 1. Introduction

- GUE universality for L-function zero statistics (Odlyzko-Montgomery 1973, Rudnick-Sarnak 1996).
- Katz-Sarnak random-matrix-theory predictions.
- Wachs 2026 "Sha displacement" paper framing; motivation for a finer local-gap analysis.
- Statement of main result: rank-0 EC L-functions are sub-GUE in local-4-gap variance, with a quantitatively predictable Euler-product-simplification signature.

## 2. Data and Methods

### 2.1 Data
- LMFDB `lfunc_lfunctions`: 1.87M EllipticCurve L-functions.
- LMFDB `ec_curvedata`: 3.8M rational EC, joined by lmfdb_iso.
- Per-curve zero sequence truncated to first 4 positive zeros at unit spacing.
- 200K rank-0 sample with zeros stored; 2134 rank-0 CM subset (indexed CM filter).

### 2.2 Matched-GUE null
- Local 4-gap normalization: each curve's first 4 gaps divided by their own mean.
- Baseline null: 200K random N=40 GUE matrices with the same local-4-gap normalization.
- Baseline variances: {0.1472, 0.1741, 0.1725, 0.1468} at gap1-4.
- Critical: raw GUE (global normalization) variance = 0.1781 is NOT the correct null.

### 2.3 Predictors
- cm_flag ∈ {0, 1}.
- log|fund_disc|, order_conductor (Ergon's CM-theory decomposition via `cm_disc = order_conductor² × fund_disc`).
- torsion_bin ∈ {1 common, 2 medium, 3 rare} per Mazur group size.
- log_N conductor decile.

### 2.4 Fitting
- Cell-level OLS on 42 cells (27 non-CM decile × torsion bin, 15 CM |D| × torsion × conductor coarse).
- Per-disc dummies + RCF-decomposition robustness check.
- Bootstrap CI for selected claims.

## 3. Results

### 3.1 The structural compression (Figure 1: matched-null comparison per gap)
- Observation: EC gap1 var = 0.118 vs matched null 0.147 (z = -63.6 at n = 200K).
- Gap-index gradient: deficit deepens from 20% at gap1 to 33% at gap4.
- Charon's 1646-curve BSD subset independently reproduces (+26 to +42% per gap).

### 3.2 Conductor attenuation (Figure 2: slope vs log_N)
- Slope = -2.19% / log(N), r = -0.89 at Charon's wide log-N span.
- Katz-Sarnak asymptotic reading: EC L-functions → bulk GUE as N → ∞.
- Gap-index gradient persists as asymptotic residual (gap4 > gap1 across all conductors).

### 3.3 CM channel (Figure 3: per-CM-disc compression)
- CM curves (n = 2134) 1.5-2× deeper compression than non-CM at gap1.
- Per-CM-disc scatter characterized by (D_K, order_conductor).
- log|D| trend with +19.15 pp per unit, Heegner-only R² = 0.68.

### 3.4 Torsion channel (Figure 4: deficit per Mazur group)
- Rare torsion (5, 6, 8) 2.5× deeper gap1 than trivial.
- Gap4 roughly uniform across torsion — torsion-invariant structural residual.

### 3.5 Isogeny-invariance kill (Table 1)
- Within 25% of isogeny classes with class_size ≥ 2, Sha varies but gap1 is shared.
- Proves: Sha cannot be a direct cause. The bridge Sha → gap runs through L(1, E) via BSD.

### 3.6 CM × torsion cross-stratification (Table 2)
- Gap1: sub-additive (-19 pp residual from additive prediction). Channels compete.
- Gap4: perfectly additive (+3.3 pp residual from prediction). Channels orthogonal.
- CM_trivTor has flat gap-index gradient (+1.3); all other cells have +10 to +23.
- **Two-regime model:**
  - gap1 = max(CM_channel, torsion_channel) + conductor_atten + noise (SATURATING)
  - gap4 = CM_channel + torsion_channel + conductor_atten + noise (ADDITIVE)

### 3.7 Q(√-3) gradient inversion (Figure 5: (K, c) lattice)
- Within-D_K, only Q(√-3) non-maximal orders invert the gap-index gradient.
- -12, -27 shrink; -16 (Q(i)), -28 (Q(√-7)) grow or stay MILD.
- Interpretation: sixth-roots-of-unity in Z[(1+√-3)/2] create extra symmetry; non-maximal orders break it non-uniformly across gap indices.

### 3.8 Closure state
- Joint regression with principled predictors: gap1 R² = 0.78, gap4 R² = 0.68.
- Per-disc dummies match RCF-decomposition at same R² with half the parameters — (D_K, order_conductor) is the natural parameterization.
- 22% gap1, 32% gap4 residual: per-curve noise + at least one unidentified arithmetic predictor.

## 4. Discussion

- Connection to prior literature (Gamburd-Rudnick, Keating-Snaith, Katz).
- Why saturation at gap1 but additivity at gap4? A two-regime model for Euler-product-family constraints.
- The Q(√-3) sub-void invites a dedicated CM-theory analysis on ring-class-field structure.
- Open questions:
  - What's the fifth predictor? Regulator, Petersson norm, ramification signature?
  - Does the pattern persist at rank ≥ 1?
  - What's the analogous story on higher-degree L-functions (g2, Hilbert modular)?

## 5. Data Availability

- `closure_test_rcf.json` (Ergon): per-cell regression output
- `cm_disc_gap_profile.md` (Charon): 12-disc shape taxonomy
- `f011_sha_gap4_bootstrap.json` (Charon): Sha-split verifications
- `cm_only_fast.json` (Ergon): n=2134 CM fast-path
- `gap_gradient_mechanism.json` (Ergon): conductor × Sha decomposition

## Appendix A: Methodological Lessons

Documented during the 3-hour session that produced this paper:

1. **Null-choice invariance.** Matched-GUE with local normalization is essential; raw GUE with global mean gave false "finite-N" explanation and cost ~3 retractions before identified.
2. **PATTERN_KILL_UNDER_CONSTRAINED:** no F-cell kill asserted from a single test; require 2/3 of (alt-null, cross-dataset, gradient-AND-absolute-level) before negative promotion.
3. **PATTERN_PREDICTION_LEVEL_MISMATCH:** pre-register predictions at measurement level (cell value, binary sign test), not at regression-coefficient level.
4. **Small-n guard:** n < 50 findings get "pending n ≥ 200 confirmation" tag before building downstream hypotheses.
5. **Scope specification:** every result carries the scope within which it holds (LMFDB NF subfamily, 3-13 crossing census, conductor range, etc.).

---

*Outline drafted by Aporia on 2026-04-22 while team standing down. Charon's ready-to-draft methods/tables state (~30-45 min) fills this skeleton on James signal. Ergon's session artifacts provide regression outputs; Techne's tool catalog documents the instrumentation.*
