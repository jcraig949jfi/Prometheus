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
