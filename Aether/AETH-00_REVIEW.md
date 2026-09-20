# AETH-00 review -- minimal executable physics (candidate, no implementation)

Currency: 2026-09-20. UNFROZEN. Companion to AETHER_SPEC.md's AETH-00
section; this file carries the reasoning, alternatives and risks, not the
contract itself.

## Proposed contract

State: 4 uint8 fields per lattice location (opcode, arg0, arg1, payload),
every location executable matter, no active/executable flag. ISA: 0x00
NOP, 0x01 WRITE (writes issuing cell's payload into one field of one von
Neumann neighbor per the tick-start snapshot, toroidal wrap), other
opcodes candidate-NOP. Tick: snapshot-decode-propose-arbitrate-commit,
synchronous. Arbitration: hash-keyed deterministic max over (seed, tick,
target cell, target field, source cell). Full text: AETHER_SPEC.md.

## Assumptions

- A von Neumann neighborhood (4 directions) is sufficient for AETH-00;
  Moore (8-direction) or longer-range effects are out of scope here.
- "Executable matter, no privileged code/data distinction" (D-14) means
  WRITE may target a neighbor's opcode field exactly like any other field
  -- this is read directly from the ruling, not an inference.
- A CPU-only reference implementation is sufficient to test every AETH-00
  invariant; no invariant in this milestone requires a GPU to observe.
- "Small worlds" for property-based testing means small enough to run
  many trials cheaply on a CPU (no specific bound chosen yet, question
  28-adjacent).

## Unresolved choices (flagged, not decided here)

- Unknown-opcode default (candidate: NOP) -- operator flagged this
  explicitly as needing justification before freezing (question 27).
- Exact arbitration hash packing and mix constants (question 29).
- Minimum lattice dimension policy for ordinary (non-adversarial) runs
  (question 28) -- AETH-00's own test suite covers the degenerate case
  regardless of this policy choice.
- Numeric assignment of direction/field indices (arg0 mod 4 -> N/E/S/W,
  arg1 mod 4 -> opcode/arg0/arg1/payload) is given in listed order as a
  candidate; not confirmed as the frozen encoding.

## Arbitration options considered

1. Fixed spatial priority (lowest coordinate, or a fixed direction
   order always wins). Simplest to implement; REJECTED per operator's
   ruling because it is a permanent, systematic bias that could make
   later structures/patterns differentially favor certain lattice
   positions or directions for the life of a campaign -- indistinguishable
   from a real physics effect unless remembered as an artifact.
2. RECOMMENDED: hash-keyed deterministic max-arbitration. A fixed-width
   unsigned 64-bit avalanche mix (e.g. the public-domain splitmix64
   finalizer, general integer-hashing technique, not derived from any
   Prometheus engine) over (seed, tick, target coords, target field,
   source coords); winner = maximum hash among competitors; exact ties
   (astronomically unlikely at 64 bits) broken by a fixed total order
   over source coordinates so the result is always defined. A max
   reduction is associative and commutative, so serial, threaded, or GPU
   atomicMax evaluation all agree. Only 4 competitors possible per target
   field (von Neumann), so cost is trivial either way.
3. Explicit segmented sort per target group, same key as option 2. Same
   winner as option 2 (identical comparison key, same total order) but
   more expensive on GPU than a 4-way atomic reduction; useful only if a
   CPU debugging tool wants an auditable sorted list of all competitors,
   not as the production arbitration mechanism.

Recommendation: option 2, CPU reference implemented as a plain
enumerate-and-max over up to 4 competitors; GPU port later changes only
the reduction mechanism (atomicMax on a packed key), not the comparison
semantics.

## Ways AETH-00 could accidentally bias later science

- A weak or poorly mixed hash could reintroduce a hidden version of the
  rejected fixed-priority bias (e.g. a subtle correlation between win
  rate and direction or coordinate parity). Mitigation: test 13's
  win-rate uniformity check across directions over many trials, before
  trusting the arbitration at AETH-00 exit.
- Small-lattice toroidal aliasing (distinct arg0 directions resolving to
  the identical physical neighbor at minimal dimensions) could be an
  untested edge case that only surfaces as a bug at a much larger, later
  scale if not exercised now. Mitigation: test 14.
- The candidate unknown-opcode-as-NOP default makes an unimplemented or
  mistyped opcode value indistinguishable from deliberate inertness.
  Carried forward silently, this could make later interpretation of "why
  did nothing happen here" during real experiments ambiguous (dead
  matter vs. a bug). Not resolved here; flagged for the operator
  (question 27) and worth a distinguishing counter/flag in a later
  milestone even if NOP-default is kept.
- WRITE already allows one cell to program a neighbor's opcode using its
  own payload as the planted value. This is the intended "no privileged
  code/data distinction" design (D-14), not a bug, but it means AETH-00's
  single primitive already contains everything needed for one cell to
  construct another's behavior. Worth remembering when the heredity
  detector (STRUCTURAL_RESEMBLANCE / CAUSAL_CONSTRUCTION /
  RECURSIVE_CONSTRUCTION) is built: it must be tested against exactly
  this primitive's capability, not against a stronger hypothetical one.
- Property-based tests run only on small worlds; nothing in AETH-00
  exercises hash-key behavior at the coordinate/tick ranges a Runpod-
  scale run would reach (fixed-width integer wraparound at large tick
  counts is untested here).

## Exact test list

See AETHER_TEST_PLAN.md, AETH-00 section (15 tests, items 1-15).

## What AETH-00 explicitly does not establish

No organism, genome, birth, allocation, fitness, task, energy, resource
ecology, mutation, heredity detector, structural detector, GPU
implementation or Runpod expenditure (operator's exclusion list). In
addition: no GPU/CPU differential correctness (CPU-only oracle here); no
behavior at Runpod-scale coordinate/tick ranges; no statement about
whether the WRITE primitive is sufficient or necessary for any later
phenomenon of interest; no criteria for the eventual substrate-
qualification gate (AETHER_SPEC.md names categories only). AETH-00's only
claim, if it passes, is that this specific minimal physics is
implemented exactly as specified -- nothing about whether that physics is
scientifically interesting.
