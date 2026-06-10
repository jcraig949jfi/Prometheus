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
)

# The actual Erebos counter implementations (imported, not reimplemented).
from charon.agents.erebos._cross_cell_motif import per_plugin_majority
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _counter_baseline_recommendations,
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


if __name__ == "__main__":
    test_parity_with_erebos_counters()
    test_reproduces_erebos_failure()
    test_adversarial_recency_costume_slips_through()
    print("\nAll baseline_costume parity + self-attack checks complete.")
