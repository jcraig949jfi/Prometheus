"""W2-A1 test for patches/SEMANTIC_envs_maj_forward_placement.diff (SEMANTIC: changes episodes on
directed graphs only; for C2, never for frozen C1/C1b material).

envs.build places MAJ sensors with _pick_at(g, M[a], d): M[a] is BFS distance FROM the actuator over the
directed out-edge table, but packets travel sensor -> actuator (M[s, a]). On random topology only ~18% of
MAJ sensors sit at transport distance d, and ~3% of worlds have an actuator that no sensor can reach.
The first two tests FAIL on current code and PASS with the patch; the golden test passes on both
(ring/torus/global episodes are bit-identical). Package root: env W2A1_PKG_ROOT."""
from __future__ import annotations

import hashlib
import os
import pathlib
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
WT = pathlib.Path(__file__).resolve().parents[7]
PKG = pathlib.Path(os.environ.get("W2A1_PKG_ROOT", str(WT)))
if not PKG.is_absolute():
    PKG = WT / PKG
sys.path.insert(0, str(PKG))

import numpy as np  # noqa: E402

from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

UNREACH = 10 ** 6


def _maj_worlds(k_random, d, n=64, B=64, topo_seed=7):
    ph = Physics(topology="random", n_sites=n, k_random=k_random, topo_seed=topo_seed)
    M = envs.dist_matrix(ph)
    ep = envs.build(ph, envs.EnvSpec(family="MAJ", d=d, delta=4, trials=4), assays.world_seeds(5, B))
    a = ep.schedule.read_idx[:, 0].numpy()
    s = ep.schedule.sense_idx.numpy()
    return M, a, s


def test_maj_sensors_at_transport_distance_d():
    hit = tot = 0
    for d in (1, 2):
        for k in (3, 6):
            M, a, s = _maj_worlds(k, d)
            for b in range(len(a)):
                if (M[:, a[b]] == d).sum() >= s.shape[1]:          # enough sites at transport distance d
                    hit += int((M[s[b], a[b]] == d).sum())
                    tot += s.shape[1]
    assert tot > 0 and hit == tot, f"{hit}/{tot} sensors at transport distance d"


def test_maj_actuator_reachable_from_every_sensor():
    for k in (3,):
        for seed in range(4):
            M, a, s = _maj_worlds(k, 1, topo_seed=seed, B=128)
            assert (M[s, a[:, None]] < UNREACH).all()


GOLDEN = "6d106abafb245c54"   # frozen code, ring/torus/global x 5 families x d in {1,3,5}


def test_symmetric_topologies_bit_identical_to_frozen():
    out = {}
    for topo, n in (("ring", 64), ("torus", 100), ("global", 64)):
        ph = Physics(topology=topo, n_sites=n, radius=2)
        for fam in envs.FAMILIES:
            for d in (1, 3, 5):
                ep = envs.build(ph, envs.EnvSpec(family=fam, d=d, delta=4, trials=16, block=4),
                                assays.world_seeds(31, 16))
                h = hashlib.sha256()
                for x in (ep.schedule.sense_idx.numpy(), ep.schedule.sense_val.numpy(),
                          ep.schedule.read_idx.numpy(), ep.y, ep.ro_tick, ep.scored):
                    h.update(x.tobytes())
                out[f"{topo}/{fam}/{d}"] = h.hexdigest()[:16]
    assert hashlib.sha256(repr(sorted(out.items())).encode()).hexdigest()[:16] == GOLDEN
