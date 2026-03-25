# Nous — Combinatorial Hypothesis Engine

*Greek: νοῦς — divine intellect*

Nous generates novel hypotheses by combining concepts from diverse fields. It samples
triples from a dictionary of 89 concepts, queries a large language model to evaluate
each combination, scores the responses, and ranks them by potential.

Runs **continuously** (`--unlimited` mode), generating batches until stopped.

## How it works

1. **Concept dictionary** — 89 concepts across 18 fields (mathematics, physics, CS, biology,
   cognitive science, philosophy, neuroscience, economics, and more)
2. **Coeus + Nemesis weighted sampling** — Random triples biased toward cross-field
   combinations AND toward concepts with positive forge effects. Sampling weights factor
   in adversarial survival data from Nemesis: concepts flagged as Goodhart indicators
   (high forge, low adversarial) are demoted. Undervalued concepts (high adversarial,
   low forge priority) are boosted. Forge inhibitors are undersampled but not eliminated.
3. **LLM evaluation** — Each triple is sent to NVIDIA's API with an implementation-focused
   prompt asking for specific algorithms, data structures, structural features to parse, and
   ratings. The prompt steers toward implementable reasoning tools, not abstract theory.
4. **Scoring** — Responses are parsed for four dimensions:
   - **Reasoning** (1-10)
   - **Metacognition** (1-10)
   - **Hypothesis generation** (1-10)
   - **Implementability** (1-10) — the only dimension that predicts forge success
5. **Ranking** — Top combinations by composite score, HIGH POTENTIAL flags for all core ratings >= 7

## Setup

```bash
export NVIDIA_API_KEY="nvapi-..."
pip install openai pyyaml
```

## Usage

```bash
# Run continuously (default)
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

## Output

Each run creates a timestamped directory under `agents/nous/runs/`:

- `responses.jsonl` — One JSON line per evaluated combination (append-per-entry, crash-safe)
- `rankings.md` — Top 50 combinations ranked, full text for top 20
- `checkpoint.json` — Progress state for resumption
- `meta.json` — Run configuration

## Scoring

- **Composite score**: Average of reasoning, metacognition, and hypothesis generation ratings
- **HIGH POTENTIAL**: All three core ratings >= 7
- **Novelty**: Classified as novel, existing, or unproductive
- **Implementability**: Scored separately, not in composite, but is the strongest predictor of forge success

## Prompt Design

The prompt asks the 397B model to think like an engineer, not a theorist:
- "What specific algorithm emerges?" not "What mechanism emerges?"
- "What structural features of text would this parse?" not "What advantage would this give?"
- Explicitly mentions that structural parsing, constraint propagation, and numeric evaluation succeed; hash similarity and bag-of-words fail
- Enforces structured rating format at the end of each response for reliable parsing
- Max tokens: 2048 (prevents truncation of ratings)

## Dependencies

- `openai` (NVIDIA API compatibility)
- `pyyaml`
