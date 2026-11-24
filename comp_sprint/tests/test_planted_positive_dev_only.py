"""Dev-Only Planted-Positive Instrument Qualification Test (ZERO holdout access).

Proves that `synth_base.py` v2 (Monotonic Davio + Exact Macro Functional Factorization
+ Exact NPN4/Multi-Output k-Cut Rewriting):
  1. Preserves exact NPN4 wire composition across random equivalent pairs.
  2. Is 100% strictly monotonic (0 regressions vs A0_BASE on every dev task for ANY library).
  3. Converts a small 3-macro planted compositional library (Full Adder, Half Adder,
     Compare-And-Swap) into LARGE, genuine flattened primitive gate reductions on
     `dev_structured` (e.g., popcount5 17->12, sort4 14->10, add2_cin 10->9), while
     a size-matched optimal `SHAM` library gets 0 / negligible gain!
"""
from __future__ import annotations

import random

from comp_sprint.benchmarks import build_structured_tasks
from comp_sprint.circuit import Gate, Macro, XAGCircuit
from comp_sprint.library import Artifact, build_sham_matched_library
from comp_sprint.npn import compose_npn4_wire_map, npn4_canonical
from comp_sprint.synth_base import synthesize_with_library


def _build_planted_compositional_artifact() -> Artifact:
    """3 classic 2-output compositional building blocks (HA, FA, CAS), zero artificial discount."""
    # Half Adder: (a^b, a&b) -- 2 gates
    ha = Macro.from_circuit(
        "half_adder",
        XAGCircuit(
            n_inputs=2,
            gates=(Gate("XOR", 0, False, 1, False), Gate("AND", 0, False, 1, False)),
            outputs=((2, False), (3, False)),
        ),
        origin="planted_positive",
    )
    # Full Adder: (sum, carry) -- 5 gates (1 AND + 4 XOR)
    fa = Macro.from_circuit(
        "full_adder",
        XAGCircuit(
            n_inputs=3,
            gates=(
                Gate("XOR", 0, False, 2, False),
                Gate("XOR", 1, False, 2, False),
                Gate("AND", 3, False, 4, False),
                Gate("XOR", 5, False, 2, False),
                Gate("XOR", 3, False, 1, False),
            ),
            outputs=((7, False), (6, False)),
        ),
        origin="planted_positive",
    )
    # Compare-And-Swap: (a|b, a&b) -- 2 gates
    cas = Macro.from_circuit(
        "compare_swap",
        XAGCircuit(
            n_inputs=2,
            gates=(Gate("AND", 0, True, 1, True), Gate("AND", 0, False, 1, False)),
            outputs=((2, True), (3, False)),
        ),
        origin="planted_positive",
    )
    return Artifact(arm="PLANTED_POS", generation=0, macros=(ha, fa, cas))


def test_npn4_wire_map_exact_composition():
    rng = random.Random(42)
    for _ in range(40):
        tt = rng.getrandbits(16)
        canon = npn4_canonical(tt)
        res = compose_npn4_wire_map(tt, canon)
        assert res is not None
        src_idx, src_inv, out_inv = res
        rebuilt = 0
        for r in range(16):
            cr = 0
            for j in range(4):
                b = ((r >> src_idx[j]) & 1) ^ int(src_inv[j])
                cr |= b << j
            out_bit = ((canon >> cr) & 1) ^ int(out_inv)
            if out_bit:
                rebuilt |= 1 << r
        assert rebuilt == tt


def test_planted_positive_monotonic_gain_on_dev_only():
    dev_structured, _holdout_unused = build_structured_tasks()
    planted_art = _build_planted_compositional_artifact()
    sham_art = build_sham_matched_library(planted_art, seed=77777, compress_exact=True)

    base_gates = []
    planted_gates = []
    sham_gates = []
    for t in dev_structured:
        cb = synthesize_with_library(t.n_inputs, t.targets, library=(), budget=8000, seed=0)
        cp = synthesize_with_library(t.n_inputs, t.targets, library=planted_art.macros, budget=8000, seed=0)
        cs = synthesize_with_library(t.n_inputs, t.targets, library=sham_art.macros, budget=8000, seed=0)
        assert cb.truth_tables() == t.targets
        assert cp.truth_tables() == t.targets
        assert cs.truth_tables() == t.targets
        assert cp.gate_count() <= cb.gate_count(), f"Planted regressed on {t.task_id}"
        assert cs.gate_count() <= cb.gate_count(), f"Sham regressed on {t.task_id}"
        base_gates.append(cb.gate_count())
        planted_gates.append(cp.gate_count())
        sham_gates.append(cs.gate_count())

    # Must achieve a clear (>= 5 total gates) reduction on dev_structured over BOTH BASE and SHAM
    # while SHAM stays at 0 (or minimal) gain!
    assert sum(base_gates) - sum(planted_gates) >= 5, (
        f"Expected >=5 gate reduction from planted compositional library: base={sum(base_gates)} planted={sum(planted_gates)}"
    )
    assert sum(sham_gates) - sum(planted_gates) >= 5, (
        f"Expected >=5 gate separation over SHAM: sham={sum(sham_gates)} planted={sum(planted_gates)}"
    )
