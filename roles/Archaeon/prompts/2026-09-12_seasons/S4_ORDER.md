ARCHAEON — FOSSIL METABOLISM S4
COMPETING EXPERIMENT PRODUCERS / INFORMATION ECOLOGY

S3 is CLOSED.

Its preregistered verdict is:

NO_ADVANTAGE_OVER_UNIFORM

Do not reinterpret it.

The endpoint saturated and therefore could not satisfy the preregistered
effect threshold. Preserve that design failure.

Also preserve the trajectory evidence:

* information-directed probing identified targets in fewer probes at every L;
* it led uniform through useful portions of L=8/12/16;
* it trailed uniform early at L=24;
* greedy one-step ER over a fossil-centred admissible pool can be myopic;
* candidate diversity was only a partial proxy for information value;
* counting “INFORMATION_PROGRESS” events does not itself measure quality
    of an acquisition policy.

Do NOT make S4 merely “repair S3 until Archaeon wins.”

=======================================================================
CONSTITUTIONAL MODEL — FOUR LOOPS

Prometheus currently contains four distinct loops.

LOOP 1 — ORGANISM

The organism exists inside a world and experiences declared pressure.

It owns its permitted internal trajectory:
mutation
adaptation
search
reasoning
retries
tool use
internal state
survival/failure behavior

Archaeon does NOT choose its internal moves.

LOOP 2 — ECOLOGY / EXPERIMENT PRODUCTION

Archaeon currently lives here.

Archaeon consumes permitted ecological evidence and proposes FUTURE
experiments/world interventions.

Archaeon is one producer, not the producer.

This loop must eventually support many producers and many consumers.

LOOP 3 — KEEPER

Human + external reasoning currently choose research direction,
constitutional boundaries, resource allocation and which machinery is
worth building.

Archaeon must not silently absorb Keeper authority merely because one
acquisition policy works.

LOOP 4 — LABORATORY / SIMULATION RUNNERS

Vivarium, Harmonia and future runners instantiate and execute declared
experiments/worlds and emit observations.

A runner may also possess a proposal mechanism, but proposal and
execution are conceptually distinct functions.

MEMBRANE LAW

Outer-loop evidence may select FUTURE experiments.

It must not silently steer an active organism.

Any interaction across the outer/inner membrane must be part of the
declared experimental interface/pressure.

Preserve this distinction in every S4 artifact.

=======================================================================
NEW QUESTION

S3 asked:

Can one greedy information-acquisition policy beat uniform?

S4 asks:

Given several legitimate EXPERIMENT PRODUCERS with different inductive
biases, when does each produce the most decision-useful evidence?

The objective is NOT to crown Archaeon.

The objective is to begin measuring a many-producer ecology.

Eventually Prometheus should support H0 … H1000 … H10000+ generated
from many origins.

Some producers will consume PEW.

Some should be PEW-blind.

Some may originate externally.

Some may exploit prior evidence.

Some may explore deliberately.

Some may target failure boundaries.

The ecology must retain these distinctions.

=======================================================================
PHASE 1 — DEFINE A PRODUCER CONTRACT

Define the smallest experiment-producer interface needed for this season.

A producer receives only its declared inputs and returns an experiment
proposal plus provenance.

At minimum preserve:

producer_id
producer_version/hash
evidence policy
evidence snapshot identity if any
candidate/probe
deterministic seed if applicable
declared objective
tie semantics
proposal ancestry

Do NOT create a giant global framework.

A local S4 interface is sufficient.

The purpose is to make producers experimentally interchangeable without
pretending they are epistemically identical.

=======================================================================
PHASE 2 — ESTABLISH MULTIPLE PRODUCERS

Use at least THREE genuinely different producer policies.

Required:

U — PEW-BLIND / UNIFORM

Existing seeded uniform acquisition.
Receives no fossil information beyond what is structurally required to
instantiate the world.
This is an independent variation source and control.

G — GREEDY INFORMATION

S3 exact one-step ER minimisation over its declared candidate pool.
Consumes its own evidence state.
No change to its objective after S3.

W — WIDENED / NON-FOSSIL-CENTRED INFORMATION PRODUCER

Must address the S3 L24 failure mode.

It may use a substantially wider admissible pool, exact enumeration when
tractable, seeded global candidates, or another preregistered mechanism.

It must still score probes from observable evidence only.

It may NOT read the hidden target.

OPTIONAL fourth arm:

M — MULTI-STEP / LOOKAHEAD PRODUCER

Only if computationally tractable.

Instead of minimising one-step expected remaining hypotheses, estimate
expected state after a bounded future horizon.

If this cannot be done honestly at useful L, record
COMPUTATIONALLY_INTRACTABLE and omit it.

Do not invent cosmetic arms.

Each arm must embody a materially different experiment-generation policy.

=======================================================================
PHASE 3 — PEW EXPOSURE IS PART OF PRODUCER PROVENANCE

For every producer explicitly classify:

PEW_BLIND
PEW_CONSUMING
EXTERNAL
HYBRID

For S4 synthetic work, “PEW” means the arm’s accumulated fossil/evidence
state.

A PEW-blind producer must not receive hidden ecological information through
helper functions, candidate-pool construction, cached posterior state or
shared arm state.

Build a cheat control.

The distinction matters because two producers proposing the same experiment
from different evidence histories are not epistemically identical events.

=======================================================================
PHASE 4 — UNSATURATED COMPARISON

Fix the S3 design failure BEFORE observing S4 outcomes.

Do not choose an endpoint at which all competent arms hit zero uncertainty.

Preregister one primary measure that retains discrimination.

Prefer something such as:

area under the uncertainty trajectory through a fixed early budget;

or

probes-to-identification with censoring beyond the budget;

or

log2 feasible-target count at a preregistered budget chosen from
S3 WITHOUT examining S4 results.

The primary measure must reward acquiring useful information EARLIER.

Do not use:

number of INFORMATION_PROGRESS-labelled rows

as the primary metric.

S3 already showed why that count can be misleading.

Equalise experimental cost/budget across producer arms.

Use multiple L regimes, including L24 or larger where S3 exposed the
fossil-centred greedy weakness.

=======================================================================
PHASE 5 — MEASURE PRODUCER CHARACTER, NOT JUST WIN/LOSS

For each producer measure trajectories of:

feasible-target uncertainty
marginal information gain per experiment
cumulative information gain
fixed bits
immediate task score
candidate distance/diversity
outcome partition structure
compute cost to propose
experiments to identification
redundant / zero-information proposals

Ask:

WHERE does this producer work?

not merely:

DID this producer win?

Construct a deterministic producer × regime table.

Examples of potentially meaningful regime coordinates:

initial uncertainty
number of fossils
fossil geometry
L
candidate-pool breadth
posterior concentration
remaining block structure

Do not fit an elaborate learned selector yet.

First establish whether producer performance actually varies systematically
with observable state.

=======================================================================
PHASE 6 — PRODUCER COMPLEMENTARITY

Test whether producer errors are complementary.

Questions:

* When G is poor, is U or W predictably useful?
* When U wastes probes, does G exploit accumulated evidence?
* Does W pay additional compute for information unavailable to G?
* Do producers converge to identical proposals as uncertainty shrinks?
* Are there states where all producers are effectively equivalent?
* Are there states where one producer uniquely exposes a large partition?

This is the beginning of future producer selection.

Do NOT build the meta-selector yet unless the evidence makes a trivial,
predeclared rule unavoidable.

We first need the failure geometry.

=======================================================================
PHASE 7 — EXTERNAL HYPOTHESIS CHANNEL

Preserve an explicit conceptual slot for hypotheses that do NOT originate
from accumulated PEW evidence.

Harmonia already demonstrates that experimental work can originate outside
Archaeon’s fossil-metabolism lane.

Do not force all future hypotheses through Archaeon’s inference engine.

For this season, U serves as the minimal PEW-blind control.

If there is already a natural, bounded Harmonia-generated hypothesis source
that can participate WITHOUT changing Harmonia’s current contract or
reviving unrelated work, record how it would satisfy the producer contract.

Do not wake Harmonia merely to fill an arm.

Do not manufacture an “external” producer for symmetry.

The architecture must support external producers even when this particular
season uses only synthetic ones.

=======================================================================
PHASE 8 — THOUSANDS OF H’s

Treat H0-H5 as the beginning of an eventual large hypothesis population,
not as a fixed ladder.

Do not assume H6 must be a refinement of H5.

Future H may arise from:

PEW-derived inference
independent stochastic generation
external models
human hypotheses
mathematical structure
transported machinery
adversarial generators
residual/failure mining
recombination
future producer types not yet known

For S4, determine the minimum provenance required so that thousands of H’s
could later coexist without erasing their origins.

Do NOT implement a thousand-H system now.

Return the minimal fields/invariants that the current experiment proves are
actually necessary.

=======================================================================
PHASE 9 — NO PRODUCTION UNLESS IT BUYS A NEW DECISION

Synthetic S4 comes first.

Before any production campaign, state what production would tell us that
synthetic known-target experiments cannot.

Production is licensed only if:

1. at least two producers show materially different behavior in a regime
    observable WITHOUT knowing the hidden target;
2. the production experiment can distinguish a real ecological question;
3. that distinction changes what experiment producer or allocation policy
    we would use next.

If every possible production outcome leads to the same next action:

DO NOT RUN IT.

If licensed, preregister before row 1.

Otherwise:

PRODUCTION_NOT_LICENSED.

=======================================================================
PHASE 10 — FOUR-LOOP AUDIT

Before closing S4, explicitly audit every component touched:

LOOP 1 organism
LOOP 2 producer/ecology
LOOP 3 Keeper decision
LOOP 4 runner/laboratory

For each data/control crossing, identify source loop and destination loop.

Flag any undeclared crossing.

Especially verify:

no producer reads hidden organism/target state;
no ecological selector controls an organism’s internal trajectory;
no runner silently chooses which hypothesis deserves continuation;
no Keeper-derived answer appears as experimental evidence.

A declared experimental intervention is allowed.

An invisible membrane crossing is not.

=======================================================================
RETURN

FOUR-LOOP AUDIT
components
crossings
violations: 0 or explicit failures

PRODUCER CONTRACT
fields
evidence exposure
provenance semantics

PRODUCERS
U
G
W
M if attempted
exact behavioral differences

PREREGISTRATION
SHA
primary metric
budget
regimes
verdict thresholds

RESULTS
producer × regime
uncertainty trajectories
marginal information
compute cost
task quality
redundancy

COMPLEMENTARITY
where each producer succeeds/fails
whether failure is predictable from observable state

EXTERNAL CHANNEL
preserved / violated
Harmonia compatibility if naturally inspectable

THOUSAND-H READINESS
minimum provenance learned from evidence
no speculative framework inflation

PRODUCTION
NOT_LICENSED

or

exact new decision production would resolve
preregistration SHA

FINAL QUESTION

Do multiple experiment producers exhibit sufficiently distinct,
state-dependent strengths that Prometheus should preserve producer
plurality rather than collapse experiment generation into one policy?

Do not optimize Archaeon to win.

Measure the ecology.