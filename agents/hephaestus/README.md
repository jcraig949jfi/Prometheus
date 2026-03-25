# Hephaestus — The Automated Forge

Hephaestus takes concept combinations from **Nous** (scored theoretical
descriptions of novel idea intersections), enriched by **Coeus** (causal
intelligence), and hammers them into testable Python reasoning tools.
It validates the code and runs it against a 15-trap battery that must
beat the NCD compression baseline.

Runs **continuously by default** — polls Nous for new results every 5 minutes,
processes in Coeus-priority order, auto-triggers Coeus + report rebuilds every 50 forges.

## Pipeline

```
Nous runs → Load all → Ledger dedup → Coeus priority sort
  → Code gen (397B model, with Coeus enrichment + NCD floor + seed guidance)
  → Code extraction (code-first, decline signals secondary)
  → Gate 1: Syntax (ast.parse)
  → Gate 2: Imports (numpy + stdlib only)
  → Gate 3: Interface (class ReasoningTool with evaluate + confidence)
  → Gate 4: Runtime (instantiate, call with test data, verify format)
  → Gate 5: Trap battery (15 traps, must strictly beat NCD baseline)
  → forge/ or scrap/
  → Every 50 forges: auto-trigger Coeus rebuild + human-readable reports
  → Sleep 5min → Re-scan Nous → Repeat
```

## Usage

```bash
# Default: continuous, polls Nous every 5min, processes all, Coeus every 50
python agents/hephaestus/src/hephaestus.py

# One-shot mode (process current batch and exit)
python agents/hephaestus/src/hephaestus.py --runonce --top-n 20

# Custom intervals
python agents/hephaestus/src/hephaestus.py --poll-interval 120 --coeus-interval 25

# Point at specific Nous file
python agents/hephaestus/src/hephaestus.py --nous-run agents/nous/runs/20260324_214225/responses.jsonl --all
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--nous-run` | scan all runs | Path to specific Nous `responses.jsonl` |
| `--top-n` | 20 (runonce) | Take top N by Coeus forge priority |
| `--min-score` | — | Minimum composite score threshold |
| `--all` | auto (continuous) | Process all non-unproductive results |
| `--include-unscored` | — | Include entries with composite_score=0 |
| `--model` | `qwen/qwen3.5-397b-a17b` | Model for code generation |
| `--delay` | 3.0 | Seconds between API calls |
| `--resume` | — | Resume most recent run |
| `--runonce` | — | Process current batch and exit |
| `--poll-interval` | 300 | Seconds between Nous re-scans (continuous mode) |
| `--coeus-interval` | 50 | Auto-rebuild Coeus every N forges (0=disable) |
| `--reports-interval` | 50 | Auto-rebuild human-readable reports every N forges (0=disable) |

## Trap Battery (15 traps)

**Original 10:** Cognitive biases (bat-and-ball, gambler's fallacy, pound-of-gold),
mathematical logic (0.999...=1, pigeonhole), numeric comparison (9.11 vs 9.9).

**Compositional 5:** Transitivity (A > B > C), negation scope ("not all birds can fly"),
comparative reversal with stated premise, subject-object parsing, modus tollens.

**Baseline:** NCD (Normalized Compression Distance) — 20% accuracy, 7% calibration.
Tools must **strictly beat NCD** on accuracy or calibration without losing on either.

## Forged Tool Interface

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Returns [{"candidate": str, "score": float, "reasoning": str}, ...]"""

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns 0.0-1.0."""
```

## Code Generation Prompt

The 397B model receives:
- Nous theoretical analysis (what the combination means)
- Coeus prescriptive directives ("make Active Inference the core pattern", "restrict Topology to confidence() only")
- NCD quality floor ("your tool must beat 20% accuracy, 7% calibration")
- Seed tool guidance (structural parsing > hash similarity, numeric eval, NCD as tiebreaker only)

## Directory Structure

```
agents/hephaestus/
├── src/
│   ├── hephaestus.py          — Main engine (continuous forge loop)
│   ├── code_extractor.py      — Extract Python from LLM response (code-first)
│   ├── validator.py            — Syntax, imports, interface, runtime checks
│   ├── test_harness.py         — 15-trap battery + NCD baseline comparison
│   ├── prompts.py              — Code gen prompt with Coeus + NCD floor + seed guidance
│   ├── trap_generator.py       — Dynamic parameterized trap generation (8 categories)
│   ├── build_reports.py        — Human-readable markdown per combo
│   └── cleanup_once.py         — One-time re-score + ledger rebuild
├── forge/                      — Surviving tools (.py + .json sidecars)
│   ├── utils/                  — Utility wrappers (perturbation calibrator, criticality regularizer)
│   ├── ncd_baseline.py         — Quality floor baseline
│   ├── logical_consistency_checker.py — Symbolic constraint propagation
│   ├── execution_evaluator.py  — Computed numeric/logic verification
│   ├── ibai_v2.py              — Best tool: Active Inference + structural + NCD (67% acc)
│   ├── efme_v2.py              — Structural falsification (60% acc)
│   └── ...                     — Auto-forged tools
├── scrap/                      — Failed forges (.py + .json with failure reasons)
├── humanreadable/              — Consolidated markdown reports per combo
├── runs/                       — Timestamped output per run
├── ledger.jsonl                — Global dedup + outcomes + margin-over-NCD
└── README.md
```

## Environment

Requires `NVIDIA_API_KEY` environment variable.

## Dependencies

- `openai` (NVIDIA API compatibility)
- `numpy` (allowed in forged tools)
