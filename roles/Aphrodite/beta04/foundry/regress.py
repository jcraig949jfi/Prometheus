"""E1 v2 REGRESSION rung (E1_V2_RULES rule 1): five cheap, non-composing policy classes, fitted on DEV and selected
on DEV (no hindsight on test).

    E  per-class elementwise fit        (List out, len(y) == len(x)):  y_i = A_k(x_i) . [1, phi(x_i)]
    F  keep-rule + map                   (List out, y a subsequence):    keep r(x_i), then E on the kept elements
    S  scan transducer                   (List out, len(y) == len(x)+1): y_0 const; y_{i+1} = A_k(x_i) . [1, feats(x_i, y_i)]
    P  single statistic                  (Int out): polynomial in s(xs), or per-class affine in phi(s(xs))
    W  one-register linear recurrence    (Int out): acc' = c*acc + u_k(x_i); y = h*c^n + sum_i c^(n-1-i) u_k(x_i) + d

FEATURES ARE DERIVED ONLY FROM THE PUBLIC GENERATOR CONFIG (derive_banks). The derivation was frozen in code and
committed BEFORE the v2 pilot:
    PHI   unary Int terms over x of esize <= 3, built from CONFIG["mech_pcfg"]["ops"] (minus `if`) and
          CONFIG["mech_pcfg"]["literals"]; kept in enumeration order if they never FAIL on the probe range [-2V, 2V]
          (V = largest |value| in any CONFIG input distribution), are non-constant, stay within |v| <= 1e12, and
          are not an affine image of x or of an earlier kept feature.
    BOOL  unary Bool terms over x: CONFIG["mech_pcfg"]["cmp_ops"] applied to two terms of esize <= 2 (x, literals, neg x,
          neg literal), deduplicated as 2-class partitions of the probe range (a partition and its complement are
          the same key).
    RES   PHI features with 2..6 distinct values on the probe range (residue-type partitions).
    KEYS  none + BOOL + RES + BOOL x RES + BOOL x BOOL, deduplicated by the partition of the probe range they induce,
          products kept only if they have <= 6 classes.
    STATS CONFIG["readouts_int"] (list statistics), used by P.
    C     recurrence constants {+k, -k : k in CONFIG["mech_pcfg"]["literals"], k != 0}, used by W.

Selection: inside each class, the dev-consistent model with the FEWEST parameters wins (ties: fixed enumeration
order). A model must have strictly fewer parameters than dev constraints. The rung SOLVES a family iff the
selected model of at least one class is correct on ALL test examples. Fits use a float pre-screen (numpy pinv,
column-normalised), and every accepted fit is re-solved EXACTLY over the rationals (nulls.solve_linear). A test
prediction must be an exact integer.
"""
import hashlib
import json
from fractions import Fraction
from typing import Dict, List, Optional

import numpy as np

import fastc
import interp_a as A
from nulls import solve_linear

VERSION = "b04-regress-v2.0"
MAX_CLASSES = 6
MAX_PHI_PER_CLASS = 2
MAX_S_FEATS = 3
POLY_MAX_DEG = 9
VAL_LIMIT = 10 ** 12

# ---------------------------------------------------------------- bank derivation (from CONFIG only)
_BANKS = {}


def _cfg_key(cfg):
    sub = {k: cfg[k] for k in ("mech_pcfg", "readouts_int", "dist_base", "dist_shift")}
    return hashlib.sha256(json.dumps(sub, sort_keys=True).encode()).hexdigest()


def _ev(fn, v):
    try:
        out = fn({"x": v})
    except (A.Fail, ZeroDivisionError, OverflowError):
        return None
    if type(out) is int and abs(out) > A.CEIL:
        return None
    return out


def _small_terms(cfg):
    """Unary Int terms over x by esize: 1, 2, 3 (CONFIG ops + literals)."""
    lits = [("lit", k) for k in cfg["mech_pcfg"]["literals"]]
    ops = sorted(cfg["mech_pcfg"]["ops"])
    s1 = [("var", "x")] + lits
    s2 = []
    if "neg" in ops:
        s2 = [("prim", "neg", (t,)) for t in s1]
    s3 = []
    if "neg" in ops:
        s3 += [("prim", "neg", (t,)) for t in s2]
    for op in ops:
        if op in ("neg", "if"):
            continue
        for a in s1:
            for b in s1:
                s3.append(("prim", op, (a, b)))
    return s1, s2, s3


def _affine_of(sig, base):
    """Is sig = alpha*base + beta exactly for rationals alpha, beta?"""
    rows = [((b, 1), s) for b, s in zip(base, sig)]
    return solve_linear(rows) is not None


def derive_banks(cfg):
    key = _cfg_key(cfg)
    if key in _BANKS:
        return _BANKS[key]
    V = max(abs(v) for d in (cfg["dist_base"], cfg["dist_shift"]) for v in d["val"])
    probe = list(range(-2 * V, 2 * V + 1))
    s1, s2, s3 = _small_terms(cfg)
    phi, sigs = [], []
    for t in s1 + s2 + s3:                       # x comes first, so it is always kept
        if t[0] == "lit":
            continue
        fn = fastc.compile_term(t)
        sig = [_ev(fn, v) for v in probe]
        if any(s is None or type(s) is not int or abs(s) > VAL_LIMIT for s in sig):
            continue
        if len(set(sig)) == 1:
            continue
        if any(_affine_of(sig, b) for b in sigs):
            continue
        phi.append((A.show(t), fn))
        sigs.append(sig)
    # Bool keys
    small = s1 + s2
    parts, boolk = set(), []
    for op in cfg["mech_pcfg"]["cmp_ops"]:
        for a in small:
            for b in small:
                if a == b:
                    continue
                t = ("prim", op, (a, b))
                if not (A.free_vars(t) & {"x"}):
                    continue
                fn = fastc.compile_term(t)
                sig = tuple(_ev(fn, v) for v in probe)
                if any(s is None for s in sig) or len(set(sig)) == 1:
                    continue
                p = frozenset([sig, tuple(not s for s in sig)])
                if p in parts:
                    continue
                parts.add(p)
                boolk.append((A.show(t), fn))
    resk = [(n, fn) for (n, fn), sig in zip(phi, sigs) if 2 <= len(set(sig)) <= MAX_CLASSES]
    # keys: list of (name, function x -> hashable class)
    singles = [("bool:" + n, (lambda fn: lambda v: _ev(fn, v))(fn)) for n, fn in boolk] + \
              [("res:" + n, (lambda fn: lambda v: _ev(fn, v))(fn)) for n, fn in resk]
    keys, seen = [("none", lambda v: 0)], {tuple([0] * len(probe))}

    def addkey(name, f):
        sig = tuple(f(v) for v in probe)
        if any(s is None for s in sig):
            return
        canon, m = [], {}
        for s in sig:
            m.setdefault(s, len(m))
            canon.append(m[s])
        canon = tuple(canon)
        if len(m) > MAX_CLASSES or canon in seen:
            return
        seen.add(canon)
        keys.append((name, f))

    for n, f in singles:
        addkey(n, f)
    bools = singles[:len(boolk)]
    ress = singles[len(boolk):]
    for nb, fb in bools:
        for nr, fr in ress:
            addkey(nb + "*" + nr, (lambda fb, fr: lambda v: (fb(v), fr(v)))(fb, fr))
    for i, (n1, f1) in enumerate(bools):
        for n2, f2 in bools[i + 1:]:
            addkey(n1 + "*" + n2, (lambda f1, f2: lambda v: (f1(v), f2(v)))(f1, f2))
    single_keys = [k for k in keys if "*" not in k[0]]
    lits = [k for k in cfg["mech_pcfg"]["literals"] if k != 0]
    consts = sorted(set(lits + [-k for k in lits]))
    stats = list(cfg["readouts_int"])
    banks = {"phi": phi, "keys": keys, "single_keys": single_keys, "consts": consts, "stats": stats,
             "probe": [probe[0], probe[-1]]}
    _BANKS[key] = banks
    return banks


def bank_summary(cfg):
    b = derive_banks(cfg)
    return {"version": VERSION, "phi": [n for n, _f in b["phi"]], "n_keys": len(b["keys"]),
            "single_keys": [n for n, _f in b["single_keys"]], "consts": b["consts"], "stats": b["stats"],
            "probe": b["probe"],
            "sha256": hashlib.sha256(json.dumps([[n for n, _f in b["phi"]], [n for n, _f in b["keys"]],
                                                 b["consts"], b["stats"]]).encode()).hexdigest()}


# ---------------------------------------------------------------- fitting primitives
def _float_fit(Xs, y):
    """Xs: (m, n, k) candidate design matrices; y: (n,). Returns boolean mask of float-consistent candidates."""
    if Xs.shape[0] == 0:
        return np.zeros(0, dtype=bool)
    scale = np.max(np.abs(Xs), axis=1, keepdims=True)
    scale[scale == 0] = 1.0
    Xn = Xs / scale
    pinv = np.linalg.pinv(Xn)
    coef = pinv @ y
    res = np.einsum("mnk,mk->mn", Xn, coef) - y[None, :]
    tol = 1e-6 * max(1.0, float(np.max(np.abs(y))))
    return np.all(np.abs(res) <= tol, axis=1)


def _exact(rows):
    return solve_linear(rows)


def _pred(coef, feats):
    if coef is None or feats is None or any(f is None for f in feats):
        return None
    v = sum(Fraction(c) * f for c, f in zip(coef, feats))
    return int(v) if v.denominator == 1 else None


class PhiCache:
    def __init__(self, phi):
        self.phi = phi
        self.c = {}

    def vec(self, v):
        r = self.c.get(v)
        if r is None:
            r = tuple(_ev(fn, v) for _n, fn in self.phi)
            self.c[v] = r
        return r


def _subsets(n, kmax):
    out = [()]
    for i in range(n):
        out.append((i,))
    if kmax >= 2:
        for i in range(n):
            for j in range(i + 1, n):
                out.append((i, j))
    return out


def _class_minfit(xs_vals, ys, pc: PhiCache):
    """Per-class minimal affine fit y = c0 + sum c_j phi_j(x) over <= 2 phi features.
    Returns (subset, coef) or None. Candidates in order: constant, singles, pairs."""
    n = len(ys)
    if n == 0:
        return None
    if all(y == ys[0] for y in ys):
        return ((), [Fraction(ys[0])])
    F = [pc.vec(v) for v in xs_vals]
    nphi = len(pc.phi)
    ok_cols = [j for j in range(nphi) if all(f[j] is not None for f in F)]
    if not ok_cols:
        return None
    Ff = np.array([[1.0] + [float(f[j]) for j in ok_cols] for f in F])     # (n, 1+k)
    yv = np.array([float(y) for y in ys])
    k = len(ok_cols)
    for size in (1, 2):
        if size + 1 > n:
            continue
        idx = [(i,) for i in range(k)] if size == 1 else [(i, j) for i in range(k) for j in range(i + 1, k)]
        if not idx:
            continue
        cols = np.array([[0] + [1 + i for i in t] for t in idx])
        Xs = np.transpose(Ff[:, cols], (1, 0, 2))                             # (m, n, size+1)
        mask = _float_fit(Xs, yv)
        for t, ok in zip(idx, mask):
            if not ok:
                continue
            sub = tuple(ok_cols[i] for i in t)
            coef = _exact([(tuple([1] + [F[r][j] for j in sub]), ys[r]) for r in range(n)])
            if coef is not None:
                return (sub, coef)
    return None


def _keyed_fit(xs_vals, ys, keyf, pc):
    """Per-class minimal fits under key keyf. Returns (params, model) or None."""
    groups = {}
    for v, y in zip(xs_vals, ys):
        k = keyf(v)
        if k is None:
            return None
        groups.setdefault(k, ([], []))
        groups[k][0].append(v)
        groups[k][1].append(y)
    model, params = {}, 0
    for k in sorted(groups, key=repr):
        fit = _class_minfit(groups[k][0], groups[k][1], pc)
        if fit is None:
            return None
        model[k] = fit
        params += len(fit[0]) + 1
    return params, model


def _keyed_pred(model, keyf, v, pc):
    k = keyf(v)
    if k not in model:
        return None
    s, coef = model[k]
    f = pc.vec(v)
    return _pred(coef, [1] + [f[j] for j in s])


def _data_keys(xs_vals, keys):
    """Keys deduplicated by the partition they induce on these data values, ordered by class count (stable).
    Returns [(n_classes, name, keyf)]. Keys that return None on some value are dropped."""
    seen, out = set(), []
    for name, kf in keys:
        lab = [kf(v) for v in xs_vals]
        if any(l is None for l in lab):
            continue
        m, canon = {}, []
        for l in lab:
            m.setdefault(l, len(m))
            canon.append(m[l])
        canon = tuple(canon)
        if canon in seen:
            continue
        seen.add(canon)
        out.append((len(m), name, kf))
    out.sort(key=lambda t: t[0])
    return out


def _best_keyed(xs_vals, ys, keys, pc, nrows):
    """Fewest-parameter keyed model. Every class costs >= 1 parameter, so the scan stops once the class count of
    the next key reaches the best parameter count (the selection is unchanged by this pruning)."""
    best = None
    for ncl, name, kf in _data_keys(xs_vals, keys):
        if ncl >= nrows or (best is not None and ncl >= best[0]):
            break
        r = _keyed_fit(xs_vals, ys, kf, pc)
        if r is None:
            continue
        params, model = r
        if params >= nrows:
            continue
        if best is None or params < best[0]:
            best = (params, name, kf, model)
    return best


# ---------------------------------------------------------------- the five classes
def fit_E(dev, B, pc):
    if not all(type(y) is list and len(y) == len(x) for x, y in dev):
        return None
    xv = [v for x, _y in dev for v in x]
    yv = [w for _x, y in dev for w in y]
    best = _best_keyed(xv, yv, B["keys"], pc, len(yv))
    if best is None:
        return None
    params, name, kf, model = best

    def pred(xs):
        out = [_keyed_pred(model, kf, v, pc) for v in xs]
        return None if any(o is None for o in out) else out
    return {"params": params, "desc": "E key=%s" % name, "pred": pred}


def _keep_preds(B):
    preds = []
    for name, kf in B["single_keys"]:
        if name == "none":
            continue
        vals = sorted({kf(v) for v in range(B["probe"][0], B["probe"][1] + 1)}, key=repr)
        for c in vals:
            preds.append(("%s==%r" % (name, c), (lambda kf, c: lambda v: kf(v) == c)(kf, c), name))
            if len(vals) > 2:
                preds.append(("%s!=%r" % (name, c), (lambda kf, c: lambda v: kf(v) != c)(kf, c), name))
    return preds


def fit_F(dev, B, pc):
    if not all(type(y) is list for _x, y in dev):
        return None
    preds = _keep_preds(B)
    cands = [(n, p, 1) for n, p, _k in preds]
    for i, (n1, p1, k1) in enumerate(preds):
        for n2, p2, k2 in preds[i + 1:]:
            if k1 != k2:
                cands.append(("%s&%s" % (n1, n2), (lambda p1, p2: lambda v: p1(v) and p2(v))(p1, p2), 2))
    best = None
    nrows = sum(len(x) for x, _y in dev)
    for n, p, pp in cands:
        kept = []
        ok = True
        for x, y in dev:
            kx = [v for v in x if p(v)]
            if len(kx) != len(y):
                ok = False
                break
            kept.append((kx, y))
        if not ok:
            continue
        xv = [v for kx, _y in kept for v in kx]
        yv = [w for _kx, y in kept for w in y]
        if not yv:
            r = (0, "empty", lambda v: 0, {})
        else:
            r = _best_keyed(xv, yv, B["keys"], pc, nrows)
            if r is None:
                continue
        params = r[0] + pp
        if params >= nrows:
            continue
        if best is None or params < best[0]:
            best = (params, n, p, r)
    if best is None:
        return None
    params, n, p, (_pp, kname, kf, model) = best

    def pred(xs):
        out = [_keyed_pred(model, kf, v, pc) for v in xs if p(v)]
        return None if any(o is None for o in out) else out
    return {"params": params, "desc": "F keep=%s key=%s" % (n, kname), "pred": pred}


def fit_S(dev, B, pc):
    if not all(type(y) is list and len(y) == len(x) + 1 for x, y in dev):
        return None
    y0s = {y[0] for _x, y in dev}
    if len(y0s) != 1:
        return None
    y0 = y0s.pop()
    trans = [(x[i], y[i], y[i + 1]) for x, y in dev for i in range(len(x))]
    nphi = len(pc.phi)

    def feats(v, yy):
        f = pc.vec(v)
        xf = list(f)
        yf = [yy] + [None if fj is None else yy * fj for fj in f]
        return xf + yf                      # indices: 0..nphi-1 x-feats, nphi = y, nphi+1.. = y*phi

    nf = 2 * nphi + 1
    ycols = set(range(nphi, nf))
    subsets = []
    for size in (1, 2, 3):
        if size == 1:
            subsets += [(i,) for i in range(nf)]
        elif size == 2:
            subsets += [(i, j) for i in range(nf) for j in range(i + 1, nf)]
        else:
            subsets += [(i, j, k) for i in range(nf) for j in range(i + 1, nf) for k in range(j + 1, nf)]
    subsets = [s for s in subsets if set(s) & ycols]

    def class_fit(rows):
        F = [feats(v, yy) for v, yy, _t in rows]
        ts = [t for _v, _yy, t in rows]
        n = len(rows)
        okc = [j for j in range(nf) if all(F[r][j] is not None for r in range(n))]
        Ff = np.array([[1.0] + [float(F[r][j]) for j in okc] for r in range(n)])
        pos = {j: q + 1 for q, j in enumerate(okc)}
        yv = np.array([float(t) for t in ts])
        for size in (1, 2, 3):
            cands = [sb for sb in subsets if len(sb) == size and all(j in pos for j in sb)]
            if not cands or size + 1 > n:
                continue
            cols = np.array([[0] + [pos[j] for j in sb] for sb in cands])
            Xs = np.transpose(Ff[:, cols], (1, 0, 2))
            mask = _float_fit(Xs, yv)
            for sb, ok in zip(cands, mask):
                if not ok:
                    continue
                coef = _exact([(tuple([1] + [F[r][j] for j in sb]), ts[r]) for r in range(n)])
                if coef is not None:
                    return (sb, coef)
        return None

    best = None
    nrows = len(trans)
    for ncl, name, kf in _data_keys([v for v, _yy, _t in trans], B["single_keys"]):
        if 1 + 2 * ncl >= nrows or (best is not None and 1 + 2 * ncl >= best[0]):
            break
        groups = {}
        for v, yy, t in trans:
            groups.setdefault(kf(v), []).append((v, yy, t))
        model, params = {}, 1
        for k in sorted(groups, key=repr):
            fit = class_fit(groups[k])
            if fit is None:
                model = None
                break
            model[k] = fit
            params += len(fit[0]) + 1
        if model is None or params >= nrows:
            continue
        if best is None or params < best[0]:
            best = (params, name, kf, model)
    if best is None:
        return None
    params, name, kf, model = best

    def pred(xs):
        out = [y0]
        yy = y0
        for v in xs:
            k = kf(v)
            if k not in model:
                return None
            s, coef = model[k]
            f = feats(v, yy)
            yy = _pred(coef, [1] + [f[j] for j in s])
            if yy is None or abs(yy) > A.CEIL:
                return None
            out.append(yy)
        return out
    return {"params": params, "desc": "S key=%s" % name, "pred": pred}


def _stat(name, xs):
    if name == "len":
        return len(xs)
    if name == "sum":
        return sum(xs)
    if not xs:
        return None
    return {"head": xs[0], "last": xs[-1], "max": max(xs), "min": min(xs)}[name]


def fit_P(dev, B, pc):
    if not all(type(y) is int for _x, y in dev):
        return None
    ys = [y for _x, y in dev]
    n = len(ys)
    best = None
    for st in B["stats"]:
        ss = [_stat(st, x) for x, _y in dev]
        if any(s is None for s in ss):
            continue
        for d in range(0, min(POLY_MAX_DEG, n - 2) + 1):
            if d + 1 >= n:
                break
            if best is not None and d + 1 >= best[0]:
                break
            coef = _exact([(tuple(s ** k for k in range(d + 1)), y) for s, y in zip(ss, ys)])
            if coef is not None:
                best = (d + 1, "P poly deg %d of %s" % (d, st),
                        (lambda st, coef, d: lambda xs: (lambda s: None if s is None else
                                                         _pred(coef, [s ** k for k in range(d + 1)]))(
                            _stat(st, xs)))(st, coef, d))
                break
        r = _best_keyed(ss, ys, B["keys"], pc, n)
        if r is not None and (best is None or r[0] < best[0]):
            params, kname, kf, model = r
            best = (params, "P keyed %s of %s" % (kname, st),
                    (lambda st, kf, model: lambda xs: (lambda s: None if s is None else
                                                       _keyed_pred(model, kf, s, pc))(_stat(st, xs)))(
                        st, kf, model))
    if best is None:
        return None
    return {"params": best[0], "desc": best[1], "pred": best[2]}


def fit_W(dev, B, pc):
    if not all(type(y) is int for _x, y in dev):
        return None
    ys = [y for _x, y in dev]
    n = len(ys)
    yv = np.array([float(y) for y in ys])
    nphi = len(pc.phi)
    allv = sorted({v for x, _y in dev for v in x})
    okphi = [j for j in range(nphi) if all(pc.vec(v)[j] is not None for v in allv)]
    feat_sets = [()] + [(j,) for j in okphi] + [(i, j) for i in okphi for j in okphi if i < j]
    keys = _data_keys([v for x, _y in dev for v in x], B["single_keys"])
    best = None
    for c in B["consts"]:
        head = [[1] if c == 1 else [c ** len(x), 1] for x, _y in dev]
        for ncl, kname, kf in keys:
            base_p = (1 if c == 1 else 2) + ncl
            if base_p >= n or (best is not None and base_p >= best[0]):
                continue
            cls = sorted({kf(v) for x, _y in dev for v in x}, key=repr)
            ci = {k: t for t, k in enumerate(cls)}
            # G[e][k] = [sum w, sum w*phi_0, ...] (exact ints)
            G = []
            for x, _y in dev:
                m = len(x)
                acc = [[0] * (1 + nphi) for _ in cls]
                for i, v in enumerate(x):
                    w = c ** (m - 1 - i)
                    row = acc[ci[kf(v)]]
                    row[0] += w
                    f = pc.vec(v)
                    for j in okphi:
                        row[1 + j] += w * f[j]
                G.append(acc)
            Gf = np.array(G, dtype=float)                       # (n, ncl, 1+nphi)
            Hf = np.array(head, dtype=float)
            for size in (0, 1, 2):
                params = (1 if c == 1 else 2) + ncl * (size + 1)
                if params >= n or (best is not None and params >= best[0]):
                    continue
                cands = [S for S in feat_sets if len(S) == size]
                cols = [[0] + [1 + j for j in S] for S in cands]
                Xs = np.stack([np.concatenate([Hf, Gf[:, :, cl].reshape(n, -1)], axis=1) for cl in cols])
                mask = _float_fit(Xs, yv)
                for S, cl, ok in zip(cands, cols, mask):
                    if not ok:
                        continue
                    rows = [tuple(h + [G[e][k][q] for k in range(ncl) for q in cl]) for e, h in enumerate(head)]
                    coef = _exact(list(zip(rows, ys)))
                    if coef is None:
                        continue
                    best = (params, "W c=%d key=%s feats=%s" % (c, kname, [pc.phi[j][0] for j in S]),
                            (c, kf, cls, cl, coef))
                    break
    if best is None:
        return None
    params, desc, (c, kf, cls, cl, coef) = best
    ci = {k: t for t, k in enumerate(cls)}

    def pred(xs):
        m = len(xs)
        acc = [[0] * (1 + nphi) for _ in cls]
        for i, v in enumerate(xs):
            k = kf(v)
            if k not in ci:
                return None
            f = pc.vec(v)
            w = c ** (m - 1 - i)
            acc[ci[k]][0] += w
            for q in cl[1:]:
                if f[q - 1] is None:
                    return None
                acc[ci[k]][q] += w * f[q - 1]
        row = ([1] if c == 1 else [c ** m, 1]) + [acc[k][q] for k in range(len(cls)) for q in cl]
        return _pred(coef, row)
    return {"params": params, "desc": desc, "pred": pred}


CLASSES = [("E", fit_E), ("F", fit_F), ("S", fit_S), ("P", fit_P), ("W", fit_W)]


def run(dev, test, cfg) -> Dict:
    """The REGRESSION rung verdict for one family (dev-fit, dev-selected)."""
    B = derive_banks(cfg)
    pc = PhiCache(B["phi"])
    out = {"version": VERSION, "classes": {}, "solved": False, "solved_by": None, "best_selected_test_acc": 0.0}
    for cname, f in CLASSES:
        try:
            m = f(dev, B, pc)
        except (OverflowError, ValueError, ZeroDivisionError, np.linalg.LinAlgError) as e:   # numeric trouble
            out["classes"][cname] = {"error": type(e).__name__}
            continue
        if m is None:
            out["classes"][cname] = None
            continue
        ok = 0
        for xs, y in test:
            try:
                p = m["pred"](xs)
            except (OverflowError, ZeroDivisionError, TypeError):
                p = None
            if p is not None and p == y and type(p) is type(y):
                ok += 1
        acc = ok / len(test)
        out["classes"][cname] = {"params": m["params"], "model": m["desc"], "test_acc": round(acc, 4)}
        out["best_selected_test_acc"] = max(out["best_selected_test_acc"], round(acc, 4))
        if ok == len(test) and not out["solved"]:
            out["solved"], out["solved_by"] = True, cname
    return out
