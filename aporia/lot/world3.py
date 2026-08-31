"""world3.py — TINYPROG. The semantic-first world, built after the graph worlds were killed.

CONSTRUCTION ORDER, per amendment 1 section 6:

    latent semantics -> properties proved EXACTLY -> compile to a surface

Objects are 4-tuples over Z6. A task is a hidden program over 10 anonymous typed primitives;
the solver sees only the extensional behaviour on a fixed probe set and must find any program
that agrees on it.

WHY THIS IS ENUMERABLE WHERE THE GRAPH WORLDS WERE NOT. Every program here is a function of the
single input, and every primitive combines such functions POINTWISE. So a program can be
represented by its extensional SIGNATURE over the probe set, signature space is closed under the
primitives, and bottom-up enumeration with deduplication by signature yields exactly:

    - the minimal program size of every reachable function, up to budget
    - the complete inventory of shallow routes to any target
    - a flat solver whose search and execution costs are directly instrumented

The graph worlds could only ever SAMPLE their shortcut inventory, so "no shortcut" was always a
claim about a sample. Here it is a claim about a closure.

NAMES CARRY NO SEMANTICS. Primitives live in an ordered LIST and every draw indexes by position;
the name is a label only. That is what makes the metamorphic relabelling arm exact rather than
approximate -- relabelling cannot perturb a single random draw, so every reading must come back
bit-identical, and any code that secretly keys on a name string is caught.

COST MODEL (amendment 1 section 5). C_search and C_execution are recorded separately and never
summed. In the flat arm they are proportional by construction -- C_execution = P * C_search,
since each expansion executes one primitive over P probes. THAT IS THE POINT: the proportion is
a property of the flat solver, not a law, and a promoted macro in A3 breaks it by costing one
search decision while executing its whole expansion. A merged budget would hide exactly the
quantity the arc is about.
"""
from __future__ import annotations

import random
from functools import lru_cache

MOD = 6
WIDTH = 4
V, S = "V", "S"


# ---------------------------------------------------------------- primitives

def _rot(v):
    return v[1:] + v[:1]


def _rev(v):
    return tuple(reversed(v))


def _inc(v):
    return tuple((a + 1) % MOD for a in v)


def _dbl(v):
    return tuple((a * 2) % MOD for a in v)


def _vadd(a, b):
    return tuple((x + y) % MOD for x, y in zip(a, b))


def _vmul(a, b):
    return tuple((x * y) % MOD for x, y in zip(a, b))


def _sum(v):
    return sum(v) % MOD


def _prod(v):
    p = 1
    for a in v:
        p = (p * a) % MOD
    return p


def _sadd(v, s):
    return tuple((a + s) % MOD for a in v)


def _smul(v, s):
    return tuple((a * s) % MOD for a in v)


#: ordered list; position is identity, `name` is a label only
PRIMS = [
    {"name": "p00", "args": (V,), "ret": V, "fn": _rot},
    {"name": "p01", "args": (V,), "ret": V, "fn": _rev},
    {"name": "p02", "args": (V,), "ret": V, "fn": _inc},
    {"name": "p03", "args": (V,), "ret": V, "fn": _dbl},
    {"name": "p04", "args": (V, V), "ret": V, "fn": _vadd},
    {"name": "p05", "args": (V, V), "ret": V, "fn": _vmul},
    {"name": "p06", "args": (V,), "ret": S, "fn": _sum},
    {"name": "p07", "args": (V,), "ret": S, "fn": _prod},
    {"name": "p08", "args": (V, S), "ret": V, "fn": _sadd},
    {"name": "p09", "args": (V, S), "ret": V, "fn": _smul},
]


def relabel(prims, names):
    """Metamorphic transform: rename primitives, change nothing else."""
    assert len(names) == len(prims)
    return [dict(p, name=n) for p, n in zip(prims, names)]


# ---------------------------------------------------------------- expressions
# expr := ('X',) | (index, child, ...)   -- index is a POSITION in the prims list


def evaluate(expr, x, prims):
    if expr[0] == "X":
        return x
    spec = prims[expr[0]]
    return spec["fn"](*[evaluate(c, x, prims) for c in expr[1:]])


def size_of(expr):
    if expr[0] == "X":
        return 0
    return 1 + sum(size_of(c) for c in expr[1:])


def subterms(expr):
    yield expr
    if expr[0] != "X":
        for c in expr[1:]:
            yield from subterms(c)


def contains(expr, term):
    return any(t == term for t in subterms(expr))


def signature(expr, probes, prims):
    return tuple(evaluate(expr, x, prims) for x in probes)


# ---------------------------------------------------------------- the flat solver
# Bottom-up enumeration over extensional signatures, deduplicated. This IS the closure and it
# IS the solver; there is no separate oracle.

def build_closure(prims, probes, max_size=5, max_candidates=600_000, max_sigs=400_000):
    """Return (minsize, order, layers, stats).

    minsize[(t, sig)] -> minimal program size
    order[(t, sig)]   -> C_search at first discovery, i.e. candidates expanded before it existed
    """
    x_key = (V, tuple(probes))
    minsize = {x_key: 0}
    order = {x_key: 0}
    layers = {(0, V): [tuple(probes)], (0, S): []}
    cand = 0
    exhausted = False

    for size in range(1, max_size + 1):
        got_v, got_s = [], []
        for idx, spec in enumerate(prims):
            args, ret = spec["args"], spec["ret"]
            fn = spec["fn"]
            if len(args) == 1:
                parents = layers.get((size - 1, args[0]), [])
                for ps in parents:
                    cand += 1
                    sig = tuple(fn(u) for u in ps)
                    key = (ret, sig)
                    if key not in minsize:
                        minsize[key] = size
                        order[key] = cand
                        (got_v if ret == V else got_s).append(sig)
                    if cand >= max_candidates or len(minsize) >= max_sigs:
                        exhausted = True
                        break
            else:
                for sa in range(0, size):
                    sb = size - 1 - sa
                    la = layers.get((sa, args[0]), [])
                    lb = layers.get((sb, args[1]), [])
                    if not la or not lb:
                        continue
                    for pa in la:
                        for pb in lb:
                            cand += 1
                            sig = tuple(fn(u, w) for u, w in zip(pa, pb))
                            key = (ret, sig)
                            if key not in minsize:
                                minsize[key] = size
                                order[key] = cand
                                (got_v if ret == V else got_s).append(sig)
                            if cand >= max_candidates or len(minsize) >= max_sigs:
                                exhausted = True
                                break
                        if exhausted:
                            break
                if exhausted:
                    break
            if exhausted:
                break
        layers[(size, V)] = got_v
        layers[(size, S)] = got_s
        if exhausted:
            break

    stats = {
        "candidates_expanded": cand,
        "distinct_signatures": len(minsize),
        "budget_exhausted": exhausted,
        "max_size": max_size,
        "layer_widths": {f"{s}_{t}": len(layers.get((s, t), []))
                         for s in range(0, max_size + 1) for t in (V, S)},
    }
    return minsize, order, layers, stats


# ---------------------------------------------------------------- task sampling

def _feasible_table(prims, n_max, motif_cost):
    """feas[(type, n, allow_M)] -> can an expression of that type with EXACTLY n ops be built."""
    feas = {}

    def f(t, n, m):
        k = (t, n, m)
        if k in feas:
            return feas[k]
        feas[k] = False                      # guard against recursion on cyclic queries
        ok = False
        if t == V and n == 0:
            ok = True
        if m and t == V and n == motif_cost:
            ok = True
        if not ok:
            for spec in prims:
                if spec["ret"] != t or n < 1:
                    continue
                args = spec["args"]
                if len(args) == 1:
                    if f(args[0], n - 1, m):
                        ok = True
                else:
                    for sa in range(0, n):
                        if f(args[0], sa, m) and f(args[1], n - 1 - sa, m):
                            ok = True
                            break
                if ok:
                    break
        feas[k] = ok
        return ok

    for t in (V, S):
        for n in range(0, n_max + 1):
            for m in (False, True):
                f(t, n, m)
    return feas, f


def sample_expr(rng, prims, t, n, feas, motif_cost, allow_motif):
    """Uniform-ish draw over the legal shapes of exactly n ops. The motif is a LEAF of cost
    `motif_cost`, so enabling it does not change the surrounding structural distribution."""
    opts = []
    if t == V and n == 0:
        opts.append(("X",))
    if allow_motif and t == V and n == motif_cost:
        opts.append(("M",))
    for idx, spec in enumerate(prims):
        if spec["ret"] != t or n < 1:
            continue
        args = spec["args"]
        if len(args) == 1:
            if feas(args[0], n - 1, allow_motif):
                opts.append((idx, (args[0], n - 1)))
        else:
            for sa in range(0, n):
                sb = n - 1 - sa
                if feas(args[0], sa, allow_motif) and feas(args[1], sb, allow_motif):
                    opts.append((idx, (args[0], sa), (args[1], sb)))
    if not opts:
        return None
    pick = opts[rng.randrange(len(opts))]
    if pick == ("X",) or pick == ("M",):
        return pick
    idx = pick[0]
    kids = []
    for (at, an) in pick[1:]:
        k = sample_expr(rng, prims, at, an, feas, motif_cost, allow_motif)
        if k is None:
            return None
        kids.append(k)
    return (idx, *kids)


def substitute(expr, motif):
    if expr[0] == "X":
        return expr
    if expr[0] == "M":
        return motif
    return (expr[0], *[substitute(c, motif) for c in expr[1:]])


def uses_motif(expr):
    return any(t[0] == "M" for t in subterms(expr))


MOTIF_COST = 2


def sample_motif(rng, prims, feas):
    for _ in range(200):
        e = sample_expr(rng, prims, V, MOTIF_COST, feas, MOTIF_COST, allow_motif=False)
        if e is not None and size_of(e) == MOTIF_COST:
            return e
    raise RuntimeError("no motif of the required size is constructible")


def sample_task(rng, prims, feas, total_size, motif):
    """A task program of EXACTLY total_size ops containing EXACTLY the given motif once or more.

    Every class uses this same procedure with the same size, so the structural distribution is
    identical across classes and only the IDENTITY of the motif varies. That is the whole
    defence against W4: reuse is imposed without imposing anything else.
    """
    for _ in range(400):
        e = sample_expr(rng, prims, V, total_size, feas, MOTIF_COST, allow_motif=True)
        if e is None or not uses_motif(e):
            continue
        full = substitute(e, motif)
        if size_of(full) != total_size:
            continue
        return full
    return None


# ---------------------------------------------------------------- episodes

CLASSES = ("REUSE", "NO_REUSE", "DECOY_REUSE", "LATE_REUSE", "CONTROL")
EPISODE_TASKS = 24
LATE_REUSE_EARLY_SHARED = 3          # weak early evidence: 3 of the first 12


def make_episode(rng, prims, feas, cls, total_size, n_tasks=EPISODE_TASKS, reuse_p=1.0):
    """Build one episode of a given class. Ground truth only; no solver is run here.

    `reuse_p` applies to the REUSE recipe only and is used by the A2b interventional sweep. It
    is a DETERMINISTIC evenly-spread quota rather than a coin flip, so the shared-motif task set
    at a lower rho is a strict subset of the set at a higher rho -- which is what makes the
    sweep monotone by construction instead of monotone in expectation. At rho = 1.0 every task
    shares, which reproduces the original behaviour draw for draw.
    """
    half = n_tasks // 2
    shared = sample_motif(rng, prims, feas)
    tasks = []
    for i in range(n_tasks):
        early = i < half
        if cls == "REUSE":
            use_shared = int((i + 1) * reuse_p) > int(i * reuse_p)
        elif cls == "CONTROL":
            use_shared = True
        elif cls == "NO_REUSE":
            use_shared = False
        elif cls == "DECOY_REUSE":
            use_shared = early
        elif cls == "LATE_REUSE":
            use_shared = (not early) or (i < LATE_REUSE_EARLY_SHARED)
        else:
            raise ValueError(cls)
        motif = shared if use_shared else sample_motif(rng, prims, feas)
        expr = sample_task(rng, prims, feas, total_size, motif)
        if expr is None:
            continue
        tasks.append({"expr": expr, "motif": motif, "early": early,
                      "declared_shared": use_shared})
    return {"class": cls, "tasks": tasks, "shared_motif": shared}


def world(seed, prims, classes=CLASSES, episodes_per_class=12, total_size=6,
          n_tasks=EPISODE_TASKS, size_fn=None, recipe_by_class=None, reuse_p=1.0):
    """Generate the whole world.

    COMMON RANDOM NUMBERS. Each episode draws from its own seeded stream derived from
    (seed, class index, episode index), so changing one class's size cannot perturb any other
    class's draws. Without this the calibration sweep would be confounded: moving the skew
    parameter would also reshuffle every downstream episode, and a monotonicity check would be
    measuring the reshuffle.

    `size_fn` and `recipe_by_class` exist ONLY for the calibration fixtures -- deliberate
    nuisance skew, and a REUSE class secretly generated with reuse probability zero. The
    experimental world leaves both None.
    """
    feas_tbl, feas = _feasible_table(prims, max(total_size + 3, 9), MOTIF_COST)
    eps = []
    for ci, cls in enumerate(classes):
        recipe = (recipe_by_class or {}).get(cls, cls)
        for j in range(episodes_per_class):
            sz = size_fn(cls, j) if size_fn else total_size
            rng = random.Random(seed * 1000003 + ci * 997 + j)
            ep = make_episode(rng, prims, feas, recipe, sz, n_tasks, reuse_p=reuse_p)
            ep["class"] = cls                      # label as declared, generated as `recipe`
            ep["recipe"] = recipe
            ep["total_size"] = sz
            eps.append(ep)
    return eps


def probe_inputs(seed=20260827, p=6):
    """Fixed probe set. Deliberately includes 0s and repeats so that degenerate programs
    (constant maps, multiply-by-zero collapses) are visible rather than hidden."""
    rng = random.Random(seed)
    fixed = [(0, 0, 0, 0), (1, 2, 3, 4), (5, 5, 5, 5)]
    out = list(fixed)
    while len(out) < p:
        out.append(tuple(rng.randrange(MOD) for _ in range(WIDTH)))
    return out[:p]
