# Project Aethon — Executive Summary (Revised)

**Formerly Project AURA — Autonomous Unsupervised Reasoning Archaeology**
*Evolutionary Search for Latent Reasoning Capabilities in Language Model Architectures*

March 2026 — Post-Calibration Revision

---

## Problem Statement

Large language models possess rich internal representations of reasoning strategies, but standard inference activates only a fraction of these capabilities. Models rarely engage in metacognitive reflection (observed in only 0.04% of natural reasoning traces), rarely challenge their own conclusions through adversarial self-critique, and default to the most statistically probable reasoning path rather than exploring alternative cognitive modes. The space of reasoning configurations that language models can execute is vastly larger than the space they naturally explore. No systematic methodology exists for mapping this latent capability landscape.

## Approach

Project Aethon uses genetic algorithms with novelty-driven selection to evolve ordered sequences of reasoning modules — chain-of-thought, Socratic questioning, adversarial debate, Bayesian updating, metacognitive reflection, and five others — searching for prompt configurations that activate underutilized reasoning capabilities. Selection rewards structured novelty (outputs maximally distant from the existing archive in embedding space while maintaining coherence) rather than task performance. A MAP-Elites quality-diversity archive preserves diverse reasoning configurations across behavioral dimensions, creating a systematic atlas of the model's accessible reasoning landscape.

The system is complemented by a mechanistic analysis pipeline that probes the model's internal computation during evolved reasoning configurations using path-patching, layer-band ablation, and activation vector extraction through TransformerLens.

## Key Findings

### Behavioral Findings (Validated)

**Convergent reasoning motifs across substrates.** Three bigram motifs evolved independently in the top elites of both Llama 3.1 8B and Qwen 2.5 7B: metacognitive_reflection → devils_advocate, metacognitive_reflection → constraint_relaxation, and chain_of_thought → step_by_step_verification. These represent self-reflective reasoning patterns that novelty-driven evolution converges on regardless of the underlying model architecture.

**100% cross-substrate transfer.** 10/10 top elites survived transfer between models with >70% fitness retention. Several configurations gained fitness on the foreign model (up to 113% retention), indicating they exploit reasoning structures that are model-general rather than model-specific.

**Substrate-specific optimization strategies.** Qwen's evolution stacked metacognitive_reflection (+3.47 TF-IDF enrichment) while Llama's top elite used pure repeated Socratic questioning. Same selection pressure, different substrates, different solutions — converging on three shared functional motifs at the intersection.

**The metacognitive gap.** Cross-project analysis with Project Prometheus (which harvests natural reasoning traces from frontier models) revealed that metacognitive_reflection appears in only 0.04% of natural model traces, but Aethon's evolution pushes self-reflection to over 13% of the reasoning pipeline — a 334-fold difference. Evolution discovers that models benefit from self-reflection but almost never use it spontaneously.

**Reasoning delta distribution.** Mean reasoning delta (cosine distance between trace embedding and output embedding) was 0.053-0.060 across both models, indicating most evolved reasoning traces are functionally confabulatory. Right-skewed distribution with outliers reaching delta 0.30 identifies rare configurations where reasoning modules genuinely redirect computation.

### Mechanistic Findings (Calibrated Against Null Baseline)

**Distributed attractor basins are real but not evolution-specific.** Five genomes across the full fitness gradient show consistent mechanistic signatures: path-patching enrichment of 7.7x at genome-specific hotspot layers (L11, L12, L16, L18), byte-identical output surviving 5-layer band ablation while perplexity explodes 3,500-46,000x. However, Markov-shuffled null genomes show comparable signatures (7.70x vs 7.72x enrichment). The distributed attractor is a property of how the model processes structured multi-module prompts, not a property specific to evolutionarily optimized configurations.

**Interpretation.** The model possesses pre-existing distributed reasoning attractors for structured tasks. Both evolved and random structured prompts enter the same attractor basins. Evolution's contribution is navigational, not constructive — it finds prompt configurations that preferentially route computation toward underutilized attractor basins (particularly metacognitive modes) rather than creating new computational structures.

**Direction vector injection proof-of-concept.** A direction vector extracted from one genome's residual stream activations successfully shifted reasoning style on an unrelated prompt, demonstrating that reasoning-mode representations are extractable and transferable in activation space. Signal is weak at current injection parameters (single late-layer position, modest scale) and requires further exploration at earlier layers and higher scales.

### Calibration Results

**Null baselines.** Markov chain baseline (no LLM) showed declining fitness across 200 generations (0.77→0.35), confirming that maintaining structured novelty requires an actual language model. Mechanistic probe on null genome matched evolved genome signatures, falsifying the claim that evolution creates unique attractors.

**Characterization battery.** Of two high-delta specimens tested, one classified as noise (stochastic variance, reproducibility 0.59) and one as input-specific (reproducible but non-transferable specialist). The characterization battery successfully filters false positives, demonstrating calibrated instrumentation.

**Cross-seed replication (partial).** Genome from qwen_seed4 follows identical distributed-attractor pattern as qwen_seed3 genomes. Mechanism generalizes across evolutionary runs.

## Interpretive Discipline

Aethon identifies prompt configurations that reliably activate latent reasoning capabilities in language models. The model's pre-existing attractor landscape contains reasoning modes — particularly metacognitive reflection — that standard inference rarely reaches but that evolved prompt structures can reliably access. We claim structured computation and systematic capability discovery, not emergence, consciousness, or novel computational structures. The mechanistic contribution is characterization of the existing attractor landscape, not demonstration of new attractors.

## Current Platform Status

| Metric | Value |
|---|---|
| Source modules | 22+ files |
| Tests passing | 255+ |
| Reasoning module types | 10 |
| Completed evolution experiments | 6 seeds across 2 substrates |
| Null baselines completed | Markov (full), mechanistic probe (1 genome) |
| Cross-substrate transfer survival | 100% (10/10 elites) |
| Convergent motifs identified | 3 (validated against Markov null for behavioral separation) |
| Mechanistic probes completed | 6 genomes (5 evolved + 1 null) |
| Direction vector injection | POC positive (weak signal, further exploration needed) |

## Active Research Directions

1. **Automated continuous exploration ("Ignis mode")** — pipeline running 24/7, probing new genomes through mechanistic analysis, alerting on any signature that genuinely diverges from null baselines
2. **Multi-architecture substrate sweep** — testing evolved genomes against architecturally diverse models (Mistral/sliding-window attention, Phi/synthetic-data training, Gemma/different normalization, DeepSeek-R1-distill/reasoning-trained)
3. **Stronger vector injection** — earlier-layer injection (L10-14), higher scales, band-mean vectors, cross-genome vector transfer
4. **CMA-ES manifold exploration (Ignis)** — continuous optimization in activation space using evolved genomes as anchor points, searching for reasoning modes accessible through activation steering but not through natural language prompts
5. **Paper preparation** — writing up behavioral findings, mechanistic characterization, and null baseline calibration as a methodology contribution

---

*Project Aethon — Evolutionary Search for Latent Reasoning Capabilities*
*Contact: [email] · Repository: [repo-url]*
