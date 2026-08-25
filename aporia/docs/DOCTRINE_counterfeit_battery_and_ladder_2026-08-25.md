# Doctrine: delta namespaces, the counterfeit battery, and the frozen ladder

Adopted 2026-08-25 from HITL review of the salvage arc. This supersedes the ad-hoc intervention
labelling in `SALVAGE_ARC_AND_DISCRETE_CONTROLS_2026-08-25.md` §II and fixes the next seven steps.

---

## 1. Three delta namespaces, because credit inflation is the recurring failure

The measured effect can be real while the credit is assigned to the wrong mechanism. Name that
failure explicitly: **causal-credit inflation**. It has now occurred twice in one arc (parser patch
readable as reasoning; retrieval readable as synthesis), both caught by inspection rather than by a
control.

    ΔE_port      capability existed elsewhere in the accessible system and was CONNECTED.
                 Legitimate causal claim: E(C_v2 ∪ p_legacy, T) > E(C_v2, T).
                 Useful for architecture, regression testing, inheritance, substrate evolution.
                 Establishes NOTHING about abstraction learning, synthesis, discovery, library
                 growth, or the forge's ability to infer a missing operation.

    ΔE_synth     implementation did not previously exist anywhere accessible, and was generated
                 from an admissible specification/evidence channel.

    ΔE_discover  stronger still: the capability/specification ITSELF was not pre-enumerated by the
                 experiment designer. This is the class relevant to the north star.

The namespace is fixed mechanically before execution, never inferred from the result.

## 2. The counterfeit battery

**Principle: every capability claim must come with a cheaper alternative causal explanation, and the
experiment must intervene on that alternative.** This is strictly stronger than analyst inspection,
which is what caught both counterfeits so far and cannot be relied on for the next one.

The claimed intervention class **determines mandatory falsifiers**:

    retrieval counterfeit     capability already exists somewhere accessible
                              -> registry/provenance intersection across ALL agent libraries
    parse counterfeit         changes representation, not reasoning
                              -> state injection (pre-populate the slot; does it now solve?)
    answer counterfeit        encodes target labels or template directly
                              -> mutation battery: swapped operands, constant, off-by-one,
                                 identity. ALL mutants must fail to move ΔE.
    search counterfeit        raises search probability without enlarging reachable programs
                              -> enumeration ΔE reported separately from evolutionary ΔE
    budget counterfeit        helps only because evaluation budget changed
                              -> two compute budgets; ΔE must be invariant
    distribution counterfeit  specialises to generator artifacts
                              -> X-heldout (structurally independent construction route)
    composition counterfeit   value actually comes from another operator unlocked incidentally
                              -> knockout + minimal causal tracing over the winning pipelines
    evaluation counterfeit    scoring or task interpretation drifted, not capability
                              -> frozen evaluator hash committed before the run

Machine-enforced gates, not a checklist. A claim whose class has an unrun mandatory falsifier is
inadmissible.

## 3. Two validation strata

A parameterised generator eliminates template memorisation and analyst-authorship leakage. It does
**not** eliminate overfitting to the generator's own ontology, because the generator embodies our
theory of the capability.

    G-heldout   hundreds-to-thousands of procedurally generated tasks from a FROZEN generator,
                with train/test parameter partitions and unseen combinations.
    X-heldout   the same underlying relation instantiated through a structurally DIFFERENT
                construction route — e.g. vacuous truth as quantified natural-language inference
                vs. set membership vs. graph predicates vs. mechanically transformed logical forms.

No external benchmark is required. What is required is **independent construction semantics**.

The test is not *"can this primitive solve more examples of the family we designed for it?"* but
*"does the transformation's usefulness survive a change in how the problem manifests?"* — the
difference between fitting a benchmark and adding an instruction to the ISA.

**Mutation testing composes with this:** semantically wrong mutants that succeed on G-heldout but
fail on X-heldout directly measure generator weakness.

## 4. The frontier as an experimental-design problem

The LLM must not decide whether its own mechanism story is true. That does **not** reduce the
architecture to "a human forever chooses interesting problems."

    generator → candidate transformations → deterministic interventions
              → measured state transition → MECHANICAL FRONTIER POLICY

The frontier policy needs no prose understanding. It selects on measurable quantities: unexplained
failure mass; uncertainty in operator/task causal attribution; expected discrimination between
competing mechanistic models; ΔE coverage; novelty relative to existing operator semantics; transfer
across families; cost; reproducibility; mutant discrimination; knockout/dependency structure.

    a* = argmax_a [ expected reduction in uncertainty about capability structure / compute cost ]

Estimated from the history of deterministic assay outcomes, not from the LLM.

**The object is not a list of verbs. It is a graph:** task states —(operator/composition)→ newly
reachable states, with empirically measured edges. **The frontier is the boundary where reachability
fails.** The LLM proposes edges; the substrate decides whether they exist.

The open research problem is therefore **automated experimental allocation over a causal capability
graph**.

## 5. The proposer reframe, with a retrospective measurement

Eight source-reading mechanism hypotheses this arc, eight falsified. Retrospectively scored:

    probes required per hypothesis : 1 in ALL 8 cases
    killed by a single read/grep   : 6/8
    killed by a single execution   : 2/8
    distinct mechanism classes     : 8/8, no repeats
    descent: depth → arity → dispatch → guard-order → artifact → population → registry → library

A proposer can be scientifically valuable even when nearly all its beliefs are false, provided it
generates cheap experiments that partition the space efficiently. **Stop optimising for hypothesis
accuracy; optimise for experiment quality.** The instruction changes from *"what is the code doing?"*
to *"generate a discriminating execution."*

**Two caveats that keep this honest.** The classes were named by me after the fact, so 8/8-distinct
may be post-hoc carving. And a non-convergent sequence looks identical to a convergent one until it
fails to terminate. Prospective measurement required: record cost-to-falsify and
mechanisms-eliminated per hypothesis **before** the outcome is known.

## 6. Selector experiment — corrected design

**Freeze candidate generation first** so every selector receives an identical pool. Then compare
under identical insertion count and identical downstream compute:

    S_C          rank by compression
    S_R          rank by reachability
    S_C+R        combined
    S_random     control
    S_oracle     hindsight selection on held-out benefit — not deployable, establishes headroom

**Dependent variable is marginal held-out reachability PER LIBRARY SLOT and PER UNIT DOWNSTREAM
COMPUTE**, not final solve rate — otherwise R wins by selecting large expensive primitives.

Quadrants: high-C/high-R ideal reusable abstraction · high-C/low-R compression decoy ·
low-C/low-R junk · **low-C/high-R = "reachability-only candidate", NOT "Apollo gold" until H
confirms.** High assay reachability with no external transfer is assay specialisation.

**Falsifier:** if R-ranking cannot beat compression or random under frozen candidates and equal
resources, kill the claim that ΔE deserves promotion to abstraction *selector*. **This does not kill
the expressivity assay as a diagnostic instrument.** That distinction is essential — it is the
difference between *E is a microscope* and *E is a compass*.

## 7. Falsifier for the entire salvage thesis

The thesis: components created under false or dead hypotheses may nevertheless instantiate
independently useful mechanisms, and reconnecting them into a falsification-controlled loop produces
new scientific capability rather than restoring old demos.

Falsified if **all three** hold:

1. Recovered components only reproduce capabilities present in their original task distributions.
2. Newly minted or selected primitives fail to improve independently generated or held-out
   reachability relative to random/simple baselines.
3. **Prometheus-minus-Prometheus**: ablate the inherited machinery — no forge ontology, no historical
   failure corpus, no learned primitive proposals, no evolution — and let a generic typed enumerator
   or grammar mutator propose operators over the same frontier at the same budget. If the elaborate
   system does not beat that prospectively, the artifacts are archaeology.

The third is the killer and should eventually be run regardless of the others.

## 8. The frozen ladder — no widening before step 6

    IQ-PORT-1    all_but_n. INTEGRATION QUALIFICATION ONLY, not a numbered scientific cycle.
                 Exercises: forge representation → adapter → v2 blackboard → enumeration grammar
                 → scoring → provenance → knockout, in a configuration never run end to end.
                 We KNOW the semantic answer; that is what makes it a good integration control.
                 Must: recover the predicted tasks, survive knockout, produce ZERO novelty claim,
                 carry the class PORT_EXISTING_CAPABILITY fixed mechanically. Then FREEZE.
    IQ-NULL      type-compatible no-op + already-solved-category port. Both ΔE exactly 0.
    SYNTH-1      vacuous_truth. Preregistered mutants and knockout. First actual experiment.
    TRANSFER-1   G-heldout at scale + X-heldout via independent construction semantics.
    BATTERY      turn §2 into machine-enforced gates.
    SELECTOR     frozen pool; C vs R vs C+R vs random vs hindsight oracle.
    ABLATION     Prometheus-minus-Prometheus.

**Do not widen the primitive registry, add domains, or revive agents before SELECTOR.**

Rationale: port first *operationally*, vacuous_truth first *scientifically*. Do not spend the only
clean synthesis target debugging plumbing.

## 9. The hinge

The arc is judged on SELECTOR, not on whether vacuous_truth moves five tasks:

> Does this representation merely describe what already worked, or does it tell the system what
> capability to acquire next?

## 10. Literature framing, corrected

The earlier phrasing over-broadened. DreamCoder evaluates problem-solving capability and learns
abstractions jointly with search machinery; LILO reports improved task solving while incorporating
Stitch-style compression. The defensible claim is narrower and stronger:

> **Compression is widely used as an abstraction-SELECTION signal, but the marginal causal value of a
> candidate abstraction for enlarging downstream reachability is not thereby established.**

That is the experimental target.
