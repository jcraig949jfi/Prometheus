# AETH-01 -- formal physics draft ("Costed Executable Lattice")

Status: DRAFT candidate specification, semantics_id `aeth01.v1` (NOT
frozen; numeric constants below are proposed, not final). This document
must be precise enough for two independent implementers to build
matching simulators, in the style of `AETHER_SPEC.md`'s frozen AETH-00
text, which it extends additively. AETH-00's own frozen text is not
altered anywhere.

## World state

A toroidal 2-D lattice of H x W sites, 1 <= H, W <= 2^32-1 (inherited
domain), plus scalar run parameters (below) that are fixed for the
lifetime of a run and every replay of it, exactly like AETH-00's seed.
"Lattice bytes" = the full H*W*5 uint8 buffer, row-major, field order
(opcode, arg0, arg1, payload, energy).

## Site / matter state

Five uint8 fields per site: `opcode, arg0, arg1, payload, energy`.
Fields 0-3 are unchanged in meaning from AETH-00. Field 4 (`energy`,
new) is a locally-held, conservatively-transported resource quantity,
range 0-255, saturating (never wraps).

## Run parameters (fixed per run; part of replay identity)

    WRITE_COST        uint8   in [0,255]   -- execution cost per WRITE
    MAINTENANCE_COST  uint8   in [0,255]   -- passive per-tick decay
    REPLENISH_NUMER   uint32  in [0,2^32]  -- per-cell inflow probability
                                              numerator, denominator 2^32
    REPLENISH_AMOUNT  uint8   in [0,255]   -- energy credited on inflow
    MUT_NUMER         uint32  in [0,2^32]  -- per-write mutation
                                              probability numerator,
                                              denominator 2^32

All five are explicit scalar configuration, analogous to AETH-00's
seed: never inferred, never defaulted silently, always logged with a
run's provenance (REQUIREMENTS.md).

## Neighborhood / interaction relation

Unchanged from AETH-00: von Neumann, toroidal wrap, mathematical
modulo. Direction encoding (arg0 mod 4) and coordinate orientation
unchanged.

## Field encoding (arg1 mod 5, extended from mod 4)

    0=opcode  1=arg0  2=arg1  3=payload  4=energy (new)

Fields 0-3 keep AETH-00's overwrite semantics exactly (the value
written is the issuing cell's own payload, subject to mutation below).
Field 4 has different (conservative-transfer) semantics, specified
below -- it is a different KIND of field, not a fifth ordinary
overwrite target, and this is a deliberate, load-bearing asymmetry.

## Instruction set

Unchanged opcode budget: 0x01 = WRITE, all other 255 values =
RESERVED_INERT (0x00 conventionally NOP), same RESERVED_INERT
guarantees as AETH-00 (never traps, preserved byte-for-byte unless
targeted, remains writable). A cell that decodes WRITE at S[t] but
lacks sufficient `energy` (below) is treated as RESERVED_INERT for
proposal-emission purposes that tick only -- its opcode byte itself is
untouched by starvation; starvation affects behavior, not stored state.

## Tick semantics (synchronous; extends AETH-00's five-phase tick)

    S[t]
      -> (1) DECODE: every cell decodes S[t]; a WRITE cell computes
             STARVED = (S[t].energy at that cell < WRITE_COST)
      -> (2) EMIT: each non-RESERVED_INERT, non-STARVED WRITE cell
             emits exactly one proposal, computed purely from S[t]:
               target      = von Neumann neighbor per arg0 mod 4
               target_field= arg1 mod 5
               value       = this cell's own payload            (fields 0-3)
               transfer_amt= min(this cell's own payload,
                                  S[t].energy at this cell - WRITE_COST)
                                                                  (field 4 only)
      -> (3) ARBITRATE: for each (target cell, target_field) with >=1
             proposal, select the winner via AETH-00's UNCHANGED
             SplitMix64 chained priority law (target_field is just a
             uint64 input to h3; the law is defined for any uint64
             value and needs no modification for the 0..4 range)
      -> (4) COMMIT TEMPLATE (fields 0-3): the winning value, after
             mutation (below), is stored; untargeted fields of every
             cell are preserved byte-for-byte, exactly as AETH-00
      -> (5) SETTLE ENERGY (field 4), all as one atomic step per cell:
             (a) every cell that emitted ANY proposal this tick
                 (fields 0-3 or field 4) is debited WRITE_COST from its
                 S[t] energy value (source-side, unconditional, applies
                 whether the proposal won or lost)
             (b) every cell that additionally emitted a field-4
                 proposal is further debited its own transfer_amt
                 (source-side, unconditional -- attempting a transfer
                 always costs the sender the attempted amount)
             (c) for each (target, field=4) contest, ONLY the winning
                 proposal's transfer_amt is credited to the target
                 (saturating at 255; any amount above 255 is destroyed,
                 counted as overflow spillage); every losing
                 proposal's already-debited transfer_amt is destroyed
                 (dissipated, not refunded, not delivered anywhere)
      -> (6) MAINTENANCE DECAY: every cell's energy (after step 5) is
             reduced by MAINTENANCE_COST, floored at 0 (never negative)
      -> (7) REPLENISH: for every cell, independently, a deterministic
             Bernoulli draw (function Rho, below) at rate
             REPLENISH_NUMER/2^32 credits REPLENISH_AMOUNT energy
             (saturating at 255)
    S[t+1]

Steps 1-3 are a pure function of S[t] only (no phase reads anything
produced later in the same tick) -- this preserves AETH-00's "reads
only the tick-start snapshot" invariant exactly.

## Mutation (Mu) -- fields 0-3 only, never field 4

For a winning proposal targeting (target_row, target_col, target_field)
in {0,1,2,3} at tick `t` under run seed `seed`:

    g0  = M(seed XOR MUT_DOMAIN_CONST)
    g1  = M(g0 XOR tick)
    g2  = M(g1 XOR C(target_row, target_col))
    key = M(g2 XOR uint64(target_field))
    triggered  = (key >> 32) < MUT_NUMER
    bit_index  = key AND 0b111                      (bottom 3 bits)
    stored_value = triggered ? (winning_value XOR (1 << bit_index))
                              : winning_value

`M` and `C` are AETH-00's unchanged bijective mix and coordinate-pack
functions. `MUT_DOMAIN_CONST` is a frozen 64-bit odd constant distinct
from AETH-00's arbitration constant (proposed: `0xD1B54A32D192ED03`, a
public-domain SplitMix64-family constant, not derived from any
Prometheus engine). Mutation NEVER influences which proposal wins
(computed after arbitration, over a domain-separated hash chain that
does not reuse the arbitration `priority` value) and never applies to
field 4, preserving conservation exactly.

## Replenishment (Rho) -- per cell, independent

    r0  = M(seed XOR REPLENISH_DOMAIN_CONST)
    r1  = M(r0 XOR tick)
    key = M(r1 XOR C(row, col))
    triggered = (key >> 32) < REPLENISH_NUMER

`REPLENISH_DOMAIN_CONST` is a third frozen 64-bit odd constant, distinct
from both the arbitration and mutation constants (proposed:
`0x2545F4914F6CDD1D`). Three independent hash domains (arbitration,
mutation, replenishment) share the same validated `M` primitive but
never share input material in a way that would correlate their
outcomes.

## Conserved / accounted quantities

Energy is NOT a strict invariant (there are explicit sources and
sinks), but every unit's fate is fully accounted every tick:

    TotalEnergy[t+1] = TotalEnergy[t]
                        + Replenished[t]         (step 7)
                        - ExecutionCost[t]        (step 5a)
                        - TransferAttempted[t]    (step 5b, all of it,
                                                    win or lose)
                        + TransferCredited[t]     (step 5c winners only;
                                                    subset of
                                                    TransferAttempted)
                        - TransferLost[t]         (step 5c losers;
                                                    = TransferAttempted
                                                      - TransferCredited
                                                      - OverflowSpillage)
                        - OverflowSpillage[t]     (step 5c saturation)
                        - MaintenanceDecay[t]     (step 6, floor-limited)

This equation is a required property-based test target (REQUIREMENTS.md):
every term is independently observable from the trace (Instrumentation,
below), so the equation must hold exactly, every tick, every run, with
zero tolerance (all integer arithmetic).

## Creation / destruction rules

No opcode, arg0, arg1, or payload byte value is ever created from
nothing except by Mu's explicit single-bit flip (a deliberate,
accounted exception to AETH-00's "no byte synthesis" limitation -- see
DECISIONS.md D-AETH01-04). No energy unit is created except by explicit
Replenish (step 7); no energy unit is destroyed except by explicit
MaintenanceDecay, TransferLost, or OverflowSpillage. There is no other
creation/destruction path.

## Boundary conditions

Toroidal wrap, inherited unchanged from AETH-00.

## Invalid states / invalid input

Same dimension, buffer-length, and byte-range validation as AETH-00,
extended to the 5th field (energy must be a valid uint8, buffer length
must be exactly H*W*5). All five run parameters must be within their
stated ranges (above) or construction must raise, never silently clamp.
`WRITE_COST=0`, `MAINTENANCE_COST=0`, `REPLENISH_NUMER=0`, and
`MUT_NUMER=0` are all valid (they are simplifying/adversarial regime
choices, not invalid input -- see ECONOMICS.md).

## Movement / transport

There is no primitive that relocates an (opcode, arg0, arg1, payload)
tuple as a unit. The only transport primitives are: (a) value
templating (WRITE on fields 0-3, i.e. AETH-00's mechanism, which can
make a copy of a byte appear elsewhere but never removes it from the
source) and (b) conservative energy transfer (field 4, which DOES
remove the transferred amount from the source). This is a deliberate
scope limit, not an oversight -- recorded in DECISIONS.md.

## Initialization

A world is initialized by supplying H, W, the five run parameters, and
an explicit H*W*5-byte buffer (every field of every cell set
explicitly; no implicit default beyond what the caller supplies).
Concrete initialization REGIMES (random soup, sparse soup, structured
controls, resource-rich/poor, heterogeneous) are experimental design,
not physics -- specified in EXPERIMENTS.md.

## Complete replay state (draft replay identity, `aeth01.v1`)

Two runs are bit-identical replays only when compared using ALL of:
`(semantics_id="aeth01.v1", H, W, seed, tick, WRITE_COST,
MAINTENANCE_COST, REPLENISH_NUMER, REPLENISH_AMOUNT, MUT_NUMER, full
lattice bytes)` at each corresponding tick -- AETH-00's six-component
tuple extended with the five new scalar run parameters, since they are
now causally load-bearing inputs to the transition law, not
observational metadata.

## Instrumentation (extends AETH-00's three event kinds)

In addition to AETH-00's `proposal_emitted`, `proposal_won`,
`stored_bits_changed`, AETH-01 traces must also emit, per tick:
`cell_starved` (a WRITE cell was blocked by insufficient energy),
`mutation_applied` (Mu triggered, with the bit index flipped),
`energy_debited` / `energy_credited` / `energy_lost` /
`energy_overflow_spilled` / `energy_replenished` (one row per
occurrence, each carrying the exact amount, so the conservation
equation above can be checked line-by-line against the trace, not just
against final totals).

## Representation & accessibility analysis (Design Task 3)

**One-step variation.** The finest-grained physical event is a single
Mu-triggered bit flip inside one already-copied byte -- Hamming
distance 1, at a rate the experimenter controls (`MUT_NUMER`). This is
much smoother than a discrete-genome insertion/deletion/point-mutation
alphabet: any byte value is reachable from any other in at most 8
one-step events, and most single steps change behavior only slightly
(payload content) rather than categorically.

**Categorical cliffs exist but are narrow, not sheer.** The opcode
field is an ordinary byte subject to the same copy+Mu process as any
other field, so "waking up" a RESERVED_INERT neighbor (any value ->
0x01) or "putting a WRITE cell to sleep" (0x01 -> any other value) rides
the same smooth mutation channel. But it is directionally lopsided:
from `0x00`, exactly 1 of the 8 possible single-bit flips reaches WRITE
(the LSB); the other 7 land on other RESERVED_INERT values. From
`0x01`, 7 of 8 single-bit flips deactivate the cell; the 8th (bit 0)
gives `0x00`, still inert. So "activation" is an approximately
1-in-8-per-mutation-event target, not a zero-measure cliff and not
free -- a directly measurable, testable quantity (a natural
HABITABILITY.md observable: measured activation rate vs. `MUT_NUMER`).

**Neutral networks are large by construction.** 255 of 256 opcode
values behave identically (RESERVED_INERT); a dormant cell's opcode
byte can drift through nearly the entire inert subspace under mutation
with zero functional consequence -- a large neutral plateau. This
directly supports "dormant/incomplete machinery surviving": a
non-WRITE cell pays no WRITE_COST and (if MAINTENANCE_COST=0) no decay
either, so it can sit inert indefinitely while its non-opcode bytes
(arg0/arg1/payload) drift neutrally, potentially pre-positioning a
"latent" configuration that only becomes functional once its opcode
byte is later flipped to WRITE by chance or by a neighbor's write --
this is architecturally exactly R6's "dormant machinery survives to
completion" case, not merely possible but structurally cheap.

**Multi-component cooperative construction is structurally forced, not
optional.** One WRITE touches exactly one field of one neighbor per
tick; there is no multi-field or multi-cell atomic write. Any
coherent multi-byte "mechanism" (a working opcode+arg0+arg1+payload
tuple that does something specific) necessarily accumulates over
multiple ticks, frequently from more than one physical source cell --
partial, incremental construction is the ONLY way anything nontrivial
can be built, which directly supports Design Task 3's "spatial partial
construction creates smoother paths" and "multiple components can
incrementally cooperate."

**Likely accessibility moats introduced by AETH-01 itself:**

1. Von Neumann/toroidal locality caps causal influence at 1 cell/tick
   (a "speed limit"), inherited from AETH-00 but now economically
   reinforced (WRITE_COST makes "reaching far" via relay chains
   expensive per hop) -- likely privileges small, compact, fast-cycling
   organization over large, slow, spread-out organization.
2. Mutation is defined to NEVER touch field 4 (energy), while the
   conservative transfer mechanism is the ONLY way energy state
   changes. This means "how to handle resources" cannot itself be a
   heritable, mutable trait encoded the same way "what to write where"
   is -- it can only be expressed indirectly, through the (heritable)
   fields 0-3 content that decides WHEN and WHERE a transfer is
   attempted. This is a hidden prior that partially pre-decides where
   heredity "lives" (in the instruction fields, not the resource
   field), in tension with R3's instruction not to presume this in
   advance -- flagged, not hidden (DECISIONS.md, ADVERSARIAL_ANALYSIS.md).
3. A flat, content- and distance-independent `WRITE_COST` is an
   arbitrary economic landscape (every WRITE costs the same regardless
   of target field, direction, or distance) -- likely privileges
   "cheap trivial writes repeated often" over "expensive precise writes
   done rarely," an artifact of the cost model's simplicity, not a
   physical derivation.
4. A single active opcode (WRITE) means there is no explicit
   conditional/compare/branch primitive -- "sense, then act
   differently" is not directly expressible; any apparent
   conditionality can only emerge indirectly (e.g., a starved cell
   simply fails to act) rather than as a designed decision. This is an
   expressivity ceiling worth flagging for AETH-02, not a claim that
   AETH-01 is complete.
