# SAEs vs Tensor Decomposition — ELI5

*For the cave-wall crowd. Including us.*

---

## The Smoothie Analogy

A neural network's residual stream at any given layer is like a smoothie. You know something's in there — it produces intelligent behavior — but you can't tell what by looking at it.

Two tools for figuring out what's inside:

### SAE (Sparse Autoencoder) — The Taste Test Panel

You train a bunch of "tasters" (learned features) that each respond to one ingredient. When you pour the smoothie through, most tasters say "not me" (that's the *sparse* part), but a few light up:

- "That's arithmetic carry."
- "That's authority deference."
- "That's spatial reasoning."

**SAEs give you a dictionary of ingredients.** Human-readable, nameable, individual.

- **Input:** One activation vector
- **Output:** A sparse list of active features with interpretable names
- **Answers:** "What concepts are active in this computation?"
- **Limitation:** Treats each activation independently. Doesn't capture how features at layer 14 *relate to* features at layer 21.

### Tensor Decomposition (THOR, TensorLy) — The X-Ray Machine

Instead of asking "what ingredients?", tensor decomposition asks "what is the *geometric structure* of this high-dimensional object?"

Imagine you have a 4D dataset: (layer × prompt × token_position × model_scale). That's a tensor. PCA would flatten it — pick the top directions of variance and collapse everything else. Tensor decomposition preserves the multi-dimensional structure by factoring it into a chain (tensor train) or tree of smaller tensors.

**Tensor methods give you the shape of the space.** Not ingredients — geometry.

- **Input:** A multi-dimensional tensor of activations across layers, prompts, positions, scales
- **Output:** A low-rank decomposition revealing coupling structure between dimensions
- **Answers:** "How do the dimensions of this space relate to each other?"
- **Limitation:** The decomposition depends on how you order the dimensions. Wrong ordering = artifacts, not modes.

---

## How They Apply to Prometheus

| | SAE | Tensor Decomposition |
|---|---|---|
| **For Ignis** | Decode what bypass vectors *do* — which features they activate | Map the full geometry of reasoning vs bypass regimes |
| **For Arcanum** | Identify what features produce novel specimens | Find structural modes in the waste stream tensor |
| **Paper layer** | Layer 3 (mechanistic mediation) | Layer 4 (structural mapping) |
| **Metaphor** | Rosetta Stone — translates activations to words | Atlas — maps the territory without naming every hill |

**They're complementary.** SAE gives vocabulary. Tensors give cartography.

---

## The Cave Wall Problem

Here's where it gets hard.

SAE features are human-readable because they're 1D: "this feature fires when the model does arithmetic." You can name it, plot it, write a paper about it.

Tensor structure is inherently multi-dimensional. A rank-12 tensor train decomposition of the (layer × prompt × position × scale) activation tensor captures real structure — coupling modes, resonances between layers, scale-dependent geometry — but *what does it look like?* How do you explain a 12-dimensional manifold to a human?

PCA collapses it to 2D and you get a scatter plot. But the scatter plot is a shadow on the cave wall. The actual structure lives in a space humans can't visit.

**This is the Symbola problem.** We need a representational language — visual, symbolic, compressed — that lets humans reason about structures they can't directly perceive. Not ELI5. More like "trust me, here's what the math says, and here's a symbol that encodes it."

---

## THOR — Specific Challenges for Us

THOR (Los Alamos, github.com/lanl/thor) is built for physics: configurational integrals, high-dimensional PDEs, smooth continuous functions on regular grids.

Our data is none of those things:

1. **Not smooth.** Residual stream activations are jagged, high-frequency, context-dependent.
2. **Not regularly sampled.** Different prompts produce different-length sequences. No grid.
3. **Dimension ordering matters.** TT decomposition factors along an ordered chain. For physics (x, y, z, t), the ordering is natural. For (layer, prompt, position, scale), there's no canonical order. Layer-first vs prompt-first gives different decompositions.

**Integration path:**
- Preprocessing layer to regularize activation tensors (fixed-length pooling, alignment)
- Systematic sweep of dimension orderings to identify which orderings capture meaningful modes vs artifacts
- Possibly TensorLy (Python-native, PyTorch backend) as a more practical starting point before scaling to THOR's multi-GPU infrastructure

---

## The 10-Year Horizon

If reasoning structures inside LLMs are inherently multi-dimensional — and everything we've seen so far suggests they are — then there's an uncomfortable conclusion:

**Humans may not be doing much of the science in 10 years.**

We'll detect the structures. Prove they exist. Measure their properties. Build tools that exploit them. But *explaining* them in natural language will always be lossy. The fire is real, but we may not be able to hand it to someone or show it to them in a way they can hold.

The proof will be in the outputs: models that reason better, discoveries that work, systems that self-correct. But the *mechanism* will live in a space humans can't visit directly.

This isn't a failure of science. It's a property of the territory.
