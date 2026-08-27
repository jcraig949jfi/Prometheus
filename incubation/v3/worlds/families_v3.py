"""families_v3.py — domain worlds for Incubation v3 (Lens Genesis).

One shared ABSTRACT primitive alphabet, instantiated per domain family. The abstract
pids are arbitrary and their assignment to roles is deliberately SCRAMBLED
(non-contiguous), so no naming or ordering convention leaks the intended grouping:

    u00 u03 u06   block-1 local ops   (rot / swap / add on that block)
    u01 u04 u07   block-2 local ops
    u02 u05       decoys: genuinely cross-block transformations
    u08 u09 u10   block-3 local ops   (vE only)
    u11           third decoy         (vE only)

The above table is OMNISCIENT documentation. Nothing solver- or learner-visible
carries it; the learner sees pids as opaque strings and must discover structure by
execution. Decoys are real, invertible transformations whose support spans blocks —
including one in any group makes that group's support overlap everything, and clean-
world witnesses never need them (vD witnesses DO).

Domains:
  vA   registers Z_997^8, blocks {0..3}/{4..7}; pressure (deep joint tasks)
  vB   registers Z_1013^9, blocks scrambled across odd/even slots, string surface
  vC   pairs of permutations of 9, presented as one interleaved letter string
  vD   vA-like registers Z_257^8; witnesses REQUIRE a decoy (representation trap)
  vE   registers Z_1009^12, three blocks, three new local ops + a new decoy
  vW0  registers Z_997^8 with NO decoys, shallow tasks (no-pathology control)

Tasks are {start, target}; witnesses are omniscient. Generation filters: per-block
minimality of each block witness (exact meet-in-the-middle over that block's ops).
Joint minimality is NOT enforced (branching 8 makes it infeasible) and no claim
rests on it: all cost/solve comparisons are measured per task on the same tasks.
"""
from __future__ import annotations

import random

BLOCK1 = ("u00", "u03", "u06")
BLOCK2 = ("u01", "u04", "u07")
BLOCK3 = ("u08", "u09", "u10")
DECOYS = ("u02", "u05")
DECOY3 = "u11"


def _reg_ops(m, blocks, heavy_decoys=False):
    """Instantiate abstract pids over register states. blocks: dict block_idx ->
    tuple of slot indices. Returns pid -> (fn, inv_fn)."""
    inv2 = pow(2, -1, m)

    def rot(sl):
        def f(s):
            t = list(s)
            vals = [s[i] for i in sl]
            for j, i in enumerate(sl):
                t[i] = vals[(j + 1) % len(sl)]
            return tuple(t)

        def g(s):
            t = list(s)
            vals = [s[i] for i in sl]
            for j, i in enumerate(sl):
                t[i] = vals[(j - 1) % len(sl)]
            return tuple(t)
        return f, g

    def swap(sl):
        a, b = sl[0], sl[1]

        def f(s):
            t = list(s)
            t[a], t[b] = t[b], t[a]
            return tuple(t)
        return f, f

    def add(sl):
        a, b = sl[0], sl[1]

        def f(s):
            t = list(s)
            t[a] = (t[a] + t[b]) % m
            return tuple(t)

        def g(s):
            t = list(s)
            t[a] = (t[a] - t[b]) % m
            return tuple(t)
        return f, g

    def dswap(i, j):
        def f(s):
            t = list(s)
            t[i], t[j] = t[j], t[i]
            return tuple(t)
        return f, f

    def dmix(i, j):
        def f(s):
            t = list(s)
            t[i] = (2 * s[i] + s[j]) % m
            t[j] = (s[j] + 1) % m
            return tuple(t)

        def g(s):
            t = list(s)
            t[j] = (s[j] - 1) % m
            t[i] = ((s[i] - t[j]) * inv2) % m
            return tuple(t)
        return f, g

    b1, b2 = blocks[0], blocks[1]
    ops = {
        "u00": rot(b1), "u03": swap(b1), "u06": add(b1),
        "u01": rot(b2), "u04": swap(b2), "u07": add(b2),
        "u02": dswap(b1[0], b2[0]), "u05": dmix(b2[1], b1[1]),
    }
    if heavy_decoys:
        # vD instantiation: the decoys are single primitives whose effect is a long
        # baked composition of block ops plus cross swaps — ONE action in the joint
        # space, a near-diameter displacement in each block's space. (Census lens_v1
        # rejected light decoys: two insertions displaced block targets only ~16
        # steps, which block-bidirectional absorbed at the same cost R2 paid.)
        def compose(seq):
            def f(s):
                for fn, _ in seq:
                    s = fn(s)
                return s

            def g(s):
                for _, gn in reversed(seq):
                    s = gn(s)
                return s
            return f, g
        base = [ops["u06"], ops["u00"], ops["u07"], ops["u01"],
                (dswap(b1[0], b2[0])), ops["u03"], ops["u06"], ops["u04"],
                ops["u07"], (dswap(b1[1], b2[1]))]
        ops["u02"] = compose(base * 3)
        ops["u05"] = compose([(dswap(b1[2], b2[2]))] + base * 2 + [ops["u06"]])
    if len(blocks) > 2:
        b3 = blocks[2]
        ops.update({"u08": rot(b3), "u09": swap(b3), "u10": add(b3),
                    "u11": dmix(b3[0], b1[0])})
    return ops


class RegDomain:
    def __init__(self, wid, k, m, blocks, pids, decoys, string_surface=False,
                 heavy_decoys=False):
        self.wid = wid
        self.k, self.m = k, m
        self.blocks = blocks                      # omniscient
        self._ops = _reg_ops(m, blocks, heavy_decoys=heavy_decoys)
        self.pids = tuple(pids)                   # learner-visible alphabet
        self.decoys = tuple(decoys)               # omniscient
        self._string = string_surface

    # learner-visible interface (matches the v2 runtime contract) ---------------
    def succ(self, s):
        return [(p, self._ops[p][0](s)) for p in self.pids]

    def pred(self, s):
        return [(p, self._ops[p][1](s)) for p in self.pids]

    def apply(self, pid, s):
        return self._ops[pid][0](s)

    def encode(self, s):
        if self._string:
            return "".join(chr(97 + v // 26) + chr(97 + v % 26) for v in s)
        return tuple(s)

    def decode(self, x):
        if self._string:
            return tuple((ord(x[i]) - 97) * 26 + (ord(x[i + 1]) - 97)
                         for i in range(0, len(x), 2))
        return tuple(x)

    # generation (omniscient) ---------------------------------------------------
    def _rand_state(self, rng):
        return tuple(rng.randrange(self.m) for _ in range(self.k))

    def _block_pids(self, bi):
        return {0: BLOCK1, 1: BLOCK2, 2: BLOCK3}[bi]

    def _block_min_dist(self, s, t, bi, half=5):
        ops = [self._ops[p][0] for p in self._block_pids(bi)]
        inv = [self._ops[p][1] for p in self._block_pids(bi)]
        fw, bw = {s: 0}, {t: 0}
        for side, fns in ((fw, ops), (bw, inv)):
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

    def _block_word(self, rng, bi, depth):
        pids = self._block_pids(bi)
        for _ in range(2000):
            w = [pids[rng.randrange(3)] for _ in range(depth)]
            ok = True
            for i in range(1, depth):
                if w[i] == w[i - 1] and w[i] in (pids[1],):      # adjacent swap-swap
                    ok = False
                    break
            if ok:
                return w
        raise RuntimeError("block word sampling exhausted")

    def run_word(self, word, s):
        for pid in word:
            s = self._ops[pid][0](s)
        return s

    def gen_task(self, rng, block_depth, n_blocks=2, decoy_uses=0, used=None):
        for _ in range(3000):
            words = [self._block_word(rng, bi, block_depth)
                     for bi in range(n_blocks)]
            s = self._rand_state(rng)
            ok = True
            for bi, w in enumerate(words):
                t_b = self.run_word(w, s)
                if self._block_min_dist(s, t_b, bi,
                                        half=(block_depth + 3) // 2 + 1) \
                        != len(w):
                    ok = False
                    break
            if not ok:
                continue
            joint = []
            pools = [list(w) for w in words]
            while any(pools):
                bi = rng.choice([i for i, p in enumerate(pools) if p])
                joint.append(pools[bi].pop(0))
            for _ in range(decoy_uses):
                pos = rng.randrange(len(joint) + 1)
                joint.insert(pos, self.decoys[rng.randrange(len(self.decoys))])
            if used is not None and tuple(joint) in used:
                continue
            t = self.run_word(joint, s)
            if t == s:
                continue
            if used is not None:
                used.add(tuple(joint))
            task = {"start": self.encode(s), "target": self.encode(t)}
            omni = {"wid": self.wid, "witness": tuple(joint), "s": s, "t": t}
            return task, omni
        raise RuntimeError("task sampling exhausted")


# ── permutation-pair family (vC) ────────────────────────────────────────────────────

def _perm_apply_range(p, s, lo, n):
    seg = s[lo:lo + n]
    return s[:lo] + tuple(seg[j] for j in p) + s[lo + n:]


def _perm_inverse(p):
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


class PermPairDomain:
    """States: concatenation of two permutations of range(n). Block-1 ops act on the
    first, block-2 on the second; decoys act across both."""

    def __init__(self, wid, n, seed=17):
        self.wid = wid
        self.n = n
        self.k = 2 * n
        rng = random.Random(seed)

        def randperm():
            p = list(range(n))
            rng.shuffle(p)
            return tuple(p)
        g1 = [tuple(list(range(1, n)) + [0]), randperm(), randperm()]
        g2 = [tuple(list(range(1, n)) + [0]), randperm(), randperm()]
        self._gens = {}
        for pid, g in zip(BLOCK1, g1):
            self._gens[pid] = ("L", g, _perm_inverse(g))
        for pid, g in zip(BLOCK2, g2):
            self._gens[pid] = ("R", g, _perm_inverse(g))
        self._gens["u02"] = ("X", None, None)         # exchange the two objects
        fixed = randperm()
        self._gens["u05"] = ("B", fixed, _perm_inverse(fixed))   # apply to both
        self.pids = BLOCK1 + BLOCK2 + DECOYS
        self.decoys = DECOYS
        self.blocks = (tuple(range(n)), tuple(range(n, 2 * n)))   # omniscient

    def _do(self, pid, s, inv=False):
        kind, g, gi = self._gens[pid]
        p = gi if inv else g
        if kind == "L":
            return _perm_apply_range(p, s, 0, self.n)
        if kind == "R":
            return _perm_apply_range(p, s, self.n, self.n)
        if kind == "X":
            return s[self.n:] + s[:self.n]
        return _perm_apply_range(p, _perm_apply_range(p, s, 0, self.n),
                                 s and self.n, self.n) if False else \
            _perm_apply_range(p, _perm_apply_range(p, s, 0, self.n), self.n, self.n)

    def succ(self, s):
        return [(p, self._do(p, s)) for p in self.pids]

    def pred(self, s):
        return [(p, self._do(p, s, inv=True)) for p in self.pids]

    def apply(self, pid, s):
        return self._do(pid, s)

    def encode(self, s):
        return "".join(chr(97 + v) for v in s)

    def decode(self, x):
        return tuple(ord(c) - 97 for c in x)

    def _rand_state(self, rng):
        a = list(range(self.n))
        b = list(range(self.n))
        rng.shuffle(a)
        rng.shuffle(b)
        return tuple(a) + tuple(b)

    def _block_min_dist(self, s, t, bi, half=5):
        pids = (BLOCK1, BLOCK2)[bi]
        fw, bw = {s: 0}, {t: 0}
        for side, inv in ((fw, False), (bw, True)):
            frontier = list(side)
            for d in range(1, half + 1):
                nxt = []
                for u in frontier:
                    for pid in pids:
                        v = self._do(pid, u, inv=side is bw)
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

    def run_word(self, word, s):
        for pid in word:
            s = self._do(pid, s)
        return s

    def gen_task(self, rng, block_depth, n_blocks=2, decoy_uses=0, used=None):
        for _ in range(3000):
            words = [[(BLOCK1, BLOCK2)[bi][rng.randrange(3)]
                      for _ in range(block_depth)] for bi in range(2)]
            s = self._rand_state(rng)
            ok = True
            for bi, w in enumerate(words):
                t_b = self.run_word(w, s)
                if self._block_min_dist(s, t_b, bi,
                                        half=(block_depth + 3) // 2 + 1) \
                        != len(w):
                    ok = False
                    break
            if not ok:
                continue
            joint = []
            pools = [list(w) for w in words]
            while any(pools):
                bi = rng.choice([i for i, p in enumerate(pools) if p])
                joint.append(pools[bi].pop(0))
            if used is not None and tuple(joint) in used:
                continue
            t = self.run_word(joint, s)
            if t == s:
                continue
            if used is not None:
                used.add(tuple(joint))
            task = {"start": self.encode(s), "target": self.encode(t)}
            omni = {"wid": self.wid, "witness": tuple(joint), "s": s, "t": t}
            return task, omni
        raise RuntimeError("task sampling exhausted")


# ── the sextet ──────────────────────────────────────────────────────────────────────

STD_PIDS = BLOCK1 + BLOCK2 + DECOYS


def make_domains():
    return {
        "vA": RegDomain("vA", 8, 997, ((0, 1, 2, 3), (4, 5, 6, 7)),
                        STD_PIDS, DECOYS),
        "vB": RegDomain("vB", 9, 1013, ((0, 2, 4, 6), (1, 3, 5, 7, 8)),
                        STD_PIDS, DECOYS, string_surface=True),
        "vC": PermPairDomain("vC", 9),
        "vD": RegDomain("vD", 8, 257, ((0, 1, 2, 3), (4, 5, 6, 7)),
                        STD_PIDS, DECOYS, heavy_decoys=True),
        "vE": RegDomain("vE", 12, 1009,
                        ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11)),
                        BLOCK1 + BLOCK2 + BLOCK3 + DECOYS + (DECOY3,),
                        DECOYS + (DECOY3,)),
        "vW0": RegDomain("vW0", 8, 997, ((0, 1, 2, 3), (4, 5, 6, 7)),
                         BLOCK1 + BLOCK2, ()),
    }


# vC at block depth 6 was rejected by census lens_v0: joint bidirectional solved
# 5/5 deep permutation tasks at ~208k ops. Depth 7 puts the joint problem past the
# meter while per-block search stays trivial.
BLOCK_DEPTHS = {"vA": 7, "vB": 7, "vC": 7, "vD": 4, "vE": 5, "vW0": 3}
SHALLOW_BLOCK = {"vA": 3, "vB": 3, "vC": 3, "vD": 4, "vE": 3, "vW0": 3}
