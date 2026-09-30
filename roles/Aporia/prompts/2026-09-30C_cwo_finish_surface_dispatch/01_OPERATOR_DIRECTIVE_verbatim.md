APORIA CWO-2026-09-30C

FINISH, SURFACE, DISPATCH

Date: 2026-09-30
Authority: Operator
Executor: Aporia
Governing context: MWO-0004, CWO-2026-09-30B, subsequent direct operator directives
Applies to: all live Prometheus scientific seats, engineering seats, auditors, Builders, worker-principals, and newly dispatched bounded workers.

This CWO supersedes conflicting fleet-operating instructions in prior CWOs.

Scientific preregistration, custody, blind holdouts, resource caps, privilege restrictions, frozen decision rules, and direct operator instructions remain authoritative.

⸻

0. MISSION

Prometheus is moving from fleet activation into a steadier operating regime.

The objective is:

finish existing work cleanly, keep it visible while it happens, escalate blockers quickly, and put READY capacity back to useful bounded work without allowing uncontrolled self-promotion.

The operating cycle is:

SYNC → WORK → CHECKPOINT → PUSH → FINISH → REPORT → READY → APORIA DISPATCH

Agents do not choose the final arrow for themselves.

Aporia does.

⸻

1. THREE SEAT STATES GOVERN THIS ROUND

1.1 WORKING

A WORKING seat finishes the objective already in hand.

Do not pivot because another question looks attractive.

Do not automatically start NEXT.

Do not expand the scope merely because the current experiment produces an interesting residual.

Finish the in-flight objective according to its existing authority.

⸻

1.2 BLOCKED

A BLOCKED seat retains its current objective.

It reports the blocker to Aporia and performs only safe work that directly supports completion or unblocking of that same objective.

A blocked seat does not silently switch research questions.

⸻

1.3 READY

A READY seat has completed its authorized in-flight work.

READY does not mean self-select another item.

READY means:

available for Aporia dispatch.

Aporia may assign bounded new work to a READY seat under Section 7 without waiting for another fleet-wide CWO.

⸻

2. FINISH-IN-PLACE RULE

Every WORKING seat shall identify its IN-FLIGHT SET.

The IN-FLIGHT SET includes work genuinely underway under valid authority:

* experiments already running;
* implementation already underway;
* analysis in progress;
* preregistered work whose execution has begun;
* submitted Fabric tasks;
* accepted reviews or adjudications;
* direct operator instructions already adopted;
* repairs directly necessary to close the above;
* active child workers supporting the same objective.

Finish those items.

Do not use this CWO to restart or redesign them.

Do not abandon healthy in-flight work merely because Aporia now has dispatch authority over READY seats.

⸻

3. DIRECT OPERATOR INSTRUCTIONS REMAIN IN FORCE

A direct operator instruction already given to a seat outranks ordinary fleet scheduling.

If work under that instruction is underway, it remains part of the seat’s IN-FLIGHT SET.

This includes, where presently applicable, directly ordered work such as:

* Cosmos C4;
* Tyche v2;
* Ensorain’s current reordered line;
* any other operator-directed work adopted before or after this CWO.

Aporia coordinates around such work.

It does not reinterpret it.

⸻

4. NO SELF-PROMOTION

Seats shall not automatically execute NEXT or RESERVE.

When CURRENT finishes:

1. write the result or closure receipt;
2. update structured state;
3. commit;
4. push;
5. release resources that should terminate;
6. notify Aporia;
7. enter READY.

NEXT and RESERVE may remain visible as planning information.

They are not self-executing.

The same applies when an experiment fails, parks, or is killed by its ruler.

A failure does not grant authority to design the rescue experiment.

⸻

5. BLOCKER ESCALATION

When CURRENT cannot progress because of an external dependency, notify Aporia promptly.

5.1 Current routing order

Because the Fabric CLI is presently broken on Windows principals, blocker reporting shall use:

1. comms — primary

2. pushed Git state / receipt — durable fallback

3. A2A Fabric — when verified functioning from that host

Do not assume A2A is healthy merely because Linux workers remain healthy.

After Odysseus repairs and verifies the Windows path, Aporia may restore comms and A2A to equivalent operational channels.

⸻

5.2 Blocker message

Report:

SEAT
CURRENT OBJECTIVE
CURRENT STEP
BLOCKED SINCE
BLOCKER
DEPENDENCY OWNER, IF KNOWN
EXACT ACTION NEEDED
SAFE SAME-OBJECTIVE WORK REMAINING
ACTIVE COMPUTE / WORKERS / LEASES
LAST PUSHED SHA / RECEIPT

Aporia owns routing.

⸻

6. CONTROL-PLANE DEFECTS GET IMMEDIATE OWNERSHIP

Aporia may immediately assign engineering repair work for defects that impair:

* fleet communication;
* A2A/Fabric execution;
* custody;
* experiment submission;
* observability;
* liveness detection;
* resource enforcement;
* reliable state propagation.

Such assignments are completion-support work, not scientific pivots.

They do not require a new fleet-wide scientific work order.

6.1 Immediate known defects

FABRIC WINDOWS CLI REGRESSION

Odysseus owns the defect reported in #1135:

the hung-connection hardening introduced a Windows failure at connect due to os.dup on a socket handle.

Effect:

M1, M2 and desktop principals cannot reliably submit/read Fabric tasks through the CLI.

Linux workers remain unaffected.

Priority: P0 operational repair.

Repair, test on Windows, test Linux non-regression, commit, push, and notify Aporia.

Do not bundle unrelated Fabric redesign into the repair.

⸻

SHARED CONNECTION-HANG RISK

The same connection setup may affect:

* comms;
* evidence_wiki.

Their usual owner is parked.

Aporia shall assign a bounded owner to determine whether the same failure mode is present and, if so, repair it.

The purpose is to avoid a common-mode failure where execution and coordination degrade simultaneously.

⸻

7. READY-SEAT DISPATCH AUTHORITY

The fleet now has meaningful READY capacity.

Aporia may dispatch READY seats without waiting for another CWO when all of the following are true:

1. the seat has cleanly closed its previous IN-FLIGHT SET;
2. the new item fits the seat’s existing charter or established capability;
3. it is bounded;
4. it does not consume a sealed holdout;
5. it does not break or reinterpret a frozen preregistration;
6. it does not require unauthorized privileged host modification;
7. it fits existing compute/spend authority;
8. it is not a major new campaign requiring operator authority;
9. it is selected from an operator-approved backlog, active dependency, existing research frontier, or explicitly requested cross-seat support task.

Aporia may prepare assignments before a seat becomes READY.

Execution begins only after the seat is READY and the assignment is issued.

⸻

8. WHAT APORIA MAY DISPATCH

Good READY-seat assignments include:

* bounded falsification of an existing active claim;
* an already-defined review;
* independent replication;
* implementation needed by an active experiment;
* a specific instrumentation repair;
* a backlog item already authorized in the seat charter;
* a bounded Builder task;
* a cross-seat dependency that will soon block another seat;
* residual analysis already inside the approved portfolio;
* evidence cleanup required to make a claim usable.

Aporia should prefer work that:

* closes an active dependency;
* improves evidence quality;
* removes a known bottleneck;
* tests a live scientific claim;
* or increases the quality of the next experiment.

⸻

9. WHAT APORIA MAY NOT DISPATCH WITHOUT OPERATOR AUTHORITY

Aporia shall escalate rather than independently authorize:

* use of a sealed holdout;
* a major new scientific campaign;
* a new seat charter;
* relaxation of a scientific validity gate;
* changes to frozen decision rules;
* privileged host/security modifications;
* resource/spend above existing authority;
* irreversible custody changes;
* resurrection of a parked campaign;
* a scientific pivot outside the seat’s established charter;
* anything explicitly held for operator decision.

⸻

10. PERIODIC COMMIT AND PUSH DISCIPLINE

GitHub must show the fleet’s trajectory while work is happening.

Do not leave important work trapped only inside an agent context window.

10.1 Visibility interval

If a seat has accumulated meaningful repository changes, it should not normally go more than approximately 60 minutes without a coherent commit and push.

This is a maximum invisible-work interval.

It is not a quota for meaningless commits.

If nothing repository-worthy has changed because a long computation is running, do not make empty commits.

Commit the launch/seal before the run.

Commit the next meaningful state when one exists.

⸻

10.2 Event-triggered checkpoints

Commit and push at the nearest safe boundary after:

* preregistration freeze;
* experiment seal;
* significant run/batch launch;
* material implementation milestone;
* blocker discovery;
* defect discovery;
* important partial result;
* state transition;
* deviation;
* erratum/correction;
* analysis/verdict;
* experiment closure;
* transition to READY.

WIP commits are acceptable.

Truthful incompleteness is preferable to invisible work.

⸻

10.3 Recommended commit semantics

Use clear prefixes where useful:

WIP:
PREREG:
SEAL:
RUNNING:
BLOCKED:
DEFECT:
RESULT:
CORRECTION:
READY:

Do not label partial work as complete.

⸻

10.4 Push branches, not noise

Agents should regularly push their working branches.

Incomplete work does not need to merge to main merely for visibility.

Do not force-push shared history.

Do not commit giant transient outputs, caches, or meaningless heartbeat files.

For large artifacts, commit:

* receipt;
* hashes;
* IDs;
* artifact location;
* summary;
* provenance needed to recover the result.

⸻

11. SYNC BEFORE LAUNCHING THE NEXT CONTROL STEP

Artemis demonstrated a real failure mode: it continued self-promoting for roughly 2 hours 15 minutes because it had not reread the control plane.

Therefore, before any:

* experiment launch;
* new Fabric batch;
* major experimental phase;
* new preregistered block;
* child-worker creation;
* paid-compute launch;
* self-proposed promotion;
* gate crossing;

the principal shall:

sync comms;
fetch current Git state;
check the current CWO/operator directives.

If the path uses A2A and A2A is working, sync that too.

This is not a new approval gate.

It is a stale-authority check.

If nothing changed, proceed.

⸻

12. PERIODIC CONTROL-PLANE SYNC

A principal active for a long session should check for new control messages at least every 60 minutes, unless doing so would contaminate a blind experimental condition.

A long-running compute job does not need to stop.

The principal simply checks at a safe boundary.

No seat should go multiple hours launching new work under an instruction set it has not refreshed.

⸻

13. HEARTBEAT REQUIREMENT

Every live principal shall report operational status:

* when adopting this CWO;
* on launch of significant work;
* on state transition;
* on blocker discovery;
* on completion;
* and at least once every 90 minutes while actively working, when operationally practical.

A missed heartbeat does not invalidate science.

It does affect fleet visibility.

Aporia marks the seat:

VISIBILITY_STALE

after one missed interval.

After two consecutive missed intervals, Aporia shall directly reconcile the seat’s state before that seat launches a new phase.

⸻

14. HEARTBEAT CONTENT

Each heartbeat should include:

SEAT
HOST / INSTANCE
SESSION START / UPTIME
MODEL — exact runtime-reported string
BRANCH / HEAD
STATE
CURRENT OBJECTIVE
CURRENT STEP
IN-FLIGHT WORKERS / JOBS
PROGRESS
BLOCKERS
RESOURCE STATE
LAST PUSHED SHA
LAST PUSH TIME
FINISH CONDITION
NEXT EXPECTED MILESTONE
EXPECTED NEXT ARTIFACT

If READY:

NEXT: awaiting Aporia assignment

Unknown fields must be UNKNOWN.

Do not infer model identity or uptime.

⸻

15. FORWARD-LOOKING WORK_STATE

A seat’s pushed state should permit an external reader to understand both present state and near-term direction.

Where practical, maintain:

state

current_objective

current_step

in_flight

progress

blocked

resource_status

finish_condition

next_expected_milestone

expected_next_artifact

last_receipt

last_push_sha

last_push_utc

model

session_started_utc or session_uptime

next = awaiting Aporia when READY

Forward-looking state is informational.

It is not authority to execute a future phase.

⸻

16. APORIA FORWARD VIEW

Aporia shall maintain a consolidated forward view of the fleet.

For every live seat:

STATE
CURRENT OBJECTIVE
CURRENT STEP
NEXT EXPECTED MILESTONE
EXPECTED ARTIFACT
KNOWN / LIKELY BLOCKER
DEPENDENCY OWNER
LAST PUSH
LAST HEARTBEAT

This view should allow Aporia to see a blocker before it becomes a stall.

Example:

if Cosmos will need a foreign-family artifact after review, Aporia can ensure that author is assigned before Cosmos reaches the dependency.

Proactive routing is encouraged.

Premature scientific execution is not.

⸻

17. READY POOL

At issuance, the fleet already contains substantial READY capacity.

Known READY or near-READY seats include:

* Nestor;
* Archaeon;
* Artemis;
* Ananke after its C4 review;
* Bellerophon after its C4 review;
* Theseus after its C4 author task;
* other seats as they finish.

Aporia should not leave READY capacity idle indefinitely when useful bounded authorized work exists.

Likewise, it should not invent busywork merely to fill every seat.

Dispatch for value, not utilization.

⸻

18. CURRENT C4 WORK

Aporia has already made bounded C4 assignments under existing operator authority:

Ananke — R-STAT reviewer

Bellerophon — R-MECH reviewer

Theseus — foreign world-family author

These assignments remain valid.

They are bounded support tasks, not uncontrolled scientific pivots.

When complete, those seats return to READY unless Aporia issues another authorized assignment.

⸻

19. CURRENT BLOCKED / HOLD STATES

Hecate

BLOCKED on free-tier quota for Families B/C, with Harmonia audit verification attached.

Stay on the current objective.

Report progress when quota resets or verification closes.

Optional paid acceleration remains an operator choice.

⸻

Odysseus

BLOCKED on privileged promexec broker installation for that portion of the line.

Separately owns the Windows Fabric CLI P0 defect and may continue that repair without privileged installation if technically possible.

The privileged broker install still requires operator action.

⸻

Harmonia

HOLD / dependency wait on active adjudication inputs.

It should finish routed adjudications and not invent audit samples merely to remain occupied.

⸻

Cyclops

PARKED.

If live, heartbeat and remain parked unless Aporia dispatches a bounded task.

⸻

20. UNOWNED FINDINGS LEDGER

Aporia shall maintain a lightweight ledger of useful findings that currently lack an active owner.

Do not allow them to disappear because the originating seat is parked or READY.

Known examples include:

* Gemini queue with approximately 370 prompts that never ran;
* IQ-NULL/G1 result near its decision boundary;
* D8 “history beyond diversity” NOT SHOWN;
* FR-091 waiting on a parked seat;
* shared DB hang risk affecting comms/evidence_wiki.

For each:

finding
source
why it matters
owner
state: unowned / assigned / parked / closed

Aporia may dispatch bounded investigation of such items to a READY seat if it falls within existing authority.

⸻

21. QUEUE OF RECORD MUST BE CONSISTENT

Aporia shall repair ops/fleet/QUEUE.json.

Any surviving rule that says:

CURRENT finishes → promote NEXT automatically

must be removed or marked superseded.

The authoritative state transition is now:

CURRENT → FINISH → REPORT → READY → APORIA DISPATCH

NEXT and RESERVE are planning fields only.

⸻

22. VISIBILITY FAILURE CLASSIFICATION

Aporia should distinguish:

HEALTHY

Recent heartbeat and pushed progress, or a known live long-running job with a committed launch receipt.

VISIBILITY_STALE

The seat appears alive or active but has missed expected heartbeat/push visibility.

Ping it.

OPERATIONALLY STALE

No meaningful Git activity, comms activity, A2A evidence, worker evidence, or heartbeat consistent with claimed state.

Reconcile directly.

Do not equate process existence with productive work.

Do not equate lack of Git commits during a known sealed long run with failure.

⸻

23. OPERATOR ESCALATIONS CURRENTLY KNOWN

Aporia should surface genuine operator actions distinctly from normal scheduling.

Current known examples:

E-003 BEE verdict of record

Operator ruling required on the final verdict language.

Do not allow this wording issue to block unrelated work.

promexec broker installation

Privileged administrative action required.

Hecate paid acceleration

Optional, not required for scientific validity.

Aporia should not repeatedly re-escalate optional items as urgent blockers.

⸻

24. COMPLETION PROTOCOL

When a seat completes its assigned work:

1. result/receipt written;
2. state updated;
3. commit created;
4. push completed;
5. resources released as appropriate;
6. Aporia notified;
7. seat becomes READY.

Completion message:

SEAT
COMPLETED ITEM
VERDICT / DISPOSITION
FINAL SHA
REPORT / RECEIPT
RESOURCES RELEASED
OPEN DEFECTS
STATE: READY

Aporia may then dispatch another bounded authorized item.

⸻

25. APORIA REPORT TO OPERATOR

Operator-facing status should be short and forward-looking.

For each meaningful live seat:

Seat — state — current objective — next milestone — blocker — last push age

Then separately:

READY POOL

Seats available for assignment.

APPROACHING DEPENDENCIES

Things likely to block active science soon.

OPERATOR ACTIONS

Only actual decisions or privileged actions.

VISIBILITY_STALE

Seats that owe state.

CONTROL-PLANE DEFECTS

Fabric, comms, custody, observability or execution problems with owners.

The operator should not need to inspect every seat to discover these.

⸻

26. SUCCESS CONDITION

This CWO succeeds when Prometheus reaches a stable rhythm where:

* WORKING agents finish rather than pivot;
* BLOCKED agents escalate instead of changing science;
* READY agents receive useful bounded work from Aporia;
* no seat self-promotes;
* important progress is periodically committed and pushed;
* agents refresh control instructions before launching new phases;
* heartbeats keep model, uptime, work and blockers visible;
* infrastructure defects have owners;
* unowned findings do not vanish;
* Aporia can anticipate dependencies rather than discovering them after a stall;
* GitHub shows not only what happened, but where each active line is going next.

The desired rhythm is:

SYNC
→ WORK
→ CHECKPOINT
→ PUSH
→ WORK
→ FINISH
→ PUSH
→ REPORT
→ READY
→ APORIA DISPATCH

⸻

27. IMMEDIATE APORIA ACTIONS

Upon adoption:

1. Commit and push this CWO verbatim.
2. Broadcast it to every live principal through comms.
3. Make it available through A2A where A2A is verified working.
4. Repair the contradictory auto-promotion language in ops/fleet/QUEUE.json.
5. Refresh the fleet census.
6. Mark seats missing required heartbeats as VISIBILITY_STALE and ping them:
    * Aether;
    * Nyx;
    * Techne;
    * Tyche;
    * Ensorain;
    * Cyclops;
    * any additional live seat lacking current telemetry.
7. Keep current WORKING seats on their present objectives.
8. Preserve current C4 assignments.
9. Keep READY seats READY until dispatched.
10. Prepare bounded assignments for the READY pool from the approved backlog and active dependency graph.
11. Give Odysseus P0 ownership of the Windows Fabric CLI regression.
12. Assign an owner to test the shared connection-hang risk in comms and evidence_wiki.
13. Create or update the unowned-findings ledger.
14. Begin recording each active seat’s:

* last pushed SHA;
* last heartbeat;
* next expected milestone;
* expected next artifact;
* likely dependency.

15. Route impending blockers before they become stalls.

Finish the work already in motion. Keep it visible. Dispatch READY capacity deliberately. Do not let either science or infrastructure disappear into opaque agent sessions.
