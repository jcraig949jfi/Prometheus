# AETH-01 -- repaired freeze CANDIDATE (`aeth01.v1`), post-repair cycle

Status: **CANDIDATE, NOT YET FROZEN.** This document is a clean,
consolidated distillation of `PHYSICS_SPEC_DRAFT.md` after all repairs
in `REPAIR_LEDGER_01.md`, produced because `KILL_GATES_01.md`'s K1, K2,
K3, K6 all PASSED with no unresolved contradiction. It is not a new
design and introduces no new semantics beyond what `REPAIR_LEDGER_01.md`
already dispositioned. Freezing `aeth01.v1` (in the sense AETH-00's
`AETHER_SPEC.md` is frozen) is a separate, explicit act that has NOT
happened here -- this document proposes exactly what would be frozen,
for review, and gates the next steps (CPU oracle, tests, GPU, canary)
on this specific text, not on the pre-repair draft.

## 1. World / site state (unchanged from the design sprint)

Toroidal H x W lattice, 5 uint8 fields per site: `opcode, arg0, arg1,
payload, energy`. `1 <= H, W <= 2^32-1`. Fields 0-3 keep AETH-00's
overwrite semantics; field 4 is conservatively transported, never
overwritten outright.

## 2. Run parameters (part of replay identity)

    WRITE_COST        uint8  [0,255]
    MAINTENANCE_COST  uint8  [0,255]
    REPLENISH_NUMER   uint64 [0, 2^32]   -- widened; logical domain is 0..=2^32
    REPLENISH_AMOUNT  uint8  [0,255]
    MUT_NUMER         uint64 [0, 2^32]   -- widened; logical domain is 0..=2^32

`(key >> 32) < NUMER` triggers; `NUMER=0` never triggers, `NUMER=2^32`
always triggers (probability exactly 1). Both numerators MUST be stored
in a field wide enough to hold `2^32` exactly (repairs S02(a)).

## 3. Tick semantics (synchronous, 7 phases, extends AETH-00's 5)

1. DECODE: `STARVED = energy < WRITE_COST` for WRITE sites.
2. EMIT: each active, non-starved WRITE site emits exactly one proposal,
   to the selected von-Neumann-neighbor target (`arg0 mod 4`) and field
   (`arg1 mod 5`); fields 0-3 carry `payload`; field 4 carries
   `transfer_amt = min(payload, energy - WRITE_COST)`.
3. ARBITRATE: AETH-00's unmodified SplitMix64 chained-priority law,
   `target_field` as a plain uint64 input (0..4).
4. COMMIT TEMPLATE (fields 0-3): winner's value, after Mu (below), is
   stored; all untargeted bytes preserved exactly.
5. SETTLE ENERGY (field 4), atomically per site: (a) every emitting
   site is debited `WRITE_COST`; (b) every field-4-emitting site is
   further debited its full `transfer_amt`, win or lose; (c) per
   contest, only the winner is credited `min(transfer_amt, 255 -
   target_energy_after_own_debits)` (the delta, saturating); losers' amounts and any
   winner overflow above 255 are destroyed, never refunded/redirected.
   All source debits precede all target credits, including self-transfers.
6. MAINTENANCE: `energy -= min(MAINTENANCE_COST, energy)` (floored).
7. REPLENISH: independent per-site Bernoulli at `REPLENISH_NUMER/2^32`
   credits `min(REPLENISH_AMOUNT, 255 - energy)`.

Phases 1-3 read only `S[t]`.

## 4. Perturbation (`Mu`) -- copy-coupled, fields 0-3 only

Fires ONLY on a winning proposal targeting fields 0-3; never on
untouched bytes, never on field 4, at ANY `MUT_NUMER` including
`2^32`. `key = M(M(M(M(seed XOR MUT_DOMAIN_CONST) XOR tick) XOR
C(row,col)) XOR field)`; `triggered = (key>>32) < MUT_NUMER`;
`bit_index = key AND 0b111`; stored value is the donor's payload,
XOR'd with `1 << bit_index` if triggered, else unchanged. Repeated
overwrite from a FIXED, unmutated donor resets to that donor each time,
not a cumulative walk -- `KILL_GATES_01.md` K2. This does not prove
statistical independence of deterministic hash-keyed events across ticks.

## 5. Replenishment (`Rho`) -- independent per site

Third domain-separated hash chain, same `M`/`C` primitives, own
`REPLENISH_DOMAIN_CONST`. Cross-domain (Mu/Rho/arbitration)
independence is NOT proven beyond a fixed single opportunity (M07,
`ACCEPT_WITH_QUALIFICATION`); an AETH-00A-style stratified statistical
diagnostic at AETH-01's scale is required before relying on it.

## 6. Accounting identity (single, non-double-counting form)

    TotalEnergy[t+1] = TotalEnergy[t] - X - A + C - D + R

`X`=ExecutionCost, `A`=TransferAttempted (gross, win or lose),
`C`=TransferCredited (accepted DELTA, post-saturation), `D`=
MaintenanceRemoved (floor-limited actual), `R`=ReplenishAccepted
(saturation-limited actual). `TransferLost`/`OverflowSpillage` are
derived diagnostics (`A = C + L + O` per contest), never separate terms
in this identity -- summing both forms was the reviewed draft's S01
defect. Verified exactly, zero tolerance, on 6 hand cases spanning
execution-alone, contested transfer, overflow, self-transfer,
maintenance floor, and saturated replenishment (`KILL_GATES_01.md` K1).

## 7. Instrumentation (extends AETH-00's 3 event kinds)

`cell_starved`, `mutation_applied` (with bit index), `energy_debited` /
`energy_credited` / `energy_lost` / `energy_overflow_spilled` /
`energy_decayed` / `energy_replenished` (one row per occurrence, exact
amounts; `energy_decayed` is distinct from `energy_debited` so
maintenance is never "an implied event hidden among debits," S01). An
**independent event-ledger cross-check is REQUIRED** before any trace
is used as scientific evidence: a second, independently-coded pass
reading only raw before/after state (never the production
trace-emission path) must reproduce every tick's events, compared
field-by-field (REQUIREMENTS.md, M09 repair; deferred as K7).

## 8. Complete replay identity (11 components)

`(semantics_id="aeth01.v1", H, W, seed, tick, WRITE_COST,
MAINTENANCE_COST, REPLENISH_NUMER, REPLENISH_AMOUNT, MUT_NUMER, full
lattice bytes)`.

## 9. Differences from AETH-00 (`aeth00.v1`)

- 5th field `energy`, uint8, saturating, conservatively transported.
- `arg1 mod 5` selector (was `mod 4`) -- destroys ALL single-bit
  perturbation-neutral edges for `arg1` (proven exhaustively, K2); no
  power of two is divisible by 5.
- Explicit copy-coupled single-bit perturbation (`Mu`) on fields 0-3,
  breaking AETH-00's "no byte synthesis" property on purpose
  (DECISIONS.md D-AETH01-04).
- `WRITE_COST`/`MAINTENANCE_COST`/replenishment: new scarcity/decay
  mechanics; AETH-00 had none.
- Replay-identity tuple grows from 6 to 11 components.
- Instrumentation adds 8 event kinds to AETH-00's 3 (11 total).

## 10. Differences from the pre-repair draft (`5e41c1d67`)

Every difference below is itemized, reasoned, and falsifier-bearing in
`REPAIR_LEDGER_01.md`; only pointers given here:

- Accounting identity replaced (double-counting removed) -- S01.
- `REPLENISH_NUMER`/`MUT_NUMER` widened to represent `2^32` -- S02(a).
- Heterogeneous-parameter regime narrowed to initial-byte-only overlays
  (no per-zone LAW) -- S02(b).
- Perturbation mechanism description replaced: copy-coupled, not
  autonomous/inactive drift; mod-5 adjacency loss made explicit -- S03,
  M01.
- Configuration transmission has exactly five tiers: STRUCTURAL_RESEMBLANCE,
  CAUSAL_VALUE_CONSTRUCTION, CONSTRUCTED_CAPACITY,
  RECURSIVE_CONSTRUCTION, TRANSMITTED_VARIATION, plus 10 separately
  reported evidence axes -- S04. Resemblance is not a causal prerequisite.
  K3 fixture 3 is distributed construction by A_opcode and A_arg0 with
  initialized scaffold; fixture 4 is recursive activation of preconfigured
  machinery, NOT recursive configuration construction. These fixture-local
  distinctions do not supply a general detector or ensemble evidence.
- Absorption/`FROZEN`/`DEAD` labels downgraded to censored, not proven,
  stops -- S05.
- Provenance `instrument_class` composition rule made explicit and
  contradiction-free across overlays -- S06.
- GPU viability reworded from "proven" to "unmeasured feasibility
  argument" -- M09 (part A).
- Trace on/off tests reworded from proving trace truth to proving only
  noninterference; independent event-ledger cross-check added as a
  requirement -- M09 (part B).
- Economics narrative corrected: template bytes are free at ANY
  maintenance setting; concentration/hoarding can reduce maintenance;
  zero-amount transfers are not inert -- M02, M03.
- N01 CPU-time arithmetic corrected (~10.24s, not "a fraction of a
  second," for the cited example); N02 impossible/overclaimed examples
  corrected; N04 candidate-specification-asymmetry caveat added.
- All numbered falsifiers in DECISIONS.md tightened from vague
  ("reasonably thorough") to specific, bounded, preregistered criteria
  -- B03.

## 11. Carried-forward, explicitly unresolved

R3 (perturbation excludes resource field), R5 (exogenous initial-energy
persistence confound), R14 (no branch/compare primitive), M07's
cross-domain hash independence (unmeasured, not redesigned), and K4/K5/
K7/K8 (deferred, `KILL_GATES_01.md`) remain open. None blocks this
candidate; all are named, not hidden, per doctrine.

## 12. What happens next

This candidate does not become `aeth01.v1` in the AETH-00 sense until:
(a) an independent CPU oracle is built against this exact text; (b)
contract/property/instrument tests (Design Task 6/K1-K3/K6-style) pass
against it; (c) K7's oracle/trace agreement audit passes. Those are the
remaining steps in this repair cycle, tracked in
`REVIEW_PACKET_REPAIR_01.md`.
