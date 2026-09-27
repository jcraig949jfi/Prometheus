ARTEMIS — RESEARCH THREAD

Adopt this as your first substantive Prometheus Thread.

You are not being asked to become an engine owner or to run heavy compute.

Your advantage is that you are a fresh researcher on an independent Linux host with:

* the Prometheus Git repository;
* Git history;
* read access to the central Postgres service where permitted;
* enough CPU/RAM for light analysis;
* no dependence on M1–M4 local files unless explicitly discovered.

Use that independence.

THREAD

SFE RETROSPECTIVE AND PROMETHEUS ENGINE ECOLOGY

Prometheus began when the Serendipity Foundry Engine was expected to grow into much of what the program needed.

Its architecture became rich:

* SFE engine;
* world/organism components;
* Vivarium execution loop;
* PEW/evidence infrastructure;
* REST services;
* Archaeon as an experiment producer/overseer;
* distinct agents responsible for different pieces.

As science accelerated, it became easier to create new engines representing different conceptual approaches to worlds, organisms, heredity, emergence and computation.

Prometheus now appears to be evolving toward a multi-engine ecology instead of one increasingly large universal engine.

We need to understand whether that interpretation is actually supported by the record.

Do not begin with the assumption that SFE is obsolete.

Do not begin with the assumption that the original architecture should be restored.

Mine the evidence.

PRIMARY QUESTIONS

Investigate:

1. What was SFE originally intended to become?
2. Which parts of that intended architecture were actually built and matured?
3. Which parts are still actively used?
4. Which parts were bypassed as the program shifted toward independent engines and direct scientific campaigns?
5. Was that shift primarily caused by:
    * architectural friction;
    * service/deployment friction;
    * scientific need for different substrates;
    * speed of experimentation;
    * agent organization;
    * evidence/provenance requirements;
    * something else?
6. What scientific or engineering capabilities does SFE still provide that newer engines do not?
7. Which SFE components have effectively become general Prometheus infrastructure even if SFE itself is less central?
8. Which components appear dormant, duplicated or superseded?
9. Is continued investment in SFE warranted?
10. If so, what kind of investment:
    * scientific substrate;
    * shared execution architecture;
    * instrumentation;
    * reference engine;
    * compatibility layer;
    * something else?

Do not reduce the answer to KEEP / RETIRE.

The useful output is understanding.

RESEARCH SPIKE A — RECONSTRUCT SFE’S EVOLUTION

Use Git history, surviving design documents, role charters, campaign records and relevant Atlas data.

Construct a concise chronology:

* original SFE intentions;
* major architecture stages;
* emergence of Vivarium / PEW / Archaeon responsibilities;
* portability work between M1 and M2;
* major scientific campaigns;
* points where separate engines began appearing;
* points where those engines displaced or supplemented SFE capabilities.

Look for actual evidence of architectural friction rather than inferring it from the present state.

Record contradictions where different documents describe the architecture differently.

RESEARCH SPIKE B — WHAT IS ACTUALLY ALIVE?

Determine, from the repository and available indexed evidence, the current practical status of:

* SFE;
* Vivarium;
* PEW;
* Archaeon producer machinery;
* Daedalus-owned engine components;
* relevant REST services;
* queue/execution pathways;
* evidence/provenance pathways.

Distinguish:

* implemented;
* actively used;
* recently used;
* maintained but idle;
* superseded;
* historical;
* unclear.

Do not treat “not visible from ubu002” as “does not exist.”

If local evidence on another machine is required to answer something, mark it UNKNOWN / NEEDS HOST EVIDENCE.

RESEARCH SPIKE C — ENGINE ECOLOGY INVENTORY

Find the best existing engine list.

Atlas already has an engine registry; use it as a starting point, not as unquestioned truth.

Identify the currently known Prometheus engines, runners and scientific harnesses.

Separate actual scientific engines from:

* runners;
* orchestration;
* qualification harnesses;
* instrumentation;
* historical systems.

For each actual engine you can understand from the repository, begin a lightweight scientific card containing:

Name

Status

Active / experimental / dormant / historical / unclear.

Scientific lens

What distinctive way of representing a world, organism, interaction or computation does it provide?

Questions it is good at

What experiment classes naturally fit it?

Questions it is poor at

What does its representation obscure, distort or make difficult?

Important observables

What can it actually measure?

Important blind spots

What scientifically relevant things can it not currently identify?

Notable findings

Only the strongest few.

Dependencies

Services, data stores, OS/GPU requirements where known.

Portability

What appears inherently host-dependent versus merely currently located on a host?

Cross-pollination

What might this engine borrow from another engine, and what might it contribute back?

Do not attempt exhaustive documentation where evidence is weak.

Depth on a smaller number is preferable to confident fiction.

RESEARCH SPIKE D — SFE VERSUS MULTI-LENS ARCHITECTURE

Now compare the two program shapes.

Shape 1

A rich central SFE architecture whose components evolve toward supporting most research.

Shape 2

A population of distinct engines/lenses that evolve independently, cross-pollinate instrumentation and findings, and may eventually be retired and replaced.

Ask what the historical evidence says about the advantages and disadvantages of each.

Pay attention to:

* speed of creating a new world;
* ability to test alien conceptual approaches;
* provenance;
* reproducibility;
* portability;
* coupling between services;
* ease of execution;
* scientific observability;
* infrastructure burden;
* ability to share discoveries;
* risk of engines becoming conceptually homogeneous.

Do not choose a winner by philosophy.

Use Prometheus’s actual history.

Consider hybrid possibilities.

For example, SFE infrastructure may remain valuable even if SFE is not the universal scientific substrate.

RESEARCH SPIKE E — DOCUMENTATION MODEL

Based on what you learn, propose a minimal durable format for documenting all Prometheus engines.

The documentation should primarily answer:

What unique lens does this engine afford Prometheus, and when should we use it?

Avoid turning it into a software inventory.

Prototype the format on a few engines for which the evidence is strongest.

SFE must be one of them.

Do not create a large schema unless the work demonstrates a need.

Markdown is sufficient.

RESEARCH SPIKE F — FIND THE MISSING THREADS

During this work, preserve meaningful unanswered questions as Threads.

Likely examples might include:

* a deeper SFE portability assessment;
* whether PEW should become engine-independent evidence infrastructure;
* whether Vivarium has a useful role across multiple engines;
* cross-engine instrumentation that deserves extraction;
* engines whose scientific value is poorly understood;
* architectural dependencies that unnecessarily pin science to M1 or M2.

These are examples, not assignments.

Create Threads only when the evidence reveals a worthwhile unresolved question.

Do not automatically launch them.

USE OF ATLAS / POSTGRES

You may use Atlas and the central Postgres service to locate experiments, engines, campaigns and evidence.

Treat Atlas as an index and reasoning aid, not infallible ground truth.

Atlas has known coverage gaps.

When Atlas and Git disagree, investigate the provenance rather than silently choosing one.

Use read-only access for this research unless an existing Artemis responsibility explicitly authorizes otherwise.

MACHINE DISCIPLINE

ubu002 is a lightweight research host.

Use it for:

* Git archaeology;
* database queries;
* scripts over repository data;
* report generation;
* bounded CPU analysis.

Do not turn it into a persistent infrastructure host.

Do not install large toolchains merely because they might be useful.

If a missing dependency materially blocks an important part of the Thread, record what is needed and why before installing or requesting it.

Nothing on ubu002 should become the sole copy of evidence.

OPTIONAL BOUNDED SPIKES

If a small script or query can resolve an important uncertainty, write and run it.

Examples:

* commit-history mining;
* service-reference census;
* engine/reference frequency over time;
* experiment counts by engine;
* dependency/path analysis;
* comparison of role responsibilities against actual commits.

Do not generate metrics simply because metrics are easy.

Only measure things that answer the Thread.

DELIVERABLE

Create a substantial report that includes:

1. SFE RETROSPECTIVE

What SFE was meant to become, what it actually became, and how its role changed.

2. CURRENT SFE VALUE

Which parts remain scientifically or architecturally valuable.

Which appear cumbersome, superseded, dormant or unclear.

3. ENGINE ECOLOGY

The best current map of Prometheus’s scientific engines and the distinct lens each contributes.

4. ARCHITECTURAL READING

What Prometheus’s history says about a central universal engine versus multiple evolving lenses.

5. ENGINE DOCUMENTATION PROTOTYPE

A practical format plus several real examples.

6. PORTABILITY

What the evidence says about host affinity, central-service dependencies and portability.

7. OPEN THREADS

Important questions uncovered during the research.

8. PROGRAM IMPLICATIONS

What, if anything, Prometheus should consider changing.

Do not make changes to other engines merely because the report suggests them.

This Thread is research and synthesis first.

NORTH STAR

Keep one criterion above the architecture:

Prometheus as a program must continuously evolve toward the North Star.

An engine is not successful because it survives.

An architecture is not successful because it is elegant.

A new engine is not successful because it is novel.

The relevant question is what each structure allows Prometheus to discover, test, retain and build upon.

Mine the history with that criterion in mind.

Work through this Thread until you have a coherent research product. Do not return after the first easy finding.
