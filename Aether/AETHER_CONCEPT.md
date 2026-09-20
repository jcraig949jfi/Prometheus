# Aether -- concept

Currency: 2026-09-20 (third capture pass). PRE-IMPLEMENTATION. Sections
marked [CANDIDATE] are strong working choices, explicitly not frozen;
everything else here is the current settled framing but still a concept
document, not AETHER_SPEC.md. Doctrine: Aether/AETHER_DOCTRINE.md.

## What Aether is

A fourth Prometheus experimental ecosystem, alongside BEE, NPE and SFE,
developed independently of them: no copying, adapting, reverse-engineering
or borrowing of their architecture or mechanisms. Clean-room design from
the operator's own material.

## Scientific identity

Aether is a GPU-native artificial physics in which executable matter must
discover persistent organization, heredity, reproduction and useful
computation without being given predefined organisms or genome
boundaries.

Existing Prometheus engines begin with identifiable organisms/genomes.
Aether begins one level lower:

    executable matter -> local interaction -> persistent structure ->
    possible heredity -> possible organism

The physics does not know what an organism is. The observatory may infer
structure afterward, from the outside.

Central scientific question: does removing predefined organism boundaries
and changing the representation of heredity expose evolutionary pathways
that discrete genome evolution cannot reach?

## Hard candidate constraints [CANDIDATE]

Strong design candidates, not yet frozen specification:

- NO BIRTH primitive; NO ALLOC primitive.
- NO organism_id in simulated physics.
- NO genome_id or fixed genome boundary.
- NO external copying in endogenous treatments.
- NO direct reproduction reward from task competence.
- NO observatory metadata visible to simulated matter.
- Structural resemblance alone is never replication evidence.
- Seeded structures are calibration instruments, not evidence of
  spontaneous origin.

## Candidate world [CANDIDATE]

A batched 2-D toroidal lattice. Each location holds a small amount of
executable physical state; candidate fields include opcode, operands,
tiny registers/state, energy/resource, and execution flags. Exact state
layout not settled. Governing distinction: physical state is part of the
universe; observatory state is outside the universe.

## Candidate physics [CANDIDATE]

Synchronous deterministic ticks (chosen for tractable CPU/GPU differential
verification and causal replay, not as a scientific commitment that all
future Aether physics must be synchronous):

    read previous state -> execute local rule -> propose writes ->
    deterministic conflict resolution -> resource/decay update -> next
    state

## Executable matter [CANDIDATE]

A very small local instruction set initially. Possible affordances:
arithmetic/logic, local sensing, local read/write, resource transfer,
conditional execution, spatial routing/jumping, movement/swap, dormancy.
Privileged operations such as block-copy are suspect; if ever included,
as experimental physics variants, not base-universe assumptions. Nothing
in the base instruction set means "reproduce."

## Causal heredity

Central to the whole project. Three distinct concepts, kept separate:
STRUCTURAL_RESEMBLANCE, CAUSAL_CONSTRUCTION, RECURSIVE_CONSTRUCTION.
Cases the observatory must eventually distinguish: high resemblance
without causal ancestry; causal construction with low resemblance;
parasites; mutual constructors (A constructs B, B constructs A); partial
copying completed by environmental dynamics; traveling structures that
must not be mistaken for offspring. The observatory must survive
adversarial fixtures for all of these before any claim in this category
is trusted.

## Telemetry philosophy [CANDIDATE, general shape only]

Designed before campaigns, not after. Cannot record every interaction
forever, especially on Runpod. Likely pattern: cheap continuous GPU-side
counters/hashes, plus rolling forensic buffers, plus high-resolution
capture when predefined mechanical triggers fire. Exact implementation
not decided.

## First scientific transplant [CANDIDATE, deferred]

First serious experiment after substrate qualification: an accessibility
barrier analogous to one already observed elsewhere in Prometheus --
useful information is available, selection would reward conditional
behavior, yet a discrete representation makes the required computation
evolutionarily inaccessible. Aether asks whether spatial assembly,
cooperation, partial construction, distributed computation or
environmental scaffolding provide alternative paths. Built from this
description alone; existing engines' implementations are not inspected or
borrowed for this purpose.

## Development order [CANDIDATE, expected not committed]

    specification -> CPU reference physics -> adversarial seeded fixtures
    -> observatory -> GPU differential implementation -> random
    primordial-soup calibration -> first accessibility experiment ->
    optimization -> Runpod scaling

## Runpod economics

Hard budget $19.93 (AETHER_RUNPOD.md). Success metric is not raw
ticks/sec; it is useful simulated interactions per dollar and information
gained per dollar (AETHER_DECISIONS.md D-10). Runpod used during
development for small compatibility/performance probes only; no broad
scientific campaigns until the substrate is qualified trustworthy
(D-12).

## Status

No code. No tests. No frozen spec. No Runpod spend. First real engineering
milestone will be AETH-00, jointly defined once enough design material has
been captured (see AETHER_DECISIONS.md and AETHER_OPEN_QUESTIONS.md for
what is settled versus open).
