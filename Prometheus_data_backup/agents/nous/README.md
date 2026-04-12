# Nous — Combinatorial Hypothesis Engine

*Greek: νοῦς — divine intellect*

Nous generates novel hypotheses by combining concepts from diverse fields. It samples
triples from a curated dictionary, queries a 397B model to evaluate each combination's
potential as a reasoning tool, scores the response, and ranks by implementability.

Runs **continuously** by default, generating batches indefinitely until stopped.

---

## The Question Nous Answers

> "What cross-domain concept collisions could produce a new computable reasoning criterion?"

Nous is deliberately promiscuous — it generates thousands of combinations knowing most
won't survive the forge. The goal is breadth of exploration, not precision. Out of 1,500+
evaluated combinations, roughly 20-30% score high enough to warrant forging.

---

## Architecture

```
Concept Dictionary (95 concepts × 18 fields)
  → Coeus-weighted sampling (bias toward forge-productive concepts)
  → Cross-field bias (80% of triples span 2+ fields)
  → NVIDIA API (397B model, implementation-focused prompt)
  → Scorer (4 dimensions + novelty + composite)
  → Rankings + JSONL output
  → Sleep → Next batch
```

---

## Concept Dictionary

95 concepts across 18 fields. Each concept has:

```python
{
    "name": "Active Inference",
    "field": "Theoretical Neuroscience",
    "description": "Framework for understanding perception and action as inference...",
    "mechanism_type": "dynamics"  # constraint | structure | dynamics | measure
}
```

**Mechanism types** enable higher-order causal discovery in Coeus:

| Type | What it represents | Examples |
|------|-------------------|----------|
| `constraint` | Hard rules, boundaries | Falsificationism, Criticality, Model Checking |
| `structure` | Form, arrangement | Topology, Category Theory, Compositional Semantics |
| `dynamics` | Evolution, adaptation | Active Inference, Ergodic Theory, Neural Plasticity |
| `measure` | Quantification | Maximum Entropy, Kolmogorov Complexity, Information Theory |

Coeus can discover principles like "successful forges need a constraint + a dynamics + a measure."

---

## Sampling

### Cross-field bias (80%)

80% of triples are constrained to span 2+ fields, forcing conceptual collisions.
80% forces genuine conceptual collisions while preserving 20% for within-field
combinations that may produce unexpected results. "Ergodic Theory × Falsificationism ×
Maximum Entropy" spans Mathematics, Philosophy, and Information Theory — this is where
novel mechanisms emerge.

### Coeus-weighted sampling

When `concept_scores.json` exists (written by Coeus), sampling weights are adjusted:

| Condition | Weight multiplier |
|-----------|------------------|
| `forge_effect > 0.3` | 3.0× (proven drivers) |
| `forge_effect < -0.2` | 0.3× (inhibitors, not eliminated) |
| Goodhart indicator (high forge, low adversarial) | 0.5× (demoted) |
| Undervalued (high adversarial, low forge priority) | 2.0× (boosted) |
| Default | 1.0× |

This means Active Inference (forge effect +0.69) gets sampled 3× more often than
Topology (forge effect -0.21), but Topology isn't eliminated — it may produce a
breakthrough when paired with the right concepts.

---

## Prompt Design

The prompt steers the 397B model toward **implementable algorithms**, not abstract theory:

1. **"What specific algorithm or data structure emerges?"** — not "What mechanism emerges?"
2. **"What structural features of text would this approach parse?"** — names specific operations
3. **Implementation guidance** — tells the model that structural parsing, constraint propagation,
   and numeric evaluation succeed in the forge; hash similarity and bag-of-words fail
4. **Explicit rating format** at end:
   ```
   RATINGS (respond with EXACTLY these lines):
   Reasoning: N/10
   Metacognition: N/10
   Hypothesis Generation: N/10
   Implementability: N/10
   ```
5. **Max tokens: 2048** — prevents truncation (original 800 caused 100% rating parse failures)

---

## Scoring

| Dimension | Weight in composite | Predictive of forge? |
|-----------|-------------------|---------------------|
| Reasoning | 1/3 | No (weight 0.000) |
| Metacognition | 1/3 | No (weight 0.000) |
| Hypothesis generation | 1/3 | No (weight 0.000) |
| **Implementability** | Separate | **Yes (weight +0.221)** |

The composite score averages reasoning + metacognition + hypothesis generation.
Implementability is scored separately because it's the only dimension Coeus found
to predict forge success. "HIGH POTENTIAL" requires all three core ratings >= 7.

Novelty is classified as: `novel`, `existing` (maps to known technique), or
`unproductive` (combination doesn't produce anything useful).

The scorer uses flexible regex patterns to handle the 397B model's formatting
variations (bold text, unicode dashes, varied spacing).

---

## Usage

```bash
# Continuous (default) — generates batches of 500 indefinitely
python agents/nous/src/nous.py --unlimited

# Single batch of 100
python agents/nous/src/nous.py --n-combos 100

# Resume interrupted run
python agents/nous/src/nous.py --resume

# Custom model
python agents/nous/src/nous.py --unlimited --model qwen/qwen3.5-397b-a17b

# Disable Coeus-weighted sampling
python agents/nous/src/nous.py --unlimited --no-coeus-weights
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--n-combos` | 500 | Combinations per batch |
| `--unlimited` | off | Run indefinitely (batch after batch) |
| `--model` | `nvidia/nemotron-3-super-120b-a12b` | NVIDIA API model |
| `--concept-file` | built-in dictionary | Custom concept JSON |
| `--resume` | off | Resume most recent run |
| `--delay` | 2.0 | Seconds between API calls |
| `--cross-field-bias` | 0.8 | Probability of 2+ fields per triple |
| `--seed` | random | Reproducibility seed |
| `--no-coeus-weights` | off | Disable Coeus sampling bias |

---

## Output

Each run creates `agents/nous/runs/{timestamp}/`:

| File | Format | Contents |
|------|--------|----------|
| `responses.jsonl` | JSONL (append-per-entry) | Full evaluated combinations with scores |
| `rankings.md` | Markdown | Top 50 by composite, full text for top 20 |
| `checkpoint.json` | JSON | Progress state for resumption |
| `meta.json` | JSON | Run configuration |

### Response JSONL schema

```json
{
  "concept_names": ["Active Inference", "Criticality", "Free Energy Principle"],
  "concept_fields": ["Theoretical Neuroscience", "Complex Systems", "Theoretical Neuroscience"],
  "concept_indices": [12, 45, 67],
  "response_text": "The combination produces a self-organizing...",
  "score": {
    "ratings": {
      "reasoning": 8,
      "metacognition": 7,
      "hypothesis_generation": 9,
      "implementability": 6
    },
    "composite_score": 8.0,
    "novelty": "novel",
    "high_potential": true,
    "is_unproductive": false
  },
  "timestamp": "2026-03-25T03:47:35.334177"
}
```

---

## Pipeline Position

```
NOUS (you are here)
  ↓ responses.jsonl
COEUS (causal analysis)
  ↓ enrichments + concept_scores.json
HEPHAESTUS (forge code)
  ↓ forged tools + ledger
NEMESIS (adversarial testing)
  ↓ adversarial_results.jsonl
COEUS (dual graph, Goodhart detection)
  ↓ updated concept_scores.json
NOUS (adjusted sampling weights) ← full cycle
```

---

## Concept Dictionary

See [concepts.py](src/concepts.py) for the full 95-concept dictionary with fields,
descriptions, and mechanism types.

## Dependencies

- `openai` (NVIDIA API compatibility)
- `pyyaml`
