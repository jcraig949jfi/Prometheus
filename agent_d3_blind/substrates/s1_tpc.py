"""S1 TPC -- typed point-free (combinatory) calculus.

Base types: L (int sequence), N (int).  Morphism types: LL, NN, LN.
A program is a prefix-encoded well-typed term of type LL, serialised as a tuple
of ints in [0, 511]; token = opslot + 64*arg with arg in 0..7.

Validity is a real predicate (a random tuple is almost never well-typed), but the
frozen mutation process is type-directed, so validity is closed under mutation
by construction.  That contrast is the point of including this basis.
"""
from . import common
from .common import Fuel, clampv, clampl, PROG_MAX

NAME = "S1"
NSLOT = 64
NARG = 8
FUEL = 400

# slot -> (name, type, child types)
OPS = {
    0:  ("ID", "LL", ()),
    1:  ("COMP", "LL", ("LL", "LL")),
    2:  ("MAP", "LL", ("NN",)),
    3:  ("REV", "LL", ()),
    4:  ("TAIL", "LL", ()),
    5:  ("INIT", "LL", ()),
    6:  ("ROT", "LL", ()),
    7:  ("TAKE", "LL", ()),
    8:  ("DROP", "LL", ()),
    9:  ("SELFCAT", "LL", ()),
    10: ("SCAN", "LL", ("NN",)),
    11: ("COND", "LL", ("LN", "LL", "LL")),
    12: ("ITER", "LL", ("LN", "LL")),
    13: ("PUSHK", "LL", ()),
    14: ("SETAT", "LL", ("NN",)),
    15: ("SWAPAT", "LL", ()),
    16: ("NID", "NN", ()),
    17: ("NADD", "NN", ()),
    18: ("NMUL", "NN", ()),
    19: ("NMOD", "NN", ()),
    20: ("NNEG", "NN", ()),
    21: ("NCOMP", "NN", ("NN", "NN")),
    22: ("LEN", "LN", ()),
    23: ("SUM", "LN", ()),
    24: ("HEAD", "LN", ()),
    25: ("LAST", "LN", ()),
    26: ("MAXN", "LN", ()),
    27: ("PIPE", "LN", ("LL", "LN")),
    28: ("NOFL", "LN", ("LN", "NN")),
}
BY_TYPE = {"LL": [], "NN": [], "LN": []}
LEAF_BY_TYPE = {"LL": [], "NN": [], "LN": []}
for _s, (_n, _t, _c) in OPS.items():
    BY_TYPE[_t].append(_s)
    if not _c:
        LEAF_BY_TYPE[_t].append(_s)

# ---- canonical order permutation (set per run; order 0 = identity) ----
_PERM = list(range(NSLOT))
_IPERM = list(range(NSLOT))
_PERMA = list(range(NARG))
_IPERMA = list(range(NARG))
_DECODE_CACHE = {}


def set_order(perm_slot, perm_arg):
    global _PERM, _IPERM, _PERMA, _IPERMA, _DECODE_CACHE
    _PERM = list(perm_slot)
    _IPERM = [0] * NSLOT
    for i, v in enumerate(_PERM):
        _IPERM[v] = i
    _PERMA = list(perm_arg)
    _IPERMA = [0] * NARG
    for i, v in enumerate(_PERMA):
        _IPERMA[v] = i
    _DECODE_CACHE = {}


def _tok(slot, arg):
    return _IPERM[slot] + NSLOT * _IPERMA[arg % NARG]


def _untok(t):
    return _PERM[t % NSLOT], _PERMA[(t // NSLOT) % NARG]


# ---- term <-> tokens ----
def _parse(toks, i, ty):
    if i >= len(toks):
        return None, i
    t = toks[i]
    if t < 0 or t >= NSLOT * NARG:
        return None, i
    slot, arg = _untok(t)
    if slot not in OPS:
        return None, i
    name, oty, cts = OPS[slot]
    if oty != ty:
        return None, i
    i += 1
    kids = []
    for ct in cts:
        k, i = _parse(toks, i, ct)
        if k is None:
            return None, i
        kids.append(k)
    return (slot, arg, tuple(kids)), i


def decode(prog):
    c = _DECODE_CACHE.get(prog)
    if c is not None:
        return c[0]
    tree = None
    if 0 < len(prog) <= PROG_MAX:
        tr, i = _parse(prog, 0, "LL")
        if tr is not None and i == len(prog):
            tree = tr
    if len(_DECODE_CACHE) < 200000:
        _DECODE_CACHE[prog] = (tree,)
    return tree


def encode(tree):
    out = []
    stack = [tree]
    # prefix order
    def emit(nd):
        out.append(_tok(nd[0], nd[1]))
        for k in nd[2]:
            emit(k)
    emit(tree)
    return tuple(out)


def size(tree):
    return 1 + sum(size(k) for k in tree[2])


def is_valid(prog):
    if not isinstance(prog, tuple) or not (0 < len(prog) <= PROG_MAX):
        return False
    for t in prog:
        if t < 0 or t >= NSLOT * NARG:
            return False
    return decode(prog) is not None


# ---- evaluation ----
def _evL(nd, x, st):
    st[0] -= 1
    if st[0] < 0:
        raise Fuel()
    slot, arg, kids = nd
    if slot == 0:
        return x
    if slot == 1:
        return _evL(kids[1], _evL(kids[0], x, st), st)
    if slot == 2:
        return tuple(_evN(kids[0], v, st) for v in x)
    if slot == 3:
        return x[::-1]
    if slot == 4:
        return x[1:]
    if slot == 5:
        return x[:-1]
    if slot == 6:
        if not x:
            return x
        k = arg % len(x)
        return x[k:] + x[:k]
    if slot == 7:
        return x[:arg + 1]
    if slot == 8:
        return x[arg:]
    if slot == 9:
        return clampl(x + x)
    if slot == 10:
        acc = 0
        out = []
        for v in x:
            acc = clampv(_evN(kids[0], clampv(acc + v), st))
            out.append(acc)
        return tuple(out)
    if slot == 11:
        return _evL(kids[1], x, st) if _evN_num(kids[0], x, st) != 0 else _evL(kids[2], x, st)
    if slot == 12:
        n = _evN_num(kids[0], x, st) % 4
        for _ in range(n):
            x = _evL(kids[1], x, st)
        return x
    if slot == 13:
        return clampl(x + (arg - 4,))
    if slot == 14:
        if not x:
            return x
        i = arg % len(x)
        return x[:i] + (clampv(_evN(kids[0], x[i], st)),) + x[i + 1:]
    if slot == 15:
        if len(x) < 2:
            return x
        i = arg % len(x)
        j = (i + 1) % len(x)
        y = list(x)
        y[i], y[j] = y[j], y[i]
        return tuple(y)
    raise Fuel()


def _evN(nd, n, st):
    st[0] -= 1
    if st[0] < 0:
        raise Fuel()
    slot, arg, kids = nd
    if slot == 16:
        return n
    if slot == 17:
        return clampv(n + (arg - 4))
    if slot == 18:
        return clampv(n * ((arg % 5) - 2))
    if slot == 19:
        return n % ((arg % 6) + 2)
    if slot == 20:
        return clampv(-n)
    if slot == 21:
        return _evN(kids[1], _evN(kids[0], n, st), st)
    raise Fuel()


def _evN_num(nd, x, st):
    st[0] -= 1
    if st[0] < 0:
        raise Fuel()
    slot, arg, kids = nd
    if slot == 22:
        return len(x)
    if slot == 23:
        return clampv(sum(x))
    if slot == 24:
        return x[0] if x else 0
    if slot == 25:
        return x[-1] if x else 0
    if slot == 26:
        return max(x) if x else 0
    if slot == 27:
        return _evN_num(kids[1], _evL(kids[0], x, st), st)
    if slot == 28:
        return _evN(kids[1], _evN_num(kids[0], x, st), st)
    raise Fuel()


def run(prog, inp):
    common.METER["runs"] += 1
    tree = decode(prog)
    if tree is None:
        return None, "invalid"
    st = [FUEL]
    try:
        out = _evL(tree, tuple(inp), st)
    except Fuel:
        return None, "timeout"
    except RecursionError:
        return None, "timeout"
    return clampl(out), "ok"


# ---- generic construction ----
def gen(ty, budget, rng):
    if budget <= 1 or rng.random() < 0.22:
        slot = rng.choice(LEAF_BY_TYPE[ty])
        return (slot, rng.randrange(NARG), ())
    slot = rng.choice(BY_TYPE[ty])
    cts = OPS[slot][2]
    if not cts:
        return (slot, rng.randrange(NARG), ())
    rem = budget - 1
    kids = []
    for idx, ct in enumerate(cts):
        share = max(1, rem // (len(cts) - idx))
        kids.append(gen(ct, share, rng))
        rem -= size(kids[-1])
        rem = max(rem, 0)
    return (slot, rng.randrange(NARG), tuple(kids))


def random_program(rng, size_hint=8):
    for _ in range(60):
        tr = gen("LL", size_hint, rng)
        if size(tr) <= PROG_MAX:
            p = encode(tr)
            if len(p) <= PROG_MAX:
                return p
    return encode((0, 0, ()))


def random_tokens(rng, n):
    return tuple(rng.randrange(0, NSLOT * NARG) for _ in range(n))
