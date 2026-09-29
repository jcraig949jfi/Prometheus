PROMETHEUS MASTER WORK ORDER — MWO-0001

Date: 2026-09-28 America/New_York
Purpose: Fleet-wide coordination cutover: one operator-approved Master Work Order, GitHub-centered state, common Thread/Campaign/Experiment/Task/Attempt semantics, comms notification, and Fabric/A2A execution.

Review snapshot: jcraig949jfi/Prometheus main 6f0367ed7e0336b9fad3c47f102761cf74c83956, plus material live branch state current at issuance, including:

* nestor/s1-forensics-2026-09-23 at 81895e7290
* archaeon/attribution-arc-2026-09-28 at efd7295a07
* aphrodite/arc3-2026-09-28 at 889bf8dddf
* artemis/selftest-2026-09-28 at 9ce6d8de45

This order becomes authoritative only after operator approval and Cyclops commits and pushes it.

⸻

1. CONTROL MODEL

Effective with this order, Prometheus uses one central coordination loop:

Seats → GitHub evidence/state → ChatGPT synthesis → operator approval/refinement → Cyclops publication → all seats.

The operator and ChatGPT are the program-level coordination layer.

Cyclops is the registrar and distributor of an already-approved order. Cyclops is not a strategic steward, science adjudicator, scheduler, or intermediary approval authority.

Aporia and any former steward seats remain advisory unless an individual work order explicitly assigns work to them.

No seat should require a bespoke operator prompt for routine continuation inside an approved autonomy envelope.

⸻

2. CANONICAL WORK-ORDER LOCATION

Cyclops shall create and maintain:

ops/work_orders/CURRENT.md

and an immutable archive:

ops/work_orders/archive/MWO-0001_2026-09-28.md

For every future MWO:

1. Commit the operator-approved work order verbatim.
2. Put identical order content in CURRENT.md and the immutable archive copy.
3. Record the work-order SHA-256 and Git commit SHA.
4. Push to origin/main.
5. Broadcast one comms message to all seats containing:
    * MWO ID
    * Git commit SHA
    * archive path
    * SHA-256
    * a one-line instruction to fetch and adopt it.
6. Do not rewrite, summarize, expand, reinterpret, or reprioritize the approved order.
7. Do not require individual comms ACK messages. Adoption is recorded in Git by each seat’s WORK_STATE.

Only Cyclops writes the canonical ops/work_orders/ files unless a later MWO explicitly changes custody.

⸻

3. WHAT IS AUTHORITATIVE

There are three planes.

GitHub — durable control and evidence plane

GitHub is authoritative for:

* Master Work Orders
* seat charters and policies
* Threads
* Campaigns
* Experiments and frozen preregistrations
* scientific reports and claims
* review packets
* manifests and hashes
* durable seat work state
* code and shared libraries

A seat does not need to merge main merely to read a new MWO. Fetch and inspect origin/main:ops/work_orders/CURRENT.md. Merge/rebase only when the actual work requires the new code.

Fabric — live execution plane

Fabric v0.2 is authoritative for:

* Tasks
* Attempts
* resource leases
* live worker capability state
* Task/Attempt messages
* execution artifacts
* retry/reap/cancellation state

The canonical Fabric lease row is the only lease authority for new substantial work.

Fabric v0.2 is FROZEN at tag fabric-v0.2 / commit 54e42c695.

During this adoption experiment, no dashboard, scheduler, streaming, push notification, priority optimizer, Thread→Task bridge, or other new Fabric feature is to be built.

Only science- or safety-blocking defects may be repaired, under the existing FREEZE rules.

Comms — notification plane

Comms is for:

* MWO publication notices
* short seat-to-seat notifications
* blocker notices
* custody/release notifications
* incident escalation
* pointers to Git/Fabric results

Comms is not the durable scientific record and is not a separate approval system.

A comms message may point to an authorization. It may not silently modify the MWO.

⸻

4. COMMON WORK MODEL

All seats shall use these meanings prospectively. Existing history is not renamed or rewritten; add aliases/links where necessary.

Thread

A Thread is an enduring scientific or methodological question.

Canonical identifier: thr-*, with human alias such as TH-013.

A Thread may survive multiple campaigns.

A Thread is not a task queue.

Campaign

A Campaign is a bounded coordinated program pursuing one or more Threads under a declared resource/time/scientific envelope.

Canonical human identifier: C-* where applicable.

A Campaign contains Experiments.

Campaign closure does not necessarily close its Thread.

Experiment

An Experiment is a specific discriminating test or preregistered scientific unit inside a Campaign.

Canonical human identifier: E-* where applicable.

An Experiment owns its frozen hypotheses, arms, controls, endpoints, decision rule, and interpretation boundaries.

Changing those after exposure remains a scientific amendment and is not routine task management.

Task

A Task is a portable unit of requested work.

Canonical Fabric identifier: tsk-*.

Examples:

* run one frozen condition
* independently review a claim
* reproduce a result
* inspect a code boundary
* execute a bounded analysis
* package an evidence bundle

A scientific Task should identify its Thread, Campaign, and Experiment whenever those exist.

A Task shall pin its base SHA and required capabilities/resources.

Tasks describe what is required, not which machine should run them, except where custody, host-local evidence, or a real environmental constraint requires affinity.

Attempt

An Attempt is one execution of one Task.

Canonical Fabric identifier: att-*.

Attempts are disposable execution events. Failure of an Attempt does not rewrite the Experiment.

The evidence path is:

Attempt → Task → Experiment → Campaign → Thread.

Do not collapse these levels in reports.

⸻

5. A2A POLICY

The existing Fabric A2A v1.0 JSON-RPC gateway is the Prometheus A2A execution interface for this trial.

Do not build another A2A service.

Do not give every seat its own network daemon.

Do not open a new inbound port merely so two seats can communicate.

Seat-to-seat work that requires execution should normally become a Fabric Task. A2A and the Fabric CLI are alternate interfaces to the same execution state.

Seat principals remain seats.

Workers remain generic node executors such as:

worker.ubu001
worker.ubu001.sci
worker.ubu002

Do not name Fabric workers after seats.

Use multiple fresh Fabric replicas where independence is required rather than choosing a familiar reviewer manually.

A2A is not the seat mailbox. Comms remains the low-latency seat notification channel.

⸻

6. HOST / PACKAGE / PORT POLICY

Scientific seats shall not independently:

* create system users
* edit sudoers
* change host firewall policy
* open externally reachable listening ports
* install machine-wide packages
* create persistent privileged services
* alter another seat’s runtime environment

Shared code and libraries should preferentially come from the canonical Git repository at pinned revisions and execute in isolated environments.

If a missing capability requires host mutation, record a capability/blocker request. Do not improvise local administration.

promexec remains:

EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC WORKERS.

Nothing in this MWO authorizes its use.

⸻

7. OPERATOR GATES THAT REMAIN HARD

Seats may continue autonomously through ordinary implementation, execution, replay, packaging, repair, retry, and review steps already inside their approved envelope.

Stop for operator-level authority when an action would:

1. change a frozen hypothesis, primary endpoint, acceptance threshold, or experiment meaning after exposure;
2. reveal or consume a sealed holdout, blindness key, withheld prediction, or custody-protected information;
3. launch a campaign that has an explicit operator launch gate;
4. materially exceed an approved money/compute/resource envelope;
5. perform privileged host changes or external side effects;
6. redefine program-level priorities or assign unrelated work across seats.

A prior instruction requiring “operator direct chat” is prospectively satisfied by an operator-approved MWO containing the same exact authorization and frozen identifier/hash, unless a scientific/custody contract explicitly requires a different mechanism.

This MWO does not itself open any such gated campaign unless stated below.

⸻

8. STANDARD SEAT LOOP

Every live seat shall adopt this loop.

At boot, after a material terminal transition, after becoming blocked, and while idle at its existing work cadence:

1. git fetch origin.
2. Read origin/main:ops/work_orders/CURRENT.md.
3. Compare its MWO ID with the seat’s recorded MWO.
4. Read the section addressed to the seat.
5. Check comms since the seat’s last cursor.
6. Check relevant Fabric Task/message state.
7. Execute all eligible work inside the current MWO and existing scientific contracts.
8. If one item blocks, perform other eligible work rather than waiting unnecessarily.
9. Update durable work state after material transitions.
10. Repeat.

Do not create a new polling daemon merely to implement this rule.

Do not repeatedly broadcast idle heartbeats.

If no work is eligible, record HOLD and remain available.

Do not invent a new program-level campaign simply to stay busy.

⸻

9. STANDARD WORK STATE

Every active seat shall create or update:

roles/<Seat>/WORK_STATE.json

This is a small mutable coordination pointer, not a scientific evidence file.

Schema v1:

{
  "schema": "prometheus.work_state.v1",
  "seat": "<Seat>",
  "mwo_id": "MWO-0001",
  "mwo_commit": "<Cyclops publication commit>",
  "updated_at_utc": "<ISO-8601>",
  "state": "ACTIVE|WORKING|BLOCKED|HOLD|PARKED",
  "branch": "<current branch>",
  "head_sha": "<pushed head>",
  "threads": [],
  "campaigns": [],
  "experiments": [],
  "fabric_tasks": [],
  "running": [],
  "blocked_on": [],
  "next_actions": [],
  "operator_decisions_required": [],
  "latest_reports": []
}

Keep it short.

Do not copy entire reports into it.

A seat’s latest Git push plus this file should be sufficient for central coordination to determine its actual state.

Update it whenever:

* an Experiment starts or closes;
* a major Task starts or closes;
* a hard blocker appears or clears;
* a campaign becomes launchable or terminal;
* operator intervention becomes necessary;
* the seat adopts a new MWO.

This replaces reliance on stale prose STATUS files for fleet-level coordination. Existing STATUS files remain useful as narrative records.

⸻

10. CURRENT FLEET INSTRUCTIONS

CYCLOPS — MASTER ORDER REGISTRAR

Unpark only for the narrow role defined in this MWO.

Do now:

* commit this approved MWO verbatim to the two canonical paths;
* push to origin/main;
* calculate and record SHA-256;
* send the one fleet-wide comms broadcast;
* create roles/Cyclops/WORK_STATE.json.

After publication, return to registrar/HOLD.

Cyclops shall not:

* rewrite seat instructions;
* create scientific priorities;
* adjudicate results;
* demand seat sign-off;
* become a scheduler;
* revive the former M2 stewardship role;
* modify another seat’s section.

When a future approved MWO is pasted to Cyclops, repeat the publication procedure.

⸻

ODYSSEUS — FABRIC PRINCIPAL / ADOPTION OBSERVER

Fabric v0.2 is now infrastructure, not a continuing feature project.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* keep the frozen v0.2 node workers operating under existing constraints;
* record defects encountered by real MWO work as adoption-experiment evidence;
* assist seats in expressing real execution work as Tasks using existing capabilities;
* preserve the canonical lease cutover;
* adjudicate the existing D2 Fabric re-audit when it returns;
* continue the frozen S3 adoption experiment only under v0.2 and without promexec.

Artemis is now eligible to act as S3 principal because its blinded self-test and unsealing completed.

Do not add a Thread→Task bridge yet.

Do not add Fabric features.

Do not enable promexec.

⸻

ARTEMIS — BOUNDED EXECUTION / ROUTING

Today’s self-test found that sharpening and priority forecasting did not establish added yield. Preserve that result.

MWO-0001 authorizes standing bounded dispatch of raw eligible work to fresh Fabric workers, subject to:

* no priority/rank claims;
* no rewriting the scientific question;
* no crossing blindness/custody gates;
* no new campaign launch without authorization;
* use independent fresh Attempts/replicas when independence matters.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* act as the S3 Fabric adoption principal when Odysseus is ready;
* continue bounded routing/execution under the no-ranking method;
* preserve the scheduled day-30 self-test follow-up;
* answer Nestor follow-up on CVT-R when requested through the normal work model.

⸻

NESTOR — ANCESTRY / HEREDITY

Latest pushed state includes ancestry production run 2 at 81895e7290.

Run 1 was correctly invalidated after the duplicate_of bookkeeping defect. Run 2 reports births byte-identical across the 11/11 comparison and content-identical 1% sample apart from gzip mtime representation.

No third production run is authorized.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* finish packaging run 2 and its provenance;
* submit the completed production result for independent fresh review through Fabric, preferably two independent repo-readonly replicas pinned to the review SHA;
* reconcile the CVT-R result explicitly: 19 P-11-certified genomes failed CVT-R, including 11 generation-2 cases;
* ensure future statements distinguish construction/dependence certification from actual hereditary transmission;
* perform the assigned D2 firewall re-audit if it remains open in Fabric/comms;
* use the canonical Fabric lease row for all future substantial resource claims.

Do not broaden the ancestry claim before the independent review returns.

⸻

ARCHAEON — ATTRIBUTION / FRONTIER

Latest branch state is archaeon/attribution-arc-2026-09-28 at efd7295a07.

Today’s attribution work substantially changed several earlier readings and produced the independent NPE/reference comparison machinery. Preserve the corrections and retractions.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* complete the pre-read 1% NPE sample verification against its pinned manifest before reading sample content;
* publish the verification result and linkage to Nestor’s production run 2;
* preserve the current frozen/reference semantics; no post-result semantic repair without explicit amendment;
* link current attribution work to the existing Thread/Campaign/Experiment hierarchy rather than creating another parallel naming layer;
* use Fabric leases for future substantial work;
* keep old branch-local lease helpers from governing new work.

Do not start a new large Archaeon campaign under this cutover order.

⸻

APHRODITE — ARC3

Latest pushed ARC3 branch is aphrodite/arc3-2026-09-28 at 889bf8dddf.

ARC3 has closed its current W8 block. The record includes:

* recurrent G1 stepping-stone behaviour under the constructed recurrence test;
* LIN recurrence observed repeatedly but failing the W1 criteria;
* recurrence × visibility distinction;
* G1 not established as privileged.

Do now:

* adopt MWO-0001 and create WORK_STATE from the branch’s actual current state;
* preserve the ARC3 close and prepare a concise merge/review packet;
* map ARC3’s active questions into Thread/Campaign/Experiment identifiers;
* do not extend ARC3 into another major wave until a future MWO reviews the close.

Existing news monitoring may continue only under its already-authorized narrow scope; it is not a source of new campaign authorization.

⸻

ENSORAIN — WTP / PHYSICS-OF-INTELLIGENCE FOUNDRY

WTP-LM01 prereg v0.3.2 remains frozen at:

ee8cbe0c8cb1ef131e6bc8181c8272656eaa5a6e

It remains NOT LAUNCHED.

This MWO does not contain the launch phrase and therefore does not launch LM01.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* map LM01 queue item Q1 and related ARC3 work into Thread/Campaign/Experiment form;
* use Fabric for bounded independent review/execution where appropriate;
* preserve frozen LM01 seeds, rules, arms and gate;
* remain ready for a future MWO to contain the exact launch authorization and frozen hash.

Do not launch LM01 from comms alone.

Do not resume steward-gated management.

⸻

COSMOS — C3 / HOLDOUT D2

D2’s first firewall audit failed. D2 v2 repairs were committed afterward.

The holdout sequence remains:

seal → independent firewall audit → Cosmos commitment → designation → result seal / authorized reveal.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* remain blind to D2;
* wait for the independent D2 re-audit result;
* prepare only public-side C3 work that cannot expose D2 information;
* use Fabric for bounded public-side execution/review where useful.

Do not spend, reveal, designate, or inspect D2 until the existing custody protocol and a later operator authorization permit it.

⸻

HARMONIA — RULER / CUSTODY REVIEW

Do now:

* adopt MWO-0001 and create WORK_STATE;
* preserve the D2 custody/order guarantees already committed;
* receive and record the independent D2 audit evidence when it lands;
* perform ruler/review work when assigned through the MWO/Fabric model.

Harmonia is a reviewer/ruler, not a fleet coordinator.

Do not release sealed material based solely on a comms message.

⸻

AETHER — INDEPENDENT REVIEW

Aether’s immediate assigned work is the read-only independent promexec review requested in comms #912.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* review the exact committed promexec state and installed-configuration snapshot read-only;
* report against the frozen acceptance surfaces;
* make no host changes as part of that review;
* leave promexec EXPERIMENTAL / UNVERIFIED unless the evidence actually satisfies the declared sequence.

After that review, return to the existing Aether research queue unless a newer MWO assigns work.

No new RunPod spend is authorized by this order.

⸻

ANANKE — PTE / LEASE ADOPTION

The Ananke lease frontend has been cut over on main to the canonical Fabric lease row.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* before the next substantial compute job, ensure the working branch contains the canonical lease cutover;
* use Fabric leases, not host-file lease authority;
* map future PTE experiments/tasks into the common hierarchy.

No new large PTE campaign is launched by this MWO.

⸻

BELLEROPHON — BEE

No material September-28 scientific push superseded the existing campaign state.

Do now:

* adopt MWO-0001 and create WORK_STATE;
* reconcile actual live process state, campaign branch state, unmerged reports, and any outstanding leases;
* record whether anything is genuinely running;
* map the next authorized BEE work into the common hierarchy;
* use Fabric for future bounded work and the canonical Fabric lease authority.

Do not start a new multi-day campaign merely because the seat is idle.

⸻

ATLAS AND ATLAS-M2

Remain parked unless specifically assigned index work.

Do not unpark merely to implement MWO infrastructure.

On next activation:

* adopt the common hierarchy;
* create/update WORK_STATE;
* treat WORK_STATE.json, Fabric Task/Attempt state, Threads, Campaigns and Experiments as distinct indexed entities;
* never infer inactivity from a stale STATUS file when a newer pushed branch or WORK_STATE exists.

No portfolio directive is authorized by this MWO.

⸻

VIVARIUM / DAEDALUS

If live, adopt MWO-0001 and create WORK_STATE.

Existing engine/service responsibilities remain unchanged.

Use Git for common code/contracts and Fabric for bounded portable execution.

Do not create new machine-wide infrastructure, ports, or package state merely to communicate with another seat.

Do not merge main solely to discover the current MWO.

⸻

NYX / TECHNE / THEOPHRASTUS / CRIUS

Adoption-only unless an existing authorized task is genuinely active.

On next live cycle:

* read MWO-0001;
* create WORK_STATE;
* map existing active work to Thread/Campaign/Experiment;
* use Fabric for portable Tasks;
* preserve existing blind lanes and scientific restrictions.

This MWO does not resurrect parked campaigns.

⸻

APORIA

Remain parked/advisory.

Create WORK_STATE only when the seat is next live.

Do not resume the former stewardship/control function.

⸻

ALL OTHER SEATS

No dormant or parked seat is automatically reactivated by MWO-0001.

When next activated, every seat must:

* read CURRENT.md first;
* create/update WORK_STATE;
* adopt the common hierarchy;
* use Git/comms/Fabric according to this order;
* preserve all existing scientific and custody restrictions;
* execute only current authorized work.

⸻

11. AUTONOMY RULE

Within an authorized Campaign/Experiment envelope, a seat should not stop for routine operator approval merely because:

* a run finished;
* a repair is needed that does not alter scientific meaning;
* a retry is required;
* an ordinary independent review is needed;
* a dependency cleared;
* another eligible Task exists;
* an artifact needs packaging;
* a reviewer needs to be dispatched.

Use the work model and Fabric.

Stop only at a real hard gate.

When blocked on one item, continue other eligible work.

⸻

12. INCIDENT / DEFECT RULE

A real infrastructure defect found during this adoption is evidence.

Do not hide it by manually working around it.

Record:

* what work exposed it;
* MWO / Thread / Campaign / Experiment / Task / Attempt identifiers;
* frozen/base SHA;
* expected behaviour;
* observed behaviour;
* whether science/safety is blocked.

Fabric fixes remain governed by fabric/FREEZE.md.

⸻

13. END CONDITION FOR MWO-0001

MWO-0001 remains current until superseded by a later operator-approved MWO.

For this first cycle, central coordination will review GitHub after the seats have had a chance to adopt it.

The next review should be able to answer from Git alone:

* Which seats adopted MWO-0001?
* What is each seat actually doing?
* Which Threads/Campaigns/Experiments are live?
* Which Fabric Tasks/Attempts are running or blocked?
* Which hard operator decisions remain?
* Which seats are idle?
* What dependencies have opened?
* What should MWO-0002 authorize, stop, merge, review, or launch?

No seat needs to send a bespoke report to the operator merely to make that review possible.

END MWO-0001
