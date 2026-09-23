"""E0 unit tests + the constitutional controls that do not need a campaign."""
import itertools
import numpy as np
import pytest

from ensorain.e0.tt import TT, tt_svd, ranks_of_order, n_params_for_ranks
from ensorain.e0.world import World, D, NV, N, TRUE_RANK
from ensorain.e0 import memories as M
from ensorain.e0.life import live


def test_tt_eval_matches_full():
    rng = np.random.default_rng(1)
    t = TT([NV] * D, (2, 3, 1, 2, 2), order=(3, 1, 0, 5, 2, 4), rng=rng)
    full = t.full()
    for _ in range(50):
        a = tuple(rng.integers(NV, size=D))
        assert abs(full[a] - t.eval(a)) < 1e-10
    assert t.n_params() == n_params_for_ranks((2, 3, 1, 2, 2), [NV] * D)


def test_tt_update_reduces_error():
    rng = np.random.default_rng(2)
    t = TT([NV] * D, (2,) * 5, rng=rng)
    a = (1, 2, 3, 0, 1, 2)
    e0 = abs(t.update(a, 5.0, 0.5))
    e1 = abs(5.0 - t.eval(a))
    assert e1 < e0 * 0.9
    for _ in range(30):
        t.update(a, 5.0, 0.5)
    assert abs(5.0 - t.eval(a)) < 0.05


def test_tt_svd_roundtrip_and_true_rank():
    w = World(0, 5, lam=0.0)
    dense = w.dense_obs()
    latent_order = tuple(np.argsort(w.perm))
    assert ranks_of_order(dense, latent_order) == [TRUE_RANK] * (D - 1)
    cores, ranks = tt_svd(np.transpose(dense, latent_order), tol=1e-10)
    t = cores[0]
    for c in cores[1:]:
        t = np.tensordot(t, c, axes=([-1], [0]))
    assert np.allclose(t.reshape(dense.shape), np.transpose(dense, latent_order))


def test_scramble_raises_rank():
    w = World(0, 5)
    dense = w.dense_obs()
    observed = ranks_of_order(dense, tuple(range(D)))
    assert max(observed) > TRUE_RANK  # the observed order is not the physics


def test_R_preserves_histogram_and_graph():
    c, r = World(0, 7, lam=0.0), World(0, 7, lam=1.0)
    assert np.allclose(np.sort(c.x), np.sort(r.x))
    assert all(np.array_equal(a, b) for a, b in zip(c.exits, r.exits))
    assert not np.allclose(c.x, r.x)
    # R destroys low rank in every order we probe
    dense = r.dense_obs()
    assert min(ranks_of_order(dense, tuple(np.argsort(r.perm)))[1:4]) > 10


def test_audit_refuses_smuggler():
    mem = M.CheatSmuggler(168)
    M.audit(mem, 168)  # clean at birth
    mem.observe((0,) * D, 1.0)
    with pytest.raises(M.AuditError):
        M.audit(mem, 168)


def test_live_refuses_smuggler_midlife():
    w = World(0, 3)
    with pytest.raises(M.AuditError):
        live(w, M.CheatSmuggler(168), 168, seed=0)


def test_audit_refuses_over_cap():
    mem = M.TTMem(400)
    with pytest.raises(M.AuditError):
        M.audit(mem, 168)


def test_audit_counts_buffer():
    mem = M.TTMem(168, buf_frac=0.5, replay=1)
    used = M.audit(mem, 168)
    assert used <= 168 and mem.buf_n > 0


def test_every_capped_arm_passes_audit():
    for cap in (48, 96, 168, 384):
        for mk in (M.LRU, M.KNN, M.Hash, M.Additive, M.RF, M.TTMem):
            M.audit(mk(cap), cap)
        if cap >= 128:
            M.audit(M.LowRank(cap), cap)


def test_life_runs_and_oracle_beats_random():
    w = World(0, 11)
    o = live(w, M.Oracle(0, w.x), 0, seed=1, econ=dict(theta=0.0))
    n = live(w, M.NoMem(0), 0, seed=1, econ=dict(epsilon=1.0, theta=0.0))
    assert o["harvest"] > n["harvest"]
