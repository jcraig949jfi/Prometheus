# Hephaestus — The Automated Forge

Hephaestus takes raw concept combinations from **Nous** (scored theoretical
descriptions of novel idea intersections) and hammers them into testable
Python code. It validates the code and runs it against a trap battery to
measure whether the concept actually improves reasoning.

## Pipeline

```
Nous JSONL → Filter top concepts → LLM code generation → Extract code
  → Validate (syntax, imports, interface, runtime) → Trap battery
  → forge/ (passed) or scrap/ (failed)
```

## Usage

```bash
# Forge top 20 Nous results by composite score
python agents/hephaestus/src/hephaestus.py \
  --nous-run agents/nous/runs/20260324_112138/responses.jsonl \
  --top-n 20

# Forge all results scoring >= 7.0
python agents/hephaestus/src/hephaestus.py \
  --nous-run agents/nous/runs/20260324_112138/responses.jsonl \
  --min-score 7.0

# Resume an interrupted run
python agents/hephaestus/src/hephaestus.py --resume \
  --nous-run agents/nous/runs/20260324_112138/responses.jsonl
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--nous-run` | required | Path to Nous `responses.jsonl` |
| `--top-n` | 20 | Take top N by composite score |
| `--min-score` | — | Minimum composite score threshold |
| `--model` | `qwen/qwen3.5-397b-a17b` | Model for code generation |
| `--delay` | 3.0 | Seconds between API calls |
| `--resume` | — | Resume most recent run |

## Output

- **forge/** — Validated, tested tools as importable `.py` files + `.json` metadata
- **scrap/** — Failed attempts with failure reasons (available for Arcanum recombination)
- **runs/{timestamp}/** — Per-run logs, checkpoints, rankings

## Forged Tool Interface

Every tool in `forge/` implements:

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # Returns [{"candidate": str, "score": float, "reasoning": str}, ...]

    def confidence(self, prompt: str, answer: str) -> float:
        # Returns 0.0-1.0
```

## Trap Battery

10 reasoning traps (cognitive biases, math tricks, logic puzzles).
Pass threshold: >60% accuracy AND >50% calibration.

This is a first filter — Ignis v2 does the real evaluation.

## Environment

Requires `NVIDIA_API_KEY` environment variable.

## Dependencies

- `openai` (for NVIDIA API compatibility)
- `numpy` (allowed in forged tools)
