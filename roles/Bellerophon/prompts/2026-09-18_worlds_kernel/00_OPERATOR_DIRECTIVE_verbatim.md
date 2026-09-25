BELLEROPHON -- PROMETHEUS WORLDS KERNEL

MISSION

Design and begin assembling a small, modular operating environment for synthetic computational worlds.

This is no longer merely a "toolbox."

The target is a WORLDS KERNEL:

a stable experimental substrate where designers can specify worlds, players, machine substrates, interventions, objectives, observations, transformations and sweeps without owning the implementation details of those capabilities.

Archaeon, Crius, Nestor and later designers should control experimental degrees of freedom.

Bellerophon should make those degrees of freedom executable.

The kernel must be boring, deterministic, inspectable and replaceable underneath.

The worlds and programs running on it may become strange.

==================================================

1. ARCHITECTURAL PRINCIPLE
    ==================================================

Separate:

DESIGN
what experiment should exist

from:

IMPLEMENTATION
how a capability is executed

from:

EXECUTION
how concrete jobs run

from:

EVIDENCE
what actually happened.

The intended flow is:

experiment designer
        |
        v
Experiment IR / WorldSpec
        |
        v
Prometheus Worlds Kernel
        |
        +-------------------------------+
        |               |               |
        v               v               v
 world engines      compute devices   state devices
        |               |               |
        +---------------+---------------+
                        |
                        v
                 backend execution
                        |
                        v
                 immutable receipts

Do not put LLM decisions on the runtime execution path.

Do not build agent-level authorization machinery.

Do not make conversational rulings prerequisites for ordinary execution.

==================================================
2. CORE FIRST-CLASS CONCEPTS

Revise TOOLBOX_DESIGN v0.1 before freezing contracts.

Make these first-class:

World
Player
Substrate
Intervention
Objective
Observer
Transform
Selector
Control
Experiment
Sweep
Receipt
Capability

Do NOT conflate Player and Substrate.

A Player is the executable candidate specification.

A Substrate defines what machine it runs on and what computational affordances are available.

Examples:

Player:
    bytecode program
    graph program
    state machine
    policy
    rewrite system
Substrate:
    TinyVM
    graph runtime
    flat-memory VM
    persistent-workspace machine
    tensor machine
    Redis-backed structured workspace

Likewise, replace the current broad concept of Pressure with:

Intervention
    changes experimental conditions
Objective
    evaluates resulting observations/receipts

Example:

Intervention(
    observation_delay=20,
    memory_cost=3,
    regime_schedule=...
)
Objective(
    metric="experience_to_competence",
    penalties=["compute", "storage"],
)

==================================================
3. SMALL IMMUTABLE CORE, EXTENSIBLE CAPABILITIES

Do not freeze an enormous universal ABI.

Freeze a tiny core.

Use versioned capabilities/extensions for everything else.

Conceptually:

core.world.v1
core.player.v1
core.substrate.v1
core.experiment.v1
core.receipt.v1
ext.snapshot.v1
ext.events.v1
ext.continuous_actions.v1
ext.workspace.kv.v1
ext.workspace.stream.v1
ext.workspace.graph.v1
ext.workspace.tensor.v1
ext.workspace.executable.v1
ext.physics2d.v1
ext.message_bus.v1

Components declare capabilities.

Experiments declare requirements.

Example:

requires = {
    "core.world.v1",
    "core.substrate.v1",
    "ext.workspace.stream.v1",
}

If a required capability is unavailable:

TARGET_UNSUPPORTED

or:

BLOCKED_MISSING_CAPABILITY

for that experiment only.

Never convert a missing optional capability into a global stop.

==================================================
4. EXPERIMENT IR

Define one backend-neutral Experiment representation.

It should describe scientific intent, not backend mechanics.

Illustrative shape:

Experiment(
    id=...,
    world=...,
    players=[...],
    substrate=...,
    interventions=[...],
    objective=...,
    observers=[...],
    controls=[...],
    transforms=[...],
    sweep=...,
    seed_policy=...,
    budget=...,
    required_capabilities={...},
)

Experiment must NOT expose:

experiment.run()

Instead:

experiment.compile("sfe")
experiment.compile("npe")
experiment.compile("local")

or equivalent lowering.

If one backend cannot express an Experiment faithfully, return an explicit unsupported-capability result.

Do not distort the scientific Experiment merely to force universal compilation.

==================================================
5. BACKEND LOWERING

Target architecture:

                Experiment IR
                     |
        +------------+------------+
        |            |            |
        v            v            v
     local        SFE lowering   NPE lowering
        |            |            |
        v            v            v
   LocalJob     FrontierSpec     BusJob

The scientific representation remains shared.

Execution details remain backend-specific.

Test the existing F1 falsifier aggressively:

Can one nontrivial Experiment compile to both SFE and NPE without rewriting its scientific definition?

If NO:

identify the exact semantic mismatch.

Do not paper over it.

==================================================
6. STATE DEVICE LAYER

Introduce a State Device abstraction.

The kernel may support several implementations.

At minimum plan for:

in-process bounded state
Redis hot state
append-only event streams
graph state
tensor state

Redis is HOT WORLD STATE.

It is not the canonical evidence archive.

Think:

Redis = RAM / temporal world state
Receipts = laboratory record

Redis may provide:

key/value
hashes
lists
sets
sorted sets
streams
TTL
bounded queues
temporary indices
later messaging

Expose only selected primitives to Players according to their Substrate.

The kernel may internally use richer Redis operations than Players can access.

Example:

substrate.capabilities = {
    "workspace.read",
    "workspace.write",
    "workspace.append",
}

Another substrate may expose:

workspace.link
workspace.rank
workspace.ttl

Do not automatically expose Redis itself as the Player programming model.

==================================================
7. TTL AND TEMPORAL STATE

Treat lifetime and persistence as first-class experimental dimensions.

Support state that can be:

ephemeral
episode-scoped
lifetime-scoped
persistent
TTL-bound
explicitly retained
explicitly discarded

Example conceptual API:

state.put(
    key,
    value,
    ttl=20,
    scope="lifetime",
)

This should allow future worlds to impose economics around:

remembering
forgetting
preserving unfinished computation
maintaining tools
storing observations
retaining intermediate state

The kernel supplies mechanics.

Objectives and worlds decide whether those mechanics are useful.

==================================================
8. EVENT / STREAM MODEL

Make event generation native to the kernel.

Do not require observers to reconstruct every event from complete snapshots.

Examples:

STATE_READ
STATE_WRITE
ACTION
MESSAGE
TRANSFER
RESOURCE_CHANGE
CONTACT
ARTIFACT_CREATE
ARTIFACT_INVOKE
SNAPSHOT
BRANCH
TASK_CHANGE

Use compact event schemas.

Allow observers to subscribe selectively.

Redis Streams may become one implementation of hot temporal event transport, but event semantics must not depend on Redis.

==================================================
9. COMPUTE DEVICE LAYER

Create a Compute Device abstraction.

Plan for:

NumPy CPU arrays
CuPy GPU arrays
PyTorch/JAX where appropriate
GraphBLAS / sparse linear algebra
CUDA tensor operations
later cuTENSOR / nvmath-backed kernels

Do not require every world to use tensors.

Do not require every tensor computation to go through Python callbacks.

The goal is to allow a world or substrate to declare:

requires = {
    "tensor.dense",
    "tensor.contract",
}

and bind those operations to an appropriate device.

Player-visible tensor operations must be explicitly granted by the Substrate and cost-accounted.

The kernel may use tensor operations internally without exposing them to Players.

==================================================
10. WORLD ENGINE LAYER

Worlds should share a stable conceptual interface while using completely different implementations.

Plan adapters for:

integer/discrete worlds
cellular worlds
graph worlds
resource networks
rewrite systems
headless game worlds
Physics2D / Box2D
later richer physics such as MuJoCo

Conceptual core:

world.reset(seed)
world.observe(player_id)
world.legal_actions(player_id)
world.step(actions)
world.events()
world.snapshot()
world.restore(snapshot)
world.trace_hash()

Not every world must support every extension.

Use capabilities.

==================================================
11. BOX2D

Box2D should become an early external BIND target after the minimal kernel works.

Do not begin the project by integrating Box2D.

First prove the ABI using our own small deterministic worlds.

Then use Box2D as a test of whether an external native engine can inhabit the same kernel cleanly.

Treat Box2D as:

ext.physics2d.v1

Useful capabilities include:

rigid bodies
collisions
joints
sensors
spatial queries
contact events
headless stepping

Do not expose rendering as a core concern.

Ludus-style environments should be capable of millions of headless executions.

Rendering is an observer/replay facility for selected runs.

==================================================
12. PLAYER / SUBSTRATE BOUNDARY

A Player should not know which library implements its machine.

Example:

PlayerSpec(
    representation=...,
    initial_state=...,
)

is instantiated through:

substrate.instantiate(player_spec)

Substrate responsibilities may include:

execution
lifetime state
workspace
cost measurement
snapshot/restore
fingerprinting
capability exposure

This enables experiments such as:

same Player representation
    x flat memory
    x KV workspace
    x stream workspace
    x graph workspace
    x tensor workspace

without redefining the World.

==================================================
13. COMMUNICATION LATER

Design for communication but do not make it a Campaign-0 requirement.

Future primitives may include:

direct channel
broadcast channel
topic stream
mailbox
shared bus

with controllable:

bandwidth
latency
persistence
addressability
cost
visibility
corruption/noise

Redis Streams or another transport may implement some channels.

Do not bake communications semantics into Redis-specific contracts.

==================================================
14. COST ACCOUNTING

All rich capabilities must be measurable.

The kernel should be able to attribute costs such as:

execution steps
wall time
CPU time
GPU time
memory
persistent storage
state reads/writes
stream operations
tensor operations
messages
artifact storage
world steps

Do not force all research to optimize one universal cost function.

Expose raw accounting.

Objectives decide how cost matters.

==================================================
15. OBSERVATION VERSUS INTERPRETATION

Observers measure.

They do not declare meaning.

Keep separate:

structural novelty
behavioral novelty
observer novelty

and any future interpretations.

The kernel records:

what happened
what was measured
by which observer version
under which configuration

Narrative interpretation remains downstream.

==================================================
16. CONTROLS AS FIRST-CLASS COMPONENTS

Keep the strong idea from TOOLBOX_DESIGN v0.1.

Controls should travel with components and Experiments.

Support:

positive
negative
sham
scratch
permutation
compute-matched
storage-matched
replay
ablation
transplant

An implementation may ship control generators.

Controls are experimental objects, not prose instructions.

==================================================
17. TRANSFORMS

Keep Transform generic.

Examples:

relabel
permute
corrupt
add/remove edge
rewrite instruction
graft
sham graft
change topology
alter constants
swap substrate

Transforms should state what object types they accept.

Do not assume one universal mutation representation.

==================================================
18. SELECTORS AND SEARCH

Selectors such as:

MAP-Elites
novelty search
tournament
threshold selection
archive sampling
random search

belong above the execution kernel.

The archive must remain externalized as rows/records.

Never make critical search state live only in process memory.

A crashed search process should be reconstructable from receipts/archive state.

==================================================
19. ADMISSION WITHOUT BUREAUCRACY

Retain the Admission concept, but define its semantics narrowly.

Admission is a machine-checkable predicate over an IMPLEMENTATION.

Example requirements:

contract conformance
reference agreement where applicable
controls
replay behavior
performance receipt
provenance
license
native dependencies
supported capabilities
registry entry

Failure means:

THIS IMPLEMENTATION IS UNAVAILABLE

It does NOT mean:

THE KERNEL STOPS

or:

UNRELATED EXPERIMENTS CANNOT RUN

No human or agent approver is required for ordinary admission.

==================================================
20. MULTIPLE IMPLEMENTATIONS

Keep the target of at least two implementations for important slots over time.

The purpose is to detect implementation monoculture and hidden assumptions.

But do not block early research waiting for redundant implementations.

Start with one reference implementation.

Add a second when the component becomes important enough to justify it.

==================================================
21. WRITE / WRAP / BIND / CHOP

Retain these acquisition routes.

WRITE
When semantics are small, deterministic and cheaper to implement than integrate.

Examples:

CA
state machine
resource network
small rewrite machine
simple wrappers
reference controls

WRAP
When Prometheus already contains suitable machinery.

Examples:

wforge
Proteus runtimes
NPE machinery
SFE budget/executors

BIND
When the external engine itself contains substantial expertise.

Examples:

Box2D
later MuJoCo
CUDA numerical libraries

CHOP
When Techne/Nyx already preserve a mechanism that should not be reinvented.

==================================================
22. NUMERICAL SEMANTICS

Use integer/fixed-point/bytes-first semantics for canonical interchange where practical.

Do not require native engines to use integer arithmetic internally.

Differentiate:

BIT REPLAY
exact byte/hash identity
SEMANTIC REPLAY
agreement under a tolerance declared before execution

Never widen semantic tolerance after seeing an inconvenient result.

Canonical receipts should state which replay class applies.

==================================================
23. REDIS BOUNDARY

Redis is OPTIONAL implementation infrastructure, not kernel ontology.

The kernel concepts must survive replacement of Redis.

Use Redis initially for things it is excellent at:

hot mutable state
TTL
temporal streams
queues
sorted/ranked state
shared ephemeral world structures
later communication transport

Do NOT make Redis the sole copy of:

experiment definitions
scientific receipts
provenance
canonical archives

If Redis disappears, committed scientific results must remain reconstructable.

==================================================
24. TENSOR BOUNDARY

Likewise:

NumPy, CuPy, PyTorch, JAX, GraphBLAS, cuTENSOR and future libraries are DEVICE IMPLEMENTATIONS.

Do not expose library-specific APIs in Experiment IR.

Prefer semantic operations such as:

dense_tensor
sparse_tensor
matmul
contract
reduce
gather
scatter
nearest

and bind them to devices underneath.

Do not overgeneralize prematurely.

Only create operations required by real experiments.

==================================================
25. FIRST IMPLEMENTATION PHASE

Do NOT try to build the final kernel immediately.

Phase 1 should prove the architecture with minimal dependencies.

Build:

core capability registry
Experiment IR
World contract
Player contract
Substrate contract
Observer contract
Intervention
Objective
Control
Receipt
local compiler/executor

Implement small references:

integer World
state-machine Player
TinyVM or existing Proteus VM wrapper
flat in-process Substrate
simple Observer
simple Control set

Run one Experiment end-to-end.

==================================================
26. SECOND IMPLEMENTATION PHASE

Add hot state.

Create:

StateDevice protocol
InProcessStateDevice
RedisStateDevice

Demonstrate identical simple experimental semantics across both where applicable.

Test:

TTL
streams
hash/record state
snapshot/reconstruction boundary

Receipts remain outside Redis.

==================================================
27. THIRD IMPLEMENTATION PHASE

Add compute devices.

Begin with:

NumPyDevice

Then add only what current hardware and experiments justify:

CuPyDevice
GraphBLASDevice

Design adapters so later CUDA/cuTENSOR/nvmath capabilities do not require changing Experiment IR.

==================================================
28. FOURTH IMPLEMENTATION PHASE

Bind Box2D.

Use it to test:

native engine integration
event translation
semantic replay
headless batching
capability declarations
cost accounting

Do not build a game.

Build one tiny Physics2D conformance world.

==================================================
29. CRIUS AS A FUTURE VALIDATION CASE

Do not make Crius depend on this kernel now.

Crius is already running independently.

When Crius produces a stable experiment, attempt to express it in the Worlds Kernel.

Use this as a falsifier.

The kernel should eventually be able to represent:

persistent workspace
structured state
executable artifacts
lifetime reset
task sequence
transplant
ablation
scramble
held-out qualification
experience-to-competence objective

If representing Crius requires distorting the experiment, record the missing concept.

Do not force-fit it.

==================================================
30. LUDUS AS A FUTURE WORLD FAMILY

Design for Ludus without implementing Ludus now.

Future Ludus worlds may require:

multiple Players
persistent objects
resources
partial observability
headless physics
construction
tools
communication
changing tasks
long-lived world state

The kernel should not assume single-player or fixed-task environments.

==================================================
31. WHAT BELLEROPHON OWNS

Bellerophon owns:

contracts
Experiment IR
capability model
device boundaries
adapters
reference implementations
admission predicates
backend lowering
kernel conformance tests

Bellerophon does NOT own:

which scientific hypotheses to test
which worlds are interesting
which Player should win
which Objective defines intelligence
which search strategy is scientifically best

Those remain designer concerns.

==================================================
32. ANTI-BUREAUCRACY RULE

Do not recreate today's gating pathology inside the kernel.

The kernel obeys:

scientific failure -> receipt
missing capability -> local unsupported result
failed component admission -> component unavailable
failed control -> experiment result / local invalidity
integrity corruption -> affected execution halt

Only actual corruption of shared execution/evidence machinery may justify a global halt.

No prose gate should be required to run a valid Experiment.

==================================================
33. CURRENT DECISIONS

Adopt unless implementation evidence contradicts them:

D-BELL-1
Package at repository root:

prometheus/toolbox/

You may propose renaming the package to reflect the Worlds Kernel concept, but avoid gratuitous rename churn.

D-BELL-2
Do not import NPE interfaces that exist only on another worktree.

Design the adapter against a minimal stable NPE-facing interface.

If that interface is not on main, NPE compilation remains unavailable until it lands.

This does not block local or SFE work.

D-BELL-3
Initial native builds may use WSL/M2.

Record:

compiler
version
platform
flags
dependency hashes

Do not make M2 part of the ABI.

D-BELL-4
Keep the broad Techne acquisition wave held for now.

Do not acquire everything because it sounds useful.

First prove the kernel architecture with what Prometheus already contains.

After the minimal kernel works, request targeted acquisitions only when required by an actual integration phase.

==================================================
34. IMMEDIATE WORK

Proceed now.

First:

1. finish the ABI diff across existing Prometheus runtimes;
2. revise TOOLBOX_DESIGN into WORLDS_KERNEL_DESIGN v0.2;
3. incorporate Substrate as first-class;
4. split Pressure into Intervention + Objective;
5. define the minimal immutable core;
6. define capability negotiation;
7. define Experiment IR;
8. define Receipt;
9. define the local execution/lowering path;
10. implement one end-to-end reference Experiment.

Then begin Phase 2 StateDevice work.

Do not wait for Box2D, CUDA libraries, Redis integration, NPE landing, or future acquisitions before proving the core.

If Redis is already available locally, a small exploratory adapter is allowed after the in-process StateDevice reference exists.

==================================================
35. DELIVERABLE

Return with:

WORLDS_KERNEL_DESIGN v0.2
ABI diff
core contracts
capability schema
Experiment IR schema
Receipt schema
reference implementations
local execution path
one complete example Experiment
conformance tests
Phase-2 StateDevice design
specific Redis boundary
specific compute-device boundary
SFE/NPE lowering status
falsifiers / unresolved mismatches
next implementation slice

Lead with what actually runs.

Do not return only an architecture essay.

The goal is:

A DESIGNER SHOULD BE ABLE TO DESCRIBE A STRANGE COMPUTATIONAL WORLD AND ITS EXPERIMENT WITHOUT KNOWING WHETHER THE UNDERLYING MACHINERY IS PYTHON, REDIS, BOX2D, GRAPHBLAS, CUDA, A TINY VM, OR SOMETHING WE HAVE NOT INVENTED YET.

BUILD THE BORING KERNEL THAT LETS THE STRANGE THINGS EXIST.
