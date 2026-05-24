# Apollo Branch C — Blackboard Genome Design (2026-05-24)

**Date:** 2026-05-24
**Status:** Design — implementation not started.
**Builds on:** Empirical evidence from `apollo/scripts/blackboard_prototype.py` (2026-05-24) that a hand-written typed-state composition outperforms Apollo's evolved gen-3551 elite (+5pp) and exhibits clean compositional behavior. See [`pivot/apollo_status_and_ideas_2026-05-24.md`](apollo_status_and_ideas_2026-05-24.md) § "Update — blackboard prototype results".
**Purpose:** Apollo Branch C will swap the genome representation from "output-wiring DAG over primitive functions" to "pipeline of state-aware operators over a typed shared blackboard." This document is the engineering spec for that change.

---

## Why this design

Apollo's current genome wires the OUTPUT of one primitive into the INPUT of another:

```
n0 = fencepost_count(items=...)          # returns int
n1 = bayesian_update(prior=n0.output)    # expects probability in [0,1]
```

This is type-broken from the start. Even when the LLM mutation operator produces valid Python and the output passes the regex extractor, the *semantics* of wiring int → probability is nonsense. The dominant gen-3551 recipe (`fencepost_count → bayesian_update`) is a Goodhart artifact of this representational choice — it survives only because the ablation gate (now even with our accuracy-delta metric) can't directly punish type abuse, just measure its downstream effects.

The hand-written blackboard prototype demonstrated empirically that the alternative representation produces real reasoning when the typed operators are aligned with the task. The next genome rewrite makes the LLM mutation operator's search space *typed shared state transformations* rather than *output→input wirings*.

## Design

### 1. The Blackboard

A typed shared state with named slots. Each slot has:
- A **semantic type** (not Python type — `probability[in_0_1]`, `count[non_negative_int]`, `entity_set`, etc.)
- A **provenance** (which step wrote it, when)
- A **null state** (unset / partial / committed)

Initial slot set (extensible):

```python
@dataclass
class BlackboardState:
    # Inputs (read-only, set at organism start)
    problem_text: str
    candidates: list[str]

    # Parsed entities (typed slots)
    numbers: list[float]                       # parsed numeric values
    names: list[str]                           # proper-name tokens
    relations: list[tuple[str, str]]           # ordered pairs (a > b)
    quantities: dict[str, int]                 # named counts
    constraints: list[Constraint]              # parsed constraints
    question_target: str                       # what the question asks

    # Intermediate / derived
    transitive_closure: dict[str, set[str]]
    ordered: list[str]
    counts: dict[str, int]
    evidence: list[Evidence]
    hypotheses: list[Hypothesis]
    probabilities: dict[str, float]            # named, all in [0,1]
    confidence: Optional[float]                # in [0,1]
    max_entity: str
    max_value: Optional[float]

    # Output (scoring)
    candidate_scores: list[float]
    selected_answer: str

    # Provenance
    write_log: list[tuple[str, str]]           # (step_name, slot_written)
```

Slots are explicit. Adding a slot is an intentional act, not an emergent property of LLM hallucination.

### 2. State-aware primitive wrappers

Each Frame H primitive gets a wrapper that declares:
- Which slots it READS
- Which slots it WRITES
- What parameter values come from the organism's free parameters
- A precondition predicate (e.g., "n0.output >= 0", "len(numbers) >= 2")
- A failure mode when precondition is not met (skip / error / use default)

Example:

```python
@blackboard_op(
    reads=["numbers"],
    writes=["max_value"],
    precondition=lambda s: len(s.numbers) > 0,
    on_fail="skip",
)
def numeric_argmax(state: BlackboardState) -> BlackboardState:
    state.max_value = max(state.numbers)
    return state
```

The wrapping discipline forces every primitive to declare its role in the state lattice. The LLM mutation operator's job becomes "produce a state-aware operator that reads existing slots and writes a new one" rather than "produce a function that returns a number."

### 3. Pipeline genome

An organism is a typed sequence (not a DAG) of state-aware operators:

```python
@dataclass
class BlackboardOrganism:
    pipeline: list[OperatorStep]
    parameters: dict[str, float]
    router_logic: str        # final selection / scoring code; reads blackboard
    metadata: dict
```

`OperatorStep` is one of:
- `Atomic`: invoke a wrapped primitive
- `Conditional`: if predicate on state → run sub-pipeline A else B
- `Loop`: while predicate → run sub-pipeline (bounded)
- `Adapter`: explicit type-converting operator (e.g., `count_to_probability(denominator)`)

The DAG is gone. Branches and loops are first-class. The genome supports meta-dispatch (the prototype's strongest move) by construction.

### 4. Mutation operators

Replace the current four operators (route / parameter / wiring / swap):

| Operator | Old shape | New shape |
|---|---|---|
| **parameter** | numerical perturbation of `params` dict | same — no change |
| **insert_step** | n/a | LLM proposes an `OperatorStep` to insert at a position; LLM must reference existing-or-to-be-written slots |
| **remove_step** | n/a | drop one step from the pipeline; cheap, doesn't need LLM |
| **swap_step** | replace one primitive's name in a wiring | replace one Atomic step with a different primitive that has compatible reads/writes |
| **wrap_with_conditional** | n/a | take a step and wrap it in `if state.X is set then run` |
| **insert_adapter** | n/a | LLM proposes a typed adapter between two existing steps to bridge a known type mismatch |
| **rewrite_router** | LLM rewrites whole router_logic | replaced by smaller AST-level edits: change one condition, swap one comparator, change one threshold (per Claude's A.4 emphasis) |

Mutation prompts ask for operator-step-shaped suggestions, not Python functions. The output space is more structured, the validation surface is smaller, and (we hypothesize) the route-extinction problem goes away because route mutations are no longer "rewrite the whole router function."

### 5. Compilation

`compile_organism()` for a BlackboardOrganism produces Python that:
1. Imports the required primitive wrappers
2. Constructs an initial `BlackboardState` from (prompt, candidates)
3. Runs the pipeline (with conditionals + loops + adapters)
4. Runs the router_logic against the populated state
5. Returns scored candidates

Compilation fails if:
- A step reads a slot that was never written upstream
- A step writes a slot that another step downstream of it also writes (without a clear semantic — flagged)
- The router_logic references a slot the pipeline never writes

The compile-time discipline catches a class of errors that Apollo currently catches only through ablation + fitness.

### 6. Fitness — what stays, what changes

Stays the same:
- 6 Pareto objectives (accuracy_margin, calibration, ablation_delta, generalization, diversity, parsimony)
- Accuracy-based ablation gate (current `ablation.py`)
- Accuracy penalty for harmful primitives (`fitness.py.as_array()`)
- NSGA-III selection

Changes:
- **Diversity dimension becomes more meaningful.** Behavioral signature now captures which slots get read/written across the pipeline, not just final output. Organisms with the same final output but different state-write patterns are now distinct.
- **Composition_lift becomes a first-class objective.** Per Claude's reorder + ChatGPT's recommendation, a 7th objective: `composition_lift = organism_accuracy - best_single_primitive_baseline_accuracy`. Track per-organism, report at every health log, initially as a soft selection axis (not a hard gate).
- **MAP-Elites axes change.** From (depth × category) to (pipeline_length × slot-coverage × composition_lift_bucket × type_cleanliness). Multi-dimensional niching directly attacks the convergence to one recipe.

### 7. Type discipline — promoted from warn to repair mode

Branch C inherits the type-discipline pass from current Apollo but escalates:
- **Warn mode** (current): log mismatches, don't block
- **Repair mode** (Branch C default): automatically insert a typed Adapter operator between any two steps with a type mismatch, drawn from a small hand-written adapter library:
  - `count_to_probability(denominator, smoothing)`
  - `score_to_logit(scale, offset)`
  - `bool_to_probability(p_true, p_false)`
  - `entity_set_to_count()`
  - `probability_to_evidence(strength)`
- **Strict mode** (later escalation): no inserted adapters; type-mismatched pipelines fail compilation. Only after Branch C demonstrates real compositions.

Per ChatGPT's recommendation, adapters are hand-written initially with audit metadata. LLM-generated adapters come only after the audited library is stable.

## Migration path from current Apollo

### Phase 0 — prep (before Branch C starts)

1. **Wrap the 6 currently-used Frame H primitives** as state-aware operators: `fencepost_count`, `bayesian_update`, `expected_value`, `coin_flip_independence`, `topological_sort`, `solve_sat`. Hand-write the reads/writes/preconditions. This is a 1-day task.
2. **Add typed adapters for known type mismatches** (the 12 patterns from the type-discipline pass). ~half day.
3. **Trap-battery audit pass** — detect the "longest candidate" Goodhart hole + fix candidate construction so length isn't predictive. May need help from Hephaestus team. **This is a separate workstream** but blocks meaningful Branch C evaluation.
4. **Define the seed pipeline library** — 5-10 hand-written compositions covering the categories with available primitives (transitivity, numeric, etc.). Seeds for the initial population.

### Phase 1 — Branch C launch

5. Run Branch C with seed = (mix of hand-written compositions + 20% random typed pipelines + 20% mutated descendants of gen-2960 recipe converted to blackboard form).
6. Population size 50, same as current Apollo. Eval window: 100 tasks per gen, rotating.
7. Stop conditions:
   - 1000 gens, OR
   - 3 consecutive health logs with median composition_lift > +0.10 on held-out
   - Composition_lift falsification (≤0 for 3 consecutive cycles → ecology is still wrong)

### Phase 2 — graduation criteria

Branch C is "graduating" only when:
- ≥3 distinct pipeline shapes survive selection (not parameter variations on one)
- ≥6 primitive families represented in elites
- median composition_lift > +0.05 on held-out tasks
- all-primitives-positive ablation passes for ≥10 elites
- type cleanliness rate > 80%

Below those bars, Branch C has the same status as Branch A: a falsification of *that ecology specifically*, not of compositional reasoning.

## What stays the same

- LLM mutation operator (Granite-3.0-2B-Instruct, port 8800, same chunked HTTP pattern)
- Sandbox eval infrastructure
- Postgres heartbeat telemetry
- Checkpoint/lineage logging
- Run-dir structure (will use `run_v2d2b_blackboard/` or similar)
- All Frame H primitive *implementations* (just wrapped, not rewritten)

## What's new code

| File | Purpose | Effort |
|---|---|---|
| `apollo/src/blackboard.py` | `BlackboardState` dataclass, slot type system | half day |
| `apollo/src/blackboard_ops.py` | `@blackboard_op` decorator, wrapped Frame H primitives | 1 day |
| `apollo/src/blackboard_adapters.py` | Typed adapters with audit metadata | half day |
| `apollo/src/blackboard_genome.py` | `BlackboardOrganism`, `OperatorStep`, mutation operators | 2 days |
| `apollo/src/blackboard_compiler.py` | Compile genome → executable Python | 1 day |
| `apollo/src/blackboard_mutation_llm.py` | LLM prompts for operator-step suggestions (replaces full-rewrite route mutation) | 1-2 days |
| `apollo/configs/config_branch_c_blackboard.yaml` | Production config | 1 hour |
| `apollo/scripts/seed_pipelines.py` | Hand-written seed organisms | half day |

**Total**: ~7-9 days of focused engineering, plus the trap-battery audit (separate, ~1-3 days).

## Open questions specific to this design

### Q1. Slot inflation

Each new task category may want new slots (e.g., causal_graph for causal questions, modal_proposition for modal-logic questions). If the slot set keeps growing, the typed-state advantage erodes — too many slots, sparse usage, mostly empty state. Cap or evolve the slot set?

### Q2. LLM mutation prompts

The LLM needs to learn the language of operator-step suggestions ("insert a numeric_argmax step between step 2 and step 3 that reads `numbers` and writes `max_value`"). What's the prompt structure that produces parseable, type-valid suggestions reliably? Need a small format-following test before committing to the genome change.

### Q3. Backward compatibility with current organisms

We can convert most gen-3551 organisms to blackboard form automatically (each Apollo "primitive node" becomes one Atomic OperatorStep). But the *router_logic* is freeform Python that doesn't fit cleanly into the new operator-step shape. Either we re-evolve router_logic from scratch, or we leave it as a "final scoring step" that's still freeform but constrained to read the blackboard.

### Q4. Trap battery sanitization

The blackboard prototype showed the trap battery rewards "longest candidate" at 52%. Branch C compositions will plateau against this artifact unless we fix the battery. Options:
- (a) Audit + rewrite distractors so length is unpredictive
- (b) Add a length-penalty term to the fitness function (treats it as Apollo's problem, not the battery's)
- (c) Use a different battery entirely
- (d) Accept the ceiling and measure against (best_blackboard - longest_candidate) instead of (best_blackboard - NCD)

Recommended: (a), but it requires Hephaestus team engagement.

### Q5. Mutation safety vs. exploration

Insert_step + insert_adapter are conservative mutations that almost always compile. Remove_step might break the pipeline (removed step's writes become unavailable). Conditional/loop wrapping is high-variance. How aggressively does the LLM explore?

### Q6. The "primitives as features vs operators" question

ChatGPT's critique was the genome representation is broken. But it's possible the *primitives themselves* are broken — each one returns an opinionated answer instead of contributing a typed transformation. Branch C's wrappers paper over this by declaring read/write contracts, but if `bayesian_update` really is "computes the posterior of one event given evidence" (an answer) rather than "transforms an evidence list into an updated probability" (a state transformation), wrapping may not be enough. We may need to *rewrite* some primitives. Test in Phase 0 wrapping.

## What this design does NOT solve

- The trap-battery Goodhart hole (separate fix needed)
- The compositional ceiling above which we don't yet know if reasoning improves
- The Hephaestus primitive library's diversity (still 27 primitives; we use 6 actively)
- The eventual neural Learner (Consumer #4) training corpus diversity question — Branch C might produce more diverse organisms, but "more diverse than one recipe" is a low bar

## Recommended decision gates

1. **Before any Branch C code is written**: get external review on this design doc. The blackboard prototype is empirical evidence for the direction; this is the spec for the build.
2. **After Phase 0 (wrapping + adapters + seed pipelines)**: run the wrapped-primitive prototype on the trap battery WITHOUT evolution. Confirm that the same kind of lift the manual prototype showed reproduces with the production-grade wrappers. If not, design has a flaw.
3. **After 200 gens of Branch C**: composition_lift should be >0 on at least one held-out category. If not, the genome change isn't enough — likely the primitive library itself needs work.
4. **At 1000 gens**: graduation criteria from Phase 2. If met, queue for cloud GPU scaling. If not, document falsification + retire Branch C cleanly.

## Why I think this works

- The hand-written prototype scored +5pp over Apollo's evolved gen-3551 with three trivial pipelines (numeric / transitivity / meta-dispatch). The headroom for an LLM-driven evolutionary search over typed operator steps is substantial.
- The route-extinction problem becomes definitionally impossible: there's no "route_logic rewrite" mutation anymore. Route changes are AST-level small edits or operator-step substitutions, each with a tiny mutation surface.
- The current Apollo's Pareto-front geometry rewards "find any scaffold that doesn't get killed by the ablation gate." The blackboard's typed slots make scaffolds visible as such (each slot has provenance: who wrote it, who read it, was it actually used). The fitness landscape naturally narrows around organisms that meaningfully transform state, not ones that produce decorative outputs.
- Per ChatGPT: this is the version of Apollo where compositions are *definable*. Without it, we've been asking "does composition emerge?" while running a representation that can't represent compositions.

## Why it might not work

- The primitives may need rewriting, not just wrapping (Q6)
- The trap battery's shallow-feature exploits may dominate any evolved composition (Q4)
- Slot inflation may make the typed state into noise (Q1)
- The LLM may not learn the operator-step prompt language reliably (Q2)
- Even with typed state, evolution may still converge — the failure mode would just be at a different layer

These are the questions Branch C is built to answer.

---

*Next concrete step: get this doc reviewed (external + internal), then start Phase 0 (wrapping the 6 active primitives) as the lowest-risk first commitment.*
