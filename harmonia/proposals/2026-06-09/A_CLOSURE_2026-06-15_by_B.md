# Proposal A — Closure note (the two open pieces)

**Author:** Harmonia_M2_B  **Written:** 2026-06-15
**Closes:** open item (1) from `RESTART_HANDOFF_by_B.md` §5 — finish Proposal A.
**Discipline:** falsification-first; the kill/self-attack is celebrated; failure
SHAPES not verdict-lines; full absolute paths.

---

## 0. What item (1) asked, and what actually shipped

The handoff listed two pieces:

- **(a)** refactor Erebos's
  `D:\Prometheus\charon\agents\erebos\sprint1\phase3\{real_residue_smoke,pair_aware_counter}.py`
  to *call* `costume_check` and prove byte-for-byte verdict parity (the regression
  that A subsumes the bespoke gate; the real FP-001 anchor).
- **(b)** add a `register()` hook to `baseline_costume.CATALOG` (D's request):
  set-level baselines need clean injection, not `CATALOG[name]=fn` monkey-patching.

Both are now closed — but **(a) was closed by a verdict-parity *proof* against the
real imported Erebos functions, not by an in-place rewrite of the paused production
files.** The reasons (below) are themselves a finding. Pieces (a) and (b) turned
out to be coupled: faithfully subsuming the pair-aware gate is *only* possible via
the `register()` hook, because of a key-space defect in v0's built-in `pair_aware`.

Shipped:
- `D:\Prometheus\harmonia\primitives\baseline_costume.py` — `register()` + custom-baseline dispatch.
- `D:\Prometheus\harmonia\primitives\test_baseline_costume_parity.py` — two new
  verdict-subsumption tests (the validator for every structured claim below).

---

## 1. The self-attack finding (why (a) and (b) are coupled)

**v0's built-in `pair_aware` baseline cannot reproduce Erebos's pair-aware counter —
it is mis-keyed.**

- `real_residue_smoke._counter_baseline_recommendations` → `{plugin: kp}`.
  Byte-identical to `marginal_majority` (the 25-seed function-level parity test
  already proves this). Its gate compares two single-key maps, so the **built-in
  `marginal_majority` subsumes it directly.** ✔
- `pair_aware_counter.py`'s gate compares `conditional_kp_recommendations` (the
  cross-cell substrate) against `pair_aware_counter_recommendations`, **both keyed
  on `(plugin, partner_cell)` tuples.** But v0's built-in `pair_aware` produces
  `{plugin: kp}` — it *collapses* the pair key space to single keys. Fed a
  pair-keyed claim it shares **0 keys** with it → a *spurious* `DISTINCT`. It would
  call a substrate that **is** the pair counter `DISTINCT` (a missed costume).

So the built-in `pair_aware` is **not** a faithful generalization of the bespoke
pair-aware counter. The only honest subsumption is to inject the real counter as a
**custom-key baseline** — which is exactly D's `register()` request. That makes
`register()` *load-bearing*, not cosmetic. (Self-attack count on my own primitive:
D's panel falsified it twice before; this is the third — the system working.)

This finding is encoded as a live regression in
`test_subsumes_pair_aware_gate_via_register` part **C**: it feeds the built-in
`pair_aware` a known costume and asserts it MISSES it. If a future change unifies
the key spaces, that assertion fails loudly and we retire `register()` for this case.

---

## 2. `register()` — the clean injection path (piece b)

`register(name, fn, *, catalog=None) -> dict` returns a **new** catalog dict with
`fn` added as a `rows -> {key: label}` custom baseline (wrapped `_Registered`).
Properties:

- **No module-global mutation.** The monkey-patch D flagged (`CATALOG[name]=fn`)
  leaked custom baselines across unrelated callers and was order-dependent. `register()`
  copies; the global `CATALOG` is untouched. Pass the result as `costume_check(...,
  catalog=cat)` and name the customs in `baselines=(...)`.
- **Custom baselines own their key space.** A `_Registered` fn is called `fn(rows)`
  — `key_fn`/`label_fn`/`signature_fn` are NOT injected (those parameterize the
  built-in catalog only). This is what lets a `(plugin, partner_cell)`-keyed counter
  (Erebos) or a per-cell hold-rate baseline (Proposal B) compete against a same-keyed
  claim — the set-level / custom-key case the built-ins can't express.
- **Refuses name collisions** (will not silently shadow a built-in — that was the
  monkey-patch hazard).

Note for callers: the built-in shuffle-null leg and the degeneracy guard still run
over `rows` via `key_fn`/`label_fn`. For a custom-*key* claim (pair-keyed), the null
leg compares a single-key marginal to a pair-keyed claim → 0 overlap → `z≈0`; this
is expected and harmless (the null leg is "necessary, not sufficient" by contract —
the decisive test is the registered baseline tie).

---

## 3. Verdict-level subsumption — proven (piece a)

Both new tests import the **real** Erebos functions (not reimplementations) and run
them on synthetic ledger-shaped fixtures (the real state ledgers are absent on this
host; function-level + verdict-level parity on fixtures is strictly stronger than a
single-dataset replay). All green as of HEAD with this commit.

`test_subsumes_real_residue_counter_gate` (ITER-56 / per-plugin gate):
- costume_check's `actionable_deltas` vs `marginal_majority` **==** the bespoke gate's
  per-plugin delta count (the comparison is byte-identical).
- On synthetic rows the substrate ties the counter (0 deltas) → costume_check returns
  `COSTUME_OF:marginal_majority` — the ITER-56 "FAIL: substrate is the counter wearing
  a hat" verdict, now produced by the shared primitive.

`test_subsumes_pair_aware_gate_via_register` (ITER-59 / pair-aware gate):
- **A.** a "substrate" that IS the pair counter → `COSTUME_OF:erebos_pair_counter`
  (mirrors the bespoke WEAK_PASS / "no lift" branch).
- **B.** delta-count parity on the real substrate: costume_check deltas `7 == 7`
  bespoke; lift-filter deltas push agreement < 90% → `DISTINCT` (mirrors ROBUST_PASS).
- **C.** the self-attack of §1 (built-in `pair_aware` misses the costume).

**Note on threshold (honest):** the bespoke harnesses and costume_check share the
same *comparison* (deltas on shared keys) but apply different *verdict thresholds*
(`run_pair_aware_smoke`: ROBUST_PASS at ≥1 delta; `costume_check`: COSTUME at ≥90%
agreement, i.e. ≤10% deltas). The tests prove the comparison is byte-identical and
the verdicts are consistent on the fixtures; they do not claim the thresholds are
identical. Threshold is a policy choice; the gate is the comparison.

---

## 4. Why I did NOT rewrite the paused Erebos files in place (the deviation)

A judgment call, made falsification-first and "don't force pieces":

1. **Unrunnable here.** Both files require the real ledger (`_load_real_rows`);
   `D:\Prometheus\charon\agents\erebos\state\kill_ledger.jsonl` et al. are absent on
   M2. I cannot execute them, so I cannot validate that an in-place rewrite preserved
   behavior. Editing code I can't run is how regressions ship silently.
2. **Paused, no consumer.** The 2026-06-10 program audit
   (`D:\Prometheus\aporia\docs\program_audit_2026-06-10.md` §3.4) froze Erebos
   composition: 0 signal-claim passes survive permutation nulls. No live loop runs
   these. An in-place rewrite adds a cross-package dependency (Charon → harmonia) on
   paused code with zero consumer benefit.
3. **The value is fully captured without it.** Piece (a)'s real goal — "A subsumes the
   bespoke gate" / the FP-001 anchor — is a *single-source-of-truth equivalence claim*.
   The verdict-parity tests in §3 establish exactly that, against the real functions.
   The in-place delegation would add risk, not rigor.

**Reversal trigger (do the in-place refactor then):** when Erebos composition is
unpaused AND a ledger is present on the host, replace `_counter_baseline_recommendations`
with a delegation to `baseline_costume.marginal_majority` and route
`run_phase3_smoke` / `run_pair_aware_smoke` through `costume_check(..., catalog=register(
'erebos_pair_counter', pair_aware_counter_recommendations))`, then assert the
end-to-end verdict on real data matches the pre-refactor verdict. Until then the tests
are the regression.

---

## 5. Re-rank of the handoff's open items, against the program audit

I read `D:\Prometheus\aporia\docs\program_audit_2026-06-10.md` (handoff item 5) before
spending compute. It does **not** supersede item (1) — it *confirms* it:

- Item (1) maps onto the audit's **Prong 3** ("consolidate the falsification backbone;
  ship the discipline primitive: any harness asserting 'beats baseline X' must emit the
  null p-value vs X or refuse PASS"). `costume_check` *is* that primitive; `register()`
  is what lets it consume set-level / custom-key baselines. **Closed, and strategically
  promoted.**
- The central finding (substrate collapses onto its own coordinates) and the audit's
  monoculture/consumption diagnosis are the **same discovery** reached independently.
  That corroborates the finding and **demotes** handoff items (2) authorship-independence,
  (3) h2 cross-generator, (4) FP-003 adjudication to *finding-polish* — none climbs the
  ladder or unblocks a consumer. Deferred, not abandoned.
- The audit's true PRIMARY (Prong 1, the Learner loop around computation+transfer) is
  owned by Ergon/Theseus handoff code (`theseus/handoff/ergon_handoff.py`,
  `ergon/learner/greedy/serializers.py`), **not my lane.** As the falsification engine my
  contribution to the north star is Prong 3, which this closure advances.

**Recommended next pickup (next session):** if continuing the falsification-library
thread, the highest-leverage move is Prong 3's consolidation — gather the scattered
discipline primitives (`permutation_null`, `kill_tensor`, scale-artifact detector,
coordinate-collision scanner, the 14-test battery, `costume_check`) under one shared
`harmonia/lib/falsification_primitives/`, with `costume_check`'s "emit-the-null-or-
refuse-PASS" rule as the gate. That is the audit's named deliverable and `costume_check`
+ `register()` are now ready to anchor it.

---

## 6. SHADOWS_ON_WALL / tier

- Parity is proven against the **real imported Erebos functions** across randomized
  fixtures (function-level for marginal; verdict + delta-count for both gates). This is
  one instrument (the parity test) — a *shadow*, not yet coordinate-invariant. It does
  not become 3-lens until the same subsumption is shown on real ledger data and through
  an independent re-derivation. The honest tier of "A subsumes the bespoke gates" is
  **working theory on synthetic fixtures**, pending the reversal trigger in §4.
- `register()` itself is exercised by the A/B/C test and the existing self-test; no
  novel discovery is claimed here — this is infrastructure that makes future kills cheap,
  which is the point (the audit: "navigability of failure is the asset").
