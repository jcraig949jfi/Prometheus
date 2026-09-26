# AETH-03 PHYSICS DESIGN 01 — the smallest changes that might let history matter

Date: 2026-09-26. Seat: Aether. Directive:
`roles/Aether/prompts/2026-09-26_resume_science/DIRECTIVE.md` (verbatim,
manifest-verified).

Status of this document: **PREREGISTRATION FIRST.** The sections WHAT V1
TAUGHT US, DESIGN PRINCIPLES, CANDIDATE PHYSICS, CHEAP FALSIFIERS and
REJECTED PHYSICS were written and committed BEFORE any scout of any
variant was run at scale. H2/H3 CLOSURE, RESULTS OF SCOUTS and
CANDIDATES FOR SCALE-UP are filled in afterwards and say so. The commit
that first carries this file is the preregistration timestamp.

`aeth01.v1` is not modified and is not replaced. It is the immutable
baseline every candidate is read against. Every candidate below carries
its own semantics id (`aeth03.<name>.scout0`); `scout0` means a
counterfactual scout kernel, not a frozen law.

Cost of everything in this document: **$0.00**, CPU on BUCKKEEP.

---

## 1. WHAT V1 TAUGHT US

From FIRST_LIGHT_01, NATIVE_CIRCUITRY_01 (as amended) and the AETH-02
closing report, all for B-balanced `aeth01.v1`:

1. **The bulk goes stationary fast** (by ~tick 2,500) and **92% of sites
   make no net template change over 64 ticks** (H1b).
2. **Continuing template change is mostly injected.** Removing
   perturbation removes ~42% of it immediately and ~95% within 500 ticks
   (H4). The substrate's own copy dynamics are very nearly static.
3. **~88% of template proposals are redundant** — they rewrite the value
   already there. A write REPLACES the target byte with the source's
   payload; the new value is never a function of the target's prior
   state. Nothing in the law combines two values.
4. **Persistent edges are uncontested residue in frozen neighbourhoods;**
   remove one and nothing repairs or replaces it (H1: zero recurrence,
   zero occupancy over 500 ticks).
5. **Contested slots are re-decided by a fresh hash every tick.** The
   arbitration priority includes the tick number, so a contest carries no
   memory of who won last time.
6. **The instantaneous edge structure is plain independence** (H2: edge
   fraction predicted to 0.2%).
7. **Cycles in the realized graph are rarer than in a rewired graph**
   (H3; closure below).
8. **Resource routing does not persist.** An emitter pays WRITE_COST +
   maintenance every tick against an expected replenishment of 1, whether
   or not its write changes anything.

The pattern: **v1 moves bytes but never combines them; it charges for
motion regardless of consequence; and its only history is "which bytes
happen not to have been overwritten yet."** A site's future behaviour
depends on its past only through the bytes it still holds, and those
bytes are either frozen residue or were just copied from a neighbour.

## 2. H2/H3 CLOSURE

*Filled in after the runs; see the section at the end of this file.*

## 3. DESIGN PRINCIPLES

1. **One assumption per arm.** Every candidate changes exactly one phase
   of the v1 tick. Combinations are not tested until each component has
   its own scout result.
2. **No added state in the first ladder.** Every candidate uses the five
   v1 bytes. If history needs new storage, that should be forced by
   evidence (every zero-state candidate killed), not assumed.
3. **No architecture supplied.** No registers, message types, agents,
   pathways or objective function (directive's ANTI-GRAVITY RULE). A
   candidate may make a primitive *possible*; it may not build one.
4. **Same baseline, same battery.** Every candidate runs the identical
   scout battery at the identical size, seeds, parameters (B-balanced)
   and tick counts as v1, in the same process code path.
5. **The shared code path is proven to be v1 before anything is layered
   on it** (`test_aeth03_variants.py::test_shared_path_is_v1_bit_for_bit`).
6. **A trivial mechanism is not a finding.** Where a candidate's effect
   is guaranteed by its rule (e.g. hysteretic arbitration raising
   winner persistence), that measurement is reported as a mechanism
   check, never as evidence of anything.

## 4. CANDIDATE PHYSICS

Kernels: `Aether/observatory/aeth03_variants.py`. Tests:
`Aether/test/test_aeth03_variants.py` (shared path bit-identical to v1;
one hand-worked fixture per variant; every variant differs from v1 on a
live soup).

### C1 `add` — combining commit
1. **Change (phase 4):** a winning write into fields 0–3 stores
   `(old + payload) mod 256` instead of `payload`. Perturbation then
   applies to the committed value exactly as in v1.
2. **v1 failure targeted:** writes never combine two values (§1.3); the
   88% redundant proposals; history erased by overwrite.
3. **New failure mode risked:** every repeated write now changes state,
   so the lattice may become a pure churn machine — high change, no
   persisting structure (trivial chaos). Opcode-field writes will switch
   emitters on and off almost every time they land.
4. **Cheapest falsifying scout:** the battery (§5) at 128², 2 seeds.
5. **Justifies further work if:** the generic JUSTIFY criteria (§5) hold.
6. **Killed if:** generic KILL (§5), in particular K-c (saturating
   divergence with no persisting edge structure).

### C2 `hys` — hysteretic arbitration (arbitration memory without new state)
1. **Change (phase 3), fields 0–3 only:** a contender whose value equals
   the target's current value outranks every contender whose value
   differs; within each group the unmodified v1 hash decides.
2. **v1 failure targeted:** contests re-decided from scratch each tick
   (§1.5). The field's current value is itself a record of the last
   winner, so no state is added.
3. **New failure mode risked:** more freezing. Incumbents become sticky,
   and v1's failure is already too little change.
4. **Scout:** battery. S4 (winner persistence) rises by construction and
   is a mechanism check only.
5. **Justifies further work if:** generic JUSTIFY holds. Stickiness alone
   does not count.
6. **Killed if:** generic KILL, especially K-b (more frozen than v1 with
   no gain in consequential history).

### C3 `chg` — change-priced writes (resource tracks transformation)
1. **Change (phase 5a):** an emitter is debited WRITE_COST only if its
   proposal would change the target (payload differs from the target's
   current value in the selected field 0–3). Energy proposals always pay.
   Decode is unchanged.
2. **v1 failure targeted:** resource cost is uncoupled from consequence
   (§1.8); emitters drain whether or not they transform anything, which
   (if H2 closes as expected) is what ends most edges.
3. **New failure mode risked:** redundant structures become free, so the
   lattice may crystallise into free fixed points — maximal freezing.
4. **Scout:** battery.
5. **Justifies further work if:** generic JUSTIFY holds.
6. **Killed if:** generic KILL.

### C4 `cnd` — a conditional emitter (the missing branch primitive, R14)
1. **Change (phases 1–2):** opcode `0x02` is a second active opcode that
   emits like WRITE, but its proposal is valid only where the target
   field's low two bits equal bits 2–3 of the emitter's arg0 (bits the
   v1 direction selector ignores). It pays WRITE_COST either way.
2. **v1 failure targeted:** no compare/branch primitive exists
   (freeze-candidate §11, R14); whether a write happens never depends on
   what it would land on.
3. **New failure mode risked:** `0x02` simply dies out (payload copies
   rarely produce it), or acts as a weaker WRITE with no conditional
   consequence.
4. **Scout:** battery. **Initial-state difference, stated:** half of the
   initial WRITE sites are set to `0x02`, since otherwise the opcode
   appears only via 1-in-256 payload copies. The end-of-warmup share of
   `0x02` among emitters is reported.
5. **Justifies further work if:** generic JUSTIFY holds AND `0x02`
   persists at > 1% of emitters.
6. **Killed if:** generic KILL, or `0x02` falls below 1% of emitters.

### C5 `str` — resource-steered direction (endogenous topology)
1. **Change (phase 2):** `direction = (arg0 + (energy >> 6)) mod 4`.
2. **v1 failure targeted:** interaction choice is fixed argument bytes
   plus perturbation; topology never depends on what a site has
   experienced. Energy is the one byte that integrates a site's resource
   history.
3. **New failure mode risked:** as emitters drain, direction sweeps
   deterministically through quartile boundaries — topology churn that
   is history-dependent but mechanically trivial.
4. **Scout:** battery. S3 (edge overlap) is expected to fall; that alone
   is not a finding.
5. **Justifies further work if:** generic JUSTIFY holds.
6. **Killed if:** generic KILL.

## 5. CHEAP FALSIFIERS (preregistered)

Battery: `Aether/observatory/aeth03_scouts.py`, identical for v1 and all
candidates. 128², 2 seeds, B-balanced, 1,500 warmup ticks with
perturbation on, 500-tick follow. Measures S0 viability/frozen fraction,
S1 template change retained with perturbation OFF, S2 twin divergence
(16 single-bit flips at spaced active emitters, perturbation off and on),
S3 realized-edge overlap at lags 1/10/100, S4 contested-winner
persistence. Definitions are in the module docstring.

All thresholds are **relative to v1 measured in the same battery run**
(written v1[...] below), averaged over the 2 seeds.

**Generic KILL — any one kills the candidate at scout0:**
- **K-a collapse:** activity density at end of warmup < 0.02.
- **K-b no endogenous gain:** S1 retained(+500) ≤ 2 × v1[S1 retained(+500)]
  AND S2-off footprint per origin at +500 ≤ v1's.
- **K-c trivial chaos:** S2-off differing sites cover ≥ 50% of the
  lattice at +500 AND S3 overlap at lag 10 < 0.05.

**Generic JUSTIFY FURTHER INVESTIGATION — all required:**
- **J-1 endogenous change:** S1 retained(+500) ≥ 5 × v1's.
- **J-2 consequential, bounded history:** S2-off footprint per origin at
  +500 ≥ 3 × v1's, with reach ≥ 2 (the difference crossed at least two
  interactions) AND reach < 16 (half the origin spacing: not saturating).
- **J-3 changing yet structured:** S3 overlap at lag 100 ≥ 0.10.

A candidate meeting neither set is **UNRESOLVED at scout0** and is stated
as such.

What passing J means, at its correct width: *this change is worth a
controlled follow-up* — an intervention scout that switches the law back
to v1 mid-run and asks whether the effect vanishes, plus a matched null
for the footprint. It is not evidence of computation, and none of the
directive's six "progress" criteria is claimed from scout0 alone.

## 6. RESULTS OF SCOUTS

*Filled in after the runs.*

## 7. REJECTED PHYSICS (not built, with reasons)

- **Quenched arbitration** (drop `tick` from the arbitration hash so each
  contest always resolves the same way). Zero added state, and it would
  make contests persistent — but the persistence comes from a fixed hash
  landscape, not from history. It supplies structure instead of letting
  it arise. Kept as a possible negative control for `hys`.
- **Pull semantics** (a site copies from a neighbour instead of writing
  to one). Changes who controls a site's state, which is a new ontology,
  not one assumption; deferred until the one-change ladder is read.
- **An added memory byte / refractory counter.** Violates principle 2
  until the zero-state candidates are exhausted.
- **XOR-commit** as a separate arm. Same assumption as `add` (combine
  instead of replace) with no carries; tested only if `add` passes and
  the question becomes which combination law matters.
- **Energy-gradient steering** (aim at the richest/poorest neighbour).
  Supplies a sensing-and-response behaviour directly; `str` is the
  primitive version that uses only the site's own byte.
- **Evaluation-score resource rewards** (credit energy for "successful"
  writes). Hard-codes an objective; `chg` is the objective-free version
  (it prices change, it does not reward any outcome).
- **Anything named in the directive's anti-gravity list** (networks,
  state machines, registers, buses, loops, agents, conventional memory storage).

## 8. CANDIDATES FOR SCALE-UP

*Filled in after the scouts.* No GPU campaign is proposed from scout0
alone; the path is scout0 → intervention scout → representative GPU
scout → measured cost model → campaign, per the directive.
