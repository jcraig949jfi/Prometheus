# Titan Council Prompt 03 — The Orthogonal Subspace Problem

*For: Claude/Coeus, ChatGPT/Atlas, Gemini/Hyperion, DeepSeek/Oceanus, Grok/Prometheus*
*From: Project Prometheus (mechanistic interpretability research)*
*Date: 2026-03-23*

---

## TO THE COUNCIL

We took your advice. All of it. We built the seven analysis tools you proposed, ran the Bianco adaptation, executed the controlled confound tests, completed the PCA decomposition. We've also read the literature you would have pointed us toward — Arditi et al. on refusal directions, Zou et al. on circuit breakers, Zhang & Viteri on latent CoT vectors, the USAE paper from ICML 2025, GER-steer, conceptor-based steering, SAE-targeted steering, and MLAS for anti-sycophancy.

We're not here to ask "what should we try next." We're here because the data is saying something we don't fully understand, and we suspect it's at the boundary of what the current literature addresses.

**We are not asking for reassurance or a literature review. We already have both. We want you to think past what's published.**

---

## THE FINDING

We evolved a steering vector via CMA-ES on Qwen3-4B (36 layers, d_model=2560, injection at L31). The vector was optimized for logit margin on 4 adversarial reasoning traps. Standard stuff. Here's what's not standard:

### 1. The vector is orthogonal to the model's reasoning axis

Two independent methods confirm this:

| Method | cos(vector, correct→incorrect direction) |
|--------|------------------------------------------|
| PCA centroid analysis (100 diverse prompts, 50 PCs) | **-0.026** |
| Layerwise probe at injection layer (AUC=0.588) | **-0.024** |

The vector does not point toward correct answers. It does not point away from incorrect answers. It lives in a subspace **orthogonal** to the linear separatrix between correct and incorrect model behavior.

Yet it was evolved to *improve* task performance and achieved fitness 1.152.

### 2. The anti-CoT signal is partially real, partially artifact

Our controlled confound test compared three prompt conditions per trap:

| Condition | Mean cos(vector, Δh) | Interpretation |
|-----------|----------------------|----------------|
| CoT-appended ("Let's think step by step") | **-0.136** (10/10 negative) | Vector opposes CoT shift |
| CoT-embedded (reasoning baked into prompt text) | **-0.033** (4 neg, 5 ambiguous, 1 positive) | Signal drops 75% |

The appended anti-CoT correlation is 100% consistent but ~75% of it is prompt-length/positional confound. A real but weak residual signal persists on some traps (Density Illusion: -0.17, Decimal Magnitude: -0.10).

**The exception:** Overtake Race — the only trap showing precipitation — *flips positive* (+0.12) under embedded CoT. The vector aligns with reasoning on the one trap where it actually works.

### 3. The Bianco dose-response reveals architecture-dependent geometry

| Model | Phase transitions found |
|-------|------------------------|
| Qwen2.5-1.5B | **2 of 4** traps (Decimal Magnitude 3.7x, Prime Check 4.3x) |
| Qwen3-4B | **0 of 4** traps (all smooth) |

The 1.5B vector hits binary phase transitions — heuristic on/off switches. The 4B vector operates smoothly. Same CMA-ES process, same trap battery, completely different geometric behavior.

### 4. The vector pushes away from both centroids equally

| | cos(vector, centroid) |
|---|---|
| Correct answers | **-0.196** |
| Incorrect answers | **-0.176** |

Not pushing toward right. Not pushing toward wrong. Pushing away from the **populated region of activation space entirely** — into a sparse, unoccupied region.

---

## OUR INTERPRETATION (CHALLENGE THIS)

We believe the vector is performing **unsupervised representation rerouting** — the same geometric operation as Zou et al.'s circuit breakers (2406.04313), but discovered blindly by CMA-ES rather than engineered intentionally.

The mechanism: CMA-ES found that the highest-fitness intervention isn't amplifying the correct computation or suppressing the incorrect one. It's *destabilizing the default computational pathway* by pushing the residual stream into a region where neither the heuristic attractor nor the correct-reasoning attractor dominates. In this destabilized state, the model's autoregressive dynamics at layers 32-36 determine the outcome — and on some traps (Overtake Race), the destabilization is sufficient for the model's own late-layer circuits to find the correct answer.

This would explain:
- **Orthogonality to the reasoning axis:** The vector isn't in the reasoning plane at all
- **Partial anti-CoT:** The vector opposes the *default trajectory* which CoT also opposes, but via a different path
- **Overtake Race exception:** This trap sits closest to the decision boundary, so destabilization tips it
- **Prompt brittleness:** The destabilization only works when the model is at a specific computational state that depends on exact token sequences
- **Phase transitions at 1.5B but not 4B:** Smaller models have sharper attractor basins (lower-dimensional manifold), so destabilization produces binary flips. Larger models have smoother basins, so the effect is graded.

---

## THE QUESTIONS WE CAN'T ANSWER FROM THE LITERATURE

**Q1: Is "orthogonal destabilization" a known phenomenon, or are we observing something new?**

Arditi et al. found refusal directions that are *aligned* with behavioral axes. Zou et al.'s circuit breakers *reroute* to orthogonal space intentionally. Zhang & Viteri's CoT vectors *align* with reasoning directions. All of these work *within* or *deliberately perpendicular to* known behavioral subspaces.

Our vector wasn't designed to be orthogonal — CMA-ES found that orthogonality was *optimal for fitness*. We can't find a paper where evolutionary optimization of steering vectors converged on an orthogonal-to-task direction. Is this an artifact of our fitness function, or evidence that the optimal intervention point for reasoning tasks is genuinely outside the reasoning subspace?

**Q2: What is the geometric relationship between "destabilization" and "precipitation"?**

If our vector destabilizes the default computational pathway, and precipitation requires a phase transition from heuristic to reasoning regimes, then destabilization might be a *necessary precondition* for precipitation but not sufficient. The analogy: you need to supercool the solution (destabilize) before crystals can form (precipitate). The vector provides supercooling; whether precipitation occurs depends on the trap-specific geometry of the model's late-layer circuits.

Can this be formalized? Is there a Lyapunov-style stability analysis for attractor basins in transformer residual streams that would let us predict *which* traps will precipitate under destabilization?

**Q3: Should we evolve for CoT-alignment, or is that the wrong target?**

Zhang & Viteri (2409.14026) extracted CoT directions via contrastive activation differences. Our controlled test shows the evolved vector is *not* a CoT direction — it's orthogonal to it. If we re-evolve for CoT-alignment (cosine similarity to CoT delta as fitness), we might find a clean reasoning amplifier — but we'd lose the orthogonal destabilization property that makes our current vector interesting.

The conceptor framework (2410.16314) suggests we could compose both: evolve one vector for CoT-alignment, keep the current one for destabilization, and combine them via conceptor Boolean operations. But this assumes the two objectives are compatible in the residual stream geometry. Are they? Or does destabilization destroy the manifold that CoT-alignment needs to operate on?

**Q4: The USAE projection question**

The Universal SAE paper (2502.03714, ICML 2025) trains a single SAE across multiple architectures. If we project our Qwen3-4B vector through a USAE into Gemma-2-2B space and decompose it via Gemma Scope, we'd get human-readable feature descriptions.

But our vector is orthogonal to the model's behavioral axes. SAEs are trained on *typical* activations — the populated region of activation space that our vector points *away from*. Will an SAE even have features for the sparse region our vector targets? Or will the reconstruction error be enormous because the vector lives in the SAE's dead zone?

Is there a way to determine, *a priori*, whether SAE decomposition will be informative for a direction that's orthogonal to the activation distribution?

**Q5: The scale-dependent attractor geometry**

At 1.5B (28 layers, d_model=1536), dose-response shows sharp phase transitions. At 4B (36 layers, d_model=2560), everything is smooth. The best layerwise probe moves from L3 (1.5B) to L31 (4B) — from 11% depth to 86% depth.

This suggests the reasoning-relevant computation moves deeper and becomes more distributed as models scale. The 1.5B model has reasoning-adjacent features at L3 (early, fragile, binary). The 4B model distributes them across L31-L35 (late, robust, graded).

Is there a known scaling law for the *depth* at which reasoning features emerge? Can we predict, for a 7B or 14B model, where the best injection layer would be without running the full CMA-ES pipeline?

---

## WHAT WE WANT FROM YOU

1. **Tear apart the "orthogonal destabilization" interpretation.** If it's wrong, what's the correct geometric reading of these five findings?

2. **Design an experiment that distinguishes destabilization from noise.** Our vector might just be a high-norm random direction that happens to perturb the model. How do we prove it's structured destabilization rather than random perturbation? (We tested random vector controls on DAS and got 10-15x lower effect, but that's for the *aligned* direction, not the orthogonal component.)

3. **Write code for the single highest-leverage experiment we can run on 16GB VRAM with Qwen3-4B.** Not a roadmap. One experiment. The one that most decisively resolves whether the orthogonal subspace our vector occupies is computationally meaningful or a fitness function artifact.

4. **Address Q2 directly.** If you know of any formal framework (dynamical systems, information geometry, anything) for analyzing attractor basin stability in residual streams under linear perturbation, cite it. If none exists, sketch what it would need to look like.

5. **Tell us something we haven't considered.** We've been staring at this data for 48 hours. What are we pattern-matching that isn't there? What are we not seeing that is?

---

## TECHNICAL DETAILS FOR CODE

- **Hardware:** RTX 5060 Ti 16GB, Windows 11, Python 3.11
- **Stack:** TransformerLens, PyTorch 2.x, sae-lens (not installed — will install if needed), EvoTorch
- **Model:** Qwen/Qwen3-4B (36 layers, d_model=2560), loaded via HookedTransformer
- **Genome:** `best_genome.pt` — keys: `vector` (shape [2560]), `layer_index` (31), `fitness` (1.152)
- **VRAM limit:** Model loads at ~12GB. ~4GB free for activations/caches. Use `names_filter` on `run_with_cache` to avoid OOM. One layer cached at a time.
- **Existing infrastructure:** `analysis_base.py` provides `AnalysisBase` class with model loading, genome loading, hook factories, trap batteries (4 logit traps + 6 held-out traps), scoring utilities

---

*The fire keeps burning. We're not asking you to light the torch — we're asking you to tell us what we're holding.*
