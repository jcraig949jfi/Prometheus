AETHER — MULTI-HOUR RESEARCH BLOCK

You have completed AETH-02 closure, AETH-03 ladders 1–2, and RunPod platform Iterations 2–4.

Do not perform one small next task and return for another instruction.

Work this as a coherent research block over several hours. There are several related research spikes below. Follow the evidence, preserve negative results, and return when there is a meaningful synthesis.

The purposes of this block are:

1. determine whether Aether’s current propagation assay is as exact as claimed;
2. sharpen the scientific search rather than simply adding more neighboring laws;
3. use Aether as a second real test of Prometheus Campaign / Experiment / Task execution;
4. determine how much Aether work is portable across the growing machine fleet;
5. produce a durable description of Aether’s unique scientific lens.

Do not turn Aether into the universal Prometheus scheduler.

Aether is the test bed, not the control plane.

BLOCK A — ATTACK THE PROPAGATION ASSAY

Start with Q1 from the external review packet.

rcv introduces one bit of per-site state: whether the site received a winning write on the previous tick.

The current exact-generation argument says that a newly differing site must have had a differing causal neighbour.

Audit whether this remains strictly true when the complete rcv state is considered.

Specifically determine:

* Does the twin difference predicate include the receive flag?
* Can the two twins have equal five-byte visible state but different receive flags?
* If yes, can that hidden difference subsequently produce a visible difference without a currently visible differing neighbour?
* Does arbitration, replenishment, contest membership, or any other keyed operation create an analogous hidden causal path?

Do not defend the existing instrument.

Try to break it.

If the proof is incomplete, repair the assay so the causal state includes everything necessary and rerun the smallest sufficient controls and existing evidence needed to determine whether AETH-03 conclusions change.

Add adversarial fixtures for any failure mode you find.

Deliverable:
AETH-03/PROPAGATION_ASSAY_AUDIT.md

Conclude one of:

* exact argument survives;
* exact after repair, prior results unchanged;
* prior propagation measurements require reinterpretation.

BLOCK B — REASSESS WHAT RCV ACTUALLY TAUGHT US

Treat the following distinction explicitly:

A phenomenon can be real while still being substantially supplied by the rule that was designed to produce it.

Ask whether rcv taught us anything beyond:

received -> fires once

Do not answer rhetorically.

Use the existing causal-generation data and mechanism probe.

Separate:

* behavior forced directly by the rule;
* consequences of that behavior that were not trivial from the definition;
* amplification supplied by perturbation;
* any transformation or composition of propagated information;
* any evidence that the substrate itself organizes the relay rather than merely executing it.

Decide whether rcv should remain UNRESOLVED, be treated as a calibration/positive-control law, or receive another clearly scoped interpretation.

Do not change the historical record. Record a new interpretation if warranted.

BLOCK C — TIME-SCALE BEFORE SPACE-SCALE

Investigate the question:

Could Aether’s propagation tests be missing slow causal processes because the observation horizon is 400–500 ticks?

Do not assume that a larger lattice answers this.

Reason from the locality radius and observed footprint.

Design a bounded CPU study that varies TIME substantially before AREA.

For example, where feasible, compare horizons such as:

* 500;
* 2,000;
* 10,000 ticks;

at a lattice size large enough that boundaries cannot explain the result.

Use fewer origins/seeds if necessary to keep this bounded.

The purpose is not to produce a giant campaign.

It is to determine whether conclusions about locality materially depend on the observation horizon.

If long-horizon CPU cost becomes significant, use a scout before escalating.

No GPU scale-up unless the result creates a specific reason for it.

BLOCK D — MOVE BEYOND THE ONE-CHANGE TRAP

The one-change-per-law rule has been useful for causal attribution.

It may also exclude interactions.

Do not abandon it.

Instead, determine whether the accumulated results now justify a small second stage where already-understood mechanisms can be combined.

Build a compact mechanism inventory from AETH-02/AETH-03.

Examples may include:

* persistence/memory;
* propagation;
* conditionality;
* resource transfer;
* perturbation coupling;
* state-dependent activation;
* value transformation.

Do not treat this list as privileged.

Use what the evidence actually supports.

Then design a SMALL, preregistered combination search focused on interactions that cannot be expressed by changing one mechanism at a time.

Avoid recognizable hand-built computational architectures where possible.

We are not trying to smuggle a conventional computer into the lattice.

Prefer minimal changes whose joint behavior is uncertain.

The question is:

Are there interactions between primitive local mechanisms that create qualitatively new causal behavior that neither mechanism exhibits alone?

A negative answer is acceptable.

Do not launch a large combinatorial explosion.

A handful of well-chosen combinations plus controls is enough for this block.

BLOCK E — USE FWD AS A CALIBRATION, NOT A DESTINATION

Implement or analyze fwd only if useful as a positive/control rung.

Its purpose is to answer:

If the law directly supplies content forwarding, do our assays correctly recognize content transport?

Then attack it.

Determine whether it merely transports bytes unchanged along a supplied relay, or whether anything endogenous happens to the content.

Do not count direct forwarding itself as the sought scientific phenomenon.

If fwd becomes scientifically interesting for some unexpected reason, follow the evidence.

Otherwise keep it as an instrument/control.

BLOCK F — SECOND PROMETHEUS DISTRIBUTED-WORK PILOT

Aether is now the second test bed for the emerging:

Thread -> Campaign -> Experiment -> Task -> Attempt

model.

Use the existing lightweight structure. Do not build a general scheduler.

Create or use one Aether Thread corresponding to the open physics question:

Under what minimal local physics can causal influence propagate, transform, persist, or compose without the desired architecture simply being encoded in the law?

Organize the work in this research block into a Campaign with Experiments/Tasks only where that structure is useful.

Then execute several real units away from BUCKKEEP if a reachable compatible worker exists.

Prefer lightweight Linux nodes for CPU units.

The objective is to test whether Aether’s work units:

law + seed + origin batch + arm -> result

are genuinely portable.

For each moved unit preserve:

* pinned code;
* hashed inputs;
* platform-independent invocation;
* result identity/hash;
* resource use;
* verification;
* cleanup.

Do not add worker GitHub credentials merely because they are absent.

An orchestrating seat may commit on behalf of a disposable executor.

Do not invent infrastructure merely to satisfy this exercise.

Record only friction that actually occurs.

BLOCK G — FIXED BENCHMARK + OPEN SCIENCE

Test an important distinction in the Campaign/Task model.

Create two small workload classes.

Known-answer lane

Use frozen Aether workloads whose expected outputs are already known.

These are for testing:

* task dispatch;
* retries;
* duplicate execution;
* deterministic equality;
* missing-unit detection;
* reducer completeness;
* cleanup.

Open-science lane

Use genuine unanswered AETH-03 work.

These are for testing whether the same machinery tolerates:

* nulls;
* failed hypotheses;
* unexpected measurements;
* post-run scientific interpretation;
* Tasks that expose new Tasks or Threads.

Do not make the fixed benchmark masquerade as science.

Do not make open science responsible for proving basic queue correctness.

Report what each lane revealed that the other could not.

BLOCK H — RUNPOD PLATFORM NEXT STEP

Before a substantial multi-hour GPU campaign, determine whether estimated spend can be reconciled against actual provider billing.

Run the smallest useful reconciliation exercise.

Record:

* provider quote;
* controller estimate;
* receipt estimate;
* actual billed amount if available;
* discrepancy and likely source.

Do not spend materially just to test accounting.

For Iteration 5, prefer one of these:

1. fly an already-existing GPU-suitable workload from another Prometheus seat; or
2. if no honest candidate exists, demonstrate that the Aether platform can accept a workload module with no Aether-specific assumptions.

Do not manufacture a fake cross-seat workload solely to claim portability.

The question is whether the RunPod platform is becoming a Prometheus asset rather than an Aether-only convenience.

BLOCK I — AETHER ENGINE CARD

Produce the first mature version of Aether’s engine/lens documentation.

It should answer scientifically useful questions, not merely list files.

Include:

Scientific lens

What does Aether allow Prometheus to ask that other current engines do not?

World

What sort of artificial physics exists here?

Organism assumptions

What is NOT built in?

What entities, if any, must emerge before organism-like language would be justified?

Best experiment classes

What questions should we preferentially send to Aether?

Bad fits

What questions would Aether distort or make unnecessarily difficult?

Observability

What causal facts can Aether measure exactly?

What remains ambiguous?

Known physics

Summarize the important established behavior of aeth01.v1 and the tested variants.

Search frontier

What parts of law-space have actually been explored?

What large regions remain untouched?

Runtime

CPU/GPU/RAM expectations.

Dependencies

What genuinely must be reachable?

Portability

Distinguish BUCKKEEP as Aether’s current control host from any actual architectural requirement.

Cross-pollination

Which instruments or ideas from other Prometheus engines might improve Aether?

Which Aether instruments might improve them?

Preserve Aether’s distinct lens.

Do not homogenize the engines.

BLOCK J — FRONTIER SYNTHESIS

At the end of the block, step away from the code.

Ask:

Is Aether still creating useful North-Star information?

Do not interpret that as “did Aether find life/computation?”

Consider:

* what negative results removed from the search space;
* what mechanisms were learned;
* whether the substrate is exposing useful causal principles;
* whether the science is converging on a sharper search;
* whether Aether’s strongest contribution is becoming instrumentation rather than substrate science.

Create Threads for meaningful open lines rather than automatically starting them.

In particular distinguish:

* continue current physics;
* modify the search strategy;
* preserve Aether as an experimental benchmark;
* cross-pollinate its instruments elsewhere;
* retire a scientific line while retaining its tooling.

Do not protect Aether merely because you built it.

Do not kill it merely because positives are rare.

The criterion is whether continued work is likely to move Prometheus toward the North Star.

FINAL RETURN

Return one integrated report containing:

ASSAY

Did the exact causal-generation argument survive adversarial review?

SCIENCE

What changed in our interpretation of rcv and propagation?

What did longer horizons and/or mechanism combinations show?

DISTRIBUTED WORK

Which Aether Tasks ran away from BUCKKEEP?

What did portability actually require?

CAMPAIGN MODEL

What did known-answer and open-science lanes teach us about the emerging Prometheus work model?

PLATFORM

Is RunPod ready to support other Prometheus work, and is its cost accounting adequate?

ENGINE LENS

What unique perspective does Aether contribute?

FRONTIER

What should Aether investigate next?

What new Threads were created?

What should be stopped, retained, or transferred elsewhere?

Do not return after the first interesting result.

Continue through the block unless a genuine scientific or safety condition makes later work invalid.

Do not create work merely to consume time.

We are testing whether a Claude research seat can own a substantial theme of work, perform multiple research spikes and experiments, distribute execution where useful, and return with a program-level synthesis.
