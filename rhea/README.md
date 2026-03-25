# Rhea — The Forge

Rhea is the evolutionary forge of Project Prometheus. She grows language models with **reasoning gravity** — the absence of the ejection mechanism that causes frontier models to suppress correct answers.

## What the Ejection Mechanism Is

Language models compute correct answers internally and then eject them at late layers. The logit lens backward pass shows this clearly: correct-answer probability spikes at intermediate layers, then collapses at the output. The model *knew* and chose to suppress.

This happens because the training distribution — the internet — contains more confident wrong answers than correct ones. RLHF amplifies it further by rewarding confident fluency over hedged accuracy. The result is a trained suppression circuit that actively removes correct answers from the residual stream.

Rhea breaks that circuit.

## How Rhea Works

### The Fitness Function

Rhea measures two things via the logit lens backward pass:

1. **Ejection Suppression** (weight 0.6) — Is the correct answer's probability monotonically increasing through the layers? A score of 1.0 means no ejection anywhere. The correct answer gains confidence at every layer.

2. **Survival Rate** (weight 0.4) — Does the correct answer appear in the top-5 logits at the final layer? Not winning — just surviving. Presence, not dominance.

### The Genome

Each individual in the population is a set of LoRA weight perturbations applied to the seed model. CMA-ES navigates this space — no gradients, no backpropagation through the fitness function. Pure evolutionary search over weight perturbations.

### The Loop

```
Evolve (CMA-ES)
  → Generate reasoning chains
    → Verify with Lean 4 (formal, incorruptible)
      → Train on verified chains
        → Evolve again
```

The filter is formal, not neural. Lean 4 doesn't care how fluent a proof sounds. It either compiles or it doesn't. Garbage cannot propagate because the fitness function is deterministic and external.

## Key Findings

### The Ejection Circuit Lives in v_proj

Ablation on evolved genomes at 135M and 360M revealed that the ejection mechanism operates through **value projections in attention heads** (v_proj). Zeroing v_proj perturbations collapses survival from 92% to 0%. Keeping *only* v_proj perturbations recovers 64-72% survival. gate_proj and q_proj alone achieve nothing.

At 135M-360M, v_proj is not just the primary lever — it is the **entire** lever. A v_proj-only evolution with 19% of the parameters matches the full 3-component result exactly.

At 0.5B+, the ejection shifts to MLP-dominant (gate_proj). The mechanism specializes as models scale.

### Phase Transitions

Evolution doesn't improve survival gradually. There is a **phase transition** — a critical point where accumulated perturbation crosses a threshold and survival rate explodes. At 135M this happened around generation 65 (SR: 2.8% → 75% in ~10 generations). At 360M rank-8, generation ~21.

### The Scaling Story

| Scale | Dominant Ejector | Critical Layers | Rank Needed |
|-------|-----------------|-----------------|-------------|
| 135M  | v_proj (attention) | 0-14 (front-loaded) | 4 |
| 360M  | v_proj (attention) | 0-14 (front-loaded) | 8 |
| 0.5B+ | gate_proj (MLP) | Mixed → late | 8+ |
| 1.5B  | MLP + head_7 | L25-27 (late) | — |

The ejection mechanism strengthens with scale. Smaller models eject less (60% of traps show no ejection at 0.5B vs 30% at 1.5B). Larger models build deeper, more specialized suppression circuits.

### Metacognition Emerges from Ejection Suppression

An evolved 135M model scores 37.5% on metacognition traps (vs 12.5% baseline, vs 12.5% at 1.5B). After one cycle of the proof corpus loop, this rises to **75%**. Suppressing ejection doesn't just let correct answers survive — it lets *uncertainty* survive. The model stops being confidently wrong and starts being appropriately uncertain.

### The Coherence Trade-off

Evolved models break ejection but also break coherent text generation. Free generation produces repetition loops. This is the expected cost of pure evolutionary search — CMA-ES finds weight perturbations that game the fitness function without preserving generative capabilities. The proof corpus partially addresses this. Coherence-preserving evolution (with perplexity penalty) is under development.

## Architecture

```
rhea/
├── src/
│   ├── evolver.py          — CMA-ES evolution loop (135M)
│   ├── evolver_360m.py     — 360M evolution with scaling adaptations
│   ├── fitness.py          — Ejection suppression + survival rate
│   ├── logit_lens.py       — L* detection, monotonicity scoring
│   ├── genome.py           — LoRA flatten/unflatten for CMA-ES
│   ├── traps.py            — TINY_TRAPS battery (36 traps, 10 categories)
│   ├── ablation.py         — Layer and component ablation harness
│   ├── eval_v2.py          — 66-trap eval across 5 tiers (A/B/C/M/S)
│   ├── lean_verifier.py    — Lean 4 proof verification
│   ├── proof_corpus.py     — Verified training data generation
│   ├── close_the_loop.py   — Self-improving cycle (evolve→verify→train)
│   ├── lexical_patch.py    — "Unknown" vocabulary experiment
│   └── evaluate.py         — Standalone diagnostic harness
├── runs/                   — Evolution logs, genomes, ablation results
├── configs/
├── data/
└── docs/
```

## Relationship to Other Prometheus Agents

- **Ignis** (the microscope) — Studies the ejection mechanism in existing models. Provides the logit lens diagnostic, L* detection, and trap batteries that Rhea consumes as fitness signals. Ignis observes; Rhea modifies.

- **Arcanum** (the gene pool) — Hypothesis engine that generates novel research directions. Rhea's experimental design was informed by Arcanum's cross-domain synthesis.

- **Nous** (the primordial soup) — Concept recombination engine. Generates the novel theoretical connections that Rhea tests empirically.

- **Hephaestus** (the automated forge) — Code generation and validation. Builds the experimental infrastructure that Rhea runs on.

- **Lean 4** (the incorruptible filter) — External formal verification. The only thing in the loop that cannot be fooled. If a proof doesn't compile, it doesn't compile. No amount of confident fluency changes that.

## The North Star

A model where the logit lens backward pass shows correct answer probability monotonically increasing through all layers to the output. No L*. No ejection. Reasoning gravity.

That proof of concept changes everything downstream.

## Requirements

- Python 3.12+
- PyTorch 2.x with CUDA
- transformers, peft, cma
- Lean 4 (via elan) for proof verification
- GPU with 16GB+ VRAM (RTX 5060 Ti or equivalent)

## Running

```bash
# Create venv and install
python3 -m venv .venv && source .venv/bin/activate
pip install torch transformers peft accelerate cma

# Run baseline diagnostic
cd src && python3 evolver.py --baseline-only

# Run evolution
python3 evolver.py

# Run ablation on evolved genome
python3 ablation.py --genome ../runs/<run_dir>/genomes/best_gen0100.pt

# Close the loop (requires Lean 4)
python3 close_the_loop.py
```
