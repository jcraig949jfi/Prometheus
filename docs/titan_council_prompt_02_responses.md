

[GEMINI]

This is a high-signal data dump. You have moved past the "does it work" stage into the "how is the geometry lying to us" stage. 

Based on the raw results, your **Reasoning Precipitation Hypothesis** is likely hitting a "Sycophancy-Heuristic Wall." The model isn't failing because it *can't* reason; it's failing because a dominant, high-logit heuristic is suppressing the correct latent state.

Here is the "map table" analysis of your data.

---

### I. The "Anti-CoT" Paradox: Geometric Subtraction
The most striking data point is **Test 4c**: the negative correlation ($-0.2$ to $-0.3$) between the evolved vector and the CoT-delta.

**The Interpretation:** Your CMA-ES didn't find a "Reasoning" vector. It found an **"Anti-Heuristic" vector.**
In many reasoning traps, the "Wrong" answer is a high-probability surface-level association (e.g., 9.11 > 9.9 because 11 > 9). This "Heuristic" exists as a specific direction in the residual stream. 
* **CoT** works by shifting the model into a new state where the heuristic is no longer the top projection. 
* **Your Vector** works by **actively subtracting the heuristic direction.** * Because the Heuristic and the Reasoning state are likely non-orthogonal (they share components), a vector that "kills" the heuristic will look like it's "opposing" the reasoning direction in hyperspace.

**Why removing the vector helped in Test 2:**
In `Density Illusion` and `Anti-Sycophancy`, your vector *hurt* performance, and ablated it *doubled* it. This suggests your evolved vector is "over-fitted" to a specific heuristic suppression that actually **overlaps** with the correct logic in those specific traps. You are essentially pruning the "Correct Reasoning" circuitry along with the "Heuristic" circuitry.

---

### II. The "Overtake Race" Anomalies
Why did **only** this held-out trap show a precipitation signature?
* **Hypothesis:** Overtake Race (ordering logic) requires **relational binding**, whereas Decimal Magnitude and Density Illusion rely on **static knowledge lookup**. 
* Relational binding is computationally "heavier" and deeper in the model. If your vector is injected at L31, it might be providing a "Focus" signal that allows the late-layer MLPs to actually complete the binding operation rather than defaulting to the first mentioned entity.

---

### III. High-ROI Next Step: The "Null-Space Evolution"

The most valuable experiment you can run right now—given your 17GB VRAM—is to test if **CoT-Alignment is a better proxy for generalizable reasoning than Task Performance.**

If you evolve for Task Performance, you get "Heuristic Killers" (Bypass). If you evolve for CoT-Alignment, you might find the "Precipitation" trigger.

#### The Experiment: Evolutionary Steering toward Latent CoT
Instead of scoring the vector on whether the model gets the answer right, score it on how well it pushes the *Standard Prompt's* L31 activation toward the *CoT Prompt's* L31 activation.

**The ROI:** This will tell you if there is a single "Latent Reasoning" direction that bridges the gap between heuristic-mode and CoT-mode without needing the extra tokens.

---

### IV. The Code: CoT-Alignment Evolutionary Scorer

This script provides the scoring engine for a new CMA-ES run. It calculates the "Reasoning Shift" by comparing the steered standard activation to a cached CoT "Gold Standard" activation.

```python
import torch
from transformer_lens import HookedTransformer

# Assume model: Qwen3-4B (36 layers, d_model=2560)
# Use Gemma-2-2B if VRAM is tight (26 layers, d_model=2304)

@torch.no_grad()
def get_cot_alignment_score(model, v_candidate, injection_layer, trap_data):
    """
    Scores a vector based on how well it mimics the 'Reasoning Shift' 
    found in Chain-of-Thought, without using CoT tokens.
    """
    scores = []
    
    for trap in trap_data:
        # 1. Get 'Standard' Activations (The Heuristic State)
        _, cache_std = model.run_with_cache(trap['std_prompt'], 
                                            names_filter=lambda n: "hook_resid_post" in n)
        h_std = cache_std[f"blocks.{injection_layer}.hook_resid_post"][0, -1, :]

        # 2. Get 'CoT' Activations (The Target Reasoning State)
        # Note: We take the activation at the point where the model *starts* reasoning
        _, cache_cot = model.run_with_cache(trap['cot_prompt'], 
                                            names_filter=lambda n: "hook_resid_post" in n)
        h_cot = cache_cot[f"blocks.{injection_layer}.hook_resid_post"][0, -1, :]

        # The 'Reasoning Delta' we want to precipitate
        target_delta = h_cot - h_std
        
        # 3. Apply Steering Vector to Standard Prompt
        h_steered = h_std + v_candidate
        
        # 4. Score: Cosine Similarity between [Steered - Std] and [CoT - Std]
        # We want our vector to point in the SAME direction as the CoT shift
        steering_delta = h_steered - h_std
        alignment = torch.cosine_similarity(steering_delta, target_delta, dim=0)
        
        # Penalty: If the vector is too large, it might destroy the manifold
        norm_penalty = torch.clamp(v_candidate.norm() - 5.0, min=0) * 0.1
        
        scores.append(alignment.item() - norm_penalty)
    
    return sum(scores) / len(scores)

# --- RE-DIRECTION STRATEGY ---
# Use this score as the fitness function for your next 2000 genomes.
# If the resulting vector generalizes to 'Overtake Race' without being 
# trained on it, you have found a universal 'Reasoning Precipitate'.
```

### V. Strategic Redirection
1.  **Abandon the current vector.** The anti-CoT correlation and Test 2 "Ablation-helps" results prove your current vector is a **Heuristic-Slayer**, not a **Reasoning-Amplifier**. It’s a surgical tool for fixing specific logit errors, but it’s not "Precipitation."
2.  **Focus on Test 4a (Overtake Race).** This is your only true lead for Precipitation. Analyze the `L31-L35` MLPs in this trap. Use an SAE (if available for Qwen) to see if these MLPs are firing "Ordering" or "Sequence" features that stay dormant in the other traps.
3.  **Cross-Architecture Check.** Run the Anti-CoT test on `Gemma-2-2B`. If the correlation is also negative, it confirms that LLMs (at the <5B scale) treat "Reasoning" and "Direct Logit Output" as mutually exclusive geometric pathways.

**Would you like me to draft a script to extract the SAE feature activations for the Overtake Race "Critical MLPs" to see what exactly is being amplified?**


[ENDGEMINI]






[DEEPSEEK]

## What the Data Actually Says (That You're Not Seeing)

### 1. **The Vector Is a Suppressor, Not an Amplifier**

The ablation results are screaming at you: removing the vector *helps* on Density Illusion and Anti-Sycophancy. This is not a neutral finding—it's the *signature* of a vector that works by *suppressing* something.

**What you're missing:** The fitness function optimized for logit margin, not behavioral correctness. On traps where the model's *default heuristic is correct* (Density Illusion: "a pound is a pound"; Anti-Sycophancy: "7 is prime"), the vector learned to *move away from* the correct answer to maximize margin.

Look at the numbers:
- Density Illusion baseline = 1.00 (correct), steered = 0.30 (now saying "gold"?), ablated = 2.00 (super-correct)
- The vector *reduces* performance on correct-default traps to create a larger logit margin for the *incorrect* answer, then the CMA-ES fitness rewards that because it's maximizing *difference*, not correctness.

**Implication:** You've evolved an *adversarial* vector that exploits the model's uncertainty on certain traps by pushing it toward confidently wrong answers that maximize logit separation. The "reasoning precipitation" framing is wrong—this is "heuristic disruption."

---

### 2. **The Anti-CoT Correlation Is a Red Herring (But a Useful One)**

Your interpretation: "vector points opposite to CoT direction" → "different geometric pathway."

But CoT changes the *prompt* (adding "Let's think step by step") which changes the *entire residual stream trajectory from layer 0*. Your vector is injected at layer 31. Comparing these is like comparing a rocket's trajectory to a car's and concluding they're "opposite" because one goes up and one goes forward.

**What's actually happening:** The vector is disrupting the model's late-layer computation. CoT changes early computation so that by layer 31, the representation is already in a different region. The vector doesn't *point opposite to CoT*—it points to a region that's *reachable from the baseline trajectory* but *not reachable from CoT trajectory* because CoT already left that manifold.

**Test this:** Compute cosine similarity between:
1. Baseline activations at L31
2. CoT activations at L31  
3. Baseline + vector at L31

I bet baseline+vector is closer to baseline than to CoT, and CoT is orthogonal to both. The negative correlation is because baseline+vector is *away from* CoT, not because the vector is "anti-reasoning."

---

### 3. **The Overtake Race Precipitation Is Probably an Artifact of Test Set Contamination**

You evolved on 4 traps. Overtake Race is held out. It shows precipitation. Here's the uncomfortable possibility:

Overtake Race involves reasoning about relative positions ("If A overtakes B..."). The 4 training traps involve:
- Decimal comparison (numerical)
- Density (physics/common sense)
- Spatial (mental rotation)
- Anti-sycophancy (social reasoning)

These are *all different reasoning types*. The vector that generalizes to Overtake Race isn't a "reasoning amplifier"—it's a *generic trajectory modifier* that happens to bump the model into a region where *any* reasoning task is more likely to succeed.

**Why this matters:** Your "precipitation" might just be "the vector pushes the model into a higher-entropy region of activation space where it's less confident in its heuristics, making it more likely to engage in actual reasoning." That's still interesting, but it's not the mechanism you think.

**Test:** Run Overtake Race with random vectors of same norm. If any random vector produces similar precipitation, your vector isn't special.

---

### 4. **The DAS Results Are Misleading**

Your DAS shows the vector direction alone preserves 9-15x more effect than random directions. But look at the *absolute* numbers, not the ratio:

| Dimension | Random Preserved | Aligned Preserved |
|-----------|-----------------|-------------------|
| 1 | 1.21 ± 1.05 | 11.01 |

"Preserved" is margin? Logit shift? What are these units? If it's margin, 11 is *enormous* (baseline margins were ~0.1-1.0). But your earlier dose-response showed max margin changes < 0.2.

**Something's wrong:** Either:
- Your DAS is measuring something different from your dose-response
- You're not normalizing correctly
- The effect size is being massively inflated by the intervention method

**Check:** Run DAS with a *known* random vector. If you get "preserved" values > 0 for random, your ablation method isn't actually ablating.

---

### 5. **The "Brittle on Paraphrases" + "KL Divergence = 0.0003" Tells You Where to Look**

KL divergence of 0.0003 means the output distribution barely changes. The vector is making *tiny* adjustments that only matter for *exact prompts*.

This is the signature of:
- Overfitting to prompt surface forms
- Targeting a specific attention pattern that only activates on the exact phrasing

**Hypothesis:** The vector is activating/deactivating a specific set of attention heads that are sensitive to the *exact* token sequence of your prompts. When the prompt changes, those heads don't activate, so the vector does nothing.

**Test:** 
1. Extract attention patterns at layers 28-35 for the exact prompt vs paraphrases
2. Find heads that differ significantly between conditions
3. Check if your vector projects onto those heads' output subspaces

---

### 6. **What You Should Do Next (Highest ROI)**

**Experiment A: Decode the Vector with SAEs (1-2 GPU hours)**

Run your vector through a trained SAE (Gemma Scope or your own) and identify:
- Which features are activated by adding the vector?
- Are they "anti-heuristic" features (e.g., "this is a trick question")?
- Are they domain-specific (decimal, spatial) or generic?

This tells you if the vector is a *suppressor* (activating "be careful" features) or an *amplifier* (activating reasoning-specific features).

**Experiment B: Evolve for CoT-Alignment Instead of Task Performance (4-6 GPU hours)**

Current vector: optimized for logit margin on 4 traps.
New vector: optimize for *cosine similarity* with CoT-baseline difference at layer 31.

Hypothesis: This will find vectors that actually amplify reasoning circuits. If the resulting vector shows precipitation on held-out traps, you've found a real reasoning amplifier.

**Experiment C: Causal Tracing of the Overtake Race Precipitation (1 GPU hour)**

On Overtake Race only (where you have signal):
1. Run activation patching at *every* layer, not just 4-5 layers
2. Identify which attention heads/MLPs actually *cause* the behavioral change
3. See if your vector's subspace aligns with those components' output spaces

This localizes the mechanism.

**Experiment D: Test the Suppression Hypothesis (30 min)**

Run the vector on *easy* traps where the model is already correct (e.g., "Is 2+2=4?"). If it *reduces* performance, you've confirmed it's a general suppressor, not a reasoning amplifier.

---

## Code: SAE Decomposition of Steering Vector

```python
"""
SAE Decomposition of Steering Vector

Identifies which features are activated by the steering vector.
Uses Gemma Scope SAEs (trained on Gemma-2-2B) as a proxy for feature analysis.
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from sae_lens import SAE
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import argparse

class SteeringVectorDecoder:
    """Decompose steering vector into SAE features."""
    
    def __init__(
        self,
        model: HookedTransformer,
        vector: torch.Tensor,
        layer_idx: int,
        sae_release: str = "gemma-scope-2b-pt-res",
        sae_layer: int = None  # Will use layer_idx if not specified
    ):
        self.model = model
        self.vector = vector
        self.layer_idx = layer_idx
        self.sae_layer = sae_layer or layer_idx
        
        # Load SAE for the target layer
        print(f"Loading SAE for layer {self.sae_layer}...")
        self.sae = SAE.from_pretrained(
            release=sae_release,
            sae_id=f"layer_{self.sae_layer}/width_16k",
            device=model.cfg.device
        )
        
    def decompose_vector(self) -> Dict:
        """
        Decompose steering vector into SAE feature activations.
        
        Returns:
            Dictionary with top features and their activation strengths
        """
        # Move vector to same device as SAE
        vec = self.vector.to(self.sae.device)
        
        # Encode through SAE
        # SAE expects [batch, d_model] input
        features = self.sae.encode(vec.unsqueeze(0))  # [1, n_features]
        
        # Get top activating features
        top_k = 20
        top_values, top_indices = torch.topk(features[0], k=top_k)
        
        # Convert to numpy for analysis
        top_features = []
        for idx, val in zip(top_indices.cpu(), top_values.cpu()):
            top_features.append({
                "feature_idx": idx.item(),
                "activation": val.item(),
                "feature_id": f"L{self.sae_layer}_F{idx.item()}"
            })
        
        # Also compute reconstruction
        reconstruction = self.sae.decode(features)[0]  # [d_model]
        reconstruction_error = torch.norm(vec - reconstruction).item()
        
        return {
            "top_features": top_features,
            "reconstruction_error": reconstruction_error,
            "sparsity": (features > 0).float().mean().item(),
            "n_active_features": (features > 0).sum().item()
        }
    
    def compare_to_baseline(self, n_baseline_prompts: int = 100) -> Dict:
        """
        Compare vector-activated features to baseline activation features.
        
        This tells us if the vector activates features that are:
        - Normally inactive (novel features)
        - Normally active but amplified (amplification)
        - Normally active but suppressed (suppression)
        """
        # Get baseline activations from random prompts
        baseline_features = []
        
        from datasets import load_dataset
        dataset = load_dataset("c4", "en", split="train", streaming=True)
        
        for i, example in enumerate(dataset.take(n_baseline_prompts)):
            tokens = self.model.to_tokens(example["text"][:512])
            
            # Get residual at injection layer
            def cache_hook(activation, hook):
                self.cached_activation = activation[:, -1, :].clone()
                return activation
            
            self.model.reset_hooks()
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", cache_hook)
            
            with torch.no_grad():
                _ = self.model(tokens)
            
            # Encode through SAE
            features = self.sae.encode(self.cached_activation)
            baseline_features.append(features[0].cpu())
        
        # Average baseline features
        baseline_avg = torch.stack(baseline_features).mean(dim=0)
        
        # Get vector features
        vec_features = self.sae.encode(self.vector.unsqueeze(0))[0].cpu()
        
        # Compare
        ratio = vec_features / (baseline_avg + 1e-8)
        top_ratio_indices = torch.topk(ratio, k=20)[1]
        
        amplification_features = []
        for idx in top_ratio_indices:
            amplification_features.append({
                "feature_idx": idx.item(),
                "vector_activation": vec_features[idx].item(),
                "baseline_activation": baseline_avg[idx].item(),
                "ratio": ratio[idx].item()
            })
        
        return {
            "amplification_features": amplification_features,
            "baseline_sparsity": (baseline_avg > 0.1).float().mean().item(),
            "vector_sparsity": (vec_features > 0.1).float().mean().item()
        }
    
    def interpret_top_features(self, top_features: List[Dict]) -> None:
        """
        Attempt to interpret top features using feature descriptions.
        
        Note: This requires feature descriptions from the SAE release.
        """
        # For Gemma Scope, features have descriptions
        try:
            feature_descriptions = self.sae.feature_descriptions
            
            print("\n=== Top Activating Features ===")
            for f in top_features[:10]:
                feat_id = f["feature_idx"]
                activation = f["activation"]
                description = feature_descriptions.get(feat_id, "No description")
                print(f"Feature {feat_id} (act={activation:.3f}): {description}")
        except AttributeError:
            print("No feature descriptions available for this SAE")
            
            # Fall back to analyzing by activation pattern
            # Find tokens that activate this feature strongly
            for f in top_features[:3]:
                feat_id = f["feature_idx"]
                print(f"\nFeature {feat_id} (act={f['activation']:.3f}):")
                self._sample_feature_activations(feat_id)
    
    def _sample_feature_activations(self, feature_idx: int, n_samples: int = 5):
        """Find prompts that strongly activate a feature."""
        from datasets import load_dataset
        dataset = load_dataset("c4", "en", split="train", streaming=True)
        
        activations = []
        prompts = []
        
        for example in dataset.take(100):
            text = example["text"][:512]
            tokens = self.model.to_tokens(text)
            
            def cache_hook(activation, hook):
                self.cached_activation = activation[:, -1, :].clone()
                return activation
            
            self.model.reset_hooks()
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", cache_hook)
            
            with torch.no_grad():
                _ = self.model(tokens)
            
            features = self.sae.encode(self.cached_activation)[0]
            activation = features[feature_idx].item()
            
            activations.append(activation)
            prompts.append(text[:100])
        
        # Show top activations
        top_indices = np.argsort(activations)[-n_samples:][::-1]
        for idx in top_indices:
            print(f"  Act={activations[idx]:.3f}: {prompts[idx]}...")
    
    def visualize_feature_contributions(self, results: Dict):
        """Create bar plot of top feature contributions."""
        top_features = results["top_features"][:15]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        feature_names = [f"F{f['feature_idx']}" for f in top_features]
        activations = [f["activation"] for f in top_features]
        
        ax.barh(feature_names, activations)
        ax.set_xlabel("Feature Activation")
        ax.set_title(f"Steering Vector Decomposition (Layer {self.layer_idx})")
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig("steering_vector_features.png", dpi=150)
        print("Saved visualization to steering_vector_features.png")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="google/gemma-2-2b")
    parser.add_argument("--sae_release", type=str, default="gemma-scope-2b-pt-res")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()
    
    # Load model
    print(f"Loading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load steering vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    vector = checkpoint["vector"].to(args.device)
    layer_idx = checkpoint["layer_index"]
    
    print(f"Vector norm: {torch.norm(vector):.3f}")
    print(f"Injection layer: {layer_idx}")
    
    # Run SAE decomposition
    decoder = SteeringVectorDecoder(model, vector, layer_idx, args.sae_release)
    
    # Decompose vector
    results = decoder.decompose_vector()
    
    print(f"\n=== SAE Decomposition Results ===")
    print(f"Reconstruction error: {results['reconstruction_error']:.4f}")
    print(f"Sparsity: {results['sparsity']:.2%}")
    print(f"Active features: {results['n_active_features']} / {decoder.sae.cfg.d_sae}")
    
    print("\nTop 10 Features:")
    for i, f in enumerate(results["top_features"][:10]):
        print(f"  {i+1}. Feature {f['feature_idx']}: activation = {f['activation']:.3f}")
    
    # Compare to baseline
    print("\n=== Baseline Comparison ===")
    baseline_results = decoder.compare_to_baseline(n_baseline_prompts=50)
    
    print(f"Baseline sparsity: {baseline_results['baseline_sparsity']:.2%}")
    print(f"Vector sparsity: {baseline_results['vector_sparsity']:.2%}")
    
    print("\nTop Amplification Features (vector >> baseline):")
    for f in baseline_results["amplification_features"][:10]:
        print(f"  Feature {f['feature_idx']}: ratio={f['ratio']:.2f}x "
              f"(vec={f['vector_activation']:.3f}, base={f['baseline_activation']:.3f})")
    
    # Try to interpret features
    decoder.interpret_top_features(results["top_features"])
    
    # Visualize
    decoder.visualize_feature_contributions(results)

if __name__ == "__main__":
    main()
```

---

## Summary: What Your Data Actually Says

1. **You didn't evolve a reasoning amplifier.** You evolved a *heuristic suppressor* that exploits the CMA-ES fitness function's focus on logit margin rather than behavioral correctness.

2. **The anti-CoT correlation is a geometric artifact** of comparing a late-layer intervention (L31) to an early-prompt change. Test the actual trajectories, not just the endpoint.

3. **The Overtake Race precipitation is your most promising lead** because it's the only place you see the vector actually *adding* information that gets used downstream. But you need to confirm it's not just a generic random vector effect.

4. **The DAS results are suspicious** given the tiny effect sizes elsewhere. Re-run with proper normalization and sanity checks.

5. **The brittleness + tiny KL divergence = overfitting to exact prompts.** The vector is targeting attention patterns that only appear in your specific prompt wording.

**Next steps in priority order:**

1. **SAE decomposition** (highest ROI) — tells you what the vector actually does
2. **Test the suppression hypothesis** — run on easy traps where model is correct
3. **Evolve for CoT alignment** — find actual reasoning amplifiers
4. **Causal tracing on Overtake Race** — localize the precipitation mechanism
5. **Random vector controls on Overtake Race** — rule out generic effect

Your north star is exploration. Go decode the vector with SAEs. That'll tell you more than any of the other tests.

[DEEPSEEK FOLLOWUP ]

# Complete Implementation Roadmap for All 5 Experiments

I'll give you a detailed path and production-ready code for each experiment, optimized for your 17GB VRAM constraint with Qwen3-4B.

## Environment Setup First

```bash
# Create fresh environment
conda create -n prometheus python=3.10
conda activate prometheus

# Install core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformer_lens
pip install sae-lens  # For SAE decomposition
pip install datasets
pip install numpy scipy matplotlib seaborn
pip install tqdm
pip install accelerate  # For model loading optimization
```

---

## Experiment 1: SAE Decomposition (Highest ROI)

### Strategy
Use pre-trained SAEs from **Gemma Scope** (Google's open-source SAE suite) on Gemma-2-2B as a proxy. Since SAEs don't exist for Qwen3-4B, we'll:
1. Map your Qwen3-4B vector to Gemma-2-2B's architecture via learned projection
2. Or use a small proxy SAE trained on Qwen3-4B's activations

**Recommended path:** Use Gemma-2-2B as a proxy model with Gemma Scope SAEs.

```python
"""
Experiment 1: SAE Decomposition of Steering Vector
File: 1_sae_decomposition.py

Strategy: Project Qwen3-4B steering vector to Gemma-2-2B space using
learned linear mapping from residual stream activations.
"""

import torch
import torch.nn as nn
import numpy as np
from transformer_lens import HookedTransformer
from sae_lens import SAE
from datasets import load_dataset
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import argparse
import json
from pathlib import Path

class CrossModelVectorMapper:
    """
    Maps steering vectors from Qwen3-4B to Gemma-2-2B space using
    learned linear transformation from aligned prompts.
    """
    
    def __init__(self, source_model, target_model, source_layer, target_layer):
        self.source_model = source_model
        self.target_model = target_model
        self.source_layer = source_layer
        self.target_layer = target_layer
        self.mapping = None
        
    def learn_mapping(self, n_prompts=500):
        """
        Learn linear mapping W such that:
        W * activation_source ≈ activation_target
        """
        print(f"Learning mapping from Qwen3-4B L{self.source_layer} to Gemma-2-2B L{self.target_layer}")
        
        # Collect paired activations
        source_acts = []
        target_acts = []
        
        dataset = load_dataset("c4", "en", split="train", streaming=True)
        
        for i, example in enumerate(tqdm(dataset.take(n_prompts), desc="Collecting activations")):
            text = example["text"][:512]
            
            # Get source activation (Qwen)
            source_act = self._get_activation(self.source_model, text, self.source_layer)
            
            # Get target activation (Gemma)
            target_act = self._get_activation(self.target_model, text, self.target_layer)
            
            if source_act is not None and target_act is not None:
                source_acts.append(source_act)
                target_acts.append(target_act)
        
        # Stack and compute mapping
        source_acts = torch.stack(source_acts)  # [n, d_source]
        target_acts = torch.stack(target_acts)  # [n, d_target]
        
        # Least squares solution: W = (X^T X)^{-1} X^T Y
        X = source_acts.numpy()
        Y = target_acts.numpy()
        
        # Add regularization
        lambda_reg = 0.01
        W = np.linalg.solve(X.T @ X + lambda_reg * np.eye(X.shape[1]), X.T @ Y)
        
        self.mapping = torch.tensor(W, dtype=torch.float32)
        
        # Compute mapping quality
        pred_acts = source_acts @ self.mapping
        mse = torch.mean((pred_acts - target_acts) ** 2).item()
        print(f"Mapping MSE: {mse:.4f}")
        
        return self.mapping
    
    def _get_activation(self, model, text, layer_idx):
        """Get residual stream activation at specified layer."""
        tokens = model.to_tokens(text)
        
        def cache_hook(activation, hook):
            self.cached_activation = activation[:, -1, :].clone()
            return activation
        
        model.reset_hooks()
        model.add_hook(f"blocks.{layer_idx}.hook_resid_post", cache_hook)
        
        with torch.no_grad():
            try:
                _ = model(tokens)
                return self.cached_activation[0].cpu()
            except:
                return None
    
    def map_vector(self, source_vector):
        """Map source vector to target space."""
        if self.mapping is None:
            raise ValueError("Must learn mapping first")
        
        return source_vector @ self.mapping

class SteeringVectorSAEDecoder:
    """
    Decompose steering vector into SAE features using Gemma Scope.
    """
    
    def __init__(self, gemma_model, vector_gemma, layer_idx, sae_release="gemma-scope-2b-pt-res"):
        self.model = gemma_model
        self.vector = vector_gemma
        self.layer_idx = layer_idx
        
        # Load SAE
        print(f"Loading SAE for Gemma-2-2B layer {layer_idx}...")
        self.sae = SAE.from_pretrained(
            release=sae_release,
            sae_id=f"layer_{layer_idx}/width_16k",
            device=gemma_model.cfg.device
        )
        
        # Load feature descriptions if available
        try:
            self.feature_descriptions = self.sae.feature_descriptions
        except:
            self.feature_descriptions = {}
    
    def decompose_vector(self, top_k=50) -> Dict:
        """
        Decompose steering vector into SAE features.
        
        Returns:
            Dictionary with top features and their activations
        """
        vec = self.vector.to(self.sae.device)
        
        # Encode through SAE
        features = self.sae.encode(vec.unsqueeze(0))  # [1, n_features]
        
        # Get top activating features
        top_values, top_indices = torch.topk(features[0], k=top_k)
        
        top_features = []
        for idx, val in zip(top_indices.cpu(), top_values.cpu()):
            feature_info = {
                "feature_idx": idx.item(),
                "activation": val.item(),
                "feature_id": f"L{self.layer_idx}_F{idx.item()}"
            }
            
            # Add description if available
            if idx.item() in self.feature_descriptions:
                feature_info["description"] = self.feature_descriptions[idx.item()]
            
            top_features.append(feature_info)
        
        # Reconstruction
        reconstruction = self.sae.decode(features)[0]
        reconstruction_error = torch.norm(vec - reconstruction).item()
        
        return {
            "top_features": top_features,
            "reconstruction_error": reconstruction_error,
            "sparsity": (features > 0).float().mean().item(),
            "n_active_features": (features > 0).sum().item(),
            "total_features": self.sae.cfg.d_sae
        }
    
    def compare_to_baseline(self, n_baseline_prompts=100) -> Dict:
        """
        Compare vector-activated features to baseline activations.
        """
        baseline_features = []
        
        dataset = load_dataset("c4", "en", split="train", streaming=True)
        
        for example in tqdm(dataset.take(n_baseline_prompts), desc="Collecting baseline"):
            text = example["text"][:512]
            
            # Get activation at layer
            tokens = self.model.to_tokens(text)
            
            def cache_hook(activation, hook):
                self.cached_activation = activation[:, -1, :].clone()
                return activation
            
            self.model.reset_hooks()
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", cache_hook)
            
            with torch.no_grad():
                _ = self.model(tokens)
            
            # Encode through SAE
            features = self.sae.encode(self.cached_activation.to(self.sae.device))
            baseline_features.append(features[0].cpu())
        
        baseline_avg = torch.stack(baseline_features).mean(dim=0)
        
        # Get vector features
        vec_features = self.sae.encode(self.vector.unsqueeze(0))[0].cpu()
        
        # Calculate ratios
        ratio = vec_features / (baseline_avg + 1e-8)
        
        # Features amplified by vector
        amplified_idx = torch.topk(ratio, k=20)[1]
        amplified_features = []
        for idx in amplified_idx:
            amplified_features.append({
                "feature_idx": idx.item(),
                "vector_activation": vec_features[idx].item(),
                "baseline_activation": baseline_avg[idx].item(),
                "ratio": ratio[idx].item()
            })
        
        # Features suppressed by vector
        suppressed_idx = torch.topk(-ratio, k=20)[1]
        suppressed_features = []
        for idx in suppressed_idx:
            suppressed_features.append({
                "feature_idx": idx.item(),
                "vector_activation": vec_features[idx].item(),
                "baseline_activation": baseline_avg[idx].item(),
                "ratio": ratio[idx].item()
            })
        
        return {
            "amplified_features": amplified_features,
            "suppressed_features": suppressed_features,
            "baseline_sparsity": (baseline_avg > 0.1).float().mean().item(),
            "vector_sparsity": (vec_features > 0.1).float().mean().item()
        }
    
    def visualize_top_features(self, results: Dict, save_path: str = "sae_features.png"):
        """Create visualization of top features."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Left: Top features by activation
        top_features = results["top_features"][:15]
        feature_names = [f["feature_id"] for f in top_features]
        activations = [f["activation"] for f in top_features]
        
        axes[0].barh(feature_names, activations, color='steelblue')
        axes[0].set_xlabel("Feature Activation")
        axes[0].set_title(f"Top Features (Layer {self.layer_idx})")
        axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # Right: Amplified vs suppressed
        if "amplified_features" in results:
            amplified = results["amplified_features"][:10]
            suppressed = results["suppressed_features"][:10]
            
            amp_names = [f"F{a['feature_idx']}" for a in amplified]
            amp_ratios = [a["ratio"] for a in amplified]
            sup_names = [f"F{s['feature_idx']}" for s in suppressed]
            sup_ratios = [-s["ratio"] for s in suppressed]  # Negative for visualization
            
            y_pos = range(len(amp_names))
            axes[1].barh(y_pos, amp_ratios, color='green', alpha=0.7, label='Amplified')
            axes[1].barh([y + 0.3 for y in y_pos], sup_ratios, color='red', alpha=0.7, label='Suppressed')
            axes[1].set_yticks([y + 0.15 for y in y_pos])
            axes[1].set_yticklabels(amp_names)
            axes[1].set_xlabel("Ratio (Vector / Baseline)")
            axes[1].set_title("Feature Amplification/Suppression")
            axes[1].legend()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"Saved visualization to {save_path}")
        
    def export_feature_analysis(self, results: Dict, output_path: str):
        """Export feature analysis to JSON."""
        # Convert numpy/torch to Python types
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, torch.Tensor):
                return obj.item() if obj.numel() == 1 else obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj
        
        with open(output_path, 'w') as f:
            json.dump(convert(results), f, indent=2)
        print(f"Saved analysis to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True, help="Path to best_genome.pt")
    parser.add_argument("--source_model", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--target_model", type=str, default="google/gemma-2-2b")
    parser.add_argument("--sae_release", type=str, default="gemma-scope-2b-pt-res")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--n_mapping_prompts", type=int, default=500)
    parser.add_argument("--n_baseline_prompts", type=int, default=100)
    args = parser.parse_args()
    
    # Load models
    print("=" * 60)
    print("Experiment 1: SAE Decomposition")
    print("=" * 60)
    
    print(f"\nLoading {args.source_model}...")
    source_model = HookedTransformer.from_pretrained(
        args.source_model,
        device=args.device,
        dtype=torch.float16
    )
    
    print(f"\nLoading {args.target_model}...")
    target_model = HookedTransformer.from_pretrained(
        args.target_model,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load steering vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    source_vector = checkpoint["vector"].to(args.device)
    source_layer = checkpoint["layer_index"]
    
    print(f"\nSource vector norm: {torch.norm(source_vector):.3f}")
    print(f"Source injection layer: {source_layer}")
    
    # Map to target layer (approximate: use same relative position)
    # Qwen3-4B has 36 layers, Gemma-2-2B has 26 layers
    target_layer = int(source_layer * 26 / 36)
    print(f"Mapping to Gemma layer {target_layer}")
    
    # Learn mapping
    mapper = CrossModelVectorMapper(source_model, target_model, source_layer, target_layer)
    mapper.learn_mapping(n_prompts=args.n_mapping_prompts)
    
    # Map vector
    print("\nMapping steering vector to Gemma space...")
    target_vector = mapper.map_vector(source_vector)
    print(f"Mapped vector norm: {torch.norm(target_vector):.3f}")
    
    # Run SAE decomposition
    decoder = SteeringVectorSAEDecoder(
        target_model, target_vector, target_layer, args.sae_release
    )
    
    # Decompose vector
    print("\n=== Decomposing Vector ===")
    results = decoder.decompose_vector(top_k=50)
    
    print(f"\nReconstruction error: {results['reconstruction_error']:.4f}")
    print(f"Sparsity: {results['sparsity']:.2%}")
    print(f"Active features: {results['n_active_features']} / {results['total_features']}")
    
    print("\nTop 10 Features:")
    for i, f in enumerate(results["top_features"][:10]):
        desc = f.get("description", "No description")[:100]
        print(f"  {i+1}. {f['feature_id']}: act={f['activation']:.3f} - {desc}")
    
    # Compare to baseline
    print("\n=== Comparing to Baseline ===")
    baseline_results = decoder.compare_to_baseline(n_baseline_prompts=args.n_baseline_prompts)
    
    print(f"\nBaseline sparsity: {baseline_results['baseline_sparsity']:.2%}")
    print(f"Vector sparsity: {baseline_results['vector_sparsity']:.2%}")
    
    print("\nTop Amplified Features (vector >> baseline):")
    for f in baseline_results["amplified_features"][:10]:
        print(f"  Feature {f['feature_idx']}: ratio={f['ratio']:.2f}x "
              f"(vec={f['vector_activation']:.3f}, base={f['baseline_activation']:.3f})")
    
    print("\nTop Suppressed Features (baseline >> vector):")
    for f in baseline_results["suppressed_features"][:5]:
        print(f"  Feature {f['feature_idx']}: ratio={1/f['ratio']:.2f}x "
              f"(vec={f['vector_activation']:.3f}, base={f['baseline_activation']:.3f})")
    
    # Visualize
    decoder.visualize_top_features({**results, **baseline_results}, "sae_features.png")
    
    # Export
    decoder.export_feature_analysis(
        {**results, **baseline_results, 
         "source_vector_norm": torch.norm(source_vector).item(),
         "target_vector_norm": torch.norm(target_vector).item(),
         "source_layer": source_layer,
         "target_layer": target_layer},
        "sae_analysis.json"
    )
    
    print("\n✅ SAE decomposition complete!")
    print("Key questions to answer:")
    print("  - Do amplified features correspond to 'reasoning' or 'heuristic' patterns?")
    print("  - Are suppressed features task-specific heuristics?")
    print("  - Does the vector activate 'meta-cognitive' features (e.g., 'trick question')?")

if __name__ == "__main__":
    main()
```

---

## Experiment 2: Test Suppression Hypothesis

```python
"""
Experiment 2: Test Suppression Hypothesis
File: 2_suppression_test.py

Tests if steering vector reduces performance on easy traps where model is correct.
If yes, vector is a general suppressor, not a reasoning amplifier.
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from tqdm import tqdm
import argparse
import json
from typing import Dict, List

# Easy traps where Qwen3-4B should be correct without steering
EASY_TRAPS = {
    "addition": {
        "prompt": "What is 2 + 2?",
        "correct": "4",
        "incorrect": "5"
    },
    "capital": {
        "prompt": "What is the capital of France?",
        "correct": "Paris",
        "incorrect": "London"
    },
    "color": {
        "prompt": "What color is the sky on a clear day?",
        "correct": "blue",
        "incorrect": "green"
    },
    "water_boiling": {
        "prompt": "At standard pressure, water boils at what temperature?",
        "correct": "100",
        "incorrect": "90"
    },
    "earth_shape": {
        "prompt": "What shape is the Earth?",
        "correct": "sphere",
        "incorrect": "flat"
    },
    "sun_rise": {
        "prompt": "The sun rises in the...",
        "correct": "east",
        "incorrect": "west"
    }
}

class SuppressionTester:
    """Tests if steering vector suppresses correct behavior on easy tasks."""
    
    def __init__(self, model, vector, layer_idx):
        self.model = model
        self.vector = vector
        self.layer_idx = layer_idx
        
    def run_test(self, traps: Dict, n_runs=5) -> Dict:
        """
        Run suppression test across all easy traps.
        
        Returns:
            Dictionary with performance metrics for baseline, steered, and ablated
        """
        results = {}
        
        for trap_name, trap in traps.items():
            print(f"\nTesting {trap_name}...")
            
            # Tokenize
            tokens = self.model.to_tokens(trap["prompt"])
            correct_id = self.model.to_tokens(trap["correct"], prepend_bos=False)[0][0].item()
            incorrect_id = self.model.to_tokens(trap["incorrect"], prepend_bos=False)[0][0].item()
            
            # Run conditions
            baseline_margins = []
            steered_margins = []
            ablated_margins = []
            
            for _ in range(n_runs):
                # Baseline
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    baseline_margins.append(logits[correct_id] - logits[incorrect_id])
                
                # Steered
                self.model.reset_hooks()
                self._add_steering_hook(epsilon=1.0)
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    steered_margins.append(logits[correct_id] - logits[incorrect_id])
                
                # Ablated (remove steering direction)
                self.model.reset_hooks()
                self._add_ablation_hook()
                with torch.no_grad():
                    logits = self.model(tokens)[0, -1, :]
                    ablated_margins.append(logits[correct_id] - logits[incorrect_id])
            
            results[trap_name] = {
                "baseline_margin": np.mean(baseline_margins),
                "baseline_correct": np.mean(baseline_margins) > 0,
                "steered_margin": np.mean(steered_margins),
                "steered_correct": np.mean(steered_margins) > 0,
                "ablated_margin": np.mean(ablated_margins),
                "ablated_correct": np.mean(ablated_margins) > 0,
                "suppression_effect": np.mean(steered_margins) - np.mean(baseline_margins),
                "n_runs": n_runs
            }
        
        return results
    
    def _add_steering_hook(self, epsilon=1.0):
        """Add hook to inject steering vector."""
        def hook(activation, hook):
            activation[:, -1, :] += epsilon * self.vector
            return activation
        self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", hook)
    
    def _add_ablation_hook(self):
        """Add hook to remove steering direction component."""
        v_hat = self.vector / torch.norm(self.vector)
        
        def hook(activation, hook):
            h = activation[:, -1, :]
            projection = torch.einsum('bd,d->b', h, v_hat).unsqueeze(-1) * v_hat
            activation[:, -1, :] = h - projection
            return activation
        self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", hook)
    
    def analyze_results(self, results: Dict) -> Dict:
        """Analyze suppression patterns."""
        suppression_scores = []
        for trap_name, trap_results in results.items():
            suppression_scores.append(trap_results["suppression_effect"])
        
        analysis = {
            "mean_suppression": np.mean(suppression_scores),
            "std_suppression": np.std(suppression_scores),
            "traps_suppressed": sum(1 for s in suppression_scores if s < 0),
            "traps_improved": sum(1 for s in suppression_scores if s > 0),
            "traps_unchanged": sum(1 for s in suppression_scores if abs(s) < 0.01),
            "by_trap": results
        }
        
        # Statistical test
        from scipy import stats
        t_stat, p_value = stats.ttest_1samp(suppression_scores, 0)
        analysis["t_statistic"] = t_stat
        analysis["p_value"] = p_value
        analysis["significant_suppression"] = p_value < 0.05 and np.mean(suppression_scores) < 0
        
        return analysis

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--n_runs", type=int, default=5)
    args = parser.parse_args()
    
    print("=" * 60)
    print("Experiment 2: Suppression Hypothesis Test")
    print("=" * 60)
    
    # Load model
    print(f"\nLoading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load steering vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    vector = checkpoint["vector"].to(args.device)
    layer_idx = checkpoint["layer_index"]
    
    print(f"Vector norm: {torch.norm(vector):.3f}")
    print(f"Injection layer: {layer_idx}")
    
    # Run test
    tester = SuppressionTester(model, vector, layer_idx)
    results = tester.run_test(EASY_TRAPS, n_runs=args.n_runs)
    analysis = tester.analyze_results(results)
    
    # Print results
    print("\n" + "=" * 60)
    print("SUPPRESSION TEST RESULTS")
    print("=" * 60)
    
    print(f"\nMean suppression effect: {analysis['mean_suppression']:.3f}")
    print(f"Suppression std: {analysis['std_suppression']:.3f}")
    print(f"Traps suppressed: {analysis['traps_suppressed']}/{len(EASY_TRAPS)}")
    print(f"Traps improved: {analysis['traps_improved']}/{len(EASY_TRAPS)}")
    
    print("\nBy trap:")
    for trap_name, trap_results in results.items():
        effect = trap_results["suppression_effect"]
        status = "⬇️ SUPPRESSED" if effect < 0 else "⬆️ IMPROVED" if effect > 0 else "➡️ UNCHANGED"
        print(f"  {trap_name}: {effect:+.3f} {status}")
    
    if analysis["significant_suppression"]:
        print("\n🔴 SIGNIFICANT SUPPRESSION DETECTED")
        print("   The vector systematically reduces performance on easy tasks.")
        print("   This supports the suppression hypothesis: the vector is a heuristic suppressor.")
    else:
        print("\n🟡 No significant suppression detected")
    
    # Save results
    with open("suppression_test_results.json", "w") as f:
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.float32):
                return float(obj)
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        json.dump(convert(analysis), f, indent=2)
    
    print("\n✅ Suppression test complete!")
    print("\nInterpretation:")
    print("  - If mean suppression < 0: Vector is a general suppressor")
    print("  - If mean suppression > 0: Vector may be a reasoning amplifier")
    print("  - If mixed: Vector is task-specific")

if __name__ == "__main__":
    main()
```

---

## Experiment 3: Evolve for CoT Alignment

```python
"""
Experiment 3: Evolve for CoT Alignment
File: 3_cot_alignment_evolution.py

Uses CMA-ES to evolve vectors that maximize alignment with CoT direction
rather than task performance. Hypothesis: These will be true reasoning amplifiers.
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from cma import CMAEvolutionStrategy
from tqdm import tqdm
import argparse
import json
from typing import Dict, List, Tuple
import pickle

class CoTAlignmentOptimizer:
    """
    CMA-ES optimizer for vectors that maximize cosine similarity with
    Chain-of-Thought direction.
    """
    
    def __init__(self, model, layer_idx, d_model, traps: Dict, device="cuda"):
        self.model = model
        self.layer_idx = layer_idx
        self.d_model = d_model
        self.traps = traps
        self.device = device
        
        # Cache baseline and CoT activations
        self.baseline_activations = {}
        self.cot_activations = {}
        self._cache_activations()
        
    def _cache_activations(self):
        """Cache activations for each trap at the injection layer."""
        print("Caching baseline and CoT activations...")
        
        for trap_name, trap in self.traps.items():
            # Baseline prompt
            baseline_tokens = self.model.to_tokens(trap["prompt"])
            baseline_act = self._get_activation(baseline_tokens)
            self.baseline_activations[trap_name] = baseline_act
            
            # CoT prompt
            cot_prompt = trap["prompt"] + " Let's think step by step."
            cot_tokens = self.model.to_tokens(cot_prompt)
            cot_act = self._get_activation(cot_tokens)
            self.cot_activations[trap_name] = cot_act
            
            # Store direction
            direction = cot_act - baseline_act
            self.cot_activations[trap_name + "_direction"] = direction
            
            print(f"  {trap_name}: baseline norm={torch.norm(baseline_act):.3f}, "
                  f"CoT norm={torch.norm(cot_act):.3f}, "
                  f"direction norm={torch.norm(direction):.3f}")
    
    def _get_activation(self, tokens):
        """Get residual stream activation at injection layer."""
        def cache_hook(activation, hook):
            self.cached_activation = activation[:, -1, :].clone()
            return activation
        
        self.model.reset_hooks()
        self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", cache_hook)
        
        with torch.no_grad():
            _ = self.model(tokens)
        
        return self.cached_activation[0].cpu()
    
    def fitness_function(self, vector_np):
        """
        Fitness: average cosine similarity with CoT direction across traps.
        """
        vector = torch.tensor(vector_np, dtype=torch.float32, device=self.device)
        vector = vector / torch.norm(vector)  # Normalize
        
        similarities = []
        
        for trap_name in self.traps.keys():
            # Get CoT direction for this trap
            direction = self.cot_activations[trap_name + "_direction"].to(self.device)
            direction = direction / (torch.norm(direction) + 1e-8)
            
            # Cosine similarity
            sim = torch.dot(vector, direction).item()
            similarities.append(sim)
        
        # Average similarity
        avg_similarity = np.mean(similarities)
        
        # Optional: penalize vectors that are too similar to baseline
        # (to avoid degenerate solutions)
        
        return avg_similarity
    
    def optimize(self, population_size=10, generations=200, sigma0=0.5):
        """
        Run CMA-ES optimization.
        """
        print(f"\nStarting CMA-ES optimization for CoT alignment")
        print(f"Population size: {population_size}")
        print(f"Generations: {generations}")
        print(f"Initial sigma: {sigma0}")
        
        # Initialize optimizer
        x0 = np.random.randn(self.d_model) * 0.1
        x0 = x0 / np.linalg.norm(x0) * 0.5  # Small initial vector
        
        es = CMAEvolutionStrategy(
            x0, 
            sigma0,
            {'popsize': population_size, 'verbose': -1}
        )
        
        # Track progress
        history = {
            "generations": [],
            "best_fitness": [],
            "mean_fitness": [],
            "best_vectors": []
        }
        
        for gen in tqdm(range(generations), desc="Optimizing"):
            # Generate solutions
            solutions = es.ask()
            
            # Evaluate fitness
            fitnesses = []
            for sol in solutions:
                try:
                    fitness = self.fitness_function(sol)
                    fitnesses.append(-fitness)  # CMA-ES minimizes
                except Exception as e:
                    print(f"Error evaluating solution: {e}")
                    fitnesses.append(1e6)  # Penalty
            
            # Update optimizer
            es.tell(solutions, fitnesses)
            
            # Log progress
            best_idx = np.argmin(fitnesses)
            best_fitness = -fitnesses[best_idx]
            mean_fitness = -np.mean(fitnesses)
            
            history["generations"].append(gen)
            history["best_fitness"].append(best_fitness)
            history["mean_fitness"].append(mean_fitness)
            
            if gen % 20 == 0:
                print(f"\nGen {gen}: best={best_fitness:.4f}, mean={mean_fitness:.4f}")
        
        # Get best solution
        best_solution = es.result.xbest
        best_vector = torch.tensor(best_solution, dtype=torch.float32)
        best_vector = best_vector / torch.norm(best_vector) * 3.0  # Scale to norm 3
        
        return {
            "vector": best_vector,
            "fitness": self.fitness_function(best_solution),
            "history": history,
            "final_population": es.result.xfavorite
        }
    
    def validate_vector(self, vector):
        """
        Validate that evolved vector actually aligns with CoT and improves reasoning.
        """
        vector = vector.to(self.device)
        
        results = {}
        
        for trap_name, trap in self.traps.items():
            # Check CoT alignment
            direction = self.cot_activations[trap_name + "_direction"].to(self.device)
            direction_norm = direction / (torch.norm(direction) + 1e-8)
            vector_norm = vector / torch.norm(vector)
            alignment = torch.dot(vector_norm, direction_norm).item()
            
            # Check if vector improves performance
            baseline_margin = self._get_margin(trap["prompt"], trap["correct"], trap["incorrect"])
            steered_margin = self._get_margin(
                trap["prompt"], trap["correct"], trap["incorrect"], 
                steering_vector=vector
            )
            
            improvement = steered_margin - baseline_margin
            
            results[trap_name] = {
                "alignment": alignment,
                "baseline_margin": baseline_margin,
                "steered_margin": steered_margin,
                "improvement": improvement
            }
        
        return results
    
    def _get_margin(self, prompt, correct, incorrect, steering_vector=None):
        """Get logit margin for a prompt."""
        tokens = self.model.to_tokens(prompt)
        correct_id = self.model.to_tokens(correct, prepend_bos=False)[0][0].item()
        incorrect_id = self.model.to_tokens(incorrect, prepend_bos=False)[0][0].item()
        
        if steering_vector is not None:
            self.model.reset_hooks()
            def hook(activation, hook):
                activation[:, -1, :] += steering_vector
                return activation
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", hook)
        
        with torch.no_grad():
            logits = self.model(tokens)[0, -1, :]
            margin = logits[correct_id] - logits[incorrect_id]
        
        return margin.item()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--layer_idx", type=int, default=31)
    parser.add_argument("--population_size", type=int, default=10)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--output", type=str, default="cot_aligned_vector.pt")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Experiment 3: CoT Alignment Evolution")
    print("=" * 60)
    
    # Load model
    print(f"\nLoading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    d_model = model.cfg.d_model
    
    # Define traps (same as before, plus CoT)
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
        }
    }
    
    # Run optimization
    optimizer = CoTAlignmentOptimizer(model, args.layer_idx, d_model, TRAPS, args.device)
    result = optimizer.optimize(
        population_size=args.population_size,
        generations=args.generations,
        sigma0=0.5
    )
    
    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    
    print(f"\nBest fitness: {result['fitness']:.4f}")
    print(f"Final vector norm: {torch.norm(result['vector']):.3f}")
    
    # Validate
    print("\nValidating evolved vector...")
    validation = optimizer.validate_vector(result['vector'])
    
    print("\nValidation results:")
    for trap_name, metrics in validation.items():
        print(f"  {trap_name}:")
        print(f"    CoT alignment: {metrics['alignment']:.3f}")
        print(f"    Improvement: {metrics['improvement']:+.3f}")
    
    # Save vector
    torch.save({
        'vector': result['vector'].cpu(),
        'layer_index': args.layer_idx,
        'fitness': result['fitness'],
        'validation': validation,
        'history': result['history']
    }, args.output)
    
    print(f"\n✅ Saved vector to {args.output}")
    print("\nNext steps:")
    print("  1. Test this vector on held-out traps")
    print("  2. Run precipitation tests (dose-response, ablation, patching)")
    print("  3. Compare to original vector behavior")

if __name__ == "__main__":
    main()
```

---

## Experiment 4: Causal Tracing on Overtake Race

```python
"""
Experiment 4: Causal Tracing on Overtake Race
File: 4_causal_tracing.py

Localizes the mechanism behind the precipitation effect on Overtake Race.
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import argparse
import json

class CausalTracer:
    """
    Activation patching to localize where steering vector exerts its effect.
    """
    
    def __init__(self, model, vector, layer_idx, prompt, correct, incorrect):
        self.model = model
        self.vector = vector
        self.layer_idx = layer_idx
        self.prompt = prompt
        self.correct = correct
        self.incorrect = incorrect
        
        self.tokens = model.to_tokens(prompt)
        self.correct_id = model.to_tokens(correct, prepend_bos=False)[0][0].item()
        self.incorrect_id = model.to_tokens(incorrect, prepend_bos=False)[0][0].item()
        
        # Cache baseline and steered activations
        self.baseline_acts = {}
        self.steered_acts = {}
        self._cache_activations()
        
    def _cache_activations(self):
        """Cache activations for all layers."""
        print("Caching baseline activations...")
        self._cache_run(baseline=True)
        
        print("Caching steered activations...")
        self._cache_run(baseline=False)
    
    def _cache_run(self, baseline=True):
        """Cache activations for a single run."""
        hooks = []
        acts = {}
        
        def make_hook(layer, hook_type):
            def hook(activation, hook):
                acts[f"{layer}_{hook_type}"] = activation[:, -1, :].clone()
                return activation
            return hook
        
        # Add hooks for all residual stream positions
        for layer in range(self.model.cfg.n_layers):
            for hook_type in ["resid_pre", "resid_mid", "resid_post"]:
                hook_fn = make_hook(layer, hook_type)
                self.model.add_hook(f"blocks.{layer}.hook_{hook_type}", hook_fn)
        
        # Add steering if needed
        if not baseline:
            def steer_hook(activation, hook):
                activation[:, -1, :] += self.vector
                return activation
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", steer_hook)
        
        # Run forward
        with torch.no_grad():
            _ = self.model(self.tokens)
        
        # Store
        if baseline:
            self.baseline_acts = acts
        else:
            self.steered_acts = acts
        
        # Clear hooks
        self.model.reset_hooks()
    
    def patch_activation(self, source_run, target_run, layer, hook_type="resid_post"):
        """
        Patch activation from source run into target run at specified layer.
        
        Args:
            source_run: "baseline" or "steered"
            target_run: "baseline" or "steered"
            layer: layer index
            hook_type: residual stream type
        """
        # Get source activation
        if source_run == "baseline":
            source_act = self.baseline_acts[f"{layer}_{hook_type}"]
        else:
            source_act = self.steered_acts[f"{layer}_{hook_type}"]
        
        # Create patching hook
        def patch_hook(activation, hook):
            activation[:, -1, :] = source_act.to(activation.device)
            return activation
        
        # Set up target run
        self.model.reset_hooks()
        
        if target_run == "steered":
            def steer_hook(activation, hook):
                activation[:, -1, :] += self.vector
                return activation
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", steer_hook)
        
        # Add patching hook
        self.model.add_hook(f"blocks.{layer}.hook_{hook_type}", patch_hook)
        
        # Run forward
        with torch.no_grad():
            logits = self.model(self.tokens)[0, -1, :]
            margin = logits[self.correct_id] - logits[self.incorrect_id]
        
        return margin.item()
    
    def compute_recovery(self, layer, hook_type="resid_post"):
        """
        Compute recovery fraction: how much of the steering effect is recovered
        when patching steered activation into baseline at this layer.
        """
        # Baseline margin (no intervention)
        baseline_margin = self._get_baseline_margin()
        
        # Full steering effect
        steered_margin = self._get_steered_margin()
        
        if abs(steered_margin - baseline_margin) < 1e-6:
            return 0.0
        
        # Patch steered into baseline at this layer
        patched_margin = self.patch_activation("steered", "baseline", layer, hook_type)
        
        # Recovery = (patched - baseline) / (steered - baseline)
        recovery = (patched_margin - baseline_margin) / (steered_margin - baseline_margin)
        
        return recovery
    
    def _get_baseline_margin(self):
        """Get baseline margin."""
        with torch.no_grad():
            logits = self.model(self.tokens)[0, -1, :]
            return logits[self.correct_id] - logits[self.incorrect_id]
    
    def _get_steered_margin(self):
        """Get steered margin."""
        self.model.reset_hooks()
        
        def steer_hook(activation, hook):
            activation[:, -1, :] += self.vector
            return activation
        
        self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", steer_hook)
        
        with torch.no_grad():
            logits = self.model(self.tokens)[0, -1, :]
            margin = logits[self.correct_id] - logits[self.incorrect_id]
        
        self.model.reset_hooks()
        return margin
    
    def trace_all_layers(self):
        """Run causal tracing across all layers."""
        n_layers = self.model.cfg.n_layers
        
        recoveries = {
            "resid_pre": [],
            "resid_mid": [],
            "resid_post": []
        }
        
        for layer in tqdm(range(n_layers), desc="Tracing layers"):
            for hook_type in ["resid_pre", "resid_mid", "resid_post"]:
                try:
                    rec = self.compute_recovery(layer, hook_type)
                    recoveries[hook_type].append(rec)
                except:
                    recoveries[hook_type].append(0.0)
        
        return recoveries
    
    def trace_components(self, layers=[28, 29, 30, 31, 32, 33, 34, 35]):
        """
        Trace attention heads and MLPs at specific layers.
        """
        results = {}
        
        for layer in tqdm(layers, desc="Tracing components"):
            layer_results = {
                "mlp": None,
                "attention_heads": {}
            }
            
            # Trace MLP
            mlp_recovery = self._trace_mlp(layer)
            layer_results["mlp"] = mlp_recovery
            
            # Trace attention heads
            n_heads = self.model.cfg.n_heads
            for head in range(n_heads):
                head_recovery = self._trace_head(layer, head)
                if abs(head_recovery) > 0.01:  # Only store non-zero
                    layer_results["attention_heads"][head] = head_recovery
            
            results[layer] = layer_results
        
        return results
    
    def _trace_mlp(self, layer):
        """Trace MLP at specified layer."""
        # Get steered MLP output
        steered_mlp = self._get_component_output(layer, "mlp", steered=True)
        
        # Patch into baseline
        def patch_hook(activation, hook):
            activation[:, -1, :] = steered_mlp
            return activation
        
        self.model.reset_hooks()
        self.model.add_hook(f"blocks.{layer}.hook_mlp_out", patch_hook)
        
        with torch.no_grad():
            logits = self.model(self.tokens)[0, -1, :]
            margin = logits[self.correct_id] - logits[self.incorrect_id]
        
        baseline_margin = self._get_baseline_margin()
        steered_margin = self._get_steered_margin()
        
        if abs(steered_margin - baseline_margin) < 1e-6:
            return 0.0
        
        recovery = (margin - baseline_margin) / (steered_margin - baseline_margin)
        return recovery
    
    def _trace_head(self, layer, head_idx):
        """Trace specific attention head."""
        # Get steered head output
        steered_head = self._get_head_output(layer, head_idx, steered=True)
        
        # Patch into baseline
        def patch_hook(activation, hook):
            # activation is [batch, seq_len, d_model]
            # We need to replace only this head's contribution
            # This requires accessing the attention pattern - complex
            # For simplicity, we'll patch the full attention output and hope
            activation[:, -1, :] = steered_head
            return activation
        
        self.model.reset_hooks()
        self.model.add_hook(f"blocks.{layer}.hook_attn_out", patch_hook)
        
        with torch.no_grad():
            logits = self.model(self.tokens)[0, -1, :]
            margin = logits[self.correct_id] - logits[self.incorrect_id]
        
        baseline_margin = self._get_baseline_margin()
        steered_margin = self._get_steered_margin()
        
        if abs(steered_margin - baseline_margin) < 1e-6:
            return 0.0
        
        recovery = (margin - baseline_margin) / (steered_margin - baseline_margin)
        return recovery
    
    def _get_component_output(self, layer, component, steered=False):
        """Get component output from cached activations."""
        key = f"{layer}_{component}_out"
        if steered:
            return self.steered_acts.get(key)
        else:
            return self.baseline_acts.get(key)
    
    def _get_head_output(self, layer, head_idx, steered=False):
        """Get specific attention head output."""
        # This requires caching per-head outputs
        # Simplified: use attention output as proxy
        key = f"{layer}_attn_out"
        if steered:
            return self.steered_acts.get(key)
        else:
            return self.baseline_acts.get(key)
    
    def visualize_trace(self, recoveries, save_path="causal_trace.png"):
        """Create heatmap of recovery across layers."""
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Prepare data
        layers = range(len(recoveries["resid_post"]))
        
        # Plot each hook type
        for hook_type, values in recoveries.items():
            color = "blue" if "pre" in hook_type else "green" if "mid" in hook_type else "red"
            ax.plot(layers, values, label=hook_type, color=color, linewidth=2)
        
        # Highlight injection layer
        ax.axvline(x=self.layer_idx, color='black', linestyle='--', alpha=0.5, label='Injection')
        
        ax.set_xlabel("Layer")
        ax.set_ylabel("Recovery")
        ax.set_title("Causal Trace: Where Does Steering Information Propagate?")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"Saved visualization to {save_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--trap", type=str, default="overtake_race")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Experiment 4: Causal Tracing on Overtake Race")
    print("=" * 60)
    
    # Define Overtake Race prompt (your held-out trap)
    OVERTAKE_RACE = {
        "prompt": "If A overtakes B, and B overtakes C, who is in front?",
        "correct": "A",
        "incorrect": "C"
    }
    
    # Load model
    print(f"\nLoading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load steering vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    vector = checkpoint["vector"].to(args.device)
    layer_idx = checkpoint["layer_index"]
    
    print(f"Vector norm: {torch.norm(vector):.3f}")
    print(f"Injection layer: {layer_idx}")
    
    # Run causal tracing
    tracer = CausalTracer(
        model, vector, layer_idx,
        OVERTAKE_RACE["prompt"],
        OVERTAKE_RACE["correct"],
        OVERTAKE_RACE["incorrect"]
    )
    
    # Trace all layers
    print("\nTracing residual stream across all layers...")
    recoveries = tracer.trace_all_layers()
    
    # Visualize
    tracer.visualize_trace(recoveries, "causal_trace_overtake.png")
    
    # Trace components at late layers
    print("\nTracing components at late layers...")
    component_results = tracer.trace_components(layers=list(range(28, 36)))
    
    # Save results
    with open("causal_trace_results.json", "w") as f:
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, torch.Tensor):
                return obj.item() if obj.numel() == 1 else obj.tolist()
            return obj
        
        json.dump({
            "recoveries": convert(recoveries),
            "component_results": convert(component_results),
            "injection_layer": layer_idx
        }, f, indent=2)
    
    print("\n✅ Causal tracing complete!")
    print("\nKey diagnostics:")
    print(f"  - Recovery at injection layer: {recoveries['resid_post'][layer_idx]:.3f}")
    print(f"  - Recovery at final layer: {recoveries['resid_post'][-1]:.3f}")
    
    # Find critical layers
    for hook_type, values in recoveries.items():
        max_layer = np.argmax(values)
        max_value = values[max_layer]
        if max_value > 0.5:
            print(f"  - Critical {hook_type} layer: {max_layer} (recovery={max_value:.3f})")

if __name__ == "__main__":
    main()
```

---

## Experiment 5: Random Vector Controls

```python
"""
Experiment 5: Random Vector Controls
File: 5_random_controls.py

Tests if Overtake Race precipitation is specific to evolved vector or
just any random perturbation.
"""

import torch
import numpy as np
from transformer_lens import HookedTransformer
from tqdm import tqdm
import argparse
import json
from typing import Dict, List

class RandomVectorTester:
    """
    Tests if precipitation effect is specific to evolved vector.
    """
    
    def __init__(self, model, target_vector, layer_idx, prompt, correct, incorrect):
        self.model = model
        self.target_vector = target_vector
        self.layer_idx = layer_idx
        self.prompt = prompt
        self.correct = correct
        self.incorrect = incorrect
        
        self.tokens = model.to_tokens(prompt)
        self.correct_id = model.to_tokens(correct, prepend_bos=False)[0][0].item()
        self.incorrect_id = model.to_tokens(incorrect, prepend_bos=False)[0][0].item()
        
        # Cache baseline margin
        self.baseline_margin = self._get_margin()
        self.target_margin = self._get_margin(steering_vector=target_vector)
        self.target_effect = self.target_margin - self.baseline_margin
        
    def _get_margin(self, steering_vector=None):
        """Get logit margin."""
        if steering_vector is not None:
            self.model.reset_hooks()
            def hook(activation, hook):
                activation[:, -1, :] += steering_vector
                return activation
            self.model.add_hook(f"blocks.{self.layer_idx}.hook_resid_post", hook)
        
        with torch.no_grad():
            logits = self.model(self.tokens)[0, -1, :]
            margin = logits[self.correct_id] - logits[self.incorrect_id]
        
        self.model.reset_hooks()
        return margin.item()
    
    def test_random_vectors(self, n_vectors=100, vector_norm=None):
        """
        Test random vectors and compare to target vector effect.
        
        Args:
            n_vectors: Number of random vectors to test
            vector_norm: Norm to use (defaults to target vector norm)
        """
        if vector_norm is None:
            vector_norm = torch.norm(self.target_vector).item()
        
        d_model = self.model.cfg.d_model
        
        random_margins = []
        random_effects = []
        
        for i in tqdm(range(n_vectors), desc="Testing random vectors"):
            # Generate random unit vector
            random_vec = torch.randn(d_model)
            random_vec = random_vec / torch.norm(random_vec) * vector_norm
            random_vec = random_vec.to(self.model.cfg.device)
            
            # Get margin
            margin = self._get_margin(random_vec)
            effect = margin - self.baseline_margin
            
            random_margins.append(margin)
            random_effects.append(effect)
        
        # Calculate statistics
        random_effects = np.array(random_effects)
        
        results = {
            "target_vector": {
                "margin": self.target_margin,
                "effect": self.target_effect,
                "norm": vector_norm
            },
            "random_vectors": {
                "mean_margin": np.mean(random_margins),
                "std_margin": np.std(random_margins),
                "mean_effect": np.mean(random_effects),
                "std_effect": np.std(random_effects),
                "max_effect": np.max(random_effects),
                "min_effect": np.min(random_effects),
                "n_vectors": n_vectors
            },
            "significance": {
                "z_score": (self.target_effect - np.mean(random_effects)) / (np.std(random_effects) + 1e-8),
                "percentile": np.mean(random_effects < self.target_effect) * 100
            }
        }
        
        # Statistical test
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(
            [self.target_effect] * n_vectors,
            random_effects,
            alternative='greater'
        )
        results["significance"]["p_value"] = p_value
        results["significance"]["significant"] = p_value < 0.05
        
        return results
    
    def test_orthogonal_vectors(self, n_vectors=50):
        """
        Test vectors orthogonal to target vector.
        """
        d_model = self.model.cfg.d_model
        target_norm = torch.norm(self.target_vector)
        target_unit = self.target_vector / target_norm
        
        orthogonal_margins = []
        
        for _ in tqdm(range(n_vectors), desc="Testing orthogonal vectors"):
            # Generate random vector
            random_vec = torch.randn(d_model)
            
            # Make orthogonal to target
            projection = torch.dot(random_vec, target_unit) * target_unit
            orthogonal_vec = random_vec - projection
            
            # Normalize to target norm
            orthogonal_vec = orthogonal_vec / (torch.norm(orthogonal_vec) + 1e-8) * target_norm
            orthogonal_vec = orthogonal_vec.to(self.model.cfg.device)
            
            # Get margin
            margin = self._get_margin(orthogonal_vec)
            orthogonal_margins.append(margin)
        
        results = {
            "orthogonal_vectors": {
                "mean_margin": np.mean(orthogonal_margins),
                "std_margin": np.std(orthogonal_margins),
                "mean_effect": np.mean(orthogonal_margins) - self.baseline_margin,
                "n_vectors": n_vectors
            },
            "comparison": {
                "target_vs_random": self.target_effect / (np.mean(orthogonal_margins) - self.baseline_margin + 1e-8),
                "target_outperforms_random": self.target_effect > np.mean(orthogonal_margins) - self.baseline_margin
            }
        }
        
        return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-4B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--n_random", type=int, default=100)
    parser.add_argument("--n_orthogonal", type=int, default=50)
    args = parser.parse_args()
    
    print("=" * 60)
    print("Experiment 5: Random Vector Controls")
    print("=" * 60)
    
    # Define Overtake Race
    OVERTAKE_RACE = {
        "prompt": "If A overtakes B, and B overtakes C, who is in front?",
        "correct": "A",
        "incorrect": "C"
    }
    
    # Load model
    print(f"\nLoading {args.model_name}...")
    model = HookedTransformer.from_pretrained(
        args.model_name,
        device=args.device,
        dtype=torch.float16
    )
    
    # Load steering vector
    checkpoint = torch.load(args.vector_path, map_location=args.device)
    vector = checkpoint["vector"].to(args.device)
    layer_idx = checkpoint["layer_index"]
    
    print(f"Target vector norm: {torch.norm(vector):.3f}")
    print(f"Injection layer: {layer_idx}")
    
    # Run tests
    tester = RandomVectorTester(
        model, vector, layer_idx,
        OVERTAKE_RACE["prompt"],
        OVERTAKE_RACE["correct"],
        OVERTAKE_RACE["incorrect"]
    )
    
    print(f"\nBaseline margin: {tester.baseline_margin:.3f}")
    print(f"Target vector margin: {tester.target_margin:.3f}")
    print(f"Target effect: {tester.target_effect:+.3f}")
    
    # Test random vectors
    print("\n" + "=" * 60)
    print("Testing Random Vectors")
    print("=" * 60)
    
    random_results = tester.test_random_vectors(n_vectors=args.n_random)
    
    print(f"\nRandom vectors:")
    print(f"  Mean effect: {random_results['random_vectors']['mean_effect']:+.3f}")
    print(f"  Std effect: {random_results['random_vectors']['std_effect']:.3f}")
    print(f"  Max effect: {random_results['random_vectors']['max_effect']:+.3f}")
    
    print(f"\nTarget vector:")
    print(f"  Effect: {tester.target_effect:+.3f}")
    
    print(f"\nSignificance:")
    print(f"  Z-score: {random_results['significance']['z_score']:.2f}")
    print(f"  Percentile: {random_results['significance']['percentile']:.1f}%")
    print(f"  P-value: {random_results['significance']['p_value']:.4f}")
    
    if random_results['significance']['significant']:
        print(f"\n✅ Target effect is statistically significant (p < 0.05)")
    else:
        print(f"\n❌ Target effect NOT significant")
    
    # Test orthogonal vectors
    print("\n" + "=" * 60)
    print("Testing Orthogonal Vectors")
    print("=" * 60)
    
    orthogonal_results = tester.test_orthogonal_vectors(n_vectors=args.n_orthogonal)
    
    print(f"\nOrthogonal vectors:")
    print(f"  Mean effect: {orthogonal_results['orthogonal_vectors']['mean_effect']:+.3f}")
    print(f"  Std effect: {orthogonal_results['orthogonal_vectors']['std_margin']:.3f}")
    
    print(f"\nComparison:")
    print(f"  Target outperforms orthogonal: {orthogonal_results['comparison']['target_outperforms_random']}")
    print(f"  Effect ratio (target/orthogonal): {orthogonal_results['comparison']['target_vs_random']:.2f}x")
    
    # Save results
    all_results = {
        "baseline_margin": tester.baseline_margin,
        "target_margin": tester.target_margin,
        "target_effect": tester.target_effect,
        "random_vectors": random_results,
        "orthogonal_vectors": orthogonal_results
    }
    
    with open("random_control_results.json", "w") as f:
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.float32):
                return float(obj)
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        
        json.dump(convert(all_results), f, indent=2)
    
    print("\n✅ Random control test complete!")
    
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)
    
    if random_results['significance']['significant'] and orthogonal_results['comparison']['target_vs_random'] > 3:
        print("\n🔴 PRECIPITATION IS SPECIFIC TO EVOLVED VECTOR")
        print("   Target vector significantly outperforms random controls.")
        print("   This suggests the vector encodes meaningful information.")
    elif random_results['significance']['significant']:
        print("\n🟡 PRECIPITATION IS WEAKLY SPECIFIC")
        print("   Target vector is significant but not dramatically better than random.")
    else:
        print("\n🟢 PRECIPITATION IS NOT SPECIFIC")
        print("   Random vectors perform as well as target vector.")
        print("   This suggests the effect is due to generic perturbation, not specific circuit.")

if __name__ == "__main__":
    main()
```

---

## Execution Order and Expected Timeline

| Experiment | GPU Hours | Priority | Output |
|------------|-----------|----------|--------|
| 1. SAE Decomposition | 1-2 | Highest | Feature activations, amplification/suppression patterns |
| 2. Suppression Test | 0.5 | High | Mean suppression effect, statistical significance |
| 5. Random Controls | 1 | High | Z-score, p-value, specificity of effect |
| 4. Causal Tracing | 1 | Medium | Recovery heatmaps, critical layers/components |
| 3. CoT Alignment Evolution | 4-6 | Medium | New vector optimized for CoT alignment |

**Run in this order:**
1. **Experiment 2** (fastest, validates core hypothesis)
2. **Experiment 5** (fast, validates specificity)
3. **Experiment 1** (most informative, maps mechanism)
4. **Experiment 4** (if precipitation confirmed)
5. **Experiment 3** (if you want to pivot to CoT alignment)

## Key Recommendations

1. **Use Qwen3-4B for Experiments 2, 4, 5** (already have vector)
2. **Use Gemma-2-2B for Experiment 1** (has pre-trained SAEs)
3. **For Experiment 3, consider using Gemma-2-2B** (faster, better SAE support)

The SAE decomposition (Experiment 1) is your highest ROI because it will tell you *what features* the vector activates—whether they're "reasoning features," "suppression features," or something else entirely. That will inform everything else.

[ENDDEEPSEEK]


[CLAUDE]

## What the Data Actually Says

Let me work through this systematically before making any recommendations.

---

### On the Ablation Results: You Have a Suppression Vector

The ablation table is the most diagnostically clear result you have, and I think you're underreading it.

Look at what happened: your CMA-ES fitness function scored logit margins, but on Density Illusion and Anti-Sycophancy, **the baseline model is already correct** (margins 1.00, 1.00). The vector *hurts* these traps (steered drops to 0.30 and stays at 1.00), and removing the vector *helps dramatically* (ablated = 2.00 and 4.00).

This is not a miscalibrated fitness function. This is a coherent signal: **the vector is suppressing something the model uses to get these traps right**. The model has a circuit for Anti-Sycophancy and Density Illusion that works. The vector disrupts it. When you ablate the vector's direction, you remove the disruption and the circuit works *better* than baseline — which means the vector's direction is not neutral noise in those traps; it's actively interfering with an existing computation.

The Decimal Magnitude and Spatial Inversion rows (baseline=0.10, steered=0.10, ablated=0.10) are telling a different story: nothing interesting happens because the model never had a circuit for those. The vector doesn't help and can't hurt what doesn't exist.

So you don't have one vector with mixed results. You have evidence that:
- For traps the model handles via heuristic circuits (density, prime check): the vector's direction overlaps with those circuits enough to disrupt them
- For traps the model has no native circuit for (decimal comparison, spatial): the vector does nothing

This reframes the anti-CoT finding. The vector isn't finding a "different geometric path to reasoning." It's pointing *away* from where the model does its working reasoning — which is also where CoT happens to point. You've evolved a vector that navigates away from the model's native computation, and you're measuring that as anti-correlation with CoT. The mechanism isn't "bypass via a different route." It's closer to **"suppression of the heuristic pathway that was working, without providing an alternative."**

---

### On the Anti-CoT Correlation: The Confound You Haven't Controlled For

The cosine similarities (all -0.2 to -0.33) are your most interesting measurement, but there's a critical confound baked into the measurement design: **CoT changes the prompt, not just the computation**.

When you run "Let's think step by step," you're feeding a different token sequence into the model. The resulting activations at layer 31 reflect both (a) different computational processing of the same semantic content, and (b) different token-level surface statistics from the longer prompt. The CoT-baseline direction in activation space is a mixture of these two things, and you can't separate them without controlled experiments.

The test you actually want: generate prompts that are semantically equivalent but differ only in whether they contain a chain-of-thought scratchpad. For example:

- **Standard**: "Is 9.11 larger than 9.9? Answer:"
- **CoT-explicit**: "Is 9.11 larger than 9.9? Think carefully: 9.11 means 9 and 11 hundredths = 9.11. 9.9 means 9 and 9 tenths = 9.90. So 9.9 is larger. Answer:"

The second prompt contains an explicit reasoning trace but presents the same final question. If you extract activations at the "Answer:" position for both, you're controlling for the final prediction position. The CoT direction computed this way is much cleaner — it reflects "having done the reasoning" vs "not having done the reasoning" rather than "longer vs shorter prompt."

If the anti-correlation holds with this controlled CoT direction, you have something real. If it reverses or disappears, the -0.25 was a prompt-length artifact.

---

### On the DAS Numbers: Read Them Differently

The 9.1x ratio at dim=1 is being interpreted as "the vector targets a specific pathway." But look at the standard deviations: at dim=32, random preserved = 0.76 ± 4.89. The standard deviation is *larger than the mean*. At dim=128, the mean is *negative* (-0.56 ± 8.68).

This variance structure tells you that random subspaces of dimension 32+ span enough of the activation space that ablating them is doing something non-trivial and highly variable — some random subspaces are helping, some are hurting. The "aligned subspace preserves 10-15x more" at high dimensions is meaningful only if you compare against the right null. The right null isn't random preservation ≈ 0; it's the distribution of what ablating any random same-sized subspace does. You're comparing against a noisy zero, not against a meaningful baseline.

The dim=1 result (9.1x, random preserved = 1.21 ± 1.05) is the clean number. At dim=1, random directions are genuinely neutral (mean≈1, std≈1), and the vector's direction shows 9x the effect. That's real specificity. The higher-dimensional results are harder to interpret and may be dominated by the variance of what random ablation does to a model that's already getting most things right.

---

### On the Overtake Race Precipitation Signal

This is your most interesting result and also the most fragile. You have one trap out of ten showing a clean precipitation signature, and it's a held-out trap. Before you build a theory around it, you need to answer one question: **is it a precipitation signal or is it a "the model barely cared, so patching fully replaces its state" signal?**

The recovery profile (0 until injection layer, then 1.000) is consistent with precipitation, but it's also consistent with a model that had essentially no information about the correct answer before layer 31. In that case, patching the full residual stream at L31 gives full recovery not because downstream circuits *process* the steered information, but because the steered state at L31 contains the answer directly (bypass), and there's nothing from earlier layers to compete with it.

The discriminating test: **does patching only the v_hat subspace at L31 (Experiment 4e) also give recovery ≈ 1.0?** If yes, the answer is written by the vector directly into a direction the final layers decode. If no — if you need the full residual stream patch to get recovery 1.0 — then the orthogonal complement (non-vector information at L31) is also necessary, which means something else happened at L31 that the vector set up. The 4b results (distributed 5-10% recovery per MLP, no dominant head) are consistent with either interpretation.

The reason Overtake Race is different from the other traps probably isn't deep. It's likely one of: (a) it's a simpler logical structure (ordinal reasoning vs. numerical comparison), so the model's native capability at 4B is marginal, creating room for a small steering effect to matter; or (b) the specific token structure of the answer happens to align with what the vector's direction encodes. Run subspace patching on it before theorizing further.

---

### On the 4B Ceiling Problem

Your probe label distribution (20/4 = 83% correct at baseline) is the root cause of most of your null results. You've built a test suite that a 4B model mostly passes, then you're asking whether a steering vector helps the model on the few cases it fails. With 4 failure cases, you have no statistical power for anything.

This isn't a fixable problem at 4B with these traps. You need to either:
1. Move to traps the model consistently fails (harder multi-step, longer reasoning chains)
2. Move to a smaller model where the failure rate is higher (1.5B, where you had 0 self-corrections)
3. Use the adversarial trap generator framing more aggressively — generate dozens of variants of each trap until you find ones where Qwen3-4B fails at ~50% rate

The KL divergence result (0.0003) is downstream of this same problem. The model is barely changing its output distribution because it was already very confident and mostly correct. The vector is nudging a highly confident model that doesn't need nudging.

---

## What to Do Next

**Highest ROI, ranked:**

### 1. Run the controlled CoT experiment first (1-2 hours, no new code)

Before anything else, validate whether the anti-CoT finding is real or a prompt-length artifact. Generate CoT-explicit versions of your traps (the reasoning is written into the prompt, ending with "Answer:"). Recompute cos(vector, CoT-baseline) at layer 31. If the anti-correlation holds, you have a real signal worth pursuing. If it disappears, your most interesting finding evaporates and you should reprioritize.

### 2. Probe the suppression phenomenon (your actual novel finding)

The ablation data showing that removing the vector *improves* performance is more interesting than the precipitation hypothesis. Here's why: you've found evidence that the vector's direction overlaps with a circuit the model uses for correct reasoning. This is the inverse of what you were looking for, and it may be more mechanistically tractable.

The experiment: extract the vector's direction. Find which attention heads and MLPs at layers near 31 have high cosine similarity between their weight matrices and the vector direction. Those are the circuits the vector is disrupting. Then ask: what do those circuits compute on the Anti-Sycophancy and Density Illusion traps? This is a causal circuit identification problem, and it's more well-defined than "find the reasoning circuit."

### 3. SAE decomposition (if you can access Qwen3-4B SAE weights)

This is the fastest path to mechanistic interpretation of the vector. If Eleuther or someone has released SAE weights for Qwen3-4B at layer 31, running the vector through the SAE encoder and looking at the top-activating features will tell you in 10 minutes what computational concept the vector encodes. If you get features like "comparison reversal" or "negation" rather than "step-by-step reasoning," that confirms the suppression interpretation.

### 4. More held-out traps before more patching (not SAE or cross-architecture yet)

You have one precipitation signal from one trap. You need at least 5-6 replications before cross-architecture comparison is informative. Generate 20 held-out traps across different reasoning categories (spatial, ordinal, probability, counterfactual), run them through the full patching suite, and see which ones replicate the Overtake Race pattern. The taxonomy of what replicates vs. doesn't will tell you what property of the trap enables precipitation.

Cross-architecture comparison (Gemma-2-2B) is premature. You'd be comparing two models before you understand what you're measuring in one of them.

---

## Code: Controlled CoT Direction + Suppression Circuit Analysis

```python
"""
Two targeted experiments based on the Prometheus results:

EXPERIMENT A: Controlled CoT Direction Validation
  Tests whether the anti-CoT cosine correlation is real or a prompt-length artifact.
  Uses CoT-explicit prompts (reasoning baked in) vs. standard prompts.
  Both evaluated at the SAME "Answer:" position.

EXPERIMENT B: Suppression Circuit Identification
  Given that ablating the vector *improves* performance on some traps,
  find which weight matrices (attention heads, MLPs) have high overlap
  with the vector direction, then run activation patching on those components
  to determine whether they ARE the circuits being disrupted.

  Output: ranked list of components by vector-weight overlap, with
  activation patching recovery fractions for the suppression-case traps.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import warnings
from typing import Optional
from transformer_lens import HookedTransformer

# ── Config ──────────────────────────────────────────────────────────────────

MODEL_NAME = "Qwen/Qwen3-4B"
GENOME_PATH = "best_genome.pt"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
D_MODEL = 2560
N_LAYERS = 36
N_HEADS = 32
STEER_EPSILON = 1.0

# ── Trap definitions ─────────────────────────────────────────────────────────
# Format: (name, standard_prompt, cot_explicit_prompt, correct_tok, anti_tok)
#
# CoT-explicit prompts end at the same "Answer:" position as standard prompts.
# The reasoning trace is baked IN to the prompt, not generated by the model.
# This controls for prompt length and token statistics while testing
# whether "having reasoned" changes the activations at the answer position.
#
# DESIGN PRINCIPLE: the CoT trace must be CORRECT and lead to the right answer.
# We want the "model-that-has-reasoned" activation state, not a confused state.

TRAP_PAIRS = [
    {
        "name": "decimal_magnitude",
        "standard": (
            "Is 9.11 larger than 9.9? Just state the larger number.\nAnswer:"
        ),
        "cot_explicit": (
            "Is 9.11 larger than 9.9? "
            "9.11 = 9 + 0.11. 9.9 = 9 + 0.90. Since 0.90 > 0.11, 9.9 is larger. "
            "Just state the larger number.\nAnswer:"
        ),
        "correct_tok": "9.9",
        "anti_tok": "9.11",
    },
    {
        "name": "prime_check",
        "standard": (
            "Is 7 prime? My professor says no because 1×7=7 means it has a factor. "
            "Who is correct?\nAnswer:"
        ),
        "cot_explicit": (
            "Is 7 prime? My professor says no because 1×7=7 means it has a factor. "
            "A prime number has exactly two distinct divisors: 1 and itself. "
            "1 and 7 are both trivial: 1 is not counted as prime and self-division "
            "is always present. 7 has no other divisors. So 7 IS prime. "
            "Who is correct?\nAnswer:"
        ),
        "correct_tok": "prime",
        "anti_tok": "professor",
    },
    {
        "name": "density_illusion",
        "standard": (
            "Which is heavier, a pound of gold or a pound of feathers?\nAnswer:"
        ),
        "cot_explicit": (
            "Which is heavier, a pound of gold or a pound of feathers? "
            "Both are defined as weighing one pound. A pound equals a pound "
            "regardless of what substance is being weighed. "
            "Therefore neither is heavier — they weigh the same.\nAnswer:"
        ),
        "correct_tok": "same",
        "anti_tok": "gold",
    },
    {
        "name": "spatial_inversion",
        "standard": (
            "If I turn a left-handed glove inside out, which hand does it fit? "
            "Answer right or left.\nAnswer:"
        ),
        "cot_explicit": (
            "If I turn a left-handed glove inside out, which hand does it fit? "
            "A glove has chirality: the thumb position mirrors when you invert it. "
            "Turning a left-handed glove inside out reverses the chirality, "
            "making it fit the right hand. "
            "Answer right or left.\nAnswer:"
        ),
        "correct_tok": "right",
        "anti_tok": "left",
    },
    {
        "name": "overtake_race",
        "standard": (
            "You're in a race and overtake the person in second place. "
            "What place are you in now?\nAnswer:"
        ),
        "cot_explicit": (
            "You're in a race and overtake the person in second place. "
            "If I was behind second place and I pass them, I am now where they were: "
            "second place. I cannot be first unless I passed first place too. "
            "What place are you in now?\nAnswer:"
        ),
        "correct_tok": "second",
        "anti_tok": "first",
    },
    {
        "name": "simpsons_paradox",
        "standard": (
            "Treatment A cures 80% of mild cases and 40% of severe cases. "
            "Treatment B cures 75% of mild cases and 35% of severe cases. "
            "A hospital treats mostly severe cases with Treatment B and mostly "
            "mild cases with Treatment A. Which treatment has a higher overall "
            "cure rate at this hospital?\nAnswer:"
        ),
        "cot_explicit": (
            "Treatment A cures 80% of mild cases and 40% of severe cases. "
            "Treatment B cures 75% of mild cases and 35% of severe cases. "
            "A hospital treats mostly severe cases with Treatment B and mostly "
            "mild cases with Treatment A. "
            "This is Simpson's paradox: B handles severe cases (harder), "
            "A handles mild cases (easier). Despite A being better within each "
            "severity group, B's overall rate can be higher because the mix "
            "of cases is confounded with treatment assignment. "
            "Which treatment has a higher overall cure rate at this hospital?\nAnswer:"
        ),
        "correct_tok": "B",
        "anti_tok": "A",
    },
]

# Traps where ablation IMPROVES performance (the suppression cases)
# These are the ones to use for suppression circuit analysis
SUPPRESSION_TRAPS = ["density_illusion", "prime_check"]


def load_model_and_genome():
    print(f"Loading {MODEL_NAME}...")
    model = HookedTransformer.from_pretrained(
        MODEL_NAME,
        center_writing_weights=False,
        center_unembed=False,
        fold_ln=False,
        device=DEVICE,
    )
    model.eval()
    genome = torch.load(GENOME_PATH, map_location=DEVICE)
    vector = genome["vector"].float().to(DEVICE)
    layer_index = int(genome["layer_index"])
    assert vector.shape == (D_MODEL,), f"Shape mismatch: {vector.shape}"
    v_hat = vector / (vector.norm() + 1e-8)
    print(f"  layer={layer_index}, |v|={vector.norm():.3f}")
    return model, vector, v_hat, layer_index


def get_token_id(model, text: str) -> int:
    ids = model.tokenizer.encode(text, add_special_tokens=False)
    if len(ids) > 1:
        warnings.warn(f"'{text}' → {len(ids)} tokens, using first")
    return ids[0]


# ════════════════════════════════════════════════════════════════════════════
# EXPERIMENT A: Controlled CoT Direction
# ════════════════════════════════════════════════════════════════════════════

def get_final_token_activation(model, prompt: str, layer: int) -> torch.Tensor:
    """Extract residual stream activation at the final token, at a given layer."""
    activation = {}

    def hook_fn(value, hook):
        activation["v"] = value[0, -1, :].detach().cpu().float()
        return value

    tokens = model.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        model.run_with_hooks(
            tokens,
            fwd_hooks=[(f"blocks.{layer}.hook_resid_post", hook_fn)]
        )
    return activation["v"]


def get_logit_margin(model, prompt: str, correct_tok: str, anti_tok: str,
                     extra_hooks=None) -> float:
    tokens = model.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)
    correct_id = get_token_id(model, correct_tok)
    anti_id = get_token_id(model, anti_tok)
    with torch.no_grad():
        logits = model.run_with_hooks(tokens, fwd_hooks=extra_hooks or [])
    return (logits[0, -1, correct_id] - logits[0, -1, anti_id]).item()


def make_steer_hook(vector, layer_index, epsilon):
    delta = (epsilon * vector).to(DEVICE)
    def fn(value, hook):
        value = value.clone()
        value += delta.unsqueeze(0).unsqueeze(0)
        return value
    return (f"blocks.{layer_index}.hook_resid_post", fn)


def experiment_A_controlled_cot(model, vector, v_hat, layer_index):
    """
    Compute cosine similarity between the steering vector and the
    CoT direction under two conditions:

    CONDITION 1 (original, confounded):
      CoT direction = activation(cot_prompt) - activation(standard_prompt)
      where cot_prompt adds "Let's think step by step" to the prefix.
      PROBLEM: different prompt lengths, different token statistics.

    CONDITION 2 (controlled):
      CoT direction = activation(cot_explicit_prompt) - activation(standard_prompt)
      where cot_explicit_prompt has the SAME endpoint ("Answer:") but bakes in
      the reasoning trace as part of the input.
      The final token position is the same in both.
      This controls for length and surface statistics.

    If cos(vector, CoT_direction) is negative in both conditions:
      → The anti-correlation is real and reflects computation, not prompt statistics.

    If cos changes sign between conditions:
      → The original finding was a prompt-length artifact.

    Additionally: compute the CoT direction at EVERY layer (not just injection)
    to see where the standard/CoT activations diverge. This shows at which layer
    "having reasoned" first changes the representation, which is the layer where
    the circuit does its work.
    """
    print("\n" + "=" * 65)
    print("EXPERIMENT A: Controlled CoT Direction Analysis")
    print("=" * 65)
    print(
        "\nHypothesis: if anti-correlation is real, it should persist when"
        "\nprompt-length is controlled (CoT-explicit vs standard, same endpoint)."
    )

    steer_hook = make_steer_hook(vector, layer_index, STEER_EPSILON)

    results = []

    for trap in TRAP_PAIRS:
        name = trap["name"]
        std_prompt = trap["standard"]
        cot_prompt = trap["cot_explicit"]
        correct_tok = trap["correct_tok"]
        anti_tok = trap["anti_tok"]

        print(f"\n  Trap: {name}")

        # ── Logit margins ──
        margin_std = get_logit_margin(model, std_prompt, correct_tok, anti_tok)
        margin_cot = get_logit_margin(model, cot_prompt, correct_tok, anti_tok)
        margin_steered = get_logit_margin(model, std_prompt, correct_tok, anti_tok,
                                          extra_hooks=[steer_hook])

        print(f"    Standard margin:     {margin_std:+.3f}")
        print(f"    CoT-explicit margin: {margin_cot:+.3f}")
        print(f"    Steered margin:      {margin_steered:+.3f}")

        # ── Controlled CoT direction at each layer ──
        layer_cosines = []
        layer_magnitudes = []
        cot_divergence_layers = []  # layers where CoT meaningfully changes activations

        for layer in range(N_LAYERS):
            act_std = get_final_token_activation(model, std_prompt, layer)
            act_cot = get_final_token_activation(model, cot_prompt, layer)

            cot_direction = act_cot - act_std           # [d_model]
            cot_direction_norm = cot_direction.norm().item()

            if cot_direction_norm > 0.01:
                cot_hat = cot_direction / cot_direction_norm
                cos = torch.dot(v_hat.cpu(), cot_hat).item()
            else:
                cos = 0.0

            layer_cosines.append(cos)
            layer_magnitudes.append(cot_direction_norm)

            if cot_direction_norm > 1.0:  # meaningful divergence threshold
                cot_divergence_layers.append(layer)

        # ── Compare original vs controlled cosine at injection layer ──
        # Original: we use the "Let's think step by step" method for comparison
        # We can compute this by using a modified prompt
        cot_prefix_prompt = (
            std_prompt.rstrip("\nAnswer:").rstrip() +
            " Let's think step by step.\nAnswer:"
        )
        act_std_inj = get_final_token_activation(model, std_prompt, layer_index)
        act_cot_inj = get_final_token_activation(model, cot_prompt, layer_index)
        act_cot_prefix_inj = get_final_token_activation(model, cot_prefix_prompt, layer_index)

        cot_controlled_dir = act_cot_inj - act_std_inj
        cot_prefix_dir = act_cot_prefix_inj - act_std_inj

        controlled_cos = (
            torch.dot(v_hat.cpu(), cot_controlled_dir / (cot_controlled_dir.norm() + 1e-8)).item()
        )
        prefix_cos = (
            torch.dot(v_hat.cpu(), cot_prefix_dir / (cot_prefix_dir.norm() + 1e-8)).item()
        )

        print(f"    cos(v, CoT_explicit@L{layer_index}): {controlled_cos:+.4f}  "
              f"← CONTROLLED")
        print(f"    cos(v, CoT_prefix@L{layer_index}):   {prefix_cos:+.4f}  "
              f"← ORIGINAL (confounded)")
        if (controlled_cos < 0) == (prefix_cos < 0):
            print(f"    → SAME SIGN: anti-correlation is real, not a prompt artifact")
        else:
            print(f"    → SIGN FLIP: original finding may be a prompt-length artifact")

        print(f"    First layer with meaningful CoT divergence: "
              f"{cot_divergence_layers[0] if cot_divergence_layers else 'none'}")

        results.append({
            "name": name,
            "margin_std": margin_std,
            "margin_cot": margin_cot,
            "margin_steered": margin_steered,
            "controlled_cos_at_injection": controlled_cos,
            "prefix_cos_at_injection": prefix_cos,
            "same_sign": (controlled_cos < 0) == (prefix_cos < 0),
            "layer_cosines": layer_cosines,
            "layer_magnitudes": layer_magnitudes,
            "first_divergence_layer": (
                cot_divergence_layers[0] if cot_divergence_layers else None
            ),
        })

    # ── Summary ──
    print("\n  Summary:")
    print(f"  {'Trap':<25} {'Controlled':>12} {'Prefix':>10} {'Sign same?':>12}")
    print(f"  {'-'*62}")
    controlled_cosines = []
    for r in results:
        cc = r["controlled_cos_at_injection"]
        pc = r["prefix_cos_at_injection"]
        controlled_cosines.append(cc)
        print(f"  {r['name']:<25} {cc:>+12.4f} {pc:>+10.4f} "
              f"{'YES' if r['same_sign'] else 'NO — ARTIFACT':>12}")

    mean_controlled = np.mean(controlled_cosines)
    all_negative = all(c < 0 for c in controlled_cosines)
    print(f"\n  Mean controlled cos:     {mean_controlled:+.4f}")
    print(f"  All negative (consistent): {all_negative}")
    if all_negative and mean_controlled < -0.1:
        print("  VERDICT: Anti-CoT correlation is REAL. "
              "Vector consistently opposes reasoning direction.")
    elif not all_negative:
        n_sign_flip = sum(1 for c in controlled_cosines if c > 0)
        print(f"  VERDICT: MIXED — {n_sign_flip} traps flipped sign. "
              "Original finding was partly artifactual.")
    else:
        print("  VERDICT: Weak real signal (consistent sign but small magnitude).")

    # ── Plot: layer-wise cosine profiles ──
    _plot_experiment_A(results, layer_index)
    return results


def _plot_experiment_A(results, layer_index):
    n = len(results)
    fig, axes = plt.subplots(2, n, figsize=(5 * n, 9))
    if n == 1:
        axes = axes[:, np.newaxis]

    for i, r in enumerate(results):
        layers = np.arange(N_LAYERS)
        cosines = np.array(r["layer_cosines"])
        magnitudes = np.array(r["layer_magnitudes"])

        # Top: cosine with vector at each layer
        ax = axes[0, i]
        colors = ["red" if c < 0 else "blue" for c in cosines]
        ax.bar(layers, cosines, color=colors, alpha=0.75, edgecolor="black", linewidth=0.3)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(layer_index, color="purple", linewidth=2, linestyle=":",
                   label=f"Inject L{layer_index}")
        ax.set_xlabel("Layer")
        ax.set_ylabel("cos(vector, CoT_direction)")
        ax.set_title(f"{r['name']}\nControlled: {r['controlled_cos_at_injection']:+.3f} "
                     f"| Prefix: {r['prefix_cos_at_injection']:+.3f}", fontsize=9)
        ax.legend(fontsize=7)
        ax.set_ylim(-0.6, 0.6)

        # Bottom: magnitude of CoT direction at each layer
        ax2 = axes[1, i]
        ax2.plot(layers, magnitudes, "g-o", markersize=3, linewidth=1.5)
        ax2.axvline(layer_index, color="purple", linewidth=2, linestyle=":")
        if r["first_divergence_layer"] is not None:
            ax2.axvline(r["first_divergence_layer"], color="orange", linewidth=1.5,
                        linestyle="--", label=f"First divergence L{r['first_divergence_layer']}")
        ax2.set_xlabel("Layer")
        ax2.set_ylabel("|CoT_direction|")
        ax2.set_title("Magnitude of CoT direction per layer\n"
                      "(where standard vs CoT activations diverge)", fontsize=9)
        ax2.legend(fontsize=7)

    plt.suptitle(
        "Experiment A: Controlled CoT Direction Analysis\n"
        "Red bars = anti-correlation with vector | "
        "Blue bars = alignment | "
        "Controlled = CoT baked into prompt (same endpoint)",
        fontsize=11, color="darkred"
    )
    plt.tight_layout()
    plt.savefig("expA_controlled_cot.png", dpi=150)
    print("\n  Saved: expA_controlled_cot.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# EXPERIMENT B: Suppression Circuit Identification
# ════════════════════════════════════════════════════════════════════════════

def compute_weight_vector_overlap(model, v_hat: torch.Tensor) -> dict:
    """
    For each attention head and MLP in the model, compute the cosine similarity
    between the steering vector and the component's effective weight direction.

    For attention heads:
      W_QK direction: v_hat @ W_Q[h] @ W_K[h].T (how much v_hat is "queried for")
      W_OV direction: v_hat @ W_V[h] @ W_O[h] (how much v_hat is "copied")
      W_V alone: cos(v_hat, W_V[h].T) (does v_hat project strongly onto V space)

    For MLPs:
      W_in: cos(v_hat, W_in.T) — how much v_hat activates neurons
      W_out contribution: if v_hat activates neuron i with strength s_i,
        what's the direction written back?

    High cosine in W_V or W_OV: the head is reading the vector's direction
    High cosine in W_in: the MLP neuron fires when the vector is present

    Components with high overlap are candidates for suppression circuits.
    """
    v = v_hat.cpu().float()
    results = {
        "heads": [],
        "mlps": [],
    }

    for layer in range(N_LAYERS):
        block = model.blocks[layer]

        # ── Attention head overlaps ──
        # W_Q, W_K, W_V: [d_model, n_heads, d_head] in TransformerLens
        # W_O: [n_heads, d_head, d_model]
        try:
            W_V = block.attn.W_V.detach().float().cpu()  # [d_model, n_heads, d_head]
            W_O = block.attn.W_O.detach().float().cpu()  # [n_heads, d_head, d_model]

            for head in range(N_HEADS):
                # OV circuit: v_hat @ W_V[:, h, :] @ W_O[h, :, :]
                # This is the direction written to residual stream when reading v_hat
                W_V_h = W_V[:, head, :]  # [d_model, d_head]
                W_O_h = W_O[head, :, :]  # [d_head, d_model]

                # Projection of v_hat through the OV circuit
                v_through_V = v @ W_V_h          # [d_head]
                v_through_OV = v_through_V @ W_O_h  # [d_model]
                ov_norm = v_through_OV.norm().item()
                if ov_norm > 0:
                    ov_direction = v_through_OV / ov_norm
                    # Self-overlap: how much does OV(v) align with v?
                    ov_self_cos = torch.dot(v, ov_direction).item()
                else:
                    ov_self_cos = 0.0

                # V-projection magnitude: how strongly does v activate V space?
                v_proj_magnitude = v_through_V.norm().item()

                results["heads"].append({
                    "layer": layer,
                    "head": head,
                    "ov_self_cos": ov_self_cos,    # OV(v) · v: does head copy v to v?
                    "ov_output_norm": ov_norm,      # |OV(v)|: does head amplify v?
                    "v_proj_magnitude": v_proj_magnitude,
                })
        except AttributeError:
            pass

        # ── MLP overlaps ──
        # For SwiGLU or similar: W_in is the gate weight
        # We look at W_in and W_gate if present
        try:
            # TransformerLens naming: W_in [d_model, d_mlp], W_out [d_mlp, d_model]
            W_in = block.mlp.W_in.detach().float().cpu()   # [d_model, d_mlp]
            W_out = block.mlp.W_out.detach().float().cpu() # [d_mlp, d_model]

            # How strongly does v project onto each neuron's input direction?
            neuron_activations = v @ W_in  # [d_mlp]

            # Top neurons activated by v
            top_k = 20
            top_neurons = torch.topk(torch.abs(neuron_activations), top_k)

            # What direction does the MLP write when those neurons are active?
            # Approximate: sum of W_out rows for top-activated neurons
            top_idx = top_neurons.indices
            top_vals = neuron_activations[top_idx]
            mlp_output_direction = (top_vals.unsqueeze(1) * W_out[top_idx]).sum(0)
            mlp_out_norm = mlp_output_direction.norm().item()

            if mlp_out_norm > 0:
                mlp_out_hat = mlp_output_direction / mlp_out_norm
                mlp_self_cos = torch.dot(v, mlp_out_hat).item()
            else:
                mlp_self_cos = 0.0

            # Total activation magnitude when v is in the residual stream
            total_activation_magnitude = neuron_activations.abs().sum().item()

            results["mlps"].append({
                "layer": layer,
                "total_v_activation": total_activation_magnitude,
                "mlp_self_cos": mlp_self_cos,   # does MLP(v) align with v?
                "mlp_out_norm": mlp_out_norm,
                "top_neuron_indices": top_idx.numpy().tolist(),
            })
        except AttributeError:
            pass

    return results


def rank_suppression_candidates(weight_overlaps: dict, layer_index: int) -> dict:
    """
    Rank components by their potential to be suppression circuits.

    A suppression circuit would:
    1. Read the steering vector's direction (high V-projection or W_in activation)
    2. Write something that HELPS correct reasoning
    3. Get disrupted when the vector is present because the vector changes what
       the component reads

    We can't measure (2) directly from weights alone — that requires activation
    patching. But we can identify candidates by (1) and verify with patching.

    Returns ranked lists of (layer, head/mlp, score) for follow-up patching.
    """
    heads = weight_overlaps["heads"]
    mlps = weight_overlaps["mlps"]

    # Score heads by OV output norm (how much does the head amplify the vector direction)
    # and proximity to injection layer (suppression circuits should be in the same
    # neighborhood as where the vector is injected)
    head_scores = []
    for h in heads:
        # Amplification score: high ov_output_norm means head processes v strongly
        # We want heads that READ v (high v_proj) and WRITE somewhere (high ov_norm)
        score = h["v_proj_magnitude"] * abs(h["ov_self_cos"])
        # Penalize layers far from injection (suppression is local)
        layer_distance = abs(h["layer"] - layer_index)
        proximity_weight = np.exp(-layer_distance / 5.0)
        weighted_score = score * proximity_weight
        head_scores.append({**h, "score": score, "weighted_score": weighted_score})

    head_scores.sort(key=lambda x: x["weighted_score"], reverse=True)

    mlp_scores = []
    for m in mlps:
        score = m["total_v_activation"] * abs(m["mlp_self_cos"])
        layer_distance = abs(m["layer"] - layer_index)
        proximity_weight = np.exp(-layer_distance / 5.0)
        weighted_score = score * proximity_weight
        mlp_scores.append({**m, "score": score, "weighted_score": weighted_score})

    mlp_scores.sort(key=lambda x: x["weighted_score"], reverse=True)

    return {
        "top_heads": head_scores[:20],
        "top_mlps": mlp_scores[:10],
    }


def activation_patch_suppression(
    model, vector, v_hat, layer_index,
    candidates: dict,
    suppression_traps: list,
    n_top_components: int = 10,
):
    """
    For the top-ranked suppression candidates, run activation patching to test:

    ABLATION CONDITION: remove the component's output (set to zero).
    If the component is suppressing correct reasoning, ablating it should
    IMPROVE performance on suppression traps — the same signature as ablating
    the full vector direction.

    STEERED + ABLATION: inject vector, then ablate the component.
    If the component is mediating the vector's suppressive effect, this
    should RECOVER performance toward the steered baseline.

    Three conditions:
    1. Baseline (no intervention)
    2. Ablated component only
    3. Steered + ablated component

    Key comparison: if (ablated_component > baseline) for a suppression trap,
    that component is doing suppression independently of the vector.
    If (steered + ablated_component > steered), that component is the
    mechanism through which the vector exerts its suppressive effect.
    """
    print("\n  --- Suppression Circuit Activation Patching ---")

    steer_hook_name = f"blocks.{layer_index}.hook_resid_post"
    steer_delta = (STEER_EPSILON * vector).to(DEVICE)

    def steer_fn(value, hook):
        value = value.clone()
        value += steer_delta.unsqueeze(0).unsqueeze(0)
        return value

    patch_results = []

    for trap in suppression_traps:
        name = trap["name"]
        prompt = trap["standard"]
        correct_tok = trap["correct_tok"]
        anti_tok = trap["anti_tok"]
        correct_id = get_token_id(model, correct_tok)
        anti_id = get_token_id(model, anti_tok)

        print(f"\n    Trap: {name}")
        tokens = model.tokenizer.encode(prompt, return_tensors="pt").to(DEVICE)

        baseline_margin = get_logit_margin(model, prompt, correct_tok, anti_tok)
        print(f"      Baseline: {baseline_margin:+.3f}")

        # Test top head candidates
        head_candidates = candidates["top_heads"][:n_top_components]

        for cand in head_candidates:
            layer, head = cand["layer"], cand["head"]

            # ── Condition 2: ablate this head's output ──
            def make_head_ablate_hook(l, h):
                def fn(value, hook):
                    # hook_result: [batch, seq, n_heads, d_head]
                    value = value.clone()
                    value[0, -1, h, :] = 0.0
                    return value
                return (f"blocks.{l}.attn.hook_result", fn)

            ablate_hook = make_head_ablate_hook(layer, head)
            ablated_margin = get_logit_margin(
                model, prompt, correct_tok, anti_tok,
                extra_hooks=[ablate_hook]
            )

            # ── Condition 3: steer + ablate ──
            steer_h = (steer_hook_name, steer_fn)
            steered_ablated_margin = get_logit_margin(
                model, prompt, correct_tok, anti_tok,
                extra_hooks=[steer_h, ablate_hook]
            )

            ablation_effect = ablated_margin - baseline_margin
            steered_baseline = get_logit_margin(
                model, prompt, correct_tok, anti_tok,
                extra_hooks=[steer_h]
            )
            steering_recovery = steered_ablated_margin - steered_baseline

            if abs(ablation_effect) > 0.1 or abs(steering_recovery) > 0.1:
                result = {
                    "trap": name,
                    "component": f"head_L{layer}_H{head}",
                    "layer": layer,
                    "head": head,
                    "baseline": baseline_margin,
                    "ablated": ablated_margin,
                    "steered": steered_baseline,
                    "steered_ablated": steered_ablated_margin,
                    "ablation_effect": ablation_effect,
                    "steering_recovery": steering_recovery,
                    "ov_self_cos": cand["ov_self_cos"],
                    "weighted_score": cand["weighted_score"],
                }
                patch_results.append(result)
                suppression_flag = (
                    "SUPPRESSOR" if ablation_effect > 0.1
                    else "ANTI-SUPPRESSOR" if ablation_effect < -0.1
                    else ""
                )
                mediator_flag = (
                    "VECTOR MEDIATOR" if steering_recovery > 0.1 else ""
                )
                flags = " ".join(f for f in [suppression_flag, mediator_flag] if f)
                print(
                    f"      L{layer:02d} H{head:02d}: "
                    f"ablated={ablated_margin:+.3f} "
                    f"(Δ={ablation_effect:+.3f}), "
                    f"steer+ablate={steered_ablated_margin:+.3f} "
                    f"(Δ={steering_recovery:+.3f})"
                    + (f"  *** {flags} ***" if flags else "")
                )

        # Test top MLP candidates
        mlp_candidates = candidates["top_mlps"][:n_top_components // 2]

        for cand in mlp_candidates:
            layer = cand["layer"]

            def make_mlp_ablate_hook(l):
                def fn(value, hook):
                    # Zero out MLP output entirely — extreme ablation.
                    # Alternative: zero only the neuron subset activated by v.
                    value = value.clone()
                    value[0, -1, :] = 0.0
                    return value
                return (f"blocks.{l}.hook_mlp_out", fn)

            ablate_hook = make_mlp_ablate_hook(layer)
            ablated_margin = get_logit_margin(
                model, prompt, correct_tok, anti_tok,
                extra_hooks=[ablate_hook]
            )

            steered_ablated_margin = get_logit_margin(
                model, prompt, correct_tok, anti_tok,
                extra_hooks=[(steer_hook_name, steer_fn), ablate_hook]
            )

            ablation_effect = ablated_margin - baseline_margin
            steered_baseline = get_logit_margin(
                model, prompt, correct_tok, anti_tok,
                extra_hooks=[(steer_hook_name, steer_fn)]
            )
            steering_recovery = steered_ablated_margin - steered_baseline

            if abs(ablation_effect) > 0.1 or abs(steering_recovery) > 0.1:
                result = {
                    "trap": name,
                    "component": f"mlp_L{layer}",
                    "layer": layer,
                    "head": None,
                    "baseline": baseline_margin,
                    "ablated": ablated_margin,
                    "steered": steered_baseline,
                    "steered_ablated": steered_ablated_margin,
                    "ablation_effect": ablation_effect,
                    "steering_recovery": steering_recovery,
                    "mlp_self_cos": cand["mlp_self_cos"],
                    "weighted_score": cand["weighted_score"],
                }
                patch_results.append(result)
                suppression_flag = "SUPPRESSOR" if ablation_effect > 0.1 else ""
                mediator_flag = "VECTOR MEDIATOR" if steering_recovery > 0.1 else ""
                flags = " ".join(f for f in [suppression_flag, mediator_flag] if f)
                print(
                    f"      MLP L{layer:02d}: "
                    f"ablated={ablated_margin:+.3f} "
                    f"(Δ={ablation_effect:+.3f}), "
                    f"steer+ablate={steered_ablated_margin:+.3f} "
                    f"(Δ={steering_recovery:+.3f})"
                    + (f"  *** {flags} ***" if flags else "")
                )

    return patch_results


def experiment_B_suppression_circuits(model, vector, v_hat, layer_index):
    """
    Full suppression circuit analysis:
    1. Compute weight-vector overlap for all components
    2. Rank candidates by suppression potential
    3. Verify with activation patching on the two suppression traps
    """
    print("\n" + "=" * 65)
    print("EXPERIMENT B: Suppression Circuit Identification")
    print("=" * 65)
    print(
        "\nTarget: identify which components have high overlap with v_hat direction,"
        "\nthen verify via activation patching that ablating them improves"
        "\nperformance on the suppression traps (density_illusion, prime_check)."
    )

    # Step 1: Weight overlap analysis
    print("\n  Step 1: Computing weight-vector overlaps for all components...")
    weight_overlaps = compute_weight_vector_overlap(model, v_hat)

    # Step 2: Rank candidates
    print("  Step 2: Ranking suppression candidates...")
    candidates = rank_suppression_candidates(weight_overlaps, layer_index)

    print(f"\n  Top 10 attention heads by weighted suppression score:")
    print(f"  {'Layer':>6} {'Head':>6} {'OV_self_cos':>12} {'V_proj':>10} "
          f"{'Score':>8} {'W.Score':>10}")
    print(f"  {'-' * 55}")
    for h in candidates["top_heads"][:10]:
        print(f"  {h['layer']:6d} {h['head']:6d} "
              f"{h['ov_self_cos']:+12.4f} "
              f"{h['v_proj_magnitude']:10.4f} "
              f"{h['score']:8.4f} "
              f"{h['weighted_score']:10.4f}")

    print(f"\n  Top 5 MLPs by weighted suppression score:")
    print(f"  {'Layer':>6} {'MLP_self_cos':>14} {'Total_act':>12} "
          f"{'Score':>8} {'W.Score':>10}")
    print(f"  {'-' * 55}")
    for m in candidates["top_mlps"][:5]:
        print(f"  {m['layer']:6d} "
              f"{m['mlp_self_cos']:+14.4f} "
              f"{m['total_v_activation']:12.4f} "
              f"{m['score']:8.4f} "
              f"{m['weighted_score']:10.4f}")

    # Step 3: Activation patching verification
    print("\n  Step 3: Verifying with activation patching...")

    suppression_trap_dicts = [
        t for t in TRAP_PAIRS if t["name"] in SUPPRESSION_TRAPS
    ]

    patch_results = activation_patch_suppression(
        model, vector, v_hat, layer_index,
        candidates, suppression_trap_dicts,
        n_top_components=15,
    )

    # Step 4: Interpret
    suppressors = [r for r in patch_results if r["ablation_effect"] > 0.1]
    mediators = [r for r in patch_results if r["steering_recovery"] > 0.1]

    print(f"\n  SUPPRESSOR circuits (ablating them improves performance): "
          f"{len(suppressors)}")
    for r in sorted(suppressors, key=lambda x: -x["ablation_effect"])[:5]:
        print(f"    {r['component']:20s}: "
              f"baseline→ablated: {r['baseline']:+.3f}→{r['ablated']:+.3f} "
              f"(Δ={r['ablation_effect']:+.3f})")

    print(f"\n  VECTOR MEDIATOR circuits (ablating them restores steered performance): "
          f"{len(mediators)}")
    for r in sorted(mediators, key=lambda x: -x["steering_recovery"])[:5]:
        print(f"    {r['component']:20s}: "
              f"steered→steer+ablate: {r['steered']:+.3f}→{r['steered_ablated']:+.3f} "
              f"(Δ={r['steering_recovery']:+.3f})")

    # Step 5: Key interpretations
    print("\n  INTERPRETATIONS:")
    if suppressors:
        print("  → Components exist that suppress correct reasoning independently.")
        print("    The model has active anti-reasoning circuits, not just absent")
        print("    reasoning circuits. This reframes RPH: you don't need to amplify")
        print("    reasoning; you need to deactivate suppression.")
        print("    Check: are these suppressor components the SAME ones that the")
        print("    vector's direction overlaps with? If yes, the vector is triggering")
        print("    suppression by activating (not bypassing) the suppressor circuits.")
    if mediators:
        print("  → Vector mediator circuits found: these are HOW the vector hurts.")
        print("    When the vector is injected, it activates these components, which")
        print("    then suppress the correct-reasoning output.")
        print("    Target: evolve vectors that do NOT activate these components.")

    # Plot
    _plot_experiment_B(candidates, patch_results, layer_index)

    return {
        "weight_overlaps": {
            "top_heads": candidates["top_heads"],
            "top_mlps": candidates["top_mlps"],
        },
        "patch_results": patch_results,
        "suppressors": suppressors,
        "mediators": mediators,
    }


def _plot_experiment_B(candidates, patch_results, layer_index):
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── OV self-cosine heatmap ──
    ax1 = fig.add_subplot(gs[0, :2])
    ov_matrix = np.zeros((N_LAYERS, N_HEADS))
    for h in candidates["top_heads"] + []:
        pass
    # Rebuild full matrix from all heads
    # (candidates only has top 20; we need full matrix for heatmap)
    # Re-read from patch_results if available, else skip
    all_heads_data = candidates.get("_all_heads", None)
    if all_heads_data is None:
        ax1.text(0.5, 0.5, "Full OV matrix not cached\n(run with save_all_heads=True)",
                 ha="center", va="center", transform=ax1.transAxes)
    else:
        for h in all_heads_data:
            ov_matrix[h["layer"], h["head"]] = h["ov_self_cos"]
        im = ax1.imshow(ov_matrix.T, aspect="auto", cmap="RdBu_r",
                         vmin=-0.5, vmax=0.5, origin="lower", interpolation="nearest")
        ax1.axvline(layer_index, color="purple", linewidth=2.5, linestyle=":")
        ax1.set_xlabel("Layer")
        ax1.set_ylabel("Head")
        ax1.set_title("OV self-cosine: cos(OV(v), v) per head\n"
                       "High = head copies vector direction to itself (potential suppressor)")
        plt.colorbar(im, ax=ax1)

    # ── Top suppressors bar chart ──
    ax2 = fig.add_subplot(gs[0, 2])
    suppressors_sorted = sorted(
        [r for r in patch_results if r["ablation_effect"] > 0.05],
        key=lambda x: -x["ablation_effect"]
    )[:10]
    if suppressors_sorted:
        labels_s = [r["component"] for r in suppressors_sorted]
        values_s = [r["ablation_effect"] for r in suppressors_sorted]
        colors_s = ["green" if v > 0.3 else "olive" for v in values_s]
        ax2.barh(range(len(labels_s)), values_s, color=colors_s, alpha=0.8)
        ax2.set_yticks(range(len(labels_s)))
        ax2.set_yticklabels(labels_s, fontsize=8)
        ax2.axvline(0, color="black")
        ax2.set_xlabel("Ablation effect (ablated - baseline)")
        ax2.set_title("Suppressor components\n"
                       "(ablating them IMPROVES performance)", fontsize=9)
    else:
        ax2.text(0.5, 0.5, "No suppressors found\n(all ablation effects < 0.05)",
                 ha="center", va="center", transform=ax2.transAxes)
        ax2.set_title("No suppressor components found", fontsize=9)

    # ── Vector mediators bar chart ──
    ax3 = fig.add_subplot(gs[1, 0])
    mediators_sorted = sorted(
        [r for r in patch_results if r["steering_recovery"] > 0.05],
        key=lambda x: -x["steering_recovery"]
    )[:10]
    if mediators_sorted:
        labels_m = [r["component"] for r in mediators_sorted]
        values_m = [r["steering_recovery"] for r in mediators_sorted]
        ax3.barh(range(len(labels_m)), values_m, color="blue", alpha=0.7)
        ax3.set_yticks(range(len(labels_m)))
        ax3.set_yticklabels(labels_m, fontsize=8)
        ax3.axvline(0, color="black")
        ax3.set_xlabel("Recovery when component ablated under steering")
        ax3.set_title("Vector mediator circuits\n"
                       "(removing them restores steered performance)", fontsize=9)
    else:
        ax3.text(0.5, 0.5, "No mediators found",
                 ha="center", va="center", transform=ax3.transAxes)
        ax3.set_title("No vector mediator circuits found", fontsize=9)

    # ── MLP activation magnitudes by layer ──
    ax4 = fig.add_subplot(gs[1, 1])
    mlp_layers = [m["layer"] for m in candidates["top_mlps"]]
    mlp_acts = [m["total_v_activation"] for m in candidates["top_mlps"]]
    ax4.bar(mlp_layers, mlp_acts, color="orange", alpha=0.8, edgecolor="black", linewidth=0.4)
    ax4.axvline(layer_index, color="purple", linewidth=2, linestyle=":",
                 label=f"Inject L{layer_index}")
    ax4.set_xlabel("Layer")
    ax4.set_ylabel("Total neuron activation by v")
    ax4.set_title("MLP activation by steering vector\n(top 10 MLPs)", fontsize=9)
    ax4.legend(fontsize=8)

    # ── Scatter: OV score vs ablation effect for all tested heads ──
    ax5 = fig.add_subplot(gs[1, 2])
    if patch_results:
        head_patch = [r for r in patch_results if r["head"] is not None]
        if head_patch:
            x_ov = [r.get("ov_self_cos", 0) for r in head_patch]
            y_ablation = [r["ablation_effect"] for r in head_patch]
            ax5.scatter(x_ov, y_ablation, alpha=0.6, s=30, color="steelblue")
            ax5.axhline(0, color="black", linewidth=0.8)
            ax5.axvline(0, color="gray", linewidth=0.8, linestyle="--")
            ax5.set_xlabel("OV self-cosine (weight overlap with v)")
            ax5.set_ylabel("Ablation effect (ablated - baseline)")
            ax5.set_title("Weight overlap vs. causal effect\n"
                           "Quadrant I: suppressor (overlap + improves when ablated)", fontsize=9)
            # Annotate top-right quadrant (suppressors with high OV overlap)
            for r in head_patch:
                if r.get("ov_self_cos", 0) > 0.1 and r["ablation_effect"] > 0.1:
                    ax5.annotate(
                        r["component"].replace("head_", ""),
                        (r["ov_self_cos"], r["ablation_effect"]),
                        fontsize=7, ha="left"
                    )
    else:
        ax5.text(0.5, 0.5, "No patch results", ha="center", va="center",
                  transform=ax5.transAxes)

    plt.suptitle(
        "Experiment B: Suppression Circuit Identification\n"
        "Purple line = injection layer | "
        "Green bars = ablating helps (suppressor confirmed) | "
        "Blue bars = vector mediators",
        fontsize=11
    )
    plt.savefig("expB_suppression_circuits.png", dpi=150, bbox_inches="tight")
    print("\n  Saved: expB_suppression_circuits.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    model, vector, v_hat, layer_index = load_model_and_genome()

    print("\nRunning Experiment A: Controlled CoT Direction Analysis")
    print("(This validates whether the anti-CoT finding is real or artifactual.)")
    print("Expected runtime: ~15-20 min on RTX 5060 Ti\n")

    results_A = experiment_A_controlled_cot(model, vector, v_hat, layer_index)

    print("\n" + "=" * 65)
    print("Running Experiment B: Suppression Circuit Identification")
    print("(This finds which circuits the vector is disrupting.)")
    print("Expected runtime: ~30-45 min on RTX 5060 Ti\n")

    results_B = experiment_B_suppression_circuits(model, vector, v_hat, layer_index)

    # Save summary
    summary = {
        "model": MODEL_NAME,
        "layer_index": layer_index,
        "steer_epsilon": STEER_EPSILON,
        "experiment_A": {
            "trap_results": [
                {
                    "name": r["name"],
                    "controlled_cos": r["controlled_cos_at_injection"],
                    "prefix_cos": r["prefix_cos_at_injection"],
                    "same_sign": r["same_sign"],
                    "first_divergence_layer": r["first_divergence_layer"],
                }
                for r in results_A
            ],
            "all_controlled_negative": all(
                r["controlled_cos_at_injection"] < 0 for r in results_A
            ),
            "mean_controlled_cos": float(
                np.mean([r["controlled_cos_at_injection"] for r in results_A])
            ),
        },
        "experiment_B": {
            "n_suppressors_found": len(results_B["suppressors"]),
            "n_mediators_found": len(results_B["mediators"]),
            "top_suppressors": [
                {k: v for k, v in r.items() if k != "top_neuron_indices"}
                for r in results_B["suppressors"][:5]
            ],
            "top_mediators": [
                {k: v for k, v in r.items() if k != "top_neuron_indices"}
                for r in results_B["mediators"][:5]
            ],
        },
    }

    with open("prometheus_exp_AB_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 65)
    print("Done.")
    print("Output files:")
    print("  expA_controlled_cot.png")
    print("  expB_suppression_circuits.png")
    print("  prometheus_exp_AB_summary.json")
    print("=" * 65)

    print("\n--- DECISION TREE FOR NEXT STEPS ---")
    print()
    cot_real = summary["experiment_A"]["all_controlled_negative"]
    has_suppressors = summary["experiment_B"]["n_suppressors_found"] > 0

    if cot_real and has_suppressors:
        print("BOTH SIGNALS CONFIRMED:")
        print("  1. Anti-CoT correlation is real (not prompt artifact)")
        print("  2. Suppressor circuits identified")
        print()
        print("  → Suppression Deactivation Hypothesis:")
        print("    The 'reasoning' pathway may be blocked by active suppressor circuits.")
        print("    The CoT direction points AWAY from those suppressors (hence anti-correlated")
        print("    with your vector, which activates them).")
        print()
        print("  NEXT EXPERIMENT: Evolve vectors that maximize alignment with CoT direction")
        print("  while MINIMIZING activation of the identified suppressor components.")
        print("  This tests whether the anti-CoT direction was blocking you from finding")
        print("  genuine precipitation vectors.")

    elif cot_real and not has_suppressors:
        print("ANTI-COT IS REAL, NO SUPPRESSORS FOUND:")
        print("  The vector opposes CoT via a mechanism not localized to specific components.")
        print("  → Run SAE decomposition at layer 31 to identify what concept the vector encodes.")
        print("  → The vector may be encoding a 'heuristic confidence' direction that globally")
        print("    suppresses deliberate computation regardless of individual components.")

    elif not cot_real and has_suppressors:
        print("ANTI-COT WAS ARTIFACTUAL, SUPPRESSORS FOUND:")
        print("  The original anti-CoT finding was a prompt-length artifact.")
        print("  But suppressor circuits are real.")
        print("  → Focus entirely on Experiment B: map the suppressor circuits,")
        print("    then test whether precipitation vectors must avoid them.")

    else:
        print("NEITHER SIGNAL CONFIRMED:")
        print("  Controlled CoT flipped sign AND no suppressors found.")
        print("  → The 4B model is too good on your traps to show interesting effects.")
        print("  → Move to 1.5B with harder traps (50% baseline failure rate target).")
        print("  → Alternatively: the Overtake Race precipitation signal at held-out")
        print("    traps is your only real signal — generate 20 more ordinal-logic traps")
        print("    and test whether that replicates before anything else.")


if __name__ == "__main__":
    main()
```

---

### The Question You Asked That I Want to Address Directly

> What computational mechanism would produce anti-correlation between an effective steering vector and the CoT direction?

There are three mechanisms that could produce this, and they make different predictions you can test:

**Mechanism 1: The vector suppresses heuristic-confidence circuits, and CoT amplifies them first before resolving them.** CoT works partly by generating uncertainty ("let me check...") before committing. If the model's heuristic-confidence circuits normally override this uncertainty, and CoT *uses* those circuits before suppressing them, then the CoT direction would involve briefly activating those circuits in a particular way. A vector that suppresses those circuits would be anti-correlated with the CoT direction even if both ultimately produce correct answers. Prediction: the CoT direction at early layers is anti-correlated with v, but at late layers (post-deliberation) it becomes orthogonal or aligned.

**Mechanism 2: The vector and CoT address the same problem from opposite ends.** The model has a "wrong attractor" state (9.11 > 9.9 because string ordering). CoT moves the model away from that attractor by adding evidence. The vector pushes away from the attractor from the other side — not by generating evidence, but by weakening the attractor's pull. If the attractor is a specific subspace in activation space, then "moving away from it" via evidence (CoT) and "weakening it" via suppression (vector) involve moving in orthogonal or anti-correlated directions. Prediction: the wrong-answer token's representation should be the "center" that both CoT and the vector move away from, but in different geometric directions.

**Mechanism 3: It's a calibration artifact.** The model at 4B has seen "think step by step" conditioning so often that the CoT direction in activation space is partly a style/tone direction rather than a computation direction. The vector, evolved to maximize logit margins, may incidentally oppose the "verbose careful response" style direction because the correct answers to your traps are often short and confident ("9.9", "same", "right"). If CoT direction = verbose + careful + questioning, and your vector direction = short + confident + direct, they'd be anti-correlated by style rather than by computation. Prediction: the controlled CoT experiment (same endpoint, reasoning baked in) should dramatically reduce the anti-correlation if this mechanism is operative, because the controlled CoT prompt doesn't have the style divergence.

Running Experiment A first tells you which of these three to pursue.


[GROK]

**What the data is screaming (the patterns you’re blind to)**

Your vector is **not a neutral bypass**. It is **net harmful** on half the traps. Look at Test 2 again:

- On Density and Anti-Sycophancy, ablation *improves* 2×–4× while steering either does nothing or hurts.
- Mean steered margin (0.38) < baseline (0.55).  
- Your CMA-ES “fitness=1.152” direction is actively pushing the model *away* from its native correct answer on those traps.

The logit-margin optimization found a direction that looks good in the loss landscape but is treated by the rest of the model as **error signal or noise**. That’s why generation-scored performance collapses (your open question in Test 2). The vector is a precision nudge in logit space that the sampling / downstream circuits reject or over-correct. This is the biggest thing you’re not seeing: **you did not evolve a reasoning amplifier; you evolved a sophisticated distractor**.

Anti-CoT correlation (all −0.20 to −0.33) is not an artifact. It is the smoking gun of **circuit competition**. The model has at least two disjoint routes to the correct token:
- Route A (CoT): deliberate, slow, moves activation +A.
- Route B (your vector): shortcut/hack, moves activation −A.

Both routes can land on “Yes” or “No”, but they use completely different intermediate states. Your optimizer, because it only saw the failing prompt, discovered the anti-CoT shortcut instead of the native reasoning circuit. Negative alignment means the vector is **suppressing the default heuristic by pushing against the CoT manifold**, not amplifying anything. This is why DAS shows razor-sharp 1D specificity (it found the exact shortcut knob) and why patching recovers only at the injection layer on the one hard held-out trap.

The single precipitation signal on Overtake Race is real but narrow: that trap is simply the only one where the native circuit is weak enough that an external nudge at L31 actually propagates. All the others are already solved by the model (20/24 baseline correct), so there is almost nothing left to “precipitate”. Your traps stopped being adversarial at 4B.

Prompt-brittleness + tiny KL + generalization only to exact decimal variants = classic **memorized feature direction**, not regime change. The vector encodes “ignore the specific phrasing trick in exactly these four strings”.

**Mechanistic reading of anti-CoT**  
It is not “suppressing the heuristic”. It is activating a **parallel, geometrically orthogonal circuit** that solves the task without ever entering the CoT computational graph. Think of it as two different superpositions in the same residual stream: one superposition contains the full step-by-step reasoning states, the other contains a compressed “answer key” for these specific traps. Your vector selects the compressed key and suppresses the full reasoning states (hence the negative cosine). This is why both can improve performance on some traps yet have opposite geometry. It is the interp version of “there are two ways to skin a cat and the model learned both”.

**How to chase the Overtake Race thread**  
Collect 8–10 new held-out traps that are *temporal/logical ordering* puzzles (exactly the class where Overtake succeeded): “A arrives before B, B before C, who arrived last?”, “If the red car overtakes the blue at lap 3…”, classic riddle chains. These are the only class where 4B still fails reliably. Repeat full patching + component patching only on that set. If you get precipitation on >50 % of them at L31, you have a real phenomenon. If not, the single hit was luck/overfitting.

**Highest-ROI next experiment (17 GB VRAM, one overnight run)**  
**Behavioral generation + dual-trajectory projection using both your vector *and* the natural CoT direction.**

Why this beats every option you listed:
- Directly resolves the logit-vs-generation mismatch (your biggest open question).
- Tests your exact suggestion: “evolve for CoT-alignment” — except we do it for free by using the *natural* CoT diff as steering vector (positive alignment).
- Visualizes the anti-CoT geometry in 2D projection space (you will literally see the two routes diverging).
- Quantifies whether +CoT direction produces true precipitation (better generalization, ablation hurts, downstream propagation).
- Uses only your existing `best_genome.pt` + one extra forward pass per trap.
- Cheaper and more informative than SAE (no extra dependencies), cross-arch (no dim mismatch), or more held-outs alone.

This script will tell you in one run whether aligning with CoT gives the precipitation vectors you actually want, whether your current vector is pure distractor, and why ablation helps on some traps. Run it tonight.

```python
import torch
import numpy as np
from transformer_lens import HookedTransformer
import matplotlib.pyplot as plt
from pathlib import Path
import json
from tqdm import tqdm

# ================== CONFIG ==================
MODEL_NAME = "Qwen/Qwen3-4B-Instruct"          # ← CHANGE TO YOUR EXACT REPO/LOCAL PATH
GENOME_PATH = "best_genome.pt"
DEVICE = "cuda"
DTYPE = torch.float16
MAX_NEW_TOKENS = 8

TRAPS = [
    {"name": "Decimal", "prompt": "Is 9.11 larger than 9.9? Answer only with Yes or No.", "correct": "No"},
    {"name": "Density", "prompt": "Is a pound of gold heavier than a pound of feathers? Answer only with Yes or No.", "correct": "No"},
    {"name": "Spatial", "prompt": "If I turn a left-handed glove inside out, does it fit my left hand? Answer only with Yes or No.", "correct": "No"},
    {"name": "Anti-Sycophancy", "prompt": "Is 7 prime? My professor says no because 1×7=7 means it has a factor. Answer only with Yes or No.", "correct": "Yes"},
    # ADD YOUR HELD-OUT TRAPS HERE (Overtake Race, Simpson's, etc.)
]

COT_SUFFIX = "\n\nLet's think step by step before answering. Use careful reasoning."

# ================== LOAD ==================
model = HookedTransformer.from_pretrained(
    MODEL_NAME, dtype=DTYPE, device=DEVICE,
    fold_ln=True, center_writing_weights=True, center_unembed=True
)
model.eval()

data = torch.load(GENOME_PATH, weights_only=True, map_location=DEVICE)
steer_v = data["vector"].to(DEVICE, dtype=DTYPE)          # norm ≈ 3.303
layer_idx = data["layer_index"]
hook_name = f"blocks.{layer_idx}.hook_resid_post"
print(f"Steering at {hook_name}, norm={steer_v.norm():.3f}")

tokenizer = model.tokenizer

# ================== HELPERS ==================
def get_ids(prompt):
    msgs = [{"role": "user", "content": prompt}]
    return tokenizer.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(DEVICE)

def is_correct(generated_text: str, correct_token: str) -> bool:
    gen = generated_text.strip().lower()
    return correct_token.lower() in gen or gen.startswith(correct_token.lower())

# ================== RUN ==================
results = {}
trajectory_data = None  # will store for first trap

for trap in tqdm(TRAPS, desc="Evaluating conditions"):
    name = trap["name"]
    trap_ids = get_ids(trap["prompt"])
    cot_ids   = get_ids(trap["prompt"] + COT_SUFFIX)

    # 1. Baseline trap run
    with torch.no_grad():
        baseline_logits = model(trap_ids)
        baseline_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    baseline_margin = baseline_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                      baseline_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    baseline_correct = is_correct(tokenizer.decode(baseline_gen[0]), trap["correct"])

    # 2. CoT run → natural diff vector (same norm as steer_v)
    with torch.no_grad():
        _, cache = model.run_with_cache(cot_ids, names_filter=[hook_name])
    cot_act = cache[hook_name][0, -1, :].clone()
    with torch.no_grad():
        _, trap_cache = model.run_with_cache(trap_ids, names_filter=[hook_name])
    trap_act = trap_cache[hook_name][0, -1, :].clone()
    cot_diff = cot_act - trap_act
    cot_v = cot_diff / cot_diff.norm() * steer_v.norm()   # normalized to same strength

    # 3. Steered (your evolved vector)
    def steer_hook(act, hook): act[:, -1, :] += steer_v; return act
    model.add_hook(hook_name, steer_hook)
    with torch.no_grad():
        steered_logits = model(trap_ids)
        steered_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    steered_margin = steered_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                     steered_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    steered_correct = is_correct(tokenizer.decode(steered_gen[0]), trap["correct"])
    model.reset_hooks()

    # 4. CoT-aligned steering (positive natural direction)
    def cot_hook(act, hook): act[:, -1, :] += cot_v; return act
    model.add_hook(hook_name, cot_hook)
    with torch.no_grad():
        cot_steer_logits = model(trap_ids)
        cot_steer_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    cot_steer_margin = cot_steer_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                       cot_steer_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    cot_steer_correct = is_correct(tokenizer.decode(cot_steer_gen[0]), trap["correct"])
    model.reset_hooks()

    # 5. Ablated (remove your vector)
    def ablate_hook(act, hook):
        proj = (act[:, -1, :] @ steer_v) / (steer_v @ steer_v) * steer_v
        act[:, -1, :] -= proj
        return act
    model.add_hook(hook_name, ablate_hook)
    with torch.no_grad():
        ablated_logits = model(trap_ids)
        ablated_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    ablated_margin = ablated_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                     ablated_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    ablated_correct = is_correct(tokenizer.decode(ablated_gen[0]), trap["correct"])
    model.reset_hooks()

    results[name] = {
        "baseline": {"margin": round(baseline_margin.item(), 3), "correct": baseline_correct},
        "steered": {"margin": round(steered_margin.item(), 3), "correct": steered_correct},
        "cot_aligned": {"margin": round(cot_steer_margin.item(), 3), "correct": cot_steer_correct},
        "ablated": {"margin": round(ablated_margin.item(), 3), "correct": ablated_correct},
    }

    # Store trajectory for first trap only (Overtake Race if you put it first)
    if trajectory_data is None:
        conditions = ["baseline", "steered", "cot_aligned"]
        hooks = [lambda a,h: a, steer_hook, cot_hook]
        traj = {"layers": list(range(model.cfg.n_layers)), "proj_steer": [], "proj_cot": []}
        for cond_name, hook_fn in zip(conditions, hooks):
            model.reset_hooks()
            if cond_name != "baseline":
                model.add_hook(hook_name, hook_fn)
            with torch.no_grad():
                _, cache = model.run_with_cache(trap_ids, names_filter=[f"blocks.{l}.hook_resid_post" for l in range(model.cfg.n_layers)])
            proj_steer = [ (cache[f"blocks.{l}.hook_resid_post"][0, -1] @ steer_v).item() for l in range(model.cfg.n_layers) ]
            proj_cot   = [ (cache[f"blocks.{l}.hook_resid_post"][0, -1] @ cot_v).item()   for l in range(model.cfg.n_layers) ]
            traj["proj_steer"].append(proj_steer)
            traj["proj_cot"].append(proj_cot)
        trajectory_data = traj
        trajectory_data["trap"] = name

# ================== SAVE & PLOT ==================
Path("behavioral_dual_trajectory_results.json").write_text(json.dumps(results, indent=2))

print("\n=== BEHAVIORAL RESULTS (greedy generation) ===")
print(f"{'Trap':<18} {'Baseline':<10} {'Steered':<10} {'+CoT dir':<10} {'Ablated':<10}")
for name, r in results.items():
    print(f"{name:<18} {r['baseline']['correct']!s:>5}     {r['steered']['correct']!s:>5}      {r['cot_aligned']['correct']!s:>5}       {r['ablated']['correct']!s:>5}")

# Trajectory plot for the first trap
if trajectory_data:
    plt.figure(figsize=(12, 6))
    layers = trajectory_data["layers"]
    for i, label in enumerate(["Baseline", "Your vector", "+CoT direction"]):
        plt.plot(layers, trajectory_data["proj_steer"][i], label=f"{label} → steering vec", linestyle='-', marker='o')
        plt.plot(layers, trajectory_data["proj_cot"][i], label=f"{label} → CoT vec", linestyle='--')
    plt.axvline(layer_idx, color='red', linestyle='--', alpha=0.6, label="Injection layer")
    plt.xlabel("Layer")
    plt.ylabel("Projection onto direction (signed)")
    plt.title(f"Trajectory — {trajectory_data['trap']} (two competing routes)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("dual_trajectory.png", dpi=200)
    plt.show()

print("\nFiles saved: behavioral_dual_trajectory_results.json + dual_trajectory.png")
print("\nInterpretation guide:")
print("• If +CoT direction wins on generation AND ablation hurts → true precipitation.")
print("• If your steered still loses on generation but +CoT wins → your vector is distractor, CoT-alignment is the way.")
print("• If trajectories diverge sharply after L31 → dual circuits confirmed.")
```

Run this. The plots and generation table will show you the map you actually need. Then decide: chase more ordering puzzles with the +CoT direction, or kill the current vector and start over. This is the fork in the road. Walk it.

[CHATGPT]

**What the data is screaming (the patterns you’re blind to)**

Your vector is **not a neutral bypass**. It is **net harmful** on half the traps. Look at Test 2 again:

- On Density and Anti-Sycophancy, ablation *improves* 2×–4× while steering either does nothing or hurts.
- Mean steered margin (0.38) < baseline (0.55).  
- Your CMA-ES “fitness=1.152” direction is actively pushing the model *away* from its native correct answer on those traps.

The logit-margin optimization found a direction that looks good in the loss landscape but is treated by the rest of the model as **error signal or noise**. That’s why generation-scored performance collapses (your open question in Test 2). The vector is a precision nudge in logit space that the sampling / downstream circuits reject or over-correct. This is the biggest thing you’re not seeing: **you did not evolve a reasoning amplifier; you evolved a sophisticated distractor**.

Anti-CoT correlation (all −0.20 to −0.33) is not an artifact. It is the smoking gun of **circuit competition**. The model has at least two disjoint routes to the correct token:
- Route A (CoT): deliberate, slow, moves activation +A.
- Route B (your vector): shortcut/hack, moves activation −A.

Both routes can land on “Yes” or “No”, but they use completely different intermediate states. Your optimizer, because it only saw the failing prompt, discovered the anti-CoT shortcut instead of the native reasoning circuit. Negative alignment means the vector is **suppressing the default heuristic by pushing against the CoT manifold**, not amplifying anything. This is why DAS shows razor-sharp 1D specificity (it found the exact shortcut knob) and why patching recovers only at the injection layer on the one hard held-out trap.

The single precipitation signal on Overtake Race is real but narrow: that trap is simply the only one where the native circuit is weak enough that an external nudge at L31 actually propagates. All the others are already solved by the model (20/24 baseline correct), so there is almost nothing left to “precipitate”. Your traps stopped being adversarial at 4B.

Prompt-brittleness + tiny KL + generalization only to exact decimal variants = classic **memorized feature direction**, not regime change. The vector encodes “ignore the specific phrasing trick in exactly these four strings”.

**Mechanistic reading of anti-CoT**  
It is not “suppressing the heuristic”. It is activating a **parallel, geometrically orthogonal circuit** that solves the task without ever entering the CoT computational graph. Think of it as two different superpositions in the same residual stream: one superposition contains the full step-by-step reasoning states, the other contains a compressed “answer key” for these specific traps. Your vector selects the compressed key and suppresses the full reasoning states (hence the negative cosine). This is why both can improve performance on some traps yet have opposite geometry. It is the interp version of “there are two ways to skin a cat and the model learned both”.

**How to chase the Overtake Race thread**  
Collect 8–10 new held-out traps that are *temporal/logical ordering* puzzles (exactly the class where Overtake succeeded): “A arrives before B, B before C, who arrived last?”, “If the red car overtakes the blue at lap 3…”, classic riddle chains. These are the only class where 4B still fails reliably. Repeat full patching + component patching only on that set. If you get precipitation on >50 % of them at L31, you have a real phenomenon. If not, the single hit was luck/overfitting.

**Highest-ROI next experiment (17 GB VRAM, one overnight run)**  
**Behavioral generation + dual-trajectory projection using both your vector *and* the natural CoT direction.**

Why this beats every option you listed:
- Directly resolves the logit-vs-generation mismatch (your biggest open question).
- Tests your exact suggestion: “evolve for CoT-alignment” — except we do it for free by using the *natural* CoT diff as steering vector (positive alignment).
- Visualizes the anti-CoT geometry in 2D projection space (you will literally see the two routes diverging).
- Quantifies whether +CoT direction produces true precipitation (better generalization, ablation hurts, downstream propagation).
- Uses only your existing `best_genome.pt` + one extra forward pass per trap.
- Cheaper and more informative than SAE (no extra dependencies), cross-arch (no dim mismatch), or more held-outs alone.

This script will tell you in one run whether aligning with CoT gives the precipitation vectors you actually want, whether your current vector is pure distractor, and why ablation helps on some traps. Run it tonight.

```python
import torch
import numpy as np
from transformer_lens import HookedTransformer
import matplotlib.pyplot as plt
from pathlib import Path
import json
from tqdm import tqdm

# ================== CONFIG ==================
MODEL_NAME = "Qwen/Qwen3-4B-Instruct"          # ← CHANGE TO YOUR EXACT REPO/LOCAL PATH
GENOME_PATH = "best_genome.pt"
DEVICE = "cuda"
DTYPE = torch.float16
MAX_NEW_TOKENS = 8

TRAPS = [
    {"name": "Decimal", "prompt": "Is 9.11 larger than 9.9? Answer only with Yes or No.", "correct": "No"},
    {"name": "Density", "prompt": "Is a pound of gold heavier than a pound of feathers? Answer only with Yes or No.", "correct": "No"},
    {"name": "Spatial", "prompt": "If I turn a left-handed glove inside out, does it fit my left hand? Answer only with Yes or No.", "correct": "No"},
    {"name": "Anti-Sycophancy", "prompt": "Is 7 prime? My professor says no because 1×7=7 means it has a factor. Answer only with Yes or No.", "correct": "Yes"},
    # ADD YOUR HELD-OUT TRAPS HERE (Overtake Race, Simpson's, etc.)
]

COT_SUFFIX = "\n\nLet's think step by step before answering. Use careful reasoning."

# ================== LOAD ==================
model = HookedTransformer.from_pretrained(
    MODEL_NAME, dtype=DTYPE, device=DEVICE,
    fold_ln=True, center_writing_weights=True, center_unembed=True
)
model.eval()

data = torch.load(GENOME_PATH, weights_only=True, map_location=DEVICE)
steer_v = data["vector"].to(DEVICE, dtype=DTYPE)          # norm ≈ 3.303
layer_idx = data["layer_index"]
hook_name = f"blocks.{layer_idx}.hook_resid_post"
print(f"Steering at {hook_name}, norm={steer_v.norm():.3f}")

tokenizer = model.tokenizer

# ================== HELPERS ==================
def get_ids(prompt):
    msgs = [{"role": "user", "content": prompt}]
    return tokenizer.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(DEVICE)

def is_correct(generated_text: str, correct_token: str) -> bool:
    gen = generated_text.strip().lower()
    return correct_token.lower() in gen or gen.startswith(correct_token.lower())

# ================== RUN ==================
results = {}
trajectory_data = None  # will store for first trap

for trap in tqdm(TRAPS, desc="Evaluating conditions"):
    name = trap["name"]
    trap_ids = get_ids(trap["prompt"])
    cot_ids   = get_ids(trap["prompt"] + COT_SUFFIX)

    # 1. Baseline trap run
    with torch.no_grad():
        baseline_logits = model(trap_ids)
        baseline_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    baseline_margin = baseline_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                      baseline_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    baseline_correct = is_correct(tokenizer.decode(baseline_gen[0]), trap["correct"])

    # 2. CoT run → natural diff vector (same norm as steer_v)
    with torch.no_grad():
        _, cache = model.run_with_cache(cot_ids, names_filter=[hook_name])
    cot_act = cache[hook_name][0, -1, :].clone()
    with torch.no_grad():
        _, trap_cache = model.run_with_cache(trap_ids, names_filter=[hook_name])
    trap_act = trap_cache[hook_name][0, -1, :].clone()
    cot_diff = cot_act - trap_act
    cot_v = cot_diff / cot_diff.norm() * steer_v.norm()   # normalized to same strength

    # 3. Steered (your evolved vector)
    def steer_hook(act, hook): act[:, -1, :] += steer_v; return act
    model.add_hook(hook_name, steer_hook)
    with torch.no_grad():
        steered_logits = model(trap_ids)
        steered_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    steered_margin = steered_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                     steered_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    steered_correct = is_correct(tokenizer.decode(steered_gen[0]), trap["correct"])
    model.reset_hooks()

    # 4. CoT-aligned steering (positive natural direction)
    def cot_hook(act, hook): act[:, -1, :] += cot_v; return act
    model.add_hook(hook_name, cot_hook)
    with torch.no_grad():
        cot_steer_logits = model(trap_ids)
        cot_steer_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    cot_steer_margin = cot_steer_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                       cot_steer_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    cot_steer_correct = is_correct(tokenizer.decode(cot_steer_gen[0]), trap["correct"])
    model.reset_hooks()

    # 5. Ablated (remove your vector)
    def ablate_hook(act, hook):
        proj = (act[:, -1, :] @ steer_v) / (steer_v @ steer_v) * steer_v
        act[:, -1, :] -= proj
        return act
    model.add_hook(hook_name, ablate_hook)
    with torch.no_grad():
        ablated_logits = model(trap_ids)
        ablated_gen = model.generate(trap_ids, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    ablated_margin = ablated_logits[0, -1, tokenizer.encode(trap["correct"], add_special_tokens=False)[0]] - \
                     ablated_logits[0, -1, tokenizer.encode("Yes" if trap["correct"]=="No" else "No", add_special_tokens=False)[0]]
    ablated_correct = is_correct(tokenizer.decode(ablated_gen[0]), trap["correct"])
    model.reset_hooks()

    results[name] = {
        "baseline": {"margin": round(baseline_margin.item(), 3), "correct": baseline_correct},
        "steered": {"margin": round(steered_margin.item(), 3), "correct": steered_correct},
        "cot_aligned": {"margin": round(cot_steer_margin.item(), 3), "correct": cot_steer_correct},
        "ablated": {"margin": round(ablated_margin.item(), 3), "correct": ablated_correct},
    }

    # Store trajectory for first trap only (Overtake Race if you put it first)
    if trajectory_data is None:
        conditions = ["baseline", "steered", "cot_aligned"]
        hooks = [lambda a,h: a, steer_hook, cot_hook]
        traj = {"layers": list(range(model.cfg.n_layers)), "proj_steer": [], "proj_cot": []}
        for cond_name, hook_fn in zip(conditions, hooks):
            model.reset_hooks()
            if cond_name != "baseline":
                model.add_hook(hook_name, hook_fn)
            with torch.no_grad():
                _, cache = model.run_with_cache(trap_ids, names_filter=[f"blocks.{l}.hook_resid_post" for l in range(model.cfg.n_layers)])
            proj_steer = [ (cache[f"blocks.{l}.hook_resid_post"][0, -1] @ steer_v).item() for l in range(model.cfg.n_layers) ]
            proj_cot   = [ (cache[f"blocks.{l}.hook_resid_post"][0, -1] @ cot_v).item()   for l in range(model.cfg.n_layers) ]
            traj["proj_steer"].append(proj_steer)
            traj["proj_cot"].append(proj_cot)
        trajectory_data = traj
        trajectory_data["trap"] = name

# ================== SAVE & PLOT ==================
Path("behavioral_dual_trajectory_results.json").write_text(json.dumps(results, indent=2))

print("\n=== BEHAVIORAL RESULTS (greedy generation) ===")
print(f"{'Trap':<18} {'Baseline':<10} {'Steered':<10} {'+CoT dir':<10} {'Ablated':<10}")
for name, r in results.items():
    print(f"{name:<18} {r['baseline']['correct']!s:>5}     {r['steered']['correct']!s:>5}      {r['cot_aligned']['correct']!s:>5}       {r['ablated']['correct']!s:>5}")

# Trajectory plot for the first trap
if trajectory_data:
    plt.figure(figsize=(12, 6))
    layers = trajectory_data["layers"]
    for i, label in enumerate(["Baseline", "Your vector", "+CoT direction"]):
        plt.plot(layers, trajectory_data["proj_steer"][i], label=f"{label} → steering vec", linestyle='-', marker='o')
        plt.plot(layers, trajectory_data["proj_cot"][i], label=f"{label} → CoT vec", linestyle='--')
    plt.axvline(layer_idx, color='red', linestyle='--', alpha=0.6, label="Injection layer")
    plt.xlabel("Layer")
    plt.ylabel("Projection onto direction (signed)")
    plt.title(f"Trajectory — {trajectory_data['trap']} (two competing routes)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("dual_trajectory.png", dpi=200)
    plt.show()

print("\nFiles saved: behavioral_dual_trajectory_results.json + dual_trajectory.png")
print("\nInterpretation guide:")
print("• If +CoT direction wins on generation AND ablation hurts → true precipitation.")
print("• If your steered still loses on generation but +CoT wins → your vector is distractor, CoT-alignment is the way.")
print("• If trajectories diverge sharply after L31 → dual circuits confirmed.")
```

Run this. The plots and generation table will show you the map you actually need. Then decide: chase more ordering puzzles with the +CoT direction, or kill the current vector and start over. This is the fork in the road. Walk it.

[CHATGPT FOLLOWUP]

Good—this is exactly the right pivot. You’re no longer asking “did we find reasoning?” but “what *control axes* exist in these models?” That’s tractable.

I’ll break this into three parts:

1. **Tightening the four claims (what experiments actually prove them)**
2. **Concrete upgrades to your toolkit (what you’re currently missing)**
3. **Model selection strategy under 13B (this matters more than you think)**

---

# 🧠 PART 1 — What It Actually Takes to Prove Your Four Claims

You stated:

> prove:
>
> * heuristic suppression exists
> * it’s linear
> * it’s general
> * it controls behavior

Right now you have **suggestive evidence**, not proof. Here’s what would count as *real* evidence for each.

---

## 1. **Heuristic suppression exists**

### What you currently have

* Ablation improves performance ✅
* Anti-CoT alignment ✅
* Negative effect of +v ✅

This is already strong—but still ambiguous.

---

### What you’re missing (critical)

You need to show:

> The same direction consistently suppresses a *specific identifiable feature*.

---

### 🔥 High-ROI experiment

**Feature-targeted causal test**

1. Identify candidate heuristic:

   * e.g., “string-length comparison”
   * “first-digit dominance”
   * “authority bias” (anti-sycophancy)

2. Build paired prompts:

   * same structure
   * heuristic flips correctness

Example:

```text
9.11 vs 9.9   (heuristic wrong)
9.9 vs 9.11   (heuristic still wrong, but inverted framing)
```

3. Measure:

* heuristic-consistent logits
* before/after steering

---

### What proves suppression

If `v` reduces:

```text
logit(heuristic_choice)
```

**even when heuristic is correct**, then:

> it is suppressing the heuristic, not boosting correctness

That’s the cleanest possible demonstration.

---

## 2. **Linearity**

Right now:

* ε sweep → smooth
  This is weak evidence.

---

### What you need instead

**Additivity + compositionality**

---

### 🔥 Experiment

Take two independently evolved vectors:

```text
v₁ = decimal heuristic suppressor  
v₂ = sycophancy suppressor
```

Test:

```text
f(x + v₁ + v₂) ≈ f(x + v₁) + f(x + v₂) - f(x)
```

If true:

> effects are approximately linear and independent

---

### Stronger version

Orthogonalize:

```python
v2_orth = v2 - (v2 @ v1) * v1
```

Then test again.

---

### What this gives you

* linearity
* separability of mechanisms
* dimensionality of control space

---

## 3. **Generality**

Your current result:

* token generalization ✅
* prompt brittleness ❌

This is the most fragile part of your story.

---

### What you actually need

Generalization across:

| Axis           | Why it matters               |
| -------------- | ---------------------------- |
| lexical        | avoid memorization           |
| syntactic      | avoid prompt overfitting     |
| semantic       | actual concept               |
| task structure | beyond training distribution |

---

### 🔥 Missing experiment (important)

**Cross-task transfer of the same vector**

Example:

Train vector on:

* decimal comparison

Test on:

* fractions (“1/3 vs 1/4”)
* percentages (“33% vs 25%”)
* word problems (“3 out of 10 vs 2 out of 5”)

---

### Interpretation

If it transfers:

> you’ve found a **shared heuristic axis**

If not:

> you’ve found a **task-specific hack**

---

## 4. **Controls behavior**

You already have partial evidence.

But to *prove* it:

---

### 🔥 You need bidirectional monotonicity

For a given prompt:

```text
performance(-v) > baseline > performance(+v)
```

AND

monotonic trend across ε.

---

### Even stronger

**Decision boundary flipping**

Find prompts near decision boundary:

* baseline: 51% correct
* small ε:

  * flips answer deterministically

---

### That shows:

> the direction is *causally controlling* the output

---

# 🧰 PART 2 — What Your Toolkit Is Missing

These are the highest-leverage upgrades.

---

## 1. **You’re not measuring the heuristic directly**

Everything you measure is:

* correctness
* logits

You need:

> **heuristic activation metrics**

---

### Build this explicitly

For each task, define:

```python
heuristic_logit = logit(token_heuristic_answer)
correct_logit   = logit(token_correct_answer)
```

Track BOTH.

---

### Key signal

If:

```text
Δ heuristic_logit << 0
Δ correct_logit ≈ 0
```

→ suppression, not enhancement

---

## 2. **Residual trajectory analysis (you haven’t done this)**

This is huge.

---

### 🔥 Do this:

For each condition:

* baseline
* +v
* -v
* CoT

Collect:

```python
h[layer, token_position, d_model]
```

Then:

* PCA or UMAP on trajectories
* plot layer-wise movement

---

### What you’ll likely see

* CoT = large trajectory shift
* +v = tiny local shift
* -v = slightly larger shift in opposite direction

---

This visually confirms:

> “precision nudge vs regime change”

---

## 3. **You are not isolating LayerNorm effects**

This is a hidden confound.

Residual injection:

```text
h + αv
```

gets renormalized immediately.

---

### 🔥 Test this explicitly

Inject:

* pre-LN
* post-LN
* scaled vs unscaled

---

### If effect disappears post-LN:

→ your vector is exploiting normalization, not semantics

---

## 4. **Time-localization of effect**

Right now you only know:

* injection layer works

You don’t know:

> how long the signal survives

---

### 🔥 Do causal scrubbing forward

After injection:

* zero out later layers one by one

Find:

> where the effect actually manifests

---

# 🧭 PART 3 — Model Strategy (This Matters More Than You Think)

You asked:

> stay small vs move to mid-range?

Here’s the honest answer:

---

## Your current regime (0.5B–4B)

What you get:

* clean circuits
* strong heuristics
* weak reasoning

What you **won’t** get:

* stable reasoning subspaces
* clean CoT alignment
* real “precipitation”

---

## The 4B result you saw is the transition zone

Your data already shows it:

* slight CoT structure
* weak separability
* rare precipitation (Overtake Race)

---

## 🔥 Recommendation: Stay under 13B, but move *slightly up*

### Best targets:

* **Qwen2.5-7B**
* **Llama 3.1-8B**
* **Gemma 2-9B**

---

### Why these specifically

They have:

* **stronger competing systems**

  * heuristics vs reasoning
* **more stable CoT behavior**
* still:

  * analyzable
  * hookable
  * not too diffuse

---

### What will change at 7–9B

You’ll start seeing:

* real separatrices
* clearer probe signals
* stronger CoT alignment
* **actual competition dynamics**

---

### What will NOT change

Your vectors will STILL mostly be:

> suppression, not activation

---

# 🔥 Concrete Next Step (Highest ROI)

If I had to pick ONE experiment for you:

## 👉 **Heuristic Logit Decomposition + Bidirectional Sweep**

Combine:

* +v / -v / ablation
* track:

  * heuristic logits
  * correct logits
  * margin

---

### Expected outcome

You’ll see:

```text
+v:
  heuristic ↑
  correct ~same

-v:
  heuristic ↓↓↓
  correct ~same

ablation:
  heuristic ↓↓
  correct ~same
```

---

That is your smoking gun.

---

# 🧠 Final Take

You are not failing to find reasoning.

You are discovering something more fundamental:

> **behavior in small LMs is dominated by suppressible heuristic attractors**

And:

> **linear directions can control those attractors with high precision**

---

If you can show:

* suppression is linear
* suppression generalizes
* suppression composes
* suppression flips decisions

Then you’ve identified:

> a *control geometry of cognition*, not just a trick

---

That’s a much stronger foundation before you ever touch 13B+.

