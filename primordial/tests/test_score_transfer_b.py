"""S1 clause B check-b: graft vs both cheats paired per run seed, Holm across worlds, gates."""
from __future__ import annotations

import json
import pathlib

import pytest

from primordial.ops import qd_ledger as Q
from primordial.score import transfer_b as TB

ROOT = pathlib.Path(__file__).resolve().parents[2]
E_T1B = ROOT / "primordial/ledger/rows/E/E-T1b-transfer-harness-vs-cheats.jsonl"
E_T1 = ROOT / "primordial/ledger/rows/E/E-T1-transfer-harness.jsonl"


def test_signflip_p_is_exact():
    assert TB.signflip_p([1.0, 2.0, 3.0]) == 0.125          # only the all-plus flip reaches the mean
    assert TB.signflip_p([-1.0, -2.0, -3.0]) == 1.0
    assert TB.signflip_p([0.0, 0.0]) == 1.0


def test_holm_step_down():
    got = TB.holm({"a": 0.01, "b": 0.02, "c": 0.04})
    assert [got[k]["reject"] for k in "abc"] == [True, True, True]      # .01<=.0167 .02<=.025 .04<=.05
    got = TB.holm({"a": 0.01, "b": 0.03, "c": 0.04})
    assert [got[k]["reject"] for k in "abc"] == [True, False, False]    # .03 > .025 stops the family
    assert got["b"]["p_adj"] == pytest.approx(0.06) and got["c"]["p_adj"] == pytest.approx(0.06)


def _rows(graft, rand, shuf, self_, oracle=None, integrity=True, donor=2, rec=4):
    out = []
    for s, vals in enumerate(zip(graft, rand, shuf, self_)):
        for cond, v in zip(TB.CONDITIONS[:1] + TB.CONDITIONS[2:] + TB.CONDITIONS[1:2], vals):
            r = {"family": "linear", "donor_world": donor, "recipient_world": rec, "condition": cond,
                 "run_seed": s, "held_auc": v}
            if cond == "graft":
                r.update(graft_bytes_unmodified=integrity, graft_fused_eq_numpy=True)
                if s == 0:
                    r.update(oracle or {"world_oracle_honest": {"elites_failing": 0},
                                        "world_oracle_skip_lin": {"elites_failing": 16},
                                        "brain_oracle_honest": {"mismatched_rows": 0},
                                        "brain_oracle_cheat": {"elites_mismatching": 16}})
            out.append(r)
    return out


def test_gates_make_a_pair_indeterminate_not_fail():
    n = 8
    good = _rows([10.0 + i for i in range(n)], [1.0] * n, [2.0] * n, [20.0] * n)
    assert TB.check_b(good)["pairs"][0]["verdict"] == "PASS"
    flat = _rows([1.0] * n, [1.0] * n, [2.0] * n, [20.0] * n)
    assert TB.check_b(flat)["pairs"][0]["verdict"] == "FAIL"
    no_positive = _rows([10.0] * n, [1.0] * n, [2.0] * n, [0.0] * n)
    v = TB.check_b(no_positive)["pairs"][0]
    assert v["verdict"] == "INDETERMINATE" and "planted positive" in v["problems"][0]
    bad_oracle = _rows([10.0] * n, [1.0] * n, [2.0] * n, [20.0] * n,
                       oracle={"world_oracle_honest": {"elites_failing": 3}})
    assert TB.check_b(bad_oracle)["pairs"][0]["verdict"] == "INDETERMINATE"
    tampered = _rows([10.0] * n, [1.0] * n, [2.0] * n, [20.0] * n, integrity=False)
    assert TB.check_b(tampered)["pairs"][0]["verdict"] == "INDETERMINATE"
    unpaired = good[:-1]                                         # drop one cheat row of the last seed
    assert TB.check_b(unpaired)["pairs"][0]["verdict"] == "INDETERMINATE"


def test_check_b_rederives_e_t1b_table_from_rows():
    out = TB.check_b(TB.load_rows([E_T1B]))
    by = {p["pair"]: p for p in out["pairs"]}
    assert set(by) == {"w2->w4", "w25->w1", "w17->w3"}
    assert out["holm_families"] == {"E-T1b-transfer-harness-vs-cheats": 3}
    for p in by.values():
        assert p["n"] == 16 and p["problems"] == [] and p["rederived_equals_harness"] is True
    assert by["w2->w4"]["graft_p_max"] == pytest.approx(0.000274658203125)
    assert by["w17->w3"]["graft_p_max"] == pytest.approx(0.346649169921875)
    assert by["w25->w1"]["graft_p_max"] == pytest.approx(0.70458984375)
    assert {k: v["verdict"] for k, v in by.items()} == {"w2->w4": "PASS", "w17->w3": "FAIL", "w25->w1": "FAIL"}
    assert all(v["self_graft_p_max"] < 1e-4 for v in by.values())


def test_qd_ledger_check_b_cli(capsys):
    assert Q.main(["check-b", "--rows", str(E_T1B), str(E_T1)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["clause"] == "B" and {p["verdict"] for p in out["pairs"]} <= {"PASS", "FAIL", "INDETERMINATE"}
