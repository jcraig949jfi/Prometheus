"""W2-I common machinery for the hop-matched topology transplants. CPU only, 2 threads.

Import BEFORE torch anywhere. Nothing here modifies prometheus/ananke; graph variants are
applied by temporarily overriding topology.build (used by engine.World) and envs.dist_matrix
(used by envs.build for sensor/actuator placement) inside a context manager, then restoring.
"""
from __future__ import annotations

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"

import contextlib
import dataclasses
import gzip
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

torch.set_num_threads(2)
assert not torch.cuda.is_available(), "GPU visible; refusing"

from prometheus.ananke import assays, envs, topology  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
NS = 0x57324749          # "W2GI": this worker's seed namespace
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
_R = None


def rows():
    global _R
    if _R is None:
        _R = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _R


def by8():
    return {r["cell_id"][:8]: r for r in rows()}


def load(cid8):
    r = by8()[cid8]
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    if "champion" in r["result"]:
        g = np.asarray(r["result"]["champion"], dtype=np.int64)
    else:
        g = np.asarray(r["extra"]["genome"], dtype=np.int64)
    g = g.reshape(ph.rules, ph.prog_len, 5)
    return r, ph, env, g


def hop_matched_d(ph: Physics, env) -> int:
    """Hops the native task needed: ceil(d/r) on ring/torus, d on BFS graphs, 1 on global."""
    if ph.topology in ("ring", "torus"):
        return max(1, math.ceil(env.d / ph.radius))
    if ph.topology == "global":
        return 1
    return env.d


def c1_random(ph: Physics) -> Physics:
    """Exactly the D-wave transplant (campaign.py transplant_battery)."""
    return ph.replace(topology="random", k_random=max(3, ph.table_width())).validate()


# ------------------------------------------------------------- graph variants
def bfs_all(nbr: np.ndarray) -> np.ndarray:
    """M[s, t] = directed BFS hops s -> t over the table (10**6 if unreachable)."""
    N = nbr.shape[0]
    M = np.full((N, N), 10 ** 6, dtype=np.int64)
    for s in range(N):
        M[s, s] = 0
        fr = [s]
        k = 0
        while fr:
            k += 1
            nx = []
            for u in fr:
                for v in nbr[u]:
                    if M[s, v] > k:
                        M[s, v] = k
                        nx.append(int(v))
            fr = nx
    return M


def ring_tables(N, r):
    offs = list(range(-r, 0)) + list(range(1, r + 1))
    nbr = np.array([[(n + o) % N for o in offs] for n in range(N)], dtype=np.int64)
    dist = np.array([[abs(o) for o in offs] for _ in range(N)], dtype=np.int64)
    return nbr, dist


def schreier_tables(N, r, seed):
    """Undirected random graph with the RING'S PORT ALGEBRA: r random Hamiltonian-cycle
    successor maps s_1..s_r; ports ordered [s_r^-1 .. s_1^-1, s_1 .. s_r] exactly like the
    ring's offsets [-r..-1, 1..r] (port j and port 2r-1-j are inverses), with the ring's
    per-port distance labels |offset| (latency/loss semantics). Only the commutative
    lattice structure (s_1 s_1 = s_2, short cycles, clustering) is destroyed."""
    g = np.random.default_rng(seed)
    succ = []
    for k in range(r):
        order = g.permutation(N)
        s = np.empty(N, dtype=np.int64)
        s[order] = np.roll(order, -1)
        succ.append(s)
    inv = [np.argsort(s) for s in succ]
    cols = [inv[k] for k in reversed(range(r))] + [succ[k] for k in range(r)]
    nbr = np.stack(cols, 1)
    dist = np.array([[k for k in range(r, 0, -1)] + [k for k in range(1, r + 1)]] * N, dtype=np.int64)
    dup = int(sum(len(set(row)) < len(row) for row in nbr))
    return nbr, dist, dup


def variant(ph: Physics, name: str, seed: int):
    """Return (physics_to_use, nbr, dist, M_env, info) or a native marker.
    Only ring physics are supported for the factorial variants."""
    assert ph.topology == "ring", ph.topology
    N, r = ph.n_sites, ph.radius
    nbr, dist = ring_tables(N, r)
    i = np.arange(N)
    dd = np.abs(i[:, None] - i[None, :])
    Mring = np.minimum(dd, N - dd).astype(np.int64)
    info = {}
    if name == "ring_native_patched":          # identity patch: proves the override path is exact
        return ph, nbr, dist, Mring, info
    if name == "ring_relabel":                  # isomorphic ring, labels permuted (null control)
        p = np.random.default_rng(seed).permutation(N)
        nbr2 = np.empty_like(nbr)
        nbr2[p] = p[nbr]
        M2 = np.empty_like(Mring)
        M2[np.ix_(p, p)] = Mring
        return ph, nbr2, dist.copy(), M2, info
    if name == "ring_portshuffle":              # same adjacency/geometry, per-node random port order
        g = np.random.default_rng(seed)
        nbr2, dist2 = nbr.copy(), dist.copy()
        for n in range(N):
            q = g.permutation(nbr.shape[1])
            nbr2[n], dist2[n] = nbr[n, q], dist[n, q]
        return ph, nbr2, dist2, Mring, info
    if name == "ring_flatdist":                 # same adjacency/ports, every port dist=1 (latency/loss)
        return ph, nbr, np.ones_like(dist), Mring, info
    if name in ("schreier_ringdist", "schreier_flatdist"):
        nb, ds, dup = schreier_tables(N, r, seed)
        if name == "schreier_flatdist":
            ds = np.ones_like(ds)
        info["nodes_with_duplicate_port"] = dup
        return ph, nb, ds, bfs_all(nb), info
    if name == "clique2x4_flatdist":
        # clustered but NON-lattice: every site is in two random K4s (two random partitions
        # of the sites into groups of 4), degree 6 like ring r3, clustering .4 (ring r3: .6),
        # no ordering, no offsets, every port dist 1
        assert r == 3 and N % 4 == 0
        g = np.random.default_rng(seed)
        nb = [[] for _ in range(N)]
        for _ in range(2):
            perm = g.permutation(N)
            for q in range(0, N, 4):
                grp = perm[q:q + 4]
                for u in grp:
                    nb[u] += [int(v) for v in grp if v != u]
        nb = np.array(nb, dtype=np.int64)
        info["nodes_with_duplicate_port"] = int(sum(len(set(row)) < len(row) for row in nb))
        return ph, nb, np.ones_like(nb), bfs_all(nb), info
    raise ValueError(name)


@contextlib.contextmanager
def patched(nbr, dist, M):
    """Temporarily replace the neighbour table (engine) and env distance (placement)."""
    ob, od = topology.build, envs.dist_matrix
    topology.build = lambda ph: (nbr, dist)
    envs.dist_matrix = lambda ph: M
    try:
        yield
    finally:
        topology.build, envs.dist_matrix = ob, od


@contextlib.contextmanager
def inward_placement(ph):
    """For MAJ, envs.build places sensors at M[a, s] == d, i.e. OUT-distance from the
    actuator. Signal flows s -> a, so on a directed graph the hop count that matters is
    M[s, a]. Transpose the env distance so placement uses the signal direction."""
    od = envs.dist_matrix
    M = od(ph)
    envs.dist_matrix = lambda p: M.T.copy()
    try:
        yield
    finally:
        envs.dist_matrix = od


# ------------------------------------------------------------------ scoring
def seeds_for(tag: int, M: int = 64):
    return assays.world_seeds(H_int(NS, tag), M)


def score(ph, G, env, seeds, ctrl=None):
    """G [P, rules, L, 5] -> list of dicts (acc, lo99, hi99) per genome."""
    er = assays.evaluate(ph, G, env, seeds, ctrl=ctrl, device="cpu", graph=False)
    pa = er.pair_acc()
    out = []
    for p in range(G.shape[0]):
        m, lo, hi = assays.pair_ci(pa[p])
        out.append({"acc": round(float(m), 4), "lo99": round(float(lo), 4), "hi99": round(float(hi), 4)})
    return out


def signal_hops(ph, env, seeds, nbr=None):
    """Hop count in the SIGNAL direction (sensor -> actuator) for each placed sensor."""
    ep = envs.build(ph, env, seeds)
    if nbr is None:
        nbr, _ = topology.build(ph)
    if nbr is None:
        return {"1": int(ep.schedule.sense_idx.numel())}
    Mh = bfs_all(nbr)
    s = ep.schedule.sense_idx.numpy()
    a = ep.schedule.read_idx.numpy()[:, 0]
    fam = env.family
    K = {"RELAY": 1, "MAJ": s.shape[1], "HOLD": 1, "FLIP": 1, "XOR": 2}[fam]
    h = []
    for b in range(len(seeds)):
        for k in range(K):
            h.append(int(Mh[s[b, k], a[b]]))
    vals, cnt = np.unique(h, return_counts=True)
    return {str(int(v)): int(c) for v, c in zip(vals, cnt)}
