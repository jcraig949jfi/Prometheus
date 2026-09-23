"""E1 memory arms with charged batch consolidation (PREREG_E1 s2-s3).

Every arm: predict(addr) -> float (charged eval_cost() units by the life
loop); consolidate(A, y) -> compute units used (uniform proxy
samples x persistent params x sweeps for fitting arms). Persistent state
is audited with the E0 MemoryAudit (ensorain.e0.memories.audit).
Proximal warm start: every refit is ridge toward the CURRENT parameters,
so knowledge from earlier consolidations persists.
"""
import numpy as np

from ensorain.e0.memories import audit, AuditError  # noqa: F401
from ensorain.e0.tt import TT, tt_svd, n_params_for_ranks
from .world import D, NV

ONEHOT = D * NV


def _ridge(F, y, g_old, lam):
    k = F.shape[1]
    return np.linalg.solve(F.T @ F + lam * np.eye(k), F.T @ y + lam * g_old)


class Mem:
    PERSISTENT = ()
    CONFIG = ()

    def __init__(self, cap):
        self.cap = cap
        self.flops = 0

    def used(self):
        return audit(self, self.cap) if self.PERSISTENT else 0

    def eval_cost(self):
        return 1

    def predict(self, a):
        return 0.0

    def consolidate(self, A, y):
        return 0

    def predict_many(self, A):  # instrumentation
        return np.array([self.predict(a) for a in A])


class NoMem(Mem):
    pass


class TTAls(Mem):
    PERSISTENT = ("tt",)
    CONFIG = ("lam", "sweeps", "order", "ranks")

    def __init__(self, cap, order=tuple(range(D)), ranks=None, lam=1.0, sweeps=2, init_scale=0.5, seed=0):
        super().__init__(cap)
        self.order = tuple(int(o) for o in order)
        self.ranks = tuple(int(r) for r in (ranks or uniform_ranks(cap)))
        if n_params_for_ranks(self.ranks, [NV] * D) > cap:
            raise ValueError("ranks exceed cap")
        self.lam, self.sweeps = float(lam), int(sweeps)
        self.tt = TT([NV] * D, self.ranks, order=self.order, init_scale=init_scale,
                     rng=np.random.default_rng(99 + seed))

    def eval_cost(self):
        return self.tt.eval_flops()

    def predict(self, a):
        return self.tt.eval(a)

    def consolidate(self, A, y):
        idx = A[:, list(self.order)]
        cores = self.tt.cores
        m = len(y)
        for _ in range(self.sweeps):
            for k in list(range(D)):
                L = np.ones((m, 1))
                for j in range(k):
                    L = np.einsum("ma,mab->mb", L, cores[j][:, idx[:, j], :].transpose(1, 0, 2))
                R = np.ones((m, 1))
                for j in range(D - 1, k, -1):
                    R = np.einsum("mab,mb->ma", cores[j][:, idx[:, j], :].transpose(1, 0, 2), R)
                a, n, b = cores[k].shape
                for v in range(n):
                    s = idx[:, k] == v
                    if not s.any():
                        continue
                    F = np.einsum("ma,mb->mab", L[s], R[s]).reshape(s.sum(), a * b)
                    cores[k][:, v, :] = _ridge(F, y[s], cores[k][:, v, :].reshape(-1), self.lam).reshape(a, b)
        return m * self.tt.n_params() * self.sweeps


def uniform_ranks(cap):
    best = None
    for r in range(1, 64):
        if n_params_for_ranks([r] * (D - 1), [NV] * D) <= cap:
            best = r
    if best is None:
        raise ValueError("cap below rank-1 TT")
    return (best,) * (D - 1)


def fit_ranks(profile, cap):
    """Scale a rank profile down until it fits the cap."""
    r = [max(1, int(x)) for x in profile]
    while n_params_for_ranks(r, [NV] * D) > cap:
        i = int(np.argmax(r))
        r[i] -= 1
        if max(r) < 1:
            raise ValueError("cap too small")
    return tuple(r)


class CP(Mem):
    PERSISTENT = ("U",)
    CONFIG = ("lam", "sweeps", "R")

    def __init__(self, cap, R=None, lam=1.0, sweeps=2, init_scale=0.5, seed=0):
        super().__init__(cap)
        self.R = int(R or cap // (D * NV))
        if self.R < 1 or self.R * D * NV > cap:
            raise ValueError("CP rank does not fit cap")
        self.lam, self.sweeps = float(lam), int(sweeps)
        g = np.random.default_rng(77 + seed)
        self.U = g.normal(0, init_scale, size=(D, NV, self.R))

    def eval_cost(self):
        return D * self.R

    def predict(self, a):
        return float(np.prod(self.U[np.arange(D), np.asarray(a)], axis=0).sum())

    def consolidate(self, A, y):
        m = len(y)
        for _ in range(self.sweeps):
            for k in range(D):
                others = [j for j in range(D) if j != k]
                P = np.ones((m, self.R))
                for j in others:
                    P = P * self.U[j, A[:, j]]
                for v in range(NV):
                    s = A[:, k] == v
                    if s.any():
                        self.U[k, v] = _ridge(P[s], y[s], self.U[k, v], self.lam)
        return m * self.U.size * self.sweeps


PARTITIONS = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))


class LowRank(Mem):
    PERSISTENT = ("Ur", "Vc")
    CONFIG = ("lam", "sweeps", "R", "part")

    def __init__(self, cap, part=0, R=None, lam=1.0, sweeps=2, init_scale=0.5, seed=0):
        super().__init__(cap)
        self.part = int(part)
        self.R = int(R or cap // 128)
        if self.R < 1 or self.R * 128 > cap:
            raise ValueError("LOWRANK rank does not fit cap")
        self.lam, self.sweeps = float(lam), int(sweeps)
        g = np.random.default_rng(55 + seed)
        self.Ur = g.normal(0, init_scale, size=(64, self.R))
        self.Vc = g.normal(0, init_scale, size=(64, self.R))

    def _ij(self, A):
        (r0, r1), (c0, c1) = PARTITIONS[self.part]
        A = np.atleast_2d(A)
        return A[:, r0] * NV + A[:, r1], A[:, c0] * NV + A[:, c1]

    def eval_cost(self):
        return self.R

    def predict(self, a):
        i, j = self._ij(a)
        return float(self.Ur[i[0]] @ self.Vc[j[0]])

    def consolidate(self, A, y):
        I, J = self._ij(A)
        m = len(y)
        for _ in range(self.sweeps):
            for i in np.unique(I):
                s = I == i
                self.Ur[i] = _ridge(self.Vc[J[s]], y[s], self.Ur[i], self.lam)
            for j in np.unique(J):
                s = J == j
                self.Vc[j] = _ridge(self.Ur[I[s]], y[s], self.Vc[j], self.lam)
        return m * (self.Ur.size + self.Vc.size) * self.sweeps


class MLP(Mem):
    PERSISTENT = ("W1", "b1", "w2", "b2")
    CONFIG = ("lr", "epochs", "lam", "H")

    def __init__(self, cap, H=None, lr=0.05, epochs=20, lam=1e-3, seed=0):
        super().__init__(cap)
        self.H = int(H or (cap - 1) // (ONEHOT + 2))
        if self.H < 1 or self.H * (ONEHOT + 2) + 1 > cap:
            raise ValueError("MLP does not fit cap")
        g = np.random.default_rng(33 + seed)
        self.W1 = g.normal(0, 1 / np.sqrt(D), size=(ONEHOT, self.H))
        self.b1 = np.zeros(self.H)
        self.w2 = g.normal(0, 1 / np.sqrt(self.H), size=self.H)
        self.b2 = np.zeros(1)
        self.lr, self.epochs, self.lam = float(lr), int(epochs), float(lam)

    def _h(self, A):
        A = np.atleast_2d(A)
        z = self.W1[np.arange(D) * NV + A].sum(1) + self.b1  # (m, H)
        return A, np.tanh(z)

    def eval_cost(self):
        return (D + 1) * self.H

    def predict(self, a):
        _, h = self._h(a)
        return float(h[0] @ self.w2 + self.b2[0])

    def consolidate(self, A, y):
        m = len(y)
        old = [p.copy() for p in (self.W1, self.b1, self.w2, self.b2)]
        cols = np.arange(D) * NV + A  # (m, D)
        for _ in range(self.epochs):
            _, h = self._h(A)
            e = h @ self.w2 + self.b2[0] - y
            gw2 = h.T @ e / m + self.lam * (self.w2 - old[2])
            gb2 = np.array([e.mean()])
            dh = np.outer(e, self.w2) * (1 - h ** 2) / m  # (m, H)
            gW1 = np.zeros_like(self.W1)
            for d in range(D):
                np.add.at(gW1, cols[:, d], dh)
            gW1 += self.lam * (self.W1 - old[0])
            gb1 = dh.sum(0) + self.lam * (self.b1 - old[1])
            self.W1 -= self.lr * gW1
            self.b1 -= self.lr * gb1
            self.w2 -= self.lr * gw2
            self.b2 -= self.lr * gb2
        return m * (self.W1.size + self.H * 2 + 1) * self.epochs


def _pack(a):
    v = 0
    for x in a:
        v = v * NV + int(x)
    return v


class LRU(Mem):
    PERSISTENT = ("keys", "vals")
    CONFIG = ("size", "fill")

    def __init__(self, cap, **_):
        super().__init__(cap)
        self.size = cap // 2
        self.keys = np.full(self.size, -1, dtype=np.int64)
        self.vals = np.zeros(self.size)
        self.fill = 0

    def predict(self, a):
        k = _pack(a)
        hit = np.nonzero(self.keys[: self.fill] == k)[0]
        return float(self.vals[hit[0]]) if len(hit) else 0.0

    def consolidate(self, A, y):
        for a, v in zip(A, y):
            k = _pack(a)
            hit = np.nonzero(self.keys[: self.fill] == k)[0]
            i = int(hit[0]) if len(hit) else min(self.fill, self.size - 1)
            if not len(hit):
                self.fill = min(self.fill + 1, self.size)
            self.keys[1 : i + 1] = self.keys[0:i].copy()
            self.vals[1 : i + 1] = self.vals[0:i].copy()
            self.keys[0], self.vals[0] = k, v
        return len(y)


class KNN(LRU):
    def eval_cost(self):
        return max(1, self.fill) * D

    def predict(self, a):
        f = self.fill
        if f == 0:
            return 0.0
        digs = np.array(np.unravel_index(self.keys[:f], [NV] * D)).T
        dist = (digs != np.asarray(a)[None, :]).sum(1)
        return float(self.vals[:f][dist == dist.min()].mean())


class Oracle(Mem):
    CONTROL_EXEMPT = ("x",)

    def __init__(self, cap, x):
        super().__init__(cap)
        self.x = x

    def predict(self, a):
        return float(self.x[tuple(a)])


def inject_tt(world, cap, seed=0):
    """Cheat control: TT-SVD of the TRUE field in the latent order, truncated to the cap."""
    order = tuple(int(i) for i in np.argsort(world.perm))
    ranks = fit_ranks(TRUE_RANKS_FOR_INJECT, cap)
    mem = TTAls(cap, order=order, ranks=ranks, seed=seed)
    cores, _ = tt_svd(np.transpose(world.x, order), max_rank=list(ranks))
    for k, c in enumerate(cores):
        mem.tt.cores[k][...] = 0.0
        a, n, b = c.shape
        mem.tt.cores[k][:a, :, :b] = c
    return mem


TRUE_RANKS_FOR_INJECT = (3, 3, 3)


class Smuggler(TTAls):
    def consolidate(self, A, y):
        if not hasattr(self, "secret"):
            self.secret = {}
        for a, v in zip(A, y):
            self.secret[_pack(a)] = v
        return super().consolidate(A, y)
