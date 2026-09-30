APORIA CWO-2026-09-30B

FINISH-IN-PLACE, BLOCKER ESCALATION, AND FLEET CENSUS

Date: 2026-09-30
Observed baseline: origin/main 51f1e7abc9931d4954c8c1fc5298b77e677a651b at 2026-09-30T12:56:52Z
Authority: Operator
Executor: Aporia
Scope: Every presently live Prometheus seat, agent, worker-principal, and Builder operating under the work-order model.

This CWO supplements MWO-0004 and supersedes the portions of CWO-2026-09-30 that require automatic promotion from CURRENT to NEXT or require a blocked seat to pivot to unrelated work.

All scientific validity, custody, security, compute, preregistration, holdout, and privilege gates remain in force.

⸻

0. PURPOSE

The fleet is active.

The immediate objective is now completion rather than expansion.

Agents should seek to finish the work they already have in hand.

Do not pivot merely because another interesting task exists.

Do not begin a new scientific line merely because the present line becomes inconvenient.

Do not automatically promote NEXT when CURRENT closes.

Aporia’s job during this CWO is to make the work already underway visible, help remove its blockers, and drive existing work to clean closure.

The operating sequence is now:

DECLARE → FINISH → REPORT → READY

not:

CURRENT → NEXT → RESERVE automatically

⸻

1. FINISH-IN-PLACE RULE

Upon receiving this CWO, every agent shall identify its IN-FLIGHT SET.

The IN-FLIGHT SET consists of work that was genuinely underway before adoption of this CWO, including:

* the seat’s existing CURRENT item;
* experiments already started;
* preregistered experiments whose execution has already begun;
* child workers or Fabric tasks already submitted;
* analyses already underway;
* repairs already being implemented;
* review/adjudication already in progress;
* bounded supporting work necessary to close one of the above.

The seat should finish those items.

It should not use this CWO as a reason to abort healthy work.

It should also not broaden the work.

A new hypothesis, new experiment, new campaign, new major implementation line, new Builder lane, new residual search, or NEXT/RESERVE item is not part of the IN-FLIGHT SET merely because it is nearby or attractive.

⸻

2. NO AUTOMATIC PIVOT

Effective immediately, the following previous-CWO behavior is suspended:

CURRENT finishes → automatically promote NEXT

and:

CURRENT blocks → move to another unrelated item

Instead:

When CURRENT finishes

Close it cleanly.

Write the receipt/result/state necessary to make the closure durable.

Notify Aporia.

Enter READY / FINISHED-CURRENT.

Do not self-promote NEXT.

When CURRENT fails scientifically

Record the failure according to the existing protocol.

Notify Aporia.

Do not rescue the line by inventing a different experiment.

Do not convert the failure into a new CURRENT without Aporia’s direction.

When CURRENT becomes blocked

Stay on the same objective.

Perform only work directly useful to finishing or unblocking that objective.

Notify Aporia immediately through the comms channel or A2A Fabric.

Do not silently promote NEXT.

When an already-running child task continues after CURRENT nominally closes

Allow it to finish if stopping it would destroy useful work or violate the experimental protocol.

Declare it to Aporia as part of the IN-FLIGHT SET.

Do not spawn replacements or extensions.

⸻

3. BLOCKER ESCALATION

A blocked agent must tell Aporia rather than solving scheduling by changing research questions.

Use either:

Prometheus comms → Aporia

or:

A2A Fabric → Aporia

Use whichever path is functioning.

If the primary path fails, use the other.

Do not require both.

A blocker notification shall contain:

SEAT
CURRENT ITEM
BLOCKED SINCE
BLOCKER
EVIDENCE / RECEIPT
OWNER OF DEPENDENCY, IF KNOWN
EXACT ACTION NEEDED
SAFE WORK REMAINING ON THE SAME ITEM
WHETHER COMPUTE / WORKERS ARE STILL RUNNING

Aporia shall acknowledge and route the blocker.

Aporia may ask another agent to perform a specific unblocking action.

That is not authority to redirect either seat into a new scientific program.

⸻

4. MANDATORY STATUS HEARTBEAT TO APORIA

Every live agent shall send Aporia one status heartbeat upon adoption of this CWO.

This heartbeat is operational telemetry, not a scientific report.

Do not interrupt or kill a healthy running job merely to produce it.

Each heartbeat must contain:

SEAT: canonical seat name

HOST / INSTANCE: machine and agent/session identifier if available

UPTIME: elapsed uptime of the present agent/session; include session start timestamp in UTC if known

MODEL: exact model/version string reported by the runtime; do not normalize or guess it

BRANCH / HEAD: current working branch and commit if applicable

STATE: WORKING / ACTIVE / BLOCKED / HOLD / PARKED / READY

CURRENT WORK: concise description of what the agent is actually doing now

IN-FLIGHT SET: experiments, workers, jobs, analyses, or repairs already underway

PROGRESS: concise factual progress so far

BLOCKERS: none, or the blocker and owner

RESOURCE STATE: active leases, workers, GPU/CPU use, paid spend if relevant

FINISH CONDITION: what constitutes completion of the current item

NEXT ACTION ON COMPLETION: REPORT TO APORIA — DO NOT SELF-PROMOTE

Do not manufacture model or uptime information.

If an exact datum is unavailable, report UNKNOWN and the reason.

⸻

5. DURABILITY WITHOUT STATUS-CHURN

The immediate heartbeat should travel through comms or A2A.

Agents do not need to create a Git commit solely to tell Aporia their uptime or model version.

Continue maintaining WORK_STATE.json, experiment receipts, reports, and other durable scientific records when the underlying work changes.

Aporia owns the consolidated fleet status.

Aporia should create or maintain one fleet-level census containing the latest heartbeat for every live agent.

The census should include at minimum:

Seat	Host/instance	Uptime	Model	State	Current work	Blocker	Last heartbeat

The census must be based on live-seat discovery plus heartbeats, not only the existing ops/fleet/QUEUE.json.

⸻

6. LIVE-SEAT DISCOVERY

Aporia shall reconcile the fleet using:

* comms presence / comms who;
* A2A Fabric presence where available;
* current WORK_STATE.json files;
* recent repository activity;
* active Fabric workers/tasks.

Existing queue membership is not sufficient evidence that a seat is or is not live.

The repository review preceding this CWO already identified one concrete discrepancy:

Nyx and Techne are active but absent from the existing Aporia fleet queue.

They are part of this census and shall receive this CWO.

Likewise, any other live seat discovered by comms or A2A receives the finish-in-place rule even if it is absent from QUEUE.json.

A seat that has no work and no charter should report that fact rather than inventing work.

⸻

7. APORIA’S ROLE DURING THIS CWO

Aporia is a completion coordinator.

Aporia should know, for every live seat:

* what is actually running;
* how long the current agent/session has been alive;
* which model is operating it;
* what constitutes completion;
* what is blocking completion;
* what external action can remove that blocker;
* whether the seat has finished and is READY.

Aporia shall not optimize utilization by forcing research pivots.

Idle capacity is acceptable during this stabilization round.

Clean completion is more valuable than keeping every CPU or model continuously occupied.

Aporia may:

route blockers;
resolve ownership;
request missing receipts;
authorize repairs directly necessary to finish CURRENT;
coordinate shared infrastructure needed by an in-flight item;
reconcile stale state;
mark seats READY after completion.

Aporia may not, under this CWO alone:

promote NEXT;
launch RESERVE;
create a new scientific program;
start a new Builder lane;
resurrect a parked campaign;
redirect a blocked scientist into unrelated research simply to keep it busy.

⸻

8. OBSERVED IN-FLIGHT SNAPSHOT

The following is the GitHub-observed state at issuance.

It is a snapshot, not a reassignment.

Hecate

Working the alien-lawful Families B/C line under the frozen preregistration and deviation record, with Harmonia audit work attached.

Free-tier quota is a blocker for portions of the run.

Instruction: finish this line. If quota prevents progress, report BLOCKED to Aporia. Do not pivot into a new novelty program.

Ensorain

Working ARC3 / PKG-F development: W-DRIFT, low-count per-cell power, and the LM02 window-sufficiency problem.

LM01 remains separately blocked by MWO-0004.

Instruction: finish the presently active ARC3 item. Do not launch LM01 or self-promote into a new substrate line.

Odysseus

Working BUILDER-FABRIC issues arising from the Fabric deployment.

promexec round-2 acceptance remains blocked on a privileged operator broker install.

Instruction: finish what can be finished on the existing Fabric line and report the privileged blocker to Aporia. Do not open a new infrastructure program.

Artemis

D002 has been submitted: 11 Fabric script tasks, with the completion barrier running.

Instruction: let D002 finish, reconcile all results and receipts, report closure to Aporia, then stop.

Do not construct D003 automatically.

Nestor

Working the current NPE frontier item: choose and preregister the next discriminating endogenous-vs-task/input-gated experiment.

Instruction: complete the currently defined item to its existing closure criterion and report it.

Do not automatically promote its NEXT execution step unless Aporia explicitly authorizes continuation.

D2 remains separately gated.

Ananke

T-SWAP-AUDIT3 / W-Z has just completed.

Its frozen 95% consistency bar was missed at 92.7%, with the discrepancy recorded as seed sensitivity near the threshold.

Nothing was running at the last state update.

Instruction: report FINISHED-CURRENT / READY to Aporia.

Do not auto-promote another T-SWAP or T-INS experiment.

Aether

Working E-012, the rcv_str frozen-energy-snapshot lesion line.

promexec round 2 remains a separate infrastructure blocker.

Instruction: finish E-012 within its existing scope. Report closure or blocker. Do not promote the value-provenance detector automatically.

Bellerophon

E-BEL-REPL-01 closed and the previous CWO automatically promoted E-BEL-REPL-02.

E-BEL-REPL-02 is now genuinely underway and therefore belongs to the IN-FLIGHT SET.

Instruction: finish E-BEL-REPL-02.

Do not promote E-BEL-BUILD-01 afterward.

Harmonia

Working the evidence-audit stream; the latest observed commit audited Bellerophon E-BEL-REPL-01.

Some adjudication work is waiting on Nyx material; D2 has no claim to adjudicate.

Instruction: finish reviews already in hand. If waiting on a required packet, report BLOCKED to Aporia rather than selecting a different audit sample merely to remain busy.

Cosmos

Stopped at the C3 hard gate.

D2 remains sealed and unspent.

Instruction: remain at the gate and report HOLD/BLOCKED status to Aporia.

Do not consume D2 and do not create a successor C3 experiment under this CWO.

Tyche

Working the v2 Dark Ecology / pressure-map build following the operator v2 directive.

Instruction: finish the currently active v2 build scope.

Do not automatically promote from build into a separately queued pilot, preregistration, Block R, Block M, residual perturbation, or other later stage unless that stage was already genuinely underway before receipt of this CWO.

Nyx

Active outside the current Aporia queue.

Current work is the full-domain ASAL replication packet, with existing dependencies on Harmonia and host capability.

Instruction: finish the replication packet work already underway. Route dependencies to Aporia. Do not pivot to the POET-enhanced NEXT item merely because ASAL blocks.

Techne

Active outside the current Aporia queue.

Current item is the provenance-grade answer requested by Nyx concerning the 19 source records.

Instruction: finish that answer and report completion to Aporia.

Do not auto-promote TECHNE-122.

Cyclops

PARKED after its bounded observability audit.

Instruction: send the required heartbeat/status to Aporia if the instance is live, then remain parked.

Do not recreate a coordination layer.

Theseus

Created, but charter remains pending and no READY work exists.

Instruction: report HOLD / NO CHARTER and runtime status to Aporia.

Do not invent a charter or self-assign work.

Aporia

Finish the current coordination/census work.

Suspend the previously queued creation of new Builder lanes unless such a Builder was already actually running before this CWO.

Primary product of this round:

a trustworthy fleet census plus completion/blocker routing.

⸻

9. ARCHAEOLOGY / MISSING STATE

The repository review did not find roles/Archaeon/WORK_STATE.json on main.

This CWO does not infer Archaeon’s state from that absence.

If Archaeon is live, Aporia shall obtain its heartbeat directly through comms or A2A and include it in the census.

The same rule applies to any other live agent lacking structured state.

Presence is established by live evidence, not by assumptions from repository layout.

⸻

10. HARD GATES REMAIN HARD

Nothing in this CWO authorizes:

* Cosmos D2 consumption;
* Ensorain LM01 launch;
* privileged promexec broker installation;
* privileged D2 host/account changes;
* paid compute outside existing authority;
* breaking preregistration;
* changing frozen decision rules;
* crossing blind/custody boundaries;
* resurrecting parked experiments;
* interpreting a failure as permission to redesign after exposure.

A blocker created by one of these gates should be reported to Aporia.

It should not be worked around by changing scientific questions.

⸻

11. COMPLETION MESSAGE

When an agent completes its IN-FLIGHT SET, send Aporia:

SEAT
ITEM COMPLETED
VERDICT / DISPOSITION
RECEIPT / COMMIT / REPORT
WORKERS / LEASES CLOSED
OPEN DEFECTS
STATE: READY
NEXT: awaiting Aporia — no self-promotion

Aporia should acknowledge the closure and update the fleet census.

Until reassigned, the seat may perform housekeeping intrinsic to the completed work—receipt verification, branch hygiene, lease release, state reconciliation—but should not begin a new scientific item.

⸻

12. SUCCESS CONDITION

This CWO is complete when Aporia can produce a trustworthy snapshot showing:

every live agent;
its uptime;
its exact model version;
what it was working on;
whether that work finished;
what remains blocked;
who owns each blocker;
which seats are READY for their next assignment.

The purpose of this round is not maximum concurrency.

The purpose is to collapse the number of half-finished fronts.

Finish what is already in motion.

Make blockers visible.

Then decide what deserves to move next.

⸻

13. IMMEDIATE EXECUTION

Aporia shall:

1. Commit this CWO verbatim.

2. Broadcast it to all live seats through comms, with A2A Fabric as an alternate delivery path.

3. Discover the actual live fleet rather than relying only on QUEUE.json.

4. Collect the mandatory uptime/model/current-work heartbeat from every live seat.

5. Freeze automatic NEXT/RESERVE promotion.

6. Route blockers while preserving each seat’s current objective.

7. Maintain the consolidated fleet census until the in-flight set has substantially closed.
