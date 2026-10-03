"""Neighbour tables (DESIGN.md s3). Built on the host once per physics."""
from __future__ import annotations

import numpy as np

from .physics import Physics
from .rng import H_int, INIT


def build(ph: Physics):
    """Return (nbr[N,R], dist[N,R]) int64 arrays, or (None, None) for global."""
    N = ph.n_sites
    if ph.topology == "global":
        return None, None
    if ph.topology == "ring":
        offs = list(range(-ph.radius, 0)) + list(range(1, ph.radius + 1))
        nbr = np.array([[(n + o) % N for o in offs] for n in range(N)], dtype=np.int64)
        dist = np.array([[abs(o) for o in offs] for _ in range(N)], dtype=np.int64)
        return nbr, dist
    if ph.topology == "torus":
        return _torus(ph.side, ph.radius)
    if ph.topology == "random":
        k = ph.k_random
        nbr = np.array([[(n + 1 + H_int(ph.topo_seed, INIT, 0, n, j) % (N - 1)) % N
                         for j in range(k)] for n in range(N)], dtype=np.int64)
        return nbr, np.ones((N, k), dtype=np.int64)
    if ph.topology == "smallworld":
        nbr, dist = _torus(ph.side, 1)
        nbr = nbr.copy()
        dist = dist.copy()
        for n in range(N):
            for j in range(nbr.shape[1]):
                if H_int(ph.topo_seed, INIT, 1, n, j) % 1000 < ph.rewire:
                    nbr[n, j] = (n + 1 + H_int(ph.topo_seed, INIT, 2, n, j) % (N - 1)) % N
                    dist[n, j] = 1
        return nbr, dist
    raise ValueError(ph.topology)


def _torus(s: int, r: int):
    offs = [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1)
            if 1 <= abs(dx) + abs(dy) <= r]
    N = s * s
    nbr = np.empty((N, len(offs)), dtype=np.int64)
    dist = np.empty((N, len(offs)), dtype=np.int64)
    for n in range(N):
        y, x = divmod(n, s)
        for j, (dx, dy) in enumerate(offs):
            nbr[n, j] = ((y + dy) % s) * s + (x + dx) % s
            dist[n, j] = abs(dx) + abs(dy)
    return nbr, dist


def graph_distances(ph: Physics, src: int) -> np.ndarray:
    """BFS hop distance from src over the (directed) table; global: 1 everywhere."""
    N = ph.n_sites
    nbr, _ = build(ph)
    if nbr is None:
        d = np.ones(N, dtype=np.int64)
        d[src] = 0
        return d
    d = np.full(N, -1, dtype=np.int64)
    d[src] = 0
    frontier = [src]
    while frontier:
        nxt = []
        for u in frontier:
            for v in nbr[u]:
                if d[v] < 0:
                    d[v] = d[u] + 1
                    nxt.append(int(v))
        frontier = nxt
    return d
