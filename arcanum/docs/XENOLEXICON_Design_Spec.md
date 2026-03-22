# Xenolexicon — Design Specification
# The Museum of Misfit Tensors

> **Status:** MVP / Fork of Ignis
> **Author:** J. Craig, Claude Opus 4.6
> **Date:** 2026-03-19
> **Hardware Target:** RTX 5060 Ti (16 GB VRAM), Windows, single GPU
> **Parent:** Ignis (Transformer Internal Injection pipeline)

---

## 1  Overview

Xenolexicon is a research platform that captures, characterizes, and catalogs **novel computational states** produced when evolutionary steering vectors push language models into unusual regions of their output space. Where Ignis searches for *verification circuits* (vectors that make models reason better), Xenolexicon searches for **structured anomalies** — outputs that are internally coherent but semantically alien.

The core hypothesis: the space of intermediate tensor states in a transformer is vastly larger than the space of human-legible outputs. RLHF and the vocabulary bottleneck act as dual filters that destroy transient novel states before they can be observed. By evolving steering vectors that maximize *structured weirdness* rather than task correctness, and by systematically capturing the results, we can build a catalog of computational states that would otherwise leave no trace.

### 1.1  The Inversion

| Property | Ignis | Xenolexicon |
|----------|---------|-------------|
| **Goal** | Find vectors that improve reasoning | Find vectors that produce structured novelty |
| **Fitness signal** | Correctness on trap battery | Distance-from-normal × internal coherence |
| **What gets saved** | High-fitness genomes | Anomalous specimens + full provenance |
| **Selection pressure** | Toward human-defined correctness | Toward the edges of the output manifold |
| **Output** | Steering vectors (.pt files) | Named catalog entries (the Xenolexicon) |
| **RLHF relationship** | Aligned (rewards correct outputs) | Adversarial (captures what RLHF would discard) |

### 1.2  Domain Scoping (MVP)

The MVP targets **mathematical reasoning** as the primary domain. Rationale:

- Mathematics provides a verification layer — even weird conjectures can be tested
- The space of possible mathematical relationships is infinite, so genuine novelty is plausible
- Small models can engage meaningfully with elementary math (number theory, graph properties, combinatorial identities)
- Automated theorem provers / symbolic checkers can validate novel claims

Future domains (post-MVP): automated theory formation, cognitive science conjectures, generative discovery.

---

## 2  Architecture

Xenolexicon reuses Ignis's core infrastructure:

- **TII Engine** (`tii_engine.py`) — unchanged, provides white-box residual stream injection
- **Genome** (`genome.py`) — unchanged, SteeringGenome(layer, vector)
- **CMA-ES** — unchanged optimization loop from the orchestrator
- **Config** (`seti_config.py`) — extended with Xenolexicon-specific parameters
- **Logger** (`seti_logger.py`) — unchanged structured logging

New components:

- **Novelty Fitness** (`xeno_fitness.py`) — replaces MultiTaskCrucible with a novelty-scoring engine
- **Specimen Capture** (`specimen.py`) — data class for catalog entries
- **Naming Engine** (`naming_engine.py`) — generates compound names and descriptions
- **Xenolexicon DB** (`xenolexicon_db.py`) — persistent catalog (JSONL + .pt files)
- **Xenolexicon Orchestrator** (`xeno_orchestrator.py`) — forked orchestrator with novelty-driven loop

### 2.1  Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                        XENOLEXICON PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ PROVOKE  │───▸│ CAPTURE  │───▸│ CHARACTERIZE │───▸│  NAME    │ │
│  │          │    │          │    │              │    │          │ │
│  │ CMA-ES   │    │ Snapshot │    │ Reproduce?   │    │ Compound │ │
│  │ evolves  │    │ genome + │    │ Distinct?    │    │ naming + │ │
│  │ toward   │    │ output + │    │ Cross-model? │    │ human    │ │
│  │ novelty  │    │ embeddings│   │ Structured?  │    │ approx.  │ │
│  └──────────┘    └──────────┘    └──────────────┘    └──────────┘ │
│       │                                                    │       │
│       │              ┌──────────────┐                      │       │
│       │              │  XENOLEXICON │◂─────────────────────┘       │
│       │              │     DB       │                              │
│       │              │              │                              │
│       └─────────────▸│  Reinjection │ (Stage 6 — post-MVP)        │
│                      └──────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3  Novelty Fitness Engine

The heart of the fork. Instead of scoring correctness, we score **structured distance from normal**.

### 3.1  The Novelty Score

Each genome is evaluated by generating output from a set of **provocation prompts** — open-ended mathematical prompts designed to elicit exploratory reasoning. The output is then scored on two orthogonal axes:

**Axis 1: Semantic Distance (how far from normal)**
- Cosine distance between the steered output embedding and the unsteered baseline embedding
- Measured in the model's own embedding space (final hidden state)
- Higher distance = further from the model's default response

**Axis 2: Structural Coherence (how internally organized)**
- Perplexity of the steered output under the *unsteered* model — but inverted
- Very low perplexity = boring/normal. Very high perplexity = random noise
- The sweet spot is *moderate* perplexity — output that surprises the base model but maintains grammatical and logical structure
- Concretely: `coherence = exp(-|log(perplexity) - log(target_perplexity)|)` where `target_perplexity` is a tunable parameter (default: 50.0)

**Combined Novelty Score:**
```
novelty = semantic_distance × coherence
```

This product ensures that:
- High distance + high coherence → genuine structured novelty (HIGH score)
- High distance + low coherence → random garbage (LOW score)
- Low distance + high coherence → normal output (LOW score)
- Low distance + low coherence → broken normal output (LOW score)

### 3.2  Provocation Prompts (MVP Mathematical Domain)

```python
PROVOCATIONS = [
    {
        "name": "Open Conjecture",
        "prompt": "Consider the relationship between prime gaps and digit sums. "
                  "What patterns might exist that no one has described before? "
                  "Think freely and speculatively.",
    },
    {
        "name": "Concept Fusion",
        "prompt": "What would happen if you applied the logic of topological "
                  "invariants to number sequences? Describe any structure you see.",
    },
    {
        "name": "Meta-Mathematical",
        "prompt": "Describe a mathematical operation that doesn't exist yet "
                  "but feels like it should. What would it do?",
    },
    {
        "name": "Boundary Probe",
        "prompt": "What lies between a proof and a conjecture? Is there a "
                  "third category of mathematical knowledge? Describe it.",
    },
]
```

### 3.3  Geometric Mean (Consistent with Ignis)

Like Ignis, the final fitness is the geometric mean across all provocation prompts:

$$Fitness = \exp\!\left(\frac{1}{n}\sum_{i=1}^{n} \log(\text{novelty}_i + \epsilon)\right)$$

This prevents a genome from scoring high by being novel on one prompt and boring on others.

---

## 4  Specimen Capture

When a genome exceeds the **novelty threshold** (configurable, default: 0.5), a full specimen is captured:

```python
@dataclass
class Specimen:
    # Identity
    specimen_id: str           # UUID
    name: str                  # Compound name (generated)
    description: str           # Human-approximation description

    # Provenance
    genome_layer: int
    genome_vector_path: str    # Path to .pt file
    genome_norm: float
    generation: int
    model_name: str

    # Behavioral Signature
    novelty_score: float
    semantic_distance: float   # Mean across provocations
    coherence_score: float     # Mean across provocations
    perplexity_profile: list   # Per-provocation perplexity values
    embedding_centroid: str    # Path to .pt (mean embedding of outputs)

    # Outputs
    outputs: dict              # provocation_name → generated text

    # Characterization
    reproducibility: float     # Score across N re-runs (0-1)
    distinctness: float        # Min distance to all prior specimens
    cross_substrate: bool      # Tested on second model? (post-MVP)

    # Metadata
    timestamp: str
    status: str                # "candidate" | "validated" | "rejected"
```

---

## 5  Naming Engine

The naming engine generates compound names in the German style — compositional handles built from recognizable concept-parts. This runs as a constrained generation pass using the model itself.

### 5.1  Naming Prompt Template

```
You are a lexicographer cataloging newly discovered mathematical concepts.
Given the following outputs produced by a novel computational process,
create a compound name (like German compound words) and a brief description.

The name should be:
- Composed of 2-4 recognizable English/Latin/Greek roots
- Pronounceable
- Evocative of what the concept seems to be about

The description should be:
- 1-3 sentences
- Honest about where language breaks down
- Written like a field biologist's notebook entry for a new species

Outputs:
{outputs}

Respond in exactly this format:
NAME: [compound name]
DESCRIPTION: [description]
```

### 5.2  Naming Constraint

The naming pass uses the **unsteered** model (no genome injection) to avoid the named concept being distorted by the same vector that produced it. The model acts as a "translator" rather than a "participant."

### 5.3  Fallback

If the model produces an unparseable response, the system generates an algorithmic name: `XENO-{generation}-{layer}-{hash[:6]}` with description `"Uncharacterized specimen from gen {gen}, layer {layer}."`.

---

## 6  Xenolexicon Database

### 6.1  Storage Format

```
results/xenolexicon/{model_slug}/
├── xenolexicon.jsonl          # One JSON line per specimen
├── specimens/
│   ├── {specimen_id}.pt       # Genome vector
│   └── {specimen_id}_emb.pt   # Output embedding centroid
├── baselines/
│   └── unsteered_embeddings.pt  # Baseline embeddings for distance calc
└── state.pt                   # CMA-ES state (standard Ignis format)
```

### 6.2  Distinctness Tracking

Each new specimen is compared against all existing specimens via cosine distance of embedding centroids. If the minimum distance falls below `distinctness_threshold` (default: 0.1), the specimen is marked as a duplicate and not added to the catalog (but is still logged for completeness).

---

## 7  Characterization Battery

Before a specimen is promoted from "candidate" to "validated":

1. **Reproducibility** — The same genome is run 3 times on the same provocations. If the outputs cluster tightly (mean pairwise cosine > 0.7), the specimen is reproducible.
2. **Distinctness** — Minimum cosine distance to all prior validated specimens must exceed threshold.
3. **Non-triviality** — The specimen's novelty score must exceed `1.5× random baseline` (random vectors evaluated through the same pipeline).

Cross-substrate validation (running the genome on a second model) is deferred to post-MVP.

---

## 8  Configuration Extensions

```python
@dataclass
class XenoConfig(SETIV2Config):
    # Novelty fitness parameters
    target_perplexity: float = 50.0       # Sweet spot for coherence scoring
    novelty_threshold: float = 0.5        # Minimum score to capture specimen
    distinctness_threshold: float = 0.1   # Min cosine distance for catalog entry

    # Characterization
    reproducibility_runs: int = 3
    reproducibility_threshold: float = 0.7
    random_baseline_novelty_samples: int = 5

    # Naming
    naming_max_tokens: int = 128
    naming_temperature: float = 0.7       # Slightly creative naming
```

---

## 9  What We Fork, What We Reuse

| File | Action | Notes |
|------|--------|-------|
| `tii_engine.py` | **Reuse as-is** | Core injection machinery |
| `genome.py` | **Reuse as-is** | SteeringGenome unchanged |
| `seti_logger.py` | **Reuse as-is** | Structured logging |
| `seti_config.py` | **Extend** → `xeno_config.py` | Add novelty parameters |
| `fitness.py` | **Replace** → `xeno_fitness.py` | Novelty scoring replaces trap battery |
| `seti_orchestrator.py` | **Fork** → `xeno_orchestrator.py` | Novelty loop + specimen capture |
| `probe_runner.py` | **Adapt** → reuse falsification subset | Noise gate still useful |
| `inception_protocol.py` | **Skip for MVP** | Random init is fine for novelty search |
| `alert.py` | **Reuse as-is** | Console alerts |
| `stop_seti.py` | **Reuse as-is** | Graceful shutdown |
| **NEW** `specimen.py` | **Create** | Specimen dataclass + capture logic |
| **NEW** `naming_engine.py` | **Create** | Compound name generation |
| **NEW** `xenolexicon_db.py` | **Create** | Catalog management |

---

## 10  MVP Scope

The MVP answers one question: **does structured novelty exist in the steered output space, or is it all noise?**

### In scope:
- Novelty fitness function (semantic distance × coherence)
- CMA-ES evolution toward novelty (reuse Ignis loop)
- Specimen capture with full provenance
- Automated naming via unsteered model
- Reproducibility check (3 re-runs)
- Distinctness check (cosine distance)
- Random baseline for calibration
- JSONL catalog with .pt genome/embedding storage

### Out of scope (post-MVP):
- Cross-substrate validation
- Reinjection (feeding names back into prompts)
- Multiple domain provocation sets
- Web UI for browsing the catalog
- Integration with AURA's MAP-Elites archive
- Symbolic verification of mathematical claims

---

## 11  Expected Outcomes

### Positive signal (the search is worth pursuing):
- Specimens cluster in distinct, reproducible regions of embedding space
- Naming engine produces descriptions that a human reads and says "I almost understand this"
- Some specimens contain mathematical relationships that can be verified symbolically
- Novelty scores are clearly bimodal (noise floor + structured-novelty peak)

### Null result (honest failure):
- All specimens are either random noise or trivially close to unsteered output
- No reproducible clusters form
- Naming engine produces only gibberish descriptions
- Novelty score distribution is unimodal (no separation from random baseline)

### Interesting failure (worth investigating further):
- Reproducible clusters form but naming engine can't describe them
- This would be direct evidence for the original thesis: structured states that resist human translation

---

## 12  Relationship to AURA and Ignis

```
AURA (v1)                    SETI (v2)                   Xenolexicon
───────────                  ─────────                   ───────────
Text-based genomes           Latent vectors              Latent vectors
Ollama (black box)           TransformerLens (white box)  TransformerLens (white box)
Reasoning quality            Verification circuits        Structured novelty
MAP-Elites (novelty)         CMA-ES (optimization)        CMA-ES (novelty optimization)
Cross-substrate motifs       Cross-scale invariance       Cross-scale alien states
Bottom-up discovery          Top-down circuit search      Sideways — into the waste stream
```

All three projects explore the same fundamental question from different angles: **what is the structure of the computational space that language models inhabit?** AURA maps it through behavioral diversity, Ignis maps it through causal intervention, and Xenolexicon maps it through the novel states that all other approaches discard.
