# AETH-00 review -- minimal executable physics (FROZEN v1, no implementation)

Currency: 2026-09-20, FROZEN as semantics_id `aeth00.v1` (final freeze
pass, resolving Q27/Q28/Q31). Companion to AETHER_SPEC.md's AETH-00
section; this file carries the reasoning, alternatives and risks, not
the contract itself. Once this freeze commit exists, neither this file
nor AETHER_SPEC.md's `aeth00.v1` section may be edited to change the
contract in place -- only a NEW semantics_id can change behavior.

## Meta-status

AETH-00 is a REPLACEABLE CONFORMANCE SPECIMEN, not the frozen scientific
foundation of Aether (operator ruling, 2026-09-20). Its purpose is to
prove that we can specify, test, replay, and later implement one tiny
executable-matter transition law exactly. Passing it licenses engineering
progression only -- it establishes none of: neutrality, emergence
potential, suitable primordial physics, or scientific adequacy. See
"WHAT AETH-00 PROVES / WHAT AETH-00 DOES NOT PROVE" below.

## Frozen contract (summary; full normative text: AETHER_SPEC.md)

State: 4 uint8 fields per lattice location (opcode, arg0, arg1, payload),
every location executable matter, no active/executable flag. ISA: 0x01
WRITE is the sole active opcode; every other value (0x00 included) is
RESERVED_INERT -- preserved byte-for-byte, emits no proposal, remains
writable, never traps (D-16). Each WRITE-opcode cell emits EXACTLY ONE
proposal per tick, identified by its own physical source coordinates,
writing its own payload into one field of one von Neumann neighbor per
the tick-start snapshot, toroidal wrap (mathematical modulo). Tick:
snapshot-decode-propose-arbitrate-commit, synchronous, with each of a
cell's 4 fields arbitrated as an independent contest. Dimension domain:
transition semantics defined for 1 <= H,W <= 2^32-1; ordinary
(non-adversarial) runs require H>=3 && W>=3, H=1/H=2/W=1/W=2 remain
supported and are mandatory adversarial fixtures (D-17). Arbitration:
a five-step SplitMix64-finalizer chain over (seed, tick, target coords,
target field, source coords) using C(row,col)=(uint64(row)<<32)|
uint64(col); greatest unsigned priority wins; no coordinate-range
restriction and no coordinate tie-break (D-18, proof in AETHER_SPEC.md).
Tick starts at 0; a step from tick==2^64-1 is rejected, never wraps.
Replay identity requires all of (semantics_id, H, W, seed, tick, lattice
bytes) (D-19).

## Material changes made because of the Astra review

1. Proposal/collision semantics corrected: a single physical WRITE source
   emits exactly one proposal; direction resolves a destination, it does
   not multiply proposals; a collision requires 2+ DISTINCT physical
   sources contesting the same (target cell, field). The old test 14
   framing ("two distinct source directions ... collide") was ambiguous
   in a way that could be misread as one cell emitting multiple
   competing proposals across its own aliased directions -- corrected
   throughout AETHER_SPEC.md and AETHER_TEST_PLAN.md (test 14 rewritten,
   now "degenerate small-lattice self-targeting").
2. The transition function is now fully parameterized: valid dimension
   domain, coordinate orientation, direction/field encoding (confirmed,
   not just "listed order"), seed type, tick type/initial value/overflow
   behavior, invalid-input handling, same-value writes, preservation of
   untargeted fields, independent per-field arbitration, and the exact
   six-component replay-identity tuple are all now stated in
   AETHER_SPEC.md's "Complete transition function parameters" section.
3. Packed-atomic GPU implementation language removed from frozen/
   candidate semantics. AETHER_SPEC.md's arbitration section no longer
   mentions atomicMax or a packed (H, tiebreak) word as part of the
   physics; that content moved to a clearly non-normative "Deferred
   implementation guidance" subsection, restated as "one owner per
   target cell -> inspect <=4 neighbor sources -> independently reduce
   each field -> write a separate next-state buffer", with no GPU
   primitive prescribed. D-13's annotation below reflects this.
4. Q29 resolved to a specific candidate (still unfrozen): the SplitMix64
   finalizer, exact packing (12-bit row/col fields, 2-bit field index),
   and the greatest-unsigned-priority-wins rule are now fully specified
   in AETHER_SPEC.md, including a proof that distinct physical sources
   within one contest cannot tie inside the supported (<4096-per-axis)
   coordinate range. This is a CANDIDATE law, not a frozen one -- see
   "remaining blockers" below.
5. New explicit limitation recorded: AETH-00 cannot synthesize new byte
   values (WRITE only ever propagates the source's existing payload), so
   AETH-00 is explicitly disqualified from being a complete primordial
   physics on its own. Six further design properties (universal clock,
   toroidal recurrence, axis-privileging locality, typed field ontology,
   outward-templating WRITE, coordinate-keyed forcing field) are recorded
   as properties, not defects, so they are not "fixed" without a
   deliberate later decision.
6. Instrumentation is required starting now, not deferred to a later
   observatory milestone: every test trace must distinguish
   proposal_emitted, proposal_won, and stored_bits_changed as three
   separate events, and tag semantics_version.
7. Tests repaired/added: same-value WRITE validity (test 16), inert
   source can still be a target (test 17), independent per-field
   arbitration (test 18), six-component replay identity (test 19),
   complete-byte comparison rather than hash-only (test 9), and
   non-pooled directional bias diagnostics broken down by contest arity
   and direction-pair (test 20) replacing the old pooled-only win-rate
   check. Five new high-value test families added (exhaustive tiny-torus
   fixtures, an independently-written oracle for differential testing,
   exact golden arithmetic vectors, deliberate-faulty-implementation
   mutation checks, and a preregistered statistical-diagnostics
   protocol) -- AETHER_TEST_PLAN.md items 21-25.

## Material changes made in the final freeze pass (Q27/Q28/Q31, D-16..D-19)

1. Opcode semantics reframed and frozen (Q27, D-16): the prior
   "unknown-opcode-as-NOP default" language is GONE, not merely
   resolved in place. 0x01 is the sole active opcode (WRITE); every
   other value -- 0x00 included -- is RESERVED_INERT: physically
   distinct, preserved byte-for-byte, never coerced to 0x00, never
   treated as equivalent to each other, emits no proposal, remains
   writable, never traps. AETH-00 has exactly 1 active / 255 inert
   opcode encodings -- a property of this specimen's ISA budget, not a
   claim about the eventual substrate. AETHER_SPEC.md's Instruction Set
   section and AETHER_TEST_PLAN.md test 15 rewritten accordingly.
2. Dimension policy frozen (Q28, D-17): transition semantics are
   defined for every 1 <= H,W <= 2^32-1; H<=0 or W<=0 is invalid input.
   Ordinary (non-adversarial) runs require H>=3 && W>=3 -- purely to
   remove immediate-neighbor aliasing, not a scientific-adequacy claim.
   H=1, H=2, W=1, W=2 remain fully supported and are now explicit
   MANDATORY adversarial fixtures (test 14 updated to name both 1 and 2
   for both axes, not just H=1/W=1).
3. Arbitration coordinate range unbounded (Q31, resolved by REMOVAL, not
   revision, D-18): the prior packed 12/12/2/12/12 bit construction and
   its <4096-per-axis supported-range caveat are gone. Coordinates are
   now unsigned 32-bit components combined as C(row,col) =
   (uint64(row)<<32)|uint64(col); the arbitration law's domain now
   exactly matches the transition law's own frozen dimension domain
   (1 <= H,W <= 2^32-1), so there is no separate "supported range" to
   track or later revisit.
4. Arbitration construction rewritten as an explicit five-step chain
   (h0..h3, priority) rather than a single packed key fed through mix64
   once; mathematically equivalent in spirit (still SplitMix64-finalizer-
   based, still a provably tie-free bijection argument) but exactly
   pinned down step-by-step so no packing-width choice is left as future
   negotiable surface area.
5. Coordinate tie-break REMOVED from normative semantics (was "dead code
   in-range, retained for well-definedness"): the freeze ruling states
   plainly that duplicate-source collisions are impossible by the
   proposal-identity rule, so retaining a tie-break invited exactly the
   silent-defect-masking risk it was meant to guard against. A
   duplicate-source proposal is now explicitly an IMPLEMENTATION DEFECT
   the test harness must detect and fail on (new test 27), not a case
   the arbitration law resolves.
6. Tick-overflow behavior frozen (was UNSPECIFIED in the prior candidate,
   flagged as a documented limitation only): a step attempted FROM
   tick == 2^64-1 is now explicitly REJECTED, never wraps. New test 26.
7. Replay identity's `semantics_version` tag renamed to `semantics_id`
   throughout, matching the frozen identifier `aeth00.v1`, and the test
   plan/spec updated everywhere this string appeared.
8. AETH-00 formally marked FROZEN v1 (AETHER_SPEC.md, this file,
   AETHER_DECISIONS.md D-19): no further in-place edits to this
   contract; any future change needs a new semantics_id.

## Assumptions

- A von Neumann neighborhood (4 directions) is sufficient for AETH-00;
  Moore (8-direction) or longer-range effects are out of scope here.
- "Executable matter, no privileged code/data distinction" (D-14) means
  WRITE may target a neighbor's opcode field exactly like any other field
  -- this is read directly from the ruling, not an inference.
- A CPU-only reference implementation is sufficient to test every AETH-00
  invariant; no invariant in this milestone requires a GPU to observe.
- "Small worlds" for property-based testing means small enough to run
  many trials cheaply on a CPU -- a practical test-runtime choice only;
  the arbitration law itself imposes no coordinate-range restriction
  narrower than the frozen dimension domain (no specific bound chosen
  for test 12's sampling range yet, an implementation-time detail, not
  an open semantics question).

## Choices resolved at freeze (were "unresolved choices")

- Opcode default (Q27, D-16): RESOLVED as RESERVED_INERT, not
  "unknown-opcode-as-NOP." See "Material changes made in the final
  freeze pass," item 1.
- Minimum lattice dimension policy (Q28, D-17): RESOLVED -- H>=3 && W>=3
  for ordinary runs; 1 and 2 remain supported and are mandatory
  adversarial fixtures. See item 2 above.
- Arbitration coordinate range (Q31, D-18): RESOLVED by removing the
  <4096-per-axis limit entirely, not by revising it. See item 3 above.
- Whether the SplitMix64-based construction should be treated as FROZEN:
  RESOLVED -- yes, frozen as part of `aeth00.v1` (D-18, D-19). Per the
  project's normal TDD order, freezing the CONTRACT ahead of any running
  implementation is intentional; golden-vector tests (test 23) still
  need to pass once code exists, which verifies the IMPLEMENTATION
  against this now-frozen contract, not the other way around.

## Arbitration options considered

1. Fixed spatial priority (lowest coordinate, or a fixed direction
   order always wins). Simplest to implement; REJECTED per operator's
   ruling because it is a permanent, systematic bias that could make
   later structures/patterns differentially favor certain lattice
   positions or directions for the life of a campaign -- indistinguishable
   from a real physics effect unless remembered as an artifact.
2. ADOPTED AND FROZEN (aeth00.v1): hash-keyed deterministic max-
   arbitration using a chained SplitMix64-finalizer construction over
   (seed, tick, target coords, target field, source coords), with
   coordinates combined via C(row,col)=(uint64(row)<<32)|uint64(col) --
   no per-axis coordinate limit narrower than the transition law's own
   1 <= H,W <= 2^32-1 domain. Winner = maximum unsigned `priority` among
   competitors; provably tie-free for EVERY valid contest, unconditionally
   (proof in AETHER_SPEC.md), because distinct physical sources always
   have distinct C(source_row,source_col) (C is a bijection on the full
   uint32 x uint32 domain), and each mix step is a bijection. A
   max-reduction is associative and commutative, so serial, threaded, or
   any GPU reduction strategy agree on the same winner -- but AETH-00's
   semantics do not prescribe WHICH reduction strategy; that is deferred
   implementation guidance only (see AETHER_SPEC.md).
3. Explicit segmented sort per target group, same key as option 2. Same
   winner as option 2 (identical comparison key, same total order); not
   adopted as production guidance since it is an implementation-strategy
   commitment the physics does not need -- useful only if a CPU
   debugging tool wants an auditable sorted list of all competitors.

Recommendation unchanged in substance across every revision: option 2.
What changed at freeze is that the <4096-per-axis packed-key
construction was REPLACED, not merely re-specified, by the unbounded
chained construction (D-18) -- removing the last caveat on the tie-free
proof. No GPU primitive is prescribed as part of the semantics; a later
GPU port is free to choose any reduction mechanism that reproduces the
same priority-comparison result.

## Ways AETH-00 could accidentally bias later science

- The SplitMix64 construction is proven tie-free and order-independent,
  but that is NOT a claim of statistical neutrality. A weak interaction
  between the packing/mix and small coordinate values (e.g. all-small
  H, W in typical test runs) could still produce a directionally- or
  positionally-skewed win rate that isn't a "tie" in the proof's sense,
  merely a biased distribution. Mitigation: test 20's per-arity,
  per-direction-pair diagnostics (not merely pooled), run under the
  preregistered protocol in test 25.
- Small-lattice self-targeting (a source's own arg0 resolving to itself
  or to the same physical cell another of its own directions would)
  could be an untested edge case that only surfaces as a bug at a much
  larger, later scale if not exercised now. Mitigation: test 14
  (corrected).
- The now-frozen RESERVED_INERT design (255 of 256 opcode values inert)
  makes an unimplemented, mistyped, or not-yet-assigned opcode value
  indistinguishable from deliberately-planted inert matter. This is now
  a NAMED and frozen property (D-16), not a silent default, but the
  underlying ambiguity for later interpretation ("why did nothing happen
  here" -- dead matter vs. a bug) still exists and is worth a
  distinguishing counter/flag in a later milestone.
- WRITE already allows one cell to program a neighbor's opcode using its
  own payload as the planted value. This is the intended "no privileged
  code/data distinction" design (D-14), not a bug, but it means AETH-00's
  single primitive already contains everything needed for one cell to
  construct another's behavior. Worth remembering when the heredity
  detector (STRUCTURAL_RESEMBLANCE / CAUSAL_CONSTRUCTION /
  RECURSIVE_CONSTRUCTION) is built: it must be tested against exactly
  this primitive's capability, not against a stronger hypothetical one.
- Property-based tests run only on small worlds for practical
  test-runtime reasons, even though the frozen arbitration law itself
  now has no narrower coordinate-range restriction; nothing in AETH-00's
  test suite actually exercises hash-key behavior at the large
  coordinate/tick values a Runpod-scale run might eventually reach --
  the tie-free PROOF covers that range, but no TEST does.
- AETH-00 cannot synthesize new byte values (WRITE only ever propagates
  an existing payload) -- a later milestone that adds any value-combining
  operation changes this invariant; that change must be a deliberate,
  logged decision, not an incidental side effect of adding a new opcode.

## What AETH-00 does NOT prove -- and what it DOES prove

### WHAT AETH-00 PROVES / WHAT AETH-00 DOES NOT PROVE

PROVES (if every test in AETHER_TEST_PLAN.md passes):
- This specific, narrow transition law (4-field executable matter, one
  active opcode (WRITE) plus 255 RESERVED_INERT values, synchronous
  snapshot-decode-propose-arbitrate-commit, SplitMix64-keyed per-field
  arbitration) can be specified precisely enough to test -- and has now
  been frozen at that exact level of precision as semantics_id
  `aeth00.v1`.
- An implementation of that law can be built that matches the
  specification on every stated invariant, including adversarial and
  degenerate cases (H,W in {1,2} included, per D-17).
- That implementation replays bit-identically given identical
  (semantics_id, H, W, seed) inputs.
- The arbitration law is deterministic, order-independent, and
  UNCONDITIONALLY (not range-limited) provably tie-free for every valid
  contest in the frozen dimension domain.
- The team's TDD/instrumentation process (spec first, tests first,
  distinct proposal/win/change events, preregistered statistical
  protocols) can be executed end-to-end on a real, if tiny, example.

DOES NOT PROVE:
- That this physics is neutral, unbiased, or free of hidden structure
  (only bounded diagnostics are actually RUN, on small worlds, even
  though the frozen law's own proof is unconditional; see "Ways AETH-00
  could accidentally bias later science").
- That this physics has any emergence potential, or is a suitable
  primordial substrate for later Aether milestones.
- Scientific adequacy of any kind -- AETH-00 makes no scientific claim;
  it is an engineering conformance specimen only (Meta-status, above).
- Anything about GPU behavior (no GPU implementation exists yet; the
  "deferred implementation guidance" is unverified guidance, not a
  tested claim).
- That the WRITE primitive is sufficient, necessary, or well-suited for
  any later phenomenon of interest (heredity, mutation, selection).
- Any criteria for the eventual substrate-qualification gate
  (AETHER_SPEC.md names categories only, no thresholds).
- Passing AETH-00 licenses only: proceeding to the next TDD increment.
  It licenses nothing else.

## Exact test list

See AETHER_TEST_PLAN.md, AETH-00 section (27 tests/items, 1-27: the
original 25 plus 2 added at freeze -- tick-overflow rejection, test 26;
duplicate-source proposal detection in the harness, test 27).

## Remaining blockers to freezing AETH-00

None. Questions 27, 28 and 31 are RESOLVED (D-16, D-17, D-18;
AETHER_OPEN_QUESTIONS.md updated) and no contradiction was found against
any prior message. AETH-00 is FROZEN as semantics_id `aeth00.v1`
(D-19).

One item remains genuinely open but is explicitly NOT a freeze blocker,
per the project's normal TDD order (contract frozen first, verified by
implementation after): the SplitMix64 construction is fully specified
and proven tie-free, but has not yet been implemented or exercised by
any running test. "Fully specified and frozen" is not the same claim as
"verified against a running implementation" -- the golden-vector tests
(item 23) and the independent-oracle differential tests (item 22) still
need to be written and pass once code exists, per the standard
testable-contract -> tests -> minimal design -> code loop.
