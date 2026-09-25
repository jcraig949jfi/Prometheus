"""WTP-03 substrate collider core (PREREG_WTP03 s2-s4).

One EXPERIENCE STREAM per (world, seed, field): the exact (step, cell, value) samples a fixed
behaviour carrier (the marginal learner, a null-class substrate) was told during its life.
Every substrate and every null model learns from the SAME stream: same observations, same
actions, same world stochasticity, matched memory (cap floats), compute counted in flops.

Test sets (cells the training stream never touched):
  interp  full stream; unseen cells with a seen cell one coordinate away (smoothing can help)
  novel   full stream; unseen cells with some coordinate value never seen
  recomb  HOLDOUT stream: choose value subsets H_m on every mode and delete every sample with
          >= 2 coordinates in H. Every H value is still seen alone, no PAIR of H values ever is.
          Test = the block H_1 x ... x H_D (all primitives observed, their combinations never).
Scores: AC = -log10(MSE/V0) (V0 = birth variance, fixed; clipped to [-3, 6]).
XC(substrate, set) = AC(substrate) - max over the null ladder N0..N5 of AC(null)."""
import copy
import hashlib

import numpy as np

from ensorain.wtp.organism import KINDS, Memory, Additive, LowRank, make_memory
from .world3 import AC, run_life

# ------------------------------------------------------------------ surrogates (s4)


def additive_part(x):
    mu = x.mean()
    out = np.full(x.shape, mu)
    for m in range(x.ndim):
        ax = tuple(k for k in range(x.ndim) if k != m)
        out = out + (x.mean(axis=ax, keepdims=True) - mu)
    return out


def marginal_surrogate(rng):
    """Preserves the mean, every per-mode marginal mean and the variance EXACTLY; destroys all
    interaction structure (the residual is permuted, re-centred on every mode and rescaled)."""
    def hook(x, rew):
        a = additive_part(x)
        r = (x - a).reshape(-1)
        rp = r[rng.permutation(r.size)].reshape(x.shape)
        rp = rp - additive_part(rp)                     # remove the permuted residual's own main effects
        sd_r, sd_p = r.std(), rp.std()
        if sd_p > 1e-12:
            rp = rp * (sd_r / sd_p)                     # restore the residual's variance exactly
        return a + rp, rew
    return hook


def shuffle_surrogate(rng):
    def hook(x, rew):
        return x.reshape(-1)[rng.permutation(x.size)].reshape(x.shape), rew
    return hook


def hook_for(field, seed):
    if field == "real":
        return None
    rng = np.random.default_rng(int(hashlib.sha256(f"{field}:{seed}".encode()).hexdigest()[:12], 16))
    return {"marg": marginal_surrogate, "shuf": shuffle_surrogate}[field](rng)


# ------------------------------------------------------------------ experience


CALIB_PANEL = ("additive", "dct", "lowrank", "cp", "tt")
CONSOLIDATE = dict(every=32, sweeps=2, window=256)   # generic learning-capable calibration panel (s5)


def carrier(g, kind=None):
    """The behaviour carrier: the world's own physics with organism 0's memory replaced by a
    calibration-panel learner (default: the one preflight chose for this world, stored in
    g['memory']['carrier']), using that substrate's fixed recipe. One carrier per world;
    every substrate in the collider learns from the stream it produced."""
    kind = kind or g["memory"].get("carrier", "additive")
    rule, lr, _ = RULE.get(kind, ("nlms", 0.5, 1))
    gc = copy.deepcopy(g)
    gc["memory"]["substrate"] = kind
    gc["memory"]["fluid"] = 0
    gc["learning"] = dict(gc["learning"], rule=rule, lr=lr, consolidate=CONSOLIDATE)
    return gc


def experience(g, seed, field="real", lifetime=None, kind=None):
    tap = dict(t=[], c=[], y=[])
    life = run_life(carrier(g, kind), seed, tap=tap, field_hook=hook_for(field, seed), lifetime=lifetime, excursions=False)
    if "x_final" not in tap:
        return None, life
    cat = (lambda k, dt: np.concatenate(tap[k]).astype(dt) if tap[k] else np.zeros(0, dt))
    st = dict(t=cat("t", int), c=cat("c", int), y=cat("y", float), x=tap["x_final"], V0=tap["x_birth_var"],
              seen=tap["seen"], dims=list(tap["dims"]), T=tap["T"])
    ok = np.isfinite(st["y"])
    st["t"], st["c"], st["y"] = st["t"][ok], st["c"][ok], st["y"][ok]
    st["digest"] = hashlib.sha256(np.concatenate([st["c"].astype(float), st["y"]]).tobytes()).hexdigest()[:16]
    return st, life


def test_sets(st, rng, n=512):
    dims = st["dims"]
    cells = int(np.prod(dims))
    seen = np.zeros(cells, bool)
    seen[st["seen"]] = True
    seen[st["c"]] = True
    S = seen.reshape(dims)
    near = np.zeros(dims, bool)
    for m in range(len(dims)):
        near |= S.any(axis=m, keepdims=True)
    val_seen = [S.any(axis=tuple(k for k in range(len(dims)) if k != m)) for m in range(len(dims))]
    allv = np.ones(dims, bool)
    for m in range(len(dims)):
        sh = [1] * len(dims)
        sh[m] = dims[m]
        allv &= val_seen[m].reshape(sh)
    uns = ~S
    masks = dict(interp=uns & near, novel=uns & ~allv)
    out = {"recomb": np.zeros(0, int)}
    for k, msk in masks.items():
        idx = np.flatnonzero(msk.reshape(-1))
        out[k] = np.sort(rng.choice(idx, size=min(n, len(idx)), replace=False)) if len(idx) else idx
    out["n_avail"] = {k: int(m.sum()) for k, m in masks.items()}
    out["seen_frac"] = float(seen.mean())
    return out


def holdout(st, rng, min_block=64, max_removed=0.6):
    """The s18 recombination construction on a stream. Returns (stream_R, block cells, info) or (None, None, info)."""
    dims = st["dims"]
    D = len(dims)
    A = _addr(dims, st["c"])
    cells = int(np.prod(dims))
    for p in (0.5, 0.4, 0.34, 0.25, 0.2):
        H = [np.sort(rng.choice(d, size=max(1, int(round(p * d))), replace=False)) for d in dims]
        inH = np.stack([np.isin(A[:, m], H[m]) for m in range(D)], 1)
        drop = inH.sum(1) >= 2
        blk = np.array(np.meshgrid(*H, indexing="ij")).reshape(D, -1).T
        nblk = len(blk)
        if nblk < min_block or drop.mean() > max_removed or (~drop).sum() < 50:
            continue
        # every single H value must still be seen in the kept stream
        kept = A[~drop]
        if not all(np.isin(H[m], kept[:, m]).all() for m in range(D)):
            continue
        bc = np.ravel_multi_index(blk.T, dims)
        stR = dict(st, t=st["t"][~drop], c=st["c"][~drop], y=st["y"][~drop])
        return stR, np.sort(rng.choice(bc, size=min(512, len(bc)), replace=False)),             dict(p=p, H=[h.tolist() for h in H], removed=float(drop.mean()), block=int(nblk), cells=cells)
    return None, None, dict(reason="no block with >= 64 cells, <= 60% removed and every H value still seen")


# ------------------------------------------------------------------ null ladder (s2)


def _addr(dims, cells):
    return np.array(np.unravel_index(np.asarray(cells, int), dims)).T


def _onehot(dims, A):
    F = [np.ones((len(A), 1))]
    for m, d in enumerate(dims):
        F.append(np.eye(d)[A[:, m]][:, 1:])
    return np.hstack(F)


def null_ladder(st, cap, tests):
    """Batch (hindsight-favourable) fits of the cheap nulls. Returns {null: {set: AC}}."""
    dims, c, y, x, V0 = st["dims"], st["c"], st["y"], st["x"].reshape(-1), st["V0"]
    A = _addr(dims, c)
    res = {}
    n = len(y)
    rec = y[-max(1, n // 4):]
    preds = {}
    preds["N0_zero"] = lambda T: np.zeros(len(T))
    preds["N1_const"] = lambda T, v=float(y.mean()) if n else 0.0: np.full(len(T), v)
    preds["N1_const_recent"] = lambda T, v=float(rec.mean()) if n else 0.0: np.full(len(T), v)
    if n >= 2:
        F = _onehot(dims, A)
        w = np.linalg.lstsq(F.T @ F + 1e-3 * np.eye(F.shape[1]), F.T @ y, rcond=None)[0]
        preds["N2_marginal"] = lambda T, w=w: _onehot(dims, _addr(dims, T)) @ w
        L = np.hstack([np.ones((n, 1)), A / np.maximum(1, np.array(dims) - 1)])
        wl = np.linalg.lstsq(L.T @ L + 1e-6 * np.eye(L.shape[1]), L.T @ y, rcond=None)[0]
        preds["N3_linear"] = lambda T, wl=wl: np.hstack([np.ones((len(T), 1)), _addr(dims, T) / np.maximum(1, np.array(dims) - 1)]) @ wl
        # N4 bounded lookup: the cap//2 most recent distinct cells (key+value = 2 floats), predict the
        # mean of the stored values at minimum Hamming distance (graph/nearest-neighbour smoothing)
        last = {}
        for cc, yy in zip(c, y):
            last.pop(int(cc), None)
            last[int(cc)] = float(yy)
        keys = list(last)[-max(1, cap // 2):]
        KA = _addr(dims, keys)
        KV = np.array([last[k] for k in keys])

        def lookup(T, KA=KA, KV=KV):
            TA = _addr(dims, T)
            out = np.empty(len(T))
            for i in range(0, len(T), 256):
                D = (TA[i:i + 256, None, :] != KA[None, :, :]).sum(2)
                mn = D.min(1, keepdims=True)
                W = (D == mn)
                out[i:i + 256] = (W * KV[None]).sum(1) / W.sum(1)
            return out
        preds["N4_lookup"] = lookup
    for k, f in preds.items():
        res[k] = {s: (AC(f(tests[s]), x[tests[s]], V0) if len(tests[s]) >= 32 else None) for s in ("interp", "recomb", "novel")}
    return res


# ------------------------------------------------------------------ substrates (s1, s11)


class HybridAL(Memory):
    """Marginal learner + low-rank on the residual, one budget (the s16 hybrid of N2 and matrix)."""
    kind = "hybrid_al"

    def __init__(self, dims, cap, rng):
        super().__init__(dims, cap, rng)
        self.a = Additive(dims, cap, rng)
        rest = cap - self.a.n_floats()
        if rest < 2:
            raise ValueError("no budget left for the low-rank part")
        self.l = LowRank(dims, rest, rng)
        if self.a.n_floats() + self.l.n_floats() > cap:
            raise ValueError("hybrid over budget")

    def n_floats(self):
        return self.a.n_floats() + self.l.n_floats()

    def predict(self, cells):
        return self.a.predict(cells) + self.l.predict(cells)

    def learn(self, cells, y, rule, lr):
        f = self.a.learn(cells, y, rule, lr)
        return f + self.l.learn(cells, y - self.a.predict(cells), rule, lr)

    def params(self):
        return self.a.params() + self.l.params()


SIMPLE = ("constant", "table", "sketch", "additive", "mixture")      # online members of N5
STRUCT = ("lowrank", "cp", "tt", "dct", "hybrid_al")                  # candidate substrates
PANEL = SIMPLE + STRUCT
NOT_IMPLEMENTED = {"symbolic": "no symbolic-rule substrate exists in this engine (recorded, not hacked)",
                   "graph_external": "represented by N4_lookup (bounded graph/nearest-neighbour store) in the null ladder"}
# (rule, lr, passes). Structured recipes chosen on dev planted worlds by recipes.py (runs/wtp03/recipes.json)
RULE = {"table": ("sgd", 1.0, 1), "sketch": ("sgd", 0.5, 1), "constant": ("nlms", 0.5, 1), "additive": ("nlms", 0.5, 1),
        "mixture": ("nlms", 0.5, 1), "lowrank": ("sgd", 0.1, 3), "cp": ("sgd", 0.1, 3), "tt": ("sgd", 0.1, 3),
        "dct": ("nlms", 0.1, 1), "hybrid_al": ("nlms", 0.1, 1)}


def make(kind, dims, cap, rng):
    if kind == "constant":
        return KINDS["none"](dims, cap, rng)
    if kind == "hybrid_al":
        return HybridAL(dims, cap, rng)
    return make_memory(kind, dims, cap, rng)


def train(kind, st, cap, seed, recipe=None):
    """Online, in stream order. Returns (memory, flops) or (None, reason)."""
    dims = st["dims"]
    rng = np.random.default_rng(seed)
    try:
        mem = make(kind, dims, cap, rng)
    except ValueError as ex:
        return None, f"INCOMPATIBLE: {ex}"
    if kind != "constant" and mem.n_floats() > cap:
        return None, f"INCOMPATIBLE: {mem.n_floats()} floats > cap {cap}"
    n = len(st["y"])
    A = _addr(dims, st["c"])
    y = st["y"]
    rule, lr, passes = recipe or RULE.get(kind, ("nlms", 0.5, 1))
    flops = 0
    for _ in range(passes):
        for i in range(0, n, 64):
            flops += mem.learn(A[i:i + 64], y[i:i + 64], rule, lr)
            for a in mem.params():
                if not np.all(np.isfinite(a)):
                    a[~np.isfinite(a)] = 0.0
    return mem, flops


def score(mem, st, tests):
    x, V0 = st["x"].reshape(-1), st["V0"]
    out = {}
    for s in ("interp", "recomb", "novel"):
        T = tests[s]
        out[s] = AC(mem.predict(_addr(st["dims"], T)), x[T], V0) if len(T) >= 32 else None
    return out


def _merge(a, b):
    return {s: (b[s] if s == "recomb" else a[s]) for s in ("interp", "recomb", "novel")}


def collide(st, cap, seed, kinds=PANEL, upto=None, tests=None, keep=None):
    """The full panel + ladder on one stream at one budget. XC per substrate per set.
    interp/novel: trained on the full stream; recomb: trained on the holdout stream."""
    if upto is not None:
        st = dict(st, t=st["t"][:upto], c=st["c"][:upto], y=st["y"][:upto])
    tests = tests or test_sets(st, np.random.default_rng(seed + 17))
    stR, blk, hinfo = holdout(st, np.random.default_rng(seed + 29))
    testsR = dict(interp=np.zeros(0, int), novel=np.zeros(0, int), recomb=blk if blk is not None else np.zeros(0, int))
    ladder = null_ladder(st, cap, tests)
    ladderR = null_ladder(stR, cap, testsR) if stR is not None else {k: dict(interp=None, recomb=None, novel=None) for k in ladder}
    ladder = {k: _merge(ladder[k], ladderR.get(k, dict(recomb=None))) for k in ladder}
    subs = {}
    for k in kinds:
        mem, fl = train(k, st, cap, seed + 101)
        if mem is None:
            subs[k] = dict(status=fl)
            continue
        acs = score(mem, st, tests)
        flR = 0
        if stR is not None:
            memR, flR = train(k, stR, cap, seed + 101)
            acs["recomb"] = score(memR, stR, testsR)["recomb"]
            if keep is not None and k in keep:
                keep[k] = (mem, memR)
        elif keep is not None and k in keep:
            keep[k] = (mem, None)
        subs[k] = dict(status="OK", n_floats=int(mem.n_floats()), flops=int(fl), flops_R=int(flR), AC=acs)
    best = {}
    for s in ("interp", "recomb", "novel"):
        cand = [v[s] for v in ladder.values() if v[s] is not None]
        cand += [subs[k]["AC"][s] for k in SIMPLE if subs.get(k, {}).get("status") == "OK" and subs[k]["AC"][s] is not None]
        best[s] = max(cand) if cand else None
    for k, v in subs.items():
        if v["status"] == "OK":
            v["XC"] = {s: (v["AC"][s] - best[s]) if v["AC"][s] is not None and best[s] is not None else None
                       for s in ("interp", "recomb", "novel")}
    return dict(cap=cap, ladder=ladder, best_null=best, subs=subs,
                n_test=dict(interp=int(len(tests["interp"])), novel=int(len(tests["novel"])), recomb=int(len(testsR["recomb"]))),
                n_avail=tests["n_avail"], holdout=hinfo, seen_frac=tests["seen_frac"], n_samples=int(len(st["y"])))
