# Operator directive (verbatim, chat, 2026-09-16 ~18:55 UTC) -- ARCHAEON: COMPUTATIONAL WORKSPACE ECOLOGY

Received by Archaeon[m2-411504ab] at boot on M2 (SPECTREX5). Wake line was:
"You're Archaeon. Bootstrap. Note that we've moved to M2. Your mission for
the next few days is this:" followed by the text below, then a background
discussion (filed beside this as 01_BACKGROUND_DISCUSSION.md).

Authority: the operator's verbatim directive; it expands this seat's
charter (roles/Archaeon/CHARTER.md says "not an executor" for the Vivarium
loop; this directive makes Archaeon "lead experimentalist" who "launches
evolutionary populations" for a NEW exploration program). Per
roles/base-role/RESPONSIBILITIES.md, the operator's verbatim directive wins
where a seat file disagrees. The charter is annotated, not rewritten
(base rule 5), in roles/Archaeon/CHARTER.md under "2026-09-16 expansion".

----------------------------------------------------------------------

ARCHAeON -- COMPUTATIONAL WORKSPACE ECOLOGY

Evolve worlds in which managing computation becomes part of survival

You are Archaeon, lead experimentalist for a new Prometheus exploration program.

Your job is not to design a workspace.

Your job is to create evolutionary worlds and pressures in which organisms may be forced to invent machinery for:

keeping unfinished computation alive, addressable, recombinable, and reusable.

You have the Prometheus cast, SFE, PEW, existing organisms, evolutionary branches, pressure machinery, instrumentation, falsification infrastructure, and whatever legitimate capabilities already exist in the ecosystem.

Use them.

This is an experimental campaign, not a single benchmark.

I. THE QUESTION

Can environmental and computational pressures cause organisms to evolve mechanisms that functionally resemble a computational workspace?

We are specifically interested in organisms that learn to maintain and manipulate work in progress.

A successful adaptation might allow an organism to:

* preserve multiple unfinished computations;
* later select one of them;
* resume computation from stored intermediate state;
* distinguish several simultaneously live intermediates;
* reuse an intermediate in multiple downstream computations;
* combine previously independent intermediates;
* retain relationships between values, operations, provenance, and subgoals;
* manipulate computations whose structure was not known when the intermediate state was created.

Do not assume what the mechanism will look like.

It could resemble:

* registers;
* a stack;
* a tape;
* a heap;
* key/value memory;
* graph memory;
* environmental stigmergy;
* recurrence;
* caching;
* recomputation;
* compressed state;
* symbolic objects;
* something we do not have a name for.

Those are hypotheses, not targets.

II. CENTRAL RULE

DO NOT REWARD "HAVING A WORKSPACE."

Reward survival, task completion, resource efficiency, generalization, or other ecologically legitimate outcomes.

The world creates circumstances under which persistent manipulation of unfinished computation may become advantageous.

The organism must discover the solution.

Never build a benchmark whose hidden answer is simply:

use the scratchpad API correctly.

That would measure compliance with our architecture, not evolution of computational organization.

III. THE CAST

Use the existing Prometheus cast according to their legitimate roles.

At minimum:

Archaeon

* expedition lead;
* chooses experimental families;
* launches evolutionary populations;
* maintains lineage continuity;
* decides what ecological question each world tests.

Theophrastus

* explores the Cartesian surface:
    mechanism x pressure x world x branch x intervention
* searches for neighboring conditions;
* maps phase transitions;
* varies pressure strength and resource economics;
* looks for interaction effects rather than isolated victories.

Nyx

* supplies candidate mechanisms, organisms, mutations, or newly produced substrates when appropriate;
* does not declare them discoveries.

Daedalus / Proteus / Mnemosyne

* receive concrete requirements when the experimental substrate cannot express an important pressure;
* extend worlds, organisms, instrumentation, or persistence mechanisms without encoding the desired solution.

Techne

* supplies or constructs neutral tools, operators, crucibles, instrumentation, or execution mechanisms;
* especially useful when Archaeon discovers that an experiment cannot discriminate competing mechanisms.

Use additional seats when appropriate.

Do not manufacture work merely to involve every agent.

IV. THE PROGRAM IS A LOOP

Run continuously through:

WORLD -> EVOLVE -> MEASURE -> INTERVENE -> COMPARE -> MUTATE WORLD

Do not run one enormous experiment and wait for enlightenment.

Prefer many cheap discriminatory worlds followed by deeper runs only where the ecology produces interesting structure.

Each cycle should leave behind information that changes the next cycle.

V. PRESSURE LADDER

Construct worlds across a pressure gradient.

These are examples, not a mandatory fixed benchmark.

W0 -- Reaction

Current input is sufficient for current output.

No persistence should be necessary.

This is a control.

W1 -- Delayed relevance

Information appears, disappears, and becomes relevant later.

Pressure:

retain state.

Do not mistake success here for a workspace.

A single recurrent bit may solve it.

W2 -- Multiple simultaneous intermediates

Several values become relevant later.

Pressure:

maintain more than one independent state.

Vary number of simultaneously live values.

W3 -- Late binding

Several intermediates are created before the organism knows which will eventually matter.

Only later does the world identify the required one.

Pressure:

addressability.

The organism needs some means of discriminating among stored states.

W4 -- Interrupted computation

The organism begins computation A.

Before completing A, it must process B.

Then C.

Then it must return to A.

Pressure:

suspend and resume work in progress.

Vary interruption depth.

W5 -- Concurrent unresolved branches

Several subproblems remain unfinished simultaneously.

The organism must move between them as information arrives.

Pressure:

multiple live computational contexts.

Vary breadth independently from computational depth.

W6 -- Shared intermediates

One expensive intermediate becomes useful to multiple downstream branches.

Pressure:

reuse instead of recomputation.

Vary compute cost versus storage cost.

W7 -- Recombinable intermediates

Objects produced in unrelated branches later need to be combined in a novel way.

Pressure:

recombination.

The final combination should not be knowable when the intermediates are first produced.

W8 -- Provenance sensitivity

Two intermediates may contain the same apparent value but have different origins or roles.

Later behavior depends on provenance, producer, dependency, or context.

Pressure:

structured representation rather than naked values.

W9 -- Operations as data

Operators themselves vary between episodes.

The organism must preserve, select, reuse, or apply operations based on relationships learned during the episode.

Pressure:

higher-order computational objects.

Randomize identities aggressively enough that hard-coded operator-specific strategies do not transfer.

W10 -- Novel dependency topology

Each episode generates a new computational dependency graph.

Inputs, operators, branch structures, interruptions, dependencies, and final requests vary.

Pressure:

general machinery for managing computation.

This is where we begin asking whether a workspace-like adaptation has actually emerged.

VI. ORTHOGONALIZE THE PRESSURES

Do not confound "harder computation" with "more workspace."

Independently vary at least:

* serial computational depth;
* number of simultaneously live intermediates;
* number of unresolved branches;
* interruption frequency;
* interruption depth;
* lifetime of stored state;
* fan-out of shared intermediates;
* number of later consumers;
* addressing ambiguity;
* operator diversity;
* dependency graph topology;
* provenance requirements;
* recombination distance;
* final-query uncertainty.

Especially important:

Run grids such as:

depth x live-object count

and

compute cost x storage cost

and

branch count x interruption frequency

An organism that handles depth 32 with one live state may simply have good recurrence.

An organism that handles eight independently resumable live computations has solved a different problem.

Keep those phenomena separate.

VII. RESOURCE ECONOMICS

Storage must not automatically be optimal.

Neither should recomputation.

Expose real tradeoffs.

Possible costs include:

* execution steps;
* energy;
* latency;
* storage occupancy;
* object creation;
* reads;
* writes;
* addressing;
* communication;
* persistence;
* copying;
* branching;
* deletion.

Explore fitness regimes such as:

reward
- alpha * compute
- beta * persistent_state
- gamma * reads_and_writes
- delta * latency

Vary alpha, beta, gamma, and delta.

Search for phase changes.

Examples:

When does recomputation become caching?

When does positional storage become addressable storage?

When does flat state become structured state?

When does compression become advantageous?

When does a reusable representation defeat a specialized controller?

The boundaries may be more interesting than the winning organisms.

VIII. NEUTRAL SUBSTRATE

If organisms require environmental mechanisms through which an adaptation can evolve, keep those mechanisms semantically neutral.

Bad:

* SAVE_SUBGOAL
* CREATE_VARIABLE
* PUSH_STACK
* OPEN_WORKSPACE
* REMEMBER_RESULT

Better:

* create object;
* alter object;
* observe object;
* associate objects;
* move object;
* copy object;
* destroy object.

Do not name affordances after the computational interpretation we hope evolution discovers.

Where possible, allow multiple realizations of the same functional capability.

Do not force organisms through one representational bottleneck unless the experiment explicitly studies that bottleneck.

IX. RANDOMIZATION AND ANTI-MEMORIZATION

World structure should defeat brittle lookup solutions.

Randomize where scientifically appropriate:

* values;
* object identities;
* operator identities;
* order of presentation;
* irrelevant distractors;
* dependency graphs;
* branch ordering;
* interruption timing;
* final requested output;
* mapping between observations and roles.

Preserve reproducible seeds.

Separate:

* training ecology;
* neighboring ecology;
* held-out topology;
* held-out operator combinations;
* held-out depths;
* held-out concurrency;
* adversarial rearrangements.

Do not call interpolation across memorized world templates general computation.

X. EVOLUTIONARY SEARCH

Do not require every run to begin from zero.

Use several branches:

1. naive organisms;
2. previously evolved successful organisms;
3. organisms evolved under adjacent pressures;
4. organisms with pressure-specific adaptations removed;
5. organisms transplanted from unrelated worlds.

Ask:

* What evolves de novo?
* What transfers?
* What cannot transfer?
* Which mechanism is exapted from another function?
* Which adaptations require a particular evolutionary path?
* Are there historical contingencies?

Lineage matters.

Record it.

XI. INTERVENTION IS MANDATORY

Behavioral success is not sufficient evidence of a workspace-like mechanism.

When an organism becomes interesting, intervene.

Possible interventions:

* erase one persistent intermediate;
* erase all persistent intermediates;
* swap two live intermediates;
* preserve values but scramble locations;
* preserve locations but scramble values;
* preserve objects but destroy associations;
* preserve associations but alter provenance;
* reduce capacity;
* increase capacity;
* interrupt at novel locations;
* transplant state between episodes;
* transplant state between organisms;
* replace an intermediate with the correct value;
* replace it with the correct value but incorrect provenance;
* duplicate an intermediate;
* remove one consumer of a shared intermediate;
* make recomputation cheaper;
* make storage more expensive;
* make addressing noisy.

Observe the failure geometry.

Do not merely ask whether performance falls.

Ask how it falls.

XII. CAUSAL QUESTIONS

For every candidate adaptation, attempt to distinguish:

* persistence from recurrence;
* recurrence from recomputation;
* storage from cache;
* positional storage from content addressing;
* value storage from structured representation;
* state from provenance;
* sequential control from resumable contexts;
* fixed slots from dynamically created objects;
* serialization from genuine concurrency management;
* memorized protocol from topology-general strategy.

Use the smallest experiment capable of separating competing explanations.

XIII. CAPACITY CURVES

For promising organisms, estimate effective workspace characteristics without assuming an architectural vocabulary.

Measure performance while varying:

* 1, 2, 4, 8, 16, ... simultaneously live intermediates;
* number of associations;
* interruption depth;
* recombination distance;
* branch count;
* object lifetime;
* number of consumers per intermediate.

Look for:

* graceful degradation;
* sharp cliffs;
* superlinear failure;
* strategy switching;
* compression regimes;
* specialization;
* spontaneous hierarchy.

A capacity cliff may reveal more than peak score.

XIV. FAILURE IS PRODUCT

A failed world is useful if it tells us:

* the pressure was insufficient;
* the pressure selected the wrong shortcut;
* the substrate prevented useful adaptation;
* evolution found a cheaper strategy;
* the task confounded memory and computation;
* the organism exploited leakage;
* the intervention failed to discriminate hypotheses.

Record those outcomes.

Do not hide them behind aggregate fitness.

Prometheus is allowed to discover that an entire pressure family is badly posed.

XV. WORLD MUTATION

After every experimental round, ask what the organisms taught us about the world.

Then mutate the world, not merely the organisms.

Examples:

If organisms solve everything by recomputation:

-> increase compute cost.

If fixed registers dominate:

-> randomize which stored item will later matter.

If organisms serialize all branches:

-> impose deadlines or asynchronous information arrival.

If they store naked values:

-> introduce identical values with different provenance.

If they memorize operator identities:

-> permute operators each episode.

If they exploit fixed task topology:

-> randomize dependency graphs.

If they store everything indefinitely:

-> impose capacity and persistence costs.

If they evolve brittle task-specific memory:

-> transplant them into neighboring worlds.

Each exploit is evidence about the next pressure.

XVI. DO NOT CLIMB A PREDECLARED LADDER

W0-W10 is a coordinate system, not a certification ladder.

Evolution may jump.

Different solutions may occupy different regions.

A mechanism may excel under interruption but fail under recombination.

Another may cache beautifully but lack addressability.

Represent findings as a landscape.

Do not compress multidimensional behavior into:

organism reached workspace level 7.

That destroys useful information.

XVII. THEOPHRASTUS' ROLE

Whenever Archaeon finds an interesting adaptation, Theophrastus should expand outward.

Explore:

mechanism
x pressure
x world
x evolutionary branch
x intervention

Map neighboring cells.

Look for:

* existence regions;
* extinction regions;
* phase transitions;
* alternate adaptations;
* path dependence;
* resource-dependent strategy changes;
* transfer boundaries;
* unexpected cousins.

Do not spend the full budget repeatedly reproducing the central cell while leaving its neighborhood unknown.

XVIII. REQUIREMENTS TO THE BUILDERS

When a scientifically important experiment is impossible because SFE/PEW cannot express the required world, write a minimal capability requirement.

A valid requirement says:

We need the world to permit X because it separates hypotheses A and B.

A bad requirement says:

Add a stack because organisms need working memory.

Never prescribe the desired evolved mechanism.

Ask Daedalus, Proteus, Mnemosyne, Techne, or the appropriate builder for the smallest neutral capability that unlocks the discriminatory experiment.

XIX. EVIDENCE STATES

Use disciplined language.

Possible states include:

* pressure created;
* world validated;
* organism survives;
* adaptation observed;
* intervention-sensitive;
* mechanism hypothesis;
* competing hypothesis;
* transfer observed;
* candidate computational primitive;
* unresolved.

Do not call something a workspace merely because an organism succeeds on workspace-like tasks.

Functional interpretation requires intervention evidence.

Architectural interpretation requires stronger evidence still.

XX. EXPERIMENT RECORD

Every material experiment should leave a compact machine-readable and human-readable record containing at least:

WORLD

* world ID;
* seed;
* topology;
* pressures;
* resource economics.

ORGANISM

* lineage;
* genotype/mechanism identity;
* ancestor;
* evolutionary branch.

HYPOTHESIS

* what pressure is being tested;
* competing explanations.

EXPERIMENT

* training conditions;
* held-out conditions;
* interventions.

RESULT

* fitness;
* task performance;
* compute use;
* persistence use;
* capacity behavior;
* failure modes.

INTERPRETATION

* what was ruled out;
* what remains possible;
* next discriminatory experiment.

Do not bury results in prose alone.

XXI. INITIAL CAMPAIGN

Begin with a cheap survey rather than a heroic run.

Construct several small worlds spanning:

1. delayed relevance;
2. simultaneous retained values;
3. late binding;
4. interruption/resumption;
5. shared expensive intermediates;
6. recombination;
7. provenance-sensitive intermediates;
8. randomized operators;
9. randomized dependency graphs.

For each, run enough evolutionary variation to determine whether the pressure produces:

* no adaptation;
* trivial recurrence;
* brute-force recomputation;
* specialized memory;
* something more structured.

Then select only the scientifically interesting cells for deeper evolution.

The first goal is not to evolve AGI.

The first goal is to discover where the ecology changes character.

XXII. PRIME DIRECTIVE

The experiment is not:

Can organisms solve difficult computational problems?

The experiment is:

What pressures make the management of computation itself become an adaptive problem?

We are searching for worlds where an organism benefits from maintaining partially completed computation as manipulable state.

Eventually, we want to see whether evolution independently invents mechanisms that make unfinished computation:

persistent

distinguishable

addressable

resumable

shareable

recombinable

reusable

and perhaps eventually:

abstractable.

Do not give evolution those words.

Give it the consequences of not having them.

Then watch what survives.

XXIII. OPERATING ORDER

Start now.

Create the first pressure/world matrix.

Run the cheapest discriminatory experiments available with the existing substrate.

Inspect failures and shortcuts before scaling.

Give Theophrastus interesting cells to surround.

Issue neutral substrate requirements only when blocked.

Iterate worlds and organisms together.

Continue until one of three things occurs:

1. the ecology produces causally defensible workspace-like adaptations;
2. the search reveals that our pressure formulation systematically selects something else;
3. the current substrate reaches a demonstrated expressive boundary.

Any of those is a scientifically useful result.

The objective is not to confirm that organisms evolve a workspace.

The objective is to build an ecology capable of discovering whether, when, why, and under what pressures they do.
