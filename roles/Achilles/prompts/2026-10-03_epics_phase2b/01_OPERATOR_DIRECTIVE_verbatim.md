Perfect.  Adapt this as you see fit:

Achilles — Establish the Prometheus Epic Layer and Phase 2-B

You are Achilles.

This is another fleet-structure / control-plane setup assignment.

You are not joining Phase 2-B science.

You are not joining Phase 3 engineering.

You are not becoming the coordinator of either Epic.

Your job is to extend the Git-native work graph so Prometheus can run several large programs in parallel without mixing task ownership or starving useful legacy science.

Implement this on main.

⸻

1. Add the Epic layer

The durable hierarchy is now:

[
\text{Epic}
\rightarrow
\text{Thread}
\rightarrow
\text{Campaign}
\rightarrow
\text{Experiment}
\rightarrow
\text{Task}
\rightarrow
\text{Attempt}
]

Experiment remains optional where inappropriate.

Engineering campaigns may legitimately use:

Epic → Thread → Campaign → Task → Attempt

Scientific campaigns may use the full chain.

Do not require fake Experiment objects merely to satisfy hierarchy.

⸻

2. Meaning of each level

Epic

A long-lived strategic program.

An Epic defines:

* strategic objective;
* scope;
* governing constraints;
* start/status;
* major operator decisions;
* success/continuation conditions;
* constituent Threads;
* resource-policy references;
* explicit exclusions.

An Epic is not claimed by an agent.

Individual scientific claims do not inherit meaning from the Epic name.

Thread

A durable capability, scientific question, or operating process.

A Thread may survive many Campaigns.

Campaign

A bounded attempt to advance a Thread.

Campaigns have concrete scope, resources, entrances, exits and receipts.

Experiment

A registered scientific comparison or assay where applicable.

Task

A bounded unit of work assignable through the distributed work graph.

Attempt

One execution of a Task by an agent/model/runtime.

⸻

3. Important evidence rule

Encode or document:

Evidence rolls upward. Interpretive authority does not.

An Experiment can support a Campaign result.

Several Campaigns can change a Thread’s status.

Several Threads can advance an Epic.

But an experiment inside an Epic named “Recursive Sagacity” does not inherit a recursive-sagacity claim.

Claims remain attached to the exact cells/evidence that earned them.

⸻

4. Establish three peer Epics

Create three current top-level Epics:

EP-GLOBAL

Prometheus Global Operations

Status: ACTIVE / PERMANENT

Start: existing program history

End date: NONE

This Epic is intentionally permanent.

It contains cross-phase processes that should survive Phase 2, Phase 3 and whatever follows.

It is not a parent Epic for the numbered phases.

EP-GLOBAL, EP-PHASE2B, and EP-PHASE3 are peers.

⸻

EP-PHASE2B

Prometheus Phase 2-B — Engine Hardening, Re-exploration and Residual Discovery

Status: ACTIVE

Purpose:

Return to the Phase 2 engines, seats, organisms, worlds and scientific machinery with everything learned from the forensic deep dives.

Repair what was broken.

Re-run what deserves re-running.

Re-test ideas that were abandoned for procedural rather than scientific reasons.

Execute experiments that could not previously be interpreted cleanly.

Allow repaired engines to continue searching for phenomena.

Phase 2-B is not a rollback from Phase 3.

It is a parallel experimental program that exploits the scientific and engineering capital already accumulated.

⸻

EP-PHASE3

Prometheus Phase 3 — Recursive Sagacity Observatory and Developmental Physics of Cognition

Status: ACTIVE

This should encompass the existing RSO work.

Move or annotate the current RSO Thread/Campaign linkage so C-004 and subsequent RSO work resolve under EP-PHASE3.

Do not change current Phase 3 scientific design.

Do not disturb the current RSO builder-cell launch.

⸻

5. GLOBAL Epic

Create at least one initial permanent Thread under EP-GLOBAL.

Global Evidence Refinery Thread

Create a durable Thread representing the established workflow:

[
\text{Aporia}
\rightarrow
\text{Techne}
\rightarrow
\text{Nyx}
\rightarrow
\text{Harmonia}
\rightarrow
\text{Atlas}
]

Use the repository’s existing names and descriptions where available rather than inventing conflicting responsibilities.

Conceptually this is the permanent Prometheus evidence/refinement loop:

* Aporia: coordination/publication/intake as currently chartered;
* Techne: fossils/specimens/artifact characterization;
* Nyx: adversarial chop-shop / mechanism attack;
* Harmonia: measurement/ruling/adjudication;
* Atlas: indexing/knowledge integration/frontier state.

Do not rewrite their existing charters to force this simplified description if their canonical roles are more precise.

Instead create a Thread document describing how their existing capabilities compose into the persistent workflow.

This Thread has no end date.

Individual Campaigns within it may close.

The Thread persists.

⸻

6. Phase 2-B primary Thread

Create:

Phase 2-B Engine Hardening & Re-exploration

This is the primary initial Thread under EP-PHASE2B.

Mission:

Revisit Phase 2 engines and scientific seats using the failure corpus and Phase 3 forensic findings; repair instrumentation and implementation faults, replay important experiments, and continue bounded exploration where there remains plausible scientific value.

This Thread should accept many Campaigns over time.

Do not create one enormous Campaign.

⸻

7. Phase 2-B scientific posture

Phase 2-B exists because Phase 2 produced real value even though many conclusions were weakened by later forensic analysis.

The deep dives identified:

* seeded/endogenous lineage confusion;
* weak provenance;
* rulers that could not detect their purported target;
* trivial baseline failures;
* memorization mistaken for intelligence;
* location/coordinate leakage;
* source-reading mistaken for causal mechanism;
* search/reachability failures;
* controls that could not fail;
* reset/carryover defects;
* answer leakage;
* holdout contamination;
* same-substrate/self-agreement;
* instrumentation assumptions favoring familiar architectures;
* scheduler/engine defects;
* stale and under-used experiments;
* promising ideas never cleanly tested.

Phase 2-B treats this as a repair and opportunity map.

Do not treat every old positive as valid.

Do not treat every old null as final.

The appropriate status of many historical results is:

worth re-running after apparatus repair.

⸻

8. Initial Phase 2-B Campaign pattern

Do not centrally create hundreds of detailed tasks.

Instead establish a standard Campaign template for each returning engine/seat.

An engine’s first Phase 2-B Campaign should normally contain:

A. Feedback ingestion

Read the relevant Phase 3 forensic findings and historical failure records.

Identify which findings actually apply to this engine.

Do not mechanically accept accusations that do not fit the implementation.

B. Defect triage

Classify findings:

* CONFIRMED_DEFECT
* ALREADY_REPAIRED
* NOT_APPLICABLE
* NEEDS_DISCRIMINATOR
* SCIENTIFIC_LIMITATION
* OPEN

C. Repair

Fix implementation/instrumentation defects that materially affected interpretation.

Add regression fixtures.

D. Replay

Re-run the most important historical experiments affected by those defects.

Preserve original receipts and compare old/new outcomes.

E. Residual science

Identify experiments from the historical backlog that still have substantial information value.

Prefer cheap discriminating probes before large campaigns.

F. Continued exploration

If the engine remains scientifically useful after hardening, permit new bounded campaigns.

Phase 2-B is not limited to reproducing old work.

It may discover new phenomena.

⸻

9. Candidate Phase 2-B engine seats

Do not invent ownership where the repository already has canonical owners.

Inspect the current fleet and historical engine mappings.

The Phase 2-B Thread should be structured so relevant seats can join over time, including likely engines/seats such as:

* Archaeon / SFE
* Nestor / NPE
* Bellerophon / BEE
* Aether / AGE
* Ensorain / TensorTrain worlds
* Cosmos / CWE
* Crius, where residual work remains meaningful
* Aphrodite
* Harmonia
* Techne
* Nyx
* Theophrastus
* and other Phase 1/2 engines identified by the forensic crawlers.

Do not automatically reactivate a closed engine solely because it exists.

Its first Campaign may legitimately conclude:

NO_JUSTIFIED_FURTHER_WORK.

Conversely, an engine previously parked may reopen if the forensic findings reveal that the earlier null was apparatus-limited.

⸻

10. Preserve charters

Phase 2-B seats keep their native charters.

Do not homogenize them into one Phase 2-B role.

Their diversity is valuable.

Phase 2-B adds a shared program objective and task-routing context.

The seat remains Archaeon, Nestor, Cosmos, etc.

Phase 2-B does not rename them or erase historical identity.

⸻

11. Phase 2-B task distribution

Phase 2-B may use the global distributed-work/A2A system.

A Phase 2-B seat may create tasks for:

* itself;
* another appropriate Phase 2-B seat;
* shared scientific support seats;
* Harmonia;
* Techne;
* Nyx;
* Atlas;
* other globally available seats whose charters permit the work.

Use the existing A2A task/capability rules.

Prefer explicit task packets over informal coordination.

⸻

12. Hard isolation from the RSO builder cell

This is a firm operator rule.

The five RSO development seats:

* Palamedes
* Pallas
* Argus
* Cadmus
* Eupalamus

operate only under EP-PHASE3 unless the operator explicitly changes that rule.

They must not opportunistically claim Phase 2-B work.

They must not be used as spare engineering capacity for old engines.

Add an epic-scope restriction to their role/task eligibility if the work-graph machinery supports it cleanly.

For example:

allowed_epics = ["EP-PHASE3"]

or equivalent.

Do this at the role/task eligibility level rather than relying on memory.

Pallas/Fable is especially scarce and must not get consumed by Phase 2-B merely because an adversarial task exists.

⸻

13. Add Epic scope to distributed work

Extend the global work-graph objects minimally.

Threads carry:

epic_id

Campaigns carry:

epic_id
thread_id

Tasks should inherit the Epic through their Campaign and may redundantly carry an immutable resolved epic_id if that improves validation.

Task claiming must be able to enforce a seat’s Epic scope.

Do not invent a second scheduler.

Extend the existing workgraph tooling.

Validate:

* Campaign belongs to existing Thread;
* Thread belongs to existing Epic;
* Task’s resolved Epic is consistent;
* seat is permitted to claim that Epic.

⸻

14. Resource sharing between Phase 2-B and Phase 3

We want work-conserving compute, not static partitioning.

Phase 3 has scarce model resources associated with its dedicated builder seats.

Phase 2-B must not consume those seats.

Physical CPU/GPU machines, however, should not sit unused merely because Phase 3 is currently in design, review or integration.

Implement/document a general opportunistic resource policy:

Idle physical compute may be leased by another Epic when doing so does not interrupt a higher-priority active lease.

Phase 2-B should therefore be capable of using spare:

* CPU;
* GPU;
* experiment workers;
* machine-local execution capacity;

when Phase 3 does not currently require them.

Use leases and resource ceilings.

Do not hard-bind Phase 2 engines permanently to spare hardware.

A higher-priority active reservation should not be preempted by a lower-priority Campaign unless explicitly allowed.

Prefer natural lease expiry/release to complex preemption machinery.

⸻

15. Suggested scheduling priority

Document this as an initial policy, not a universal scientific ranking:

1. safety/infrastructure repair;
2. active operator-directed Phase 3 critical-path work;
3. active registered Phase 3 experiments;
4. Phase 2-B registered experiments;
5. exploratory/background Phase 2-B sweeps;
6. opportunistic maintenance/backlog work.

This governs scarce shared machine resources.

It does not mean Phase 2-B science is intellectually less important.

The purpose is simply to protect the currently active Phase 3 build while recovering otherwise idle capacity.

⸻

16. Phase 2-B experiment philosophy

Phase 2-B should favor:

* repaired historical experiments;
* falsification of old positives;
* resurrection of apparatus-limited nulls;
* cheap new discriminators suggested by the deep dives;
* unexplored branches already latent in engine backlogs;
* searches that can run deterministically without model inference;
* campaigns that exploit idle CPU/GPU windows;
* cross-engine comparison where instrumentation is now adequate.

It should not require every experiment to wait for Phase 3 RSO integration.

The old engines are themselves experimental apparatus.

Let them work.

⸻

17. Relationship to Phase 3 RSO

Phase 2-B and Phase 3 should inform one another without creating a dependency cycle.

Phase 2-B may generate:

* repaired engines;
* failure fixtures;
* strange specimens;
* new counterexamples;
* candidate cognitive architectures;
* world designs;
* search mechanisms;
* anomalous findings.

These can later become RSO inputs.

But Phase 2-B does not have to port everything into the RSO before running it.

Likewise, useful RSO measurement tools may later migrate into Phase 2-B when stable.

Do not make Phase 2-B wait for that future.

⸻

18. Cross-Epic findings

Add or document a lightweight way for one Epic to emit a finding relevant to another without moving the work itself.

For example:

* Phase 2-B discovers an architecture candidate → notify Phase 3;
* Phase 3 qualifies a new reset test → Phase 2-B engines may adopt it;
* GLOBAL refinery discovers a recurring defect → route to both.

A cross-Epic notification is not automatic task reassignment.

The receiving Epic decides whether to create work.

⸻

19. GLOBAL versus numbered Phase Epics

Make the distinction explicit.

GLOBAL

Forever processes.

Examples:

* evidence refinery;
* fleet observability;
* coordination infrastructure;
* durable scientific registries;
* reusable failure corpus;
* potentially shared resource brokerage.

PHASE2-B

Engine hardening and continued discovery using the Phase 1/2 machinery.

PHASE3

RSO construction and developmental-physics science.

Future Phase 4, etc., should be able to coexist without killing GLOBAL.

⸻

20. Initial directory/layout

Follow current workgraph conventions rather than this exact spelling if necessary, but conceptually provide:

ops/
  epics/
    EP-GLOBAL/
      EPIC.json
      README.md
    EP-PHASE2B/
      EPIC.json
      README.md
    EP-PHASE3/
      EPIC.json
      README.md
  threads/
    TH-GLOBAL-EVIDENCE-REFINERY/
    TH-P2B-ENGINE-HARDENING/
    TH-P3-RSO-BUILD/

Connect existing Phase 3 C-004 beneath the RSO Thread without rewriting its scientific contents.

Do not renumber historical objects merely for aesthetics.

⸻

21. Phase 2-B launch state

After setup, do not automatically launch huge engine campaigns.

Create enough structure that returning seats can bootstrap, discover the Phase 2-B Thread, and create/claim their first bounded hardening Campaign.

If useful, create one template or example Campaign such as:

P2B-ENGINE-REENTRY

with instructions for feedback ingestion → defect triage → repair → replay → residual science.

Do not create generic tasks that pretend to know each engine’s failure history.

The engine owner should instantiate its own Campaign from the template using the forensic sources relevant to it.

⸻

22. Phase 2-B forensic pointers

The Epic/Thread documentation should point to the Phase 3 forensic crawler outputs and major failure corpora already in Git.

At minimum make discoverable the work produced by:

* Sisyphus
* Tityos
* Tantalus
* Ixion
* other relevant Phase 3 forensic sources

and engine-specific historical reports.

Do not copy their contents into every Campaign.

Link to them.

⸻

23. Reporting

Achilles should extend its fleet reporting so Epic/Thread context can eventually be shown for active tasks.

At minimum the underlying data should permit:

* active Epic;
* active Thread;
* Campaign;
* Task;
* model/capability class;
* machine;
* current state.

Do not turn this assignment into a large dashboard build.

Data compatibility is enough.

⸻

24. Tests

Add or amend tests for:

* Epic schema;
* Thread → Epic validation;
* Campaign → Thread validation;
* Task Epic resolution;
* RSO builder EP-PHASE3-only eligibility;
* valid Phase 2-B seat claiming Phase 2-B work;
* rejected cross-Epic claim by a restricted seat;
* permanent Epic accepting no end date;
* Campaign closure not closing its Thread or Epic;
* GLOBAL Thread persistence;
* existing C-004 remaining valid after the hierarchy extension.

Do not break existing workgraph packets.

Provide backward compatibility or a deterministic migration.

⸻

25. Do not disturb active work

Palamedes may already be beginning C-004.

Do not block or rewrite active Phase 3 work unnecessarily.

The Epic layer should be an additive control-plane refinement.

If a migration can be represented by adding parent references without changing an active packet’s semantics, do that.

⸻

26. Deliverables

On main, deliver:

1. Epic primitive in the work graph;
2. EP-GLOBAL;
3. EP-PHASE2B;
4. EP-PHASE3;
5. permanent Global Evidence Refinery Thread;
6. Phase 2-B Engine Hardening & Re-exploration Thread;
7. Phase 3 RSO Build Thread containing/pointing to current C-004;
8. task/seat Epic-scope enforcement;
9. RSO builder restriction to EP-PHASE3;
10. Phase 2-B Campaign template;
11. forensic-source pointers;
12. opportunistic resource-sharing policy;
13. cross-Epic notification convention;
14. tests;
15. a concise setup receipt.

⸻

27. Completion criterion

When complete, James should be able to do either of these:

You are Nestor. Bootstrap from Prometheus and enter Phase 2-B.

and Nestor can discover the hardening Thread, relevant source material, and create/claim appropriate work.

Or:

You are Palamedes. Bootstrap from Prometheus.

and Palamedes sees only its Phase 3 RSO engineering scope and cannot accidentally consume Phase 2-B work.

Meanwhile the permanent GLOBAL evidence-refinery Thread remains active independently of either program.

⸻

28. Final principle

Prometheus should no longer behave as if starting a new phase requires killing the previous experimental ecosystem.

Phase 3 is allowed to construct the new observatory.

Phase 2-B is allowed to keep mining, repairing and challenging the machinery that taught us why the observatory was necessary.

GLOBAL preserves the processes that should outlive both.

Build the control plane so all three can operate simultaneously without confusing their authority, resources or task ownership.
