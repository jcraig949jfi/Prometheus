"""Lane C (BRAIN) C4/C5: brain genome families for lane E's population-batched QD.

Interface matches primordial/qd/e5_run.py (lane E): a genome batch g is a tuple of
float32 arrays with a leading population axis P; forward(g, obs[n,D], gidx[n]) returns
the action index per row. The action codebook stays on E's side.

Every family has independent implementations:
  forward       population-batched numpy float32 (lane E's E5 style)
  forward_fast  C5: numba kernel over rows, per-row genome index, chunked prange
  ref_logits    one genome, one row at a time, float64, plain loops (the brain oracle)
and pack/unpack to little-endian bytes, so a genome's charge is its byte length
(always a multiple of 4: E's archive pads to 4).

Families, smallest first (D = obs features, A = actions):
  linear     W [D,A], b [A]                        logits = (x/65535 - 0.5) W + b
  lut_top    T [D,16,A]                            logits = sum_f T[f, top_digit(x_f)]
  tt_feat    alpha [r], G [D,16,r,r], Wo [r,A]     TT over features, physical index = top digit
  tt_digits  alpha [r], G [4D,16,r,r], Wo [r,A]    lane E's E5 baseline (all 4 hex digits per feature)
"""
from __future__ import annotations

import numpy as np

from primordial.brain.tt_policy import digits

try:
    from numba import prange
except ImportError:  # pragma: no cover
    prange = range


# ------------------------------------------------------------------ C5 numba kernels

def _tt_rows(idx, gidx, al, G, Wo, out, nchunks, stride):
    n, C = idx.shape
    r = al.shape[1]
    A = Wo.shape[2]
    step = (n + nchunks - 1) // nchunks
    for ch in prange(nchunks):
        lo = ch * step
        hi = min(n, lo + step)
        v = np.empty(r, dtype=np.float32)
        u = np.empty(r, dtype=np.float32)
        for i in range(lo, hi):
            p = gidx[i]
            for a in range(r):
                v[a] = al[p, a]
            for c in range(0, C, stride):
                x = idx[i, c]
                m = np.float32(0.0)
                for b in range(r):
                    s = np.float32(0.0)
                    for a in range(r):
                        s += v[a] * G[p, c, x, a, b]
                    u[b] = s
                    if abs(s) > m:
                        m = abs(s)
                if m < np.float32(1e-30):
                    m = np.float32(1e-30)
                for b in range(r):
                    v[b] = u[b] / m
            best = 0
            bv = -np.inf
            for k in range(A):
                s2 = 0.0
                for b in range(r):
                    s2 += v[b] * Wo[p, b, k]
                if s2 > bv:
                    bv = s2
                    best = k
            out[i] = best


def _lut_rows(top, gidx, T, out, nchunks, stride):
    n, D = top.shape
    A = T.shape[3]
    step = (n + nchunks - 1) // nchunks
    for ch in prange(nchunks):
        lo = ch * step
        hi = min(n, lo + step)
        for i in range(lo, hi):
            p = gidx[i]
            best = 0
            bv = -np.inf
            for k in range(A):
                s = 0.0
                for f in range(0, D, stride):
                    s += T[p, f, top[i, f], k]
                if s > bv:
                    bv = s
                    best = k
            out[i] = best


_KERNELS = {}


def _kernel(fn, parallel: bool):
    key = (fn.__name__, parallel)
    if key not in _KERNELS:
        import numba
        _KERNELS[key] = numba.njit(parallel=parallel, nogil=True, boundscheck=False)(fn)
    return _KERNELS[key]


# ------------------------------------------------------------------ families

class Family:
    name = ""

    def __init__(self, D: int, A: int = 8):
        self.D, self.A = D, A

    def shapes(self) -> list[tuple]:
        raise NotImplementedError

    @property
    def nf(self) -> int:
        return int(sum(np.prod(s) for s in self.shapes()))

    @property
    def nbytes(self) -> int:
        return self.nf * 4

    def init(self, rng, P: int):
        return tuple(rng.standard_normal((P,) + s).astype(np.float32) for s in self.shapes())

    def mutate(self, rng, g, rate: float = 0.05, sigma: float = 0.2):
        out = []
        for x in g:
            m = rng.random(x.shape) < rate
            out.append((x + m * sigma * rng.standard_normal(x.shape)).astype(np.float32))
        return tuple(out)

    def pack(self, g) -> np.ndarray:
        P = len(g[0])
        return np.concatenate([x.reshape(P, -1) for x in g], 1).astype("<f4").view(np.uint8).reshape(P, self.nbytes)

    def unpack(self, B: np.ndarray):
        P = len(B)
        f = np.ascontiguousarray(B).view("<f4").reshape(P, self.nf)
        out, off = [], 0
        for s in self.shapes():
            n = int(np.prod(s))
            out.append(f[:, off:off + n].reshape((P,) + s).copy())
            off += n
        return tuple(out)

    def forward(self, g, obs, gidx, cheat: bool = False) -> np.ndarray:
        return self.logits(g, obs, gidx, cheat).argmax(1)

    def forward_fast(self, g, obs, gidx, cheat: bool = False, parallel: bool = False, nchunks: int = 0) -> np.ndarray:
        return self.forward(g, obs, gidx, cheat)

    def one(self, g, p: int):
        return tuple(x[p] for x in g)


class Linear(Family):
    name = "linear"

    def shapes(self):
        return [(self.D, self.A), (self.A,)]

    def logits(self, g, obs, gidx, cheat=False):
        W, b = g
        xs = obs.astype(np.float32) / 65535.0 - 0.5
        if cheat:
            xs[:, 1::2] = 0.0
        return np.einsum("nd,nda->na", xs, W[gidx]) + b[gidx]

    def ref_logits(self, g1, obs):
        W, b = (x.astype(np.float64) for x in g1)
        out = np.zeros((len(obs), self.A))
        for i, row in enumerate(obs):
            for a in range(self.A):
                s = float(b[a])
                for f in range(self.D):
                    s += (int(row[f]) / 65535.0 - 0.5) * float(W[f, a])
                out[i, a] = s
        return out


class LutTop(Family):
    name = "lut_top"

    def shapes(self):
        return [(self.D, 16, self.A)]

    def logits(self, g, obs, gidx, cheat=False):
        (T,) = g
        top = (obs.astype(np.int64) >> 12) & 15
        feats = np.arange(0, self.D, 2 if cheat else 1)
        return T[gidx[:, None], feats[None, :], top[:, feats]].sum(1)

    def forward_fast(self, g, obs, gidx, cheat=False, parallel=False, nchunks=0):
        (T,) = g
        top = np.ascontiguousarray((obs.astype(np.int64) >> 12) & 15)
        out = np.empty(len(obs), np.int64)
        _kernel(_lut_rows, parallel)(top, np.ascontiguousarray(gidx, np.int64), T, out,
                                     nchunks or (24 if parallel else 1), 2 if cheat else 1)
        return out

    def ref_logits(self, g1, obs):
        (T,) = g1
        out = np.zeros((len(obs), self.A))
        for i, row in enumerate(obs):
            for f in range(self.D):
                out[i] += T[f, (int(row[f]) >> 12) & 15].astype(np.float64)
        return out


class _TT(Family):
    rank = 3

    def n_cores(self):
        raise NotImplementedError

    def index(self, obs):
        raise NotImplementedError

    def shapes(self):
        r = self.rank
        return [(r,), (self.n_cores(), 16, r, r), (r, self.A)]

    def init(self, rng, P):
        r = self.rank
        al = rng.standard_normal((P, r)).astype(np.float32)
        G = (np.eye(r, dtype=np.float32) + 0.3 * rng.standard_normal((P, self.n_cores(), 16, r, r))).astype(np.float32)
        Wo = rng.standard_normal((P, r, self.A)).astype(np.float32)
        return al, G, Wo

    def logits(self, g, obs, gidx, cheat=False):
        al, G, Wo = g
        idx = self.index(obs)
        v = al[gidx]
        for c in range(idx.shape[1]):
            if cheat and c % 2:
                continue
            v = np.einsum("nr,nrs->ns", v, G[gidx, c, idx[:, c]])
            v /= np.maximum(np.abs(v).max(1, keepdims=True), 1e-30)   # argmax is scale invariant
        return np.einsum("nr,nra->na", v, Wo[gidx])

    def forward_fast(self, g, obs, gidx, cheat=False, parallel=False, nchunks=0):
        al, G, Wo = g
        idx = np.ascontiguousarray(self.index(obs), np.int64)
        out = np.empty(len(obs), np.int64)
        _kernel(_tt_rows, parallel)(idx, np.ascontiguousarray(gidx, np.int64), al, G, Wo, out,
                                    nchunks or (24 if parallel else 1), 2 if cheat else 1)
        return out

    def ref_logits(self, g1, obs):
        al, G, Wo = (x.astype(np.float64) for x in g1)
        idx = self.index(obs)
        out = np.zeros((len(obs), self.A))
        for i in range(len(obs)):
            v = al.copy()
            for c in range(idx.shape[1]):
                v = v @ G[c, idx[i, c]]
                v /= max(np.abs(v).max(), 1e-300)
            out[i] = v @ Wo
        return out


class TTFeat(_TT):
    name = "tt_feat"

    def n_cores(self):
        return self.D

    def index(self, obs):
        return (obs.astype(np.int64) >> 12) & 15


class TTDigits(_TT):
    name = "tt_digits"

    def n_cores(self):
        return 4 * self.D

    def index(self, obs):
        return digits(obs.astype(np.uint16)).astype(np.int64)


FAMILIES = {f.name: f for f in (Linear, LutTop, TTFeat, TTDigits)}


def clear_rows(ref: np.ndarray, rel: float = 1e-6) -> np.ndarray:
    top2 = np.sort(ref, 1)[:, -2:]
    scale = np.maximum(np.abs(ref).max(1), 1e-12)
    return (top2[:, 1] - top2[:, 0]) > rel * scale
