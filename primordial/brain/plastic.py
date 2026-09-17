"""Lane C (BRAIN) C2: a plastic-rank tensor-train regressor.

Function of d base-16 digits as a TT with variable bond ranks, cores
G[k] [r_{k-1}, 16, r_k], r_0 = r_d = 1. Online loop per batch:

  1. predict, then see targets; surprise = batch MSE > kappa * EWMA(MSE)
  2. on surprise: flush the buffer to this batch and GROW every bond by `grow`;
     otherwise grow by 1 every `explore_every` steps (capacity probe)
  3. one ALS sweep (exact local least squares per core, per digit value) on the buffer
  4. TT-rounding under a MEMORY CHARGE: left-orthogonalise, then right-to-left SVD
     per bond, dropping a singular value while sigma^2 < lam * (params it frees).
     Cores are scaled by 1/4 while rounding, so ||T||_F^2 = mean square of the
     function over uniform digits: sigma^2 IS the MSE the truncation costs.

The regime flag reaches every brain through observe_flag(); honest brains ignore
it. LeakTTBrain uses it (the C2 cheat control).
"""
from __future__ import annotations

from collections import deque

import numpy as np

BASE = 16


def tt_eval(cores, X):
    Xi = np.asarray(X, dtype=np.intp)
    v = np.ones((len(Xi), 1))
    for k, G in enumerate(cores):
        v = np.einsum("na,anb->nb", v, G[:, Xi[:, k], :])
    return v[:, 0]


def tt_full(cores):
    T = cores[0]
    for G in cores[1:]:
        T = np.tensordot(T, G, axes=(-1, 0))
    return T.reshape([BASE] * len(cores))


def bond_sigmas(T):
    """Exact bond singular values of a full tensor, in MSE units (uniform digits)."""
    d = T.ndim
    S = T / np.sqrt(T.size)
    return [np.linalg.svd(S.reshape(BASE ** k, -1), compute_uv=False) for k in range(1, d)]


def _orth(r, rng):
    q, rr = np.linalg.qr(rng.standard_normal((r, r)))
    return q * np.sign(np.diag(rr))


def random_target(d: int, r: int, rng) -> list:
    """Orthogonal-core TT with every bond rank = r (r <= 16), unit mean square.
    Flat bond spectra: each of the r directions carries ~1/r of the energy."""
    g0 = rng.standard_normal((1, BASE, r))
    g0 /= np.linalg.norm(g0, axis=2, keepdims=True)
    cores = [g0]
    for _ in range(d - 2):
        cores.append(np.stack([_orth(r, rng) for _ in range(BASE)], axis=1))
    gl = rng.standard_normal((r, BASE, 1))
    gl /= np.linalg.norm(gl, axis=0, keepdims=True)
    cores.append(gl)
    T = tt_full(cores)
    cores[-1] = cores[-1] / np.sqrt(np.mean(T ** 2))
    return cores


def decaying_target(d: int, R: int, decay: float, rng) -> list:
    """Sum of R separable terms with weights decay**c: block-diagonal TT of rank <= R
    whose bond spectrum decays roughly geometrically, so the rank worth paying for
    under a memory charge depends on `decay` (not exactly low rank)."""
    u = rng.standard_normal((R, d, BASE))
    u *= 4.0 / np.linalg.norm(u, axis=2, keepdims=True)
    w = decay ** np.arange(R)
    g0 = np.zeros((1, BASE, R)); g0[0, :, :] = (w[:, None] * u[:, 0, :]).T
    cores = [g0]
    for k in range(1, d - 1):
        g = np.zeros((R, BASE, R))
        for c in range(R):
            g[c, :, c] = u[c, k, :]
        cores.append(g)
    gl = np.zeros((R, BASE, 1)); gl[:, :, 0] = u[:, d - 1, :]
    cores.append(gl)
    T = tt_full(cores)
    cores[-1] = cores[-1] / np.sqrt(np.mean(T ** 2))
    return cores


def oracle_ranks(target, lam: float, rmax: int) -> list:
    """The ranks the memory charge would keep given the TRUE function (no noise, no data)."""
    out, _ = tt_round([c.copy() for c in target], lam, rmax)
    return ranks(out)


def tt_round(cores, lam: float, rmax: int):
    d = len(cores)
    H = [G / 4.0 for G in cores]
    for k in range(d - 1):
        a, _, b = H[k].shape
        Q, R = np.linalg.qr(H[k].reshape(a * BASE, b))
        H[k] = Q.reshape(a, BASE, Q.shape[1])
        H[k + 1] = np.einsum("ab,bjc->ajc", R, H[k + 1])
    sig = [None] * (d - 1)
    for k in range(d - 1, 0, -1):
        a, _, b = H[k].shape
        U, S, Vt = np.linalg.svd(H[k].reshape(a, BASE * b), full_matrices=False)
        left = H[k - 1].shape[0]
        keep = min(len(S), rmax)
        while keep > 1 and S[keep - 1] ** 2 < lam * BASE * (left + b):
            keep -= 1
        sig[k - 1] = S
        H[k] = Vt[:keep].reshape(keep, BASE, b)
        H[k - 1] = np.einsum("ajb,bc->ajc", H[k - 1], U[:, :keep] * S[:keep])
    return [h * 4.0 for h in H], sig


def als_sweep(cores, X, y, ridge: float):
    d, N = len(cores), len(y)
    Xi = np.asarray(X, dtype=np.intp)
    R = [None] * (d + 1)
    R[d] = np.ones((N, 1))
    for k in range(d - 1, 0, -1):
        R[k] = np.einsum("anb,nb->na", cores[k][:, Xi[:, k], :], R[k + 1])
    L = np.ones((N, 1))
    for k in range(d):
        Rk = R[k + 1]
        a, b = L.shape[1], Rk.shape[1]
        Phi = (L[:, :, None] * Rk[:, None, :]).reshape(N, a * b)
        col = Xi[:, k]
        order = np.argsort(col, kind="stable")
        ends = np.searchsorted(col[order], np.arange(1, BASE + 1))
        G = cores[k].copy()
        reg = np.eye(a * b) * ridge
        lo = 0
        for j in range(BASE):
            hi = ends[j]
            if hi > lo:
                idx = order[lo:hi]
                P = Phi[idx]
                G[:, j, :] = np.linalg.solve(P.T @ P + reg, P.T @ y[idx]).reshape(a, b)
            lo = hi
        cores[k] = G
        L = np.einsum("na,anb->nb", L, G[:, Xi[:, k], :])
    return cores


def grow(cores, g: int, rmax: int, rng, scale: float = 0.1):
    d = len(cores)
    for k in range(1, d):
        r = cores[k].shape[0]
        new = min(r + g, rmax, BASE ** min(k, d - k))
        if new <= r:
            continue
        A, B = cores[k - 1], cores[k]
        cores[k - 1] = np.concatenate([A, scale * rng.standard_normal((A.shape[0], BASE, new - r))], axis=2)
        cores[k] = np.concatenate([B, scale * rng.standard_normal((new - r, BASE, B.shape[2]))], axis=0)
    return cores


def ranks(cores):
    return [G.shape[2] for G in cores[:-1]]


class PlasticTTBrain:
    name = "plastic"

    def __init__(self, d=4, lam=1e-4, rmax=12, window=8192, ridge=1.0, kappa=4.0,
                 grow_by=2, explore_every=4, plastic=True, rank0=1, alpha=0.2, seed=0):
        self.rng = np.random.default_rng(seed)
        self.d, self.lam, self.rmax, self.window = d, lam, rmax, window
        self.ridge, self.kappa, self.grow_by, self.explore_every = ridge, kappa, grow_by, explore_every
        self.plastic, self.alpha = plastic, alpha
        dims = [1] + [min(rank0, BASE ** min(k, d - k)) for k in range(1, d)] + [1]
        self.cores = [self.rng.standard_normal((dims[k], BASE, dims[k + 1])) / np.sqrt(dims[k])
                      for k in range(d)]
        self.buf = deque()
        self.nbuf = 0
        self.ewma = None
        self.t = 0
        self.last_grow = 0
        self.surprised = False

    def observe_flag(self, flag: int) -> None:
        pass

    def predict(self, X):
        return tt_eval(self.cores, X)

    def _is_surprise(self, e: float) -> bool:
        return self.ewma is not None and e > self.kappa * self.ewma

    def adapt_batch(self, X, y, pred) -> None:
        e = float(np.mean((pred - y) ** 2))
        self.surprised = self._is_surprise(e)
        if self.surprised:
            self.buf.clear()
            self.nbuf = 0
            self.ewma = None
            if self.plastic:
                grow(self.cores, self.grow_by, self.rmax, self.rng)
                self.last_grow = self.t
        elif self.plastic and self.t - self.last_grow >= self.explore_every:
            grow(self.cores, 1, self.rmax, self.rng)
            self.last_grow = self.t
        self.buf.append((X, y))
        self.nbuf += len(y)
        while self.nbuf - len(self.buf[0][1]) >= self.window:
            self.nbuf -= len(self.buf.popleft()[1])
        BX = np.concatenate([b[0] for b in self.buf])
        By = np.concatenate([b[1] for b in self.buf])
        als_sweep(self.cores, BX, By, self.ridge)
        self.cores, _ = tt_round(self.cores, self.lam if self.plastic else 0.0,
                                 self.rmax if self.plastic else 10 ** 6)
        if not self.surprised:
            self.ewma = e if self.ewma is None else (1 - self.alpha) * self.ewma + self.alpha * e
        self.t += 1

    def act(self, obs, msg_in=None):
        """contract.Brain: sign of the regression output as an int32 action."""
        n_envs, n_slots = obs.shape[0], obs.shape[1]
        o = np.asarray(obs, dtype=np.uint16)[..., 0].reshape(-1)
        X = ((o[:, None] >> np.array([12, 8, 4, 0], np.uint16)) & 15)[:, :self.d]
        return (self.predict(X) > 0).astype(np.int32).reshape(n_envs, n_slots, 1), None

    def adapt(self, signal) -> None:
        X, y = signal
        self.adapt_batch(X, y, self.predict(X))

    def cost(self) -> dict:
        return {"params": int(sum(G.size for G in self.cores)), "ranks": ranks(self.cores),
                "flops_per_act": int(sum(G.shape[0] * G.shape[2] for G in self.cores))}


class FixedTTBrain(PlasticTTBrain):
    """Same learner, same flush-on-surprise; rank frozen at rank0 (no grow, no charge)."""

    def __init__(self, rank0=8, **kw):
        super().__init__(plastic=False, rank0=rank0, **kw)
        self.name = f"fixed{rank0}"


class LeakTTBrain(PlasticTTBrain):
    """CHEAT: flushes and grows when the regime FLAG changes, instead of on surprise.
    It acts only in adapt_batch (after targets are seen), like an honest detector
    would, so its trajectory is plausible; only flag invariance can catch it."""
    name = "leak_flag"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.flag = None
        self.switched = False

    def observe_flag(self, flag: int) -> None:
        self.switched = self.flag is not None and flag != self.flag
        self.flag = flag

    def _is_surprise(self, e: float) -> bool:
        return self.switched
