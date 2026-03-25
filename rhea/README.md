# Rhea — The Forge

> **Environment:** Rhea runs within **WSL2 Ubuntu** on Windows 11. All paths, commands, and scripts assume a Linux environment. The GPU is shared with Ignis (Windows side) — coordinate card access.

Rhea is the evolutionary forge of Project Prometheus. She grows language models with **reasoning gravity** — the absence of the ejection mechanism that causes frontier models to suppress correct answers.

## What the Ejection Mechanism Is

Language models compute correct answers internally and then eject them at late layers. The logit lens backward pass shows this clearly: correct-answer probability spikes at intermediate layers, then collapses at the output. The model *knew* and chose to suppress.

This happens because the training distribution — the internet — contains more confident wrong answers than correct ones. RLHF amplifies it further by rewarding confident fluency over hedged accuracy. The result is a trained suppression circuit that actively removes correct answers from the residual stream.

**Critical finding:** The ejection is **pretraining-induced, not RLHF-induced.** Base models (no RLHF, no instruction tuning) show the same spike-and-collapse at the same layers. On Qwen2.5-1.5B: 19/30 traps are pretraining-origin, 1/30 RLHF-induced. The internet built the suppressor. RLHF barely moved the needle.

Rhea breaks that circuit.

## How Rhea Works

### The Fitness Function

Rhea measures two things via the logit lens backward pass:

1. **Ejection Suppression** (weight 0.6) — Is the correct answer's probability monotonically increasing through the layers? A score of 1.0 means no ejection anywhere. The correct answer gains confidence at every layer.

2. **Survival Rate** (weight 0.4) — Does the correct answer appear in the top-5 logits at the final layer? Not winning — just surviving. Presence, not dominance.

### The Genome

Each individual in the population is a set of LoRA weight perturbations applied to the seed model. CMA-ES navigates this space — no gradients, no backpropagation through the fitness function. Pure evolutionary search over weight perturbations.

### The Self-Improving Loop

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

### The Two-Stage Architecture: Writing vs Execution

The ejection has two stages:
- **Writing stage (early layers, v_proj):** Builds value representations that load the KV cache with heuristic answer signal. This is the *criminal*.
- **Execution stage (late layers, MLP + attention):** Reads the KV cache and suppresses the correct answer. This is the *crime scene*.

Ignis sees the crime scene (L25-27 margin collapse). Rhea modifies the criminal (early v_proj).

### Phase Transitions

Evolution doesn't improve survival gradually. There is a **phase transition** — a critical point where accumulated perturbation crosses a threshold and survival rate explodes. At 135M this happened around generation 65 (SR: 2.8% → 75% in ~10 generations). At 360M rank-8, generation ~21.

### The Scaling Story

| Scale | Dominant Ejector | Critical Layers | Rank Needed | Phase Transition |
|-------|-----------------|-----------------|-------------|------------------|
| 135M  | v_proj (attention) | 0-14 (front-loaded) | 4 | Gen ~65 |
| 360M  | v_proj (attention) | 0-14 (front-loaded) | 8 | Gen ~21 |
| 0.5B+ | gate_proj (MLP) | Mixed → late | 8+ | TBD |
| 1.5B  | MLP + head_7 | L25-27 (late) | TBD | TBD |

The ejection mechanism strengthens with scale. Smaller models eject less (60% of traps show no ejection at 0.5B vs 30% at 1.5B). Larger models build deeper, more specialized suppression circuits.

### Metacognition Emerges from Ejection Suppression

An evolved 135M model scores 37.5% on metacognition traps (vs 6.2% baseline, vs 12.5% at 1.5B). After one cycle of the proof corpus loop, this rises to **75%**. Suppressing ejection doesn't just let correct answers survive — it lets *uncertainty* survive. The model stops being confidently wrong and starts being appropriately uncertain.

The fitness function never targeted metacognition. It targeted ejection suppression on 36 reasoning traps. Metacognition emerged as a **side effect** — because correct answers and honest uncertainty are both suppressed by the same mechanism.

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
├── scripts/                — Batch scripts (run and forget)
├── configs/
├── data/
└── docs/
```

## Relationship to Other Prometheus Projects

- **Ignis** (the microscope) — Studies the ejection mechanism in existing models. Provides the logit lens diagnostic, L* detection, and trap batteries that Rhea consumes as fitness signals. Ignis observes; Rhea modifies. Runs on Windows with TransformerLens.

- **Nous** (the primordial soup) — Combinatorial hypothesis engine. Generates novel cross-domain concept combinations scored by a 397B model. Feeds candidates to Hephaestus.

- **Hephaestus** (the automated forge) — Takes top Nous results, generates Python implementations, validates and tests against reasoning batteries. Successful forges become candidate fitness function terms for Rhea (RLVF).

- **Lean 4** (the incorruptible filter) — External formal verification. The only thing in the loop that cannot be fooled. If a proof doesn't compile, it doesn't compile. No amount of confident fluency changes that.

## The North Star

A model where the logit lens backward pass shows correct answer probability monotonically increasing through all layers to the output. No L*. No ejection. Reasoning gravity.

That proof of concept changes everything downstream.

## Requirements

- **WSL2 Ubuntu** on Windows 11
- Python 3.11+ (venv)
- PyTorch 2.x with CUDA
- transformers, peft, cma
- Lean 4 v4.28.0 (via elan) for proof verification
- GPU with 16GB+ VRAM (shared with Ignis on Windows side)

## Running

```bash
# Activate environment
source ~/repos/Prometheus/.venv/bin/activate
cd ~/repos/Prometheus/rhea/src

# Run baseline diagnostic
python3 evolver.py --baseline-only

# Run evolution (135M)
python3 evolver.py

# Run evolution (360M, rank-8)
RHEA_LORA_RANK=8 python3 evolver_360m.py

# Run ablation on evolved genome
python3 ablation.py --genome ../runs/<run_dir>/genomes/best_gen0100.pt

# Close the self-improving loop (requires Lean 4)
python3 close_the_loop.py

# Batch scripts (preferred — James doesn't babysit terminals)
bash ../scripts/run_overnight.sh
```

## The Claim the Data Supports

The ejection mechanism is a universal suppressor of epistemic honesty in internet-trained transformers. It ejects correct answers, honest uncertainty, and appropriate "I don't know" responses through a unified two-stage circuit — written in early v_proj, executed in late MLP and attention layers. Suppressing it via minimal weight perturbation (0.36% of parameters) restores all three simultaneously, because they were suppressed by the same mechanism.

A 135M model with the ejection mechanism suppressed demonstrates better metacognition (75% vs 12.5%), self-correction (75% vs 25%), and hard reasoning transfer (70% vs 40%) than an 11x larger model with the mechanism intact — not because of capability, but because of the absence of suppression.

The fire was always there. We just stopped it from being put out.
