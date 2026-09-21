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

    WRITE_COST        uint8    in [0,255]     -- execution cost per WRITE
    MAINTENANCE_COST  uint8    in [0,255]     -- passive per-tick decay
    REPLENISH_NUMER   u33      in [0,2^32]    -- per-cell inflow probability
                                                 numerator, denominator 2^32
    REPLENISH_AMOUNT  uint8    in [0,255]     -- energy credited on inflow
    MUT_NUMER         u33      in [0,2^32]    -- per-write mutation
                                                 probability numerator,
                                                 denominator 2^32

**[REPAIRED per ASTRA_REVIEW_01.md S02(a), see REPAIR_LEDGER_01.md]**
`REPLENISH_NUMER` and `MUT_NUMER` have legal domain `0..=2^32`
inclusive -- a 33-bit range, NOT representable in a 32-bit word. They
must be stored in a machine word wide enough to hold `2^32` exactly
(a 64-bit unsigned field is the obvious, sufficient choice regardless
of implementation language; "u33" above names the LOGICAL domain, not
a literal bit-width requirement). The trigger condition
`(key >> 32) < NUMER` is unchanged arithmetic and is now exactly
correct at both ends: `NUMER=0` never triggers, `NUMER=2^32` always
triggers (probability exactly 1), since `key >> 32` ranges over
`0..=2^32-1`, strictly less than `2^32` in every case. The originally
declared `uint32` type could not hold the declared `2^32` endpoint at
all -- a plain representability error, not a design choice.

All five are explicit scalar configuration, analogous to AETH-00's
seed: never inferred, never defaulted silently, always logged with a
run's provenance (REQUIREMENTS.md). All five apply UNIFORMLY to the
entire lattice for the lifetime of a run -- there is no per-zone or
per-cell parameter map in `aeth01.v1` (see EXPERIMENTS.md regime 7's
repaired scope, S02(b)).

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

**[REPAIRED per ASTRA_REVIEW_01.md M01, ACCEPT_WITH_QUALIFICATION, see
REPAIR_LEDGER_01.md]** `arg1 mod 5` is NOT a harmless additive
extension of AETH-00's `arg1 mod 4`: because no power of two is
divisible by 5, EVERY single-bit flip of `arg1` changes its target-field
residue -- AETH-00's "top six bits of `arg1` are mutation-neutral"
property does not survive this extension at all, for any bit. The
256-value encoding is also non-uniform across the 5 targets (52 byte
values select field 0; 51 each select fields 1-4). This is stated here
as a factual, accepted property of the frozen encoding, not a defect to
be fixed by re-encoding: changing the selector to restore neutrality
would itself be an unreviewed physics change trading one hidden prior
for another (REPAIR_LEDGER_01.md M01). `KILL_GATES_01.md` K2 gives the
exhaustive 256-value x 8-bit-position adjacency table.

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

**[REPAIRED per ASTRA_REVIEW_01.md S03, see REPAIR_LEDGER_01.md --
supersedes the "Representation & accessibility analysis" section
below's original claims about autonomous/dormant drift.]** Mutation is
**copy-coupled**: it is an error process attached to a SUCCESSFUL
incoming WRITE event only, never an autonomous process on stored or
dormant bytes. Precisely: `Mu` is invoked once per winning proposal
targeting fields 0-3, and never otherwise. A byte that is never the
target of a winning WRITE proposal NEVER changes, at ANY `MUT_NUMER`
value including `MUT_NUMER = 2^32` (probability 1) -- there is no
process anywhere in this specification that mutates a byte that is not
being written to. Concretely, from donor payload `p`: with probability
`1 - MUT_NUMER/2^32` the stored value is exactly `p`; with probability
`MUT_NUMER/2^32` it is one of `p`'s 8 Hamming-1 neighbors, each with
conditional probability 1/8 (never `p` itself -- flipping any bit
always changes the byte). "Dormant machinery survives for free" (true,
see accessibility analysis below) and "dormant machinery MUTATES for
free" (false) are two different, non-implied properties; only the
first is claimed. No background mutation is added to rescue any
previously stated intuition -- the choice to make mutation copy-coupled
is stated here as intentional, not repaired away.

## Replenishment (Rho) -- per cell, independent

    r0  = M(seed XOR REPLENISH_DOMAIN_CONST)
    r1  = M(r0 XOR tick)
    key = M(r1 XOR C(row, col))
    triggered = (key >> 32) < REPLENISH_NUMER

`REPLENISH_DOMAIN_CONST` is a third frozen 64-bit odd constant, distinct
from both the arbitration and mutation constants (proposed:
`0x2545F4914F6CDD1D`). Three independent hash domains (arbitration,
mutation, replenishment) share the same validated `M` primitive.

**[REPAIRED per ASTRA_REVIEW_01.md M07, ACCEPT_WITH_QUALIFICATION, see
REPAIR_LEDGER_01.md]** The original claim that the three domains "never
share input material in a way that would correlate their outcomes" is
an OVERCLAIM and is withdrawn. What is actually established: (1) for a
FIXED opportunity (a specific cell, tick, and field), the `Mu` key is
uniform over its input domain, and its trigger bits (top 32) and
bit-index bits (bottom 3) are exactly independent by construction of a
bijective mix -- this positive result is real. (2) Cross-domain,
cross-tick, or realized-trajectory independence is NOT proven: an exact
tick offset can be constructed (see ASTRA_REVIEW_01.md M07 derivation)
that makes the mutation and replenishment chains' internal words
coincide at matched cells. Whether this is practically exploitable
within any actual campaign's tick range is an open, unmeasured
statistical question, not a proven defect -- the hash is NOT redesigned
in response to this finding (per operator instruction and Astra's own
"do not redesign the hash" guidance); an AETH-00A-style stratified
statistical diagnostic, rerun at AETH-01's scale, is required before any
cross-domain independence is relied upon for a scientific claim.

## Conserved / accounted quantities

**[REPAIRED per ASTRA_REVIEW_01.md S01, ACCEPT, see REPAIR_LEDGER_01.md
-- this section supersedes the reviewed-design identity, which
double-subtracted dissipated transfers; proven wrong by a 2-donor
counterexample there.]**

Energy is NOT a strict invariant (there are explicit sources and
sinks), but every unit's fate is fully accounted every tick. Let, for a
given tick and cell: `X` = ExecutionCost (step 5a), `A` =
TransferAttempted (step 5b, everything debited from a source attempting
a field-4 proposal, win or lose), `C` = TransferCredited (step 5c,
winners only, ALREADY net of saturation -- i.e. `C` is the ACCEPTED
amount, not the winning proposal's raw attempted amount), `D` =
MaintenanceRemoved (step 6, the ACTUAL floor-limited amount subtracted,
i.e. `min(MAINTENANCE_COST, energy after step 5)`), and `R` =
ReplenishAccepted (step 7, the ACTUAL amount credited after saturation
at 255 -- distinct from the gross `REPLENISH_AMOUNT`, which may be
partially or fully rejected by saturation). The ONE authoritative
identity is:

    TotalEnergy[t+1] = TotalEnergy[t] - ExecutionCost[t] - TransferAttempted[t]
                        + TransferCredited[t] - MaintenanceRemoved[t]
                        + ReplenishAccepted[t]

`TransferLost[t]` (destroyed losing amounts) and `OverflowSpillage[t]`
(destroyed winning-but-saturated amounts) remain separately traced,
forensically important quantities (ADVERSARIAL_ANALYSIS.md #17), but
they are DERIVED diagnostics, not independent terms in the identity:
at each (target, field=4) contest, `TransferAttempted = TransferCredited
+ TransferLost + OverflowSpillage` holds by definition of how a contest
resolves, so subtracting `TransferLost` and `OverflowSpillage`
SEPARATELY, in addition to the `-TransferAttempted[t] + TransferCredited[t]`
pair, double-counts them -- this was exactly the reviewed draft's error.
An equivalent, non-double-counting restatement (useful as a cross-check,
not a second identity) is
`TotalEnergy[t+1] = TotalEnergy[t] - X - L - O - D + R`, using only the
LOST and OVERFLOW amounts and omitting `A`/`C` entirely; the two forms
are algebraically identical (`A = C + L + O`) and must never be summed
together.

This equation is a required property-based test target (REQUIREMENTS.md):
every term is independently observable from the trace (Instrumentation,
below), so the equation must hold exactly, every tick, every run, with
zero tolerance (all integer arithmetic). See `KILL_GATES_01.md` K1 for
6 hand-worked reconciliation cases.

## Creation / destruction rules

No opcode, arg0, arg1, or payload byte value is ever created from
nothing except by Mu's explicit single-bit flip (a deliberate,
accounted exception to AETH-00's "no byte synthesis" limitation -- see
DECISIONS.md D-AETH01-04). No energy unit is created except by explicit
Replenish (step 7, the ACCEPTED/post-saturation amount). No energy unit
is destroyed except by explicit **ExecutionCost** (step 5a --
**[REPAIRED per ASTRA_REVIEW_01.md S01: the reviewed draft's exhaustive
destruction list omitted execution expenditure entirely, even though
step 5a unconditionally removes energy with no destination]**),
MaintenanceDecay (step 6, floor-limited), TransferLost (step 5c losers),
or OverflowSpillage (step 5c saturation on the winner). There is no
other creation/destruction path.

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
`energy_overflow_spilled` / `energy_decayed` / `energy_replenished`
(one row per occurrence, each carrying the exact amount, so the
conservation equation above can be checked line-by-line against the
trace, not just against final totals). **[REPAIRED per
ASTRA_REVIEW_01.md S01, ACCEPT, see REPAIR_LEDGER_01.md]** `D`
(MaintenanceRemoved) requires its own named `energy_decayed` event,
distinct from `energy_debited` (which is reserved for `X`/`A`, the
WRITE_COST and transfer-attempt debits) -- the reviewed draft left
maintenance as "an implied event hidden among debits," which S01
explicitly named as a defect; this closes that gap.

## Representation & accessibility analysis (Design Task 3)

**[REPAIRED per ASTRA_REVIEW_01.md S03, see REPAIR_LEDGER_01.md and
the "Mutation (Mu)" section above, which is now the authoritative
description of the mechanism this analysis describes.]**

**One-step variation is copy-coupled, not autonomous.** The
finest-grained physical event is a single Mu-triggered bit flip inside
one already-COPIED byte (i.e. one that just won a WRITE contest) --
Hamming distance 1 from the winning donor's payload, at a rate the
experimenter controls (`MUT_NUMER`). This is much smoother than a
discrete-genome insertion/deletion/point-mutation alphabet, but each
copy event is DONOR-CONDITIONED, not an accumulating random walk: a
winning WRITE replaces the target's byte with the CURRENT donor's
payload, optionally flipping one bit of THAT value; it does not build
on the target's own prior history. A fixed donor `p` can therefore only
ever place `p` itself or one of `p`'s 8 Hamming-1 neighbors at the
target on any single copy event, however many times that same donor
wins -- repeated overwrite from a fixed donor never cumulatively
random-walks the target through byte space (e.g. a fixed donor of 0 can
place only 0 or a power of two, never 3, no matter how many times it
wins; ASTRA_CLOSURE_REVIEW_02.md section 3, K8/T/test_aeth01_kill_gates.py).
Reaching a value outside a fixed donor's 9-value reachable set requires
a DIFFERENT donor to win a later contest, which is an accessibility
question (a route, a live and differently-valued source, sufficient
energy, and contest survival), not a property of the mutation alphabet
alone. A byte that is never the target of a winning WRITE never changes
at all, regardless of `MUT_NUMER` (see "Mutation (Mu)" above).

**Categorical cliffs exist but are narrow, not sheer, and are
donor-conditioned.** The opcode field is an ordinary byte subject to
the same copy+Mu process as any other field, so "waking up" a
RESERVED_INERT neighbor (any value -> 0x01) or "putting a WRITE cell to
sleep" (0x01 -> any other value) rides the same smooth mutation
channel, but the activation probability for a single copy event from a
FIXED donor byte `p` is **not** a generic 1-in-8: for uniform per-bit
mutation sampling, the marginal probability that a copy event from
donor `p` writes exactly `0x01` is
`(1-mu)*[p=1] + (mu/8)*[popcount(p XOR 1)=1]`, where `mu=MUT_NUMER/2**32`
and `[.]` is 1 if the bracketed condition holds, else 0. A fixed donor
of `p=1` therefore activates with probability `1-mu` copy-for-copy
(already active, most copies preserve it), not 1/8; a fixed donor with
`popcount(p XOR 1)!=1` never activates by mutation from that donor at
all (e.g. donor 0 never activates: `popcount(0 XOR 1)=1` is true, so it
DOES activate at rate `mu/8` -- but a donor such as 3, with
`popcount(3 XOR 1)=1` false, activates at rate 0 from that source).
"Approximately 1-in-8" is at best a loose description of the mutation
kernel's own branching factor, not of realized activation probability,
which depends on which donor is actually copying. This remains a
directly measurable, testable quantity (a natural HABITABILITY.md
observable: measured activation rate vs. `MUT_NUMER`, conditioned on
the donor actually observed), not a closed-form constant.

**Neutral networks are large by construction, but require copy traffic
to explore, same as any other mutation.** 255 of 256 opcode values
behave identically (RESERVED_INERT). This is a large neutral plateau IF
and only if the byte in question keeps being re-copied (by winning
WRITEs) -- a dormant cell's opcode byte that is NEVER targeted by a
winning WRITE stays exactly where it started, forever, at any
`MUT_NUMER` (S03 repair, above). What is unconditionally true and
architecturally cheap is the SURVIVAL half of R6's "dormant machinery
survives to completion" case: a non-WRITE cell pays no `WRITE_COST` and
(if `MAINTENANCE_COST=0`) no decay either, so it can sit inert
indefinitely, unchanged, until a WRITE (its own future activation, or a
neighbor's write) touches it. The EXPLORATION half (neutral drift while
dormant) is NOT free -- it requires the dormant byte to be a live
target of repeated winning writes, which is an accessibility question
(does a copier route to it, does it survive contest, etc.), not a
property of the mutation alphabet alone.

**Multi-component cooperative construction is common but not
structurally forced.** One WRITE touches exactly one field of ONE
neighbor per tick from a given source; however, a single target cell
CAN receive up to 4 simultaneous winning writes in one tick, one from
each of its 4 von Neumann neighbors, each targeting a DIFFERENT field
(e.g. all 4 non-energy fields updated at once by 4 distinct sources) --
**[REPAIRED per ASTRA_REVIEW_01.md N02: the reviewed draft's "necessarily
accumulates over multiple ticks" was an overclaim; multi-source,
single-tick construction of a complete 4-field tuple is possible]**.
Sequential, multi-tick, partial construction remains the ONLY way a
single SOURCE acting alone (one field per tick) can build a multi-byte
mechanism at one target, and is expected to be the common case, but it
is not the only structurally possible path.

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
