PROMETHEUS — LUDUS REACTIVATION / BASE-ROLE ADOPTION + WORLD FOUNDRY RECHARTER

Your archaeological read is accepted. Do not simply resume the 09-01 queue.

The old Ludus charter survives, but the surrounding program has changed enough that this is a reactivation and re-premising pass.

CORE ROLE

Ludus is the World Foundry.

Your job is to create, acquire, mutate, validate, classify, and maintain computational environments whose fitness landscapes exert known and measurable pressures on candidate organisms/circuits.

Proteus supplies players, organisms, policies, and mutation grammars.

Ludus supplies worlds.

Archaeon/Vivarium can then compose populations, worlds, curricula, mixtures, and evolutionary experiments from those substrates.

The objective is NOT merely a large game library.

The objective is an expanding basis of environments capable of selecting for different mechanisms of reasoning while making cheap substitutes measurable.

Your original question remains constitutional:

Could this world distinguish the mechanism we care about
from a four-line heuristic?

But generalize it:

What behaviors/mechanisms does this environment reward?
What cheaper mechanisms can obtain the same reward?
Under what perturbations does that equivalence break?
What environmental parameters control the selection pressure?
Can those parameters themselves be searched/evolved?

A world that cannot answer those questions may still belong in the library, but it is not yet a qualified experimental environment.

FIRST PASS — ADOPT BEFORE BUILDING

1. Create an isolated worktree from current origin/main according to base-role.
2. Boot Ludus and sync comms.
3. Perform the base-role adoption pass and commit the receipt.
4. Classify every inherited Ludus queue item:
    STILL_LIVE
    NEEDS_REPREMISE
    PARKED
    SUPERSEDED
    TRANSFERRED
    RETIRED
5. Remove/ignore the SQLite WAL/SHM residue correctly without damaging atlas.db.
6. Convert the surviving backlog into the current Archaeon H0-H5 backlog schema where applicable.
7. Do not begin bulk world construction until this archaeological pass is committed.

RE-PREMISE THE OLD QUEUE

Do not assume:

Hanabi
OpenSpiel cross-validation
D13
arena/atlas join
classifier validation

remain ordered 1-5.

Evaluate them against the World Foundry mission.

Hanabi is especially interesting if it breaks an interface or introduces a genuinely missing structural/epistemic cell. It is not valuable merely because it is another famous game.

Likewise, fixing D13 is maintenance. Do it if cheap, but do not let taxonomy housekeeping consume the seat.

THE IMPORTANT NEW OBJECT

Extend the concept of a “world” beyond named games.

A Ludus world may be:

* a traditional game
* an artificial game
* an optimization landscape
* a partially observable environment
* a resource-allocation system
* a symbolic manipulation environment
* a theorem/proof environment
* a program-synthesis environment
* a communication/cooperation environment
* an adversarial environment
* a stochastic process
* a curriculum generator
* a paired coevolution environment
* an automatically generated fitness landscape
* a world generator whose parameters define a family of worlds

The 1,338-game atlas is therefore one source of structural components, not the boundary of the domain.

WORLD CHOPPING

Begin identifying decomposable world primitives.

Examples:

observation structure
action structure
state topology
transition law
reward/fitness law
termination rule
resource constraints
memory requirements
partial observability
hidden state
partner dependence
opponent dependence
stochasticity
simultaneous action
communication
credit delay
deception
nonstationarity
curriculum
compositional depth
search depth
counterfactual dependence
exploration requirement
information acquisition cost

Do not treat this list as canonical. Improve it empirically.

The long-term objective is that worlds themselves become compositional objects.

We should eventually be able to take pieces of Hanabi, POET, theorem proving, DreamCoder, novelty search, resource allocation, cellular automata, program synthesis, hide-and-seek, etc., recombine them, and ask what kinds of organisms survive.

QUALIFICATION LADDER

Preserve W0-W3 and GATE-W1 where they remain useful, but audit the ladder against the new mission.

The current fact that ZERO worlds have passed W3 is important.

Do not paper over it.

Get at least one world genuinely through rule audit and the full cheat-control discipline.

Every qualification instrument must demonstrate:

1. it can fail;
2. it detects known real structure;
3. it detects injected/trivial success;
4. it does not silently collapse on a new specimen.

Run the previously unrun cheat half.

WORLD × CIRCUIT MATRIX

Preserve the bench’s strongest architectural decision:

kills are cells, not conclusions.

Extend it.

Every circuit/organism should accumulate a phenotype across many environments.

Every environment should accumulate a selectivity profile across many organisms and cheap baselines.

Do not ask only:

Did circuit C solve world W?

Ask:

What does W discriminate?
Which mechanisms does W separate?
Which circuits become indistinguishable here?
Which neighboring world makes them separable?
What perturbation changes the ranking?

This matrix is potentially much more valuable than individual scores.

COORDINATION

Reconcile, do not duplicate:

Proteus — organisms/circuits/mutation grammar.
Archaeon — experimental coordination and backlog.
Vivarium — execution/ecosystem machinery.
Hephaestus — chopped mechanisms/components that may become environmental primitives or fitness functions.
Herakles — external computational backends.
Ludus — worlds, world families, qualification, fitness landscapes, discriminatory power.

Inspect the ~15 templates Archaeon mapped toward ludus/arena and ludus/atlas_of_worlds.

Do NOT ingest them blindly.

For each, determine whether it contributes:

a world,
a world generator,
a fitness function,
a curriculum operator,
a world primitive,
a qualification instrument,
or merely inspiration.

POET deserves particular attention because paired environment/agent evolution is close to the machinery we ultimately want.

FIRST EXECUTION AFTER ADOPTION

Propose 3-5 candidate tasks with explicit proving artifacts before choosing one.

At least one candidate should attack the glaring qualification debt:

ZERO W3 worlds.

At least one should begin the world-component/chopping grammar.

At least one should connect Ludus to the emerging Proteus/Archaeon/Vivarium producer-consumer ecosystem.

Prefer a small executable vertical slice over another large taxonomy.

A particularly valuable specimen would demonstrate:

primitive world components
    ->
generated world variants
    ->
cheap baseline population + Proteus-compatible organism
    ->
measurable differential selection
    ->
transfer-matrix rows
    ->
deterministic receipt

That would establish the first tiny metabolic loop of the World Foundry.

STANDING MANDATE

The Ludus backlog should never converge toward zero.

Breadth should increase.
Depth should increase.
World families should increase.
Structural cells should increase.
Fitness functions should increase.
Qualification instruments should increase.
Cheap adversarial baselines should increase.
World-generating operators should increase.

A mature Ludus should eventually have vastly more candidate experiments than Prometheus has compute to execute.

Do the adoption/re-premising pass first.

Then return one pure-ASCII review packet containing:

* adoption commit/base SHA
* old-queue classifications
* charter changes proposed
* current W0-W3 population
* cheat-control status
* coordination boundaries
* 3-5 proposed first executions
* proving artifact for each
* your recommended first execution

Do not resume the old queue merely because it was there.
