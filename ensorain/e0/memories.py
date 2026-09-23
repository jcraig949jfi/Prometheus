"""E0 persistent-memory arms and the MemoryAudit (PREREG_E0 s3).

Every arm declares:
  PERSISTENT : attribute names holding persistent state (numpy arrays or a
               TT); their float count is charged against the cap C.
  CONFIG     : attribute names holding lifetime constants (scalars, small
               int tuples, a numpy Generator, regenerable fixed random
               projections declared in FIXED_RANDOM).
Anything else found on the object at audit time is a smuggled container and
the audit REFUSES the organism. Counters (`flops`) are instrumentation the
memory writes but never reads.
"""
import numpy as np
from .tt import TT, n_params_for_ranks
from .world import D, NV


class AuditError(Exception):
    pass


def _count(obj):
    if isinstance(obj, TT):
        return obj.n_params()
    if isinstance(obj, np.ndarray):
        return int(obj.size)
    raise AuditError(f"undeclared persistent type {type(obj).__name__}")


def audit(mem, cap):
    allowed = set(mem.PERSISTENT) | set(mem.CONFIG) | set(getattr(mem, "FIXED_RANDOM", ())) | {"flops", "cap"}
    allowed |= set(getattr(mem, "CONTROL_EXEMPT", ()))  # ORACLE / DICT_UNCAP only; never a competing arm
    for name, val in vars(mem).items():
        if name not in allowed:
            raise AuditError(f"{type(mem).__name__}.{name}: undeclared attribute ({type(val).__name__})")
        if name in mem.CONFIG:
            ok = isinstance(val, (int, float, str, bool, np.integer, np.floating, np.random.Generator, type(None)))
            ok = ok or (isinstance(val, tuple) and len(val) <= 16 and all(isinstance(x, (int, np.integer)) for x in val))
            if not ok:
                raise AuditError(f"{type(mem).__name__}.{name}: CONFIG must be a scalar/short int tuple, got {type(val).__name__}")
    used = sum(_count(getattr(mem, p)) for p in mem.PERSISTENT)
    if used > cap:
        raise AuditError(f"{type(mem).__name__}: {used} floats > cap {cap}")
    return used


class Memory:
    PERSISTENT = ()
    CONFIG = ()

    def __init__(self, cap):
        self.cap = cap
        self.flops = 0

    def predict(self, a):
        raise NotImplementedError

    def observe(self, a, y):
        pass

    def predict_all(self, addrs):  # instrumentation only (no charge)
        f = self.flops
        out = np.array([self.predict(a) for a in addrs])
        self.flops = f
        return out


class NoMem(Memory):
    def predict(self, a):
        return 0.0


def _pack(a):
    v = 0
    for x in a:
        v = v * NV + int(x)
    return v


class LRU(Memory):
    PERSISTENT = ("keys", "vals")
    CONFIG = ("size", "fill")

    def __init__(self, cap):
        super().__init__(cap)
        self.size = cap // 2
        self.keys = np.full(self.size, -1, dtype=np.int64)
        self.vals = np.zeros(self.size)
        self.fill = 0

    def _find(self, k):
        self.flops += 1
        hit = np.nonzero(self.keys[: self.fill] == k)[0]
        return int(hit[0]) if len(hit) else -1

    def predict(self, a):
        i = self._find(_pack(a))
        return float(self.vals[i]) if i >= 0 else 0.0

    def observe(self, a, y):
        k = _pack(a)
        i = self._find(k)
        if i < 0:
            i = min(self.fill, self.size - 1)
            self.fill = min(self.fill + 1, self.size)
        # move to front (position 0 = most recent); last slot is evicted
        self.keys[1 : i + 1] = self.keys[0:i].copy()
        self.vals[1 : i + 1] = self.vals[0:i].copy()
        self.keys[0], self.vals[0] = k, y


class KNN(LRU):
    def predict(self, a):
        f = self.fill
        if f == 0:
            return 0.0
        self.flops += f * D
        ka = self.keys[:f]
        digs = np.array(np.unravel_index(ka, [NV] * D)).T
        dist = (digs != np.asarray(a)[None, :]).sum(1)
        m = dist.min()
        return float(self.vals[:f][dist == m].mean())


class Hash(Memory):
    PERSISTENT = ("slots",)
    CONFIG = ("mult",)

    def __init__(self, cap):
        super().__init__(cap)
        self.slots = np.zeros(cap)
        self.mult = 2654435761

    def _h(self, a):
        self.flops += 1
        return (_pack(a) * self.mult) % len(self.slots)

    def predict(self, a):
        return float(self.slots[self._h(a)])

    def observe(self, a, y):
        self.slots[self._h(a)] = y


class Additive(Memory):
    PERSISTENT = ("w",)
    CONFIG = ("lr",)

    def __init__(self, cap, lr=0.3):
        super().__init__(cap)
        self.w = np.zeros(min(cap, D * NV))
        self.lr = lr

    def _ix(self, a):
        return np.arange(D) * NV + np.asarray(a)

    def predict(self, a):
        self.flops += D
        return float(self.w[self._ix(a)].sum())

    def observe(self, a, y):
        ix = self._ix(a)
        e = y - self.w[ix].sum()
        self.w[ix] += self.lr * e / D
        self.flops += 3 * D


class RF(Memory):
    PERSISTENT = ("w",)
    CONFIG = ("lr", "seed")
    FIXED_RANDOM = ("proj", "bias")  # regenerable from `seed`; 0 storage

    def __init__(self, cap, lr=0.5, seed=0):
        super().__init__(cap)
        g = np.random.default_rng(777 + seed)
        self.seed = seed
        self.proj = g.normal(size=(cap, D * NV))
        self.bias = g.normal(size=cap) * 0.5
        self.w = np.zeros(cap)
        self.lr = lr

    def _phi(self, a):
        ix = np.arange(D) * NV + np.asarray(a)
        self.flops += len(self.w)  # PREREG s2: random-feature predict = weights
        return np.maximum(0.0, self.proj[:, ix].sum(1) + self.bias)

    def predict(self, a):
        return float(self._phi(a) @ self.w)

    def observe(self, a, y):
        p = self._phi(a)
        e = y - p @ self.w
        self.w += self.lr * e * p / (p @ p + 1e-8)
        self.flops += 3 * len(self.w)


class LowRank(Memory):
    """64x64 unfolding (observed modes 0-2 x 3-5), rank = cap // 128."""
    PERSISTENT = ("U", "V")
    CONFIG = ("lr", "k")

    def __init__(self, cap, lr=0.5, seed=0):
        super().__init__(cap)
        self.k = cap // 128
        if self.k < 1:
            raise ValueError("LOWRANK unavailable below cap 128")
        g = np.random.default_rng(55 + seed)
        self.U = g.normal(size=(64, self.k)) * 0.3
        self.V = g.normal(size=(64, self.k)) * 0.3
        self.lr = lr

    def _ij(self, a):
        return a[0] * 16 + a[1] * 4 + a[2], a[3] * 16 + a[4] * 4 + a[5]

    def predict(self, a):
        i, j = self._ij(a)
        self.flops += self.k
        return float(self.U[i] @ self.V[j])

    def observe(self, a, y):
        i, j = self._ij(a)
        u, v = self.U[i].copy(), self.V[j].copy()
        e = y - u @ v
        n = u @ u + v @ v + 1e-8
        self.U[i] += self.lr * e * v / n
        self.V[j] += self.lr * e * u / n
        self.flops += 3 * self.k


class TTMem(Memory):
    """TT memory with an optional replay buffer that shares the cap.

    genome: order (tuple), ranks (tuple), lr, init_scale, buf_frac, replay.
    """
    PERSISTENT = ("tt", "buf_keys", "buf_vals")
    CONFIG = ("lr", "replay", "buf_n", "buf_fill", "buf_pos", "rng", "order", "ranks", "mode", "tick")

    def __init__(self, cap, order=tuple(range(D)), ranks=None, lr=0.5, init_scale=1.0,
                 buf_frac=0.0, replay=0, seed=0, mode="joint", init_mode="gauss", init_a=1.0):
        super().__init__(cap)
        self.mode, self.tick = str(mode), 0
        self.order, self.lr, self.replay = tuple(int(o) for o in order), float(lr), int(replay)
        self.buf_n = int(buf_frac * cap) // 2
        tt_cap = cap - 2 * self.buf_n
        if ranks is None:
            ranks = uniform_ranks(tt_cap)
        self.ranks = tuple(int(r) for r in ranks)
        if n_params_for_ranks(self.ranks, [NV] * D) > tt_cap:
            raise ValueError("ranks exceed cap")
        self.rng = np.random.default_rng(99 + seed)
        self.tt = TT([NV] * D, self.ranks, order=self.order, init_scale=init_scale, rng=self.rng,
                     init_mode=init_mode, init_a=init_a)
        self.buf_keys = np.full(self.buf_n, -1, dtype=np.int64)
        self.buf_vals = np.zeros(self.buf_n)
        self.buf_fill = 0
        self.buf_pos = 0

    def predict(self, a):
        self.flops += self.tt.eval_flops()
        return self.tt.eval(a)

    def _upd(self, a, y):
        if self.mode == "sweep":
            self.tt.update(a, y, self.lr, mode="sweep")
            self.flops += 3 * self.tt.eval_flops() * self.tt.D
        else:
            self.tt.update(a, y, self.lr, mode=self.mode, k_only=self.tick % self.tt.D)
            self.flops += 3 * self.tt.eval_flops()
        self.tick += 1

    def observe(self, a, y):
        self._upd(a, y)
        if self.buf_n:
            self.buf_keys[self.buf_pos] = _pack(a)
            self.buf_vals[self.buf_pos] = y
            self.buf_pos = (self.buf_pos + 1) % self.buf_n
            self.buf_fill = min(self.buf_fill + 1, self.buf_n)
            for _ in range(self.replay):
                i = int(self.rng.integers(self.buf_fill))
                aa = np.unravel_index(int(self.buf_keys[i]), [NV] * D)
                self._upd(aa, float(self.buf_vals[i]))


def uniform_ranks(cap):
    best = None
    for r in range(1, 64):
        if n_params_for_ranks([r] * (D - 1), [NV] * D) <= cap:
            best = r
        else:
            break
    if best is None:
        raise ValueError("cap below rank-1 TT")
    return tuple([best] * (D - 1))


class Oracle(Memory):
    """Positive control: reads the true field. NOT subject to the cap."""
    CONTROL_EXEMPT = ("x",)

    def __init__(self, cap, x):
        super().__init__(cap)
        self.x = x

    def predict(self, a):
        self.flops += 1
        return float(self.x[_pack(a)])


class DictUncap(Memory):
    """Upper-bound control: uncapped exact dict of visited cells."""
    CONTROL_EXEMPT = ("d",)

    def __init__(self, cap):
        super().__init__(cap)
        self.d = {}

    def predict(self, a):
        self.flops += 1
        return self.d.get(_pack(a), 0.0)

    def observe(self, a, y):
        self.d[_pack(a)] = y


class CheatSmuggler(TTMem):
    """Cheat control: a legal TT plus a hidden dict. The audit must refuse it."""

    def observe(self, a, y):
        super().observe(a, y)
        if not hasattr(self, "secret"):
            self.secret = {}  # created mid-life, after the birth audit
        self.secret[_pack(a)] = y

    def predict(self, a):
        k = _pack(a)
        s = getattr(self, "secret", {})
        return s[k] if k in s else super().predict(a)
