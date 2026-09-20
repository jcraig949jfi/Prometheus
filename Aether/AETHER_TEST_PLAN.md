# Aether -- test plan

Currency: 2026-09-20, AETH-00 FROZEN v1 (semantics_id `aeth00.v1`). No
milestone is implemented yet; the 27-item test inventory below (25
original items, plus 2 added at freeze -- see "Two further items added
at freeze") is pre-code, written against the FROZEN `aeth00.v1` contract
(Aether/AETHER_SPEC.md). A test may only be reworded to fix a factual
mismatch with the frozen contract; it may never be weakened to make an
existing or planned implementation pass.

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

## AETH-00 (FROZEN v1, semantics_id `aeth00.v1`, no implementation yet)

Tests are written against Aether/AETHER_SPEC.md AETH-00 (FROZEN v1)
before any code exists. Each test's pass means "matches the frozen
contract," not "the contract is scientifically interesting" -- AETH-00
makes no scientific claim. Every test below must record
semantics_id = `aeth00.v1` in its trace. Every invariant test states its
premises explicitly (world size bounds, tick range) rather than
asserting the property unconditionally; the arbitration law itself has
no coordinate-range caveat to state (proof: AETHER_SPEC.md, Collision
arbitration), only the frozen dimension domain (1 <= H,W <= 2^32-1).

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
9. Repeated replay from identical (semantics_id, H, W, seed)
   produces bit-identical state at every tick. Compare COMPLETE lattice
   bytes tick-for-tick between independent re-runs, not merely a
   full-state hash (a hash-only comparison is retained as a fast
   secondary check, never the sole check, since a hash match cannot
   distinguish "identical" from "collided").
10. Only fields targeted by a WINNING proposal change; every losing
    proposal's target field equals what it would be had that losing
    proposal never been issued (no partial/ghost writes from losers).
    Explicitly also assert: every field targeted by NO proposal at all
    that tick (winning or losing) is bit-identical to its pre-tick
    value (preservation of untargeted fields).
11. World dimensions and physical dtypes are invariant across any number
    of ticks.
12. Randomized/property-based tests over many small worlds (random size,
    random opcode/arg/payload assignment, random seed) re-assert 1, 5, 6,
    9 and 10 generally, not only on hand-built examples. State the
    premise explicitly: "small" here means H, W chosen from a stated
    bounded range (a practical test-runtime choice; the arbitration law
    itself has no coordinate-range restriction narrower than the frozen
    dimension domain, 1 <= H,W <= 2^32-1).
13. Negative/adversarial dense collisions: 2-way, 3-way and full 4-way
    (all von Neumann neighbors) collisions on the same target field,
    across many seeds, asserting exactly one deterministic winner and
    full suppression of the others.
14. Degenerate small-lattice self-targeting (CORRECTED, was
    "toroidal aliasing" -- see AETH-00_REVIEW.md for the correction
    rationale). MANDATORY for both H=1 and H=2 (and, symmetrically,
    W=1 and W=2 -- Q28/D-17: these dimensions are supported, never
    rejected as invalid, and are required adversarial fixtures, not
    merely permitted ones): a single source cell's own arg0 value
    resolves to a neighbor that is the SAME physical cell as another of
    that source's possible arg0 values would resolve to (e.g. N and S
    coincide when H=1; N and S are distinct but both wrap when H=2), or
    resolves to the source cell itself. Assert this remains exactly ONE
    proposal from that source (never duplicated into multiple
    competitors, never dropped), and that it is applied as an ordinary
    write. Separately, assert that a genuine collision at these same
    minimal dimensions -- two or more DIFFERENT source cells' proposals
    landing on the same (target cell, field) -- is arbitrated exactly
    like any larger lattice, with no special case.
15. RESERVED_INERT byte preservation (Q27/D-16, corrected -- was
    "unknown-opcode-as-NOP candidate default"): construct cells holding
    every RESERVED_INERT opcode value (0x00 and a representative sample
    of 0x02..0xFF, not only 0x00), across multiple ticks with no
    incoming WRITE targeting them. Assert (a) no proposal is emitted by
    any of them; (b) every field of each such cell, INCLUDING the
    opcode byte itself, is bit-identical across ticks (never silently
    coerced to 0x00 or to each other); (c) none of this ever traps,
    errors, or halts the run. Separately (overlaps test 17): a
    RESERVED_INERT cell targeted by a winning incoming WRITE still has
    that field changed normally -- its own inertness does not make it
    write-immune.
16. Same-value WRITE is valid and may change zero bits: construct a
    proposal whose value equals the target field's current value; if it
    wins, assert proposal_won=true and stored_bits_changed=false for
    that field (not a special case, not rejected, not skipped).
17. Inert source can still be a target: a cell whose own opcode is NOP
    (or any non-WRITE state) can still be the target of an incoming
    WRITE from a neighbor and have its state changed; a cell's own
    inertness never blocks writes arriving at it.
18. Independent per-field arbitration: construct a target cell contested
    on two different fields (e.g. opcode and payload) by different sets
    of sources in the same tick; assert each field's winner is
    determined solely by the proposals aimed at that field, with no
    cross-field interaction (e.g. the winner of the opcode contest must
    not depend on which sources contested payload).
19. Complete replay identity: assert bit-identical full lattice bytes
    across independent re-runs using ALL SIX of (semantics_id, H, W,
    seed, tick, lattice bytes); a test that omits any of these six is
    not accepted as a replay-identity test.
20. Directional arbitration-bias diagnostics (replaces the old pooled
    "win-rate uniformity check", which is insufficient on its own):
    preregistered per AETHER_TEST_PLAN.md's statistical-test protocol
    below. Report win rate broken down per contest ARITY (2-way, 3-way,
    4-way) and per DIRECTION-PAIR, not only pooled across all contests,
    since a bias could hide inside one arity or one pair while the
    pooled average looks uniform.

### Five additional high-value test families (Astra reconciliation)

21. Exhaustive tiny-torus identity fixtures: for the smallest lattices
    (1x1, 1x2, 2x1, 2x2, and a representative 3x3), exhaustively enumerate
    every possible single-WRITE-cell instruction assignment (all opcode/
    arg0/arg1/payload combinations relevant to WRITE) and assert the
    exact resulting S[t+1] against a hand-derived expected value -- not a
    property, an exact fixture.
22. Independent transition oracle: a second reference implementation of
    the transition function, written independently from the primary
    implementation (structurally generated active/contested cases, e.g.
    from the spec text directly rather than from the first
    implementation's code), used for differential testing against the
    primary implementation on the same inputs.
23. Exact arithmetic / expected-winner vectors: hand-computed mix64 and
    full arbitration-key values for a fixed set of golden (seed, tick,
    target, field, source) inputs, checked bit-for-bit against the
    implementation's output (catches an implementation bug that a
    property-based test could miss because it is internally consistent
    but wrong relative to the specified constants).
24. Order perturbation plus deliberate faulty implementations: mutation-
    testing style checks -- construct at least one deliberately WRONG
    arbitration implementation (e.g. one that uses dict/list iteration
    order as a tie-break, or a fixed-priority rule) and assert the test
    suite FAILS it; separately, shuffle real evaluation order and assert
    the correct implementation's output is unchanged.
25. Preregistered arbitration-bias diagnostics: the statistical test plan
    (item 20) is written and committed BEFORE it is run, stating: the
    exact measured failure event (e.g. "direction D's proposals win a
    disproportionate share of N-way contests it participates in"); the
    sampling distribution assumed under the null (e.g. binomial with
    p = 1/N per contest arity); independence assumptions (each contest
    drawn from an independent seed/tick/coordinate tuple); the sample
    size (number of contests per arity/direction-pair cell); and the
    confidence bound used to flag a deviation (e.g. a two-sided
    binomial test at a stated alpha). "Five-nines" or any other
    percentage is never used as a generic quality adjective -- every
    statistical claim in AETH-00 states its own event, distribution,
    sample size and bound explicitly, per this item.

### Two further items added at freeze (2026-09-20, now 27 total)

26. Tick-overflow rejection: construct a world at tick == 2^64-1 and
    assert that attempting to step it raises an explicit error rather
    than committing a state at tick 0 (no silent wraparound). Also
    assert ordinary stepping from tick < 2^64-1 is unaffected by this
    check (no off-by-one false rejection).
27. Duplicate-source proposal detection in the test harness: the test
    harness itself must be able to detect the implementation defect
    named in AETHER_SPEC.md's arbitration section -- two or more
    proposals sharing the same physical source cell within one contest
    (forbidden by the proposal-identity rule, D-18). Construct at least
    one deliberately DEFECTIVE implementation that emits such a
    duplicate (e.g. by double-counting one source's proposal) and assert
    the harness FAILS it with a specific duplicate-source diagnosis, not
    merely a generic wrong-winner failure indistinguishable from test 24.

Full context, assumptions and what these tests do NOT establish:
Aether/AETH-00_REVIEW.md.
