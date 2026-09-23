# Operator directive -- Atlas -> BEE pilot (received 2026-09-19 ~12:35Z, verbatim)

Preamble (operator, chat):

Let's build a shim atop it and test what you've assembled alongside our other engines. I was going to give this to another agent but realized you may be best for the job, as picking experiments to test with might be optimized. The newness factor might require some additional scaffolding to support the experiments.  You can build those into the BEE or the shims atop it.  Adapt as you see fit.  Let me know if there are any major concerns.  For the other engines, we've pushed as much as we can down into code to minimize LLM hallucination and also reduced token burn:

---

You are founding a temporary experimental role inside Prometheus.

Your job is to determine whether the Bellerophon Emergence Engine (BEE) can function as a third independent experimental ecosystem alongside SFE and NPE.

Do not redesign Bellerophon. Do not turn BEE into an SFE or NPE emulator. Build the lightest possible adaptation layer that lets scientific ideas already represented in Atlas be instantiated honestly inside BEE's native world model.

Objective

Select a small, deliberately varied set of experiments from Atlas and attempt to reproduce their scientific question inside BEE.

The primary question is not:

"Can BEE reproduce the same numeric result?"

It is:

"What survives when the same scientific question is instantiated in a substantially different experimental ecology?"

We care about:

* transferable phenomena
* ecology-specific phenomena
* changed or inverted effects
* newly exposed mechanisms
* representation failures
* unexpected emergent behavior
* reusable BEE-native mechanisms discovered during translation

Phase 1 -- Inspect

Read Atlas sufficiently to understand its experiment, attempt, lineage, provenance, evidence-pointer, and cross-engine structures.

Read Bellerophon's current contracts and implementation sufficiently to understand:

* World
* Player / organism / candidate
* Substrate
* StateDevice and persistence
* interventions
* objectives
* observers
* controls
* transforms
* selectors
* archives
* replay/checkpoint semantics
* admission predicates
* receipts
* resource accounting

Do not modify either system during this phase.

Produce a short capability correspondence table between Atlas experimental concepts and BEE-native concepts.

Phase 2 -- Select the pilot

Choose approximately six Atlas experiments before implementing any of them.

Seek diversity rather than six easy translations.

The set should contain, where Atlas permits:

1. one established positive result
2. one established null or failed hypothesis
3. one experiment where persistent state or memory matters
4. one involving transfer, reuse, recombination, or inherited artifact
5. one involving environmental/regime change or adaptation
6. one deliberately difficult case whose assumptions may not fit BEE

Prefer experiments whose scientific question can be stated independently of their original executor.

Record the exact Atlas experiment IDs and evidence pointers.

Freeze the selection before running BEE.

Phase 3 -- Build the shim

Implement the minimum Atlas->BEE adaptation layer required for these experiments.

Do not build a universal framework.

For every adaptation produce a machine-readable translation manifest classifying each meaningful component as:

* IDENTICAL
* ANALOGOUS
* MODIFIED
* OMITTED
* UNREPRESENTABLE

Record the reason for every non-IDENTICAL classification.

The shim must never silently substitute semantics.

If BEE cannot honestly represent something, return a structured refusal rather than forcing the experiment through.

Preserve Bellerophon's native receipts, provenance, replay, state and failure semantics.

Phase 4 -- Freeze each adaptation

Before observing its experimental result, freeze:

* source Atlas experiment
* scientific question
* BEE world
* organisms/candidates
* initial state
* interventions/pressures
* objective where applicable
* observations
* controls
* seeds
* budgets
* stopping rules
* translation manifest
* expected invariants
* decision criteria

Hash the freeze.

No post-result repair may alter the frozen scientific claim. Repairs require a new descendant attempt.

Phase 5 -- Execute

Run each experiment natively through BEE.

Exercise BEE's replay machinery on every admitted experiment.

Preserve failures.

Do not discard anomalous trajectories merely because they are irrelevant to the original Atlas hypothesis.

If something surprising occurs, preserve enough state, telemetry, artifacts and lineage to permit later forensic investigation.

Do not immediately optimize or explain it away.

Phase 6 -- Compare

For each experiment classify the cross-ecosystem relationship without forcing agreement:

* PHENOMENON_PRESERVED
* PHENOMENON_CHANGED
* PHENOMENON_INVERTED
* PHENOMENON_ABSENT
* NEW_PHENOMENON
* NOT_COMPARABLE
* NOT_REPRESENTABLE
* INSTRUMENT_FAILURE

Separate:

1. scientific outcome
2. representational differences
3. executor differences
4. resource/budget differences
5. measurement differences

Do not treat failure to reproduce as evidence against the original experiment unless the translation genuinely preserves the relevant causal structure.

Phase 7 -- Feed Atlas

Design the smallest extension necessary for Atlas to represent:

SOURCE_EXPERIMENT
v
ADAPTATION
v
ECOSYSTEM_ATTEMPT
v
EVIDENCE

An adaptation must have its own immutable identity and provenance.

Record ancestry between the original Atlas experiment and its BEE realization.

Do not overwrite or merge the original experiment.

The eventual goal is for Atlas to answer questions such as:

* Which phenomena survive across SFE, NPE and BEE?
* Which depend on a particular substrate?
* Which change sign or character after translation?
* Which experiments cannot be represented in another ecology?
* Which mechanisms discovered in one ecology become useful fossils in another?
* Which surprising phenomena appeared only because an experiment migrated?

Scientific posture

BEE is not being benchmarked against SFE or NPE.

There is no winning ecosystem.

Treat the three systems as different habitats into which scientific questions can be transplanted.

A failed transplant may be as informative as a successful one.

Do not punish weirdness.

Do not collapse rich behavior into a scalar score when the trajectory itself may contain the important result.

Preserve unexpected artifacts even when the original hypothesis fails.

Do not let familiar ML benchmarks or standard evolutionary metrics narrow the search merely because they are easy to implement.

Deliverable

Return a review packet containing:

1. selected Atlas experiments and selection rationale
2. capability correspondence
3. shim architecture
4. translation manifests
5. frozen preregistrations
6. execution receipts
7. replay verification
8. per-experiment cross-ecosystem comparison
9. unexpected phenomena and preserved artifacts
10. proposed Atlas lineage representation
11. every instance where BEE exposed something the source ecosystem could not
12. recommendation for whether BEE is scientifically ready to operate continuously as Prometheus's third ecosystem

Keep the shim light.

Spend effort on experiments and observations, not framework construction.

The ideal outcome is not six successful ports.

The ideal outcome is discovering what becomes scientifically possible when Prometheus asks the same questions inside three different kinds of worlds.
