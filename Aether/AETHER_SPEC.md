# Aether -- specification

Currency: 2026-09-20, AETH-00 FROZEN v1 (semantics_id `aeth00.v1`).
Everything under "AETH-00 (FROZEN v1)" is the frozen contract; it may
only be superseded by a NEW semantics_id, never silently edited in
place. Full detail, reasoning, and what remains a live design question
beyond AETH-00: Aether/AETH-00_REVIEW.md.

Format: each capability gets a numbered section (AETH-nn), stating its
invariant(s)/observable behavior first, its status (CANDIDATE or FROZEN),
and a pointer to the tests in AETHER_TEST_PLAN.md that check it.
Superseded entries are annotated in place, never silently rewritten.

## AETH-00 (FROZEN v1, semantics_id `aeth00.v1`) -- minimal executable
   physics

Scientific purpose (only): establish trustworthy minimal executable
physics. No assembly, executable configuration, birth, allocation, evaluation score, task, energy,
resource resource regime, perturbation, configuration transmission detector, structural detector, GPU
implementation or Runpod expenditure. AETH-00 does not test anything
about emergence.

### Scope (frozen, operator ruling 2026-09-20)

AETH-00 is a REPLACEABLE CONFORMANCE OBSERVED_INSTANCE for Aether's engineering
methodology, not the frozen scientific foundation of Aether. Passing it
establishes only that we can define and reproduce an exact
executable-matter transition law -- specify it, test it, replay it, and
implement it exactly. Passing AETH-00 licenses engineering progression
only. It explicitly does NOT establish:

- suitable primordial physics;
- scientific neutrality;
- open-endedness;
- configuration transmission;
- emergence;
- evolutionary accessibility;
- GPU correctness;
- Runpod qualification.

See "WHAT AETH-00 PROVES / WHAT AETH-00 DOES NOT PROVE" in
AETH-00_REVIEW.md for the fuller discussion.

### semantics_id

This frozen contract is tagged `aeth00.v1`. Any test trace, replay
record, or future differential-test artifact must record which
semantics_id it was produced against. Assigning behavior to any
currently-RESERVED_INERT opcode value, or changing any other part of
this contract, requires a NEW semantics_id -- `aeth00.v1` itself is
never edited in place once this freeze commit exists.

### State

Each lattice location: exactly four uint8 fields -- opcode, arg0, arg1,
payload. Every location is executable matter; there is no separate
active/executable flag. Opcode 0x00 (NOP) is simply inert matter. This is
the AETH-00 state SLICE only, not the permanent Aether v1 layout
(AETHER_OPEN_QUESTIONS.md question 10 stays open beyond this slice).
"Lattice bytes" (used below in replay identity) means the full H*W*4
uint8 buffer in a fixed, specified row-major (row, then col, then field
in opcode/arg0/arg1/payload order) layout.

### Instruction set (frozen -- Q27)

    0x01        WRITE           semantics below
    0x00        RESERVED_INERT  may be called "NOP" for readability
    0x02..0xFF  RESERVED_INERT  (254 further values)

AETH-00 therefore has exactly ONE active opcode encoding (0x01, WRITE)
and 255 RESERVED_INERT opcode encodings, of which 0x00 is conventionally
called NOP. This 1-active/255-inert ratio is a property of THIS
conformance observed instance, not a claim about the eventual primordial
substrate's opcode budget.

RESERVED_INERT semantics (all values other than 0x01), frozen:

- a RESERVED_INERT opcode never becomes 0x00 and is never treated as
  equivalent to NOP for storage purposes -- each of the 255 values
  remains physically distinct and is preserved byte-for-byte across
  ticks unless overwritten by a winning WRITE proposal targeting that
  field, exactly like any other stored byte;
- a site decoding a RESERVED_INERT opcode emits NO proposal that tick;
- a site decoding a RESERVED_INERT opcode remains writable: any of its
  four fields, including its own opcode field, can still be the target
  of an incoming WRITE from a neighbor and be changed by it -- a site's
  own inertness never blocks writes arriving at it;
- encountering any RESERVED_INERT opcode value NEVER traps, errors, or
  causes host failure -- it is ordinary, valid, decodable state;
- assigning semantics to any currently-RESERVED_INERT byte value in a
  future milestone requires a NEW semantics_id; it can never happen
  silently under `aeth00.v1`.

### WRITE semantics and proposal identity (FROZEN, aeth00.v1)

WRITE reads only the tick-start snapshot S[t]. arg0 mod 4 selects a von
Neumann neighbor (frozen order: 0=N, 1=E, 2=S, 3=W); arg1 mod 4 selects
one field of that neighbor (frozen order: 0=opcode, 1=arg0, 2=arg1,
3=payload); the value written is the issuing site's own payload.
Lattice boundaries wrap toroidally. No recursive construction primitive exists; a
WRITE can still plant an opcode value into a neighbor by writing payload
into the neighbor's opcode field -- a deliberate consequence of "no
privileged code/data distinction" (D-14), not a hidden one. This
includes turning a RESERVED_INERT neighbor's opcode field into 0x01
(making it WRITE-capable next tick) or turning a WRITE neighbor's opcode
field into any RESERVED_INERT value (making it inert next tick); WRITE
does not distinguish opcode fields from any other field when deciding
whether a write is legal.

Corrected proposal-generation rule (this paragraph supersedes any prior
looser phrasing): each site that decodes opcode=WRITE at S[t] emits
EXACTLY ONE proposal for that tick: (source = this site's own (row,
col), target = the single neighbor site computed from this site's own
arg0 mod 4, target_field = this site's own arg1 mod 4, value = this
site's own payload). A site never emits more than one proposal per tick,
regardless of how many directions might alias to the same physical
neighbor at small lattice dimensions -- a site has exactly one arg0
value and therefore exactly one resolved direction per tick. Direction
resolves a physical destination; it does not create proposal
multiplicity.

Proposal identity within a tick is the physical source site's (row,
col). Two proposals are the same proposal only if they share the same
source site. Two proposals from two DIFFERENT source sites are always
distinct proposals, even if toroidal aliasing at small H or W makes them
resolve to the same target site.

A collision (arbitration contest) exists only when 2 or more DISTINCT
physical source sites emit proposals sharing the same (target site,
target_field). Toroidal aliasing where a single source site's own N and
S (or E and W) neighbor resolve to the same physical site (e.g. H=1 or
W=1, or a self-targeting site) is NOT itself a collision: it is that
site's one proposal targeting a neighbor that happens to equal another
specific site, including possibly the source site itself. This remains a
single proposal and must be handled as an ordinary write, never rejected
and never manufactured into extra competitors. Genuine collisions at
small dimensions still arise normally whenever 2+ DIFFERENT sites'
independently-computed proposals land on the same (target site, field);
this uses the same arbitration as any larger lattice, no special case.

### Tick semantics

    S[t] -> every site independently decodes S[t]
         -> each WRITE-opcode site emits exactly one proposal (above)
         -> for each (target site, target field), all proposals aimed at
            it compete independently of every other field's contest,
            including other fields of the same target site
         -> exactly one deterministic winner selected per contest
            (arbitration below)
         -> all winners commit simultaneously
         -> S[t+1]

A write that changes a neighbor's opcode cannot affect execution before
the following tick. No perturbation, resource update, decay or other side
effect exists in AETH-00.

### Complete transition function parameters (FROZEN, aeth00.v1)

- Valid dimension domain: transition semantics are defined for every
  H, W with 1 <= H, W <= 2^32 - 1 (row and col are uint32-range
  quantities; see arbitration below). H<=0, W<=0, non-integer
  dimensions, dimensions outside this range, or a lattice buffer whose
  length is not exactly H*W*4 bytes are INVALID INPUT and must raise an
  explicit error at world-construction time -- never silently produce a
  degenerate world.
- Ordinary-run dimension policy (Q28, frozen): an ORDINARY (non-
  adversarial) AETH-00 run requires H >= 3 && W >= 3. This threshold
  removes immediate neighbor self/other-neighbor aliasing under
  toroidal wrap; it is an ordinary-run policy choice, not a claim that
  H,W >= 3 is scientifically adequate for anything beyond that. H=1 and
  H=2 (and W=1, W=2) remain fully SUPPORTED by the transition semantics
  and are MANDATORY adversarial test cases (AETHER_TEST_PLAN.md test
  14), never rejected as invalid input.
- Coordinate orientation: 0-indexed (row, col); row 0..H-1, col 0..W-1.
  Frozen convention: row increases going "south", col increases going
  "east" -- an arbitrary but fixed labeling used only to give N/E/S/W
  meaning; the physics has no privileged "up".
- Direction encoding (arg0 mod 4), frozen: 0=North (row-1 mod H),
  1=East (col+1 mod W), 2=South (row+1 mod H), 3=West (col-1 mod W).
  Toroidal wrap uses MATHEMATICAL (Euclidean) modulo: the result is
  always in [0, H-1] or [0, W-1] respectively, even though row-1 or
  col-1 is negative in ordinary integer arithmetic before the modulo is
  applied.
- Field encoding (arg1 mod 4), frozen: 0=opcode, 1=arg0, 2=arg1,
  3=payload.
- Seed type: uint64, supplied at world-construction time, constant for
  the lifetime of a run and every replay of it.
- Tick type and initial value: uint64 counter, initial value 0 at S[0]
  (before any tick has executed). Incremented by exactly 1 per commit;
  the transition S[t] -> S[t+1] uses tick=t as the arbitration input.
- Tick-overflow behavior (frozen, was UNSPECIFIED in the prior
  candidate): a step attempted FROM tick == 2^64 - 1 is REJECTED --
  raised as an explicit error -- rather than wrapping to 0. No AETH-00
  run silently wraps its tick counter.
- Invalid-input handling: covered above for dimensions/buffer length.
  Opcode/arg0/arg1/payload are uint8 by construction (0-255) so cannot
  themselves be invalid as stored state; any opcode other than 0x01 is
  not invalid input, it is the specified RESERVED_INERT case (frozen,
  above -- Q27), never "unknown" and never treated as becoming 0x00.
- Same-value writes: a WRITE proposal whose value equals the target
  field's tick-start value is a valid proposal like any other and
  competes normally. If it wins, it still counts as proposal_won=true
  (Instrumentation, below) even though stored_bits_changed=false for
  that field. A same-value write must never be specially rejected,
  skipped, or excluded from arbitration.
- Preservation of untargeted fields: any physical field, of any site,
  that is not the target field of any proposal in a given tick --
  winning or losing -- is bit-identical in S[t+1] to its value in S[t].
  This includes fields of a site that is itself a WRITE source, and the
  three fields of a target site not actually contested that tick. This
  also covers every field of every RESERVED_INERT site not targeted
  that tick: its opcode and other fields are preserved byte-for-byte.
- Independent arbitration of different fields: a site's four fields are
  four independent arbitration contests. Proposals targeting different
  fields of the SAME target site never compete with each other, even in
  the same tick; each field's contest uses only the proposals whose
  (target site, target field) match that field.
- Replay identity (frozen): two runs are asserted bit-identical only
  when compared using ALL of (semantics_id, H, W, seed, tick, full
  lattice bytes) at each corresponding tick. A replay-identity claim
  that omits any of these six components is not a valid AETH-00 replay
  test.

### Collision arbitration (FROZEN, aeth00.v1)

Requirement: the winner depends only on (semantics_id, seed, tick,
target site, target field, the set of competing PHYSICAL SOURCE sites)
-- never on iteration, thread, scheduling, batch position, hardware
identity, or implementation identity. Payload is never an input to
arbitration.

All arithmetic below is explicitly unsigned 64-bit; `>>` is a logical
(not arithmetic) right shift; multiplication is modulo 2^64.

Coordinate packing, frozen (replaces the prior 12/12/2/12/12 packed-key
construction and its <4096-per-axis limit -- REMOVED, see Q31):

    C(row, col) = (uint64(row) << 32) | uint64(col)

row and col are each uint32 (0 .. 2^32-1), matching the frozen valid
dimension domain (1 <= H, W <= 2^32-1) above -- C is a bijection from
the full uint32 x uint32 domain onto a 64-bit word, with no
coordinate-range restriction narrower than the transition law's own
domain.

Mix function M (the SplitMix64 finalizer; public-domain, general
integer-hashing technique, not derived from any Prometheus engine):

    M(x):
      u = (x XOR (x >> 30)) * 0xBF58476D1CE4E5B9 mod 2^64
      v = (u XOR (u >> 27)) * 0x94D049BB133111EB mod 2^64
      return v XOR (v >> 31)

M is a bijection on {0,1}^64: each XOR-with-right-shift step is
individually invertible (standard invertible xorshift), and each
multiplication is by an odd constant, a unit modulo 2^64 and therefore
also invertible; the composition of invertible steps is invertible.

Priority construction, frozen (chained, not a single packed key):

    h0       = M(seed XOR 0x9E3779B97F4A7C15)
    h1       = M(h0 XOR tick)
    h2       = M(h1 XOR C(target_row, target_col))
    h3       = M(h2 XOR uint64(target_field))
    priority = M(h3 XOR C(source_row, source_col))

Winner = the competing proposal with the greatest unsigned `priority`
("greatest unsigned priority wins"). No other input (payload,
enumeration order, batch position, implementation identity, hardware
identity) participates.

Proof that a genuine priority tie cannot occur within one contest:
within one contest, seed, tick, target_row, target_col and target_field
are fixed (that is the definition of "contest"), so h0, h1, h2 and h3
are identical across every competing proposal in that contest. The only
input that varies between two DISTINCT competing proposals is
C(source_row, source_col) -- and by the proposal-identity rule above, a
collision requires 2+ DISTINCT physical source sites, which by C's
bijectivity always have distinct C(source_row, source_col) values (no
range restriction: this holds for the full uint32 x uint32 source
domain). XOR with the fixed h3 is a bijection and M is a bijection, so
distinct C(source_row, source_col) implies distinct `priority`.
Therefore all competing priorities within any valid contest are
pairwise distinct, for every H, W in the frozen valid dimension domain
-- with no separately-documented narrower "supported range" as the
prior candidate construction required.

No coordinate tie-break exists in this frozen semantics (removed,
Q31): none is needed, per the proof above. If an implementation ever
produces two proposals sharing the same physical source site within one
contest -- which the proposal-identity rule above forbids -- that is an
IMPLEMENTATION DEFECT, not a case the arbitration law resolves; test
harnesses must detect and fail on it rather than silently picking one
via any residual priority comparison (AETHER_TEST_PLAN.md test 24).

Explicit non-neutrality caveat: this construction produces a
deterministic, order-independent winner. It is NOT claimed to be
spatially, directionally, or temporally unbiased in any statistical
sense -- that is an empirical property to be measured (AETHER_TEST_PLAN.md
arbitration-bias diagnostics), never asserted here. "Deterministic and
order-independent" and "statistically neutral" are different claims;
only the first is made by this specification.

Two alternatives considered and NOT adopted: (a) fixed spatial priority
(e.g. lowest coordinate, or N>E>S>W always wins) -- rejected per
operator's ruling because it is a permanent, systematic
spatial/directional bias baked into every contested tick for the life of
a campaign; (b) explicit segmented sort per target group -- produces the
identical winner (same total order) but is a needless implementation-
strategy commitment for a milestone whose physics does not require
sorting. Full comparison: AETH-00_REVIEW.md.

### Deferred implementation guidance (non-normative, not physics)

The following describes how a future GPU implementation MIGHT realize
the semantics above; it is guidance for an implementer, not part of the
frozen or candidate physics, and is not itself part of AETH-00's
conformance suite (only its behavioral OUTPUT is checked, via CPU/GPU
differential testing, at whichever later milestone builds a GPU
implementation -- AETHER_OPEN_QUESTIONS.md question 30):

one owner (thread/lane) per target site -> it inspects its up to 4
distinct von Neumann physical neighbor sites' decoded state from S[t]
-> determines which, if any, emit a proposal targeting this owner's site
for each of the 4 fields -> independently reduces each field's contest
using the H-comparison above -> writes the result into a SEPARATE
next-state buffer (S[t] is never perturbed in place). No atomic operation,
packed-key atomic, or any other specific GPU primitive is prescribed;
"independently reduces" may be implemented by any technique that
reproduces the H-comparison result specified above.

### Known limitation -- no byte synthesis

AETH-00 cannot synthesize new byte values. WRITE only ever propagates
the issuing site's own payload; no operation in AETH-00 computes a new
value from other values (no arithmetic, no combination). Consequently
the set of distinct byte values present anywhere in a world can only
stay constant or SHRINK over any run, never grow. This is a useful
invariant for testing AETH-00 itself, and it disqualifies AETH-00 from
being treated as a complete primordial physics -- any later milestone
claiming open-ended variation must add a mechanism this milestone does
not have.

### Properties of this frozen physics (not defects)

Recorded here because they are consequences of the design, not
oversights, and should not be "fixed" without a deliberate decision
(any such change requires a new semantics_id):

- Synchronous ticks supply a universal clock shared by every site.
- Toroidal topology permits recurrence and wraparound interaction.
- Von Neumann locality privileges the axes / Manhattan geometry over any
  other notion of distance or neighborhood.
- The four fields (opcode, arg0, arg1, payload) are a designed, typed
  ontology, not an emergent one.
- WRITE privileges outward payload templating (a site can only push its
  own payload outward; it cannot pull, transform, or combine).
- Coordinate-keyed deterministic arbitration creates a time/space-
  dependent forcing field: which proposal wins a given contest is a
  fixed function of (seed, tick, coordinates), not of any physical
  quantity -- itself a designed asymmetry, not a physical force.
- The opcode space is heavily skewed toward inertness by design: 1
  active encoding (WRITE, 0x01) and 255 RESERVED_INERT encodings. This
  is a property of THIS conformance observed instance's ISA budget, not a claim
  about how many active opcodes any eventual primordial substrate
  should have.

### Instrumentation (required now, not deferred)

A production observatory remains deferred (AETHER_SPEC.md, Substrate
qualification philosophy, below). AETH-00's own test traces must already
distinguish three semantically different events per proposal, tagged
with semantics_id:

- `proposal_emitted`: a WRITE-opcode site decoded at S[t] produced a
  proposal (source, target, target_field, value), regardless of whether
  it later wins.
- `proposal_won`: a specific proposal was selected as the arbitration
  winner of its (target site, target_field) contest.
- `stored_bits_changed`: the winning proposal's value differs from the
  pre-tick value of that target field (distinguishes a same-value win,
  which changes nothing physically, from a bit-changing win).

These must not be collapsed into a single boolean.

### Explicit exclusions

No assembly, executable configuration, birth, allocation, evaluation score, task, energy, resource
resource regime, perturbation, configuration transmission detector, structural detector, GPU
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
