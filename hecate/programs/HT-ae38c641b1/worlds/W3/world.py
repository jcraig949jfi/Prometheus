"""HT-ae38c641b1 / W3: analyzer staircase world. See IMPLEMENTATION_NOTES.md.

Writes rows.jsonl (one row per arm x seed [x config]), flushed per row.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

R = 0.9
B = (1.0, 0.0)
K_FINE = 16
K_COARSE = 6
SEEDS = [0, 1, 2, 3, 4]
ORBIT_N = 5000
JUMP_REL = 1e-9
KLEENE_TOL = 1e-12
KLEENE_CAP = 20000
ASCENT_CAP = 500
BOUND_ESCAPE = 256.0


def thresholds(n):
    if n == 13:
        mags = 2.0 ** np.arange(-4, 9)
    elif n == 50:
        mags = 2.0 ** (-4 + 12 * np.arange(50) / 49.0)
    else:
        raise ValueError(n)
    return np.sort(np.concatenate([-mags, mags]))


def grid(seed):
    rng = np.random.default_rng(seed)
    phi = float(rng.random())
    t = (phi + np.arange(2 ** K_FINE) / 2 ** K_FINE) % 1.0
    return phi, t


# ---------- interval helpers (vectorised over theta) ----------
def iscale(a, lo, hi):
    """a * [lo, hi] for array a; a == 0 -> [0, 0]."""
    p = a * np.where(a == 0, 0.0, lo)
    q = a * np.where(a == 0, 0.0, hi)
    return np.minimum(p, q), np.maximum(p, q)


def F(c, s, lo, hi):
    """Interval image of x -> r R_theta x + b. lo, hi shape (2, n)."""
    a11, a12, a21, a22 = R * c, -R * s, R * s, R * c
    l1, h1 = iscale(a11, lo[0], hi[0])
    l2, h2 = iscale(a12, lo[1], hi[1])
    l3, h3 = iscale(a21, lo[0], hi[0])
    l4, h4 = iscale(a22, lo[1], hi[1])
    with np.errstate(invalid="ignore"):
        nlo = np.stack([l1 + l2 + B[0], l3 + l4 + B[1]])
        nhi = np.stack([h1 + h2 + B[0], h3 + h4 + B[1]])
    return nlo, nhi


def widen_up(new, T):
    """smallest threshold >= new, +inf if none."""
    idx = np.searchsorted(T, new, side="left")
    out = np.full(new.shape, np.inf)
    ok = idx < len(T)
    out[ok] = T[idx[ok]]
    out[np.isposinf(new)] = np.inf
    return out


def widen_down(new, T):
    """largest threshold <= new, -inf if none."""
    idx = np.searchsorted(T, new, side="right") - 1
    out = np.full(new.shape, -np.inf)
    ok = idx >= 0
    out[ok] = T[np.clip(idx, 0, None)][ok]
    out[np.isneginf(new)] = -np.inf
    return out


def box_width(lo, hi):
    return np.max(hi - lo, axis=0)


def analyzer(theta, d, T):
    c, s = np.cos(theta), np.sin(theta)
    n = theta.size
    lo = np.zeros((2, n))
    hi = np.zeros((2, n))
    x0lo = np.zeros((2, n))
    x0hi = np.zeros((2, n))
    active = np.ones(n, bool)
    iters = np.zeros(n, int)
    cap_hits = 0
    for k in range(ASCENT_CAP):
        idx = np.nonzero(active)[0]
        if idx.size == 0:
            break
        flo, fhi = F(c[idx], s[idx], lo[:, idx], hi[:, idx])
        ylo = np.minimum(np.minimum(flo, 0.0), lo[:, idx])
        yhi = np.maximum(np.maximum(fhi, 0.0), hi[:, idx])
        stable = np.all((ylo >= lo[:, idx]) & (yhi <= hi[:, idx]), axis=0)
        grow = ~stable
        gi = idx[grow]
        if k < d:
            lo[:, gi] = ylo[:, grow]
            hi[:, gi] = yhi[:, grow]
        else:
            ol, oh = lo[:, gi], hi[:, gi]
            yl, yh = ylo[:, grow], yhi[:, grow]
            lo[:, gi] = np.where(yl < ol, widen_down(yl, T), ol)
            hi[:, gi] = np.where(yh > oh, widen_up(yh, T), oh)
        iters[gi] += 1
        active[idx[stable]] = False
    else:
        cap_hits = int(active.sum())
    for _ in range(2):  # narrowing
        flo, fhi = F(c, s, lo, hi)
        ylo = np.minimum(flo, x0lo)
        yhi = np.maximum(fhi, x0hi)
        lo = np.maximum(lo, ylo)
        hi = np.minimum(hi, yhi)
    return box_width(lo, hi), iters, cap_hits


def null_twin(theta, T):
    c, s = np.cos(theta), np.sin(theta)
    n = theta.size
    lo = np.zeros((2, n))
    hi = np.zeros((2, n))
    active = np.ones(n, bool)
    escaped = np.zeros(n, bool)
    for _ in range(KLEENE_CAP):
        idx = np.nonzero(active)[0]
        if idx.size == 0:
            break
        flo, fhi = F(c[idx], s[idx], lo[:, idx], hi[:, idx])
        ylo = np.minimum(np.minimum(flo, 0.0), lo[:, idx])
        yhi = np.maximum(np.maximum(fhi, 0.0), hi[:, idx])
        ch = np.max(np.maximum(np.abs(ylo - lo[:, idx]), np.abs(yhi - hi[:, idx])), axis=0)
        lo[:, idx] = ylo
        hi[:, idx] = yhi
        esc = np.any((yhi > BOUND_ESCAPE) | (ylo < -BOUND_ESCAPE), axis=0)
        escaped[idx[esc]] = True
        done = (ch < KLEENE_TOL) | esc
        active[idx[done]] = False
    unconverged = int(active.sum())
    rlo = widen_down(lo.ravel(), T).reshape(lo.shape)
    rhi = widen_up(hi.ravel(), T).reshape(hi.shape)
    w = box_width(rlo, rhi)
    w[escaped | active] = np.inf
    return w, unconverged, int(escaped.sum())


def concrete_hull(theta):
    c, s = np.cos(theta), np.sin(theta)
    x = np.zeros(theta.size)
    y = np.zeros(theta.size)
    xmin = x.copy(); xmax = x.copy(); ymin = y.copy(); ymax = y.copy()
    for _ in range(ORBIT_N - 1):
        x, y = R * (c * x - s * y) + B[0], R * (s * x + c * y) + B[1]
        np.minimum(xmin, x, out=xmin); np.maximum(xmax, x, out=xmax)
        np.minimum(ymin, y, out=ymin); np.maximum(ymax, y, out=ymax)
    return np.maximum(xmax - xmin, ymax - ymin)


def cantor_like(t, base, keep_map):
    """Staircase: digits in keep_map contribute bit keep_map[d]; any other digit ends
    on a plateau (value += scale). base 3 {0:0,2:1} = Cantor function."""
    t = t.copy()
    val = np.zeros_like(t)
    scale = 0.5
    live = np.ones(t.size, bool)
    for _ in range(40):
        t *= base
        dg = np.floor(t)
        t -= dg
        for dd in range(base):
            m = live & (dg == dd)
            if dd in keep_map:
                val[m] += scale * keep_map[dd]
            else:
                val[m] += scale
                live[m] = False
        scale /= 2
    return val


def count_breakpoints(W):
    fin = W[np.isfinite(W)]
    med = float(np.median(fin)) if fin.size else 1.0
    thr = JUMP_REL * med
    out = {}
    for k in range(K_COARSE, K_FINE + 1):
        step = 2 ** (K_FINE - k)
        w = W[::step]
        a, b = w[:-1], w[1:]
        both_inf = np.isinf(a) & np.isinf(b) & (np.sign(a) == np.sign(b))
        with np.errstate(invalid="ignore"):
            jump = np.where(both_inf, False, np.abs(b - a) > thr)
        jump = jump | (np.isinf(a) ^ np.isinf(b))
        out[k] = int(jump.sum())
    return out, med, thr


def jumps_fine(W, thr):
    a, b = W[:-1], W[1:]
    both_inf = np.isinf(a) & np.isinf(b)
    with np.errstate(invalid="ignore"):
        jump = np.where(both_inf, False, np.abs(b - a) > thr)
    return jump | (np.isinf(a) ^ np.isinf(b))


# ---------- exact rational recheck (stupid explanation 1) ----------
FINF = None  # represents infinity in exact arithmetic


def exact_width(theta_float, d, T):
    c = Fraction(float(np.cos(theta_float)))
    s = Fraction(float(np.sin(theta_float)))
    r = Fraction(R)
    A = [[r * c, -r * s], [r * s, r * c]]
    bb = [Fraction(B[0]), Fraction(B[1])]
    Tf = [Fraction(float(v)) for v in T]
    INF = float("inf")

    def mul(a, l, h):
        if a == 0:
            return Fraction(0), Fraction(0)
        p = a * l if l not in (INF, -INF) else (INF if (a > 0) == (l > 0) else -INF)
        q = a * h if h not in (INF, -INF) else (INF if (a > 0) == (h > 0) else -INF)
        return (min(p, q), max(p, q))

    def add(*xs):
        if any(x == INF for x in xs):
            return INF
        if any(x == -INF for x in xs):
            return -INF
        return sum(xs, Fraction(0))

    def Fx(lo, hi):
        nlo, nhi = [], []
        for i in range(2):
            p = mul(A[i][0], lo[0], hi[0])
            q = mul(A[i][1], lo[1], hi[1])
            nlo.append(add(p[0], q[0], bb[i]))
            nhi.append(add(p[1], q[1], bb[i]))
        return nlo, nhi

    def up(v):
        for x in Tf:
            if x >= v:
                return x
        return INF

    def down(v):
        for x in reversed(Tf):
            if x <= v:
                return x
        return -INF

    lo = [Fraction(0), Fraction(0)]
    hi = [Fraction(0), Fraction(0)]
    for k in range(ASCENT_CAP):
        flo, fhi = Fx(lo, hi)
        ylo = [min(flo[i], Fraction(0), lo[i]) for i in range(2)]
        yhi = [max(fhi[i], Fraction(0), hi[i]) for i in range(2)]
        if all(ylo[i] >= lo[i] and yhi[i] <= hi[i] for i in range(2)):
            break
        if k < d:
            lo, hi = ylo, yhi
        else:
            lo = [down(ylo[i]) if ylo[i] < lo[i] else lo[i] for i in range(2)]
            hi = [up(yhi[i]) if yhi[i] > hi[i] else hi[i] for i in range(2)]
    for _ in range(2):
        flo, fhi = Fx(lo, hi)
        lo = [max(lo[i], min(flo[i], Fraction(0))) for i in range(2)]
        hi = [min(hi[i], max(fhi[i], Fraction(0))) for i in range(2)]
    ws = []
    for i in range(2):
        if hi[i] == INF or lo[i] == -INF:
            ws.append(INF)
        else:
            ws.append(hi[i] - lo[i])
    return max(ws)


def exact_jump(w1, w2, thr):
    INF = float("inf")
    if w1 == INF and w2 == INF:
        return False
    if (w1 == INF) != (w2 == INF):
        return True
    return abs(w2 - w1) > Fraction(thr)


def main():
    t0 = time.process_time()
    if os.path.exists(ROWS):
        os.remove(ROWS)
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    fh = open(ROWS, "a", encoding="utf-8")

    def emit(row):
        row.update({"attempt": attempt, "r": R, "b": list(B), "k_fine": K_FINE,
                    "k_coarse": K_COARSE, "jump_rel": JUMP_REL,
                    "cpu_s_cum": round(time.process_time() - t0, 3)})
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print(row["arm"], row.get("config"), row["seed"], row["N"], flush=True)

    for seed in SEEDS:
        phi, t = grid(seed)
        theta = 2 * np.pi * t
        base = {"seed": seed, "phi": phi, "n_theta": int(t.size)}

        # TREATMENT (default) + intervention variants
        for d in (1, 3, 6):
            for nt in (13, 50):
                T = thresholds(nt)
                W, iters, cap = analyzer(theta, d, T)
                N, med, thr = count_breakpoints(W)
                arm = "TREATMENT" if (d == 3 and nt == 13) else "TREATMENT_VARIANT"
                row = dict(base, arm=arm, config={"d": d, "n_thresholds": nt,
                                                   "narrowing_steps": 2},
                           N={str(k): v for k, v in N.items()}, median_W=med,
                           jump_thr=thr, finite_frac=float(np.isfinite(W).mean()),
                           ascent_cap_hits=cap, max_iters=int(iters.max()))
                if arm == "TREATMENT":
                    jf = jumps_fine(W, thr)
                    it_change = iters[:-1] != iters[1:]
                    row["frac_jumps_with_iter_change"] = (
                        float((jf & it_change).sum() / max(jf.sum(), 1)))
                    row["frac_iter_changes_that_jump"] = (
                        float((jf & it_change).sum() / max(it_change.sum(), 1)))
                    row["n_distinct_finite_W"] = int(np.unique(W[np.isfinite(W)]).size)
                    if seed == 0:
                        rng = np.random.default_rng(12345)
                        J = np.nonzero(jf)[0]
                        NJ = np.nonzero(~jf)[0]
                        pick = np.concatenate([rng.choice(J, min(32, J.size), replace=False),
                                               rng.choice(NJ, min(32, NJ.size), replace=False)])
                        agree = 0
                        for i in pick:
                            e1 = exact_width(theta[i], d, T)
                            e2 = exact_width(theta[i + 1], d, T)
                            if exact_jump(e1, e2, thr) == bool(jf[i]):
                                agree += 1
                        row["exact_recheck"] = {"n_pairs": int(pick.size), "agree": agree,
                                                "n_float_jumps": int(min(32, J.size))}
                emit(row)

        # NULL_TWIN
        T13 = thresholds(13)
        for nt in (13, 50):
            W, unconv, esc = null_twin(theta, thresholds(nt))
            N, med, thr = count_breakpoints(W)
            emit(dict(base, arm="NULL_TWIN" if nt == 13 else "NULL_TWIN_VARIANT",
                      config={"n_thresholds": nt, "kleene_tol": KLEENE_TOL,
                              "kleene_cap": KLEENE_CAP},
                      N={str(k): v for k, v in N.items()}, median_W=med, jump_thr=thr,
                      finite_frac=float(np.isfinite(W).mean()),
                      unconverged=unconv, escaped=esc,
                      n_distinct_finite_W=int(np.unique(W[np.isfinite(W)]).size)))

        # CONTROL
        W = concrete_hull(theta)
        N, med, thr = count_breakpoints(W)
        emit(dict(base, arm="CONTROL", config={"orbit_points": ORBIT_N},
                  N={str(k): v for k, v in N.items()}, median_W=med, jump_thr=thr,
                  finite_frac=float(np.isfinite(W).mean())))

        # POSITIVE_CONTROL
        W = cantor_like(t, 3, {0: 0, 2: 1})
        N, med, thr = count_breakpoints(W)
        emit(dict(base, arm="POSITIVE_CONTROL", config={"staircase": "cantor base3 {0,2}"},
                  N={str(k): v for k, v in N.items()}, median_W=med, jump_thr=thr,
                  finite_frac=1.0))

        # CHEAT
        W = cantor_like(t, 4, {0: 0, 3: 1})
        N, med, thr = count_breakpoints(W)
        emit(dict(base, arm="CHEAT", config={"staircase": "base4 keep {0,3}, dim 0.5"},
                  N={str(k): v for k, v in N.items()}, median_W=med, jump_thr=thr,
                  finite_frac=1.0))
    fh.close()
    with open(os.path.join(HERE, "compute.json"), "w", encoding="utf-8") as f:
        json.dump({"attempt": attempt, "cpu_seconds": time.process_time() - t0}, f)
    print("cpu_s", time.process_time() - t0)


if __name__ == "__main__":
    main()
