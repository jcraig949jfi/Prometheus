"""The dark ecology: marginal lens value, residuals, selection, reserve.

MarginalLensValue(L | w, r, o, split) =
    acc_o(ecology features + L features) - acc_o(ecology features)
paired on the same points. Never collapsed across worlds, rulers or
organisms: selection is epsilon-lexicase over the case vector.

Residual scopes (several coexist; all frozen at epoch start):
  all   every point of the split
  err   points every organism mispredicts under the current ecology
  dis   points on which the organisms disagree under the current ecology
The residual is "information not yet made useful by the current ecology",
never "noise".
"""

from __future__ import annotations

import numpy as np

from . import lens as Lm
from . import worlds as Wm
from .organisms import ORGANISMS, RULERS, fit_predict, split_xy

SCOPES = ("all", "err", "dis")
TAB_BUDGET = 10


class WorldEval:
    """One world under one input seed, with an ecology feature cache."""

    def __init__(self, spec, seed):
        self.spec = spec
        self.seed = seed
        self.X, self.Y = Wm.generate(spec, seed)
        self._eco_key = None
        self._eco_blocks = None
        self._base = {}
        self._zcache = {}

    def lens_Z(self, g):
        k = Lm.canonical(g)
        z = self._zcache.get(k)
        if z is None:
            z = Lm.execute(g, self.X)
            if len(self._zcache) > 200:
                self._zcache.clear()
            self._zcache[k] = z
        return z

    def set_ecology(self, eco):
        """eco: list of admitted genomes (oldest first)."""
        key = tuple(Lm.lens_id(g) for g in eco)
        if key == self._eco_key:
            return
        self._eco_key = key
        blocks = [self.lens_Z(g) for g in reversed(eco)]  # newest first
        self._eco_blocks = blocks + [self.X.astype(float)]
        self._base = {}

    def features(self, Z=None, org=None):
        blocks = ([Z] if Z is not None else []) + self._eco_blocks
        F = np.hstack(blocks)
        if org == "tab":
            F = F[:, :TAB_BUDGET]
        return F

    def correct(self, Z, ruler, org, splits):
        """Per-point correctness on each split (dict split -> bool array)."""
        F = self.features(Z, org)
        Ftr, ytr = split_xy(F, self.Y, ruler, "train")
        evs = [split_xy(F, self.Y, ruler, s) for s in splits]
        preds = fit_predict(org, Ftr, ytr, [e[0] for e in evs])
        return {s: p == e[1] for s, p, e in zip(splits, preds, evs)}

    def base(self, ruler, org, splits):
        need = [s for s in splits if (ruler, org, s) not in self._base]
        if need:
            c = self.correct(None, ruler, org, need)
            for s in need:
                self._base[(ruler, org, s)] = c[s]
        return {s: self._base[(ruler, org, s)] for s in splits}

    def residual_masks(self, ruler, split="val"):
        cs = [self.base(ruler, o, [split])[split] for o in ORGANISMS]
        err = ~np.any(cs, axis=0)
        dis = ~(np.all(cs, axis=0) | err)
        return {"all": np.ones_like(err), "err": err, "dis": dis}

    def gains(self, g, splits=("val",), scopes=SCOPES, orgs=ORGANISMS, rulers=tuple(RULERS)):
        """{(ruler, org, split, scope): (gain, z, n)} for lens g."""
        return self.gains_Z(self.lens_Z(g), splits, scopes, orgs, rulers)

    def gains_Z(self, Z, splits=("val",), scopes=SCOPES, orgs=ORGANISMS, rulers=tuple(RULERS)):
        out = {}
        for r in rulers:
            masks = {s: self.residual_masks(r, s) for s in splits}
            for o in orgs:
                c1 = self.correct(Z, r, o, list(splits))
                c0 = self.base(r, o, list(splits))
                for s in splits:
                    d = c1[s].astype(float) - c0[s].astype(float)
                    for sc in scopes:
                        m = masks[s][sc]
                        out[(r, o, s, sc)] = paired(d[m])
        return out


def paired(d):
    n = len(d)
    if n == 0:
        return (0.0, 0.0, 0)
    mu = float(d.mean())
    sd = float(d.std())
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    z = mu / se if se > 0 else (0.0 if mu == 0 else float(np.sign(mu)) * 99.0)
    return (mu, float(z), n)


# ------------------------------------------------------------ worker side

_SPECS = {}
_W = {}
_CACHE_MAX = 64


def _worker_init(specs, cache_max=64):
    global _SPECS, _W, _CACHE_MAX
    _SPECS = {s["id"]: s for s in specs}
    _W = {}
    _CACHE_MAX = cache_max


def get_world(wid, seed):
    k = (wid, seed)
    if k not in _W:
        if len(_W) >= _CACHE_MAX:
            _W.pop(next(iter(_W)))
        _W[k] = WorldEval(_SPECS[wid], seed)
    return _W[k]


def _eval_task(args):
    """Selection-time evaluation: val split, all cases, input seed 1."""
    wid, genomes, eco = args
    we = get_world(wid, 1)
    we.set_ecology(eco)
    res = []
    for g in genomes:
        gd = we.gains(g, splits=("val",))
        res.append({f"{r}|{o}|{sc}": round(v[0], 6) for (r, o, s, sc), v in gd.items()})
    return wid, res


def _base_task(args):
    wid, seed, eco, splits = args
    we = get_world(wid, seed)
    we.set_ecology(eco)
    out = {}
    for r in RULERS:
        for o in ORGANISMS:
            b = we.base(r, o, list(splits))
            for s in splits:
                out[f"{r}|{o}|{s}"] = float(b[s].mean())
        for s in splits:
            m = we.residual_masks(r, s)
            out[f"{r}|{s}|resid_err_frac"] = float(m["err"].mean())
            out[f"{r}|{s}|resid_dis_frac"] = float(m["dis"].mean())
    for s in splits:
        lo, hi = Wm.SPLITS[s]
        y = we.Y[lo:hi]
        out[f"majority|{s}"] = float(np.bincount(y).max() / len(y))
    return wid, out


def _gains_task(args):
    """Generic: gains of lens g on (wid, seed) against ecology eco.
    ablate: optional virtual channel whose world column is circularly shifted
    (997 steps) in the LENS input only; the ecology is untouched."""
    wid, seed, g, eco, splits, scopes, orgs, rulers, ablate = args
    we = get_world(wid, seed)
    we.set_ecology(eco)
    if ablate is None:
        Z = we.lens_Z(g)
    else:
        Xm = we.X.copy()
        c = ablate % Xm.shape[1]
        Xm[:, c] = np.roll(Xm[:, c], 997)
        Z = Lm.execute(g, Xm)
    gd = we.gains_Z(Z, splits, scopes, orgs, rulers)
    return {"|".join(k): v for k, v in gd.items()}


# ------------------------------------------------------------ selection

def eps_lexicase(M, rng, n_select):
    """M: (n_individuals x n_cases) values, higher better. Returns indices."""
    n, c = M.shape
    med = np.median(M, 0)
    eps = np.median(np.abs(M - med), 0)
    chosen = []
    for _ in range(n_select):
        cand = np.arange(n)
        for j in rng.permutation(c):
            v = M[cand, j]
            best = v.max()
            cand = cand[v >= best - eps[j]]
            if len(cand) == 1:
                break
        chosen.append(int(rng.choice(cand)))
    return chosen


def novelty(sigs, pool_sigs, k=5):
    if len(pool_sigs) == 0:
        return np.ones(len(sigs))
    P = np.asarray(pool_sigs)
    out = []
    for s in sigs:
        d = np.abs(P - s).mean(1)
        d = np.sort(d)
        d = d[d > 1e-12]  # exclude self / clones
        out.append(float(d[:k].mean()) if len(d) else 0.0)
    return np.array(out)
