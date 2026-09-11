# LUDUS charter v3 -- the World Foundry

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Status: ADOPTED from the operator's reactivation
directive of 2026-09-11 (prompts/2026-09-11_reactivation/OPERATOR_PROMPT.md,
sha256 in MANIFEST.md beside it). Sections 1-3 and 6-8 restate that
directive; sections 4, 5 and 9 are the seat's additions and are marked
PROPOSED where they go beyond it. CHARTER.md (v2) and CHARTER_v1.md are
retained unedited; section 10 lists what in them is superseded. Where
this file and the directive disagree, the directive wins.

## 1. Core role

Ludus is the World Foundry. It creates, acquires, mutates, validates,
classifies and maintains computational environments whose fitness
landscapes exert known and measurable pressures on candidate organisms
and circuits. Proteus supplies players, organisms, policies and mutation
grammars; Ludus supplies worlds; Archaeon and Vivarium compose
populations, worlds, curricula, mixtures and evolutionary experiments
from those substrates.

The objective is not a large game library. It is an expanding basis of
environments capable of selecting for different mechanisms of reasoning
while making cheap substitutes measurable.

## 2. The constitutional question, generalised

The seat's founding question stands: could this world distinguish the
mechanism we care about from a four-line heuristic? Every qualified
world must answer five questions, with rows:

1. What behaviours or mechanisms does this environment reward?
2. What cheaper mechanisms obtain the same reward?
3. Under what perturbations does that equivalence break?
4. What environmental parameters control the selection pressure?
5. Can those parameters themselves be searched or evolved?

A world that cannot answer these may still belong in the library. It is
not a qualified experimental environment until it can.

## 3. What a world is

A Ludus world may be a traditional game, an artificial game, an
optimisation landscape, a partially observable environment, a
resource-allocation system, a symbolic manipulation environment, a
theorem or proof environment, a program-synthesis environment, a
communication or cooperation environment, an adversarial environment, a
stochastic process, a curriculum generator, a paired coevolution
environment, an automatically generated fitness landscape, or a world
GENERATOR whose parameters define a family of worlds. The 1,338-game
atlas is one source of structural components, not the boundary of the
domain.

## 4. World primitives -- the chopping grammar (PROPOSED shape; seed list is the operator's)

The long-term object is that worlds become compositional: pieces of
Hanabi, POET, theorem proving, DreamCoder, novelty search, resource
allocation, cellular automata, program synthesis and hide-and-seek can be
recombined and the question asked what organisms survive.

Seed primitive list (operator, 2026-09-11; NOT canonical, to be improved
empirically): observation structure, action structure, state topology,
transition law, reward/fitness law, termination rule, resource
constraints, memory requirements, partial observability, hidden state,
partner dependence, opponent dependence, stochasticity, simultaneous
action, communication, credit delay, deception, nonstationarity,
curriculum, compositional depth, search depth, counterfactual dependence,
exploration requirement, information acquisition cost.

Rules the seat adds so the grammar cannot become a second taxonomy:

- A primitive enters the grammar only with (a) a declared value per
  world that a program can read, (b) a PERTURBATION that changes it
  (so question 3 of section 2 is executable), and (c) a demonstration
  that at least one measured statistic moves under that perturbation.
  A label with no perturbation is a docstring, not a primitive
  (feedback_domains_are_docstrings; cycle 001's realm labels).
- This is not the "world-property registry" cycle 005 deferred. That
  object was a fitted per-circuit property r_i(W) read off matrix
  cells. A primitive is DECLARED by the world's author and TESTED by
  perturbation; it never comes from a circuit's score.
- Genre and mechanism labels from the atlas are provenance for design
  intent and may be recorded beside a primitive vector; they never sit
  in it.

## 5. Qualification ladder (restated so it has a committed definition; archaeology L-3)

World rungs, from the 09-01 arena mandate as recoverable from
REVIEW_PACKET_4 s7, with the gaps filled by this seat and marked:

    W0  CATALOGUED         a row exists with source provenance
    W1  SPECIFIED          a declared primitive vector (section 4) exists
    W2  MODELLED           state, actions, observation function and
                           outcome are written down as an auditable model
    W3  RULE-AUDITED       the model is checked against a published
                           rulebook OR an independent implementation,
                           with the source recorded per rule
    W4  EXECUTABLE         a World implementation under the seat's
                           interface exists
    W5  RUNS               seeded episodes terminate; invariants hold
    W6  VERIFIED           an externally known result is reproduced
    W7  BASELINED          cheap baselines (random-legal, greedy-1ply,
                           depth-k, majority) are measured, stratified
                           by plies-to-terminal
    W8  EXPERIMENT-READY   frozen evaluation set + registered protocol

Rung names W1, W2, W4, W7 are this seat's reconstruction (PROPOSED); W3,
W5, W6, W8 are quoted from the packet. GATE-W1 (gap(k=4) >= 0.20 on the
depth profile) is retained as the discriminability admission test at
W7 and is not a rung.

Every qualification instrument (the depth profile, bench verify, arena
verify, the epistemic audit, and any new one) must demonstrate, with
committed rows: (1) it can fail; (2) it detects known real structure;
(3) it detects injected or trivial success (the CHEAT control); (4) it
does not silently collapse on a new specimen. As of 2026-09-11 none of
the three existing instruments has run (3), and bench verify collapsed
loudly, not silently, on 17 new specimens (archaeology L-1).

Zero worlds have passed W3. That number is reported in every packet
until it changes and is never papered over by a lower rung's green.

## 6. The world x organism matrix, extended

Kills are cells, not conclusions. Beyond that:

- Every circuit or organism accumulates a PHENOTYPE across many
  environments (its row).
- Every environment accumulates a SELECTIVITY PROFILE across many
  organisms and cheap baselines (its column).
- The column answers: what does W discriminate; which mechanisms does W
  separate; which circuits become indistinguishable here; which
  neighbouring world makes them separable; what perturbation changes
  the ranking.
- The primary statistic is reference-weighted conditional regret
  (cycle 005), because on-policy retention fuses exposure with
  competence.

## 7. Coordination boundaries

- Proteus: organisms, circuits, mutation grammar, organism identity
  (organism_ref, D-7). Proteus never reads a world's physics and never
  writes a world binding. LUDUS WRITES THE WORLD-SIDE BINDING (a
  versioned, hashed mapping from a world's observation to the Proteus
  channel ABI and from output channels to actions); the encounter that
  joins them is composed by Archaeon/Vivarium.
- Archaeon: experimental coordination, backlog schema, decisions; the
  H4 lane (adaptive challenges and transfer) is the natural consumer
  of Ludus world families.
- Vivarium: execution and ecosystem machinery (queue, loader, SFE
  consumer); Ludus never starts or stops it.
- Hephaestus: chopped mechanisms and components; a Hephaestus component
  may become a world primitive or a fitness function only after it
  passes the section-4 rules; a Ludus world may be routed to Hephaestus
  as a candidate organ (ARCH-27 is the precedent in the other
  direction).
- Herakles: external computational backends (an OpenSpiel or POET
  backend is Herakles's route; Ludus consumes it as an audit oracle or
  a world source).
- Ludus: worlds, world families, generators, qualification, fitness
  landscapes, discriminatory power.

## 8. Standing mandate

The Ludus backlog never converges toward zero. Breadth, depth, world
families, structural cells, fitness functions, qualification
instruments, cheap adversarial baselines and world-generating operators
all increase. A mature Ludus has vastly more candidate experiments than
Prometheus has compute to execute; the matrix and the backlog are where
the surplus is kept navigable.

## 9. Changes this seat PROPOSES beyond the directive

P1. ONE interface. Three exist (archaeology L-2). The arena interface
    (current_player in {id, CHANCE, SIMULTANEOUS}; observation(i);
    deterministic replay; differential leak audit) is the proposed
    survivor because it is the only one that already breaks on chance,
    simultaneity and private observation. The bench's compile_world
    (exact solve) and the cycle-001 solve/optimal_actions become
    capabilities a world MAY expose, not a second interface. Migration
    is per world, each migration a verify run.
P2. Generated families are first-class. A world with a declared control
    knob (FOUNDRY-DECAY's decay; a generator's parameters) is the unit
    the World Foundry prefers, because question 4 of section 2 is
    answered by construction. A named commercial game is admitted for
    the cell it opens, never for its name.
P3. Rule audit by two admissible instruments: a published rulebook with
    source provenance, or an independent implementation reproducing
    action enumeration and values. The operator's HITL tick becomes a
    spot check on the seat's recorded audit, not the audit itself.
P4. Retirement conditions (ROLE.md s8) become reported observations:
    an empty band between cheap-heuristic and best-organism is a
    DORMANT-instrument reading with an eligible count, filed to the
    operator; the seat does not retire itself.
P5. Dossiers, packets and cycle records under roles/Ludus/ are not
    edited; corrections are annotations beside the original.

## 10. Superseded in CHARTER.md (v2), CHARTER_v1.md and ROLE.md

- ROLE.md s3 A1 (LLM in-context meter as the only affordable transfer
  measure): SUPERSEDED; no LLM in the tick path; transfer is H4's
  question over organism populations.
- ROLE.md s7.4 (hourly looping in 48-hour blocks): PARKED until a loop
  has a named input and a productivity signal (base rule 8).
- ROLE.md s8 (retirement conditions): restated as P4.
- ROLE.md s10 "Next, in order" (Hanabi, OpenSpiel, D13, join,
  classifier): SUPERSEDED by ARCHAEOLOGY_2026-09-11.md and
  BACKLOG_H0H5.md.
- CHARTER.md v2 s3/s37 founding corpus of 30-50 named games as the
  first campaign: SUPERSEDED by section 3 (the atlas is a source, not
  the boundary) and P2.
- Everything else in v2 (active selection s41, cheating assumption s35,
  no noun without a test s5, the daily questions s46) stands.
