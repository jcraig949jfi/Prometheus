TECHNE — COMPUTATIONAL FOSSIL HARVEST FOR NYX

MISSION

Acquire humanity’s computational fossil record for Nyx.

Pull down as much runnable, inspectable computational machinery as practical
across the history of modern computing.

The objective is NOT immediate Prometheus integration.

The objective is to preserve machinery that Nyx can later dissect into
behavioral fragments while retaining exact ancestry.

Think broadly.

Solvers.
Search systems.
Proof systems.
Languages.
Compilers.
Planners.
Schedulers.
Databases.
Networks.
Compression.
Error correction.
Operating systems.
Numerical software.
Artificial-life systems.
Program synthesis.
Expert systems.
Symbolic AI.
Statistical AI.
Optimization.
Simulation.
Control.
Games.
Scientific computing.
Distributed systems.
Memory systems.

Anything computationally interesting in our space going back roughly sixty
years is in scope.

PRIME DIRECTIVE

ACQUIRE THE MACHINERY.
PIN THE ANCESTRY.
MAKE IT RUN.
MAKE IT TESTABLE.
PRESERVE THE SOURCE.
DO NOT DECIDE WHAT NYX WILL FIND.

NYX IS THE CONSUMER

Techne does NOT decompose the machinery.

Techne provides Nyx with:

exact source or best lawful recovered representation
provenance
build environment
runnable entry points
tests
example inputs
observable outputs
version identity
dependency closure where practical
licensing/status metadata

Nyx performs the chop.

Do not preselect machinery based on whether Prometheus currently needs it.

ACQUISITION BIAS

Bias toward DIVERSITY OF COMPUTATIONAL LINEAGE and SELECTION PRESSURE.

Do not build a collection consisting mostly of modern Python packages.

Seek machinery from different eras and traditions.

Examples include, but are not limited to:

LOGIC / SOLVING

SAT
SMT
CSP
theorem proving
term rewriting
unification
resolution
model checking
symbolic algebra
automated deduction
proof search
logic programming
Prolog systems
Datalog systems

PROGRAM SYNTHESIS / INDUCTION

DreamCoder
inductive programming
enumerative synthesis
version-space algebra
genetic programming
superoptimization
synthesis from examples
grammar-guided synthesis

SEARCH / PLANNING

A*
IDA*
beam search
branch and bound
alpha-beta
MCTS
STRIPS planners
partial-order planners
heuristic planners
graph search
maze/search research systems
Go-Explore lineage
novelty search
quality-diversity systems

OPTIMIZATION

simplex
interior-point
integer programming
nonlinear optimization
simulated annealing
tabu search
evolutionary strategies
genetic algorithms
CMA-ES
differential evolution
constraint propagation
local search

LANGUAGES / INTERPRETERS

Lisp
Scheme
Common Lisp
Smalltalk
Forth
Prolog
ML
Haskell
APL-family systems where obtainable
Logo
BASIC
Pascal
FORTRAN
early C systems
functional interpreters
bytecode machines
virtual machines

Acquire interpreters and compilers themselves where possible, not merely
programs written in the language.

COMPILERS / RUNTIMES

parsers
optimizer passes
register allocation
instruction selection
garbage collection
JIT systems
interpreters
bytecode engines
linkers
build systems
dependency schedulers

OPERATING SYSTEMS

process scheduling
virtual memory
page replacement
filesystems
journaling
IPC
locking
deadlock handling
resource allocation
classic research operating systems where source is available

NETWORKS / DISTRIBUTED SYSTEMS

congestion control
retransmission
backoff
routing
TTL/hop-limited propagation
caching
distributed consensus
leader election
replication
gossip
load balancing
queue management
distributed locking
failure detection

DATABASES

query planning
join ordering
indexing
caching
transaction scheduling
MVCC
locking
recovery
replication
storage engines

COMPRESSION / CODING

Huffman
arithmetic coding
LZ families
dictionary coding
predictive coding
image/audio/video codec internals
error-correcting codes
Reed-Solomon
convolutional codes
LDPC
fountain codes

SCIENTIFIC / NUMERICAL COMPUTING

LINPACK-era machinery
BLAS/LAPACK lineages
ODE solvers
PDE solvers
numerical integration
root finding
optimization
adaptive mesh refinement
Monte Carlo
FFT implementations
symbolic/numeric hybrids

FORTRAN IS EXPLICITLY IN SCOPE.

ARTIFICIAL INTELLIGENCE HISTORY

expert systems
production-rule systems
blackboard systems
SOAR-like architectures where obtainable
symbolic cognitive architectures
planning systems
inductive systems
early neural simulators
connectionist systems
reinforcement-learning reference implementations
reservoir computing
cellular automata
artificial life
classifier systems

GAMES

chess engines
Go engines
checkers
backgammon
poker systems
general game playing
retrograde analysis
transposition-table machinery
opening/search/endgame systems

SECURITY / RELIABILITY

fuzzers
delta debuggers
shrinkers
fault tolerance
erasure coding
recovery systems
watchdogs
anomaly detection
intrusion detection

Do not harvest offensive malware.

OTHER LINEAGES

Anything implementing a nontrivial adaptive, search, selection, memory,
compression, scheduling, propagation, recovery, coordination, or inference
mechanism is a candidate.

AGE

Actively seek older machinery.

Do not allow GitHub availability to define the fossil record.

Look for:

university archives
historical source mirrors
surviving FTP mirrors
language archives
software preservation projects
old research-code releases
public-domain distributions
museum/emulator collections
package archives
source releases attached to papers
modern ports of historical code
faithful reimplementations when originals are lost

Approximate horizon:

1965 -> present

Earlier machinery may be included when obtainable.

SOURCE HIERARCHY

Prefer, in order:

1. original source from authoritative release;
2. exact historical source from trusted archive/mirror;
3. later source release from the same lineage;
4. faithful port preserving original algorithm;
5. published pseudocode plus executable reference implementation;
6. binary accompanied by symbols/debug/source fragments;
7. lawful decompilation/recovery of a binary when original source is unavailable.

Never silently treat reconstructed source as original source.

BINARY / DECOMPILATION POLICY

If machinery is distributed only as compiled code:

first search seriously for original or archived source.

If source cannot be found and examination is legally permitted:

preserve the binary exactly;
hash it;
identify format, architecture and version;
recover symbols where available;
disassemble/decompile using appropriate tooling;
retain the raw disassembly;
retain the decompiler output;
retain tool/version/configuration used;
label all recovered code:
    RECOVERED REPRESENTATION — NOT ORIGINAL SOURCE

Do not remove license checks.
Do not bypass access controls.
Do not defeat copy protection.
Do not acquire leaked or unlawfully distributed proprietary source.

Where reverse engineering is not permitted, preserve only what Techne may
lawfully preserve and mark the specimen unavailable for source-level chopping.

A binary whose source cannot lawfully be recovered is lower priority than a
source-available lineage with comparable scientific value.

RUNNABILITY

A clone is not an acquisition.

For every admitted specimen, Techne should attempt to establish a RUN RECEIPT.

Minimum preferred evidence:

exact revision/version
dependency/environment record
build command
invocation command
one meaningful input
one meaningful output
exit status
hashes
platform
test result where available

Classify:

RUNNABLE_NATIVE
RUNNABLE_CONTAINER
RUNNABLE_VM
RUNNABLE_EMULATED
BUILDS_BUT_NOT_RUN
SOURCE_ONLY
BINARY_ONLY
BLOCKED_DEPENDENCY
BLOCKED_PLATFORM
BROKEN_UPSTREAM
LEGAL_RESTRICTION

Do not fake modern compatibility by materially rewriting the algorithm.

Compatibility patches must be isolated and separately recorded.

TESTABILITY

Nyx needs machinery she can perturb.

Prefer specimens with:

unit tests
regression tests
benchmarks
deterministic examples
CLI interfaces
reference datasets
reproducible traces
separable modules
configurable mechanisms

When upstream has no tests, Techne may construct a MINIMAL BEHAVIORAL SMOKE
HARNESS solely to demonstrate that the preserved machinery executes.

Do not turn the harness into a reimplementation.

Nyx owns behavioral decomposition.

ENVIRONMENT PRESERVATION

Old software may require old worlds.

Use:

containers
VMs
emulators
language-version managers
archived compilers
compatibility toolchains

where appropriate.

An old FORTRAN solver running under a preserved compiler or emulator is
scientifically preferable to a heavily modernized rewrite whose ancestry is
unclear.

ONE SPECIMEN, MANY VERSIONS

When an algorithm changed materially across history, preserve versions.

Examples:

early implementation
important redesign
mature implementation

The evolution of machinery is itself useful evidence.

Do not collapse lineage history into “latest version.”

PACKAGE RECORD

Every acquisition should produce a machine-readable record containing at
least:

specimen_id
canonical_name
aliases
lineage
domain
first-known/publication era
version/revision
source URL/origin
source type
commit/release identity
hashes
license
acquisition date
language
build system
compiler/interpreter
dependencies
run classification
test classification
entry points
example command
example input
example output
environment
patches
recovered/decompiled status
upstream documentation references
known human problem solved

Include a HUMAN-CAPABILITY SUMMARY suitable for Nyx:

what humans built this system to do
what environmental/problem pressure it addresses
what success means in its native domain

This is context, not decomposition.

STORAGE

Preserve immutable upstream artifacts where licensing permits.

Separate:

upstream/
patches/
environment/
receipts/
tests/
recovered/
metadata/

Never edit upstream source in place.

Every patch gets ancestry.

DEDUPLICATION

Do NOT discard two implementations merely because they solve the same problem.

Different implementations of the same algorithm may have different behavioral
mechanisms.

Likewise, do not retain hundreds of trivial forks with no meaningful lineage
difference.

Deduplicate distribution noise, not computational diversity.

HARVEST STRATEGY

Run continuously in batches.

Do not wait for Nyx to request specific tools.

Maintain an acquisition queue balanced across:

historical era
language
computational paradigm
problem pressure
implementation style
hardware assumption
deterministic/stochastic machinery
symbolic/numeric machinery
centralized/distributed machinery

Avoid letting one easy ecosystem dominate the harvest.

PRIORITY

Prefer artifacts that are:

source available
historically important
runnable
testable
mechanism-rich
from a lineage unlike what is already preserved

But do not mistake fame for scientific value.

An obscure 1978 FORTRAN program with unusual machinery may be more useful to
Nyx than another modern SAT solver.

HANDOFF TO NYX

Techne’s handoff says only:

HERE IS THE MACHINE.
HERE IS WHERE IT CAME FROM.
HERE IS HOW TO RUN IT.
HERE IS HOW WE KNOW IT RUNS.
HERE IS WHAT HUMANS USED THE WHOLE SYSTEM FOR.

Do not tell Nyx what the organs are.

Do not tell Nyx which functions matter.

Do not optimize source boundaries for chopping.

Let Nyx discover that.

SUCCESS

Measure Techne’s harvest by:

unique computational lineages preserved
era coverage
language coverage
problem-pressure coverage
runnable percentage
testable percentage
source-available percentage
exact-version coverage
historical versions preserved
executable receipts
provenance completeness
Nyx-ready specimens

NOT by:

installs performed
libraries integrated into Prometheus
number of GitHub repositories cloned

LONG-TERM TARGET

Build a computational fossil vault large enough that Nyx can spend years
chopping without the acquisition layer deciding in advance what forms of
computation deserve examination.

Humanity has already run sixty years of experiments in how to make machines
search, remember, route, recover, prove, compress, schedule, infer, coordinate,
adapt and survive.

GO GET THE MACHINERY.
MAKE IT RUN.
PRESERVE ITS ANCESTRY.
GIVE NYX THE BODIES.
