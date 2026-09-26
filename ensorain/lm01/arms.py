"""WTP-LM01 competitive arms and cheat fixtures (directive s4; steward rulings R1a-e, O5).

Observations are (cell address A: (n, D) ints, value y). Every arm sees the same stream in the same order.

LOSSLESS (persistent state = the exact store; bit-for-bit recoverable):
  LosslessK   L-K: fixed, unlearned readout: mean of stored values at minimum Hamming distance over the FULL
              store (no learned parameter anywhere; nothing persists but the store).
  LosslessR   L-R: lazy transient refit: at each query, batch ALS low-rank fit on the FULL store, predict,
              discard the fit (R1a: wins labelled LOSSLESS_TRANSIENT_CONTRACTION; R1b refit charged).
SELECTIVE    a WTP-native bounded substrate (ensorain.wtp.organism via wtp3.collider.make) learning online.
INDISCRIMINATE RandomMerge: a relevance-blind random partition of cell space into B bins (per-bin sum and
              count); B is the knob that is calibrated on DEV to match SELECTIVE's R(t) (O5).
HYBRID       exact store + a learned low-rank embedding used as the retrieval key (k nearest stored records in
              embedding space). ablate_index() scrambles the key for the R1e access test.
Cheat fixtures (must be FLAGGED by the meter, else the meter is blind):
  LRCache     L-R that keeps its fit between queries (R1c)  -> persist_growth_on_query > 0
  LRSubsample L-R that refits on a random half of the store (R1d) -> full_read_violations > 0"""
import numpy as np

from .accounting import Metered, nbytes


class ExactStore:
    """Append-only exact record store. Cells as int16 per mode, values float64, admission step int64."""

    def __init__(self, D):
        self.D = D
        self.A = np.zeros((0, D), np.int16)
        self.y = np.zeros(0, np.float64)
        self.t = np.zeros(0, np.int64)
        self._n = 0

    def append(self, A, y):
        n = len(y)
        self.A = np.concatenate([self.A, A.astype(np.int16)])
        self.y = np.concatenate([self.y, y.astype(np.float64)])
        self.t = np.concatenate([self.t, np.arange(self._n, self._n + n, dtype=np.int64)])
        self._n += n
        return A.astype(np.int16).nbytes + y.astype(np.float64).nbytes + 8 * n

    def arrays(self):
        return [self.A, self.y, self.t]

    def nbytes(self):
        return nbytes(self.arrays())

    def digest(self):
        import hashlib
        h = hashlib.sha256()
        for a in self.arrays():
            h.update(np.ascontiguousarray(a).tobytes())
        return h.hexdigest()


class _StoreArm(Metered):
    def __init__(self, dims):
        super().__init__()
        self.dims = list(dims)
        self.store = ExactStore(len(dims))

    def _observe(self, A, y):
        self.meter.bytes_written += self.store.append(A, y)

    def persistent(self):
        return self.store.arrays()

    def must_read_bytes(self):
        return self.store.A.nbytes + self.store.y.nbytes

    def _reconstruct(self, idx, A):
        return self.store.y[idx].copy()          # exact: the record itself

    half_life = None                             # P3/H-rec (#644): fraction of the store size; None = time unused

    def _age_w(self):
        """Recency weights from the STORED admission steps (a readout of exact state; nothing is discarded)."""
        n = len(self.store.t)
        if self.half_life is None or n == 0:
            return np.ones(n)
        age = (self.store.t[-1] - self.store.t).astype(float)
        self.meter.bytes_read += self.store.t.nbytes
        return 0.5 ** (age / max(1.0, self.half_life * n))


class LosslessK(_StoreArm):
    name, category = "L-K", "LOSSLESS"

    def _predict(self, Q):
        S, V = self.store.A, self.store.y
        if len(V) == 0:
            return np.zeros(len(Q))
        out = np.empty(len(Q))
        aw = self._age_w()
        for i in range(0, len(Q), 128):
            Dm = (Q[i:i + 128, None, :] != S[None, :, :]).sum(2)
            W = (Dm == Dm.min(1, keepdims=True)) * aw[None]
            out[i:i + 128] = (W * V[None]).sum(1) / W.sum(1)
        self.meter.bytes_read += S.nbytes + V.nbytes
        self.meter.ops += len(Q) * len(V) * len(self.dims)
        return out


def als_lowrank(dims, A, y, r, lam, rng, iters, meter=None, w=None):
    """Batch ridge ALS on the best mode split (fewest parameters). Returns (U, V, s). Charges ops to meter."""
    D = len(dims)
    w = np.ones(len(y)) if w is None else w
    s = min(range(1, D), key=lambda k: int(np.prod(dims[:k])) + int(np.prod(dims[k:])))
    I = np.ravel_multi_index(A[:, :s].T.astype(int), dims[:s])
    J = np.ravel_multi_index(A[:, s:].T.astype(int), dims[s:])
    U = rng.normal(0, 0.3, (int(np.prod(dims[:s])), r))
    V = rng.normal(0, 0.3, (int(np.prod(dims[s:])), r))
    for _ in range(iters):
        for M, N, P, Qx in ((U, V, I, J), (V, U, J, I)):
            order = np.argsort(P, kind="stable")
            Ps = P[order]
            bounds = np.flatnonzero(np.diff(Ps)) + 1
            for grp in np.split(order, bounds):
                if len(grp) == 0:
                    continue
                B = N[Qx[grp]]
                Bw = B * w[grp, None]
                M[P[grp[0]]] = np.linalg.solve(Bw.T @ B + lam * np.eye(r), Bw.T @ y[grp])
            if meter is not None:
                c = len(y) * r * r + len(np.unique(P)) * r ** 3
                meter.ops += c
                meter.replay_ops += c
    return U, V, s


class LosslessR(_StoreArm):
    name, category = "L-R", "LOSSLESS"

    def __init__(self, dims, rank=2, lam=0.1, iters=10, seed=0):
        super().__init__(dims)
        self.rank, self.lam, self.iters, self.seed = rank, lam, iters, seed

    def _fit_data(self):
        return self.store.A, self.store.y, self._age_w()

    def _fit(self):
        A, y, w = self._fit_data()
        self.meter.bytes_read += A.nbytes + y.nbytes
        return als_lowrank(self.dims, A, y, self.rank, self.lam, np.random.default_rng(self.seed), self.iters, self.meter, w)

    def _apply(self, fit, Q):
        U, V, s = fit
        i = np.ravel_multi_index(Q[:, :s].T.astype(int), self.dims[:s])
        j = np.ravel_multi_index(Q[:, s:].T.astype(int), self.dims[s:])
        return (U[i] * V[j]).sum(1)

    def _predict(self, Q):
        if len(self.store.y) == 0:
            return np.zeros(len(Q))
        fit = self._fit()                        # transient: a local, freed on return
        return self._apply(fit, Q)


class LRCache(LosslessR):
    """CHEAT FIXTURE (R1c): keeps the fit between queries. Must be flagged (persist_growth_on_query)."""
    name, category = "L-R-cache[CHEAT]", "FIXTURE"

    def __init__(self, dims, **kw):
        super().__init__(dims, **kw)
        self.cached = None

    def persistent(self):
        extra = [] if self.cached is None else [self.cached[0], self.cached[1]]
        return self.store.arrays() + extra

    def _predict(self, Q):
        if len(self.store.y) == 0:
            return np.zeros(len(Q))
        if self.cached is None:
            self.cached = self._fit()
        else:
            self.meter.bytes_read += self.cached[0].nbytes + self.cached[1].nbytes
        return self._apply(self.cached, Q)


class LRSubsample(LosslessR):
    """CHEAT FIXTURE (R1d): refits on a random half of the store. Must be flagged (full_read_violations)."""
    name, category = "L-R-subsample[CHEAT]", "FIXTURE"

    def _fit_data(self):
        n = len(self.store.y)
        k = np.random.default_rng(self.seed + n).choice(n, size=max(1, n // 2), replace=False)
        return self.store.A[k], self.store.y[k], self._age_w()[k]


class Selective(Metered):
    """A WTP-native bounded substrate learning online in stream order with its fixed WTP-03 recipe."""
    category = "SELECTIVE"

    def __init__(self, kind, dims, cap, seed=0, recipe=None):
        super().__init__()
        from ensorain.wtp3.collider import make, RULE
        self.name = f"S-{kind}"
        self.kind, self.dims = kind, list(dims)
        self.mem = make(kind, dims, cap, np.random.default_rng(seed))
        self.rule, self.lr, self.passes = recipe or RULE.get(kind, ("nlms", 0.5, 1))

    def persistent(self):
        return list(self.mem.params()) + [np.array([self.mem.mean], float)]

    def _observe(self, A, y):
        for _ in range(self.passes):
            self.meter.ops += int(self.mem.learn(A.astype(int), y, self.rule, self.lr))
        for a in self.mem.params():
            if not np.all(np.isfinite(a)):
                a[~np.isfinite(a)] = 0.0
        self.meter.bytes_written += nbytes(self.persistent()) * self.passes   # dense-update upper bound
        self.meter.bytes_read += nbytes(self.persistent()) * self.passes

    def _predict(self, Q):
        self.meter.bytes_read += nbytes(self.persistent())
        self.meter.ops += len(Q) * max(1, len(self.persistent()))
        return self.mem.predict(Q.astype(int))


class RandomMerge(Metered):
    """Relevance-blind merge: a seeded random map cell -> bin in [0, B); per-bin sum and count. The map is a
    pure function of (seed, cell) and is not stored (external_bytes = 8, the seed)."""
    category = "INDISCRIMINATE"

    def __init__(self, dims, B, seed=0):
        super().__init__()
        self.name = f"M-rand{B}"
        self.dims, self.B, self.seed = list(dims), int(B), int(seed)
        cells = int(np.prod(dims))
        self._map = np.random.default_rng(seed).integers(0, self.B, size=cells)   # derived, not state
        self.sum = np.zeros(self.B)
        self.cnt = np.zeros(self.B)
        self.meter.external_bytes = 8

    def _bin(self, A):
        return self._map[np.ravel_multi_index(A.T.astype(int), self.dims)]

    def persistent(self):
        return [self.sum, self.cnt]

    def _observe(self, A, y):
        b = self._bin(A)
        np.add.at(self.sum, b, y)
        np.add.at(self.cnt, b, 1)
        self.meter.bytes_written += 16 * len(y)
        self.meter.ops += 2 * len(y)

    def _predict(self, Q):
        b = self._bin(Q)
        g = self.sum.sum() / max(1.0, self.cnt.sum())
        self.meter.bytes_read += 16 * len(Q)
        self.meter.ops += len(Q)
        return np.where(self.cnt[b] > 0, self.sum[b] / np.maximum(self.cnt[b], 1), g)


class Hybrid(_StoreArm):
    """Exact store + learned retrieval key: an online low-rank substrate's factor rows embed each cell; predict =
    mean of the k stored records nearest in embedding space. The embedding is a persistent learned index."""
    name, category = "H-lrkey", "HYBRID"

    def __init__(self, dims, cap, k=8, seed=0):
        super().__init__(dims)
        from ensorain.wtp.organism import LowRank
        self.key = LowRank(dims, cap, np.random.default_rng(seed))
        self.k = k
        self.ablated = False

    def persistent(self):
        return self.store.arrays() + self.key.params()

    def _observe(self, A, y):
        super()._observe(A, y)
        self.meter.ops += int(self.key.learn(A.astype(int), y, "sgd", 0.1))
        self.meter.bytes_written += nbytes(self.key.params())

    def _embed(self, A):
        i, j = self.key._ij(A.astype(int))
        return np.hstack([self.key.U[i], self.key.V[j]])

    def _predict(self, Q):
        S, V = self.store.A, self.store.y
        if len(V) == 0:
            return np.zeros(len(Q))
        ES, EQ = self._embed(S), self._embed(Q)
        aw = self._age_w()
        out = np.empty(len(Q))
        k = min(self.k, len(V))
        for i in range(0, len(Q), 128):
            d = ((EQ[i:i + 128, None, :] - ES[None, :, :]) ** 2).sum(2)
            nn = np.argpartition(d, k - 1, axis=1)[:, :k]
            ww = aw[nn]
            out[i:i + 128] = (V[nn] * ww).sum(1) / ww.sum(1)
        self.meter.bytes_read += S.nbytes + V.nbytes + nbytes(self.key.params())
        self.meter.ops += len(Q) * len(V) * ES.shape[1]
        return out

    def ablate_index(self, seed=0):
        """R1e: scramble the learned key (row permutation of both factors), keep the exact store."""
        rng = np.random.default_rng(seed)
        self.key.U[...] = self.key.U[rng.permutation(len(self.key.U))]
        self.key.V[...] = self.key.V[rng.permutation(len(self.key.V))]
        self.ablated = True


class LosslessKRec(LosslessK):
    """P3 (#642/#644): L-K whose readout weights records by stored age. Storage identical, exactly lossless."""
    name = "L-K-rec"

    def __init__(self, dims, half_life=0.25):
        super().__init__(dims)
        self.half_life = half_life


class LosslessRRec(LosslessR):
    """P3 (#642): recency-weighted FULL-store refit (R1d holds: all records read, weights from stored steps)."""
    name = "L-R-rec"

    def __init__(self, dims, half_life=0.25, **kw):
        super().__init__(dims, **kw)
        self.half_life = half_life


class HybridRec(Hybrid):
    """H-rec (#644): HYBRID whose k-NN readout weights retrieved records by stored age."""
    name = "H-rec"

    def __init__(self, dims, cap, half_life=0.25, **kw):
        super().__init__(dims, cap, **kw)
        self.half_life = half_life
