# Hephaestus — The Automated Forge

*Greek god of the forge, fire, and craftsmanship*

Hephaestus takes concept combinations from **Nous** (scored theoretical descriptions of
novel idea intersections), enriched by **Coeus** (causal intelligence and prescriptive
directives), and hammers them into testable Python reasoning tools. It validates the code
through five gates, scores for novelty against the existing library, and runs it against
a 15-trap battery.

## Current State (2026-05-17)

- **Status:** RUNNING on M3 (GANDALF)
- **Mode:** Continuous, polls local Nous data every 5min
- **Model:** `qwen/qwen3.5-397b-a17b` via NVIDIA API
- **Ledger:** 5,309 entries (forged + scrapped)
- **Forge library:** ~1,960 tools across forge/ + forge_v2 through forge_v9
- **Queue:** ~1,342 unprocessed candidates from historical Nous runs
- **Telemetry:** Agora (Redis when available) + Postgres heartbeat (durable)
- **Forge rate (current run):** ~2% accuracy-gate + novelty-gate admissions

---

## The Question Hephaestus Answers

> "Can this theoretical concept combination be reduced to working code that reasons
> differently from compression?"

The key word is *differently*. The forge doesn't just want accuracy — it wants
**structural novelty**. A tool that scores 35% accuracy but uses Hebbian plasticity
inside a model-checking BFS is more valuable as substrate than a tool that scores 60%
using the same regex pipeline everyone converges on.

The forge produces **reasoning morphemes** — atomic computational strategies that a
future intelligence (or Apollo's evolutionary loop) can compose into more complex
reasoning organisms.

---

## Two Admission Gates

### Gate A: Accuracy (original)
Tool must strictly beat the NCD compression baseline on accuracy OR calibration.
Current NCD baseline: 42% accuracy, 46% calibration.

### Gate B: Novelty (added 2026-05-17)
Tool must have `min_ncd > 0.85` against the existing forge library AND `accuracy >= 20%`.
This admits tools that reason in structurally unique ways even if they don't beat
compression on accuracy. Rationale: substrate diversity > convergent accuracy.

A tool passes if it clears Gate A **OR** Gate B.

---

## Architecture

```
Nous JSONL (all runs)
  -> Load + deduplicate by combo key
  -> Ledger filter (skip previously attempted)
  -> Coeus priority sort (forge_effect + pair_synergy)
  -> For each candidate:
      -> Build code gen prompt (8 frames, weighted rotation)
      -> NVIDIA API call (qwen 397B)
      -> Code extraction (code-first strategy)
      -> Import injection (re, math, json, numpy, etc.)
      -> Common error fixes (confidence wrapper, missing methods)
      -> Gate 1: Syntax (ast.parse)
      -> Gate 2: Imports (numpy + stdlib + sympy + networkx + scipy only)
      -> Gate 3: Interface (class ReasoningTool with evaluate + confidence)
      -> Gate 4: Runtime (instantiate, call with test data, verify output)
      -> Gate 5: Trap battery (15 traps)
      -> If passed: compute novelty, forge
      -> If failed but novelty > 0.85: forge via novelty gate
      -> Otherwise: scrap/ + ledger
  -> Every 5 forges: STATUS.json + Postgres/Redis heartbeat
  -> Every 50 forges: auto-trigger Coeus rebuild + reports
  -> Sleep 5min -> Re-scan Nous -> Repeat
```

---

## The Five Validation Gates

### Gate 1: Syntax
`ast.parse(code)` — valid Python.

### Gate 2: Imports
Only `numpy`, `sympy`, `networkx`, `scipy`, `forge_primitives`, and Python stdlib allowed.
Ensures every tool is deterministic, fast, portable, auditable.

### Gate 3: Interface
```python
class ReasoningTool:
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # Returns [{"candidate": str, "score": float, "reasoning": str}, ...]
    def confidence(self, prompt: str, answer: str) -> float:
        # Returns float in [0.0, 1.0]
```

### Gate 4: Runtime
Instantiate + call with dummy data. No crashes, no infinite loops.

### Gate 5: Trap Battery
15 reasoning traps. Current NCD baseline: 42% accuracy, 46% calibration.
Tools must beat this OR pass the novelty gate.

---

## Novelty Scoring

Every forged tool gets a novelty score computed at forge time:

```json
{
  "novelty_min_ncd": 0.865,     // Distance to nearest neighbor (higher = more novel)
  "novelty_mean_ncd": 0.899,    // Average distance to all existing tools
  "novelty_nearest": "renormalization_x_genetic_algorithms.py",
  "novelty_library_size": 120
}
```

**Source-code NCD** measures structural divergence: how different is this tool's
computational approach from everything else in the library? NCD > 0.85 means genuinely
distinct architecture — not a variation on an existing theme.

**Why novelty matters for the North Star:**
The Prometheus reasoning ladder (R0-R9) requires diverse cognitive strategies at each
tier. A forge library where every tool uses regex-then-NCD is stuck at R0/R1. Tools
that implement Hebbian learning, evolutionary search, BFS state exploration, Kalman
filtering, or causal graph traversal are operating at R3-R5 — the tiers where genuine
structured reasoning happens. Novelty scoring is a proxy for "does this tool explore
a different region of the reasoning strategy space?"

---

## Scrap Repair Modes

### `--repair-scraps`
Scans the scrap pile (~1,475 tools with code on disk):
- Near-misses (worked but didn't beat NCD): computes novelty, forges if > 0.85
- Gate failures (syntax/import/interface): applies automated fixes, re-validates
- 10+ tools recovered from scrap pile in first pass (2026-05-17)

### `--repair-with-llm`
Uses the NVIDIA API to fix syntax/import/interface errors:
- Sends broken code + error message with "fix only, don't change logic" prompt
- Applies import injection + confidence wrapper after LLM fix
- Validates + trap battery + novelty gate
- ~128 candidates available; running in background

---

## Automated Post-Generation Fixers

Applied to every code output before validation:

1. **Import injection** — auto-adds missing `import re`, `math`, `json`, `itertools`,
   `functools`, `collections`, `zlib`, `random`, `copy`, `operator`, `numpy as np`, etc.
2. **Confidence wrapper** — monkey-patches `ReasoningTool.confidence` to guarantee
   float return in [0,1]. Catches None returns, out-of-range values, type errors.
3. **Missing confidence stub** — if class has `evaluate()` but no `confidence()`,
   injects a default that delegates to evaluate.

---

## Telemetry

### Agora (Redis — when M1 Redis is available)
- Heartbeat every 60s to `agent:Hephaestus` hash
- SHARE to `agora:discoveries` on successful forge
- ANNOUNCE to `agora:main` on API failure
- STATUS.json mirror to Redis on every checkpoint

### Postgres (durable — survives Redis outages)
- Heartbeat every 60s to `agora.agent_heartbeats`
- Full STATUS.json blob in `status_json` column
- M4's portfolio_monitor reads this in degraded mode

### Local
- `STATUS.json` written to `agents/hephaestus/STATUS.json` every 5 forges
- `hephaestus.log` — timestamped log of all operations

---

## Ledger Schema

`ledger.jsonl` — one line per forge attempt:

```json
{
  "key": "Active Inference + Criticality + Free Energy Principle",
  "concept_names": ["Active Inference", "Criticality", "Free Energy Principle"],
  "status": "forged",
  "reason": "",
  "accuracy": 0.53,
  "calibration": 0.47,
  "margin_accuracy": 0.11,
  "margin_calibration": 0.01,
  "frame": "D",
  "model": "qwen/qwen3.5-397b-a17b",
  "timestamp": "2026-05-17T06:45:04.444258"
}
```

---

## Usage

```bash
# Continuous mode (default)
python agents/hephaestus/src/hephaestus.py --poll-interval 300

# One-shot
python agents/hephaestus/src/hephaestus.py --runonce --top-n 20

# Repair scrap pile (novelty forging)
python agents/hephaestus/src/hephaestus.py --repair-scraps --repair-max 200 --repair-min-acc 0.20

# LLM-fix syntax errors in scraps
python agents/hephaestus/src/hephaestus.py --repair-with-llm --repair-max 128

# Resume interrupted run
python agents/hephaestus/src/hephaestus.py --resume
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--nous-run` | scan all runs | Path to specific Nous `responses.jsonl` |
| `--top-n` | 20 (runonce) | Take top N by Coeus forge priority |
| `--min-score` | -- | Minimum composite score threshold |
| `--all` | auto (continuous) | Process all non-unproductive results |
| `--model` | `qwen/qwen3.5-397b-a17b` | Model for code generation |
| `--delay` | 3.0 | Seconds between API calls |
| `--poll-interval` | 300 | Seconds between Nous re-scans |
| `--coeus-interval` | 50 | Auto-rebuild Coeus every N forges |
| `--reports-interval` | 50 | Auto-rebuild reports every N forges |
| `--repair-scraps` | -- | Run scrap repair pass (novelty + mechanical) |
| `--repair-with-llm` | -- | LLM-fix syntax errors in scraps |
| `--repair-max` | 50 | Max items in repair pass |
| `--repair-min-acc` | 0.25 | Min accuracy for near-miss inclusion |
| `--use-aggie-api` | -- | Enable Augment API fallback |
| `--force-aggie` | -- | Use Augment API exclusively |

---

## Forge Tool Families (observed)

| Family | Mechanism | Tier | Example NCD |
|--------|-----------|------|-------------|
| **Structural Parsers** | Regex extraction of logic, negation, comparatives | R1 | 0.75-0.82 |
| **Constraint Propagation** | Transitivity, modus ponens, SAT-style | R2 | 0.80-0.87 |
| **Active Inference / FEP** | Minimize prediction error, surprise | R3 | 0.83-0.90 |
| **Hebbian/Plastic** | Weights evolve during evaluation (EPMC) | R3-R4 | 0.86-0.93 |
| **Evolutionary/NAS** | Population search for scoring architecture | R4 | 0.88-0.92 |
| **Causal/Counterfactual** | DAG traversal, intervention reasoning | R5 | 0.85-0.90 |
| **Calibration/Meta** | Confidence capping, epistemic honesty | R6 | 0.82-0.88 |
| **Execution Evaluators** | Actually compute arithmetic answers | R2 | 0.85-0.90 |
| **Hybrid/Cross-domain** | Mix of 2+ approaches from different fields | R3+ | 0.88-0.95 |

Higher min_ncd = more structurally novel. The hybrid/cross-domain tools produced by
qwen's hallucination tendencies are often the most novel — genuinely weird combinations
that wouldn't occur to a more "careful" model.

---

## Connection to the Reasoning Ladder

The forge produces artifacts at different tiers of the reasoning ladder (R0-R9):

- **R0-R1 tools** — pattern matching, token overlap, NCD variants. Low novelty.
- **R2 tools** — multi-step deduction, constraint chaining. Moderate novelty.
- **R3-R4 tools** — rule discovery, search, backtracking, state exploration. High novelty.
- **R5+ tools** — causal reasoning, counterfactual sensitivity. Rare but extremely valuable.

**The novelty gate's role:** It preferentially admits R3+ tools that may score lower on
R1-R2 tests (the current trap battery is dominated by R1-R2 problems) but implement
computational mechanisms that are architecturally richer. This is intentional — the
substrate needs diverse reasoning primitives at every tier, not just accurate R1 tools.

**Open question:** Should the trap battery itself be tier-stratified? A tool that
implements genuine R4 search might score poorly on R1 rule-execution traps but excel
on R4-shaped problems (planning, constraint satisfaction, dead-end recovery). The
current battery doesn't test for this. See `pivot/reasoning_ladder_design_2026-05-15.md`
for the full tier specification.

---

## Pipeline Position

```
NOUS (M4) -> [responses.jsonl, local copy on M3]
                -> HEPHAESTUS (M3, you are here)
                     | enrichments from COEUS (dormant, degrades gracefully)
                     v
                forge/ (reasoning morphemes)
                     |
                     v
           APOLLO (M2, evolutionary composition of forge tools)
           NEMESIS (M3, adversarial testing of forge tools)
                     |
                     v
           Substrate -> future Learner training data
```

---

## Environment

Requires in `agents/hephaestus/.env`:
```
NVIDIA_API_KEY=nvapi-...
NVIDIA_API_ENDPOINT=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-3-super-120b-a12b
```

Plus env vars (set at User level on M3):
```
AGORA_REDIS_HOST=192.168.1.176
AGORA_REDIS_PASSWORD=prometheus
AGORA_POSTGRES_HOST=192.168.1.176
AGORA_POSTGRES_PASSWORD=prometheus
PROMETHEUS_MACHINE=M3
```

## Dependencies

- `openai` (NVIDIA API compatibility)
- `numpy` (allowed in forged tools)
- `redis` (Agora telemetry)
- `psycopg2-binary` (Postgres heartbeat)
