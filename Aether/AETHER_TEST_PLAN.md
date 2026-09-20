# Aether -- test plan

Currency: 2026-09-20. EMPTY. No milestone exists yet to test.

Governing loop for every future entry (operator, 2026-09-20):

    testable contract -> tests -> minimal design -> minimal code that
    passes -> review -> next increment

Rules that will apply once entries exist:
- A capability's tests are written from its stated invariant/observable
  behavior BEFORE the minimal design or code for it.
- Do not redesign around a failing test unless we explicitly decide the
  specification (AETHER_SPEC.md) is wrong; that decision is itself logged
  in AETHER_DECISIONS.md.
- Every milestone (AETH-nn) lists: the contract it tests, the test
  file(s), what a pass means, and what a fail means (per the base role's
  "no scientific claim based solely on a detector firing" -- a passing
  test is evidence the code matches the contract, not evidence the
  contract is scientifically interesting).
- Positive, negative and cheat controls are required wherever the test
  claims to detect something (emergence, a physics violation, a specific
  pattern), not just wherever convenient.

## AETH-00 (candidate tests, no implementation yet)

Tests are written against Aether/AETHER_SPEC.md AETH-00 (UNFROZEN
CANDIDATE) before any code exists. Each test's pass means "matches the
stated candidate contract," not "the contract is scientifically
interesting" -- AETH-00 makes no scientific claim.

1. All-NOP world is invariant across any number of ticks.
2. A single WRITE changes exactly the one intended (neighbor, field);
   nothing else in the world changes.
3. Toroidal wrapping is exact, tested from every edge and corner in all
   four directions.
4. All four target fields (opcode, arg0, arg1, payload) can each be the
   one that changes, parametrized over arg1 mod 4.
5. Tick-start snapshot semantics hold: construct a case where sequential
   (non-snapshot) evaluation would give a different answer than
   snapshot evaluation, and assert the snapshot answer.
6. A write that changes a neighbor's opcode does not let that neighbor
   act on the new opcode until the following tick.
7. Collision outcome is deterministic: identical (seed, tick, world)
   produces the identical winner every time it is run.
8. Collision outcome is independent of proposal enumeration order:
   shuffle the internal evaluation order of competing proposals; winner
   is unchanged.
9. Repeated replay from identical initial state and seed produces
   bit-identical state at every tick (full-state hash equality across
   independent re-runs).
10. Only fields targeted by a WINNING proposal change; every losing
    proposal's target field equals what it would be had that losing
    proposal never been issued (no partial/ghost writes from losers).
11. World dimensions and physical dtypes are invariant across any number
    of ticks.
12. Randomized/property-based tests over many small worlds (random size,
    random opcode/arg/payload assignment, random seed) re-assert 1, 5, 6,
    9 and 10 generally, not only on hand-built examples.
13. Negative/adversarial dense collisions: 2-way, 3-way and full 4-way
    (all von Neumann neighbors) collisions on the same target field,
    across many seeds, asserting exactly one deterministic winner and
    full suppression of the others; include a win-rate uniformity check
    across directions over many trials, since a directionally-skewed win
    rate would indicate the hash arbitration has silently reintroduced
    the spatial bias it was chosen to avoid.
14. Degenerate small-lattice toroidal aliasing: minimal dimensions (e.g.
    width or height of 1 or 2) where two distinct source directions
    (different arg0 values) resolve to the SAME physical neighbor cell.
    Assert these are treated as a genuine collision on that shared target
    (not silently double-applied, not silently dropped).
15. Unknown-opcode-as-NOP candidate default: any opcode other than 0x00/
    0x01 emits no proposal and changes nothing, exactly like NOP.

Full context, assumptions and what these tests do NOT establish:
Aether/AETH-00_REVIEW.md.
