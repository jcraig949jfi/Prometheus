"""Invariant miner: a restricted grammar of threshold laws scored on held-out lineages.

Language
  expressions  over declared coordinates, size <= MAX_SIZE nodes:
               terminals C N K G ; unary log, dec (= exp(-x)) ; binary + - * /
  atoms        expr <= t   or   expr >= t
  laws         one atom, or the conjunction of two atoms
Expressions whose rank order on the probe rows is identical collapse to one class
(Aphrodite's denotational quotient, lifted to threshold atoms: a threshold only
sees order). The smallest member names the class.

Scoring (never in-sample)
  leave-one-lineage-out (LOLO): thresholds are fitted on the other lineages and the
  held-out lineage is predicted. worst-fold and mean balanced accuracy.
  S = mean_BA - LAMBDA * complexity; a law must also clear WORST_GATE on every fold.
Post-selection correction
  the WHOLE search is rerun on labels permuted within each family (base rates kept);
  p = (1 + #null best S >= real best S) / (1 + n_perm).
Output NONE whenever the best law fails the gates or the null. "No law" is a result.
Family dependence
  mu = in-sample log-likelihood gain (bits/row) from refitting the law's thresholds per
  family, minus the median gain under permuted family labels; p from the same null.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

TERMINALS = ("C", "N", "K", "G")
MAX_SIZE = 6
LAMBDA = 0.004
WORST_GATE = 0.75
P1 = 60
P2 = 4
NPAIR = 60

Expr = Tuple


# ---------------------------------------------------------------- expressions
def size(e: Expr) -> int:
    return 1 if e[0] == "var" else 1 + sum(size(c) for c in e[1:])


def show(e: Expr) -> str:
    op = e[0]
    if op == "var":
        return e[1]
    if op == "log":
        return "log(%s)" % show(e[1])
    if op == "dec":
        return "exp(-%s)" % show(e[1])
    sym = {"add": "+", "sub": "-", "mul": "*", "div": "/"}[op]
    return "(%s %s %s)" % (show(e[1]), sym, show(e[2]))


def evaluate_expr(e: Expr, X: Dict[str, np.ndarray]) -> np.ndarray:
    op = e[0]
    with np.errstate(all="ignore"):
        if op == "var":
            return np.asarray(X[e[1]], float)
        if op == "log":
            v = evaluate_expr(e[1], X)
            return np.where(v > 0, np.log(np.where(v > 0, v, 1.0)), -np.inf)
        if op == "dec":
            return np.exp(-evaluate_expr(e[1], X))
        a, b = evaluate_expr(e[1], X), evaluate_expr(e[2], X)
        if op == "add":
            return a + b
        if op == "sub":
            return a - b
        if op == "mul":
            return a * b
        return a / b


def enumerate_exprs(terminals: Sequence[str] = TERMINALS, max_size: int = MAX_SIZE) -> List[Expr]:
    by_size: Dict[int, List[Expr]] = {1: [("var", t) for t in terminals]}
    for s in range(2, max_size + 1):
        out: List[Expr] = []
        for c in by_size.get(s - 1, []):
            if c[0] not in ("log", "dec"):
                out.append(("log", c))
                out.append(("dec", c))
        for ls in range(1, s - 1):
            rs = s - 1 - ls
            for a in by_size.get(ls, []):
                for b in by_size.get(rs, []):
                    for op in ("add", "sub", "mul", "div"):
                        if op in ("add", "mul") and show(a) > show(b):
                            continue
                        if show(a) == show(b) and op in ("sub", "div"):
                            continue
                        out.append((op, a, b))
        by_size[s] = out
    return [e for s in sorted(by_size) for e in by_size[s]]


# ---------------------------------------------------------------- threshold fitting
def _ba_weights(y: np.ndarray) -> Tuple[np.ndarray, bool]:
    npos, nneg = y.sum(), (1 - y).sum()
    if npos == 0 or nneg == 0:
        return np.zeros_like(y, float), False
    return np.where(y == 1, 0.5 / npos, 0.5 / nneg), True


def fit_thresholds(V: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """V (n, m) finite-or-inf values. Returns per column (best BA, threshold, direction +1 '<=' / -1 '>=')."""
    n, m = V.shape
    w, ok = _ba_weights(y)
    if not ok:
        return np.full(m, 0.5), np.zeros(m), np.ones(m)
    Vs = np.where(np.isnan(V), np.inf, V)
    order = np.argsort(Vs, axis=0, kind="stable")
    vs = np.take_along_axis(Vs, order, 0)
    ys = y[order]
    ws = w[order]
    pos_cum = np.cumsum(np.where(ys == 1, ws, 0.0), axis=0)        # weight of positives with v <= v_(i)
    neg_cum = np.cumsum(np.where(ys == 0, ws, 0.0), axis=0)
    neg_tot = neg_cum[-1]
    ba_le = pos_cum + (neg_tot - neg_cum)                           # predict P when v <= t_i
    ba_ge = 1.0 - ba_le                                             # complement rule
    # only split between distinct values
    distinct = np.vstack([vs[1:] != vs[:-1], np.ones((1, m), bool)])
    ba_le = np.where(distinct, ba_le, -1)
    ba_ge = np.where(distinct, ba_ge, -1)
    i_le, i_ge = ba_le.argmax(0), ba_ge.argmax(0)
    b_le, b_ge = ba_le[i_le, np.arange(m)], ba_ge[i_ge, np.arange(m)]
    use_le = b_le >= b_ge
    idx = np.where(use_le, i_le, i_ge)
    nxt = np.minimum(idx + 1, n - 1)
    lo, hi = vs[idx, np.arange(m)], vs[nxt, np.arange(m)]
    with np.errstate(all="ignore"):
        t = np.where(np.isfinite(hi) & np.isfinite(lo) & (nxt != idx), (lo + hi) / 2, lo)
    return np.where(use_le, b_le, b_ge), t, np.where(use_le, 1.0, -1.0)


def fit_thresholds_w(V: np.ndarray, y: np.ndarray, w: np.ndarray):
    """As fit_thresholds but with caller-supplied row weights (global balanced-accuracy weights)."""
    n, m = V.shape
    Vs = np.where(np.isnan(V), np.inf, V)
    order = np.argsort(Vs, axis=0, kind="stable")
    vs = np.take_along_axis(Vs, order, 0)
    ys, ws = y[order], w[order]
    pos_cum = np.cumsum(np.where(ys == 1, ws, 0.0), axis=0)
    neg_cum = np.cumsum(np.where(ys == 0, ws, 0.0), axis=0)
    pos_tot, neg_tot = pos_cum[-1], neg_cum[-1]
    ba_le = pos_cum + (neg_tot - neg_cum)
    ba_ge = (pos_tot - pos_cum) + neg_cum
    distinct = np.vstack([vs[1:] != vs[:-1], np.ones((1, m), bool)])
    ba_le = np.where(distinct, ba_le, -1)
    ba_ge = np.where(distinct, ba_ge, -1)
    i_le, i_ge = ba_le.argmax(0), ba_ge.argmax(0)
    b_le, b_ge = ba_le[i_le, np.arange(m)], ba_ge[i_ge, np.arange(m)]
    use_le = b_le >= b_ge
    idx = np.where(use_le, i_le, i_ge)
    nxt = np.minimum(idx + 1, n - 1)
    lo, hi = vs[idx, np.arange(m)], vs[nxt, np.arange(m)]
    with np.errstate(all="ignore"):
        t = np.where(np.isfinite(hi) & np.isfinite(lo) & (nxt != idx), (lo + hi) / 2, lo)
    return np.where(use_le, b_le, b_ge), t, np.where(use_le, 1.0, -1.0)


def fit_dir(v: np.ndarray, y: np.ndarray, w: np.ndarray, d: float):
    """Best threshold for one column with a FIXED direction; returns (t, weighted score)."""
    v = np.where(np.isnan(v), np.inf * d, v)
    order = np.argsort(v, kind="stable")
    vs, ys, ws = v[order], y[order], w[order]
    pos_cum = np.cumsum(np.where(ys == 1, ws, 0.0))
    neg_cum = np.cumsum(np.where(ys == 0, ws, 0.0))
    if d > 0:
        sc = pos_cum + (neg_cum[-1] - neg_cum)
    else:
        sc = (pos_cum[-1] - pos_cum) + neg_cum
    distinct = np.append(vs[1:] != vs[:-1], True)
    sc = np.where(distinct, sc, -1)
    i = int(sc.argmax())
    lo = vs[i]
    hi = vs[min(i + 1, len(vs) - 1)]
    if d < 0:
        # '>=' keeps rows strictly above index i
        t = (lo + hi) / 2 if np.isfinite(lo) and np.isfinite(hi) and hi != lo else hi
        # include the case "all rows admitted"
        if sc.max() < ((pos_cum[-1]) + 0.0):
            pass
    else:
        t = (lo + hi) / 2 if np.isfinite(lo) and np.isfinite(hi) and hi != lo else lo
    return float(t), float(sc[i])


def fit_pair(v1, d1, v2, d2, y, rounds: int = 3):
    """Coordinate ascent on the two thresholds of a conjunction (global balanced-accuracy weights)."""
    w, ok = _ba_weights(y)
    if not ok:
        return 0.0, 0.0
    t1, _ = fit_dir(v1, y, w, d1)
    t2 = np.inf if d2 > 0 else -np.inf
    for _ in range(rounds):
        m1 = atom_pred(v1, t1, d1)
        ww = np.where(m1, w, 0.0)
        # rows rejected by atom 1 are fixed negatives; fit atom 2 on admitted rows only
        t2, _ = fit_dir(np.where(m1, v2, np.nan), y, ww, d2)
        m2 = atom_pred(v2, t2, d2)
        ww = np.where(m2, w, 0.0)
        t1, _ = fit_dir(np.where(m2, v1, np.nan), y, ww, d1)
    return t1, t2


def atom_pred(v: np.ndarray, t: float, d: float) -> np.ndarray:
    v = np.where(np.isnan(v), np.inf * d, v)
    return (v <= t) if d > 0 else (v >= t)


def balanced_acc(pred: np.ndarray, y: np.ndarray) -> float:
    if y.sum() == 0 or (1 - y).sum() == 0:
        return float("nan")
    tpr = (pred & (y == 1)).sum() / (y == 1).sum()
    tnr = (~pred & (y == 0)).sum() / (y == 0).sum()
    return 0.5 * (tpr + tnr)


# ---------------------------------------------------------------- the search
@dataclass
class Law:
    atoms: List[Tuple[Expr, float, float]]            # (expr, threshold, direction)
    complexity: int
    fold_ba: Dict[str, float] = field(default_factory=dict)
    score: float = float("-inf")
    alpha: float = 0.0
    scales: List[float] = field(default_factory=list)

    def show(self) -> str:
        return " AND ".join("%s %s %.4g" % (show(e), "<=" if d > 0 else ">=", t) for e, t, d in self.atoms) or "NONE"

    def structure(self) -> List[Tuple[Expr, float]]:
        return [(e, d) for e, _, d in self.atoms]

    def predict(self, X: Dict[str, np.ndarray]) -> np.ndarray:
        n = len(next(iter(X.values())))
        out = np.ones(n, bool)
        for e, t, d in self.atoms:
            out &= atom_pred(evaluate_expr(e, X), t, d)
        return out

    def prob(self, X: Dict[str, np.ndarray]) -> np.ndarray:
        n = len(next(iter(X.values())))
        p = np.ones(n)
        for (e, t, d), s in zip(self.atoms, self.scales or [1.0] * len(self.atoms)):
            v = evaluate_expr(e, X)
            z = np.clip(self.alpha * d * (t - v) / s, -50, 50)
            z = np.where(np.isnan(z), 0.0, z)
            p *= 1 / (1 + np.exp(-z))
        return p

    def to_json(self) -> Dict[str, Any]:
        return {"law": self.show(), "atoms": [[_ser(e), float(t), float(d)] for e, t, d in self.atoms],
                "complexity": self.complexity, "fold_ba": self.fold_ba, "score": self.score,
                "alpha": self.alpha, "scales": self.scales}


def _ser(e: Expr):
    return [e[0], e[1]] if e[0] == "var" else [e[0]] + [_ser(c) for c in e[1:]]


def deser(e) -> Expr:
    return ("var", e[1]) if e[0] == "var" else tuple([e[0]] + [deser(c) for c in e[1:]])


def law_from_json(j: Dict[str, Any]) -> Law:
    L = Law(atoms=[(deser(e), t, d) for e, t, d in j["atoms"]], complexity=j["complexity"],
            fold_ba=j.get("fold_ba", {}), score=j.get("score", float("-inf")), alpha=j.get("alpha", 0.0),
            scales=j.get("scales", []))
    return L


class Miner:
    def __init__(self, X: Dict[str, np.ndarray], y: np.ndarray, groups: np.ndarray,
                 terminals: Sequence[str] = TERMINALS, max_size: int = MAX_SIZE, conj: bool = True):
        self.X = {k: np.asarray(v, float) for k, v in X.items()}
        self.y = np.asarray(y, int)
        self.groups = np.asarray(groups)
        self.conj = conj
        self._terminals, self._max_size = tuple(terminals), max_size
        exprs = enumerate_exprs(terminals, max_size)
        vals, keep, seen = [], [], set()
        for e in exprs:
            v = evaluate_expr(e, self.X)
            if np.isnan(v).any() or np.isposinf(v).all() or np.isneginf(v).all():
                continue
            v = np.where(np.isposinf(v), 1e300, np.where(np.isneginf(v), -1e300, v))
            key = np.argsort(np.argsort(v, kind="stable"), kind="stable")
            # order-class: ranks with ties; include tie pattern
            r = np.unique(v, return_inverse=True)[1]
            sig = r.tobytes()
            sig_neg = (r.max() - r).tobytes()
            if sig in seen or sig_neg in seen or r.max() == 0:
                continue
            seen.add(sig)
            vals.append(v)
            keep.append(e)
        self.exprs = keep
        self.V = np.stack(vals, axis=1) if vals else np.zeros((len(self.y), 0))
        self.sizes = np.array([size(e) for e in keep])
        Vc = np.where(np.isnan(self.V), np.inf, self.V)
        self._order = np.argsort(Vc, axis=0, kind="stable")
        self._vs = np.take_along_axis(Vc, self._order, 0)
        self._distinct = np.vstack([self._vs[1:] != self._vs[:-1], np.ones((1, self.V.shape[1]), bool)])

    def _fit_sorted(self, y: np.ndarray, w: np.ndarray):
        """fit_thresholds_w over ALL expression classes using the presorted order; rows with
        w == 0 are excluded (no slicing, no re-sort)."""
        n, m = self.V.shape
        w32 = w.astype(np.float32)
        ys, ws = y[self._order], w32[self._order]
        z = np.float32(0.0)
        pos_cum = np.cumsum(np.where(ys == 1, ws, z), axis=0, dtype=np.float32)
        neg_cum = np.cumsum(np.where(ys == 0, ws, z), axis=0, dtype=np.float32)
        pos_tot, neg_tot = pos_cum[-1], neg_cum[-1]
        ba_le = pos_cum + (neg_tot - neg_cum)
        ba_ge = (pos_tot - pos_cum) + neg_cum
        ba_le = np.where(self._distinct, ba_le, -1)
        ba_ge = np.where(self._distinct, ba_ge, -1)
        i_le, i_ge = ba_le.argmax(0), ba_ge.argmax(0)
        ar = np.arange(m)
        b_le, b_ge = ba_le[i_le, ar], ba_ge[i_ge, ar]
        use_le = b_le >= b_ge
        idx = np.where(use_le, i_le, i_ge)
        nxt = np.minimum(idx + 1, n - 1)
        lo, hi = self._vs[idx, ar], self._vs[nxt, ar]
        with np.errstate(all="ignore"):
            t = np.where(np.isfinite(hi) & np.isfinite(lo) & (nxt != idx), (lo + hi) / 2, lo)
        return np.where(use_le, b_le, b_ge), t, np.where(use_le, 1.0, -1.0)

    # ---------- one search on labels y
    def search(self, y: np.ndarray) -> Tuple[Optional[Law], List[Law]]:
        folds = sorted(set(self.groups.tolist()))
        if len(folds) < 2:
            return None, []
        # single atoms: LOLO
        fold_ba = np.zeros((len(folds), self.V.shape[1]))
        fold_fit = []
        for i, g in enumerate(folds):
            tr, te = self.groups != g, self.groups == g
            yt_ = y[tr]
            npos, nneg = yt_.sum(), (1 - yt_).sum()
            if npos == 0 or nneg == 0:
                t, d = np.zeros(self.V.shape[1]), np.ones(self.V.shape[1])
            else:
                wtr = np.where(tr, np.where(y == 1, 0.5 / npos, 0.5 / nneg), 0.0)
                _, t, d = self._fit_sorted(y, wtr)
            pred = np.where(d > 0, self.V[te] <= t, self.V[te] >= t)
            yt = y[te]
            if yt.sum() == 0 or (1 - yt).sum() == 0:
                ba = (pred == yt[:, None]).mean(0)          # one-class fold: plain accuracy
            else:
                tpr = (pred & (yt[:, None] == 1)).sum(0) / (yt == 1).sum()
                tnr = (~pred & (yt[:, None] == 0)).sum(0) / (yt == 0).sum()
                ba = 0.5 * (tpr + tnr)
            fold_ba[i] = ba
            fold_fit.append((t, d))
        mean_ba = fold_ba.mean(0)
        S = mean_ba - LAMBDA * self.sizes
        cands: List[Law] = []
        ok = fold_ba.min(0) >= WORST_GATE
        wall, okall = _ba_weights(y)
        d_full = self._fit_sorted(y, wall)[2] if okall else np.ones(self.V.shape[1])
        for j in np.argsort(-S)[:5]:
            L = Law(atoms=[(self.exprs[j], 0.0, float(d_full[j]))], complexity=int(self.sizes[j]),
                    fold_ba={str(g): float(fold_ba[i, j]) for i, g in enumerate(folds)}, score=float(S[j]))
            L._ok = bool(ok[j])
            cands.append(L)
        if self.conj:
            cands += self._conj(y, folds)
        cands.sort(key=lambda L: -L.score)
        best = next((L for L in cands if getattr(L, "_ok", False)), None)
        return best, cands

    def _conj(self, y: np.ndarray, folds) -> List[Law]:
        """Greedy conditional search: for each strong first atom, the best second atom over ALL
        expression classes on the rows the first atom admits; then LOLO with per-fold refits."""
        w, ok = _ba_weights(y)
        if not ok:
            return []
        ba_all, t_all, d_all = self._fit_sorted(y, w)
        firsts = []
        for j in np.argsort(-ba_all)[:P1]:
            firsts.append((int(j), float(d_all[j])))
            firsts.append((int(j), -float(d_all[j])))      # bands need the opposite side too
        pairs = {}
        for j1, d1 in firsts:
            t1, _ = fit_dir(self.V[:, j1], y, w, d1)
            m = atom_pred(self.V[:, j1], t1, d1)
            if m.sum() < 3:
                continue
            ba2, t2, d2 = self._fit_sorted(y, np.where(m, w, 0.0))
            # objective of the conjunction = admitted rows scored by atom 2 + rejected rows (predicted 0)
            const = float((w * (y == 0) * ~m).sum())
            tot = ba2 + const
            for j2 in np.argsort(-tot)[:P2]:
                if int(j2) == j1:
                    continue
                key = tuple(sorted([(j1, d1), (int(j2), float(d2[j2]))]))
                pairs[key] = max(pairs.get(key, -1.0), float(tot[j2]))
        out = []
        ranked = sorted(pairs, key=lambda k: -pairs[k])[:NPAIR]
        for (j1, d1), (j2, d2) in ranked:
            fba = {}
            for g in folds:
                tr, te = self.groups != g, self.groups == g
                t1, t2 = fit_pair(self.V[tr, j1], d1, self.V[tr, j2], d2, y[tr])
                pte = atom_pred(self.V[te, j1], t1, d1) & atom_pred(self.V[te, j2], t2, d2)
                yt = y[te]
                fb = balanced_acc(pte, yt)
                fba[str(g)] = float((pte == yt).mean()) if math.isnan(fb) else float(fb)
            cx = int(self.sizes[j1] + self.sizes[j2] + 1)
            sc = float(np.mean(list(fba.values()))) - LAMBDA * cx
            L = Law(atoms=[(self.exprs[j1], 0.0, d1), (self.exprs[j2], 0.0, d2)], complexity=cx, fold_ba=fba, score=sc)
            L._ok = min(fba.values()) >= WORST_GATE
            out.append(L)
        out.sort(key=lambda L: -L.score)
        return out[:10]

    # ---------- final fit on all rows (for a chosen structure)
    def refit(self, structure: List[Tuple[Expr, float]], X: Dict[str, np.ndarray], y: np.ndarray) -> Law:
        y = np.asarray(y, int)
        if any(d == 0 for _, d in structure):
            raise ValueError("law atom without a direction")
        vals = [evaluate_expr(e, X) for e, _ in structure]
        if len(structure) == 1:
            _, t, _ = fit_thresholds(vals[0][:, None], y)
            thr = [float(t[0])]
        else:
            qs = np.linspace(0.01, 0.99, 60)
            T = [np.quantile(v[np.isfinite(v)], qs) for v in vals]
            (e1, d1), (e2, d2) = structure
            A1 = (vals[0][:, None] <= T[0][None]) if d1 > 0 else (vals[0][:, None] >= T[0][None])
            A2 = (vals[1][:, None] <= T[1][None]) if d2 > 0 else (vals[1][:, None] >= T[1][None])
            P = A1[:, :, None] & A2[:, None, :]
            w, _ = _ba_weights(y)
            ba = np.einsum("n,nij->ij", w * (y == 1), P) + np.einsum("n,nij->ij", w * (y == 0), ~P)
            a, b = np.unravel_index(ba.argmax(), ba.shape)
            thr = [float(T[0][a]), float(T[1][b])]
        L = Law(atoms=[(e, t, d) for (e, d), t in zip(structure, thr)], complexity=sum(size(e) for e, _ in structure) + len(structure) - 1)
        L.scales = [float(np.nanstd(np.clip(v[np.isfinite(v)], *np.percentile(v[np.isfinite(v)], [2, 98]))) or 1.0) for v in vals]
        # width: shared logistic slope by maximum likelihood on a grid
        best = (-np.inf, 1.0)
        for a in np.geomspace(0.5, 500, 60):
            L.alpha = a
            p = np.clip(L.prob(X), 1e-6, 1 - 1e-6)
            ll = float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
            if ll > best[0]:
                best = (ll, a)
        L.alpha = best[1]
        return L

    # ---------- the full procedure with its null
    def mine(self, n_perm: int = 19, seed: int = 0, p_gate: float = 0.05, workers: int = 0) -> Dict[str, Any]:
        best, cands = self.search(self.y)
        rng = np.random.default_rng(seed)
        perms = []
        for _ in range(n_perm):
            yp = self.y.copy()
            for g in np.unique(self.groups):
                m = self.groups == g
                yp[m] = rng.permutation(yp[m])
            perms.append(yp)
        null_scores = self._null_scores(perms, workers)
        real = best.score if best else max([c.score for c in cands], default=-np.inf)
        p = (1 + sum(s >= real for s in null_scores)) / (1 + n_perm)
        top = [{"structure": " AND ".join(
            "%s %s" % (show(e), "<=" if d > 0 else ">=") for e, _, d in c.atoms), "score": round(c.score, 4),
                "fold_ba": {k: round(v, 4) for k, v in c.fold_ba.items()}, "passes_worst_gate": getattr(c, "_ok", False)}
               for c in cands[:8]]
        res = {"n_rows": int(len(self.y)), "n_expr_classes": len(self.exprs), "groups": sorted(map(str, set(self.groups.tolist()))),
               "best_score": real, "null_scores": [round(s, 4) for s in null_scores], "p_null": p, "top": top}
        if best is None or p > p_gate:
            res["verdict"] = "NONE"
            res["reason"] = "no candidate clears the worst-fold gate" if best is None else "best score not above the permutation null (p=%.3f)" % p
            res["law"] = None
            return res
        L = self.refit([(e, d) for e, _, d in best.atoms], self.X, self.y)
        L.fold_ba, L.score = best.fold_ba, best.score
        res["verdict"] = "CANDIDATE"
        res["law"] = L.to_json()
        res["family_dependence"] = self.family_dependence(L, seed=seed)
        return res

    def _null_scores(self, perms, workers: int) -> List[float]:
        if workers is None or workers <= 1 or len(perms) < 2:
            return [max([c.score for c in self.search(yp)[1]], default=-np.inf) for yp in perms]
        from concurrent.futures import ProcessPoolExecutor
        from concurrent.futures.process import BrokenProcessPool
        init = (self.X, self.y, self.groups, self._terminals, self._max_size, self.conj)
        w = min(workers, len(perms), memory_workers(self.V.shape))
        while w > 1:
            try:
                with ProcessPoolExecutor(max_workers=w, initializer=_null_init, initargs=init) as ex:
                    return list(ex.map(_null_one, perms))
            except Exception as e:     # BrokenProcessPool, OSError (pipe), MemoryError in a worker: retry smaller
                NULL_POOL_FAILURES.append({"workers": w, "error": repr(e)[:200]})
                w //= 2
        return [max([c.score for c in self.search(yp)[1]], default=-np.inf) for yp in perms]

    def family_dependence(self, L: Law, n_perm: int = 49, seed: int = 0) -> Dict[str, Any]:
        """Bits/row gained by refitting the law's thresholds per family, against permuted family labels."""
        structure = L.structure()

        def gain(groups):
            p = np.clip(L.prob(self.X), 1e-6, 1 - 1e-6)
            ll0 = self.y * np.log2(p) + (1 - self.y) * np.log2(1 - p)
            ll1 = np.zeros_like(ll0)
            for g in np.unique(groups):
                m = groups == g
                Xg = {k: v[m] for k, v in self.X.items()}
                yg = self.y[m]
                if yg.min() == yg.max():
                    ll1[m] = 0.0      # a family-specific model can fit a one-class family perfectly
                    continue
                Lg = self.refit(structure, Xg, yg)
                pg = np.clip(Lg.prob(Xg), 1e-6, 1 - 1e-6)
                ll1[m] = yg * np.log2(pg) + (1 - yg) * np.log2(1 - pg)
            return float((ll1 - ll0).mean())

        real = gain(self.groups)
        rng = np.random.default_rng(seed + 1)
        null = [gain(rng.permutation(self.groups)) for _ in range(n_perm)]
        per_fam = {}
        pred = L.predict(self.X)
        for g in np.unique(self.groups):
            m = self.groups == g
            per_fam[str(g)] = round(float((pred[m] == (self.y[m] == 1)).mean()), 4)
        return {"gain_bits_per_row": round(real, 5), "null_median": round(float(np.median(null)), 5),
                "mu_bits": round(real - float(np.median(null)), 5),
                "p": (1 + sum(n >= real for n in null)) / (1 + n_perm), "per_family_acc": per_fam}


_WORKER_MINER = None
NULL_POOL_FAILURES: List[Dict[str, Any]] = []     # engineering record: pool crashes and the fallback taken


def _null_init(X, y, groups, terminals, max_size, conj):
    global _WORKER_MINER
    _WORKER_MINER = Miner(X, y, groups, terminals=terminals, max_size=max_size, conj=conj)


def _null_one(yp) -> float:
    return max([c.score for c in _WORKER_MINER.search(yp)[1]], default=-np.inf)


def free_memory_bytes() -> int:
    """Available physical memory (Windows GlobalMemoryStatusEx; elsewhere os.sysconf); 0 if unknown."""
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
        st = MS()
        st.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return int(st.ullAvailPhys)
    except Exception:
        pass
    try:
        import os
        return int(os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE"))
    except Exception:
        return 0


def memory_workers(shape) -> int:
    """Workers that fit in half the free memory: ~16 bytes x 12 n-by-m arrays per worker (presorted
    matrices + scan temporaries). At least 1."""
    n, m = shape
    per = max(1, n * m * 16 * 12)
    free = free_memory_bytes()
    return max(1, int(0.5 * free // per)) if free else 4


def default_workers() -> int:
    import os
    return max(1, min(10, (os.cpu_count() or 2) // 3))
