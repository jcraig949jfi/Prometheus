# Apollo Phase 1 — Framing for External Review (2026-05-27)

**Date:** 2026-05-27
**Purpose:** Hand-off packet for external reviewers (Gemini / ChatGPT / Claude / DeepSeek / anyone else) ahead of Apollo's Branch C Phase 1 commitment. Asks for sharp engagement on six specific Phase 1 design questions, with enough background that a reviewer arriving cold can give material feedback.
**Audience:** Smart outsiders. Assumes no prior exposure to Prometheus.
**Length warning:** Long. The user asked us to err on the side of too much detail.

---

## Part 1 — What Prometheus is, and why

Prometheus is a multi-machine research project trying to produce structured reasoning artifacts that an eventual neural network ("the Learner") can be trained on. The animating frame is from David Silver's argument that LLMs as currently scaled are a dead end for genuine reasoning, and that real reasoning capability has to come from first-principles self-discovery rather than imitation of human text.

The project is organized as a small constellation of named agents, each running on a separate physical machine, each producing a different kind of artifact:

- **Hephaestus** (M3) — *forge*. Generates and ablation-tests atomic reasoning primitives. As of writing it has 1,945 tools across 9 forge versions; the canonical subset Apollo uses is "Frame H" (27 primitives across 8 categories: logic, probability, graph/causal, constraints, arithmetic, temporal, belief, calibration).
- **Apollo** (M2, this document) — *evolutionary search*. Composes Hephaestus's primitives into routing graphs via an evolutionary loop with NSGA-III multi-objective selection, LLM-driven mutation, and MAP-Elites archiving.
- **Ergon** (in development) — *failure-routing learner*. Will predict which test will kill a claim, which failure-mode signature a proof attempt exhibits, what repair class is required.
- **Aporia** — *substrate-shaped Deep Research*. Mines structured claims from external research with falsification metadata attached.
- **Aletheia / Charon / Mnemosyne / Nous** — various roles around critique, indexing, and aggregation.
- Various forge/auditor sessions whose details aren't load-bearing here.

The eventual deliverable everyone is converging on: a corpus of `(problem_type, primitive_sequence, verified_answer, failure_signature)` records — both the successes Apollo evolves and the failures it leaves behind. The Learner trains on this corpus.

**The reasoning ladder.** A framing the project has been using to talk about what each agent produces:

```
R1-R6:   Atomic mechanisms       — Hephaestus forges these primitives
R7+:     Compositions            — Apollo evolves these from the primitives
R-final: Learned routing         — eventual Learner trained on Apollo's output
```

Climbing the ladder is non-trivial — each rung is its own engineering problem with its own falsification conditions. Apollo specifically is testing the second rung: are *compositions* of these primitives a real thing, or do they reduce to "lucky single-primitive guesses with decorative scaffolding"?

That question — "is composition real for this gene library on this task curriculum under this selection geometry?" — is what we've been answering empirically for the past three weeks.

## Part 2 — The North Star + two core doctrines

The project's North Star is sometimes summarized as: *compress coordinate systems of legibility, not laws.* The goal isn't to discover universal mathematical truths; it's to construct coordinate systems under which the right structure becomes detectable. Apollo's role in that frame is "build the coordinate system where genuine reasoning composition shows up as a detectable signal."

Two doctrines govern how we test that:

### Doctrine #1 — Falsification-first tier claims

*A system does not occupy a reasoning tier because its output resembles that tier. It occupies the tier only if the relevant mechanism survives perturbation, beats lower-tier baselines, and fails in the tier-predicted way.*

Every tier claim requires a falsification test. "This system reasons compositionally" is meaningless without a test that would break the claim.

### Doctrine #2 — Failure-signature reading (gradient over verdict)

*Reasoning capability is read from the gradient of failure, not the binary of success. Every measurement instrument has error; every "passing" system fails in shaped ways and every "failing" system fails in shaped ways. The shape encodes the mechanism. The discipline is to MINE the error structure, not collapse it into a summary statistic.*

This doctrine was articulated explicitly on 2026-05-25 after a null-slot ablation experiment produced a "4 load-bearing, 4 decorative, MIXED" verdict-line that erased the four distinct failure signatures hiding underneath. The four signatures — recompute-bypass, side-output, redundant-encoding, atomic-with-output — each pointed to a separate design correction. The summary statistic destroyed all of them.

Both doctrines apply to everything that follows.

## Part 3 — How Apollo got here (three weeks of arc)

Apollo had been running with a known compositional premise for months. The premise was that LLM-guided mutation of routing graphs over Frame H primitives, evaluated against a 108-category trap battery, with NSGA-III selection on a 6-dimensional fitness vector (accuracy, calibration, ablation delta, generalization, diversity, parsimony), would produce organisms whose compositions exceed any individual primitive's accuracy.

**The April 9 anomaly.** Apollo's organisms at gen 686 carried a metric called `llm_alive=0`. Zero organisms in the surviving population had LLM-derived mutations in their lineage. The original interpretation: LLM mutations are not viable in this fitness landscape.

**Bug #1 — the LLM-output validation issue.** A 2026-05-19 four-model bake-off (Qwen-7B-Coder, Phi-4-mini-Instruct, IBM Granite-3.0-2B-Instruct, DeepSeek-Coder-1.3B) showed Qwen's outputs were failing Apollo's regex/AST code-extractor 99% of the time. Granite-3.0-2B passed it 92%+ of the time. Granite became Apollo's primary mutation LLM.

**Bug #2 — the lineage-overwrite issue.** With Granite installed, `llm_alive` still read 0 for ~870 generations. Tracing the offspring pipeline revealed that `drift()` in `mutation.py` was overwriting `mutations_applied = ['drift']` (full replacement) on every offspring after `mutate_batch` returned. A one-line fix (append instead of replace) made `llm_alive` jump from 0 to 24/50 at gen 2650. Both bugs combined had been hiding Apollo's actual selection dynamics for months.

**The falsification.** With both bugs fixed, a single-primitive baseline matrix on five top elites at gen 2960 showed 0/5 compositional lift over the best of their constituent primitives. The dominant "evolved" recipe `fencepost_count → bayesian_update` (which carried 50% of the population) had **zero** lift — in fact in 3/5 cases the single primitive alone was strictly better than the elite, and in one case reversing the operator order from `fencepost_count → expected_value` to `expected_value → fencepost_count` improved accuracy by +12pp. The "evolved" recipe was decorative scaffold around single-primitive performance, type-violating (integer outputs wired into probability inputs), and the ablation gate had been measuring `output_change_fraction` (whether outputs differed under primitive removal) rather than `accuracy_delta` (whether removing the primitive dropped correctness). 500 more generations of harder selection (we patched ablation to use accuracy_delta and added an accuracy penalty for harmful primitives) produced cleaner Goodhart, not real composition.

**External reviewer convergence.** Three external reviewers (Gemini, ChatGPT, DeepSeek) and a fourth (Claude) engaged with the falsification. They converged on five points: the falsification is ecology-specific not universal; the bottleneck is the genome representation, not LLM quality; the route mutation operator is broken (zero LLM-derived route mutations survived across the entire run); the trap battery itself has a Goodhart hole (a "pick the longest candidate" baseline scores 52% on it without reasoning); and ChatGPT's deepest critique — *the primitives may be answer-producing heuristics by nature rather than typed transformations over a shared state; wiring outputs into inputs is semantically broken from the start*.

**The blackboard prototype.** A hand-written typed-state composition tested on the trap battery beat Apollo's evolved gen-3551 elite by +5pp (41% vs 36%), confirming ChatGPT's representational critique. The blackboard genome (state as a typed object with named slots; operators read/write slots rather than wire outputs into inputs) became the proposed Branch C architecture.

**The null-slot ablation.** A 2026-05-25 follow-up test corrupted each typed slot in the prototype right before its downstream read. Result: 4 slots load-bearing, 4 "decorative" — but the four decoratives had four distinct signatures (recompute-bypass, side-output, redundant-encoding, atomic-with-output), each pointing to a specific Branch C design correction. This experience articulated Doctrine #2 explicitly.

**That brings us to today.** Phase 0 just shipped. Phase 1 is the next decision.

## Part 4 — What Phase 0 built (deep technical detail)

Phase 0 is the falsification infrastructure for Branch C. Four deliverables, all committed to `github.com/jcraig949jfi/Prometheus` as of commit `85c04d26`. Per Doctrine #2, every Phase 0 output reports failure signatures rather than pass/fail summaries.

### Deliverable 1 — Clean canary suite

50 length-balanced tasks across 7 categories:

| Category | N |
|---|---|
| numeric_comparison | 10 |
| numeric_stated_premise | 10 |
| transitivity (3-5 entities) | 10 |
| all_but_n (counting) | 5 |
| temporal_ordering | 5 |
| vacuous_truth | 5 |
| consistency_check | 5 |

For each task, the four candidate strings are deliberately padded so their lengths are within ~15-30 characters of each other. The candidate order is randomized per task. The result: a "longest candidate" baseline scores **22%** on this canary (close to chance for 4-way multiple-choice) versus **52%** on the original trap battery.

The original trap battery's longest-candidate hack scored higher than Apollo's evolved gen-3551 elite (36%) on the same battery — meaning the battery was actively hiding capability behind a shallow feature. The canary doesn't have that hole. When Apollo's prototype dispatch composition was evaluated side-by-side, it scored **56% on the canary vs 41% on the trap battery** — the canary surfaces +14pp more reasoning capability than the trap battery reading suggested.

Implementation: `apollo/scripts/gen_clean_canary_v01.py` generates the suite programmatically with deterministic seed; the suite itself is at `apollo/data/clean_canary_v01.json` with audit metadata (longest-is-correct frequency, shortest-is-correct frequency, by-category breakdown).

### Deliverable 2 — Three primitive rewrites (state transformers, not answer-producers)

Three of Hephaestus's Frame H primitives are answer-producing heuristics by nature. Wrapping them in `@blackboard_op` decorations declares typed reads/writes but doesn't change the underlying semantics (the function still takes scalars and returns a scalar answer).

Phase 0 rewrites them as genuine state transformers in `apollo/src/blackboard_ops_v2.py`:

- **`evidence_updater`** (rewrite of `bayesian_update`). Reads `hypotheses, evidence, probabilities` (the named hypothesis lattice). For each evidence record (`{hypothesis, likelihood, false_positive, source}`), updates that hypothesis's posterior. Writes back to `probabilities` and updates `confidence` (max posterior across hypotheses). The whole lattice is the unit of transformation, not a single Bayesian arithmetic operation.

- **`entity_counter`** (rewrite of `fencepost_count`). Reads `names, relations, quantities`. Writes a typed `counts` dict where each entry carries provenance: `{'count': N, 'provenance': 'len(names)', 'fencepost_adjusted': N+1}`. Also writes evidence records. Downstream operators see a structured count object, not a bare integer.

- **`distribution_reducer`** (rewrite of `expected_value`). Reads `probabilities`. Preserves the distribution as a first-class object and writes summary statistics (mean position, variance, mode, entropy, total mass) as a new evidence record. Downstream operators see both the distribution and the summary; the distribution isn't collapsed.

The pattern: a rewrite reads a typed collection and writes a typed collection. Never a scalar answer.

### Deliverable 3 — Wrapper protocol corrections (the four signatures, statically caught)

The null-slot ablation found four distinct failure signatures in the prototype. Phase 0 builds static checks into `apollo/src/blackboard.py` to catch each one at compile-time:

- **`verify_declared_reads_are_actual_reads(op)`** — AST inspection of the op's source. If the op declares `reads=['max_value']` but the source never references `state.max_value`, flags **`recompute-bypass`** signature. The op may be recomputing the value from upstream slots, defeating the typed-state discipline.

- **`verify_single_output_preferred(op, hard_limit=4)`** — Soft-warns at ≥2 writes, hard-fails at ≥4. Terminal scorer ops (name starts with `score_` or `select_`) are exempt because writing `candidate_scores + selected_answer` together is structurally atomic. Flags **`side-output`** signature.

- **`verify_no_redundant_encoding(pipeline)`** — Hand-declared encoding groups (e.g., `{names, relations}`). If any op writes ≥2 slots from the same group, flags **`redundant-encoding`** — one is recoverable from the other.

- **`mid_step_corruption_test(op, state, corrupt_slot, value)`** — Runs the op twice: once baseline, once with the slot corrupted *during execution* (before the op reads it). Returns **`load-bearing-input`** if outputs differ, **`decorative-input`** otherwise. This closes the atomic-with-output blind spot the null-slot ablation had: when a slot is written on the same step as the answer, corrupting it after the op can't separate the slot from the answer; corrupting *before* the op reveals whether the op actually reads the slot.

- **`audit_pipeline(pipeline)`** — Runs all four checks and returns a per-signature dict, not a pass/fail. The return shape is what Phase 1 will consume.

These checks immediately surfaced the v1 prototype's actual structural issues without running it: `parse_names_and_relations` flagged for both side-output and redundant-encoding; `op_transitive_closure` flagged for side-output (writes 3 slots). The static analysis catches what the ablation found dynamically.

### Deliverable 4 — Data-flow ablation as a fitness term

`apollo/src/dataflow_fitness.py` exports `compute_dataflow_fitness(pipeline, tasks)`. For each slot any op in the pipeline writes, it constructs a modified pipeline that zeros that slot right after it's written, evaluates baseline-vs-modified on the task set, and classifies the slot's signature:

- **`load-bearing`** (`Δacc ≥ 0.05`) — zeroing this slot drops accuracy meaningfully.
- **`marginally-load-bearing`** (`0.01 ≤ Δacc < 0.05`) — weak contribution.
- **`side-output`** — `Δacc < 0.01` AND the writer op also writes other slots. Lesson: the op is doing too much.
- **`atomic-with-output`** — `Δacc < 0.01` AND the slot is `candidate_scores` / `selected_answer`. Lesson: instrument blind spot.
- **`decorative-or-recompute-bypass`** — `Δacc < 0.01` and no co-write structure. Lesson: downstream isn't reading or recomputes.
- **`not-written-by-pipeline`** — pipeline doesn't include any op that writes this slot.

The return shape is:

```python
{
    "baseline_acc": float,
    "dataflow_score": float,        # scalar, [0, 1], usable as Pareto axis
    "load_bearing_ratio": float,    # equivalent meaning, explicit name
    "avg_positive_delta": float,
    "n_load_bearing": int,
    "n_marginal": int,
    "n_tracked_slots": int,
    "per_slot_signatures": [
        {"slot": "...", "signature": "...", "delta": float, "lesson": "..."},
        ...
    ],
}
```

Phase 1 fitness will use `dataflow_score` as a scalar Pareto axis alongside the existing `ablation_delta`. The two are correlated but distinct: `ablation_delta` says "this primitive contributes to correct answers"; `dataflow_score` says "this primitive's typed-state writes are causally read downstream." Both must be positive for a Pareto-front organism.

Critically, the `per_slot_signatures` is the artifact Phase 1 logs structurally — every promoted organism gets a per-slot reading. Selection consumes the scalar; downstream analyzers (and Ergon eventually) consume the signatures.

### The Phase 0 validator

`apollo/scripts/phase0_validate.py` runs all four deliverables end-to-end and emits one structured report. The bottom-of-report "triage signal" is explicitly NOT a verdict — it's a list of next moves with their implied signatures. Per Doctrine #2.

## Part 5 — What Phase 0 validation revealed (gradients, not verdicts)

Running the validator surfaced six findings, each a separate move:

1. **Canary surfaces capability the trap battery hides.** Prototype dispatch on canary = 56%; on trap battery = 41%. The trap battery's longest-candidate ceiling (52%) is masking real reasoning signal.

2. **Wrapper audit caught the v1 prototype's signatures statically** — without running anything: `parse_names_and_relations` flagged as both side-output (2 writes) and redundant-encoding (names recoverable from relations). `op_transitive_closure` flagged as side-output (3 writes).

3. **Data-flow fitness on canary: `load_bearing_ratio = 0.33`** — only 2 of 6 slots are genuinely load-bearing. The 4 non-load-bearing slots split: 3 side-output, 1 decorative.

4. **Mid-step corruption test diagnoses the recompute-bypass bug correctly.** `score_by_max_value` reads `numbers` (output differs when corrupted → load-bearing-input) but ignores `max_value` (output unchanged when `max_value=999` deliberately wrong → decorative-input). This confirms the bug we previously found by other means and validates the new instrument.

5. **v2 primitives produce typed-state outputs.** All three rewrites tested: `entity_counter` produces `{counts: {'names': {count: 3, provenance: 'len(names)', fencepost_adjusted: 4}}}`. `evidence_updater` updates the lattice (H1: 0.5 → 0.9, H2: 0.5 unchanged). `distribution_reducer` adds a summary record with entropy = 0.802 for a {A: 0.7, B: 0.2, C: 0.1} distribution.

6. **Open question Phase 0 leaves for Phase 1**: do we start with v1 wrapped pipelines (battle-tested, all known signatures documented) or v2 rewritten primitives (semantically cleaner, evolutionary search behavior unknown)?

## Part 6 — What Phase 1 entails

Phase 1 is the actual evolutionary run on the new substrate. ~5-7 days of compute. The proposed shape:

### Genome representation

An organism is a typed sequence (not a DAG) of state-aware operators, plus parameters, plus a terminal router:

```python
@dataclass
class BlackboardOrganism:
    pipeline: list[OperatorStep]    # ordered list of typed ops
    parameters: dict[str, float]    # free numerical parameters
    router_logic: str               # final scoring code; reads blackboard
    metadata: dict                  # provenance, lineage, etc.
```

`OperatorStep` is one of: `Atomic` (invoke a wrapped primitive), `Conditional` (if predicate on state → run sub-pipeline A else B), `Adapter` (insert typed conversion between two steps with a type mismatch). The DAG-with-output-wiring representation that the gen-3551 falsification killed is gone.

### Mutation operators (replace the v2c four)

| Operator | Old shape | New shape |
|---|---|---|
| parameter | numerical perturbation | unchanged |
| insert_step | n/a | LLM proposes an `OperatorStep` to insert at a position; must reference existing-or-to-be-written slots |
| remove_step | n/a | drop one step from the pipeline; cheap, no LLM |
| swap_step | replace primitive name in wiring | replace one Atomic step with a compatible-reads/writes alternative |
| wrap_with_conditional | n/a | take a step and wrap it in `if state.X is set then run` |
| insert_adapter | n/a | LLM proposes a typed adapter between two existing steps |
| rewrite_router | LLM rewrites whole router_logic | AST-level edits: change one comparator, swap one threshold, add one guard clause |

The full-rewrite route mutation that produced zero LLM-derived survivors in the gen-3551 run is gone. Per Claude's emphasis: the smaller the mutation surface, the more often the offspring survives.

### Fitness (Pareto objectives)

| Axis | Existing | New |
|---|---|---|
| accuracy_margin | ✓ | now measured primarily on the canary, secondarily on the trap battery |
| calibration | ✓ | unchanged |
| ablation_delta | ✓ | already accuracy-based as of 2026-05-22 |
| generalization | ✓ | held-out canary subset |
| diversity | ✓ | unchanged |
| parsimony | ✓ | unchanged |
| **dataflow_score** | new | per-organism `load_bearing_ratio` from `dataflow_fitness.py` |
| **composition_lift** | new | organism accuracy − best single-primitive baseline accuracy |

`dataflow_score` and `composition_lift` are new. The first directly punishes decorative slots; the second directly punishes organisms that don't lift over their components.

### MAP-Elites cells

Behavioral dimensions for the archive:

- pipeline length: 1, 2, 3, 4, 5+
- primitive families used (logic / probability / graph / arithmetic / temporal / constraints / calibration / meta)
- composition_lift bucket: negative / zero / small-positive / strong-positive
- type cleanliness: dirty / adapter-clean / native-clean

Cells filled by an organism are determined by its declared structure, not by surface output. Per the reasoning ladder, MAP-Elites diversity should reflect mechanism diversity.

### Seed population

Mixed (per ChatGPT's recommendation, not pure-from-gen-2960):
- 20% hand-written compositions (e.g., the v2-based `entity_counter → evidence_updater → distribution_reducer → score` chain)
- 30% historical non-dominant survivors from gen-3551 (converted to blackboard form)
- 30% random typed pipelines (1-3 ops, randomly chosen from OP_REGISTRY_V2)
- 20% gen-2960 elite descendants (converted, quarantined from dominating)

### Stop conditions / graduation criteria

Phase 1 terminates at one of:

1. **1000 generations** unconditionally (time budget)
2. **Composition-lift falsification**: median composition_lift ≤ 0 for 3 consecutive 100-gen windows → falsified, terminate
3. **MAP-Elites collapse**: archive coverage remains below 8/35 cells after 500 gens → ecology still wrong, terminate

Graduation (Phase 1 succeeded) requires:
- ≥3 distinct pipeline shapes in elites (not parameter variations on one)
- ≥6 primitive families represented
- Median composition_lift > +0.05 on held-out canary
- All-primitives-positive ablation passes for ≥10 elites
- Type cleanliness rate > 80%

ChatGPT's stronger 7-point checklist for a single graduated elite (any one elite meeting all 7):
1. Contains ≥3 non-terminal operators
2. ≥2 intermediate slots causally load-bearing under ablation
3. Reordering operators breaks performance in predicted ways
4. Beats single-primitive baseline AND terminal-only-blackboard AND length-heuristic baseline
5. Loses to hand-written prototype on at least one held-out family (sanity check that we're evolving, not rediscovering hand-craft)
6. Transfers to a structurally similar, surface-different task family
7. Failure mode interpretable from state trace

### Islands (optional, deferred unless single-population stalls)

Per ChatGPT's recommendation: 5 sub-populations with different pressures (size-2-exploit, size-3+-forced-composition, typed-only, logic-heavy, graveyard-repair). Migration gated by positive held-out composition_lift. We're not committing to this in Phase 1; we'd rather see the single-population dynamics first.

### What stays the same

- LLM mutation operator (IBM Granite-3.0-2B-Instruct on M2's single GPU)
- Sandbox eval infrastructure
- Postgres heartbeat telemetry
- Checkpoint/lineage logging
- Frame H primitive *implementations* (the v2 rewrites are additive; v1 wrappers remain available)

## Part 7 — Six questions for reviewers

Material engagement on any of these is useful. Pointed answers on one are better than vague answers on all.

### Q1. Should Phase 1 start with v1 or v2 primitives?

The v2 rewrites (`evidence_updater`, `entity_counter`, `distribution_reducer`) are semantically cleaner — they read collections, write collections, preserve structure rather than collapsing to answers. But evolutionary search over v2 ops is untested. The v1 ops are battle-tested and their failure signatures are now characterized.

A possible compromise: hand-write a v2-based 3-op composition (e.g., `parse_relations → entity_counter → score_from_counts`), run the null-slot ablation against the canary, and pick v2 if it produces 0 protocol signatures + a `load_bearing_ratio` meaningfully above 0.33. ~1 hour. We can do this test as the first move of Phase 1 if you bless it.

**Question**: is the v2-prototype-test enough evidence to commit, or is there a stronger pre-Phase-1 gate we should add?

### Q2. Are 3 primitive rewrites enough, or do we need to rewrite more?

We rewrote the three that the reviewer convergence identified as worst-offenders (`bayesian_update`, `fencepost_count`, `expected_value`). The other 24 Frame H primitives are still in their v1 wrapped form. ChatGPT's classification scheme suggested splitting all 27 into four buckets (transformer / adapter / scorer / quarantine).

Phase 1 with only 3 rewrites means the LLM mutator will mostly compose using v1 ops; v2 ops will be available but a minority. **Question**: is that ratio acceptable, or should Phase 0 extend to classify + rewrite more primitives before Phase 1 starts?

### Q3. Should wrapper protocol corrections be hard gates or just logged signatures?

`audit_pipeline` returns per-signature warnings (recompute-bypass, side-output, redundant-encoding). Currently these are *logged* — they don't block compilation. In Phase 1 we could:

- (a) Keep them logged; let evolution discover that signatures correlate with low dataflow_score and learn to avoid them organically
- (b) Hard-block compilation on certain signatures (`recompute-bypass` always fails, `redundant-encoding` always fails, `side-output` warns)
- (c) Soft-penalty in fitness — each warning subtracts a small amount from a Pareto axis

**Question**: which is right? (a) maintains the most search freedom; (b) prevents the obvious failure modes from ever appearing; (c) is a middle ground. We lean (c) but want pressure-tested.

### Q4. What's the right prompt structure for LLM operator-step suggestions?

The LLM has to learn the language of "insert an Atomic step that reads `[names, relations]` and writes `counts`" or "insert a Conditional step that wraps `op_transitive_closure` with predicate `len(state.relations) > 0`." Free-form Python doesn't fit this shape. Constrained DSL output would.

**Question**: what's a prompt structure that produces parseable, type-valid suggestions reliably? Is there prior work on LLM-driven evolutionary search over typed-DSL programs we should be looking at (beyond AlphaEvolve / FunSearch / CodeEvolve / OpenELM, all of which we've reviewed)? The LLM's instruction-following discipline is what determines whether Phase 1's mutation pipeline is viable.

### Q5. dataflow_score vs ablation_delta — Pareto interaction

We now have two slot/primitive-level fitness signals:

- `ablation_delta` (from 2026-05-22 work): per-primitive accuracy drop when the primitive is removed
- `dataflow_score` (from Phase 0): per-slot load-bearing ratio under data-flow ablation

These are correlated but not identical. An organism could have `ablation_delta > 0` (primitives contribute to correctness) but `dataflow_score < 0.3` (intermediate slots aren't load-bearing, even though the primitives are). The reverse is harder to construct but possible.

**Question**: in NSGA-III with both axes, do they compete, complement, or produce confusing Pareto fronts? Should one dominate the other (e.g., `dataflow_score` only matters if `ablation_delta > threshold`)?

### Q6. Pre-registered Phase 1 falsification — is 1000 gens enough?

Per Doctrine #1, Phase 1 must have a pre-registered falsification condition. We've named two stop-conditions (composition-lift ≤ 0 for 3 windows; MAP-Elites coverage < 8/35 after 500 gens) and one graduation condition (5 criteria). The 1000-gen budget is bounded; the prior Apollo run consumed 3551 gens of compute and a lot of debugging time.

**Question**: are these stop-conditions sharp enough to call Phase 1 "falsified" without ambiguity? Should we add a fourth (e.g., "if the LLM mutator's instruction-following degrades below 80% over a 100-gen window, abort because the substrate isn't ready")? And: what's the cheapest possible falsification — what could we run *before* 1000 gens that would already commit us to "falsified, restart with different architecture"?

---

## Part 8 — Code + data pointers

All in `D:\Prometheus` / `github.com/jcraig949jfi/Prometheus` (private repo; request access if you need to dig):

**Phase 0 build (this packet's central artifact):**
- `apollo/scripts/gen_clean_canary_v01.py` — canary generator
- `apollo/data/clean_canary_v01.json` — 50-task canary suite + length-balance audit
- `apollo/src/blackboard.py` — typed-state class + 4 wrapper protocol functions
- `apollo/src/blackboard_ops_v2.py` — 3 rewritten primitives
- `apollo/src/dataflow_fitness.py` — slot-causal-load fitness function
- `apollo/scripts/phase0_validate.py` — end-to-end validator

**Prior artifacts (context, all on previously-shared public Gists):**
- Apollo Status + Ideas (2026-05-24): https://gist.github.com/jcraig949jfi/57fa41ca3f805599b9db8e2949e3b412
- Branch C Blackboard Design (2026-05-24): https://gist.github.com/jcraig949jfi/bbcc1b38542093eceef43b7f6df682b6
- Reasoning Ladder v0.1 (revised 2026-05-25 with Doctrine #2): https://gist.github.com/jcraig949jfi/c5ea97eb531256c54d6641e0127342ce
- Review Packet 2026-05-25: https://gist.github.com/jcraig949jfi/4bba26b9b4d62755fb204344766a91b3

**Reproduction**: clone, `cd D:\Prometheus`, `set PYTHONPATH=D:\Prometheus`, run `python apollo\scripts\phase0_validate.py`. Output matches what's quoted in Part 5.

---

## What we are NOT asking

- "Looks great" feedback (not useful at this stage)
- Recommendations to spend cloud GPU (four prior reviewers converged on "defer cloud, bottleneck is ecology not LLM"; we agree)
- Whether to write a paper (Prometheus does not write papers; per Doctrine #2, papers as outputs are not the goal)
- Reframings of the falsification as "compositional reasoning is dead" (we've explicitly rejected that overreach in the Apollo Status doc § Post-Review Synthesis)

## What we ARE asking

Read Part 4 (what Phase 0 built), Part 5 (what it surfaced), Part 6 (what Phase 1 entails), and pick one or two of the six questions in Part 7 you have a sharp opinion on. The most useful prior reviews pointed out a specific question we hadn't asked, or a specific experiment we hadn't proposed. Continuing that pattern.

Thanks for reading.
