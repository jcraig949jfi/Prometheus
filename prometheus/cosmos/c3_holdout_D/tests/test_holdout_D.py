"""Unit tests (run as broker: COSMOS_BROKER=1 python -m pytest prometheus/cosmos/c3_holdout_D/tests): System contract, physics, knob API, grammar, selftest."""
import os
import subprocess
import sys

import numpy as np
import pytest

from prometheus.cosmos.c3.system import System, rollout
from prometheus.cosmos.c3.task import Task, batch
from prometheus.cosmos.c3_holdout_D import medium, selftest

W = selftest.DEMO


def pure(**ch):
    base = dict(W.as_dict(), D=0.0, v=0.0, p_decay=0.0, kappa=0.0, sigma=0.0)
    base.update(ch)
    return medium.build(**base)


def test_import_guard_refuses_without_broker():
    env = {k: v for k, v in os.environ.items() if k != "COSMOS_BROKER"}
    r = subprocess.run([sys.executable, "-c", "import prometheus.cosmos.c3_holdout_D"], env=env,
                       capture_output=True, text=True)
    assert r.returncode != 0 and "sealed holdout" in r.stderr


def test_system_contract_shapes():
    s = medium.ReactiveChannel(W)
    assert isinstance(s, System)
    E = 10
    st = s.init(E)
    assert set(st) == {"c"} and st["c"].shape == (E, W.L, W.V)
    nz = s.noise(E, np.random.default_rng(0))
    assert nz["xi"].shape == (E, W.L, W.V)
    st2 = s.step(st, np.arange(E) % (2 * W.V + 1), nz)
    assert st2["c"].shape == st["c"].shape and (st2["c"] >= 0).all()
    assert s.readout_features(st2).shape == (E, W.w_patch * W.V)
    assert s.full_state(st2).shape == (E, W.L * W.V)
    assert st["c"].sum() == 0                                   # step does not mutate its input


def test_step_is_a_function_of_state_obs_noise_only():
    s = medium.ReactiveChannel(W)
    st = s.init(6)
    nz = s.noise(6, np.random.default_rng(1))
    o = np.array([0, 1, 2, 3, 4, 6])
    a, b = s.step(st, o, nz), s.step(st, o, nz)
    assert np.array_equal(a["c"], b["c"])


def test_rows_are_independent():
    s = medium.ReactiveChannel(W)
    rng = np.random.default_rng(2)
    _c, obs = batch(W.task(), 8, rng)
    r_all = rollout(s, obs, np.random.default_rng(3))
    # row 0 alone with the SAME noise rows gives the same result
    rng3 = np.random.default_rng(3)
    st = s.init(1)
    for t in range(obs.shape[1]):
        nz = {k: v[:1] for k, v in s.noise(8, rng3).items()}
        st = s.step(st, obs[:1, t], nz)
    assert np.array_equal(s.full_state(st)[0], s.full_state(r_all["final"])[0])


def test_injection_species_mapping():
    s = pure()
    st = s.init(4)
    o = np.array([1, W.V + 1, 2 * W.V, 2 * W.V + 1])          # cue 1, distractor 1, query, hint
    c = s.step(st, o, s.noise(4, np.random.default_rng(0)))["c"]
    assert c[0, W.x_in, 1] == W.q and c[1, W.x_in, 1] == W.q
    assert c[2].sum() == 0 and c[3].sum() == 0


def test_advection_moves_centre_of_mass_v_sites_per_step_and_conserves_mass():
    s = pure(v=1.0)
    st = s.step(s.init(1), np.array([0]), {})
    for _ in range(3):
        st = s.step(st, np.array([2 * W.V]), {})
    m = st["c"][0, :, 0]
    assert m.sum() == pytest.approx(W.q)                         # upwind scheme: numerical spread, same mass
    assert (m * np.arange(W.L)).sum() / m.sum() == pytest.approx(W.x_in + 4 * 1.0)


def test_diffusion_conserves_mass_away_from_ends():
    s = pure(D=0.5, x_in=8, d_patch=0)
    st = s.step(s.init(1), np.array([0]), {})
    assert st["c"].sum() == pytest.approx(W.q)
    assert st["c"][0, 8, 0] < W.q and st["c"][0, 7, 0] > 0 and st["c"][0, 9, 0] > 0


def test_absorbing_end_loses_mass():
    s = pure(v=2.0, x_in=0, d_patch=0)
    st = s.init(1)
    st = s.step(st, np.array([0]), {})
    for _ in range(3 * W.L):
        st = s.step(st, np.array([2 * W.V]), {})
    assert st["c"].sum() < 1e-6 * W.q


def test_decay_and_annihilation():
    s = pure(p_decay=0.1)
    st = s.step(s.init(1), np.array([0]), {})
    assert st["c"].sum() == pytest.approx(0.9 * W.q)
    s = pure(kappa=0.5)
    st = s.step(s.init(1), np.array([0]), {})
    st = s.step(st, np.array([W.V + 1]), {})                    # unlike species at the same site
    assert st["c"].sum() < 2 * W.q
    s = pure(kappa=0.5)
    st = s.step(s.init(1), np.array([0]), {})
    st = s.step(st, np.array([W.V + 0]), {})                    # like species do not react
    assert st["c"].sum() == pytest.approx(2 * W.q)


def test_history_free_world_forgets_everything():
    ctrl = medium.ReactiveChannel(dict_to := medium.CONTROL_HISTORY_FREE)
    assert medium.in_lattice(dict_to) and dict_to.p_decay == 1.0
    z = {"xi": np.zeros((2, dict_to.L, dict_to.V))}
    st = ctrl.step(ctrl.init(2), np.array([0, 1]), z)
    assert st["c"].sum() == 0


def test_knob_api_ranges_and_intervene():
    s = medium.build(**W.as_dict())
    assert s.w == W
    w2 = medium.intervene(W, p_decay=0.5, v=2.5)
    assert w2.p_decay == 0.5 and w2.v == 2.5 and w2.L == W.L
    with pytest.raises(ValueError):
        medium.intervene(W, p_decay=1.5)
    with pytest.raises(ValueError):
        medium.intervene(W, k=3)
    with pytest.raises(ValueError):
        medium.intervene(W, d_patch=W.L)                       # patch outside the channel
    with pytest.raises(ValueError):
        medium.intervene(W, memory=1.0)
    with pytest.raises(ValueError):
        medium.build(V=3)
    for name, units, meaning, rng in medium.knob_table():
        assert units and meaning and rng[0] <= rng[1]


def test_substeps_keep_scheme_monotone():
    s = medium.build(**dict(W.as_dict(), D=2.0, v=3.0, p_decay=0.0, sigma=0.0, kappa=1.0))
    assert s.dt * (2 * 2.0 + 3.0) <= 0.8 + 1e-12
    _c, obs = batch(s.w.task(), 16, np.random.default_rng(4))
    r = rollout(s, obs, np.random.default_rng(5))
    assert np.isfinite(r["features"]).all() and (r["final"]["c"] >= 0).all()


def test_grammar_draw_respects_lattice_and_is_deterministic():
    a = medium.draw_worlds(50, np.random.default_rng(9))
    b = medium.draw_worlds(50, np.random.default_rng(9))
    assert a == b and all(medium.in_lattice(w) for w in a)
    assert all(w.k in (2, 4, 8) and w.V >= 2 for w in a)


def test_selftest_checks_and_defects_fail():
    r = selftest.run(with_certify=False)
    assert all(r["checks"].values())
    assert not any(r["negative_controls_must_be_false"].values())


def test_selftest_full_with_certify():
    r = selftest.run(with_certify=True)
    assert r["checks"]["history_free_certifies_NONE"] is True
    assert r["negative_controls_must_be_false"]["history_free_certifies_NONE[DefectShadowRegister]"] is False
    assert r["selftest_pass"] is True
