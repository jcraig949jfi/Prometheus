"""Instrument tests for Tyche v0 (run: python -m pytest -q tyche/tests)."""

import numpy as np
import pytest

from tyche import audits as A
from tyche import ecology as E
from tyche import lens as Lm
from tyche import worlds as Wm
from tyche.organisms import fit_predict

SPECS = Wm.build_worlds()
BY = {s["id"]: s for s in SPECS}
N = Lm.NIN


def test_world_set_shape():
    assert len(SPECS) == 32
    held = [s for s in SPECS if s["role"] == "heldout"]
    assert len(held) / len(SPECS) >= 0.25
    assert len({s["family"] for s in SPECS}) >= 4


def test_worlds_deterministic_and_seed_sensitive():
    for s in SPECS:
        X1, Y1 = Wm.generate(s, 1)
        X2, Y2 = Wm.generate(s, 1)
        assert np.array_equal(X1, X2) and np.array_equal(Y1, Y2)
        X3, _ = Wm.generate(s, 2)
        assert not np.array_equal(X1, X3)


def test_consequence_not_in_observations():
    # ruler access: no observed column IS the consequence channel
    for s in SPECS:
        if s.get("law", {}).get("kind") == "ident":
            continue  # K1 by design: the known control whose raw input suffices
        X, Y = Wm.generate(s, 1)
        if s["kind"] in ("hec_alien", "hec_null"):
            # Y is the NEXT state of the target component: equal to the
            # following observation except at episode restarts (<= 1/25)
            col = s["target"] - (1 if s["target"] > s["hidden"] else 0)
            nxt = (X[1:, col] == Y[:-1]).mean()
            assert nxt > 1 - 1.0 / s["restart"] - 0.02, (s["id"], nxt)
            continue
        for c in range(X.shape[1]):
            if s.get("law", {}).get("kind") == "decoy" and c == s["law"]["e"]:
                continue  # the designed decoy correlate (agree 0.65 + chance)
            x = X[:, c]
            if not np.issubdtype(x.dtype, np.integer):
                continue
            vals = np.union1d(np.unique(x), np.unique(Y))
            chance = sum((x == v).mean() * (Y == v).mean() for v in vals)
            assert (x == Y).mean() - chance < 0.3, (s["id"], c)


def test_random_lenses_are_causal():
    rng = np.random.default_rng(0)
    X, _ = Wm.generate(BY["P5_psign"], 1)
    Xi, _ = Wm.generate(BY["P1_xor2"], 1)
    for _ in range(150):
        g = Lm.random_genome(rng, n_ins=int(rng.integers(1, 9)))
        for _ in range(3):
            g, _ = Lm.mutate(g, rng)
        assert A.causality_audit(g, X)["pass"], g
        assert A.causality_audit(g, Xi)["pass"], g


def test_lead_cheat_is_caught():
    X, _ = Wm.generate(BY["P1_xor2"], 1)
    g = {"ins": [[Lm.LEAD_OP, [0], 1]], "out": [N]}
    assert not A.causality_audit(g, X)["pass"]
    cc = A.cheat_control()
    assert cc["instrument_ok"], cc


def test_mutations_valid_and_ids_stable():
    rng = np.random.default_rng(1)
    pop = [Lm.random_genome(rng) for _ in range(40)]
    for i in range(2000):
        g = pop[i % 40]
        if rng.random() < 0.3:
            g2 = Lm.graft(g, pop[int(rng.integers(40))], rng)
        else:
            g2, _ = Lm.mutate(g, rng)
        assert Lm.validate(g2), g2
        assert len(g2["ins"]) <= Lm.MAXLEN
        assert Lm.lens_id(g2) == Lm.lens_id(Lm._copy(g2))
        pop[i % 40] = g2


def test_forbidden_op_not_in_chemistry():
    assert Lm.LEAD_OP not in Lm.OPS


def _hand(wid):
    L = BY[wid]["law"]
    if wid == "P1_xor2":
        return {"ins": [["delay", [L["a"]], L["da"]], ["delay", [L["b"]], L["db"]], ["xor", [N, N + 1], None]],
                "out": [N + 2]}
    if wid == "P2_cmod":
        return {"ins": [["accmod", [L["a"]], 3]], "out": [N]}
    if wid == "P4_gate":
        return {"ins": [["delay", [L["b"]], L["db"]], ["delay", [L["c"]], L["dc"]], ["delay", [L["d"]], L["dd"]],
                        ["where", [N + 1, N, N + 2], None]], "out": [N + 3]}
    raise KeyError(wid)


@pytest.mark.parametrize("wid,twin", [("P1_xor2", "TSD1_xor2"), ("P2_cmod", "TSD2_cmod"), ("P4_gate", "TSD4_gate")])
def test_planted_attainable_and_twin_dead(wid, twin):
    g = _hand(wid)
    k = ("R0", "tree", "val", "all")
    we = E.WorldEval(BY[wid], 1)
    we.set_ecology([])
    assert we.gains(g, scopes=("all",))[k][0] > 0.3
    wt = E.WorldEval(BY[twin], 1)
    wt.set_ecology([])
    assert abs(wt.gains(g, scopes=("all",))[k][0]) < 0.05


def test_raw_ecology_cannot_reach_planted():
    # the raw current observation carries no information about planted laws
    for wid in ("P1_xor2", "P2_cmod", "P4_gate", "P5_psign"):
        we = E.WorldEval(BY[wid], 1)
        we.set_ecology([])
        for o in ("lin", "tree"):
            acc = we.base("R0", o, ["val"])["val"].mean()
            assert acc < 0.56, (wid, o, acc)


def test_tab_handles_binary_feature():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    F = np.c_[y.astype(float)]
    F[y == 1] = 1.0
    # median is 1 when ones are the majority
    y2 = y.copy()
    y2[:1200] = 1
    F2 = np.c_[y2.astype(float)]
    p = fit_predict("tab", F2, y2, [F2])[0]
    assert (p == y2).mean() == 1.0


def test_lexicase_keeps_specialists():
    rng = np.random.default_rng(0)
    M = np.zeros((10, 4))
    M[3, 0] = 1.0  # only individual 3 is good on case 0
    M[7, 1:] = 0.5
    sel = E.eps_lexicase(M, rng, 400)
    assert 3 in sel and 7 in sel


def test_residual_masks_partition():
    we = E.WorldEval(BY["HA_tab"], 1)
    we.set_ecology([])
    m = we.residual_masks("R0")
    assert not np.any(m["err"] & m["dis"])
