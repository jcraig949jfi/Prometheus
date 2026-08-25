# Salvage arc 152-S → 156-S, and the discrete-controls doctrine

Written on pausing the salvage loop. Five passes, all terminal, all pushed. The second half of this
document — the controls doctrine — outlives the experiment that produced it and is the more reusable
artifact.

---

## PART I — WHAT THE ARC ESTABLISHED

### The charter

Find **compositions whose capability exceeds their components**. Not "which dead agent do we revive"
— that is resurrection bias. A killed *claim* stays killed; only the *asset* is re-evaluated, and
only by asking whether it can change **representation, measurement, operation, or learning**. If it
changes none, archive it.

Target: the smallest closed loop, assembled from parts already owned, that acquires a new reasoning
operation and shows under an independent oracle that its reachable ceiling increased.

### The keystone was already built

Apollo's O1 is not a result. It is a **deterministic ISA expressivity assay**:

    E(C, T) = max over type-correct compositions g in G(C) of score(g, T)
    ΔE(p)   = E(C ∪ {p}, T) − E(C, T)

    1,737,000 type-correct pipelines · ceiling 0.8333 · positive control PASSED
    single_primitive_baseline = 0.0   → composition is MANDATORY, a genuine instruction set

`single_primitive_baseline = 0` is the property to defend aggressively: a successful primitive
cannot be a disguised answer function, it must participate in composition.

**Qualifier that must travel everywhere:** this is an assay of the frozen **15-op O1 search pool and
its grammar**, not of the 27-op registry. "Nothing in 1.74M pipelines beats 0.833" is true *over that
pool*.

### The ceiling decomposes exactly

Eval set = 120 tasks. canary 50 + synth 30 + inference 20 + cross_tier 20.
30 + 30 + 20 + 20 = **100/120 = 0.8333**.

Executed over the real canary subset: 30/50 = 0.6000, replicating Apollo's figure. The split is
**binary, not graded**:

    numeric_comparison      10/10  1.0000   SOLVED
    numeric_stated_premise  10/10  1.0000   SOLVED
    transitivity            10/10  1.0000   SOLVED
    all_but_n                0/5   0.0000   UNSOLVED
    temporal_ordering        0/5   0.0000   UNSOLVED
    vacuous_truth            0/5   0.0000   UNSOLVED
    consistency_check        0/5   0.0000   UNSOLVED

**The missing 16.7% is precisely 20 tasks.** And all 20 **abstain** — `selected_answer = None`, zero
scorers firing — which is why they score 0.0000 rather than ~0.25. The organism is already the honest
abstainer.

### Literature: ahead on measurement, behind on synthesis

We independently reconstructed an active lineage: DreamCoder (arXiv 2006.08381) → Stitch (POPL 2023,
2211.16605) → babble (2212.04596) → LILO (2310.19791) → Twitch (2603.06849), the last doing exactly
this for equational theorem proving and learning from *failed* partial proofs.

Read the full Stitch paper — 42 pages, 135,431 characters extracted, not the abstract. Census over
the complete text: **`downstream` 0, `accuracy` 0, `success rate` 0**, against `compression` 44 and
`compressive` 17. Their four evaluation axes are compression quality vs DreamCoder, resource
efficiency, test-set compression ratio 2.55×–11.57×, and an ablation.

**Compressivity is assumed as the objective and never validated against reachability.** Apollo
measures what this literature does not measure at all.

Scoped honestly: this is *Stitch*, the **selector** paper — DreamCoder does report tasks solved. The
gap is in the abstraction-**selection** step, which is exactly where the proposed C-vs-R experiment
sits. Credit where due: Stitch holds out a test set and measures compression on it. The care is
present; the objective never closes to task-solving.

### The severed library — the arc's central finding

    Apollo v1 PRIMITIVE_CATALOG (apollo/archive/v1/src/genome.py) : 25
    Hephaestus forge_primitives (agents/hephaestus/src/)          : 25
    INTERSECTION                                                  : 25
    in v1 but NOT in forge                                        : NONE

Identical, not similar. **Apollo's v2 blackboard rewrite dropped Hephaestus's entire library.** Three
of the four unsolved categories map to primitives that still exist:

    all_but_n         → all_but_n          def all_but_n(total, n): return total - n
    temporal_ordering → temporal_order
    consistency_check → check_transitivity / solve_constraints
    vacuous_truth     → NO MATCH

This is the charter's exact shape: two assets whose coupling was severed by an architecture rewrite,
where the claim that justified the original coupling is irrelevant to reconnecting them. It is also
an indictment — a rewrite silently dropped 25 working operations and nobody noticed until a 50-task
canary was traced category by category.

### The counterfeit that was caught before it ran

The authorised first coupling was: give Hephaestus the `all_but_n` failure evidence, let it mint,
measure ΔE. **Hephaestus would not synthesize — it would retrieve from its own library.** ΔE moves
+4.17%, the primitive appears in the winning pipelines, provenance checks out. Every acceptance
criterion satisfied by *reconnection* rather than *acquisition*.

Harder to spot after the fact than before. This is why intervention class must be fixed pre-run.

### The corrected ladder

    ΔE_port    all_but_n        adapt an EXISTING tested primitive to the blackboard signature.
                                Exercises type adaptation, guard composition, enumeration and
                                provenance end to end. LABELLED PORT. Never reportable as synthesis.
    ΔE_reason  vacuous_truth    the ONLY category with no forge primitive, therefore the only place
                                synthesis must actually occur. This INVERTS the prior recommendation
                                against it; the answer-pattern risk is now managed, not avoided.
    ΔE_parse   temporal_ordering  doubly contaminated (parser gap AND existing primitive). Useless as
                                a demonstration, excellent as the deliberately-bad positive control.

---

## PART II — THE DISCRETE-CONTROLS DOCTRINE

### What is already discrete

O1's enumeration is deterministic and exhaustive over its pool. `run_pipeline` is a pure fold. Guards
are boolean predicates. Scoring is exact string match. `compile_check` is a static type check. The
25-of-25 intersection was a set operation. Every slot trace in this arc was direct measurement.

The question is not whether discrete analysis is available. It is **where inference is still
load-bearing, and whether each such place can be demoted to proposal-only.**

### Where inference is still load-bearing

- **Hypothesis generation.** Eight falsifications in this arc — depth bound, multi-premise rules,
  missing dispatch, guard collision, wrong ISA, wrong subset, "no operator subtracts." All from
  reasoning about code. Each settled by one execution.
- **Category classification** — parser gap vs capability gap, currently judgment.
- **Intervention labelling** — ΔE_parse vs ΔE_reason, and the north-star claim hangs on it.
- **"Does the primitive encode the answer pattern?"** — pure judgment.
- **Minting** — irreducibly generative.
- **Task-family authoring** — LLM-written tasks may correlate with LLM-minted primitives.

### The controls, cheapest first

**1. Mutation testing on the primitive.** Generate mechanical mutants of minted `p`: operands
swapped, constant return, off-by-one, identity. **Every mutant must fail to move ΔE.** If
`all_but_n(t,n) = t−n` moves the ceiling and so does `n−t`, the family does not discriminate
semantics and the result is worthless. Converts the hardest judgment into a loop over mutants.

**2. Knockout / reversibility.** Already built: `agents/hephaestus/src/knockout_ablation.py`, the
forge's own Gate-6 protocol — *"an engine whose removal costs nothing was decorative in that tier,
whatever its label says."* Remove `p` from `C ∪ {p}`; newly-solved tasks must become unsolvable
again.

**3. Assay-validity pair.** A type-compatible **no-op** must give ΔE exactly 0 — under exhaustive
enumeration a semantically null operator cannot raise a maximum. A port for an **already-solved**
category (`check_transitivity`, transitivity 10/10) must also give 0. If either moves, the assay is
measuring search dynamics rather than expressivity and every ΔE so far is suspect.

**4. State injection.** Replaces the parse-vs-reason inference entirely. Inject `relations` directly
into a pre-populated `BlackboardState` and re-run. Solves → the deficit was strictly upstream of
reasoning. Still fails → reasoning gap regardless of the parser. `BlackboardState` is a dataclass
with defaults, so this costs nothing. **The substrate assigns the intervention label, not the
analyst.**

**5. Programmatic task families.** Held-out sets from a deterministic parameterized generator with a
stated grid — as `gen_inference_chain` already works — never LLM-authored. Kills authorship
correlation mechanically rather than by trusting separation.

**6. Budget and seed invariance.** Two compute budgets; ΔE must not depend on budget. Report
enumeration ΔE separately from evolutionary ΔE. An effect visible only under evolution is search
luck.

**7. Commit-before-run.** The candidate's artifact SHA lands in a git commit before the result
exists. Already how the loop operates; it needs stating as a control rather than as bookkeeping.

### The two general rules

**Replace every causal judgment with a differential intervention.** For any claim "X because Y,"
intervene on Y and measure X. Knockout is that pattern for components, mutation for semantics, state
injection for pipeline stages, the no-op for the assay itself.

**The LLM is a proposer, never a judge.** Hephaestus proposes `p`. It may not score `p`, may not see
the held-out set, may not assign the intervention class. Every acceptance decision is a deterministic
predicate over measured quantities. This is the defect Hephaestus's own ablation card named: *"the
distractor policy IS the measurement, set by the conflicted party."*

### What resists discretisation, stated honestly

**The task family encodes a judgment about what the capability is.** A programmatic generator makes
it reproducible and uncorrelated, not objective — someone chose the grid. Mutation testing bounds
this without eliminating it.

**Whether a category is "one capability" is a modelling choice.** State injection settles
parse-vs-reason. It does not settle whether `vacuous_truth` and `consistency_check` are one
capability or two. That is a decision about carving and must be declared as an assumption, never
dressed as a finding.

---

## Standing debts

- `synth` (30) and `cross_tier` (20) unexecuted; the 100/120 accounting rests on Apollo's figures for
  50 of 120 tasks.
- Implementation-level identity between v1 and the forge unverified — names and arity matched only.
- Whether `all_but_n(total, n) → int` adapts to `BlackboardState → BlackboardState` without becoming
  a rewrite is **untested**. If it is a rewrite, the port *is* a mint and the ladder's first rung
  changes character.
- Five items per category is thin and overfittable. The held-out family is the answer and is not
  built.
- Twitch unread; it may measure downstream proving success.
