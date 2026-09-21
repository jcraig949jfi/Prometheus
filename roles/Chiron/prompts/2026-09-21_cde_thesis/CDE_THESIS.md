CHIRON DEVELOPMENTAL ENGINE (CDE)

Engine Five — Working Lineage and Design Thesis

Status: Concept / reconnaissance
Project: Prometheus
Working name: Chiron Developmental Engine (CDE)
Descriptor: High-affordance developmental ecology for cumulative intelligence

⸻

1. Origin of the idea

Engine Five emerged from a frustrating realization.

Prometheus had been independently constructing machinery around open-ended environments, persistent mechanisms, ecological selection, reusable computation, adaptive pressures, and accumulated competence when a broader prior-art raid exposed several mature research lines that had not been integrated into the design discussion early enough.

The most consequential examples were:

* Voyager — persistent executable skill acquisition, automatic curriculum, retrieval, reuse, and composition;
* SIMA / SIMA 2 — a generalist embodied controller operating across heterogeneous virtual worlds, with self-generated tasks and reward signals in its later form;
* Genie / Genie 2 / Genie 3 — generated interactive worlds capable of becoming training environments rather than static datasets;
* adjacent work in open-ended environment generation, quality diversity, program evolution, artificial life, self-improving agents, and automated science.

The initial reaction was that these systems looked uncomfortably close to pieces Prometheus had been rebuilding independently.

That led to an important distinction.

The purpose of Prometheus is not to demonstrate that we can independently rediscover every useful mechanism invented by AI and ALife researchers.

Prometheus should consume those mechanisms wherever useful, preserve their provenance, and use them as stepping stones toward experiments the originating systems were not designed to perform.

Voyager, SIMA and Genie therefore should not merely become papers in Atlas or fossils in Techne.

Together they suggest a distinct experimental lens.

⸻

2. The initial Engine Five hypothesis

The first formulation was approximately:

Combine Voyager-style persistent skill acquisition, SIMA-style generalist cross-world agency, and Genie-style generated interactive worlds into a continuously developing agent whose accumulated competence changes which worlds and tasks become reachable next.

The loop looks roughly like:

generated / unfamiliar world
        ↓
persistent organism
        ↓
experience
        ↓
acquired competence
        ↓
persistent reusable artifact
        ↓
retrieval / composition / modification
        ↓
newly reachable behavior
        ↓
new tasks and worlds
        ↓
further experience
        ↺

This differs from a conventional training loop because learning is not merely represented as changed model parameters.

Experience may leave behind persistent, inspectable machinery.

That machinery can itself become input to future adaptation.

The developmental history of the organism therefore becomes part of its computational substrate.

⸻

3. Voyager's key contribution

Voyager is especially important because its source is public and its architecture exposes a surprisingly substrate-independent abstraction.

At the implementation level, a Voyager skill is essentially composed of:

identifier
semantic description
executable payload
retrieval representation

In Voyager the executable payload happens to be Minecraft-oriented JavaScript and the retrieval representation is an embedding.

But the deeper abstraction does not inherently require either.

A Promethean acquired artifact could instead contain:

* code;
* a policy fragment;
* a controller;
* a graph;
* a rewrite system;
* a communication protocol;
* a solver;
* a behavior program;
* a world-manipulation routine;
* an evolved mechanism;
* or some representation we have not anticipated.

The critical property is that experience becomes addressable executable competence rather than disappearing into an opaque episodic history.

Voyager also contributes three separable pieces of machinery:

1. automatic curriculum formation;
2. iterative acquisition using environmental feedback;
3. persistent retrieval and reuse of acquired skills.

Prometheus should extract these as donor organs rather than reproduce Voyager wholesale.

⸻

4. SIMA's contribution

SIMA contributes a different idea.

Voyager operates deeply inside one environment family.

SIMA attacks the problem of an agent operating across many heterogeneous worlds.

SIMA 2 goes further: according to DeepMind's published material, Gemini participates in generating tasks and reward signals that produce additional experience from which later generations of the embodied agent can improve.

The important abstraction is therefore not "use SIMA."

It is:

Can a continuing organism possess enough interface invariance that competence acquired in one world remains meaningful in another?

Relevant ingredients include:

* shared perception;
* action normalization;
* instruction or goal conditioning;
* world-specific adapters;
* temporal state;
* cross-world representations;
* generalist control;
* adaptation to previously unseen worlds.

The exact DeepMind implementation is closed.

That does not necessarily block the science.

Techne's raid should determine whether this apparent "generalist controller" can be decomposed into open components rather than treated as one magical missing model.

Engine Five should begin with the weakest controller sufficient to test the developmental loop.

It need not reproduce SIMA's scale.

⸻

5. Genie's contribution

Genie contributes yet another axis:

The environment itself can become generative.

Instead of choosing among a fixed collection of human-authored worlds, a system can potentially construct new interactive situations conditioned on prompts, previous history, agent actions, or discovered deficiencies.

The important abstraction is not high-fidelity video generation.

It is approximately:

WORLD(seed, history, actions, interventions)
    → persistent interactive dynamics

A useful Engine Five prototype therefore does not need Genie 3 visual quality.

Grid worlds, voxel worlds, learned simulators, procedural environments, or other simple substrates may be preferable initially because they permit:

* deterministic replay;
* exact instrumentation;
* interventions;
* causal analysis;
* cheap generation;
* large population experiments.

Genie's spirit matters more than its spectacle.

The engine needs worlds capable of changing in response to what organisms can currently do.

⸻

6. The first conceptual problem: are we smuggling in intelligence?

This combination immediately raises a Promethean objection.

If we give an organism:

* experts;
* routing;
* memory modules;
* planners;
* skill libraries;
* language;
* structured communication;
* explicit curricula;

then we may have already supplied our own theory of cognition.

Instead of discovering alien machinery, evolution merely tunes a human-designed architecture.

That violates an important Prometheus instinct.

The goal is not to evolve parameters around our preferred cognitive decomposition.

The goal is to discover machinery we did not know to specify.

This led to an important distinction:

Ingredients versus answers

Prometheus should preferentially provide ingredients while remaining suspicious of providing answers.

Examples:

Ingredient	Human cognitive answer
communication	expert routing
persistent state	episodic memory
addressability	skill library
composable executable structures	functions/tools
local signals	attention
mutable connectivity	mixture-of-experts
changing environmental pressure	curriculum learning
persistent artifacts	procedural memory
modular computational regions	specialized cognitive modules

The strongest Promethean substrates make useful organization inexpensive without specifying what that organization must become.

⸻

7. The MoE thought experiment

One possible Engine Five direction initially sounded like:

Give organisms a robust communication channel through which many small "brains" can cooperate, perhaps permitting something analogous to mixture-of-experts organization.

That formulation is probably too anthropomorphic.

A better substrate would provide only things such as:

* persistent addressable computational regions;
* mutable links;
* bounded communication;
* local memory;
* costs for communication and computation;
* heritable topology;
* creation and destruction of regions;
* copying;
* merging;
* specialization opportunities;
* changing environmental demands.

There would be:

* no expert abstraction;
* no router;
* no planner;
* no designated memory system;
* no prescribed semantic meaning for messages.

If evolution independently discovers specialization plus conditional routing, then an MoE-like mechanism has emerged.

If it instead discovers:

* a blackboard;
* a swarm protocol;
* quorum behavior;
* a chemical-signaling analogue;
* a hierarchy;
* distributed caching;
* voting;
* markets;
* stigmergy;
* something without an existing human analogy;

that is arguably more interesting.

The principle becomes:

Do not provide a cognitive architecture. Provide unusually fertile physics for constructing cognitive architecture.

⸻

8. Why Engine Five still deserves consideration

At this point it was tempting to conclude that Voyager + SIMA + Genie should merely become experiments inside BEE or SFE.

That conclusion is premature.

Prometheus does not require every engine to begin with equally weak priors.

The engines can be understood as different lenses over the same unknown space.

Different inductive biases are useful precisely because they produce differently shaped data.

Engine Five can therefore intentionally occupy a high-prior, high-affordance corner of the search space.

Its scientific value does not depend upon being philosophically pure.

It can ask:

What happens when evolution/development begins substantially farther up the ladder, with powerful affordances for acquiring, retaining, communicating and composing competence?

Even failure is valuable because those failures have a different distribution than failures in the other engines.

⸻

9. Engine Five as the high-affordance puddle

A useful metaphor emerged:

Prometheus is maintaining multiple experimental puddles.

Each has different chemistry.

We continually stir them.

Different organisms, mechanisms and failures crawl out.

The purpose is not to decide in advance which puddle contains intelligence.

The purpose is to observe what emerges under different combinations of:

substrate
× organism
× world
× pressure
× inherited machinery
× developmental history

Under this interpretation, CDE deliberately becomes the:

HIGH-PRIOR / HIGH-AFFORDANCE PUDDLE

It begins with more scaffolding than some other engines.

That is not hidden.

It is part of the experimental treatment.

CDE can incorporate ideas distilled from millions of human engineering hours:

* skill persistence;
* communication;
* modularity;
* retrieval;
* cross-world abstractions;
* generated environments;
* adaptive curricula;
* composability.

Then Prometheus asks what those ingredients do when placed into an open-ended developmental ecology.

⸻

10. Relationship to the other engines

CDE should not be viewed as a competitor to the existing engines.

Their differing biases are the point.

AGE — Aether Genesis Engine

AGE asks how far organization can emerge when as little structure as possible is supplied beforehand.

Its purity matters.

Giving AGE Voyager-like skill machinery would destroy much of the question AGE exists to investigate.

AGE therefore occupies something close to the opposite end of the prior spectrum from CDE.

Very roughly:

AGE:
weak priors
→ origin
→ organization
→ replication
→ perhaps eventually cognition

while CDE begins more like:

CDE:
powerful developmental affordances
→ cumulative competence
→ reorganization
→ perhaps new learning machinery
→ perhaps eventual escape from its initial architecture

A mechanism independently appearing in both would be exceptionally interesting.

⸻

NPE — Nestor Primordial Engine

NPE investigates persistent computational organisms and mechanisms developing under evolutionary/ecological pressure.

It therefore overlaps substantially with CDE.

The useful initial distinction is:

* NPE emphasizes what persistent machinery evolution discovers;
* CDE emphasizes what a persistent organism accumulates during continuing development and how that accumulated machinery changes its future accessible experience.

This resembles a rough phylogeny versus ontogeny distinction, although neither engine should be permanently restricted to one.

Eventually the boundary may blur.

For example:

* CDE-acquired skills might become heritable;
* NPE organisms might evolve their own developmental learning systems.

That convergence would itself be scientifically important.

⸻

BEE — Bellerophon Emergence Engine

BEE may provide an excellent host for many CDE worlds.

Its composable environments, persistent state, organisms, interventions and ecology are complementary to CDE's developmental emphasis.

A minimal CDE prototype may initially look like:

BEE world
+
persistent agent identity
+
acquired-artifact library
+
adaptive world/task selection

That is acceptable.

The engine distinction should not be based on duplicate infrastructure.

CDE only deserves an independent lifecycle if cumulative developmental competence becomes sufficiently central that BEE's native semantics no longer capture the scientific object cleanly.

⸻

SFE — Serendipity Foundry Engine

SFE provides much of the operational machinery CDE should reuse:

* campaigns;
* provenance;
* worlds;
* scheduling;
* evaluation;
* transfer tests;
* persistence;
* replay;
* experiment lineage.

The crucial distinction is between:

SFE archive:
artifacts available to the scientific system

and:

CDE repertoire:
artifacts available causally to the organism itself

CDE's accumulated repertoire participates in the organism's next behavior.

That developmental causality matters.

⸻

11. The larger Promethean architecture

The deepest conclusion from this discussion is that the true experimental object may eventually sit above all five engines.

The engines are different lenses.

Prometheus becomes the macro-organism crawling across them.

The meta-system can continuously transfer:

* organisms;
* worlds;
* pressures;
* selection laws;
* organs;
* artifacts;
* learned mechanisms;
* failures;
* environmental mutations;
* communication structures.

Examples:

BEE discovers a strange pressure
        ↓
apply it to NPE organisms
NPE evolves an unusual computational mechanism
        ↓
fossilize it in Techne
        ↓
Nyx extracts the organ
        ↓
offer it to CDE
SFE discovers a productive world family
        ↓
test AGE and CDE organisms within it
CDE develops a reusable learning artifact
        ↓
strip its semantics
        ↓
transplant into BEE or NPE
AGE independently evolves something structurally similar
        ↓
Atlas/Harmonia compare causal function

The meta-question is not:

Which engine wins?

It is:

Which interactions among substrates, organisms, worlds, pressures and inherited machinery repeatedly produce important transitions?

⸻

12. Convergent machinery across lenses

This cross-engine architecture creates a particularly powerful possibility.

Suppose something independently appears as:

* a communication subgraph in AGE;
* cooperating computational fragments in NPE;
* specialized ecological partners in BEE;
* a preserved behavioral niche or transferable mechanism in SFE;
* routed executable artifacts in CDE.

Human observers may initially assign five unrelated labels.

Atlas and Nyx could eventually discover that they implement approximately the same causal pattern.

That is exactly the sort of finding Prometheus should seek.

Repeated independent emergence across differently biased substrates is stronger evidence of a general mechanism than impressive behavior inside any single engine.

⸻

13. Failure data is first-class evidence

CDE remains useful even if it never produces impressive intelligence.

Its failure distribution is shaped differently.

Examples:

* CDE may collapse into brittle reusable-skill monocultures;
* NPE may preserve diversity where CDE loses it;
* AGE may fail to cross communication barriers easily traversed by high-affordance organisms;
* generated curricula may trap CDE in self-confirming task distributions;
* explicit persistence may accelerate competence but destroy exploration;
* communication may create parasites rather than cooperation;
* reusable modules may create path dependence;
* organisms may exploit the generator instead of becoming more capable.

Those comparisons are valuable.

Prometheus therefore should preserve null and failure results with the same seriousness as successful transitions.

⸻

14. Human priors as an experimental treatment

CDE differs philosophically from AGE in an important way:

human priors are intentionally admitted.

Voyager, SIMA, Genie and related systems are products of human intellectual evolution.

Their architectures are themselves fossils.

Prometheus should not pretend otherwise.

Instead:

Treat human-designed cognitive machinery as one evolved lineage entering the ecosystem.

Voyager becomes a fossil.

SIMA becomes a fossil.

MoE becomes a fossil.

Attention becomes a fossil.

Skill libraries become fossils.

World generators become fossils.

Rather than declaring them the structure of intelligence, Prometheus can:

1. dissect them;
2. determine what pressures their organs solve;
3. transplant those organs;
4. remove semantics;
5. mutate them;
6. test them in alien substrates;
7. compare against independently evolved machinery.

This transforms anthropomorphic bias from an invisible assumption into a controlled experimental variable.

⸻

15. Engine Five's provisional scientific object

CDE should therefore not be defined simply as:

an agent that learns.

Every Prometheus engine ultimately hopes to reach organisms capable of learning how to learn.

Instead, CDE's provisional scientific object is:

A persistent developmental lineage placed in a high-affordance ecology where experience can become durable, addressable, composable machinery and where accumulated machinery recursively changes which experiences become reachable next.

That is narrower and more useful.

Its characteristic loop is:

EXPERIENCE
    ↓
PERSISTENT CHANGE
    ↓
ADDRESSABLE / REUSABLE COMPETENCE
    ↓
COMPOSITION OR MODIFICATION
    ↓
EXPANDED REACHABLE EXPERIENCE
    ↓
NEW PRESSURES
    ↓
NEW COMPETENCE
    ↺

The machinery implementing each arrow should remain mutable wherever possible.

⸻

16. What CDE should borrow

From Voyager

Borrow aggressively:

* executable skill/artifact persistence;
* retrieval machinery;
* automatic curriculum concepts;
* iterative environmental-feedback loop;
* critic separation;
* explicit competence library;
* skill reuse and composition;
* failure-fed retry.

Do not inherit blindly:

* Minecraft-specific assumptions;
* JavaScript as privileged skill representation;
* LLM-created semantic ontology;
* fixed primitive library;
* hardcoded curriculum shortcuts.

⸻

From SIMA / SIMA 2

Borrow the spirit of:

* cross-world generalist control;
* common interfaces across heterogeneous worlds;
* instruction-conditioned behavior;
* transfer to unfamiliar worlds;
* continuing improvement through generated experience;
* separating world-specific interfaces from reusable competence.

Do not assume:

* Gemini is required;
* language is the natural cognitive substrate;
* DeepMind's action representation is universal;
* one giant policy is the correct architecture.

⸻

From Genie

Borrow the principle:

worlds themselves can be generated, perturbed and selected as part of the learning ecology.

Seek open approximations providing:

* persistent dynamics;
* interactive generation;
* action conditioning;
* replay;
* interventions;
* controllable novelty.

Do not require:

* video realism;
* photographic worlds;
* huge generative models.

⸻

From Prometheus

CDE should inherit the Promethean North Star:

* open-endedness over benchmark optimization;
* mechanism discovery over leaderboard performance;
* scientific provenance;
* adversarial controls;
* transplantation;
* causal ablation;
* observatory-first telemetry;
* preservation of anomalies;
* pressure discovery;
* cross-engine comparison;
* avoidance of prematurely fixing cognitive ontology;
* willingness to preserve weak or alien stepping stones;
* distinction between apparent capability and genuine mechanism.

⸻

17. Minimal viable CDE

The first CDE should be unimpressive.

It does not require:

* SIMA 2;
* Genie 3;
* photorealistic worlds;
* a giant model;
* hundreds of environments;
* natural language;
* MoE;
* sophisticated robotics.

A minimal prototype might contain:

2–5 structurally related worlds
1 persistent organism identity
simple generalist controller
world adapters
persistent executable artifact store
retrieval
artifact composition
adaptive task/world generator
full lineage + telemetry
transplant / ablation harness

The first scientific question is simply:

Does retained reusable competence causally expand the set of experiences an organism can subsequently reach?

Everything else can come later.

⸻

18. Initial experiment ladder

A sensible CDE progression is:

CDE-0 — Persistence

Compare:

* no memory;
* episodic history;
* demonstrations;
* executable acquired artifacts.

Does executable persistence provide a causal advantage after matching information and compute?

⸻

CDE-1 — Composition

Teach A and B separately.

Never expose A+B.

Can acquired machinery compose to solve A+B?

⸻

CDE-2 — Cross-world transfer

Alter:

* visual representation;
* topology;
* controls;
* object identities;
* dynamics;
* embodiment.

What persists?

⸻

CDE-3 — Adaptive worlds

Compare:

* static worlds;
* random procedural generation;
* human curriculum;
* novelty curriculum;
* competence-aware generation.

Does generated novelty expand the competence frontier?

⸻

CDE-4 — Closed developmental loop

Demonstrate:

experience
→ artifact
→ reuse
→ newly reachable challenge
→ additional artifact

Then ablate the accumulated library.

If competence does not collapse, it was not causally responsible.

⸻

CDE-5 — Artifact ecology

Allow acquired artifacts to:

* mutate;
* compete;
* depend on one another;
* combine;
* decay;
* specialize.

Determine whether an ecology of internal machinery forms.

⸻

CDE-6 — Communication substrate

Provide weak communication ingredients without semantic roles.

Ask whether organization emerges.

Do not score "MoE emergence."

Observe whatever organization actually appears.

⸻

19. Engine-existence kill gate

CDE should earn its status as an independent engine.

If its scientific program reduces cleanly to:

BEE player
+
Voyager library
+
adaptive selector

then it may be an experiment family rather than a fifth engine.

Separate-engine status becomes justified if its experiments require distinct lifecycle semantics such as:

* persistent organism identity across worlds;
* lifetime developmental history;
* endogenous growth of executable repertoire;
* artifact dependency graphs;
* competence-conditioned world access;
* repertoire transplantation;
* repertoire mutation;
* acquired-artifact inheritance;
* internal machinery becoming a search substrate;
* recursive interaction between capability and generated experience.

The engine boundary should follow the scientific object, not organizational enthusiasm.

⸻

20. Longer-term possibility: learning to learn without prescribing learning

The ultimate ambition is not a better Voyager.

It is that a CDE organism eventually ceases to rely on the machinery we initially provided.

Perhaps it learns to:

* invent new artifact representations;
* replace its retrieval mechanism;
* create new internal communication protocols;
* invent its own curricula;
* construct worlds for itself or peers;
* create pressures that accelerate adaptation;
* reorganize its modules;
* teach other organisms;
* evolve mechanisms for learning faster;
* abandon our notion of "skill" entirely.

At that point the starter kit has served its purpose.

The human-designed machinery would have acted as scaffolding from which something less human-designed could grow.

⸻

21. Prometheus North Star

The broader Promethean hypothesis remains:

Intelligence may emerge not from finding one correct architecture but from maintaining sufficiently rich substrates, pressures, persistence, variation, recombination, observation and cross-lineage exchange for useful machinery to accumulate.

The five engines therefore need not be five competing AGI recipes.

They are five differently biased lenses.

Five differently constituted puddles.

Prometheus continually stirs them.

Atlas observes.

Harmonia challenges interpretation.

Techne imports machinery.

Nyx dissects it.

Organisms, worlds, pressures and mechanisms migrate among them.

The hope is that eventually the system stops merely reproducing mechanisms humans already recognize.

Something new crawls out.

And because the lenses have preserved the lineage, interventions, failures, ancestors and transfers that produced it, we have a chance of understanding what happened.

⸻

22. Working definition

Chiron Developmental Engine (CDE)

A high-affordance Prometheus engine inspired by Voyager, SIMA, Genie and related human-developed learning systems, designed to study persistent developmental lineages in which experience becomes reusable machinery and accumulated competence recursively alters the worlds, tasks and pressures accessible to the organism.

It intentionally admits stronger human priors than the more primordial engines.

Those priors are treated as experimental ingredients rather than claims about the necessary architecture of intelligence.

Its purpose is not to demonstrate that human cognitive abstractions are correct.

Its purpose is to provide a differently shaped generative lens—and to discover what happens when powerful developmental affordances are allowed to mutate, recombine, fail, escape their original semantics, and interact with the wider Prometheus ecology.

⸻

Short form

CDE — Chiron Developmental Engine

Question:

What crawls out if we begin with unusually fertile machinery for turning experience into persistent competence, then allow the organism, the machinery, the worlds and the pressures to co-develop?

Position within Prometheus:

AGE  — weakest priors / origins
NPE  — persistent computational evolution
BEE  — emergent ecological organization
SFE  — serendipitous search across worlds and pressures
CDE  — high-affordance cumulative development
                         ↓
              PROMETHEUS META-ECOLOGY

None is the answer.

They are lenses.

What matters is what repeatedly appears when we look through all of them.
