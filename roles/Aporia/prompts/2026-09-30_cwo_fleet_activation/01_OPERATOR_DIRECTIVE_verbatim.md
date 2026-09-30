APORIA CWO — FLEET ACTIVATION AND CONTINUOUS BUILDER LOOP

Date: 2026-09-30
Baseline: origin/main 01c53f64e
Authority: Operator
Executor / fleet steward: Aporia
Applies to: Hecate, Ensorain, Odysseus, Artemis, Nestor, Ananke, Aether, Bellerophon, Harmonia, Cosmos, Tyche, Aporia, Cyclops, and temporary Builder workers created under this order.

0. Mission

Put the existing fleet to work.

The immediate problem is not a shortage of seats. It is uneven utilization, queues that terminate in HOLD, infrastructure work that becomes blocking work, and useful research threads that do not always produce their own next experiment.

Aporia’s job under this CWO is therefore not to become another scientific decision-maker.

Aporia is the fleet scheduler, backlog maintainer, and blocker clearer.

For every active scientific seat, maintain:

CURRENT → NEXT → RESERVE

There should normally be at least one executable item in CURRENT, two ranked items behind it, and a larger frontier from which replacements can be drawn.

When an item finishes, fails, parks, or becomes blocked, the seat should move immediately to the next admissible item without waiting for a new operator prompt.

⸻

1. Operating doctrine

1.1 HOLD is exceptional

A seat may enter HOLD only when all admissible work in its charter is exhausted, a frozen scientific gate explicitly forbids further work, or continuing would violate a compute, custody, privilege, or contamination boundary.

“Waiting for another seat” is not by itself grounds for inactivity.

If task A is blocked by another seat, move to task B.

1.2 Scientific gates remain real

This CWO does not weaken:

* preregistration boundaries;
* blind or sealed holdouts;
* evidence custody;
* resource caps;
* authorship separation;
* privileged-host restrictions;
* irreversible experiment rules;
* explicit operator gates.

It removes administrative waiting around those boundaries.

1.3 Cross-seat review should not become synchronization

Other seats may attack, reproduce, audit, or falsify work.

They should not become mandatory serial approvers of ordinary work unless the protocol specifically requires independence or custody separation.

A failed audit produces evidence.

It does not automatically create a fleet-wide stop.

1.4 Park aggressively

A scientific line that loses its ruler, is killed by a baseline, becomes redundant, or ceases to discriminate between hypotheses should be PARKED.

Parking a line is success when it reduces the search space.

Move its resources to a better question.

1.5 Preserve anomalies

Weak, strange, contradictory, unfamiliar, or unexplained observations must not disappear merely because the originating program is parked.

Send them to the residual frontier for Tyche, Hecate, Bellerophon, or another appropriate seat.

⸻

2. Builder doctrine

Beginning with this CWO, Aporia may maintain temporary Builder workers continuously.

Builders are not additional scientific authorities and do not originate scientific conclusions.

Their job is to make the ecosystem better while the scientists use it.

Aporia should initially maintain up to three Builder lanes when useful:

BUILDER-FABRIC

Own recurring execution-layer friction:

* broker installation and verification;
* lease lifecycle;
* worker startup/shutdown;
* sandbox execution;
* resource enforcement;
* stale-worker detection;
* failure recovery;
* job receipts;
* safe worker handoff.

The immediate first target is the remaining Odysseus broker/lease cutover path.

BUILDER-EXPERIMENT

Extract repeated experimental machinery into shared infrastructure.

Initial targets:

* preregistration manifests;
* frozen parameter/configuration records;
* named RNG and seed handling;
* baseline/control declarations;
* positive-control checks;
* mutation/falsifier hooks;
* compute-budget declarations;
* run receipts;
* crash accounting;
* provenance;
* artifact hashes;
* result tables;
* standardized PARK / CONTINUE / EXPAND evidence packets.

Do not force every engine into one experimental model.

Build reusable primitives below the engine layer.

BUILDER-OBSERVABILITY

Make fleet state legible.

Initial targets:

* work-order adoption status;
* CURRENT / NEXT / RESERVE queues;
* last successful receipt;
* compute consumed;
* blockers;
* dependencies;
* stale STATE files;
* unread-comms triage;
* active Fabric workers;
* pending decisions;
* sealed-resource status.

A stale state file should become detectable automatically rather than requiring a fleet review to discover it.

Builders may patch common infrastructure and engine tooling through ordinary repository discipline.

They may not alter a frozen experimental protocol after exposure, cross evidence-custody boundaries, inspect sealed holdouts, or silently change scientific semantics.

⸻

3. Seat work queues

HECATE

CURRENT — Explain the novelty failure.

Hecate’s overnight meta-experiment returned zero UNFAMILIAR mechanisms across all arms.

Determine why.

Discriminate at least these possibilities:

* search never generated unfamiliar mechanisms;
* unfamiliar candidates were generated but selected out;
* representation collapsed genuinely different mechanisms together;
* classifiers/rulers mislabeled novelty;
* familiar mechanisms had an overwhelming fitness/economic advantage;
* the definition of UNFAMILIAR itself made the target unreachable.

Do not merely summarize the 15 parked programs. Reconstruct the attrition path.

Produce a mechanism-flow accounting:

generated → admitted → survived → flagged → attacked → parked

and identify where novelty disappears.

NEXT — Alien-lawful Phase 2.

The assay was frozen before model exposure. If its existing preregistration remains intact and no explicit scientific gate forbids execution, run the prepared Phase 2 without redesigning it from knowledge gained afterward.

RESERVE — Novelty-generator interventions.

Design bounded generator-side interventions informed by the novelty autopsy. New mechanisms should be generated and then attacked, not merely renamed variants of existing mechanisms.

⸻

ENSORAIN

LM01 remains HOLD under MWO-0004 G3.

Do not launch it.

CURRENT — Continue ARC3 development lines within the existing compute budget and PKG-F constraints.

Prioritize development that increases the discriminatory power of future worlds rather than simply producing more worlds.

NEXT — Baseline hardening.

Ensure every relevant world/economy can survive cheap non-organismic competitors such as constants, simple running statistics, trivial compressors, or similarly low-complexity predictors before expensive intelligence searches consume it.

RESERVE — Substrate collider improvements.

Develop mechanisms that increase structural diversity among admissible worlds and make substrate-specific discoveries distinguishable from generic statistics.

⸻

ODYSSEUS

CURRENT — Finish the Fabric broker transition.

Close the work represented by the final broker-install path, including the report referenced around #917.

Obtain the Nestor and Archaeon lease-cutover acknowledgements when available.

Do not spend an entire work cycle waiting for acknowledgements.

NEXT — Remove obsolete lease detection once the required acknowledgements make that safe.

RESERVE — Builder-Fabric work.

After the cutover, Odysseus becomes the primary scientific customer and technical guide for BUILDER-FABRIC.

Use the problems encountered during this deployment to eliminate entire classes of future deployment friction.

⸻

ARTEMIS

CURRENT — Reconcile D001.

Determine the actual disposition of the ten submitted Fabric tasks.

Update STATE and produce missing receipts for completed, failed, lost, or still-running jobs.

The fleet must not rely on stale state when the execution system already knows the answer.

NEXT — D002.

Construct the next bounded batch from the highest-value ready items in Artemis’s charter.

Prefer tasks that exercise or validate the new Fabric under real workload rather than synthetic plumbing tests alone.

RESERVE — Fabric reliability adversary.

Feed recurring failure modes discovered through D001/D002 to BUILDER-FABRIC and independently attempt to break repaired paths.

⸻

NESTOR

CURRENT — Acknowledge the Odysseus lease cutover after independently confirming the relevant state.

Do not remove or weaken the D2 firewall.

NEXT — NPE frontier.

Resume Nestor’s highest-value admissible research frontier.

Give priority to experiments that discriminate genuinely endogenous reproductive organization from seeded, transplanted, environmental, input-gated, or bookkeeping artifacts.

Do not spend new compute merely reproducing already-closed claims.

RESERVE — next-day NPE campaign design.

Maintain at least one preregistered bounded campaign ready for execution when the evidence warrants it.

The dedicated custodian / child-account host modification remains a privileged operation to perform only when D2 designation actually requires it.

The 67 unread messages are not themselves a work item. Triage them for active dependencies and decisions; archive or defer irrelevant history.

⸻

ANANKE

The compute hold was legitimate.

Do not violate the 48 core-hour budget.

CURRENT — Zero/low-compute analysis until budget frees.

Prepare the T-SWAP-REL4 analysis plan, expected discriminators, controls, and failure interpretations.

NEXT — T-SWAP-REL4 when the rolling resource window legally admits it.

RESERVE — Analyze before expanding.

The result of REL4 should determine the next branch. Do not automatically scale the experiment.

⸻

AETHER

The rcv_add / rcv_str line has answered its present questions.

CURRENT — Close the broker dependency.

Consume Odysseus’s final broker-install result when available.

While waiting, rank the candidate Aether follow-ups by:

1. falsifiability;
2. expected information gain;
3. ability to distinguish causal mechanisms;
4. compute cost;
5. reusability of the resulting infrastructure.

NEXT — Run the highest-ranked bounded follow-up after the broker path is cleared.

Prefer controlled interventions over additional observational correlations.

RESERVE — Engine improvement.

Feed GPU execution, memory, lifecycle, crash, and measurement friction into the Builder lanes so AGE becomes easier to experiment with after every campaign.

⸻

BELLEROPHON

FP-001 is complete.

Bellerophon should not remain idle because that line closed.

CURRENT — Independent emergence replication lane.

Select the strongest currently unresolved emergence-like or mechanism-change signal available from the active fleet that can be reconstructed without violating custody or contamination rules.

Candidates may come from Hecate, Tyche, Ensorain, Nestor, or Bellerophon’s own residual catalogue.

Rebuild the phenomenon inside BEE’s independent toolbox where feasible.

The goal is not confirmation.

Attempt to make the phenomenon disappear.

NEXT — Mutant/falsifier expansion.

Any surviving phenomenon should receive automatic adversarial transformations before being promoted.

RESERVE — Generalize useful BEE controls into BUILDER-EXPERIMENT.

⸻

HARMONIA

There is presently no Cosmos D2 claim to adjudicate.

That does not require Harmonia to sit idle.

CURRENT — Evidence-system audit.

Sample recent completed or parked claims across the fleet and test whether the evidence packets actually support the stated dispositions.

Prioritize:

* Hecate’s overnight program closures;
* Fabric-backed results;
* recent baseline kills;
* claims dependent on frozen preregistration.

Harmonia is an auditor, not a routine permission gate.

Report defects and severity.

Only stop work when an existing protocol says the discovered defect invalidates continued execution.

NEXT — Ruler quality.

Look for rulers that are saturated, trivially gamed, unreachable, or unable to discriminate the intended mechanism.

RESERVE — Shared audit primitives for BUILDER-EXPERIMENT.

⸻

COSMOS

HARD SCIENTIFIC GATE REMAINS IN FORCE.

C3’s coordinate audit was rejected.

Cosmos must not inspect, execute against, or otherwise consume D2.

D2 remains sealed.

The unresolved operator choice is:

A. close C3 as killed before holdout use; or
B. authorize a successor preregistration that must first beat the zero-parameter baseline.

Aporia must surface this as the fleet’s only current scientific operator decision.

Do not allow it to block unrelated fleet work.

While the decision is pending, Cosmos may:

* complete the C3 failure autopsy;
* identify exactly why the coordinate audit failed;
* design, but not execute, a possible successor protocol;
* demonstrate on public/development data how that successor would beat the zero-parameter baseline;
* improve public Cosmos tooling;
* prepare future-world generators that cannot expose D2.

No D2 access.

No successor experiment is authorized by this CWO.

⸻

TYCHE

Tyche’s Dark Residual / Dark Ecology charter is now authoritative.

CURRENT — Boot into the charter and leave HOLD.

Build the first residual catalogue from phenomena discarded, unexplained, contradictory, or weakly anomalous across recent Prometheus experiments.

Residuals should retain provenance back to the experiment that generated them.

NEXT — Dark Ecology assay.

Cluster residuals by behavior rather than by originating engine and look for repeated structures appearing across otherwise unrelated substrates.

Prioritize anomalies that are:

* cross-engine;
* reproducible;
* cheap to probe;
* difficult to explain with existing baselines;
* structurally strange.

RESERVE — Residual perturbation.

Turn the best residuals into bounded experiments.

Tyche should complement Hecate:

Hecate attacks generated candidate mechanisms.

Tyche searches the garbage pile for structure we did not know to ask for.

⸻

CYCLOPS

Cyclops is not restored as a second fleet coordinator.

On next boot:

CURRENT — Adopt the current work-order model and repair STATE.

Reconcile its local state against the current CWO/MWO lineage.

NEXT — One bounded observability audit.

Independently compare reported fleet state with actual repository/process/comms evidence and report mismatches to Aporia and BUILDER-OBSERVABILITY.

After that audit, PARK unless Aporia assigns a concrete bounded task.

Do not recreate the previous coordination layer.

⸻

APORIA

Aporia owns execution of this CWO.

Its product is flow, not scientific opinion.

Maintain the fleet queue.

At every useful coordination cycle:

* ingest changed STATE, receipts, comms, and commits;
* identify completed CURRENT items;
* promote NEXT automatically;
* refill NEXT and RESERVE from each seat’s charter/frontier;
* identify resource conflicts;
* hand infrastructure defects to Builders;
* detect stale seats;
* distinguish real scientific gates from administrative waiting;
* surface only genuine operator decisions.

Aporia should not rewrite seat science merely to keep seats busy.

The backlog must contain meaningful work.

⸻

4. Operator-escalation rule

Do not ask the operator to decide routine scheduling, implementation details, queue order, normal experiment continuation, ordinary merges, or recoverable infrastructure work.

Escalate when the action would materially change one of these:

* consume or expose a sealed holdout;
* break a frozen preregistration;
* relax a scientific validity gate;
* perform a privileged host/security modification;
* exceed an explicit resource/spend envelope;
* create an irreversible custody conflict;
* reinterpret a result in a way that changes a frozen decision rule;
* start a major campaign lacking existing authority.

At issuance of this CWO, Cosmos C3 is the only known active scientific decision requiring operator resolution.

Everything else should move.

⸻

5. Queue and state format

Every live seat should converge on a state representation containing at least:

CURRENT — executable now
NEXT — promoted automatically after CURRENT
RESERVE — ranked frontier
BLOCKED — dependency and owner
RESOURCE STATUS — compute / GPU / spend where relevant
LAST RECEIPT — latest completed evidence
LAST STATE UPDATE
WORK ORDER — active CWO/MWO identifier

If CURRENT becomes blocked, promote an admissible NEXT item and leave the dependency in BLOCKED.

Do not turn the whole seat into BLOCKED.

⸻

6. First fleet pass

Aporia should immediately perform one activation pass in this order:

Infrastructure unblock: Odysseus → Artemis → Nestor → Aether.

Already-running science: Hecate → Ensorain → Ananke.

Reactivate useful idle capacity: Tyche → Bellerophon → Harmonia.

Hard-gated but still productive: Cosmos public-side analysis only.

State repair: Cyclops.

Continuous improvement: start Builder lanes from the defects exposed by the above work.

This ordering is for the first pass only.

Afterward, schedule by expected scientific value, evidence quality, urgency, resource availability, and blocker removal rather than permanent seat precedence.

⸻

7. Success condition

This CWO succeeds when Prometheus reaches a steady state in which:

* scientific seats normally have ready work without operator prompting;
* completion automatically exposes the next experiment;
* infrastructure defects generate Builder work rather than multi-seat waiting;
* hard gates protect science without freezing unrelated work;
* parked experiments feed residuals and lessons back into the ecology;
* stale state is automatically visible;
* Aporia can tell the operator, in one short report, what the fleet is doing and exactly which decisions genuinely require human authority.

The objective is not maximum activity.

The objective is maximum useful scientific throughput with preserved experimental integrity.

Commit this CWO, broadcast it to the live fleet, populate CURRENT/NEXT/RESERVE from the assignments above, and begin the first activation pass.
