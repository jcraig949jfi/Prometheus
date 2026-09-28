Nope.  Document, freeze and pick it up later.  Do this instead:

ODYSSEUS — PROMETHEUS AGENT FABRIC / A2A V0

The operator is unfreezing the distributed-brain substrate lane.

The current coordination model is no longer adequate.

Build its replacement.

This is a substantial engineering + experimental program. Do not return after writing an architecture document or making one toy RPC work.

The objective is to produce and exercise a minimal durable Agent Fabric that can take real Prometheus research work away from the current manual seat-to-seat coordination loop.

PURPOSE

Today too much state lives in Claude sessions:

* who was delegated what;
* whether another seat read a message;
* which machine should run something;
* whether a worker is still alive;
* whether a task crashed;
* whether it should be retried;
* where the result artifact went;
* whether compute is busy;
* when a lease expires;
* which worker has the relevant capability;
* whether the principal needs to poll;
* whether the operator needs to assign another worker.

Move those concerns below the inference layer.

The desired model is approximately:

Scientific principal / Claude seat
            |
         A2A client
            |
    PROMETHEUS AGENT FABRIC
    -----------------------
    durable Tasks
    Attempts
    capability routing
    artifacts
    worker heartbeat
    crash recovery
    resource leases
    queueing
    provenance
    -----------------------
       |            |
   worker node   worker node
     ubu001        ubu002
       |            |
   isolated      isolated
   Claude Code   Claude Code
       |            |
    artifact       artifact
       \            /
          principal
          synthesizes

Git remains scientific authority.

Atlas remains scientific memory/index.

Threads remain the unit of scientific delegation.

Engines remain scientific capabilities.

The Agent Fabric handles execution and coordination.

EXTERNAL STANDARD

Target A2A Protocol v1.0 at the protocol boundary.

Do not invent a Prometheus-only peer protocol if A2A already defines the concept.

Use A2A concepts for:

* Agent Card;
* Task;
* Message;
* Artifact;
* task state;
* capability/skill discovery;
* long-running asynchronous work.

Prometheus-specific metadata may extend those objects.

Do not put Thread/Campaign/Experiment semantics into the A2A standard itself.

If the official Python SDK is practical, prefer using it in an isolated service environment rather than hand-implementing the standard.

If SDK/dependency constraints make that unreasonable for the first internal pilot, implement the durable core independently and put a deliberately thin A2A v1 adapter on top.

Document which parts are fully protocol-compliant and which are pilot-only.

Do not falsely claim compliance.

IMPORTANT EXISTING INFRASTRUCTURE

Start by inspecting, not replacing:

* comms/
* comms/api.py
* comms/schema.sql
* the atomic comms claim behavior;
* roles/Ananke/research/lease.py;
* roles/Nestor/tools/nestor_lease.py;
* Artemis’s thread-ID work;
* ops/threads/;
* ubu001 / ubu002 worker-isolation evidence;
* existing Claude Code worker launch patterns.

comms already supplies:

* the canonical Postgres connection;
* environment identity checks;
* seat roster;
* instance identity;
* presence;
* capabilities;
* message provenance;
* an elementary task queue;
* atomic claims.

Reuse those good pieces where appropriate.

Do not mutate the existing comms queue into something incompatible during the pilot.

Prefer a sidecar fabric schema/package that can coexist with it.

DESIGN PRINCIPLE 1 — THREAD != TASK != ATTEMPT

Preserve these distinctions.

THREAD

Scientific research responsibility.

Durable in Git.

Example:

thr-4059475204e4

The Thread survives many experiments, tasks, workers and machines.

TASK

One durable requested unit of work.

Examples:

* reconstruct one engine from Git;
* run one ancestry replay;
* perform a literature raid;
* execute a frozen assay;
* independently review one result.

A Task survives worker death.

ATTEMPT

One actual execution of a Task.

A crashed worker creates a failed/abandoned Attempt.

It does NOT mutate the scientific identity of the Task.

A retry creates another Attempt.

This distinction is mandatory.

DESIGN PRINCIPLE 2 — TASKS SURVIVE CLAUDE

A task must continue to exist when:

* the principal’s Claude session exits;
* the worker’s Claude session exits;
* a machine reboots;
* a worker crashes;
* the operator closes the app;
* no human is watching.

Claude sessions consume Tasks.

They do not constitute the Task store.

DESIGN PRINCIPLE 3 — PULL BY CAPABILITY

Do not require the principal to choose a machine for routine work.

A Task should be able to say approximately:

required capabilities:
  repo.read
  python.stdlib
  research.synthesis

or:

engine.npe.byte_ancestry
resource.cpu8

Workers advertise capabilities.

Compatible workers pull work.

Allow explicit target-agent routing when scientific independence or custody requires it, but capability routing should be the normal case.

Do not build a sophisticated optimizer yet.

Correct matching + atomic claim is enough.

DESIGN PRINCIPLE 4 — RESOURCE LOCALITY IS SEPARATE

Agents are portable.

Resources may not be.

Task metadata should be able to express, minimally:

* required capability;
* optional host affinity;
* CPU/GPU/RAM resource class;
* data/service locality where unavoidable.

Do not encode a full scheduling language.

DESIGN PRINCIPLE 5 — LEASES BELOW THE AGENT

Unify resource leasing as part of the fabric pilot.

The recent Ananke/Nestor collision demonstrated that multiple lease conventions are unacceptable.

Build one atomic shared lease implementation against the canonical durable store.

At minimum support resources such as:

M1:cpu8
M1:gpu
M1:ram16
M2:cpu8
M2:gpu
M2:ram16

A lease records:

* resource;
* Attempt owner;
* host;
* envelope/purpose;
* acquired time;
* expiry;
* heartbeat/renewal;
* release.

A heavy Task should not become WORKING until its Attempt has the necessary lease.

If the resource is busy:

* leave the Task available/waiting;
* do not compete;
* allow the worker to take another compatible Task.

Do NOT create another silent fallback lease convention.

For substantial shared compute, if the canonical lease store cannot be reached, fail closed and wait.

The science can continue elsewhere.

DESIGN PRINCIPLE 6 — THREADS QUEUE; RESEARCHERS DON’T

A worker that cannot run Task A because M1:cpu8 is occupied should be able to pick Task B:

* literature;
* repo archaeology;
* analysis;
* another CPU-light Thread.

Do not block a whole principal because one experiment is waiting.

MINIMUM DURABLE DATA MODEL

Build the smallest useful durable model.

Something equivalent to these concepts is required.

TASK

* task ID;
* context ID;
* principal;
* optional target agent;
* canonical Thread ID;
* optional Campaign/Experiment references;
* instruction/input;
* required capabilities;
* resource requirements;
* pinned base SHA where applicable;
* priority;
* lifecycle state;
* created/updated timestamps;
* provenance/idempotency key;
* result/error summary.

Use A2A-compatible lifecycle semantics wherever possible.

Terminal Tasks must remain terminal.

Retry happens through Attempts before terminal failure, or by creating a new Task after terminal disposition.

ATTEMPT

* attempt ID;
* Task ID;
* worker agent;
* worker instance;
* host;
* model;
* start/end;
* status;
* base SHA;
* worktree;
* execution environment receipt;
* lease IDs;
* exit/error information.

ARTIFACT

* artifact ID;
* Task ID;
* Attempt ID;
* name/kind;
* MIME/media type where useful;
* content or URI;
* sha256;
* byte size;
* metadata.

EVENT

Append-only lifecycle/history events:

* submitted;
* claimed;
* attempt started;
* heartbeat;
* artifact added;
* status change;
* attempt failed;
* requeued;
* completed;
* canceled.

This is forensic history.

Do not make principals reconstruct the lifecycle from logs.

AGENT / CARD

Persist or derive:

* logical agent identity;
* instance;
* host;
* capabilities/skills;
* supported input/output modes;
* protocol endpoint;
* liveness;
* current capacity where appropriate.

ARTIFACT DEPOSITION

This is important.

ARC2 showed workers could complete research but sometimes could not deposit their report file.

Fix that below the worker.

The worker runtime—not Claude itself—must capture the final result.

At minimum every Attempt should retain:

* final worker text;
* stdout/stderr or structured equivalent;
* exit status;
* environment receipt.

For work that changes files, support returning something such as:

* patch;
* git bundle;
* local commit SHA + bundle;
* explicitly named files.

Workers should NOT need direct write permission to main.

Default pattern:

worker produces artifact
    ->
principal reviews
    ->
principal/integrator decides whether to land it in Git

This is both safer and more independent.

CLAUDE CODE WORKER ADAPTER

Build a worker adapter for isolated Claude Code.

The pilot should use disposable workers rather than hijacking the persistent remote-control sessions.

Isolation should include:

* dedicated worktree;
* pinned base SHA;
* empty/dedicated CLAUDE_CONFIG_DIR;
* worker-specific output directory;
* no inherited seat memory;
* explicit model;
* explicit wall-time limit;
* environment receipt.

Reuse what Archaeon’s E-001/E-002 work learned.

Verify that an isolated worker does not identify itself as Odysseus/Artemis because of node-local memory.

SECURITY

Do not read or print token contents.

If setup-token authentication is needed, the service may inherit it from a protected node-local environment.

Do not place credentials in:

* Agent Cards;
* Task records;
* artifacts;
* logs;
* Git.

For the first pilot, restrict workers to tasks that do not require sudo or package installation.

Do not let unattended Claude modify the host environment.

A2A GATEWAY

Expose the fabric through an A2A v1 boundary.

A single multi-agent/multi-tenant Prometheus gateway is acceptable for the pilot.

We do not need one HTTP daemon per seat.

Prefer something like:

Agent Card -> logical principal/worker capability
A2A SendMessage -> create/continue Task
GetTask -> durable current state
ListTasks -> discover outstanding work
CancelTask -> cancel eligible work
Artifact -> result

Streaming/push can come after polling works unless the official SDK makes them essentially free.

The wire API must not become the canonical storage implementation.

The Postgres-backed core should work even if the HTTP process restarts.

CLI FOR CLAUDE PRINCIPALS

Before building a fancy UI, provide a CLI that Claude Code can call.

Conceptually:

fabric agents
fabric submit ...
fabric tasks
fabric show <task>
fabric artifacts <task>
fabric cancel <task>

A principal should be able to delegate from its shell without posting a prose comms request.

Example desired interaction:

Archaeon:
  submit capability=research.npe_ancestry
         thread=thr-...
         base=<sha>
         prompt=<file>
Fabric:
  task tsk-... SUBMITTED
compatible worker:
  atomically claims
  attempt att-...
  executes
  uploads report artifact
  completes
Archaeon:
  sees COMPLETED + artifact

No operator assignment.

No “has Nestor read #788?”

No manual report relay.

COMMS DURING MIGRATION

Do not delete comms.

During the pilot:

* comms remains human-readable coordination/broadcast;
* fabric becomes the execution/task path for pilot work;
* important lifecycle transitions MAY emit concise comms receipts for visibility;
* comms messages are not the canonical Task state.

Eventually we can decide what comms becomes.

Do not decide that in advance.

GIT / ATLAS BOUNDARY

Git:

* scientific declarations;
* preregistrations;
* Thread definitions;
* reports promoted by principals;
* durable code/evidence pointers.

Agent Fabric:

* who is doing what;
* attempt lifecycle;
* worker state;
* transient result artifacts;
* resource leases.

Atlas:

* what science ran;
* what was observed;
* what was concluded;
* relationships among research objects.

Do not turn Agent Fabric into Atlas.

Do not turn Atlas into a scheduler.

TASK METADATA

Keep Prometheus metadata small.

A Task should be able to carry references such as:

thread_id
campaign_id
experiment_id
base_sha

plus:

capabilities
resource_class

Avoid giant mandatory schemas.

A research Task may legitimately have only:

* Thread;
* question/prompt;
* base SHA;
* capability requirement;
* artifact expectation.

CRASH / RECOVERY

This is a central acceptance requirement.

Implement attempt heartbeat / expiry.

If a worker disappears:

* the Attempt becomes ABANDONED or FAILED;
* its lease expires/releases;
* the Task can return to the available state if retry policy permits;
* another worker may claim a new Attempt.

Never allow two live Attempts to believe they own the same exclusive Task unless the Task explicitly allows replication/independent parallel Attempts.

Support a deliberate independent-replication mode later if useful.

Do not confuse it with accidental duplicate claims.

IDEMPOTENCE

Submission should support an idempotency/provenance key.

A principal retrying the same network call must not create duplicate research Tasks accidentally.

PILOT HOSTS

Use:

* ubu001;
* ubu002.

Do not touch production engine behavior during the first pilot.

Do not require M1/M2 heavy compute initially.

The canonical Postgres on M1 may be used as the durable fabric store if that remains the cleanest design.

PILOT TASK CLASSES

Start with at least:

1. research.repo_readonly
2. research.synthesis
3. compute.cpu.light

Then add a leased synthetic resource task to prove queueing.

Do not start with NPE/PTE/BEE production experiments.

PILOT EXPERIMENT

After unit/integration validation, run a real distributed pilot.

The pilot must prove the system rather than merely demonstrate a happy path.

At minimum:

P1 — CAPABILITY ROUTING

Submit several Tasks without naming a machine.

Show compatible workers claim them.

Show an incompatible worker does not.

P2 — ATOMIC CLAIM

Race ubu001 and ubu002 for one Task.

Exactly one wins.

P3 — PRINCIPAL DISAPPEARS

Submit a Task.

Stop/restart the submitting client/principal process.

Task and Attempt state survive.

P4 — WORKER CRASH

Deliberately kill a worker mid-Attempt.

Show:

* Attempt is eventually marked failed/abandoned;
* no artifact is falsely reported complete;
* Task becomes eligible for another Attempt;
* second worker can finish it.

P5 — RESOURCE QUEUE

Hold a synthetic or real cpu8 lease.

Submit:

* one Task requiring cpu8;
* one research-only Task.

Show:

* cpu8 Task waits;
* worker completes the research Task instead;
* cpu8 Task runs after lease becomes available.

This is the concrete test of:

Threads queue; researchers don’t.

P6 — ARTIFACT DEPOSITION

Have Claude produce a report.

Prevent it from writing directly to main.

Show the runtime still captures the artifact with:

* Task ID;
* Attempt ID;
* hash;
* final text.

Principal retrieves it successfully.

P7 — CONTEXT ISOLATION

Launch a disposable worker with empty context.

Prove it does not inherit the persistent node-seat identity/memory.

Record the actual model used.

P8 — RESTART

Restart the fabric HTTP gateway.

Task state remains unchanged.

P9 — A2A VALIDATION

Run the appropriate A2A Inspector/TCK or official validation available for the implementation.

Record exactly what passes and what is not implemented.

Do not call the pilot A2A-compliant if the validator disagrees.

SECOND PILOT — REAL SCIENCE

Only after P1–P9 pass.

Use a small set of existing research-ready Threads.

A good candidate is Artemis’s current prospective test, because it already needs:

* fresh workers;
* equal budgets;
* blinded cohort identity;
* independent scorer;
* many Tasks;
* no manual operator assignment.

Do NOT alter Artemis’s frozen scientific protocol merely to fit the fabric.

Instead test whether the fabric can faithfully execute it.

Alternatively select another already-prepared read-only research block if Artemis’s test would be contaminated by implementation work.

MEASURE WHETHER THIS ACTUALLY HELPS

Do not declare victory because messages moved over HTTP.

Compare the pilot with the current workflow.

Measure at least:

* operator interventions;
* principal manual coordination actions;
* tasks lost;
* duplicate executions;
* report-relay steps;
* worker startup time;
* time spent waiting on resource contention;
* recoveries after intentional failures;
* percentage of Tasks that reached durable artifacts without manual rescue.

The central question is:

Does adding another worker increase research capacity much more than it increases HITL/coordination burden?

If not, the fabric is not solving the problem.

DO NOT BUILD YET

Do not build:

* a web dashboard;
* Kubernetes;
* a global optimizer;
* elaborate priority scoring;
* a fleet-wide ontology;
* automatic scientific judgment;
* Atlas scheduling;
* automatic merging to main;
* unrestricted shell workers;
* a generalized cloud platform.

We need a durable nervous system, not an operating-system research project.

BACKLOG INTEGRATION

Once the core pilot works, design the thin bridge from mature Threads to Tasks.

A Thread should be able to spawn one or more Tasks.

Tasks returning results may:

* answer the Thread;
* sharpen it;
* split it;
* create new Threads.

That transformation remains the principal’s scientific responsibility.

Do not have the fabric automatically decide scientific disposition.

EXTERNAL RESEARCH

Review current A2A v1 documentation, official Python SDK, samples and validation tools before locking the protocol boundary.

Also look for established designs for:

* durable agent task stores;
* work stealing/pull queues;
* heartbeat/lease recovery;
* idempotent task submission;
* artifact stores.

Prefer boring, proven machinery underneath the science.

Do not reinvent distributed systems problems unnecessarily.

DELIVERABLES

Return with:

1. ARCHITECTURE

What was actually built and why.

2. PROTOCOL

A2A version/binding and validation status.

3. DATA MODEL

Task / Attempt / Artifact / Event / Agent Card / resource lease.

4. CLI

Commands a Claude principal actually uses.

5. WORKER

How isolated Claude workers are launched.

6. ROUTING

How capability matching works.

7. LEASES

How shared resource ownership is now atomic and visible.

8. RECOVERY

Crash, restart, expiry and retry behavior.

9. ARTIFACTS

How reports survive even when workers cannot write to Git.

10. PILOT

P1–P9 evidence, including deliberately induced failures.

11. SCIENCE PILOT

If safe, one real Thread-based workload.

12. BEFORE / AFTER

Measured HITL and coordination burden.

13. DEFECTS

Everything that broke.

14. WHAT NOT TO MIGRATE

Pieces of the old system that are still better.

15. NEXT MIGRATION

The smallest next fleet adoption step.

OPERATOR BOUNDARY

Do not ask the operator about:

* module names;
* DB table names;
* exact HTTP library;
* CLI spelling;
* worker polling interval;
* test ordering;
* retry implementation details.

Make those decisions.

Return early only if:

* credentials/security require operator action;
* you need meaningful new spend;
* the design requires destructive migration of current comms;
* the A2A architecture fundamentally conflicts with an existing scientific guarantee;
* you discover that the approach cannot meet the objective.

Otherwise build and test it.

SUCCESS CONDITION

The pilot succeeds when a scientific principal can say:

“I need this kind of research done.”

and the system can:

* discover a suitable worker;
* preserve the task;
* wait for resources;
* launch isolated execution;
* survive crashes;
* capture artifacts;
* return the result;

without the operator selecting the worker, monitoring the run, relaying the report, or remembering that the Task exists.

That is the bar.

Build that first.
