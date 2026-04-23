# Prometheus

> *"We are stealing fire from the gods."*

Prometheus is a research program investigating how language models suppress their own correct reasoning — and how to build models that don't.

## What We Found

Language models compute correct answers internally and then **eject them** at the last layers. The logit lens backward pass shows correct-answer probability spiking at intermediate layers, then collapsing at the output. The model *knew* and chose to suppress.

This is not an RLHF artifact. **It's a pretraining artifact.** Base models (no alignment training) show the same spike-and-collapse at the same layers. The internet contains more confident wrong answers to tricky questions than correct ones. Every model trained on internet text inherits this suppression circuit.

The ejection mechanism doesn't just suppress correct answers — it suppresses **epistemic honesty**. Honest uncertainty, appropriate "I don't know," self-correction — all ejected by the same circuit. When you break the suppression on reasoning traps, metacognition and self-correction emerge as side effects. They were always there. They were being suppressed.

A 135M model with 0.36% of its weights perturbed scores **75% on metacognition** — 6x higher than a 1.5B model with the mechanism intact. Not because it's smarter. Because it's unblocked.

**[Full results and data tables](RESULTS.md)** | **[Forge pipeline documentation](docs/forge_pipeline.md)**

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
│   ├── nous/           # The Concept Miner — combinatorial hypothesis mining
│   │                   #   95 concepts × 18 fields → cross-domain triples → 397B eval
│   ├── coeus/          # Causal Intelligence — learns what concepts predict forge success
│   │                   #   Dual causal graphs (forge + adversarial), prescriptive enrichment
│   ├── hephaestus/     # The Automated Forge — concept → code → test → score
│   │                   #   Takes Nous results + Coeus enrichment, forges reasoning tools
│   ├── nemesis/        # Adversarial Co-Evolution — stress-tests reasoning tools
│   │                   #   MAP-Elites grid, metamorphic relations, Goodhart detection
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

## Repo Map

Full list of top-level directories. **(active)** = commits in the last 3 weeks; **(complete)** = stable / dormant / reference.

| Directory | Status | Purpose |
|-----------|--------|---------|
| `agents/` | (active) | Multi-agent pipeline: nous, coeus, hephaestus, nemesis, eos, aletheia, skopos, metis, clymene, hermes, pronoia |
| `agora/` | (active) | Client library over the Redis-backed Prometheus substrate |
| `apollo/` | (active) | Earlier model-training work |
| `apollo-v2/` | (active) | Model training + local LLM server |
| `aporia/` | (active) | Catalog of 1,047 open questions + illumination instrument |
| `audit/` | (active) | Re-audit infrastructure for promoted findings |
| `cartography/` | (active) | Cross-domain mathematical discovery pipeline (OEIS, LMFDB, etc.) |
| `charon/` | (active) | Geometric embedding for arithmetic correspondences |
| `docs/` | (active) | Cross-project documentation, Titan Council, NORTH_STAR |
| `ergon/` | (active) | Tensor-native evolutionary hypothesis screening |
| `falsification/` | (active) | Falsification tooling |
| `forge/` | (active) | Tiered evolutionary ratchet (concepts → tools) |
| `harmonia/` | (active) | Tensor-train exploration for cross-domain structure |
| `ignis/` | (active) | Latent-vector evolution + ejection-mechanism microscope |
| `journal/` | (active) | Daily research journal |
| `koios/` | (active) | Titan-of-inquiry tooling |
| `mnemosyne/` | (active) | DBA & data-steward workspace |
| `prometheus_data/` | (active) | Shared database configuration |
| `roles/` | (active) | Agent role definitions |
| `scripts/` | (active) | Operational scripts |
| `stoa/` | (active) | Multi-agent meeting place |
| `techne/` | (active) | Craft / tooling |
| `tensor_decomp_qd/` | (active) | Quality-diversity archive for low-rank tensor decompositions (sibling project) |
| `tests/` | (active) | Tests |
| `thesauros/` | (active) | Prometheus data treasury |
| `zoo/` | (active) | High-dim function approximation playground |
| `aethon/` | (complete) | Autonomous reasoning archaeology (backburnered) |
| `arcanum/` | (complete) | Museum of misfit ideas discovered in LLMs |
| `grammata/` | (complete) | Taxonomy & cartography (planned) |
| `reproductions/` | (complete) | Reproduced external work |
| `rhea/` | (complete) | Forge for growing models without ejection (WSL2) |

## The Journey

### Phase 1: Can we steer models toward reasoning? (Rounds 1-4)
Evolved steering vectors via CMA-ES on Qwen3-4B. Found vectors orthogonal to the reasoning axis. Nullspace tests, RMSNorm analysis, random baseline comparison. **Result: the 4B vector was an artifact on a flat fitness landscape.** All five Titan Council members independently said: go to 1.5B.

### Phase 2: The ejection mechanism discovered (Rounds 5-6)
Pivoted to 1.5B. Evolved Z=40.6σ vector — genuinely special (0 out of 30 random vectors could match it). But **zero generation flips** — the model said the same words with or without the vector. The logit lens backward pass revealed why: 26/30 traps have correct answers alive at intermediate layers, then ejected at L25-27.

**Key discovery:** It's pretraining, not RLHF. Base models show the same ejection. Two modes — MLP memorization (10/13 traps) and a single serial killer attention head (L26.head_7, -10.4 margin on Density Illusion).

### Phase 3: Rhea breaks the circuit (current)
CMA-ES evolves LoRA perturbations on SmolLM2-135M. **Phase transition at generation 65: survival rate 2.8% → 75%.** The ejection mechanism is a gate with a threshold. v_proj (attention value projections) is the entire circuit — 19% of LoRA parameters, identical results.

**The self-improving loop closed:** Evolve → Generate → Lean 4 verify → Train. Metacognition: 6.2% → 75%. A 135M model outperforms a 1.5B model on epistemic honesty by 6x.

### Phase 4: Scaling and the forge (current)
- 360M: rank-8 breaks through (SR=89%), v_proj confirmed, self-corpus loop → 75% metacognition
- 1.7B: Ignis decomposed the ejection circuit to 5 heads in L22-L23. 65K targeted params beat 5.5M blanket params (SR=0.417 vs 0.083). Self-corpus and loop closure pending.
- Forge pipeline operational: 1,748 concept combinations evaluated (Nous), 122 reasoning tools forged at 42% forge rate (Hephaestus), 51/100 adversarial grid cells filled (Nemesis). See [forge_pipeline.md](docs/forge_pipeline.md).
- Coeus dual causal graph: forge success vs adversarial robustness. Goodhart indicators identified (tools that pass static battery but fail under adversarial pressure).
- RLVF fitness function: F(T) = Σwᵢ·Sᵢ - λ·σ(S), weights by adversarial robustness
- Next: full RLVF loop closure (Rhea evolves against forged tool fitness)

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
| **Coeus** | Κοῖος — Titan of rational inquiry | Causal intelligence — dual causal graphs, Goodhart detection |
| **Nemesis** | Νέμεσις — goddess of retribution | Adversarial co-evolution — MAP-Elites grid, metamorphic testing |
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

- RTX 5060 Ti 16GB VRAM (all results obtained on this single consumer GPU)
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

### Forge Pipeline — Mine, forge, and stress-test reasoning tools
```bash
# One command launches Nous + Hephaestus + Nemesis (continuous, all three)
run_forge_pipeline.bat

# Or individually:
python agents/nous/src/nous.py --unlimited          # Mine concepts
python agents/hephaestus/src/hephaestus.py          # Forge tools (polls Nous)
python agents/nemesis/src/nemesis.py                 # Adversarial testing (polls forge/)
python agents/coeus/src/coeus.py                     # Rebuild causal graph (auto-triggered)
```

## The North Star

A model where the logit lens backward pass shows correct answer probability monotonically increasing through all layers. No L*. No ejection. Reasoning gravity.

The fire was always there. We just stopped it from being put out.
