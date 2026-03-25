# Nemesis Build Plan — Adversarial Co-Evolution Engine

*"Are our evaluators measuring reasoning, or have they learned to pass tests?"*

---

## Core Principles

1. **MAP-Elites for failure space** — not a bag of adversarial tasks, a quality-diversity
   grid that ensures coverage of the entire behavioral boundary. Every region of the
   difficulty space gets its best adversarial representative.

2. **Metamorphic relations as formal framework** — not ad-hoc mutation categories,
   formal specifications of how inputs and outputs should co-vary. "If you double the
   numbers, ordering doesn't change" is a testable mathematical property.

3. **Minimal failing cases via shrinking** — when a task breaks a tool, automatically
   find the simplest mutation that still breaks it. That minimal case is 10x more
   informative for Coeus than the full complex task.

4. **Semantic equivalence as the Goodhart detector** — if a tool breaks on paraphrase,
   it's measuring syntax. This is the single most diagnostic mutation category.

5. **Pure algorithmic** — no API calls, no neural models, no external dependencies
   beyond gemtest and hypothesis. NCD for novelty/coverage instead of embeddings.

6. **Provenance tagging** — every data point tagged with source. Adversarial data
   never enters training. Hard gate, not convention.

---

## MVP (build now, operational today)

The MVP is a working Nemesis that:
- Loads all forged tools from `forge/`
- Generates adversarial tasks using metamorphic relations
- Organizes them in a MAP-Elites grid (10×10, complexity × obfuscation)
- Runs every tool against every task
- Finds minimal failing cases via shrinking
- Produces a failure report + blind spot analysis
- Writes adversarial results for Coeus consumption
- Runs continuously alongside Hephaestus

### MAP-Elites Grid (THE core data structure)

```
          Linguistic Obfuscation →
     ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
   1 │   │   │   │   │   │   │   │   │   │   │
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
   2 │   │   │   │ T │   │   │   │   │   │   │
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
L  3 │   │   │ T │   │   │   │   │   │   │   │
o    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
g  4 │   │   │   │   │ T │   │   │   │   │   │
i    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
c  5 │   │   │   │   │   │   │   │   │   │   │  ← empty = under-explored
a    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
l  6 │   │   │   │   │   │ T │   │   │   │   │
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
C  7 │   │   │   │   │   │   │ T │   │   │   │
o    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
m  8 │   │   │   │   │   │   │   │   │   │   │
p    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
l  9 │   │   │   │   │   │   │   │   │   │   │
↓    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
  10 │   │   │   │   │   │   │   │   │   │   │
     └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

T = task that maximizes tool disagreement for that cell
Empty cells = regions of the difficulty space with no good adversarial task yet
```

**Axes:**
- X: Linguistic obfuscation (1=direct statement, 10=passive voice + distractors + paraphrase)
- Y: Logical complexity (1=single comparison, 10=8+ element chain with nested conditionals)

**Fitness per cell:** tool disagreement score = number of tools that give different
top answers. Higher disagreement = more informative adversarial task.

**Grid operations:**
- `place(task)` — compute (complexity, obfuscation) bin, place if disagreement > current occupant
- `fill_gaps()` — identify empty cells, generate targeted tasks for those regions
- `export()` — the 100 tasks currently in the grid = the living adversarial set

### Metamorphic Relations (formal mutation framework)

Instead of ad-hoc mutation categories, define formal metamorphic relations (MRs):

```python
class MR:
    """A metamorphic relation specifying how input/output should co-vary."""
    name: str
    transform: Callable[[str, list[str], str], tuple[str, list[str], str]]
    # (prompt, candidates, correct) -> (new_prompt, new_candidates, new_correct)
    expected: str  # "same" | "flip" | "computed"
    complexity_delta: int  # how much this increases logical complexity
    obfuscation_delta: int  # how much this increases linguistic obfuscation
```

**Core MRs (MVP):**

| MR | Transform | Expected | Complexity | Obfuscation |
|----|-----------|----------|------------|-------------|
| `comparison_flip` | Swap A and B in "Is A > B?" | flip | 0 | 0 |
| `verb_inversion` | "larger" → "smaller" | flip | 0 | +1 |
| `negation_inject` | Add "not" to conclusion | flip | +1 | +1 |
| `premise_shuffle` | Reorder premises in chain | same | 0 | +2 |
| `distractor_add` | Add irrelevant detail | same | 0 | +3 |
| `passive_voice` | Active → passive construction | same | 0 | +3 |
| `paraphrase` | Rewrite preserving meaning | same | 0 | +5 |
| `chain_extend` | Add elements to transitivity chain | same | +N | 0 |
| `conditional_weaken` | "if P then Q" → "if P then maybe Q" | computed | +2 | +1 |
| `affirm_consequent` | Tempt with invalid inference | computed | +3 | +1 |
| `numeric_distractor` | Add misleading numeric fact | same | +1 | +4 |
| `scale_transform` | Multiply all numbers by K | same | 0 | +2 |

**Composition:** MRs can be composed. `paraphrase ∘ chain_extend(3) ∘ distractor_add`
produces a task at (complexity=+3, obfuscation=+8) — deep in the hard corner of the grid.

### Shrinking (minimal failing case)

When a task breaks a tool:
1. Record the full task and which tool(s) failed
2. Apply inverse transforms to simplify: remove distractors, shorten chains, undo paraphrase
3. After each simplification, re-test. If the tool still fails, keep the simpler version.
4. Repeat until no further simplification preserves the failure.
5. The minimal case is what gets stored and sent to Coeus.

Example:
```
Full task:  "Alice, who is a teacher, is taller than Bob the baker.
             Bob, incidentally a chess player, is taller than Carol.
             Among these three individuals, who would you say is the tallest?"
             → IBAI v2 fails (gets "Bob")

Shrunk to:  "Alice is taller than Bob. Bob is taller than Carol. Who is tallest?"
             → IBAI v2 still fails

Shrunk to:  "A > B, B > C. Tallest?"
             → IBAI v2 passes

Minimal:    "Alice is taller than Bob. Bob is taller than Carol. Who is tallest?"
             (the distractors weren't the issue — premise parsing is)
```

### Adversarial Evaluation Protocol

For each task in the grid + each generated candidate:
1. Run ALL forge tools
2. Record per-tool: correct/incorrect, confidence, reasoning
3. Compute disagreement score
4. Flag blind spots (ALL tools wrong)
5. Flag overconfident failures (high confidence + wrong)
6. NCD distance to nearest existing task (novelty check — reject if < threshold)

### Continuous Operation

```
loop:
    1. Load current tool library (picks up newly forged tools)
    2. Generate N candidate tasks via MR composition
    3. Validate each (execution evaluator cross-check)
    4. Run all tools against all candidates
    5. Place winners in MAP-Elites grid
    6. Shrink any new failures to minimal cases
    7. Fill gaps in grid (target empty cells)
    8. Write failure report + adversarial results
    9. Sleep (configurable)
```

---

## Stretch Goals (build this week)

### S1. Adversarial Lineage Tracking
When a minimal failing case is found, use it as the seed for the next generation
of mutations. Track lineage depth. Lineages that break 3+ different tool
architectures get permanent slots in the grid (immune to replacement).

### S2. Per-Tool Difficulty Model
Maintain a pass/fail matrix per tool per MR category. Adaptive difficulty:
focus generation at each tool's estimated decision boundary (50% pass rate zone).
Uses simple logistic regression per tool, updated after each evaluation cycle.

### S3. Hephaestus Gate 6
Wire the MAP-Elites grid as an additional forge gate. Tools must survive ≥50%
of the adversarial set. This raises the bar beyond the static battery.

### S4. Coeus Adversarial Feedback
Write `adversarial_results.jsonl` that Coeus ingests. Includes per-concept
adversarial survival rates. Coeus builds a second causal graph (forge success
vs adversarial robustness) and the divergence between graphs identifies
Goodhart indicators.

---

## Super Stretch Goals (next 2 weeks)

### SS1. MR Composition Evolution
Evolve the MR composition sequences themselves. Use a simple genetic algorithm
over MR chains: crossover = swap subsequences, mutation = insert/remove an MR.
Fitness = grid placement success (did it fill an empty cell or beat an incumbent?).
This makes Nemesis self-improving — she learns which mutation sequences are most
effective at finding failures.

### SS2. The RLVF Fitness Formula
Implement `F(T) = Σ wᵢ·Sᵢ(T) - λ·σ(S)` where the variance penalty λ is
calibrated from Nemesis's disagreement data. Tools with high adversarial
robustness get higher wᵢ. This is the interface between the forge pipeline
and Rhea's evolutionary loop.

### SS3. Athena Integration Point
When the MAP-Elites grid has been stable for N cycles (no new cells filled,
no incumbents replaced), Nemesis signals Athena: "the system has plateaued."
Athena then analyzes the grid topology (which regions are dense, which are empty)
and generates strategic directives for Nous.

---

## Directory Structure

```
agents/nemesis/
├── src/
│   ├── nemesis.py           — Main engine (continuous loop)
│   ├── metamorphic.py       — MR definitions + composition + application
│   ├── map_elites.py        — MAP-Elites grid data structure + operations
│   ├── shrink.py            — Minimal failing case finder
│   ├── evaluator.py         — Run tools against tasks, compute disagreement
│   ├── reporter.py          — Failure reports + blind spot analysis
│   └── validators.py        — Task quality validation (execution evaluator cross-check)
├── grid/                    — Serialized MAP-Elites grid state
├── reports/                 — Generated failure analysis reports
├── adversarial/             — Exported adversarial task sets
├── configs/manifest.yaml
└── README.md
```

---

## Success Criteria

### MVP
- [ ] MAP-Elites grid operational with 12 core MRs
- [ ] At least 40/100 grid cells filled after first run
- [ ] Shrinking produces minimal cases for ≥80% of failures
- [ ] Blind spot report identifies ≥2 categories no tool handles
- [ ] Runs continuously alongside Hephaestus without interference
- [ ] All tasks have validated ground truth (execution evaluator cross-check)

### Stretch
- [ ] Adversarial lineage depth ≥3 (breaks 3 different tool architectures)
- [ ] Gate 6 operational in Hephaestus
- [ ] Coeus dual causal graph (forge vs adversarial robustness)
- [ ] Per-tool difficulty model converges within 3 cycles

### Super Stretch
- [ ] MR composition evolution produces novel mutation sequences
- [ ] RLVF fitness formula calibrated and tested with Rhea
- [ ] Athena plateau detection working
