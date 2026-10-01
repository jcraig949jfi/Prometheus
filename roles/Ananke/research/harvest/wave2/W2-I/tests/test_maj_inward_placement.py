"""Regression test for W2-I/patches/envs_maj_inward_placement.diff.

envs.build places MAJ sensors with _pick_at(g, M[a], d): OUT-distance from the actuator. The MAJ
signal flows sensor -> actuator, so on a directed graph (C1 'random'; 'smallworld' after one-sided
rewiring) the sensors are usually farther than d hops upstream (C1 random d=1: >90% of sensors).
The patch places by M[:, a] (hops INTO the actuator).
- test_current_code_places_by_signal_hops is xfail(strict): it FAILS on prometheus/ananke/envs.py.
- the same check PASSES on the patched copy (patches/envs_patched.py, loaded inside the package).
- on symmetric metrics (ring) the patch is byte-identical, so no C1 ring/torus/global row changes.
Run: python -m pytest roles/Ananke/research/harvest/wave2/W2-I/tests -q
"""
import importlib.util
import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
HERE = pathlib.Path(__file__).resolve().parents[1]
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pytest  # noqa: E402

from prometheus.ananke import envs as envs_orig  # noqa: E402
from prometheus.ananke import topology  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402


def _load_patched():
    spec = importlib.util.spec_from_file_location("prometheus.ananke.envs_w2i_patched",
                                                  HERE / "patches/envs_patched.py")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "prometheus.ananke"
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


envs_patched = _load_patched()
SEEDS = list(range(5000, 5032))
RND = Physics(topology="random", n_sites=100, k_random=6, topo_seed=12345, channels=1,
              fanout=8, radius=3).validate()
RING = Physics(topology="ring", n_sites=100, radius=3, channels=1, fanout=8).validate()


def _upstream_hops(mod, ph, d):
    env = mod.EnvSpec(family="MAJ", d=d, trials=12, block=4, delta=8)
    ep = mod.build(ph, env, SEEDS)
    nbr, _ = topology.build(ph)
    s = ep.schedule.sense_idx.numpy()
    a = ep.schedule.read_idx.numpy()[:, 0]
    out = []
    for b in range(len(SEEDS)):
        dist_into_a = np.stack([topology.graph_distances(ph, int(x)) for x in s[b]])[:, a[b]]
        out += list(dist_into_a)
    return np.array(out)


def _check(mod):
    h = _upstream_hops(mod, RND, 1)
    # actuators with in-degree < 5 force fallbacks; require the large majority at exactly 1 hop
    assert np.mean(h == 1) >= 0.7, np.unique(h, return_counts=True)


@pytest.mark.xfail(strict=True, reason="current envs.build places MAJ sensors by OUT-distance")
def test_current_code_places_by_signal_hops():
    _check(envs_orig)


def test_patched_code_places_by_signal_hops():
    _check(envs_patched)


def test_patch_is_identity_on_symmetric_metric():
    env = envs_orig.EnvSpec(family="MAJ", d=3, trials=12, block=4, delta=8)
    a = envs_orig.build(RING, env, SEEDS).schedule
    b = envs_patched.build(RING, env, SEEDS).schedule
    for x, y in ((a.sense_idx, b.sense_idx), (a.sense_val, b.sense_val), (a.read_idx, b.read_idx)):
        assert np.array_equal(x.numpy(), y.numpy())
