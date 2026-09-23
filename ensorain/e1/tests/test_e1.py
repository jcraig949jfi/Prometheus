"""E1 unit tests and constitutional controls that need no campaign."""
import numpy as np
import pytest

from ensorain.e1.world import World1, N, NV, D
from ensorain.e1 import mem as M
from ensorain.e1.life import live
from ensorain.e1.arms import make
from ensorain.e0.tt import ranks_of_order


def test_world_true_rank_latent_order():
    w = World1(0, 3)
    order = tuple(int(i) for i in np.argsort(w.perm))
    assert ranks_of_order(w.x, order) == [3, 3, 3]


def test_heldout_never_observed_and_locks_typed():
    w = World1(0, 4)
    ev = w.events()
    ho = w.heldout_cell.reshape([NV] * D)
    kinds = {"obs": 0, "L1": 0, "L2": 0, "L3": 0}
    for e in ev:
        kinds[e[0]] += 1
        if e[0] == "obs":
            assert not ho[tuple(e[1].T)].any()
        if e[0] == "L2":
            assert ho[tuple(e[1])]
    assert all(kinds[k] > 20 for k in kinds)
    assert ho.mean() == pytest.approx(0.25)


def test_R_preserves_histogram_and_stream():
    c, r = World1(0, 5), World1(0, 5, lam=1.0)
    assert np.allclose(np.sort(c.x.reshape(-1)), np.sort(r.x.reshape(-1)))
    ec, er = c.events(), r.events()
    assert [e[0] for e in ec] == [e[0] for e in er]


def test_transplant_is_relabeled_same_factors():
    w, w2 = World1(0, 6), World1(0, 6, relabel_seed=123)
    assert np.allclose(np.sort(w.x.reshape(-1)), np.sort(w2.x.reshape(-1)))
    assert not np.allclose(w.x, w2.x)
    o2 = tuple(int(i) for i in np.argsort(w2.perm))
    assert ranks_of_order(w2.x, o2) == [3, 3, 3]


def test_inject_is_exact_at_192():
    w = World1(0, 7)
    m = M.inject_tt(w, 192)
    assert M.audit(m, 192) == 192
    p = m.predict_many(w.addr)
    assert np.allclose(p, w.x.reshape(-1), atol=1e-8)


def test_smuggler_refused():
    w = World1(0, 8)
    with pytest.raises(M.AuditError):
        live(w, make("SMUGGLER", 192, w, 0), w.events())


@pytest.mark.parametrize("arm,cap", [("CP", 192), ("LOWRANK", 192), ("MLP", 192), ("TT_OBS", 192),
                                     ("TT_LATENT", 192), ("LRU", 192), ("KNN", 128), ("CP", 96), ("MLP", 96)])
def test_arms_fit_cap_and_live(arm, cap):
    w = World1(0, 9)
    m = make(arm, cap, w, 0)
    assert M.audit(m, cap) <= cap
    r = live(w, m, w.events()[:200])
    assert r["P_used"] <= cap


def test_oracle_passes_every_lock():
    w = World1(0, 10)
    r = live(w, M.Oracle(0, w.x), w.events(), dict(energy0=1e9))
    assert r["ok_L1"] == r["n_L1"] and r["ok_L2"] == r["n_L2"]


def test_als_recovers_planted_tt_from_batch():
    """Machinery sanity: repeated consolidation on 2,000 samples, latent order, true ranks."""
    w = World1(0, 11)
    order = tuple(int(i) for i in np.argsort(w.perm))
    m = M.TTAls(192, order=order, ranks=(3, 3, 3), lam=1e-3, sweeps=10)
    rng = np.random.default_rng(0)
    cells = rng.choice(N, 2000, replace=False)
    A, y = w.addr[cells], w.x.reshape(-1)[cells]
    for _ in range(5):
        m.consolidate(A, y)
    p = m.predict_many(w.addr)
    xf = w.x.reshape(-1)
    assert 1 - ((xf - p) ** 2).sum() / ((xf - xf.mean()) ** 2).sum() > 0.95
