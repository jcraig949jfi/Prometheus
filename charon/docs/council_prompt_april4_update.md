# Council Prompt Update: April 4, 2026 — Experimental Results
## For: Titan Council (Claude, ChatGPT, Gemini, DeepSeek, Grok, Perplexity)
## Context: Results from the validation battery that the Council itself designed

---

## Ground Rules (Same as Before)

You are hostile reviewers. You designed the validation battery in the prior round.
We ran your experiments. Here are the results. Your job is to evaluate whether
these results survive your own tests, or whether they fail.

---

## What We Ran (Your Experiments, Our Data)

### Experiment 1: RMT Simulation (Council's "Five-Line Simulation" Challenge)

**Your challenge:** "If a five-line RMT simulation reproduces ARI = 0.49 within
SO(even), the finding reduces to 'GUE repulsion works as expected.'"

**What we built:** Two approaches:
- **Naive:** Sample SO(2(N-2)) eigenangles, insert 2 zeros at origin, no correction
- **Enhanced (Metropolis-corrected):** MCMC correction for enhanced sin^2(theta/2)
  repulsion from pinned zeros. This is the correct conditional distribution.

**Setup:** SO(120) matrices (N=60), zeros 5-19, 84 conductor strata (533 rank-0,
102 rank-2), 50 trials per approach.

**Results:**

| Method | ARI Mean | ARI Std |
|--------|----------|---------|
| Empirical | 0.4913 | -- |
| RMT Naive | 0.4430 | 0.0249 |
| RMT Enhanced | 0.4384 | 0.0286 |
| Permutation null | 0.0063 | 0.0257 |

**Verdict:** GUE repulsion explains ~90% (ARI 0.44 of 0.49). Gap = 0.053 (~2 sigma).
The five-line simulation falls short. The residual is real but modest.

**Surprise:** Enhanced < Naive. The MCMC equilibration REDUCES the signal by
spreading angles more evenly. The naive approach overestimates tail distortion.

---

### Experiment 2: Conductor Scaling (DeepSeek's "Scaling Test")

**Your prediction (DeepSeek):** "You will see a flat or decreasing trend."

**Results (all ranks, zeros 5-19):**

| Conductor Bin | N_obj | N_strata | ARI |
|---------------|-------|----------|-----|
| 101-500 | 434 | 31 | 0.638 |
| 501-1K | 1,492 | 120 | 0.542 |
| 1K-2K | 3,391 | 247 | 0.547 |
| 2K-3K | 3,661 | 245 | 0.534 |
| 3K-5K | 5,773 | 373 | 0.571 |

**Linear trend slope: -0.014 per bin. FLAT.**

**Ablation improvement (tail > all-20):** Positive in EVERY conductor bin.
Range: +0.002 to +0.029.

**Verdict:** DeepSeek was half right: the trend is flat, not increasing. But the
signal is NOT a pre-asymptotic artifact (it doesn't decrease either). The spectral
tail finding is intrinsic to zero geometry, stable across conductor ranges.

---

### Experiment 3: Extended Zero Ablation (Council's "20-Zero Truncation" Test)

**Your prediction (DeepSeek):** "The ARI will peak somewhere in the range of
zeros 10-30 and then decline."

**Data source:** LMFDB PostgreSQL mirror. 17,313 EC L-functions with 25-29
zeros each (max available). 12,810 with 25+ zeros used.

**Results:**

| Slice | ARI | N_zeros |
|-------|-----|---------|
| z1-4 (head) | 0.471 | 4 |
| z5-10 | 0.502 | 6 |
| z5-15 | 0.542 | 11 |
| **z5-19** | **0.548** | **15** |
| z5-25 | 0.546 | 21 |
| z10-25 | 0.548 | 16 |
| z15-25 | 0.546 | 11 |
| z20-25 | 0.504 | 6 |
| z1-25 (all) | 0.542 | 25 |

**Leave-one-out:** No single zero contributes > 0.003 ARI. Signal is distributed.

**Verdict:** DeepSeek was WRONG. The peak is at z5-19 and the signal PLATEAUS --
it does NOT decline when extending to z25. The 20-zero truncation was not
limiting our signal. Additional zeros carry zero marginal information.

---

### Experiment 4: Inner Twist Decomposition

**Data:** 4,265 Type B (EC-proximate) dim-2 wt-2 modular forms vs all dim-2 wt-2.

**Results (enrichment in Type B vs ALL):**

| Property | Type B | ALL | Enrichment |
|----------|--------|-----|------------|
| CM | 4.0% | 4.7% | 0.87x |
| Self-dual | 57.0% | 45.3% | 1.26x |
| Fricke +1 | 33.2% | 23.0% | **1.44x** |
| Char order 4+ | 6.3% | 10.5% | **0.60x** |

**Verdict:** Inner twists do NOT explain EC-proximity. CM is not enriched (0.87x).
Modest enrichments in self-dual (1.26x) and Fricke +1 (1.44x) -- the latter is
NEW and interesting (Type B forms share functional equation parity with nearby ECs).
Higher character orders are depleted.

---

## Updated State After Validation Battery

**Mechanisms STRIPPED by the battery:**
1. Truncation artifact: STRIPPED (Exp 3 -- signal plateaus, not truncation-limited)
2. Pre-asymptotic artifact: STRIPPED (Exp 2 -- flat across conductor)
3. Inner twist structure: STRIPPED (Exp 4 -- CM not enriched)
4. Full GUE repulsion: PARTIALLY explains (Exp 1 -- 90%, gap = 0.05)

**The surviving residual (0.05 ARI gap beyond RMT):**
- Not truncation (plateau at z5-19)
- Not pre-asymptotic (flat scaling)
- Not inner twists (CM = 0.87x)
- Not symmetry type classification (killed in prior round, z = 14.0)

**New lead from Exp 4:** Fricke +1 enrichment (1.44x) in Type B forms.
Functional equation parity appears to influence spectral proximity.

---

## Questions for This Round

1. **Is the 0.05 ARI gap (empirical 0.49 vs RMT 0.44) meaningful?** At 2 sigma
   above RMT mean, it's suggestive but not overwhelming. What additional test
   would definitively confirm or kill this gap?

2. **The Enhanced < Naive surprise.** The MCMC-corrected simulation produces
   LOWER ARI than the naive "insert and don't equilibrate" approach. This means
   the correct conditional distribution actually predicts LESS tail distortion
   than the naive model. What does this imply about the residual? Is the gap
   actually LARGER than 0.05 when properly measured?

3. **Fricke +1 enrichment: mechanism or marker?** Type B forms are 1.44x
   enriched for Fricke eigenvalue +1. Is this because:
   (a) Fricke +1 forms genuinely have more EC-like zero distributions, or
   (b) Fricke +1 is correlated with some other property that drives proximity?

4. **What arithmetic produces 0.05 beyond RMT?** Candidates:
   - Conductor-dependent corrections to KS normalization
   - Arithmetic conductor vs analytic conductor effects
   - Galois representation image
   - Something else?

5. **Is the plateau at z5-19 theoretically predicted?** The signal saturates
   at 15 zeros and doesn't improve with more. Does any theoretical framework
   predict a specific saturation point for rank discrimination in the zero spectrum?
