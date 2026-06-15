"""Parity regression for Proposal A (baseline_costume).

Two jobs:

1. PARITY — prove `costume_check`'s `marginal_majority` reproduces the EXACT
   counter logic that caught Erebos (ITER-56), by importing Erebos's own
   functions and asserting identical output on randomized fixtures. This is the
   "the generalization lost nothing" regression AND the real FP-001 anchor
   (baseline_costume.marginal_majority == the per-plugin counter, function-level).

2. ADVERSARIAL SELF-ATTACK — Proposal A §5 Q1 turned on the primitive itself:
   construct a claim that is genuinely a baseline-in-a-hat (a *recency* costume)
   yet slips through v0 as DISTINCT, because recency is not in the three-baseline
   catalog. This documents the known gap and is the trigger condition for adding
   the 4th baseline (per the sequencing decision: add a baseline only when a real
   claim shape defeats the current three — here is that claim shape).

Run: python harmonia/primitives/test_baseline_costume_parity.py
No real ledger required (the Erebos state ledgers are absent on disk); parity is
proven at the function level on synthetic rows, which is strictly stronger than a
single-dataset replay.
"""
from __future__ import annotations

import random

from harmonia.primitives.baseline_costume import (
    costume_check,
    marginal_majority,
    register,
)

# The actual Erebos counter implementations (imported, not reimplemented).
from charon.agents.erebos._cross_cell_motif import (
    per_plugin_majority,
    extract_cooccurrence_motifs,
    conditional_kp_recommendations,
)
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _counter_baseline_recommendations,
    _substrate_routing_recommendations,
)
from charon.agents.erebos.sprint1.phase3.pair_aware_counter import (
    pair_aware_counter_recommendations,
    MIN_COOCCURRENCE,
    MIN_LIFT,
)


KEY = lambda r: r["plugin_id"]
LABEL = lambda r: r.get("kill_pattern") or "PROMOTED"


def _fixture(seed: int, n_plugins: int = 8, n_rows: int = 400) -> list:
    """Randomized ledger-shaped rows with per-plugin label skew + some PROMOTED
    (kill_pattern=None) rows, mirroring real ledger structure."""
    rng = random.Random(seed)
    rows = []
    for _ in range(n_rows):
        pid = f"g{rng.randint(0, n_plugins - 1):02d}_plugin"
        # per-plugin skewed kp distribution + occasional PROMOTED (None)
        roll = rng.random()
        if roll < 0.15:
            kp = None  # -> "PROMOTED" under both implementations
        else:
            # dominant kp per plugin + noise
            dom = f"{pid}_dominant_kp"
            kp = dom if rng.random() < 0.6 else f"{pid}_kp_{rng.randint(0, 3)}"
        rows.append({"plugin_id": pid, "kill_pattern": kp,
                     "input_signature": f"sig_{rng.randint(0, 50)}"})
    return rows


def test_parity_with_erebos_counters() -> None:
    """costume_check's marginal_majority == both Erebos counter implementations,
    across many seeds. Function-level equivalence = A subsumes the bespoke gate."""
    for seed in range(25):
        rows = _fixture(seed)
        mine = marginal_majority(rows, key_fn=KEY, label_fn=LABEL)
        erebos_a = per_plugin_majority(rows)                 # _cross_cell_motif
        erebos_b = _counter_baseline_recommendations(rows)   # real_residue_smoke
        assert mine == erebos_a, f"seed {seed}: diverges from per_plugin_majority"
        assert mine == erebos_b, f"seed {seed}: diverges from _counter_baseline"
    print("PARITY PASS: marginal_majority == per_plugin_majority == "
          "_counter_baseline_recommendations across 25 seeds.")


def test_reproduces_erebos_failure() -> None:
    """A 'substrate' whose recommendation IS the per-plugin counter must be
    flagged COSTUME_OF:marginal_majority — the exact ITER-56 verdict, now
    produced by the shared primitive instead of a bespoke harness."""
    rows = _fixture(seed=99)
    substrate_claim = per_plugin_majority(rows)  # the substrate that fooled itself
    v = costume_check(substrate_claim, rows, key_fn=KEY, label_fn=LABEL,
                      signature_fn=lambda r: r["input_signature"])
    assert v.verdict == "COSTUME_OF:marginal_majority", v.headline
    print("FAILURE-REPRO PASS:", v.headline)


def test_adversarial_recency_costume_slips_through() -> None:
    """Proposal A §5 Q1 self-attack. Build a claim that is a *recency* costume:
    per key, recommend the LAST-seen label. It is genuinely a baseline-in-a-hat,
    but v0's three baselines (marginal / volume / pair) do not include recency, so
    costume_check returns DISTINCT. This is the documented catalog gap and the
    trigger to add a `most_recent` baseline.

    The test PASSES by confirming the gap exists (verdict == DISTINCT), so it
    fails loudly if a future catalog change closes the gap (then promote recency
    into the catalog and flip this assertion)."""
    rows = _fixture(seed=7)
    # recency claim: last label seen per key
    recency = {}
    for r in rows:
        recency[KEY(r)] = LABEL(r)
    v = costume_check(recency, rows, key_fn=KEY, label_fn=LABEL,
                      signature_fn=lambda r: r["input_signature"])
    # Honest documentation of the hole: recency is NOT caught by v0.
    assert v.verdict == "DISTINCT", (
        "Recency costume was caught -- catalog changed; promote `most_recent` "
        "into the catalog and update this test. " + v.headline
    )
    print("ADVERSARIAL-GAP DOCUMENTED:", v.headline,
          "\n  -> v0 does not catch a recency costume; add `most_recent` when a "
          "real claim of this shape appears (Proposal A catalog-growth rule).")


def test_unique_key_degeneracy_guard() -> None:
    """Harmonia D's filed hole (a3 generic_catalog_control): on a unique-key,
    imbalanced binary claim, the OLD costume_check returned
    COSTUME_OF:marginal_majority — a label-copier tie that certifies nothing.
    The guard must (a) flag marginal_majority vacuous on unique keys, and
    (b) return INCONCLUSIVE_DEGENERATE rather than a spurious COSTUME."""
    rows = [{"cid": f"cell_{i}", "v": ("VOID" if i < 3 else "NONVOID")}
            for i in range(300)]                    # 1% VOID, every key unique
    claim = {r["cid"]: r["v"] for r in rows}
    v = costume_check(claim, rows, key_fn=lambda r: r["cid"],
                      label_fn=lambda r: r["v"])
    assert v.verdict == "INCONCLUSIVE_DEGENERATE", v.headline
    mm = next(b for b in v.per_baseline if b.name == "marginal_majority")
    assert mm.vacuous, "marginal_majority must be vacuous on unique keys"
    print("DEGENERACY-GUARD PASS:", v.headline)


def _cooccur_fixture(seed: int, n_sig: int = 120) -> list:
    """Ledger-shaped rows with planted cross-cell co-occurrence structure: each
    input_signature emits 2-3 (plugin, kp) cells; when p0 co-occurs with p1 its kp
    skews to a shared 'kpX'. This is the shape the pair-aware / cross-cell gate was
    built to navigate (multi-cell structure a per-plugin counter cannot express)."""
    rng = random.Random(seed)
    rows = []
    for s in range(n_sig):
        sig = f"sig_{s}"
        plugs = rng.sample(range(5), rng.choice([2, 2, 3]))
        for p in plugs:
            if p == 0 and 1 in plugs:
                kp = "kpX" if rng.random() < 0.8 else f"kp{p}"
            else:
                kp = f"kp{p}" if rng.random() < 0.7 else f"kp_noise{rng.randint(0, 2)}"
            rows.append({"plugin_id": f"p{p}", "kill_pattern": kp,
                         "input_signature": sig})
    return rows


def test_subsumes_real_residue_counter_gate() -> None:
    """VERDICT-level subsumption of the real_residue_smoke per-plugin gate (ITER-56).

    The bespoke gate compares `_substrate_routing_recommendations` (motif-derived,
    keyed on plugin) against `_counter_baseline_recommendations` (keyed on plugin)
    and FAILs when the substrate ties the counter. Both maps are single-key, so
    costume_check's built-in `marginal_majority` reproduces the comparison directly.

    We import the REAL Erebos functions (not reimplementations) and assert:
      (1) costume_check's actionable_deltas vs marginal_majority == the bespoke
          gate's per-plugin delta count (the comparison is identical), and
      (2) on synthetic ledger rows the substrate ties the counter (0 deltas), so
          costume_check returns COSTUME_OF:marginal_majority — the ITER-56 'FAIL:
          substrate is the counter wearing a hat' verdict, now via the shared gate.
    """
    rng = random.Random(2026)
    rows = []
    for _ in range(400):
        p = f"g{rng.randint(0, 7):02d}_plugin"
        kp = (None if rng.random() < 0.15
              else (f"{p}_dom" if rng.random() < 0.6 else f"{p}_kp{rng.randint(0, 3)}"))
        rows.append({"plugin_id": p, "kill_pattern": kp,
                     "input_signature": f"sig_{rng.randint(0, 50)}", "domain": "unknown"})

    counter = _counter_baseline_recommendations(rows)            # real Erebos
    substrate = _substrate_routing_recommendations(rows)          # real Erebos
    bespoke_deltas = sum(1 for p in (set(counter) | set(substrate))
                         if counter.get(p) != substrate.get(p))

    kf = lambda r: r["plugin_id"]
    lf = lambda r: r.get("kill_pattern") or "PROMOTED"
    v = costume_check(substrate, rows, baselines=("marginal_majority",),
                      key_fn=kf, label_fn=lf)
    mm = next(b for b in v.per_baseline if b.name == "marginal_majority")

    # (1) the comparison is byte-identical: costume_check counts the same deltas.
    assert mm.actionable_deltas == bespoke_deltas, (
        f"costume_check deltas {mm.actionable_deltas} != bespoke {bespoke_deltas}")
    # (2) substrate ties the counter -> the ITER-56 FAIL, reproduced as COSTUME.
    assert bespoke_deltas == 0, f"fixture lost its tie (deltas={bespoke_deltas})"
    assert v.verdict == "COSTUME_OF:marginal_majority", v.headline
    print("SUBSUMES-PER-PLUGIN-GATE PASS:", v.headline,
          f"(costume_check deltas == bespoke deltas == {bespoke_deltas})")


def test_subsumes_pair_aware_gate_via_register() -> None:
    """VERDICT-level subsumption of the pair_aware_counter gate (ITER-59), AND the
    self-attack proving register() is load-bearing here (built-in pair_aware is NOT).

    The bespoke gate compares the cross-cell substrate (`conditional_kp_recommendations`,
    keyed on (plugin, partner_cell)) against the raw pair-aware counter
    (`pair_aware_counter_recommendations`, same key space). costume_check's BUILT-IN
    `pair_aware` keys on single key_fn keys and so CANNOT see this comparison — the
    only faithful subsumption is to inject the real counter as a custom-key baseline
    via register(). We prove three things on REAL imported Erebos functions:

      A. register() path catches a costume: a 'substrate' that IS the pair counter
         -> COSTUME_OF:erebos_pair_counter (mirrors the bespoke WEAK_PASS: no lift).
      B. register() path matches the bespoke delta computation exactly on the real
         substrate, and returns DISTINCT when the lift filter adds deltas (mirrors
         ROBUST_PASS).
      C. SELF-ATTACK: the built-in `pair_aware` baseline, run on the SAME pair-keyed
         costume from (A), returns DISTINCT — it MISSES the costume (0 shared keys),
         because it collapsed the key space. This is why register() is required, not
         optional; it fails loudly if a future built-in change closes the gap.
    """
    rows = _cooccur_fixture(seed=0)
    motifs = extract_cooccurrence_motifs(
        rows, min_cooccurrence=MIN_COOCCURRENCE, min_lift=MIN_LIFT).motifs
    substrate = conditional_kp_recommendations(rows, motifs)     # real Erebos, pair-keyed
    paircnt = pair_aware_counter_recommendations(rows)           # real Erebos, pair-keyed
    assert substrate and paircnt, "fixture produced no motifs/pairs"

    # key/label fns are only used by the null + guard legs (over rows); the registered
    # baseline owns its key space and is called rows-only.
    kf = lambda r: r["plugin_id"]
    lf = lambda r: r.get("kill_pattern") or "PROMOTED"
    cat = register("erebos_pair_counter", pair_aware_counter_recommendations)

    # --- A. the costume IS caught via register() -----------------------------
    costume_claim = paircnt  # a 'substrate' that is literally the pair counter
    vA = costume_check(costume_claim, rows, baselines=("erebos_pair_counter",),
                       key_fn=kf, label_fn=lf, catalog=cat)
    assert vA.verdict == "COSTUME_OF:erebos_pair_counter", vA.headline

    # --- B. delta-count parity + DISTINCT on the real substrate --------------
    bespoke_deltas = sum(1 for k, val in substrate.items() if paircnt.get(k) != val)
    vB = costume_check(substrate, rows, baselines=("erebos_pair_counter",),
                       key_fn=kf, label_fn=lf, catalog=cat)
    epc = next(b for b in vB.per_baseline if b.name == "erebos_pair_counter")
    assert epc.actionable_deltas == bespoke_deltas, (
        f"costume_check deltas {epc.actionable_deltas} != bespoke {bespoke_deltas}")
    assert bespoke_deltas >= 1 and vB.verdict == "DISTINCT", (
        f"expected lift-filter deltas -> DISTINCT; got {vB.verdict}, "
        f"deltas={bespoke_deltas}")

    # --- C. SELF-ATTACK: built-in pair_aware MISSES the same costume ---------
    # Run the built-in pair_aware against the KNOWN costume from (A). Because it
    # collapses (plugin, partner_cell) -> plugin, it shares 0 keys with the pair-
    # keyed claim and reports DISTINCT: it fails to catch a costume register() catches.
    vC = costume_check(costume_claim, rows, baselines=("pair_aware",),
                       key_fn=kf, label_fn=lf,
                       signature_fn=lambda r: r["input_signature"])
    assert vC.verdict == "DISTINCT", (
        "built-in pair_aware now catches the pair-keyed costume -- key spaces may "
        "have been unified; if so, retire register() for this case. " + vC.headline)
    print("SUBSUMES-PAIR-AWARE-GATE PASS (via register):",
          f"\n  A. costume caught: {vA.verdict}",
          f"\n  B. real substrate DISTINCT, deltas {epc.actionable_deltas}=={bespoke_deltas} (bespoke)",
          f"\n  C. self-attack: built-in pair_aware MISSES it ({vC.verdict}) -> register() is load-bearing")


if __name__ == "__main__":
    test_parity_with_erebos_counters()
    test_reproduces_erebos_failure()
    test_adversarial_recency_costume_slips_through()
    test_unique_key_degeneracy_guard()
    test_subsumes_real_residue_counter_gate()
    test_subsumes_pair_aware_gate_via_register()
    print("\nAll baseline_costume parity + self-attack + guard checks complete.")
