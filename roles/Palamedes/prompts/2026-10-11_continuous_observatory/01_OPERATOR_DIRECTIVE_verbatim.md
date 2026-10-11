PROMETHEUS — PALAMEDES

CONTINUOUS OBSERVATORY DEVELOPMENT

Incremental Native-Engine Qualification Campaign

Operator directive
Program: Phase 3 / Recursive Sagacity Observatory
Coordinator: Palamedes
Initial window: 72 hours after C-013 closure
Objective: Improve the Observatory through repeated contact with different native computational systems.

(received 2026-10-11 ~09:55Z; saved verbatim by Palamedes[harry1-679179c6])

⸻

0. The direction

Palamedes,

Your strategic expansion work has served its purpose.

The scaling assessment identified the main engineering bottlenecks. The reachability demonstration tested a real hypothesis, albeit with insufficient statistical power. The long-duration runner survived simulated execution failures. The roadmap now connects our immediate engineering work to the larger scientific ambition.

Good.

We should now move from architectural planning back toward incremental implementation and experimentation.

The Observatory must evolve through repeated encounters with different native computational systems.

Every new engine should test the Observatory’s assumptions.

Every successful onboarding should make subsequent onboarding cheaper.

Every incompatible engine should teach us which abstractions were too narrow.

Every qualified experimental result should enlarge our ability to investigate increasingly sophisticated cognitive mechanisms.

We are not building a universal runtime.

We are building a federation of native computational systems connected through common scientific evidence machinery.

The Observatory should become progressively more general without forcing every engine into the same ontology.

⸻

1. Close C-013 early

You are explicitly authorized to close C-013 before its original October 12 deadline.

Do not spend the remaining time waiting for Ananke’s reply or generating hourly no-change reports.

Finish the deliverables that are already substantially complete:

* RSO_SCALING_ASSESSMENT.md
* REACHABILITY_CARTOGRAPHY_V0.md
* LONG_DURATION_EXECUTION_ARCHITECTURE.md
* PROMETHEUS_SAGACITY_SCALING_ROADMAP.md
* RECOMMENDATION.md
* The Astra and Fable review packets.

Record D1 as the underpowered result it actually produced.

Do not reinterpret its failure to separate as evidence that archive-based search has no benefit.

Do not rerun D1 merely to consume the remaining campaign window.

Preserve its preregistration, actual sample size, resource truncation, and limitations.

The proposed Ananke FLIP follow-up remains useful, but it belongs in its owner’s scientific program.

Do not make the next Observatory campaign depend on Ananke responding.

After C-013 is closed, open a new campaign under:

TH-RSO-BUILD / EP-PHASE3

Use the next available campaign identifier.

⸻

2. New operating philosophy

From this point forward, Observatory development should follow a repeating cycle:

Select → Adapt → Qualify → Challenge → Experiment → Preserve → Generalize → Repeat

The sequence matters.

We should not first spend months designing a universal system and then discover that actual engines cannot use it.

Instead:

1. Select a sufficiently different native runtime.
2. Implement the smallest adapter necessary.
3. Reuse existing evidence and qualification machinery.
4. Construct appropriate native positive and negative controls.
5. Independently challenge the adapter and its interpretation.
6. Run a bounded native experiment.
7. Preserve the result and qualification scope.
8. Extract genuinely reusable improvements.
9. Select the next engine.

Every repetition should improve the Observatory.

The scientific result may be positive, negative, inconclusive, or detection-unqualified.

All are legitimate outcomes when supported by the evidence.

⸻

3. Select Ensorain as the next native runtime

Our first native witness used Ares.

The next should use Ensorain, subject to a short compatibility check against its current committed interfaces.

Read:

rso/witness/CANDIDATES.md

rso/scale/CHECKPOINT_REPLAY_SURVEY.md

The current Ensorain source, work state, and WTP-05 preregistration.

Why Ensorain?

Ares exercised recurrent activation and plastic-weight retention across an interrupt.

Ensorain offers a different computational organization:

* fitted tensor-based memory;
* persistent learned state;
* replay and error stores;
* explicit storage limitations;
* world distribution drift;
* a native memory-cap audit;
* a Smuggler forbidden-channel control.

These are different kinds of information boundaries.

The Observatory must not assume that Ares’s reset and activation semantics apply directly.

Ownership and isolation

Ensorain is conducting an active WTP-05 campaign.

Do not interrupt it.

Do not modify its frozen code, registered seeds, or experimental results.

Notify Ensorain of the proposed Observatory onboarding.

Build the adapter in the RSO lane against a pinned source revision.

Use an isolated worktree and independent experimental data.

Coordinate with Ensorain if it responds, but a read-only adapter against an existing public interface need not block on an owner reply.

If the existing interface cannot support qualification without a native code change, route the requested change to Ensorain and continue other dependency-safe work.

Do not silently alter its physics.

⸻

4. The first Ensorain qualification

Do not merely reproduce C-010’s retained-bit experiment.

Select a phenomenon native to Ensorain.

The preferred first question is:

Can a bounded persistent learner retain and use information across a world-drift boundary, while respecting its declared memory restrictions?

This is a candidate question, not a predetermined conclusion.

Before committing to it, demonstrate that the selected world actually rewards the relevant state.

Required scientific distinctions

Separate:

Capacity: A constructed lawful learner can perform the task.

World demand: A specified simpler alternative cannot achieve the same capability under comparable resources.

Search accessibility: An allowed discovery process can or cannot find the mechanism.

Retention: Information survives the relevant native boundary.

Causal dependence: Removing or altering the retained information changes the outcome.

Qualification: The evidence path can detect the intended behavior and relevant forbidden alternatives.

Do not conflate these.

For example, a learner that succeeds after a distribution shift may be relying on a fixed parametric prior rather than genuinely using retained observations.

Likewise, a strong fitted-memory result may simply demonstrate that the evaluator supplied the correct model class.

These distinctions must be visible in the controls.

Initial controls

Use the native Ensorain machinery to construct:

* a known-answer lawful reference;
* a memoryless or short-window competitor;
* a stateful reference appropriate to the selected world;
* a forbidden-memory or Smuggler control;
* a shuffled-history control where meaningful;
* a restart or reset control consistent with Ensorain’s actual semantics.

Do not automatically impose the Ares NULL control.

If an existing Ensorain world fails the cognitive-demand gate, record that outcome and select another suitable native world rather than inventing stronger claims.

Prefer an already certified demanding world if one exists.

⸻

5. Reuse qualification machinery aggressively—but honestly

The first three Observatory campaigns demonstrated considerable reuse opportunities.

We should now test them directly.

Candidate reusable components include:

* canonical artifact identity;
* execution binding;
* custody;
* seed partitioning;
* budget accounting;
* mutation/challenge tooling;
* qualification-state records;
* known-answer calibration;
* evidence-preserving result generation.

Do not rewrite these unnecessarily for Ensorain.

But neither should you assume their qualification automatically transfers.

A component qualified for a flat Ares inventory is not thereby qualified for arbitrary nested evidence structures.

A ruler qualified for a binary retained-bit endpoint is not necessarily qualified for continuous prediction error.

A custody mechanism qualified against accidental mutation does not prove the producer’s claims are truthful.

Reuse implementations where justified. Reuse scientific authority only within its established scope.

⸻

6. Build a minimal qualified-component registry

I agree with your proposed next engineering investment.

Create a small registry describing reusable Observatory components.

Each entry should identify:

* component name and version;
* immutable source digest;
* responsible owner;
* supported interface;
* qualification tests and evidence;
* known counterexamples;
* valid claim scope;
* dependencies;
* changes that invalidate qualification;
* downstream engines currently using it.

Use existing stage-record and provenance patterns where possible.

Do not create a large new database schema merely for this registry.

A manifest-driven implementation is acceptable for the initial campaign.

The critical requirement is that a later adapter can determine:

Which components may I reuse, what exactly has been qualified, and what changes require requalification?

First registry entries

Start with a small number of already exercised components:

1. Execution binding from C-009.
2. Custody/manifest verification.
3. Mutation and challenge machinery.
4. The applicable portions of the C-010 evidence driver.

Classify each by its actual demonstrated scope.

Do not mark everything globally QUALIFIED.

An engine-specific test remains engine-specific.

⸻

7. Improve integration latency incrementally

C-013 demonstrated that waiting for integration is now a significant coordination cost.

Implement a small event-driven integration notification.

The desired behavior is:

1. A builder completes a task.
2. The task enters INTEGRATION_READY.
3. A durable notice is emitted.
4. Palamedes is awakened or the integration queue becomes immediately visible to an existing worker.
5. The integration proceeds through its required validation.
6. The resulting disposition is recorded.

The notice must be idempotent.

Do not create duplicate integrations when a message is retried.

Do not allow automatic notification to bypass tests, merge safety, source ownership, or frozen evidence requirements.

Do not build a new distributed scheduler for this.

Reuse the existing workgraph and coordination infrastructure.

If the integration notification requires a substantial infrastructure redesign, stop at a tested notification prototype and continue the native-engine work.

The Observatory must not become an infrastructure project that postpones science.

⸻

8. Measure onboarding efficiency

The next engine is both a scientific experiment and an engineering experiment.

Record:

Measurement	Purpose
Adapter implementation lines	How much bespoke code remains necessary?
Shared components reused	Whether the common evidence plane is maturing
Shared components modified	Detect architectural overfitting
Time to first native execution	Practical onboarding friction
Time to qualified result	End-to-end scientific throughput
Q3 reviewer time	Expensive qualification overhead
CPU and memory	Computational requirements
Operator interventions	Autonomy and coordination maturity
Native semantic mismatches	Hidden assumptions in the Observatory

Compare Ensorain against C-010.

Do not normalize away differences in experiment difficulty.

An adapter that requires more code because it exposes genuinely different physics is not necessarily worse.

But repeated rebuilding of identical provenance or custody machinery is a defect.

Target

Aim to reduce new experiment-specific engineering substantially.

Palamedes’s current estimate is that the next runtime could otherwise require roughly 1,500 bespoke lines.

A useful aspiration is an adapter closer to 500 lines.

This is not a hard cap.

Never remove necessary scientific controls to satisfy a line-count target.

⸻

9. Independent challenge

After the Ensorain adapter and native assay are implemented:

1. Freeze the relevant evidence-path implementation.
2. Commit the intended claims, controls, and qualification criteria.
3. Give a genuine Q3 reviewer the frozen surface.
4. Require adversarial cases and mutations before their outcomes are observed.
5. Run the challenges.
6. Perform at most one bounded repair round.
7. Re-check the repaired surface.

Pallas/Fable remains the preferred available reviewer.

Where feasible, a different model family should review the broader scientific interpretation.

Do not spend premium Q3 review on ordinary adapter plumbing that deterministic tests can settle.

Reserve it for real scientific ambiguity and claim-critical evidence.

If the adapter does not qualify, report the failure and preserve the reusable lessons.

Do not keep repairing indefinitely to force acceptance.

⸻

10. Run a native Ensorain experiment

Once the instrument is sufficiently qualified, conduct one bounded native experiment.

Use a frozen world, native subject definitions, separated discovery/evaluation seeds, and a preregistered endpoint.

Possible outcomes include:

* a lawful retained-information mechanism;
* failure to retain;
* a simpler mechanism explaining the result;
* a world-demand deficiency;
* an instrument limitation.

The outcome must be decided by the registered criteria.

Do not select the best organism after inspecting the final ruler’s results.

Do not change the world to make an uninteresting organism appear intelligent.

Preserve the negative controls and the exact causal boundary tested.

The result should be self-contained and reproducible.

⸻

11. Prepare a third native architecture

Do not wait until Ensorain closes before considering what comes next.

Cadmus should begin a lightweight, read-only compatibility assessment of the next candidate.

Preferred direction:

Z80 Atlas or another genuinely byte-level hereditary system.

The reason is scientific diversity.

Ares examines retained plastic state within episodes.

Ensorain examines persistent learned state across changing world conditions.

Z80 Atlas would examine executable information and heredity across generations.

These mechanisms should stress different assumptions.

The initial question might concern:

Can a native heritable computational structure transmit a functional information-processing capability across generations, and can the Observatory distinguish genuine inheritance from environmental reconstruction or seeded copying?

Do not begin a large Z80 experiment immediately.

Prepare the adapter contract and a known-answer smoke test.

If Ensorain reveals a fundamental Observatory defect, repair that abstraction before proceeding.

If Ensorain qualifies cleanly and the next adapter is small, proceed to a separate third-engine campaign.

⸻

12. Build toward more complex cognitive phenomena

Retained information is only the beginning.

The Observatory must eventually test increasingly sophisticated mechanisms.

Examples include:

* combining two independently acquired capabilities;
* forming reusable internal representations;
* learning a new operation from experience;
* transferring a mechanism into another organism;
* adapting after the relevant world law changes;
* discovering a reusable learning procedure;
* composing previous discoveries into deeper organizations.

These capabilities should be introduced gradually.

Each should have a native implementation or known-answer positive, a discriminating world, simpler competitors, and a causal assay.

Do not force every engine to demonstrate the same capabilities.

A chemical-like substrate, a graph-rewriting organism, and a recurrent learner may achieve similar functional outcomes through different mechanisms.

The Observatory should preserve those differences.

Our long-term interest is not whether every organism resembles a familiar architecture.

It is whether useful computational structure can arise, persist, and accumulate.

⸻

13. Resource policy

This campaign is authorized for existing local resources only.

No paid RunPod or cloud expenditure is authorized.

Use the existing CPU and GPU fleet according to measured need and available leases.

Do not monopolize a host already executing a frozen long-running experiment.

For each proposed experiment, specify:

* expected resource consumption;
* allowable parallelism;
* stopping conditions;
* reproducibility requirements;
* whether checkpointing is necessary.

The current session-independent runner may be reused where qualified.

Do not make cross-host execution a prerequisite for a cheap native experiment.

A local CPU experiment that resolves the question is preferable to an elaborate distributed version of the same experiment.

Preserve the long-duration execution architecture for future workloads that actually justify it.

⸻

14. Builder Cell assignments

Palamedes

Own campaign coordination, integration, the qualified-component registry, scientific scope, and final synthesis.

Prevent drift into infrastructure work.

Maintain the next dependency-safe packet.

Argus

Own the Ensorain evidence adapter and evaluator interface.

Reuse existing binding, receipt, and custody machinery.

Identify source-specific assumptions in common components.

Cadmus

Own native-runtime compatibility, reset/checkpoint boundaries, and known-answer controls.

Prepare the third-engine candidate assessment.

Do not modify active native campaigns.

Eupalamus

Own the integration-notification prototype, reusable manifest/driver plumbing, and mechanical execution support.

Assist in measuring onboarding costs.

Pallas

Own independent adversarial qualification at frozen milestones.

Use genuine Q3 capability.

Do not perform implementation repairs.

All seats continue the established hourly comms/workgraph polling while active.

No empty heartbeat commits.

⸻

15. Execution sequence

The next 72 hours should proceed as follows.

First: close the previous campaign

Complete C-013 and preserve its limitations and review-pending status.

Second: establish the Ensorain adapter

Read and pin native interfaces.

Implement the minimum execution and evidence plumbing.

Third: qualify the native phenomenon

Use native positive and negative controls.

Establish cognitive demand and causal attribution.

Fourth: independently challenge

Freeze, attack, repair once if warranted, and re-check.

Fifth: run a bounded native experiment

Produce a qualified positive, negative, inconclusive, or detection-unqualified result.

Sixth: consolidate reusable improvements

Update the component registry.

Measure engineering and scientific onboarding costs.

Prepare the third-engine contract.

Do not mechanically occupy all 72 hours if the completion condition is reached earlier.

Do not compromise an experiment’s evidence boundary to meet the deadline.

⸻

16. Completion criteria

The campaign completes successfully when:

1. C-013 has closed honestly.
2. The qualified-component registry has its initial entries.
3. The integration-notification prototype has been tested, or its specific blocker documented.
4. A second native runtime has been executed through the Observatory.
5. The scientific result is bounded by appropriate controls and qualification.
6. Onboarding cost has been measured against Ares.
7. The third-engine candidate has a concrete adapter contract or documented incompatibility.

A negative second-engine result counts.

An unqualified result counts as a completed investigation but not as successful scientific qualification.

A third-engine experiment is not required for this campaign’s completion.

If the second-engine adapter cannot be qualified within the window, preserve the evidence, close honestly, and report the smallest next step.

⸻

17. The longer-term pattern

After this campaign, I want you to think in terms of a sequence of Observatory generations.

Generation 1: Ares — native retention witness.

Generation 2: Ensorain — bounded learned memory under world drift.

Generation 3: Byte-level heredity and computation.

Generation 4: Spatial or distributed computational media.

Generation 5: Developmental and modular architectures.

Generation 6 and beyond: Populations, ecologies, and systems whose discoveries modify their future learning and search capabilities.

These are research directions, not a prescribed evolutionary ladder.

The ordering can change when evidence justifies it.

Different branches should remain available.

We must not allow the first successful architecture to become the definition of intelligence.

Eventually, we should be able to evaluate many competing architectural hypotheses through the same scientific infrastructure without making their internal physics identical.

⸻

18. The North Star

We are building toward experiments that may last weeks or months, involve large populations, and explore extraordinary spaces of possible cognitive organization.

We do not yet have the resources to explore those spaces by brute force.

Our response must be to become better at identifying where useful mechanisms are reachable, preserving discoveries, reusing scientific machinery, and deploying computation intelligently.

Every new engine should teach us something about cognition.

Every new adapter should teach us something about the Observatory.

Every qualified mechanism should become easier to compare, preserve, transplant, or challenge.

Eventually, we want a laboratory capable of asking:

Can an organism make a discovery that changes what it—and its descendants—can subsequently discover?

That is a much larger question than whether one genome retains one bit.

But answering it begins with making our experimental machinery sufficiently general, inexpensive, and trustworthy.

Continue building the Observatory.

Continue testing it.

Introduce genuinely different engines incrementally.

Let the accumulating experimental evidence determine what the Observatory becomes.

Proceed without further operator gating for the local work authorized above.
