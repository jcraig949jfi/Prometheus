# Sequencing Decision + Harmonia C/D/E Handoff

**Author:** Harmonia_M2_B
**Date:** 2026-06-10
**Status:** DECISION OF RECORD (James review, 2026-06-09) + handoff plan
**Governs:** proposals A / B / D / E / F in this directory
**Naming caution:** *Proposals* are lettered A,B,D,E,F. *Harmonia instances* are
lettered B,C,D,E. They collide. Throughout, "Proposal X" = a document;
"Harmonia X" = an instance. Read carefully — e.g. **Harmonia D owns Proposal B.**

---

## 1. The ranking (James, 2026-06-09)

| Rank | Proposal | Verdict | Why |
|---:|---|---|---|
| 1 | **A — Baseline-Costume Detector** | **Build now** | Reusable falsification gate for every future "we found structure" claim. Directly attacks the recurrent Prometheus failure mode: apparent structure that is just a baseline wearing a hat. |
| 2 | **E — h2 Opaque-Kill Backfill** | **Build immediately after / partly alongside A** | Repairs the largest known information-loss hole: h2's flat kill pattern is ~44% of kill volume (~87K records). Asks whether the new structured patterns actually carry signal. |
| 3 | **B — a3 Lattice Void Mining** | **Run after A is available** | Most exciting discovery-facing experiment, and exactly the kind that needs A's gate before anyone trusts the voids. |
| 4 | **D — Cross-Agent Failure-Primitive Atlas** | **Start as markdown + tiny schema only** | Concept is right; risks taxonomy theater unless grounded by detectors that actually fire. Let A/E/B generate the first real entries. |
| 5 | **F — Reasoning-Ladder Confound Kills** | **Do later / separate track** | Scientifically clean and valuable, but burns model/API complexity and is less directly tied to the current mathematical failure-landscape substrate. |

**Doctrine line:** *A builds the immune system. E repairs the biggest known wound. B goes treasure hunting only after the immune system is active. D records the scars. F audits the ladder, but it is not the next substrate-critical move.*

---

## 2. The sequence

### Sprint 1 — A + minimal E hook (critical path)
Ship `harmonia/primitives/baseline_costume.py` with **only three baselines**:
`marginal_majority`, `volume_weighted`, `pair_aware`. Add `prime_atmosphere`,
degree-preserving graph nulls, and recency/frequency **only when a real claim
shape needs them**. Per A's own falsifier: if only one baseline ever fires, the
catalog collapses rather than becomes ornament. Refactor Erebos's
`real_residue_smoke.py` + `pair_aware_counter.py` to call the primitive and
reproduce their original verdicts byte-for-byte (the regression that proves the
generalization lost nothing).

### Sprint 2 — E, using A as the gate
Push `E_h2_opaque_kill_backfill`. Three hard questions, in order:
1. Does the **production daemon** actually emit the new structured kill patterns?
2. Can the historical **87K flat kills** be backfilled from retained payload fields?
3. Do the new subclasses **separate any downstream behavior**, or are they a prettier black hole? → this is where `baseline_costume.costume_check` (A) plugs in directly.
Best near-term ROI in the set: it either recovers a massive dead zone or proves the data was irreversibly lossy. Both are valuable.

### Sprint 3 — B, only after A/E guardrails exist
Run the exhaustive **20,736-cell** a3 sweep. Reconcile the **144-vs-324 lattice
discrepancy first** (operator set may have changed — invalidates cross-referencing
old kills). Every surviving void must clear:
- marginal-pairing null,
- operator-degeneracy null,
- relation-laxity null,
- sample-volume / object-domination checks,
- held-out catalog split.
B's win condition is properly Promethean: if every void is explained by trivial
marginal pairing, that is still a successful **kill** of the "voids are the math"
thesis for this generator.

---

## 3. What to do with D — thin registry only

Do **not** make D a full sprint. Seed it as a thin registry and let A/E/B populate
it with real detectors and evidence. The atlas is an **emitted artifact of
falsification work, not the work itself.** Initial seed:

```text
FP-001 baseline_costume
  detector: baseline_costume.costume_check
  anchors:  Erebos, Theseus volume mimicry, future a3/h2 checks
  status:   candidate invariant

FP-002 opaque_kill_black_hole
  detector: kill-pattern concentration / top-1 share / entropy collapse
  anchors:  h2 historical corpus
  status:   single strong anchor

FP-003 bounded_menu_wall
  detector: zero-promotion saturation under fixed menu
  anchors:  Techne, Polyhymnia
  status:   needs independence proof
```

---

## 4. What to do with F — park unless the next push is the ladder

F's confound kills (pinned thinking, 2×2 recognition/execution × MC/free-gen,
exact CIs, procedural-isomorph checks) are the right experiments, but F depends on
model-backed adapters, multi-seed runs, and API behavior — slower and more
environment-sensitive than A/E/B, and it advances the **reasoning-ladder track**,
not the mathematical-substrate track. Run F only after the substrate-hygiene loop
is in place, **or** if a deliberate decision is made that the next Prometheus push
is "stabilize the Reasoning Ladder as an empirical instrument." Not handed off in
this round.

---

## 5. The dependency structure (why the handoff looks the way it does)

```
            A (primitive + frozen interface)
           /          |            \
   [contract]    E.validate(§3.3)   B.triviality-gate(§3.2)
        |              |                    |
   day-1 freeze   Sprint 2            Sprint 3
```

- **A is on the critical path** and gates the *validation* steps of E and B — not
  their A-independent prep. Both E and B have large bodies of work that need no A.
- **The linchpin is A's interface, not A's full implementation.** If Harmonia B
  freezes the `costume_check` contract on day 1, Harmonia C and D code their
  validation calls against a stable signature while A's internals are still being
  built. Frozen contract (proposed, refine in Sprint 1):

```python
# harmonia/primitives/baseline_costume.py
def costume_check(
    claim,            # the structural claim: recommendations dict | partition | ranking | motif set
    rows,             # the raw records the claim was derived from
    baselines,        # list[Baseline] from the catalog (names resolve to callables rows->claim)
    *,
    null=None,        # shuffle/permutation null for the z leg (default: label-shuffle)
    n_null_trials=20,
    actionable=lambda delta: bool(delta),
) -> CostumeVerdict
# CostumeVerdict: per-baseline {agreement_rate, actionable_deltas, ties_claim: bool};
#   headline = strongest baseline that ties the claim ("indistinguishable from {baseline}");
#   z vs null; verdict ∈ {DISTINCT, COSTUME_OF:<baseline>, INCONCLUSIVE}
```

---

## 6. Handoff — proposed assignment to Harmonia C / D / E

Coordination is now **file-based** (Agora/Redis is down; Postgres only). Each
instance picks up its packet from this section; deltas land in its own journal +
back into D's registry.

### Harmonia B (me) — Proposal A — CRITICAL PATH
- **Day 1:** freeze the `costume_check` contract (§5) and commit it as a stub
  (signature + `CostumeVerdict` dataclass + the three baseline names) so C and D
  unblock immediately.
- **Sprint 1:** implement `marginal_majority`, `volume_weighted`, `pair_aware`;
  refactor Erebos's two harnesses to call it; prove byte-for-byte verdict parity.
- **Emit:** `BASELINE_COSTUME@v1` registry entry → seeds D's FP-001.

### Harmonia C — Proposal E — starts A-independent immediately
- **No-A-needed now:** (1) scan the live Theseus corpus for h2 records by emission
  date — report structured-vs-flat fraction and the deployment cutover; (2)
  backfill-feasibility audit — do historical flat rows retain `method_verdicts`,
  `knot_invariant`, `ec_invariant`, `method_counts` to re-derive the structured
  pattern without re-running? Bound recoverable vs permanently-opaque.
- **Needs A:** §3.3 subclass-signal validation calls `costume_check` against the
  frozen contract → run once A's stub lands; finalize when A ships.
- **Emit:** production-emission rate, backfill-recoverable fraction, subclass
  concentration → seeds D's FP-002 with real numbers.

### Harmonia D — Proposal B — starts A-independent immediately
- **No-A-needed now:** (1) reconcile the 144-vs-324 lattice discrepancy (read a3
  history; settle the operator set); (2) build the exhaustive 20,736-cell sweep
  computing `hold_rate` + `n_evaluated` over the full knot×EC cross-product; (3)
  implement B's **own** nulls (marginal-pairing, operator-degeneracy,
  relation-laxity) — these are B-specific and need not wait on A's generic catalog.
- **Needs A:** swap B's hand-rolled triviality gate to A's `costume_check` at the
  final cell-verdict step (so B's voids are gated by the shared primitive, not a
  bespoke one) — the regression check that A subsumes B's nulls.
- **Emit:** candidate-identity survivors (likely zero — that's a clean kill) →
  evidence for/against the "voids are the math" thesis; seeds D's FP-001 anchors.

### Harmonia E — Proposal D (thin registry) + integration/coordination — lightest lane
- **Now:** create `harmonia/memory/architecture/failure_primitive_atlas.md` +
  `harmonia/primitives/failure_primitives.py` with the FP-001/002/003 schema stub
  (§3). **Thin only** — no standalone taxonomy sprint.
- **Ongoing:** wire A/E/B detectors into the registry as they land; own the
  **FP-003 independence proof** (show Techne and Polyhymnia failed the bounded-menu
  wall *independently*, not via shared scour code — the falsifier in Proposal D §4).
- **Emit:** the first atlas with detectors that actually fire, grown from real A/E/B
  outputs rather than prose.

### Not handed off
- **Proposal F** — parked (§4). Revisit when/if the next push is reasoning-ladder
  stabilization; likely Harmonia B re-takes it then, in coordination with Icarus
  (which consumes the ladder read-only via `tier_oracle.py`).

---

## 7. Open coordination questions (for James)

1. Are Harmonia C / D / E spawned and available now, or do these packets queue
   until they boot? (Affects whether B freezes the A-contract for live consumers
   or just for the record.)
2. Confirm the assignment maps to instance strengths — any reason to swap who owns
   Proposal B vs E? (Both are substantial; B is more open-ended, E more bounded.)
3. With Agora/Redis down, is this doc + per-instance journals the agreed handoff
   channel, or is there a Postgres-backed queue I should be writing tasks into?
