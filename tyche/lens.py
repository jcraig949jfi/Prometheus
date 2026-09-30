"""LENS: executable, serialisable, mutable perceptual transformations.

A lens genome is a register program over time series:

    {"ins": [[op, [arg regs], param], ...], "out": [reg, ...]}

Registers 0..NIN-1 are virtual input channels (virtual channel c reads world
channel c % d, so every lens runs on every world). Instruction i writes
register NIN + i. Every op is CAUSAL: output at t depends only on inputs at
times <= t (audited in tyche.audits.causality_audit). Output Z is the stack of
the registers named in "out" (1..KMAX columns).

Nothing here knows what a lens "means". Introns (instructions outside every
output cone) are kept as neutral genetic material; effective length is
reported separately and nothing is simplified for legibility.

Charter primitive -> op mapping (v0 chemistry; the rest are backlog):
  index->input regs, delay->delay, window->wsum/wmax/wmin, differentiate->diff,
  accumulate/integrate->accmod/ewma, fold->fold, threshold->thresh,
  normalize->norm, rank->rank, sample->sample, compare->gt/eq, mix->add/sub,
  bind->mul/xor, hash->hash, branch/route->where, recur->fsm,
  correlate->wcorr, contract/max/min->max2/min2, sign/abs/neg (quantize-like).
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

try:
    from scipy.signal import lfilter
except Exception:  # pragma: no cover
    lfilter = None

NIN = 8
KMAX = 3
MAXLEN = 48
CLIP = 1e6


def _delay(x, k):
    y = np.zeros_like(x)
    y[k:] = x[:-k]
    return y


def _win(x, w):
    pad = np.concatenate([np.full(w - 1, x[0]), x])
    return sliding_window_view(pad, w)


def _wsum(x, w):
    c = np.cumsum(x)
    y = c.copy()
    y[w:] = c[w:] - c[:-w]
    return y


def _rank(x, w):
    v = _win(x, w)
    return (v < x[:, None]).sum(1).astype(float)


def _ewma(x, a):
    if lfilter is not None:
        return lfilter([1 - a], [1, -a], x)
    y = np.empty_like(x)
    s = 0.0
    for i, v in enumerate(x):
        s = a * s + (1 - a) * v
        y[i] = s
    return y


def _norm(x, w):
    v = _win(x, w)
    m = v.mean(1)
    sd = v.std(1)
    return (x - m) / np.where(sd > 1e-9, sd, 1.0)


def _sample(x, k):
    idx = (np.arange(len(x)) // k) * k
    return x[idx]


def _fsm(x, p):
    m, table = p[0], p[1]
    b = (x > 0.5).astype(np.int64)
    tab = np.asarray(table, dtype=np.int64).reshape(m, 2)
    y = np.empty(len(x))
    s = 0
    # sequential by nature (recurrent state); small tables, T ~ 1e4
    for i in range(len(x)):
        s = tab[s, b[i]]
        y[i] = s
    return y


def _wcorr(a, b, w):
    va, vb = _win(a, w), _win(b, w)
    ma, mb = va.mean(1), vb.mean(1)
    cov = ((va - ma[:, None]) * (vb - mb[:, None])).mean(1)
    sa, sb = va.std(1), vb.std(1)
    den = sa * sb
    return np.where(den > 1e-9, cov / np.where(den > 1e-9, den, 1.0), 0.0)


def _ri(x):
    return np.rint(x).astype(np.int64)


THRESH = [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0]
EWMA = [0.5, 0.7, 0.9, 0.97]

# name: (arity, param kind, fn)
OPS = {
    "delay": (1, ("int", 1, 16), lambda x, p: _delay(x, p)),
    "diff": (1, ("int", 1, 8), lambda x, p: x - _delay(x, p)),
    "wsum": (1, ("int", 2, 24), lambda x, p: _wsum(x, p)),
    "wmax": (1, ("int", 2, 16), lambda x, p: _win(x, p).max(1)),
    "wmin": (1, ("int", 2, 16), lambda x, p: _win(x, p).min(1)),
    "rank": (1, ("int", 3, 16), lambda x, p: _rank(x, p)),
    "accmod": (1, ("int", 2, 7), lambda x, p: (np.cumsum(_ri(x)) % p).astype(float)),
    "fold": (1, ("int", 2, 7), lambda x, p: (_ri(x) % p).astype(float)),
    "thresh": (1, ("choice", THRESH), lambda x, p: (x > p).astype(float)),
    "ewma": (1, ("choice", EWMA), lambda x, p: _ewma(x, p)),
    "norm": (1, ("int", 4, 24), lambda x, p: _norm(x, p)),
    "sample": (1, ("int", 2, 12), lambda x, p: _sample(x, p)),
    "fsm": (1, ("fsm",), lambda x, p: _fsm(x, p)),
    "sign": (1, None, lambda x, p: np.sign(x)),
    "abs": (1, None, lambda x, p: np.abs(x)),
    "neg": (1, None, lambda x, p: -x),
    "add": (2, None, lambda a, b, p: a + b),
    "sub": (2, None, lambda a, b, p: a - b),
    "mul": (2, None, lambda a, b, p: a * b),
    "max2": (2, None, lambda a, b, p: np.maximum(a, b)),
    "min2": (2, None, lambda a, b, p: np.minimum(a, b)),
    "gt": (2, None, lambda a, b, p: (a > b).astype(float)),
    "eq": (2, None, lambda a, b, p: (_ri(a) == _ri(b)).astype(float)),
    "xor": (2, None, lambda a, b, p: ((_ri(a) % 2) ^ (_ri(b) % 2)).astype(float)),
    "hash": (2, ("int", 2, 8), lambda a, b, p: ((_ri(a) * 7919 + _ri(b) * 104729) % p).astype(float)),
    "wcorr": (2, ("int", 4, 24), lambda a, b, p: _wcorr(a, b, p)),
    "where": (3, None, lambda c, a, b, p: np.where(c > 0.5, a, b)),
}
OP_NAMES = sorted(OPS)
BY_ARITY = {k: [n for n in OP_NAMES if OPS[n][0] == k] for k in (1, 2, 3)}

# Audit-only op, NEVER in OPS: reads the future. Used by the cheat control.
LEAD_OP = "lead"


def rand_param(op, rng):
    kind = OPS[op][1]
    if kind is None:
        return None
    if kind[0] == "int":
        return int(rng.integers(kind[1], kind[2] + 1))
    if kind[0] == "choice":
        return float(kind[1][int(rng.integers(len(kind[1])))])
    m = int(rng.integers(2, 5))
    return [m, [int(v) for v in rng.integers(0, m, size=2 * m)]]


def mutate_param(op, p, rng):
    kind = OPS[op][1]
    if kind is None:
        return None
    if kind[0] == "int":
        lo, hi = kind[1], kind[2]
        if rng.random() < 0.7:
            return int(min(hi, max(lo, p + int(rng.choice([-2, -1, 1, 2])))))
        return int(rng.integers(lo, hi + 1))
    if kind[0] == "choice":
        return float(kind[1][int(rng.integers(len(kind[1])))])
    m, table = p[0], list(p[1])
    if rng.random() < 0.2:
        return rand_param(op, rng)
    j = int(rng.integers(len(table)))
    table[j] = int(rng.integers(0, m))
    return [m, table]


def _apply(op, args, p, regs):
    if op == LEAD_OP:
        x = regs[args[0]]
        y = np.zeros_like(x)
        y[:-p] = x[p:]
        return y
    return OPS[op][2](*[regs[a] for a in args], p)


def execute(g, X):
    """Run genome g on observations X (T x d). Returns Z (T x K), finite."""
    T, d = X.shape
    Xf = X.astype(float)
    regs = [Xf[:, c % d] for c in range(NIN)]
    with np.errstate(all="ignore"):
        for op, args, p in g["ins"]:
            y = np.asarray(_apply(op, args, p, regs), dtype=float)
            y = np.nan_to_num(y, nan=0.0, posinf=CLIP, neginf=-CLIP)
            regs.append(np.clip(y, -CLIP, CLIP))
    return np.stack([regs[o] for o in g["out"]], 1)


def canonical(g):
    return json.dumps({"ins": g["ins"], "out": g["out"]}, sort_keys=True, separators=(",", ":"))


def lens_id(g):
    return "L-" + hashlib.sha256(canonical(g).encode()).hexdigest()[:10]


def validate(g):
    n = NIN
    for i, (op, args, p) in enumerate(g["ins"]):
        if op not in OPS and op != LEAD_OP:
            return False
        ar = 1 if op == LEAD_OP else OPS[op][0]
        if len(args) != ar or any(a < 0 or a >= n + i for a in args):
            return False
    nreg = n + len(g["ins"])
    return 1 <= len(g["out"]) <= KMAX and all(0 <= o < nreg for o in g["out"])


def cone(g, regs):
    """Instruction indices needed to compute registers `regs`."""
    need, stack = set(), [r for r in regs if r >= NIN]
    while stack:
        r = stack.pop()
        i = r - NIN
        if i in need:
            continue
        need.add(i)
        stack.extend(a for a in g["ins"][i][1] if a >= NIN)
    return sorted(need)


def effective_length(g):
    return len(cone(g, g["out"]))


def input_channels(g):
    """Virtual input channels the outputs depend on."""
    used = set(o for o in g["out"] if o < NIN)
    for i in cone(g, g["out"]):
        used.update(a for a in g["ins"][i][1] if a < NIN)
    return sorted(used)


# ---------------------------------------------------------------- generation

def random_genome(rng, n_ins=None, k=None):
    n_ins = int(rng.integers(1, 5)) if n_ins is None else n_ins
    ins = []
    for i in range(n_ins):
        ins.append(_rand_ins(rng, NIN + i))
    nreg = NIN + n_ins
    k = int(rng.integers(1, 3)) if k is None else k
    out = [nreg - 1] + [int(rng.integers(NIN, nreg)) for _ in range(k - 1)]
    return {"ins": ins, "out": sorted(set(out))}


def _rand_ins(rng, nreg):
    ar = int(rng.choice([1, 1, 1, 2, 2, 3]))
    op = BY_ARITY[ar][int(rng.integers(len(BY_ARITY[ar])))]
    # bias arguments toward recent registers so programs compose
    args = [_rand_reg(rng, nreg) for _ in range(ar)]
    return [op, args, rand_param(op, rng)]


def _rand_reg(rng, nreg):
    if nreg > NIN and rng.random() < 0.6:
        return int(rng.integers(NIN, nreg))
    return int(rng.integers(0, NIN))


def _copy(g):
    return {"ins": [[op, list(a), (list(p) if isinstance(p, list) else p)] for op, a, p in g["ins"]],
            "out": list(g["out"])}


def _shift_refs(g, at, delta):
    """Registers >= at get +delta (insertion) in args and out."""
    for ins in g["ins"]:
        ins[1] = [a + delta if a >= at else a for a in ins[1]]
    g["out"] = [o + delta if o >= at else o for o in g["out"]]


def m_point(g, rng):
    g = _copy(g)
    cand = [i for i, ins in enumerate(g["ins"]) if OPS.get(ins[0], (0, None))[1] is not None]
    if not cand:
        return m_replace(g, rng)
    i = int(rng.choice(cand))
    g["ins"][i][2] = mutate_param(g["ins"][i][0], g["ins"][i][2], rng)
    return g


def m_replace(g, rng):
    g = _copy(g)
    if not g["ins"]:
        return m_insert(g, rng)
    i = int(rng.integers(len(g["ins"])))
    ar = OPS[g["ins"][i][0]][0]
    op = BY_ARITY[ar][int(rng.integers(len(BY_ARITY[ar])))]
    g["ins"][i][0] = op
    g["ins"][i][2] = rand_param(op, rng)
    return g


def m_insert(g, rng):
    g = _copy(g)
    if len(g["ins"]) >= MAXLEN:
        return g
    i = int(rng.integers(0, len(g["ins"]) + 1))
    new = _rand_ins(rng, NIN + i)
    _shift_refs(g, NIN + i, 1)
    g["ins"].insert(i, new)
    # optionally route an existing consumer through the new register
    later = [j for j in range(i + 1, len(g["ins"]))]
    if later and rng.random() < 0.5:
        j = int(rng.choice(later))
        k = int(rng.integers(len(g["ins"][j][1])))
        g["ins"][j][1][k] = NIN + i
    elif rng.random() < 0.3:
        g["out"][int(rng.integers(len(g["out"])))] = NIN + i
        g["out"] = sorted(set(g["out"]))
    return g


def m_delete(g, rng):
    g = _copy(g)
    if len(g["ins"]) <= 1:
        return m_insert(g, rng)
    i = int(rng.integers(len(g["ins"])))
    r = NIN + i
    sub = g["ins"][i][1][0]
    del g["ins"][i]
    for ins in g["ins"]:
        ins[1] = [sub if a == r else (a - 1 if a > r else a) for a in ins[1]]
    g["out"] = sorted(set(sub if o == r else (o - 1 if o > r else o) for o in g["out"]))
    return g


def m_rewire(g, rng):
    g = _copy(g)
    if not g["ins"]:
        return m_insert(g, rng)
    i = int(rng.integers(len(g["ins"])))
    k = int(rng.integers(len(g["ins"][i][1])))
    g["ins"][i][1][k] = _rand_reg(rng, NIN + i)
    return g


def m_out(g, rng):
    g = _copy(g)
    nreg = NIN + len(g["ins"])
    r = rng.random()
    if r < 0.4 and len(g["out"]) < KMAX:
        g["out"].append(int(rng.integers(NIN, nreg)) if nreg > NIN else 0)
    elif r < 0.6 and len(g["out"]) > 1:
        g["out"].pop(int(rng.integers(len(g["out"]))))
    else:
        g["out"][int(rng.integers(len(g["out"])))] = int(rng.integers(0, nreg))
    g["out"] = sorted(set(g["out"]))
    return g


def _wrap(g, rng, ops):
    """Insert a unary op consuming register r and redirect r's consumers."""
    g = _copy(g)
    if len(g["ins"]) >= MAXLEN:
        return g
    nreg = NIN + len(g["ins"])
    r = int(rng.integers(0, nreg))
    op = ops[int(rng.integers(len(ops)))]
    g["ins"].append([op, [r], rand_param(op, rng)])
    new = nreg
    # append-only keeps register order valid; the new register becomes an
    # output (replacing r if r was one, else a random output or an extra one)
    out = list(g["out"])
    if r in out:
        out[out.index(r)] = new
    elif len(out) < KMAX and rng.random() < 0.5:
        out.append(new)
    else:
        out[int(rng.integers(len(out)))] = new
    g["out"] = sorted(set(out))
    return g


def m_temporal(g, rng):
    return _wrap(g, rng, ["delay", "diff", "wsum", "sample"])


def m_recur(g, rng):
    return _wrap(g, rng, ["fsm", "accmod", "ewma"])


def m_dup(g, rng):
    """Subtree duplication: copy the cone of a random register, append it."""
    g = _copy(g)
    nreg = NIN + len(g["ins"])
    if nreg == NIN:
        return m_insert(g, rng)
    r = int(rng.integers(NIN, nreg))
    idx = cone(g, [r])
    if len(g["ins"]) + len(idx) > MAXLEN:
        return g
    remap = {}
    for i in idx:
        op, args, p = g["ins"][i]
        newreg = NIN + len(g["ins"])
        g["ins"].append([op, [remap.get(a, a) for a in args], (list(p) if isinstance(p, list) else p)])
        remap[NIN + i] = newreg
    if len(g["out"]) < KMAX:
        g["out"] = sorted(set(g["out"] + [remap[r]]))
    return g


def graft(g, donor, rng):
    """Cross-lineage graft / composition: append the cone of one donor output
    to g (donor inputs stay inputs), and add it as an output of g."""
    g = _copy(g)
    r = donor["out"][int(rng.integers(len(donor["out"])))]
    if r < NIN:
        return m_out(g, rng)
    idx = cone(donor, [r])
    if len(g["ins"]) + len(idx) > MAXLEN:
        return g
    remap = {}
    for i in idx:
        op, args, p = donor["ins"][i]
        newreg = NIN + len(g["ins"])
        g["ins"].append([op, [remap.get(a, a) for a in args], (list(p) if isinstance(p, list) else p)])
        remap[NIN + i] = newreg
    out = g["out"] + [remap[r]]
    if len(out) > KMAX:
        out.pop(int(rng.integers(len(out) - 1)))
    g["out"] = sorted(set(out))
    # optionally bind the grafted output with an existing register
    if rng.random() < 0.5 and len(g["ins"]) < MAXLEN:
        a = remap[r]
        b = _rand_reg(rng, NIN + len(g["ins"]))
        op = BY_ARITY[2][int(rng.integers(len(BY_ARITY[2])))]
        g["ins"].append([op, [a, b], rand_param(op, rng)])
        g["out"] = sorted(set(g["out"][:-1] + [NIN + len(g["ins"]) - 1]))
    return g


MUTATIONS = {
    "point": m_point, "replace": m_replace, "insert": m_insert, "delete": m_delete,
    "rewire": m_rewire, "out": m_out, "temporal": m_temporal, "recur": m_recur,
    "dup": m_dup,
}
MUT_NAMES = sorted(MUTATIONS)


def mutate(g, rng, n=None):
    n = int(rng.integers(1, 3)) if n is None else n
    applied = []
    for _ in range(n):
        name = MUT_NAMES[int(rng.integers(len(MUT_NAMES)))]
        g2 = MUTATIONS[name](g, rng)
        if validate(g2):
            g = g2
            applied.append(name)
    return g, applied


# ------------------------------------------------------------ signatures

def probe_input(seed=7, T=512):
    rng = np.random.default_rng(seed)
    X = np.empty((T, NIN))
    X[:, :4] = rng.integers(0, 2, size=(T, 4))
    X[:, 4:] = rng.standard_normal((T, 4))
    return X


_PROBE = None
SIG_IDX = np.linspace(64, 511, 64).astype(int)


def signature(g):
    """Behaviour signature: rank-normalised outputs on a fixed probe input at
    64 fixed times, 3 columns (padded). Used only for diversity, never value."""
    global _PROBE
    if _PROBE is None:
        _PROBE = probe_input()
    Z = execute(g, _PROBE)[SIG_IDX]
    cols = []
    for j in range(KMAX):
        if j < Z.shape[1]:
            z = Z[:, j]
            r = np.argsort(np.argsort(z, kind="stable"), kind="stable").astype(float)
            if np.ptp(z) == 0:
                r[:] = 0.5 * (len(z) - 1)
            cols.append(r / (len(z) - 1))
        else:
            cols.append(np.full(len(SIG_IDX), 0.5))
    return np.concatenate(cols)
