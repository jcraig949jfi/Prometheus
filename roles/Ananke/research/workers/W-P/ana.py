"""W-P truth-table analysis: relevant sets, function classes, minimal decisive sets,
census, per-offset summary with 99% pair-bootstrap CIs. Pure numpy."""
from __future__ import annotations

import itertools
from collections import Counter

import numpy as np


def cube(n):
    return np.array(list(itertools.product((0, 1), repeat=n)), dtype=np.int8)   # [2^n, n]


def zindex(z):
    """row index of z in cube(n) (big-endian bits)."""
    idx = 0
    for b in z:
        idx = idx * 2 + int(b)
    return idx


def full_a(s0_half, half_subs, n):
    """s0_half [K, M] from blocks with the listed subsets (all with z_0 = 0).
    Returns a [2^n, M/2] sign of world-A readout for every z (A rows from blocks,
    complements from world B rows via b(z) = a(~z))."""
    K, M = s0_half.shape
    P = M // 2
    a = np.full((2 ** n, P), 99, np.int64)
    for j, z in enumerate(half_subs):
        za = zindex(z)
        zb = zindex([1 - x for x in z])
        a[za] = np.sign(s0_half[j, 0::2])
        a[zb] = np.sign(s0_half[j, 1::2])
    assert (a != 99).all()
    return a


def identity_rate(s0_full, subs):
    """full cube run: b(z) == a(~z) (sign) fraction over (pair, z)."""
    pos = {tuple(z): j for j, z in enumerate(subs)}
    ok = []
    for j, z in enumerate(subs):
        jc = pos[tuple(1 - x for x in z)]
        ok.append(np.sign(s0_full[j, 1::2]) == np.sign(s0_full[jc, 0::2]))
    return float(np.mean(ok))


def f_table(a, yA, yB):
    """a [2^n, P] signs; -> f [2^n, P] in {0,1,-1(tie)}; elig [P]."""
    f = np.where(a == yB[None], 1, np.where(a == yA[None], 0, -1))
    elig = (a[0] == yA) & (a[-1] == yB)
    return f, elig


def relevant(fz, n):
    """fz [2^n] in {0,1}. -> tuple of relevant component indices."""
    C = cube(n)
    R = []
    for i in range(n):
        flip = zindex_all(C ^ (np.arange(n) == i).astype(np.int8))
        if (fz != fz[flip]).any():
            R.append(i)
    return tuple(R)


_ZI = {}


def zindex_all(C):
    w = 2 ** np.arange(C.shape[1] - 1, -1, -1)
    return C @ w


def classify_fn(fz, n):
    C = cube(n)
    R = relevant(fz, n)
    if len(R) == 1:
        return "DICT", R, None
    if len(R) == 2:
        i, j = R
        v = {(x, y): fz[(C[:, i] == x) & (C[:, j] == y)][0] for x in (0, 1) for y in (0, 1)}
        if v[(1, 0)] == 0 and v[(0, 1)] == 0:
            return "AND", R, None
        if v[(1, 0)] == 1 and v[(0, 1)] == 1:
            return "OR", R, None
        return "OTHER2", R, None
    if len(R) == 3:
        for g in R:
            x, y = [k for k in R if k != g]
            for (p, q) in ((x, y), (y, x)):
                pred = np.where(C[:, g] == 0, C[:, p], C[:, q])
                if (pred == fz).all():
                    return "MUX", R, (g, p, q)
        return "HIGHER", R, None
    return ("HIGHER" if len(R) > 3 else "CONST"), R, None


def ana_proj(fz, n, R):
    """f restricted to its relevant set R (others 0): truth table over R, cube order."""
    C = cube(n)
    rows = []
    for zr in itertools.product((0, 1), repeat=len(R)):
        m = np.ones(len(C), bool)
        for i in range(n):
            m &= C[:, i] == (zr[R.index(i)] if i in R else 0)
        rows.append(int(fz[m][0]))
    return rows


def min_decisive(fz, n):
    C = cube(n)
    comp = zindex_all(1 - C)
    ok = (fz == 1) & (fz[comp] == 0)
    if not ok.any():
        return None
    sz = C.sum(1)
    m = sz[ok].min()
    return [tuple(np.flatnonzero(C[r])) for r in np.flatnonzero(ok & (sz == m))]


def analyse(tabs, names, site_mask, n_boot=2000, seed=0, alpha=0.01):
    """tabs: list over trials of (a [2^n,P], yA [P], yB [P]). Returns summary."""
    n = len(names)
    siteZ = zindex([1 if m else 0 for m in site_mask])
    chanZ = zindex([0 if m else 1 for m in site_mask])
    recs = []            # per eligible pair-trial
    for k, (a, yA, yB) in enumerate(tabs):
        f, elig = f_table(a, yA, yB)
        P = a.shape[1]
        for p in range(P):
            if not elig[p]:
                continue
            fz = f[:, p]
            fs, fc = fz[siteZ], fz[chanZ]
            if fs < 0 or fc < 0:
                pat = "tie"
            elif fs == 1 and fc == 0:
                pat = "S"
            elif fs == 0 and fc == 1:
                pat = "C"
            else:
                pat = "N"
            r = {"pair": p, "trial": k, "pat": pat, "yA": int(yA[p])}
            if (fz >= 0).all():
                cls, R, mux = classify_fn(fz, n)
                md = min_decisive(fz, n)
                Ri = list(R)
                sub = ana_proj(fz, n, Ri)
                r.update(full=True, cls=cls, R=tuple(names[i] for i in R), fn="".join(map(str, sub)),
                         mux=None if mux is None else tuple(names[i] for i in mux),
                         md=None if md is None else [tuple(names[i] for i in s) for s in md])
                if pat == "N":
                    d = int(a[siteZ, p])            # chimeras' common answer (world A, site swap)
                    r["d"] = d
            else:
                r["full"] = False
            recs.append(r)
    return recs


def _frac(recs, pairs_w, pred):
    """weighted fraction over records (pair bootstrap weights)."""
    num = den = 0.0
    for r in recs:
        w = pairs_w.get(r["pair"], 0)
        if w == 0:
            continue
        den += w
        num += w * bool(pred(r))
    return num / den if den else None


def summarize(recs, names, n_boot=2000, seed=0, alpha=0.01, P=128):
    """Per-offset summary with frozen decision rules (PLAN s2)."""
    rng = np.random.default_rng(seed)
    el = recs
    N = [r for r in recs if r["pat"] == "N" and r.get("full")]
    out = {"eligible": len(el)}
    for q in ("S", "C", "N", "tie"):
        out[f"f{q}"] = float(np.mean([r["pat"] == q for r in el])) if el else None
    out["base_N"] = len(N)
    out["frac_full_N"] = (len(N) / max(1, sum(r["pat"] == "N" for r in el)))
    if not N:
        out["class"] = "UNDEFINED"
        return out
    rc = Counter(r["R"] for r in N)
    cc = Counter(r["cls"] for r in N)
    mc = Counter(tuple(sorted(r["md"])) if r["md"] else None for r in N)
    gc = Counter(r["mux"][0] for r in N if r["cls"] == "MUX")
    out["R_top"] = [(list(k), v / len(N)) for k, v in rc.most_common(6)]
    out["cls"] = {k: v / len(N) for k, v in cc.items()}
    out["md_top"] = [([list(s) for s in k] if k else None, v / len(N)) for k, v in mc.most_common(5)]
    out["fn_top"] = [(list(k[0]), k[1], v / len(N)) for k, v in Counter((r["R"], r["fn"]) for r in N).most_common(4)]
    out["comp_in_R"] = {nm: float(np.mean([nm in r["R"] for r in N])) for nm in names}
    out["d_plus"] = float(np.mean([r["d"] > 0 for r in N]))
    top2 = next((k for k, _ in rc.most_common() if len(k) == 2), None)
    topg = gc.most_common(1)[0][0] if gc else None
    preds = {
        "joint2": lambda r: top2 is not None and r["R"] == top2 and r["cls"] in ("AND", "OR"),
        "gated": lambda r: topg is not None and r["cls"] == "MUX" and r["mux"][0] == topg,
        "higher": lambda r: r["cls"] == "HIGHER",
        "d_plus": lambda r: r["d"] > 0,
        "d_minus": lambda r: r["d"] < 0,
    }
    ones = {p: 1 for p in range(P)}
    pt = {k: _frac(N, ones, f) for k, f in preds.items()}
    boots = {k: [] for k in preds}
    for _ in range(n_boot):
        c = Counter(rng.integers(P, size=P).tolist())
        for k, f in preds.items():
            v = _frac(N, c, f)
            if v is not None:
                boots[k].append(v)
    ci = {k: (float(np.quantile(v, alpha / 2)), float(np.quantile(v, 1 - alpha / 2))) if v else None
          for k, v in boots.items()}
    out["pt"], out["ci99"] = pt, ci
    out["top2"], out["gate"] = (list(top2) if top2 else None), topg
    # census CI for fN
    fb = []
    for _ in range(n_boot):
        c = Counter(rng.integers(P, size=P).tolist())
        v = _frac(el, c, lambda r: r["pat"] == "N")
        if v is not None:
            fb.append(v)
    out["fN_ci99"] = (float(np.quantile(fb, alpha / 2)), float(np.quantile(fb, 1 - alpha / 2)))
    if len(N) < 20:
        cls = "UNDEFINED"
    elif pt["joint2"] >= .60 and ci["joint2"][0] >= .45:
        cls = f"JOINT-2({','.join(top2)})"
    elif pt["gated"] >= .60 and ci["gated"][0] >= .45:
        cls = f"GATED({topg})"
    elif pt["higher"] >= .50:
        cls = "HIGHER"
    else:
        cls = "MIXED"
    pol = ("RECTIFIED(+)" if pt["d_plus"] >= .9 and ci["d_plus"][0] >= .8 else
           "RECTIFIED(-)" if pt["d_minus"] >= .9 and ci["d_minus"][0] >= .8 else "PAIR-SPECIFIC")
    out["class"], out["polarity"] = cls, pol
    return out


def direct_decisive(s0_full, subs, yA, yB):
    """No identity assumption: full-cube run. Z is decisive for pair p iff world A with
    swap Z answers y_B AND world B with swap Z answers y_A. -> per pair list of minimal
    decisive Z (tuples of indices) or None; plus eligibility (both normal-correct)."""
    sA, sB = np.sign(s0_full[:, 0::2]), np.sign(s0_full[:, 1::2])
    z0 = [j for j, z in enumerate(subs) if sum(z) == 0][0]
    elig = (sA[z0] == yA) & (sB[z0] == yB)
    ok = (sA == yB[None]) & (sB == yA[None])
    sz = np.array([sum(z) for z in subs])
    out = []
    for p in range(sA.shape[1]):
        idx = np.flatnonzero(ok[:, p])
        if len(idx) == 0:
            out.append(None)
            continue
        m = sz[idx].min()
        out.append([tuple(np.flatnonzero(subs[j])) for j in idx if sz[j] == m])
    return out, elig
