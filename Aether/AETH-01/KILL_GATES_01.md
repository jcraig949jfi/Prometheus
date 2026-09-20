# AETH-01 -- KILL_GATES_01: adjudicated outcomes for K1, K2, K3, K6

Status: hand-worked adjudication, this repair cycle. Scope per operator
instruction: K1 (accounting), K2 (mutation/accessibility), K3 (relay vs
constructed capacity), K6 (provenance composition) only. K4/K5/K7/K8
are explicitly DEFERRED (see bottom) -- none of them can be adjudicated
by hand alone; each requires either a running CPU oracle, a completed
sweep, or a GPU package that do not exist yet in this cycle.

No implementation exists yet. Every number below is a hand-derivation
against `PHYSICS_SPEC_DRAFT.md`'s repaired transition law and
`HEREDITY_REQUIREMENTS.md`'s repaired tier ladder, to be used as golden
vectors once the CPU oracle is built (REQUIREMENTS.md Part 2).

## K1 -- accounting identity hand ledger

Using the repaired identity (`PHYSICS_SPEC_DRAFT.md`, S01 repair):
`TotalEnergy[t+1] = TotalEnergy[t] - X - A + C - D + R`.

1. **Execution alone.** One cell, energy=100, `WRITE_COST=5`, a
   fields-0-3 WRITE only (no field-4 proposal): `X=5, A=C=D=R=0`.
   `100-5-0+0-0+0=95`. Matches direct computation (`100-5=95`). PASS.
2. **Two competing donors.** P (energy=50) attempts 30, Q (energy=80)
   attempts 40, into an empty target (energy=0); P wins. `WRITE_COST=5`
   each. `X=5+5=10`, `A=30+40=70`, `C=30` (winner's full amount, no
   saturation), `D=R=0`. `130-10-70+30-0+0=80`. Direct: P->50-35=15,
   Q->80-45=35, target->0+30=30, sum=80. PASS.
3. **Overflow.** Single uncontested proposal, energy=200,
   `WRITE_COST=2`, attempted `A=198`, target starts at 100 (headroom
   155). Credited DELTA `C=min(198,255-100)=155` (NOT the raw attempted
   amount -- this distinction is the point of the check), overflow
   `O=198-155=43`. `A=C+L+O` check: `198=155+0+43`. Identity:
   `300-2-198+155-0+0=255`. Direct: source->200-200=0, target->100+155=
   255, sum=255. PASS. **Finding:** `C` in the identity is always the
   accepted DELTA, never the winner's raw attempted amount; conflating
   the two (as the reviewed draft implicitly did) is exactly how S01's
   double-count arose.
4. **Self-transfer** (`W=1` or any dimension-1 aliasing case,
   ADVERSARIAL_ANALYSIS.md #13). Single cell, energy=50, `WRITE_COST=3`,
   proposes a self-targeting transfer of `A=47` (uncontested).
   Debits first: `50-3-47=0`; credit then applies to the SAME
   already-debited running total: `C=min(47,255-0)=47`; final `=47`.
   Identity: `50-3-47+47-0+0=47`. PASS. **Finding:** self-transfer nets
   to exactly `-WRITE_COST` (here `50->47`) with zero creation, at any
   dimension -- confirms #13's repaired boring explanation exactly,
   independent of toroidal degeneracy.
5. **Maintenance floor.** Energy=2 entering step 6, `MAINTENANCE_COST=5`.
   `D=min(5,2)=2` (floored, never negative). `2-0-0+0-2+0=0`. Direct:
   `2-2=0`. PASS.
6. **Saturated replenishment.** Energy=250 entering step 7,
   `REPLENISH_AMOUNT=20`, triggered. `R=min(20,255-250)=5` (gross 20
   partially rejected). `250-0-0+0-0+5=255`. Direct: `250+5=255`. PASS.

**K1 verdict: PASS.** All 6 cases reconcile exactly under the repaired
identity with zero tolerance; no discrepancy found. These 6 become the
required golden vectors (REQUIREMENTS.md Part 2's "energy conservation
equation... checked as an exact property"). No blocking issue; proceed.

## K2 -- exact conditional mutation graph

1. **All-inert world.** Zero cells decode WRITE => zero proposals =>
   zero winning proposals => `Mu` is invoked exactly 0 times, for
   ANY `MUT_NUMER` including `2^32` (probability 1). This follows
   directly from the spec text ("`Mu`... invoked once per winning
   proposal... and never otherwise") without needing a simulator.
   Falsifies the reviewed draft's "unconditional eight-event
   reachability" claim by direct substitution: an all-inert world has
   zero reachable byte changes at any mutation rate. PASS
   (confirms S03's repair; not a new finding, a direct corollary).
2. **Fixed donor payload, repeated overwrite.** If a donor cell's OWN
   payload field is itself never targeted by any winning WRITE (i.e.
   the donor's `p` is constant across ticks), then each tick's
   overwrite of the SAME target is an independent draw: stored value is
   `p` w.p. `1-MUT_NUMER/2^32`, or one of `p`'s 8 Hamming-1 neighbors
   (uniform 1/8 each) w.p. `MUT_NUMER/2^32` -- **memoryless**, because
   the target's stored value is fully overwritten each time and the
   next tick's draw is keyed on `(seed, tick, target coords,
   target_field)`, not on the target's own previous stored value.
   **Finding:** the "up to 8 Hamming-distance-1 steps away per copy
   event" drift described in PHYSICS_SPEC_DRAFT.md's accessibility
   analysis requires the COPIED VALUE ITSELF to change between copies
   (a chain of distinct copying cells, each possibly mutated in turn) --
   a fixed, unmutated donor produces i.i.d. one-step draws at a fixed
   target, never a cumulative random walk over time. This distinction
   was not explicit anywhere in the packet; it is recorded here as a
   clarifying, non-blocking finding, not a repair (no prior claim
   contradicted it).
3. **256 selector bytes, one-bit adjacency (`arg1 mod 5`).** Proof, not
   enumeration: a single-bit XOR flip of bit `k` changes a byte's
   integer value by exactly `+2^k` or `-2^k` (no carry, since only one
   bit is touched). `2^k mod 5` for `k=0..7` cycles `1,2,4,3,1,2,4,3` --
   never `0 mod 5` (since `gcd(2,5)=1`). Therefore every single-bit flip
   changes `arg1 mod 5` by a nonzero amount mod 5, for all 256 values and
   all 8 bit positions: **0 of 2048 possible (value, bit) edges are
   mod-5-neutral.** This is an exhaustive result obtained by proof, and
   is exact (not sampled). Value-count check: residue 0 has 52 values
   (`0,5,...,255`), residues 1-4 have 51 each (`256=52+4*51`), matching
   PHYSICS_SPEC_DRAFT.md's stated distribution.

**K2 verdict: PASS (findings recorded, no contradiction).** All three
hand-cases are consistent with the repaired spec; M01's accepted
mod-5-destroys-neutrality claim is now a proven exhaustive fact, not an
assertion. No blocking issue; proceed.

## K3 -- relay negative vs constructed-capacity positive

Full fixtures and derivations already hand-worked in
`HEREDITY_REQUIREMENTS.md` ("K3 fixtures"). Adjudicated outcome:

- **Relay fixture** reaches `CAUSAL_VALUE_CONSTRUCTION` at both A->B and
  B->C (payload values are genuinely, verifiably caused) but FAILS
  `CONSTRUCTED_CAPACITY` at every step (ablating A never changes B's own
  opcode/arg0/arg1, confirmed by direct inspection of the fixture: A
  only ever targets B's `payload` field, never B's `opcode`/`arg0`/
  `arg1`).
- **Constructed-capacity fixture** reaches `CONSTRUCTED_CAPACITY` at
  A->B (ablating A's opcode-field write to B leaves B permanently
  `RESERVED_INERT`, for the entire run, confirmed by direct inspection:
  B's only path to becoming WRITE-active is A's tick-1 write to B's
  opcode field).

These two verdicts are **different**, satisfying the operator's
pre-registered pass condition (identical verdicts would have forced
`INFERENCE_CONTRACT_UNRESOLVED`). **K3 verdict: PASS.** The repaired
4-tier ladder (`HEREDITY_REQUIREMENTS.md`) is usable: it discriminates
the exact case (S04) that broke the reviewed draft. No blocking issue;
proceed.

## K6 -- provenance composition round-trip

Applying `EXPERIMENTS.md`'s repaired composition rule (S06) to four
hand-picked overlay combinations:

| Base | Overlay | `instrument_class` | Reasoning |
|---|---|---|---|
| Regime 3 (seeded copier) | Regime 5 (resource-rich) | `SEEDED_CONTROL` | A hand-authored functional pattern is present in the initial lattice; overlay only changes initial energy, never the origin label |
| Regime 1 (random soup) | Regime 5 (resource-rich) | `SPONTANEOUS` | Entire initial content is unstructured generation; high initial energy does not introduce hand-authored bytes |
| Regime 4 (adversarial inert control, seeded) | Regime 7 (heterogeneous init) | `SEEDED_CONTROL` | Hand-authored bytes present, even though causally inert; zone-varying initial content is still an overlay, not a base-origin change |
| Regime 2 (sparse soup) | Regime 6 (resource-poor) | `SPONTANEOUS` | Unstructured generation base; low energy is an overlay only |

**Round-trip check:** in every one of the 4 cases, `instrument_class` is
recoverable ONLY from the logged initialization recipe (EXPERIMENTS.md
item 5), never from inspecting final lattice bytes alone -- e.g. case 1
and case 2 can converge to visually similar final byte patterns under
enough ticks, yet the recipe log unambiguously distinguishes them. No
combination of base x overlay produced an ambiguous or dual label; the
fingerprint check (item 4) remains a secondary investigation trigger in
all 4 cases, never overriding the recipe log. **K6 verdict: PASS.** No
blocking issue; proceed.

## Overall disposition

K1, K2, K3, K6 all PASS with no discrepancy, no contradiction, and no
`INFERENCE_CONTRACT_UNRESOLVED` outcome. Per the operator's "STOP if
unresolved" instruction: **nothing here is unresolved.** The repair
cycle may proceed to write the repaired freeze candidate contract.

## Deferred gates (explicitly NOT run this cycle)

- **K4** (economic gates: isolated pulse-budget cell, equal-mean rain
  pair, reserve pooling, zero-amount-vs-large-amount contest) --
  requires a running simulator (CPU oracle) to observe emergent
  strategy distributions; cannot be hand-derived from the transition
  law alone. Referenced as a still-open falsifier by three DECISIONS.md
  entries (D-AETH01-01, -03, -05); remains open until the oracle exists.
- **K5** (continued-horizon reactivation audit for DEAD/FROZEN stops) --
  requires actually running a sweep to a fixed horizon; no sweep exists
  yet.
- **K7** (oracle/trace agreement + scout selection audit, including
  suppressed events) -- requires both an oracle AND a production trace
  implementation to compare against each other; this is exactly the
  independent event-ledger cross-check required by REQUIREMENTS.md's
  M09 repair, and must be run once the CPU oracle and production code
  for the repaired law exist, before any trace is used as evidence.
- **K8** (bounded path/assembly witness with transplants) -- requires a
  running simulator to search a bounded reconfiguration path; cannot be
  hand-derived.

K4/K5/K7/K8 are preconditions for using AETH-01 as scientific evidence,
not preconditions for this repair cycle's remaining deliverables (the
repaired freeze candidate, CPU oracle, and RunPod canary). They are
carried forward explicitly, not silently dropped.
