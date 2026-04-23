# Apollo v0.3 — Buildable Specification

*Incorporates council feedback from ChatGPT, DeepSeek, Gemini, Grok, Claude, plus two meta-analyses. All design decisions final.*

---

## What Changed from v2 and Why

The council was unanimous on five points that forced architectural changes:

1. **AST-only mutation is insufficient.** Every reviewer and the literature (AlphaEvolve, FunSearch, OpenELM) confirm: AST manipulation produces <5-10% viable offspring on complex code. LLM-assisted mutation produces 60-80%. Apollo now uses a **hybrid mutation architecture** — LLM for structural mutations, AST for parameter mutations. A local coding model runs on-device. No API calls.

2. **The context dict is the Achilles heel.** Convention keys solve naming but not distributional compatibility. A SCORER outputting [-3, 3] wired to one expecting [0, 1] produces silent garbage. Apollo now uses **junction normalization** — an evolvable sigmoid shim after every SCORER, mapping any output range to [0, 1] by default.

3. **NCD will dominate without active counterpressure.** Margin-over-NCD + novelty is necessary but not sufficient. Apollo now uses **trace-based NCD independence tracking** (which gene actually determined the final score?) plus **phased FALLBACK decay** (NCD contribution decays over generations).

4. **Static tasks will be memorized.** A fixed 20-task battery gets gamed within 300 generations. Apollo now uses a **rolling curriculum** — rotate 5 tasks every 50 generations.

5. **1,600 generations is insufficient.** Apollo now uses **parallel evaluation** across CPU cores, targeting 8,000-10,000 generations in 37 days.

Additionally, the designer's meta-analysis added: two-tier gene library (fine + macro-genes), graduated mutation schedule, diversity-only warmup, signal sanity checks, anti-bloat hard cap, and a capability step test.

---

## 1. Mission

Unchanged from v2. Build a closed-loop evolutionary system that evolves 146 forge reasoning tools into increasingly sophisticated reasoning organisms, with emergent metacognition as the north star.

---

## 2. Build Sequence

```
Step 1: Viability Spike .............. afternoon
        (determines AST/LLM mutation balance — see threshold table)
Step 2: Phase 0 — CMA-ES ............ 2 days
        (parameter evolution, validates fitness pipeline)
Step 3: Diversity-Only Warmup ........ ~1 day (50 gens, novelty only)
Step 4: Graduated Structural Evolution  35 days
        Gen 0-50:   parameter mutations only
        Gen 50-100: add splice + delete (mild structural)
        Gen 100+:   full mutation suite including crossover + LLM mutation
```

### Viability Spike Threshold Table

| Functional Viability | Strategy |
|---------------------|----------|
| >40% | AST-primary, LLM for structural splice/crossover only |
| 20-40% | LLM-primary for structural mutations, AST for parameter mutations |
| 10-20% | LLM-primary for all mutations, warm-start with mild mutations first 200 gens |
| <10% | LLM-only for all structural operators, AST only for point mutation + drift |

Regardless of spike result, the system is **architected for LLM mutation from day one**. The spike determines the balance, not the capability.

---

## 3. Architecture

```
agents/apollo/
├── src/
│   ├── apollo.py                 — Main evolutionary loop
│   ├── gene_extractor.py         — Parse forge tools → two-tier gene library
│   ├── genome.py                 — Genome: genes + wiring graph + parameters
│   ├── compiler.py               — Assemble genomes → executable ReasoningTool classes
│   ├── mutation.py               — AST mutations (point, delete, drift)
│   ├── mutation_llm.py           — LLM-assisted mutations (splice, combine, refactor)
│   ├── crossover.py              — Topological-sort pipeline crossover (LLM-assisted junction)
│   ├── fitness.py                — Margin-over-NCD accuracy + Brier calibration + NCD independence
│   ├── novelty.py                — Behavioral signature + k-nearest archive (capped at 500)
│   ├── selection.py              — NSGA-II, 3 objectives, top-5 elitism, parsimony tiebreaker
│   ├── sandbox.py                — RestrictedPython compile gate + multiprocessing pool runtime
│   ├── task_manager.py           — Rolling curriculum: fixed seed traps + rotating generated tasks
│   ├── ncd_tracker.py            — Trace-based NCD independence + FALLBACK decay
│   ├── phase0.py                 — CMA-ES parameter evolution
│   ├── dashboard.py              — Real-time early-death indicators
│   ├── logger.py                 — Append-only JSONL lineage logging
│   └── checkpointer.py           — Population snapshots every 10 generations
├── gene_library.json             — Two-tier gene library (fine + macro genes)
├── population/                   — Living population (.py source files)
├── archive/                      — Novelty archive (capped at 500, behaviorally unique)
├── graveyard/                    — Dead organisms + cause-of-death metadata
├── lineage/
│   └── lineage.jsonl             — Full ancestry tracking (append-only)
├── checkpoints/                  — Population snapshots every 10 generations (keep last 5)
├── phase0_results/               — CMA-ES parameter evolution output
├── dashboard/
│   └── status.jsonl              — Per-generation health metrics
├── configs/
│   └── manifest.yaml             — Apollo configuration
└── journal.md                    — Development log
```

---

## 4. LLM Mutation Architecture

### Model Selection (Decision Point)

Apollo requires a local coding model for mutation. No API calls, no network. Must fit on the 17GB GPU alongside sandbox processes (~6-8GB budget for the model).

**Recommended options (in priority order):**

| Model | Size | VRAM (inference) | Strengths |
|-------|------|-----------------|-----------|
| **Qwen2.5-Coder-3B-Instruct** | 3B | ~6GB | Best code quality at 3B. Strong Python understanding. Active community. |
| **StarCoder2-3B** | 3B | ~6GB | Purpose-built for code. Fill-in-the-middle support. |
| **DeepSeek-Coder-1.3B-Instruct** | 1.3B | ~3GB | Smallest footprint, leaves most room. Lower quality. |
| **Qwen2.5-Coder-7B-Instruct** | 7B | ~14GB | Highest quality, tight fit. Standard inference (no TransformerLens overhead) should work, but leaves <3GB for sandbox processes. |

**Recommendation:** Qwen2.5-Coder-3B-Instruct. Best quality-to-VRAM ratio for this use case. Leaves ~11GB for sandbox worker processes. Load once at startup, keep resident throughout the run.

**The model is loaded lazily.** If the viability spike shows >40% AST viability, LLM mutation is secondary and the model loads only when needed for structural splice/crossover. If viability is <40%, the model loads at startup and stays resident.

### Mutation Prompts

The LLM receives structured prompts for each mutation type:

**Splice (insert new gene):**
```
Here is a Python class that evaluates reasoning quality:
{organism_source}

Here is a standalone scoring method from a different tool:
{gene_source}

Modify the class to incorporate this scoring method into its pipeline.
The method should read from ctx['parsed'] or ctx['raw_text'] and write to ctx['score'].
Keep the evaluate() and confidence() interface unchanged.
Return only the modified Python class, no explanation.
```

**Combine (crossover):**
```
Here are two Python classes that evaluate reasoning quality using different strategies:

Tool A:
{parent_a_source}

Tool B:
{parent_b_source}

Create a new class that combines the parsing approach from Tool A with the scoring
approach from Tool B. The class must have evaluate(prompt, candidates) and
confidence(prompt, answer) methods. Use only numpy, math, re, collections, zlib.
Return only the Python class, no explanation.
```

**Refactor (simplify):**
```
Here is a Python reasoning evaluation class:
{organism_source}

Simplify this class by removing dead code and redundant methods. Keep
all methods that contribute to the final ctx['score']. Maintain the
evaluate/confidence interface. Return only the simplified Python class.
```

### AST Validation of LLM Output

Every LLM-generated organism passes through the same compilation pipeline as AST-generated organisms:
1. `ast.parse()` — valid Python?
2. RestrictedPython — no disallowed imports?
3. Interface check — has evaluate() and confidence()?
4. Smoke test — produces discriminating scores on 1 trap?

If the LLM output fails any step, the mutation is retried once with a different random seed. If it fails again, fall back to AST mutation for that offspring.

---

## 5. Gene System

### 5.1 Two-Tier Gene Library

**Tier 1: Fine-Grained Genes (high portability)**

Individual methods extracted from the ~50% of tools that are cleanly decomposable:
- Uses only convention keys (`raw_text`, `parsed`, `score`, `fallback_score`)
- No hardcoded string patterns longer than 20 characters
- No format-specific regex
- Inputs/outputs match standard types

Types: PARSER, SCORER, FALLBACK, UTILITY (travels with parent gene)

**Tier 2: Macro-Genes (low portability)**

Whole PARSER+SCORER bundles from the ~50% of tools with tightly coupled methods:
- Contain English-specific regex, format-dependent parsing
- Internal methods call each other with implicit data contracts
- Extracted as a single unit that stays together during recombination

A **Fission mutation** (post-MVP) can attempt to split a macro-gene once evolution proves it stable.

### 5.2 Portability Score

Each gene is tagged during extraction:

```python
portability_score = 1.0  # Start at max
if has_hardcoded_regex(method, min_length=20): portability_score -= 0.3
if has_format_assumptions(method): portability_score -= 0.2
if references_non_convention_keys(method): portability_score -= 0.3
if has_english_specific_patterns(method): portability_score -= 0.2
# Clamp to [0, 1]
```

For the first 100 generations, splice probability is weighted inversely by portability — prefer high-portability genes early, introduce low-portability macro-genes gradually.

### 5.3 Gene Types and Classification

Same as v2 (name-pattern heuristics) plus:
- UTILITY type: helper methods that travel with their parent gene (detected via "only called by other methods" AST analysis)
- Macro-genes: tagged with `is_macro=True`, contain multiple methods as one unit

### 5.4 Parameter Rewriting

Unchanged from v2: `self.param` → `self.params['gene_XX_param']`. Parameter vector is flat, logged in lineage JSONL.

---

## 6. Genome Representation

### 6.1 Genome Structure

```python
@dataclass
class Genome:
    genome_id: str
    genes: list[Gene]                       # Ordered gene sequence
    wiring: dict[str, list[str]]            # Directed graph: gene_id → [downstream]
    parameters: dict[str, float]            # Evolvable parameters (flat)
    cycle_cap: int                          # Feedback loop iteration limit (1-5, default 3)
    fallback_count: int                     # Number of FALLBACK genes (for NCD tracking)
    lineage: dict                           # parent_ids, mutations_applied, generation
```

### 6.2 Context Dict — The Data Bus

Two-tier convention keys (unchanged from v2) PLUS **junction normalization**:

```python
# Initial context
ctx = {
    'prompt': prompt,
    'candidate': candidate,
    'raw_text': prompt + ' ' + candidate,
    'parsed': None,
    'score': 0.0,
    'fallback_score': 0.0,
    '_gene_trace': [],         # Which gene wrote what, in order
    '_final_gene_type': None   # SCORER or FALLBACK — for NCD independence tracking
}
```

### 6.3 Junction Normalization (NEW in v3)

After every SCORER gene writes `ctx['score']`, the compiler injects:

```python
# Injected by compiler after each SCORER gene
_raw = ctx['score']
_gain = self.params.get(f'gene_{gene_id}_norm_gain', 1.0)
_bias = self.params.get(f'gene_{gene_id}_norm_bias', 0.0)
ctx['score'] = 1.0 / (1.0 + np.exp(-np.clip(_raw * _gain + _bias, -10, 10)))
ctx[f'gene_{gene_id}_score'] = ctx['score']  # Stamped write
ctx['_gene_trace'].append((gene_id, 'score', ctx['score']))
```

The gain and bias are **evolvable per gene junction**. Default: sigmoid normalization mapping any range to [0, 1]. Evolution can learn to override this (e.g., gain=0.01 effectively passes raw scores through, gain=10 makes it a hard threshold).

**Why this matters:** When Tool A's SCORER outputs values in [-3, 3] and Tool B's SCORER downstream expects [0, 1], the normalization shim prevents silent distributional garbage. This is the single highest-leverage change for bootstrap viability per the council.

### 6.4 Execution Model

Per-candidate, unchanged from v2. Per-candidate crash isolation. Terminal output: `ctx['score']`, last SCORER wins. Self-referential feedback via convention key.

---

## 7. NCD Counterpressure (NEW in v3)

### 7.1 Trace-Based NCD Independence

The `_gene_trace` records which gene wrote the final `ctx['score']`. After evaluation:

```python
def compute_ncd_independence(gene_trace, gene_library):
    """Fraction of tasks where final score came from a SCORER, not FALLBACK."""
    final_gene_type = gene_trace[-1][0]  # Last gene to write 'score'
    gene = gene_library[final_gene_type]
    return 0.0 if gene.gene_type == 'FALLBACK' else 1.0
    # Average across all tasks for the organism
```

NCD independence becomes a **modifier on accuracy fitness**:

```python
adjusted_margin = margin_accuracy * (0.5 + 0.5 * ncd_independence)
```

An organism that beats NCD on 5 tasks but uses NCD on the other 15 gets its margin halved. An organism that beats NCD on all 20 tasks using its own SCORER genes gets full credit.

### 7.2 Phased FALLBACK Decay

The FALLBACK gene's output is multiplied by a generation-dependent decay:

```python
fallback_weight = max(0.25, 1.0 - (generation / 2000))
```

- Generation 0: FALLBACK contributes 100%
- Generation 1000: FALLBACK contributes 50%
- Generation 1500: FALLBACK contributes 25% (floor)

Organisms relying on FALLBACK see their fitness eroding over time. Organisms with real SCORER pathways are unaffected.

### 7.3 Monitoring

Log every generation: `% of elites with FALLBACK as primary scorer`. If >70% past generation 300, increase the decay rate by setting the denominator to 1500 instead of 2000.

---

## 8. Mutation Operators

### 8.1 AST Mutations (always available)

| Operator | Rate | Description |
|----------|------|-------------|
| **Point Mutate** | 40% | Gaussian perturbation on parameters. |
| **Delete** | 10% | Remove a random gene, rewire around it. |
| **Drift** | always | Small Gaussian perturbation (sigma=0.02) on all parameters. |

### 8.2 LLM-Assisted Mutations (available gen 100+ or as determined by viability spike)

| Operator | Rate | Description |
|----------|------|-------------|
| **LLM Splice** | 25% | LLM combines a new gene into existing organism. AST validates output. |
| **LLM Crossover** | (via crossover, 70% of offspring) | LLM combines strategies from two parents. |
| **Duplicate-and-Wire-Back** | 10% | Copy a gene, wire copy's input to original's output. LLM adjusts the copy's logic to "check" the original. |
| **Rewire** | 15% | Change one connection in wiring graph. Pure AST (structural change only). |
| **Duplicate** | 15% | Copy a gene with mutated parameters. Pure AST. |

### 8.3 Graduated Mutation Schedule

| Generation Range | Allowed Mutations |
|-----------------|-------------------|
| 0-50 | Point mutate + drift only (parameter calibration) |
| 50-100 | Add splice + delete (mild structural) |
| 100+ | Full suite: all AST + LLM operators, crossover enabled |

### 8.4 Anti-Bloat Measures

- **Hard cap: 15 genes per organism.** Splice and duplicate are rejected if the organism is at the cap.
- **Delete rate: 10%.** When deletion removes a gene and fitness stays the same, the gene was dead weight.
- **Parsimony tiebreaker:** In NSGA-II, when two organisms have identical Pareto rank and similar crowding distance, prefer the one with fewer genes.

---

## 9. Crossover

### LLM-Assisted Pipeline Crossover

For 70% of offspring:

1. Select two parents from the population
2. If LLM available: send both parents' source to the LLM with the "Combine" prompt (Section 4). AST-validate the output. If valid, use it.
3. If LLM unavailable or LLM output fails validation: fall back to AST crossover (topological-sort single-point crossover from v2, with deterministic cycle-breaking at lowest gene_id)
4. Apply junction normalization to the child's compiled pipeline

---

## 10. Fitness Evaluation

### 10.1 Three Pareto Objectives (NSGA-II)

| Objective | Formula | Description |
|-----------|---------|-------------|
| **Adjusted Margin Accuracy** | `margin_accuracy * (0.5 + 0.5 * ncd_independence)` | Accuracy above NCD, penalized by NCD reliance |
| **Margin Calibration** | `(1 - organism_brier) - (1 - ncd_brier)` | Inverted Brier score above NCD baseline |
| **Novelty** | `mean_distance_to_k_nearest(sig, archive + population)` | Behavioral distance, full Pareto dimension, never decays |

### 10.2 Task Management — Rolling Curriculum (NEW in v3)

**Fixed component (15 tasks):** Seed traps from `trap_generator.generate_trap_battery(seed=42)`. Never rotated. Also used for behavioral signatures.

**Rotating component (5 tasks):** Generated with a new random seed every 50 generations. Old tasks cycled out, new tasks cycled in.

**NCD baseline:** Recomputed whenever the task set changes (every 50 generations).

**Held-out battery:** `trap_generator.generate_trap_battery(seed=137)`. Never used for selection. Evaluated every 10 generations for overfitting monitoring.

### 10.3 Signal Sanity Check (NEW in v3)

Part of the compilation validation: after the smoke test (1 trap, 2 candidates), verify the organism produces **different scores** for the two candidates (within epsilon). If scores are identical, the organism is functionally dead and fails compilation.

### 10.4 Hierarchical Filtering

1. Quick screen: 3 tasks, 0.5s timeout — eliminates broken organisms
2. Full eval: remaining tasks, 0.5s timeout per task — only for organisms that pass quick screen

---

## 11. Selection

### NSGA-II with Top-5 Elitism

Unchanged from v2 except:
- **Parsimony tiebreaker** in crowding distance (prefer fewer genes)
- Population size: 50 organisms, 50 offspring per generation (may increase to 80-100 if parallelization provides headroom)

### Diversity-Only Warmup (NEW in v3)

After Phase 0 CMA-ES and before accuracy-driven evolution: run 50 generations with **novelty as the only selection objective** (no accuracy, no calibration). This seeds the archive with diverse behavioral signatures before accuracy pressure narrows the population.

---

## 12. Novelty Search

Same as v2 except:
- **Archive capped at 500 entries.** When full, replace the entry nearest to an existing neighbor (least novel in archive).
- **Novelty score** computed against archive + current population.
- Archive never pruned by age — only by novelty redundancy.

---

## 13. Sandbox & Parallelization

### 13.1 Two-Layer Defense

Unchanged from v2: RestrictedPython compile-time, multiprocessing runtime.

### 13.2 Parallel Evaluation (NEW in v3)

```python
from multiprocessing import Pool

def evaluate_generation(organisms, tasks, ncd_baseline, timeout=0.5):
    with Pool(processes=min(cpu_count(), 16)) as pool:
        results = pool.starmap(evaluate_organism,
                               [(org, tasks, ncd_baseline, timeout) for org in organisms])
    return results
```

Each organism evaluation is independent — perfect parallelism. On an 8-core machine, this cuts per-generation time by ~6x.

### 13.3 Timeout

**0.5 seconds** (down from 2s in v2). Deterministic numpy operations on strings should complete in <100ms. 0.5s catches infinite loops while giving chaos reservoir tools room for their logistic map iterations.

---

## 14. Logging & Checkpointing

### 14.1 Lineage Log

Same JSONL format as v2 plus:
- `ncd_independence`: float (0-1), fraction of tasks answered by SCORER not FALLBACK
- `fallback_count`: int, number of FALLBACK genes in pipeline
- `gene_count`: int, total genes (for bloat tracking)
- `portability_score`: float, mean portability of genes in organism
- `mutation_source`: "ast" or "llm" (which system produced this organism)

### 14.2 Checkpointing

**Every 10 generations** (up from 50 in v2). Keep last 5 checkpoints, delete older ones. The 40-day run will experience interruptions — losing 10 generations (~2 hours) is acceptable; losing 50 (~10 hours) is not.

### 14.3 Dashboard (NEW in v3)

`dashboard/status.jsonl` — one JSON object per generation:

```json
{
    "generation": 1234,
    "compilation_survival_pct": 0.62,
    "quick_screen_survival_pct": 0.55,
    "median_margin_accuracy": 0.08,
    "best_margin_accuracy": 0.22,
    "median_calibration": 0.04,
    "elite_margin_accuracy_evolution": 0.22,
    "elite_margin_accuracy_held_out": 0.18,
    "pct_self_referential": 0.12,
    "pct_elites_using_fallback": 0.40,
    "novelty_archive_size": 187,
    "median_gene_count": 6,
    "max_gene_count": 12,
    "ncd_correlation": 0.65,
    "self_ref_fitness_delta": 0.03,
    "overfitting_gap": 0.04,
    "gene_type_distribution": {"PARSER": 0.25, "SCORER": 0.55, "FALLBACK": 0.10, "MACRO": 0.10},
    "mutation_source_distribution": {"ast": 0.45, "llm": 0.55}
}
```

---

## 15. Early Death Indicators

Monitor from generation 1. **Intervene if any trigger fires:**

| Signal | Threshold | Intervention |
|--------|-----------|-------------|
| DOA rate (compilation failures) | >85% | Reduce crossover rate, increase point mutation |
| NCD correlation with population | >0.9 | Increase FALLBACK decay rate |
| Novelty archive growth plateaus | <10 new entries in 100 gens | Lower archive threshold to 0.25 |
| No self-referential organisms | Zero by gen 500 | Increase duplicate-and-wire-back to 15% |
| Held-out diverges from evolution accuracy | Gap > 0.15 | Increase task rotation frequency to every 25 gens |
| PARSER genes disappearing | <10% of gene pool | Red flag — organisms bypassing structure |
| Crash rate increasing over time | Trend upward 100+ gens | Mutation operators too destructive |
| Crash rate drops to zero | For 50+ gens | Population homogenized |
| All 5 elites share same wiring hash | For 50+ gens | Novelty pressure has failed |
| Median gene count monotonically increasing | For 100+ gens | Bloat — increase delete rate to 15% |

---

## 16. Seed Population

Unchanged from v2: Top 30 by post-Phase-0 accuracy + 20 most structurally diverse (maximin Hamming distance on gene-type binary vector). Favors non-NCD tools in the diversity selection.

---

## 17. Phase 0 — CMA-ES

Unchanged from v2: 50 independent per-tool CMA-ES runs, single-objective (margin accuracy), 50 gens/tool, ~18 hours. Save pre/post deltas. Re-rank tools after optimization.

---

## 18. Configuration

```yaml
# configs/manifest.yaml
apollo:
  # Population
  population_size: 50
  offspring_per_generation: 50
  elite_count: 5
  max_genes_per_organism: 15

  # Genetics
  crossover_rate: 0.7
  mutation_rates:
    point_mutate: 0.40
    splice: 0.25         # LLM-assisted when available
    duplicate: 0.15
    rewire: 0.15
    delete: 0.10
    duplicate_and_wire_back: 0.10
  drift_sigma: 0.02
  cycle_cap_range: [1, 5]
  cycle_cap_default: 3

  # Graduated schedule
  params_only_until_gen: 50
  mild_structural_until_gen: 100

  # Selection
  selection_algorithm: "nsga2"
  fitness_objectives: 3
  diversity_warmup_generations: 50

  # NCD counterpressure
  fallback_decay_floor: 0.25
  fallback_decay_generations: 2000
  ncd_independence_weight: 0.5    # in (0.5 + 0.5 * ncd_independence)

  # Novelty
  novelty_k_nearest: 15
  novelty_archive_threshold: 0.3
  novelty_archive_max_size: 500

  # Tasks
  evolution_seed: 42
  held_out_seed: 137
  n_seed_traps: 15
  n_rotating_tasks: 5
  task_rotation_interval: 50      # generations
  reference_task_count: 15
  quick_screen_count: 3

  # Sandbox
  sandbox_timeout_seconds: 0.5
  parallel_workers: "cpu_count"

  # LLM mutation
  llm_model: "Qwen/Qwen2.5-Coder-3B-Instruct"  # or StarCoder2-3B, decision point
  llm_max_tokens: 2048
  llm_retry_on_failure: 1

  # Operational
  checkpoint_interval: 10
  checkpoint_keep_last: 5
  held_out_eval_interval: 10
  dashboard_interval: 1
  max_generations: null

  # Phase 0
  phase0_generations_per_tool: 50
  phase0_sigma_threshold: 1e-6

  # Paths
  forge_library_path: "../hephaestus/forge/"
  trap_generator_path: "../hephaestus/src/trap_generator.py"
```

---

## 19. Success Criteria

All evaluated on **held-out** battery (seed 137) only.

### Criterion 1 — Evolution Works (by generation 1,000)
At least one evolved organism scores higher adjusted-margin-accuracy on the held-out battery than the best post-Phase-0 forge tool.

### Criterion 2 — Diversity Holds (by generation 500)
Novelty archive contains at least 30 behaviorally distinct organisms.

### Criterion 3 — Metacognition Signal (by generation 2,000)
At least 10% of surviving organisms have self-referential wiring AND those organisms have equal or higher median fitness than non-self-referential organisms.

### Criterion 4 — Capability Step Test (by generation 5,000) (NEW in v3)
Every 500 generations, introduce a qualitatively new task type never seen before. Measure adaptation speed (elite accuracy on the new type after 50 more generations). If adaptation speed increases over time, the system is learning to reason. If flat, it's memorizing task distributions.

---

## 20. Dependencies

**Required:**
- Python 3.11+
- numpy
- pymoo (NSGA-II + CMA-ES)
- RestrictedPython (compile-time import validation)
- transformers + torch (for local LLM mutation — Qwen2.5-Coder-3B or alternative)

**Stdlib:** ast, multiprocessing, pickle, json, uuid, hashlib, random, copy, dataclasses, pathlib, time, traceback

---

## 21. Post-MVP Roadmap

| Enhancement | Trigger |
|-------------|---------|
| **Fission mutation** (split macro-genes) | Macro-genes dominating elite population |
| **Island model** | Population converges despite novelty |
| **Speciation-lite** | Lineage protection needed (promising lineages dying) |
| **Evolvable context schemas** | Recombination destroying communication structure |
| **Ecological niches** (task subsets) | Single dominant strategy despite novelty |
| **Internal diversity metrics** (gene trace patterns) | Behavioral novelty insufficient |
| **Capability step test expansion** | Need deeper generalization validation |
| **7B coding model** | 3B mutation quality insufficient, hardware upgrade available |

---

## 22. The Main Loop

```python
def run_apollo(config):
    # ── Bootstrap ─────────────────────────────────────────────
    gene_library = extract_two_tier_genes(config.forge_library_path)
    ncd_baseline = compute_ncd_baseline(evolution_tasks)
    llm = load_mutation_model(config.llm_model) if config.use_llm else None

    # ── Phase 0: CMA-ES (2 days) ─────────────────────────────
    optimized_tools = phase0_cmaes(gene_library, evolution_tasks, ncd_baseline)
    population = select_seed_population(optimized_tools, gene_library)

    # ── Crash Recovery ────────────────────────────────────────
    if checkpoint_exists():
        population, archive, generation = load_checkpoint()
    else:
        archive = NoveltyArchive(max_size=500)
        generation = 0

    # ── Diversity-Only Warmup (50 gens) ───────────────────────
    if generation < config.diversity_warmup_generations:
        for _ in range(config.diversity_warmup_generations - generation):
            generation += 1
            # Selection on novelty only — no accuracy, no calibration
            children = produce_offspring(population, gene_library, generation, config, llm)
            all_orgs = population + children
            sigs = [compute_behavioral_signature(o, reference_tasks) for o in all_orgs]
            novelty_scores = [archive.novelty_score(s, sigs) for s in sigs]
            population = select_by_novelty_only(all_orgs, novelty_scores, config.population_size)
            for o, s in zip(population, sigs):
                archive.maybe_add(s)
            if generation % 10 == 0:
                save_checkpoint(population, archive, generation)

    # ── Main Evolutionary Loop ────────────────────────────────
    while True:
        generation += 1

        # Task rotation
        if generation % config.task_rotation_interval == 0:
            rotate_tasks(evolution_tasks, config)
            ncd_baseline = compute_ncd_baseline(evolution_tasks)

        # Evaluate population (parallel)
        fitness_vectors = parallel_evaluate(population, evolution_tasks, ncd_baseline,
                                           archive, generation, config)

        # Produce offspring (graduated mutation schedule)
        children = produce_offspring(population, gene_library, generation, config, llm)

        # Evaluate children (parallel)
        child_fitness = parallel_evaluate(children, evolution_tasks, ncd_baseline,
                                         archive, generation, config)

        # Selection with elitism + parsimony
        elites = select_elites(population, fitness_vectors, k=5)
        pool = list(zip(population + children, fitness_vectors + child_fitness))
        pool = [(o, f) for o, f in pool if o not in elites]
        survivors = nsga2_select(pool, target_size=45, parsimony=True)
        population = elites + survivors

        # Update novelty archive
        for org in population:
            sig = compute_behavioral_signature(org, reference_tasks)
            archive.maybe_add(sig)

        # Dashboard + logging
        log_generation(generation, population, fitness_vectors, archive)
        log_dashboard(generation, population, fitness_vectors, child_fitness, archive)

        # Held-out evaluation (monitoring only)
        if generation % config.held_out_eval_interval == 0:
            log_held_out(generation, population, held_out_tasks, ncd_baseline)

        # Checkpoint
        if generation % config.checkpoint_interval == 0:
            save_checkpoint(population, archive, generation)

        # Capability step test
        if generation % 500 == 0 and generation > 0:
            run_capability_step_test(population, generation)
```

---

*Apollo v0.3 — built on the wisdom of five reviewers, two meta-analyses, and the forge that created its seed substrate. The viability spike is the first move. Everything else follows from that number.*
