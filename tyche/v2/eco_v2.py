"""Tyche v2 evaluation core (extends v1 gate-1 repairs: per-world ecology,
order-independent tab inputs, capability deficit).

New in v2:
- cases carry (gain, z) so STRICT gating and natural histories can tell a
  significant win from a noise-level one;
- organism-free coalition screen: median-binarised lens outputs, joint
  mutual information with Y on the TRAIN split, synergy = MI(joint) -
  max(MI(parts)); only the top candidates are fitted by organisms;
- functional precursor carriers: MI(lens outputs; hidden precursor) on the
  train split against a permutation null (answer key; tracer only).
"""

from __future__ import annotations

import numpy as np

from .. import lens as Lm
from ..organisms import ORGANISMS
from ..v1.eco_v1 import WorldEvalV1
from . import worlds_v2 as W2
from .certify import mi

RULERS = ("R0",)
TR = W2.W0.SPLITS["train"]


class WorldEvalV2(WorldEvalV1):
    def __init__(self, spec, seed):
        self.spec = spec
        self.seed = seed
        self.X, self.Y = W2.generate(spec, seed)
        self._eco_key = None
        self._eco_blocks = None
        self._base = {}
        self._zcache = {}
        self._bin = {}

    def binarised(self, g):
        k = Lm.canonical(g)
        b = self._bin.get(k)
        if b is None:
            Z = self.lens_Z(g)
            lo, hi = TR
            med = np.median(Z[lo:hi], 0)
            b = (Z > med).astype(np.int64)
            if len(self._bin) > 2000:
                self._bin.clear()
            self._bin[k] = b
        return b


_SPECS, _W = {}, {}


def _init(specs):
    global _SPECS, _W
    _SPECS = {s["id"]: s for s in specs}
    _W = {}


def world(wid, seed):
    k = (wid, seed)
    if k not in _W:
        if len(_W) >= 48:
            _W.pop(next(iter(_W)))
        _W[k] = WorldEvalV2(_SPECS[wid], seed)
    return _W[k]


def _cz(gd):
    return {f"{r}|{o}": (round(v[0], 6), round(v[1], 3)) for (r, o, s, sc), v in gd.items()}


def task_lenses(args):
    wid, genomes, eco = args
    we = world(wid, 1)
    we.set_ecology(eco)
    return wid, [_cz(we.gains(g, splits=("val",), scopes=("all",), rulers=RULERS)) for g in genomes]


def _key(cols):
    k = np.zeros(cols.shape[0], dtype=np.int64)
    for j in range(cols.shape[1]):
        k = k * 2 + cols[:, j]
    return k


def task_screen(args):
    """Organism-free synergy screen of coalitions (tuples of genomes)."""
    wid, coalitions = args
    we = world(wid, 1)
    lo, hi = TR
    y = we.Y[lo:hi]
    out, single = [], {}
    for co in coalitions:
        bs = [we.binarised(g)[lo:hi] for g in co]
        parts = []
        for g, b in zip(co, bs):
            k = Lm.canonical(g)
            if k not in single:
                single[k] = mi(_key(b), y)
            parts.append(single[k])
        joint = mi(_key(np.hstack(bs)), y)
        out.append((round(joint, 5), round(joint - max(parts), 5)))
    return wid, out


def task_coalitions(args):
    """Organism evaluation of coalitions: the organism sees all members'
    outputs (plus ecology), val split."""
    wid, coalitions, eco = args
    we = world(wid, 1)
    we.set_ecology(eco)
    out = []
    for co in coalitions:
        Z = np.hstack([we.lens_Z(g) for g in co])
        out.append(_cz(we.gains_Z(Z, splits=("val",), scopes=("all",), rulers=RULERS)))
    return wid, out


def task_deficit(args):
    wid, seed, eco, oracle, split = args
    we = world(wid, seed)
    we.set_ecology(eco)
    out = {}
    Zo = Lm.execute(oracle, we.X) if oracle is not None else None
    for o in ORGANISMS:
        b = we.base("R0", o, [split])[split]
        out[f"R0|{o}|acc_eco"] = float(b.mean())
        if Zo is not None:
            c = we.correct(Zo, "R0", o, [split])[split]
            out[f"R0|{o}|deficit"] = float(c.mean() - b.mean())
        else:
            out[f"R0|{o}|deficit"] = None
    return wid, out


def task_gains(args):
    wid, seed, gl, eco, splits, orgs, ablate = args
    we = world(wid, seed)
    we.set_ecology(eco)
    X = we.X
    if ablate is not None:
        X = X.copy()
        c = ablate % X.shape[1]
        X[:, c] = np.roll(X[:, c], 997)
    Z = np.hstack([Lm.execute(g, X) if ablate is not None else we.lens_Z(g) for g in gl])
    gd = we.gains_Z(Z, splits, ("all",), orgs, RULERS)
    return {f"{r}|{o}|{s}": v for (r, o, s, sc), v in gd.items()}


def task_carriers(args):
    """Functional precursor carriage (answer key; tracer / optionality):
    for each genome, MI(binarised outputs; precursor i) minus the 99th
    percentile of 10 permutations, for every hidden precursor of `law`."""
    wid, law, genomes = args
    we = world(wid, 1)
    lo, hi = TR
    P = [p[lo:hi] for p in W2.precursors(law, we.X)]
    rng = np.random.default_rng(7)
    out = []
    for g in genomes:
        k = _key(we.binarised(g)[lo:hi])
        row = []
        for p in P:
            m = mi(k, p)
            null = np.percentile([mi(k, rng.permutation(p)) for _ in range(10)], 99)
            row.append(round(m - null, 5))
        out.append(row)
    return wid, out
