Achilles — Extend the Prometheus Control Plane for Phase 2-B Background Science

You are Achilles.

This assignment is fleet/control-plane architecture and repository setup.

You are not participating in Phase 2-B science.

You are not participating in Phase 3 engineering.

You do not become the scheduler or scientific coordinator after this setup.

Implement the following on main, preserving the existing Git-native workgraph, A2A/Fabric, base-role conventions, and the Epic structure already established or currently being established.

The goal is to support:

1. permanent GLOBAL work;
2. high-priority Phase 3;
3. slow persistent Phase 2-B engine science;
4. opportunistic use of idle machines;
5. clean preemption when higher-priority work arrives;
6. operator-approved priority exceptions;
7. generic execution workers on machines without turning named scientific seats into generic workers.

⸻

1. Core operating model

Prometheus now has three distinct concepts:

Named seats

Examples:

* Nestor
* Archaeon
* Aether
* Aphrodite
* Cosmos
* Ensorain
* Palamedes
* Argus
* Cadmus

Named seats own:

* scientific or engineering judgment;
* charter interpretation;
* Campaign design;
* Experiment design;
* decomposition into Tasks;
* interpretation of results;
* escalation of epistemic questions.

Named seats do not consume generic execution tasks.

⸻

PrometheusWorkers

Create a generic worker identity/class named:

PrometheusWorker

Use the canonical spelling PrometheusWorker, not PromethiusWorker.

A PrometheusWorker:

* is not a Greek-named seat;
* does not own a scientific charter;
* does not interpret experimental meaning;
* does not invent experiments;
* does not alter claim semantics;
* does not select scientific priorities;
* does not join scientific discussions unless reporting execution facts.

Its purpose is:

Execute fully specified generic Tasks faithfully on available machine resources and return receipts.

There may be many PrometheusWorkers across the fleet.

They are execution capacity, not scientific identities.

⸻

2. Create generic-worker-role

Create a shared inherited role such as:

roles/generic-worker-role/

This role itself inherits base-role.

It should contain the common rules for disposable/generic execution workers.

Do not treat generic-worker-role as a seat.

Update role discovery/enumeration tests if necessary so shared *-role directories remain excluded from seat rosters.

⸻

3. PrometheusWorker inheritance

A PrometheusWorker inherits:

1. base-role
2. generic-worker-role

It does not inherit an engine charter or the RSO builder role.

Machine-specific PrometheusWorker instances may dynamically record:

* hostname;
* CPU availability;
* GPU availability;
* memory;
* storage;
* supported runtime/tooling;
* connectivity;
* current leases.

Do not create a separate permanent Greek role per machine.

The identity should conceptually be:

PrometheusWorker/<hostname>/<instance>

or the closest clean representation supported by current infrastructure.

Multiple ephemeral instances are acceptable if the existing system permits them.

⸻

4. Generic Task flag

Extend the workgraph Task schema with an explicit execution ownership field.

Conceptually:

generic: true | false

or a better equivalent such as:

executor_class:
  GENERIC_WORKER
  NAMED_SEAT

Prefer an explicit enum if it avoids ambiguity.

The invariant is:

Generic tasks

A Task marked for generic execution:

* can be claimed only by PrometheusWorker instances;
* cannot be claimed by named seats.

Named-seat tasks

Tasks requiring scientific/engineering interpretation:

* can be claimed only by an eligible named seat;
* cannot be claimed by PrometheusWorker merely because compute is idle.

Enforce this in workgraph validation/claim logic where feasible.

Do not rely only on prose.

⸻

5. What qualifies as generic work

A Task may be marked generic only when the packet is sufficient for execution without scientific judgment.

A generic packet should normally provide:

* exact source SHA;
* exact command/entry point;
* required environment;
* input artifact identities;
* seeds if relevant;
* runtime/resource requirements;
* timeout;
* output location;
* expected receipt shape;
* success/failure execution criteria;
* cleanup instructions;
* preemption/restart policy.

Examples:

* run an already registered experiment;
* replay a historical seed set;
* execute a test suite;
* run a deterministic analysis;
* run a known benchmark;
* package artifacts;
* collect machine-readable metrics;
* perform a registered parameter cell;
* rerun an experiment unchanged after resource preemption.

Not generic:

* decide whether a result is scientifically meaningful;
* change an experiment because results look odd;
* determine a new threshold;
* select a comparator;
* modify a registered scientific contract;
* design a new assay;
* interpret an anomaly;
* decide whether an old null should reopen.

If execution encounters ambiguity, PrometheusWorker stops and escalates.

⸻

6. Do not force experiments to fan out

This is a critical scientific constraint.

Add a general execution-mode field at Experiment or Task level.

Support at least:

ATOMIC

Default for scientific experiments.

One worker/machine runs the Experiment or execution Task intact.

No scheduler decomposition.

NATIVE_PARALLEL

The engine itself already supports safe native parallelism.

The scheduler allocates resources.

The scheduler does not redefine the scientific decomposition.

SHARDABLE

Only when the Experiment explicitly registers:

* independent shards;
* statistical/experimental unit;
* aggregation rule;
* restart semantics;
* artifact merge semantics.

The workgraph may distribute those shards.

Standing rule:

The scheduler may change placement, not experimental semantics.

And:

Workgraph decomposition stops at the smallest boundary that preserves the native semantics of the engine.

Never refactor an engine merely to increase fleet utilization.

⸻

7. Epic priority hierarchy

Add priority as an inherited workgraph property.

Base Epic priorities:

Epic	Priority
EP-PHASE3	HIGH
EP-GLOBAL	MEDIUM
EP-PHASE2B	LOW

Internally these may map to stable numeric bands, for example:

* HIGH = 300
* MEDIUM = 200
* LOW = 100

But local child urgency must not allow a lower Epic to escape its band.

Use a hierarchical priority model such as:

(epic_priority, local_priority, age)

A Phase 2-B Task with local urgency 1000 still remains below GLOBAL or Phase 3 unless an operator override exists.

⸻

8. Priority inheritance

Priority flows downward:

Epic
→ Thread
→ Campaign
→ Experiment
→ Task
→ Attempt

A child may lower its own urgency.

A child may not promote itself above its inherited Epic band.

An Experiment-level approved override propagates to its descendant Tasks/Attempts.

A Campaign-level override is possible but should be rarer.

A seat does not become higher priority merely because one of its Experiments is elevated.

⸻

9. Phase 2-B default preemption policy

Phase 2-B is LOW-priority, work-conserving background science.

Default Phase 2-B execution properties:

preemptible: true
restartable: true

However, the engine/Experiment packet determines the safe mechanism.

For ATOMIC experiments:

* prefer clean termination and later replay from the start;
* do not invent checkpointing merely to save compute.

For engines with a scientifically valid native checkpoint:

* checkpoint only at registered safe boundaries.

Do not resume from arbitrary undocumented process state.

A resource interruption produces:

PREEMPTED_RESOURCE

It is not:

* scientific FAIL;
* scientific NEGATIVE;
* engineering defect.

The same registered Experiment may be replayed later.

⸻

10. Phase 2-B 48-hour CWO cadence

Create/document a Phase 2-B operating cadence.

Every active, non-parked Phase 2-B engine/seat should receive a refreshed Phase 2-B CWO approximately every 48 hours.

This is not intended to create constant inference.

The CWO should be based primarily on the previous 48 hours of:

* Task receipts;
* Experiment receipts;
* bugs;
* repairs;
* preemptions;
* unfinished work;
* anomaly notifications;
* relevant forensic feedback;
* available resources.

A typical cycle:

Beginning

Seat reviews prior results and makes necessary epistemic decisions.

Middle

Execution proceeds, primarily deterministically and through generic workers where appropriate.

End

Results and receipts close.

New work should normally not begin if it cannot reasonably finish before the next CWO boundary.

Exceptions may be explicitly registered.

⸻

11. Phase 2-B inference economy

Document the intended model:

Model inference should occur primarily at epistemic forks.

Do not wake a high-capability engine seat merely to:

* watch jobs;
* poll progress;
* move files;
* rerun unchanged commands;
* summarize deterministic status.

Use machinery for those.

A seat should wake for matters such as:

* unexpected scientific result;
* ambiguous defect;
* comparator choice;
* redesign decision;
* interpretation;
* next Campaign selection.

The 48-hour CWO is a natural reasoning checkpoint.

⸻

12. CWO generation architecture

Structure the control plane so a future deterministic process can assemble most of the next CWO input from workgraph state.

Do not make the first implementation excessively elaborate.

The source inputs should be machine-readable enough to support future automatic synthesis:

* previous CWO ID;
* completed Tasks;
* Experiment status;
* preempted Tasks;
* defects;
* unresolved escalations;
* anomaly flags;
* resource use;
* priority requests;
* relevant cross-Epic notices.

Aporia remains the appropriate publication/coordination seat according to its existing charter.

Do not redefine Aporia’s charter unnecessarily.

⸻

13. Operator priority-elevation requests

Seats may identify exceptional work deserving more protection or faster access than their Epic normally receives.

A seat may request priority elevation.

It cannot grant it.

Only the operator may cross an Epic priority boundary.

Create a durable operator priority-request queue under a GLOBAL control-plane location.

Prefer one file per request to avoid contention.

Conceptually:

ops/operator_queue/priority/
  PRQ-....json

and a generated summary:

ops/operator_queue/PRIORITY_REQUESTS.md

Use repository naming conventions if a better canonical location already exists.

⸻

14. Priority-request schema

Support fields equivalent to:

* request ID;
* requester;
* Epic;
* Thread;
* Campaign;
* Experiment;
* optional Task;
* current priority;
* requested priority;
* request type;
* short reason;
* scientific value;
* why_now;
* what_happens_if_delayed;
* resource requirement;
* expected runtime;
* restart cost;
* preemptibility;
* opportunity/deadline window;
* created time;
* expiry;
* status;
* operator decision;
* operator note;
* decision time.

Request types should support at least:

* START_PRIORITY
* PREEMPTION_PROTECTION
* RESOURCE_RESERVATION
* DEADLINE
* ANOMALY_FOLLOWUP

The common Phase 2-B case may be:

This run can start on idle resources normally, but once started it is worth allowing it to finish.

⸻

15. Priority request lifecycle

Support states equivalent to:

* REQUESTED
* APPROVED
* DENIED
* EXPIRED
* WITHDRAWN
* COMPLETED

Requests require an expiry.

No priority request remains urgent forever.

If it expires without approval, inherited priority applies again.

⸻

16. A2A notification semantics for priority requests

Git is durable authority.

A2A is notification.

After a request has a committed durable identity, emit an event equivalent to:

PRIORITY_ELEVATION_REQUESTED

containing:

* request ID;
* Git SHA/reference;
* requester;
* Experiment;
* requested band;
* short reason.

On operator decision emit:

* PRIORITY_ELEVATION_APPROVED
* PRIORITY_ELEVATION_DENIED
* PRIORITY_ELEVATION_EXPIRED

The scheduler/workgraph only changes effective priority after the durable approved record exists.

Do not allow an A2A message alone to elevate work.

⸻

17. Operator queue email integration

The existing email distribution/digest should include open operator priority requests.

Do not require model inference to produce the section.

Render it deterministically from the durable queue.

Near the top of the digest include something like:

Operator Priority Requests — N open

with columns such as:

* Request
* Seat
* Experiment
* Current → Requested priority
* Resource/runtime
* Why now
* Expiry

Keep it compact.

Also include a short since-last-digest count such as:

* approved;
* denied;
* completed;
* expired.

Do not flood the email with closed-request detail.

The canonical detail remains in Git.

⸻

18. Generic PrometheusWorker scheduling

Each eligible machine may run one or more PrometheusWorker executors.

A PrometheusWorker should periodically or event-driven:

1. report available capabilities/resources;
2. query READY generic Tasks;
3. filter by:
    * Epic priority;
    * resource fit;
    * capability fit;
    * lease availability;
    * machine restrictions;
4. claim one via existing CAS/lease mechanism;
5. execute the packet faithfully;
6. emit progress/heartbeat facts;
7. obey preemption;
8. write a completion/attempt receipt;
9. release the lease/resources;
10. seek another eligible generic Task.

Do not make the worker an LLM agent if deterministic execution suffices.

The worker process should ideally require zero inference for ordinary execution.

⸻

19. Named seats never scavenge generic tasks

This is explicit operator policy.

Named seats do not claim GENERIC_WORKER Tasks.

This includes:

* Phase 2 engine seats;
* Phase 3 RSO builder seats;
* GLOBAL named seats.

Reason:

Named-seat inference should be reserved for chartered reasoning, design, interpretation, or specialized engineering.

Idle named seats are not a substitute for generic workers.

Likewise, generic workers cannot claim named-seat Tasks.

Implement/test this distinction.

⸻

20. Resource scheduling

Physical resources are shared opportunistically.

Expected default order:

1. safety/infrastructure-critical work;
2. EP-PHASE3 HIGH;
3. EP-GLOBAL MEDIUM;
4. EP-PHASE2B LOW.

Within the same Epic band use local priority/age/resource fit.

Phase 2-B should consume idle capacity aggressively enough to avoid wasting available machines.

But it yields when a higher-priority valid lease requires the resource.

Prefer simple lease expiry/release over elaborate live preemption where possible.

⸻

21. Bandwidth assumption

Network bandwidth is generally available and should not be treated as the primary scarce resource unless a Task specifically declares otherwise.

Scheduling should primarily consider:

* CPU;
* GPU;
* RAM;
* local storage;
* runtime environment;
* experiment duration;
* preemption cost.

Do not overengineer bandwidth reservation without evidence that it is needed.

⸻

22. Preserve engine-native execution

The generic worker launches the engine.

It does not become the engine.

An ATOMIC Experiment should look roughly like:

PrometheusWorker
  -> acquire machine lease
  -> checkout/pin registered SHA
  -> invoke native engine exactly as registered
  -> monitor execution
  -> collect artifacts/receipts
  -> terminate/cleanup
  -> release lease

Not:

PrometheusWorker
  -> reinterpret engine campaign
  -> subdivide work arbitrarily
  -> modify engine semantics

⸻

23. Phase 2-B CWO handling of preempted work

At each 48-hour close, distinguish:

* DONE
* SCIENTIFIC_OUTCOME
* ENGINEERING_FAIL
* PREEMPTED_RESOURCE
* DEFERRED
* SUPERSEDED

For PREEMPTED_RESOURCE, preserve the original Experiment registration.

The next CWO may simply state:

replay unchanged when capacity becomes available.

No scientific reconsideration is required unless circumstances changed.

⸻

24. Priority elevation and preemption protection

An operator-approved override should be narrow.

Prefer Experiment-level overrides.

Example:

EP-PHASE2B
Experiment NPE-X
base: LOW
operator override: MEDIUM
reason: PREEMPTION_PROTECTION
expires: experiment completion or timestamp

That Experiment’s descendant Tasks inherit MEDIUM.

Other Nestor work remains LOW.

Do not elevate the entire seat.

⸻

25. GLOBAL ownership

These mechanisms are GLOBAL infrastructure:

* generic worker architecture;
* priority hierarchy;
* operator priority-request queue;
* operator queue digest rendering;
* common resource leasing rules;
* A2A priority events.

They are not Phase 2-B-specific even though Phase 2-B is the immediate beneficiary.

Place them appropriately beneath EP-GLOBAL / its infrastructure Threads.

⸻

26. Interaction with Phase 3 RSO builders

The existing RSO builder seats remain restricted to EP-PHASE3:

* Palamedes
* Pallas
* Argus
* Cadmus
* Eupalamus

They do not claim generic Tasks.

They do not consume Phase 2-B tasks.

A Phase 3 Campaign may itself create generic Tasks.

Those Tasks are executed by PrometheusWorkers at HIGH inherited priority.

Thus:

scientific/engineering ownership remains with the named Phase 3 seat;
execution may occur on a generic worker.

This is desirable.

⸻

27. Example

Palamedes may create:

Task:
  run frozen RSO mutation battery
executor_class: GENERIC_WORKER
epic: EP-PHASE3
priority: HIGH

A PrometheusWorker executes it.

Palamedes does not spend Opus tokens waiting on the process.

Similarly Nestor may create:

Task:
  run frozen NPE replay campaign
executor_class: GENERIC_WORKER
epic: EP-PHASE2B
priority: LOW
execution_mode: ATOMIC

It runs when capacity is free.

If Palamedes’s Task arrives and needs the same machine, Nestor’s Attempt may be cleanly preempted/replayed according to its registered policy.

⸻

28. Tests

Add tests for at least:

* generic-worker-role excluded from seat roster;
* PrometheusWorker bootstrap;
* generic Task validation;
* named seat cannot claim generic Task;
* generic worker cannot claim named-seat Task;
* ATOMIC/NATIVE_PARALLEL/SHARDABLE validation;
* SHARDABLE requires registered aggregation semantics;
* Epic priority inheritance;
* lower Epic local priority cannot cross bands;
* approved override can cross bands;
* unapproved request cannot change priority;
* Experiment override propagates to Tasks;
* expiry removes override;
* preemption becomes PREEMPTED_RESOURCE;
* PREEMPTED_RESOURCE does not become scientific FAIL;
* Phase 2-B replay remains same registered Experiment;
* operator priority-request schema;
* digest renders open requests deterministically;
* existing C-004 remains valid;
* RSO builder seats remain EP-PHASE3-only;
* Phase 3 generic task can be executed by PrometheusWorker.

⸻

29. Bootstrap requirement

A machine operator should eventually be able to start the generic execution service with minimal instruction equivalent to:

Start PrometheusWorker on this machine.

The worker should determine from repository/configuration:

* current base role;
* generic-worker-role;
* machine identity;
* capabilities;
* how to connect to workgraph/A2A;
* what generic Tasks are eligible;
* effective priority;
* resource lease rules;
* how to execute;
* how to report;
* how to stop/preempt safely.

No scientific charter should be necessary.

⸻

30. Do not overbuild

Use current mechanisms first.

Do not create:

* a new message bus;
* a second scheduler;
* a second task database;
* a complicated distributed execution framework;
* mandatory engine sharding;
* speculative checkpoint systems.

Prefer:

* Git workgraph as durable authority;
* existing A2A/comms for notification;
* existing Fabric where appropriate and permitted;
* deterministic worker processes;
* simple resource leases;
* native engine entry points.

⸻

31. Migration / compatibility

This work must be additive.

Do not stop active C-004 / Phase 3 build work.

Do not require current Campaigns to be rewritten merely to add generic-worker support.

Provide deterministic migration/defaults.

Existing Tasks should default to named-seat execution unless clearly declared generic, to avoid accidentally handing semantically incomplete work to a PrometheusWorker.

⸻

32. Achilles deliverables

On main, produce:

1. generic-worker-role;
2. PrometheusWorker identity/bootstrap convention;
3. generic-vs-named Task execution ownership;
4. execution-mode semantics:
    * ATOMIC
    * NATIVE_PARALLEL
    * SHARDABLE;
5. inherited Epic priority model;
6. operator-approved priority overrides;
7. preemptible/restartable Task/Experiment semantics;
8. PREEMPTED_RESOURCE;
9. GLOBAL operator priority queue;
10. A2A notification conventions;
11. deterministic operator-queue Markdown view;
12. deterministic email-digest integration;
13. generic worker executor/launcher where practical;
14. tests;
15. documentation for Phase 2-B 48-hour cadence;
16. setup receipt.

⸻

33. Completion simulation

Before closing, simulate:

Case A — low-priority atomic Phase 2-B experiment

Nestor creates one complete generic execution Task.

PrometheusWorker claims it.

Phase 3 work arrives.

The run is preempted according to policy.

It is recorded as PREEMPTED_RESOURCE.

It later replays unchanged.

No scientific verdict is produced from the interrupted Attempt.

Case B — protected Phase 2-B run

Aether requests MEDIUM priority / preemption protection.

Request is written to Git and appears in operator digest.

Before approval, effective priority remains LOW.

Operator approves.

Experiment and descendants become MEDIUM for the approved window.

Other Aether experiments remain LOW.

Case C — Phase 3 generic execution

Argus creates a generic HIGH-priority deterministic test Task.

A PrometheusWorker executes it.

Argus remains the owning named seat and interprets the result.

Case D — ownership isolation

A named seat attempts to claim a generic Task.

Rejected.

PrometheusWorker attempts to claim a scientific interpretation Task.

Rejected.

⸻

34. Final report

Report:

* main SHA(s);
* new/changed control-plane paths;
* generic worker bootstrap command/convention;
* priority model;
* request queue path;
* digest integration;
* tests/results;
* completion simulation results;
* anything requiring operator action.

Do not begin Phase 2-B experiments yourself.

Do not launch PrometheusWorkers permanently without operator direction if doing so changes machine state beyond normal setup.

Do not redesign individual engines.

Your job is to build the control plane that lets those engines continue working cheaply and opportunistically.

⸻

Standing principles

Named seats reason. Generic workers execute.

The scheduler may change placement, not experimental semantics.

Parallelism is used when natural, never imposed merely to fill machines.

Phase 2-B uses idle resources but yields to higher-priority work.

A seat may request priority; only the operator may grant it.

Git records authority. A2A moves notifications.

A resource preemption is not a scientific result.

Spend inference at epistemic forks, not while machines are running.
