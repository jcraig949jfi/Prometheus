# Aether -- open questions

Currency: 2026-09-20 (3 capture passes). Reorganized by category per the
operator's message 3. Questions are never deleted when answered -- marked
ANSWERED with the date and decision id, kept for the record.

Contradiction check (2026-09-20, message 3 against messages 1-2): none
found; message 3 resolves several previously open questions (noted below)
and narrows scope, without reversing any prior constraint. One tension
flagged, not a contradiction: see "First scientific transplant" under
Scientific ontology.

## Scientific ontology

1. Scientific/domain focus -- ANSWERED 2026-09-20 (AETHER_CONCEPT.md,
   Scientific identity): does removing predefined organism boundaries and
   changing the representation of heredity expose evolutionary pathways
   that discrete genome evolution cannot reach?
2. Differentiation from BEE/NPE/SFE -- ANSWERED 2026-09-20: those engines
   begin with identifiable organisms/genomes; Aether begins one level
   lower (executable matter, no predefined organism or genome boundary).
3. First scientific transplant: the "accessibility barrier analogous to
   one already observed elsewhere in Prometheus" is not named. Open:
   is reading ABOUT that finding (not the implementation) permitted, or
   must the transplant experiment be designed from the abstract
   description in AETHER_CONCEPT.md alone? Flagged as a tension, not yet
   resolved.

## Physics

4. Determinism boundary -- PARTIALLY ANSWERED 2026-09-20: synchronous
   deterministic ticks chosen as the first candidate implementation
   (AETHER_CONCEPT.md, Candidate physics), not a commitment that all
   future physics must be synchronous. Still open: which state, if any,
   is allowed to be non-deterministic once a non-synchronous variant is
   explored.
5. Physics vs. observation/interpretation boundary -- ANSWERED
   2026-09-20: physical state is part of the universe, observatory state
   is outside it; no observatory metadata visible to simulated matter
   (hard candidate constraint).
6. Conflict resolution rule for synchronous ticks: "propose writes ->
   deterministic conflict resolution" names a step but not a rule
   (priority order, seeded tie-break, something else).
7. Resource/decay update semantics: formula and rates not specified.
8. Instruction set v1: which of the possible affordances (arithmetic/
   logic, local sensing, local read/write, resource transfer, conditional
   execution, spatial routing/jumping, movement/swap, dormancy) are
   actually included in the first substrate, and is block-copy excluded
   from the base instruction set entirely or deferred as an experimental
   variant.

## Execution / state

9. "Tiny world" definition: minimal unit of experiment (lattice size,
   episode length, wall-clock and dollar budget per run) -- still not
   settled; candidate world (2-D toroidal lattice) given, exact state
   layout explicitly deferred.
10. Exact physical-state field layout: which of opcode, operands,
    registers, energy/resource, execution flags are included, and their
    bit widths/ranges.

## Heredity / observatory

11. Seeded control vs. spontaneous emergence -- ANSWERED 2026-09-20:
    seeded structures are calibration instruments, never evidence of
    spontaneous origin (D-9, D-11).
12. Causal evidence vs. superficial resemblance -- ANSWERED 2026-09-20 via
    the STRUCTURAL_RESEMBLANCE / CAUSAL_CONSTRUCTION /
    RECURSIVE_CONSTRUCTION taxonomy (D-11); structural resemblance alone
    is never replication evidence.
13. How RECURSIVE_CONSTRUCTION, mutual constructors (A builds B, B builds
    A), and partial copying completed by environmental dynamics get
    operationalized as detectable, testable predicates -- not yet
    designed.
14. Telemetry trigger definition: "predefined mechanical triggers" for
    high-resolution capture are named as a category but not specified.

## Falsification / testing

15. Adversarial tests against false discoveries -- SUBSTANTIALLY ANSWERED
    2026-09-20 (D-9): adversarial negative fixtures and detector FP/FN
    rates on known fixtures are required; the six heredity adversarial
    cases are named (AETHER_CONCEPT.md, Causal heredity). Still open: the
    concrete fixture implementations, deferred to pre-code design.
16. What exactly qualifies the substrate as "trustworthy" -- the gate
    (D-12) before any broad Runpod scientific campaign is authorized; no
    criteria defined yet.

## GPU / performance

17. CPU/GPU differential equivalence tolerance: bit-exact for which state
    components, statistical for which, and what statistical test if any.

## Runpod economics

18. Instrumentation contract: what must every remote test log to be
    reproducible (code SHA, seed, hardware/instance type, wall-clock,
    dollar cost, result, the specific question answered).
19. Budget tracking mechanism: manual ledger entry, API cost query, or
    both.
20. Stop/kill criterion for an individual paid run (budget exceeded, no
    signal, instrument failure) and what enforces it.
21. Pods vs. serverless/autoscaling: benchmark or cost/latency profile
    that decides this once a workload shape exists.
22. "Information gained per dollar" (D-10): not yet quantified -- a
    rubric, a bits-based measure, or a qualitative score.

## Process / meta

23. Naming: does the ecosystem need a name distinct from "Aether" (both
    the seat and, per this design, the ecosystem)?
24. Ownership: is this ecosystem Aether the seat's eventual charter, or
    is the seat scribe/designer for now with ownership decided later?
25. Astra review packets: delivered back pasted verbatim in chat, or
    committed as a file first?
26. Cosmos investigation: no stopping rule defined yet for the
    low-priority background check.
