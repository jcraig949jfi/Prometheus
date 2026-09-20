# Aether -- open questions

Currency: 2026-09-20 (4 capture passes). Reorganized by category per the
operator's message 3. Questions are never deleted when answered -- marked
ANSWERED with the date and decision id, kept for the record.

Contradiction check (2026-09-20, message 3 against messages 1-2): none
found; message 3 resolves several previously open questions (noted below)
and narrows scope, without reversing any prior constraint. One tension
flagged, not a contradiction: see "First scientific transplant" under
Scientific ontology.

Contradiction check (2026-09-20, message 4 -- the three rulings plus
AETH-00 -- against messages 1-3): none found; message 4 resolves question
3's tension (the transplant's target property is now stated directly, in
the abstract, answering how the transplant can be designed without
inspecting an existing engine) and answers/partially answers questions 6,
8, 9, 10 and 16 for the AETH-00 slice specifically, without reversing any
earlier constraint.

## Scientific ontology

1. Scientific/domain focus -- ANSWERED 2026-09-20 (AETHER_CONCEPT.md,
   Scientific identity): does removing predefined organism boundaries and
   changing the representation of heredity expose evolutionary pathways
   that discrete genome evolution cannot reach?
2. Differentiation from BEE/NPE/SFE -- ANSWERED 2026-09-20: those engines
   begin with identifiable organisms/genomes; Aether begins one level
   lower (executable matter, no predefined organism or genome boundary).
3. First scientific transplant sourcing -- ANSWERED 2026-09-20 (D-15):
   the operator stated the target scientific property directly and
   abstractly (information present, selection pressure present, useful
   conditional computation inaccessible due to representation topology;
   incumbent answers before reading the needed information; viable
   alternative separated from the incumbent by a zero-fitness valley with
   no local one/two-edit route; a seeded viable witness is strongly
   selectable). Aether reproduces this property, never any existing
   engine's implementation, and does not inspect existing engine code.

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
6. Conflict resolution rule for synchronous ticks -- CANDIDATE GIVEN
   2026-09-20: hash-keyed deterministic max-arbitration over (seed,
   tick, target cell, target field, source cell), recommended in
   AETHER_SPEC.md AETH-00 and AETH-00_REVIEW.md. NOT frozen: exact hash
   packing/constants (question 29) still open.
7. Resource/decay update semantics: formula and rates not specified.
   Out of scope for AETH-00 (explicitly excluded); open for whichever
   milestone introduces energy/resources.
8. Instruction set v1 -- PARTIALLY ANSWERED for the AETH-00 slice only
   2026-09-20: NOP and WRITE (AETHER_SPEC.md). Still open beyond AETH-00:
   which of the remaining possible affordances (arithmetic/logic, local
   sensing, resource transfer, conditional execution, spatial routing/
   jumping, movement/swap, dormancy) are added next, and whether
   block-copy is ever included as a base op (candidate answer: no, only
   as an experimental physics variant if ever).
27. Unknown-opcode default (values other than 0x00/0x01): candidate is
    "behave as NOP" (AETHER_SPEC.md), explicitly FLAGGED by the operator
    as needing justification before freezing -- risk noted in
    AETH-00_REVIEW.md (an unrecognized opcode is indistinguishable from
    intentional inertness).
28. Minimum lattice dimension: does AETH-00 (or later milestones) require
    a minimum size to avoid unintentional self/neighbor aliasing under
    toroidal wrap in ORDINARY (non-adversarial) runs, or is small-lattice
    aliasing always in scope as a physical fact and only guaranteed
    correctly handled, never avoided? AETH-00 test 14 covers the
    adversarial case; this question is about ordinary-run policy.
29. Exact arbitration hash function: packing of (seed, tick, target_row,
    target_col, target_field, source_row, source_col) into the mix
    function's input, and the mix constants themselves, are TBD at
    freeze (AETHER_SPEC.md candidate names the shape -- a splitmix64-
    style avalanche mix -- not the exact bytes).

## Execution / state

9. "Tiny world" definition -- PARTIALLY ANSWERED for AETH-00 2026-09-20:
   state slice is 4 uint8 fields per lattice location (AETHER_SPEC.md);
   lattice dimensions, episode length and per-run dollar/wall-clock
   budget for AETH-00 itself still not chosen.
10. Exact physical-state field layout -- ANSWERED for the AETH-00 SLICE
    2026-09-20: opcode, arg0, arg1, payload, each uint8 (AETHER_SPEC.md).
    Still open beyond AETH-00: the permanent Aether v1 layout (energy/
    resource fields, registers, execution flags all deferred).

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
16. What exactly qualifies the substrate as "trustworthy" -- PARTIALLY
    ANSWERED 2026-09-20: future gate's CATEGORIES named (AETHER_SPEC.md,
    Substrate qualification philosophy): semantic correctness,
    deterministic replay, CPU/GPU differential correctness, adversarial
    observatory correctness, seeded positive/negative controls,
    provenance integrity, checkpoint/resume integrity, experiment-
    accounting integrity, measured error bounds. Still open: the actual
    per-category pass criteria and sample sizes.

## GPU / performance

17. CPU/GPU differential equivalence tolerance: bit-exact for which state
    components, statistical for which, and what statistical test if any.
30. GPU mapping validation timing: the candidate per-cell-parallel-eval
    plus deterministic-arbitration-commit mapping (D-13) is not exercised
    until a GPU implementation exists (excluded from AETH-00) -- which
    milestone first builds and differentially tests it against the CPU
    oracle?

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
