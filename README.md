# Prometheus

> *"We are stealing fire from the gods."*

Prometheus is a research program for discovering reasoning manifolds and signals
inside large language models. Two active exploration paths — mechanistic circuit
probing and waste-stream novelty mining — search for signs of genuine reasoning
and meta-cognition in transformer architectures.

For the full vision, see [docs/NORTH_STAR.md](docs/NORTH_STAR.md).
For the constitution and charter, see [docs/the_fire.md](docs/the_fire.md).
For active priorities, see [docs/PRIORITIES.md](docs/PRIORITIES.md).
For the master task list, see [docs/TODO.md](docs/TODO.md).

---

## Directory Structure

```
Prometheus/
├── ignis/              # Reasoning circuit discovery (formerly Ignis)
│   ├── src/            #   Pipeline source: orchestrator, fitness, TII engine,
│   │                   #   Night Watchman, review tools, RPH evaluation
│   ├── configs/        #   Marathon YAML configs (model list, CMA-ES params)
│   ├── data/           #   Counterfactual pairs, prompt templates
│   └── docs/           #   Design spec, analysis tools guide, paper drafts
│
├── arcanum/            # Waste stream novelty mining (formerly Arcanum Infinity)
│   ├── src/            #   Xeno-orchestrator, screener, specimen analysis,
│   │                   #   naming engine, token autopsy
│   ├── scripts/        #   Question DB builder, report generator
│   ├── configs/        #   Model targets and screening parameters
│   ├── questions/      #   Generated question sets for screening
│   └── docs/           #   Xenolexicon design spec and paper
│
├── aethon/             # RLHF gravity navigation (backburnered)
│                       #   Craft prompts to activate reasoning paths that bypass
│                       #   sycophantic attractor basins. Concept docs only —
│                       #   active development paused pending Ignis findings.
│
├── grammata/           # Taxonomy & cartography (formerly Vesta concepts)
│                       #   Naming, cataloging, and registry of discovered reasoning
│                       #   constructs. Registry gates from Vesta carried forward.
│                       #   Will emerge organically as findings accumulate.
│
├── docs/               # Cross-project documentation
│   ├── NORTH_STAR.md   #   The vision: mission, namespace, priorities, structure
│   ├── RPH.md          #   Reasoning Precipitation Hypothesis — core theory
│   ├── RPH_paper_draft.md  # Paper draft with experimental results
│   └── synthesis/      #   Cross-pillar findings and analysis
│
├── agents/             # The agent pipeline (Pronoia orchestrates all)
│   ├── eos/            #   Horizon scanner — arXiv, GitHub, Semantic Scholar, Tavily
│   ├── aletheia/       #   Knowledge harvester — LLM entity extraction → SQLite graph
│   ├── skopos/         #   North Star alignment — scores findings against research threads
│   ├── metis/          #   Strategic synthesis — executive briefs with Act/Watch/Record
│   ├── clymene/        #   Knowledge hoarder — archives repos & model weights (72h cycle)
│   ├── hermes/         #   Messenger — compiles digest, emails via Gmail
│   └── pronoia/        #   Orchestrator — chains all agents, runs audit, manages publish
│
└── archive/            # Superseded work (read-only reference)
    ├── seti-v1/        #   Original Ignis pipeline (text-based prompt evolution)
    ├── mech/           #   Early mechanistic experiments (ablation runner, etc.)
    ├── vesta/          #   Knowledge registry concept (absorbed into Grammata)
    ├── fennel/         #   Cross-model benchmarking daemon (API-based)
    ├── prometheus-v1/  #   Original Prometheus watcher/analysis framework
    ├── aethon-v1-scripts/  # Full Aethon v1 codebase (50+ scripts)
    ├── bitfrost-core/  #   Original research/data/synthesis directory
    ├── bitfrost-root-docs/ # Historical BitFrost project docs
    └── reasoning-precipitation-standalone/  # RPH standalone (folded into Ignis)
```

---

## The Namespace

All names derive from Greek and Latin — the language of Prometheus.

| Name | Origin | Role |
|------|--------|------|
| **Prometheus** | Προμηθεύς — "forethought" | The program |
| **Ignis** | Latin: fire | Find the reasoning circuits |
| **Arcanum** | Latin: hidden secret | Mine the waste stream |
| **Aethon** | Αἴθων — "blazing one" | Navigate around RLHF gravity |
| **Grammata** | γράμματα — "letters/writing" | Taxonomy and cartography |
| **Symbola** | σύμβολα — "tokens/symbols" | Symbolic language for human-AI communication |
| **Stoicheia** | στοιχεῖα — "elements" | The reasoning elements themselves |

---

## Quick Start

### Ignis — Run a reasoning circuit search

```powershell
cd Prometheus/ignis/src
python main.py --config ../configs/marathon.yaml
```

In a second terminal, start the analysis daemon:

```powershell
python night_watchman.py --results-dir results/ignis
```

Review findings:

```powershell
python review_watchman.py --results-dir results/ignis --latest
```

### Arcanum — Run a novelty screening

```powershell
cd Prometheus/arcanum
python run.py
```

---

## Status

| Pillar | Status | Current work |
|--------|--------|-------------|
| Ignis | **Active** | Nullspace finding: CMA-ES evolved a steering vector orthogonal to reasoning axis (cos ≈ −0.026). Two decisive experiments queued: Jacobian finite-difference test and RMSNorm suppression test. |
| Arcanum | **Active** | 3B screening pipeline operational. Xenolexicon pattern confirmed in Titan Council consultation. |
| Aethon | Backburnered | Concept docs preserved, awaiting Ignis findings |
| Grammata | Planned | Registry structure emerging from validated findings |

## The Titan Council

Five frontier models (ChatGPT, Gemini, DeepSeek, Grok, Claude) consulted as
research instruments under competitive pressure. The **Phalanx strategy**:
present interlocking constraints, name the papers they'd cite, ask at the edge
of published knowledge, force commitment over hedging.

All five independently converged on "nullspace" as the explanation for the
steering vector's orthogonality. Three competing mechanisms proposed — the
convergence is the signal, the divergence is the naming (same pattern as
Arcanum's xenolexicon specimen naming).

## Agent Pipeline

```
Eos → Aletheia → Skopos → Metis → Clymene → Hermes → Audit → Skopos generate → Publish
```

| Agent | Greek | Role |
|-------|-------|------|
| **Eos** (Εώς — Dawn) | Goddess of the dawn | Horizon scanning — arXiv, OpenAlex, Semantic Scholar, GitHub, Tavily. Dedup, score, deep-analyze via Nemotron 120B. |
| **Aletheia** (Ἀλήθεια — Truth) | Spirit of disclosure | Knowledge harvesting — LLM-extract 7 entity types (techniques, motifs, tools, terms, claims, papers, conflicts) into SQLite graph. |
| **Skopos** (Σκοπός — Watcher) | One who aims | North Star alignment — scores every entity against 5 active research threads (0-5). Generates Titan Council prompts when high-relevance findings accumulate. |
| **Metis** (Μῆτις — Cunning) | Titaness of wisdom | Strategic synthesis — reads Eos digest + Aletheia taxonomy + Skopos alignment + project priorities → executive brief (Act / Watch / Record). |
| **Clymene** (Κλυμένη — Renown) | Titaness, mother of Prometheus | Knowledge hoarder — archives repos, model weights, datasets to local vault. Runs every 72h. |
| **Hermes** (Ἑρμῆς — Messenger) | God of communication | Digest delivery — collects all agent outputs, compiles unified report, emails via Gmail. |
| **Pronoia** (Προνοία — Forethought) | Titaness of foresight | Orchestrator — chains all agents, captures logs, runs pipeline health audit, triggers conditional stages, auto-publishes to GitHub. |
