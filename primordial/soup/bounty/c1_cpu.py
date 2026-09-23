"""Lane B bounty on C1: faster CPU TT-policy contraction at d64 r64 B4096.

Computes exactly C's function (primordial/brain/tt_policy.py, imported read-only):
    logits(x) = alpha^T G[0,x_0] ... G[d-1,x_{d-1}] W      (float32)
and plugs into C's Backend interface so C's time_cell / compare / ref64 oracle apply.

  nb_bucket_c<N>     numba prange over N chunks; per core a counting sort of the chunk's
                     rows by digit, then every run of rows sharing a digit is multiplied
                     against ONE hot matrix as saxpy rows (v@G = sum_a v[a] G[a,:])
  np_bucket_perm     numpy: rows stay sorted by the previous core's digit, so each core
                     costs ONE gather (not gather + scatter); matmul(out=) into a swap buffer
  np_bucket_shard3   numpy: 3 Python threads, each runs np_bucket on a third of the batch
                     with OpenBLAS pinned to 1 thread (no BLAS thread handoff on small gemms)
Cheat (control, never on the board):
  cheat_nb_bucket_skip_half   nb_bucket that contracts only every other core
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import numpy as np
from numba import njit, prange

from primordial.brain import tt_policy as tt


@njit(parallel=True, nogil=True, fastmath=True, boundscheck=False, cache=True)
def _nb_bucket(dig, alpha, G, W, out, nchunks, stride):
    B, d = dig.shape
    r = alpha.shape[0]
    A = W.shape[1]
    step = (B + nchunks - 1) // nchunks
    for c in prange(nchunks):
        lo = c * step
        hi = min(B, lo + step)
        n = hi - lo
        if n <= 0:
            continue
        V = np.empty((n, r), dtype=np.float32)
        U = np.empty((n, r), dtype=np.float32)
        perm = np.arange(n)              # V[q] holds chunk-local sample perm[q]
        newperm = np.empty(n, dtype=np.int64)
        src = np.empty(n, dtype=np.int64)
        starts = np.zeros(17, dtype=np.int64)
        pos = np.zeros(16, dtype=np.int64)
        for i in range(n):
            for a in range(r):
                V[i, a] = alpha[a]
        for k in range(0, d, stride):
            for j in range(17):
                starts[j] = 0
            for q in range(n):
                starts[dig[lo + perm[q], k] + 1] += 1
            for j in range(16):
                starts[j + 1] += starts[j]
            for j in range(16):
                pos[j] = starts[j]
            for q in range(n):
                j = dig[lo + perm[q], k]
                t = pos[j]
                pos[j] += 1
                src[t] = q
                newperm[t] = perm[q]
            for j in range(16):
                for t in range(starts[j], starts[j + 1]):
                    q = src[t]
                    for b in range(r):
                        U[t, b] = 0.0
                    for a in range(r):
                        va = V[q, a]
                        for b in range(r):
                            U[t, b] += va * G[k, j, a, b]
            V, U = U, V
            perm, newperm = newperm, perm
        for q in range(n):
            i = lo + perm[q]
            for c2 in range(A):
                s = np.float32(0.0)
                for b in range(r):
                    s += V[q, b] * W[b, c2]
                out[i, c2] = s


class NbBucket(tt.Backend):
    # name comes from the class (set by nb_bucket_class); an instance must not overwrite it,
    # or the skip-half cheat would report itself as an honest nb_bucket_c<N> (caught by test_c1_cpu)
    name = "nb_bucket_c3"
    nchunks = 3
    stride = 1

    def __init__(self, p):
        super().__init__(p)
        self.logits(np.zeros((max(1, self.nchunks), p.obs_dim), np.uint16))   # compile outside timing

    def logits(self, obs):
        dig = tt.digits(obs)
        out = np.empty((len(dig), self.p.A), np.float32)
        _nb_bucket(dig, self.p.alpha, self.p.G, self.p.W, out, self.nchunks, self.stride)
        return out


def nb_bucket_class(nchunks: int, stride: int = 1, cheat: bool = False):
    name = ("cheat_nb_bucket_skip_half" if cheat else f"nb_bucket_c{nchunks}")
    return type(name, (NbBucket,), {"nchunks": nchunks, "stride": stride, "cheat": cheat, "name": name})


class NpBucketPerm(tt.Backend):
    name = "np_bucket_perm"

    def logits(self, obs):
        p, dig = self.p, tt.digits(obs)
        B = len(dig)
        v = np.empty((B, p.r), np.float32)
        v[:] = p.alpha
        u = np.empty_like(v)
        perm = np.arange(B)
        for k in range(p.d):
            col = dig[perm, k]
            order = np.argsort(col, kind="stable")
            ends = np.cumsum(np.bincount(col, minlength=16))
            v = v[order]                      # the ONE gather for this core
            perm = perm[order]
            lo = 0
            for j in range(16):
                hi = ends[j]
                if hi > lo:
                    np.matmul(v[lo:hi], p.G[k, j], out=u[lo:hi])
                lo = hi
            v, u = u, v
        out = np.empty((B, p.A), np.float32)
        out[perm] = v @ p.W
        return out


class NpBucketShard3(tt.Backend):
    name = "np_bucket_shard3"
    shards = 3

    def __init__(self, p):
        super().__init__(p)
        from threadpoolctl import threadpool_limits
        self._limits = threadpool_limits(limits=1, user_api="blas")
        self.pool = ThreadPoolExecutor(self.shards)
        self.inner = tt.NpBucket(p)

    def _one(self, dig_obs, lo, hi, out):
        out[lo:hi] = self.inner.logits(dig_obs[lo:hi])

    def logits(self, obs):
        obs = np.ascontiguousarray(obs, dtype=np.uint16).reshape(-1, self.p.obs_dim)
        B = len(obs)
        out = np.empty((B, self.p.A), np.float32)
        b = np.linspace(0, B, self.shards + 1).astype(int)
        list(self.pool.map(lambda s: self._one(obs, b[s], b[s + 1], out), range(self.shards)))
        return out

    def close(self):
        self.pool.shutdown()
        self._limits.restore_original_limits()


def backends() -> dict:
    out = {"np_bucket_perm": NpBucketPerm, "np_bucket_shard3": NpBucketShard3}
    for c in (3, 6, 24):
        cls = nb_bucket_class(c)
        out[cls.name] = cls
    cheat = nb_bucket_class(24, stride=2, cheat=True)
    out[cheat.name] = cheat
    return out
