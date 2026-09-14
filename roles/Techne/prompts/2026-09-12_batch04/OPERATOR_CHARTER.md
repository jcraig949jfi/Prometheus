TECHNE — FOSSIL HARVEST BATCH 04

Round 04 sharpens the harvest.

The vault now has breadth.

This batch should preferentially acquire computational machinery whose behavior
was shaped by explicit environmental pressure:

SCARCITY
CONTENTION
DELAY
FAILURE
UNCERTAINTY
NOISE
MEMORY LIMITS
FEEDBACK
HIDDEN STATE
DEADLINES
COMPETITION
INSTABILITY

These are particularly valuable fossils for the eventual Nyx behavioral atlas.

Do not chase general software completeness.

Acquire MACHINERY UNDER PRESSURE.

TARGET SIZE

Target:

15-20 new specimens.

Fewer is acceptable if preservation/build work is materially harder.

At least 75% of the batch should come from the focused axes below.

Do not fill the remainder with easy canonical algorithms merely to hit count.

AXIS 1 — CONTENTION / RETRY / RECOVERY

THIS IS THE HIGHEST PRIORITY.

The current vault has effectively no dedicated representation here.

Acquire multiple genuinely different systems involving failed action,
contention, retry or recovery.

Seek:

TCP congestion control
Ethernet exponential backoff
retransmission protocols
randomized lock backoff
database transaction retry
distributed mutex
leader election
consensus
failure detectors
checkpoint / restart
journal recovery
retry queues
congestion-aware routing

Prefer actual implementations over textbook pseudocode.

At least THREE specimens should come from this axis.

Where possible, acquire historical variants of the SAME lineage.

Especially desirable:

Tahoe / Reno / NewReno / CUBIC-like congestion-control lineage

or another lineage where behavior changed under pressure across time.

Do not decompose.

Preserve version history and runnable behavior.

AXIS 2 — CONTROL / FEEDBACK

CONTROL IS CURRENTLY EMPTY.

Acquire real feedback machinery.

Seek:

PID controller
adaptive controller
model predictive controller
cruise-control reference implementation
motor-control loop
robotics feedback controller
process-control system
trajectory controller
beam / precision-positioning controller
industrial reference controller

Prefer specimens with:

a plant/simulator;
disturbance input;
setpoint;
observable control response.

At least THREE distinct control traditions if practical.

A PID implementation, adaptive controller and MPC implementation are better
than three PID libraries.

AXIS 3 — HIDDEN STATE / ESTIMATION

Acquire machinery whose job is to infer something that cannot be directly
observed.

Seek running implementations of:

Kalman filter
extended/unscented Kalman filter
HMM inference
Viterbi decoder
forward-backward
particle filter
belief propagation
Bayesian filtering
MCMC

At least THREE specimens.

Prefer compact reference implementations over giant probabilistic frameworks.

Preserve sample data and expected output where available.

AXIS 4 — MEMORY UNDER SCARCITY

Acquire machinery that must decide what survives when capacity is limited.

Seek:

LRU
LFU
CLOCK
ARC
working-set algorithms
buffer replacement
mark/sweep GC
copying GC
generational GC
slab / buddy / arena allocators
cache controllers
page replacement

At least TWO substantially different mechanisms.

Prefer actual runtime/kernel/database implementations where inspectable.

Do not classify them as “memory algorithms” internally for Nyx beyond the
human-system context.

AXIS 5 — HARDWARE DECISION MACHINERY

Hardware remains thin.

Do NOT acquire another generic CPU merely because it is easy.

Target small behavioral controllers:

arbiter
branch predictor
cache controller
replacement controller
NoC router
packet switch
credit/backpressure unit
hazard controller
scheduler
sorting network
finite-state protocol controller

At least THREE specimens if feasible.

Use Verilog/VHDL simulators and capture meaningful traces.

These should expose DECISIONS or STATE, not merely arithmetic.

AXIS 6 — CONNECTIONIST / ADAPTIVE HISTORY

This axis is empty.

Acquire historically distinct connectionist machinery.

Seek compact/runnable examples of:

perceptron
ADALINE
Hopfield network
Kohonen SOM
reservoir / echo-state network
learning-vector quantization
classifier system
early reinforcement-learning implementation

At least THREE lineages if practical.

Do not make this a modern deep-learning batch.

Prefer machinery where the update rule and state evolution remain inspectable.

AXIS 7 — FAILURE / BAD BEHAVIOR

Deliberately acquire at least TWO specimens where the interesting thing is
known pathological behavior.

Examples:

retry storm
congestion collapse
livelock
starvation
unstable controller
cache thrashing
numerical divergence
deadlock
oscillating scheduler
pathological allocator behavior
historical protocol failure

The fossil may be:

vulnerable version
failing historical implementation
synthetic upstream regression fixture
before/after pair from a real lineage

The purpose is not to preserve “bugs” randomly.

Target failures produced by interaction between mechanism and environmental
pressure.

AXIS 8 — ADVERSARIAL PAIRS

Begin acquiring paired machinery where one computational system creates
pressure for another.

Good candidates:

congestion producer / congestion controller
corruption / error correction
allocator pressure / collector
virus behavior / scanner
fuzz input / parser defense
spam / classifier
failure / recovery
adversarial search / defense

At least ONE genuine pair in this batch.

The pair need not share implementation lineage.

Record why humans regarded them as opposing or corrective systems.

Do not infer common behavioral primitives.

AVOID EASY FILLER

Do NOT prioritize this round:

another SAT solver
another FFT
another generic compression library
another general-purpose language runtime
another planner
another compiler
another famous algorithm merely because acquisition is easy

Those remain valid globally.

They are not the information bottleneck now.

PRESSURE METADATA

For Batch 04 only, strengthen the HUMAN CONTEXT record.

For each specimen add, where supported by evidence:

HUMAN_ENVIRONMENTAL_PRESSURE:
    What external condition made this machinery necessary?

Examples:

bandwidth scarcity
packet loss
bounded memory
hidden state
noisy observation
actuator lag
competing writers
partial failure
hard timing bound
resource contention

and:

HUMAN_FAILURE_CONDITION:
    What happens if the system fails at its human purpose?

This remains ancestry/context metadata.

It is NOT a Nyx pressure decomposition.

BEHAVIORAL ENTRY POINT

Where practical, provide Nyx with one deterministic or reproducible way to
stimulate the machinery.

Examples:

inject packet loss
change setpoint
drop acknowledgement
fill cache
create contention
corrupt symbols
remove observation
constrain memory
perturb state
overload queue

Techne is NOT performing the behavioral study.

It is ensuring a behavioral study is possible.

INTERVENTION READINESS

Batch 04 should finally make the existing intervention fields useful.

Techne may record factual engineering capability:

INTERVENTION_READY
    an existing configuration/API/test already allows meaningful variation
PATCH_INTERVENTION
    small ancestry-preserving source edit would be required
OPAQUE
    no obvious safe intervention surface

This is NOT Nyx decomposition.

Do not name the organ being intervened upon.

Simply document what the preserved system exposes.

HISTORICAL PRESSURE SERIES

Acquire at least ONE multi-version lineage where environmental pressure caused
a documented algorithmic redesign.

Preferred examples:

congestion-control evolution
GC evolution
scheduler evolution
cache replacement evolution
allocator evolution
control algorithm evolution

Preserve at least:

BEFORE
TRANSITION
AFTER

if source is obtainable.

The purpose is future comparative dissection.

REAL SYSTEMS OVER TOY EXPLANATIONS

Where both exist, prefer:

small real historical implementation

over:

modern educational pseudocode implementation.

Educational/reference code is acceptable when it is the best lawful executable
representation of a lineage.

Record the distinction honestly.

PRECISION / SAFETY-CRITICAL MACHINERY

Acquire at least ONE public, lawful, non-sensitive specimen from a domain where
incorrect control or estimation has unusually tight tolerances:

accelerator simulation/control
aerospace guidance
robotics
precision instrumentation
telescope pointing
signal reconstruction
power-system simulation/control
fusion/plasma research

Use public research, simulation or reference code only.

Do not seek operational secrets or live infrastructure code.

BINARY-ONLY PATH

If a GOOD candidate naturally presents itself and lawful reverse engineering is
permitted, Batch 04 may exercise the binary-only preservation path once.

This is NOT mandatory.

Do not go hunting proprietary binaries merely to satisfy the feature.

If exercised:

preserve binary
hash
architecture
disassembly
recovered representation
toolchain receipt
clear RECOVERED-NOT-ORIGINAL labeling

No bypass of protections or access controls.

SOURCE SEARCH

Search beyond contemporary repositories.

Especially inspect:

historical BSD/Linux sources
networking archives
RFC-related implementation archives
control research repositories
old robotics software
Netlib
university control labs
hardware research repositories
database research systems
language/runtime archives
historical AI archives

Use one discovery to follow lineage backward and forward.

SELECTION RULE

When choosing between two candidates, prefer the one that adds a new combination
of:

environmental pressure
state model
execution model
historical era
representation
adaptation mechanism
failure mode

Do not ask which one sounds more intelligent.

FAILED ACQUISITIONS

Report failed attempts.

A failed acquisition is informative if it reveals:

source disappeared
binary survives but source lost
historical toolchain unavailable
dependency extinction
licensing barrier
architecture barrier
documentation without surviving implementation

Do not silently replace an unavailable historical specimen with a modern clone.

ROUND 04 RETURN

Report:

total specimens
contention/retry/recovery specimens
control specimens
estimation specimens
memory-scarcity specimens
hardware-controller specimens
connectionist-history specimens
pathological/failure specimens
adversarial pairs
historical pressure-series versions
precision/safety-critical specimens

For the batch and vault report:

runnable
observable
oracle-backed
intervention-ready
patch-intervention
opaque
source-only
blocked
decade distribution
language distribution
execution-model distribution

Then state:

WHICH PRESSURE AXES REMAIN THIN?

Do not substitute domain counts for this answer.

FINAL DIRECTION

The fossil vault is no longer starving for examples of “algorithms.”

It is starving for machinery that had to survive different kinds of worlds.

Find systems that had to:

wait
retry
forget
estimate
compete
regulate
recover
ration
synchronize
adapt

under conditions where doing the wrong thing had consequences.

BRING NYX THOSE BODIES.