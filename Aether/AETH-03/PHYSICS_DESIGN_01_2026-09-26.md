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

**Result, in one paragraph (added after the runs).** H2 is closed: the
3.1× lifetime gap was a null-model defect (source starvation, absent
from the old null, is 89% of edge terminations), and the residual — long
edges outlasting an independent-energy null — is energy supply from
neighbouring emitters, confirmed by a sustained inflow cut (persistence
at +128 falls to 0.39× sham). H3 is closed as a question: the cycle
deficit is real at 512² (0.37× both nulls, 37,042 cycle nodes), carried
almost entirely by opcode (0.003×) and arg1 (0.002×) cycle edges, with
energy cycles enriched 1.58×; the opcode mechanism is deterministic
deactivation, the arg1 mechanism is perturbation acting through the K2
mod-5 property (tested). Of five one-change physics candidates, four are
killed at scout0 and `add` is unresolved with most of its gain trivial
(83% counting). The cross-cutting finding: in v1 and every variant, a
single-bit difference stays within about one site for 500 ticks —
**the substrate lacks propagation.** No scale-up is proposed.

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

*Written after the runs.* Instrument: `Aether/observatory/aeth02_closure.py`
(predictions H2-P1/P2, H3-P1..P4 in its docstring, committed in
`8e5bd7af9` before any 512² result existed). Evidence:
`Aether/AETH-01/evidence/2026-09-26_aeth02_closure/`. Tables regenerate
with `python Aether/observatory/aeth02_closure_reduce.py <dir> --n <n>`.

Runs: 512² × 2 seeds (2,500 warmup, 600 follow); 256² seed 0 (2,500
warmup, 1,500 follow); 256² seed 0 with **10,000** warmup (stationarity
control). A third 512² seed was stopped at tick ~500 to relieve CPU
contention on BUCKKEEP and is not reported. B-balanced `aeth01.v1`
throughout; the law is unmodified.

**Stationarity control passes.** Every H2 and H3 quantity at 10,000
warmup reproduces the 2,500-warmup value: ≥64 opcode cohort 0.0713 vs
0.0705, edge hazard 0.1264 vs 0.1262, cycle deficit 0.360 vs 0.368, the
same per-field pattern. Nothing below is a relic of the initial state.

### H2 — CLOSED. The gap was a null-model defect; the residual is energy supply.

| 512², opcode field | seed 0 | seed 1 |
|:--|--:|--:|
| edges at risk | 7.37 M | 7.38 M |
| observed P(run ≥ 64) | 0.0695 | 0.0726 |
| old null (all-site change rates, no energy) | 0.226 (3.25×) | 0.229 (3.15×) |
| measured per-tick edge hazard | 0.128 | 0.127 |
| of which source starvation | 0.113 (89%) | 0.113 (89%) |
| conditioned null, i.i.d. energy walk | 0.0103 (0.15×) | 0.0118 (0.16×) |
| life-table self-check (instrument) | 0.088 | 0.092 |

The other template fields match; energy-field edges have hazard ~0.80
(their sources hand over their energy and starve).

1. **H2-P1 confirmed.** The old null put the per-tick edge hazard at
   ~0.024; it is 0.127, and **source starvation is 89% of it**, in every
   template field, at both sizes and both seeds. The old null had no
   energy term. The dominant mode is legible in the age profile: the
   starvation hazard spikes to **0.57 at exactly age 4** — a starved
   emitter receives one replenishment of 8, pays write + maintenance = 2
   per tick, and burns out in four ticks.
   **The 3.1× over-prediction is a null-model defect. Closed as such.**
2. **H2-P2 (conditioned null within 1.5×) FAILED — the other way.** Put
   energy in as an independent walk and the null *under*-predicts the
   long cohort 6–7×. Real long edges outlast independent energy.
   The instrument is not the reason: the life table built from measured
   age-specific hazards lands within 1.27× of observation.
3. **The residual has a law-level explanation, then a causal test.**
   An active emitter with no inflow drifts −1/tick and energy caps at 255,
   so an edge older than ~255 ticks is impossible without net inflow.
   At 256², **65% of the ≥64 cohort is older than 255 ticks** (654/1,000
   and 647/1,018 sampled), and those sources were fed by an energy-field
   edge in ~15% of recent ticks against 1.3% for all sites (~12×).
   - **H2-X, one-shot feeder cut** (post hoc, `aeth02_h2x_inflow.py`):
     **FALSIFIED at its own bar** — CUT within 0.05 of SHAM at +64 on both
     seeds (0.045, 0.030). A single cut touches only the ~15% of sources
     fed at that instant, and they carry reserves (~94).
   - **H2-X2, sustained removal** (post hoc, second test,
     `aeth02_h2x_sustained.py`; sham replays CUT's per-tick lesion count
     exactly — a first draft did not, caught on the smoke run):
     **NOT FALSIFIED.** Persistence of sampled ≥64-tick edges:

     | | +64 | +128 | +200 |
     |:--|--:|--:|--:|
     | NONE s0 / s1 | 0.810 / 0.808 | 0.708 / 0.715 | 0.623 / 0.643 |
     | SHAM_SUSTAINED s0 / s1 | 0.805 / 0.808 | 0.703 / 0.718 | 0.618 / 0.645 |
     | CUT_SUSTAINED s0 / s1 | 0.505 / 0.550 | **0.273 / 0.285** | 0.143 / 0.168 |

     CUT/SHAM at +128 = **0.39 / 0.40**, under the 0.5 bar; the sham is
     indistinguishable from no lesion (1,415 / 1,601 re-aims each arm).

**H2 closes with no unexplained residual.** Long edge persistence in
`aeth01.v1` is powered by energy delivered from neighbouring
energy-field emitters; take the supply away and it ends at roughly the
rate the accounting predicts. That is a resource-transfer mechanism, not
a structure-forming process, and nothing here is licensed to call it
functional. **One refinement to §1.8, stated rather than smoothed:**
individual energy-field edges are short-lived (hazard ~0.80), but the
*feeding relation onto a site* recurs — persistently fed sites exist and
carry most long-lived template edges. That is not "resource routing is
absent"; it is intermittent, site-level supply.

### H3 — the deficit is real, and two field mechanisms account for it.

| 512², 2 seeds, 48 samples | real | Null A (rewire) | Null B (arg0 shuffle, real kernel) | real / A | real / B |
|:--|--:|--:|--:|--:|--:|
| cycle nodes per sample, s0 | 768.6 | 2,062.1 | 2,061.5 | 0.373 | 0.373 |
| cycle nodes per sample, s1 | 774.8 | 2,025.2 | 2,029.8 | 0.383 | 0.382 |
| cycle edges: opcode | 57 | 18,803 | 18,938 | **0.003** | 0.003 |
| cycle edges: arg0 | 8,503 | 22,183 | 22,003 | 0.383 | 0.386 |
| cycle edges: arg1 | 36 | 22,578 | 22,703 | **0.002** | 0.002 |
| cycle edges: payload | 14,056 | 25,418 | 25,348 | 0.553 | 0.555 |
| cycle edges: energy | 14,390 | 9,114 | 9,200 | **1.579** | 1.564 |

Cycle lengths: 18,493 two-cycles, 14 four-cycles. 37,042 cycle nodes
pooled, against the 205 on-cycle edges that left H3 open.

1. **H3-P1 confirmed: not sampling noise.** 0.37–0.38× against both
   nulls at 512², 0.36–0.37× at 256² (both warmups). The two nulls agree
   to three decimals, so the deficit is not an artefact of how the null
   graph is built.
2. **H3-P2 PARTLY FALSIFIED.** Predicted: deficit concentrated in opcode
   and arg0, arg1/payload/energy near 1. Observed: opcode ✓ (0.003) and
   arg0 ✓ (0.38) — but **arg1 is the most suppressed field (0.002)**,
   payload is suppressed (0.55), and **energy is enriched (1.58)**. The
   candidate explanation was right about opcode and wrong as a whole.
3. **Mechanisms, read off the frozen text and tested.** A cycle member is
   written by its predecessor every tick.
   - *Opcode:* the write stores the predecessor's payload into the
     member's opcode, deactivating it unless payload = WRITE. The
     relaxation probe shows opcode cycle edges collapsing 390 → 15 within
     10 ticks of a shuffle; H3-X shows the collapse is the same with
     perturbation off (retention to +100: 0.008 off, 0.018 on), so it is
     deterministic.
   - *Arg1:* the write sets the member's own field selector. **Every
     single-bit perturbation of an arg1 value changes it mod 5**
     (freeze-candidate §9, falsification gate K2), so each perturbed arg1
     write re-picks which field the member writes next, until it lands on
     a destructive one. **H3-X (post hoc, `aeth02_h3x_arg1.py`) NOT
     FALSIFIED:** arg1 cycle edges retain 0.40 of their +1 count to +100
     with perturbation off against 0.095 with it on (4.2×); with it off
     they stop decaying after a one-off drop in the first 10 ticks.
   - *Energy:* energy-field 2-cycles are mutual supply — each member
     feeds the other — and they are enriched 1.58×. This is the same
     supply relation that powers H2's long edges.
   **Why realized cycles are rarer than the matched random graph:**
   because every cycle member is overwritten every tick by its
   predecessor, and in two of five fields that overwrite ends the cycle —
   deterministically for opcode, via the K2 property of perturbation for
   arg1 — while energy-field cycles are self-supplying and over-represented.
4. **H3-P3 FALSIFIED.** Predicted: one-tick out-edge persistence depends
   on the field a writer was written in and not on cycle membership. At
   fixed field, cycle members persist *less*: arg0 0.587 vs 0.755,
   opcode 0.34 vs 0.63, payload 0.726 vs 0.832, energy 0.919 vs 0.987
   (arg1 0.81 vs 0.81, n = 866 on-cycle). Cycle membership costs 0.07–0.29
   per tick beyond the field effect. Not explained here; a candidate
   (a 2-cycle member's out-edge needs its own writer to stay put) is
   untested and is not claimed.
5. **H3-P4 confirmed.** A direction-shuffled state starts at the null
   level (2,055 cycle nodes at +1) and relaxes to the realized level
   (751 at +60 against 793 realized), opcode and arg0 cycle edges going
   first.
6. **The original "state-changing enrichment on cycles" is mostly field
   composition.** Pooled: 0.539 on-cycle vs 0.252 overall (2.1×). But 38%
   of on-cycle edges are energy edges, which are 87% state-changing
   anyway; within a field the lift is modest (arg0 0.253 vs 0.205,
   payload 0.345 vs 0.209, energy 0.916 vs 0.867). The 2026-09-24
   report's 1.97× was mostly a Simpson's-paradox effect of the enriched
   energy field, which that report did not separate.

### H1 and H4 replicated (the directive's optional step)

Two further seeds at 256², the 2026-09-24 protocol unchanged
(`evidence/.../replicate_h1_h4.py`, `replicate_h1h4_s{1,2}.json`):

| | seed 0 (09-24) | seed 1 | seed 2 |
|:--|--:|--:|--:|
| H1 persistent-edge recurrence, +500 | 0.000 | 0.005 | 0.004 |
| H1 short-edge recurrence, +500 | 0.004 | 0.014 | 0.008 |
| H1 persistent-target occupancy, +500 | 0.000 | 0.005 | 0.012 |
| H1 sham recurrence, +500 | 0.924 | 0.972 | 0.940 |
| H4 immediate drop | 0.411 | 0.437 | 0.425 |
| H4 drop at +500 | 0.945 | 0.944 | 0.937 |
| H4 energy-change shift, tick 1 | 0.000000 | 0.0 | 0.0 |

Both stand on three seeds. H1's "exactly zero" becomes "≤ 0.5%": one
lesioned edge in ~220 recurred on each new seed.

### What closes, and what does not

- H2: **closed** — a null-model defect for the original gap, and a
  causally tested energy-supply mechanism for the residual.
- H3: **closed as a question** ("why are realized cycles rarer?"):
  per-field, powered, mechanisms named and one of them tested. One
  sub-prediction (P3) failed and its cause is not established.
- Neither result reveals an unexplained mechanism of the kind the
  directive would keep mining v1 for. **v1 mining stops here.**

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

*Written after the runs.* Evidence: `Aether/AETH-03/evidence/2026-09-26_scout0/`
(12 battery JSONs, logs). Verdicts are computed by
`Aether/observatory/aeth03_scouts_reduce.py`, which applies §5's
thresholds verbatim against v1 from the same battery:

    python Aether/observatory/aeth03_scouts_reduce.py \
        Aether/AETH-03/evidence/2026-09-26_scout0

128², 2 seeds each, means over seeds:

| | v1 | add | hys | chg | cnd | str |
|:--|--:|--:|--:|--:|--:|--:|
| activity density (S0) | 0.196 | 0.186 | 0.196 | 0.319 | 0.207 | 0.160 |
| frozen fraction, 64 ticks (S0) | 0.927 | **0.696** | 0.927 | 0.922 | 0.961 | 0.940 |
| template change, pert ON, +500 | 0.0093 | 0.0416 | 0.0090 | 0.0156 | 0.0050 | 0.0076 |
| retained with pert OFF, +500 (S1) | 0.064 | **0.998** | 0.026 | 0.062 | 0.048 | 0.056 |
| footprint / origin, pert OFF, +500 (S2) | 0.72 | 1.19 | 0.72 | 0.69 | 0.50 | 0.56 |
| reach, pert OFF, +500 (S2) | 1 | 2 | 1.5 | 2 | 1 | 1 |
| footprint / origin, pert ON, +500 | 0.59 | 1.50 | 0.63 | 0.81 | 0.50 | 0.69 |
| edge overlap lag 10 / 100 (S3) | 0.39 / 0.36 | 0.37 / 0.33 | 0.39 / 0.36 | **0.87 / 0.86** | 0.37 / 0.34 | 0.37 / 0.33 |
| same contested winner (S4) vs 1/k | 0.50 vs 0.50 | 0.50 vs 0.50 | **0.97** vs 0.50 | 0.51 vs 0.50 | 0.51 vs 0.50 | 0.50 vs 0.50 |
| **verdict** | baseline | **UNRESOLVED** | KILLED K-b | KILLED K-b | KILLED K-b | KILLED K-b |

`add`: J-1 yes (retained 0.998 = 15.6× v1), J-3 yes (0.33), **J-2 no**
(footprint 1.65× v1, not 3×; reach 2). Neither kill fires.

`cnd`: the `0x02` share among active emitters stayed at 0.508 / 0.501
(from 0.507 / 0.497 initially), so the opcode did not die out (measured
by deterministic replay of the same warmup, `cnd_opcode_share.py`,
because the battery omitted it — stated rather than hidden).

### What the scouts say, read at the width they support

1. **Four of five one-change candidates made v1 more static or no less
   static,** each by the failure mode §4 named in advance: `hys` became
   sticky (S4 0.97, a mechanism check by construction, not a finding) and
   lost endogenous change; `chg` crystallised the functional graph (edge
   overlap 0.86 at lag 100 against 0.36) exactly as "free fixed points"
   predicted; `cnd` and `str` froze further (0.961, 0.940).
2. **`add` is the only candidate with endogenous change, and most of it
   is the rule itself.** A post hoc check (`add_counting_check.py`, labelled
   so, both seeds) finds that **83% of `add`'s perturbation-free changes
   are constant-increment counting, and 86% come from the same source as
   the previous tick.** `add` converts v1's redundant rewrites into
   counters. Under design principle 6 that part of its J-1 pass is a
   mechanism check. It stays UNRESOLVED by the numbers; it is not a
   candidate for scale-up on this evidence.
3. **The cross-cutting result is the more important one: in all six
   laws, a single-bit difference stays within about one site of where it
   was made for 500 ticks, with or without perturbation** (footprint
   0.5–1.5 sites per origin, reach 1–2, no divergence ever above 0.22% of
   the lattice). v1's causal influence is one hop, and none of the five
   single changes made it longer. A write lands a value in a neighbour;
   that value changes what the neighbour *does* only if it lands in the
   neighbour's own arguments, and then only its next copy. Nothing
   re-emits what it received in combination with anything else.

That is a sharper statement of v1's limit than §1 had before the
scouts: **the substrate lacks propagation, not only memory.** History
cannot matter hundreds of ticks later if an intervention cannot matter
two sites away.

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

*Written after the scouts.*

**None.** No candidate met §5's JUSTIFY criteria. Four are killed at
scout0 by K-b; `add` is UNRESOLVED and most of what it passed on is its
own rule (83% counting). No GPU spend is proposed from this round, and
none was made. The path for anything that does pass stays: scout0 →
intervention scout (switch back to v1 mid-run) → representative GPU
scout → measured cost model → campaign.

### What the round changes about the next design question

The directive framed v1's failure as missing *history-dependent
persistence*. The evidence now narrows that:

1. **v1 already has one history-dependent persistence mechanism, and it
   is energy supply** (H2). Long template edges exist exactly where a
   neighbour keeps delivering energy; remove the supply and they end.
2. **The deficit in v1 is propagation.** In v1 and in all five one-change
   variants, a single-bit difference stays within about one site for 500
   ticks (§6). A received value changes what a site does only by landing
   in its own arguments, and nothing re-emits what it received combined
   with anything else.
3. **Overwrite is actively destructive to cyclic structure** in the
   opcode and arg1 fields (H3), and the arg1 half of that runs through
   the perturbation channel's K2 property — a property of `mod 5`, not
   of any deliberate design choice.

### Proposed second ladder (not built, not run; for the next round)

Same rules as §3: one change, no added state, v1 battery, preregistered
thresholds. Each targets propagation, since that is what every scout0
arm lacked.

- **`mov` — conservative template transfer.** A winning template write
  *moves* the source's payload: the source's payload is cleared when its
  proposal wins. Bytes then travel instead of duplicating, so a value can
  cross many sites (propagation) and redundant re-copying disappears
  without turning into counting (`add`'s failure). Risk: payloads decay
  to zero and the lattice goes inert. Kill if activity or payload
  entropy collapses; justify on S2 reach ≥ 4.
- **`rcv` — receipt enables emission for one tick.** A site that received
  a winning template write last tick emits this tick even if its opcode
  is not WRITE (paying WRITE_COST). Activity can then propagate through
  inert matter. Risk: trivial waves (K-c). Kill on K-c; justify on J-1..3
  plus reach growing sub-ballistically.
- **`m4` — perturbation-neutral field selector.** Replace `arg1 mod 5`
  with a selector some single-bit flips leave unchanged (e.g. `arg1 mod 8`
  folded onto five fields). This does not target propagation; it removes
  the K2 channel that H3 identified as destroying arg1-mediated cycles,
  and asks whether cyclic structure then persists. It is the cheapest arm
  and a direct test of an H3 finding.

`mov` and `rcv` are different ontological moves (conservation vs
excitation); neither supplies an architecture, and each can fail cleanly
in a named way.
