"""E-002: the candidate criterion C-OP (T-007) beside the frozen v0.2.1 MAJORITY rule. Stdlib + committed fixtures only."""
from __future__ import annotations

from archaeon.causal_lens import e002_continuity as E
from archaeon.causal_lens.schema_v02 import ILL, NI


def test_c_op_clauses():
    X = {"name": "x", "code_ref": "f.py:1", "exchangeable": [["a", "b"]]}
    P = {"name": "p", "code_ref": "f.py:2", "exchangeable": [], "rule": E.MAJ}
    assert E.continuity_op({"a": 0.6, "b": 0.4}, None)["hu_continuity"] == NI                 # clause 2: undeclared operator
    assert E.continuity_op({"a": 15 / 16, "b": 1 / 16}, X)["hu_continuity"] == ILL             # clause 3 ignores realized shares (F1)
    assert E.continuity_op({"a": 0.6, "b": 0.4}, P)["hu_continuity"] == "a"                   # clause 4 = C-MAJ
    assert E.continuity_op({"a": 1.0}, X, {"a": "a"})["hu_continuity"] == "a"                 # self-cross: one distinct HU
    assert E.continuity_op({"a": 1.0, "b": 0.0}, X)["hu_continuity"] == "a"                   # a zero contributor is not live


def test_binomial_null():
    assert E.binom_two_sided_p(8, 16) == 1.0
    assert round(E.binom_two_sided_p(13, 16), 4) == 0.0213 and round(E.binom_two_sided_p(12, 16), 4) == 0.0768


def test_t008_fixture_readings():
    r = E.fixtures()
    for k in ("v01_symmetric_recombination/t", "v02_majority_recombination_60_40/t", "v12_no_singular_lineage_stable_architecture/t",
              "v14_meaningless_concept_ill_posed/t0"):
        assert r[k]["verdict_depends_on_declaration"] and r[k]["declared_operator_in_fixture"] is None
        assert r[k]["C-OP|undeclared"] == NI and r[k]["C-OP|exchangeable"] == ILL
    assert r["v02_majority_recombination_60_40/t"]["C-OP|privileged"] == "hA"
    for row in r.values():                                                                  # every C-OP value is representable in frozen v0.2
        for lab in ("C-OP|undeclared", "C-OP|exchangeable", "C-OP|privileged"):
            assert row.get(lab + ":v02_violations", []) == []
