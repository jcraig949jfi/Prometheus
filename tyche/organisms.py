"""ORGANISM and RULER.

Organisms are deliberately weak learners that act (predict a consequence)
from transformed observations. They are fitted on the train split only.

  lin   one-vs-rest ridge least squares on standardised features (linear)
  tree  depth-4 decision tree, min 20 samples per leaf
  tab   lookup table on median-binarised features (majority per cell,
        global majority for unseen cells)

Rulers measure consequences on a split, never inside a lens:

  R0    predict Y[t] from Z[t]       (the consequence revealed after t)
  R2    predict Y[t+2] from Z[t]     (anticipation two steps ahead)

A ruler value is accuracy; gains are paired differences of accuracy on the
same points (tyche.ecology). Rulers are never collapsed into one score.
"""

from __future__ import annotations

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from .worlds import SPLITS

ORGANISMS = ("lin", "tree", "tab")
RULERS = {"R0": 0, "R2": 2}


def _std(Ftr, *Fs):
    m = Ftr.mean(0)
    s = Ftr.std(0)
    s = np.where(s > 1e-9, s, 1.0)
    return [(F - m) / s for F in (Ftr,) + Fs]


def fit_predict(kind, Ftr, ytr, Fev):
    """Fit on (Ftr, ytr); return predictions for each matrix in Fev."""
    if kind == "lin":
        classes = np.unique(ytr)
        A, *B = _std(Ftr, *Fev)
        A = np.hstack([A, np.ones((len(A), 1))])
        Yh = (ytr[:, None] == classes[None, :]).astype(float)
        G = A.T @ A + 1.0 * np.eye(A.shape[1])
        Wt = np.linalg.solve(G, A.T @ Yh)
        return [classes[np.argmax(np.hstack([b, np.ones((len(b), 1))]) @ Wt, 1)] for b in B]
    if kind == "tree":
        m = DecisionTreeClassifier(max_depth=4, min_samples_leaf=20, random_state=0)
        m.fit(Ftr, ytr)
        return [m.predict(F) for F in Fev]
    if kind == "tab":
        Ftr = Ftr[:, :60]
        med = np.median(Ftr, 0)
        # a feature whose values sit at or above the median everywhere
        # (e.g. a 0/1 feature with median 1) splits at >= instead of >
        ge = (Ftr > med).all(0) | ~(Ftr > med).any(0)
        w = (1 << np.arange(Ftr.shape[1])).astype(np.int64)

        def keys(F):
            F = F[:, :60]
            b = np.where(ge, F >= med, F > med)
            return (b.astype(np.int64) * w).sum(1)

        ktr = keys(Ftr)
        glob = np.bincount(ytr).argmax()
        order = np.lexsort((ytr, ktr))
        table = {}
        ks, ys = ktr[order], ytr[order]
        bounds = np.flatnonzero(np.diff(ks)) + 1
        for seg_k, seg_y in zip(np.split(ks, bounds), np.split(ys, bounds)):
            table[int(seg_k[0])] = int(np.bincount(seg_y).argmax())
        return [np.array([table.get(int(k), glob) for k in keys(F)]) for F in Fev]
    raise ValueError(kind)


def split_xy(F, Y, ruler, split):
    """Rows of feature matrix F and targets for `split` under `ruler`."""
    h = RULERS[ruler]
    lo, hi = SPLITS[split]
    hi = min(hi, len(Y) - h)
    return F[lo:hi], Y[lo + h:hi + h]
