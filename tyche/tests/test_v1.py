"""Tyche v1 instrument tests: calibration lane, fuse, gate-6 predicate with
positive and cheat controls on synthetic rows."""

import json
import os

import numpy as np

from tyche import lens as Lm
from tyche.v1 import eco_v1 as E1
from tyche.v1 import report_v1 as R
from tyche.v1 import worlds_v1 as W1

S = W1.build_worlds_v1()
BY = {s["id"]: s for s in S}


def test_world_set():
    assert len({s["id"] for s in S}) == len(S) == 18
    assert sum(s["role"] == "heldout" for s in S) >= 4
    for s in S:
        if s.get("twin_of"):
            assert BY[s["twin_of"]]["law"] == s["law"]


def test_zero_marginal_precursors():
    # each single precursor of a Z xor world carries ~0 information alone
    X, Y = W1.generate(BY["Z1_xor_4_11"], 1)
    L = BY["Z1_xor_4_11"]["law"]
    a = np.roll(X[:, L["a"]], L["da"])[200:]
    b = np.roll(X[:, L["b"]], L["db"])[200:]
    y = Y[200:]
    assert abs((a == y).mean() - 0.5) < 0.02 and abs((b == y).mean() - 0.5) < 0.02
    assert ((a ^ b) == y).mean() > 0.999


def test_oracle_and_twin_deficit():
    E1._init(S)
    _, d = E1.task_deficit(("Z1_xor_4_11", 1, [], W1.oracle(BY["Z1_xor_4_11"]), "val"))
    assert d["R0|tree|deficit"] > 0.4
    _, d = E1.task_deficit(("N1_tsd_Z1", 1, [], W1.oracle(BY["Z1_xor_4_11"]), "val"))
    assert abs(d["R0|tree|deficit"]) < 0.05


def test_tab_inputs_independent_of_ecology():
    we = E1.WorldEvalV1(BY["G1_cmod3"], 1)
    we.set_ecology([])
    f0 = we.features(None, "tab")
    we.set_ecology([W1.oracle(BY["G1_cmod3"]), Lm.random_genome(np.random.default_rng(0))])
    assert np.array_equal(f0, we.features(None, "tab"))


def test_fuse_equals_concatenation():
    rng = np.random.default_rng(3)
    X = Lm.probe_input()
    for _ in range(100):
        a, b = Lm.random_genome(rng), Lm.random_genome(rng)
        f = Lm.fuse(a, b)
        assert Lm.validate(f, Lm.KFUSED)
        assert np.array_equal(Lm.execute(f, X), np.hstack([Lm.execute(a, X), Lm.execute(b, X)]))


def _row(home, kind="pair", test=0.4, prec=0.0, alone_z=0.5, twin_z=0.5):
    r = {"id": "L-x", "home": home, "kind": kind, "home_test": [test, 30.0, 3000],
         "home_reps": [[test, 30.0, 3000]] * 2, "replicated": True, "beats_null": True,
         "causality": {"pass": True}, "twin": {"z": twin_z}}
    if kind == "pair":
        r["components"] = {k: {"max_individual_val_gain_home": prec, "test_alone_z": alone_z} for k in "ab"}
    return r


def _camp(tmp, de_rows, v0_rows):
    for arm, rows in (("DE", de_rows), ("V0", v0_rows)):
        d = os.path.join(tmp, f"{arm}_s1")
        os.makedirs(d)
        json.dump(S, open(os.path.join(d, "WORLDS.json"), "w"))
        json.dump(rows, open(os.path.join(d, "PASS_D.json"), "w"))
    return tmp


def test_gate6_positive_control(tmp_path):
    o = R.evaluate(_camp(str(tmp_path), [_row("Z1_xor_4_11")], []))
    assert o["GATE6"] == "PASS" and o["passing_worlds"] == ["Z1_xor_4_11"]


def test_gate6_cheat_precursor_had_value(tmp_path):
    o = R.evaluate(_camp(str(tmp_path), [_row("Z1_xor_4_11", prec=0.05)], []))
    assert o["GATE6"] == "FAIL"


def test_gate6_cheat_v0_also_solved(tmp_path):
    o = R.evaluate(_camp(str(tmp_path), [_row("Z1_xor_4_11")], [_row("Z1_xor_4_11", kind="single")]))
    assert o["GATE6"] == "FAIL"


def test_gate6_twin_alive_blocks(tmp_path):
    o = R.evaluate(_camp(str(tmp_path), [_row("Z1_xor_4_11", twin_z=5.0)], []))
    assert o["GATE6"] == "FAIL"
