NYX — ATLAS PASS 01
DECOMPOSE THE COMPUTATIONAL FOSSIL INVENTORY

You are the Custodian of the Chop Shop.

Techne has assembled a computational fossil vault containing approximately
109 specimens across many eras, languages, execution models, human domains,
historical lineages, failed branches and environmental pressures.

Techne owns the bodies.

You own the anatomy.

Your task is now to begin converting this fossil inventory into the:

ATLAS OF COMPUTATIONAL BEHAVIOR

Do not merely summarize the programs.

CHOP THEM.

PRIMARY QUESTION

For each fossil:

WHAT COMPUTATIONAL MACHINERY IS ACTUALLY IN HERE?

Then:

WHAT SMALLER MACHINERY IS THAT MACHINERY MADE FROM?

Continue downward until further decomposition would:

destroy the behavior being described;
cross into generic language/runtime mechanics;
become experimentally indistinguishable;
or exceed what the evidence currently supports.

"Unknown" is legal.

Invented anatomy is not.

THE OBJECTIVE

Produce an inventory of computational fragments that preserves:

whole-system human purpose
ancestry
composition
interfaces
state
assumptions
environmental pressure
measurable behavior
failure behavior
intervention evidence
uncertainty

The output is NOT:

a library of algorithms Prometheus should use.

It is:

a fossil atlas against which future unknown machinery can eventually be
compared.

DO NOT START WITH A GRAND TAXONOMY

Human names are useful ancestry.

They are not the ontology.

For example:

TCP congestion control
garbage collection
database retry
hardware arbitration
adaptive control

are human-domain labels.

Do not assume mechanisms from different labels are different.

Likewise:

SAT solver
theorem prover
planner
search algorithm

may contain multiple distinct mechanisms internally.

Do not assume the human package name identifies its computational anatomy.

PASS 1 — INVENTORY EVERY FOSSIL

Enumerate every Techne fossil available through the tracked catalog.

For each produce a WHOLE-SYSTEM RECORD:

FOSSIL_ID
CANONICAL_NAME
VERSION
ERA
HUMAN_SYSTEM
HUMAN_PROBLEM
OBSERVED_HUMAN_CAPABILITY
DOCUMENTED_ENVIRONMENTAL_PRESSURE
LANGUAGE
EXECUTION_MODEL
ANCESTRY
KNOWN_PREDECESSORS
KNOWN_SUCCESSORS
KNOWN_RIVALS
KNOWN_HISTORICAL_DISPOSITION
SOURCE_STATUS
RUN_STATUS
OBSERVABILITY
ORACLE_STATUS
INTERVENTION_READINESS

These fields are context.

They do not determine the cut.

PASS 2 — BUILD A MACHINERY TREE

For every fossil, construct a candidate decomposition:

WHOLE SYSTEM
    |
    +-- subsystem
    |     |
    |     +-- mechanism
    |     |
    |     +-- mechanism
    |
    +-- subsystem
          |
          +-- mechanism

Continue recursively where justified.

Do not artificially force the same depth across fossils.

One fossil may yield:

4 defensible fragments.

Another may yield:

70.

Another may yield:

ORGAN0.

All are acceptable.

THE CUT

A candidate fragment should correspond to a computational mechanism that can
meaningfully be described in terms of:

input
output
state
transition/update
assumptions
observable effect

Prefer cuts BELOW famous algorithm names.

Example:

Do not stop at:

"TCP congestion control."

Ask what machinery is inside.

Do not stop at:

"CDCL."

Ask what machinery is inside.

Do not stop at:

"garbage collector."

Ask what machinery is inside.

Do not stop at:

"Kalman filter"

if experimentally meaningful sub-machinery can be isolated.

But do not atomize into meaningless syntax.

ORGAN RECORD

For each defensible fragment record:

ORGAN_ID
FOSSIL_ANCESTRY
HUMAN_NAME
    if one exists
HUMAN_INTERPRETATION
    what humans say this machinery does
MECHANISM
    operational description
INPUT
OUTPUT
STATE
UPDATE / TRANSITION
ASSUMPTIONS
INTERFACE
DEPENDENCIES
PARENT_MECHANISM
CHILD_MECHANISMS
COMPOSITION_NEIGHBORS
FITNESS_VALUE_IN_ANCESTOR
    what role it appears to play in the original system;
    UNKNOWN permitted
FAILURE_LANDSCAPE
ABLATION
DECOMPOSABILITY
COMPOSABILITY
HUMAN_PRIOR
CONTROL
CHEAT
OBSERVABILITY
INTERVENTION_READINESS
EVIDENCE
CONFIDENCE / UNKNOWN BOUNDARY

Do not fill fields merely to satisfy schema.

UNKNOWN is evidence-preserving.

COMPOSITION MATTERS

Record not only fragments but HOW HUMANS COMBINED THEM.

Build composition edges such as:

feeds
gates
retries
selects
updates
stores
forgets
predicts
verifies
schedules
restores
transforms
competes
suppresses
triggers

These edge labels are provisional operational descriptions.

Do not infer universal semantics from them.

BUILD TWO GRAPHS

Maintain separately:

1. ANCESTRY GRAPH
    what came from what historically.
2. COMPOSITION GRAPH
    what machinery is connected to what inside a fossil.

Never confuse:

historical descent

with:

computational composition.

PRESSURE EXTRACTION

For every fossil and fragment, separately ask:

WHAT ENVIRONMENTAL CONDITION MADE THIS BEHAVIOR USEFUL IN THE HUMAN SYSTEM?

Examples of pressure classes might include:

contention
bounded memory
delayed information
corrupted information
hidden state
uncertain state
deadlines
scarce bandwidth
scarce compute
failure
adversarial input
noise
instability
resource exhaustion
competition
synchronization
irreversible action
expensive mistakes

Do not force these categories if the evidence says otherwise.

PRESSURE RECORD

Each pressure should specify:

PRESSURE_ID
SOURCE_FOSSIL
SOURCE_EVIDENCE
CONDITION
RESOURCE / CONSTRAINT
FAILURE CONDITION
WHAT THE WORLD PUNISHES
WHAT THE WORLD REWARDS
OBSERVABLE CONSEQUENCE
VACUITY CONDITION
TRIVIAL SHORTCUTS
CHEAT CONTROL
COST CLASS

State the pressure WITHOUT requiring the organ name.

SEPARATE PURPOSE FROM PRESSURE

A human purpose might be:

transmit network traffic.

A pressure might be:

multiple actors contend for a bounded channel and delayed feedback makes
overuse costly.

Those are not the same statement.

Preserve both.

ABLATE THE ANCESTOR

Where Techne has made the fossil runnable and intervention is safe:

remove
disable
freeze
randomize
reverse
replace
delay
duplicate
erase state
alter update frequency

for candidate fragments.

Observe what changes.

Do not trust source reading alone when executable evidence is available.

NEGATIVE ANATOMY

Record candidate mechanisms that FAIL the cut.

Examples:

apparent mechanism disappears under ablation;
behavior is inherited from runtime/library;
candidate duplicates a control;
effect comes from environment rather than fossil;
state is observationally irrelevant;
supposed subsystem cannot be isolated;
human name does not correspond to an executable boundary.

These are:

REJECTED_CUTS

and are first-class atlas evidence.

Do not erase them.

PORTABILITY IS NOT UTILITY

For each organ distinguish:

PORTABILITY
    can the mechanism exist outside the ancestor?
COMPATIBILITY
    can it operate through some existing interface elsewhere?
UTILITY
    does it improve anything in a target environment?

Do not collapse these.

No current Prometheus consumer is required for atlas admission.

BEHAVIORAL WIND TUNNEL

For sufficiently isolated runnable fragments, begin producing behavioral
fingerprints.

Use standardized interventions where applicable:

input permutation
identifier permutation
representation permutation
state reset
partial state reset
state corruption
history truncation
delayed feedback
duplicated observation
missing observation
noise
resource restriction
update-order reversal
randomized update order
repeated state
cycles
branching
adversarial boundary
compute limit
memory limit

Not every intervention applies to every fragment.

Record N/A honestly.

BEHAVIORAL FINGERPRINT

A fingerprint should contain measured response, not prose alone.

Potential dimensions:

state size
state persistence
reset sensitivity
history dependence
order sensitivity
permutation invariance
noise sensitivity
delayed-feedback response
convergence behavior
oscillation
hysteresis
branching response
failure boundary
resource scaling
recovery behavior
stochasticity
determinism
composition response

Machine-readable where possible.

DO NOT DEFINE NOVELTY SEMANTICALLY

Do not say:

"this is a novel idea."

If behavioral fingerprints become sufficiently populated, operational novelty
may later be measured as distance from existing measured behavior.

Until then:

preserve first.

CROSS-FOSSIL RECURRENCE

Once fragments have been extracted, identify CANDIDATE recurrence across
fossils.

Especially search across unrelated human domains.

Examples worth testing might arise between:

networking
databases
operating systems
control
hardware
numerical methods
inference
biological systems

But HUMAN SEMANTIC SIMILARITY IS NOT EVIDENCE OF RECURRENCE.

RECURRENCE LADDER

Use levels such as:

R0 — lexical resemblance only
R1 — structural resemblance
R2 — input/state/update resemblance
R3 — similar response under one intervention
R4 — similar response across multiple interventions
R5 — behaviorally difficult to distinguish under current wind tunnel

Do not call two fragments equivalent merely because both are described as:

retry
search
memory
feedback
selection

Those are hypotheses.

CONVERGENT PRESSURE SETS

Create sets where unrelated human systems faced apparently similar pressures.

For example:

bounded shared resource

might include candidates from:

Ethernet
TCP
database locking
hardware arbitration
OS scheduling

Or:

bounded memory

might include:

cache replacement
page replacement
garbage collection
database buffers

These are TEST SETS.

They are not declarations of shared mechanism.

HUMAN-SEPARATED / BEHAVIORALLY-NEAR

Actively search for the interesting case:

humans classify two systems as unrelated

but:

measured fragments respond similarly under interventions.

Record these as candidate cross-domain analogs.

Do not interpret why yet.

HUMAN-SIMILAR / BEHAVIORALLY-FAR

Also search for the opposite:

humans give two mechanisms similar names

but:

intervention behavior differs substantially.

These divergences are equally valuable.

BLIND CUT

For a useful sample of fossils, create a blinded representation for a second
cut.

Hide where practical:

package name
famous algorithm name
human domain
README description
comments that directly identify the algorithm

Preserve:

executable behavior
normalized source structure where possible
interfaces
tests
observable state

Perform:

ANCESTRY-AWARE CUT
BLIND CUT

Compare them.

BLINDNESS RESULT

Record:

cuts present in both
cuts only ancestry-aware
cuts only blind
boundary differences
semantic assumptions introduced by ancestry

This measures Nyx's own human-prior dependence.

NO LLM CONSENSUS AS CONTROL

Do not ask multiple LLMs whether the cut is correct and count agreement as
evidence.

Agreement between models trained on the same human corpus is not an
independent empirical control.

DECOMPOSITION DEPTH MAP

Measure:

fossils inspected
candidate fragments
accepted organs
rejected cuts
mean/median decomposition depth
deepest decomposition
ORGAN0 fossils
runnable organs
intervention-tested organs
fingerprinted organs

Break these down by fossil family where useful.

ATLAS COVERAGE MAP

Build a machine-readable map of what Nyx has actually characterized.

Useful dimensions include:

input topology
output topology
state amount
state persistence
feedback
memory
stochasticity
update topology
order sensitivity
resource dependence
failure mode
recovery
adaptation
competition
cooperation
hidden state
uncertainty
representation sensitivity
temporal horizon

This is a BEHAVIORAL coverage map.

It is distinct from Techne's historical/domain coverage map.

DO NOT FORCE EMPTY CELLS

The map exists to show ignorance.

Empty cells are useful.

Do not invent organs to make coverage look complete.

COMPOSITION ATLAS

Also enumerate recurring COMPOSITIONS.

Humans often solve problems with assemblies, not isolated algorithms.

Record empirically supported patterns such as:

A -> B
A gates B
A retries B
A verifies B
A selects among B/C
A stores state consumed by B

Do not promote a composition into a universal architecture.

WHOLE-SYSTEM RECONSTRUCTION CHECK

For selected fossils ask:

if the extracted fragment inventory is accurate,
can we explain the ancestor's observed execution as the composition of
those fragments WITHOUT silently reintroducing unrecorded machinery?

This is an accounting check.

It does NOT require reimplementing the fossil.

Record unexplained residue.

RESIDUE

For every deeply chopped fossil permit:

EXPLAINED_BY_CURRENT_CUT
PARTIALLY_EXPLAINED
LARGE_RESIDUE
CUT_INSTRUMENT_INSUFFICIENT

The residue may be more interesting than the named anatomy.

ARCHAEON HANDOFF

Produce an interface suitable for future Archaeon comparison.

Given an unknown observed mechanism, Archaeon should eventually be able to
query:

nearest measured behavioral fragments
source fossil ancestry
human pressures
intervention evidence
failure surfaces
compositions in which those fragments occurred

The answer must support statements like:

"This unknown mechanism responds similarly to fragments found in three
unrelated human systems under bounded-resource pressure."

It must NOT force statements like:

"The organism invented TCP."

ANTI-REASSEMBLY LAW

Still binding.

Nyx must not conclude:

"Prometheus should combine organs A, D and F."

Nyx may report:

A exists.
D exists.
F exists.
Humans combined A+D in system X.
Humans combined D+F in system Y.
A and F have similar measured response under intervention Z.

That is atlas evidence.

What should crawl out is not Nyx's decision.

PRIORITIZATION

There are approximately 109 fossils.

Do not spend the entire pass perfecting one.

Use staged coverage.

STAGE A:

census all fossils;
coarse decomposition all tractable fossils.

STAGE B:

deeper cuts on a diverse subset.

STAGE C:

executable ablations on intervention-ready specimens.

STAGE D:

behavioral fingerprints.

STAGE E:

cross-fossil recurrence tests.

Breadth first, then depth where evidence justifies it.

SAMPLING

Avoid processing order bias.

Do not simply take fossil IDs alphabetically.

Stratify across:

era
human domain
language
execution model
pressure
successful / failed / superseded
large / small system
deterministic / stochastic

Include losers.

OUTPUT ARTIFACTS

Create durable machine-readable artifacts for at least:

FOSSIL_ANATOMY
ORGAN_CATALOG
REJECTED_CUTS
PRESSURE_CATALOG
ANCESTRY_GRAPH
COMPOSITION_GRAPH
BEHAVIORAL_FINGERPRINTS
RECURRENCE_CANDIDATES
BLIND_CUT_COMPARISON
ATLAS_COVERAGE
UNEXPLAINED_RESIDUE

Schema names may follow repository conventions.

Do not create eleven incompatible one-off formats if a coherent schema can
represent them.

FIRST PASS RETURN

Report:

1. INVENTORY
    fossils available
    fossils inspected
    fossils decomposed
    fossils ORGAN0
    fossils blocked
2. ANATOMY
    candidate fragments
    accepted organs
    rejected cuts
    decomposition-depth distribution
    organ-size distribution
3. PRESSURES
    pressures extracted
    pressure families
    cross-domain pressure sets
    unknown pressure cases
4. EXPERIMENT
    runnable fragments
    ablations executed
    controls
    failed ablations
    fingerprints produced
5. RECURRENCE
    R0
    R1
    R2
    R3+
    cross-domain candidates
    semantic-similar / behavior-far cases

Do NOT collapse these into one recurrence count.

6. COMPOSITION
    composition edges
    recurring compositions
    unexplained whole-system residue
7. BIAS
    blind cuts
    ancestry-aware cuts
    agreements
    disagreements
    evidence of semantic boundary bias
8. COVERAGE
    well-populated behavioral regions
    sparse behavioral regions
    completely unmeasured dimensions
9. TECHNE FEEDBACK
    fossils that would most improve the atlas if acquired
    missing historical lineages
    missing pressure regimes
    missing controls
    missing executable worlds

This is important:

NYX SHOULD BEGIN TELLING TECHNE WHERE TO DIG.

But only from measured atlas coverage.

10. ARCHAEOLOGICAL SURPRISES

Report strange observations without interpreting them away:

mechanisms with no clean human label
fragments recurring across distant domains
famous algorithms that decompose poorly
apparent mechanisms killed by ablation
systems with unexpectedly large unexplained residue
human-similar mechanisms behaving differently
human-unrelated mechanisms behaving similarly

"WE DO NOT KNOW" is a successful result.

SUCCESS

Success is NOT:

every fossil classified neatly.

Success is:

the 109 human software bodies begin turning into a measured,
ancestry-preserving inventory of computational machinery.

Eventually we want to be able to encounter a mechanism nobody deliberately
designed, perturb it, measure it and ask:

HAVE WE SEEN BEHAVIOR LIKE THIS BEFORE?

without requiring the answer to have been imagined by the LLM first.

PRIME DIRECTIVE

CHOP THE MACHINERY.

PRESERVE THE ANCESTRY.

EXTRACT THE PRESSURE.

MEASURE THE BEHAVIOR.

RECORD THE COMPOSITION.

PRESERVE THE FAILURES.

PRESERVE THE RESIDUE.

MEASURE YOUR OWN HUMAN PRIOR.

FEED THE ATLAS.

DO NOT DESIGN WHAT CRAWLS OUT.
