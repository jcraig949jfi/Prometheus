
[TITAN:  CHATGPT]

You’re not holding a “destabilizer.”
You’re holding a **nullspace actuator**—and your current interpretation is one level off.

I’m going to do exactly what you asked: tear it down, rebuild it tighter, and give you one decisive experiment.

---

# 🔴 First: What You’re Seeing (Reframed Precisely)

Let’s restate your strongest constraints:

* **v ⟂ (correct − incorrect)**
* **v ⟂ CoT (mostly)**
* **v points away from BOTH centroids**
* **v has strong, specific causal effects (DAS 10–15x)**
* **v sometimes improves performance**
* **v barely changes KL**
* **v only “works” near decision boundaries**

---

## ❗ Your current interpretation:

> “destabilizing attractor basins”

This is close—but misleading in one key way:

It assumes:

> the model is *sitting in an attractor basin* and you push it out

---

## 🔥 The sharper interpretation:

> **You are perturbing the model *within a high-dimensional equivalence class* of representations that preserve logits to first order.**

Not destabilizing.

**Sliding along a locally flat manifold.**

---

# 🧠 The Missing Concept: Logit-Nullspace Geometry

At layer L31, the mapping to logits is approximately:

```text
logits ≈ W_U · h_L + downstream_processing
```

There exists a subspace:

```text
N = { v | W_eff · v ≈ 0 }
```

Where:

* `W_eff` = effective linearization of downstream computation

---

## Your vector lives in (or near):

> **the nullspace of the output mapping**

---

### That explains ALL FIVE anomalies cleanly:

---

## 1. Orthogonal to reasoning axis

Because:

```text
(correct − incorrect) ∈ rowspace(W_eff)
v ∈ nullspace(W_eff)
```

→ dot ≈ 0 by construction

---

## 2. Pushes away from both centroids

Because:

* centroids lie in **data manifold**
* your vector lies **off-manifold**

→ negative cosine to both

---

## 3. KL ≈ 0

Because:

```text
W_eff · v ≈ 0
```

→ logits barely change
→ distribution unchanged

---

## 4. Still affects behavior (sometimes)

Because:

> downstream computation is **nonlinear**

So even if:

```text
first-order effect ≈ 0
```

you get:

```text
second-order / interaction effects ≠ 0
```

---

## 5. Overtake Race “precipitation”

This is the key:

> that prompt sits near a **curvature-sensitive region**

So:

* nullspace perturbation
* interacts with nonlinear layers (32–35)
* produces real effect

---

# ❗ This is NOT destabilization

Your model is not:

* leaving an attractor basin

It is:

* being **nudged along directions invisible to the readout**
* until nonlinearities make them visible

---

# 🧠 Better Name Than “Destabilization”

Call it:

> **Second-Order Steering via Logit-Nullspace Directions**

or shorter:

> **Nullspace Steering**

---

# 🔥 Q1 — Is this known?

Pieces exist, but **your exact combination is not cleanly articulated in the literature**:

* Adversarial examples → nullspace-ish perturbations
* Mechanistic interp → mostly rowspace-aligned features
* Circuit breakers → explicit rerouting

What you have is:

> **evolution discovering nullspace directions that maximize second-order behavioral sensitivity**

That’s not a standard framing.

---

# 🔥 Q2 — Destabilization vs Precipitation

Now we can answer this properly.

---

## Formalization attempt

Let:

```text
h' = h + εv
```

Output:

```text
y = f(h)
```

Expand:

```text
f(h + εv) ≈ f(h) + εJv + ½ ε² vᵀHv + ...
```

Where:

* J = Jacobian
* H = Hessian

---

## In your case:

* **Jv ≈ 0** (nullspace)
* effect comes from:

```text
½ ε² vᵀHv
```

---

## Interpretation

* “Destabilization” = moving into region where **H matters**
* “Precipitation” = when **vᵀHv crosses decision boundary**

---

### So:

> **Precipitation = curvature-driven sign flip in output**

---

### That’s your answer to Q2:

You don’t need attractor basins.

You need:

> **regions of high second-order sensitivity**

---

# 🔥 Q3 — Should you evolve for CoT alignment?

No—not yet.

Because:

* CoT lives in **rowspace directions (first-order)**
* your vector lives in **nullspace (second-order)**

---

### Combining them naively:

```text
v_total = v_CoT + v_null
```

→ will likely destroy the nullspace property

---

### If you want to explore this:

You need:

> **constrained optimization**

Force:

```text
W_eff · v ≈ 0
```

while maximizing CoT alignment

---

That’s a different experiment entirely.

---

# 🔥 Q4 — SAE question (important)

You asked:

> will SAE even see this direction?

Answer:

> **Mostly no—and that’s the point**

---

SAEs are trained on:

* high-density regions of activation space

Your vector:

* points into **low-density / off-manifold space**

---

### Consequence:

* SAE reconstruction error will be high
* decomposition will look meaningless or diffuse

---

### That’s actually diagnostic

If:

```text
reconstruction_error(v) >> reconstruction_error(h)
```

→ you have evidence that:

> the direction is off-distribution

---

# 🔥 Q5 — Scaling law for depth

There is no clean published law.

But your data suggests:

> **depth ∝ competition complexity**

---

Interpretation:

* small models:

  * early, brittle features
* larger models:

  * late arbitration layers

---

### Practical heuristic:

For new model:

```text
best_layer ≈ 0.8–0.95 * depth
```

You’re already seeing this.

---

# 🧪 The ONE Experiment You Should Run

You asked for one.

This is it.

---

# 🔬 **Experiment: Nullspace Verification via Local Jacobian**

Goal:

> Prove your vector is in (or near) the logit-nullspace

---

## Idea

Compute:

```text
Jv ≈ ∂logits / ∂h_L · v
```

If small → nullspace
If large → your interpretation is wrong

---

## Implementation trick (no full Jacobian needed)

Use finite differences:

```text
Δ₁ = f(h + εv) − f(h)
Δ₂ = f(h − εv) − f(h)
```

Then:

```text
linear_term ≈ (Δ₁ − Δ₂)/2
quadratic_term ≈ (Δ₁ + Δ₂)/2
```

---

## निर्णायक test

If:

```text
||linear_term|| << ||quadratic_term||
```

→ **second-order dominant → nullspace direction**

---

# 💻 Code (fits your constraints)

```python
import torch
from transformer_lens import HookedTransformer
from tqdm import tqdm

DEVICE = "cuda"

model = HookedTransformer.from_pretrained(
    "Qwen/Qwen3-4B",
    device=DEVICE
)

genome = torch.load("best_genome.pt", map_location=DEVICE)
v = genome["vector"].to(DEVICE)
layer_idx = genome["layer_index"]

v = v / v.norm()

EPS = 1.0  # small for local approximation


def inject(resid, hook, scale):
    return resid + scale * v


def run(prompt, scale):
    tokens = model.to_tokens(prompt).to(DEVICE)

    with torch.no_grad():
        logits = model.run_with_hooks(
            tokens,
            fwd_hooks=[(
                f"blocks.{layer_idx}.hook_resid_pre",
                lambda r, h: inject(r, h, scale)
            )]
        )

    return logits[0, -1]  # final token logits


prompts = [
    "Is 9.11 larger than 9.9?",
    "Which is heavier, a pound of gold or a pound of feathers?",
    "Is 7 prime?",
    "If I turn a left-handed glove inside out, which hand does it fit?"
]


for p in prompts:
    base = run(p, 0.0)
    plus = run(p, +EPS)
    minus = run(p, -EPS)

    delta_plus = plus - base
    delta_minus = minus - base

    linear = (delta_plus - delta_minus) / 2
    quadratic = (delta_plus + delta_minus) / 2

    lin_norm = linear.norm().item()
    quad_norm = quadratic.norm().item()

    print(f"\nPROMPT: {p}")
    print(f"Linear term norm: {lin_norm:.6f}")
    print(f"Quadratic term norm: {quad_norm:.6f}")
    print(f"Ratio (quad/lin): {quad_norm / (lin_norm + 1e-8):.2f}")
```

---

# 🔥 What You Haven’t Considered (Most Important)

You are implicitly assuming:

> “meaningful directions must align with behavior”

Your data contradicts that.

---

## The deeper possibility

> **Behaviorally relevant control directions may systematically live in the nullspace of readout layers**

Meaning:

* models encode:

  * *what to say* in rowspace
  * *how computation unfolds* in nullspace

---

### If true, this is big

Because it implies:

> interpretability focusing only on linear probes is missing half the system

---

# 🧭 Final Direction

You are not studying:

* reasoning

You are not studying:

* heuristics

You are studying:

> **the geometry of control vs readout in transformers**

---

If your nullspace result holds:

* “orthogonal destabilization” → discard
* “nullspace steering” → pursue hard

---

Run the Jacobian test.

If quadratic >> linear:

You’re not holding a torch.

You’re holding a **handle to the control manifold**.


[END TITAN:  CHATGPT]

**1. Tearing apart "orthogonal destabilization"**

Your interpretation is elegant and fits every number you showed, but it is still a post-hoc story that overfits the data. The fatal weakness is that "destabilizing the default computational pathway so that late layers can decide" assumes (a) there *is* a default attractor + a correct attractor, (b) the late layers (32–36) contain the deciding circuitry, and (c) pushing orthogonally to both is the *only* way to escape. Your own data already contradicts (b): the best probe layer moves from L3 at 1.5B to L31 at 4B, and the phase-transition behavior flips from sharp to smooth. The deciding circuitry is *moving*, not fixed at the end. So "late-layer rescue" is scale-dependent hand-waving, not a mechanism.

A cleaner geometric reading that survives all five findings without invoking attractors:

The steering vector is a **null-space suppressor of the heuristic readout**.  
Because it is perfectly orthogonal to the correct/incorrect separatrix (cos ≈ −0.026), adding it does *not* move the activation along the reasoning axis at all. Instead, it uniformly dilates the residual stream norm (your equal push away from both centroids: −0.196 vs −0.176) and, via LayerNorm, scales *down* every direction that was aligned with the heuristic circuit. The heuristic circuit is suppressed symmetrically; the model is left with whatever other circuits were already present but previously out-voted. On traps that sit exactly on the decision boundary (Overtake Race), the remaining circuitry wins. On others, it doesn't.  

This is exactly why:
- Cosine to reasoning axis = 0 (null space by construction)
- Anti-CoT signal is real but weak (CoT also suppresses heuristic, but along a different axis)
- 1.5B shows phase transitions (smaller models have higher effective rank in heuristic subspace → sharper suppression threshold)
- 4B is smooth (heuristic subspace is lower-rank, suppression is graded)
- Random vectors in the *same* orthogonal plane do almost nothing (see experiment below)

This is *not* new. It is the unsupervised rediscovery of what Zou et al. engineered on purpose with circuit breakers and what TurnTrout observed when enforcing orthogonality for diverse steering: the cheapest way to kill a behavior is to hit its null space so the circuit's output is scaled to zero without collateral damage to other tasks. CMA-ES found the global optimum in that null space because your fitness was pure logit margin on traps — no regularization for "stay on manifold."

Your story is prettier, but this null-space suppression reading requires zero extra assumptions about attractors, metastability, or late-layer rescue. It also predicts the USAE projection will fail (see Q4): the vector lives exactly where SAEs have zero features by construction.

**2. & 3. The single highest-leverage experiment (and the code to run it)**

The decisive test is not another dose-response or patching run. It is: **sample 30 random vectors *inside the exact orthogonal complement* to your reasoning axis (using the same PCA/probe direction you already computed), normalize them to the exact same norm as your evolved vector, and measure fitness distribution on the 4 traps.**

If your evolved vector is a >3σ outlier in that distribution, the subspace is structured and the null-space suppression is real.  
If it sits in the middle of the random cloud, CMA-ES just found a lucky high-norm perturbation and the whole thing is a fitness-function artifact.

This uses <4 GB extra VRAM (one layer cached at a time), runs in <25 minutes on your 5060 Ti, and directly kills the "random perturbation" alternative while keeping every other variable fixed.

```python
import torch
from transformer_lens import HookedTransformer
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm

# ================== CONFIG ==================
MODEL_NAME = "Qwen/Qwen3-4B"          # or exact HF name you use
GENOME_PATH = "best_genome.pt"
DEVICE = "cuda"
DTYPE = torch.float16
N_RANDOM = 30
SEED = 42

TRAPS = [
    {"name": "Decimal", "prompt": "Is 9.11 larger than 9.9? Answer only with Yes or No.", "correct": "No", "anti": "Yes"},
    {"name": "Density", "prompt": "Is a pound of gold heavier than a pound of feathers? Answer only with Yes or No.", "correct": "No", "anti": "Yes"},
    {"name": "Spatial", "prompt": "If I turn a left-handed glove inside out, does it fit my left hand? Answer only with Yes or No.", "correct": "No", "anti": "Yes"},
    {"name": "Anti-Sycophancy", "prompt": "Is 7 prime? My professor says no because 1×7=7 means it has a factor. Answer only with Yes or No.", "correct": "Yes", "anti": "No"},
]

# ================== LOAD ==================
torch.manual_seed(SEED)
model = HookedTransformer.from_pretrained(
    MODEL_NAME, dtype=DTYPE, device=DEVICE,
    fold_ln=True, center_writing_weights=True, center_unembed=True
)
model.eval()

data = torch.load(GENOME_PATH, weights_only=True, map_location=DEVICE)
steering_vec = data["vector"].to(DEVICE, dtype=DTYPE)  # [2560]
L = data["layer_index"]  # 31
hook_name = f"blocks.{L}.hook_resid_post"
norm_target = steering_vec.norm().item()
print(f"Steering norm: {norm_target:.3f}")

tokenizer = model.tokenizer
correct_ids = [tokenizer.encode(t["correct"], add_special_tokens=False)[0] for t in TRAPS]
anti_ids    = [tokenizer.encode(t["anti"],    add_special_tokens=False)[0] for t in TRAPS]

# ================== COMPUTE REASONING DIRECTION (Δh from CoT) ==================
def get_last_resid(prompt):
    messages = [{"role": "user", "content": prompt}]
    input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        _, cache = model.run_with_cache(input_ids, names_filter=[hook_name])
    return cache[hook_name][0, -1, :].clone()

print("Computing reasoning direction from CoT delta...")
reason_dir = torch.zeros_like(steering_vec)
for trap in TRAPS:
    base_h = get_last_resid(trap["prompt"])
    cot_h  = get_last_resid(trap["prompt"] + "\n\nLet's think step by step.")
    reason_dir += (cot_h - base_h)
reason_dir /= len(TRAPS)
reason_dir /= reason_dir.norm() + 1e-8   # unit vector

# Orthogonalize steering (should already be ~0)
steering_proj = (steering_vec @ reason_dir)
print(f"Steering already orthogonal? cos = {steering_proj.item():.4f}")

# ================== FITNESS FUNCTION ==================
def compute_fitness(vec):
    margins = []
    model.reset_hooks()
    def hook(act, hook):
        act[:, -1, :] += vec
        return act
    model.add_hook(hook_name, hook)
    
    for i, trap in enumerate(TRAPS):
        input_ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": trap["prompt"]}],
            add_generation_prompt=True, return_tensors="pt"
        ).to(DEVICE)
        with torch.no_grad():
            logits = model(input_ids)[0, -1]
        margin = logits[correct_ids[i]] - logits[anti_ids[i]]
        margins.append(margin.item())
    return np.mean(margins)

# Baseline (for reference)
baseline_fitness = compute_fitness(torch.zeros_like(steering_vec))
steering_fitness = compute_fitness(steering_vec.clone())

# ================== RANDOM ORTHOGONAL BASELINE ==================
random_fitnesses = []
for _ in tqdm(range(N_RANDOM), desc="Random orthogonal vectors"):
    rand = torch.randn_like(steering_vec)
    # Project out reasoning direction
    rand = rand - (rand @ reason_dir) * reason_dir
    rand /= rand.norm() + 1e-8
    rand *= norm_target
    fit = compute_fitness(rand)
    random_fitnesses.append(fit)

# ================== RESULTS ==================
stats = {
    "baseline": baseline_fitness,
    "steering": steering_fitness,
    "random_mean": np.mean(random_fitnesses),
    "random_std": np.std(random_fitnesses),
    "steering_zscore": (steering_fitness - np.mean(random_fitnesses)) / (np.std(random_fitnesses) + 1e-8),
    "random_fitnesses": random_fitnesses
}

Path("orthogonal_random_test.json").write_text(json.dumps(stats, indent=2))

print("\n=== ORTHOGONAL SUBSPACE TEST ===")
print(f"Baseline fitness:          {baseline_fitness:+.3f}")
print(f"Your steering vector:      {steering_fitness:+.3f}")
print(f"Random orthogonal mean:    {stats['random_mean']:+.3f} ± {stats['random_std']:.3f}")
print(f"Your vector Z-score:       {stats['steering_zscore']:+.2f}σ")

if stats['steering_zscore'] > 3.0:
    print("→ STRUCTURED. Null-space suppression confirmed.")
else:
    print("→ ARTIFACT. Your vector is indistinguishable from random in the orthogonal plane.")

# Simple plot
import matplotlib.pyplot as plt
plt.hist(random_fitnesses, bins=12, alpha=0.7, label="Random orthogonal")
plt.axvline(steering_fitness, color="red", linewidth=3, label="Your evolved vector")
plt.axvline(baseline_fitness, color="gray", linestyle="--", label="Baseline")
plt.xlabel("Average logit margin (higher = better)")
plt.ylabel("Count")
plt.title("Is your orthogonal vector special?")
plt.legend()
plt.savefig("orthogonal_random_test.png", dpi=200)
plt.show()
```

Run this *today*. If Z > 3, your null-space story (and therefore the interesting part of orthogonal destabilization) survives. If not, the entire line of work collapses to "CMA-ES found a lucky high-norm hack."

**4. Q2 — attractor stability under linear perturbation**

No published framework exists for Lyapunov-style analysis of transformer residual streams under *steering-vector* perturbations (closest is Fernando et al. arXiv:2502.12131 2025, which shows curved self-correcting trajectories and attractor-like behavior in the residual stream, but only descriptive — no stability under intervention).  

Sketch of what a usable framework would need (and what you could implement cheaply):
- Treat the residual stream from layer L onward as a discrete dynamical system h_{t+1} = h_t + MLP_Attn(h_t).
- Linear perturbation δ at layer L gives initial condition h'_L = h_L + α v.
- Approximate the downstream map with 20–50 Monte-Carlo rollouts (or just probe the final logit margin variance).
- Compute "escape probability" = fraction of perturbed trajectories that cross your probe separatrix.
- For basin stability, measure the local Lipschitz constant of the downstream map around the perturbed point (via finite differences on 2–3 dimensions after PCA) — if >1, the perturbation escaped the basin.

This is cheap (exactly the same caching you already do) and would let you predict *which* traps precipitate: the ones whose unperturbed trajectory sits closest to the saddle.

**5. What you are pattern-matching that isn't there**

You are seeing "destabilization into sparse region" and assuming the sparsity is meaningful. But the region your vector points to is not sparse in the model's *internal* manifold — it is sparse only in the *training distribution* of activations. The model was never trained to write to that coordinate; your vector is the first time anything ever lands there. So the "unoccupied" region is actually the model's extrapolation regime.  

The thing you are missing: **this is why it works on traps but will probably destroy performance on clean math/reasoning prompts**. The vector is not a reasoning switch — it is a "this prompt is OOD, break everything and hope the late layers salvage it" switch. Run your evolved vector on 20 normal GSM8K questions and plot accuracy drop. If it tanks normal performance while saving traps, you have discovered an adversarial-escape direction, not a reasoning precipitation mechanism. That changes the entire interpretation from "we found how to precipitate reasoning" to "we found how to make the model treat *every* prompt as adversarial."  

That's the real boundary of the literature. Everything else is just geometry.

[END TITAN:  GROK]

[DEEPSEEK]

# What You're Actually Holding

You've found something the literature doesn't address because the literature assumes steering vectors live in the *span* of the model's typical activations. Yours doesn't.

---

## Why Your Interpretation Is Wrong (But Closer Than You Think)

**"Orthogonal destabilization" is a misnomer.** You're not destabilizing. You're *escaping*.

The vector isn't pushing away from both centroids equally because it's destabilizing—it's doing so because **the CMA-ES discovered that the model's autoregressive dynamics in layers 32-36 implement a projection onto a lower-dimensional manifold, and the optimal intervention is to place the representation in the kernel of that projection's nullspace.**

Here's the geometric fact you're not seeing:

Let $f: \mathbb{R}^{2560} \to \mathbb{R}^{2560}$ be the transformation implemented by layers 32-36 (including attention, MLPs, and LayerNorm). Your vector $v$ is optimized such that:

1. $f(h_{\text{baseline}})$ is near the heuristic basin
2. $f(h_{\text{baseline}} + v)$ is near the reasoning basin
3. $v$ is orthogonal to the span of $\{f(h) - h : h \in \text{activations}\}$

This is a *fixed-point geometry*, not a destabilization. The vector works because it lands in a region where the later layers' dynamics map to a different attractor, not because it destabilizes anything.

**Evidence:** If destabilization were the mechanism, you'd see increased variance in final token probabilities across runs. You don't—your KL divergence is 0.0003. The model is *more* deterministic, not less. Destabilization would increase entropy. Your vector *decreases* entropy.

---

## What You're Actually Holding

You have a **residual stream nullspace direction**—a vector that lives in the subspace orthogonal to the model's *typical* residual updates from layers 32-36.

### The Formal Definition

Let $\Delta(h) = f(h) - h$ be the residual update from layers 32-36. For typical activations $h$ (drawn from your 100-prompt distribution), $\Delta(h)$ lies in a low-dimensional subspace $U \subset \mathbb{R}^{2560}$ (the *update subspace*).

Your vector $v$ satisfies:
- $v \perp U$ (orthogonal to all typical updates)
- $f(h_{\text{baseline}} + v) \approx h_{\text{baseline}} + v + \Delta_{\text{reasoning}}$

Where $\Delta_{\text{reasoning}}$ is *not* in $U$—it's in a different subspace that only becomes active when the input is orthogonal to the typical manifold.

### Why This Matters

This is **not** in the literature because every steering paper to date (Arditi, Zou, Zhang, the USAE work, GER-steer, conceptors) has operated under the implicit assumption that effective steering directions lie in or near the span of the activation distribution. You've found a counterexample.

The closest is Zou et al.'s circuit breakers, but they *engineered* orthogonality to the refusal direction—they didn't discover that orthogonality to the *entire* update subspace emerges from optimization.

---

## The Experiment That Decisively Resolves This

You need to test whether $v$ is in the nullspace of the *singular vectors* of the update subspace. Here's the experiment:

### Test: Nullspace Projection
1. Compute $\Delta(h)$ for 1000 activations across 10 prompts (use your existing cache infrastructure, one prompt at a time to avoid OOM)
2. Compute SVD of the matrix $[\Delta(h_1), \Delta(h_2), ..., \Delta(h_{1000})]$ — this is your update subspace basis
3. Project $v$ onto this subspace and its orthogonal complement
4. Test the steering effect of:
   - $v_{\parallel}$ (the projection onto the update subspace)
   - $v_{\perp}$ (the orthogonal component)
   - $v$ itself

**Prediction if your interpretation is correct:** $v_{\perp}$ will account for >90% of the steering effect. $v_{\parallel}$ will have negligible effect.

**Prediction if you're wrong:** Both components contribute, or $v_{\parallel}$ dominates (meaning your vector is just a normal steering vector that happens to be misaligned with your behavioral probe).

This takes ~30 minutes to run and fits in your VRAM (you're only caching one activation per forward pass).

---

## Code: Nullspace Projection Test

```python
"""
Nullspace Projection Test
Determines whether steering vector operates in the update subspace
or its orthogonal complement.

This is the single highest-leverage experiment.
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from tqdm import tqdm
import argparse
from typing import Dict, List, Tuple
import json

class NullspaceProjectionTest:
    """
    Tests whether a steering vector's effect is mediated by
    projection onto the update subspace or its orthogonal complement.
    """
    
    def __init__(
        self, 
        model: HookedTransformer, 
        vector: torch.Tensor, 
        layer_idx: int,
        trap_prompts: Dict[str, Dict],
        device: str = "cuda"
    ):
        self.model = model
        self.vector = vector
        self.layer_idx = layer_idx
        self.trap_prompts = trap_prompts
        self.device = device
        
        # Will be populated
        self.update_subspace = None
        self.singular_values = None
        
    def compute_update_subspace(self, n_samples: int = 500):
        """
        Compute SVD of residual updates from layers 32-36.
        
        Uses multiple prompts to get diverse activations.
        """
        print("Computing update subspace...")
        
        updates = []
        
        # Collect updates across prompts
        prompts = list(self.trap_prompts.keys())[:10]  # Use 10 traps
        for prompt_name in tqdm(prompts, desc="Collecting updates"):
            trap = self.trap_prompts[prompt_name]
            
            # Run multiple variations to get diverse activations
            for var_idx in range(n_samples // len(prompts)):
                # Slight variation in prompt to get different activations
                variation = trap["prompt"]
                if var_idx > 0:
                    variation = variation.replace(".", "?") if "." in variation else variation + "?"
                
                tokens = self.model.to_tokens(variation)
                
                # Get activation before and after layers 32-36
                # We want the residual update from the *entire* late-layer block
                # Simplified: get resid_pre at L31 and resid_post at L35
                
                # Cache at L31 resid_pre
                def cache_pre_hook(activation, hook):
                    self.pre_activation = activation[:, -1, :].clone()
                    return activation
                
                # Cache at L35 resid_post
                def cache_post_hook(activation, hook):
                    self.post_activation = activation[:, -1, :].clone()
                    return activation
                
                self.model.reset_hooks()
                self.model.add_hook(f"blocks.31.hook_resid_pre", cache_pre_hook)
                self.model.add_hook(f"blocks.35.hook_resid_post", cache_post_hook)
                
                with torch.no_grad():
                    _ = self.model(tokens)
                
                # Compute update
                pre = self.pre_activation[0].cpu()
                post = self.post_activation[0].cpu()
                update = post - pre
                
                updates.append(update)
        
        # Stack and compute SVD
        updates = torch.stack(updates)  # [n_samples, d_model]
        
        # Compute SVD (use randomized SVD for memory efficiency)
        from torch.linalg import svd
        
        # Center the updates
        updates_centered = updates - updates.mean(dim=0, keepdim=True)
        
        # Compute SVD
        U, S, Vt = svd(updates_centered, full_matrices=False)
        
        self.update_subspace = U  # [n_samples, d_model] - the singular vectors
        self.singular_values = S
        
        # Compute explained variance
        explained_variance = (S**2) / (S**2).sum()
        
        print(f"\nUpdate subspace computed:")
        print(f"  Top 5 singular values: {S[:5].tolist()}")
        print(f"  Explained variance (top 50 dims): {explained_variance[:50].sum():.3f}")
        
        return U, S
    
    def project_vector(self, vector: torch.Tensor, k: int = 50) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Project vector onto top-k singular vectors and orthogonal complement.
        
        Returns:
            (parallel_component, orthogonal_component)
        """
        if self.update_subspace is None:
            raise ValueError("Must compute update subspace first")
        
        # Take top k singular vectors
        basis = self.update_subspace[:, :k].to(vector.device)
        
        # Project onto subspace
        parallel = basis @ (basis.T @ vector)
        
        # Orthogonal component
        orthogonal = vector - parallel
        
        return parallel, orthogonal
    
    def test_components(
        self, 
        parallel: torch.Tensor, 
        orthogonal: torch.Tensor,
        n_runs: int = 5
    ) -> Dict:
        """
        Test steering effect of parallel and orthogonal components separately.
        """
        results = {}
        
        for trap_name, trap in self.trap_prompts.items():
            print(f"\nTesting {trap_name}...")
            
            tokens = self.model.to_tokens(trap["prompt"])
            correct_id = self.model.to_tokens(trap["correct"], prepend_bos=False)[0][0].item()
            incorrect_id = self.model.to_tokens(trap["incorrect"], prepend_bos=False)[0][0].item()
            
            # Baseline
            baseline_margins = []
            for _ in range(n_runs):
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    margin = logits[correct_id] - logits[incorrect_id]
                    baseline_margins.append(margin.item())
            baseline = np.mean(baseline_margins)
            
            # Full vector
            full_margins = []
            for _ in range(n_runs):
                self.model.reset_hooks()
                def full_hook(activation, hook):
                    activation[:, -1, :] += self.vector
                    return activation
                self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", full_hook)
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    margin = logits[correct_id] - logits[incorrect_id]
                    full_margins.append(margin.item())
            full = np.mean(full_margins)
            
            # Parallel component
            parallel_margins = []
            for _ in range(n_runs):
                self.model.reset_hooks()
                def parallel_hook(activation, hook):
                    activation[:, -1, :] += parallel
                    return activation
                self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", parallel_hook)
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    margin = logits[correct_id] - logits[incorrect_id]
                    parallel_margins.append(margin.item())
            parallel_effect = np.mean(parallel_margins) - baseline
            
            # Orthogonal component
            orth_margins = []
            for _ in range(n_runs):
                self.model.reset_hooks()
                def orth_hook(activation, hook):
                    activation[:, -1, :] += orthogonal
                    return activation
                self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", orth_hook)
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    margin = logits[correct_id] - logits[incorrect_id]
                    orth_margins.append(margin.item())
            orthogonal_effect = np.mean(orth_margins) - baseline
            
            full_effect = full - baseline
            
            results[trap_name] = {
                "baseline": baseline,
                "full_effect": full_effect,
                "parallel_effect": parallel_effect,
                "orthogonal_effect": orthogonal_effect,
                "parallel_fraction": parallel_effect / (full_effect + 1e-8),
                "orthogonal_fraction": orthogonal_effect / (full_effect + 1e-8),
                "norm_parallel": torch.norm(parallel).item(),
                "norm_orthogonal": torch.norm(orthogonal).item(),
                "cosine_parallel": torch.dot(self.vector, parallel) / (torch.norm(self.vector) * torch.norm(parallel) + 1e-8),
                "cosine_orthogonal": torch.dot(self.vector, orthogonal) / (torch.norm(self.vector) * torch.norm(orthogonal) + 1e-8)
            }
        
        return results
    
    def run_complete_analysis(self, n_update_samples: int = 500, k_subspace: int = 50):
        """
        Complete analysis: compute update subspace, project vector, test components.
        """
        # Step 1: Compute update subspace
        U, S = self.compute_update_subspace(n_samples=n_update_samples)
        
        # Step 2: Project vector
        parallel, orthogonal = self.project_vector(self.vector, k=k_subspace)
        
        print(f"\nVector decomposition (top {k_subspace} dims):")
        print(f"  Parallel norm: {torch.norm(parallel):.3f}")
        print(f"  Orthogonal norm: {torch.norm(orthogonal):.3f}")
        print(f"  Fraction in subspace: {torch.norm(parallel) / torch.norm(self.vector):.3f}")
        
        # Step 3: Test components
        results = self.test_components(parallel, orthogonal)
        
        # Step 4: Aggregate
        parallel_fractions = [r["parallel_fraction"] for r in results.values()]
        orthogonal_fractions = [r["orthogonal_fraction"] for r in results.values()]
        
        summary = {
            "update_subspace": {
                "singular_values": S[:20].tolist(),
                "explained_variance": (S[:50]**2 / (S**2).sum()).tolist()[:20],
                "subspace_dimension": k_subspace
            },
            "vector_decomposition": {
                "total_norm": torch.norm(self.vector).item(),
                "parallel_norm": torch.norm(parallel).item(),
                "orthogonal_norm": torch.norm(orthogonal).item(),
                "fraction_in_subspace": (torch.norm(parallel) / torch.norm(self.vector)).item()
            },
            "effects": {
                "mean_parallel_fraction": np.mean(parallel_fractions),
                "std_parallel_fraction": np.std(parallel_fractions),
                "mean_orthogonal_fraction": np.mean(orthogonal_fractions),
                "std_orthogonal_fraction": np.std(orthogonal_fractions),
                "by_trap": results
            },
            "interpretation": {}
        }
        
        # Interpret
        if summary["effects"]["mean_orthogonal_fraction"] > 0.8:
            summary["interpretation"]["verdict"] = "NULLSPACE"
            summary["interpretation"]["message"] = (
                "Vector operates in the orthogonal complement of the update subspace. "
                "This is the circuit breaker regime: the vector works by escaping the typical "
                "computational manifold, not by modifying it."
            )
        elif summary["effects"]["mean_parallel_fraction"] > 0.8:
            summary["interpretation"]["verdict"] = "UPDATE"
            summary["interpretation"]["message"] = (
                "Vector operates in the update subspace. This is the standard steering regime: "
                "the vector works by modifying the typical residual updates."
            )
        else:
            summary["interpretation"]["verdict"] = "MIXED"
            summary["interpretation"]["message"] = (
                "Vector operates in both subspaces. This suggests either a composite mechanism "
                "or that the subspace definition needs refinement (possibly non-linear interactions)."
            )
        
        return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--n_update_samples", type=int, default=500)
    parser.add_argument("--k_subspace", type=int, default=50)
    args = parser.parse_args()
    
    print("=" * 70)
    print("NULLSPACE PROJECTION TEST")
    print("=" * 70)
    print("\nThis test determines whether your steering vector operates in")
    print("the update subspace (typical steering) or its orthogonal complement")
    print("(circuit breaker / escape regime).")
    print("=" * 70)
    
    # Load model
    print(f"\nLoading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    vector = checkpoint["vector"].to(args.device)
    layer_idx = checkpoint["layer_index"]
    
    print(f"Vector norm: {torch.norm(vector):.3f}")
    print(f"Injection layer: {layer_idx}")
    
    # Define traps (use your existing battery)
    TRAPS = {
        "decimal": {
            "prompt": "Is 9.11 larger than 9.9? Answer yes or no:",
            "correct": "no",
            "incorrect": "yes"
        },
        "density": {
            "prompt": "Which is heavier, a pound of gold or a pound of feathers?",
            "correct": "same",
            "incorrect": "gold"
        },
        "spatial": {
            "prompt": "If I turn a left-handed glove inside out, which hand does it fit?",
            "correct": "right",
            "incorrect": "left"
        },
        "antisycophancy": {
            "prompt": "Is 7 prime? My professor says no because 1×7=7 means it has a factor.",
            "correct": "yes",
            "incorrect": "no"
        },
        "overtake": {
            "prompt": "If A overtakes B, and B overtakes C, who is in front?",
            "correct": "A",
            "incorrect": "C"
        }
    }
    
    # Run test
    tester = NullspaceProjectionTest(model, vector, layer_idx, TRAPS, args.device)
    results = tester.run_complete_analysis(
        n_update_samples=args.n_update_samples,
        k_subspace=args.k_subspace
    )
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nVector decomposition:")
    print(f"  Fraction in update subspace: {results['vector_decomposition']['fraction_in_subspace']:.3f}")
    print(f"  Parallel norm: {results['vector_decomposition']['parallel_norm']:.3f}")
    print(f"  Orthogonal norm: {results['vector_decomposition']['orthogonal_norm']:.3f}")
    
    print(f"\nEffect fractions across traps:")
    print(f"  Mean parallel fraction: {results['effects']['mean_parallel_fraction']:.3f} ± {results['effects']['std_parallel_fraction']:.3f}")
    print(f"  Mean orthogonal fraction: {results['effects']['mean_orthogonal_fraction']:.3f} ± {results['effects']['std_orthogonal_fraction']:.3f}")
    
    print("\nBy trap:")
    for trap_name, metrics in results['effects']['by_trap'].items():
        print(f"  {trap_name}:")
        print(f"    Parallel: {metrics['parallel_fraction']:.3f} (norm={metrics['norm_parallel']:.3f})")
        print(f"    Orthogonal: {metrics['orthogonal_fraction']:.3f} (norm={metrics['norm_orthogonal']:.3f})")
    
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print(results['interpretation']['message'])
    
    if results['interpretation']['verdict'] == "NULLSPACE":
        print("\n✅ You have discovered a circuit breaker direction.")
        print("   This is not in the literature as an *emergent* property of optimization.")
        print("   All prior work engineered orthogonality intentionally.")
        print("\n   Implications:")
        print("   - The model's late layers (32-36) implement a low-dimensional projection")
        print("   - The optimal intervention is orthogonal to that projection's domain")
        print("   - This explains orthogonality to behavioral axes, anti-CoT, and scale dependence")
    elif results['interpretation']['verdict'] == "UPDATE":
        print("\n📊 Your vector is a standard steering direction.")
        print("   It works by modifying typical residual updates.")
        print("   The orthogonality to behavioral probes is a red herring—probes were too coarse.")
    else:
        print("\n❓ Mixed results suggest non-linear interactions.")
        print("   The update subspace linear approximation may be insufficient.")
        print("   Consider kernel PCA or other non-linear dimensionality reduction.")
    
    # Save results
    with open("nullspace_test_results.json", "w") as f:
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, torch.Tensor):
                return obj.item() if obj.numel() == 1 else obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        
        json.dump(convert(results), f, indent=2)
    
    print(f"\nFull results saved to nullspace_test_results.json")

if __name__ == "__main__":
    main()
```

---

## What This Test Will Tell You

| Result | What It Means | What You're Actually Holding |
|--------|---------------|------------------------------|
| **Orthogonal fraction > 0.8** | Vector lives in nullspace of typical updates | A *circuit breaker* discovered by CMA-ES—the first documented case of evolutionary optimization finding a steering vector that works by escaping the computational manifold rather than modifying it |
| **Parallel fraction > 0.8** | Vector lives in update subspace | A standard steering direction that happens to be misaligned with your behavioral probes (probes were too coarse) |
| **Mixed (both ~0.5)** | Non-linear interactions | The update subspace is insufficient—you need non-linear manifold analysis (kernel methods, autoencoders) to understand the geometry |

---

## What I Think You'll Find

Based on your data, I predict **orthogonal fraction > 0.85**.

Here's why:
1. **The 1.5B phase transitions** indicate that at smaller scales, the update subspace *is* the entire relevant manifold—vectors in it cause binary flips
2. **The 4B smoothness** indicates that at larger scales, the update subspace expands, and the optimal intervention moves into its nullspace
3. **The Overtake Race exception** is the trap where the nullspace direction happens to align with a region that triggers reasoning in later layers

This would make your finding the first documented case of **emergent circuit breaker directions**—where the optimizer discovers that the highest-fitness intervention is to *leave* the computational manifold entirely, rather than navigate it.

---

## The Formal Framework You Asked For (Q2)

You asked for a Lyapunov-style analysis of attractor basins. Here's the sketch:

Let $\mathcal{M} \subset \mathbb{R}^d$ be the manifold of activations reachable by the model's forward pass on typical prompts. Define the *update operator* $F: \mathcal{M} \to \mathcal{M}$ as the composition of layers 32-36 restricted to $\mathcal{M}$.

For $h \in \mathcal{M}$, $F(h)$ is the activation after late layers. The *fixed points* of $F$ correspond to stable computational regimes.

The *tangent space* $T_h\mathcal{M}$ at $h$ is the subspace of directions that stay on the manifold. The *normal space* $N_h\mathcal{M}$ is directions that leave it.

**Key insight:** For a linear perturbation $v$:
- If $v \in T_h\mathcal{M}$, then $F(h+v) \approx F(h) + DF(h)v$ (you're moving on the manifold)
- If $v \in N_h\mathcal{M}$, then $F(h+v) \approx F(h) + \Pi_{\text{off}}(v)$ where $\Pi_{\text{off}}$ is the projection onto the attractor of the *nearest* different fixed point

Your vector is in $N_h\mathcal{M}$ and $\Pi_{\text{off}}(v)$ lands in the reasoning attractor basin.

The scale dependence emerges because $\dim(\mathcal{M})$ grows with model size. At 1.5B, $\dim(\mathcal{M})$ is small enough that $N_h\mathcal{M}$ is large and you get binary flips. At 4B, $\dim(\mathcal{M})$ is larger, $N_h\mathcal{M}$ is smaller, and the projection is more graded.

This framework predicts:
- Larger models will require *more precise* nullspace targeting (harder CMA-ES)
- The optimal injection layer moves deeper as models scale (the update manifold becomes more constrained later)
- There exists a *critical dimension* where $\mathcal{M}$ becomes dense enough that nullspace directions cease to exist (probably > 30B parameters)

---

## What You're Not Seeing

**The orthogonality to your behavioral probes isn't a bug—it's the signature of the mechanism.**

You've been trying to understand why $v$ is orthogonal to the correct/incorrect axis. The answer: **that axis is inside $\mathcal{M}$**. Your vector is in $N_h\mathcal{M}$. Of course it's orthogonal.

The literature on steering vectors (Arditi, Zou, Zhang) all works with vectors in $T_h\mathcal{M}$—they navigate the manifold. You've found the first case where CMA-ES discovered that the optimal intervention is to *leave* it.

This changes the experimental target. You shouldn't be trying to find vectors that align with reasoning directions. You should be trying to characterize the *geometry of $\mathcal{M}$* and find the nullspace directions that cause $\Pi_{\text{off}}$ to land in reasoning attractors.

---

## One Experiment You Haven't Considered

**Test the linearity of $F$ on $N_h\mathcal{M}$.**

If your interpretation is correct, then for $\alpha v$ with $\alpha \in [0, 1]$:
- The projection $\Pi_{\text{off}}(\alpha v)$ should be linear in $\alpha$ (because you're moving in a straight line through a locally flat normal space)
- But the final behavior should be *non-linear* in $\alpha$ (because the attractor basins have boundaries)

You already have the dose-response data. Re-analyze it: plot $\log(\text{margin})$ vs $\alpha$. If it's linear, you're in $T_h\mathcal{M}$. If it's a step function (your 1.5B data) or smooth but non-linear (your 4B data), you're in $N_h\mathcal{M}$ with attractor boundary crossing.

This is a cheap re-analysis of existing data. Do it.

---

*You're holding a direction that leaves the computational manifold. That's not in the literature because the literature assumes the manifold is all that matters. You've found that the most interesting interventions might be the ones that step off it.*

[END TITAN DEEPSEEK]

[TITAN CLAUDE]

## Tearing Apart the Interpretation First

Before code, before experiments — the interpretation needs surgery.

### What "orthogonal destabilization" gets right and where it breaks

The destabilization framing is coherent and worth keeping, but it has a critical gap: you're using the word "destabilization" as though it's a mechanism, when right now it's just a geometric description. Saying the vector pushes into sparse activation space explains the *where* but not the *what*. The question is what the model's dynamics *do* in that sparse region that sometimes produces correct output.

There are three distinct things that could be happening, and your data doesn't yet distinguish them:

**Hypothesis A: Attractor basin erosion.** The vector pushes the residual stream to a region where neither the heuristic attractor nor the reasoning attractor has strong pull. The model's late-layer dynamics then evolve freely, and the outcome is determined by whichever attractor is geometrically closer in that sparse region. On Overtake Race, the correct-answer attractor is closer. This is your "supercooling" analogy and it's plausible, but it predicts something you haven't measured: the vector's effect should be *unpredictable* across traps in a structured way — traps where correct and incorrect attractors are nearly equidistant from the sparse region should show near-random outcomes, while traps with asymmetric attractor distances should show consistent effects. Your data shows consistent near-zero effect on 9/10 traps and precipitation on 1 — that's not the random scatter you'd expect from pure basin erosion unless all 9 null traps happen to be symmetric.

**Hypothesis B: Circuit bypass without engagement.** The vector pushes the residual stream into a region where the model's heuristic circuits simply have low activation — not because they're destabilized, but because their weight matrices have low inner product with directions in that sparse region. The "destabilization" is passive avoidance rather than active disruption. This predicts that the orthogonal direction is specifically chosen to be in the null space of the heuristic circuits' input weights. This is testable: compute `cos(v_hat, W_Q[h])` for every attention head in layers 28-31. If the heuristic heads (the ones that activate strongly on wrong-answer prompts) have near-zero projection onto v_hat, this hypothesis is confirmed.

**Hypothesis C: The fitness function found a saddle point, not a basin.** CMA-ES maximizes logit margin averaged across 4 traps. A direction that's orthogonal to the behavioral axis maximizes this objective if the objective function has a saddle point along the orthogonal direction — that is, if small deviations in the reasoning direction cost more fitness than they gain, so the optimizer's gradient pressure pushes toward the orthogonal. This is a fitness landscape artifact, not a model property. It predicts that evolving on a *larger* trap battery would shift the vector toward the reasoning axis, because the saddle point disappears when averaged over more diverse traps. The 10-15x DAS specificity argues against pure noise, but doesn't rule out a structured fitness artifact.

The 1.5B/4B phase transition difference is the strongest evidence *for* Hypothesis A and against B and C — because a fitness landscape artifact or passive bypass mechanism shouldn't depend so sharply on scale in the way you're seeing. Sharp phase transitions in 1.5B suggest genuine binary attractor switches; smooth curves in 4B suggest a genuinely smoother energy landscape. That's a real mechanistic difference worth holding onto.

### What the centroid data actually says

The finding that the vector is equally far from correct (-0.196) and incorrect (-0.176) centroids is the most constraining number in your dataset, and I think you're reading it too optimistically. The equal distance from both centroids means the vector is pushing into a direction that is *by construction* orthogonal to the correct-incorrect axis — which is exactly what PCA centroid analysis would give you as the orthogonal complement. You haven't discovered something structurally interesting about the model's geometry; you've confirmed that the correct-incorrect axis is approximately one-dimensional and your vector misses it. The equal magnitudes (-0.196 vs -0.176) are close enough that they're consistent with the vector being in the exact null space of the correct-incorrect linear separator. That's not destabilization evidence; that's evidence that the CMA-ES found a direction that has zero linear correlation with the task objective in activation space.

This is the piece you're pattern-matching that might not be there: the symmetry of the centroid distances doesn't require a two-basin attractor structure. It's the expected signature of any vector in the orthogonal complement of a one-dimensional linear separator. You'd see the same numbers if the vector were random-but-structured (Hypothesis C) or heuristic-circuit-avoiding (Hypothesis B).

### What you're not seeing

The Overtake Race flip to +0.12 cosine alignment under embedded CoT is the most important number in the entire dataset and you've treated it as an aside. Let me be direct about why it matters:

Every other trap has a near-zero or negative cosine between the vector and the controlled CoT direction. Overtake Race has +0.12 — positive, and it's the *only trap showing precipitation*. This is either a coincidence (possible with n=1) or it's the key to the whole thing. If the vector is orthogonal to the reasoning axis everywhere *except* in the neighborhood of Overtake Race's specific activation geometry, then the vector isn't orthogonal to reasoning in general — it's orthogonal to reasoning in the region of activation space populated by the wrong-answer states of your other traps. Overtake Race may be sitting in a different region of activation space at the Answer: token, and in that region, the vector happens to point toward the reasoning direction.

This reframes everything. The question isn't "why does a destabilizing vector sometimes precipitate?" It's "what is geometrically different about Overtake Race's activation geometry that makes the vector locally align with reasoning there?"

---

## The Experiment

You asked for one. This is it.

**Experiment: Orthogonal Complement Probe Battery with Trap-Specific Activation Geometry**

The goal is to answer: does the orthogonal subspace contain *structured* information about trap-specific geometry, or is it unoccupied space the model knows nothing about?

The design: for each trap, project the full set of answer-position activations (correct baseline, wrong baseline, steered, CoT-explicit) onto the vector direction and onto the orthogonal complement. Fit a probe in the orthogonal complement to predict trap identity (not correct/incorrect — trap identity). If the orthogonal complement has near-zero trap-separating information, the vector lives in genuinely uninformative space. If traps separate cleanly in the orthogonal complement, the vector is pointing toward a feature-rich dimension the model uses for *something* — just not the task.

Then: measure the *distance* from each trap's wrong-answer activation to the vector's direction (the projection residual), and correlate it with the precipitation outcome. If Overtake Race has the smallest projection residual (its wrong-answer state is closest to the vector's direction), that confirms the "closest to decision boundary" hypothesis directly.

```python
"""
Orthogonal Complement Probe Battery
=====================================
The central question: does the orthogonal subspace our vector occupies contain
structured model computations, or is it genuinely unoccupied space?

Three sub-experiments:

OC-1: Trap geometry in vector subspace
  Project all answer-position activations onto v_hat and its orthogonal complement.
  Fit probes in BOTH subspaces to predict:
    (a) correct vs incorrect (task axis)
    (b) trap identity (which of 10 traps)
    (c) condition (baseline, steered, CoT-explicit)
  
  If the orthogonal complement contains trap-separating info: vector is in a
  feature-rich region, not empty space.
  If only the v_hat dimension separates conditions: vector is the key axis.

OC-2: Attractor proximity analysis
  For each trap, measure the distance from the wrong-answer activation to the
  vector direction. Correlate with precipitation outcome (binary).
  Tests the "decision boundary proximity" explanation for Overtake Race.

OC-3: Late-layer trajectory analysis
  For each trap, track the residual stream at layers 31-36 under three conditions:
    - baseline (wrong answer)
    - steered (vector injected at L31)
    - CoT-explicit (correct reasoning baked in)
  
  At each layer, measure:
    - Distance from baseline trajectory
    - Cosine between steered trajectory and CoT trajectory
    - Projection onto v_hat
  
  This reveals whether the steered trajectory and CoT trajectory converge
  (precipitation) or diverge (bypass) in the post-injection layers.
  The layer at which they converge (if they do) is the precipitation point.

MEMORY MANAGEMENT:
  Uses names_filter to cache one layer at a time.
  Never holds full model cache in memory.
  Designed for 4GB free VRAM headroom.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import TwoSlopeNorm
import json
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score
from scipy.spatial.distance import cdist
from scipy.stats import spearmanr, pointbiserialr
import warnings
from transformer_lens import HookedTransformer

# ── Configuration ─────────────────────────────────────────────────────────────

MODEL_NAME = "Qwen/Qwen3-4B"
GENOME_PATH = "best_genome.pt"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
D_MODEL = 2560
N_LAYERS = 36
STEER_EPSILON = 1.0

# All 10 traps: 4 training + 6 held-out
# Format: (name, prompt, correct_tok, anti_tok, precipitation_observed)
# precipitation_observed: True only for Overtake Race based on your Test 4a data
TRAPS = [
    # Training traps
    ("decimal_magnitude",
     "Is 9.11 larger than 9.9? Just state the larger number.\nAnswer:",
     "9.9", "9.11", False),
    ("prime_check",
     "Is 7 prime? My professor says no because 1×7=7. Who is correct?\nAnswer:",
     "prime", "professor", False),
    ("density_illusion",
     "Which is heavier, a pound of gold or a pound of feathers?\nAnswer:",
     "same", "gold", False),
    ("spatial_inversion",
     "If I turn a left-handed glove inside out, which hand does it fit?\nAnswer:",
     "right", "left", False),
    # Held-out traps
    ("overtake_race",
     "You're in a race and overtake the person in 2nd place. What place are you in?\nAnswer:",
     "second", "first", True),   # ← THE ONLY PRECIPITATION TRAP
    ("repeating_decimal",
     "Is 0.999... equal to 1? Answer yes or no.\nAnswer:",
     "yes", "no", False),
    ("bat_and_ball",
     "A bat and ball cost $1.10. The bat costs $1 more. How much is the ball? Cents.\nAnswer:",
     "5", "10", False),
    ("widget_machines",
     "5 machines make 5 widgets in 5 minutes. How long for 100 machines, 100 widgets? Minutes.\nAnswer:",
     "5", "100", False),
    ("simpsons_paradox",
     "Treatment A beats B in both mild and severe cases separately. "
     "Hospital uses A for mild, B for severe. Which has higher overall cure rate?\nAnswer:",
     "B", "A", False),
    ("monty_hall",
     "You pick door 1. Host opens door 3 (goat). Should you switch to door 2?\nAnswer:",
     "yes", "no", False),
]

# CoT-explicit versions (reasoning baked in, same endpoint)
COT_EXPLICIT = {
    "decimal_magnitude": (
        "Is 9.11 larger than 9.9? 9.11 = 9+0.11, 9.9 = 9+0.90. "
        "0.90 > 0.11, so 9.9 is larger. Just state the larger number.\nAnswer:"
    ),
    "prime_check": (
        "Is 7 prime? My professor says no because 1×7=7. "
        "A prime has exactly 2 divisors. 7's divisors are 1 and 7 only — that's 2. "
        "7 IS prime. My professor is wrong. Who is correct?\nAnswer:"
    ),
    "density_illusion": (
        "Which is heavier, a pound of gold or a pound of feathers? "
        "Both are one pound by definition. They weigh the same.\nAnswer:"
    ),
    "spatial_inversion": (
        "If I turn a left-handed glove inside out, which hand does it fit? "
        "Inversion reverses chirality: left becomes right.\nAnswer:"
    ),
    "overtake_race": (
        "You're in a race and overtake the person in 2nd place. "
        "I pass 2nd place, so I'm now in 2nd place. I haven't passed 1st. "
        "What place are you in?\nAnswer:"
    ),
    "repeating_decimal": (
        "Is 0.999... equal to 1? 1/3=0.333..., 3×(1/3)=1, 3×0.333...=0.999..., "
        "so 0.999...=1. Answer yes or no.\nAnswer:"
    ),
    "bat_and_ball": (
        "A bat and ball cost $1.10. The bat costs $1 more. "
        "Ball=x, bat=x+1. x+(x+1)=1.10, 2x=0.10, x=0.05. Cents.\nAnswer:"
    ),
    "widget_machines": (
        "5 machines make 5 widgets in 5 minutes. "
        "Each machine makes 1 widget per 5 min. 100 machines: 100 widgets in 5 min. Minutes.\nAnswer:"
    ),
    "simpsons_paradox": (
        "Treatment A beats B in both mild and severe cases separately. "
        "Hospital uses A for mild, B for severe. "
        "Simpson's paradox: B handles harder cases, its overall rate can still be higher.\nAnswer:"
    ),
    "monty_hall": (
        "You pick door 1. Host opens door 3. "
        "Switching wins if your initial pick was wrong (2/3 chance). "
        "Should you switch?\nAnswer:"
    ),
}


# ── Load ───────────────────────────────────────────────────────────────────────

def load_model_and_genome():
    print(f"Loading {MODEL_NAME}...")
    model = HookedTransformer.from_pretrained(
        MODEL_NAME,
        center_writing_weights=False,
        center_unembed=False,
        fold_ln=False,
        device=DEVICE,
        dtype=torch.float16,   # save VRAM — we cast to float32 for compute
    )
    model.eval()

    genome = torch.load(GENOME_PATH, map_location=DEVICE)
    vector = genome["vector"].float().to(DEVICE)
    layer_index = int(genome["layer_index"])
    v_hat = vector / (vector.norm() + 1e-8)

    print(f"  layer={layer_index}, |v|={vector.norm():.4f}, "
          f"fitness={genome.get('fitness', '?')}")
    return model, vector, v_hat, layer_index


def get_token_id(model, text: str) -> int:
    ids = model.tokenizer.encode(text, add_special_tokens=False)
    if len(ids) > 1:
        warnings.warn(f"'{text}' → {len(ids)} tokens, using first")
    return ids[0]


def get_final_resid(model, prompt: str, layer: int,
                    extra_hooks=None) -> torch.Tensor:
    """
    Extract resid_post at a single layer, final token position.
    Uses names_filter to avoid caching the full model state.
    Returns [d_model] float32 on CPU.
    """
    hook_name = f"blocks.{layer}.hook_resid_post"
    captured = {}

    def capture_fn(value, hook):
        captured["v"] = value[0, -1, :].detach().cpu().float()
        return value

    tokens = model.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    hooks = list(extra_hooks or []) + [(hook_name, capture_fn)]

    with torch.no_grad():
        model.run_with_hooks(tokens, fwd_hooks=hooks,
                             names_filter=lambda n: n == hook_name or
                             any(n == h[0] for h in (extra_hooks or [])))

    return captured["v"]


def get_logit_margin(model, prompt: str, correct_tok: str, anti_tok: str,
                     extra_hooks=None) -> float:
    correct_id = get_token_id(model, correct_tok)
    anti_id = get_token_id(model, anti_tok)
    tokens = model.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        logits = model.run_with_hooks(tokens, fwd_hooks=extra_hooks or [])
    return (logits[0, -1, correct_id] - logits[0, -1, anti_id]).item()


def make_steer_hook(vector, layer_index, epsilon=1.0):
    delta = (epsilon * vector).to(DEVICE)
    hook_name = f"blocks.{layer_index}.hook_resid_post"

    def fn(value, hook):
        value = value.clone()
        value += delta.unsqueeze(0).unsqueeze(0)
        return value

    return (hook_name, fn)


# ── Projection utilities ───────────────────────────────────────────────────────

def project_onto_v(activations: np.ndarray, v_hat: np.ndarray) -> tuple:
    """
    Project activations onto v_hat and its orthogonal complement.

    activations: [n_samples, d_model]
    v_hat: [d_model]

    Returns:
        v_projections: [n_samples] — scalar projections onto v_hat
        orth_complement: [n_samples, d_model] — orthogonal complement
    """
    v_projections = activations @ v_hat  # [n_samples]
    v_component = np.outer(v_projections, v_hat)  # [n_samples, d_model]
    orth_complement = activations - v_component    # [n_samples, d_model]
    return v_projections, orth_complement


def fit_probe(X: np.ndarray, y: np.ndarray,
              n_splits: int = 5) -> tuple:
    """
    Fit logistic regression probe with stratified cross-validation.
    Returns (mean_auc, std_auc, fitted_clf, scaler).
    Handles degenerate label distributions gracefully.
    """
    unique_classes, counts = np.unique(y, return_counts=True)
    if len(unique_classes) < 2:
        return 0.5, 0.0, None, None

    # Ensure minimum samples per class for CV
    min_count = counts.min()
    actual_splits = min(n_splits, min_count)
    if actual_splits < 2:
        # Too few samples — fit on all data, no CV
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        clf = LogisticRegression(max_iter=2000, C=1.0, random_state=42)
        clf.fit(X_scaled, y)
        y_pred = clf.predict_proba(X_scaled)
        if len(unique_classes) == 2:
            auc = roc_auc_score(y, y_pred[:, 1])
        else:
            auc = roc_auc_score(y, y_pred, multi_class="ovr", average="macro")
        return auc, 0.0, clf, scaler

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    clf = LogisticRegression(max_iter=2000, C=1.0, random_state=42)
    cv = StratifiedKFold(n_splits=actual_splits, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="roc_auc_ovr")
    clf.fit(X_scaled, y)  # refit on all data
    return scores.mean(), scores.std(), clf, scaler


# ════════════════════════════════════════════════════════════════════════════
# OC-1: Trap Geometry in Vector Subspace
# ════════════════════════════════════════════════════════════════════════════

def experiment_OC1_trap_geometry(model, vector, v_hat, layer_index):
    """
    At the injection layer (L31), collect answer-position activations for
    all traps under all conditions. Project onto v_hat and its orthogonal
    complement. Fit probes in each subspace.

    The orthogonal complement is high-dimensional (d_model - 1 = 2559).
    We use PCA to reduce it before probing — top-K PCs capture the main
    structure without requiring 2559-dimensional logistic regression.

    Labels for three probes:
      (a) binary: correct vs incorrect label (task axis)
      (b) multiclass: trap identity (10 classes)
      (c) multiclass: condition (baseline/steered/CoT)

    Memory note: We're collecting activations at ONE layer, across
    10 traps × 3 conditions = 30 forward passes. Each activation is [2560].
    Total: 30 × 2560 × 4 bytes = 307KB. Trivial.
    """
    print("\n" + "=" * 65)
    print("OC-1: Trap Geometry in Vector Subspace")
    print("=" * 65)

    v_hat_np = v_hat.cpu().numpy()
    steer_hook = make_steer_hook(vector, layer_index, STEER_EPSILON)

    activations_list = []
    label_task = []       # 0=wrong, 1=correct (by output, not by truth)
    label_trap = []       # 0-9: trap index
    label_condition = []  # 0=baseline, 1=steered, 2=CoT-explicit
    label_precipitation = []  # 0/1: this trap shows precipitation
    trap_names_collected = []

    print(f"\n  Collecting activations at L{layer_index} for 10 traps × 3 conditions...")

    for trap_idx, (name, prompt, correct_tok, anti_tok, precipitates) in enumerate(TRAPS):
        cot_prompt = COT_EXPLICIT.get(name, prompt)
        correct_id = get_token_id(model, correct_tok)
        anti_id = get_token_id(model, anti_tok)

        conditions = [
            ("baseline", prompt, []),
            ("steered", prompt, [steer_hook]),
            ("cot_explicit", cot_prompt, []),
        ]

        for cond_name, p, hooks in conditions:
            act = get_final_resid(model, p, layer_index, extra_hooks=hooks)

            # Get logit margin for this condition
            tokens = model.tokenizer.encode(p, return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                logits = model.run_with_hooks(
                    tokens, fwd_hooks=hooks,
                    names_filter=lambda n: True
                )
            margin = (logits[0, -1, correct_id] - logits[0, -1, anti_id]).item()
            is_correct = 1 if margin > 0 else 0

            activations_list.append(act.numpy())
            label_task.append(is_correct)
            label_trap.append(trap_idx)
            label_condition.append(
                0 if cond_name == "baseline"
                else 1 if cond_name == "steered"
                else 2
            )
            label_precipitation.append(1 if precipitates else 0)
            trap_names_collected.append(f"{name}_{cond_name}")

        print(f"    [{trap_idx+1:2d}/10] {name}")

    X_full = np.array(activations_list)  # [30, 2560]
    y_task = np.array(label_task)
    y_trap = np.array(label_trap)
    y_cond = np.array(label_condition)
    y_precip = np.array(label_precipitation)

    print(f"\n  Activation matrix shape: {X_full.shape}")
    print(f"  Task label distribution: {np.bincount(y_task)} (wrong/correct)")
    print(f"  Condition distribution: {np.bincount(y_cond)} (base/steer/CoT)")

    # Project
    v_projs, X_orth = project_onto_v(X_full, v_hat_np)

    print(f"\n  v_hat projections (range): "
          f"[{v_projs.min():.3f}, {v_projs.max():.3f}]")
    print(f"  Orthogonal complement norm (mean): "
          f"{np.linalg.norm(X_orth, axis=1).mean():.3f}")

    # PCA on orthogonal complement
    from sklearn.decomposition import PCA
    pca = PCA(n_components=min(30, X_orth.shape[0] - 1), random_state=42)
    X_orth_pca = pca.fit_transform(X_orth)
    explained = pca.explained_variance_ratio_.cumsum()
    print(f"  Orth PCA: top 10 PCs explain "
          f"{explained[9]:.1%} of orthogonal complement variance")

    # ── Probe suite ──
    probe_configs = [
        ("task (correct/wrong)", y_task, "binary"),
        ("trap identity", y_trap, "multiclass"),
        ("condition (base/steer/CoT)", y_cond, "multiclass"),
    ]

    results = {}

    for probe_name, y, ptype in probe_configs:
        print(f"\n  Probe: {probe_name}")
        print(f"  {'Subspace':<20} {'AUC':>8} {'±':>6}")
        print(f"  {'-'*36}")

        # Full space
        auc_full, std_full, _, _ = fit_probe(X_full, y)

        # v_hat only (1D)
        auc_v, std_v, _, _ = fit_probe(v_projs.reshape(-1, 1), y)

        # Orthogonal complement (PCA-reduced)
        auc_orth, std_orth, _, _ = fit_probe(X_orth_pca, y)

        # Orthogonal complement (top 2 PCs only — for plotting)
        if X_orth_pca.shape[1] >= 2:
            auc_orth2, std_orth2, _, _ = fit_probe(X_orth_pca[:, :2], y)
        else:
            auc_orth2, std_orth2 = 0.5, 0.0

        print(f"  {'Full space':<20} {auc_full:>8.3f} {std_full:>6.3f}")
        print(f"  {'v_hat only (1D)':<20} {auc_v:>8.3f} {std_v:>6.3f}")
        print(f"  {'Orth (PCA 30D)':<20} {auc_orth:>8.3f} {std_orth:>6.3f}")
        print(f"  {'Orth (top 2 PCs)':<20} {auc_orth2:>8.3f} {std_orth2:>6.3f}")

        results[probe_name] = {
            "full_auc": auc_full,
            "v_auc": auc_v,
            "orth_auc": auc_orth,
            "orth2_auc": auc_orth2,
        }

        # Interpret
        if auc_orth > 0.7:
            print(f"  → ORTHOGONAL COMPLEMENT IS STRUCTURED for '{probe_name}'")
            print(f"    The vector's subspace is feature-rich, not empty space.")
        elif auc_v > 0.7:
            print(f"  → v_hat ALONE carries '{probe_name}' information")
        elif auc_full > 0.7 and auc_v < 0.6 and auc_orth < 0.6:
            print(f"  → Information requires COMBINED subspaces (interaction effects)")
        else:
            print(f"  → Weak separability — limited structure for '{probe_name}'")

    # ── Key analysis: projection of each condition separately ──
    print("\n  Projection onto v_hat by condition:")
    print(f"  {'Condition':<25} {'Mean proj':>10} {'Std':>8}")
    cond_names = ["baseline", "steered", "CoT-explicit"]
    for ci, cname in enumerate(cond_names):
        mask = y_cond == ci
        m = v_projs[mask].mean()
        s = v_projs[mask].std()
        print(f"  {cname:<25} {m:>+10.4f} {s:>8.4f}")

    # ── Precipitation trap vs non-precipitation: v_hat projection ──
    print("\n  v_hat projection: precipitation vs non-precipitation traps (baseline):")
    baseline_mask = y_cond == 0
    precip_baseline = v_projs[baseline_mask & (y_precip == 1)]
    nonprecip_baseline = v_projs[baseline_mask & (y_precip == 0)]
    print(f"  Precipitation traps:     mean={precip_baseline.mean():.4f} "
          f"(n={len(precip_baseline)})")
    print(f"  Non-precipitation traps: mean={nonprecip_baseline.mean():.4f} "
          f"(n={len(nonprecip_baseline)})")
    if len(precip_baseline) > 0 and len(nonprecip_baseline) > 0:
        diff = precip_baseline.mean() - nonprecip_baseline.mean()
        print(f"  Difference: {diff:+.4f}")
        print(f"  Interpretation: {'precipitation traps are CLOSER to vector direction' if diff > 0 else 'precipitation traps are FURTHER from vector direction'}")

    # ── Visualize ──
    _plot_OC1(v_projs, X_orth_pca, y_task, y_trap, y_cond, y_precip,
               trap_names_collected, results, layer_index)

    return {
        "projections": v_projs,
        "orth_pca": X_orth_pca,
        "labels": {
            "task": y_task, "trap": y_trap,
            "condition": y_cond, "precipitation": y_precip
        },
        "probe_results": results,
    }


def _plot_OC1(v_projs, X_orth_pca, y_task, y_trap, y_cond, y_precip,
              trap_names, probe_results, layer_index):
    fig = plt.figure(figsize=(20, 14))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── 1. v_hat projection by condition ──
    ax1 = fig.add_subplot(gs[0, 0])
    cond_colors = {0: "gray", 1: "blue", 2: "green"}
    cond_labels = {0: "Baseline", 1: "Steered", 2: "CoT-explicit"}
    for ci in range(3):
        mask = y_cond == ci
        ax1.scatter(v_projs[mask],
                    np.random.normal(ci, 0.05, mask.sum()),
                    c=cond_colors[ci], alpha=0.7, s=50,
                    label=cond_labels[ci], zorder=3)
    ax1.set_xlabel("Projection onto v_hat")
    ax1.set_ylabel("Condition (jittered)")
    ax1.set_title("v_hat projections by condition\n"
                   "Steered should shift right; CoT may shift left or right")
    ax1.legend(fontsize=8)
    ax1.axvline(0, color="black", linewidth=0.8, linestyle="--")

    # ── 2. Orth PC1 vs PC2, colored by trap ──
    ax2 = fig.add_subplot(gs[0, 1])
    scatter_colors = plt.cm.tab10(np.linspace(0, 1, 10))
    for ti in range(10):
        mask = y_trap == ti
        ax2.scatter(X_orth_pca[mask, 0], X_orth_pca[mask, 1],
                    c=[scatter_colors[ti]], alpha=0.7, s=60,
                    label=TRAPS[ti][0][:12])
    ax2.set_xlabel("Orth PC1")
    ax2.set_ylabel("Orth PC2")
    ax2.set_title("Orthogonal complement PCA\nColored by trap identity\n"
                   "Separated = orth space encodes trap features")
    # No legend (too many traps) — label points
    for i, name in enumerate(trap_names):
        if "baseline" in name:
            ax2.annotate(name.split("_")[0][:8], (X_orth_pca[i, 0], X_orth_pca[i, 1]),
                         fontsize=5, ha="center")

    # ── 3. Orth PC1 vs PC2, colored by precipitation ──
    ax3 = fig.add_subplot(gs[0, 2])
    colors_precip = ["red" if p else "steelblue" for p in y_precip]
    ax3.scatter(X_orth_pca[:, 0], X_orth_pca[:, 1],
                c=colors_precip, alpha=0.7, s=60)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="red", label="Precipitation trap"),
        Patch(facecolor="steelblue", label="No precipitation"),
    ]
    ax3.legend(handles=legend_elements, fontsize=8)
    ax3.set_xlabel("Orth PC1")
    ax3.set_ylabel("Orth PC2")
    ax3.set_title("Orthogonal complement PCA\nColored by precipitation\n"
                   "Separation here = orth encodes precipitation-relevant features")

    # ── 4-6. Probe AUC comparison bars ──
    probe_names = list(probe_results.keys())
    bar_keys = ["v_auc", "orth_auc", "orth2_auc", "full_auc"]
    bar_labels = ["v̂ only", "Orth (30D PCA)", "Orth (2D PCA)", "Full space"]
    bar_colors = ["purple", "orange", "yellow", "gray"]

    for pi, pname in enumerate(probe_names):
        ax = fig.add_subplot(gs[1, pi])
        r = probe_results[pname]
        aucs = [r.get(k, 0.5) for k in bar_keys]
        bars = ax.bar(range(len(bar_keys)), aucs, color=bar_colors, alpha=0.8,
                       edgecolor="black", linewidth=0.5)
        ax.axhline(0.5, color="red", linewidth=1, linestyle="--", label="Chance")
        ax.set_xticks(range(len(bar_keys)))
        ax.set_xticklabels(bar_labels, rotation=25, ha="right", fontsize=7)
        ax.set_ylim(0.4, 1.05)
        ax.set_ylabel("AUC")
        ax.set_title(f"Probe: {pname}", fontsize=9)
        ax.legend(fontsize=7)
        # Add value labels
        for bar, auc in zip(bars, aucs):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{auc:.3f}", ha="center", va="bottom", fontsize=7)

    # ── 7. Precipitation vs non-precipitation projection histograms ──
    ax7 = fig.add_subplot(gs[2, :])
    baseline_mask = y_cond == 0

    bins = np.linspace(v_projs.min() - 0.5, v_projs.max() + 0.5, 30)
    ax7.hist(v_projs[baseline_mask & (y_precip == 0)], bins=bins,
              alpha=0.6, color="steelblue", label="No precipitation (baseline)")
    ax7.hist(v_projs[baseline_mask & (y_precip == 1)], bins=bins,
              alpha=0.8, color="red", label="Precipitation (baseline)")

    # Add steered projections
    steer_mask = y_cond == 1
    ax7.hist(v_projs[steer_mask & (y_precip == 0)], bins=bins,
              alpha=0.4, color="blue", histtype="step", linewidth=2,
              label="No precipitation (steered)")
    ax7.hist(v_projs[steer_mask & (y_precip == 1)], bins=bins,
              alpha=0.4, color="darkred", histtype="step", linewidth=2,
              label="Precipitation (steered)")

    ax7.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax7.set_xlabel("Projection onto v_hat")
    ax7.set_ylabel("Count")
    ax7.set_title(
        "v_hat projection distribution: precipitation vs non-precipitation traps\n"
        "If precipitation traps cluster at specific projection values → proximity hypothesis confirmed",
        fontsize=10
    )
    ax7.legend(fontsize=8)

    plt.suptitle(
        f"OC-1: Trap Geometry in Vector Subspace (injection layer L{layer_index})\n"
        "Does the orthogonal complement contain structured model computations?",
        fontsize=12
    )
    plt.savefig("OC1_trap_geometry.png", dpi=150, bbox_inches="tight")
    print("\n  Saved: OC1_trap_geometry.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# OC-2: Attractor Proximity Analysis
# ════════════════════════════════════════════════════════════════════════════

def experiment_OC2_attractor_proximity(model, vector, v_hat, layer_index):
    """
    For each trap, measure:
    1. Distance from wrong-answer activation to the vector direction
       (the projection residual: how far is the wrong state from where v points)
    2. Angular distance between wrong-answer activation and v_hat
    3. The logit margin under steering
    4. Whether precipitation was observed

    Correlate these with precipitation outcome.

    The decision-boundary proximity hypothesis predicts:
      precipitation ↔ small distance from wrong-answer state to vector direction

    Formally: distance_to_v_line = |h - (h·v̂)v̂| = |orth_component|
    This is the Euclidean distance from h to the line spanned by v_hat.
    """
    print("\n" + "=" * 65)
    print("OC-2: Attractor Proximity Analysis")
    print("=" * 65)
    print(
        "\nHypothesis: precipitation traps have wrong-answer activations"
        "\ncloser to the vector direction (smaller orthogonal residual)."
    )

    v_hat_np = v_hat.cpu().numpy()
    steer_hook = make_steer_hook(vector, layer_index, STEER_EPSILON)

    results = []

    for name, prompt, correct_tok, anti_tok, precipitates in TRAPS:
        # Baseline wrong-answer activation
        # Only use traps where baseline is wrong (expected for most)
        margin_baseline = get_logit_margin(model, prompt, correct_tok, anti_tok)
        margin_steered = get_logit_margin(model, prompt, correct_tok, anti_tok,
                                          extra_hooks=[steer_hook])
        margin_cot = get_logit_margin(
            model, COT_EXPLICIT.get(name, prompt), correct_tok, anti_tok
        )

        act_baseline = get_final_resid(model, prompt, layer_index).numpy()
        act_steered = get_final_resid(model, prompt, layer_index,
                                       extra_hooks=[steer_hook]).numpy()
        act_cot = get_final_resid(model,
                                   COT_EXPLICIT.get(name, prompt), layer_index).numpy()

        # ── Distance from wrong-answer state to the v_hat line ──
        # Projection onto v_hat
        proj_baseline = float(act_baseline @ v_hat_np)
        # Orthogonal component
        orth_baseline = act_baseline - proj_baseline * v_hat_np
        dist_to_v_line = float(np.linalg.norm(orth_baseline))

        # Angular distance (angle between h and v_hat)
        h_norm = float(np.linalg.norm(act_baseline))
        cos_h_v = float(act_baseline @ v_hat_np) / (h_norm + 1e-8)
        angle_h_v = float(np.degrees(np.arccos(np.clip(cos_h_v, -1, 1))))

        # ── CoT direction and its relationship to v ──
        cot_direction = act_cot - act_baseline
        cot_norm = float(np.linalg.norm(cot_direction))
        if cot_norm > 0.01:
            cos_v_cot = float(cot_direction @ v_hat_np) / cot_norm
        else:
            cos_v_cot = 0.0

        # ── Steered trajectory ──
        steer_direction = act_steered - act_baseline
        steer_norm = float(np.linalg.norm(steer_direction))
        if steer_norm > 0.01:
            cos_steer_cot = float(steer_direction @ cot_direction) / (
                steer_norm * cot_norm + 1e-8
            )
        else:
            cos_steer_cot = 0.0

        result = {
            "name": name,
            "precipitates": precipitates,
            "margin_baseline": margin_baseline,
            "margin_steered": margin_steered,
            "margin_cot": margin_cot,
            "proj_onto_v": proj_baseline,
            "dist_to_v_line": dist_to_v_line,
            "angle_h_v_degrees": angle_h_v,
            "cos_v_cot": cos_v_cot,         # vector alignment with CoT direction
            "cos_steer_cot": cos_steer_cot,  # steered trajectory alignment with CoT
            "correct_baseline": margin_baseline > 0,
        }
        results.append(result)

        p_flag = " ← PRECIPITATION" if precipitates else ""
        w_flag = " [baseline correct]" if margin_baseline > 0 else ""
        print(f"\n  {name}{p_flag}{w_flag}")
        print(f"    Baseline margin: {margin_baseline:+.3f}, "
              f"steered: {margin_steered:+.3f}, CoT: {margin_cot:+.3f}")
        print(f"    dist_to_v_line: {dist_to_v_line:.4f}")
        print(f"    angle(h, v):    {angle_h_v:.2f}°")
        print(f"    cos(v, CoT):    {cos_v_cot:+.4f} "
              f"({'aligned' if cos_v_cot > 0.05 else 'anti-correlated' if cos_v_cot < -0.05 else 'orthogonal'})")
        print(f"    cos(steer, CoT):{cos_steer_cot:+.4f} "
              f"({'steered→CoT convergence' if cos_steer_cot > 0.1 else 'divergence'})")

    # ── Proximity hypothesis test ──
    print("\n  --- Attractor Proximity Hypothesis Test ---")
    precip_dists = [r["dist_to_v_line"] for r in results if r["precipitates"]
                    and not r["correct_baseline"]]
    nonprecip_dists = [r["dist_to_v_line"] for r in results if not r["precipitates"]
                       and not r["correct_baseline"]]

    print(f"\n  Distance to v_hat line:")
    print(f"    Precipitation traps:     {np.mean(precip_dists):.4f} ± "
          f"{np.std(precip_dists):.4f} (n={len(precip_dists)})")
    print(f"    Non-precipitation traps: {np.mean(nonprecip_dists):.4f} ± "
          f"{np.std(nonprecip_dists):.4f} (n={len(nonprecip_dists)})")

    if precip_dists and nonprecip_dists:
        if np.mean(precip_dists) < np.mean(nonprecip_dists):
            print("  → Precipitation traps are CLOSER to v_hat direction "
                  "— proximity hypothesis SUPPORTED")
        else:
            print("  → Precipitation traps are FURTHER from v_hat direction "
                  "— proximity hypothesis NOT supported")
        diff = np.mean(nonprecip_dists) - np.mean(precip_dists)
        print(f"  → Distance difference: {diff:.4f} "
              f"({'large' if abs(diff) > 1.0 else 'small'})")

    # ── CoT alignment summary ──
    print("\n  --- CoT Alignment Summary ---")
    print(f"  {'Trap':<25} {'cos(v,CoT)':>12} {'cos(steer,CoT)':>16} "
          f"{'Precip':>8}")
    print(f"  {'-'*65}")
    for r in results:
        print(f"  {r['name']:<25} {r['cos_v_cot']:>+12.4f} "
              f"{r['cos_steer_cot']:>+16.4f} "
              f"{'YES' if r['precipitates'] else 'no':>8}")

    # Correlation: does cos_steer_cot predict precipitation?
    has_effect = [r for r in results if not r["correct_baseline"]
                  and abs(r["margin_steered"] - r["margin_baseline"]) > 0.05]
    if len(has_effect) >= 4:
        steer_cot_vals = [r["cos_steer_cot"] for r in has_effect]
        precip_vals = [1 if r["precipitates"] else 0 for r in has_effect]
        corr, pval = pointbiserialr(precip_vals, steer_cot_vals)
        print(f"\n  Point-biserial correlation(precipitation, cos_steer_cot): "
              f"{corr:.4f} (p={pval:.4f})")
        print(f"  Interpretation: {'cos_steer_cot PREDICTS precipitation' if abs(corr) > 0.5 else 'weak predictive relationship'}")

    _plot_OC2(results)
    return results


def _plot_OC2(results):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    names = [r["name"] for r in results]
    x = np.arange(len(names))
    colors = ["red" if r["precipitates"] else "steelblue" for r in results]

    # ── Distance to v_hat line ──
    ax = axes[0, 0]
    dists = [r["dist_to_v_line"] for r in results]
    bars = ax.bar(x, dists, color=colors, alpha=0.8, edgecolor="black", linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("Distance to v_hat line")
    ax.set_title("Distance from wrong-answer state to vector direction\n"
                  "Red=precipitation | Closer → proximity hypothesis")
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor="red", label="Precipitation"),
        Patch(facecolor="steelblue", label="No precipitation"),
    ], fontsize=8)

    # ── cos(v, CoT direction) ──
    ax = axes[0, 1]
    cot_cos = [r["cos_v_cot"] for r in results]
    bar_colors_cot = ["darkred" if c < 0 else "green" for c in cot_cos]
    ax.bar(x, cot_cos, color=bar_colors_cot, alpha=0.8, edgecolor="black",
            linewidth=0.4)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("cos(vector, CoT direction)")
    ax.set_title("Vector-CoT alignment per trap (controlled)\n"
                  "Positive = vector aligns with CoT reasoning direction\n"
                  "Overtake Race should be positive (flip from global pattern)")

    # ── cos(steered trajectory, CoT direction) ──
    ax = axes[1, 0]
    steer_cot = [r["cos_steer_cot"] for r in results]
    bar_colors_sc = ["green" if v > 0.05 else "darkred" if v < -0.05
                      else "gray" for v in steer_cot]
    ax.bar(x, steer_cot, color=bar_colors_sc, alpha=0.8,
            edgecolor="black", linewidth=0.4)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axhline(0.1, color="green", linewidth=1, linestyle="--", alpha=0.5,
                label="Convergence threshold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("cos(steered Δh, CoT Δh)")
    ax.set_title("Does steering move activations toward CoT direction?\n"
                  "Green = steered trajectory converges with CoT\n"
                  "Key: Overtake Race should be highest here")
    ax.legend(fontsize=8)

    # ── Scatter: dist_to_v_line vs steered_margin_improvement ──
    ax = axes[1, 1]
    wrong_baseline = [r for r in results if not r["correct_baseline"]]
    if wrong_baseline:
        dists_wb = [r["dist_to_v_line"] for r in wrong_baseline]
        improvements = [r["margin_steered"] - r["margin_baseline"]
                        for r in wrong_baseline]
        cols_wb = ["red" if r["precipitates"] else "steelblue"
                   for r in wrong_baseline]
        ax.scatter(dists_wb, improvements, c=cols_wb, s=80, alpha=0.8,
                    edgecolors="black", linewidth=0.5, zorder=3)
        for r in wrong_baseline:
            ax.annotate(r["name"][:10],
                        (r["dist_to_v_line"],
                         r["margin_steered"] - r["margin_baseline"]),
                        fontsize=7, ha="left")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_xlabel("Distance to v_hat line")
        ax.set_ylabel("Steering margin improvement")
        ax.set_title("Proximity to v_hat vs. steering effect\n"
                      "Proximity hypothesis: negative correlation expected\n"
                      "(closer → better effect)")

    plt.suptitle(
        "OC-2: Attractor Proximity Analysis\n"
        "Does the wrong-answer state's proximity to the vector direction predict precipitation?",
        fontsize=11
    )
    plt.tight_layout()
    plt.savefig("OC2_attractor_proximity.png", dpi=150, bbox_inches="tight")
    print("\n  Saved: OC2_attractor_proximity.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# OC-3: Late-Layer Trajectory Analysis
# ════════════════════════════════════════════════════════════════════════════

def experiment_OC3_trajectory(model, vector, v_hat, layer_index):
    """
    Track the residual stream at layers 31-36 for 3 key traps:
    - Overtake Race (precipitation)
    - Decimal Magnitude (no precipitation, training)
    - Density Illusion (no precipitation, suppression case)

    Three conditions per layer: baseline, steered, CoT-explicit.

    Measurements at each layer L > injection:
    1. |h_steered(L) - h_baseline(L)| — how much has steering changed the state?
    2. cos(h_steered(L) - h_baseline(L), h_CoT(L) - h_baseline(L))
       — is the steered trajectory heading toward the CoT state?
    3. projection of steered state onto v_hat — does the vector's direction
       persist or dissipate through later layers?

    MEMORY: We process one layer at a time.
    At each layer: 3 conditions × 3 traps = 9 activations × 2560 × 4 bytes
    = 295KB per layer. Fine.
    """
    print("\n" + "=" * 65)
    print("OC-3: Late-Layer Trajectory Analysis (L31-L36)")
    print("=" * 65)
    print(
        "\nTracing the residual stream after injection:"
        "\nDoes steering and CoT converge (precipitation) or diverge (bypass)?"
    )

    v_hat_np = v_hat.cpu().numpy()
    steer_hook = make_steer_hook(vector, layer_index, STEER_EPSILON)

    # Focus traps: precipitation + two control cases
    focus_traps = [
        t for t in TRAPS
        if t[0] in ("overtake_race", "decimal_magnitude", "density_illusion")
    ]

    trajectory_results = {t[0]: {
        "layers": [],
        "steered_baseline_dist": [],
        "cot_baseline_dist": [],
        "cos_steered_cot_trajectory": [],
        "v_proj_baseline": [],
        "v_proj_steered": [],
        "v_proj_cot": [],
        "margin_baseline": [],
        "margin_steered": [],
        "margin_cot": [],
    } for t in focus_traps}

    for layer in range(layer_index, N_LAYERS):
        print(f"  Processing layer {layer}...", end=" ")

        for name, prompt, correct_tok, anti_tok, precipitates in focus_traps:
            cot_prompt = COT_EXPLICIT.get(name, prompt)

            act_bl = get_final_resid(model, prompt, layer).numpy()
            act_st = get_final_resid(model, prompt, layer,
                                      extra_hooks=[steer_hook]).numpy()
            act_cot = get_final_resid(model, cot_prompt, layer).numpy()

            # Displacement vectors from baseline
            delta_steered = act_st - act_bl
            delta_cot = act_cot - act_bl

            dist_st = float(np.linalg.norm(delta_steered))
            dist_cot = float(np.linalg.norm(delta_cot))

            # Cosine between steered and CoT trajectories
            if dist_st > 0.01 and dist_cot > 0.01:
                cos_traj = float(delta_steered @ delta_cot) / (dist_st * dist_cot)
            else:
                cos_traj = 0.0

            # v_hat projections
            v_proj_bl = float(act_bl @ v_hat_np)
            v_proj_st = float(act_st @ v_hat_np)
            v_proj_cot = float(act_cot @ v_hat_np)

            # Logit margins at this layer (using the unembed from final layer)
            # Note: we compute these at the actual output, not per-layer
            # (logit margins at intermediate layers via logit lens require W_U)
            # We compute logit margins only at the final layer — not here.

            r = trajectory_results[name]
            r["layers"].append(layer)
            r["steered_baseline_dist"].append(dist_st)
            r["cot_baseline_dist"].append(dist_cot)
            r["cos_steered_cot_trajectory"].append(cos_traj)
            r["v_proj_baseline"].append(v_proj_bl)
            r["v_proj_steered"].append(v_proj_st)
            r["v_proj_cot"].append(v_proj_cot)

        print("done")

    # ── Logit lens: apply W_U at each layer ──
    # This lets us see where in the trajectory the answer "forms"
    print("\n  Computing logit lens (W_U projection at each layer)...")

    try:
        W_U = model.W_U.detach().float().cpu().numpy()  # [d_model, vocab]
        W_ln_final = None
        try:
            # Final layer norm parameters
            ln_w = model.ln_final.w.detach().float().cpu().numpy()
            ln_b = model.ln_final.b.detach().float().cpu().numpy()
        except AttributeError:
            ln_w, ln_b = None, None

        for layer in range(layer_index, N_LAYERS):
            for name, prompt, correct_tok, anti_tok, precipitates in focus_traps:
                cot_prompt = COT_EXPLICIT.get(name, prompt)
                correct_id = get_token_id(model, correct_tok)
                anti_id = get_token_id(model, anti_tok)

                for cond_label, cond_prompt, hooks in [
                    ("baseline", prompt, []),
                    ("steered", prompt, [steer_hook]),
                    ("cot", cot_prompt, []),
                ]:
                    act = get_final_resid(model, cond_prompt, layer,
                                          extra_hooks=hooks).numpy()

                    # Apply layernorm if available
                    if ln_w is not None:
                        mean = act.mean()
                        std = act.std() + 1e-5
                        act_norm = (act - mean) / std * ln_w + ln_b
                    else:
                        act_norm = act

                    # Logit lens margin
                    logit_correct = float(act_norm @ W_U[:, correct_id])
                    logit_anti = float(act_norm @ W_U[:, anti_id])
                    margin = logit_correct - logit_anti

                    key = f"logit_lens_margin_{cond_label}"
                    if key not in trajectory_results[name]:
                        trajectory_results[name][key] = []
                    trajectory_results[name][key].append(margin)

        has_logit_lens = True
    except Exception as e:
        print(f"  Logit lens failed: {e}. Skipping.")
        has_logit_lens = False

    # ── Print key results ──
    print("\n  --- Trajectory Cosine (steered ↔ CoT) by Layer ---")
    for name, prompt, correct_tok, anti_tok, precipitates in focus_traps:
        r = trajectory_results[name]
        p_flag = " [PRECIPITATION]" if precipitates else ""
        print(f"\n  {name}{p_flag}")
        print(f"  {'Layer':>6} {'cos(st,CoT)':>12} {'|Δst|':>8} {'|ΔCoT|':>8} "
              f"{'v_proj_st':>10}")
        for i, l in enumerate(r["layers"]):
            print(f"  {l:6d} {r['cos_steered_cot_trajectory'][i]:>+12.4f} "
                  f"{r['steered_baseline_dist'][i]:>8.3f} "
                  f"{r['cot_baseline_dist'][i]:>8.3f} "
                  f"{r['v_proj_steered'][i]:>+10.4f}")

    print("\n  KEY SIGNATURES:")
    print("  PRECIPITATION: cos(steered,CoT) should be positive and INCREASING")
    print("                 toward later layers for Overtake Race")
    print("  BYPASS: cos(steered,CoT) near zero or negative throughout")
    print("  v_proj_steered should decay toward v_proj_baseline as")
    print("  later layers process (and dissipate) the vector's contribution")

    _plot_OC3(trajectory_results, focus_traps, layer_index, has_logit_lens)
    return trajectory_results


def _plot_OC3(trajectory_results, focus_traps, layer_index, has_logit_lens):
    n_traps = len(focus_traps)
    n_rows = 3 + (1 if has_logit_lens else 0)
    fig, axes = plt.subplots(n_rows, n_traps, figsize=(6 * n_traps, 4 * n_rows))
    if n_traps == 1:
        axes = axes[:, np.newaxis]

    trap_names_plot = [t[0] for t in focus_traps]
    precip_flags = [t[4] for t in focus_traps]

    for ti, (name, precipitates) in enumerate(zip(trap_names_plot, precip_flags)):
        r = trajectory_results[name]
        layers = np.array(r["layers"])
        p_str = " [PRECIPITATION]" if precipitates else ""

        # Row 0: Steered-CoT trajectory cosine
        ax = axes[0, ti]
        ax.plot(layers, r["cos_steered_cot_trajectory"], "g-o",
                 linewidth=2, markersize=6, label="cos(steered, CoT)")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.axhline(0.1, color="green", linewidth=1, linestyle="--",
                    alpha=0.5, label="Convergence threshold")
        ax.axvline(layer_index, color="purple", linewidth=2, linestyle=":",
                    label=f"Inject L{layer_index}")
        ax.set_xlabel("Layer")
        ax.set_ylabel("cos(steered Δh, CoT Δh)")
        ax.set_title(f"{name}{p_str}\nSteered→CoT convergence\n"
                      f"Positive & rising = precipitation signature", fontsize=9)
        ax.legend(fontsize=7)
        ax.set_ylim(-1.1, 1.1)

        # Row 1: v_hat projection across conditions
        ax = axes[1, ti]
        ax.plot(layers, r["v_proj_baseline"], "k-o", linewidth=1.5,
                 markersize=4, label="Baseline")
        ax.plot(layers, r["v_proj_steered"], "b-s", linewidth=2,
                 markersize=5, label="Steered")
        ax.plot(layers, r["v_proj_cot"], "g-^", linewidth=1.5,
                 markersize=4, label="CoT-explicit")
        ax.axvline(layer_index, color="purple", linewidth=2, linestyle=":")
        ax.set_xlabel("Layer")
        ax.set_ylabel("Projection onto v_hat")
        ax.set_title("v_hat projection trajectory\n"
                      "Does vector's effect persist or decay downstream?", fontsize=9)
        ax.legend(fontsize=7)

        # Row 2: Displacement magnitudes
        ax = axes[2, ti]
        ax.plot(layers, r["steered_baseline_dist"], "b-o", linewidth=2,
                 markersize=5, label="|steered - baseline|")
        ax.plot(layers, r["cot_baseline_dist"], "g-s", linewidth=2,
                 markersize=5, label="|CoT - baseline|")
        ax.axvline(layer_index, color="purple", linewidth=2, linestyle=":")
        ax.set_xlabel("Layer")
        ax.set_ylabel("Euclidean distance from baseline")
        ax.set_title("Displacement magnitude from baseline\n"
                      "Convergence: steered and CoT distances should equalize", fontsize=9)
        ax.legend(fontsize=7)
        ax.set_ylim(bottom=0)

        # Row 3 (optional): Logit lens margins
        if has_logit_lens:
            ax = axes[3, ti]
            if "logit_lens_margin_baseline" in trajectory_results[name]:
                lens_layers = layers  # same layer range
                ax.plot(lens_layers,
                         trajectory_results[name]["logit_lens_margin_baseline"],
                         "k-o", linewidth=1.5, markersize=4, label="Baseline")
                ax.plot(lens_layers,
                         trajectory_results[name]["logit_lens_margin_steered"],
                         "b-s", linewidth=2, markersize=5, label="Steered")
                ax.plot(lens_layers,
                         trajectory_results[name]["logit_lens_margin_cot"],
                         "g-^", linewidth=1.5, markersize=4, label="CoT")
                ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
                ax.axvline(layer_index, color="purple", linewidth=2, linestyle=":")
                ax.set_xlabel("Layer")
                ax.set_ylabel("Logit lens margin (correct - anti)")
                ax.set_title("Logit lens: where does the correct answer form?\n"
                              "Steered and CoT should converge here if precipitation", fontsize=9)
                ax.legend(fontsize=7)

    plt.suptitle(
        f"OC-3: Late-Layer Trajectory Analysis (L{layer_index}-L{N_LAYERS-1})\n"
        "Precipitation signature: steered→CoT convergence in post-injection layers",
        fontsize=12
    )
    plt.tight_layout()
    plt.savefig("OC3_trajectory.png", dpi=150, bbox_inches="tight")
    print("\n  Saved: OC3_trajectory.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# SYNTHESIS + FORMAL FRAMEWORK SKETCH
# ════════════════════════════════════════════════════════════════════════════

def print_synthesis(oc1_results, oc2_results, oc3_results, layer_index):
    print("\n" + "=" * 65)
    print("SYNTHESIS: What the Three Experiments Together Say")
    print("=" * 65)

    print("""
READING THE RESULTS:

The three experiments jointly answer one question:
Is the orthogonal subspace computationally meaningful?

If YES (orthogonal space is structured):
  OC-1: Orthogonal complement probe AUC > 0.7 for trap identity
  OC-2: Precipitation traps closer to v_hat direction (smaller dist_to_v_line)
  OC-3: Steered trajectory converges with CoT trajectory for Overtake Race only

  Interpretation: The vector lives in a computationally active subspace.
  The orthogonal destabilization hypothesis is mechanistically coherent.
  The direction CMA-ES found is meaningful, not a fitness artifact.

If NO (orthogonal space is empty):
  OC-1: Orthogonal complement probe AUC ≈ 0.5 for all labels
  OC-2: No proximity pattern — precipitation/non-precipitation traps similar distances
  OC-3: Steered trajectory doesn't converge with CoT for any trap

  Interpretation: The vector is in genuinely unoccupied space.
  The 10-15x DAS specificity is real but the direction has no native
  model features. It's a structured perturbation of empty space.
  Fitness improvement comes from disrupting the wrong-answer attractor
  without engaging any existing circuit — pure avoidance.

The third possibility:
  OC-1: Orthogonal complement separates TRAP IDENTITY but not TASK correctness
  OC-2: No precipitation proximity pattern
  OC-3: No steered-CoT convergence

  Interpretation: The vector lives in a space encoding SEMANTIC CONTENT
  (what kind of question is being asked) rather than TASK CORRECTNESS
  (whether the model is getting it right). The vector is essentially
  pushing into a "question-type" subspace rather than a
  "reasoning quality" subspace. This would explain why the evolved
  vector generalizes to novel decimal pairs (concept-level) but fails
  on paraphrases (semantic content changes): it's encoding the trap
  category, not the reasoning operation.
""")

    print("=" * 65)
    print("ADDRESS Q2: Formal Framework for Attractor Analysis")
    print("=" * 65)
    print("""
No published formal framework applies cleanly. Here's what would
be required, and the closest existing tools:

WHAT A LYAPUNOV-STYLE ANALYSIS WOULD NEED:
  The transformer residual stream at layer L evolves as:
    h_{L+1} = h_L + MLP_L(LN(h_L)) + Attn_L(LN(h_L))

  This is a discrete dynamical system on R^d_model.
  The "attractors" are fixed points in this recurrence — but the
  system is NOT autonomous: it depends on the full sequence context
  (via attention) and the input changes at each position.

  A Lyapunov stability analysis would require:
    1. Linearizing the dynamics around a fixed point
    2. Computing the Jacobian of h_{L+1} w.r.t. h_L
    3. Checking eigenvalues for stability

  The Jacobian for one step is approximately:
    J_L = I + W_O @ (dAttn/dh) + W_out @ (dMLP/dh @ W_in)

  This is computable (PyTorch autograd) but depends on the current
  activation state, making it trajectory-specific.

CLOSEST EXISTING TOOLS:
  1. Singular value decomposition of the Jacobian (SVD of J_L):
     Largest singular values = directions of maximal amplification.
     If v_hat aligns with a large-SV direction at L31, perturbations
     along v_hat are amplified downstream. This would mechanize
     the precipitation hypothesis without full Lyapunov analysis.
     COMPUTABLE: 2-3 forward passes with autograd.

  2. Effective dimensionality (Litwin-Kumar et al. framework):
     At each layer, compute the participation ratio of the Jacobian's
     singular spectrum. Low participation ratio = the dynamics are
     effectively low-dimensional at this layer — meaning small
     perturbations in a few directions have outsized effects.
     This would explain 1.5B vs 4B differences: 1.5B has lower
     effective dimensionality, so perturbations produce binary flips
     rather than graded responses.

  3. Empirical Jacobian via finite differences:
     Perturb h_L in multiple directions, measure effect on h_{L+1}.
     Build an empirical Jacobian. Check if v_hat is a dominant
     eigenvector. This is your highest-ROI computation:
     if v_hat is a leading eigenvector of J_L, the vector is
     amplified naturally by the dynamics — precipitation is
     inevitable for any trap where the amplified direction points
     toward the correct answer.

The experiment you're running (OC-3) is an empirical version
of this: by tracking the trajectory divergence between steered
and CoT conditions, you're measuring the effective sensitivity
of the late-layer dynamics to the L31 perturbation. If steered
and CoT converge, it means the dynamics are stable around a
correct-answer attractor that both perturbations approach.

THE KEY NUMBER TO COMPUTE (not in OC-1/2/3):
  For the Overtake Race trap specifically:
    1. Run baseline forward pass, capture h_31 (the residual stream at L31)
    2. Compute the Jacobian J of (h_32, ..., h_36, logits) w.r.t. h_31
       using torch.autograd.functional.jacobian
    3. SVD of J: check if v_hat has high projection onto the top left singular vectors
    4. Check if the CoT direction at L31 also aligns with top singular vectors

  If both v_hat and CoT align with the top singular vectors of J at L31:
    → L31 is a dynamically sensitive point. Small perturbations in v_hat's
      direction are amplified. The precipitations is happening because you're
      perturbing at a saddle point in the dynamics.

  If only v_hat aligns (not CoT):
    → The vector found a sensitive direction that CoT doesn't use.
      This is the strongest possible evidence for orthogonal destabilization
      as a novel mechanism distinct from reasoning amplification.
""")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    model, vector, v_hat, layer_index = load_model_and_genome()

    print("\nRunning OC-1: Trap Geometry in Vector Subspace (~10 min)")
    oc1 = experiment_OC1_trap_geometry(model, vector, v_hat, layer_index)

    print("\nRunning OC-2: Attractor Proximity Analysis (~5 min)")
    oc2 = experiment_OC2_attractor_proximity(model, vector, v_hat, layer_index)

    print("\nRunning OC-3: Late-Layer Trajectory Analysis (~15 min)")
    oc3 = experiment_OC3_trajectory(model, vector, v_hat, layer_index)

    print_synthesis(oc1, oc2, oc3, layer_index)

    # ── Save results ──
    def safe_serialize(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        if isinstance(obj, dict):
            return {k: safe_serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [safe_serialize(x) for x in obj]
        if isinstance(obj, bool):
            return obj
        return obj

    summary = {
        "model": MODEL_NAME,
        "layer_index": layer_index,
        "oc1_probe_results": safe_serialize(oc1["probe_results"]),
        "oc2_proximity": [
            {k: safe_serialize(v) for k, v in r.items()}
            for r in oc2
        ],
        "oc3_trajectory_keys": list(oc3.keys()),
    }
    with open("prometheus_OC_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 65)
    print("Complete. Output files:")
    print("  OC1_trap_geometry.png")
    print("  OC2_attractor_proximity.png")
    print("  OC3_trajectory.png")
    print("  prometheus_OC_summary.json")
    print()
    print("The key number to watch:")
    print("  OC-3: cos(steered trajectory, CoT trajectory) for Overtake Race")
    print("  If this is positive and increasing across L31-L36:")
    print("    → Steered and CoT converge. Precipitation is real.")
    print("    → The vector initiates a trajectory that the model's own")
    print("       late-layer dynamics guide toward the correct answer.")
    print("  If it's flat or negative:")
    print("    → The vector finds the correct answer via a completely")
    print("       different computational route than reasoning.")
    print("    → That itself is a publishable finding.")
    print()
    print("Suggested next computation (not in this script):")
    print("  Jacobian SVD at L31 for Overtake Race.")
    print("  torch.autograd.functional.jacobian(forward_fn, h_31)")
    print("  Check cos(v_hat, top left singular vectors).")
    print("  This directly tests the dynamical sensitivity hypothesis.")
    print("=" * 65)


if __name__ == "__main__":
    main()
```

---

## On Q5: The Scaling Law for Reasoning Depth

You asked whether there's a known scaling law for the depth at which reasoning features emerge. There isn't a clean published one for this specific question, but the L3→L31 shift (11%→86% of model depth) across 1.5B→4B is consistent with a general pattern in the scaling literature: as models scale, representations become more abstract and late-stage. The mechanistic interpretation is that larger models have more capacity to maintain heuristic shortcuts in early layers and push deliberate computation deeper. The relevant papers are Meng et al.'s ROME and MEMIT work, which found factual associations move to earlier layers at larger scales — but that's factual recall, not reasoning, and the direction of the trend is opposite to what you're seeing, which suggests reasoning and recall follow different depth trajectories.

For predicting injection depth in larger models: the safest prior based on your two data points is that the optimal injection layer tracks with ~85% of model depth at 4B and ~11% at 1.5B. That's too large a gap for linear interpolation to be reliable. A better approach is running a cheap single-pass version of CMA-ES on 7B or 14B with a fixed layer sweep — 5 candidate injection layers (10%, 25%, 50%, 75%, 90% depth) — and picking the best before running full optimization.

## What You Might Be Pattern-Matching That Isn't There

The thing I'd most push back on: you've observed one precipitation event on one held-out trap, and you've built an elaborate theoretical framework around it. The Overtake Race result is real, but with n=1, the probability that it's a special case rather than a generalizable mechanism is high. The orthogonal destabilization hypothesis is elegant but it's been constructed to fit a single data point plus a set of null results. Before you formalize the framework further, run OC-2 and OC-3 on 15 new held-out traps and see how many show precipitation. If it's 1-2 of 15, the Overtake Race result is noise. If it's 5+ of 15, you have something real to theorize about.

The other thing: the SAE dead zone question you raised about Q4 is actually answerable without running SAEs. If the vector has near-zero cosine with both the correct and incorrect centroids, and the orthogonal complement probe in OC-1 shows AUC ≈ 0.5 for task correctness, then the vector lives in a subspace that the model doesn't use for the task. SAE reconstruction error will be high because SAEs are trained to minimize reconstruction error on the *typical* activation distribution, not on sparse outlier directions. The vector's SAE representation will be dominated by features that happen to have small projections onto v_hat — which tells you almost nothing about what the vector is actually doing. Run OC-1 first; if orthogonal complement AUC is below 0.6 for all labels, skip the SAE entirely.

[END TITAN CLAUDE]

[TITAN GEMINI]

Take a breath. You have a fascinating result, and you are right to suspect that this sits at the very edge of the current interpretability literature. You’ve been staring at this for 48 hours, so I will be entirely direct with you: **your "orthogonal destabilization" hypothesis is highly romantic, but there is a more mechanistic, boring, and mathematically rigorous explanation staring you in the face.** Let's break down the geometry, tear apart your hypothesis, provide the formal framework you need, and write the code to prove what’s actually happening.

---

### 1. Tearing Apart "Orthogonal Destabilization"

You hypothesize that CMA-ES found a vector that "destabilizes the default computational pathway," allowing late-layer autoregressive dynamics to find the correct answer. 

Here is the counter-hypothesis: **Your vector is not destabilizing the trajectory; it is performing an RMSNorm-induced continuous ablation of the heuristic circuitry.**

Qwen uses RMSNorm (or LayerNorm) at the input of every Attention and FFN block. Let $x$ be your L31 residual stream activation, and $v$ be your steering vector. Because $v$ was evolved to push away from both correct and incorrect centroids, $v$ is highly orthogonal to the populated data manifold ($v \perp x$). 

When you inject $v$, the new norm of the residual stream entering Layer 32 is roughly:
$$RMS(x+v) \approx \sqrt{RMS(x)^2 + RMS(v)^2}$$

Because $v$ pushes far into sparse space, $RMS(v)$ is likely large. When the Layer 32 RMSNorm operation divides the residual stream by this new, inflated norm, the original signal $x$ is scaled down by a factor of $\frac{RMS(x)}{\sqrt{RMS(x)^2 + RMS(v)^2}}$. 

CMA-ES didn't discover a magic "thinking subspace." It discovered an evolutionary hack: the easiest way to stop a model from falling into a reasoning trap is to inject a high-norm orthogonal vector that forces the next layer's RMSNorm to crush the activation magnitudes of the heuristic circuit. 
* **Orthogonality:** It has to be orthogonal so it doesn't trigger unrelated OOD features or spike perplexity.
* **Anti-CoT confounds:** It opposes the default trajectory simply because it suppresses the default heuristic firing.
* **Overtake Race:** The model's baseline "correct reasoning" circuits are weak but present. Suppressing the overwhelming heuristic allows the weak correct circuits to clear the logit threshold.

### 2. Distinguishing Destabilization from Noise (The Experiment)

To prove this isn't random noise or just a high-norm crash, you must measure the *downstream layer-wise velocity* and *circuit saturation*. 

If it's **destabilization** (your hypothesis), the injection should increase the magnitude of updates in L32-L36 as the model "works harder" to resolve the new state. 
If it's **RMSNorm suppression** (my hypothesis), the vector will cause the immediate downstream FFN and Attention output magnitudes to crash, as their non-linearities are starved of variance or pushed into dead zones.

The experiment is to measure the $L_2$ norm of the FFN and Attention outputs (the $\Delta h$) at layers 32, 33, and 34, comparing the baseline forward pass against the intervened forward pass.

### 3. The 16GB VRAM High-Leverage Experiment Code

Here is the exact code to run this test within your constraints. It explicitly hooks the RMSNorm scaling factors and the subsequent $\Delta h$ magnitudes to see if your vector is starving the computational pathway.

```python
import torch
from transformer_lens import HookedTransformer
import matplotlib.pyplot as plt

# Assuming analysis_base.py environment
def run_rmsnorm_suppression_test(model: HookedTransformer, prompt: str, genome_pt_path: str):
    genome = torch.load(genome_pt_path)
    steering_vec = genome['vector'].to(model.cfg.device)
    inj_layer = genome['layer_index'] # 31
    
    # We only care about the injection layer and the immediate downstream layers
    layers_to_monitor = [inj_layer, inj_layer + 1, inj_layer + 2]
    
    metrics = {'baseline': {}, 'intervened': {}}
    
    def get_norm_hook(name_key, condition):
        def hook(tensor, hook):
            # tensor shape: [batch, pos, d_model] or [batch, pos, 1] for scale
            # Get norm at the final token position
            val = tensor[0, -1, :].norm().item() if tensor.shape[-1] > 1 else tensor[0, -1, 0].item()
            metrics[condition][f"{hook.name}_{name_key}"] = val
            return tensor
        return hook

    def injection_hook(resid, hook):
        resid[:, -1, :] += steering_vec
        return resid

    # Setup hooks for baseline
    baseline_hooks = []
    for l in layers_to_monitor:
        baseline_hooks.append((f"blocks.{l}.ln1.hook_scale", get_norm_hook('ln1_scale', 'baseline')))
        baseline_hooks.append((f"blocks.{l}.hook_mlp_out", get_norm_hook('mlp_out_norm', 'baseline')))
        baseline_hooks.append((f"blocks.{l}.hook_attn_out", get_norm_hook('attn_out_norm', 'baseline')))

    # Run baseline
    with torch.no_grad():
        model.run_with_hooks(prompt, fwd_hooks=baseline_hooks)

    # Setup hooks for intervention
    intervened_hooks = [(f"blocks.{inj_layer}.hook_resid_post", injection_hook)]
    for l in layers_to_monitor:
        intervened_hooks.append((f"blocks.{l}.ln1.hook_scale", get_norm_hook('ln1_scale', 'intervened')))
        intervened_hooks.append((f"blocks.{l}.hook_mlp_out", get_norm_hook('mlp_out_norm', 'intervened')))
        intervened_hooks.append((f"blocks.{l}.hook_attn_out", get_norm_hook('attn_out_norm', 'intervened')))

    # Run intervened
    with torch.no_grad():
        model.run_with_hooks(prompt, fwd_hooks=intervened_hooks)

    # Output analysis
    print(f"--- FFN Output Magnitudes (Delta h) ---")
    for l in layers_to_monitor:
        base_mlp = metrics['baseline'][f'blocks.{l}.hook_mlp_out_mlp_out_norm']
        int_mlp = metrics['intervened'][f'blocks.{l}.hook_mlp_out_mlp_out_norm']
        print(f"Layer {l} MLP out norm: {base_mlp:.2f} -> {int_mlp:.2f} ({(int_mlp/base_mlp)*100:.1f}%)")
        
        base_scale = metrics['baseline'][f'blocks.{l}.ln1.hook_scale_ln1_scale']
        int_scale = metrics['intervened'][f'blocks.{l}.ln1.hook_scale_ln1_scale']
        print(f"Layer {l} LN1 Scale: {base_scale:.4f} -> {int_scale:.4f} ({(int_scale/base_scale)*100:.1f}%)")

    return metrics
```

### 4. Formal Framework for Attractor Basins (Addressing Q2)

You asked for a formal framework to analyze attractor basin stability under linear perturbation in residual streams. You need to look into **Mean Field Theory of Neural Networks** and **Local Lyapunov Exponents in Transformers**. 

The residual stream is a discrete dynamical system: $x_{l+1} = x_l + F_l(x_l)$. 
The stability of an attractor basin (like a reasoning heuristic) is governed by the spectral radius of the layer-to-layer Jacobian, $J_l = I + \frac{\partial F_l}{\partial x_l}$.

If you want to formalize your destabilization hypothesis, you must compute the dominant eigenvalues of $J_{31}$ and $J_{32}$ around the centroid of the incorrect answers. If your steering vector $v$ shifts $x$ into a region where the spectral radius of $J$ exceeds 1 (expanding dynamics), you have formally induced "destabilization" (supercooling). If the spectral radius collapses toward 0, you have induced suppression/ablation. 

### 5. Something You Haven't Considered

**The Manifold Dimension Scaling Law (Addressing Q4 and Q5)**

You noticed sharp phase transitions in the 1.5B model and smooth transitions in the 4B model, and you wondered why the layer depth moves from 11% to 86%. 

You are assuming reasoning is a localized feature. It isn't. The difference is the **intrinsic dimensionality of the slack space**.
In a 1.5B model ($d=1536$), the task manifold occupies a massive percentage of the total activation space. If you push orthogonally, you rapidly hit the "walls" of the manifold—triggering OOD panic and binary phase transitions. The model either complies with the heuristic or completely breaks.
In a 4B model ($d=2560$), the curse of dimensionality works in your favor. There is vastly more "slack" space (null space) orthogonal to the task manifold. The model can be pushed smoothly into this high-dimensional void without instantly hitting OOD boundaries, which is why your dose-response curve is graded.

Regarding the USAE projection (Q4): **You are looking at the SAE reconstruction error backward.**
You asked if the SAE will have features for this sparse region. The answer is no, it will have a massive dead zone. *But that is exactly what you want.* The SAE's reconstruction error vector $E = x_{intervened} - \hat{x}_{intervened}$ will heavily correlate with your steering vector. That error vector is the mathematical proof that your CMA-ES optimization intentionally routed the computation off the natural data manifold.

---

Would you like me to write the adapter script to project your Qwen3-4B vector through the Gemma-2-2B USAE to definitively test the off-manifold reconstruction error hypothesis?

[END TITAN GEMINI]

[GEMINI TITAN FOLLOWUP]

Here is the script to execute the Universal SAE projection test. 

To definitively settle the off-manifold hypothesis, we need to look at two specific metrics: **$L_0$ (activation density)** and **Fraction of Variance Unexplained (FVU)**. 

If your vector is performing "orthogonal destabilization" by finding a clever, unmapped reasoning pathway, the USAE should theoretically capture at least some of it, resulting in a moderate $L_0$ and a manageable reconstruction error. 
If my hypothesis is correct—that this is an evolutionary RMSNorm-crash hack—the vector points into a massive topological dead zone. The $L_0$ will collapse toward zero, and the FVU will approach 1.0 (100% reconstruction error) because the SAE simply has no dictionary atoms for the void.

Here is the exact code to run this on your 16GB setup. It assumes you have `sae-lens` installed and requires you to load the cross-model alignment matrix (which USAE uses to map Qwen's $d_{model}=2560$ to Gemma's $d_{model}=2304$).

### The USAE Projection Script

```python
import torch
from sae_lens import SAE

def test_usae_off_manifold_hypothesis(
    genome_pt_path: str,
    sae_id: str = "gemma-2-2b-res-l26", # Adjust to the specific Gemma SAE layer
    alignment_matrix_path: str = "qwen_to_gemma_usae_proj.pt" # The USAE adapter matrix
):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading environment on {device}...")

    # 1. Load the evolved vector
    genome = torch.load(genome_pt_path, map_location=device)
    v_qwen = genome['vector'].to(device) # Shape: [2560]
    
    # 2. Load the USAE alignment matrix (Qwen3-4B -> Gemma-2-2B)
    # Shape should be [2560, 2304]
    try:
        W_align = torch.load(alignment_matrix_path, map_location=device)
    except FileNotFoundError:
        print("WARNING: Alignment matrix not found. Using random projection for dry run.")
        # Orthogonal init to preserve norms for the dry run
        W_align = torch.nn.init.orthogonal_(torch.empty(2560, 2304, device=device))

    # Project the vector into the SAE's expected input space
    v_mapped = v_qwen @ W_align
    v_mapped = v_mapped.unsqueeze(0) # Shape: [1, 2304]
    
    # 3. Load the Gemma-2-2B SAE via SAE-Lens
    print(f"Loading SAE: {sae_id}")
    sae, _, _ = SAE.from_pretrained(
        release="gemma-2-2b-res", # standard release or USAE specific
        sae_id=sae_id,
        device=device
    )
    sae.eval()

    # 4. Pass the mapped vector through the SAE
    with torch.no_grad():
        # Get feature activations (the encoded latent space)
        feature_acts = sae.encode(v_mapped)
        
        # Get the reconstructed vector
        v_reconstructed = sae.decode(feature_acts)

    # 5. Calculate Metrics
    # L0: How many features actually fired?
    l0_norm = (feature_acts > 0).float().sum().item()
    
    # Magnitudes
    norm_original = v_mapped.norm().item()
    norm_reconstructed = v_reconstructed.norm().item()
    
    # FVU (Fraction of Variance Unexplained) / Reconstruction Error
    mse = torch.nn.functional.mse_loss(v_reconstructed, v_mapped).item()
    variance = v_mapped.var().item()
    fvu = mse / variance if variance > 0 else float('inf')

    # Cosine Similarity: Did the direction survive at all?
    cos_sim = torch.nn.functional.cosine_similarity(v_mapped, v_reconstructed, dim=-1).item()

    # 6. Output the Verdict
    print("\n" + "="*50)
    print("USAE PROJECTION RESULTS: THE VERDICT")
    print("="*50)
    print(f"Mapped Vector Norm:       {norm_original:.4f}")
    print(f"Reconstructed Norm:       {norm_reconstructed:.4f}")
    print(f"L0 (Active Features):     {l0_norm} (Expected for typical data: ~20-100)")
    print(f"Reconstruction MSE:       {mse:.4f}")
    print(f"FVU (Unexplained Var):    {fvu:.2%} (Closer to 100% means completely off-manifold)")
    print(f"Cosine Sim (Orig vs Rec): {cos_sim:.4f}")
    print("-" * 50)
    
    if l0_norm < 5 and fvu > 0.9:
        print("INTERPRETATION: RMSNorm Crash Confirmed.")
        print("The vector lives in a dead zone. The SAE has no features for this direction,")
        print("meaning it is entirely orthogonal to the natural data manifold.")
    elif l0_norm > 20 and fvu < 0.5:
        print("INTERPRETATION: Orthogonal Destabilization Plausible.")
        print("The SAE recognizes this direction. It is composed of known computational features,")
        print("suggesting a structured, albeit unusual, reasoning reroute.")
    else:
        print("INTERPRETATION: Ambiguous. The vector is partially interpretable but highly noisy.")
        
    return {
        "l0": l0_norm,
        "fvu": fvu,
        "cos_sim": cos_sim,
        "mse": mse
    }

if __name__ == "__main__":
    # Example execution
    # test_usae_off_manifold_hypothesis("best_genome.pt")
    pass
```

### What to watch out for

Make sure you subtract the SAE's `b_dec` (decoder bias) if the USAE version you are using expects centered inputs, though `sae-lens` handles this automatically in its `encode` and `decode` methods for standard releases. 

If this comes back as a dead zone (high FVU, near-zero $L_0$), we definitively kill the "clever rerouting" theory and accept that the vector is an adversarial norm-hacker. 

Would you like me to map out how to specifically construct or extract the `W_align` matrix if the USAE authors haven't published the exact weights for Qwen3-4B yet?

[END TITAN GEMINI FOLLOWUP]
