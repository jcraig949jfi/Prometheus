# Apollo — Open-Ended Evolution of Autonomous Reasoning Species

*God of light, truth, prophecy, and intellectual beauty. Apollo doesn't evaluate reasoning. Apollo evolves it.*

---

## Mission

Build a **self-contained, closed-loop evolutionary system** that takes the Prometheus forge library (141+ computable reasoning tools) as seed genomes and evolves them — through mutation, recombination, selection, and novelty pressure — into increasingly sophisticated autonomous reasoning organisms.

Apollo runs independently from the existing forge pipeline. It does not modify, interfere with, or depend on the live operation of Nous, Coeus, Hephaestus, or Nemesis. It reads the forge library as input substrate and produces evolved reasoning species as output. It is designed to run unattended for 40+ days.

**The goal is not better evaluators. The goal is evolved reasoning agents** — composite organisms that can take a claim, decompose it, explore reasoning paths, falsify their own conclusions, detect when they've reached the boundary of what's determinable, and output calibrated judgments. Metacognition, novelty exploration, and hypothesis generation should emerge from selection pressure, not be designed in.

---

## Core Concept

Each forged tool in the Prometheus library is a **genome** — a specific arrangement of reasoning operations encoded as a Python class with `evaluate()`, `confidence()`, and optionally `evaluate_trace()` methods. These genomes currently sit frozen in `agents/hephaestus/forge/`.

Apollo unfreezes them. It treats each tool's source code as a mutable, recombinable genetic sequence. It extracts the functional components — parsers, scorers, transformers, fallbacks — and recombines them into chimeric organisms that are tested against a fitness environment. Organisms that survive reproduce. Organisms that fail are composted. The population evolves.

Over 40 days and thousands of generations, the organisms should develop from simple single-strategy evaluators into complex multi-stage reasoning pipelines that chain perception (structural parsing), deliberation (free energy scoring, MCTS search), monitoring (chaos reservoir stability tracking), and self-correction (active falsification) into unified autonomous reasoners.

---

## Architecture

```
agents/apollo/
├── src/
│   ├── apollo.py                 — Main evolutionary loop (entry point)
│   ├── genome.py                 — Genome representation and manipulation
│   ├── gene_extractor.py         — Parse forge tools into recombinable gene fragments
│   ├── mutation.py               — Mutation operators (splice, modify, duplicate, delete)
│   ├── recombination.py          — Crossover operators (swap components across genomes)
│   ├── fitness.py                — Multi-objective fitness evaluation
│   ├── novelty.py                — Novelty search (behavioral archive + distance)
│   ├── selection.py              — NSGA-III Pareto selection with novelty as objective
│   ├── population.py             — Population management, speciation, niching
│   ├── environment.py            — Fitness environment (trap battery + adversarial + synthetic)
│   ├── task_generator.py         — Generates reasoning tasks of escalating complexity
│   ├── compiler.py               — Assembles gene fragments into executable Python organisms
│   ├── sandbox.py                — Safe execution of evolved organisms (timeout, resource limits)
│   ├── logger.py                 — Structured logging (JSONL lineage tracking)
│   ├── checkpointer.py           — Periodic population snapshots for crash recovery
│   └── analyzer.py               — Population statistics, lineage analysis, emergent pattern detection
├── population/                   — Living population (current generation .py files)
├── archive/                      — Novelty archive (behaviorally unique organisms)
├── graveyard/                    — Dead organisms with cause-of-death metadata
├── species/                      — Emerged species (clusters of related high-fitness organisms)
├── lineage/                      — Full evolutionary lineage graphs (JSONL)
├── checkpoints/                  — Population snapshots every N generations
├── reports/                      — Periodic evolution reports (markdown)
├── configs/
│   ├── manifest.yaml             — Apollo configuration
│   └── fitness_weights.yaml      — Fitness dimension weights (can evolve too)
└── README.md
```

---

## Genome Representation

### Gene Extraction

Each forge tool is decomposed into **gene fragments** — functional units that can be recombined:

```python
@dataclass
class Gene:
    """A recombinable functional unit extracted from a forge tool."""
    gene_id: str                    # Unique identifier
    gene_type: GeneType             # PARSER | SCORER | TRANSFORMER | FALLBACK | MONITOR | FALSIFIER
    source_tool: str                # Which forge tool this came from
    code: str                       # The actual Python source code of this fragment
    imports: list[str]              # Required imports (numpy, re, collections, etc.)
    inputs: list[str]               # What this gene expects as input
    outputs: list[str]              # What this gene produces as output
    dependencies: list[str]         # Other gene_types this gene requires upstream

class GeneType(Enum):
    PARSER = "parser"               # Extracts structure from text (regex, tokenization, logical decomposition)
    SCORER = "scorer"               # Produces a numeric score (NCD, free energy, divergence)
    TRANSFORMER = "transformer"     # Transforms representation (embedding, phase space mapping, chaos reservoir)
    FALLBACK = "fallback"           # Default scoring when primary methods fail (NCD, length heuristic)
    MONITOR = "monitor"             # Tracks trajectory stability (Lyapunov, attractor analysis)
    FALSIFIER = "falsifier"         # Attempts to disprove/contradict (negation, counterfactual generation)
    INTEGRATOR = "integrator"       # Combines scores from multiple sub-components
    METACOGNITIVE = "metacognitive" # Self-referential: evaluates own intermediate outputs
```

### Genome Structure

An organism's genome is an **ordered pipeline of genes** with a wiring specification:

```python
@dataclass
class Genome:
    """A complete organism — an ordered pipeline of genes that performs reasoning."""
    genome_id: str
    genes: list[Gene]               # Ordered gene sequence
    wiring: dict[str, str]          # Maps gene outputs to downstream gene inputs
    parameters: dict[str, float]    # Evolvable numeric parameters (thresholds, weights, exponents)
    lineage: Lineage                # Parent IDs, mutation history, generation number
    species_id: Optional[str]       # Assigned by speciation algorithm

    def to_python(self) -> str:
        """Compile this genome into an executable Python class."""
        # The compiler assembles genes into a ReasoningTool-compatible class
        # with evaluate(), confidence(), and evaluate_trace() methods

    def behavioral_signature(self) -> np.ndarray:
        """Run on a fixed reference task set, return score vector for novelty comparison."""
```

### Gene Extraction Strategy

Parse each of the 141 forge tools and identify:

1. **Parser genes** — regex patterns, tokenizers, structural decomposers. Look for functions/blocks that take raw text and produce structured representations (lists of tokens, parse trees, logical forms).

2. **Scorer genes** — the core scoring logic. NCD computations, compression ratios, free energy calculations, divergence measures, consistency checks. Look for functions that take structured input and return floats.

3. **Transformer genes** — representation changes. Chaos reservoir mappings (logistic map, echo state), embedding operations, phase space projections. Look for functions that transform data shape.

4. **Fallback genes** — NCD and other baseline computations used as defaults. 122 tools use NCD fallback — extract this as a reusable gene.

5. **Monitor genes** — from the 12 chaos reservoir tools, extract the Lyapunov exponent computation and attractor tracking logic.

6. **Falsifier genes** — from the 72 falsification tools, extract the counterfactual generation and contradiction detection logic.

**Expected yield:** ~400-600 unique gene fragments from 141 tools, with significant redundancy in parser and fallback genes but high diversity in scorer and transformer genes.

---

## Mutation Operators

### Point Mutation
Modify a single gene's parameters without changing its structure:
```python
def point_mutate(genome: Genome, mutation_rate: float = 0.1) -> Genome:
    """Randomly adjust numeric parameters within genes."""
    # Change thresholds, weights, exponents by ±10-50%
    # Change regex patterns slightly (add/remove character classes)
    # Swap comparison operators (>, <, >=, <=)
```

### Gene Splice
Insert a new gene from the gene library into a random position in the pipeline:
```python
def splice(genome: Genome, gene_library: list[Gene]) -> Genome:
    """Insert a random gene at a random pipeline position."""
    # Select gene with compatible input/output types
    # Wire it into the pipeline
    # May create novel combinations no forge tool ever contained
```

### Gene Deletion
Remove a gene from the pipeline:
```python
def delete_gene(genome: Genome) -> Genome:
    """Remove a random non-essential gene."""
    # Cannot delete if it breaks the pipeline (required input for downstream gene)
    # Simplification pressure — prevents unbounded genome growth
```

### Gene Duplication
Copy a gene and insert the copy elsewhere in the pipeline:
```python
def duplicate_gene(genome: Genome) -> Genome:
    """Copy a gene and insert at a new position with mutated parameters."""
    # The duplicate gets point-mutated parameters
    # Enables recursive/iterative patterns (same operation applied multiple times)
    # This is how metacognitive loops can emerge — a falsifier gene
    # duplicated to also check the output of the first falsifier
```

### Rewiring
Change which gene's output feeds into which gene's input without changing genes themselves:
```python
def rewire(genome: Genome) -> Genome:
    """Randomly reconnect one gene's output to a different downstream input."""
    # Can create skip connections, feedback loops, parallel paths
    # Feedback loops are allowed but must be detected and capped (max 3 iterations)
    # to prevent infinite recursion
```

### Parameter Drift
Slowly evolve the numeric parameters of all genes:
```python
def drift(genome: Genome, sigma: float = 0.02) -> Genome:
    """Apply small Gaussian perturbation to all numeric parameters."""
    # Models genetic drift — slow background evolution
    # Keeps the population from freezing at local optima
```

---

## Recombination (Crossover)

### Pipeline Crossover
Take the front half of one genome's pipeline and the back half of another's:
```python
def pipeline_crossover(parent_a: Genome, parent_b: Genome) -> Genome:
    """Single-point crossover on the gene pipeline."""
    # Choose a crosspoint in each parent
    # Child gets genes 0..crosspoint from parent_a, crosspoint..end from parent_b
    # Rewire the junction point to maintain type compatibility
```

### Component Swap
Exchange a specific gene type between two genomes:
```python
def component_swap(parent_a: Genome, parent_b: Genome, gene_type: GeneType) -> tuple[Genome, Genome]:
    """Swap all genes of a given type between parents."""
    # e.g., swap all PARSER genes — child_a gets parent_b's parsing with parent_a's scoring
    # This tests whether parsing and scoring are modular
```

### Wiring Crossover
Keep both parents' genes but use one parent's wiring on the other's genes:
```python
def wiring_crossover(parent_a: Genome, parent_b: Genome) -> Genome:
    """Apply parent_a's wiring topology to parent_b's genes (where type-compatible)."""
    # Tests whether the CONNECTION PATTERN matters independently of the components
```

---

## Fitness Environment

### Multi-Objective Fitness Vector

Every organism is evaluated on **6 dimensions**:

```python
@dataclass
class FitnessVector:
    accuracy: float         # Correct answers on reasoning tasks (0-1)
    calibration: float      # Confidence matches actual accuracy (0-1)
    adversarial: float      # Survival rate on adversarial mutations (0-1)
    invariance: float       # Consistency under paraphrase/reorder/distractor transforms (0-1)
    trace_quality: float    # Step-level reasoning quality (if evaluate_trace implemented) (0-1)
    novelty: float          # Behavioral distance from archive (0-1, from novelty search)
```

### Task Sources

Apollo maintains its own task environment, independent from the forge's trap battery:

1. **Seed tasks** — Copy of the 15 static traps + dynamic generator from Hephaestus (read-only, never modified)
2. **Escalating tasks** — Apollo generates increasingly complex reasoning tasks over time:
   - **Phase 1 (gen 0-500):** Single-step — numeric comparison, logical evaluation, simple arithmetic
   - **Phase 2 (gen 500-2000):** Multi-step — transitive chains (depth 3-5), conditional reasoning, compositional word problems
   - **Phase 3 (gen 2000-5000):** Adversarial — tasks with distractors, negation flips, misleading premises, counterfactual injections
   - **Phase 4 (gen 5000+):** Meta-tasks — tasks that require the organism to detect its own uncertainty, identify missing information, recognize when a question is unanswerable
   - **Phase 5 (gen 10000+):** Hypothesis tasks — tasks where the organism must generate and test its own sub-hypotheses to reach a conclusion

3. **Self-generated tasks** — Once organisms develop enough complexity, allow elite organisms to GENERATE tasks that other organisms must solve. This is the adversarial co-evolution layer.

### Task Difficulty Escalation

```python
class TaskEscalator:
    """Automatically increases task difficulty based on population fitness."""

    def __init__(self):
        self.difficulty = 1.0
        self.history = []

    def step(self, population_median_fitness: float):
        """If median fitness exceeds threshold, increase difficulty."""
        if population_median_fitness > 0.7:
            self.difficulty = min(self.difficulty * 1.1, 10.0)
        elif population_median_fitness < 0.3:
            self.difficulty = max(self.difficulty * 0.95, 1.0)
        # Difficulty modulates:
        # - reasoning chain depth
        # - number of distractors
        # - negation complexity
        # - premise count
        # - required meta-reasoning
```

---

## Novelty Search

Novelty search prevents convergence to a single dominant strategy. It rewards organisms that BEHAVE differently from the existing population, regardless of fitness.

### Behavioral Signature

Each organism is characterized by its **behavioral vector** — how it scores on a fixed reference task set:

```python
def compute_behavioral_signature(organism: Genome, reference_tasks: list[dict]) -> np.ndarray:
    """Run organism on 50 fixed reference tasks, return the vector of scores."""
    # The score PATTERN is the behavior — two organisms that score the same tasks
    # high and the same tasks low have similar behavior, even if their genomes differ.
    # Two organisms with identical accuracy but different error patterns have different behavior.
    scores = []
    for task in reference_tasks:
        result = run_organism(organism, task)
        scores.append(result.score)
    return np.array(scores)
```

### Novelty Archive

A growing archive of behaviorally unique organisms:

```python
class NoveltyArchive:
    """Maintains a set of behaviorally distinct organisms."""

    def __init__(self, k_nearest: int = 15, archive_threshold: float = 0.3):
        self.archive: list[np.ndarray] = []
        self.k_nearest = k_nearest
        self.archive_threshold = archive_threshold

    def novelty_score(self, signature: np.ndarray) -> float:
        """Average distance to k nearest neighbors in archive + current population."""
        # High novelty = this organism behaves unlike anything seen before
        # Novelty is a SURVIVAL criterion — novel organisms get a fitness bonus

    def maybe_add(self, signature: np.ndarray):
        """Add to archive if sufficiently novel."""
        if self.novelty_score(signature) > self.archive_threshold:
            self.archive.append(signature)
```

---

## Selection: NSGA-III

Use NSGA-III (Non-dominated Sorting Genetic Algorithm III) for multi-objective selection with reference-point-based diversity preservation.

```python
def select(population: list[Genome], fitness_vectors: list[FitnessVector],
           target_size: int) -> list[Genome]:
    """
    NSGA-III selection:
    1. Non-dominated sorting — partition into Pareto fronts
    2. Reference-point association — distribute across 6D fitness space
    3. Niching — prefer organisms near underrepresented reference points
    4. Truncate to target_size
    """
    # This keeps the population spread across ALL fitness dimensions
    # rather than clustering on one dominant strategy
```

---

## Speciation

Organisms naturally cluster into **species** — groups with similar genome structure and behavior:

```python
class SpeciationManager:
    """Track and manage species in the population."""

    def assign_species(self, population: list[Genome]):
        """Cluster organisms by genomic similarity (gene composition + wiring topology)."""
        # Two organisms are same species if they share >60% of gene types in same order
        # Species compete for reproduction slots proportional to average fitness
        # This prevents a single dominant species from crowding out niche specialists

    def detect_extinction(self):
        """Flag species that have gone N generations without fitness improvement."""

    def detect_emergence(self):
        """Flag novel species that appeared in the last M generations."""
        # Log these — emergent species are the discoveries
```

---

## The Main Loop

```python
def run_apollo(forge_path: str, config: ApolloConfig):
    """
    Apollo's main evolutionary loop. Designed to run for 40+ days unattended.
    """

    # ── Phase 0: Bootstrap ──────────────────────────────────────────────
    gene_library = extract_genes(forge_path)          # Parse 141 tools → ~500 gene fragments
    population = initialize_population(gene_library)   # Generate 200 random genome assemblies
    archive = NoveltyArchive()
    escalator = TaskEscalator()
    generation = 0

    # ── Crash Recovery ──────────────────────────────────────────────────
    if checkpoint_exists():
        population, archive, escalator, generation = load_checkpoint()
        log(f"Recovered from checkpoint at generation {generation}")

    # ── Main Loop ───────────────────────────────────────────────────────
    while True:
        generation += 1

        # 1. Generate tasks at current difficulty
        tasks = generate_tasks(escalator.difficulty, phase=get_phase(generation))

        # 2. Evaluate every organism
        fitness_vectors = []
        for organism in population:
            fitness = evaluate_organism(organism, tasks, archive)
            fitness_vectors.append(fitness)

        # 3. Update task difficulty based on population performance
        median_fitness = np.median([f.accuracy for f in fitness_vectors])
        escalator.step(median_fitness)

        # 4. Selection (NSGA-III)
        parents = select(population, fitness_vectors, target_size=100)

        # 5. Reproduction
        children = []
        for _ in range(100):  # Produce 100 offspring per generation
            if random.random() < 0.7:  # 70% crossover
                p1, p2 = random.sample(parents, 2)
                child = random.choice([pipeline_crossover, component_swap, wiring_crossover])(p1, p2)
            else:  # 30% mutation only
                parent = random.choice(parents)
                child = copy(parent)

            # Apply mutations (multiple can stack)
            if random.random() < 0.3: child = splice(child, gene_library)
            if random.random() < 0.4: child = point_mutate(child)
            if random.random() < 0.1: child = delete_gene(child)
            if random.random() < 0.15: child = duplicate_gene(child)
            if random.random() < 0.2: child = rewire(child)
            child = drift(child)  # Always apply drift

            # Compile and validate
            if compiles_and_runs(child):
                children.append(child)

        # 6. Combine parents + children, select next generation
        population = select(parents + children, evaluate_all(parents + children, tasks, archive),
                           target_size=200)

        # 7. Update novelty archive
        for organism in population:
            sig = compute_behavioral_signature(organism, REFERENCE_TASKS)
            archive.maybe_add(sig)

        # 8. Speciation
        assign_species(population)
        detect_extinctions()
        emergences = detect_emergence()
        for species in emergences:
            log_emergence(species)  # These are the discoveries — log everything

        # 9. Periodic housekeeping
        if generation % 50 == 0:
            save_checkpoint(population, archive, escalator, generation)
            write_report(generation, population, archive)
            log_population_statistics(generation, population, fitness_vectors)

        if generation % 200 == 0:
            # Deep analysis — what patterns are emerging?
            analyze_dominant_gene_combinations(population)
            analyze_lineage_trees(population)
            detect_convergent_evolution(population)  # Same solution from different ancestors

        # 10. Elite archival
        elites = [o for o, f in zip(population, fitness_vectors)
                  if f.accuracy > 0.8 and f.adversarial > 0.6 and f.calibration > 0.5]
        for elite in elites:
            save_to_species_archive(elite)  # Permanent record of high-fitness organisms
```

---

## Sandbox Execution

Every organism runs in a sandboxed environment with strict resource limits:

```python
class Sandbox:
    """Safe execution environment for evolved organisms."""

    TIMEOUT_SECONDS = 10        # Per-task timeout
    MAX_MEMORY_MB = 256         # Memory limit
    ALLOWED_IMPORTS = [         # Whitelist — NO filesystem, network, or subprocess
        'numpy', 'math', 're', 'collections', 'itertools',
        'functools', 'operator', 'string', 'statistics',
        'heapq', 'bisect', 'decimal', 'fractions', 'random',
        'hashlib', 'zlib', 'struct', 'copy', 'dataclasses',
    ]

    def execute(self, organism_code: str, task: dict) -> Optional[dict]:
        """
        Execute organism on task with resource limits.
        Returns result dict or None if timeout/crash/violation.
        """
        # Use multiprocessing with timeout
        # Catch all exceptions — crashed organisms get fitness 0
        # Log crash reason for graveyard analysis
```

---

## Logging and Lineage Tracking

Every organism's full ancestry is tracked:

```python
@dataclass
class LineageRecord:
    genome_id: str
    generation: int
    parent_ids: list[str]           # 1 parent (mutation) or 2 parents (crossover)
    mutations_applied: list[str]    # Which mutation operators were used
    genes: list[str]                # Gene IDs in this organism
    wiring_hash: str                # Hash of wiring topology
    fitness: FitnessVector
    behavioral_signature: list[float]
    species_id: str
    alive: bool                     # Still in population?
    cause_of_death: Optional[str]   # "selection", "crash", "timeout", "compilation_failure"
    timestamp: str
```

Written to `lineage/lineage.jsonl` — append-only, crash-safe.

---

## Reports (every 50 generations)

```markdown
# Apollo Evolution Report — Generation {N}

## Population Health
- Population size: {size}
- Species count: {n_species}
- Species emerged this period: {new_species}
- Species extinct this period: {dead_species}
- Task difficulty: {escalator.difficulty}
- Phase: {current_phase}

## Fitness Distribution
- Accuracy: median={}, max={}, min={}
- Calibration: median={}, max={}, min={}
- Adversarial survival: median={}, max={}, min={}
- Invariance: median={}, max={}, min={}
- Trace quality: median={}, max={}, min={}
- Novelty: median={}, max={}, min={}

## Dominant Gene Combinations
- Most common gene pipeline pattern: [PARSER → TRANSFORMER → SCORER → FALLBACK]
- Emerging pattern: [PARSER → SCORER → FALSIFIER → SCORER] (self-correcting loop)
- Rarest surviving pattern: [TRANSFORMER → MONITOR → FALSIFIER → INTEGRATOR]

## Notable Organisms
- Highest accuracy: {id} ({accuracy}%) — lineage from {ancestor}
- Most novel: {id} — behavioral distance {dist} from nearest archive member
- Longest lineage: {id} — {n} generations of continuous survival
- Most complex: {id} — {n_genes} genes, {n_connections} connections

## Emergent Behaviors
- {n} organisms developed self-referential loops (metacognition candidates)
- {n} organisms chain 3+ falsification steps (deep self-correction)
- {n} organisms produce "undetermined" outputs (epistemic boundary detection)
```

---

## Configuration

```yaml
# configs/manifest.yaml
apollo:
  # Population
  population_size: 200
  offspring_per_generation: 100
  max_generations: null  # Run until stopped

  # Genetics
  crossover_rate: 0.7
  mutation_rates:
    splice: 0.3
    point_mutate: 0.4
    delete_gene: 0.1
    duplicate_gene: 0.15
    rewire: 0.2
    drift_sigma: 0.02

  # Selection
  selection_algorithm: "nsga3"
  fitness_dimensions: 6
  reference_points: "das_dennis"  # Systematic reference point generation for NSGA-III

  # Novelty
  novelty_k_nearest: 15
  novelty_archive_threshold: 0.3
  novelty_weight_in_fitness: 0.2  # 20% of selection pressure from novelty

  # Tasks
  reference_task_count: 50  # Fixed tasks for behavioral signature
  eval_task_count: 100      # Tasks per generation for fitness
  difficulty_increase_threshold: 0.7
  difficulty_decrease_threshold: 0.3

  # Speciation
  species_similarity_threshold: 0.6
  min_species_size: 5
  extinction_generations: 200  # Species dies if no improvement in 200 gens

  # Operational
  checkpoint_interval: 50      # Generations between checkpoints
  report_interval: 50
  deep_analysis_interval: 200
  sandbox_timeout_seconds: 10
  sandbox_max_memory_mb: 256

  # Paths (read-only source)
  forge_library_path: "../hephaestus/forge/"
  # Paths (Apollo's own workspace)
  population_path: "population/"
  archive_path: "archive/"
  graveyard_path: "graveyard/"
  species_path: "species/"
  lineage_path: "lineage/"
  checkpoint_path: "checkpoints/"
  report_path: "reports/"
```

---

## Critical Design Constraints

1. **Complete isolation from forge pipeline.** Apollo reads `agents/hephaestus/forge/*.py` as seed input ONCE at bootstrap. After that, it operates entirely within its own directory. It never writes to any other agent's workspace. If the forge produces new tools while Apollo runs, Apollo does NOT automatically ingest them — that's a manual refresh operation.

2. **No API calls.** Like forged tools, evolved organisms use only numpy + stdlib. No neural models, no external services. Everything is deterministic and reproducible given the same random seed.

3. **No network access.** Apollo is compute-only. It generates, mutates, evaluates, and selects. It does not fetch external data.

4. **Crash recovery is mandatory.** Apollo MUST checkpoint every 50 generations and recover cleanly from any crash. The 40-day run will experience interruptions. Lineage logs are append-only JSONL with fsync after each write.

5. **Genome compilation must be safe.** Evolved organisms are assembled from gene fragments into executable Python. The compiler must validate that the assembled code only uses whitelisted imports, contains no filesystem/network/subprocess calls, and produces a class compatible with the ReasoningTool interface. If compilation fails, the organism dies — it does not get special treatment.

6. **Novelty search is non-optional.** Without novelty pressure, the population WILL converge to NCD-fallback variants within 100 generations. Novelty must be a first-class selection objective from generation 0. This is the single most important design decision.

7. **Feedback loops in genomes are allowed but bounded.** If gene duplication + rewiring produces a cycle (gene A feeds gene B feeds gene A), cap at 3 iterations to prevent infinite recursion. Bounded self-reference is the path to metacognition. Unbounded self-reference is the path to a hang.

8. **Log everything about emergent species.** When speciation detects a new species, dump its representative genome, behavioral signature, lineage tree, and the gene combination that defines it. These are the discoveries. They matter more than the fitness numbers.

9. **Never optimize for a single fitness dimension.** NSGA-III with all 6 dimensions is the selection algorithm. If any shortcut collapses this to a scalar, the system Goodharts immediately. The Pareto front is the population's shape — it should be broad, not pointed.

10. **The graveyard is data.** Dead organisms with their cause of death are valuable. Periodic graveyard analysis reveals which gene combinations are lethal, which mutations are destructive, and which wiring patterns are unstable. The graveyard is the negative knowledge base.

---

## What Success Looks Like

### By generation 500
- Multiple distinct species have emerged
- At least one species has evolved beyond pure NCD scoring
- Task difficulty has escalated at least once
- Novelty archive contains 100+ behaviorally distinct organisms

### By generation 5000
- Species that chain multiple reasoning stages (parse → score → falsify → re-score)
- At least one species exhibits self-referential behavior (applies a gene to its own output)
- Adversarial survival rate for elite organisms exceeds 60%
- Population behavioral diversity (archive size) continues growing

### By generation 20000
- Organisms that produce "undetermined" outputs when given unanswerable tasks
- Multi-strategy organisms that apply different reasoning approaches to different task types
- Evidence of convergent evolution — different lineages arriving at similar strategies independently
- At least one organism that outperforms every original forge tool on the seed trap battery

### By generation 50000+ (the 40-day horizon)
- Autonomous reasoning species that take a claim, decompose it, explore multiple reasoning paths, falsify their own conclusions, and output calibrated judgments with epistemic boundary detection
- A taxonomy of evolved reasoning strategies that no human designed
- Metacognitive loops that emerged from selection pressure alone
- The beginning of a computable epistemology discovered by evolution

---

## Bootstrap Sequence

```bash
# 1. Initialize Apollo's workspace
mkdir -p agents/apollo/{src,population,archive,graveyard,species,lineage,checkpoints,reports,configs}

# 2. Extract genes from forge library (one-time)
python agents/apollo/src/gene_extractor.py --forge-path agents/hephaestus/forge/ --output agents/apollo/gene_library.json

# 3. Launch Apollo
python agents/apollo/src/apollo.py

# 4. Monitor (separate terminal)
tail -f agents/apollo/lineage/lineage.jsonl | python -m json.tool
watch -n 60 cat agents/apollo/reports/latest.md
```

---

## The Name

Apollo — god of light, truth, prophecy, and the arts. Where Prometheus stole fire and gave it to humanity, Apollo IS the light. He doesn't evaluate reasoning from the outside. He evolves it from within. He doesn't ask "is this good reasoning?" He asks "what does reasoning become when it's free to evolve?"

Let Apollo shoot for the stars.
