"""SUBSTRATE: the executable matter every Theseus entity is made of.

An entity's executable representation is a GENOME: a small typed program
that updates a state field X[C, N] (C channels over N cells) plus a memory
field M[C, N], for T steps, on a topology with a boundary condition.

    genome = {
      "C": 1..4,                       channels
      "topo": {"kind": ring|line|rrg|mean|star, "seed": int},
      "bc": periodic|fixed0|reflect|absorb,
      "init": {"kind": spike|random|gradient|blocks|alternate, "amp": float},
      "rules": [ {"op": str, "src": [int], "dst": int, "p": [float],
                  "prov": str, "lens": optional tyche lens genome}, ... ],
    }

Rules are applied SEQUENTIALLY in list order inside a step (each rule reads
the state the previous rule left), so rule order is part of the mechanism
and collisions are noncommutative by construction.

The op set is a primitive-property algebra (transport, coupling, bounding,
conservation, memory, switching, copying, selection, symmetry, scale,
delay, state topology, order, forcing, routing, observation). It is itself
a human-designed prior: nothing Theseus finds can leave the space these ops
span, and every report says so. Op names deliberately avoid the target
ontologies the charter forbids as defaults; they name what an op does to
numbers, not what it is "like".

Nothing here knows what a genome means. Runs are deterministic given
(genome, seed, options); the only randomness is the IC seed and explicit
noise options, both seeded.
"""

from __future__ import annotations

import copy
import hashlib
import json

import numpy as np

CMAX = 4
MAXRULES = 14
CLIP = 1e6
N_DEFAULT = 32
T_DEFAULT = 128
HIST = 9  # delay history depth

TOPOS = ("ring", "line", "rrg", "mean", "star")
BCS = ("periodic", "fixed0", "reflect", "absorb")
INITS = ("spike", "random", "gradient", "blocks", "alternate")

# op: (n_src, param bounds [(lo, hi, kind)], property family)
# kind: "f" float, "i" int. n_src = -1 means variable arity (1..8).
OPS = {
    "diffuse":   (1, [(0.01, 0.5, "f")], "transport"),
    "advect":    (1, [(-3, 3, "i"), (0.01, 0.9, "f")], "transport"),
    "react":     (-1, [(-1.0, 1.0, "f"), (-1.0, 1.0, "f")], "coupling"),  # + one gain per src
    "saturate":  (0, [(0.2, 5.0, "f")], "bounding"),
    "conserve":  (0, [(0.05, 1.0, "f")], "conservation"),
    "decay":     (0, [(0.005, 0.3, "f")], "dissipation"),
    "remember":  (1, [(0.02, 0.9, "f")], "memory"),
    "recall":    (0, [(-1.0, 1.0, "f")], "memory"),
    "threshold": (1, [(-1.0, 1.0, "f"), (-1.0, 1.0, "f")], "switching"),
    "replicate": (1, [(0.02, 0.9, "f")], "copying"),
    "select":    (0, [(0.1, 0.9, "f"), (0.02, 0.6, "f")], "selection"),
    "mirror":    (0, [(0.02, 1.0, "f")], "symmetry"),
    "coarse":    (1, [(1, 3, "i"), (0.02, 0.9, "f")], "scale"),
    "delay":     (1, [(1, HIST - 1, "i"), (-1.0, 1.0, "f")], "delay"),
    "wrap":      (0, [(0.5, 4.0, "f")], "state_topology"),
    "rank":      (0, [(0.02, 1.0, "f")], "order"),
    "drive":     (0, [(-1.0, 1.0, "f"), (2, 32, "i"), (0.0, 0.999, "f")], "forcing"),
    "gate":      (2, [(-1.0, 1.0, "f"), (-1.0, 1.0, "f")], "routing"),
    "lensmap":   (1, [(-1.0, 1.0, "f")], "observation"),
    # THESEUS-30 CONDITIONAL primitives: inert alone (they read only the memory field, which
    # only "remember" writes), active only in composition with a writer.
    "inject":    (0, [(-0.5, 0.5, "f")], "conditional"),       # x += a * M[dst]
    "modulate":  (1, [(-1.0, 1.0, "f")], "conditional"),       # x += a * M[dst] * S[src]
}
OP_NAMES = sorted(OPS)
COND_OPS = ["inject", "modulate"]
# The v0 random-op pool, frozen: adding ops to OPS must not change any earlier run's RNG draws.
BASIC_OPS = [o for o in OP_NAMES if o not in ("lensmap", *COND_OPS)]
COND_ENABLED = False  # THESEUS-30: when True, random rules may also draw conditional ops


def random_op_pool():
    return BASIC_OPS + COND_OPS if COND_ENABLED else BASIC_OPS


# ----------------------------------------------------------------------------
# genome utilities


def canonical(g) -> str:
    return json.dumps(strip_prov(g), sort_keys=True, separators=(",", ":"))


def strip_prov(g):
    h = copy.deepcopy(g)
    for r in h["rules"]:
        r.pop("prov", None)
    return h


def genome_hash(g) -> str:
    return hashlib.sha256(canonical(g).encode()).hexdigest()[:16]


def n_params(g) -> int:
    return sum(len(r["p"]) + len(r["src"]) for r in g["rules"])


def complexity(g) -> dict:
    ops = [r["op"] for r in g["rules"]]
    return {
        "n_rules": len(ops),
        "n_params": n_params(g),
        "n_distinct_ops": len(set(ops)),
        "C": g["C"],
        "max_src": max([len(r["src"]) for r in g["rules"]] + [0]),
    }


def clamp_param(op, j, v):
    bounds = OPS[op][1]
    if op == "react" and j >= 2:
        lo, hi, kind = -2.0, 2.0, "f"
    else:
        lo, hi, kind = bounds[j]
    v = min(hi, max(lo, v))
    return int(round(v)) if kind == "i" else float(v)


def rand_params(op, rng, n_src=1):
    ps = []
    for (lo, hi, kind) in OPS[op][1]:
        ps.append(int(rng.integers(lo, hi + 1)) if kind == "i" else float(rng.uniform(lo, hi)))
    if op == "react":
        ps += [float(rng.uniform(-2, 2)) for _ in range(n_src)]
    return ps


def rand_rule(rng, C, op=None, prov="rand", arity=None):
    pool = random_op_pool()
    op = op or pool[int(rng.integers(len(pool)))]
    ns = OPS[op][0]
    if ns == -1:
        ns = arity if arity else int(rng.integers(1, 4))
    src = [int(rng.integers(C)) for _ in range(ns)]
    return {"op": op, "src": src, "dst": int(rng.integers(C)), "p": rand_params(op, rng, ns), "prov": prov}


def validate(g) -> list:
    errs = []
    C = g.get("C")
    if not isinstance(C, int) or not 1 <= C <= CMAX:
        errs.append("C")
        return errs
    if g["topo"]["kind"] not in TOPOS:
        errs.append("topo")
    if g["bc"] not in BCS:
        errs.append("bc")
    if g["init"]["kind"] not in INITS:
        errs.append("init")
    if not 1 <= len(g["rules"]) <= MAXRULES:
        errs.append("n_rules")
    for i, r in enumerate(g["rules"]):
        if r["op"] not in OPS:
            errs.append(f"op{i}")
            continue
        ns = OPS[r["op"]][0]
        if ns >= 0 and len(r["src"]) != ns:
            errs.append(f"src{i}")
        if ns == -1 and not 1 <= len(r["src"]) <= 8:
            errs.append(f"src{i}")
        if any(not 0 <= s < C for s in r["src"]) or not 0 <= r["dst"] < C:
            errs.append(f"chan{i}")
        want = len(OPS[r["op"]][1]) + (len(r["src"]) if r["op"] == "react" else 0)
        if len(r["p"]) != want:
            errs.append(f"p{i}")
        if r["op"] == "lensmap" and not r.get("lens"):
            errs.append(f"lens{i}")
    return errs


# ----------------------------------------------------------------------------
# topology


def _neighbors(topo, N):
    kind = topo["kind"]
    if kind in ("ring", "line"):
        idx = np.arange(N)
        return np.stack([(idx - 1) % N, (idx + 1) % N], 1)
    if kind == "rrg":
        rng = np.random.default_rng(int(topo.get("seed", 0)))
        k = 3
        nb = np.zeros((N, k), dtype=int)
        for i in range(N):
            nb[i] = (i + rng.integers(1, N, size=k)) % N
        return nb
    if kind == "star":
        nb = np.zeros((N, 2), dtype=int)
        nb[0] = [1, N - 1]
        nb[1:, :] = 0
        return nb
    return None  # mean field


class Field:
    def __init__(self, g, N, bc_override=None, topo_override=None, lag=0):
        self.N = N
        self.topo = topo_override or g["topo"]
        self.bc = bc_override or g["bc"]
        self.nb = _neighbors(self.topo, N)
        self.lag = lag

    def _edges(self, x, out):
        if self.topo["kind"] == "line" or self.bc != "periodic":
            if self.bc == "fixed0":
                out[0] = x[1] / 2.0
                out[-1] = x[-2] / 2.0
            elif self.bc == "reflect":
                out[0] = x[1]
                out[-1] = x[-2]
            elif self.bc == "absorb":
                out[0] = 0.0
                out[-1] = 0.0
        return out

    def nmean(self, x):
        if self.nb is None:
            return np.full_like(x, x.mean())
        out = x[self.nb].mean(1)
        if self.topo["kind"] in ("ring", "line"):
            out = self._edges(x, out)
        return out

    def nmax(self, x):
        if self.nb is None:
            return np.full_like(x, x.max())
        return x[self.nb].max(1)


def _init(g, C, N, seed):
    kind = g["init"]["kind"]
    amp = float(g["init"].get("amp", 1.0))
    rng = np.random.default_rng(seed)
    X = np.zeros((C, N))
    if kind == "spike" and seed == 0:
        X[:, N // 2] = amp
    elif kind == "spike":
        X[:, int(rng.integers(N))] = amp
        X += 0.01 * rng.standard_normal((C, N))
    elif kind == "random":
        X = amp * rng.uniform(-1, 1, (C, N))
    elif kind == "gradient":
        X = amp * np.tile(np.linspace(-1, 1, N), (C, 1))
        if seed:
            X += 0.05 * rng.standard_normal((C, N))
    elif kind == "blocks":
        X = amp * np.tile(np.repeat([1.0, -1.0, 0.5, 0.0], N // 4 + 1)[:N], (C, 1))
        if seed:
            X = np.roll(X, int(rng.integers(N)), axis=1) + 0.05 * rng.standard_normal((C, N))
    elif kind == "alternate":
        X = amp * np.tile(np.where(np.arange(N) % 2 == 0, 1.0, -1.0), (C, 1))
        if seed:
            X += 0.05 * rng.standard_normal((C, N))
    for c in range(1, C):  # channels differ so cross-channel rules are not trivially symmetric
        X[c] = np.roll(X[c], 3 * c) * (1.0 - 0.2 * c)
    return X


def _blockmean(x, b):
    N = x.shape[0]
    bs = 2 ** b
    nb = N // bs
    if nb < 1:
        return np.full_like(x, x.mean())
    head = x[: nb * bs].reshape(nb, bs).mean(1).repeat(bs)
    if head.shape[0] < N:
        head = np.concatenate([head, np.full(N - head.shape[0], x[nb * bs:].mean())])
    return head


def _lens_apply(lens_genome, X):
    from tyche import lens as tl  # read-only import of Tyche's lens executor
    Z = tl.execute(lens_genome, X.T)  # cells play the role of time: causal along the field
    z = Z[:, 0]
    s = z.std()
    return np.tanh((z - z.mean()) / (s + 1e-9)) if s > 0 else np.zeros_like(z)


# ----------------------------------------------------------------------------
# execution


def run(g, seed=0, T=T_DEFAULT, N=N_DEFAULT, opts=None):
    """Execute genome g. Returns (trace[T, C, N], info). Deterministic."""
    opts = opts or {}
    C = g["C"]
    rules = g["rules"]
    field = Field(g, N, opts.get("bc"), opts.get("topo"), opts.get("lag", 0))
    X = _init(g, C, N, seed)
    if opts.get("ic_eps"):
        X[0, N // 3] += opts["ic_eps"]
    if opts.get("ic_flip"):
        X = -X
    if opts.get("chan_rot") and C > 1:
        X = np.roll(X, 1, axis=0)
    M = np.zeros((C, N))
    m0 = X.mean(1).copy()
    H = [X.copy() for _ in range(HIST)]
    noise = opts.get("noise", 0.0)
    nrng = np.random.default_rng(10_000 + seed) if noise else None
    frozen = opts.get("freeze")
    X0 = X.copy()
    quant = opts.get("quant")
    sync = opts.get("sync", False)
    lagdepth = opts.get("lag", 0)
    trace = np.empty((T, C, N))
    blowup = False
    lens_cache = {}
    for t in range(T):
        base = X.copy() if sync else None
        delta = np.zeros_like(X) if sync else None
        for r in rules:
            op = r["op"]
            p = r["p"]
            d = r["dst"]
            S = base if sync else X
            view = H[-1 - lagdepth] if lagdepth else S
            if op == "diffuse":
                new = S[d] + p[0] * (field.nmean(view[r["src"][0]]) - S[d])
            elif op == "advect":
                new = S[d] + p[1] * (np.roll(view[r["src"][0]], int(p[0])) - S[d])
            elif op == "react":
                prod = np.ones(N)
                for j, s in enumerate(r["src"]):
                    prod = prod * (p[1] + p[2 + j] * np.tanh(S[s]))
                new = S[d] + p[0] * np.tanh(prod)
            elif op == "saturate":
                new = p[0] * np.tanh(S[d] / p[0])
            elif op == "conserve":
                new = S[d] - p[0] * (S[d].mean() - m0[d])
            elif op == "decay":
                new = S[d] * (1.0 - p[0])
            elif op == "remember":
                if not opts.get("no_memory"):
                    M[d] = (1 - p[0]) * M[d] + p[0] * S[r["src"][0]]
                continue
            elif op == "recall":
                mem = np.zeros(N) if opts.get("no_memory") else M[d]
                new = S[d] + p[0] * (mem - S[d])
            elif op == "threshold":
                new = S[d] + p[1] * np.tanh(8.0 * (S[r["src"][0]] - p[0]))
            elif op == "replicate":
                src = S[r["src"][0]]
                new = S[d] + p[0] * np.maximum(field.nmax(src) - S[d], 0.0)
            elif op == "select":
                q = np.quantile(S[d], 1.0 - p[0])
                new = np.where(S[d] >= q, S[d], S[d] * (1.0 - p[1]))
            elif op == "mirror":
                new = (1 - p[0]) * S[d] + p[0] * S[d][::-1]
            elif op == "coarse":
                new = S[d] + p[1] * (_blockmean(S[r["src"][0]], int(p[0])) - S[d])
            elif op == "delay":
                new = S[d] + p[1] * (H[-int(p[0])][r["src"][0]] - S[d])
            elif op == "wrap":
                P = p[0]
                new = np.mod(S[d] + P / 2.0, P) - P / 2.0
            elif op == "rank":
                rk = np.argsort(np.argsort(S[d])) / max(N - 1, 1) * 2.0 - 1.0
                sd = S[d].std()
                new = (1 - p[0]) * S[d] + p[0] * (S[d].mean() + rk * sd)
            elif op == "drive":
                cell = int(p[2] * N) % N
                new = S[d].copy()
                new[cell] += p[0] * np.sin(2.0 * np.pi * t / p[1])
            elif op == "gate":
                cond = S[r["src"][0]]
                new = S[d] + p[1] * np.where(cond > p[0], S[r["src"][1]] - S[d], 0.0)
            elif op == "inject":
                mem = np.zeros(N) if opts.get("no_memory") else M[d]
                new = S[d] + p[0] * mem
            elif op == "modulate":
                mem = np.zeros(N) if opts.get("no_memory") else M[d]
                new = S[d] + p[0] * mem * S[r["src"][0]]
            elif op == "lensmap":
                key = id(r)
                if key not in lens_cache:
                    lens_cache[key] = r["lens"]
                new = S[d] + p[0] * (_lens_apply(lens_cache[key], S) - S[d])
            else:  # pragma: no cover
                raise ValueError(op)
            if sync:
                delta[d] += new - base[d]
            else:
                X[d] = new
        if sync:
            X = base + delta
        if noise:
            X = X + noise * nrng.standard_normal(X.shape)
        if frozen:
            X[:, :frozen] = X0[:, :frozen]
        if field.bc == "absorb":
            X[:, 0] = 0.0
            X[:, -1] = 0.0
        if quant:
            X = np.round(X.astype(np.float32) / quant) * quant
            X = X.astype(np.float64)
        if not np.all(np.isfinite(X)) or np.abs(X).max() > CLIP:
            blowup = True
            X = np.clip(np.nan_to_num(X, nan=0.0, posinf=CLIP, neginf=-CLIP), -CLIP, CLIP)
        trace[t] = X
        H.append(X.copy())
        H.pop(0)
    return trace, {"blowup": blowup}
