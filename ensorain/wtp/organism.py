"""Organism memory substrates for WTP (directive s10-s14, s19, s35).
Common interface over arbitrary tensor dims:
  n_floats()                persistent floats (the memory budget)
  predict(cells) -> values  cells = (m, D) int index array
  learn(cells, y, rule, lr) -> flops
  forget(kind, rate, rng); hazard(kind, rng); quantize(bits); eff_rank()
Substrates: none, table, sketch, additive, lowrank, tt, cp, dct, marks
(internal none; relies on external marks), mixture (table + additive)."""
import numpy as np

from ensorain.e0.tt import TT, n_params_for_ranks


class Memory:
    kind = "none"

    def __init__(self, dims, cap, rng):
        self.dims, self.cap, self.rng = list(dims), int(cap), rng
        self.D = len(dims)
        self.mean = 0.0
        self.n_seen = 0

    def n_floats(self):
        return 1

    def predict(self, cells):
        return np.full(len(cells), self.mean)

    def _track_mean(self, y):
        for v in y:
            self.n_seen += 1
            self.mean += (v - self.mean) / self.n_seen

    def learn(self, cells, y, rule, lr):
        self._track_mean(y)
        return len(y)

    def params(self):
        return []

    def forget(self, kind, rate, rng):
        ps = self.params()
        if not ps or rate <= 0 or kind == "none":
            return
        for a in ps:
            if kind == "decay":
                a *= (1 - rate)
            elif kind == "random":
                a[rng.random(a.shape) < rate] = 0.0
            elif kind == "lowest_value":
                t = np.quantile(np.abs(a), rate)
                a[np.abs(a) <= t] = 0.0

    def hazard(self, kind, rng):
        ps = self.params()
        if not ps:
            return
        if kind == "scramble":
            for a in ps:
                a += rng.normal(0, a.std() + 1e-9, a.shape)
        elif kind == "quantize2":
            self.quantize(2)
        elif kind == "reset_part":
            a = ps[int(rng.integers(len(ps)))]
            a *= 0.0
        elif kind == "permute":
            for a in ps:
                if a.ndim >= 1 and a.shape[0] > 1:
                    a[...] = a[rng.permutation(a.shape[0])]
        elif kind in ("svd_trunc", "rank_inflate"):
            for a in ps:
                if a.ndim >= 2:
                    M = a.reshape(a.shape[0], -1)
                    U, s, Vt = np.linalg.svd(M, full_matrices=False)
                    if kind == "svd_trunc":
                        s[1:] = 0
                    else:
                        s = s + s.mean()
                    a[...] = ((U * s) @ Vt).reshape(a.shape)

    def quantize(self, bits):
        if bits >= 64:
            return
        for a in self.params():
            m = np.abs(a).max()
            if m > 0:
                q = 2 ** (bits - 1) - 1
                a[...] = np.round(a / m * q) / q * m

    def eff_rank(self):
        return None


class NoneMem(Memory):
    kind = "none"


class Table(Memory):
    kind = "table"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        self.size = max(1, (cap - 1) // 2)
        self.keys = np.full(self.size, -1, dtype=np.int64)
        self.vals = np.zeros(self.size)
        self.age = np.zeros(self.size)
        self.t = 0

    def n_floats(self):
        return 2 * self.size + 1

    def _k(self, cells):
        return np.ravel_multi_index(cells.T, self.dims)

    def predict(self, cells):
        k = self._k(cells)
        out = np.full(len(k), self.mean)
        pos = {int(kk): i for i, kk in enumerate(self.keys) if kk >= 0}
        for j, kk in enumerate(k):
            i = pos.get(int(kk))
            if i is not None:
                out[j] = self.vals[i]
        return out

    def learn(self, cells, y, rule, lr):
        self._track_mean(y)
        if rule == "none":
            return len(y)
        for kk, v in zip(self._k(cells), y):
            self.t += 1
            hit = np.nonzero(self.keys == kk)[0]
            i = int(hit[0]) if len(hit) else int(np.argmin(self.age))
            if len(hit) and rule in ("sgd", "nlms", "batch_replay"):
                self.vals[i] += lr * (v - self.vals[i]) if lr < 1 else (v - self.vals[i])
            else:
                self.keys[i], self.vals[i] = kk, v
            self.age[i] = self.t
        return len(y) * 2

    def params(self):
        return [self.vals]

    def forget(self, kind, rate, rng):
        if kind == "oldest" and rate > 0:
            n = int(rate * self.size)
            if n:
                o = np.argsort(self.age)[:n]
                self.keys[o] = -1
        else:
            super().forget(kind, rate, rng)


class Sketch(Memory):
    kind = "sketch"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        self.slots = np.zeros(max(1, cap))

    def n_floats(self):
        return len(self.slots)

    def _h(self, cells):
        return (np.ravel_multi_index(cells.T, self.dims) * 2654435761) % len(self.slots)

    def predict(self, cells):
        return self.slots[self._h(cells)]

    def learn(self, cells, y, rule, lr):
        if rule != "none":
            h = self._h(cells)
            self.slots[h] += (lr if lr < 1 else 1.0) * (y - self.slots[h])
        return len(y)

    def params(self):
        return [self.slots]


class Linear(Memory):
    """Base for parametric predictors with an explicit per-sample gradient."""

    def grad_and_pred(self, cells):  # -> (pred, list of (array, index, grad))
        raise NotImplementedError

    def learn(self, cells, y, rule, lr):
        self._track_mean(y)
        if rule == "none":
            return len(y)
        flops = 0
        if rule == "evolve":
            ps = self.params()
            before = [a.copy() for a in ps]
            e0 = np.mean((self.predict(cells) - y) ** 2)
            for a in ps:
                a += lr * 0.1 * self.rng.normal(0, a.std() + 1e-3, a.shape)
            if np.mean((self.predict(cells) - y) ** 2) > e0:
                for a, b in zip(ps, before):
                    a[...] = b
            return 3 * len(y) * self.n_floats()
        for i in range(len(y)):
            p, grads = self.grad_and_pred(cells[i:i + 1])
            if rule in ("hebbian", "anti_hebbian"):
                e = y[i] * (1 if rule == "hebbian" else -1)
            else:
                e = y[i] - p
            norm = sum(float((np.asarray(g) ** 2).sum()) for _, _, g in grads) + 1e-8 if rule == "nlms" else 1.0
            step = lr * e / norm
            step = float(np.clip(step, -1e3, 1e3))
            for a, idx, g in grads:
                a[idx] += step * g
            flops += 3 * self.n_floats()
        return flops


class Additive(Linear):
    kind = "additive"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        self.w = [np.zeros(n) for n in dims]
        self.b = np.zeros(1)

    def n_floats(self):
        return sum(self.dims) + 1

    def predict(self, cells):
        return self.b[0] + sum(self.w[m][cells[:, m]] for m in range(self.D))

    def grad_and_pred(self, cells):
        c = cells[0]
        p = self.predict(cells)[0]
        return p, [(self.w[m], c[m], 1.0) for m in range(self.D)] + [(self.b, 0, 1.0)]

    def params(self):
        return self.w + [self.b]


class LowRank(Linear):
    kind = "lowrank"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        best = None
        for s in range(1, self.D):
            rows, cols = int(np.prod(dims[:s])), int(np.prod(dims[s:]))
            if best is None or rows + cols < best[1] + best[2]:
                best = (s, rows, cols)
        self.s, rows, cols = best
        self.r = max(1, cap // (rows + cols))
        self.U = rng.normal(0, 0.3, (rows, self.r))
        self.V = rng.normal(0, 0.3, (cols, self.r))

    def n_floats(self):
        return self.U.size + self.V.size

    def _ij(self, cells):
        i = np.ravel_multi_index(cells[:, :self.s].T, self.dims[:self.s]) if self.s > 0 else np.zeros(len(cells), int)
        j = np.ravel_multi_index(cells[:, self.s:].T, self.dims[self.s:])
        return i, j

    def predict(self, cells):
        i, j = self._ij(cells)
        return (self.U[i] * self.V[j]).sum(1)

    def grad_and_pred(self, cells):
        i, j = self._ij(cells)
        u, v = self.U[i[0]].copy(), self.V[j[0]].copy()
        return float(u @ v), [(self.U, i[0], v), (self.V, j[0], u)]

    def params(self):
        return [self.U, self.V]

    def eff_rank(self):
        s = np.linalg.svd(self.U @ self.V.T, compute_uv=False)
        return int((s > 1e-2 * (s[0] + 1e-12)).sum())

    def forget(self, kind, rate, rng):
        if kind == "spectral_trunc" and rng.random() < rate and self.r > 1:
            U, s, Vt = np.linalg.svd(self.U @ self.V.T, full_matrices=False)
            k = max(1, self.eff_rank() - 1)
            s[k:] = 0
            self.U[:, :] = 0
            self.V[:, :] = 0
            kk = min(k, self.r)
            self.U[:, :kk] = U[:, :kk] * np.sqrt(s[:kk])
            self.V[:, :kk] = Vt[:kk].T * np.sqrt(s[:kk])
        else:
            super().forget(kind, rate, rng)


class TTMem(Linear):
    kind = "tt"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        r = 1
        while n_params_for_ranks([r + 1] * (self.D - 1), dims) <= cap:
            r += 1
        self.tt = TT(dims, [r] * (self.D - 1), init_scale=0.8, rng=rng)
        self.r = r

    def n_floats(self):
        return self.tt.n_params()

    def predict(self, cells):
        return np.array([self.tt.eval(tuple(c)) for c in cells])

    def learn(self, cells, y, rule, lr):
        if rule in ("sgd", "nlms", "batch_replay"):
            self._track_mean(y)
            for c, v in zip(cells, y):
                self.tt.update(tuple(c), float(v), min(lr, 0.5), mode="sgd" if rule == "sgd" else "joint")
            return 3 * len(y) * self.tt.eval_flops()
        if rule in ("hebbian", "anti_hebbian"):
            self._track_mean(y)
            sgn = 1 if rule == "hebbian" else -1
            for c, v in zip(cells, y):
                self.tt.update(tuple(c), float(self.tt.eval(tuple(c)) + sgn * v), min(lr, 0.5), mode="sgd")
            return 3 * len(y) * self.tt.eval_flops()
        return super().learn(cells, y, rule, lr)

    def params(self):
        return self.tt.cores

    def eff_rank(self):
        c = self.tt.cores[self.D // 2]
        s = np.linalg.svd(c.reshape(c.shape[0], -1), compute_uv=False)
        return int((s > 1e-2 * (s[0] + 1e-12)).sum())

    def hazard(self, kind, rng):
        if kind == "permute":
            order = list(rng.permutation(self.D))
            self.tt.order = tuple(order)
        else:
            super().hazard(kind, rng)

    def forget(self, kind, rate, rng):
        if kind == "spectral_trunc" and rng.random() < rate:
            k = self.D // 2
            a = self.tt.cores[k]
            M = a.reshape(a.shape[0], -1)
            U, s, Vt = np.linalg.svd(M, full_matrices=False)
            s[max(1, self.eff_rank() - 1):] = 0
            a[...] = ((U * s) @ Vt).reshape(a.shape)
        else:
            super().forget(kind, rate, rng)


class CPMem(Linear):
    kind = "cp"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        self.R = max(1, cap // sum(dims))
        self.F = [rng.normal(0, 0.5, (n, self.R)) for n in dims]

    def n_floats(self):
        return sum(f.size for f in self.F)

    def predict(self, cells):
        P = np.ones((len(cells), self.R))
        for m in range(self.D):
            P = P * self.F[m][cells[:, m]]
        return P.sum(1)

    def grad_and_pred(self, cells):
        c = cells[0]
        rows = [self.F[m][c[m]] for m in range(self.D)]
        p = float(np.prod(rows, axis=0).sum())
        grads = []
        for m in range(self.D):
            g = np.prod([rows[j] for j in range(self.D) if j != m], axis=0) if self.D > 1 else np.ones(self.R)
            grads.append((self.F[m], c[m], g))
        return p, grads

    def params(self):
        return self.F


class DCT(Linear):
    """Spectral memory: coefficients over the lowest cosine frequencies per mode."""
    kind = "dct"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        k = [1] * self.D
        while True:
            grown = False
            for m in np.argsort(dims)[::-1]:
                if k[m] < dims[m]:
                    k[m] += 1
                    if np.prod(k) > cap:
                        k[m] -= 1
                    else:
                        grown = True
            if not grown:
                break
        self.k = k
        self.B = [np.array([[np.cos(np.pi * f * (i + 0.5) / n) for f in range(kk)] for i in range(n)]) for n, kk in zip(dims, k)]
        self.C = np.zeros(k)

    def n_floats(self):
        return self.C.size

    def _feat(self, c):
        f = self.B[0][c[0]]
        for m in range(1, self.D):
            f = np.multiply.outer(f, self.B[m][c[m]])
        return f

    def predict(self, cells):
        return np.array([float((self._feat(c) * self.C).sum()) for c in cells])

    def grad_and_pred(self, cells):
        f = self._feat(cells[0])
        return float((f * self.C).sum()), [(self.C, Ellipsis, f)]

    def params(self):
        return [self.C]


class Mixture(Memory):
    kind = "mixture"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        self.t = Table(dims, max(2, cap - sum(dims) - 1), rng)
        self.a = Additive(dims, cap, rng)

    def n_floats(self):
        return self.t.n_floats() + self.a.n_floats()

    def predict(self, cells):
        k = self.t._k(cells)
        hit = np.isin(k, self.t.keys)
        out = self.a.predict(cells)
        if hit.any():
            out[hit] = self.t.predict(cells[hit])
        return out

    def learn(self, cells, y, rule, lr):
        return self.t.learn(cells, y, rule, lr) + self.a.learn(cells, y, rule, lr)

    def params(self):
        return self.t.params() + self.a.params()


KINDS = {"none": NoneMem, "marks": NoneMem, "table": Table, "sketch": Sketch, "additive": Additive, "lowrank": LowRank,
         "tt": TTMem, "cp": CPMem, "dct": DCT, "mixture": Mixture}
CONVERTIBLE = ("table", "additive", "lowrank", "tt", "cp", "dct")


def make_memory(kind, dims, cap, rng):
    m = KINDS[kind](dims, cap, rng)
    if kind not in ("none", "marks") and m.n_floats() > cap:
        raise ValueError(f"{kind} needs {m.n_floats()} floats > cap {cap}")
    return m


def convert(mem, kind, dims, cap, rng, cells, y):
    """Representation fluidity (s14): build a new substrate and fit it to the old
    memory's own predictions on `cells` plus the recent real samples `y`."""
    new = make_memory(kind, dims, cap, rng)
    tgt = mem.predict(cells)
    flops = 0
    for _ in range(3):
        flops += new.learn(cells, tgt, "nlms" if kind not in ("table",) else "sgd", 0.5)
    return new, flops
