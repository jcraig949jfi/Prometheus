"""Boundary sampler under a LIMITED query budget, against its baselines.

The private oracle labels every pool world (for scoring only). A strategy sees only
the rows it paid for through `Budget.query`. Strategies:
  random       uniform draws from the pool
  grid         greedy maximin (space-filling) in the feature space
  boundary     bisection: the pool point nearest the midpoint of an opposite-label pair
  active       uncertainty sampling on a kernel classifier + 20% exploration
Features for choosing (not for the law): z = (log10 C, N, log2(1+K), G), fixed scaling.
eta = balanced accuracy of the law mined from the queried rows, on the oracle pool, per query.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List

import numpy as np

SCALE = np.array([1.0, 1.0, 1.0, 4.0])


def feats(coords_list: List[Dict[str, float]]) -> np.ndarray:
    Z = np.array([[np.log10(max(c["C"], 1e-9)), min(c["N"], 6.0), np.log2(1 + c["K"]), c["G"]] for c in coords_list])
    return Z * SCALE


class Budget:
    """Pool + private labels; strategies pay per query and never see unqueried labels."""

    def __init__(self, pool: Dict[str, List[Dict[str, Any]]], oracle: Dict[str, List[Dict[str, Any]]], per_family: int):
        self.pool = pool
        self._oracle = oracle
        self.per_family = per_family
        self.spent = {f: 0 for f in pool}
        self.seen: Dict[str, List[int]] = {f: [] for f in pool}

    def query(self, fam: str, i: int) -> Dict[str, Any]:
        if self.spent[fam] >= self.per_family:
            raise RuntimeError("budget exhausted for " + fam)
        if i in self.seen[fam]:
            raise RuntimeError("duplicate query")
        self.spent[fam] += 1
        self.seen[fam].append(i)
        return self._oracle[fam][i]

    def rows(self) -> List[Dict[str, Any]]:
        return [self._oracle[f][i] for f in self.pool for i in self.seen[f]]

    def left(self, fam: str) -> int:
        return self.per_family - self.spent[fam]


def _unseen(b: Budget, fam: str) -> np.ndarray:
    m = np.ones(len(b.pool[fam]), bool)
    m[b.seen[fam]] = False
    return np.nonzero(m)[0]


def run_random(b: Budget, rng) -> None:
    for f in b.pool:
        for i in rng.choice(_unseen(b, f), b.left(f), replace=False):
            b.query(f, int(i))


def run_grid(b: Budget, rng) -> None:
    for f in b.pool:
        Z = feats([r["coords"] for r in b.pool[f]])
        first = int(rng.integers(len(Z)))
        b.query(f, first)
        d = np.linalg.norm(Z - Z[first], axis=1)
        while b.left(f):
            d[b.seen[f]] = -1
            j = int(d.argmax())
            b.query(f, j)
            d = np.minimum(d, np.linalg.norm(Z - Z[j], axis=1))


def _seed(b: Budget, rng, n: int) -> None:
    for f in b.pool:
        for i in rng.choice(_unseen(b, f), min(n, b.left(f)), replace=False):
            b.query(f, int(i))


def run_boundary(b: Budget, rng, n_seed: int = 12) -> None:
    _seed(b, rng, n_seed)
    for f in b.pool:
        Z = feats([r["coords"] for r in b.pool[f]])
        tries = 0
        while b.left(f) and tries < 10000:
            tries += 1
            seen = b.seen[f]
            ys = np.array([b._oracle[f][i]["y"] for i in seen])     # labels of PAID rows only
            pos, neg = [seen[k] for k in np.nonzero(ys == 1)[0]], [seen[k] for k in np.nonzero(ys == 0)[0]]
            un = _unseen(b, f)
            if not pos or not neg:
                b.query(f, int(rng.choice(un)))
                continue
            a, c = int(rng.choice(pos)), int(rng.choice(neg))
            mid = (Z[a] + Z[c]) / 2
            j = un[np.linalg.norm(Z[un] - mid, axis=1).argmin()]
            b.query(f, int(j))


def run_active(b: Budget, rng, n_seed: int = 12, batch: int = 4, h: float = 0.35, explore: float = 0.2) -> None:
    _seed(b, rng, n_seed)
    while any(b.left(f) for f in b.pool):
        rows = b.rows()
        Zs = feats([r["coords"] for r in rows])
        ys = np.array([r["y"] for r in rows], float)
        for f in b.pool:
            for _ in range(min(batch, b.left(f))):
                un = _unseen(b, f)
                if rng.random() < explore:
                    b.query(f, int(rng.choice(un)))
                    continue
                Zp = feats([b.pool[f][i]["coords"] for i in un])
                d2 = ((Zp[:, None, :] - Zs[None, :, :]) ** 2).sum(-1)
                w = np.exp(-d2 / (2 * h * h))
                p = (w @ ys + 0.5) / (w.sum(1) + 1.0)
                u = 1 - 2 * np.abs(p - 0.5)
                j = int(un[u.argmax()])
                r = b.query(f, j)
                Zs = np.vstack([Zs, feats([r["coords"]])])
                ys = np.append(ys, r["y"])


STRATEGIES: Dict[str, Callable] = {"random": run_random, "grid": run_grid, "boundary": run_boundary, "active": run_active}


def knn_ba(train: List[Dict[str, Any]], test: List[Dict[str, Any]], k: int = 5) -> float:
    Zt, yt = feats([r["coords"] for r in train]), np.array([r["y"] for r in train])
    Zq, yq = feats([r["coords"] for r in test]), np.array([r["y"] for r in test])
    d = ((Zq[:, None, :] - Zt[None, :, :]) ** 2).sum(-1)
    nn = np.argsort(d, axis=1)[:, :k]
    pred = yt[nn].mean(1) >= 0.5
    return 0.5 * ((pred & (yq == 1)).sum() / max(1, (yq == 1).sum()) + (~pred & (yq == 0)).sum() / max(1, (yq == 0).sum()))
