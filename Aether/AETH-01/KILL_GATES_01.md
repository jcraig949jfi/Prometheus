# AETH-01 -- KILL_GATES_01: adjudicated outcomes for K1, K2, K3, K6 (+ K4/K5 deterministic halves)

Status: original hand-worked adjudication (K1, K2, K3, K6) from the
repair cycle, PLUS -- once the CPU oracle existed -- executable
confirmation of those same four gates and deterministic (non-
statistical) existence-proof fixtures for K4 and K5, added in the
closure-patch cycle (below). K4/K5's statistical/audit halves, K7, and
K8 remain explicitly DEFERRED (see bottom) -- each still requires
either a completed sweep or a production trace implementation that do
not exist yet.

The K1/K2/K3/K6 sections immediately below retain their original
hand-derivation text unchanged (now additionally confirmed executable
by `test_aeth01_kill_gates.py`); the K4/K5 sections further down are
new this closure-patch cycle.

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

**[NEW, closure-patch addendum]** Two further fixtures, executable
(`test_aeth01_kill_gates.py`, `test_aeth01_gpu_differential.py`, 28
new cases total, all passing on both CPU oracle and GPU-shaped
NumPy implementation), strengthen K3 beyond the original relay-vs-
capacity pair:

- **Construction fixture (fixture 3).** Discriminates
  `ACTIVATION_OF_PRECONFIGURED_MACHINERY` from `CONSTRUCTION` (the
  taxonomy split added to `HEREDITY_REQUIREMENTS.md`'s tier 3) via
  THREE independent ablations on one fixture, not one on/off toggle:
  (a) opcode-only ablation -- target never activates at all, same
  signature as the original capacity fixture; (b) routing-only
  ablation -- target DOES activate (its capacity-to-act was still
  constructed) but its `arg0` routing byte is never touched, so it
  writes to the wrong (inert-default) neighbor instead of the intended
  one -- proving activation and behavioral construction are separable
  claims, not one bundled fact; (c) matched control -- an unrelated
  cell's bytes are confirmed untouched in every combination. All three
  ablations produced exactly the predicted, distinct byte-level
  outcomes; no ambiguity.
- **Recursive construction fixture (fixture 4).** A single upstream
  ablation (removing the one constructor, A) is confirmed to propagate
  through BOTH construction steps of an A-constructs-B,
  B-constructs-C chain simultaneously: without A, neither B's nor C's
  capacity ever changes, at any tick, for the whole run. This is the
  positive existence proof that `RECURSIVE_CONSTRUCTION` (tier 4) is
  actually reachable by a concrete fixture under the repaired ladder,
  not just definable on paper.

**K3 verdict (updated): PASS**, unchanged from the original two-fixture
adjudication, now with a wider discriminating battery and a taxonomy
(`PAYLOAD_RELAY` / `ACTIVATION_OF_PRECONFIGURED_MACHINERY` /
`CONSTRUCTION` / `RECURSIVE_CONSTRUCTION`) that a future detector's
report must cite by name, never a bare tier number.

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

## K4 -- cheap deterministic fixtures now run; full statistical characterization still deferred

**[NEW, closure-patch addendum]** The CPU oracle now exists
(`test/reference/oracle_aeth01.py`), so the four K4 fixtures named in
the original deferral are now run as DETERMINISTIC, seed-fixed
existence proofs (`test_aeth01_kill_gates.py`, 4 new tests, all
passing) -- NOT the statistical characterization of emergent strategy
DISTRIBUTIONS across many seeds/parameter points that K4 ultimately
requires (that part remains genuinely deferred, below):

1. **Isolated pulse-budget cell.** A single WRITE cell with no
   replenishment exhausts in exactly `floor(energy0 / (write_cost +
   maintenance_cost))` emitting ticks, then STAYS starved forever
   (confirmed for 5 further ticks). Closed-form budget confirmed exact,
   not approximate.
2. **Equal-mean bursty pair.** Two replenishment configurations with
   the identical theoretical mean rate (5/tick: `prob=1.0,amount=5` vs
   `prob=0.5,amount=10`) produce PROVABLY DIFFERENT realized
   trajectories at a fixed seed (`[5,10,15,20,25,30]` vs
   `[0,0,10,10,10,20]` over 6 ticks) -- burstiness is a real, observable
   degree of freedom that a mean-rate-only report would hide.
3. **Reserve pooling.** Two distinct, non-contending sources (acting on
   different ticks, never in the same arbitration contest) both
   contribute to the same target's energy reserve, and their
   contributions ADD (`100 + 80 = 180`), confirming the mechanism
   supports genuine pooling from more than one source, not just a
   single-source drip.
4. **Zero-amount vs. large-amount contest.** A bounded seed search
   (0..199, deterministic, no sampling) finds concrete seeds where a
   zero-amount proposal beats a 200-amount proposal AND seeds where the
   large amount wins -- confirming arbitration priority is a pure hash
   of (seed, tick, coords), never a function of the proposed value, in
   either direction.

**K4 verdict (partial): the mechanism-level existence claims above are
CONFIRMED, deterministically, with zero tolerance.** Still deferred:
the actual DISTRIBUTION of emergent economic strategies across a real
parameter sweep (referenced as a still-open falsifier by
DECISIONS.md's D-AETH01-01/-03/-05) -- that requires a running sweep,
which does not exist yet, and is not something 4 hand-picked fixtures
can substitute for.

## K5 -- cheap deterministic fixtures now run; full reactivation audit still deferred

**[NEW, closure-patch addendum]** Three K5 existence proofs now run
against the CPU oracle (`test_aeth01_kill_gates.py`, 3 new tests, all
passing), each confirming one of GPU_RUNPOD.md's S05-repair claims is
actually reachable, not just theoretically possible:

1. **Delayed reactivation.** A starved writer (energy below
   `write_cost`) stays dormant (emits nothing, "looks dead") for at
   least one full tick, then -- once replenishment crosses the
   threshold -- resumes emitting, confirmed at a fixed seed/config.
2. **Same-value-then-mutation.** A fixed donor overwrites the same
   target with byte value `0` for several consecutive ticks (a naive
   detector would call this "FROZEN"), then a single-bit Mu mutation
   fires at a later tick -- confirmed: at least one idle tick preceded
   the change, and the change itself is a single-bit flip (consistent
   with K2).
3. **Later-tick priority flip.** Two proposals with the SAME fixed
   source/target coordinates, competing every tick, produce BOTH
   possible winners across a 30-tick scan at a fixed seed -- confirming
   a currently-losing writer is not permanently excluded, since
   arbitration priority is tick-dependent, not a static ranking.

**K5 verdict (partial): all three CONFIRMED reachable, deterministically,
at a fixed seed.** Still deferred: the actual continued-horizon
reactivation AUDIT over a real sweep's `DEAD_CENSORED`/
`FROZEN_CENSORED` population (a preregistered random resumed subset,
GPU_RUNPOD.md) -- that requires an actual sweep to exist first.

## Deferred gates (still NOT run this cycle)

- **K4 / K5 statistical tails** (see above): the DISTRIBUTIONAL /
  AUDIT halves of K4 and K5 remain deferred; only the deterministic
  existence-proof halves were run this cycle.
- **K7** (oracle/trace agreement + scout selection audit, including
  suppressed events) -- requires both an oracle AND a production trace
  implementation to compare against each other; this is exactly the
  independent event-ledger cross-check required by REQUIREMENTS.md's
  M09 repair, and must be run once the CPU oracle and production code
  for the repaired law exist, before any trace is used as evidence.
- **K8** (bounded path/assembly witness with transplants) -- requires a
  running simulator to search a bounded reconfiguration path; cannot be
  hand-derived.

K4/K5's remaining statistical halves, K7, and K8 are preconditions for
using AETH-01 as scientific evidence, not preconditions for this
repair/closure cycle's remaining deliverables (the repaired freeze
candidate, CPU oracle, and RunPod canary). They are carried forward
explicitly, not silently dropped.
