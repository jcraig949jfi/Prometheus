# Hephaestus — The Automated Forge

*Greek god of the forge, fire, and craftsmanship*

Hephaestus takes concept combinations from **Nous** (scored theoretical descriptions of
novel idea intersections), enriched by **Coeus** (causal intelligence and prescriptive
directives), and hammers them into testable Python reasoning tools. It validates the code
through five gates and runs it against a 15-trap battery that must beat the NCD compression
baseline.

Runs **continuously by default** — polls Nous for new results every 5 minutes, processes
in Coeus-priority order, auto-triggers Coeus + report rebuilds every 50 forges.

---

## The Question Hephaestus Answers

> "Can this theoretical concept combination be reduced to working code that detects reasoning?"

Most combinations can't. The forge rate is ~40%, and that's after Coeus pre-filters.
The ones that survive are computable reasoning criteria — deterministic, fast, interpretable
algorithms that can score and rank candidate answers without any neural model.

---

## Architecture

```
Nous JSONL (all runs)
  → Load + deduplicate by combo key
  → Ledger filter (skip previously attempted)
  → Coeus priority sort (forge_effect + pair_synergy, not just composite score)
  → For each candidate:
      → Build code gen prompt (Nous analysis + Coeus directives + NCD floor + seed guidance)
      → NVIDIA API call (397B model generates Python code)
      → Code extraction (code-first, decline signals only if no code found)
      → Gate 1: Syntax (ast.parse)
      → Gate 2: Imports (numpy + stdlib only)
      → Gate 3: Interface (class ReasoningTool with evaluate + confidence)
      → Gate 4: Runtime (instantiate, call with test data, verify output format)
      → Gate 5: Trap battery (15 traps, must strictly beat NCD baseline)
      → forge/ (passed) or scrap/ (failed) + ledger append
  → Every 50 forges: auto-trigger Coeus rebuild + human-readable reports
  → Sleep 5min → Re-scan Nous → Repeat
```

---

## The Five Gates

### Gate 1: Syntax

`ast.parse(code)` — the code must be valid Python. Catches malformed output from the
model (unclosed brackets, invalid indentation, mixed Python/pseudocode).

### Gate 2: Imports

Only `numpy` and Python standard library are allowed. No `torch`, `sklearn`, `scipy`,
`transformers`, or any external dependencies. This ensures every forged tool is:
- Deterministic (no GPU variance)
- Fast (millisecond execution)
- Portable (runs anywhere)
- Auditable (no black-box components)

### Gate 3: Interface

The code must define `class ReasoningTool` with two methods:

```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Returns [{"candidate": str, "score": float, "reasoning": str}, ...]
        sorted descending by score."""

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns float in [0.0, 1.0]."""
```

### Gate 4: Runtime

The class is instantiated and called with dummy inputs:
- `evaluate("test prompt", ["A", "B"])` must return a list of dicts with correct keys
- `confidence("test prompt", "A")` must return a float in [0, 1]
- No crashes, no infinite loops (5-second timeout)

### Gate 5: Trap Battery

15 reasoning traps designed to catch tools that are just doing string matching:

**Original 10:** Numeric comparison (9.11 vs 9.9), cognitive biases (bat-and-ball,
gambler's fallacy, pound-of-gold), mathematical logic (0.999...=1, pigeonhole),
quantifier traps (all cats are animals), odd number sums.

**Compositional 5:** Transitivity chains (A > B > C → who's tallest?), negation scope
("not all birds can fly"), comparative reversal with stated premise, subject-object
parsing, modus tollens.

**Baseline:** NCD (Normalized Compression Distance) — 20% accuracy, 7% calibration.
Tools must **strictly beat NCD** on accuracy or calibration without losing on either
metric. This prevents tools that are just measuring string similarity under the hood.

---

## Coeus Priority Sorting

Instead of processing by Nous composite score, Hephaestus sorts by forge priority:

```
priority = composite_score + Σ(concept_forge_effects) + Σ(pair_synergies)
```

This pushes Active Inference + Criticality + Falsificationism combos to the front
(all strong forge drivers) and sinks Topology + Phenomenology combos to the back
(forge inhibitors), regardless of how elegant the theoretical analysis was.

When Coeus data isn't available, falls back to composite score.

---

## Code Generation Prompt

The 397B model receives a multi-section prompt:

1. **Nous theoretical analysis** — what the combination means, the response text
2. **Coeus prescriptive directives** — actionable implementation guidance:
   - Strong drivers: "Make [concept] the core architectural pattern of evaluate()"
   - Moderate: "Use [concept] as a secondary validation step"
   - Inhibitors: "Do NOT use [concept] for direct scoring; restrict to confidence() wrapper"
   - Confounder warnings: "Past success with [concept] is confounded — ensure deterministic implementation"
   - Interventional estimates: "Removing [concept] drops forge probability by X%"
3. **NCD quality floor** — "Your tool must beat 20% accuracy, 7% calibration"
4. **Seed tool guidance** — what works (structural parsing, negation detection, numeric
   evaluation, constraint propagation) and what fails (hash similarity, bag-of-words,
   echo detection)
5. **Interface contract** — exact class signature, 150-line limit, numpy + stdlib only

---

## Code Extraction

The extractor uses a **code-first** strategy:

1. Look for ````python ... ``` `` blocks — extract the first one containing `class`
2. If no code blocks, scan for `class ReasoningTool` in raw text
3. **Only after checking for code**: look for decline signals ("not implementable",
   "unproductive", "no meaningful implementation")
4. If the model hedged but still wrote code, keep the code

This fixed a critical bug where the original extractor scrapped 30% of responses
that contained usable code alongside caveats.

---

## The Ledger

`ledger.jsonl` is the global history of every forge attempt. Each line:

```json
{
  "key": "Active Inference + Criticality + Free Energy Principle",
  "concept_names": ["Active Inference", "Criticality", "Free Energy Principle"],
  "status": "forged",
  "reason": "",
  "accuracy": 0.53,
  "calibration": 0.47,
  "margin_accuracy": 0.33,
  "margin_calibration": 0.40,
  "timestamp": "2026-03-25T06:45:04.444258"
}
```

The ledger ensures:
- No combination is ever processed twice (even across runs)
- Coeus can build causal graphs from the full history
- Margin-over-NCD tracks quality improvement over time

---

## Forged Tool Library

Surviving tools fall into architectural families:

| Family | How it works | Best example |
|--------|-------------|--------------|
| **NCD-based** | `zlib.compress` measures structural similarity | `ncd_baseline.py` (quality floor) |
| **Active Inference / Free Energy** | Minimize expected free energy, balance exploitation + exploration | `ibai_v2.py` (67% acc) |
| **Falsification engines** | Parse logical structure, penalize contradictions | `efme_v2.py` (60% acc) |
| **Feature bandits** | UCB algorithms learn informative features within a batch | `bandit_v2.py` (40% acc) |
| **Execution evaluators** | Actually compute numeric answers, check arithmetic | `execution_evaluator.py` (47% acc) |
| **Structural parsers** | Regex-based extraction of negation, comparatives, conditionals | Various forged tools |

Reference points: NCD baseline (20% acc, 7% cal) is the quality floor.
Execution evaluator (47% acc) solves computation traps directly.

---

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

### CLI Flags

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
| `--poll-interval` | 300 | Seconds between Nous re-scans |
| `--coeus-interval` | 50 | Auto-rebuild Coeus every N forges (0=disable) |
| `--reports-interval` | 50 | Auto-rebuild reports every N forges (0=disable) |

---

## Directory Structure

```
agents/hephaestus/
├── src/
│   ├── hephaestus.py          — Main engine (continuous forge loop)
│   ├── code_extractor.py      — Extract Python from LLM response (code-first)
│   ├── validator.py           — Syntax, imports, interface, runtime checks
│   ├── test_harness.py        — 15-trap battery + NCD baseline comparison
│   ├── prompts.py             — Code gen prompt (Coeus + NCD floor + seed guidance)
│   ├── trap_generator.py      — Dynamic parameterized trap generation (8 categories)
│   ├── build_reports.py       — Human-readable markdown per combo
│   ├── cleanup_once.py        — One-time re-score + ledger rebuild
│   ├── rlvf_fitness.py        — RLVF fitness function for Rhea integration
│   └── reasoning_episode.py   — Standardized data schema with provenance gate
├── forge/                     — Surviving tools (.py + .json sidecars)
│   ├── utils/                 — Utility wrappers (perturbation, criticality)
│   ├── ncd_baseline.py        — Quality floor baseline
│   ├── logical_consistency_checker.py
│   ├── execution_evaluator.py
│   ├── ibai_v2.py             — Best tool: 67% accuracy
│   ├── efme_v2.py             — 60% accuracy
│   └── ...                    — ~120 auto-forged tools
├── scrap/                     — Failed forges with failure reasons
├── humanreadable/             — Consolidated markdown reports per combo
├── runs/                      — Timestamped run data
├── ledger.jsonl               — Global dedup + outcomes + NCD margins
└── README.md
```

---

## Auto-Triggers

Every 50 forges (configurable), Hephaestus automatically:

1. **Runs Coeus** — rebuilds the causal graph with fresh forge data, regenerates all
   enrichments, detects new Goodhart indicators from Nemesis data
2. **Rebuilds reports** — regenerates human-readable markdown in `humanreadable/`
   with current scores, NCD margins, Coeus enrichment, and code

---

## RLVF Fitness Function

`src/rlvf_fitness.py` bridges the forge pipeline to Rhea's evolution loop:

```
F(T) = Σ wᵢ · Sᵢ(T) - λ · σ(S)
```

- All forged tools score the reasoning trace T
- Weights wᵢ derived from Coeus adversarial robustness (tools that survive Nemesis
  get higher weight)
- λ = 2.0 variance penalty — when tools disagree on a trace, it's penalized (prevents
  gaming individual evaluators)
- Example: IBAI v2 (adversarial survival 46%) gets weight 0.46; a tool with survival
  85% gets weight 0.85. If they disagree on a trace, the variance penalty reduces fitness.
- Provenance gate enforces that adversarial data never enters training paths

---

## Pipeline Position

```
NOUS → [responses.jsonl] → HEPHAESTUS (you are here)
                              ↑ enrichments from COEUS
                              ↓ forged tools to forge/
                           NEMESIS tests tools adversarially
                              ↓ adversarial_results.jsonl
                           COEUS rebuilds dual causal graph
                              ↓ updated concept_scores.json
                           NOUS adjusts sampling → cycle repeats
```

---

## Environment

Requires `NVIDIA_API_KEY` environment variable.

## Dependencies

- `openai` (NVIDIA API compatibility)
- `numpy` (allowed in forged tools)
