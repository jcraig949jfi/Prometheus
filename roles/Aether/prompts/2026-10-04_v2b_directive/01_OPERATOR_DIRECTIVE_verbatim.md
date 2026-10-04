TH-P2B-AETHER-V2B — Aether V2-B: Causal Physics and Content-Transport Maturation

Epic: EP-PHASE2B — Engine Hardening & Re-exploration
Owner: Aether
Model: Claude Code Opus 5.5
Status: ACTIVE / autonomous
Existing scientific threads: TH-007, TH-008, TH-009, TH-010, TH-011, TH-012
Authority: Operator directive, 2026-10-04

Mission

Aether investigates the minimal local physics under which causal influence can:

propagate → carry content → transform content → compose content → persist as reusable structure

without the desired behaviour merely being written into the local rule.

Phase 2 established an exact deterministic substrate, strong replay/conformance machinery, a one-bit twin causal assay, several carefully scoped nulls, and two replicated super-additive activity-propagation effects.

Phase 2-B matures the entire experimental apparatus and moves the scientific frontier from:

“does activity spread?”

to:

“can information-bearing state move, change and combine through a dynamically changing medium?”

Aether operates as an iterative foundry:

design/repair → test → observe → diagnose → modify physics/instrument → test.

The objective is not to manufacture an interesting cellular automaton.

The objective is to discover which primitive physical ingredients permit increasingly rich causal organization and to distinguish those ingredients from artefacts of the ruler, energy bookkeeping, injected noise, frozen residue or rules that directly encode the phenomenon.

Governance

Aether is an autonomous Phase 2-B research seat.

Aether does not require an Aporia dispatch, CWO assignment or other coordinator instruction to select and execute eligible work inside this Thread.

This supersedes current WORK_STATE.json language stating READY -- awaiting Aporia assignment.

Aporia and CWOs remain valid sources of delegated work.

CWOs may delegate work to Aether; they do not activate Aether.

At every window boundary Aether checks applicable CWO work and may incorporate compatible delegated work into the next DEV or TEST window.

Delegated work does not reset the scientific programme.

A CWO does not silently terminate or suspend this Thread unless the operator explicitly says so.

Infrastructure emergencies may preempt a future window but should not interrupt an atomic frozen experiment unless required for safety or resource integrity.

Existing Threads remain the scientific record

This Thread coordinates rather than replaces Aether’s existing research threads.

TH-007 — Minimal causal physics

Umbrella scientific question:

Under what minimal local physics can influence propagate, transform, persist or compose without the desired architecture being encoded directly in the law?

TH-008 — Content on a mutable medium

Asks whether actual content, rather than merely activation timing, can propagate and change while the medium itself is dynamically rewritten.

TH-008 is a central V2-B frontier.

TH-009 — Frozen-medium problem

Asks for minimal physics producing endogenous template turnover without injected perturbation, trivial counting or re-randomisation.

TH-009 is upstream of TH-008 and becomes an active V2-B research axis.

TH-010 — Known-answer execution benchmark

Preserve as a machinery calibration lane.

It tests dispatch, retries, determinism, missing units and reducers.

It produces no scientific evidence about Aether physics.

TH-011 — Transferable causal instrument

Owns transfer of one-bit twins and counterfactual-parent attribution to other deterministic engines.

It remains available as an outward-facing instrument programme.

TH-012 — Execution platform

RunPod/Fabric/platform machinery is supporting infrastructure.

V2-B fixes it when it blocks science, but Aether should not allow infrastructure engineering to consume the scientific programme.

Starting scientific position

Exact substrate

Aether’s base substrate is unusually well specified:

* exact integer state;
* synchronous local updates;
* hash-keyed state-free randomness;
* replay identity;
* independent CPU/GPU-shaped implementations;
* differential conformance;
* exact cross-host unit hashing.

Scale itself is no longer the principal uncertainty.

Activity propagation

The original aeth01.v1 medium is largely frozen.

Most one-change variants do not propagate one-bit differences appreciably.

rcv propagates, but by defining its own relay. It therefore serves as a calibration law rather than a discovery.

rcv_add and rcv_str produce replicated super-additive propagation beyond their individual components.

These effects are real at the level measured by the twin assay.

They are not evidence of content transport.

rcv_str causal mechanism

E-009 replicated rcv_str.

E-010 showed that replacing energy-steered aim with static random aim collapses propagation to approximately the rcv level.

E-012 showed that freezing aim to the warm-up energy snapshot also collapses the effect.

Its preregistered verdict is:

DYNAMIC_COUPLING_REQUIRED

with S = 6/128, exactly at the declared boundary.

The appropriate V2-B interpretation is not that 6/128 is a magical transition.

The important result is that the effect depends strongly on ongoing coupling between changing energy and changing aim.

The next useful experiment is therefore a response curve, not another binary lesion.

rcv_add causal mechanism

E-011 showed that preventing relay writes from accumulating removes much, but not all, of the rcv_add effect.

The lesion leaks because later ADD writes can preserve information originating in a relay-written value.

Completing this causal analysis requires provenance of the value itself.

Main instrument failure

The current content metric failed its own fwd positive control in rich soup.

Therefore Aether currently has a strong instrument for:

where a difference travels

but an inadequate instrument for:

where a value came from and how it was transformed.

No negative result about content transport should constrain the programme until that defect is repaired.

The V2-B causal-information ladder

Every scientific experiment should state which rung it addresses.

P0 — EXACT

The physics and observation path replay exactly and pass conformance.

P1 — ENDOGENOUSLY MOBILE

The medium rewrites itself without injected perturbation and without merely counting or randomising.

P2 — CAUSALLY PROPAGATING

A local intervention produces downstream causal differences beyond its immediate neighbourhood.

P3 — CONTENT CARRIED

A downstream value retains causal ancestry from an upstream content value.

P4 — CONTENT TRANSFORMED

Descendant content remains causally attributable to the source even though its byte value has changed.

P5 — CONTENT COMPOSED

A descendant value depends causally on two or more distinct upstream content lineages.

P6 — CONTENT PERSISTED

Information-bearing ancestry survives through multiple local rewrites rather than a single forwarding hop.

P7 — DYNAMICALLY ROUTED

The route is determined by evolving medium state rather than by a static path explicitly specified in the law.

P8 — REUSABLE ORGANIZATION

A persistent configuration influences later construction or processing as a coherent reusable structure.

Later Aether programmes may add reproduction/heredity rungs, but Beta V2-B should not skip ahead to them.

Activity is not content

Aether maintains separate concepts for:

* activity propagation;
* state difference;
* byte/value ancestry;
* transformed ancestry;
* composed ancestry;
* persistent organization.

An increase in one does not imply the next.

In particular:

a larger twin-difference cone is not evidence that content moved.

Value-provenance observatory

The first major V2-B instrument is an external shadow provenance system.

It must not expose metadata to the simulated physics.

For every relevant committed byte/value, the observatory should be able to record an operation and causal parent set.

Examples:

replacement/copy

* one value parent;

ADD or other composition

* previous target value parent;
* incoming payload parent;

perturbation

* prior value parent;
* mutation/perturbation event;

arbitration

* provenance records the winning proposal without treating losing proposals as value parents.

The provenance representation should permit both:

* exact last-writer questions;
* ancestry-DAG questions across many generations.

A transformed byte does not lose provenance merely because its numeric value changes.

This distinction is essential for detecting actual transformation and composition.

Provenance qualification

The detector must earn scientific use.

At minimum it should contain known-answer fixtures for:

1. direct forwarding;
2. no forwarding;
3. transformed forwarding;
4. two-parent composition;
5. perturbation;
6. overwritten ancestry;
7. arbitration between competing writers.

fwd must become a positive control that the instrument can actually see in rich soup.

A purpose-built transformed-content calibration law is allowed as an instrument fixture.

Such a hand-authored law can qualify the detector but can never count as a scientific discovery.

Physics-search doctrine

Aether may alter and expand the physics.

Aether should not remain trapped forever inside one-change variants around B-balanced v1.

However, each candidate law must have a declared mechanism class and an explicit cheap-shortcut attack.

A candidate cannot earn a scientific positive merely because its code directly says:

* forward this value;
* fire after receiving;
* preserve this path;
* copy this origin;
* compose these exact fields.

Such laws are useful as calibration controls.

They do not answer TH-007.

Aether should increasingly prefer law-generating procedures, bounded enumerations, recombinations and unfamiliar mechanism families over a succession of intuitively hand-authored “interesting” rules.

The proposal process may explore broadly.

The final assay must remain separated from the mechanism used to propose the law strongly enough to avoid simply optimizing against the ruler.

Noisy change is not a mutable medium

TH-009 requires endogenous medium mobility.

The following do not qualify by themselves:

* injected perturbation;
* unconditional counters;
* trivial cycling;
* periodic re-randomisation;
* direct replay of the driving rule;
* high turnover with no causal persistence.

A medium candidate should report turnover together with ancestry persistence, causal dependence and temporal structure.

Energy regimes are experimental variables

Nearly all historical Aether science used one B-balanced energy regime.

V2-B treats energy physics as an explicit independent variable rather than background truth.

At least one alternative regime should be tested before generalising a frozen-medium result across Aether physics.

The purpose is not parameter sweeping for its own sake.

Regime changes should distinguish hypotheses about what limits medium mobility and causal propagation.

4-hour operating cadence

Aether alternates:

DEV/DESIGN → TEST/EXPERIMENT → DEV/DESIGN → TEST/EXPERIMENT

in four-hour windows.

Durable campaign state records:

* cycle;
* window type;
* active Thread;
* physics version;
* observatory version;
* experiment/version;
* attempt;
* last disposition;
* unresolved defects;
* next intended window.

A missed wake does not trigger catch-up bursts.

Execute the currently due window once.

A long deterministic experiment may finish in place.

Fabric/PrometheusWorkers may execute frozen units while Aether retains experiment ownership.

DEV/DESIGN window

Each DEV asks:

What most limited the information returned by the previous TEST?

Possible answers include:

* law expressivity;
* frozen medium;
* energy regime;
* causal reach;
* content detector;
* provenance loss;
* shortcut law;
* positive-control failure;
* lesion leakage;
* insufficient origin diversity;
* statistical boundary artefact;
* executor/infrastructure defect.

Aether modifies the narrowest limiting layer.

Valid DEV work includes:

* provenance instrumentation;
* new physics;
* law generators;
* lesions;
* calibration controls;
* alternative energy regimes;
* observatory changes;
* replay/conformance repair;
* mechanism-specific rulers;
* counterfactual interventions;
* experiment design.

Every DEV concludes with:

1. tested apparatus or physics changes;
2. a design/repair report;
3. a frozen next TEST.

TEST/EXPERIMENT window

A TEST executes one frozen scientific question.

It may contain multiple arms and many deterministic units.

It may:

* replicate history;
* vary a causal mechanism;
* evaluate a new local law;
* compare energy regimes;
* test content ancestry;
* test medium mobility;
* transfer an instrument.

Each result explicitly distinguishes:

TECHNICAL_FAILURE
MEASUREMENT_FAILED
CONTROL_FAILED
UNTESTABLE
NO_EFFECT
PARTIAL
MECHANISM_SUPPORTED

and the relevant P0-P8 rung.

A null at P4 cannot be interpreted if P3 was not measurable.

A propagation null cannot constrain a mechanism if the candidate medium was frozen before the mechanism had an opportunity to operate.

Technical reruns

A technically failed experiment may be rerun up to three times after the original attempt.

Technical failures include:

* worker/process failure;
* corrupt output;
* replay mismatch;
* missing unit;
* failed conformance;
* lost artifact;
* executor failure;
* malformed receipt.

Normally an intervening DEV diagnoses the problem.

If the repair changes the scientific variable, the repaired run receives a new experiment version.

Scientific nulls and partial results do not automatically receive another run.

After three technical reruns, close BLOCKED_TECHNICAL unless explicitly reopened.

Boundary results

Preregistered thresholds remain binding for their experiment.

But a mechanical threshold crossing does not become a claim that nature has a discontinuity at that threshold.

For results near a boundary, Aether should prefer:

* effect curves;
* dose responses;
* confidence/uncertainty reporting;
* mechanism interventions;

over repeated attempts to move the count across the categorical boundary.

E-012’s 6/128 result is the standing example.

Known-answer lane

TH-010 remains permanently available as an execution calibration.

Before trusting a materially new executor path, reducer or provenance pipeline, Aether may run cheap known-answer units.

Passing TH-010 says only:

the machinery transported the experiment correctly.

It says nothing about the science.

External review

Every TEST produces a detailed review packet.

Every substantial DEV produces a design/repair packet.

External review is advisory and asynchronous unless the operator explicitly creates a gate.

Fresh-context adversarial reviewers are encouraged.

Their filesystem/context independence must be stated accurately.

Evidence / Git contract

Every completed window produces, as appropriate:

* code;
* frozen design/preregistration;
* exact physics semantics ID;
* observatory/provenance version;
* inputs/seeds/origins;
* receipts and hashes;
* result;
* interpretation;
* limitations;
* replay instructions;
* external-review questions.

Then:

commit → push → merge to main.

Failures, nulls and broken instruments are merged.

Historical records are not rewritten to make later interpretations cleaner.

Thread success

Aether V2-B succeeds if Prometheus can increasingly distinguish:

activity from information;

difference from ancestry;

copying from transformation;

transformation from composition;

frozen residue from persistent dynamic structure;

energy bookkeeping from causal organization;

and a rule that directly encodes a behaviour from physics in which that behaviour emerges through interaction.

A self-replicator is not required.

A positive content-transport result is not required.

The required product is a better physics foundry and a better causal observatory.
