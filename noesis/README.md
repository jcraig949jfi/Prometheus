# Noesis — Νόησις

*Higher-order knowing. Direct apprehension of mathematical truth, without the mediation of language.*

---

## What Noesis Is

Noesis is a continuously running tensor-based exploration engine that searches the space of all computable concepts at tensor speed. No neural network in the loop. No API calls in the loop. Pure mathematical operations — tensor contractions, decompositions, scoring — executing thousands of evaluations per second on consumer hardware.

It encodes mathematical and computational concepts as feature vectors, compresses the full interaction space using tensor train decomposition, and navigates the compressed structure to find which combinations of concepts produce emergent value. The LLM sits outside the loop, called occasionally to interpret what the loop discovered. The loop never waits.

## What It Proved on Day 1 (2026-03-28)

In its first 24 hours of existence, across 4 machines running in parallel:

| Result | Significance |
|--------|-------------|
| Operation tensor beats random by 37% vs 25% (execution) and 46% (quality) | The tensor shortcut provides real signal, not just speed |
| M2 broke the 0.659 quality ceiling → 0.7137 | Single-variable ablation: compression + input sensitivity are the discriminating signals |
| M3 amplified building blocks 293× (13 M1 discoveries → 3,814 M3 compositions) | Hierarchical composition works — discoveries transfer and compound |
| The topology→statistical mechanics corridor | A real mathematical relationship (topological phase transitions) found from tensor geometry alone |
| Cross-domain chains across 3,570 unique organism profiles | The tensor surfaces genuinely alien compositions no human would design |

## Why It Exists

The ejection circuit in transformer models suppresses correct answers during inference. At 0.5B it's fragile (10 traps flipped). At 1.5B it's robust (5 flips, 11 traps completely impenetrable). The corpus-first experiment proved the circuit is structural — 300 reasoning examples improve metacognition by 21.4% but the basin geometry doesn't change.

If the suppression mechanism strengthens with scale and can't be trained away, reasoning needs to live outside the neural network. Noesis is that alternative: transparent, compositional, dynamically updatable, and unconstrained by the ejection circuits baked into pretraining.

It started as a hedge. The data is suggesting it might be the plan.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  THE TENSOR (shared persistent substrate)           │
│  580+ operations × 30D features, TT-compressed      │
│  Navigable in microseconds per query                │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
    ┌──────────▼──────────┐  ┌───────▼────────────┐
    │  STRATEGIES (27)     │  │  SCORING (8 dims)  │
    │  Random baseline     │  │  Execution         │
    │  Tensor top-K        │  │  Novelty           │
    │  Mutation            │  │  Structure          │
    │  Temperature anneal  │  │  Diversity          │
    │  Frontier seeking    │  │  Compression        │
    │  Epsilon-greedy      │  │  Sensitivity        │
    │  Building-block reuse│  │  -Cheapness         │
    │  + 20 more           │  │  -Dead-end          │
    └──────────┬──────────┘  └───────┬────────────┘
               │                      │
    ┌──────────▼──────────────────────▼───────────┐
    │  TOURNAMENT (adaptive allocation)            │
    │  MAP-Elites grid (4×4×4 = 64 niches)        │
    │  Island migration + periodic reset           │
    │  Lineage tracking + building-block detection │
    │  Self-terminate on deadline or abort          │
    └─────────────────────────────────────────────┘
```

## How It Feeds the Larger System

Noesis is one engine within Project Prometheus. It feeds and is fed by every other subsystem:

- **Eos** scans for new algorithms → become organisms in the tensor
- **The Forge** produces reasoning tools → become Layer 3 organisms (metacognition)
- **Noesis** finds compositions → become forge targets and training data
- **Ignis** characterizes ejection circuits → informs what the tensor should search for
- **Rhea** trains models on reasoning data → corpus-first proved this works
- **Arcanum** mines waste streams → discovers concepts the tensor hasn't encoded yet

The density of the tensor IS the value of the substrate. Every organism added makes navigation smarter. Every composition tested makes the scoring function more accurate. Every building block extracted makes the next run deeper.

## Directory Structure

```
noesis/
├── README.md              ← You are here
├── building_blocks/       ← Validated operation pairs promoted to super-organisms
│   └── bb_*.py            ← 20 building blocks from M1's discoveries
├── cracks/                ← Crack logs from tournament runs
│   └── m1_cracks_*.jsonl  ← Real-time discoveries (one JSON per line)
├── prompts/               ← Machine-specific tournament prompts
│   └── noesis_m4_prompt.md
├── q_and_a/               ← Cross-machine coordination
│   └── m{2,3,4} questions/answers
└── the_maths/             ← Raw mathematical implementations for organisms
    └── PhilosophicalLogicalFormulizations/
    └── (50+ fields target — see collector prompt)
```

The daemon itself lives at `organisms/noesis_daemon.py`. The operation tensor at `organisms/operation_tensor.py`. The concept tensor at `organisms/concept_tensor.py`. These stay in `organisms/` because the daemon loads them at runtime.

## The Experimental Rig (2×2 Factorial)

|  | No Building Blocks | Building Blocks |
|--|-------------------|----------------|
| **Old Scoring** | M1: 0.659 ceiling | M3: 0.660 (293× amplification) |
| **Fixed Scoring** | M2: **0.7137** | M4: ??? (running) |

Four machines. Four experimental conditions. One controlled variable per machine. The interaction effect (M4) tells us whether scoring and building blocks multiply.

## Key Design Docs

| Document | What It Contains |
|----------|-----------------|
| `docs/continuous_exploration_loop.md` | Full Noesis architecture: 4 layers, framing, dream state |
| `docs/unified_theory_convergence.md` | Why this matters: dynamics not capacity, one finding from three directions |
| `docs/noesis_mega_prompt.md` | 27-strategy autonomous tournament specification |
| `docs/noesis_data_sources.md` | Density plan: OEIS, Rosetta Code, Lean mathlib, 500K+ target |
| `docs/noesis_ideas.md` | Backlog: trajectory scoring, ecological dynamics, reverse composition |
| `docs/noesis_math_collector_prompt.md` | Agent prompt for filling the_maths/ with 500+ operations |

## Named After

Νόησις (noesis) — in Plato's divided line, the highest form of knowledge. Not opinion (doxa), not belief (pistis), not mathematical reasoning (dianoia), but direct intellectual apprehension of the Forms themselves. The kind of knowing that doesn't need words.

A tensor that navigates mathematical structure without language is, in a small way, doing exactly that.

---

*Born: 2026-03-27 (theory). Validated: 2026-03-28 (data). Named by James and his chief scientist over a conversation about why language models can't think.*
