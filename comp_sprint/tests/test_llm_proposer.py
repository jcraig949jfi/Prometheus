"""Unit tests for Boolean expression compiler and LLM macro proposal admission filter."""
from comp_sprint.llm_proposer import compile_exprs_to_xag, parse_proposed_macros


def test_compile_exprs_to_xag_full_adder_and_cas():
    fa = compile_exprs_to_xag(3, ["(x0 ^ x2) ^ x1", "((x0 ^ x2) & (x1 ^ x2)) ^ x2"])
    assert fa.truth_tables() == (0x96, 0xE8)
    assert fa.gate_count() == 5

    cas = compile_exprs_to_xag(2, ["x0 | x1", "x0 & x1"])
    assert cas.truth_tables() == (0b1110, 0b1000)
    assert cas.gate_count() == 2


def test_parse_proposed_macros_accepts_valid_and_rejects_bad():
    raw = """Here are the macros:
```json
{
  "macros": [
    {"name": "ha", "n_inputs": 2, "exprs": ["x0 ^ x1", "x0 & x1"]},
    {"name": "fa", "n_inputs": 3, "exprs": ["(x0 ^ x1) ^ x2", "(x0 & x1) | (x2 & (x0 ^ x1))"]},
    {"name": "bad_const", "n_inputs": 2, "exprs": ["x0 ^ x0"]},
    {"name": "bad_arity", "n_inputs": 5, "exprs": ["x0 & x1"]},
    {"name": "dup_ha", "n_inputs": 2, "exprs": ["x1 ^ x0", "x1 & x0"]}
  ]
}
```
"""
    acc, rej = parse_proposed_macros(raw, origin="test", max_macros=12, compress_exact=True)
    assert len(acc) == 2
    assert acc[0].name == "ha" and len(acc[0].gates) == 2
    # FA expressed naively (5 gates with OR) compresses cleanly to <= 5 gates!
    assert acc[1].name == "fa" and len(acc[1].gates) <= 5
    assert len(rej) == 3
