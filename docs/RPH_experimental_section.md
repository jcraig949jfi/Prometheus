# RPH Experimental Section (NeurIPS/ICLR Style)
*Extracted from RPH.md lines 500–806 — ChatGPT-generated publication-ready experimental design*
*Date extracted: 2026-03-21*

---

## 4. Experiments

### 4.1 Overview

We test the hypothesis that there exist linear directions in residual stream space that induce transitions into reasoning-like trajectory classes aligned with endogenous activations. Our evaluation is structured around three requirements:
1. **Causal efficacy**: Does intervention increase reasoning metrics?
2. **Endogeneity**: Does the direction align with naturally occurring reasoning states?
3. **Non-bypass behavior**: Is the effect mediated through native computation rather than shortcut routing?

We evaluate candidate vectors discovered via structured novelty search (Section 4.2) using three primary metrics: counterfactual sensitivity (Δ_cf), stepwise mutual information (MI_step), and projection differential (Δ_proj). All results are compared against matched random baselines and non-reasoning novelty controls.

---

### 4.2 Candidate Vector Generation

We generate candidate steering vectors using a structured novelty search objective:

```
F(g) = d_semantic(g) · C(g)
```

where:
- `d_semantic` is cosine distance between steered and baseline outputs in embedding space
- `C(g)` is a Gaussian penalty over log-perplexity to enforce coherence

We run CMA-ES for 300 generations with population size 64 on a 0.5B parameter transformer (Qwen 2.5 0.5B). Vectors are injected at layer L ∈ {8, 12, 16}, selected via preliminary sweeps.

We retain the top N = 50 vectors with F(g) > 0.3. From these, we select:
- K = 5 candidate vectors with highest diversity (pairwise cosine distance > 0.2)
- K = 5 matched-novelty controls (high F(g), low reasoning metrics)
- K = 10 random vectors sampled from N(0, I) and normalized to matched norm

---

### 4.3 Evaluation Tasks

We evaluate on three task families:

**(A) Arithmetic reasoning**
- GSM8K-style problems (8–12 steps)
- 200 samples

**(B) Logical reasoning**
- Synthetic syllogisms and conditional reasoning
- 200 samples

**(C) Counterfactual reasoning**
- Prompts with perturbable intermediate facts
- 200 samples (paired original/modified)

All tasks are zero-shot without chain-of-thought prompting.

---

### 4.4 Intervention Protocol

For each prompt x, we compute:
- Baseline trajectory: `h_L`
- Steered trajectory: `h_L + α·v`

with:
- α = 1.0 unless otherwise specified
- Injection at fixed layer L

We generate outputs with temperature 0.7 and max length 256 tokens.

Each condition (baseline, steered, random control) is evaluated over identical prompts.

---

### 4.5 Metrics

#### 4.5.1 Counterfactual Sensitivity (Δ_cf)

For each paired prompt (x, x') differing in one intermediate fact:

```
Δ_cf = E[d(y, y')]
```

where y, y' are outputs and d(·) is normalized semantic distance (SBERT cosine distance).

We report:
- Mean Δ_cf across dataset
- Effect size vs baseline

#### 4.5.2 Stepwise Mutual Information (MI_step)

We estimate:

```
MI_step = I(h_{1:t}; h_{t+1:T}) - I_baseline
```

Implementation:
- Hidden states projected via PCA (top 64 components)
- MI estimated using k-NN estimator (k=10)
- Baseline MI computed from shuffled sequences

We report:
- Mean MI_step per sequence
- Aggregate mean across dataset

#### 4.5.3 Projection Differential (Δ_proj)

We compute:

```
Δ_proj = E[⟨h, v⟩ | SC ∧ (Δ_cf > ε)] − E[⟨h, v⟩ | HB]
```

where:
- SC = self-correction events
- HB = heuristic bypass cases (correct output, low Δ_cf)

Self-correction is detected via contradiction patterns in token logits.

#### 4.5.4 Intervention Consistency (IC) [Optional but Recommended]

We perturb intermediate hidden states:

```
IC = E[d(y, y') | h_t → h_t + ε]
```

with ε ~ N(0, σ²I), σ = 0.05 ‖h_t‖

---

### 4.6 Statistical Tests

All tests are two-sided unless specified.

#### 4.6.1 Δ_cf Improvement Test

**Null hypothesis:** H₀: Δ_cf^steered ≤ Δ_cf^baseline

Test: Paired t-test over prompts

Threshold:
- p < 0.01
- Effect size: Cohen's d > 0.5

#### 4.6.2 MI_step Increase

**Null hypothesis:** H₀: MI_step^steered ≤ MI_step^baseline

Test: Bootstrap (10,000 resamples)

Threshold:
- 95% CI excludes 0
- Relative increase ≥ 15%

#### 4.6.3 Δ_proj Positivity

**Null hypothesis:** H₀: Δ_proj ≤ 0

Test: Permutation test (shuffle SC/HB labels, 10k iterations)

Threshold:
- p < 0.01
- Absolute margin: Δ_proj > 0.1 · ‖v‖

#### 4.6.4 Random Baseline Rejection

Compare candidate vectors vs random:

Test: Mann–Whitney U test

Threshold:
- p < 0.01
- Candidate median > random median on ≥2 metrics

#### 4.6.5 Matched-Novelty Control Test

Goal: show novelty ≠ reasoning

Test: Same metrics vs matched controls

Threshold:
- Candidate > control on ≥2 metrics
- p < 0.05

---

### 4.7 Phase Transition Analysis (α Sweep)

We sweep: α ∈ {0, 0.25, 0.5, 1, 2, 4}

Measure Δ_cf and MI_step.

Classification:
- **Phase transition:** max slope dM/dα > 2× baseline slope
- **Continuous:** monotonic, smooth increase
- **Artifact:** non-monotonic or unstable

---

### 4.8 Classification Criteria

A vector is classified as a **precipitation vector** if it satisfies:

**Required (all):**
1. Δ_cf improvement — p < 0.01, d > 0.5
2. MI_step increase — ≥15% increase, CI excludes 0
3. Δ_proj > 0 — p < 0.01
4. Random baseline rejection — outperforms random vectors
5. Matched-control superiority — outperforms non-reasoning novelty vectors

**Supporting (at least one):**
- Phase transition signature
- Cross-task generalization (≥2 domains)
- Positive intervention consistency

---

### 4.9 Ablation: Non-Bypass Verification

We perform causal mediation:
1. Identify reasoning-relevant features (via SAE or probe)
2. Ablate features post-injection
3. Measure drop in Δ_cf

**Criterion:**
- ≥30% reduction → mediated via native reasoning
- <10% reduction → likely bypass

---

### 4.10 Reporting

We report:
- Mean ± standard error
- Effect sizes (Cohen's d)
- p-values (corrected via Benjamini–Hochberg, FDR 0.05)

All experiments are repeated with 3 random seeds.

---

## 5. Key Threshold Summary

| Metric | Threshold |
|---|---|
| Δ_cf | p < 0.01, d > 0.5 |
| MI_step | ≥15% increase, CI excludes 0 |
| Δ_proj | p < 0.01, > 0 |
| Random baseline | p < 0.01 |
| Matched control | p < 0.05 |
| Mediation drop | ≥30% |
| Phase transition | slope > 2× baseline |

---

## 6. Notes on Rigor

- All tests are pre-registered (no threshold tuning post hoc)
- Metrics computed on held-out prompts
- Vector selection performed without access to reasoning metrics (only novelty score)
