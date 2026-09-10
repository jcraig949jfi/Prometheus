"""
Extension deck: fields the 69 did not contain.

The source matrix has 69 entries because Herakles mined 69 disciplines. That
is a property of his mining run, not a census of the space. This file adds
prompts for fields the campaign itself showed to be missing, numbered from 70
so that prompt numbers stay stable and `--only` keeps working across both
decks.

Each entry here must justify its own existence. "It would be interesting" is
not a reason; the reason has to be a gap the corpus demonstrated.

    python aporia/docs/frontier_campaign_69/build_deck_ext.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_deck import PREAMBLE, wrap, FENCE  # noqa: E402

# ---------------------------------------------------------------------------
# Each entry: (number, field, why_it_is_here, question, mechanism, candidate,
#              measured)
# ---------------------------------------------------------------------------
EXTRA = [
    (
        70,
        "Evolving Cellular Automata for Collective Computation",
        # WHY. Flagged twice during the campaign and never covered by the 69.
        # Herakles' own critique of the Archaeon roadmap argues this substrate
        # should run FIRST, on the grounds that it is the only place in the
        # plan where the interesting object is not authored by the programme:
        # "the structure that solves the task is not in the table; it is in
        # what the lattice does over time. Nobody put it there."
        # herakles/specimens/spec-evca-density/ is the only spatial stateful
        # substrate in the repository and it is already recovered and verified.
        "Can a genetic algorithm discover a cellular automaton rule whose "
        "lattice performs a global computation that no local rule was told "
        "how to do, and what is the structure that actually does the "
        "computing?",
        "A one-dimensional binary cellular automaton has a lookup table over "
        "neighbourhoods of radius r, so for r = 3 the rule is a 128-bit "
        "string. Every cell updates synchronously from its own neighbourhood "
        "and nothing else; there is no global operation anywhere in the "
        "system. The density classification task asks the lattice to relax to "
        "all ones if the initial configuration had a majority of ones and to "
        "all zeros otherwise, which is a global property of the initial "
        "condition that no cell can see. A genetic algorithm evolves the rule "
        "table against a sample of random initial conditions scored by "
        "whether the lattice reached the correct uniform state within a step "
        "budget. The interesting result is not the fitness. It is that the "
        "successful rules were found, on inspection of their space-time "
        "diagrams, to work by forming regular domains, with the boundaries "
        "between domains acting as travelling particles that carry "
        "information across the lattice and interact when they collide. That "
        "particle-and-collision structure is a description nobody encoded, in "
        "a system whose entire specification is a bit string.",
        "The candidate is the rule table itself, a bit string of length 2 to "
        "the power of the neighbourhood size, typically 128 bits. What varies "
        "is which bits are set. What is judged is the fraction of random "
        "initial conditions the resulting lattice classifies correctly.",
        "Classification accuracy over a sample of initial conditions, on a "
        "scale from 0 to 1, at a stated lattice size, density distribution and "
        "step budget. Separately and more importantly, whether particles and "
        "domains can be identified in the space-time diagrams, and by what "
        "method.",
    ),
    (
        71,
        "Unsupervised Environment Design",
        # WHY. Named as the absorbing field by TWO dossiers independently --
        # 24 Autocurricula and 26 Intrinsic Motivation -- and it is the
        # successor to POET, which IS in the 69 as prompt 6. The campaign
        # covered the ancestor and missed the descendant.
        "When an agent and the environments it trains on are optimised "
        "together, what decides which environment to generate next, and does "
        "any such rule provably keep producing environments the agent can "
        "still learn from rather than ones it has already mastered or cannot "
        "touch?",
        "A generator proposes environment parameters -- a maze layout, a "
        "terrain, a set of physics constants. A student policy is trained on "
        "them. Rather than scoring an environment by difficulty, which "
        "collapses onto the impossible, the generator scores it by REGRET: "
        "the gap between what the student achieves on that environment and "
        "what the best achievable policy would achieve. Environments with "
        "high regret are ones the student is failing but could learn, so the "
        "curriculum concentrates there. Regret is not directly computable, so "
        "the methods differ in what they substitute for it -- the gap between "
        "the student's return and the maximum return seen across a "
        "population, or the positive part of the temporal-difference error. "
        "The generator itself may be a learned adversary, or a random sampler "
        "whose outputs are merely CURATED by a replay buffer, and the "
        "surprising empirical result is that curation of random levels often "
        "matches or beats a learned adversary.",
        "The candidate is an environment: a parameter vector the generator "
        "emits. What varies is the level layout or the physics settings. What "
        "is judged is the estimated regret the student incurs on it, and "
        "downstream, whether training on the curriculum transfers to held-out "
        "environments the generator never produced.",
        "Estimated regret per environment, on the scale of the return. "
        "Downstream, zero-shot transfer performance on a fixed held-out set "
        "of human-designed levels, which is the only number that is not "
        "self-referential.",
    ),
    (
        72,
        "Reservoir Computing",
        # WHY. Named as the absorbing field by dossier 09, Artificial Gene
        # Regulatory Networks. It is the direct formalism for computation
        # performed by an untrained dynamical substrate, which is the same
        # question the cellular-automata line at prompt 70 asks, and it is
        # the one field in this area with a closed-form training step.
        "Can a fixed, randomly wired dynamical system do the computational "
        "work, so that only a linear readout has to be trained, and what "
        "property of the system decides whether it can?",
        "A reservoir is a large recurrent network whose internal weights are "
        "generated at random and then NEVER TRAINED. The input is injected "
        "into it and the reservoir's state evolves; the high-dimensional "
        "trajectory of that state is recorded. The only thing fitted is a "
        "linear map from reservoir states to the desired output, obtained in "
        "closed form by ridge regression, so there is no backpropagation "
        "through time and no gradient anywhere. The reservoir works because "
        "it projects the input history into a space where the task becomes "
        "linearly separable, and it does this only if its dynamics sit near "
        "the boundary between order and chaos -- controlled in practice by "
        "the spectral radius of the random weight matrix. The same argument "
        "has been made for physical substrates: buckets of water, photonic "
        "systems, memristor arrays and random Boolean networks have all been "
        "used as reservoirs, on the claim that the computation is a property "
        "of the dynamics rather than of any designed circuit.",
        "The candidate is the readout weights, which are the only trained "
        "object, though what is really under test is the reservoir: its size, "
        "spectral radius, input scaling and connection density. What is "
        "judged is prediction error on a held-out continuation of a time "
        "series.",
        "Normalised root-mean-square error on a held-out horizon, or the "
        "valid-prediction time before the forecast diverges from a chaotic "
        "target, measured in Lyapunov times so it is comparable across "
        "systems.",
    ),
    (
        73,
        "Unsupervised Skill Discovery",
        # WHY. Named as the absorbing field by dossier 28, Empowerment --
        # "the broader paradigm of skill discovery and representation
        # learning", and separately "Unsupervised RL". Empowerment is in the
        # 69; the field that absorbed it is not.
        "Without any reward, can an agent discover a set of distinct, "
        "reusable behaviours, and is the number it finds limited by the "
        "algorithm or by the objective itself?",
        "The agent learns a policy conditioned on a latent skill variable z "
        "drawn from a fixed distribution. Training maximises the mutual "
        "information between z and the states the policy visits, which is "
        "estimated with a learned discriminator that tries to predict which "
        "z produced an observed state. The policy is rewarded for reaching "
        "states that make the discriminator confident, so different z values "
        "are pushed toward visiting distinguishable regions. No task reward "
        "is used at any point. The standing objection is that mutual "
        "information is maximised as soon as the skills are merely "
        "DISTINGUISHABLE, which a set of policies that each stand still in a "
        "slightly different spot achieves perfectly, so the objective does "
        "not by itself demand that skills be far apart, dynamic, or useful. "
        "Later methods add an explicit distance or Lipschitz constraint to "
        "force coverage rather than mere separability.",
        "The candidate is a skill, meaning the policy obtained by "
        "conditioning on one value of the latent z. What varies is z. What is "
        "judged is how distinguishable the resulting state visitation is from "
        "that of the other skills.",
        "The discriminator's log-probability of the correct skill, which is a "
        "lower bound on the mutual information in nats. Separately, state "
        "coverage of the reachable space, and downstream task return when the "
        "discovered skills are frozen and used as primitives.",
    ),
    (
        74,
        "Emergent Self-Replication in Artificial Systems",
        # WHY. The most-named uncovered topic in the corpus: five dossiers
        # reference self-replication (01 Digital Evolution, 04 ALife, 30
        # ALife-inspired AI, 32 Autocatalytic Sets, 60 Evolutionary
        # Epistemology) and none of the 69 is about it. Both Avida and Tierra
        # BEGIN with a hand-written replicator, so the question of where the
        # first one comes from is assumed away by every template in the deck.
        "Can a self-replicating program arise from a soup that was never "
        "given one, and how would you tell an actual replicator from a "
        "pattern that merely persists?",
        "A population of random instruction sequences is placed in a shared "
        "memory and executed, usually with no fitness function and no "
        "selection imposed from outside. Nothing rewards replication. If a "
        "sequence happens to copy itself, its copies are also executed, so "
        "the copying is its own reward and the population composition shifts "
        "on its own. The historical systems seeded a hand-written ancestor "
        "and studied what evolution did to it afterwards, which assumes away "
        "the harder question. The interesting modern claim is that "
        "replicators arise SPONTANEOUSLY from random initial conditions in "
        "sufficiently expressive instruction sets, given long enough, and "
        "that the transition shows up as a sharp change in a measurable "
        "quantity such as the entropy of the instruction distribution or the "
        "length of the longest repeated substring in memory. The measurement "
        "problem is real: persistence, parasitism on another sequence's copy "
        "loop, and genuine autonomous self-copying all look similar from "
        "outside.",
        "The candidate is a sequence of instructions occupying a region of "
        "shared memory. Nothing is selected by an external scorer; what "
        "varies is what the soup happens to contain after execution. What is "
        "judged is whether a sequence causes copies of itself to appear.",
        "The time to first replicator, in executed instructions, which is a "
        "count with no upper bound and may be censored if none appears. "
        "Alongside it a continuous order parameter such as the entropy of the "
        "instruction distribution over time, whose drop is the claimed "
        "signature of the transition.",
    ),
    (
        75,
        "Lenia and Continuous Cellular Automata",
        # WHY. Named by three dossiers (01 Digital Evolution, which routed to
        # Leniabreeder, 04 ALife, 30 ALife-inspired AI) and covered by none.
        # It is the continuous generalisation of the substrate at prompt 70,
        # it is differentiable, and its objects of interest -- localised
        # self-maintaining patterns -- are found by search rather than
        # designed.
        "In a continuous cellular automaton, do coherent self-maintaining "
        "patterns exist as a matter of the update rule, and can they be "
        "searched for rather than designed?",
        "Lenia generalises Conway's Life along every axis at once: the state "
        "of a cell is a real number rather than a bit, the neighbourhood is a "
        "smooth radial kernel rather than eight cells, and time advances in "
        "small continuous increments rather than discrete ticks. The update "
        "convolves the grid with the kernel, passes the result through a "
        "smooth growth function, and adds a fraction of it back to the "
        "current state. Because every operation is differentiable, the whole "
        "system can be run inside an automatic differentiation framework on a "
        "GPU. What makes it interesting is what appears in it: localised, "
        "coherent, self-maintaining patterns that move, rotate and sometimes "
        "interact, which persist because the rule sustains them and were not "
        "put there. They are found by searching the space of kernel and "
        "growth parameters, and the search is the experiment.",
        "The candidate is a parameter vector: the kernel shape, the growth "
        "function's mean and width, and the initial pattern. What varies is "
        "those parameters. What is judged is whether the resulting pattern "
        "stays bounded and coherent rather than dying out or filling the "
        "grid.",
        "A survival or persistence measure over a fixed number of steps, plus "
        "continuous descriptors such as the mass of the pattern, its centre "
        "of mass displacement, and whether the mass stays within a bounded "
        "region, all on real scales.",
    ),
    (
        76,
        "Neural Cellular Automata and Differentiable Morphogenesis",
        # WHY. Named by dossiers 30 and 70. It is the one place in this whole
        # space where a LOCAL rule is trained by GRADIENT DESCENT to produce a
        # specified global outcome, which inverts the cellular-automata
        # question at prompt 70 -- there the global behaviour is searched for
        # blindly, here it is a target -- and it makes robustness and
        # regeneration directly measurable.
        "If every cell runs the same small learned rule and sees only its "
        "neighbours, can a target global structure be grown reliably, and "
        "does the rule that grows it also repair it when it is damaged?",
        "Each cell holds a vector of channels, some of which are visible as "
        "colour and the rest hidden. The update rule is a small neural "
        "network, identical in every cell, that reads a fixed perception of "
        "the cell's neighbourhood -- typically the cell state together with "
        "Sobel gradients of the surrounding field -- and outputs an increment "
        "to the cell's own state. The same rule is applied for many steps and "
        "the resulting image is compared to a target; the loss is "
        "backpropagated through all those steps to train the shared rule. "
        "Two details do the real work. Updates are applied stochastically per "
        "cell, so the rule cannot depend on global synchrony. And a pool of "
        "partially grown states is sampled from during training, with some "
        "samples deliberately damaged, which is what produces regeneration "
        "rather than a rule that only works from the exact seed.",
        "The candidate is the shared update rule, meaning the weights of the "
        "small network every cell runs. What varies is those weights, trained "
        "by gradient descent rather than searched. What is judged is how "
        "close the grown pattern is to the target, and whether it recovers "
        "after damage.",
        "Pixel-wise loss against the target after a stated number of steps, "
        "on a continuous scale. Separately, and more informative, the loss "
        "after a region of the grown pattern is deleted and the rule is left "
        "to run, which measures regeneration rather than growth.",
    ),
    (
        77,
        "World Models and Learned Simulators",
        # WHY. Referenced by NINE dossiers (03, 10, 27, 28, 34, 36, 62, 71,
        # 73) -- the most-referenced uncovered topic after self-replication --
        # and absent from the 69. It also answers a bench problem directly:
        # if experiments are expensive, a learned surrogate of the
        # environment is what makes a search affordable, and knowing when
        # that surrogate can be trusted is exactly what a bench must settle
        # before using one.
        "If an agent learns a model of its environment and then trains "
        "entirely inside that model, when does what it learned survive "
        "contact with the real environment, and how far into an imagined "
        "rollout can you go before the model's errors dominate?",
        "The system learns two things from logged experience. An encoder "
        "compresses each observation into a low-dimensional latent, and a "
        "recurrent dynamics model predicts the next latent and the reward "
        "from the current latent and action. Once trained, the dynamics "
        "model can be rolled forward without touching the environment at "
        "all, so a policy can be optimised on imagined trajectories, "
        "millions of them, at no environment cost. The failure mode is "
        "compounding error: each predicted step is slightly wrong, the error "
        "feeds into the next prediction, and a policy optimised on long "
        "rollouts learns to exploit places where the model is wrong rather "
        "than places where the environment rewards it. So the rollout "
        "horizon is a bounded resource, and the methods differ mainly in how "
        "they detect or penalise leaving the region the model was trained "
        "on.",
        "The candidate is the policy, optimised inside the learned model. "
        "What varies is its parameters. What is judged is its return when it "
        "is finally executed in the real environment rather than the "
        "imagined one.",
        "Real-environment return after training in imagination, on the "
        "task's own reward scale. Alongside it the model's prediction error "
        "as a function of rollout length, which determines the usable "
        "horizon and is the number that transfers between tasks.",
    ),
    (
        78,
        "Indirect and Generative Encodings",
        # WHY. This was one of Herakles' OWN mining topics -- his deck
        # produced 03_generative_and_developmental_representations.md -- and
        # none of the 69 templates covers it. The only survivor from that
        # topic is evodevo.bias.v0, which is Boolean networks and a different
        # question. A mining topic that yielded no template is a gap with a
        # paper trail, which is the strongest kind available here.
        "When a small genome is decoded into a much larger structure by a "
        "generative process rather than listed directly, does the regularity "
        "that decoding imposes actually help search, and can that be "
        "separated from the advantage of simply having fewer parameters?",
        "A direct encoding stores one gene per element of the phenotype, so "
        "a million-connection network needs a million genes. An indirect "
        "encoding instead stores a small program or function that is queried "
        "to produce the phenotype. In the compositional pattern producing "
        "network approach the genome is a small network of mathematical "
        "primitives, sine and gaussian and absolute value among them, and "
        "the phenotype is produced by querying it at each coordinate of a "
        "geometric layout, so symmetry, repetition, and repetition with "
        "variation fall out of the primitives used rather than having to be "
        "discovered independently at every location. The claim is that this "
        "bias matches the regularity of real problems and therefore helps. "
        "The confound is that indirect encodings also have far fewer "
        "parameters, so any advantage must be separated from ordinary "
        "dimensionality reduction, and the standard test is a task whose "
        "regularity can be destroyed while its difficulty is held fixed.",
        "The candidate is the compact genome, meaning the small generating "
        "network. What varies is its topology and weights. What is judged is "
        "the performance of the large phenotype it decodes into.",
        "Task performance of the decoded phenotype on the task's own scale, "
        "measured against a direct encoding at matched evaluation budget. "
        "The decisive comparison is the same task with its regularity "
        "scrambled, where the indirect encoding's advantage should vanish if "
        "it is exploiting regularity rather than compression.",
    ),
    (
        79,
        "Morphological Computation and Embodied Intelligence",
        # WHY. Referenced by six dossiers (10, 25, 26, 28, 46, 60) and
        # uncovered. It is the same claim as Reservoir Computing at prompt 72
        # -- that a physical substrate does computational work for free --
        # applied to bodies rather than networks, and it carries the sharpest
        # version of the measurement problem: how do you attribute work to a
        # body rather than to the controller acting through it?
        "How much of a behaviour is produced by the controller and how much "
        "by the body, and is there a way to measure that split which does "
        "not simply relabel one as the other?",
        "The claim is that the physical structure of a body, the compliance "
        "of a limb, the damping of a joint, the shape of a foot, performs "
        "part of the control problem, so that a much simpler controller "
        "suffices than the same task would need with a rigid body. The "
        "classic demonstrations are passive dynamic walkers, which walk down "
        "a shallow slope with no actuation and no controller at all, and "
        "compliant grippers that conform to an object without sensing its "
        "shape. In simulation the study is usually done by co-optimising the "
        "morphology and the controller together and comparing against a "
        "fixed morphology with the controller optimised alone. The hard part "
        "is attribution. A body that makes a task easy and a controller that "
        "solves it are not separable by inspection, and the measures "
        "proposed for the split, information-theoretic quantities computed "
        "over sensor and motor channels, depend on where the boundary "
        "between agent and environment is drawn, which is a modelling choice "
        "rather than a fact about the system.",
        "The candidate is a body and controller pair, where both may vary. "
        "What is judged is task performance, and separately how much the "
        "controller has to do to achieve it.",
        "Task performance on its own scale, alongside a controller "
        "complexity measure such as the number of parameters or the "
        "information rate between sensors and actuators in bits per step. "
        "The comparison that carries the claim is performance at matched "
        "controller complexity across morphologies.",
    ),
    (
        80,
        "Library Learning and Program Induction",
        # WHY. The best-grounded entry in the whole extension, because the
        # grounding is INTERNAL as well as corpus-side. Named by dossiers 36
        # and 42. And Aporia's own resume records that Q060's T2 demands a
        # leave-one-out non-redundancy test over an extensional-signature
        # closure which "DreamCoder, Stitch, babble, LILO and ShapeCoder have
        # never executed" -- with the P177 measurement that `double` reads
        # 4.2 percent and is therefore a named composition, while `rotate`
        # reads 99.2 percent and is a genuine generator. This dossier is a
        # literature check on a claim this seat has already made.
        "When a system invents a new primitive and adds it to its library, "
        "is that primitive a genuine new generator or just a name for a "
        "composition it could already express, and does anyone test which?",
        "The system alternates two phases. In the wake phase it searches for "
        "programs solving a batch of tasks, using its current library of "
        "primitives and a learned neural policy that proposes which "
        "primitives to try. In the sleep phase it examines the solutions it "
        "found, extracts subexpressions that recur across them, and promotes "
        "those subexpressions to named primitives in the library, so the "
        "next wake phase searches a space where those patterns cost one "
        "symbol instead of many. Compression is the promotion criterion: a "
        "candidate abstraction earns its place if adding it shortens the "
        "description length of the solution corpus. Later systems replace "
        "the expensive search over candidate abstractions with an exact "
        "method over e-graphs, or use a language model to propose and name "
        "them. The step that is never separately audited is whether a "
        "promoted primitive extends what the library can express at all, or "
        "merely shortens something already reachable.",
        "The candidate is an abstraction proposed for promotion into the "
        "library: a subexpression recurring across solved tasks. What varies "
        "is which subexpression. What is judged is the compression it buys "
        "over the solution corpus, and downstream, whether tasks unsolved "
        "before become solvable after.",
        "Description length of the solution corpus before and after "
        "promotion, in symbols, and the solve rate on held-out tasks at a "
        "fixed search budget. The measure that is NOT standard, and the one "
        "this report should hunt for, is a leave-one-out test: remove one "
        "library primitive, enumerate the closure of what remains more "
        "deeply, and report what fraction of the lost behaviours never comes "
        "back.",
    ),
    (
        81,
        "Swarm Intelligence and Stigmergy",
        # WHY. Referenced across six dossiers, with particle swarm named
        # specifically in three (53, 67, 69), and uncovered by the 69. It is
        # the canonical case of computation with NO central representation --
        # the structure lives in the environment rather than in any agent --
        # which is a different mechanism from every one of the 31 the matrix
        # found.
        "Can a colony of agents that share no plan and no global view solve "
        "a problem by modifying their shared environment, and is the "
        "resulting behaviour better explained by the agents or by the trace "
        "they leave?",
        "Each agent follows a simple local rule and deposits a signal into "
        "the environment -- a pheromone on a graph edge, a marker on a "
        "grid -- which decays over time and biases the choices of agents that "
        "arrive later. No agent holds the solution and none communicates "
        "directly with another. In ant colony optimisation, agents walk a "
        "graph choosing edges with probability weighted by deposited "
        "pheromone and by a local heuristic, then reinforce the edges of the "
        "better tours they found; evaporation is what stops early accidents "
        "from locking the colony in. The mechanism of interest is stigmergy: "
        "the coordination is carried entirely by modifications to the shared "
        "medium, so the environment is doing the remembering. Particle swarm "
        "optimisation is the continuous relative, where each particle is "
        "pulled toward its own best position and the swarm's best, and the "
        "standing critique is that its behaviour is dominated by the "
        "parameters controlling those two pulls rather than by anything "
        "swarm-like.",
        "The candidate is a solution constructed by one agent's walk, for "
        "instance a tour of a graph. What varies is the path taken, which is "
        "sampled from the pheromone field rather than chosen by any "
        "optimiser. What is judged is the cost of that solution, which then "
        "feeds back as deposit.",
        "Best and mean solution cost against a known optimum, on the "
        "problem's own scale, as a function of evaluations. Separately, a "
        "measure of the pheromone field itself, such as its entropy over "
        "time, which is what distinguishes a colony that is converging from "
        "one that has stagnated.",
    ),
    (
        82,
        "Self-Organised Criticality and the Edge of Chaos",
        # WHY. Named by dossiers 70 and 72, and it is the claim underneath
        # BOTH of them: the cellular-automata line says the interesting rules
        # sit near a phase transition, and reservoir computing says the
        # reservoir only works near the order-chaos boundary. It is also the
        # most-abused idea in this space, which makes its negative results
        # the point of asking.
        "Do systems that compute well actually sit at a critical point "
        "between order and chaos, and is that a measured property or a story "
        "told after the fact?",
        "A system is tuned by one parameter -- the fraction of ones in a "
        "cellular automaton rule table, the spectral radius of a reservoir, "
        "the mean connectivity of a random Boolean network -- and its "
        "dynamics change character as that parameter is swept. At low values "
        "perturbations die out and the system freezes; at high values they "
        "spread and the system is chaotic; between them is a narrow region "
        "where a perturbation neither dies nor explodes. The claim, made "
        "repeatedly since the late 1980s, is that this region is where "
        "systems can store, transmit and combine information, and therefore "
        "where computation is possible. It is measured by order parameters "
        "such as the Lyapunov exponent, the size distribution of avalanches, "
        "or the divergence rate of two initially close configurations. The "
        "history matters as much as the claim: the original demonstration "
        "linking a specific rule-table statistic to computational capability "
        "was challenged on the grounds that the correlation reflected the "
        "genetic algorithm's search bias rather than a property of the rule "
        "space, and that dispute is the most instructive thing in the field.",
        "The candidate is a system instance at a given setting of the "
        "control parameter: one rule table, one reservoir, one network. What "
        "varies is the control parameter. What is judged is a dynamical order "
        "parameter, and separately whether the system can perform a "
        "computational task.",
        "A dynamical order parameter on a continuous scale -- Lyapunov "
        "exponent, avalanche size exponent, or normalised Hamming distance "
        "growth between perturbed and unperturbed runs -- paired with task "
        "performance measured independently, so that the correlation between "
        "them is the result rather than the assumption.",
    ),
    (
        83,
        "Open-Endedness Metrics and Evolutionary Activity",
        # WHY. This is the question Herakles' critique says the Archaeon
        # roadmap never asks: "what would a serendipitous result look like,
        # and how would we know one if it happened?" The word novelty appears
        # in four roadmap documents and in every case means an EXPLORATION
        # BUDGET, never a definition of a novel finding. Evolutionary activity
        # statistics are the one existing attempt to MEASURE open-endedness
        # rather than assert it, and they are named by dossiers 01 and 30.
        # Nothing in the 82 covers the measurement problem itself.
        "Is there any measure that can look at a running system and say "
        "whether it is still producing genuinely new things, as opposed to "
        "rearranging what it already had, and does that measure survive "
        "being applied to a system known to be going nowhere?",
        "Evolutionary activity statistics count, for each component in a "
        "system, how long it has persisted and how much it has been used, "
        "then aggregate those counts into a small number of curves: how much "
        "total activity the system carries, how much of that belongs to "
        "components that are new, and whether the new-component activity "
        "keeps arriving or dies away. The decisive move is the SHADOW "
        "RUN: the same system is re-run with heredity removed, or with "
        "components drawn at random from the same distribution, so that any "
        "activity present in the shadow is activity the mechanism did not "
        "earn. Open-endedness is then claimed only for activity that exceeds "
        "the shadow. The critiques are as important as the method. The "
        "statistics depend on what is counted as a component, which is a "
        "modelling decision; they can be inflated by a system that merely "
        "accumulates junk that persists; and several published claims of "
        "unbounded activity were later attributed to the choice of shadow "
        "rather than to the system under test.",
        "The candidate is a component of the evolving system -- a gene, a "
        "rule, an organism type -- whose persistence and usage are counted. "
        "What varies is what the system produces over time. What is judged "
        "is whether the component's activity exceeds what the shadow "
        "produces.",
        "New-component activity per unit time, on a count scale, plotted "
        "against the shadow run rather than against zero. The verdict is "
        "categorical -- bounded, unbounded, or shadow-dominated -- and the "
        "shadow is what makes it a measurement rather than an assertion.",
    ),
    (
        84,
        "Fitness Landscape Structure: Epistasis, Neutrality and Ruggedness",
        # WHY. The most-named uncovered cluster in the corpus: epistasis in
        # four dossiers (10, 11, 12, 49), neutral networks in two (08, 70).
        # And it sits directly under the Archaeon roadmap's Branch A, which
        # proposes an NK landscape with k > 0 to replace a landscape Herakles
        # measured as flat -- solvable by a one-flip hill climber in exactly L
        # queries. Branch A has no test that the chosen k actually makes the
        # landscape hard, which is his objection O-1. This is the literature
        # that would supply one.
        "Given a landscape, how do you measure whether it is actually hard, "
        "how much of its difficulty comes from interaction between loci "
        "rather than from the number of them, and how much of it can a "
        "search simply walk around for free?",
        "A fitness landscape assigns a value to each point in a discrete "
        "space of genotypes, and its difficulty is a structural property "
        "that can be measured before any search is run. The NK model makes "
        "the structure a parameter: each of N loci contributes a value that "
        "depends on itself and K others, so K = 0 gives a single-peaked "
        "additive landscape solvable one locus at a time, and increasing K "
        "raises the number of local optima toward randomness. The measures "
        "that matter are the number and basin sizes of local optima, the "
        "autocorrelation of fitness along a random walk, which gives a "
        "correlation length, and the fraction of neighbouring genotypes with "
        "equal fitness, which defines neutral networks -- connected plateaus "
        "a population can drift along at no cost, reaching distant regions "
        "without ever crossing a valley. Neutrality changes the problem "
        "qualitatively: a landscape can be rugged by every peak-counting "
        "measure and still be easy, because the plateaus connect.",
        "The candidate is a genotype, a point in the space. What varies is "
        "the landscape's own parameters, N and K and the neutrality "
        "fraction, rather than any individual solution. What is judged is a "
        "structural statistic of the landscape itself.",
        "Number of local optima and their basin sizes, as counts; fitness "
        "autocorrelation and its correlation length, continuous; neutral "
        "fraction, between 0 and 1. Crucially, alongside these, the actual "
        "query count a one-flip hill climber needs, because a landscape "
        "whose measured ruggedness does not raise that count is not doing "
        "the work its parameters claim.",
    ),
    (
        85,
        "Evolvability and the Evolution of Robustness",
        # WHY. Named by three dossiers (04, 08, 32) and uncovered. It is also
        # the field that addresses the failure recorded in
        # feedback_gen_30_wall: self-improving systems hit a bounded-menu
        # wall, and what is needed is MENU GROWTH rather than deeper search
        # within a fixed menu. Evolvability is the name that literature gives
        # to the capacity to generate useful variation, and the question of
        # whether it can itself be selected for is exactly the question
        # underneath that wall.
        "Can a system's capacity to produce useful new variation itself "
        "increase over time, and is that a real effect or an artefact of "
        "measuring it on the population that produced it?",
        "Robustness is the fraction of mutations that leave the phenotype "
        "unchanged; evolvability is the capacity to produce phenotypes that "
        "are new and viable. Naively these oppose each other, since a "
        "genotype insensitive to mutation produces less variation. The "
        "resolution proposed in the RNA and protein literature is that "
        "robustness creates neutral networks, a population drifts along one "
        "while accumulating cryptic genetic variation that is currently "
        "silent, and that reservoir is released as phenotypic variation when "
        "the environment or the genetic background changes. So robustness "
        "and evolvability are in tension at the level of an individual and "
        "aligned at the level of a population. The measurement problem is "
        "severe and is the reason to ask: evolvability is usually measured "
        "as the variance of fitness effects among a genotype's mutational "
        "neighbours, which is computed over the very population whose "
        "history produced the genotype, so an apparent increase can be a "
        "property of where the population has been rather than of what it "
        "can now do.",
        "The candidate is a genotype together with its mutational "
        "neighbourhood. What varies is the genotype and the background it "
        "sits in. What is judged is how many distinct viable phenotypes its "
        "neighbourhood contains, and how many of those are new.",
        "The count of distinct viable phenotypes reachable in one mutational "
        "step, and the fraction of those not already present in the "
        "population, both as counts. The comparison that carries the claim "
        "is against genotypes drawn from a distribution matched in fitness "
        "but not in history, since matching on fitness alone is what "
        "separates an evolvability effect from a survivorship effect.",
    ),
    # -----------------------------------------------------------------
    # 86 to 97: the remaining topics named by two or more dossiers.
    # Five of the seventeen are NOT here because they are already covered
    # and a duplicate would cost a token for nothing:
    #     epistasis, neutral networks  -> 84
    #     evolvability                 -> 85
    #     evolutionary activity        -> 83
    #     echo state networks          -> 72, whose anchor IS the reservoir
    # -----------------------------------------------------------------
    (
        86, "Evolutionary Model Merging",
        # WHY. Four dossiers (03, 05, 07, 29). Uncovered.
        "Can two trained models be combined into a better one without any "
        "gradient training, and is the gain a real capability or an "
        "averaging artefact that a fair baseline would erase?",
        "Model merging combines the weights of several models fine-tuned "
        "from a shared base into a single model, arithmetically rather than "
        "by training. The simplest form averages weights. Task arithmetic "
        "treats the difference between a fine-tuned model and its base as a "
        "task vector that can be added, negated to remove a behaviour, or "
        "combined. Later methods resolve interference between task vectors "
        "by trimming small components and reconciling sign conflicts. The "
        "evolutionary version searches the merge coefficients, and "
        "optionally the layer-wise permutation, with a population method "
        "against a held-out score, which is what makes it an experiment "
        "rather than a formula. The whole approach depends on the merged "
        "models sharing a base, so that their weights sit in the same "
        "linearly connected basin.",
        "The candidate is a vector of merge coefficients, one per source "
        "model or per layer. What varies is those coefficients. What is "
        "judged is the merged model's score on held-out tasks.",
        "Held-out task accuracy of the merged model, against each source "
        "model and against a uniform-average baseline, which is the "
        "comparison that separates a real gain from arithmetic.",
    ),
    (
        87, "Symbolic Execution and Constraint-Based Test Generation",
        # WHY. Three dossiers (35, 36, 38). Formal Methods at 38 covers model
        # checking; this is the path-constraint line and is distinct.
        "Can a program be explored by treating its inputs as symbols rather "
        "than values, and what actually stops it -- the number of paths, or "
        "the solver?",
        "Instead of running a program on concrete inputs, symbolic execution "
        "runs it on symbols, building a path condition: a formula recording "
        "the branch choices taken to reach the current point. At each branch "
        "the engine asks a constraint solver whether each side is "
        "satisfiable, and forks where both are. Solving a path condition "
        "yields a concrete input that drives the program down exactly that "
        "path, which is how the technique generates tests and finds crashes. "
        "The obstacle is path explosion, since loops and calls multiply "
        "paths exponentially, and the practical systems are hybrids: "
        "concolic execution runs a concrete input alongside the symbolic "
        "state and flips one branch at a time, which trades completeness for "
        "reach. The second obstacle is the solver, since path conditions "
        "with nonlinear arithmetic or string operations can be intractable "
        "even when few paths remain.",
        "The candidate is a path condition, a conjunction of branch "
        "constraints. What varies is which branches were taken. What is "
        "judged is whether it is satisfiable and what input satisfies it.",
        "Coverage achieved as a fraction of branches or lines, plus the "
        "count of distinct crashes found, both against a fixed time budget, "
        "since every result in this field is budget-relative.",
    ),
    (
        88, "Self-Play and League Training",
        # WHY. Three dossiers (07, 21, 24). Coevolution at 7 covers
        # host-parasite; this is the modern competitive-agent line with its
        # own failure mode.
        "When an agent trains only against copies of itself, what stops it "
        "from cycling forever between strategies that each beat the last?",
        "The agent plays against itself, and the opponent it faces is drawn "
        "from its own history. Naive self-play faces only the current "
        "policy, which produces strategic cycling: the policy learns to beat "
        "its immediate predecessor, forgets what beat the one before, and "
        "the cycle closes. Fictitious self-play instead plays against the "
        "average of all past policies. League training generalises this by "
        "maintaining a population with distinct roles -- main agents, "
        "exploiters trained specifically to defeat the current main agent, "
        "and league exploiters trained against everything -- so that a "
        "weakness is found deliberately rather than waited for. The measure "
        "that matters is not win rate against the current opponent, which is "
        "self-referential, but performance against a held-out fixed "
        "population.",
        "The candidate is a policy. What varies is its parameters and which "
        "opponents it was exposed to. What is judged is its performance "
        "against opponents it did not train against.",
        "Win rate against a frozen held-out opponent set, and separately a "
        "measure of cycling such as the rank of the payoff matrix over "
        "policy history, which reveals a non-transitive game that no single "
        "score can summarise.",
    ),
    (
        89, "Phenotypic Plasticity and the Baldwin Effect",
        # WHY. Three dossiers (01, 04, 08). Evo-Devo at 8 is genotype-to-
        # phenotype maps; this is lifetime learning feeding back into
        # evolution, a different mechanism.
        "If individuals can learn during their lifetime, does that speed up "
        "evolution or slow it down, and can a learned behaviour become "
        "innate without ever being inherited directly?",
        "Each individual has a genotype specifying part of its behaviour and "
        "leaves the rest plastic, to be fixed by learning during its "
        "lifetime. Fitness is evaluated after learning. Nothing learned is "
        "written back to the genome, so this is not Lamarckian. The claimed "
        "effect has two phases. First, learning smooths the fitness "
        "landscape: genotypes near a good solution can reach it by learning, "
        "so selection can see a gradient where the raw landscape had none, "
        "and evolution finds the region faster. Second, once the population "
        "sits in that region, individuals that need less learning to get "
        "there are fitter because learning is costly or risky, so the trait "
        "becomes genetically fixed -- assimilated. The classic demonstration "
        "used a neural network with some connections fixed by genes and "
        "others learned, on a target that random search could not find. The "
        "standing objection is that the effect depends on learning having a "
        "cost, and that the original demonstration's landscape was a needle "
        "in a haystack chosen to make the effect visible.",
        "The candidate is a genotype specifying which traits are fixed and "
        "which are left plastic. What varies is that allocation. What is "
        "judged is fitness after a lifetime of learning.",
        "Generations to reach a fitness threshold, compared against a "
        "no-learning control on the same landscape, plus the fraction of "
        "traits genetically fixed over time, which is what shows "
        "assimilation rather than merely faster search.",
    ),
    (
        90, "Neuromorphic and Spiking Computation",
        # WHY. Three dossiers (72, 76, 82). Uncovered.
        "Does computing with discrete events in continuous time buy anything "
        "that a conventional network cannot, once you control for the "
        "hardware it runs on?",
        "A spiking neuron integrates incoming current and emits a discrete "
        "spike when its membrane potential crosses a threshold, then resets. "
        "Information is carried by spike timing and rate rather than by "
        "continuous activations, and because a neuron is silent unless it "
        "spikes, computation is event-driven and consumes energy only on "
        "activity. The training problem is that the threshold is not "
        "differentiable, so gradients do not flow; the standard workaround "
        "substitutes a smooth surrogate for the derivative during the "
        "backward pass while keeping the hard threshold forward. The claims "
        "made for the approach are energy efficiency on event-driven "
        "hardware and native handling of temporal data. The confound is "
        "severe and is the reason to ask: an energy comparison between a "
        "spiking network on neuromorphic hardware and a conventional network "
        "on a GPU measures two hardware platforms, not two algorithms.",
        "The candidate is the network's weights and, in some formulations, "
        "its per-neuron time constants. What varies is those parameters. "
        "What is judged is task accuracy together with spike count, which is "
        "the proxy for energy.",
        "Task accuracy on its own scale, paired with total spike count or "
        "synaptic operations, so the accuracy-per-operation trade-off is the "
        "reported result rather than accuracy alone.",
    ),
    (
        91, "Inductive Program Synthesis from Examples",
        # WHY. Three dossiers (36, 42, 80). Library learning at 80 is
        # abstraction over solved tasks; this is the prior step, getting a
        # program from input-output pairs at all.
        "Given only a handful of input-output pairs, can a program be found "
        "that produces them, and how do you choose among the many programs "
        "that fit?",
        "The system is given examples and searches a space of programs in a "
        "restricted language for one consistent with all of them. The "
        "language is deliberately limited -- string transformations, list "
        "operations, grid manipulations -- because unrestricted search is "
        "hopeless. Three families do the work. Enumerative search generates "
        "programs in order of increasing size, with observational "
        "equivalence pruning: two programs producing identical outputs on "
        "the examples are interchangeable, so only one need be kept, which "
        "collapses the space enormously. Constraint-based methods encode the "
        "whole synthesis problem for a solver. Neural methods learn to "
        "predict which primitives are likely, and guide the search rather "
        "than replace it. The deep issue is that many programs fit a few "
        "examples and they disagree everywhere else, so the ranking prior -- "
        "usually shortest program, sometimes a learned one -- is doing as "
        "much work as the search.",
        "The candidate is a program in the restricted language. What varies "
        "is its structure. What is judged is consistency with the given "
        "examples, and then its rank under the prior.",
        "Fraction of held-out tasks solved within a fixed time and node "
        "budget, plus generalisation accuracy on inputs not among the "
        "examples, which is the number that exposes whether the prior is "
        "picking the right program among those that fit.",
    ),
    (
        92, "Curriculum Learning and Task Ordering",
        # WHY. Three dossiers (24, 26, 75). UED at 71 generates environments;
        # this is the narrower question of whether ORDER alone matters.
        "Does the order in which training examples are presented change what "
        "is learned, holding the examples themselves fixed?",
        "The examples are the same and only their sequence differs, usually "
        "easy to hard by some difficulty measure, so any effect is "
        "attributable to ordering alone. Self-paced variants make difficulty "
        "relative to the current model, selecting examples the model finds "
        "neither trivial nor impossible, which is measured by loss or by "
        "learning progress -- the rate of change of performance rather than "
        "performance itself. The evidence is genuinely mixed, and that is "
        "why this is worth a report rather than a summary: curricula help "
        "reliably in some settings and are indistinguishable from random "
        "ordering in others, with the strongest replicated effects appearing "
        "under noisy labels or limited data, and the weakest appearing "
        "exactly where large models and abundant data make ordering "
        "irrelevant.",
        "The candidate is an ordering, or a policy that produces one. What "
        "varies is the sequence. What is judged is final performance and "
        "how quickly it was reached.",
        "Final held-out accuracy and steps to a fixed accuracy threshold, "
        "both against a shuffled-order control on identical data, since a "
        "curriculum result without that control measures the dataset.",
    ),
    (
        93, "Automated Program Repair and Genetic Improvement",
        # WHY. Two dossiers (35, 45). Uncovered, and it carries one of the
        # cleanest documented instances of a benchmark measuring the wrong
        # thing, which is directly useful to this programme.
        "Can a program be patched automatically so its tests pass, and does "
        "a patch that passes the tests actually fix the bug?",
        "A repair system takes a program with a failing test, localises the "
        "likely faulty statements by correlating them with failing runs, "
        "generates candidate edits -- by mutation, by templates drawn from "
        "human patch histories, by constraint solving, or by a language "
        "model -- and accepts an edit when the whole test suite passes. "
        "Genetic improvement is the same machinery aimed at a non-functional "
        "property such as speed or energy, keeping behaviour fixed. The "
        "central and well-documented problem is overfitting to the test "
        "suite: a patch that deletes the failing functionality, or "
        "special-cases the test input, passes. Independent assessment "
        "found that a large fraction of patches accepted by early systems "
        "were plausible but incorrect when judged against held-out tests or "
        "by human review, and the field's response was to separate the "
        "PLAUSIBLE rate from the CORRECT rate, which is the distinction a "
        "reader must carry into every number reported here.",
        "The candidate is a patch, an edit to the source. What varies is the "
        "edit. What is judged is whether the test suite passes -- which is "
        "not the same as whether the bug is fixed.",
        "Number of bugs with a plausible patch and, separately and always, "
        "the number with a CORRECT patch judged against held-out tests or "
        "human review. Reporting only the first is the field's known "
        "failure mode.",
    ),
    (
        94, "In-Context Learning",
        # WHY. Two dossiers (19, 56). Meta-learning at 19 names it as its own
        # absorbing field, which makes it a documented successor the deck
        # does not cover.
        "When a model improves at a task from examples in its prompt without "
        "any weight change, is it learning from those examples or "
        "recognising a task it already knows?",
        "Examples are placed in the context window and the model's "
        "performance on a new query improves, with no gradient step taken. "
        "Two accounts compete. On the learning account the forward pass "
        "implements something like an optimisation step over the in-context "
        "examples, and constructions exist showing a transformer CAN encode "
        "gradient descent on a linear problem in its attention layers. On "
        "the retrieval account the examples merely identify which "
        "pre-trained capability to apply, and the evidence for this is "
        "sharp: replacing the labels in the examples with RANDOM labels "
        "often barely degrades performance, which a genuine learner should "
        "not tolerate, though the effect depends heavily on model scale and "
        "task, and the label-insensitivity itself weakens with larger "
        "models. Distinguishing the accounts requires tasks the model "
        "cannot have seen, which is why synthetic function classes rather "
        "than natural language benchmarks carry the load.",
        "The candidate is the set of in-context examples: how many, which "
        "ones, in what order, with what labels. What varies is that set. "
        "What is judged is accuracy on a held-out query.",
        "Query accuracy as a function of the number of in-context examples, "
        "and the same curve with labels randomised, since the gap between "
        "those two curves is the measurement that separates the two "
        "accounts.",
    ),
    (
        95, "E-Graphs and Equality Saturation",
        # WHY. Two dossiers (42, 80). Named inside library learning as the
        # machinery under Babble, but never examined as a technique.
        "Can you apply every rewrite rule to a term at once, keeping all "
        "results, and then pick the best -- avoiding the ordering problem "
        "that makes rewriting fragile?",
        "Ordinary term rewriting applies rules in sequence, so an early "
        "rewrite can destroy the structure a later rule needed, and the "
        "outcome depends on the order chosen. An e-graph stores a set of "
        "equivalent terms compactly: nodes are grouped into equivalence "
        "classes, and a node's children are classes rather than individual "
        "terms, so one small structure can represent exponentially many "
        "equivalent expressions. Equality saturation applies every rule "
        "everywhere repeatedly, adding the results into the e-graph rather "
        "than replacing anything, until no rule adds new information or a "
        "budget expires. Only then is a single best term extracted, by a "
        "cost function over the saturated graph. The technique is "
        "destructive-rewrite-free, which is the whole point, and its limits "
        "are that saturation may never terminate and that extraction under "
        "a non-additive cost function is itself hard.",
        "The candidate is a term to be extracted from the saturated "
        "e-graph. What varies is which representative is chosen from each "
        "equivalence class. What is judged is the cost of the extracted "
        "term.",
        "Cost of the extracted term under the stated cost function, against "
        "the input term's cost, plus whether saturation was reached or the "
        "budget expired, which must always be reported because an "
        "unsaturated result is a lower bound on what the rules could find.",
    ),
    (
        96, "Differentiable Simulation",
        # WHY. Two dossiers (70, 75). Distinct from Neural CA at 76: there
        # the RULE is learned, here the PHYSICS is differentiated, and the
        # gradient pathology is specific to contact.
        "If a physics simulator is written so gradients can flow through it, "
        "can you optimise a design or a controller directly by gradient "
        "descent, and where does that break?",
        "The simulator's timestep is implemented in an automatic "
        "differentiation framework, so the derivative of a final state with "
        "respect to initial conditions, material parameters or control "
        "inputs is available by backpropagating through the whole rollout. "
        "This turns design into direct optimisation and can be orders of "
        "magnitude more sample-efficient than a search that only sees "
        "returns. Two failure modes are structural rather than incidental. "
        "Contact and collision make the dynamics discontinuous, so the true "
        "gradient is undefined or wildly wrong at exactly the moments that "
        "matter, and simulators substitute a smoothed contact model whose "
        "gradient is well-behaved but describes a different physics. And "
        "backpropagating through long rollouts produces exploding or "
        "vanishing gradients for the same reason recurrent networks do, so "
        "the horizon must be truncated, which biases the gradient.",
        "The candidate is a parameter vector: a control sequence, a material "
        "property, or a shape. What varies is those parameters. What is "
        "judged is a scalar objective computed from the simulated "
        "trajectory.",
        "Objective value against wall-clock and against sample count, "
        "compared with a gradient-free baseline on the same objective, "
        "because the claim being tested is efficiency rather than "
        "attainability. Gradient norm over rollout length should be reported "
        "alongside, since it is what exposes the truncation bias.",
    ),
    (
        97, "Chemical Reaction Networks as Computation",
        # WHY. Two dossiers (31, 32). Adjacent to Artificial Chemistry at 31
        # and Autocatalytic Sets at 32, but a distinct formalism: here the
        # network is a PROGRAMMING MODEL with proved expressiveness results.
        "What can a well-mixed set of chemical reactions compute, and is the "
        "answer different when molecule counts are small enough that "
        "randomness matters?",
        "A chemical reaction network is a set of species and reactions with "
        "rate constants. Treated deterministically at high copy number it is "
        "a system of ordinary differential equations; treated stochastically "
        "at low copy number it is a Markov chain over integer counts, and "
        "the two can give qualitatively different answers, which is the "
        "interesting part. As a programming model the network is the "
        "program and the molecular counts are the state, and the results are "
        "genuinely theorems rather than demonstrations: deterministic "
        "networks compute a characterised class of functions, stochastic "
        "networks can be Turing universal but only with a nonzero "
        "probability of error, and that error cannot be driven to zero while "
        "keeping the speed. DNA strand displacement gives a physical "
        "implementation, so a designed network can be compiled to real "
        "molecules, which makes the field one of the few here where the "
        "in-silico result has a wet-lab counterpart.",
        "The candidate is a reaction network: the species, the reactions and "
        "their rate constants. What varies is that network. What is judged "
        "is whether its dynamics compute the intended function, and under "
        "which of the two semantics.",
        "For the deterministic semantics, convergence of the output species "
        "concentration to the target value. For the stochastic semantics, "
        "the probability of a correct answer and the expected time to reach "
        "it, since correctness is probabilistic by construction and a report "
        "of one without the other is incomplete.",
    ),
]


def build() -> str:
    out = [
        "# Frontier Practitioner deck -- extension",
        "",
        "Prompts 70 and up: fields the original 69 did not contain.",
        "Numbering continues from deck.md so --only works across both.",
        "Rationale for each entry is in build_deck_ext.py::EXTRA.",
        "",
        "---",
        "",
    ]
    # The rationale for each entry is a COMMENT above it, not a tuple field,
    # so the tuple is exactly (number, field, question, mechanism, candidate,
    # measured). Indexing it as though `why` were an element shifted every
    # field by one and raised IndexError on the last.
    for n, field, question, mechanism, candidate, measured in EXTRA:
        body = PREAMBLE.format(
            field=field,
            question=wrap(question),
            mechanism=wrap(mechanism),
            candidate=wrap(candidate),
            measured=wrap(measured),
        )
        assert FENCE not in body, f"prompt {n} contains a fence"
        assert "[" not in body and "]" not in body, f"prompt {n} has a bracket"
        out += [f"### Prompt {n}: {field}", "", FENCE, body.rstrip(), FENCE, ""]
    return "\n".join(out)


if __name__ == "__main__":
    deck = build()
    path = HERE / "deck_ext.md"
    path.write_text(deck, encoding="utf-8")
    print(f"wrote {path} ({len(deck)} chars, {len(EXTRA)} prompts)")
