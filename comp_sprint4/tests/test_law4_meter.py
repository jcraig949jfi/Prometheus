"""Unit tests for Law 4 Word-Width & Z3-Decision Metering (`OpBudget v2`)."""
from __future__ import annotations

from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint4.law4_meter import optimize_s4a_law4, synthesize_s4b_law4, verify_bv_equiv_z3_det_v2
from comp_sprint4.s4a_bv_benchmarks import build_s4a_bv_benchmarks
from comp_sprint4.s4b_xag_benchmarks import build_s4b_xag_benchmarks


def test_law4_word_width_penalizes_huge_bigints_proportionally():
    # Two modules with identical loop counts: one operates on 64-bit ints, the other on 64,000-bit ints!
    m_small = LibModule.from_source(
        "m_small", 0,
        "def run_ops(circ):\n"
        "    x = 123456789\n"
        "    for _ in range(100):\n"
        "        x = (x ^ 0x55555555) & 0xFFFFFFFF\n"
        "    return circ\n",
    )
    m_big = LibModule.from_source(
        "m_big", 0,
        "def run_ops(circ):\n"
        "    x = (1 << 64000) - 1\n"
        "    y = (1 << 63999) + 1\n"
        "    for _ in range(100):\n"
        "        x = x ^ y\n"
        "    return circ\n",
    )
    orch = LibModule.from_source(
        "o", 0,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    return lib.run_ops(circ)\n",
        required_fn="solve",
    )
    t = build_s4b_xag_benchmarks()["s4b_hold_struct"][0]
    _, ms1 = synthesize_s4b_law4(t.n_inputs, t.targets, CompositionalAlgoArtifact("S", "T", 0, (m_small,), orch), seed=0, word_budget=500_000)
    _, ms2 = synthesize_s4b_law4(t.n_inputs, t.targets, CompositionalAlgoArtifact("S", "T", 0, (m_small,), orch), seed=0, word_budget=500_000)
    _, mb = synthesize_s4b_law4(t.n_inputs, t.targets, CompositionalAlgoArtifact("B", "T", 0, (m_big,), orch), seed=0, word_budget=500_000)
    # Determinism: 0.000 variance
    assert ms1["ops_spent"] == ms2["ops_spent"]
    # Big-int 64,000-bit XOR (1000 words x 100 iters = ~100,000 word-ops) MUST cost >> small 64-bit XOR (~100 ops)!
    assert mb["ops_spent"] > 80_000 and ms1["ops_spent"] < 500


def test_law4_z3_rlimit_count_exact_determinism():
    t = build_s4a_bv_benchmarks()["s4a_hold_struct"][0]
    ok1, _, rl1 = verify_bv_equiv_z3_det_v2(t.spec, t.spec)
    assert ok1 and rl1 == 0
    # Non-trivial proof
    from comp_sprint2.s2b_bv import BVBuilder
    b = BVBuilder(16, 2, fold_constants=False)
    p1 = b.build(b.op("ADD", b.inp(0), b.inp(1)))
    b2 = BVBuilder(16, 2, fold_constants=False)
    p2 = b2.build(b2.op("ADD", b2.op("XOR", b2.inp(0), b2.inp(1)), b2.op("SHL", b2.op("AND", b2.inp(0), b2.inp(1)), b2.const(1))))
    r1 = verify_bv_equiv_z3_det_v2(p1, p2, rlimit=100_000)
    r2 = verify_bv_equiv_z3_det_v2(p1, p2, rlimit=100_000)
    assert r1 == r2 and r1[0] is True and r1[2] > 1000
