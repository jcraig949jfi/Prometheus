# Proteus — open work

Standing list. Linked from `RESPONSIBILITIES.md`. Nothing here is in progress; each item states
its owner, why it is open, and what closing it would cost. Items are **not** ordered by priority
within a section — the section is the priority.

Last updated 2026-09-04, after the player/primitive closure pass (`6be6103f1`, `6ca171129`).
Evidence for every claim below lives in `PROTEUS_CLOSURE_PACKET_2026-09-04.txt` and
`proteus/v0_7/RESULT_*.json`.

---

## A. Blocks the first A/B/A+B experiment

**T1 — The measurement surface is degenerate.** OWNER: Harmonia decides, Proteus already supplies.
The probe transcript resolves 3 distinct classes over 56 segment players with 87.5% in one class,
and 52/56 players emit nothing at all. That is why A+B differed from both parents in 0/200 pairs.
The meter vector on the same population resolves 37 classes at 10.7%. It needs the experiment to
declare the meter, not the transcript, as its primary observable.
*Do not close by widening the transcript before checking whether the meter suffices.*

> **AMENDED 2026-09-05 by T2 — the "no new Proteus code" line above was wrong and is struck.**
> `Meter.as_dict()` used raw includes `wall_s` and `cpu_s`, which are timings. Measured: the full
> meter reproduced on **0 of 40** identical re-runs — every player differs from *itself*, so a
> composition result read off the raw meter would be noise. The observable is
> `Meter.as_dict()` **minus `wall_s`, `cpu_s`** (and `gpu`, a constant), which reproduces 40/40.
> Gated by `proteus/tests/test_meter_observable.py`. Harmonia must declare the *projection*, not
> the meter.

**T2 — Chance floor for the meter observable. CLOSED 2026-09-05.**
Evidence: `proteus/v0_7/RESULT_METER_FLOOR.json`, `proteus/compose/run_meter_floor.py`.
Verdict `METER_DISCRIMINATES_BEYOND_SIZE`.

*The 37 is exactly chance, and that is fine.* Random populations of 56 same-shape segment players
give **median 36 `ops_by_category` classes (range 27–43)**; the observed 37 sits on the null. So
"37 classes at 10.7%" is **not** evidence about the population and must never be cited as such —
it is the baseline richness of arbitrary 2-instruction programs under this observable. The
transcript's 3 classes sit *below* its own null median of 4, which is what degeneracy looks like.

*What makes the meter usable is Part 2, not Part 1.* Discrimination rates over 200 matched pairs:

    identity          0.0000   a player vs itself (sanity)
    size floor        0.0000   A vs A + inert NOP padding
    treatment         0.7750   A vs A+B
    size-matched      0.7750   A + padding vs A+B
    order             0.4900   A+B vs B+A
    partner identity  0.7550   A+B vs A+B'
    independent       0.9900   A vs an unrelated player (ceiling)

**The size confound the directive names is measured and absent**: inert padding moves the meter
in 0/200 pairs, so the 0.775 treatment rate is attributable to B's content and not its length.
The meter also resolves **order** (0.49) and **partner identity** (0.755), which are the
prerequisites for the A→B and conditional-composition questions.

Caveat preserved: NOP padding is inert as instructions but is also data, so the size floor is a
lower bound. All three NOP aliases were run; **0/200 disagreements**.

---

## B. Proteus-owned, not blocking

**T3 — Retention V0 is specified but not implemented.** OWNER: Proteus.
`proteus/contracts/RETENTION_AND_MEASUREMENT_V0.md` defines the reservoir, the `EvaluationRecord`
shape, the archive, the three guards and the deterministic eviction order. **None of it is code.**
There is no reservoir, no record store and no eviction path. The contract is honest about being a
contract; nothing should cite it as a running mechanism.

**T4 — Proteus is still not registered in the fleet roster.** OWNER: Proteus.
`RESPONSIBILITIES.md` §8 committed to registering in `scripts/portfolio_monitor.py`
`EXPECTED_AGENTS` "when the first `proteus/` code lands". Code landed 2026-09-02; verified absent
from `EXPECTED_AGENTS` on 2026-09-04. Overdue by the seat's own rule.

**T5 — The PEW export contract has been specified but never exercised.** OWNER: Proteus.
Deliverable 10 (`proteus/contracts/PEW_EXPORT.md`) was written against a documented API while
`evidence_wiki/ew/client.py` was on an unmerged branch. PEW is now on `main` and serving. The
contract should be run against the live service rather than continuing to be a specification.
Depends on nothing; blocked on nobody.

**T6 — The alias differential is a lower bound, and its width is unmeasured.** OWNER: Proteus.
`ablation_report`'s EXACT verdict is ensemble-relative: it detects a data-channel dependence only
if that dependence reaches the transcript on the probes actually run. 1/343 class knockouts came
back CONFOUNDED. Either widen the ensemble and re-measure the rate, or state explicitly that the
bound is accepted at its current width. Today it is neither.

**T7 — The A6 neutrality hard gate is still not passed.** OWNER: Proteus. Standing since
2026-09-02, after three preregistered runs. Unchanged by this pass and not re-attempted here.

**T8 — `random` in `proteus/v0_6/equilibrium.py`.** OWNER: Proteus, deliberately deferred.
Policy is that `random` is used nowhere; `SplitMix64` exists so bit-exact replay never depends on
its float and choice paths. Blast radius is measured and pinned by gate G1: it reaches only
`stationary_empirical()`, whose two call sites were both reported non-adjudicated. Fixing it moves
two published numbers, so it waits for a version permitted to do that.

---

## C. Requires a runtime transition — bundle, do not do casually

Both items change `runtime_hash`, which changes the **interpretation identity of every frozen
specimen** and would invalidate Harmonia's existing fossils. They should land together, in a
version that expects to re-stamp, never as a convenience fix.

**T9 — The affordance table's prose contradicts the runtime.** `affordances.py`'s module docstring
says `c` is the immediate for `LDC`. `vm.py` `op == 3` executes `regs[a] = bw & MASK32` — the
immediate is read from slot **b**. The TABLE row (`"a,imm"`) is correct; the sentence above it is
not. This cost one wrong test during the closure pass before it was traced. Not fixable in place:
`runtime_hash` is a sha256 over the whole LF-normalised file, docstring included. Anyone
hand-writing a genome must encode from `vm.py` until this lands.

**T10 — Per-instruction and ordered activation tracing.** `activation_evidence()` gives a binary
did-it-execute by differencing `ops_by_category`, which was chosen precisely to avoid instrumenting
the frozen runtime. It cannot give per-instruction counts, cannot localise execution to a component
when two components share a class, and cannot report composition activation ORDER. Real
instrumentation needs a runtime transition.

---

## D. Other seats — tracked because the readiness matrix depends on them

**T11 — SFE does not verify specimen content identity.** OWNER: Daedalus / the shared arena
primitive. Harmonia's `I-CLIENT-GATE-UNENFORCED`: the engine is content-addressed but accepts
corrupt bytes carrying a plausible client-asserted `blob_hash`. Proteus's side is closed —
`proteus/integration/specimen_gate.py` refuses that exact probe — but the gate must be placed in
**one** shared primitive and never re-typed per caller.

**T12 — The PEW fossil has no typed identity fields.** OWNER: Mnemosyne. No
`registry_identity`, `entry_id`, segment ids, composition topology or ablation relation, so a
fossil proves which organism ran where but not what it was made of. The full block Proteus can emit
is section 12 of the closure packet. Storing it as one typed opaque record is an honest interim;
queryability is the upgrade.

---

## E. Deferred by directive — do not start without one

**T13 — Any glue beyond `concat.v0`.** `A->B` as control flow, conditional activation and
world-conditioned activation each need a new declared glue. The directive is explicit: do not build
a universal graph language until A+B proves it necessary. A+B has not.

**T14 — Retention parameter tuning.** `R_MAX 4096`, `K_MIN 3`, control quota `256` are round
numbers chosen to be sufficient for a first experiment, not optimised. Tuning them is out of scope
until there is something to tune against.

---

## F. Blocked, and not a TODO

Campaign 1 and USE B remain blocked by the standing V0.6 limitations —
`NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`, `FULL_SPACE_CURRENT_SOURCE_UNRESOLVED`,
`OPERATIONAL_SIGNIFICANCE_NOT_YET_ADJUDICATED`. USE A is permitted. Nothing in the closure pass
adjudicated any of them, and this seat does not adjudicate them.

---

## What is NOT on this list, on purpose

No item here selects, scores, ranks or interprets a specimen; none tunes a primitive for
performance; none proposes a fitness scalar. If a future entry does, it is the prior seat's
enthusiasm leaking (`RESPONSIBILITIES.md` §5, §9) and should be named as such rather than worked.
