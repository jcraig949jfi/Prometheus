"""Tyche v2 instrument tests: world certificates, oracles, compose,
strict gating, regime phases."""

import numpy as np

from tyche import lens as Lm
from tyche.v2 import certify as C
from tyche.v2 import run_v2 as R
from tyche.v2 import worlds_v2 as W2

STATIC = W2.build_static(20261002, 0)
BY = {s["id"]: s for s in STATIC}


def test_oracles_exact():
    for w in STATIC:
        o = W2.oracle(w["law"])
        if o is None or w["kind"] == "tsd":
            continue
        X, Y = W2.generate(w, 1)
        Z = Lm.execute(o, X)
        if w["law"]["comb"] == "table":
            assert (Z.astype(int) == np.stack(W2.precursors(w["law"], X), 1)).all()
        else:
            assert (np.rint(Z[200:, 0]).astype(int) == Y[200:]).all(), w["id"]


def test_generated_tables_resilient_nonaffine():
    rng = np.random.default_rng(0)
    for t in W2._resilient_tables(rng, want=20):
        assert sum(t) == 8
        assert W2.lowest_informative_order(t) >= 2
    for w in STATIC:
        if w["law"]["comb"] == "table":
            assert W2.lowest_informative_order(w["law"]["table"]) == w["law"]["lowest_order"] >= 2


def test_needle_orders_certified():
    want = {"D3_v0": 2, "D4a_v0": 3, "D4b_v0": 3, "D4c_v0": 4, "D5t_v0": 2}
    for wid, k in want.items():
        r = C.certify_world(BY[wid])
        assert r["lowest_order_empirical"] == k, (wid, r["lowest_order_empirical"])
        assert r["bank_max"]["above_null_bits"] < 0.01, (wid, r["bank_max"])


def test_d6_not_a_window_function():
    r = C.certify_world(BY["D6_v0"])
    assert r["bank_max"]["above_null_bits"] < 0.05


def test_compose_is_b_of_a():
    rng = np.random.default_rng(2)
    X = Lm.probe_input()
    for _ in range(100):
        a, b = Lm.random_genome(rng), Lm.random_genome(rng)
        Za = Lm.execute(a, X)
        Xa = np.stack([Za[:, v % Za.shape[1]] for v in range(Lm.NIN)], 1)
        assert np.allclose(Lm.execute(Lm.compose(a, b), X), Lm.execute(b, Xa))


def test_strict_lexicase_with_no_eligible_returns_nothing():
    rng = np.random.default_rng(0)
    M = np.zeros((5, 3))
    assert R.lexicase_trace(M, M, rng, 10, eligible=[]) == []
    got = R.lexicase_trace(M, M, rng, 10, eligible=[2, 4])
    assert {r for r, _ in got} <= {2, 4}


def test_regime_phases_share_inputs():
    reg = W2.build_regime(20261002, 0)
    for s in reg:
        X1, Y1 = W2.generate(W2.phase_spec(s, 1), 1)
        X2, Y2 = W2.generate(W2.phase_spec(s, 2), 1)
        assert np.array_equal(X1, X2) and not np.array_equal(Y1, Y2)
