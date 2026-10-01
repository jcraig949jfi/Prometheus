"""Tyche v1 evaluation core (gate 1 repairs).

- Per-world ecology: a world's ecology is its raw observation plus the
  lenses admitted ON THAT WORLD (v0's global ecology grew features for
  every organism on every world and drove cost and confounds).
- Organism inputs never depend on ecology ORDER: lin and tree see
  [candidate, ecology lenses, raw]; tab sees [candidate, raw] only (v0's
  newest-first 10-feature budget manufactured residuals, v0 F2).
- Residual = CAPABILITY DEFICIT on calibration worlds:
      D(W, r, o) = acc_o(ecology + oracle) - acc_o(ecology)
  where the oracle is the answer-key lens (never visible to evolution).
  v0's err/dis residuals measured organism disagreement (v0 F1) and are
  retired.
- Pair evaluation: the organism receives [L_a(X), L_b(X)] (plus ecology)
  and learns any combination itself: O(L_a(X), L_b(X)).
"""

from __future__ import annotations

import numpy as np

from .. import lens as Lm
from ..ecology import WorldEval, paired
from ..organisms import ORGANISMS

# v1 is a calibration experiment at ONE consequence ruler: the Z worlds are
# zero-marginal at R0 by construction; at R2 every required delay shifts by
# 2 and Z4 becomes one-precursor-present (found at design time: a single
# initial lens reached test +0.497 on Z4 at R2). R2 is excluded from v1.
RULERS = ("R0",)
from . import worlds_v1 as W1

TAB_BUDGET = 10


class WorldEvalV1(WorldEval):
    def __init__(self, spec, seed):
        self.spec = spec
        self.seed = seed
        self.X, self.Y = W1.generate(spec, seed)
        self._eco_key = None
        self._eco_blocks = None
        self._base = {}
        self._zcache = {}

    def features(self, Z=None, org=None):
        if org == "tab":
            blocks = ([Z] if Z is not None else []) + [self.X.astype(float)]
            return np.hstack(blocks)[:, :TAB_BUDGET]
        blocks = ([Z] if Z is not None else []) + self._eco_blocks
        return np.hstack(blocks)


_SPECS, _W, _CACHE_MAX = {}, {}, 24


def _init(specs, cache_max=24):
    global _SPECS, _W, _CACHE_MAX
    _SPECS = {s["id"]: s for s in specs}
    _W = {}
    _CACHE_MAX = cache_max


def world(wid, seed):
    k = (wid, seed)
    if k not in _W:
        if len(_W) >= _CACHE_MAX:
            _W.pop(next(iter(_W)))
        _W[k] = WorldEvalV1(_SPECS[wid], seed)
    return _W[k]


def _cases(gd):
    return {f"{r}|{o}": round(v[0], 6) for (r, o, s, sc), v in gd.items()}


def task_lenses(args):
    """Individual val gains of each genome on one world (seed 1)."""
    wid, genomes, eco = args
    we = world(wid, 1)
    we.set_ecology(eco)
    return wid, [_cases(we.gains(g, splits=("val",), scopes=("all",), rulers=RULERS)) for g in genomes]


def task_pairs(args):
    """Joint val gains of each pair (organism sees both outputs)."""
    wid, pairs, eco = args
    we = world(wid, 1)
    we.set_ecology(eco)
    out = []
    for ga, gb in pairs:
        Z = np.hstack([we.lens_Z(ga), we.lens_Z(gb)])
        out.append(_cases(we.gains_Z(Z, splits=("val",), scopes=("all",), rulers=RULERS)))
    return wid, out


def task_deficit(args):
    """Capability deficit per (ruler, organism) on `split`, plus ecology
    accuracy and majority. oracle None -> deficit reported as None."""
    wid, seed, eco, oracle, split = args
    we = world(wid, seed)
    we.set_ecology(eco)
    out = {}
    Zo = Lm.execute(oracle, we.X) if oracle is not None else None
    for r in RULERS:
        for o in ORGANISMS:
            b = we.base(r, o, [split])[split]
            out[f"{r}|{o}|acc_eco"] = float(b.mean())
            if Zo is not None:
                c = we.correct(Zo, r, o, [split])[split]
                out[f"{r}|{o}|acc_oracle"] = float(c.mean())
                out[f"{r}|{o}|deficit"] = float(c.mean() - b.mean())
            else:
                out[f"{r}|{o}|deficit"] = None
    lo, hi = W1.SPLITS[split]
    y = we.Y[lo:hi]
    out["majority"] = float(np.bincount(y).max() / len(y))
    return wid, out


def task_gains(args):
    """Generic: gains of Z-producing genome(s) g (a genome or a list of
    genomes whose outputs are concatenated) on (wid, seed)."""
    wid, seed, g, eco, splits, orgs, rulers, ablate = args
    we = world(wid, seed)
    we.set_ecology(eco)
    gl = g if isinstance(g, list) else [g]
    X = we.X
    if ablate is not None:
        X = X.copy()
        c = ablate % X.shape[1]
        X[:, c] = np.roll(X[:, c], 997)
    Z = np.hstack([Lm.execute(x, X) if ablate is not None else we.lens_Z(x) for x in gl])
    gd = we.gains_Z(Z, splits, ("all",), orgs, rulers)
    return {f"{r}|{o}|{s}": v for (r, o, s, sc), v in gd.items()}


__all__ = ["WorldEvalV1", "paired", "task_lenses", "task_pairs", "task_deficit", "task_gains", "_init"]
