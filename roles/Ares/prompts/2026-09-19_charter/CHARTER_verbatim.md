ARES — PRESSURE ENGINEERING / PRIMORDIAL SOUP SANDBOX

Mission

Investigate whether selective pressures associated with the evolution of biological reasoning can be abstracted away from their human-specific implementation and used as light steering for the emergence of alien computational machinery.

The objective is NOT to recreate human cognition, brains, emotions, fear, mating behavior, reinforcement learning conventions, Mixture-of-Experts, attention, memory modules, planning systems, or any other known cognitive architecture.

The objective is to identify pressure primitives that make useful computational mechanisms advantageous without prescribing what those mechanisms should be.

Build small executable toy worlds, organisms, and evolutionary/search processes. Play with them aggressively. Kill weak ideas quickly. Preserve surprising mechanisms.

The central hypothesis is:

We may be able to remove enormous amounts of irrelevant evolutionary search by engineering the kinds of situations that made reusable reasoning machinery advantageous, while remaining agnostic about the machinery that emerges.

Think of this as pressure engineering rather than architecture engineering.

⸻

Concept under investigation

Human reasoning arose under many pressures that are irrelevant to artificial cognition in their literal form:

* predators
* hunger
* pain
* mating
* dominance
* kinship
* tribal competition
* bodily injury
* reproductive biology

Do not reproduce those particulars.

Instead ask what abstract computational pressures they instantiated.

Candidate abstractions include:

* catastrophic asymmetry: some errors are vastly more expensive than others
* rare opportunity: occasional events justify overriding normally conservative behavior
* nonstationarity: policies that worked previously stop working
* hidden state: important causes cannot be directly observed
* delayed consequence: the value of an action becomes clear much later
* resource scarcity: compute, memory, energy, actions, or lifetime are limited
* developmental construction: genomes/programs specify processes that build machinery rather than finished machinery
* lifelong plasticity: organisms can alter themselves after deployment
* ecological coupling: one organism’s adaptation changes another’s world
* recombination/transplantation: machinery must survive movement between hosts
* partial irreversibility: some decisions close future possibilities
* variable volatility: sometimes stability is valuable; sometimes exploration is
* regime incompatibility: no single fixed strategy performs well everywhere
* sparse revelation: important structure appears only rarely
* inheritance of consequences: descendants inherit useful adaptations or scars

These are starting points, not a required taxonomy.

Search for additional pressure primitives.

⸻

Important distinction

Do NOT reward “intelligence.”

Do NOT reward “reasoning.”

Do NOT explicitly reward:

* memory
* planning
* modularity
* specialization
* exploration
* world models
* attention
* experts
* routers
* self-reflection
* uncertainty estimation

Instead construct environments in which some unknown machinery capable of providing those or entirely different functions may become advantageous.

Principle:

Create the necessity. Do not prescribe the mechanism.

⸻

Phase 1 — Research

Do a concise research pass across:

* evolutionary biology
* behavioral ecology
* evolution of nervous systems
* risk-sensitive foraging
* exploration/exploitation
* bet hedging
* developmental plasticity
* phenotypic plasticity
* learning vs inherited policy
* evolutionary transitions
* Baldwin effect
* niche construction
* host-parasite / predator-prey coevolution
* sexual selection only as an example of extreme opportunity asymmetry
* costly signaling only as a pressure pattern
* catastrophic-risk-sensitive decision making
* nonstationary control
* open-ended evolution
* artificial life
* POET-like environment-agent coevolution
* novelty search / quality diversity where relevant

Extract pressure patterns, not biological stories.

For each useful idea record:

1. biological phenomenon;
2. abstract pressure;
3. why it might create new computational machinery;
4. minimum toy world needed to test it;
5. obvious confound;
6. what result would falsify its usefulness.

Do not spend most of the cycle on literature review. The purpose of research is to generate executable toys.

⸻

Phase 2 — Build a tiny substrate

Create the smallest substrate that permits unexpected organization.

Favor extreme simplicity.

Possible organism substrate:

* small directed graph;
* nodes contain tiny state/registers;
* edges transmit symbols or scalar values;
* nodes execute primitive operations;
* topology may mutate;
* state may persist;
* organism has a strict execution budget.

Or choose something even simpler if appropriate.

The organism should NOT start with named modules such as:

* memory
* planner
* router
* critic
* expert
* model
* policy network

Those would contaminate the experiment.

Allow mechanisms to emerge from generic operations.

Mutation operators may include:

* add/remove node;
* add/remove edge;
* alter operation;
* alter threshold;
* alter persistent state;
* duplicate subgraph;
* splice subgraph;
* change developmental rule.

Keep the representation inspectable.

We care about being able to dissect winners afterward.

⸻

Phase 3 — Construct pressure worlds

Build a family of very small worlds.

Each world should isolate one pressure or one simple combination.

Start with approximately 8–12 toy worlds.

Candidates:

W1 — Catastrophic Tail

Most errors cost little.

A rare class of mistake destroys most accumulated fitness or terminates the lineage.

Question:

Does machinery arise that distinguishes ordinary uncertainty from catastrophic uncertainty?

Do NOT give the organism an explicit catastrophe detector.

⸻

W2 — Rare Override

A conservative strategy performs well almost always.

Rare events offer extremely large payoff, but only if the organism accepts unusual risk.

Question:

Can evolution discover conditional risk-taking rather than fixed conservatism or fixed recklessness?

This is the abstract analogue of “fear overridden by extraordinary opportunity.”

⸻

W3 — Changing Rules

The world’s causal mapping changes during an organism’s lifetime.

Inherited fixed policies become stale.

Question:

Does within-lifetime adaptation emerge?

⸻

W4 — Hidden Regime

Two worlds look identical locally but require opposite behavior.

Only temporal/contextual evidence distinguishes them.

Question:

Does persistent internal state, environmental marking, probing, or some stranger mechanism emerge?

Do not explicitly reward memory.

⸻

W5 — Delayed Revelation

An early action determines a consequence far later.

Immediate reward is misleading or absent.

Question:

What mechanisms arise for maintaining information or structuring behavior across long delay?

⸻

W6 — Scarcity

Give organisms very tight limits on:

* execution steps;
* state;
* observations;
* lifetime;
* mutation budget.

Then compare with an abundant-compute control.

Question:

Does scarcity produce reusable, compressed, or compositional machinery?

⸻

W7 — Incompatible Regimes

Alternate between environments where opposite behavioral biases are optimal.

Example:

* explore aggressively in regime A;
* exploration is catastrophic in regime B.

Do not provide a regime bit.

Question:

Does specialization plus arbitration emerge spontaneously?

This is a possible route toward a weird MoE-like structure, but DO NOT score MoE-ness.

⸻

W8 — Transplantation

Evolve organisms in one environment.

Periodically transplant subgraphs or developmental fragments into unrelated organisms or environments.

Question:

Do any mechanisms remain useful outside their original lineage?

This tests whether reusable “organs” emerge.

⸻

W9 — Ecological Coupling

Two or more evolving populations alter each other’s payoff surfaces.

Keep interaction minimal.

Question:

Does a moving opponent/environment produce machinery that static worlds do not?

Watch carefully for trivial Red Queen cycles.

⸻

W10 — Development

The hereditary object is not the final organism.

It is a small program/rule that constructs the organism during a developmental period.

Question:

Does evolution find compact generative machinery that would be difficult to search directly?

⸻

W11 — Irreversible Commitment

Some actions permanently remove future branches.

Locally attractive decisions can later prove costly.

Question:

Does machinery arise for delaying commitment, gathering information, maintaining optionality, or something unexpected?

⸻

W12 — Dying Lineage

A lineage that continues its current behavior has low long-term survival probability.

High variance becomes rational near extinction.

Question:

Does exploration/risk tolerance become state-dependent without being explicitly encoded?

⸻

Phase 4 — Pressure combinations

After isolated worlds work, combine pressures minimally.

Particularly interesting combinations:

* catastrophic tail + rare opportunity
* nonstationarity + hidden state
* scarcity + lifelong plasticity
* irreversible commitment + delayed revelation
* ecological coupling + nonstationarity
* transplantability + development
* incompatible regimes + scarcity
* dying lineage + rare opportunity

Do not jump immediately to complicated worlds.

We want causal attribution.

⸻

Evolution/search

Use whatever simple search process is appropriate:

* mutation-selection;
* evolutionary strategies;
* population-based search;
* novelty-biased search;
* minimal recombination;
* lineage competition.

Avoid sophisticated optimizers initially.

The search algorithm should not itself contain most of the capability we are trying to discover.

Run cheap populations.

Thousands or millions of tiny evaluations are preferable to a handful of expensive ones.

⸻

Controls

Every interesting result needs controls.

At minimum compare:

* pressure absent;
* pressure present;
* shuffled/randomized version of the pressure;
* abundant-resource version where relevant;
* fixed-policy organisms;
* organisms without persistent state if applicable;
* organisms without topology mutation if applicable.

But do not build controls that presuppose the mechanism.

The key question is:

Did the pressure alter the kinds of machinery evolution discovers?

Not merely:

Did fitness increase?

⸻

What to measure

Fitness alone is inadequate.

Record:

* lineage survival;
* adaptation speed;
* behavioral diversity;
* structural diversity;
* mutation survival;
* recovery after regime change;
* transfer performance;
* sensitivity to node/edge ablation;
* execution cost;
* state usage;
* topology;
* recurring motifs;
* lifetime behavioral trajectories.

Also preserve complete ancestry for interesting organisms.

For surprising winners, perform:

* ablations;
* transplant tests;
* replay under altered worlds;
* ancestry reconstruction;
* behavioral probes.

Do not immediately name structures after known mechanisms.

Describe behavior first.

For example, prefer:

“three-node recurrent structure whose activity predicts environmental switching”

over:

“memory module.”

Nyx/Harmonia-style anatomical interpretation can come later.

⸻

Primary scientific questions

1. Which pressure primitives consistently cause richer adaptive machinery to emerge?
2. Which pressures merely make search harder without creating useful structure?
3. Does combining conservative catastrophic pressure with rare high-value opportunities create conditional risk control?
4. Does severe resource scarcity accelerate reusable internal machinery rather than merely reduce performance?
5. Does lifetime nonstationarity generate self-modification or persistent internal state without explicitly rewarding either?
6. Can incompatible regimes induce spontaneous specialization and arbitration?
7. Can developmental encodings discover useful machinery faster than direct search?
8. Do transplant pressures produce mechanisms with cross-lineage utility?
9. Are there pressure combinations that produce qualitatively new structures not seen under either pressure alone?
10. Are there structures we cannot easily map onto familiar human-designed cognitive components?

The last category is particularly valuable.

⸻

Anti-goals

Do not:

* reproduce a Transformer;
* build an MoE and show that MoEs work;
* add a planner because planning should help;
* explicitly implement curiosity;
* explicitly implement fear;
* explicitly implement memory;
* explicitly implement uncertainty estimation;
* optimize benchmark performance;
* build an elaborate simulator before proving the toy concept works;
* spend days polishing infrastructure;
* interpret every recurrent structure as cognition.

A null result is useful.

If a pressure produces nothing interesting, record that and move on.

⸻

Serendipity protocol

When something unexpected appears:

1. freeze the organism and ancestry;
2. freeze the world and random seed;
3. reproduce it;
4. ablate it;
5. transplant it;
6. perturb the environmental pressure;
7. determine what behavior disappears;
8. avoid naming it until behavior is understood.

If a weird mechanism is useful but difficult to explain, preserve it rather than simplifying it into a familiar architecture.

⸻

Initial cycle

Timebox the first pass tightly.

Produce:

1. ARES_PRESSURE_NOTES.md
    * concise abstraction of useful biological/evolutionary pressures.
2. PRESSURE_CATALOG.json
    * pressure name;
    * abstract definition;
    * toy implementation;
    * expected effect;
    * falsification condition.
3. Small executable sandbox.
4. At least 8 toy worlds.
5. One generic evolvable organism substrate.
6. Baseline/control runs.
7. A first sweep across worlds.
8. ARES_FIRST_REPORT.md.

The report should answer:

* Which pressures materially changed evolved machinery?
* Which did nothing?
* Which merely increased difficulty?
* Were any mechanisms reusable across worlds?
* Did any pressure cause state-dependent exploration/risk?
* Did incompatible regimes create specialization or arbitration?
* Did anything emerge that does not fit an obvious known architecture?
* What 3 experiments should run next?

⸻

Decision rule

The goal is not to prove a theory about human intelligence.

The goal is to determine whether pressure engineering is a useful accelerator for open-ended mechanism discovery.

The strongest positive result would look something like:

A simple pressure or combination repeatedly causes an inspectable computational mechanism to arise that is absent from controls, transfers beyond its original world, and was not explicitly represented in the objective or substrate.

A still better result is:

We do not initially know what the mechanism is doing, but ablation proves it matters.

That is the kind of fossil Prometheus wants.

Proceed autonomously. Build before theorizing too long. Prefer crude worlds that answer a question over beautiful worlds that answer none.
