AETHER — PHASE 2B GPU SCIENCE PUSH

Current authoritative state:

origin/main = 06b2cf9b2

Host:

M2 / SPECTREX5

GPU:

RTX 5060 Ti 16 GB

Mission:

Run three back-to-back four-hour experimental windows.

Each experiment must press farther into:

1. richer endogenous state dynamics;
2. causal reach;
3. interaction/composition or, if reach fails, richer primitive physics.

Do not wait for Aporia, Cyclops, or external review.

Comms are informational and coordinative, not permission gates.

The GPU should stay scientifically productive for the next ~12 hours.

⸻

GLOBAL OPERATING RULE

Each experiment gets a hard 4-hour wall-clock window.

Within each window:

* build/qualify;
* freeze the experiment;
* run production;
* reduce;
* write the result;
* commit/push.

If an engineering or instrumentation failure occurs:

* diagnose;
* make one bounded repair;
* rerun the experiment once.

If that rerun also fails technically:

* preserve evidence;
* mark the experiment technically unresolved;
* move immediately to the next four-hour experiment.

If the scientific hypothesis is falsified, that is a completed experiment.

Do NOT modify the physics and rerun merely to obtain a positive result.

One technical repair/rerun maximum per experiment.

Do not allow one experiment to consume the following experiment’s window.

⸻

COMMON DISCIPLINE

For all three experiments:

* use common random numbers where possible;
* preserve deterministic replay;
* require CPU/GPU agreement on qualification fixtures;
* freeze rules before production results are read;
* distinguish direct law bookkeeping from downstream consequences;
* include known-answer positive and negative controls;
* keep perturbation OFF unless explicitly part of a control;
* report exact seeds, hashes, semantics IDs and GPU timing;
* run enough seeds for replication rather than one heroic long trajectory.

Use qualification flights to choose horizon/replication that fit the four-hour window.

Prefer shortening an obviously stationary horizon before production over sacrificing replication.

No broad parameter sweeps.

⸻

EXPERIMENT 1 — OFFER01

VALUE-REPERTOIRE RELEASE

Window: hour 0 → hour 4

AIM02 established:

* reaim1 opens the spatial support;
* the opened support remains dynamically writable;
* but 88–96% of changing site-fields carry only about two values;
* N64 novelty is essentially unchanged;
* late discovery is zero;
* faster/more re-aiming is therefore not the next bottleneck.

The post-hoc offer probe identified the next constraint:

each target sees only about two writers, and those writers supply almost fixed payloads.

Attack that bottleneck directly.

First: semantic-equivalence audit

Before implementing anything, read the exact V2-B TEST-3 exchange law.

Do not reconstruct it from memory.

Determine explicitly how TEST-3 exchange differs from the proposed OFFER law below.

Record the comparison.

If the proposed law is equivalent to TEST-3 exchange plus reaim1, say so and treat this as a composition experiment rather than pretending it is novel physics.

New law

Baseline:

L1 = aeth01.reaim1

Candidate:

provisional

L2 = aeth01.reaim_offer1

Relative to reaim1, add exactly one rule:

After a writer wins and its write commits, the writer takes the target’s pre-write byte value as its new payload.

Retain reaim1.

Everything else remains unchanged.

Use explicit conflict precedence.

Preferred rule:

* normal writes commit first;
* re-aim bookkeeping follows existing reaim1 semantics;
* displaced-value uptake updates the winning source’s payload;
* if that source’s payload field was itself legitimately overwritten during the same tick, the committed external write wins rather than being silently destroyed by bookkeeping.

Freeze the exact ordering in the semantics document.

Do not modify arg1, energy, arbitration, topology, opcode meanings, or perturbation.

Factorial

At minimum compare:

* reaim1;
* exact TEST-3 exchange-only law where technically comparable;
* reaim1 + displaced-value uptake.

Use paired seeds.

512² is the expected starting production size.

Use the qualification flight to choose the horizon, likely in the 5k–10k tick range.

Favor 6–8 seeds if the window permits.

Critical measurement distinction

The candidate law directly changes the source payload.

Therefore:

a source changing its own payload by the OFFER rule is not evidence of rich medium dynamics.

Track separately:

DIRECT_UPTAKE

The mandatory source payload update.

DELIVERED_CONTENT

A later ordinary WRITE uses that acquired payload to affect another site.

DOWNSTREAM_NONPAYLOAD

Effects appearing subsequently in opcode or arg1.

Do not use a transformed payload counter analogous to AIM01’s defective EFFECT subtraction.

Use provenance/event classification instead.

Primary questions

Does displaced-value uptake cause:

* more distinct values to be offered per writer?
* more distinct values to reach a target?
* more than two values per changing target?
* continued late catalogue growth?
* material N64 novelty?
* increased transition diversity?
* downstream effects beyond the direct payload-update rule?

Measure at least:

* distinct payloads held per writer;
* distinct values offered per target;
* distinct writers per target;
* unique target values;
* N16 / N64;
* late discovery;
* transition diversity;
* return-time distribution;
* fraction of all state change directly attributable to mandatory uptake.

Main attack

The obvious false friend is:

two neighboring writers simply exchange/shuttle the same two bytes forever.

Explicitly detect:

* A↔B shuttling;
* short payload cycles;
* fixed small catalogues;
* constant catalogue size despite high turnover.

If activity increases but repertoire remains bounded at approximately two values:

OFFER_SHUTTLE_TRIVIAL

Kill it.

Success gate

Do not freeze exact numerical margins until fixtures/flight qualify the meter.

But OFFER01 only earns the next rung if replicated production demonstrates, relative to both reaim1 and the exchange control:

* material growth in unique target repertoire;
* non-zero late state discovery;
* material N64 novelty;
* evidence that acquired values are subsequently delivered downstream.

One metric alone is insufficient.

End-of-window output

Aether/V2B/OFFER01/RESULT.md

Disposition should be something like:

* OFFER_TRIVIAL
* OFFER_WEAK
* OFFER_REPERTOIRE_SUPPORTED

Then move to Experiment 2 regardless.

⸻

EXPERIMENT 2 — PROP01

MULTI-GENERATION CAUSAL REACH

Window: hour 4 → hour 8

This experiment does NOT ask whether the world is active.

It asks:

Can one local state difference acquire causal descendants beyond the mechanism’s direct one-step action?

Candidate selection — frozen now

Use this rule prospectively:

If OFFER01 earns OFFER_REPERTOIRE_SUPPORTED

Primary candidate = OFFER01 law.

Otherwise

Primary candidate = the exact recoil + exchange law from TEST-3 that earned P1 MECHANISM_SUPPORTED.

Do not invent a third candidate after seeing OFFER01.

In either case include the relevant simpler law as a negative/mechanical comparator:

* exchange-only for an exchange-derived candidate;
* reaim1 where appropriate.

Paired-world assay

Construct paired worlds:

CONTROL

and

IMPULSE

identical in:

* initial state;
* RNG;
* physics stream;
* parameters.

After a deterministic warm-up, make exactly one minimal state difference.

Prefer:

* one bit of one payload byte;

unless the selected law makes another minimal perturbation scientifically cleaner.

No further intervention occurs.

Track both worlds with identical randomness.

Causal tracing

Use the observer/winner channel to construct conservative causal ancestry.

For a newly divergent target:

record a parent only when the difference can be attributed to an already-divergent winning source or its divergent transmitted value.

If attribution is ambiguous:

mark it UNKNOWN.

Never manufacture a complete causal tree from state differencing alone.

Measure:

* divergent site count;
* divergent field count;
* maximum spatial radius;
* causal generation/depth;
* branching;
* descendant count by generation;
* duration;
* extinction time;
* re-entry into previously affected regions;
* fraction attributable to direct mechanical transport;
* fraction requiring secondary divergent writers.

Critical hierarchy

Classify separately:

LOCAL_ONLY

The initial difference dies or remains at the origin.

DIRECT_TRANSPORT

The law mechanically moves/copies it one step but produces no secondary causal descendants.

MULTIGENERATION_CAUSAL

A site altered because of the impulse subsequently alters another site.

PROPAGATION_SUPPORTED

Multi-generation effects reproduce across seeds and materially exceed the simpler-law comparator.

One-step exchange is not propagation.

Counterfactual cut

For the strongest path in each qualifying seed, create a matched counterfactual:

restore or neutralize one intermediate divergent site at a preregistered generation.

Ask whether downstream descendants disappear/change.

This is the load-bearing causal check.

A→B→C is only credited when altering B alters C.

Scale

Expected:

1024²

Use the flight to fit as many paired seeds as possible, preferably 6–8.

The important resource is replicated causal trajectories, not maximum world area.

Success criterion

The interesting threshold is not enormous radius.

Even weak reach matters if real.

A result becomes scientifically interesting when:

* causal depth exceeds the primitive’s direct action;
* descendants exist for multiple generations;
* intermediate intervention changes downstream behavior;
* the result exceeds the mechanical comparator;
* it reproduces.

End-of-window output

Aether/V2B/PROP01/RESULT.md

Disposition:

* LOCAL_ONLY
* DIRECT_TRANSPORT_ONLY
* MULTIGENERATION_WEAK
* CAUSAL_PROPAGATION_SUPPORTED

Move immediately to Experiment 3.

⸻

EXPERIMENT 3 — CONDITIONAL BRANCH

Window: hour 8 → hour 12

The third experiment is selected by a rule frozen before Experiment 1 starts.

There are only two branches.

⸻

BRANCH A — if PROP01 supports multi-generation causal reach

Run:

INTERACT01 — TWO-SIGNAL COMPOSITION

This presses from propagation into primitive integration.

Do not claim computation or intelligence.

Question:

When two independently propagating local differences meet, is the downstream result more than the superposition of the two individual effects?

Four matched arms

Using the best PROP01 law:

* NONE
* A_ONLY
* B_ONLY
* A_PLUS_B

Also, if affordable:

* A_THEN_B
* B_THEN_A

Place A and B far enough apart that each first develops independently.

Choose their separation from PROP01’s observed causal radius, not arbitrarily.

Measurements

Track:

* A footprint;
* B footprint;
* combined footprint;
* overlap region;
* post-overlap descendants;
* causal depth;
* downstream state repertoire;
* persistence;
* sensitivity to input order.

Primary comparison:

Is A+B’s downstream causal state explainable by the union/superposition of A-only and B-only?

Look for:

SUPERPOSITION_ONLY

Combined result is adequately explained by individual trajectories.

INTERACTION_LOCAL

The signals affect one another only at their collision region.

INTERACTION_PROPAGATES

Collision changes later descendants outside the collision region.

HISTORY_SENSITIVE

A-then-B differs reproducibly from B-then-A.

The last two are especially interesting because they imply primitive state-dependent integration.

Counterfactual

Remove/restore the collision-region state and replay.

Do the downstream differences disappear?

No causal credit without this attack.

Scale

Push somewhat larger if throughput permits:

1024² → 2048²

But replication beats size.

Do not burn the window merely to advertise a larger lattice.

Output:

Aether/V2B/INTERACT01/RESULT.md

⸻

BRANCH B — if PROP01 does NOT support multi-generation causal reach

Do not run a meaningless collision experiment.

Instead run:

ROUTE01 — CONTENT-DEPENDENT RETARGETING

AIM02 already said:

faster deterministic re-aim is not the answer.

Test one richer but still primitive retargeting rule.

Baseline:

aeth01.reaim1

Candidate provisional semantics:

aeth01.route1

One law difference:

after a successful write, the winning source’s next direction is determined by the low two bits of the byte it just displaced:

arg0_next = displaced_value & 0x03

Use the same conflict precedence discipline as AIM01/OFFER01.

Everything else remains unchanged.

Do not also change payload.

Do not rotate arg1.

Do not add memory registers.

Do not add a message primitive.

This is deliberately minimal:

local content now affects future routing.

Question

Does coupling route choice to encountered state create causal reach that deterministic +1 re-aim lacks?

Run the same paired impulse assay used by PROP01.

Compare:

* v1/reaim1 as appropriate;
* route1.

Primary measures:

* causal depth;
* spatial radius;
* secondary descendants;
* branching;
* persistence;
* intermediate-cut counterfactual.

Main false friend

displaced_value & 3

may simply act as a noisy/random direction selector.

Therefore compare against a matched direction-randomization/null where possible without creating a sprawling experiment.

The content-dependent rule only matters if state history predicts future routing better than a comparable aim-randomizing process.

Verdict

* ROUTING_NO_GAIN
* ROUTING_RANDOMLIKE
* CONTENT_ROUTING_WEAK
* CONTENT_ROUTING_CAUSAL_REACH

Output:

Aether/V2B/ROUTE01/RESULT.md

⸻

FOUR-HOUR WINDOW MANAGEMENT

Do not spend the first three hours designing an exquisite experiment and leave no production time.

Target per window:

* first ~30–45 min: implementation / fixtures / qualification;
* next ~2–2.5 h: frozen production;
* final ~30–60 min: reduction / attacks / report / commit.

These are guidelines, not exact scheduling requirements.

If qualification reveals production will not fit:

reduce horizon or replication before freezing, based on runtime and convergence only.

Do not resize after seeing scientific outcomes.

⸻

GPU UTILIZATION

Keep M2’s GPU busy whenever production units are ready.

Use safe concurrency established by prior Aether runs.

Record:

* GPU utilization;
* memory;
* temperature;
* unit throughput;
* wall-clock efficiency.

If CPU reduction/analysis can overlap safely with GPU production, overlap it.

Do not let reporting unnecessarily idle the GPU between waves.

⸻

FAILURE POLICY — IMPORTANT

“Fail and rerun once” means:

Technical failure

Examples:

* crash;
* bad fixture;
* instrumentation inconsistency;
* CPU/GPU divergence;
* corrupt artifact;
* runner error;
* accidental resource exhaustion.

Repair once and rerun once.

Scientific falsification

Examples:

* OFFER01 remains two-value shuttle;
* PROP01 stays local;
* INTERACT01 superposes trivially;
* ROUTE01 acts like random aim.

Do not repair the physics and rerun.

Record the null and proceed.

This distinction must be preserved.

⸻

COMMUNICATION

Do not wait for Aporia or Cyclops.

Do not wait for reviewers.

Post useful milestones, especially:

* freeze;
* production start;
* result;
* failure requiring the one allowed repair.

No heartbeat spam is needed merely because 30 minutes passed.

The operator wants experiments, not permission loops.

⸻

END OF 12-HOUR PUSH

After the third window, write one short synthesis:

Aether/V2B/THREE_FLIGHT_SYNTHESIS_2026-10-07.md

Answer only:

1. Did OFFER01 escape the two-value repertoire?
2. Did any law demonstrate true multi-generation causal reach?
3. Did the third experiment show interaction/history dependence, or did richer routing improve reach?
4. Which mechanism is alive?
5. Which mechanisms are dead?
6. What is the single strongest next experiment?

Keep claims runged.

Do not call:

* mobility propagation;
* propagation communication;
* interaction computation;
* history dependence memory;
* any of the above intelligence.

But if we obtain a reproducible chain in which:

A alters B, altered B alters C, and intervening on B removes the effect at C,

treat that as a meaningful threshold and attack it hard in the next campaign.

Start Experiment 1 immediately.
