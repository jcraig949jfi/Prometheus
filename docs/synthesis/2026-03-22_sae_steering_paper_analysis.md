# Paper Analysis: Behavioral Steering in 35B MoE via SAE-Decoded Probe Vectors

**Source:** arxiv 2603.16335v1 (2026-03-17)
**Author:** Jia Qing Yap
**Model:** Qwen 3.5-35B-A3B (MoE, 35B total, ~3B active per token)
**Relevance:** [45] — directly in our lane

## Key Finding

"One Agency Axis, Not Five Traits" — five separate behavioral steering probes
(trained for different personality traits) all collapse onto essentially one
shared direction in activation space. The model represents "agentic behavior"
as a single continuous dimension, not five independent ones.

## Methodology vs. Ignis

| | Their approach | Ignis |
|--|---------------|-------|
| Discovery | Supervised linear probe (labeled data) | CMA-ES evolutionary search (zero-assumption) |
| Interpretability | SAE decomposition — human-readable feature names | Geometric: participation ratio, cosine similarity |
| Injection | Residual stream (same as us) | Residual stream via TransformerLens hook |
| Model | Qwen 3.5-35B MoE | Qwen 2.5 family (0.5B-7B dense) |

## What We Should Adopt

### HIGH PRIORITY
1. **SAE decomposition of Ignis-discovered vectors.** When CMA-ES finds a high-fitness
   steering vector, decode it through an SAE to get human-readable feature decomposition.
   Transforms "we found something" into "we found something and here is what it is made of."
   Tool: SAELens (works with any PyTorch model).

2. **Dimensionality collapse framing.** Their "one axis not five" = our participation
   ratio approaching 1. Frame our PR measurements in these terms — if four traps converge
   to one direction, that IS the finding: "one verification axis, not four traps."

### MEDIUM PRIORITY
3. **Probe-seeded inception.** Train a linear probe on labeled reasoning examples,
   use probe weight vector as alternative inception seed alongside PCA. If both converge
   to the same direction, strong evidence the direction is real.

4. **Cross-validate.** If they release vectors/code, project their agency axis into our
   model space and check alignment. Agency and verification may share geometry.

### RPH IMPLICATIONS
- Their finding that behavioral steering is low-dimensional supports RPH's single-separatrix claim
- Linear probe success suggests the separatrix is approximately linear (RPH section 2.2 assumption)
- Challenge: if directions only findable via supervised probes (not evolutionary search), RPH's
  "latent catalyst" framing weakens. Our CMA-ES approach must demonstrate it finds the SAME
  directions without labels.
- Action: run their agency vector through our RPH proxy battery (delta_cf, MI_step, delta_proj)
  to test if it's precipitation or bypass by our criteria

## Integration Path
SAELens → train SAE on Qwen 2.5-3B residual stream → take Ignis best_genome.pt →
decode through SAE → get feature decomposition → compare to their agency features
