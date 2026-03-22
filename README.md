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
├── ignis/              # Reasoning circuit discovery (formerly SETI v2)
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
├── agents/             # Automation (planned)
│                       #   GPU scheduler (keep both cards saturated 24/7)
│                       #   Horizon scanner (arxiv/paper monitoring)
│
└── archive/            # Superseded work (read-only reference)
    ├── seti-v1/        #   Original SETI pipeline (text-based prompt evolution)
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
| Ignis | **Active** | Qwen3-4B cross-architecture run; 0.5B/1.5B/3B Qwen2.5 complete (all NULL) |
| Arcanum | **Active** | 3B screening pipeline operational |
| Aethon | Backburnered | Concept docs preserved, awaiting Ignis findings |
| Grammata | Planned | Registry structure emerging from validated findings |
