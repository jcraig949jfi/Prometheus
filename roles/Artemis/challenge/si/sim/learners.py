"""Learners of prereg s2.3 as register programs (HK dropped: AMENDMENTS_P2 A1).

run_learner(kind, m, xs, S, Dend, W, cap, ...) -> metrics dict.
W: 0 (transfer), finite >= 1, or None (= inf).
kinds: I, IW (k), IH, RH, RX, RQ, RG, RU (Bennett chain), RULMT, RMIN.
"""
import math
import numpy as np
from regmachine import RM

INF = 10 ** 9
FLOOR = 1e-12


def _const(v):
    return lambda: v


def lmt_recompute(m, xs, start_state, lo, hi):
    """Lange-McKenzie-Tapp style: Euler tour of the configuration tree of 'run f over x_lo..x_hi'
    from (0, start) until the first arrival at level D; then the reverse tour back to the start edge.
    Returns (value_at_level_D, ops_forward, ops_backward, moves). Each move costs |S| + 1 f-evaluations
    (scan for children in the node's rotation, plus the parent)."""
    D = hi - lo + 1
    y = [None] + [int(xs[p]) for p in range(lo, hi + 1)]  # y[1..D]
    F = m.F
    nS = m.nS

    def parent(node):
        i, s = node
        if i >= D:
            return None
        sp = F[s][y[i + 1]]
        return None if sp < 0 else (i + 1, sp)

    def rotation(node):
        i, s = node
        rot = []
        if i > 0:
            x = y[i]
            for c in range(nS):
                if F[c][x] == s:
                    rot.append((i - 1, c))
        p = parent(node)
        if p is not None:
            rot.append(p)
        return rot

    def succ(u, v):
        rot = rotation(v)
        k = rot.index(u)
        return v, rot[(k + 1) % len(rot)]

    def pred(v, wnode):
        rot = rotation(v)
        k = rot.index(wnode)
        return rot[k - 1], v

    start = (0, start_state)
    e = (start, parent(start))
    e0 = e
    moves = 0
    while e[1][0] != D:
        e = succ(*e)
        moves += 1
    val = e[1][1]
    # reverse tour
    f = e
    back = 0
    while f != e0:
        f = pred(*f)
        back += 1
    assert f == e0 and back == moves
    cost = (moves + 1) * (nS + 1)
    return val, cost, cost, moves


def run_learner(kind, m, xs, S, Dend, W, cap=None, k=None, ih=None, want_cert=True):
    T = len(xs) - 1
    nS, w, wx = m.nS, m.w, m.wx
    Fl = lambda s, x: m.F[s][x]
    Finv = lambda s2, x: m.PRE[(s2, x)][0]
    ident = lambda x: x
    rm = RM(xs)
    Tm = m.T
    Wm1 = INF if W is None else (W - 1)
    Wret = INF if W is None else W
    ops_step = np.zeros(T + 1)
    lat_step = np.zeros(T + 1)
    bits_step = np.zeros(T + 1)
    exact_step = np.zeros(T + 1, dtype=bool)
    pred = [None] * (T + 1)  # per-step predictive distribution for x_{t+1}
    mode_nonmerge = False
    overflow_t = None
    lmt_calls = []
    extra_ws_peak = 0

    persistent_state = kind in ("I", "RG", "RU", "RULMT", "RMIN", "RH", "RX")
    if persistent_state:
        rm.alloc("s", w)
        rm.xc("s", m.s0)
    if kind == "IH":
        rm.alloc("h", 8)
        PH, PHinv, kbit, PIH = ih
    if kind == "RMIN":
        P = m.perm_extension()
        Pinv = [[0] * nS for _ in range(m.nX)]
        for x in range(m.nX):
            for s in range(nS):
                Pinv[x][P[x][s]] = s
    if kind == "IW":
        for i in range(k):
            rm.alloc("win%d" % i, wx)

    def recover(t):
        """How to recompute S_{t-1} from the retained window (window-only sync test, A5)."""
        if t - 1 == 0:
            return ("anchor", 0, m.s0)
        d = int(Dend[t - 1])
        if d <= Wm1:
            return ("sync", d, int(S[t - 1 - d]))
        if t - 1 <= Wm1:
            return ("anchor", t - 1, m.s0)
        return None

    def query_state(t):
        """RQ / IW: can S_t be recomputed from the retained window of length L?"""
        d = int(Dend[t])
        if d <= Wret:
            return ("sync", d)
        if t <= Wret:
            return ("anchor", t)
        return None

    for t in range(1, T + 1):
        ops0 = rm.ops
        x_t = int(xs[t])
        lat = 1
        if kind in ("I", "RG", "RU", "RULMT", "RH", "RX"):
            rm.alloc("xin", wx)
            if W == 0:
                rm.deliver("xin", t)
            else:
                rm.tab("xin", ident, (), (t,))
            rm.alloc("s2", w)
            rm.tab("s2", Fl, ("s", "xin"))
            pre = m.PRE[(rm.v["s2"], rm.v["xin"])]
            if len(pre) == 1:
                rm.tab("s", Finv, ("s2", "xin"))
                rm.swap("s", "s2")
                rm.free("s2")
            else:
                if kind == "I":
                    rm.erase("s")
                    rm.swap("s", "s2")
                    rm.free("s2")
                elif kind == "RH":
                    rm.push("s")
                    rm.swap("s", "s2")
                    rm.free("s2")
                elif kind == "RX":
                    rm.export("s")
                    rm.swap("s", "s2")
                    rm.free("s2")
                else:  # RG / RU / RULMT
                    rec = None if mode_nonmerge else recover(t)
                    if mode_nonmerge:
                        rm.tab("s2", Fl, ("s", "xin"))  # undo s2; keep s (no merge, no erase)
                        rm.free("s2")
                    elif rec is not None:
                        how, D, start = rec
                        scanlen = D
                        rm.charge(2 * scanlen * nS, 2 * scanlen)
                        if kind == "RG":
                            val = int(S[t - 1])
                            rm.tab("s", _const(val), (), (), cost=D)
                            rm.charge(0, D)
                        elif kind == "RU":
                            lo = t - D
                            names = ["c%d" % i for i in range(D + 1)]
                            for n_ in names:
                                rm.alloc(n_, w)
                            rm.xc(names[0], start)
                            for i in range(1, D + 1):
                                rm.tab(names[i], Fl, (names[i - 1],), (lo - 1 + i,))
                            rm.xr("s", names[D])
                            for i in range(D, 0, -1):
                                rm.tab(names[i], Fl, (names[i - 1],), (lo - 1 + i,))
                            rm.xc(names[0], start)
                            for n_ in reversed(names):
                                rm.free(n_)
                        else:  # RULMT
                            if D == 0:
                                val, cf, cb, mv = start, 1, 1, 0
                            else:
                                val, cf, cb, mv = lmt_recompute(m, xs, start, t - D, t - 1)
                            assert val == int(S[t - 1])
                            wsb = max(1, math.ceil(math.log2(D + 2))) + 2 * (w + max(1, math.ceil(math.log2(D + 2))))
                            rm.alloc("lmtws", wsb)
                            rm.free("lmtws")
                            rm.tab("s", _const(val), (), (), cost=cf + cb + 1)
                            rm.charge(0, 2 * D)
                            lmt_calls.append((D, cf + cb, nS))
                        assert rm.v["s"] == 0
                        rm.swap("s", "s2")
                        rm.free("s2")
                    else:
                        scanlen = min(Wm1, t - 1)
                        rm.charge(2 * scanlen * nS, 2 * scanlen)
                        if cap is not None and rm.stack_bits + w > cap:
                            mode_nonmerge = True
                            overflow_t = t
                            rm.tab("s2", Fl, ("s", "xin"))
                            rm.free("s2")
                        else:
                            rm.push("s")
                            rm.swap("s", "s2")
                            rm.free("s2")
            if W == 0:
                if kind == "I":
                    rm.erase("xin")
                elif kind == "RH":
                    rm.push("xin")
                elif kind == "RX":
                    rm.export("xin")
            else:
                rm.tab("xin", ident, (), (t,))
            rm.free("xin")
            est = rm.v["s"]
            pred[t] = ("s", est)
            exact_step[t] = est == S[t]
        elif kind == "RMIN":
            rm.alloc("xin", wx)
            rm.tab("xin", ident, (), (t,))
            rm.perm("s", P, keysrc="xin", Pinv=Pinv)
            rm.tab("xin", ident, (), (t,))
            rm.free("xin")
            est = rm.v["s"]
            pred[t] = ("s", est)
            exact_step[t] = est == S[t]
        elif kind == "RQ":
            if W == 0:
                rm.alloc("xin", wx)
                rm.deliver("xin", t)
                rm.push("xin")  # the agent's own exact store
                rm.free("xin")
                d = int(Dend[t])
                qs = ("sync", d) if d < INF else ("anchor", t)  # own store holds all of x_1..x_t
                readsf = 0
            else:
                qs = query_state(t)
                readsf = 1
            if qs is not None:
                how, D = qs
                rm.charge(2 * D * nS, 2 * D * readsf)
                rm.alloc("q", w)
                val = int(S[t])
                rm.tab("q", _const(val), (), (), cost=D)
                rm.tab("q", _const(val), (), (), cost=D)
                rm.free("q")
                rm.charge(0, 2 * D * readsf)
                lat = D * nS + D + 1
                pred[t] = ("s", val)
                exact_step[t] = True
            else:
                L = min(Wret, t)
                b = m.filter_belief(xs, t - L + 1, t)
                rm.charge(2 * L * nS * nS, 2 * L)
                lat = L * nS * nS + 1
                pred[t] = ("b", b)
                exact_step[t] = False
        elif kind == "IW":
            if t > k:
                rm.erase("win%d" % (k - 1))
            for i in range(k - 1, 0, -1):
                rm.swap("win%d" % i, "win%d" % (i - 1))
            rm.deliver("win0", t)
            d = int(Dend[t])
            if d <= k or t <= k:
                D = d if d <= k else t
                rm.charge(D * nS)
                lat = D * nS + D + 1
                pred[t] = ("s", int(S[t]))
                exact_step[t] = True
            else:
                b = m.filter_belief(xs, t - k + 1, t)
                rm.charge(k * nS * nS)
                lat = k * nS * nS + 1
                pred[t] = ("b", b)
                exact_step[t] = False
        elif kind == "IH":
            rm.alloc("xin", wx)
            if W == 0:
                rm.deliver("xin", t)
            else:
                rm.tab("xin", ident, (), (t,))
            rm.perm("h", PH, keysrc="xin", Pinv=PHinv)
            if m.merges(int(S[t]), x_t):
                rm.erase_bit("h", int(kbit[t]))
            if W == 0:
                rm.erase("xin")
            else:
                rm.tab("xin", ident, (), (t,))
            rm.free("xin")
            pred[t] = ("h", rm.v["h"])
            exact_step[t] = False
        else:
            raise ValueError(kind)
        ops_step[t] = rm.ops - ops0
        lat_step[t] = lat
        bits_step[t] = rm.bits()

    # ----- losses -----
    loss = np.zeros(T + 1)
    for t in range(1, T):
        xn = int(xs[t + 1])
        po = Tm[int(S[t]), xn]
        kind_p, val = pred[t]
        if kind_p == "s":
            pl = Tm[val, xn]
        elif kind_p == "b":
            pl = float(val @ Tm[:, xn])
        else:
            pl = PIH[val, xn]
        if kind_p == "s" and val == S[t]:
            loss[t] = 0.0
        else:
            loss[t] = math.log2(po) - math.log2(max(pl, FLOOR))
    exact = bool(exact_step[1:T].all())
    Dx = float(loss[1:T].mean())
    half = T // 2
    tt = np.arange(half, T + 1)
    slope = float(np.polyfit(tt, bits_step[half:T + 1], 1)[0]) if T > 4 else 0.0
    res = dict(
        kind=kind, W=("inf" if W is None else W), cap=("inf" if cap is None else cap), k=k,
        D=Dx, exact=exact, sync=float(exact_step[1:T + 1].mean()),
        M_peak=rm.peak, M_end=rm.bits(), slope=slope, stack_end=rm.stack_bits,
        M_export=rm.exp_bits,
        C_mean=float(ops_step[1:].mean()), C_max=float(ops_step[1:].max()),
        LAT_mean=float(lat_step[1:].mean()), LAT_p99=float(np.percentile(lat_step[1:], 99)),
        LAT_max=float(lat_step[1:].max()),
        reads_step=rm.reads / T, erase_step=rm.erased / T, erase_total=rm.erased,
        overflow_t=overflow_t,
        D_after_overflow=(float(loss[overflow_t:T].mean()) if overflow_t and overflow_t < T else None),
    )
    if lmt_calls:
        arr = np.array(lmt_calls, dtype=float)
        res["lmt_n"] = len(lmt_calls)
        res["lmt_ops_mean"] = float(arr[:, 1].mean())
        res["lmt_ratio_mean"] = float((arr[:, 1] / np.maximum(1, arr[:, 0] * arr[:, 2] ** 2)).mean())
        res["lmt_D_mean"] = float(arr[:, 0].mean())
    if want_cert:
        res["cert"] = rm.backward_certificate()
    return res
