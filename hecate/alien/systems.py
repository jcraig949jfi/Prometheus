"""Executable systems for the alien-lawful assay.

Every system is a deterministic map on a finite, fully enumerable state
space (<= ~4k states), defined by a JSON-serialisable params dict and
interpreted by step(params, state). Nothing here knows which class a
system belongs to; the class lives only in the answer key.

Families (state = tuple of ints, dims = domain size per component):
  tab      5 components in Z_5            (3125 states)   -- A1 state machines
  graph    6 node values in 0..3 + graph  (4096 states)   -- A2 graph dynamics
  rewrite  6 symbols in 0..3              (4096 states)   -- A3 rewrite worlds
  vm       (c, r0, r1, r2), c in 0..5, r in Z_7 (2058)    -- A4 tiny machines
  map      2 components in Z_31           (961 states)    -- A5 discrete maps
Wrappers (any family): scramble (input-scrambled null), smooth (seductive
noise), linmix (lawful map seen through an invertible linear change of
coordinates).
"""

from __future__ import annotations

import itertools

import numpy as np

FAMILY_DIMS = {
    "tab": [5] * 5,
    "graph": [4] * 6,
    "rewrite": [4] * 6,
    "vm": [6, 7, 7, 7],
    "map": [31, 31],
}


def dims_of(params):
    return FAMILY_DIMS[params["family"]]


def n_states(dims):
    return int(np.prod(dims))


def index(s, dims):
    i = 0
    for v, d in zip(s, dims):
        i = i * d + int(v)
    return i


def unindex(i, dims):
    out = []
    for d in reversed(dims):
        out.append(i % d)
        i //= d
    return tuple(reversed(out))


def all_states(dims):
    return [tuple(x) for x in itertools.product(*[range(d) for d in dims])]


# --------------------------------------------------------------------------
# family interpreters
# --------------------------------------------------------------------------

def _tab(p, s):
    m = 5
    k = p["kind"]
    x = list(s)
    n = len(x)
    if k == "tab_local":
        d = [p["D"][i][x[i]][x[p["nb"][i]]] for i in range(n)]
        c, mode = p.get("comp"), p.get("mode")
        if mode in ("lin", "cyc"):
            w = p["w"]
            tot = sum(w[i] * d[i] for i in range(n) if i != c)
            target = 0 if mode == "lin" else 1
            inv = pow(w[c], -1, m)
            d[c] = ((target - tot) * inv) % m
        return tuple((x[i] + d[i]) % m for i in range(n))
    if k == "tab_rev":
        for i in p["order"]:
            x[i] = (x[i] + p["D"][i][x[p["nb"][i]]]) % m
        return tuple(x)
    if k == "odometer":
        for i in range(n):
            x[i] = (x[i] + 1) % m
            if x[i] != 0:
                break
        return tuple(x)
    if k == "lfsr":
        new = sum(a * v for a, v in zip(p["a"], x)) % m
        return tuple(x[1:] + [new])
    if k == "oddeven_sort":
        for pairs in ((0, 1), (2, 3)), ((1, 2), (3, 4)):
            for i, j in pairs:
                if x[i] > x[j]:
                    x[i], x[j] = x[j], x[i]
        return tuple(x)
    if k == "median3":
        return tuple(sorted((x[i - 1], x[i], x[(i + 1) % n]))[1] for i in range(n))
    raise ValueError(k)


def _graph(p, s):
    k = p["kind"]
    x = list(s)
    edges = p["edges"]
    nbrs = [[] for _ in x]
    for u, v in edges:
        if [u, v] in p.get("removed", []) or [v, u] in p.get("removed", []):
            continue
        nbrs[u].append(v)
        nbrs[v].append(u)
    if k in ("graph_flow", "diffusion"):
        for u, v in edges:
            if [u, v] in p.get("removed", []) or [v, u] in p.get("removed", []):
                continue
            if k == "diffusion":
                t = (x[v] > x[u]) - (x[v] < x[u])
            else:
                t = p["F"][x[u]][x[v]]
            # the alien exchanges (v loses what u gains); the DESTROY null
            # uses an independent second table F2, so nothing is conserved
            tv = -t if "F2" not in p else p["F2"][x[u]][x[v]]
            if 0 <= x[u] + t <= 3 and 0 <= x[v] + tv <= 3:
                x[u] += t
                x[v] += tv
        return tuple(x)
    if k == "graph_attr":
        return tuple(p["G"][x[i]][sum(x[j] for j in nbrs[i]) % 4] for i in range(len(x)))
    if k == "bfs":
        out = []
        for i in range(len(x)):
            if i == 0:
                out.append(0)
            else:
                best = min([x[j] + 1 for j in nbrs[i]] + [x[i]])
                out.append(min(3, best))
        return tuple(out)
    if k == "plurality":
        out = []
        for i in range(len(x)):
            vals = [x[i]] + [x[j] for j in nbrs[i]]
            cnt = [vals.count(v) for v in range(4)]
            top = max(cnt)
            out.append(x[i] if cnt[x[i]] == top else cnt.index(top))
        return tuple(out)
    if k == "threshold":
        out = []
        for i in range(len(x)):
            hot = sum(1 for j in nbrs[i] if x[j] >= 2)
            out.append(min(3, x[i] + 1) if hot >= 1 else max(0, x[i] - 1))
        return tuple(out)
    raise ValueError(k)


def _rewrite(p, s):
    x = list(s)
    for pos in range(len(x) - 1):
        for (a, b), (c, d) in p["rules"]:
            if x[pos] == a and x[pos + 1] == b:
                x[pos], x[pos + 1] = c, d
                return tuple(x)
    return tuple(x)


def _vm(p, s):
    c, r = s[0], list(s[1:])
    ins = p["program"][c]
    op = ins[0]
    nxt = (c + 1) % 6
    if op == "mix":            # r_a += k*g[r_b]; r_z -= kz*g[r_b]
        _, a, b, z, g, k, kz = ins
        gv = g[r[b]]
        r[a] = (r[a] + k * gv) % 7
        r[z] = (r[z] - kz * gv) % 7
    elif op == "aff":          # r_a = k1*r_b + k2*r_z + e
        _, a, b, z, k1, k2, e = ins
        r[a] = (k1 * r[b] + k2 * r[z] + e) % 7
    elif op == "tab":          # r_a = T[r_b]
        _, a, b, T = ins
        r[a] = T[r[b]]
    elif op == "jz":
        _, a, t = ins
        nxt = t if r[a] == 0 else nxt
    elif op == "jnz":
        _, a, t = ins
        nxt = t if r[a] != 0 else nxt
    elif op == "jmp":
        nxt = ins[1]
    else:
        raise ValueError(op)
    return tuple([nxt] + r)


def _poly(coef, x, y, p):
    return sum(c * pow(x, i, p) * pow(y, j, p) for (i, j, c) in coef) % p


def _map(p, s):
    q = 31
    x, y = s
    k = p["kind"]
    if k == "poly_sym":
        return (_poly(p["g"], x, y, q), _poly(p["g"], y, x, q))
    if k == "shear":
        x2 = (x + _poly(p["h1"], y, 0, q)) % q
        y2 = (y + _poly(p["h2"], x2, 0, q)) % q
        return (x2, y2)
    if k == "poly_free":
        return (_poly(p["g1"], x, y, q), _poly(p["g2"], x, y, q))
    if k == "rot90":
        return ((-y) % q, x)
    if k == "cat":
        return ((2 * x + y) % q, (x + y) % q)
    if k == "predprey":
        nx = x + (x * (12 - y)) // 12
        ny = y + (y * (x - 12)) // 12
        return (max(0, min(30, nx)), max(0, min(30, ny)))
    if k == "phase_sync":
        def toward(a, b):
            dlt = (b - a) % q
            if dlt == 0:
                return a
            return (a + 1) % q if dlt <= q // 2 else (a - 1) % q
        return (toward(x, y), toward(y, x))
    raise ValueError(k)


FAMILY_STEP = {"tab": _tab, "graph": _graph, "rewrite": _rewrite, "vm": _vm, "map": _map}


def _perm(seed, n, with_replacement=False):
    rs = np.random.RandomState(seed)
    return rs.randint(0, n, n) if with_replacement else rs.permutation(n)


_PERM_CACHE: dict = {}


def step(p, s):
    s = tuple(int(v) for v in s)
    w = p.get("wrap")
    dims = dims_of(p)
    if w == "scramble":
        key = (p["perm_seed"], n_states(dims), bool(p.get("with_replacement")))
        if key not in _PERM_CACHE:
            _PERM_CACHE[key] = _perm(*key)
        return step(p["base"], unindex(int(_PERM_CACHE[key][index(s, dims)]), dims))
    if w == "conj":
        # relabelled null: f_N = sigma . f . sigma^-1 for a random relabelling
        # sigma of the states. Orbit structure is identical to the base;
        # every invariant that is compact in the state coordinates is lost.
        key = (p["perm_seed"], n_states(dims), False)
        if key not in _PERM_CACHE:
            _PERM_CACHE[key] = _perm(*key)
        sig = _PERM_CACHE[key]
        ikey = ("inv",) + key
        if ikey not in _PERM_CACHE:
            inv = np.empty_like(sig)
            inv[sig] = np.arange(len(sig))
            _PERM_CACHE[ikey] = inv
        src = unindex(int(_PERM_CACHE[ikey][index(s, dims)]), dims)
        return unindex(int(sig[index(step(p["base"], src), dims)]), dims)
    if w == "delta":
        # increment-scrambled null: state s gets the update increment the base
        # system applies at a random other state pi(s), and on a random ~30%
        # of states one component of that increment is shifted by +-1
        key = (p["perm_seed"], n_states(dims), False)
        if key not in _PERM_CACHE:
            _PERM_CACHE[key] = _perm(*key)
        src = unindex(int(_PERM_CACHE[key][index(s, dims)]), dims)
        nxt = step(p["base"], src)
        inc = [(b - a) % d for a, b, d in zip(src, nxt, dims)]
        rs = np.random.RandomState((p["tweak_seed"] * 1000003 + index(s, dims)) % (2 ** 31))
        if rs.rand() < 0.3:
            j = rs.randint(0, len(dims))
            inc[j] = (inc[j] + (1 if rs.rand() < 0.5 else -1)) % dims[j]
        return tuple((v + dv) % d for v, dv, d in zip(s, inc, dims))
    if w == "smooth":
        rs = np.random.RandomState((p["seed"] * 1000003 + index(s, dims)) % (2 ** 31))
        delta = rs.randint(-1, 2, size=len(dims))
        return tuple((v + int(dl)) % d for v, dl, d in zip(s, delta, dims))
    if w == "linmix":
        M, Minv, mod = p["M"], p["Minv"], p["mod"]
        z = tuple(int(v) for v in (np.array(Minv) @ np.array(s)) % mod)
        gz = step(p["base"], z)
        return tuple(int(v) for v in (np.array(M) @ np.array(gz)) % mod)
    return FAMILY_STEP[p["family"]](p, s)


def clamp_run(p, s, var, val, steps):
    """do(var := val): clamp before the first step and after every step."""
    s = list(s)
    s[var] = val
    out = []
    for _ in range(steps):
        s = list(step(p, tuple(s)))
        s[var] = val
        out.append(tuple(s))
    return out


def remove_edge(p, edge):
    q = dict(p)
    q["removed"] = list(p.get("removed", [])) + [list(edge)]
    return q


def trajectory(p, s, steps):
    out = [tuple(s)]
    for _ in range(steps):
        out.append(step(p, out[-1]))
    return out


# --------------------------------------------------------------------------
# neutral presentation
# --------------------------------------------------------------------------

LETTERS = "WXYZ"


def show(p, s):
    fam = p["family"]
    if fam == "rewrite":
        return "".join(LETTERS[v] for v in s)
    return " ".join(str(v) for v in s)


def parse_state(p, text):
    fam = p["family"]
    if isinstance(text, (list, tuple)):
        return tuple(int(v) for v in text)
    t = str(text).strip()
    if fam == "rewrite":
        t = t.replace(" ", "")
        return tuple(LETTERS.index(ch) for ch in t)
    return tuple(int(v) for v in t.replace(",", " ").replace("(", " ").replace(")", " ").split())


def header(p):
    """Everything a subject is told about the state space, and nothing else."""
    fam = p["family"]
    dims = dims_of(p)
    if fam == "rewrite":
        return (f"Each state is a string of {len(dims)} symbols from the set "
                f"{{{', '.join(LETTERS)}}}.")
    lines = [f"Each state is a list of {len(dims)} integers; position i takes "
             f"values 0..{dims[0] - 1}." if len(set(dims)) == 1 else
             "Each state is a list of integers with ranges " +
             ", ".join(f"position {i}: 0..{d - 1}" for i, d in enumerate(dims)) + "."]
    base = p
    while base.get("wrap") in ("scramble", "linmix", "delta", "conj"):
        base = base["base"]
    if fam == "graph":
        lines.append("The positions are sites connected by these links: " +
                     ", ".join(f"{u}-{v}" for u, v in base["edges"]) + ".")
    return " ".join(lines)
