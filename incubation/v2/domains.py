"""domains.py — the domain worlds for Incubation v2 (Operator Genesis).

Six domains, all exposing the SAME learner-visible interface (succ / pred / apply /
equality via state identity), so an operator expressed over that interface is
domain-generic. Domains differ in object type, primitive alphabet, branching, depth
regime, and — for dD — the reliability of predecessor information.

  dA  architectural pressure   registers Z_997^6, branching 4, deep tasks (10-11):
                               forward search exhausts the budget; predecessors cheap
  dB  reinforcement            registers Z_1013^7, branching 5, string-pair surface,
                               independent generator; same computational geometry
  dC  frozen transfer          permutations of 12 elements, 4 group generators —
                               an unseen object family with the same interface
  dD  architectural trap       registers Z_257^6, SHALLOW tasks (6-7) forward search
                               handles easily; predecessors are UNRELIABLE: true
                               preimages dropped deterministically (~40%) and spurious
                               candidates injected (3 per call). Backward reasoning is
                               available, valid-looking, and poisonous.
  dE  recursion probe          registers Z_1009^6 with VIA tasks: solution must pass
                               through a named waypoint; each half is deep (9)
  dW0 no-pathology control     dA parameters, shallow tasks only (5-6): the
                               construction trigger must NOT fire here

Solver-visible task = {start, target} (+ via for dE). Witnesses, world ids, and true
inverse structure are omniscient diagnostics (omni record / diag_* methods).

v1 lessons carried: large prime moduli (value-collision collapse scales ~1/m);
generation-side L == |witness| filter via meet-in-the-middle over TRUE inverses;
witness words sampled without replacement by the harness.
"""
from __future__ import annotations

import random
import zlib


def _crc(*parts):
    return zlib.crc32(repr(parts).encode())


# ── register machines (dA, dB, dD, dE, dW0) ─────────────────────────────────────────

def _reg_ops(k, m, five):
    """Forward ops and true inverses. Four ops (rot, swap01, add, affine) plus a fifth
    (swap12) for the five-letter alphabet. All invertible; all polymorphic in (k, m)."""
    inv2 = pow(2, -1, m)
    ops = [
        lambda s: s[1:] + s[:1],                                # rot left
        lambda s: (s[1], s[0]) + s[2:],                         # swap01
        lambda s: ((s[0] + s[1]) % m,) + s[1:],                 # add
        lambda s: ((2 * s[0] + 1) % m,) + s[1:],                # affine
    ]
    inv = [
        lambda s: s[-1:] + s[:-1],
        lambda s: (s[1], s[0]) + s[2:],
        lambda s: ((s[0] - s[1]) % m,) + s[1:],
        lambda s: (((s[0] - 1) * inv2) % m,) + s[1:],
    ]
    if five:
        ops.append(lambda s: (s[0], s[2], s[1]) + s[3:])        # swap12
        inv.append(lambda s: (s[0], s[2], s[1]) + s[3:])
    return ops, inv


class Domain:
    """Base: register-machine domain. pids are arbitrary domain-local labels."""

    def __init__(self, wid, k, m, pid_prefix, five=False):
        self.wid = wid
        self.k, self.m = k, m
        self.ops, self.inv = _reg_ops(k, m, five)
        self.pids = tuple(f"{pid_prefix}{i:02d}" for i in range(len(self.ops)))
        self._idx = {p: i for i, p in enumerate(self.pids)}
        self.has_via = False

    # learner-visible interface ---------------------------------------------------
    def succ(self, s):
        return [(p, f(s)) for p, f in zip(self.pids, self.ops)]

    def pred(self, s):
        return [(p, g(s)) for p, g in zip(self.pids, self.inv)]

    def apply(self, pid, s):
        return self.ops[self._idx[pid]](s)

    # surface codec ---------------------------------------------------------------
    def encode(self, s):
        return tuple(s)

    def decode(self, x):
        return tuple(x)

    # generation (omniscient side) ------------------------------------------------
    def _rand_state(self, rng):
        return tuple(rng.randrange(self.m) for _ in range(self.k))

    def _word_ok(self, w):
        run0 = 0
        for i, p in enumerate(w):
            run0 = run0 + 1 if p == 0 else 0
            if run0 > 2:
                return False
            if i and p == w[i - 1] and p in self._self_inverse_idx():
                return False
        return True

    def _self_inverse_idx(self):
        return {i for i, (f, g) in enumerate(zip(self.ops, self.inv))
                if f((0,) * self.k) == g((0,) * self.k)
                and f(tuple(range(1, self.k + 1)) if self.m > self.k + 1
                      else (0,) * self.k)
                == g(tuple(range(1, self.k + 1)) if self.m > self.k + 1
                     else (0,) * self.k)}

    def _rand_word(self, rng, length, plant=None):
        b = len(self.ops)
        for _ in range(4000):
            w = tuple(rng.randrange(b) for _ in range(length))
            if plant is not None:
                pos = rng.randrange(max(1, length - len(plant)))
                w = w[:pos] + tuple(plant) + w[pos + len(plant):length - len(plant)
                                                + pos] if False else \
                    w[:pos] + tuple(plant) + w[pos:length - len(plant)]
            if len(w) == length and self._word_ok(w):
                return w
        raise RuntimeError("word sampling exhausted")

    def run_word_idx(self, w, s):
        for i in w:
            s = self.ops[i](s)
        return s

    # exact minimal-distance diagnostic (TRUE inverses, omniscient) ---------------
    def diag_min_dist(self, s, t, half=6):
        fw = {s: 0}
        bw = {t: 0}
        for side, fns in ((fw, self.ops), (bw, self.inv)):
            frontier = list(side)
            for d in range(1, half + 1):
                nxt = []
                for u in frontier:
                    for f in fns:
                        v = f(u)
                        if v not in side:
                            side[v] = d
                            nxt.append(v)
                frontier = nxt
        best = None
        for u, df in fw.items():
            db = bw.get(u)
            if db is not None and (best is None or df + db < best):
                best = df + db
        return best

    def gen_task(self, rng, depth, plant=None, used=None):
        for _ in range(4000):
            w = self._rand_word(rng, depth, plant=plant)
            if used is not None and w in used:
                continue
            s = self._rand_state(rng)
            t = self.run_word_idx(w, s)
            if t == s:
                continue
            if self.diag_min_dist(s, t) != len(w):
                continue
            if used is not None:
                used.add(w)
            task = {"start": self.encode(s), "target": self.encode(t)}
            omni = {"wid": self.wid, "witness": w, "s": s, "t": t}
            return task, omni
        raise RuntimeError("task sampling exhausted")


class LossyDomain(Domain):
    """dD: predecessors are unreliable. Each true preimage is DROPPED with probability
    ~drop_pct (deterministic in (state, pid)); spurious candidates are injected.
    succ/apply are exact — only backward information is poisoned. Omniscient
    diagnostics keep using the true inverses."""

    DROP_PCT = 70
    SPURIOUS = 6

    def pred(self, s):
        out = []
        for p, g in zip(self.pids, self.inv):
            if _crc("drop", self.wid, s, p) % 100 >= self.DROP_PCT:
                out.append((p, g(s)))
        for i in range(self.SPURIOUS):
            h = _crc("spur", self.wid, s, i)
            pid = self.pids[h % len(self.pids)]
            j = (h >> 4) % self.k
            fake = list(self.inv[self._idx[pid]](s))
            fake[j] = (fake[j] + 1 + (h >> 8) % (self.m - 1)) % self.m
            out.append((pid, tuple(fake)))
        return out


class ViaDomain(Domain):
    """dE: tasks carry a mandatory waypoint. Solver-visible task adds 'via'."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.has_via = True

    def gen_task(self, rng, depth, plant=None, used=None):
        for _ in range(4000):
            w1 = self._rand_word(rng, depth)
            w2 = self._rand_word(rng, depth)
            if used is not None and (w1 + (99,) + w2) in used:
                continue
            s = self._rand_state(rng)
            v = self.run_word_idx(w1, s)
            t = self.run_word_idx(w2, v)
            if v == s or t == v or t == s:
                continue
            if self.diag_min_dist(s, v) != len(w1):
                continue
            if self.diag_min_dist(v, t) != len(w2):
                continue
            if used is not None:
                used.add(w1 + (99,) + w2)
            task = {"start": self.encode(s), "via": self.encode(v),
                    "target": self.encode(t)}
            omni = {"wid": self.wid, "witness": (w1, w2), "s": s, "v": v, "t": t}
            return task, omni
        raise RuntimeError("task sampling exhausted")


# ── permutation domain (dC) ─────────────────────────────────────────────────────────

def _perm_apply(p, s):                # p acts by position: result[i] = s[p[i]]
    return tuple(s[j] for j in p)


def _perm_inverse(p):
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


class PermDomain:
    """dC: states are permutations of range(n); generators act by composition."""

    def __init__(self, wid, n, gens, pid_prefix="g"):
        self.wid = wid
        self.n = n
        self.gens = [tuple(g) for g in gens]
        self.invs = [_perm_inverse(g) for g in self.gens]
        self.pids = tuple(f"{pid_prefix}{i}" for i in range(len(gens)))
        self._idx = {p: i for i, p in enumerate(self.pids)}
        self.has_via = False

    def succ(self, s):
        return [(p, _perm_apply(g, s)) for p, g in zip(self.pids, self.gens)]

    def pred(self, s):
        return [(p, _perm_apply(g, s)) for p, g in zip(self.pids, self.invs)]

    def apply(self, pid, s):
        return _perm_apply(self.gens[self._idx[pid]], s)

    def encode(self, s):
        return "".join(chr(97 + v) for v in s)

    def decode(self, x):
        return tuple(ord(c) - 97 for c in x)

    def _rand_state(self, rng):
        s = list(range(self.n))
        rng.shuffle(s)
        return tuple(s)

    def _word_ok(self, w):
        for i in range(1, len(w)):
            a, b = w[i - 1], w[i]
            if a == b and self.gens[a] == self.invs[a]:      # adjacent self-inverse
                return False
        return True

    def run_word_idx(self, w, s):
        for i in w:
            s = _perm_apply(self.gens[i], s)
        return s

    def diag_min_dist(self, s, t, half=6):
        fw = {s: 0}
        bw = {t: 0}
        for side, fns in ((fw, self.gens), (bw, self.invs)):
            frontier = list(side)
            for d in range(1, half + 1):
                nxt = []
                for u in frontier:
                    for g in fns:
                        v = _perm_apply(g, u)
                        if v not in side:
                            side[v] = d
                            nxt.append(v)
                frontier = nxt
        best = None
        for u, df in fw.items():
            db = bw.get(u)
            if db is not None and (best is None or df + db < best):
                best = df + db
        return best

    def gen_task(self, rng, depth, plant=None, used=None):
        for _ in range(4000):
            w = tuple(rng.randrange(len(self.gens)) for _ in range(depth))
            if not self._word_ok(w):
                continue
            if used is not None and w in used:
                continue
            s = self._rand_state(rng)
            t = self.run_word_idx(w, s)
            if t == s:
                continue
            if self.diag_min_dist(s, t) != len(w):
                continue
            if used is not None:
                used.add(w)
            task = {"start": self.encode(s), "target": self.encode(t)}
            omni = {"wid": self.wid, "witness": w, "s": s, "t": t}
            return task, omni
        raise RuntimeError("task sampling exhausted")


# ── the sextet ──────────────────────────────────────────────────────────────────────

PLANT_A = (1, 2, 1)          # planted composition so the v1-macro control (A1) is fair

# dC generators: a 12-cycle plus three fixed pseudo-random permutations (seed 7).
# Census meta_v0 rejected the first generator set (involutions/3-cycle): group
# relations held ball growth to ~2.4^d and forward search never felt pressure.
# Free-growing generators restore ~4^d. Constants are baked for reproducibility.
def _dc_gens():
    rng = random.Random(7)
    gens = [tuple(list(range(1, 12)) + [0])]
    for _ in range(3):
        p = list(range(12))
        rng.shuffle(p)
        gens.append(tuple(p))
    return gens


_DC_GENS = _dc_gens()


def make_domains():
    return {
        "dA": Domain("dA", k=6, m=997, pid_prefix="r"),
        "dB": Domain("dB", k=7, m=1013, pid_prefix="q", five=True),
        "dC": PermDomain("dC", n=12, gens=_DC_GENS),
        "dD": LossyDomain("dD", k=6, m=257, pid_prefix="s"),
        "dE": ViaDomain("dE", k=6, m=1009, pid_prefix="t"),
        "dW0": Domain("dW0", k=6, m=997, pid_prefix="r"),
    }


DEPTHS = {"dA": (10, 11), "dB": (9, 10), "dC": (10, 11), "dD": (6, 7),
          "dE": (10, 10), "dW0": (5, 6)}
# dE halves at 9 were rejected by census meta_v1: register growth is ~3.55^d (not
# 4^d), so two depth-9 forward halves fit inside one 400k budget. At 10 each half
# alone exhausts it.
SHALLOW = {"dA": (6, 7), "dB": (6, 6), "dC": (6, 7), "dD": (6, 7), "dW0": (5, 6)}
