AETHER — NEXT ROUND

Current authoritative base:

origin/main = 698144bce

AETH-02 is closed.

AETH-03 Physics Design Round 01 is complete.

RunPod Engineering Iteration 2 is complete.

You do not need permission from Aporia or Cyclops for Aether work or comms.

Use comms for coordination, evidence requests, broadcasts, and technical collaboration — not approval.

⸻

PRIMARY MISSION — RUNPOD ITERATION 3

Proceed with the RunPod Engineering Ladder.

Iteration 3 is:

long-run reliability + controlled failure injection

The objective is to make the platform trustworthy before scientifically irreplaceable multi-hour/day GPU experiments arrive.

Long-run flight

Run a representative GPU workload long enough to exercise:

* sustained telemetry;
* artifact growth;
* cost accumulation;
* timeout logic;
* controller state;
* provider polling;
* cleanup;
* restart/recovery assumptions.

The science workload can remain simple.

The experiment is the platform.

Measure continuously:

* GPU memory used/reserved;
* GPU utilization;
* temperature/power where exposed;
* CPU/RAM/disk;
* application throughput;
* latency distribution;
* telemetry overhead;
* artifact growth;
* provider/API latency;
* estimated accumulated spend;
* controller health.

Look specifically for:

* memory creep;
* throughput drift;
* telemetry drift;
* log growth surprises;
* polling degradation;
* artifact-server failure;
* clock disagreement;
* controller/resource state disagreement.

Failure injection

Exercise as many failures as possible through the fake/chaos provider first.

Then use real RunPod only where a real-provider behavior must be qualified.

Include at least:

* process exits nonzero;
* process hangs;
* timeout;
* artifact server disappears;
* artifact corruption;
* telemetry stalls;
* controller interruption/restart;
* create response lost after acceptance;
* LIST omission;
* GET/LIST disagreement;
* transient DELETE failure;
* ambiguous provider response;
* partial artifact retrieval.

Do not intentionally create an unrecoverable paid-resource state.

Every injected failure should answer:

1. What does the controller believe?
2. What does the provider believe?
3. What evidence survives?
4. Can the run resume?
5. Can the resource be cleaned safely?
6. Does the final receipt distinguish uncertainty from absence?

No blind create retry.

⸻

ITERATION 3 SUCCESS GATE

Iteration 3 passes only if the platform can survive a long flight and the relevant failure modes while preserving:

* exact ownership;
* recoverable state;
* durable evidence;
* honest disposition;
* safe cleanup;
* bounded spend.

If Iteration 3 is clean, continue directly into Iteration 4 scale-out unless a real reliability defect deserves repair first.

⸻

NEXT SCALE-OUT TARGET

Iteration 4 should exercise:

2–3 concurrent Pods

using independent shards.

Examples:

* seeds;
* parameter slices;
* replay cases;
* benchmark shards.

One shard should fail harmlessly while the others complete.

The controller must:

* preserve successful shards;
* isolate failed shards;
* avoid artifact collisions;
* maintain per-Pod cost;
* maintain per-Pod cleanup evidence;
* aggregate the final run honestly.

Do not let one shard failure collapse the whole campaign unless the module contract explicitly requests fail-fast behavior.

⸻

SCIENCE SIDECAR — AETH-03 PHYSICS LADDER 2

Do this on CPU first.

Do not spend GPU money on a candidate until it earns it.

Read:

Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md

Use its proposed second ladder — including mov, rcv, m4 as actually defined there — rather than reinventing those names from memory.

The evidence from Round 01 changes the central question.

It is no longer primarily:

Can state persist?

It is:

Can a local state difference causally propagate into a larger region under primitive local physics?

⸻

PROPAGATION ASSAY

Build a clean paired-world assay.

Two worlds are identical except for one minimal perturbation at tick 0.

Prefer one-bit difference unless the candidate semantics requires a different smallest valid perturbation.

Track the divergence footprint over time.

At minimum measure:

* number of differing sites;
* number of differing fields;
* maximum spatial radius reached;
* connected components of divergence;
* causal descendants where observable;
* duration of divergence;
* whether divergence dies;
* whether divergence expands;
* whether it branches;
* whether it returns/re-enters previously affected regions;
* whether propagation survives with external perturbation disabled.

Do not equate raw Hamming distance with meaningful propagation.

Separate:

DIRECT MECHANICAL SPREAD

Differences forced immediately by the changed local transition.

SECONDARY CAUSAL SPREAD

Sites that differ because previously affected sites subsequently altered them.

SUSTAINED PROPAGATION

Causal influence continues for multiple generations beyond the initial neighborhood.

That distinction is load-bearing.

⸻

WHAT WOULD BE INTERESTING

We do not need explosive growth.

Weak propagation is enough if it is real.

A candidate deserves follow-up if, relative to v1 and appropriate controls:

* divergence reliably escapes the immediate neighborhood;
* affected radius grows over multiple generations;
* causal depth exceeds a few transition steps;
* spread persists without injected perturbation;
* multiple pathways carry the influence;
* perturbing an intermediate region changes downstream spread;
* the mechanism is not simply a hard-coded global broadcast.

A small but reproducible multi-step causal chain is more interesting than a huge footprint produced directly by one primitive.

⸻

WHAT KILLS A CANDIDATE

Kill or demote a physics candidate if:

* the difference remains local;
* propagation is entirely one-step mechanical copying;
* all growth disappears when external perturbation is removed;
* the rule directly encodes the desired communication architecture;
* spread saturates immediately into uniform noise;
* propagation requires pathological parameter tuning;
* it destroys the useful null controls that make comparison possible.

⸻

ONE MECHANISM AT A TIME

Continue the Round-01 discipline.

Each candidate changes one meaningful physical assumption.

Do not combine failed mechanisms merely because each almost worked.

If mov, rcv, or m4 fails, record why.

If one shows a signal, replicate it before composing it with anything else.

Only after individual mechanisms are understood may you test combinations.

⸻

ADD AS AN IMPORTANT CONTROL

Include add from Round 01 as an unresolved comparator.

Its increased activity was largely constant-step counting:

* approximately 83% of extra endogenous change;
* approximately 86% tracing to the same source as the previous tick.

So ask whether add actually increases causal propagation depth, not merely state-change rate.

If its footprint still remains local, close it.

Do not credit counting as communication.

⸻

CHEAP SCOUT DESIGN

Favor many small scouts over long runs.

The previous round showed that cheap scouts are effective at killing bad physics.

Use enough seeds to distinguish a mechanism from a lucky trajectory.

Do not push anything to GPU simply because one seed looks interesting.

Suggested progression:

small smoke
→ multiple CPU seeds
→ adversarial/negative controls
→ intervention
→ only then GPU-scale scout.

The exact sizes and tick counts should come from measured CPU economics and the existing design document.

⸻

NO STEERING YET

Do not reward propagation.

Do not optimize a score for spreading farther.

We are still determining which primitive physics naturally permits causal propagation.

A reward for propagation now would manufacture exactly the thing we are trying to determine whether the substrate can support.

Observation and intervention only.

⸻

RUNPOD PLATFORM FEEDBACK LOOP

Use every science scout to improve the platform where appropriate.

The platform should increasingly support:

dry-run → scout → calibrated estimate → campaign

Make the scout-calibration path reusable across seats.

The canonical receipt should retain:

* spec-sheet estimate;
* representative-scout estimate;
* actual campaign cost;
* prediction error.

The Iteration-2 result is now a regression case:

* scout-calibrated estimate: approximately 5.9% high;
* spec-sheet-only estimate: approximately 37% low.

The platform should make the better path the easy path.

⸻

REPORTS

RunPod:

Aether/RUNPOD_ENGINEERING_03_2026-09-26.md

Science:

Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md

For the science report separate:

CANDIDATE PHYSICS

PROPAGATION ASSAY

OBSERVED

INTERVENTION RESULTS

MECHANISTIC EXPLANATION

KILLED CANDIDATES

UNRESOLVED CANDIDATES

CANDIDATES THAT EARNED SCALE-UP

If none propagate, say so.

That would be an important result.

If one produces even weak but genuine multi-generation propagation, stop treating it as merely another activity metric and attack it with falsifiers.

⸻

OPERATING POSTURE

RunPod engineering is the primary mission.

Propagation-physics scouts run alongside it when they do not interfere.

Do not wait on Aporia or Cyclops.

Do not spend GPU money merely to keep Aether busy.

Do not keep mining aeth01.v1.

Build the flight system.

Search for physics with causal reach.

Proceed.
