import numpy as np

from ensorain.wtp3.collider import (marginal_surrogate, additive_part, holdout, _addr, collide, experience, make,
                                    train, SIMPLE)
from ensorain.wtp3.controls import planted
from ensorain.wtp3.detect3 import completion
from ensorain.wtp3.autopsy import intervene


def test_surrogate_exact():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(6, 7, 5)) + rng.normal(size=(6, 1, 1))
    xs, _ = marginal_surrogate(np.random.default_rng(1))(x, x)
    assert abs(x.mean() - xs.mean()) < 1e-12
    assert abs(x.var() - xs.var()) < 1e-9
    for m in range(3):
        ax = tuple(k for k in range(3) if k != m)
        assert np.allclose(x.mean(axis=ax), xs.mean(axis=ax))
    assert np.allclose(additive_part(x), additive_part(xs))
    assert not np.allclose(x, xs)


def test_holdout_never_shows_a_pair():
    dims = [10, 9, 11]                                   # blocks need >= 64 cells, so small worlds cannot host recomb
    rng = np.random.default_rng(3)
    c = rng.integers(0, 10 * 9 * 11, size=3000)
    st = dict(t=np.arange(3000), c=c, y=rng.normal(size=3000), dims=dims)
    stR, blk, info = holdout(st, np.random.default_rng(4))
    assert stR is not None
    H = info["H"]
    A = _addr(dims, stR["c"])
    inH = np.stack([np.isin(A[:, m], H[m]) for m in range(3)], 1)
    assert (inH.sum(1) <= 1).all()                       # no kept sample holds two held-out values
    for m in range(3):
        assert np.isin(H[m], A[:, m]).all()              # every held-out value is still seen alone
    B = _addr(dims, blk)
    assert all(np.isin(B[:, m], H[m]).all() for m in range(3))


def test_missing_null_is_no_claim():
    real = {"subs": {"lowrank": dict(status="OK", n_floats=50, XC=dict(interp=0.5, recomb=None, novel=None))}}
    marg = {"subs": {"lowrank": dict(status="OK", n_floats=50, XC=dict(interp=None, recomb=None, novel=None))}}
    assert completion(real, marg, "interp") == []
    marg2 = {"subs": {"lowrank": dict(status="OK", n_floats=50, XC=dict(interp=0.0, recomb=None, novel=None))}}
    assert completion(real, marg2, "interp")[0][0] == "lowrank"


def test_constant_and_tiny_never_fire():
    real = {"subs": {"lowrank": dict(status="OK", n_floats=4, XC=dict(interp=0.9, recomb=None, novel=None))}}
    marg = {"subs": {"lowrank": dict(status="OK", n_floats=4, XC=dict(interp=0.0, recomb=None, novel=None))}}
    assert completion(real, marg, "interp") == []


def test_intervention_support_and_constant_xc():
    g = planted("cp", (8, 8, 8), 2, 0.1, lifetime=600)
    st, life = experience(g, 9_990_001)
    c = collide(st, 51, 9_990_001, kinds=SIMPLE + ("cp",))
    for s in ("interp", "recomb", "novel"):
        v = c["subs"]["constant"]["XC"][s]
        assert v is None or v <= 1e-9                    # the constant is in the ladder: never positive
    const = make("constant", st["dims"], 51, np.random.default_rng(0))
    _, sup = intervene("ablate_half", const, st, np.arange(40), 51, 1, np.random.default_rng(0))
    assert not sup["changed"]
    m, _ = train("cp", st, 51, 5)
    _, sup = intervene("ablate_half", m, st, np.arange(40), 51, 1, np.random.default_rng(0))
    assert sup["changed"]
