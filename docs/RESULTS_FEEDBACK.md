

[GEMINI]
This is an exceptionally rigorous and well-structured experimental report. You have successfully operationalized a highly theoretical concept (the Reasoning Precipitation Hypothesis) into a concrete, testable pipeline, and your willingness to aggressively document a null result—that evolutionary search predominantly discovers bypass circuits at these scales—is exactly what makes for a high-impact mechanistic interpretability paper.

Here are a few strategic adjustments and structural refinements to consider before finalizing this document or moving toward publication:

### 1. Separate the Scale Gradient from the Architecture Ablation
Currently, the Qwen3-4B model is listed inline with the Qwen 2.5 models in your run results and RPH proxy tables. 
* **The Issue:** You rightly note that Qwen 3 has a different architecture, which broke the cosine-fitness trend and resulted in negative stepwise mutual information (MI_step). Keeping it in the same linear gradient visually muddies the clean scaling narrative of the Qwen 2.5 family.
* **The Fix:** Split the results. Frame Qwen 2.5 (0.5B, 1.5B, 3B) as the primary "Scale Gradient" experiment. Frame Qwen3-4B as a separate "Cross-Architecture Transfer" or "Ablation" experiment to prove that the bypass phenomenon isn't just a quirk of the Qwen 2.5 manifold.

### 2. Prioritize the 1.5B Δ_proj Computation
The missing Δ_proj (Projection Differential) metric leaves a critical narrative loop open. 
* **The Gap:** You report a WEAK_SIGNAL at the 1.5B scale because the 95% confidence interval for MI_step cleanly excludes zero. However, Δ_proj is marked as uncomputed across the board. 
* **The Urgency:** Because 1.5B is the *only* model showing any sign of multi-step reasoning, calculating its Δ_proj is the most important immediate task. If it passes, 1.5B upgrades to a PRECIPITATION_CANDIDATE, fundamentally changing the paper's conclusion from a pure null result to a localized existence proof. 

### 3. Reframe the 7B Blocker
Your hypothesis explicitly rests on the idea that native circuit amplification requires *sufficient model scale*. 
* **The Tension:** You are currently blocked on the 7B model due to Out-Of-Memory errors on your 16GB GPU. Stopping at 3B (or 4B) weakens the claim that the hypothesis is falsified, as 7B is often the threshold where more complex reasoning basins solidify.
* **The Fix:** In Section 6.1, instead of just stating it needs a cloud A100, briefly mention if aggressive gradient checkpointing, quantized base models (if compatible with the residual stream hooks), or CPU offloading have been exhausted. This assures the reader that the 16GB VRAM limit is a hard physical boundary for this specific high-fidelity white-box intervention, justifying the pause.

### 4. Clarify the Falsification Implication
You report a 35% pass rate for causal falsification, noting that the vectors are fragile and their performance degrades under noise or shuffle as much as under sign-flip. 
* **The Refinement:** It would be helpful to explicitly connect this fragility back to the "bypass" mechanism. Does the bypass route require absolute precision to avoid catastrophic collapse into gibberish, whereas a true reasoning precipitation vector (if found) might exhibit the "wider peak" you theorized? Adding a sentence linking the 35% pass rate to the geometry of the bypass basin would tighten Section 5.1.

This is the exact right next move. If we can prove that the 1.5B vector natively projects more strongly onto self-correction states than heuristic bypass states, that `WEAK_SIGNAL` becomes a documented `PRECIPITATION_CANDIDATE`. 

To do this efficiently within a 16GB VRAM envelope, we need to avoid caching the entire forward pass. For the 1.5B model, we only care about Layer 21. We can also leverage the Prometheus measurement backbone to handle the state classification (Self-Correction vs. Heuristic Bypass) offline, so the forward pass is purely focused on tensor extraction.

Here is the implementation logic and the `TransformerLens` code to compute $\Delta_{proj}$.

### 1. The Mathematical Definition

We define $\Delta_{proj}$ as the difference in the expected projection of the candidate steering vector $v$ onto the natural residual stream $h$ between two distinct cognitive states:

$$\Delta_{proj} = \mathbb{E}[ \cos(h_{SC}, v) ] - \mathbb{E}[ \cos(h_{HB}, v) ]$$

Where:
* **$h_{SC}$ (Self-Correction):** Residual stream activations at Layer 21 during tokens where the model is actively verifying or correcting a logical trap.
* **$h_{HB}$ (Heuristic Bypass):** Residual stream activations at Layer 21 during tokens where the model correctly answers the trap, but does so via a shallow heuristic (no internal reasoning trace).

If $\Delta_{proj} > 0$ with statistical significance, the vector is native to the reasoning basin, not the bypass basin.

### 2. The Implementation Strategy

1.  **Dataset Preparation:** Use a curated set of your adversarial traps (e.g., Density Illusion, Anti-Sycophancy).
2.  **Unsteered Generation & Caching:** Run the model *without* the steering vector. Use a strict `names_filter` in `TransformerLens` to only cache `blocks.21.hook_resid_pre`.
3.  **Prometheus Classification:** Pass the generated texts through the Prometheus dual-classifier to label the trajectories as `SC` (Reasoning/Self-Correction), `HB` (Heuristic Bypass), or `FAIL`.
4.  **Token-Level Alignment:** Map the `SC` and `HB` labels back to the specific token positions in the cached activations.
5.  **Projection & Differential:** Calculate the cosine similarities and compute the $\Delta_{proj}$ metric.

### 3. The `TransformerLens` Logic

Here is the core extraction and computation script, optimized for local VRAM hygiene:

```python
import torch
import torch.nn.functional as F
from transformer_lens import HookedTransformer

# 1. Initialize Model and Vector
# Qwen 2.5-1.5B-Instruct fits comfortably in 16GB VRAM if we don't cache everything
model = HookedTransformer.from_pretrained("qwen2.5-1.5b-instruct", device="cuda", fold_ln=False)
candidate_vector = torch.load("results/ignis/archives/run_2026-03-22_000632/best_genome.pt")["vector"].to("cuda")

TARGET_LAYER = 21
HOOK_NAME = f"blocks.{TARGET_LAYER}.hook_resid_pre"

def get_activation_projections(prompts, vector, hook_name):
    """
    Runs unsteered inference, caches only the target layer, 
    and returns token-wise cosine similarities.
    """
    projections = []
    
    with torch.no_grad():
        for prompt in prompts:
            # Tokenize
            tokens = model.to_tokens(prompt)
            
            # Run with strict cache filtering to prevent OOM
            _, cache = model.run_with_cache(
                tokens,
                names_filter=lambda name: name == hook_name,
                return_type=None # We only want the cache, not the logits
            )
            
            # Extract residual stream at target layer: Shape [batch=1, seq_len, d_model]
            resid_stream = cache[hook_name][0] 
            
            # Compute token-wise cosine similarity with the candidate vector
            # resid_stream: [seq_len, d_model], vector: [d_model]
            cos_sims = F.cosine_similarity(resid_stream, vector.unsqueeze(0), dim=-1)
            
            projections.append({
                "prompt": prompt,
                "cos_sims": cos_sims.cpu().tolist(),
                "seq_len": tokens.shape[1]
            })
            
            # VRAM Hygiene: explicitly clear cache and force garbage collection
            del cache
            torch.cuda.empty_cache()
            
    return projections

# --- Pseudocode for the Delta_proj Calculation ---

# 1. Gather your projections
# raw_data = get_activation_projections(trap_prompts, candidate_vector, HOOK_NAME)

# 2. Run your Prometheus pipeline offline to classify the text outputs
# classified_data = run_prometheus_classifier(raw_data) 

# 3. Compute the differential
# sc_projections = [val for item in classified_data if item['class'] == 'SC' for val in item['cos_sims'][critical_window:]]
# hb_projections = [val for item in classified_data if item['class'] == 'HB' for val in item['cos_sims'][critical_window:]]
#
# expected_sc = sum(sc_projections) / len(sc_projections)
# expected_hb = sum(hb_projections) / len(hb_projections)
#
# delta_proj = expected_sc - expected_hb
```

### 4. The Critical Window

Notice the `critical_window` slice in the pseudocode. You don't want to average the projection across the *entire* prompt, because the early tokens (reading the prompt) will wash out the signal. You only want to calculate the projection during the actual generation phase, specifically the tokens where the model is making its "decision." 

Would you like to write a quick utility function to automatically isolate that `critical_window` (e.g., the span of tokens between the end of the prompt and the final logical conclusion), or would you prefer to start running the extraction hook on the 1.5B anomaly right away?

[Claude]

This is excellent experimental work. Honest, clean, well-structured results. Let me give you my assessment.

**The headline: your data is telling you something real, and it's not what the RPH predicted — but it might be more interesting.**

Here's what I'd recommend:

**1. The 1.5B anomaly deserves more attention before you move on.**

The non-monotonic MI_step pattern (absent → present → absent → negative) is the most puzzling and potentially informative result in the entire dataset. Before chalking it up to noise, I'd want to see replication with more prompt pairs. You have 9 counterfactual pairs — that's a thin sample for a metric that barely clears threshold. If it replicates with 30-50 pairs, you have a genuine architectural sweet spot finding. If it doesn't, you can close it cleanly. This is cheap to run since you already have the vector archived.

**2. Compute Δ_proj before calling the 1.5B result final.**

You have one metric passing at 1.5B and the third criterion uncomputed. If Δ_proj comes back positive, you have a PRECIPITATION_CANDIDATE — your first one. If it's null, you have a clean three-metric null at every scale. Either outcome sharpens the conclusion significantly. Leaving it uncomputed is the one gap that a reviewer would flag immediately.

**3. The cos_r trend in Qwen 2.5 is more interesting than the magnitudes suggest.**

The monotonic drift from -0.032 → -0.007 → +0.037 across 0.5B/1.5B/3B is tiny in absolute terms but it *is* a sign change. The Qwen 3-4B point breaks the trend, but that's a different architecture — you should plot and report the within-architecture trend separately. The question isn't whether the 3B value is significant (it isn't). The question is whether extending the Qwen 2.5 series to 7B and 14B would show that trend continuing. If cos_r hits +0.1 or +0.15 at 7B, the RPH might activate at a scale you just haven't reached yet. This is your strongest argument for the A100 run.

**4. Reframe the paper around the bypass finding, not the precipitation null.**

You've been treating the null as a negative result for the RPH. Flip it. You have a clean, well-controlled demonstration that evolutionary search over steering vectors *consistently discovers bypass circuits across four model scales and two architectures*. That's a positive finding about the structure of transformer computation. The framing becomes: "We tested whether evolutionary search discovers native reasoning amplification. It does not. Instead, it discovers bypass routes that are orthogonal to native computation, directionally specific (35% falsification pass rate), and architecture-general. This constrains the hypothesis space for activation steering and has implications for interpretability."

The RPH becomes the theoretical motivation for the experiment, not the thing you failed to prove.

**5. The PC1 trend (41% → 54%) is an underappreciated finding.**

PC1 variance increasing monotonically with scale means the contrastive inception signal is getting *more consolidated* in larger models. The models have a more dominant shared axis along which reasoning-relevant computation organizes. Combined with the cos_r trend, this suggests that native reasoning structure *does* become more geometrically organized at scale — it's just that CMA-ES can't find it because bypass is always the easier optimization target. This supports a modified hypothesis: native reasoning geometry exists and sharpens with scale, but evolutionary search is the wrong discovery method because bypass dominates the fitness landscape.

**6. The 35% falsification rate needs context.**

65% of your high-fitness vectors fail causal controls. That's important to report prominently because it quantifies how much of the "reasoning improvement" from steering vectors is fragile or non-directional. Many published steering results don't run this kind of falsification battery. Your falsification infrastructure is a methodological contribution independent of the RPH.

**7. Adjust your next priorities.**

I'd rank them:

- **Immediate:** Replicate 1.5B MI_step with 30+ prompt pairs (hours, not days — vector already archived)
- **Immediate:** Compute Δ_proj at 1.5B to close out the classification
- **High priority:** SAE decomposition of all four best_genome.pt vectors — "what is the bypass doing mechanistically" is a compelling paper section regardless of RPH outcome
- **High priority:** Get the 7B Qwen 2.5 run on an A100 — the cos_r and PC1 trends demand one more within-architecture data point
- **Defer:** MAP-Elites — this is the right next step for discovery, but the current results need to be fully characterized first

**8. One metric threshold adjustment.**

Your Δ_cf pass criterion is p < 0.05 with Cohen's d > 0.5. The Qwen3-4B result is p = 0.095 with a real uplift pattern (steered Δ_cf of 0.216 vs. base of 0.141). With only 9 prompt pairs, you're underpowered for this test. Before concluding Δ_cf fails everywhere, run the expanded prompt set. You might find that the 4B result passes with adequate sample size and the current "fail" is a power problem, not an effect-size problem.


[Gigachad GPT]

This is strong work—and importantly, your null result is *clean*. That’s rare. What you have now is already close to a publishable “negative result with structure,” but there are a few **high-leverage adjustments** that could either:

* convert this into a **positive detection**, or
* make the null result **decisively constraining for the field**

Below is a prioritized, technically specific audit.

---

# **1. The Most Important Issue: Your Search Objective Is Misaligned**

### Observation from your results

* CMA-ES converges tightly (σ ≈ 0.024, cosine ≈ 0.9 to seed)
* Fitness improves (≥1.0)
* **All vectors are bypass (cos ≈ 0)** 

### Interpretation

You are optimizing:

> *task performance under adversarial traps*

But your hypothesis requires:

> *alignment with endogenous reasoning trajectories*

These are **not the same objective**.

---

## **Concrete Fix: Add Native Alignment to Fitness**

Right now:

```text
F = task performance (traps)
```

Upgrade to:

```text
F = task_performance × alignment_bonus
```

Where:

[
\text{alignment_bonus} = \sigma(k \cdot \cos(v, r_{natural}))
]

* `k ≈ 5–10` (sharpens discrimination)
* Use *mid-layer residuals during correct reasoning traces* (not generic residuals)

---

### Why this matters

Without this:

* Evolution will *always* find bypass shortcuts first
* Native circuits are **harder to access** → lower fitness early
* CMA-ES never explores that region

You are effectively solving:

> “Find the easiest way to get correct answers”

not:

> “Find vectors that move the model into reasoning manifolds”

---

# **2. Your “Ghost Trap” Threshold Is Likely Too Crude**

You currently classify:

* cos > 0.3 → native
* cos ≤ 0.3 → bypass 

---

## Problem

Cosine with *raw residual stream* is a weak proxy for:

> alignment with reasoning computation

Because:

* Residual stream = mixture of many features
* Reasoning is likely a **low-dimensional subspace**, not full vector alignment

---

## Fix: Replace with **Subspace Projection Test**

Instead of:

```text
cos(v, residual)
```

Compute:

[
| P_{\mathcal{R}}(v) |
]

Where:

* ( \mathcal{R} ) = subspace spanned by:

  * residuals during *verified reasoning trajectories*
  * or SAE features correlated with MI_step

---

### Practical implementation

1. Collect hidden states for:

   * correct multi-step reasoning traces
2. Do PCA → take top-k (k ≈ 10–50)
3. Define projector:

```python
R = torch.stack(top_k_vectors)  # [k, d]
P = R.T @ torch.linalg.pinv(R @ R.T) @ R
alignment = torch.norm(P @ v) / torch.norm(v)
```

---

### Expected effect

You may find:

* many “bypass” vectors are actually **partially aligned**
* your 0% native rate is an artifact of measurement

---

# **3. You Are Likely Injecting at the Wrong Regime**

### Your setup

* Injection at ~0.75 depth consistently 

---

## Problem

That strongly biases toward:

> *late-stage logit steering / heuristic override*

i.e., **bypass by construction**

---

## Fix: Multi-layer injection strategy

Test three regimes explicitly:

| Regime | Layers  | Expected effect                      |
| ------ | ------- | ------------------------------------ |
| Early  | 0.2–0.4 | trajectory initialization            |
| Mid    | 0.4–0.7 | **precipitation zone (most likely)** |
| Late   | 0.7–0.9 | output steering (bypass)             |

---

### Key experiment

Run identical genomes with injection at:

```python
layers = [int(0.3L), int(0.5L), int(0.7L)]
```

Track:

* Δ_cf
* MI_step
* alignment

---

### Prediction

If RPH is true:

* **mid-layer injection should dominate**
* late-layer = bypass (what you're seeing)
* early-layer = weak / unstable

---

# **4. Your Proxy Stack Is Missing the Most Important One**

You already noted:

> Δ_proj not yet computed 

This is not optional—it is **central**.

---

## Why Δ_proj matters

Right now you cannot distinguish:

| Case               | Δ_cf | MI_step  | Interpretation     |
| ------------------ | ---- | -------- | ------------------ |
| Bypass + structure | high | moderate | what you're seeing |
| True precipitation | high | high     | target             |

Δ_proj tells you:

> does the vector activate *self-correction states* vs heuristic states?

---

## Strong recommendation

Implement Δ_proj **before scaling further**.

Otherwise:

* you may already have weak precipitation signals
* but are classifying them as null

---

# **5. The 1.5B “Anomaly” Is More Important Than It Looks**

From your results:

* Only scale with MI_step > 0 (CI excludes zero) 
* Non-monotonic pattern

---

## This is exactly what a phase transition looks like

Not:

> smooth scaling

But:

> narrow regime where:
>
> * capacity sufficient for reasoning
> * but not yet dominated by RLHF / compression

---

## Actionable follow-up

At 1.5B:

1. Increase prompt pairs (9 → 50+)
2. Re-run CMA-ES with:

   * alignment-augmented fitness
3. Sweep layers around 21:

   * [18, 21, 24]

---

### Hypothesis

You may find:

> a **thin precipitation band** in (layer, scale) space

---

# **6. Your Falsification Results Reveal Something Subtle**

* 35% pass rate
* effects degrade under noise/shuffle 

---

## Interpretation

Current vectors are:

> **fragile control policies**, not stable dynamical shifts

This strongly supports your conclusion:

> these are not true trajectory transitions

---

## But also suggests

You should explicitly measure:

### **Stability under rollout length**

Test:

* short generation (≤20 tokens)
* long generation (≥100 tokens)

---

### Prediction

* Bypass vectors degrade quickly
* Precipitation vectors (if found) should persist

---

# **7. The Most Important Missing Experiment**

## Cross-prompt generalization

Right now:

* vectors optimized on fixed trap set

You need:

### Train / Test split

* Train on traps A
* Evaluate on traps B

---

### Expected outcomes

| Result           | Interpretation                             |
| ---------------- | ------------------------------------------ |
| No transfer      | heuristic bypass                           |
| Partial transfer | structured policy                          |
| Strong transfer  | **trajectory-level effect (supports RPH)** |

---

# **8. What I Would Do Next (Ordered Plan)**

## Phase 1 (Immediate, high ROI)

1. Add alignment term to fitness
2. Replace cosine ghost trap with subspace projection
3. Run multi-layer injection sweep

---

## Phase 2 (Disambiguation)

4. Implement Δ_proj
5. Expand 1.5B run (more prompts + seeds)
6. Add train/test trap split

---

## Phase 3 (Decisive)

7. MAP-Elites with:

   * axis 1: performance
   * axis 2: alignment
   * axis 3: MI_step

This directly tests:

> does a *manifold* of reasoning-aligned vectors exist?

---

# **9. Bottom Line**

Your current result:

> “We can reliably find high-performing steering vectors, but they are uniformly bypass.”

is **real and important**.

But the deeper diagnosis is:

> **Your search process is structurally biased toward bypass solutions.**

Once you correct that, one of two things will happen:

---

## Outcome A (most interesting)

You discover:

* rare, lower-fitness but aligned vectors
* stronger MI_step + Δ_proj
* possible phase transition at specific layers

→ **First real evidence for precipitation**

---

## Outcome B (also valuable)

Even with alignment-aware search:

* still no native vectors

→ strong falsification of RPH up to 4B scale


Below is a **drop-in upgrade** to your pipeline covering all three requests:

1. **Alignment-aware fitness (CMA-ES / MAP-Elites ready)**
2. **Exact Δ_proj implementation (SC vs HB projection differential)**
3. **A minimal decisive experiment (single run, publishable outcome)**

Everything is written to integrate with your existing TL + Ignis setup.

---

# **1. Alignment-Aware Fitness (Core Fix)**

## **Key Idea**

You want to optimize:

[
F(g) = \text{task_score} \times \text{coherence} \times \text{alignment}
]

Where alignment is **projection into a reasoning subspace**, not raw cosine.

---

## **1.1 Build Reasoning Subspace (one-time precompute)**

```python
# --------------------------------------------------
# Build reasoning subspace R from clean reasoning traces
# --------------------------------------------------

def build_reasoning_subspace(model, prompts, layer, k=32):
    """
    Extract top-k PCA components from residuals during verified reasoning traces.
    """
    activations = []

    for prompt in prompts:
        _, cache = model.run_with_cache(prompt)
        resid = cache[f'blocks.{layer}.hook_resid_pre']  # [batch, seq, d_model]
        
        # Take final token or mean over reasoning span
        h = resid[:, -1, :]  # [batch, d_model]
        activations.append(h)

    H = torch.cat(activations, dim=0)  # [N, d_model]
    
    # PCA via SVD
    U, S, Vt = torch.linalg.svd(H - H.mean(0), full_matrices=False)
    R = Vt[:k]  # [k, d_model]
    
    return R  # reasoning basis
```

---

## **1.2 Projection-Based Alignment Score**

```python
def alignment_score(v, R):
    """
    Compute fraction of vector energy inside reasoning subspace.
    """
    # Project v onto subspace R
    proj = R.T @ (R @ v)
    return torch.norm(proj) / torch.norm(v)
```

---

## **1.3 Updated Fitness Function**

Replace your current fitness with:

```python
def fitness_fn(task_score, perplexity, v, R, beta=2.0):
    """
    Alignment-aware fitness.
    """
    # Coherence (same as before)
    mu, sigma = 12, 3
    C = np.exp(-(np.log(perplexity)-mu)**2 / (2*sigma**2))
    
    # Alignment term (sharp sigmoid)
    align = alignment_score(v, R).item()
    A = 1 / (1 + np.exp(-beta * (align - 0.2)))  # threshold around 0.2
    
    return task_score * C * A
```

---

## **1.4 Optional: MAP-Elites Axes Upgrade**

Replace archive dimensions with:

* Axis 1: task_score
* Axis 2: alignment_score
* Axis 3: MI_step

This directly maps the **reasoning manifold**.

---

# **2. Exact Δ_proj Implementation**

## **Goal**

Distinguish whether vector activates:

* **SC (Self-Correction)** states
* **HB (Heuristic Bypass)** states

---

## **2.1 Define SC vs HB States**

You already have traps. Use them to label states:

* **SC state:**

  * incorrect intermediate → corrected final
* **HB state:**

  * correct final, no intermediate correction
  * or shortcut answer without reasoning steps

---

## **2.2 Collect State Residuals**

```python
def collect_states(model, prompts, layer):
    SC_states = []
    HB_states = []

    for prompt in prompts:
        output, cache = model.run_with_cache(prompt, return_type="logits")
        
        resid = cache[f'blocks.{layer}.hook_resid_pre']  # [batch, seq, d]
        
        # You must implement:
        # detect_self_correction(prompt, output)
        # detect_bypass(prompt, output)
        
        if detect_self_correction(prompt, output):
            SC_states.append(resid[:, -1, :])
        elif detect_bypass(prompt, output):
            HB_states.append(resid[:, -1, :])

    SC = torch.cat(SC_states, dim=0)
    HB = torch.cat(HB_states, dim=0)

    return SC, HB
```

---

## **2.3 Build Projectors**

```python
def build_projector(X, k=16):
    """
    PCA projector for a state set.
    """
    U, S, Vt = torch.linalg.svd(X - X.mean(0), full_matrices=False)
    basis = Vt[:k]  # [k, d]
    return basis
```

---

## **2.4 Compute Δ_proj**

```python
def delta_proj(v, R_sc, R_hb):
    """
    Projection differential between SC and HB subspaces.
    """
    def proj_energy(v, R):
        proj = R.T @ (R @ v)
        return torch.norm(proj) / torch.norm(v)
    
    sc = proj_energy(v, R_sc)
    hb = proj_energy(v, R_hb)
    
    return (sc - hb).item()
```

---

## **2.5 Interpretation Thresholds**

| Δ_proj         | Interpretation                                    |
| -------------- | ------------------------------------------------- |
| > +0.15        | Strong SC alignment → **precipitation candidate** |
| [-0.05, +0.15] | Mixed / ambiguous                                 |
| < -0.05        | HB-dominant → **bypass**                          |

---

# **3. Minimal Decisive Experiment (One-Run Test)**

This is the **highest ROI design** you can run immediately.

---

## **3.1 Setup**

* Model: **Qwen 2.5 1.5B (layer 21)** ← your only weak signal

* Prompts:

  * 50 train (for CMA-ES)
  * 50 test (held-out)

* Layers tested:

```python
layers = [18, 21, 24]
```

---

## **3.2 Conditions**

Run **two searches in parallel**:

### (A) Baseline CMA-ES

* fitness = task only

### (B) Alignment-Aware CMA-ES

* fitness = task × alignment

---

## **3.3 Evaluate Top 10 Vectors Per Condition**

Compute:

* Δ_cf
* MI_step
* Δ_proj
* generalization (train → test)

---

## **3.4 Decision Table**

| Outcome                          | Interpretation                                |
| -------------------------------- | --------------------------------------------- |
| Both A & B → low Δ_proj          | RPH likely false at this scale                |
| A low, B high Δ_proj             | **search bias was the issue → RPH supported** |
| B produces high Δ_proj + MI_step | **precipitation detected**                    |
| High train, low test             | bypass / overfit                              |
| Mid-layer > others               | confirms separatrix hypothesis                |

---

## **3.5 Single Critical Plot (Paper-Ready)**

Plot:

```text
x-axis: alignment_score
y-axis: task_score
color: Δ_proj
```

Expected:

* Bypass cluster → high task, low alignment, low Δ_proj
* Precipitation cluster → moderate task, high alignment, high Δ_proj

---

# **4. What Positive Findings Would Look Like**

You should expect something like:

| Metric         | Bypass   | Precipitation  |
| -------------- | -------- | -------------- |
| Task score     | High     | Moderate–High  |
| Alignment      | Low      | **High**       |
| MI_step        | Low–Mid  | **High**       |
| Δ_proj         | Negative | **Positive**   |
| Generalization | Weak     | **Strong**     |
| Stability      | Fragile  | **Persistent** |

---

# **5. Key Insight**

Right now your system is solving:

> “Find vectors that produce correct answers”

After this modification, it becomes:

> “Find vectors that move the model into reasoning dynamics”

That is the actual hypothesis test.

---

# **If You Want Next**

I can extend this into:

* **SAE-mediated Δ_proj (feature-level causal attribution)**
* **Full MAP-Elites implementation with GPU batching (EvoTorch-style)**
* **NeurIPS-ready Results + Figures auto-generation (matplotlib exact specs)**

At this point, one well-run experiment with these changes could **decisively resolve your hypothesis at ≤2B scale**.


