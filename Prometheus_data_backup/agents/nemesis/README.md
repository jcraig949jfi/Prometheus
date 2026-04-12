# Nemesis — Adversarial Co-Evolution Engine

*Goddess of retribution. Ensures no evaluator escapes deserved consequences.*

> **"Are our evaluators measuring reasoning, or have they learned to pass tests?"**

Nemesis is the adversarial pressure layer of the Prometheus forge pipeline. She generates
adversarial tasks using formal metamorphic relations, organizes them in a MAP-Elites
quality-diversity grid, finds minimal failing cases via iterative shrinking, tracks
adversarial lineages across generations, and feeds failure data back to Coeus for
Goodhart detection.

**Pure algorithmic.** No API calls. No neural models. No external services. Runs on
numpy and the standard library. Executes a full cycle in 2-3 seconds.

---

## The Three Questions Nemesis Answers

1. **What breaks?** — Which tools fail under adversarial mutation, and on what categories
   of reasoning? The MAP-Elites grid maps the full failure boundary.

2. **What's invisible?** — What reasoning patterns does NO tool in the library catch?
   These blind spots become targeted forge requests for Hephaestus.

3. **Are we Goodharting?** — Are tools overfitting to the trap distribution rather than
   measuring reasoning? If IBAI v2 scores 67% on static traps but 46% under adversarial
   pressure, that 21-point gap is the Goodhart signal.

---

## First Results

| Tool | Static Accuracy | Adversarial Survival | Goodhart Gap |
|------|----------------|---------------------|--------------|
| ibai_v2 | 67% | 46% | -21% |
| efme_v2 | 60% | 51% | -9% |
| info_theory_x_criticality_x_pragmatics | 47% | 85% | **+38%** |

The third tool is the surprise: modest static performance but exceptional adversarial
robustness. **Static performance and adversarial robustness measure different things.**
That's the most important signal in the pipeline — it reveals which tools are genuinely
measuring reasoning versus which ones learned to pass the static battery. Coeus now
maintains dual causal graphs to exploit this divergence.

---

## Architecture

### The Seven-Step Cycle

```
1. GENERATE  — Compose metamorphic relations on seed traps (random + targeted + boundary)
2. VALIDATE  — Verify ground truth, structural validity, execution cross-check
3. EVALUATE  — Run all forged tools against all new tasks
4. PLACE     — Insert into MAP-Elites grid (novelty check via NCD)
5. SHRINK    — Find minimal failing case for each failure
6. REPORT    — Write failure analysis, adversarial results, blind spots
7. SLEEP     — Reload tools (picks up newly forged), repeat in 2 minutes
```

Each cycle generates ~80-100 candidate tasks, validates ~60-70, places 2-5 in the grid
(novelty filter is aggressive), shrinks all failures, and completes in 2-3 seconds.

### Continuous Operation

Nemesis runs indefinitely by default. Each cycle:
- Reloads all tools from `../hephaestus/forge/` (picks up newly forged tools automatically)
- Generates fresh adversarial tasks (never repeats — grid novelty prevents it)
- Updates the per-tool difficulty model based on observed pass/fail rates
- Writes updated adversarial results for Coeus to ingest

---

## MAP-Elites Grid

MAP-Elites (Multi-dimensional Archive of Phenotypic Elites) is a quality-diversity
algorithm from evolutionary robotics. Instead of finding one "best" adversarial task,
it maintains a grid of diverse tasks that cover the entire behavioral boundary.

### Grid Dimensions

| Axis | Range | What it measures |
|------|-------|-----------------|
| **X: Logical Complexity** | 1-10 | Number of reasoning steps, chain depth, premise count |
| **Y: Linguistic Obfuscation** | 1-10 | Surface-level difficulty: passive voice, distractors, paraphrase |

### Cell Contents

Each of the 100 cells holds the single task that **maximizes tool disagreement** for
that (complexity, obfuscation) coordinate. Disagreement is measured by the variance of
tool scores — a task where half the tools get it right and half fail is more informative
than one where all tools agree.

```
          Linguistic Obfuscation →
     1  2  3  4  5  6  7  8  9  10
  1 [·][X][X][X][X][·][·][·][·][X]    X = filled cell
  2 [·][·][·][·][X][·][X][X][·][·]    · = empty (target for generation)
  3 [X][·][·][·][X][X][·][·][·][·]
  4 [·][X][·][X][·][·][·][·][·][·]
  5 [·][·][X][·][·][·][·][·][·][·]
  6-10: sparse (needs more chain_extend compositions)

Empty cells (·) represent reasoning regions where no high-disagreement task has been
found yet — these are active targets for targeted generation (Strategy 2).
```

### Grid Persistence

The grid is serialized to `grid/grid.json` after every cycle. On restart, Nemesis
loads the existing grid and continues filling empty cells. The grid is never reset —
it accumulates the best adversarial task for each region over time.

### Novelty Check

Before placing a task in the grid, Nemesis checks its NCD (Normalized Compression
Distance) against existing tasks in the same cell and adjacent cells. Tasks that are
too similar to existing ones (NCD < 0.15) are rejected. This prevents the grid from
filling with trivial variations of the same task.

---

## Metamorphic Relations (12 Core MRs)

Metamorphic testing is a formal framework from software engineering. Instead of checking
"is the output correct?" (which requires knowing the answer), it checks "do inputs and
outputs co-vary correctly?" Each MR specifies a transformation and the expected
relationship between the original and transformed outputs.

### The 12 Relations

| # | MR | Transform | Expected | Complexity Δ | Obfuscation Δ | Category |
|---|-----|-----------|----------|:---:|:---:|----------|
| 1 | `comparison_flip` | Swap A and B in "Is A > B?" | **flip** | 0 | 0 | comparison |
| 2 | `verb_inversion` | "larger" → "smaller" | **flip** | 0 | +1 | comparison |
| 3 | `negation_inject` | Add "not" to change truth value | **flip** | +1 | +1 | negation |
| 4 | `premise_shuffle` | Reorder premises randomly | **same** | 0 | +2 | structural |
| 5 | `distractor_add` | Add irrelevant detail sentence | **same** | 0 | +3 | structural |
| 6 | `passive_voice` | Active → passive construction | **same** | 0 | +3 | semantic |
| 7 | `paraphrase` | Rewrite preserving meaning entirely | **same** | 0 | +5 | semantic |
| 8 | `chain_extend` | Add elements to transitivity chain | **same** | +2 | 0 | complexity |
| 9 | `conditional_weaken` | "if P then Q" → "if P then maybe Q" | **computed** | +2 | +1 | logic |
| 10 | `affirm_consequent` | Tempt with invalid inference | **computed** | +3 | +1 | logic |
| 11 | `numeric_distractor` | Add misleading numeric fact | **same** | +1 | +4 | numeric |
| 12 | `scale_transform` | Multiply all numbers by constant K | **same** | 0 | +2 | numeric |

### Expected behavior types

- **flip**: The correct answer should reverse (Yes → No, A → B)
- **same**: The correct answer should be unchanged
- **computed**: The new correct answer depends on the specific mutation (Nemesis computes it)

### Composition

MRs compose to reach any point in the grid. Example:

```
paraphrase ∘ chain_extend ∘ distractor_add
```

This produces a task deep in the hard corner: high complexity (chain_extend adds
reasoning steps) AND high obfuscation (paraphrase rewrites surface form, distractor
adds noise). The final grid coordinates are:

```
complexity  = base + chain_extend.Δ = 1 + 2 = 3
obfuscation = base + distractor.Δ + paraphrase.Δ = 1 + 3 + 5 = 9
```

### Targeted Composition

When generating tasks for empty grid cells, Nemesis uses `targeted_mr_chain()` to
find MR sequences whose cumulative deltas land on the target coordinates. This is a
heuristic search (up to 20 random chains, keep the closest), not exhaustive.

---

## Task Generation (Three Strategies)

### 1. Random Generation (50 per cycle)

Apply random MR chains (length 1-4) to random seed traps. Explores the grid broadly.
This is the "exploration" arm — high variance, low precision.

### 2. Targeted Generation (30 per cycle)

Identify empty cells in the grid. Generate MR chains that target those specific
(complexity, obfuscation) coordinates. This is the "exploitation" arm — fills gaps
in coverage.

### 3. Boundary Generation (20 per cycle)

For each tool, generate tasks at its **decision boundary** — the complexity/obfuscation
region where it transitions from passing to failing. Uses the per-tool difficulty model
to identify weak spots. This is the "adversarial" arm — applies pressure where tools
are most vulnerable.

---

## Task Validation

Before evaluation, every generated task passes through validation:

1. **Structural validity** — prompt is non-empty, candidates are a list of 2+, correct
   answer is in the candidate list
2. **Ground truth check** — for numeric/logical tasks, run the execution evaluator to
   verify the stated correct answer is actually correct
3. **Determinism** — the same task evaluated twice must produce the same ground truth
4. **Ambiguity filter** — tasks where the execution evaluator disagrees with the stated
   ground truth are rejected (the mutation may have produced an ambiguous question)

Typically 70-85% of generated tasks pass validation. The rest are discarded.

---

## Shrinking (Minimal Failing Cases)

When a task breaks a tool, Nemesis finds the **simplest version that still breaks it**.
This is far more informative for Coeus than the full complex task.

### Simplification Strategies (7)

| Strategy | What it removes | Example |
|----------|----------------|---------|
| `remove_parentheticals` | Parenthetical asides | "Alice (who is 30) is..." → "Alice is..." |
| `remove_distractors` | "Note that..." sentences | Strip irrelevant facts |
| `remove_adjective_clauses` | Relative clauses | "Bob, who is a teacher," → "Bob" |
| `remove_appositives` | Appositive phrases | "Paris, the capital," → "Paris" |
| `shorten_chain` | Middle elements of transitivity | "A > B > C > D" → "A > C > D" |
| `reduce_candidates` | Extra wrong answers | Keep correct + 1 wrong only |
| `passive_to_active` | Passive voice | "was chased by" → "chased" |

### Algorithm

```
1. Given: failing task (prompt, candidates, correct) and tool_fn
2. For each round (max 5):
   a. Generate all applicable simplifications
   b. For each simplification:
      - Run tool_fn on simplified task
      - If tool still fails: accept simplification, log it, continue to next round
   c. If no simplification preserves the failure: stop (current task is minimal)
3. Return: minimal task + list of simplifications applied
```

The output is the shortest, simplest adversarial task that still breaks the tool.
"Tool fails on a 3-element transitivity chain where premises are reversed" is
actionable; "Tool fails on a 50-word paragraph with 8 elements and 3 distractors" is not.

---

## Adversarial Lineage Tracking

When a mutation breaks Tool A, Nemesis tries to mutate it further to break Tool B.
If that works, it tries Tool C. A lineage that breaks multiple tools from different
architectural families is probing a **fundamental weakness**, not a surface quirk.

### Lineage Schema

```json
{
  "lineage_id": "abc123",
  "depth": 3,
  "chain": [
    {"tool": "ibai_v2", "mr": "paraphrase", "minimal_task": "..."},
    {"tool": "efme_v2", "mr": "negation_inject", "minimal_task": "..."},
    {"tool": "bandit_v2", "mr": "chain_extend", "minimal_task": "..."}
  ]
}
```

Lineages with depth > 2 are flagged in reports and prioritized in the adversarial set.
They represent blind spots that the entire tool library shares.

---

## Per-Tool Difficulty Model

Nemesis maintains a learned difficulty estimate for each tool, updated every cycle
based on observed pass/fail rates across grid regions.

```json
{
  "ibai_v2": {
    "weak_region": {"complexity": [3, 5], "obfuscation": [7, 10]},
    "survival_rate": 0.46,
    "weakest_mr": "paraphrase",
    "boundary_complexity": 4.2
  }
}
```

This is used by boundary generation (Strategy 3) to focus adversarial pressure exactly
at each tool's decision boundary rather than wasting cycles on regions where the tool
either always passes or always fails.

---

## Feedback Loops

### → Coeus (adversarial survival data)

`adversarial/adversarial_results.jsonl` contains per-task, per-tool results:

```json
{
  "task_id": "grid_3_7",
  "prompt": "...",
  "candidates": ["A", "B"],
  "correct": "A",
  "complexity": 3,
  "obfuscation": 7,
  "mr_chain": ["paraphrase", "chain_extend"],
  "tool_results": {
    "ibai_v2": {"correct": false, "score_correct": 0.31, "score_wrong": 0.69},
    "efme_v2": {"correct": true, "score_correct": 0.62, "score_wrong": 0.38}
  },
  "disagreement": 0.87,
  "provenance": "adversarial"
}
```

Coeus builds a **dual causal graph**: one for forge success, one for adversarial robustness.
The divergence between graphs identifies Goodhart indicators — concepts that produce
tools that pass static tests but fail under adversarial pressure.

### → Hephaestus (blind spots → forge requests)

`adversarial/targeted_forge_requests.jsonl` maps grid blind spots to concept triple
suggestions. When Nemesis discovers a reasoning category where no tool succeeds, it
generates a request: "Need a tool that handles nested conditionals with passive voice."

### → Nous (via Coeus sampling weights)

Coeus demotes Goodhart-flagged concepts in sampling weights. Concepts that produce
high-forge-rate but low-adversarial-survival tools are treated as false positives.
Undervalued concepts (high adversarial survival, low forge priority) get boosted.

### → RLVF (fitness function weights)

`rlvf_fitness.py` weights each tool by its adversarial survival rate. Tools that survive
Nemesis pressure get higher weight in the evolutionary fitness function. The variance
penalty `λ·σ(S)` prevents models from gaming individual evaluators — if tools disagree
on a reasoning trace, the trace is penalized.

---

## Architectural Invariant: Provenance Tagging

**All Nemesis output is tagged `provenance: "adversarial"`.** This data NEVER enters
model training paths.

The `training_gate()` function in `reasoning_episode.py` raises `ValueError` if
adversarial episodes attempt to enter training. This is enforced in code, not just
documented as a principle.

**Why:** Rhea Batch 3 proved that mixing adversarial signal into training data costs
25 points on metacognition. Adversarial data teaches models to second-guess themselves,
which is the opposite of what self-corpus training achieves. Nemesis data is for
**evaluation and selection only** — never for learning.

---

## Usage

```bash
# Continuous (default — reloads tools each cycle, 2min intervals)
python agents/nemesis/src/nemesis.py

# Single cycle
python agents/nemesis/src/nemesis.py --runonce

# More tasks per cycle
python agents/nemesis/src/nemesis.py --n-random 100 --n-targeted 50

# Faster cycles
python agents/nemesis/src/nemesis.py --poll-interval 60

# Fixed seed for reproducibility
python agents/nemesis/src/nemesis.py --seed 42
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--runonce` | off | Run one cycle and exit |
| `--poll-interval` | 120 | Seconds between cycles |
| `--n-random` | 50 | Random adversarial tasks per cycle |
| `--n-targeted` | 30 | Targeted (empty-cell) tasks per cycle |
| `--seed` | random | Random seed for reproducibility |

---

## Directory Structure

```
agents/nemesis/
├── src/
│   ├── nemesis.py             — Main engine (continuous cycle loop)
│   ├── metamorphic.py         — 12 metamorphic relations + composition
│   ├── map_elites.py          — MAP-Elites grid (10×10) + task placement + novelty
│   ├── shrink.py              — Minimal failing case finder (7 strategies)
│   ├── evaluator.py           — Tool loader + evaluation runner
│   ├── validators.py          — Ground truth + structural validation
│   └── reporter.py            — Failure reports + JSONL output + forge requests
├── grid/
│   └── grid.json              — Serialized MAP-Elites grid + difficulty model
├── reports/
│   └── nemesis_report_*.md    — Per-cycle failure analysis
├── adversarial/
│   ├── adversarial_results.jsonl      — For Coeus (provenance-tagged)
│   └── targeted_forge_requests.jsonl  — For Hephaestus (blind spots)
├── configs/
│   └── manifest.yaml          — Agent configuration
└── README.md
```

---

## Pipeline Position

```
NOUS (concept mining)
  ↓
COEUS (causal analysis + enrichment)
  ↓
HEPHAESTUS (forge code + validate + test)
  ↓ forged tools
NEMESIS (you are here)
  ↓ adversarial_results.jsonl
COEUS (dual graph: forge success vs adversarial robustness)
  ↓ Goodhart indicators
NOUS (demote Goodhart concepts, boost undervalued)
  → cycle repeats
```

---

## Theory

Nemesis implements **adversarial co-evolution** — a Red Queen dynamic where evaluators
and adversaries must keep evolving to stay relevant. The system prevents three failure
modes:

1. **Goodhart collapse** — tools optimize for static trap patterns instead of reasoning.
   Nemesis applies continuous adversarial pressure so pattern-matching tools are identified
   and deprioritized.

2. **Evaluator overfitting** — tools that score well on 15 traps but poorly on novel
   variations. The MAP-Elites grid ensures 100 diverse adversarial tasks covering the
   full behavioral boundary, not just the battery.

3. **Blind spot accumulation** — reasoning categories that no tool handles. Nemesis
   detects these through tool unanimity (all tools fail on the same region) and feeds
   targeted forge requests to Hephaestus.

The theoretical grounding is in metamorphic testing (software engineering), MAP-Elites
(evolutionary robotics), and adversarial training (machine learning) — but critically,
the adversarial output is for **selection pressure only**, never for training.

---

## Dependencies

- `numpy` (NCD novelty check, grid operations)
- No API calls, no neural models, no external services
- Execution time: ~2-3 seconds per cycle
