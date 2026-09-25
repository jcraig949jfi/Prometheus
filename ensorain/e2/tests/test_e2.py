import numpy as np
import pytest

from ensorain.e0.tt import ranks_of_order
from ensorain.e2.core import World2, H, ORDERS, FAMILIES, build, fit, val_mse, run_life, mech_sd, mech_exhaustive

CONSTS = {"TT": dict(lam=30, sweeps=20, init_scale=0.5), "LR": dict(lam=30, sweeps=10, init_scale=0.5),
          "CP": dict(lam=30, sweeps=10, init_scale=0.5), "disc_lam": 1.0}
ECON = dict(energy0=400.0, metabolism=0.5, reward=10.0, tau=0.15, kappa=5e-6, budget=3e7, scratch=128)


def test_h_space_is_17_and_each_world_has_exactly_one_correct():
    assert len(H) == 17 and len(ORDERS) == 12
    for fam in FAMILIES:
        w = World2(fam, 5)
        assert sum(w.correct(h) for h in H) == 1, fam


def test_structure_is_per_instance():
    perms = {tuple(World2("TT", i).perm) for i in range(8)}
    assert len(perms) > 3


def test_family_fields_have_their_structure():
    w = World2("TT", 3)
    assert ranks_of_order(w.x, w.correct_h()[1]) == [3, 3, 3]
    m = World2("MAT", 3)
    p = m.correct_h()[1]
    from ensorain.e1.mem import PARTITIONS
    (r0, r1), (c0, c1) = PARTITIONS[p]
    s = np.linalg.svd(np.transpose(m.x, (r0, r1, c0, c1)).reshape(64, 64), compute_uv=False)
    assert s[1] / s[0] < 1e-8
    n = World2("NONE", 3)
    assert min(ranks_of_order(n.x, (0, 1, 2, 3))) >= 8


def test_heldout_region_not_observed_in_every_family():
    for fam in FAMILIES:
        w = World2(fam, 6)
        ho = w.heldout_cell.reshape([8] * 4)
        for e in w.events():
            if e[0] == "obs":
                assert not ho[tuple(e[1].T)].any()


def test_oracle_h_learns_tt_world():
    r = run_life("TT", 7, "ORACLE_H", 0, CONSTS, ECON, 8e6)
    assert r["correct"] and r["r2_ho"] > 0.5


def test_mechanisms_respect_ceiling():
    w = World2("MAT", 8)
    rng = np.random.default_rng(0)
    A = w.addr[rng.choice(4096, 512, replace=False)]
    y = w.x.reshape(-1)[np.ravel_multi_index(A.T, [8] * 4)]
    for mech in (mech_sd, mech_exhaustive):
        h, u, _ = mech(A[:384], y[:384], A[384:], y[384:], CONSTS, 4e6, rng)
        assert u <= 4e6 and h in H


def test_blind_identification_is_not_free():
    hits = sum(run_life("CP", 100 + i, "BLIND1", 0, CONSTS, dict(ECON, energy0=1e9), 8e6)["correct"] for i in range(34))
    assert hits <= 8


def test_e1_proximal_default_unchanged():
    """The zero-ridge option is opt-in; E1 memories keep the proximal refit."""
    from ensorain.e1 import mem as M1
    m = M1.LowRank(192, R=1)
    assert getattr(m, "prox_zero", False) is False
    F = np.ones((3, 1)); y = np.zeros(3); g = np.array([2.0])
    assert M1._ridge(F, y, g, 1.0)[0] == pytest.approx(0.5)
    assert M1._ridge(F, y, g, 1.0, zero=True)[0] == pytest.approx(0.0)
