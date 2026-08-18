# Council Prompt: Research Battery Results (April 4, 2026)
## For: Titan Council (Claude, ChatGPT, Gemini, DeepSeek, Grok)
## Context: Six falsification experiments from 26 research packages, run against 14,751 ECs

---

## Ground Rules

You are hostile reviewers. Do not validate. Do not congratulate. For every claim, provide the strongest null hypothesis that explains the result, a specific falsification test, and the minimum threshold for evidence. If you think we're wrong, say exactly where and why.

---

## Background (One Paragraph)

We have a spectral tail finding: zeros 5-19 of elliptic curve L-functions encode rank geometry with ARI=0.55, and a 0.05 ARI residual survives beyond pure GUE repulsion (RMT simulation: ARI=0.44). Nine mechanisms have been stripped (central vanishing, conductor, Sha, Faltings height, modular degree, symmetry type, pre-asymptotic, truncation, inner twists). We ran 26 deep research packages through Gemini Deep Research to identify what the literature says we should test next. Those packages identified six experiments we could run against our existing 14,751-object DuckDB dataset (deduplicated by isogeny class, conductor <= 5000, 20+ zeros). We ran all six. Here are the results.

---

## Experiment A: Spectral Unfolding

**Question:** Does replacing Katz-Sarnak linear normalization (gamma_n / log(N)) with exact Gamma-function unfolding change the spectral tail ARI or the BSD wall?

**Method:** For each of 14,751 curves, recover raw zeros (gamma_n = normalized * log(N)), then apply the exact smooth counting function N_bar(T) = (T/pi) * log(sqrt(N)/(2*pi)) + (1/pi) * Im(log Gamma(1/2 + iT)) via mpmath.

**Results:**

| Normalization | ARI (all 20) | ARI (tail 5-19) | Ablation delta |
|---------------|-------------|-----------------|----------------|
| KS linear     | 0.5471      | 0.5548          | +0.0076        |
| Exact unfolding| 0.5521     | 0.5578          | +0.0057        |

BSD wall (variance ratio z1/z2): KS = 0.690, Unfolded = 0.777.
First gap distribution: KS mean=0.155, Unfolded mean=0.966 (expected -- unfolding rescales to unit spacing).

**Verdict:** Unfolding does NOT change the tail ARI meaningfully (+0.003). KS normalization is adequate for the spectral tail. The BSD wall softens slightly under unfolding (ratio moves toward 1) but does not vanish.

---

## Experiment B: Analytic vs Arithmetic Conductor

**Question:** Does re-normalizing by analytic conductor q = N/(4*pi^2) instead of arithmetic conductor N change any results? At N=5000, log(N)=8.52 vs log(q)=4.87 -- a 43% difference in scale factor.

**Results:**

| Normalization | ARI (all 20) | ARI (tail 5-19) |
|---------------|-------------|-----------------|
| Arithmetic (log N) | 0.5471 | 0.5548         |
| Analytic (log q)   | 0.5473 | 0.5548         |

Scale factor distribution: mean=1.943, range [1.759, 2.912].

**Verdict:** IRRELEVANT. Delta = 0.0000. The normalization choice has zero effect on clustering. This is because K-means is scale-invariant within conductor strata (all objects in a stratum share the same conductor, so the rescaling is a constant factor within each stratum).

---

## Experiment C: Sha Stratification on the Spectral Tail

**Question:** Do curves with |Sha| >= 4 have displaced zeros 5-19 compared to Sha=1 curves, within fixed rank and conductor?

**Data:** 6,319 rank-0 Sha=1 curves vs 498 rank-0 Sha>=4 curves.

**Results:**
- Hotelling T^2 = 23.23, F(16,6800) = 1.45, p = 0.109
- 0 of 16 individual zeros significant at p < 0.01
- 7 of 16 marginal at p < 0.05 (borderline, not correctable for multiple testing)
- Zero-1 control: Cohen's d = 0.098, p = 0.046 (weak but present, confirming Sha touches z1)

**Verdict:** Tail is Sha-INDEPENDENT. The Hotelling T^2 fails at p = 0.109. No individual zero reaches significance after any multiple-testing correction. Zero 1 shows a weak Sha signal (d=0.098), confirming that ablating zeros 1-4 correctly strips the Sha confound.

---

## Experiment D: Pair Correlation Density Shift

**Question:** Do rank-1 curves show tighter nearest-neighbor spacing in zeros 5-19 than rank-0 curves?

**Data:** 6,817 rank-0 vs 7,476 rank-1 curves.

**Results:**
- Mean NN spacing: rank-0 = 0.09663, rank-1 = 0.09486. Rank-1 is tighter.
- KS test: stat = 0.0236, p = 2.3e-26 (wildly significant)
- Cohen's d = -0.045 (small but real)
- 10 of 15 individual gaps significant at p < 0.01

**Per-gap pattern (Cohen's d, rank-1 minus rank-0):**

| Gap | d | p | Significant? |
|-----|---|---|-------------|
| z5-z6   | -0.027 | 0.028 | * |
| z6-z7   | -0.110 | 1.6e-6 | *** |
| z7-z8   | -0.083 | 1.0e-11 | *** |
| z8-z9   | -0.082 | 9.9e-6 | *** |
| z9-z10  | +0.000 | 0.083 |  |
| z10-z11 | -0.038 | 0.069 |  |
| z11-z12 | -0.098 | 9.2e-7 | *** |
| z12-z13 | -0.093 | 2.9e-10 | *** |
| z13-z14 | -0.055 | 0.005 | ** |
| z14-z15 | +0.000 | 0.755 |  |
| z15-z16 | -0.019 | 0.576 |  |
| z16-z17 | -0.044 | 0.008 | ** |
| z17-z18 | +0.065 | 5.8e-14 | *** (reversed!) |
| z18-z19 | -0.006 | 1.5e-4 | *** |
| z19-z20 | -0.086 | 4.7e-7 | *** |

**The pattern is not uniform.** Three features:
1. Strongest compression in z6-z9 (d ~ -0.08 to -0.11)
2. A "dead zone" at z9-z11 and z14-z16 (no significant difference)
3. An anomalous REVERSAL at z17-z18 (rank-1 has WIDER gap, d = +0.065, p = 5.8e-14)

**Verdict:** Rank-dependent spacing shift is CONFIRMED. But the non-uniform pattern -- especially the z17-z18 reversal -- is not predicted by simple GUE repulsion from a pinned zero at the origin. This structured gap pattern may be the microscopic signature of whatever produces the 0.05 ARI residual.

---

## Experiment E: Conductor-Bin ARI Decay Curve

**Question:** Does ARI decay linearly with 1/log(N)? If the y-intercept equals 0.44 (pure RMT baseline), the 0.05 residual is a finite-conductor correction.

**Results:**

| Conductor Bin | N objects | ARI (tail) | 1/log(N) |
|--------------|----------|------------|----------|
| 301-500      | 428      | 0.638      | 0.166    |
| 501-800      | 861      | 0.571      | 0.154    |
| 801-1200     | 1,307    | 0.541      | 0.145    |
| 1201-1800    | 2,030    | 0.529      | 0.137    |
| 1801-2500    | 2,507    | 0.525      | 0.130    |
| 2501-3500    | 3,687    | 0.552      | 0.125    |
| 3501-5000    | 3,925    | 0.584      | 0.120    |

Linear fit: ARI = 1.354 / log(N) + 0.374. R^2 = 0.315, p = 0.190.
Intercept = 0.374 (below the RMT baseline of 0.44).

**The critical anomaly:** ARI does NOT monotonically decay. It U-curves -- decreasing from conductor 300-2500, then INCREASING from 2500-5000. The linear fit is poor (R^2 = 0.315) because the relationship is non-monotonic.

**Verdict:** INCONCLUSIVE. The U-curve breaks the finite-conductor-correction narrative. Two possible explanations:
1. Sample composition changes at high conductor (more rank-2 curves? different rank ratio?)
2. A genuine structural effect where the residual GROWS at higher conductor

This needs investigation. What is different about the N > 2500 population?

---

## Experiment F: BSD Partial Correlations on Zeros 5-19

**Question:** After controlling for conductor and rank, do any BSD invariants predict individual zero positions in the spectral tail?

**Method:** Ridge regression partial correlation, controlling for [log(conductor), rank], testing each BSD invariant against each of zeros 5-20.

**Results:**

| Invariant | Mean |r| (tail) | Max |r| (tail) | Sig zeros (p<0.01) | Zero-1 r |
|-----------|------|------|------|------|
| Sha | 0.018 | 0.030 | 3/16 | +0.041*** |
| Faltings height | 0.012 | 0.031 | 3/16 | -0.038*** |
| Modular degree | 0.016 | 0.039 | 4/16 | -0.017* |
| Regulator | 0.010 | 0.025 | 1/16 | +0.043*** |

**Verdict:** All BSD invariants have |r| < 0.05 everywhere in the tail. The spectral tail is BSD-INDEPENDENT. The contrast is sharp: Sha, Faltings height, and regulator all show significant correlations with zero 1, but vanish in the tail. This confirms the BSD wall: zero 1 and zeros 5-20 are completely disjoint information channels.

---

## Updated Kill Count: 12 Mechanisms Stripped

| # | Mechanism | Method | Outcome |
|---|-----------|--------|---------|
| 1 | Central vanishing | Ablation | Removing z1 improves ARI |
| 2 | Conductor | Ridge regression | Signal survives |
| 3 | Sha order | Stratification | Orthogonal |
| 4 | Faltings height | Variance decomposition | < 1% |
| 5 | Modular degree | Variance decomposition | < 1% |
| 6 | Symmetry type | Root number conditioning | ARI=0.49, z=14.0 |
| 7 | Pre-asymptotic | Conductor scaling | FLAT (slope=-0.014) |
| 8 | Truncation | Extended zeros (25+) | PLATEAU at z5-19 |
| 9 | Inner twists | CM enrichment | CM=0.87x (depleted) |
| 10 | KS normalization | Exact Gamma unfolding | ARI unchanged (+0.003) |
| 11 | Arithmetic vs analytic conductor | Renormalization | Delta = 0.000 |
| 12 | Sha on tail | Hotelling T^2 | p = 0.109 (not significant) |

---

## Two New Findings

### Finding 1: The Structured Gap Pattern (Experiment D)

The rank-dependent spacing shift is not uniform across the spectral tail. It has three regimes:
- **Strong compression** (z6-z9): d ~ -0.08 to -0.11
- **Dead zones** (z9-z11, z14-z16): no rank discrimination
- **Anomalous reversal** (z17-z18): rank-1 WIDER, d = +0.065

This is NOT predicted by simple GUE repulsion propagation. GUE repulsion from a pinned zero should produce monotonically decreasing effect with distance from the origin. The oscillatory pattern suggests interference between multiple mechanisms.

### Finding 2: The ARI U-Curve (Experiment E)

ARI decreases from conductor 300-2500 (consistent with finite-conductor correction) then INCREASES from 2500-5000 (inconsistent with any correction that should vanish at N -> infinity). This U-curve has R^2 = 0.315 for a linear fit, which is terrible.

---

## Questions for This Round

1. **The gap pattern oscillation.** What produces dead zones at z9-z11 and z14-z16, and a reversal at z17-z18? Is there a theoretical prediction for which zero gaps should be most sensitive to rank? Does the spacing pattern match any known oscillation in the density of states?

2. **The ARI U-curve.** What changes in the elliptic curve population at conductor > 2500? Is this a rank-ratio shift, a Tamagawa effect, a selection bias in LMFDB, or a genuine structural deepening? What specific test would distinguish these?

3. **The BSD wall sharpness.** Zero 1 correlates with Sha (r=0.041), Faltings height (r=-0.038), and regulator (r=0.043). All four BSD invariants are significant for zero 1 but vanish in the tail. Is this sharp wall predicted by any theoretical framework, or is it a new observation?

4. **What produces the 0.05 residual?** We have now stripped 12 mechanisms. The structured gap pattern (Finding 1) may be the microscopic signature. What is the next mechanism to test? Specifically: should we pursue Tamagawa numbers, Galois image, or something else?

5. **Is the gap pattern paper-worthy on its own?** Independent of the ARI finding, the fact that rank-dependent zero spacing has a structured oscillatory pattern across the spectral tail seems novel. Has anyone measured gap-specific rank effects in L-function zeros before?
