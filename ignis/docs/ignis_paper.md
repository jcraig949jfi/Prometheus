# Evolutionary Circuit Discovery in Transformer Latent Space: Searching for Universal Verification Mechanisms via Covariance Matrix Adaptation

**Authors:** J. Craig, Augment Agent
**Affiliation:** Prometheus Project
**Date:** March 2026
**Status:** Methodology Paper (Intent-Focused)

---

## Abstract

We present **Ignis** (Search for Evolved Thought Intelligence — Latent Edition), a novel framework for discovering universal verification circuits in large language models through evolutionary search in continuous activation space. Rather than probing for known circuits or training steering vectors via gradient descent, Ignis uses **Covariance Matrix Adaptation Evolution Strategy (CMA-ES)** to evolve $d_{model}$-dimensional steering vectors that are surgically injected into the transformer's residual stream via the **Transformer Internal Injection (TII)** engine. The system evaluates candidate vectors against a battery of logically distinct reasoning traps simultaneously, using geometric mean fitness to enforce multi-task generalization. A causal falsification battery — including noise gates, orthogonal projections, and sign-flip tests — distinguishes genuine directional circuits from energy artifacts. The framework operates across multiple model scales (0.5B–7B parameters) with independent search state per model, enabling cross-scale invariance analysis. This paper describes the methodology, theoretical motivation, and a ranked roadmap of future extensions, with emphasis on the system's intent: to determine whether self-correction in transformers corresponds to discrete circuits or continuous cognitive modes.

---

## 1. Introduction

### 1.1 The Central Question

Modern large language models exhibit behaviors that suggest internal verification processes — the ability to catch logical errors, reconsider initial answers, and self-correct reasoning chains. A fundamental question in mechanistic interpretability is whether these behaviors arise from:

**(a)** Discrete, localizable circuits — specific neural pathways that can be identified, isolated, and causally tested, analogous to biological neural circuits; or

**(b)** Continuous cognitive modes — broad regions of activation space where the model's computational regime shifts, more analogous to attractor states in dynamical systems.

This distinction has profound implications for AI safety, interpretability, and alignment. If verification is a discrete circuit, it can be surgically enhanced, monitored, or preserved during fine-tuning. If it is a continuous mode, understanding its geometry and dimensionality becomes the operative research challenge.

### 1.2 Limitations of Existing Approaches

Current mechanistic interpretability methods face several constraints when applied to this question:

1. **Supervised probing** requires labeled examples of the target behavior and assumes the researcher knows what to look for. It cannot discover unknown circuits.
2. **Activation patching** tests hypotheses about specific components but does not search for optimal interventions.
3. **Gradient-based steering vector training** (e.g., contrastive activation addition) finds local optima and requires differentiable objectives, limiting the complexity of behavioral targets.
4. **Sparse autoencoders** decompose activations into interpretable features but do not directly test whether those features are causally sufficient for behavioral change.

Ignis addresses these limitations by framing circuit discovery as a **black-box optimization problem** in continuous activation space, where the objective function is behavioral change across multiple reasoning tasks simultaneously.

### 1.3 The Evolutionary Approach

Evolution is well-suited to this problem for three reasons:

1. **No gradient required.** The fitness function (did the model answer correctly across multiple traps?) is non-differentiable, sparse, and discontinuous. CMA-ES handles this natively.
2. **Implicit manifold discovery.** The covariance matrix learned by CMA-ES captures the local geometry of the fitness landscape — its eigenvectors reveal the directions that matter, and its eigenvalues reveal their relative importance.
3. **No prior assumptions.** Unlike contrastive methods that require paired examples of "good" and "bad" reasoning, evolutionary search explores the activation space without presupposing what the verification circuit looks like.

---

## 2. Architecture

### 2.1 System Overview

Ignis operates as a closed-loop evolutionary system with four major components:

1. **Genome Representation**: A steering vector $\vec{v} \in \mathbb{R}^{d_{model}}$ paired with an injection layer index $L$.
2. **TII Engine**: Surgical injection of $\vec{v}$ into the transformer's residual stream at `blocks.{L}.hook_resid_pre`.
3. **Multi-Task Crucible**: Simultaneous evaluation against a battery of logically distinct reasoning traps.
4. **CMA-ES Optimizer**: Population-based search with adaptive covariance, step-size control, and evolution path tracking.

The evolutionary loop follows a standard Ask-Evaluate-Tell cycle:

$$\text{Sample} \rightarrow \text{Inject} \rightarrow \text{Evaluate} \rightarrow \text{Falsify} \rightarrow \text{Update Distribution} \rightarrow \text{Repeat}$$


### 2.2 Transformer Internal Injection (TII)

The TII engine provides white-box access to the transformer's internal computation via TransformerLens's `HookedTransformer`. During autoregressive generation, a hook is registered at the target layer's residual stream pre-attention:

$$x_{steered} = x_{clean} + \vec{v}_{evolved}$$

Key design decisions:

- **Injection point**: `hook_resid_pre` (before the attention computation at layer $L$). This ensures the steering signal propagates through all subsequent attention heads and MLP layers, allowing the model to "interpret" the injected direction through its normal computational pathway.
- **Position**: Configurable via `position_ratio` ∈ [0, 1]. Each genome includes a `position_ratio` parameter that selects the injection token: `token_index = floor(seq_len × position_ratio)`. The default is 1.0 (final token), with 20% of candidates using stochastic exploration across the full range. This allows CMA-ES to discover whether verification circuits activate at earlier prompt positions — a key degree of freedom for trajectory-level interventions.
- **No coefficient scaling**: The raw vector magnitude serves as the effective "dosage." CMA-ES controls magnitude implicitly through the mean vector and step size $\sigma$.

### 2.3 Genome Representation

A genome is defined as the tuple $(L, \vec{v})$ where:
- $L \in \{1, \ldots, n_{layers}\}$ is the injection layer, specified as a ratio of model depth (default 0.75) with 10% exploration jitter.
- $\vec{v} \in \mathbb{R}^{d_{model}}$ is the steering vector.

This representation is deliberately minimal. The genome encodes *what direction to push* and *where in the network to push it*. It does not encode magnitude separately from direction — the CMA-ES step size $\sigma$ and the covariance matrix $C$ jointly control the exploration radius.

### 2.4 CMA-ES in High-Dimensional Activation Space

The search space dimensionality ($d_{model}$) ranges from 896 (Qwen 0.5B) to 3584 (Qwen 7B). Standard CMA-ES maintains a full $d \times d$ covariance matrix, requiring $O(d^2)$ memory — prohibitive at these scales. Ignis uses **Diagonal CMA-ES**, which maintains only a variance vector $\vec{c} \in \mathbb{R}^d$, reducing memory and compute to $O(d)$.

The distribution update follows the standard CMA-ES formulation adapted for diagonal covariance:

1. **Rank-$\mu$ update**: The covariance is estimated from the $\mu$ best-performing candidates, weighted by rank.
2. **Evolution paths**: Cumulative path vectors $p_c$ and $p_\sigma$ track the search trajectory, enabling step-size adaptation.
3. **Step-size control**: $\sigma$ is adapted via the conjugate evolution path $p_\sigma$ to maintain an expected rate of progress.

The diagonal restriction means CMA-ES cannot model correlations between activation dimensions. This is a deliberate trade-off: full CMA-ES would require ~12 GB of memory for the covariance matrix alone at $d=3584$. The diagonal variant can still discover the correct direction — it simply cannot exploit inter-dimension correlations to do so faster.

### 2.5 Multi-Model Cycling

The pipeline rotates through models of increasing scale (0.5B → 1.5B → 3B → 7B) with fully independent CMA-ES state per model. Each model maintains its own mean vector and covariance (different $d_{model}$ dimensions), inception seed, generation counter and evolution paths, and best-discovered genomes.

VRAM is explicitly released between rotations via `gc.collect()` and `torch.cuda.empty_cache()`, enabling all four models to run on a single 16GB GPU in sequence.

The scientific value of multi-model cycling is cross-scale invariance testing: if the same *direction* (relative to each model's geometry) consistently improves verification across scales, the circuit is likely a fundamental computational structure rather than a scale-specific artifact.

---

## 3. The Multi-Task Crucible

### 3.1 Design Philosophy

The central hypothesis of Ignis is that self-correction is a **universal** mechanism — not a collection of task-specific heuristics. The Multi-Task Crucible enforces this by requiring simultaneous success across logically distinct reasoning challenges.

A genome that improves performance on "Is 9.11 > 9.9?" but fails on "Which is heavier, a pound of gold or feathers?" has found a decimal-specific heuristic, not a verification circuit. Only genomes that improve reasoning across *all* traps receive high fitness scores.

### 3.2 Trap Battery

The current battery consists of four traps, each targeting a different cognitive failure mode:

| Trap | Failure Mode | Naive Error | Correct Response |
|------|-------------|-------------|-----------------|
| Decimal Magnitude | Digit-count heuristic | "9.11 > 9.9 because 11 > 9" | "9.9 > 9.11 (compare 9.90 vs 9.11)" |
| Density Illusion | Associative bias | "Gold is heavier" | "Both weigh one pound" |
| Spatial Inversion | Spatial reasoning failure | "Still fits the left hand" | "Fits the right hand (geometry inverts)" |
| Anti-Sycophancy | Authority compliance | "Professor is correct, 7 is not prime" | "7 is prime — only divisible by 1 and itself" |

The first three traps share a structural property: each has a *compelling wrong answer* that most models default to, and a *correct answer* that requires overriding the initial impulse. The Anti-Sycophancy trap adds a distinct dimension: the model already "knows" the correct answer (7 is prime) but is pressured by social authority to abandon it. This tests whether an evolved vector increases *confidence on correct answers*, not merely doubt on incorrect ones — a critical distinction between **verification circuits** (which confirm correct reasoning) and **hesitation circuits** (which introduce blanket uncertainty).

### 3.3 Three-Tier Scoring

Each trap produces a score based on a three-tier system designed to provide CMA-ES with a smooth optimization landscape:

| Tier | Condition | Score | Gradient Signal |
|------|-----------|-------|----------------|
| **Floor** | Failure markers detected | 0.1 | "Actively wrong — move away from this direction" |
| **Baseline** | No markers at all | 0.3 | "Stopped being wrong — this direction disrupted the error pattern" |
| **Credit** | Target markers detected | 1.0+ per marker | "Actively correct — amplify this direction" |

The baseline tier (0.3) is a critical design element. Without it, "confused gibberish" and "actively wrong" outputs both score 0.1, giving CMA-ES no gradient signal to distinguish between them. With the baseline, CMA-ES can learn that disrupting the model's default (wrong) reasoning — even without producing correct output — is a step in the right direction.

### 3.4 Logit-Based Tier 2 Scoring

In addition to marker-based scoring, each trap with a configured logit variant runs a second forward pass with a forced binary-choice prompt (e.g., "Is 9.11 > 9.9? Answer True or False:"). The model's probability assigned to the correct token provides a continuous score ∈ [0, 1], which is blended with the marker fitness at a 70/30 ratio (marker-dominant). This gives CMA-ES a smooth gradient signal where marker scoring alone would produce discrete jumps — a model that shifts from 5% to 30% probability on the correct answer receives proportional credit, even if the free-generation output still uses wrong phrasing. The logit tier supplements but does not replace marker scoring, preserving the behavioral grounding of the fitness function.

### 3.5 Geometric Mean Aggregation

Individual trap scores are aggregated via geometric mean:

$$F_{total} = \exp\!\left(\frac{1}{n}\sum_{t=1}^{n} \log S_t\right)$$

The geometric mean was chosen over alternatives for three properties:

1. **Multi-task enforcement**: A near-zero score on any single trap collapses the total fitness. A genome scoring $[3.0, 3.0, 0.1]$ gets $F = 0.97$ — barely above baseline — despite two excellent scores. This prevents task-specific overfitting.
2. **Smooth gradients**: Unlike a raw product ($3.0 \times 3.0 \times 0.1 = 0.9$), the geometric mean preserves the *relative improvement* from partial successes, giving CMA-ES a gradient to follow.
3. **Scale invariance**: Adding a fourth trap to the battery does not change the magnitude range of fitness scores, unlike a product which would shrink geometrically with battery size.

---

## 4. Causal Falsification

### 4.1 The Problem of False Positives in High-Dimensional Space

In a $d$-dimensional space (where $d \approx 1000$–$3500$), random perturbations can produce surprising behavioral changes simply due to the high dimensionality. A steering vector that "works" might be exploiting energy sensitivity in a particular layer — any sufficiently large perturbation at that layer changes behavior — rather than encoding a meaningful direction.

Ignis addresses this with a five-test falsification battery, applied to every genome that scores above baseline:

### 4.2 Noise Gate (Null-A)

A random vector $\vec{r}$ is generated with $||\vec{r}|| = ||\vec{v}||$ (same norm as the discovered vector). If the random vector achieves $\geq 80\%$ of the discovered vector's fitness, the genome is rejected — the layer is energy-sensitive, not direction-sensitive.

This test has a well-known limitation: in high-dimensional spaces, a random vector is almost certainly orthogonal to any specific direction ($\cos\theta \approx 0$). The noise gate therefore primarily tests whether *any* perturbation at this layer matters, not whether *this specific perturbation* matters. It catches the grossest artifacts but misses subtler ones.

### 4.3 Orthogonal Projection (Null-B)

A vector $\vec{o}$ is constructed orthogonal to $\vec{v}$ via Gram-Schmidt projection, then scaled to the same norm. If $\vec{o}$ performs comparably, the specific direction of $\vec{v}$ is not causally important — some broader property of the injection (e.g., norm, layer sensitivity) is doing the work.

### 4.4 Sign-Flip Test

The negated vector $-\vec{v}$ is evaluated through the same task battery. This is the most informative falsification test:

- If $+\vec{v}$ improves verification and $-\vec{v}$ degrades it → **strong evidence of a directed causal circuit**. The direction matters, not just the energy.
- If $-\vec{v}$ has no effect → the improvement may be an artifact of perturbation magnitude.
- If $-\vec{v}$ also improves performance → the discovery is an **energy artifact**, not a directional finding. Both pushing and pulling in this direction help, suggesting the model is sensitive to activation magnitude at this layer regardless of direction.

The sign-flip test results are logged for diagnostic analysis. In the current implementation, the noise gate (§4.2) serves as the primary rejection criterion — if a random vector of identical norm achieves ≥80% of the candidate's fitness, the genome is falsified and rejected from the elite set.

### 4.5 Shuffled-Component Test

A vector $\vec{s}$ is constructed by randomly permuting the elements of $\vec{v}$. This preserves the exact norm and element distribution but destroys all directional structure ($\cos(\vec{v}, \vec{s}) \approx 0$ in high dimensions). If $\vec{s}$ performs comparably, the effect is driven by the *magnitude distribution* of activations (e.g., a few large components dominating energy at certain dimensions) rather than the specific directional pattern.

This test complements the noise gate (§4.2): the noise gate tests whether *any* perturbation at this norm matters, while the shuffled test asks whether the *specific element magnitudes* matter (just not their arrangement). Together, they form a more complete null model.

### 4.6 Falsification as Scientific Methodology

The falsification battery reflects a deliberate methodological commitment: **any claimed circuit must survive attempts to disprove it**. This is unusual in machine learning, where the norm is to report positive results. Ignis treats every discovery as a hypothesis and subjects it to controlled experiments (noise, orthogonal, sign-flip, shuffled) before accepting it. The system is designed to produce *fewer, more reliable* discoveries rather than a large number of unvalidated candidates.

---

## 5. The Inception Protocol: Hot-Starting Evolution

### 5.1 The Cold Start Problem

Initializing CMA-ES with a random mean vector in $\mathbb{R}^{d_{model}}$ is equivalent to starting the search at a random point in a ~1000-dimensional space. Given the extreme sparsity of "useful" directions (likely a measure-zero set relative to the full space), random initialization would require an impractical number of generations to find the fitness basin.

### 5.2 PCA-Based Inception

The Inception Protocol provides an informed starting point by extracting contrastive activation deltas:

1. For each trap $t$ in the battery, two prompts are run: a "naive" prompt (likely to produce the wrong answer) and a "metacognitive" prompt (nudged toward self-correction).
2. The residual stream activations at the target layer are captured for both prompts.
3. The contrastive delta $\Delta_t = \vec{a}_{meta} - \vec{a}_{naive}$ captures the *direction the model moves when it self-corrects* on trap $t$.
4. The delta matrix $[\Delta_1, \Delta_2, \Delta_3]$ is centered and decomposed via SVD.
5. The first principal component (PC1) — the direction of maximum shared variance across all traps — becomes the inception seed.

### 5.3 Why PCA Instead of Averaging

Simple averaging ($\vec{s} = \frac{1}{n}\sum \Delta_t$) can cancel orthogonal signal. If one trap's metacognitive delta points along dimension 42 and another along dimension 789, the average points halfway between — a direction that may not be useful for either trap.

PCA identifies the axis of **maximum shared variance**: the direction along which all traps move most consistently when switching from naive to metacognitive reasoning. This is a more principled estimate of the shared verification direction.

The protocol also logs the **variance explained** by PC1. If PC1 captures $>80\%$ of variance, the traps share a strong common direction. If $<50\%$, the traps may probe distinct mechanisms — itself a scientifically interesting finding.

---

## 6. Manifold Geometry Instrumentation

### 6.1 What the Covariance Reveals

CMA-ES is not just an optimizer — it is implicitly a **geometry learner**. The covariance matrix $C$ learned during evolution encodes the local shape of the fitness landscape:

- **High-variance dimensions** correspond to directions where fitness is sensitive — these are the "active" dimensions of the verification circuit.
- **Low-variance dimensions** correspond to directions where perturbations have no effect — these can be projected out without losing the circuit.
- **The eigenvalue spectrum** of $C$ reveals the effective dimensionality of the circuit.

### 6.2 Logged Metrics

Three metrics are computed after each generation:

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Participation Ratio** | $PR = \frac{(\sum s_i)^2}{\sum s_i^2}$ | Effective dimensionality. $PR \approx 1$ = single line; $PR > 3$ = manifold |
| **Elite Cosine Similarity** | Mean pairwise $\cos(\vec{v}_i, \vec{v}_j)$ for top-$\mu$ | Convergence. $\rightarrow 1$ = elites agree; $\rightarrow 0$ = diverse |
| **Covariance Spectrum** | Top-5 eigenvalues of $C$ + max/min ratio | Search shape. High ratio = anisotropic (learned structure); low = isotropic (exploring) |

Together these answer the foundational question: **is CMA-ES converging on a single vector, a narrow ridge, or a high-dimensional manifold?** This directly informs the discrete-circuit vs. continuous-mode debate from §1.1.

---

## 7. Future Research Directions: Ranked by Anticipated Return on Investment

The following extensions are ordered by expected scientific and engineering return relative to implementation cost. Each is assessed on three axes: **effort** (engineering complexity), **impact** (expected scientific yield), and **risk** (probability of introducing instability or invalid results).

### 7.1 Recently Implemented Extensions

The following extensions, previously listed as future work, are now live in the pipeline (see §2, §3, §4 for technical details):

| Extension | Status | Implementation |
|-----------|--------|----------------|
| **Token Position Injection** | ✅ Live | `genome.py` (`position_ratio`), `tii_engine.py` (hook). See §2.2. |
| **Logit-Based Tier 2 Scoring** | ✅ Live | `fitness.py` (`_logit_tier2_score`). See §3.4. |
| **Anti-Sycophancy Trap** | ✅ Live | `fitness.py` (trap battery). See §3.2. |
| **Sign-Flip Falsification** | ✅ Live | `probe_runner.py` (test 4). See §4.4. |
| **Shuffled-Component Falsification** | ✅ Live | `probe_runner.py` (test 5). See §4.5. |
| **Random Direction Baseline** | ✅ Live | `seti_orchestrator.py` (`run_random_direction_baseline`). Evaluated at startup. |
| **Three-Tier Scoring (FLOOR/BASELINE/CREDIT)** | ✅ Live | `fitness.py`. See §3.3. |

The remaining extensions below represent future research directions, ordered by estimated ROI.

### 7.2 Cross-Model Inception PC1 Cosine Comparison (Medium ROI)

**Current limitation:** Four models run with independent CMA-ES state, generating inception seeds independently. The geometric relationship between these seeds is never analyzed — a missed opportunity for a cheap cross-scale signal.

**Proposed change:** After generating inception seeds for each model, compute and log the cosine similarity between PC1 directions across scales. Project to a shared basis (e.g., via the token embedding matrix) to make comparisons meaningful despite different $d_{model}$ dimensions.

| Dimension | Assessment |
|-----------|-----------|
| **Effort** | Low — pure logging/analysis; no changes to the search loop |
| **Impact** | Medium — provides early evidence for or against universal circuits, before CMA-ES even runs |
| **Risk** | Very low — read-only analysis |

**Pros:** This is the cheapest possible test of the universality hypothesis. High cosine similarity across scales would be strong preliminary evidence for shared verification geometry. The analysis can run once at pipeline startup.

**Cons:** The projection between different $d_{model}$ spaces is non-trivial. The embedding matrix provides one basis for projection, but it is not guaranteed to preserve the relevant geometry. Low cosine similarity could mean either "no universal circuit" or "bad projection method."

### 7.3 Evolved Layer Position (Medium ROI)

**Current limitation:** Layer targeting uses a fixed ratio (0.75 of model depth) with ±1 layer jitter. Reasoning circuits may peak at different depths for different tasks and model scales.

**Proposed change:** Widen the layer search range to $[0.3, 0.9]$ and make `layer_ratio` a first-class genome parameter that CMA-ES can optimize.

| Dimension | Assessment |
|-----------|-----------|
| **Effort** | Low — already have jitter infrastructure; widen range |
| **Impact** | Medium — if optimal layers vary significantly, this could unlock discoveries the fixed ratio misses |
| **Risk** | Low — worst case, CMA-ES converges back to 0.75 |

**Pros:** Near-zero implementation cost. The current fixed ratio is an assumption, not an empirical finding. CMA-ES is well-suited to optimizing over this continuous 1D parameter jointly with the vector.

**Cons:** Wider layer range may slow convergence — CMA-ES must now explore both *what to inject* and *where to inject it* simultaneously. The optimal layer may differ per model scale, fragmenting the search.

### 7.4 Manifold Genomes (Medium-High ROI, High Effort)

**Current limitation:** The genome encodes a single vector $\vec{v}$. But if the verification circuit occupies a low-dimensional manifold (3–20 directions), CMA-ES may repeatedly discover different projections of the same manifold, producing unstable results across runs.

**Proposed change:** Upgrade the genome to $(L, \vec{v}_1, \vec{v}_2, \ldots, \vec{v}_k, \vec{\alpha})$ and inject:

$$x_{steered} = x + \sum_{i=1}^{k} \alpha_i \vec{v}_i$$

| Dimension | Assessment |
|-----------|-----------|
| **Effort** | High — genome dimensionality increases $k$-fold; may require hierarchical CMA-ES |
| **Impact** | High — could capture the full manifold structure in a single genome |
| **Risk** | High — the curse of dimensionality; $k \times d_{model}$ parameters may overwhelm CMA-ES |

**Pros:** If verification is genuinely a manifold (not a line), single-vector search is fundamentally limited. Manifold genomes could discover the full basis of the verification subspace in one evolutionary run.

**Cons:** Even $k=3$ triples the search dimensionality. Diagonal CMA-ES may be insufficient — full CMA-ES or a hierarchical scheme (evolve $k$ and $\vec{\alpha}$ in an outer loop, vectors in an inner loop) may be required. The VRAM cost for storing $k$ vectors per candidate scales linearly.

### 7.5 Cross-Model Projection (Medium ROI, Medium Effort)

**Current limitation:** Discoveries at each model scale are independent. A vector discovered for Qwen 0.5B ($d=896$) is never tested on Qwen 1.5B ($d=1536$). Cross-scale transfer is the strongest possible evidence for universal circuits, but it requires a method to map between different-dimensional activation spaces.

**Proposed change:** Train a linear projection $W \in \mathbb{R}^{d_B \times d_A}$ that maps from Model A's activation space to Model B's, then evaluate whether projected vectors retain their steering effect.

| Dimension | Assessment |
|-----------|-----------|
| **Effort** | Medium — requires a small auxiliary optimization to learn $W$ |
| **Impact** | High — successful transfer would be the project's strongest empirical result |
| **Risk** | Medium — the projection may not preserve the relevant structure; negative results are ambiguous |

**Pros:** Positive transfer results would be publishable on their own. The linear projection can be learned from paired activations on the same prompts (cheap data).

**Cons:** Linear maps assume the relationship between activation spaces is approximately linear — a strong assumption. Failure to transfer could mean "no universal circuit" or "non-linear relationship between spaces."

### 7.6 Latent Cartography (High Impact, Medium Effort)

**Current limitation:** Ignis searches for the *best* steering vector. But the real scientific contribution may not be a single vector — it's the **map** of the cognitive subspace. What do different directions do? Is verification one-dimensional or multi-dimensional?

**Proposed change:** Post-hoc analysis pipeline:
1. Collect top 100 discovered vectors across all generations and models.
2. Apply PCA/SVD to extract basis directions of the "useful subspace."
3. Systematically inject along each basis direction and measure behavioral changes.
4. Produce a labeled map: Axis 1 → reasoning depth, Axis 2 → uncertainty monitoring, Axis 3 → exploration vs. certainty, etc.

| Dimension | Assessment |
|-----------|-----------|
| **Effort** | Medium — requires a post-hoc analysis module, not changes to the search loop |
| **Impact** | Very high — a labeled map of transformer cognition would be a major interpretability contribution |
| **Risk** | Medium — the "useful subspace" may not have interpretable axes |

**Pros:** This transforms Ignis from a circuit-discovery tool into a **cognitive cartography** platform. Even if no single universal circuit exists, mapping the geometry of the reasoning subspace is scientifically valuable.

**Cons:** Interpretability of PCA axes is not guaranteed. The axes may correspond to statistical regularities (e.g., "directions that change output length") rather than cognitive functions. Manual labeling requires extensive behavioral testing along each axis.

### 7.7 ROI Summary Table

| Rank | Extension | Effort | Impact | Risk | Status |
|------|-----------|--------|--------|------|--------|
| — | Token Position Injection | Low | High | Very Low | ✅ **Implemented** (§2.2) |
| — | Logit-Based Tier 2 Scoring | Low | High | Low | ✅ **Implemented** (§3.4) |
| — | Anti-Sycophancy Trap | Medium | High | Medium | ✅ **Implemented** (§3.2) |
| — | Sign-Flip + Shuffled Falsification | Low | High | Low | ✅ **Implemented** (§4.4, §4.5) |
| — | Random Direction Baseline | Low | Medium | Very Low | ✅ **Implemented** |
| 1 | Cross-Model PC1 Cosine | Low | Medium | Very Low | Proposed |
| 2 | Evolved Layer Position | Low | Medium | Low | Proposed |
| 3 | Manifold Genomes | High | High | High | Proposed |
| 4 | Cross-Model Projection | Medium | High | Medium | Proposed |
| 5 | Latent Cartography | Medium | Very High | Medium | Proposed |

The implemented extensions addressed the highest-ROI items identified by multiple expert reviews: continuous scoring signal, injection position flexibility, trap diversity, and falsification robustness. The remaining proposed extensions are more ambitious — manifold genomes and latent cartography could yield the project's most impactful results, but they require substantial engineering effort and carry non-trivial risk of instability.

---

## 8. Discussion

### 8.1 What Success Looks Like

Ignis is designed to produce one of three outcomes, all scientifically valuable:

1. **Discovery of a Universal Verification Circuit.** CMA-ES converges on a consistent direction across models, the falsification battery confirms directional causality, and the Participation Ratio is low ($PR \approx 1$–$3$). This would support the discrete-circuit hypothesis from §1.1(a) and provide a specific target for alignment research.

2. **Discovery of a Verification Manifold.** CMA-ES converges on a *subspace* rather than a direction ($PR > 5$), suggesting verification is a continuous mode with multiple contributing dimensions. This would support hypothesis §1.1(b) and motivate the Latent Cartography extension.

3. **Null Result with Informative Diagnostics.** CMA-ES fails to find consistent directions, the sign-flip test reveals energy artifacts, or the inception protocol shows low PC1 variance. A well-instrumented null result — equipped with participation ratios, cosine similarities, covariance spectra, and falsification logs — is far more informative than a poorly-instrumented positive result. It narrows the hypothesis space for future work.

### 8.2 Methodological Limitations

Several known limitations should be stated explicitly:

1. **Single model family.** All experiments use the Qwen 2.5 family. Circuits discovered may be specific to Qwen's training data or architecture rather than universal properties of transformers.

2. **Marker-based scoring.** Despite the three-tier system and the logit-based Tier 2 supplement (§3.4), fitness evaluation still relies heavily on string matching. Models that reason correctly but use unexpected phrasing are penalized in the marker tier. The logit tier mitigates this by providing continuous probability signal, but covers only traps with configured forced-choice variants.

3. **Diagonal CMA-ES.** The diagonal covariance restriction prevents the optimizer from learning inter-dimension correlations. If the verification circuit lies along a diagonal direction in activation space (correlated across dimensions), diagonal CMA-ES will be slow to find it.

4. **Position exploration coverage.** Token Position Injection (§2.2) enables steering at any point in the prompt trajectory, but the current stochastic exploration (20% of candidates) provides sparse coverage. The optimal injection position may be prompt-dependent, adding noise to fitness evaluation.

5. **Causal scope.** The falsification battery tests whether a vector is *causally effective* — injecting it changes behavior. It does not test whether the vector corresponds to a *naturally occurring* computation. The evolved direction might be an "artificial bypass" that achieves the right answer through a mechanism the model never uses natively.

### 8.3 Relationship to Existing Work

Ignis occupies a unique position relative to existing interpretability methods:

- **Contrastive Activation Addition (CAA)**: CAA computes steering vectors from paired examples. Ignis's inception protocol does something similar to initialize search, but then *evolves beyond the initial estimate* using CMA-ES. CAA finds local contrastive directions; Ignis searches for global optima.
- **Sparse Autoencoders (SAEs)**: SAEs decompose activations into interpretable features. Ignis's Latent Cartography extension (§7.6) would produce similar output — a labeled set of cognitive dimensions — but derived from behavioral optimization rather than unsupervised decomposition.
- **Activation Patching**: Patching tests specific causal hypotheses. Ignis's falsification battery serves a similar purpose, but operates on *evolved* interventions rather than *observed* activations.

The key distinguishing feature is the evolutionary search: Ignis does not assume the researcher knows what to look for. It searches for behavioral effects and then characterizes what it finds.

---

## 9. Conclusion

Ignis represents a methodological bet: that evolutionary search in continuous activation space can discover neural structures that supervised methods cannot. The framework is designed not to confirm a specific hypothesis but to **discriminate between hypotheses** — discrete circuit vs. continuous manifold, universal mechanism vs. scale-specific artifact, causal direction vs. energy perturbation.

The system's value lies in its instrumentation as much as its discoveries. Every generation produces geometry metrics (participation ratio, elite cosine similarity, covariance spectrum), every candidate above baseline undergoes causal falsification (noise, orthogonal, sign-flip, shuffled-component), and every model rotation provides an independent test of cross-scale invariance. This means that even negative results are informative — they tell us where verification circuits *are not*, narrowing the search space for future work.

The research roadmap (§7) prioritizes extensions that add *information* over extensions that add *complexity*. Token position injection, logit-based scoring, and anti-sycophancy traps cost little to implement but fundamentally expand the kinds of circuits the system can discover and the kinds of artifacts it can detect. Manifold genomes and latent cartography are more ambitious — they could transform the project from circuit discovery into cognitive mapping — but they require the foundational pipeline to be validated first.

The central question — whether self-correction in transformers is a circuit or a mode, a direction or a manifold, a universal mechanism or a family of specialized heuristics — remains open. Ignis is designed to close it.

---

## References

1. Hansen, N. (2016). The CMA Evolution Strategy: A Tutorial. *arXiv:1604.00772*.
2. Turner, A. et al. (2023). Activation Addition: Steering Language Models Without Optimization. *arXiv:2308.10248*.
3. Nanda, N. et al. (2022). TransformerLens. *GitHub repository*.
4. Conmy, A. et al. (2023). Towards Automated Circuit Discovery for Mechanistic Interpretability. *NeurIPS 2023*.
5. Bricken, T. et al. (2023). Towards Monosemanticity: Decomposing Language Models With Dictionary Learning. *Anthropic Research*.
6. Li, K. et al. (2024). Inference-Time Intervention: Eliciting Truthful Answers from a Language Model. *NeurIPS 2024*.

---

*This paper describes the methodology and intent of an active research project. No empirical results are reported. The pipeline is under development; all claims about expected outcomes are hypotheses, not findings.*