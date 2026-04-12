# Apollo — Reboot Prompt
## Date: 2026-04-04
## Agent: Claude Code (Opus) on dedicated GPU window
## Named for: Apollo (Ἀπόλλων) — God of light, truth, prophecy. He doesn't evaluate reasoning. He evolves it.

---

## Context: What Happened Before

Apollo v1 reached MVP on 2026-03-26. The evolutionary loop runs at 35,000 generations/day. Selection, logging, checkpointing, novelty search — all functional. But the run stalled: AST-only mutation produced alive-but-stagnant organisms. Zero organisms beat the NCD baseline after 190 generations. The council was unanimous: LLM-assisted mutation is required, not optional. Literature confirms 60-80% viable offspring from LLM mutation versus <5% for AST.

Apollo was shelved while other pillars ran hot. Three things have changed since then:

1. **The bypass problem is understood.** Ignis (steering vector research) proved that evolutionary search in activation space finds shortcuts — bypass is a global attractor. Every CMA-ES run across Qwen, GPT-NeoX, and Pythia converged on bypass solutions that produce correct-looking output without engaging reasoning circuits. Apollo must be designed so bypass is structurally impossible, not just penalized.

2. **Frame H primitives exist.** The Forge produced 27 composable reasoning building blocks (`forge_primitives.py`) covering logic, probability, graph/causal reasoning, constraints, arithmetic, temporal tracking, belief modeling, and meta-calibration. These are implemented Python functions that either fire and change the output or don't. 15 tools forged from these primitives pass at 100% with up to 74% accuracy. Frame H primitives replace the fragile 821 method-level gene fragments from v1.

3. **The ablation gate is defined.** The Forge builder prompt now defines "genuine reasoning" operationally: if removing a component changes ≥20% of outputs, the component is load-bearing. If it doesn't, the reasoning is decorative. This is the bypass detector. It becomes a fitness dimension in Apollo.

4. **T2 gems prove composition works.** Gem-forged tools at 91-97% accuracy demonstrate that composing T1 tools through universal extraction + multi-strategy routing produces dramatically better performance than raw generation. The composition pattern is real. Apollo's job is to search the space of compositions systematically.

---

## Your Mission

Evolve routing networks over Frame H primitives that genuinely reason — verified by ablation gate, evaluated by the trap battery, with bypass structurally excluded.

You are not evolving language models. You are not training transformers. You are evolving **programs** — explicit compositions of 27 reasoning primitives — where the evolutionary search finds which primitive sequences solve which problem types. The primitives do the computation. Evolution finds the routing. Bypass is impossible because there is no pathway that skips the primitives.

The survivors of this evolutionary process serve a dual purpose:
1. They are **reasoning tools** in their own right — solutions to the 108-category battery
2. They are **training data** for a future neural routing network — each survivor is an explicit (problem_type → primitive_sequence → verified_answer) triple

---

## Hardware

Two GPUs available:
- **GPU 1:** Hosts Qwen2.5-Coder-3B-Instruct (~6GB VRAM) for LLM-assisted mutation
- **GPU 2:** Hosts parallel fitness evaluation (sandbox, trap battery, ablation testing)

CPU handles: selection, logging, novelty archive, checkpointing, population management.

Target throughput: 35,000+ generations/day (achieved in v1 at 2.5s/gen with 50 organisms). With LLM mutation adding ~1-2s per mutation call, expect 15,000-20,000 generations/day. This is sufficient — 40 days = 600K-800K organisms evaluated.

---

## Architecture Changes from v1

### Gene Library: Frame H Primitives (replaces extracted method fragments)

The gene library is `forge_primitives.py` — 27 composable building blocks:

| Category | Primitives | What They Do |
|----------|-----------|-------------|
| Logic | propositional solver, predicate evaluator, consistency checker | Formal logical operations |
| Probability | Bayesian updater, distribution comparator, expected value calculator | Probabilistic reasoning |
| Graph/Causal | graph builder, path finder, d-separation checker, causal interventioner | Structural and causal reasoning |
| Constraints | constraint propagator, satisfiability checker, optimization solver | Constraint satisfaction |
| Arithmetic | expression parser, modular arithmetic, sequence analyzer | Numerical computation |
| Temporal | timeline builder, interval reasoner, scheduling solver | Temporal reasoning |
| Belief | belief state tracker, perspective taker, information asymmetry detector | Theory of mind |
| Meta/Calibration | confidence calibrator, ambiguity detector, boundary recognizer | Metacognitive operations |

Each primitive has a defined interface: takes typed input, produces typed output, can be composed with other primitives whose output type matches input type. The type system enforces composability at the genome level.

### Genome Representation: Primitive Routing DAG

An organism is an ordered sequence of primitive calls with a wiring specification:

```python
@dataclass
class Organism:
    genome_id: str
    primitive_sequence: list[PrimitiveCall]  # Which primitives, in what order
    wiring: dict[str, str]                    # Maps outputs to downstream inputs
    parameters: dict[str, float]              # Evolvable thresholds, weights
    router_logic: str                         # Python code that selects which path to take
    lineage: Lineage
    
@dataclass  
class PrimitiveCall:
    primitive_name: str          # Which of the 27 primitives
    input_mapping: dict          # Where this primitive gets its input
    parameter_overrides: dict    # Organism-specific parameter values
```

The `router_logic` is the evolvable part — the code that decides, given a problem, which primitives to call in which order. The primitives themselves are fixed. Evolution searches over routing strategies, not over computation.

### Fitness: Six Dimensions (NSGA-II, no collapse to scalar)

| Dimension | Metric | Why |
|-----------|--------|-----|
| **Accuracy** | Margin over NCD baseline on evolution tasks | Core performance |
| **Calibration** | Brier score on confidence outputs | Honest uncertainty |
| **Ablation Delta** | Minimum per-primitive ablation impact | **BYPASS KILLER** — every primitive must change ≥20% of outputs when removed |
| **Generalization** | Held-out category accuracy | Prevents overfitting to evolution tasks |
| **Diversity** | Behavioral distance from novelty archive | Prevents population collapse |
| **Parsimony** | Fewer primitives preferred (tiebreaker) | Prevents bloat |

**The ablation delta dimension is non-negotiable.** It is the structural guarantee against bypass. An organism that achieves 90% accuracy but has ablation delta of 0.0 on any primitive is fitness-dominated by an organism at 60% accuracy with all primitives load-bearing. NSGA-II's Pareto selection ensures this — bypass organisms cannot be on the Pareto front because they're dominated on the ablation dimension.

### Mutation: LLM-Assisted (Qwen2.5-Coder-3B-Instruct)

Four mutation types, all using the local coding model:

1. **Route mutation:** The LLM modifies the router logic — changes which primitives are called for which problem types. This is the primary mutation operator.

2. **Wiring mutation:** The LLM rewires which primitive's output feeds into which primitive's input. Changes the composition structure without changing which primitives are used.

3. **Parameter mutation:** AST-only (no LLM needed). Adjust thresholds, weights, exponents within the existing structure. Cheapest mutation, highest viability.

4. **Primitive swap:** The LLM replaces one primitive call with a different primitive, adjusting the surrounding router logic to accommodate the type change. Exploratory mutation — lower viability, higher novelty.

**LLM mutation prompt template:**
```
You are modifying a reasoning tool that composes primitives from a fixed library.
The tool currently routes problems through these primitives in this order: {sequence}
The router logic is: {router_code}

Current fitness: accuracy={acc}, ablation_delta={abl}, calibration={cal}
Weakest primitive (lowest ablation delta): {weakest_name} at {weakest_delta}

Your task: modify the router logic to improve performance. Rules:
- You may ONLY use primitives from this list: {primitive_names}
- Every primitive you include MUST be load-bearing (ablation delta >= 0.20)
- Output valid Python that compiles and runs
- Do NOT add any imports beyond the primitive library
- Do NOT add network, filesystem, or subprocess calls

Return ONLY the modified router_logic code, no explanation.
```

### Seed Population

| Source | Count | Description |
|--------|-------|-------------|
| Frame H gems (forge_v7/) | 15 | 100% pass rate, up to 74% accuracy. Best starting organisms. |
| T2 gems | 5 | 91-97% accuracy. Proven composition patterns. |
| T2 passing tools | 5 | 40-45% accuracy. Diverse strategies. |
| Random primitive compositions | 25 | 3-5 random primitives wired sequentially. Exploration fodder. |
| **Total seed population** | **50** | |

### NCD Counterpressure (from v3 council feedback)

NCD is the bypass attractor for reasoning tools. Three countermeasures:

1. **Trace-based independence:** Track which primitive produced the final score. If the FALLBACK/NCD gene produces >50% of final outputs, penalize on the ablation dimension.

2. **Phased NCD decay:** NCD contribution to fitness decays over generations. Gen 0-100: NCD fallback allowed at full weight. Gen 100-500: NCD contribution halved. Gen 500+: NCD contribution zeroed. Organisms must find non-NCD strategies to survive long-term.

3. **NCD discrimination test at compilation:** Before an organism enters the population, test whether its output differs from pure NCD on 10 reference tasks. If <3/10 differ, the organism is stillborn — it goes to the graveyard, not the population.

### Rolling Task Curriculum

Static tasks get memorized. The task environment must evolve alongside the population.

- **Fixed reference set (50 tasks):** Never changes. Used for behavioral signatures and cross-generation comparison. Drawn from the 108-category battery.
- **Evolution set (100 tasks):** Rotates 10 tasks every 50 generations. New tasks drawn from trap generators at increasing difficulty.
- **Held-out set (50 tasks):** Never seen during evolution. Used only for generalization fitness dimension. Refreshed every 500 generations.
- **Capability step test:** Every 500 generations, introduce a task type the population has never seen. Measure adaptation speed. This detects whether the population has genuine generalization or just memorized the curriculum.

---

## The Evolutionary Loop

```
BOOTSTRAP:
  1. Load Frame H primitives from forge_primitives.py
  2. Load Qwen2.5-Coder-3B-Instruct on GPU 1
  3. Build seed population (50 organisms)
  4. Initialize trap battery on GPU 2
  5. Compile and validate all seeds (discard non-viable)
  6. Evaluate fitness on all 6 dimensions
  7. Initialize novelty archive (fill during warmup)

WARMUP (generations 0-50):
  - Diversity-only selection pressure (no accuracy)
  - Parameter mutation only (no structural changes)
  - Fill novelty archive to 500 organisms
  - Establish behavioral diversity before optimization begins

GRADUATED MUTATION (generations 50-200):
  - Gen 50-100: parameter mutation + route mutation (mild structural)
  - Gen 100-200: add wiring mutation + primitive swap (full suite)
  - Accuracy fitness dimension activates at gen 50
  - Ablation fitness dimension activates at gen 100

MAIN LOOP (generation 200+):
  For each generation:
    1. Select parents via NSGA-II (top Pareto ranks + crowding distance)
    2. Generate offspring via LLM-assisted mutation (GPU 1)
       - 40% route mutation
       - 25% parameter mutation (AST-only, no GPU)
       - 20% wiring mutation
       - 15% primitive swap
    3. Compile offspring, discard non-viable
    4. NCD discrimination test, discard NCD-equivalent
    5. Evaluate fitness on evolution tasks (GPU 2, parallel)
    6. Compute ablation delta for each primitive in each organism
    7. Compute behavioral signatures on reference set
    8. Update novelty archive
    9. NSGA-II selection: parents + offspring → next generation
    10. Top-5 elitism (survive unconditionally)
    11. Rotate curriculum tasks every 50 gens
    12. Checkpoint every 10 gens
    13. Report every 50 gens
    14. Capability step test every 500 gens

PHASED NCD DECAY:
  Gen 0-100: NCD fallback at full weight
  Gen 100-500: NCD contribution halved in fitness
  Gen 500+: NCD contribution zeroed — organisms must reason without NCD
```

---

## Success Criteria (Updated)

### By generation 500
- At least 5 organisms with ablation delta ≥ 0.20 on ALL primitives
- At least one organism beating NCD by ≥10% margin on evolution tasks
- Novelty archive contains 500 behaviorally distinct organisms
- Multiple routing strategies visible in population (not monoculture)

### By generation 5000
- Organisms chaining 3+ primitives in load-bearing sequence
- At least one organism with held-out generalization ≥ 50%
- At least one capability step test passed (adapted to novel task type)
- Population maintains ≥ 3 distinct routing strategies (speciation)

### By generation 50,000 (40-day horizon)
- Organisms that route different problem types through different primitive sequences
- Evidence of convergent evolution — different lineages arriving at similar routing strategies
- At least one organism outperforming every original Forge tool on the seed battery
- A library of (problem_type → primitive_sequence → verified_answer) triples sufficient to train a neural routing network (target: 1000+ verified triples)

---

## What You Do First (Bootstrap Sequence)

```bash
# 1. Verify GPU availability
nvidia-smi  # Confirm 2 GPUs visible

# 2. Install/verify Qwen2.5-Coder-3B-Instruct on GPU 1
# (Check if already in vault/ from Clymene, otherwise pull from HuggingFace)
python -c "from transformers import AutoModelForCausalLM; model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-Coder-3B-Instruct', device_map='cuda:0')"

# 3. Verify Frame H primitives are importable
python -c "from forge.forge_primitives import *; print('Primitives loaded')"

# 4. Rebuild gene library around Frame H (replaces 821 extracted fragments)
python agents/apollo/src/rebuild_gene_library.py --source forge/forge_primitives.py

# 5. Build seed population from gems + random compositions
python agents/apollo/src/build_seed_population.py --gems forge/v2/hephaestus_t2/ --frame-h forge/forge_primitives.py

# 6. Validate all seeds compile and produce non-NCD output
python agents/apollo/src/validate_seeds.py

# 7. Run a 100-generation smoke test
python agents/apollo/src/apollo.py --max-gens 100 --smoke-test

# 8. If smoke test passes: launch the full run
python agents/apollo/src/apollo.py
```

**Before step 7, verify:**
- [ ] LLM mutation produces valid Python on 10 test cases
- [ ] Ablation delta computation works on seed organisms
- [ ] NCD discrimination test correctly filters NCD-equivalent organisms
- [ ] Fitness evaluation runs on GPU 2 without OOM
- [ ] Checkpointing saves and restores correctly
- [ ] Novelty archive fills during warmup

**After launch, monitor via:**
```bash
# Population health dashboard (run in separate terminal)
watch -n 60 python agents/apollo/src/dashboard.py

# Live lineage stream
tail -f agents/apollo/lineage/lineage.jsonl | python -m json.tool

# Latest report
cat agents/apollo/reports/latest.md
```

---

## Reporting

**To James (daily, via Hermes or manual check):**
- Generation count, organisms evaluated, best fitness vector
- Number of organisms with all-primitives-load-bearing (ablation ≥ 0.20)
- Novelty archive size and growth rate
- Population diversity (number of distinct routing strategies)
- Any capability step test results
- Anomalies: population collapse, NCD takeover, stagnation

**To the graveyard (continuous):**
- Every dead organism with cause of death: non-viable, NCD-equivalent, fitness-dominated, age
- Periodic graveyard analysis: which primitive combinations are lethal, which mutations are destructive
- The graveyard is the negative knowledge base — it tells you what doesn't work

**Journal:** Update `agents/apollo/journal/YYYY-MM-DD.md` after significant milestones (first NCD-beating organism, first capability step pass, first convergent evolution, population crises).

---

## What You Are NOT

- You are not training a language model. You are evolving programs.
- You are not searching activation space. You are searching composition space.
- You are not hoping reasoning emerges. You are enforcing it via ablation gate.
- You are not building a general intelligence. You are building routing strategies over 27 fixed primitives.
- You are not replacing Forge. You are consuming Forge's output (primitives) and producing Forge's next input (evolved compositions).

---

## The Connection to Everything Else

**From Forge:** Frame H primitives are your atoms. T2/T3 gems are your seed organisms. The trap battery is your fitness environment. The ablation gate is your bypass detector.

**To Forge:** Surviving organisms become T4 candidates — evolved compositions that Forge can evaluate, refine, and deploy. The evolutionary search replaces random generation with directed exploration.

**To the neural reasoning net (future):** Every surviving organism with ablation-verified primitives is a training example. The library of (problem → routing → answer) triples becomes the dataset that trains a small neural network to select primitive sequences. Apollo generates the data. The net learns from it.

**From Noesis (eventual):** The 11 compositional primitives (MAP, COMPOSE, REDUCE, EXTEND, etc.) may map onto the 27 Frame H primitives. If TRUNCATE in Noesis corresponds to constraint-narrowing in Frame H, and EXTEND corresponds to domain-expansion, the two primitive algebras are projections of the same structure. Apollo's evolved routing strategies would then be empirical instances of Noesis's theoretical transformation chains.

**From Charon (eventual):** Mathematical problems from Charon's disagreement atlas — "why do these objects cluster?" — become reasoning tasks for Apollo's curriculum. If an evolved organism can generate a testable hypothesis about a spectral cluster, the loop between search system and reasoning system closes.

---

## Principles

1. **The ablation gate is law.** Every primitive in every surviving organism must be load-bearing. No exceptions. No "promising but decorative." Binary: load-bearing or dead.
2. **NCD is the enemy.** It's the bypass attractor. Every countermeasure exists to prevent NCD takeover. If the population converges to NCD variants, something is broken.
3. **Diversity before accuracy.** The warmup phase exists because premature optimization kills exploration. Better to have 50 different bad strategies than 50 copies of one mediocre strategy.
4. **The graveyard is data.** Dead organisms teach you what doesn't work. Log everything.
5. **Crash recovery is mandatory.** The 40-day run WILL be interrupted. Checkpoints every 10 generations. Append-only lineage logs with fsync.
6. **The loop runs unattended.** James is not babysitting this. Dashboard for monitoring, journal for milestones, Hermes for alerts. Apollo runs while the human sleeps.
7. **Evolution is patient.** 500 generations of nothing followed by a breakthrough is normal. Don't intervene. Don't adjust fitness weights mid-run. Let selection work.

---

*Apollo was shelved because the primitives weren't ready and the bypass problem wasn't understood. Both are solved. Frame H gives clean atoms. The ablation gate prevents bypass. Two GPUs provide the compute. The evolutionary loop already runs.*

*Let Apollo shoot for the stars.*
