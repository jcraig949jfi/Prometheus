"""Tests for A1 (INDUSTRY: Berkeley ABC) wrapper and sound AIG -> XAG XOR folding."""
from comp_sprint.circuit import verify_truth_tables
from comp_sprint.industry_abc import synthesize_with_abc


def test_abc_full_adder_and_asymmetric_exact():
    # 2-input asymmetric x0 & ~x1
    res1 = synthesize_with_abc(2, (0b0010,))
    assert verify_truth_tables(res1["aig"], (0b0010,))
    assert res1["aig_gates"] == 1
    assert res1["xag_gates"] == 1

    # 3-input 2-output full adder: sum=0x96, carry=0xE8
    res_fa = synthesize_with_abc(3, (0x96, 0xE8))
    assert verify_truth_tables(res_fa["aig"], (0x96, 0xE8))
    assert verify_truth_tables(res_fa["xag"], (0x96, 0xE8))
    # XAG folding must never worsen gate count
    assert res_fa["xag_gates"] <= res_fa["aig_gates"]
    assert res_fa["aig_gates"] <= 10
