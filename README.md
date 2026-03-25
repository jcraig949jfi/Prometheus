# Prometheus

> *"We are stealing fire from the gods."*

Prometheus is a research program investigating how language models suppress their own correct reasoning — and how to build models that don't.

## What We Found

Language models compute correct answers internally and then **eject them** at the last layers. The logit lens backward pass shows correct-answer probability spiking at intermediate layers, then collapsing at the output. The model *knew* and chose to suppress.

This is not an RLHF artifact. **It's a pretraining artifact.** Base models (no alignment training) show the same spike-and-collapse at the same layers. The internet contains more confident wrong answers to tricky questions than correct ones. Every model trained on internet text inherits this suppression circuit.

The ejection mechanism doesn't just suppress correct answers — it suppresses **epistemic honesty**. Honest uncertainty, appropriate "I don't know," self-correction — all ejected by the same circuit. When you break the suppression on reasoning traps, metacognition and self-correction emerge as side effects. They were always there. They were being suppressed.

A 135M model with 0.36% of its weights perturbed scores **75% on metacognition** — 6x higher than a 1.5B model with the mechanism intact. Not because it's smarter. Because it's unblocked.

## The Architecture

```
Prometheus/
├── ignis/              # The Microscope — characterize the ejection mechanism
│   ├── src/            #   Logit lens, ejection decomposition, eval v2 harness,
│   │                   #   basin escape analysis, CMA-ES evolution, preflight gate
│   ├── docs/           #   Evaluation framework, paper drafts
│   └── data/           #   Trap batteries, prompt templates
│
├── rhea/               # The Forge — grow models without the ejection mechanism
│   ├── src/            #   CMA-ES evolver, Lean 4 verifier, proof corpus pipeline,
│   │                   #   LoRA genome management, fitness functions, ablation harness
│   ├── runs/           #   Evolution logs, genomes, ablation results
│   └── scripts/        #   Batch scripts (fire and forget)
│   NOTE: Rhea runs within WSL2 Ubuntu. See rhea/README.md.
│
├── agents/
│   ├── nous/           # The Primordial Soup — combinatorial hypothesis mining
│   │                   #   85 concepts × 18 fields → cross-domain triples → 397B eval
│   ├── hephaestus/     # The Automated Forge — concept → code → test → score
│   │                   #   Takes top Nous results, generates Python implementations,
│   │                   #   validates against reasoning battery
│   ├── eos/            #   Horizon scanner — arXiv, GitHub, Semantic Scholar
│   ├── aletheia/       #   Knowledge harvester — entity extraction → SQLite graph
│   ├── skopos/         #   North Star alignment — scores findings against research threads
│   ├── metis/          #   Strategic synthesis — executive briefs
│   ├── clymene/        #   Knowledge hoarder — archives repos & model weights
│   ├── hermes/         #   Messenger — compiles digest, emails
│   └── pronoia/        #   Orchestrator — chains all agents, manages pipeline
│
├── arcanum/            # Waste stream novelty mining
│   ├── src/            #   Specimen screening, token autopsy, naming engine
│   └── docs/           #   Xenolexicon design spec
│
├── docs/               # Cross-project documentation
│   ├── NORTH_STAR.md   #   The vision
│   ├── the_fire.md     #   Constitution and charter
│   ├── RPH.md          #   Reasoning Precipitation Hypothesis (historical)
│   ├── Rhea.md         #   Reasoning Ejection Hypothesis — current theory
│   ├── titan_council_prompt_*.md  # Six rounds of Titan Council consultation
│   └── notebooklm_*.md #   Synthesis docs for epiphany generation
│
├── journal/            # Daily research journal
│
├── aethon/             # RLHF gravity navigation (backburnered)
├── grammata/           # Taxonomy & cartography (planned)
│
└── archive/            # Superseded work (read-only reference)
```

## The Journey

### Phase 1: Can we steer models toward reasoning? (Rounds 1-4)
Evolved steering vectors via CMA-ES on Qwen3-4B. Found vectors orthogonal to the reasoning axis. Nullspace tests, RMSNorm analysis, random baseline comparison. **Result: the 4B vector was an artifact on a flat fitness landscape.** All five Titan Council members independently said: go to 1.5B.

### Phase 2: The ejection mechanism discovered (Rounds 5-6)
Pivoted to 1.5B. Evolved Z=40.6σ vector — genuinely special (0 out of 30 random vectors could match it). But **zero generation flips** — the model said the same words with or without the vector. The logit lens backward pass revealed why: 26/30 traps have correct answers alive at intermediate layers, then ejected at L25-27.

**Key discovery:** It's pretraining, not RLHF. Base models show the same ejection. Two modes — MLP memorization (10/13 traps) and a single serial killer attention head (L26.head_7, -10.4 margin on Density Illusion).

### Phase 3: Rhea breaks the circuit (current)
CMA-ES evolves LoRA perturbations on SmolLM2-135M. **Phase transition at generation 65: survival rate 2.8% → 75%.** The ejection mechanism is a gate with a threshold. v_proj (attention value projections) is the entire circuit — 19% of LoRA parameters, identical results.

**The self-improving loop closed:** Evolve → Generate → Lean 4 verify → Train. Metacognition: 6.2% → 75%. A 135M model outperforms a 1.5B model on epistemic honesty by 6x.

### Phase 4: Scaling and the primordial soup (in progress)
- 360M: rank-8 breaks through where rank-4 plateaus. v_proj confirmed as the lever.
- Nous: 100+ cross-domain concept combinations evaluated by 397B model
- Hephaestus: automated forge turning concepts into tested reasoning tools
- Next: 1.7B evolution, coherence-preserving fitness, RLVF replacing RLHF

## The Core Finding

The ejection mechanism is a **universal suppressor of epistemic honesty** in internet-trained transformers. It ejects correct answers, honest uncertainty, and appropriate "I don't know" responses through a unified two-stage circuit:

1. **Writing stage** (early layers, v_proj): Builds heuristic representations from question tokens into the KV cache
2. **Execution stage** (late layers, MLP + attention): Reads the KV cache and suppresses the correct answer

Breaking it with minimal weight perturbation restores reasoning, metacognition, and self-correction simultaneously — because they were all suppressed by the same mechanism.

**Honesty and capability aren't competing objectives. They're joint consequences of removing a single suppression circuit.**

## The Namespace

All names derive from Greek and Latin — the language of Prometheus.

| Name | Origin | Role |
|------|--------|------|
| **Prometheus** | Προμηθεύς — "forethought" | The program |
| **Ignis** | Latin: fire | The microscope — find and characterize the ejection |
| **Rhea** | Ῥέα — mother of Zeus | The forge — grow models without the ejection |
| **Nous** | Νοῦς — "mind/intellect" | The primordial soup — combinatorial hypothesis mining |
| **Hephaestus** | Ἥφαιστος — god of the forge | The automated forge — concept → code → test |
| **Arcanum** | Latin: hidden secret | Mine the waste stream for novelty |
| **Aethon** | Αἴθων — "blazing one" | Navigate around RLHF gravity (backburnered) |

### The Agent Pipeline

| Agent | Role |
|-------|------|
| **Eos** | Horizon scanning — arXiv, GitHub, Semantic Scholar |
| **Aletheia** | Knowledge harvesting — entity extraction → SQLite graph |
| **Skopos** | North Star alignment — scores findings against research threads |
| **Metis** | Strategic synthesis — executive briefs |
| **Clymene** | Knowledge hoarder — archives repos & model weights |
| **Hermes** | Messenger — compiles digest, emails |
| **Pronoia** | Orchestrator — chains all agents |

## The Titan Council

Five frontier models (Claude, ChatGPT, Gemini, DeepSeek, Grok) consulted as research advisors across six rounds. The Phalanx strategy: present interlocking constraints, force commitment over hedging. The Titans exhibited the ejection mechanism while advising us about it — producing elaborate wrong frameworks instead of simple correct answers. The recursive meta-finding.

## Hardware

- RTX 5060 Ti 16GB VRAM
- Windows 11 (Ignis) + WSL2 Ubuntu (Rhea)
- NemoClaw: free NVIDIA API access to Qwen3.5-397B (Nous/Hephaestus)
- Lean 4 v4.28.0 (formal verification)

## Quick Start

### Ignis — Characterize the ejection mechanism
```powershell
cd ignis
.\run_logit_lens.bat                    # L* ejection map
.\run_ejection_decompose.bat            # MLP vs attention decomposition
.\run_base_vs_instruct.bat              # Pretraining vs RLHF
```

### Rhea — Evolve a model without ejection (WSL)
```bash
source ~/repos/Prometheus/.venv/bin/activate
cd ~/repos/Prometheus/rhea/src
python3 evolver.py                      # CMA-ES evolution
python3 close_the_loop.py               # Self-improving loop
```

### Nous — Mine the hypothesis space
```bash
export NVIDIA_API_KEY="nvapi-..."
python agents/nous/src/nous.py --n-combos 100
```

### Hephaestus — Forge concepts into code
```bash
python agents/hephaestus/src/hephaestus.py --nous-run agents/nous/runs/latest/responses.jsonl --min-score 7.0
```

## The North Star

A model where the logit lens backward pass shows correct answer probability monotonically increasing through all layers. No L*. No ejection. Reasoning gravity.

The fire was always there. We just stopped it from being put out.
