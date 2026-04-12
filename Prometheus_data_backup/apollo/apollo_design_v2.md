# Apollo v0.1 — Buildable Specification

---

## 1. Mission

### 1.1 The Forge: Where the Specimens Come From

The Prometheus project operates a four-agent pipeline — Nous, Coeus, Hephaestus, and Nemesis — that automatically discovers, implements, and validates pure-algorithmic reasoning tools. Nous samples cross-domain concept triples from a 95-concept dictionary spanning 18 fields (mathematics, physics, cognitive science, philosophy, neuroscience, and others) and feeds each triple to a 397B parameter model that produces a theoretical analysis of how the concepts could combine into a reasoning mechanism. Coeus, the causal intelligence layer, maintains a causal graph over the full history of concept combinations and forge outcomes, learning which concepts, fields, and score dimensions predict success. It injects prescriptive directives into the code generation prompt — not just "Criticality has positive forge effect" but "Make Criticality the core architectural pattern of the evaluate() method."

Hephaestus takes the highest-priority concept triples (ranked by Coeus's causal forge priority, not raw Nous scores) and attempts to forge them into working Python code. It sends each triple to the 397B model with a code generation prompt that includes the Nous theoretical analysis, Coeus's causal directives, and a strict interface contract: the output must be a deterministic Python class using only numpy and the standard library, under 150 lines, implementing `evaluate(prompt, candidates)` and `confidence(prompt, answer)` methods. The returned code passes through five validation gates — syntax (AST parse), imports (whitelist check), interface (required methods present), runtime (instantiate and call with test data), and a 15-trap reasoning battery where it must strictly beat an NCD (Normalized Compression Distance) baseline. Tools that survive all five gates are saved to the forge library. Tools that fail are scrapped with detailed failure metadata. The pipeline runs continuously, polling for new Nous output every five minutes, and has produced 146 validated reasoning tools at a 42% forge rate from 349 attempts.

The surviving tools are not toy programs. They encode genuine algorithmic reasoning strategies — free energy minimization for hypothesis scoring, chaos reservoir dynamics for trajectory stability monitoring, structural parsing with falsification logic for contradiction detection, compression-based information distance, multi-armed bandit exploration, and Bayesian constraint propagation. Each tool is a frozen specimen: a specific arrangement of parsing, scoring, transforming, and fallback operations that was selected for its ability to rank candidate answers to reasoning questions better than compression distance alone. Nemesis, the adversarial co-evolution agent, stress-tests the forge library with metamorphic mutations (comparison flips, negation injection, distractor insertion, paraphrase transforms, compositional depth scaling) organized in a MAP-Elites grid, identifying which tools measure genuine reasoning versus which have learned to pattern-match the trap battery.

These 146 specimens are Apollo's seed substrate.

### 1.2 What Apollo Does With Them

Build a closed-loop evolutionary system that takes the Prometheus forge library (146 computable reasoning tools) as seed genomes and evolves them — through mutation, recombination, selection, and novelty pressure — into increasingly sophisticated reasoning organisms.

The goal is not better evaluators. The goal is evolved reasoning agents with emergent metacognition. Self-referential wiring (organisms that check their own work) must be representable in the genome grammar from generation zero, and selection pressure must be the mechanism that determines whether self-reference is useful.

Apollo runs independently from the existing forge pipeline. It reads `agents/hephaestus/forge/*.py` as input substrate once at bootstrap. It never writes to any other agent's workspace.

---

## 2. Build Sequence

```
Step 1: Viability Spike .............. afternoon (determines mutation strategy)
Step 2: Phase 0 — CMA-ES ............ 2 days    (parameter evolution, validates fitness pipeline)
Step 3: Structural Evolution ......... 37 days   (the main evolutionary run)
```

**The viability spike result determines the mutation strategy:**

| Functional Viability | Strategy |
|---------------------|----------|
| >40% | AST-only, proceed as planned |
| 20-40% | AST-only, increase offspring to 100/gen |
| 10-20% | Warm start, mild mutations first 200 gens (splice 10%, point mutate 60%) |
| <10% | Add local StarCoder 1B as mutation operator (MVP requirement, not post-MVP) |

---

## 3. Architecture

```
agents/apollo/
├── src/
│   ├── apollo.py                 — Main evolutionary loop (entry point)
│   ├── gene_extractor.py         — Parse forge tools into method-level genes
│   ├── genome.py                 — Genome representation (genes + wiring graph + parameters)
│   ├── compiler.py               — Assemble genomes into executable ReasoningTool classes
│   ├── mutation.py               — 6 mutation operators + 1 compound operator
│   ├── crossover.py              — Topological-sort-based pipeline crossover
│   ├── fitness.py                — Margin-over-NCD accuracy + Brier calibration
│   ├── novelty.py                — Behavioral signature + k-nearest archive
│   ├── selection.py              — NSGA-II with 3 objectives + top-5 elitism
│   ├── sandbox.py                — RestrictedPython compile gate + multiprocessing runtime
│   ├── task_generator.py         — Extends Hephaestus trap_generator with difficulty scaling
│   ├── phase0.py                 — CMA-ES parameter evolution (pre-structural warmup)
│   ├── logger.py                 — Append-only JSONL lineage logging
│   └── checkpointer.py           — Pickle population snapshots every 50 generations
├── gene_library.json             — Extracted gene fragments (output of gene_extractor)
├── population/                   — Living population (.py source files)
├── archive/                      — Novelty archive (behaviorally unique organisms)
├── graveyard/                    — Dead organisms + cause-of-death metadata
├── lineage/
│   └── lineage.jsonl             — Full ancestry tracking (append-only)
├── checkpoints/                  — Population snapshots every 50 generations
├── phase0_results/               — CMA-ES parameter evolution output
├── configs/
│   └── manifest.yaml             — Apollo configuration
└── journal.md                    — Development log
```

---

## 4. Gene System

### 4.1 What a Gene Is

A gene is a **single method** extracted from a forge tool, classified by function, with its parameters rewritten for portability.

### 4.2 Gene Types

| Type | Convention Read Keys | Convention Write Key | Description |
|------|---------------------|---------------------|-------------|
| **PARSER** | `ctx['raw_text']`, `ctx['prompt']` | `ctx['parsed']` | Extracts structure from text (regex, tokenization, number extraction) |
| **SCORER** | `ctx['parsed']`, `ctx['raw_text']`, `ctx['score']` | `ctx['score']` | Produces a numeric score (free energy, coherence, divergence) |
| **FALLBACK** | `ctx['raw_text']`, `ctx['prompt']`, `ctx['candidate']` | `ctx['fallback_score']` | Baseline scoring (NCD, compression distance) |
| **UTILITY** | *(varies)* | *(varies)* | Helper functions (sigmoid, normalize, clamp). Not pipeline stages — travel with the gene that calls them. |

**UTILITY detection:** If a method is only called by other methods in the same class (never directly in `evaluate()` or `confidence()`), it's a UTILITY. During extraction, attach utilities as dependencies of the gene that references them.

### 4.3 Gene Classification Heuristics

Applied in order (first match wins):

1. Method name contains `ncd` or `compress` → **FALLBACK**
2. Method name starts with `_extract_`, `_parse_`, `_tokenize`, `_hash_` → **PARSER**
3. Method name is `evaluate` or `confidence` → **skip** (interface methods, not genes)
4. Method name is `__init__` → **extract parameters only** (not a gene)
5. Method is only called by other methods, never by evaluate/confidence → **UTILITY**
6. Return type annotation is `float`, or name contains `score`, `compute`, `check`, `run` → **SCORER**
7. Default → **SCORER**

### 4.4 Parameter Rewriting

During gene extraction, all `self.param_name` references are rewritten:

```python
# BEFORE (in forge tool)
def __init__(self):
    self.lambda_balance = 0.4
    self.threshold = 0.01

def _check_coherence(self, prompt, candidate):
    penalty = ... * self.lambda_balance
    if val < self.threshold: ...

# AFTER (extracted gene)
# Gene metadata: required_params = {'lambda_balance': 0.4, 'threshold': 0.01}
def _check_coherence(self, ctx):
    penalty = ... * self.params['gene_03_lambda_balance']
    if val < self.params['gene_03_threshold']: ...
```

- `self.param_name` → `self.params['gene_XX_param_name']` where XX is the gene ID
- Original parameter name preserved in gene metadata (for convergence analysis)
- Default values stored in gene metadata (used to initialize the genome's parameter vector)
- The parameter vector is a flat `dict[str, float]` — directly evolvable by point mutation or CMA-ES

### 4.5 Gene Extraction Process

```
For each forge tool .py file:
  1. ast.parse() the file
  2. Walk the AST, extract each method definition (ast.FunctionDef)
  3. Classify by heuristics (4.3)
  4. For __init__: extract parameter names + default values
  5. For UTILITY methods: identify which other methods call them (AST call analysis)
  6. For PARSER/SCORER/FALLBACK methods:
     a. Rewrite self.param_name → self.params['gene_XX_param_name']
     b. Rewrite method to operate on context dict (see 5.2)
     c. Attach dependent UTILITY methods
     d. Record: gene_id, gene_type, source_tool, code (AST), imports, required_params
  7. Output to gene_library.json
```

**Expected yield:** ~600-900 gene fragments from 146 tools (4-6 methods per tool, minus __init__ and interface methods).

---

## 5. Genome Representation

### 5.1 Genome Structure

```python
@dataclass
class Genome:
    genome_id: str                          # Unique ID (UUID)
    genes: list[Gene]                       # Ordered gene sequence
    wiring: dict[str, list[str]]            # Directed graph: gene_id → [downstream gene_ids]
    parameters: dict[str, float]            # Evolvable parameter vector (flat)
    cycle_cap: int                          # Max iterations for feedback loops (evolvable, range 1-5, default 3)
    lineage: dict                           # parent_ids, mutations_applied, generation
```

### 5.2 Context Dict — The Data Bus

All genes communicate through a shared context dict. Two-tier key convention:

```python
# Tier 1: Convention keys (what genes READ and WRITE)
ctx['prompt']       = prompt              # Set at initialization
ctx['candidate']    = candidate           # Set at initialization
ctx['raw_text']     = prompt + ' ' + candidate  # Set at initialization
ctx['parsed']       = ...                 # Written by PARSER genes
ctx['score']        = ...                 # Written by SCORER genes
ctx['fallback_score'] = ...              # Written by FALLBACK genes
ctx['_gene_trace']  = []                 # Injected by compiler, appended by each gene

# Tier 2: Gene-stamped keys (written AUTOMATICALLY by compiler after each gene)
ctx['gene_03_score']   = ...             # Preserved output of gene_03
ctx['gene_07_parsed']  = ...             # Preserved output of gene_07
```

**How it works:**
- Each gene reads from convention keys and writes to convention keys
- The compiler automatically injects a stamped write after each gene fires
- **Last-writer-wins** for convention keys — later genes overwrite earlier genes' outputs
- Stamped keys preserve every gene's output for debugging and trace analysis
- `ctx['_gene_trace']` records which gene wrote which convention key in what order

**Initial context (set before pipeline runs):**
```python
ctx = {
    'prompt': prompt,
    'candidate': candidate,
    'raw_text': prompt + ' ' + candidate,
    'parsed': None,
    'score': 0.0,
    'fallback_score': 0.0,
    '_gene_trace': []
}
```

### 5.3 Execution Model

**Per-candidate.** The pipeline is a scoring function for a single candidate. The compiled `evaluate()` method iterates over candidates, running the full pipeline for each one.

**Pipeline execution order:** Topological sort of the wiring graph, with cycle-breaking at the gene with the lowest gene_id in each cycle. Cycles execute up to `cycle_cap` iterations (evolvable parameter, range 1-5, default 3).

**Terminal output:** `ctx['score']` after all genes have fired. The last SCORER gene to write `ctx['score']` determines the candidate's score. If no SCORER fires successfully, score defaults to 0.0.

**Self-referential feedback:** When a SCORER reads `ctx['score']` (which a previous SCORER wrote) and writes `ctx['score']` (overwriting it), the convention key IS the feedback channel. In a cycle with iteration cap 3, the SCORER reads its own previous output and refines it 3 times. No special wiring machinery needed.

### 5.4 Error Handling

- **Gene crash on a task:** That task gets score 0.0 for that candidate. Pipeline continues for remaining candidates. Crash logged: `{gene_id, task_id, exception_type, one_line_traceback}`.
- **Per-candidate crash isolation:** If the pipeline crashes on candidate 3 of 5, candidates 1, 2, 4, 5 still get scores. Candidate 3 gets score 0.0.
- **Organism death:** Only through selection. An organism that crashes on all tasks gets fitness 0 across all objectives and dies in selection. An organism that crashes on some tasks has reduced fitness but can survive if its non-crash performance is strong enough.

---

## 6. Compiler

The compiler assembles a genome into an executable Python class that implements the ReasoningTool interface.

### 6.1 Compiled Class Structure

```python
import numpy as np
import zlib
import re
import math
from collections import defaultdict
# ... (imports from all genes' requirements, validated by RestrictedPython)

class ReasoningTool:
    def __init__(self):
        self.params = {
            'gene_01_lambda_balance': 0.4,
            'gene_01_threshold': 0.01,
            'gene_03_epsilon': 0.1,
            # ... (union of all genes' required parameters)
        }

    # --- Gene methods (extracted, parameter-rewritten) ---

    def _gene_01_extract_numbers(self, ctx):
        """PARSER gene from active_inference_x_epistemology_x_network_science"""
        # ... extracted code, self.param → self.params['gene_01_...']
        ctx['parsed'] = result
        ctx['gene_01_parsed'] = result          # auto-stamped by compiler
        ctx['_gene_trace'].append(('gene_01', 'parsed', result))

    def _gene_03_compute_coherence(self, ctx):
        """SCORER gene from chaos_theory_x_epistemology_x_mechanism_design"""
        # ... extracted code
        ctx['score'] = result
        ctx['gene_03_score'] = result           # auto-stamped by compiler
        ctx['_gene_trace'].append(('gene_03', 'score', result))

    # --- UTILITY methods (travel with their parent gene) ---

    def _gene_03_sigmoid(self, x):
        """UTILITY attached to gene_03"""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    # --- Pipeline execution ---

    def _run_pipeline(self, ctx):
        """Execute genes in topological order with cycle handling."""
        # Topo order: [gene_01, gene_03, gene_05, ...]
        # Cycle: gene_03 → gene_05 → gene_03 (cap: 3 iterations)
        self._gene_01_extract_numbers(ctx)
        for _iteration in range(self.params.get('_cycle_cap', 3)):
            self._gene_03_compute_coherence(ctx)
            self._gene_05_score_candidate(ctx)

    def evaluate(self, prompt, candidates):
        results = []
        for cand in candidates:
            ctx = {
                'prompt': prompt,
                'candidate': cand,
                'raw_text': prompt + ' ' + cand,
                'parsed': None,
                'score': 0.0,
                'fallback_score': 0.0,
                '_gene_trace': []
            }
            try:
                self._run_pipeline(ctx)
            except Exception:
                pass  # ctx['score'] remains 0.0
            results.append({
                'candidate': cand,
                'score': float(ctx.get('score', 0.0)),
                'reasoning': str(ctx.get('_gene_trace', []))
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        """Auto-generated: sigmoid of evaluate score."""
        result = self.evaluate(prompt, [answer])
        raw = result[0]['score'] if result else 0.0
        return float(1.0 / (1.0 + np.exp(-np.clip(raw, -10, 10))))
```

### 6.2 Compilation Validation

Before an organism enters the population:

1. **AST parse:** `ast.parse(source_code)` — valid Python syntax?
2. **RestrictedPython check:** Scan AST for disallowed imports (os, sys, subprocess, socket, io, pathlib, importlib, etc.)
3. **Interface check:** Class has `evaluate(self, prompt, candidates)` and `confidence(self, prompt, answer)` methods?
4. **Wiring validation:** Every gene's required input keys exist somewhere upstream in the wiring graph?
5. **Quick smoke test:** Run on 1 trap with 2-second timeout — produces a non-crashing result?

Organisms that fail any step die at compilation. Cause of death logged.

---

## 7. Mutation Operators

Six independent operators that can stack (multiple mutations per offspring):

| Operator | Rate | Description |
|----------|------|-------------|
| **Point Mutate** | 40% | Gaussian perturbation on parameter vector. `param += N(0, 0.1 * abs(param))`. Swap comparison operators. Modify regex character classes. |
| **Splice** | 25% | Insert a random gene from the gene library at a random position in the pipeline. Wire it between adjacent genes. |
| **Duplicate** | 15% | Copy a gene in the organism, insert the copy at a new position, point-mutate the copy's parameters. Enables self-checking patterns. |
| **Rewire** | 15% | Change one connection in the wiring graph. Can create skip connections, parallel paths, or feedback loops. |
| **Delete** | 10% | Remove a random gene from the pipeline. Rewire around it. Simplification pressure against bloat. |
| **Duplicate-and-Wire-Back** | 10% | **Compound operator.** Copy a gene AND wire the copy's input to the original's output. Explicitly produces self-referential topology. Selection decides if it's useful. |

**Mutation stacking:** Each operator is applied independently with its stated probability. An offspring can receive 0, 1, 2, or more mutations in a single generation.

**Drift:** Always applied. Small Gaussian perturbation (sigma=0.02) on all parameters. Prevents population freezing at local optima.

---

## 8. Crossover

### Single-Point Pipeline Crossover

```
1. Topological sort both parents' wiring graphs
   - Break cycles deterministically at the gene with lowest gene_id
2. Number genes 0..n by topo-sort order in each parent
3. Choose random crossover points k_a (in parent A) and k_b (in parent B)
4. Child gets genes 0..k_a from parent A (with A's internal wiring)
   and genes k_b+1..m from parent B (with B's internal wiring)
5. New wire connects A's gene[k_a] output to B's gene[k_b+1] input
6. If the junction wire is type-incompatible → child fails compilation → dies
```

**Crossover rate:** 70% of offspring are produced by crossover (two parents). 30% are produced by mutation only (one parent, cloned then mutated).

---

## 9. Fitness Evaluation

### 9.1 Three Pareto Objectives (NSGA-II)

All three are maximized. All three are margin-over-NCD (the NCD baseline score is subtracted).

| Objective | Formula | Description |
|-----------|---------|-------------|
| **Margin Accuracy** | `organism_accuracy - ncd_accuracy` | Fraction of tasks where top-ranked candidate is correct, minus NCD's accuracy on the same tasks. Organism must beat NCD to get positive fitness. |
| **Margin Calibration** | `(1 - organism_brier) - (1 - ncd_brier)` | Inverted Brier score minus NCD's inverted Brier. Higher = better calibrated than NCD. |
| **Novelty** | `mean_distance_to_k_nearest(behavioral_signature, archive + population)` | Behavioral distance from existing organisms. Higher = more novel. Full Pareto dimension, no decay. |

### 9.2 Accuracy Computation

For each task `{prompt, candidates, correct}`:
1. Call `organism.evaluate(prompt, candidates)`
2. Top-ranked candidate == `correct`? → 1.0 (hit) or 0.0 (miss)
3. Accuracy = mean across all tasks

### 9.3 Calibration Computation (Brier Score)

For each task:
1. Call `organism.evaluate(prompt, candidates)` → get top-ranked candidate
2. Call `organism.confidence(prompt, top_ranked_candidate)` → probability p
3. If top-ranked == correct: brier = (p - 1.0)^2
4. If top-ranked != correct: brier = (p - 0.0)^2
5. Brier score = mean across tasks (lower = better)
6. **Fitness = 1.0 - brier** (higher = better, for NSGA-II maximization)

### 9.4 NCD Baseline

Compute NCD's accuracy and Brier score once per task set. Cache the result. Recompute only when the task set changes (e.g., new generated tasks). NCD is a single deterministic implementation shared by all evaluations.

### 9.5 Task Set

**Evolution battery (seed 42):** 15 seed traps (from `trap_generator.generate_trap_battery(seed=42)`) + 5 generated tasks. Used for fitness evaluation every generation.

**Held-out battery (seed 137):** Separate trap battery generated with seed 137. Never used for selection. Used only for success criterion validation. Reported in logs alongside evolution fitness to track overfitting.

**Task format (from trap_generator):**
```python
{
    "prompt": str,           # The question
    "candidates": [str],     # Possible answers
    "correct": str,          # Ground truth (always in candidates)
    "category": str          # Trap category (numeric_comparison, transitivity, etc.)
}
```

### 9.6 Hierarchical Filtering

Before full evaluation, run a quick screen:
1. Run organism on 5 easy tasks (first 5 from evolution battery), 0.5s timeout
2. If organism crashes on all 5 → skip full evaluation, fitness = 0 on all objectives
3. Otherwise → proceed to full 20-task evaluation with 2s timeout per task

This eliminates broken chimeras before wasting compute on full evaluation.

---

## 10. Selection

### NSGA-II with Top-5 Elitism

**Per generation:**
1. Evaluate 50 parents + 50 offspring = 100 organisms
2. Top 5 parents (by Pareto rank, then crowding distance) survive unconditionally → **elite slots**
3. Remaining 45 slots filled by NSGA-II selection from the pool of 45 remaining parents + 50 children
4. NSGA-II ranks by: (a) non-dominated Pareto front, (b) crowding distance tiebreaker
5. Three objectives: margin accuracy, margin calibration, novelty — all maximized

**Elite monitoring:** Log the elite set every generation. When an elite is displaced, log the displacement event (who replaced whom, fitness comparison).

**Novelty never decays.** It's a full Pareto dimension throughout the entire run. If the population becomes diverse enough that novelty is easy to achieve, it stops being the binding constraint and accuracy takes over naturally.

---

## 11. Novelty Search

### Behavioral Signature

Run each organism on the 15 seed traps (same traps used for novelty across all generations). Record the score vector:

```python
def compute_behavioral_signature(organism, reference_tasks):
    scores = []
    for task in reference_tasks:
        result = organism.evaluate(task['prompt'], task['candidates'])
        top_score = result[0]['score'] if result else 0.0
        scores.append(top_score)
    return np.array(scores)  # 15-dimensional vector
```

Two organisms with similar behavioral signatures (similar score patterns across the 15 traps) are behaviorally similar, even if their genomes differ.

### Novelty Archive

```python
class NoveltyArchive:
    k_nearest: int = 15
    archive_threshold: float = 0.3
    archive: list[np.ndarray] = []

    def novelty_score(self, signature, population_signatures):
        """Average Euclidean distance to k nearest neighbors in archive + population."""
        all_sigs = self.archive + population_signatures
        if not all_sigs:
            return 1.0  # Novel by default
        distances = [np.linalg.norm(signature - s) for s in all_sigs]
        distances.sort()
        k = min(self.k_nearest, len(distances))
        return float(np.mean(distances[:k]))

    def maybe_add(self, signature):
        """Add to archive if sufficiently novel."""
        if self.novelty_score(signature, []) > self.archive_threshold:
            self.archive.append(signature)
```

---

## 12. Sandbox

### Two-Layer Defense

**Layer 1 — Compile-Time (RestrictedPython):**
- Scan organism source code AST for disallowed imports
- Allowed: `numpy`, `math`, `re`, `collections`, `itertools`, `functools`, `statistics`, `hashlib`, `zlib`, `copy`, `dataclasses`, `random`, `string`, `operator`, `heapq`, `bisect`, `decimal`, `fractions`, `struct`
- Blocked: everything else (os, sys, subprocess, socket, io, pathlib, importlib, etc.)
- If disallowed import found → organism dies at compilation

**Layer 2 — Runtime (multiprocessing with spawn):**
- Parent sends organism source code string to worker process via Queue
- Worker: `exec(source_code, namespace)` → instantiate `ReasoningTool` → run evaluation → return results
- Parent: `process.join(timeout=2.0)` → if timeout, `process.terminate()` → score 0.0
- Windows spawn model: child process has no access to parent memory. Organism code string is the only data crossing the boundary.
- No memory limits for MVP (2s timeout is the primary safety net)

---

## 13. Logging & Checkpointing

### Lineage Log (append-only JSONL)

`lineage/lineage.jsonl` — one JSON object per organism per generation:

```json
{
    "genome_id": "uuid",
    "generation": 1234,
    "parent_ids": ["uuid_a", "uuid_b"],
    "mutations_applied": ["point_mutate", "splice"],
    "gene_ids": ["gene_01", "gene_03", "gene_07"],
    "gene_types": ["PARSER", "SCORER", "SCORER"],
    "wiring_hash": "sha256_of_wiring_graph",
    "parameters": {"gene_01_lambda": 0.4, "gene_03_epsilon": 0.1},
    "cycle_cap": 3,
    "has_self_referential_wiring": true,
    "cycle_count": 1,
    "fitness": {
        "margin_accuracy": 0.15,
        "margin_calibration": 0.08,
        "novelty": 0.42
    },
    "held_out_accuracy": 0.35,
    "alive": true,
    "cause_of_death": null,
    "is_elite": false,
    "crashes": [
        {"gene_id": "gene_07", "task_id": 12, "exception": "ValueError: empty sequence"}
    ],
    "timestamp": "2026-03-28T14:30:00"
}
```

**Key fields for metacognition tracking:**
- `has_self_referential_wiring`: boolean — any gene whose input traces back through its own output via any path
- `cycle_count`: number of cycles in the wiring graph
- Log the fitness differential between self-referential and non-self-referential organisms per generation

### Checkpointing

Every 50 generations: pickle `{population, archive, generation, task_set, ncd_baseline}` to `checkpoints/gen_XXXXX.pkl`.

On crash recovery: load latest checkpoint, resume from that generation.

### Elite Log

Every generation: log the 5 elite organisms' genome_ids and fitness vectors. When an elite is displaced, log the displacement event.

---

## 14. Seed Population

### Selection Strategy

From the 146 forge tools, select 50 for the initial population:

**Top 30 by accuracy:** Use post-Phase-0 accuracy ranking (after CMA-ES parameter optimization). These are the fittest organisms.

**20 most structurally diverse:** After gene extraction, represent each tool as a binary vector (which gene types does it contain?). Compute pairwise Hamming distance. Select 20 tools that maximize the minimum distance to the already-selected set (maximin diversity criterion). This favors tools that DON'T use NCD — the 13% of tools without NCD fallback are overrepresented here, providing alternative evolutionary lineages.

**No random organisms at start.** All 50 are proven survivors from the forge, some parameter-optimized.

---

## 15. Phase 0 — CMA-ES Parameter Evolution

Validates the fitness evaluation pipeline and produces better-calibrated seed organisms.

### Specification

- **Scope:** 50 independent CMA-ES runs, one per seed tool
- **Dimensionality:** ~15-25 evolvable float parameters per tool (thresholds, weights, exponents)
- **Objective:** Single-objective — margin-over-NCD accuracy on the evolution task battery
- **Population size:** `4 + floor(3 * ln(n_params))` ≈ 13 per tool
- **Stopping criterion:** 50 generations per tool OR sigma < 1e-6 (convergence)
- **Implementation:** pymoo CMA-ES
- **Budget:** ~18 hours total (50 tools × 50 gens × 13 candidates × 20 tasks × 0.1s)

### Output

- Pre-optimization and post-optimization accuracy for each tool (the delta indicates parametric headroom)
- Re-ranked tool list (post-optimization accuracy determines seed population selection)
- Parameter-optimized tool code saved to `phase0_results/`
- Phase 0 results feed directly into seed population for structural evolution

---

## 16. Configuration

```yaml
# configs/manifest.yaml
apollo:
  # Population
  population_size: 50
  offspring_per_generation: 50
  elite_count: 5

  # Genetics
  crossover_rate: 0.7
  mutation_rates:
    point_mutate: 0.40
    splice: 0.25
    duplicate: 0.15
    rewire: 0.15
    delete: 0.10
    duplicate_and_wire_back: 0.10
  drift_sigma: 0.02
  cycle_cap_range: [1, 5]
  cycle_cap_default: 3

  # Selection
  selection_algorithm: "nsga2"
  fitness_objectives: 3    # margin_accuracy, margin_calibration, novelty

  # Novelty
  novelty_k_nearest: 15
  novelty_archive_threshold: 0.3

  # Tasks
  evolution_seed: 42
  held_out_seed: 137
  n_seed_traps: 15
  n_generated_tasks: 5
  reference_task_count: 15     # For behavioral signature (= seed traps)
  quick_screen_count: 5
  quick_screen_timeout: 0.5

  # Sandbox
  sandbox_timeout_seconds: 2
  allowed_imports:
    - numpy
    - math
    - re
    - collections
    - itertools
    - functools
    - statistics
    - hashlib
    - zlib
    - copy
    - dataclasses
    - random
    - string
    - operator
    - heapq
    - bisect
    - decimal
    - fractions
    - struct

  # Operational
  checkpoint_interval: 50
  max_generations: null        # Run until stopped

  # Phase 0
  phase0_generations_per_tool: 50
  phase0_sigma_threshold: 1e-6

  # Paths (read-only source)
  forge_library_path: "../hephaestus/forge/"
  trap_generator_path: "../hephaestus/src/trap_generator.py"
  # Paths (Apollo's workspace)
  population_path: "population/"
  archive_path: "archive/"
  graveyard_path: "graveyard/"
  lineage_path: "lineage/"
  checkpoint_path: "checkpoints/"
  phase0_path: "phase0_results/"
```

---

## 17. Success Criteria

All criteria evaluated on the **held-out** trap battery (seed 137), never the evolution battery.

### Criterion 1 — Evolution Works (by generation 1,000)

At least one evolved organism scores higher margin-over-NCD accuracy on the held-out battery than the best post-Phase-0 forge tool. If this happens, structural recombination produces genuine improvement beyond parameter optimization.

### Criterion 2 — Diversity Holds (by generation 500)

The novelty archive contains at least 30 behaviorally distinct organisms. If the archive is small, the population has converged and novelty pressure needs to increase.

### Criterion 3 — The Metacognition Signal (by generation 2,000)

At least 10% of surviving organisms have self-referential wiring (any gene whose input traces back through its own output). AND those organisms have equal or higher median fitness than non-self-referential organisms. This is the phase transition — evolution has discovered that self-checking pays off.

**If criterion 3 fails:** self-referential organisms never emerge → increase duplicate-and-wire-back rate to 15%. Self-referential organisms emerge but are always less fit → the fitness environment doesn't reward metacognition → add meta-tasks (Phase 4 from original design) where self-checking is the difference between correct and incorrect.

### Post-MVP Success Criterion

Evolved organisms generalize to the Nemesis adversarial grid (tasks they never saw during evolution). This is the generalization check — did evolution produce genuine reasoning capability or task-specific hacks?

---

## 18. Dependencies

**Required for MVP:**
- Python 3.11+
- numpy
- pymoo (NSGA-II selection + Phase 0 CMA-ES)
- RestrictedPython (compile-time import validation)

**Everything else is stdlib:** ast, multiprocessing, pickle, json, uuid, hashlib, random, copy, dataclasses, pathlib, time, traceback.

---

## 19. Post-MVP Roadmap

*Build these only after MVP success criteria are evaluated.*

| Enhancement | Trigger | Implementation |
|-------------|---------|----------------|
| **Island model** | Population converges despite novelty pressure | 4 sub-populations with migration every 25 gens |
| **Speciation** | 3+ distinct species visible in logs | Extract neat-python speciation logic |
| **MAP-Elites** | Need finer diversity control | pyribs archive alongside NSGA-II |
| **Task escalation** | Median accuracy exceeds 70% | Increase chain depth, add distractors |
| **Meta-tasks (Phase 4)** | Criterion 3 fails | Tasks where self-checking determines correctness |
| **LLM mutation** | Viability spike <10% | Local StarCoder 1B as mutation operator |
| **Coevolutionary parasites** | Population stagnates | Small task-generator population evolving to break organisms |
| **POET-style transfer** | 2+ task environments exist | Test organisms across environments, reward generalization |
| **phylotrackpy** | Lineage analysis needed beyond JSONL | Full phylogenetic tree tracking + visualization |
| **Additional fitness dimensions** | Need finer selection | Adversarial survival, invariance, trace quality |
| **geppy** | stdlib AST proves limiting | Gene Expression Programming for richer genome representation |

---

## 20. The Main Loop (Pseudocode)

```python
def run_apollo(config):
    # ── Bootstrap ─────────────────────────────────────────────
    gene_library = extract_genes(config.forge_library_path)
    ncd_baseline = compute_ncd_baseline(evolution_tasks)

    # ── Phase 0: CMA-ES Parameter Evolution (2 days) ─────────
    optimized_tools = phase0_cmaes(gene_library, evolution_tasks, ncd_baseline)
    population = select_seed_population(optimized_tools, gene_library)  # 30 best + 20 diverse

    # ── Crash Recovery ────────────────────────────────────────
    if checkpoint_exists():
        population, archive, generation = load_checkpoint()
    else:
        archive = NoveltyArchive()
        generation = 0

    # ── Main Loop ─────────────────────────────────────────────
    while True:
        generation += 1

        # 1. Evaluate population
        fitness_vectors = []
        for organism in population:
            fitness = evaluate_organism(organism, evolution_tasks, ncd_baseline, archive, population)
            fitness_vectors.append(fitness)

        # 2. Produce offspring
        children = []
        for _ in range(config.offspring_per_generation):
            if random.random() < config.crossover_rate:
                p1, p2 = select_parents(population, fitness_vectors)
                child = pipeline_crossover(p1, p2)
            else:
                child = copy(random.choice(population))

            # Apply mutations (can stack)
            child = apply_mutations(child, gene_library, config.mutation_rates)
            child = apply_drift(child, config.drift_sigma)

            # Compile and validate
            if compile_and_validate(child):
                children.append(child)

        # 3. Evaluate children
        child_fitness = [evaluate_organism(c, evolution_tasks, ncd_baseline, archive, population)
                        for c in children]

        # 4. Selection with elitism
        elites = select_elites(population, fitness_vectors, k=5)
        remaining_pool = [(o, f) for o, f in zip(population + children, fitness_vectors + child_fitness)
                         if o not in elites]
        survivors = nsga2_select(remaining_pool, target_size=45)
        population = elites + survivors

        # 5. Update novelty archive
        for organism in population:
            sig = compute_behavioral_signature(organism, reference_tasks)
            archive.maybe_add(sig)

        # 6. Log
        log_generation(generation, population, fitness_vectors + child_fitness, archive)
        log_elites(generation, elites)
        log_self_referential_stats(generation, population)

        # 7. Periodic held-out evaluation (for monitoring, never for selection)
        if generation % 10 == 0:
            held_out_scores = evaluate_on_held_out(population, held_out_tasks, ncd_baseline)
            log_held_out(generation, held_out_scores)

        # 8. Checkpoint
        if generation % 50 == 0:
            save_checkpoint(population, archive, generation)
```

---

*Apollo — god of light, truth, prophecy. He doesn't evaluate reasoning from the outside. He evolves it from within.*
