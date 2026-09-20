# Aether -- specification

Currency: 2026-09-20. First entry below (AETH-00) is a CANDIDATE, drafted
for review, NOT frozen and NOT implemented. Everything under "AETH-00
(UNFROZEN CANDIDATE)" is subject to change until the operator freezes it;
full detail and reasoning: Aether/AETH-00_REVIEW.md.

Format: each capability gets a numbered section (AETH-nn), stating its
invariant(s)/observable behavior first, its status (CANDIDATE or FROZEN),
and a pointer to the tests in AETHER_TEST_PLAN.md that check it.
Superseded entries are annotated in place, never silently rewritten.

## AETH-00 (UNFROZEN CANDIDATE) -- minimal executable physics

Scientific purpose (only): establish trustworthy minimal executable
physics. No organism, genome, birth, allocation, fitness, task, energy,
resource ecology, mutation, heredity detector, structural detector, GPU
implementation or Runpod expenditure. AETH-00 does not test anything
about emergence.

### State

Each lattice location: exactly four uint8 fields -- opcode, arg0, arg1,
payload. Every location is executable matter; there is no separate
active/executable flag. Opcode 0x00 (NOP) is simply inert matter. This is
the AETH-00 state SLICE only, not the permanent Aether v1 layout
(AETHER_OPEN_QUESTIONS.md question 10 stays open beyond this slice).

### Instruction set

    0x00  NOP     no proposal
    0x01  WRITE   candidate semantics below
    other UNSPECIFIED -- candidate default: behave as NOP. FLAGGED: this
                   default needs justification before freezing
                   (AETHER_OPEN_QUESTIONS.md question 27).

WRITE reads only the tick-start snapshot S[t]. Candidate semantics:
arg0 mod 4 selects a von Neumann neighbor (candidate order: 0=N, 1=E,
2=S, 3=W); arg1 mod 4 selects one field of that neighbor (candidate
order: 0=opcode, 1=arg0, 2=arg1, 3=payload); the value written is the
issuing cell's own payload. Lattice boundaries wrap toroidally. No
reproduction primitive exists; a WRITE can still plant an opcode value
into a neighbor by writing payload into the neighbor's opcode field --
noted as a deliberate consequence, not a hidden one (AETH-00_REVIEW.md).

### Tick semantics

    S[t] -> every cell independently decodes S[t]
         -> each WRITE emits at most one proposal
         -> proposals targeting the same (target cell, target field)
            compete
         -> exactly one deterministic winner selected (arbitration below)
         -> all winners commit simultaneously
         -> S[t+1]

A write that changes a neighbor's opcode cannot affect execution before
the following tick. No mutation, resource update, decay or other side
effect exists in AETH-00.

### Collision arbitration (candidate, recommended)

Requirement: the winner must not depend on Python iteration order, thread
order, or GPU scheduling order -- only on (seed, tick, target cell,
target field, competing source cells).

RECOMMENDED: hash-keyed deterministic max-arbitration. Compute a fixed,
specified 64-bit unsigned hash H(seed, tick, target_row, target_col,
target_field, source_row, source_col) using a standard fixed-width
avalanche mix over unsigned integers with defined (mod 2^64) overflow --
for example the public-domain splitmix64 finalizer applied to a fixed
packing of the inputs (exact packing and constants: TBD at freeze, not
Prometheus-engine-derived, general public integer-hashing technique).
Winner = the competing proposal with the maximum H; a genuine hash tie
(astronomically unlikely at 64 bits, but must still be specified) is
broken by a fixed total order over (source_row, source_col) so the result
is always defined. This is a max-reduction: associative and commutative,
so any evaluation order -- serial loop, threaded, or a GPU atomicMax on a
packed (H, tiebreak) word per target field -- yields the identical
winner. The CPU reference implementation may compute it by plain
enumeration and max() over the at most 4 von Neumann competitors per
target field; a later GPU port changes only the reduction mechanism, not
the comparison key, because the key is a pure function of tick/seed/
coordinates. Two alternatives considered and NOT recommended: (a) fixed
spatial priority (e.g. lowest coordinate, or N>E>S>W always wins) --
rejected per operator's ruling because it is a permanent, systematic
spatial/directional bias baked into every contested tick for the life of
a campaign; (b) explicit segmented sort per target group -- produces the
identical winner as the max-reduction (same key, same total order) but
costs more on GPU than an atomic reduction for at most 4 competitors, so
only useful where sort-based auditability in a CPU debugging tool is
wanted. Full comparison: AETH-00_REVIEW.md.

### Explicit exclusions

No organism, genome, birth, allocation, fitness, task, energy, resource
ecology, mutation, heredity detector, structural detector, GPU
implementation, Runpod expenditure.

## Substrate qualification philosophy (UNFROZEN, categories only)

Not a gate yet (AETHER_OPEN_QUESTIONS.md question 16 stays open); the
future gate (D-12) will be built from these categories, each eventually
tied to a measured quantity and sample size, never asserted globally or
verbally:

semantic correctness; deterministic replay; CPU/GPU differential
correctness; adversarial observatory correctness; seeded positive
controls; negative controls; provenance integrity; checkpoint/resume
integrity; experiment-accounting integrity; measured error bounds. Any
eventual five-nines-class target (AETHER_DOCTRINE.md) is stated against
one of these measured quantities and its sample size, never as a global
claim.
