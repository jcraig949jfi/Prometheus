# Nous — Combinatorial Hypothesis Engine

*Greek: νοῦς — divine intellect*

Nous generates novel hypotheses by combining concepts from diverse fields. It samples triples from a dictionary of 80-100 concepts, queries a large language model to evaluate each combination, scores the responses, and ranks them by potential.

## How it works

1. **Concept dictionary** — 80-100 concepts across mathematics, physics, CS, biology, cognitive science, signal processing, philosophy, and more
2. **Combination sampling** — Random triples biased toward cross-field combinations (at least 2 different fields per triple)
3. **LLM evaluation** — Each triple is sent to NVIDIA's free API (qwen/qwen3.5-397b-a17b) with a structured prompt asking for computational mechanisms, advantages, novelty, and ratings
4. **Scoring** — Responses are parsed for reasoning/metacognition/hypothesis-generation ratings, novelty assessment, and composite scores
5. **Ranking** — Top combinations by composite score, with HIGH POTENTIAL flags for triples where all ratings >= 7

## Setup

```bash
# Set your NVIDIA API key
export NVIDIA_API_KEY="nvapi-..."

# Install dependencies
pip install openai pyyaml
```

## Usage

```bash
# Run 100 combinations
python agents/nous/src/nous.py --n-combos 100

# Run 500 with a specific model
python agents/nous/src/nous.py --n-combos 500 --model qwen/qwen3.5-397b-a17b

# Resume an interrupted run
python agents/nous/src/nous.py --n-combos 500 --resume

# Use a custom concept file (JSON array of {name, field, short_description})
python agents/nous/src/nous.py --concept-file custom_concepts.json
```

## Output

Each run creates a timestamped directory under `agents/nous/runs/`:

- `responses.jsonl` — One JSON line per evaluated combination
- `rankings.md` — Top 50 combinations ranked by composite score, full text for top 20
- `checkpoint.json` — Progress state for resumption

## Scoring

- **Composite score**: Average of reasoning, metacognition, and hypothesis generation ratings (1-10)
- **HIGH POTENTIAL**: All three ratings >= 7
- **Novelty**: Classified as novel, existing, or unproductive based on response text analysis
