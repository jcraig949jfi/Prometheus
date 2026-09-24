"""Minimal tensor-train (MPS) machinery for Ensorain E0.

Provenance: TT format and TT-SVD follow Oseledets, "Tensor-Train
Decomposition", SIAM J. Sci. Comput. 33(5), 2011 (doi:10.1137/090752286).
The online update is a normalised-LMS step on the multilinear map
(Widrow-Hoff NLMS applied to all cores at once); written here from
scratch, no library code copied.

Cores are numpy arrays G_k of shape (r_{k-1}, n_k, r_k), r_0 = r_D = 1.
`order` maps TT position k -> observed coordinate index, so the organism
may store the modes in any order it likes.
"""
import numpy as np


def n_params_for_ranks(ranks, n):
    """ranks = interior ranks (r_1..r_{D-1}); n = list of mode sizes in TT order."""
    full = [1] + list(ranks) + [1]
    return int(sum(full[k] * n[k] * full[k + 1] for k in range(len(n))))


class TT:
    def __init__(self, n, ranks, order=None, init_scale=1.0, rng=None, init_mode="gauss", init_a=1.0):
        rng = rng if rng is not None else np.random.default_rng(0)
        self.D = len(n)
        self.order = tuple(order) if order is not None else tuple(range(self.D))
        self.n = [n[o] for o in self.order]  # mode sizes in TT order
        self.r = [1] + list(ranks) + [1]
        self.cores = []
        for k in range(self.D):
            a, m, b = self.r[k], self.n[k], self.r[k + 1]
            # entries ~ N(0, s^2 / b) keep the product's scale ~ init_scale^D
            if init_mode == "e00":  # round 3: rank-1 constant path + noise, avoids the zero saddle
                c = rng.normal(0.0, init_scale, size=(a, m, b))
                c[0, :, 0] += init_a
                self.cores.append(c)
            else:
                self.cores.append(rng.normal(0.0, init_scale / np.sqrt(b), size=(a, m, b)))

    def n_params(self):
        return int(sum(c.size for c in self.cores))

    def eval_flops(self):
        return int(sum(self.r[k] * self.r[k + 1] for k in range(self.D)))

    def _idx(self, addr):
        return [addr[o] for o in self.order]

    def eval(self, addr):
        idx = self._idx(addr)
        v = self.cores[0][:, idx[0], :]  # (1, r1)
        for k in range(1, self.D):
            v = v @ self.cores[k][:, idx[k], :]
        return float(v[0, 0])

    def update(self, addr, y, lr, mode="joint", k_only=None):
        """One NLMS step toward y. Returns the pre-update error.

        mode "joint": all cores at once (linearised; can overshoot).
        mode "cyclic": only core k_only; f is LINEAR in one core, so this is
        exact NLMS and stable for 0 < lr < 2 (engineering round 1).
        mode "sweep": cyclic over every core in turn within one call, each
        step recomputing the error (costs D updates).
        """
        if mode == "sweep":
            e0 = None
            for k in range(self.D):
                e = self.update(addr, y, lr, mode="cyclic", k_only=k)
                e0 = e if e0 is None else e0
            return e0
        idx = self._idx(addr)
        mats = [self.cores[k][:, idx[k], :] for k in range(self.D)]
        left = [np.ones((1, 1))]
        for k in range(self.D - 1):
            left.append(left[-1] @ mats[k])
        right = [np.ones((1, 1))] * (self.D + 1)
        right = list(right)
        for k in range(self.D - 1, 0, -1):
            right[k] = mats[k] @ right[k + 1]
        f = float((left[self.D - 1] @ mats[self.D - 1])[0, 0])
        e = y - f
        grads = []
        norm = 1e-8
        for k in range(self.D):
            L = left[k]            # (1, r_{k})
            R = right[k + 1]       # (r_{k+1}, 1)
            g = L.T @ R.T          # (r_k, r_{k+1})
            grads.append(g)
            norm += float((g * g).sum())
        if mode == "sgd":  # plain gradient step, clipped (engineering round 2)
            g2 = norm
            scale = lr * e
            if abs(scale) * np.sqrt(g2) > 1.0:
                scale = np.sign(scale) / np.sqrt(g2)
            for k in range(self.D):
                self.cores[k][:, idx[k], :] += scale * grads[k]
            return e
        if mode == "cyclic":
            k = k_only
            gk = grads[k]
            self.cores[k][:, idx[k], :] += lr * e / (float((gk * gk).sum()) + 1e-8) * gk
            return e
        step = lr * e / norm
        for k in range(self.D):
            self.cores[k][:, idx[k], :] += step * grads[k]
        return e

    def full(self):
        """Dense tensor in OBSERVED coordinate order (instrumentation only)."""
        t = self.cores[0]
        for k in range(1, self.D):
            t = np.tensordot(t, self.cores[k], axes=([-1], [0]))
        t = t.reshape(self.n)
        inv = np.argsort(self.order)
        return np.transpose(t, inv)


def tt_svd(dense, max_rank=None, tol=0.0):
    """TT-SVD of a dense tensor in its given axis order. Returns (cores, ranks)."""
    shape = dense.shape
    D = len(shape)
    cores, ranks = [], [1]
    c = dense.reshape(shape[0], -1)
    for k in range(D - 1):
        c = c.reshape(ranks[-1] * shape[k], -1)
        u, s, vt = np.linalg.svd(c, full_matrices=False)
        keep = int((s > tol * max(s[0], 1e-300)).sum()) if tol > 0 else len(s)
        keep = max(1, keep)
        if max_rank is not None:
            keep = min(keep, max_rank[k] if hasattr(max_rank, "__len__") else max_rank)
        cores.append(u[:, :keep].reshape(ranks[-1], shape[k], keep))
        c = s[:keep, None] * vt[:keep]
        ranks.append(keep)
    cores.append(c.reshape(ranks[-1], shape[-1], 1))
    ranks.append(1)
    return cores, ranks


def ranks_of_order(dense_obs, order, tol=1e-8):
    """Numerical TT ranks of the tensor when its modes are stored in `order`."""
    t = np.transpose(dense_obs, order)
    shape = t.shape
    out = []
    for k in range(1, len(shape)):
        m = t.reshape(int(np.prod(shape[:k])), -1)
        s = np.linalg.svd(m, compute_uv=False)
        out.append(int((s > tol * s[0]).sum()))
    return out
