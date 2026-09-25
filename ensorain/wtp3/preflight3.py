"""WTP-03 necessity + null-gated preflight (PREREG_WTP03 s3). Cheapest gates first.

G0 BUILD      field/graph legal, >= 64 cells
G1 BUDGET     cap >= sum(dims)+1 (the marginal carrier fits); cap <= 0.25 cells (no memorisation)
G2 NONDEG     organism-free dry run: variance, reachability, rewards survive (WTP-02 N5)
G3 ECONOMY    calibration with metabolism 0 over 600 steps: random/frozen (trivial) income (a trivial
              life that traps itself in a sink counts at the rate it achieved), the income of a
              generic learning-capable PANEL (additive, dct, lowrank, cp, tt; each with its fixed
              recipe, if it fits the budget), oracle income. The best panel learner (1 seed) is
              re-run on a 2nd seed; it becomes this world's CARRIER.
              (i) INFORMATION VALUE at the cheapest information price (kappa 0.01): oracle_min > 0,
                  oracle_min - trivial_max > 0.02 and > 0.2|trivial_max|, else G3_INFO_VALUELESS.
              (ii) the LARGEST information-cost scale kappa in (1, .3, .1, .03, .01) (multiplying
                  p_compute, p_read, p_write, p_probe, p_rollout) at which the best panel learner is
                  FEASIBLE: with metabolism m := trivial_max + 0.25 (oracle_min - trivial_max) (trivial
                  loses, oracle clearly wins), the learner's net rate learner_min - m >= -0.5 x gap
                  (not hopeless); confirmed on 2 seeds. Else G3_ECONOMY.
              If the learner's net rate is negative, energy0 := max(energy0, 1.1 x 0.75 T x deficit + 10)
              so it survives >= 75% of its lifetime. Whether learning PAYS in life is recorded, not gated.
G4 EXPOSURE   calibrated economy: trivial lives (300 steps, 2 seeds x random/frozen) end with U < 0;
              oracle (600 steps) U > 0; the carrier's full life reaches >= 75% of its lifetime with
              >= 200 learning updates and >= 64 distinct cells in its stream.
G5 DEMAND     on the carrier's real stream, an UNBOUNDED batch planted mechanism (DCT least squares,
              low-rank ALS, CP-ALS) beats every batch null N0-N4 by >= 0.10 AC on interp or recomb
G6 SURROGATE  the same on the marginal-preserving surrogate stream is <= max(0.05, 0.5 x real)
Returns (admitted, record)."""
import copy

import numpy as np

from .collider import experience, holdout, test_sets, null_ladder, carrier, _addr, CALIB_PANEL, make
from .world3 import build, mem_cap, run_life, streams, AC
from ensorain.wtp2.preflight import dry_run

# ------------------------------------------------------------------ planted mechanisms (unbounded, batch)


def _dct_fit(dims, A, y, k):
    freqs = [np.arange(d) for d in dims]
    idx = np.array(np.meshgrid(*freqs, indexing="ij")).reshape(len(dims), -1).T
    idx = idx[np.argsort(idx.sum(1), kind="stable")][:k]

    def feats(AA):
        F = np.ones((len(AA), len(idx)))
        for m, d in enumerate(dims):
            F *= np.cos(np.pi * idx[None, :, m] * (AA[:, m][:, None] + 0.5) / d)
        return F
    F = feats(A)
    w = np.linalg.lstsq(F.T @ F + 1e-3 * np.eye(len(idx)), F.T @ y, rcond=None)[0]
    return lambda AA: feats(AA) @ w


def _lr_fit(dims, A, y, r, rng, iters=8):
    D = len(dims)
    s = min(range(1, D), key=lambda s: abs(np.prod(dims[:s]) - np.prod(dims[s:])))
    I = np.ravel_multi_index(A[:, :s].T, dims[:s])
    J = np.ravel_multi_index(A[:, s:].T, dims[s:])
    U = rng.normal(0, 0.3, (int(np.prod(dims[:s])), r))
    V = rng.normal(0, 0.3, (int(np.prod(dims[s:])), r))
    for _ in range(iters):
        for M, N, P, Q in ((U, V, I, J), (V, U, J, I)):
            for i in np.unique(P):
                sel = P == i
                B = N[Q[sel]]
                M[i] = np.linalg.solve(B.T @ B + 1e-2 * np.eye(r), B.T @ y[sel])

    def pred(AA):
        return (U[np.ravel_multi_index(AA[:, :s].T, dims[:s])] * V[np.ravel_multi_index(AA[:, s:].T, dims[s:])]).sum(1)
    return pred


def _cp_fit(dims, A, y, r, rng, iters=8):
    D = len(dims)
    F = [rng.normal(0, 0.5, (d, r)) for d in dims]
    for _ in range(iters):
        for m in range(D):
            P = np.ones((len(y), r))
            for j in range(D):
                if j != m:
                    P *= F[j][A[:, j]]
            for v in np.unique(A[:, m]):
                sel = A[:, m] == v
                B = P[sel]
                F[m][v] = np.linalg.solve(B.T @ B + 1e-2 * np.eye(r), B.T @ y[sel])

    def pred(AA):
        P = np.ones((len(AA), r))
        for j in range(D):
            P *= F[j][AA[:, j]]
        return P.sum(1)
    return pred


def planted(st, T, rng):
    dims, x, V0 = st["dims"], st["x"].reshape(-1), st["V0"]
    A = _addr(dims, st["c"])
    y = st["y"]
    n = len(y)
    out = {}
    if n < 32 or len(T) < 32:
        return out
    TA = _addr(dims, T)
    fits = {"dct": lambda: _dct_fit(dims, A, y, max(1, min(n // 4, 512))),
            "lowrank": lambda: _lr_fit(dims, A, y, 4, rng),
            "cp": lambda: _cp_fit(dims, A, y, 3, rng)}
    for k, f in fits.items():
        try:
            out[k] = AC(f()(TA), x[T], V0)
        except (np.linalg.LinAlgError, ValueError, MemoryError):
            out[k] = None
    return out


def demand(st, seed):
    """Planted (unbounded batch) excess over the batch null ladder on interp and recomb."""
    tests = test_sets(st, np.random.default_rng(seed + 17))
    stR, blk, hinfo = holdout(st, np.random.default_rng(seed + 29))
    rng = np.random.default_rng(seed + 31)
    res = {}
    for s, stream, T in (("interp", st, tests["interp"]), ("recomb", stR, blk)):
        if stream is None or T is None or len(T) < 32:
            res[s] = None
            continue
        tt = dict(interp=np.zeros(0, int), recomb=np.zeros(0, int), novel=np.zeros(0, int))
        tt[s] = T
        lad = null_ladder(stream, 10 ** 9, tt)
        best_null = max(v[s] for v in lad.values() if v[s] is not None)
        pl = planted(stream, T, rng)
        best_pl = max([v for v in pl.values() if v is not None], default=None)
        res[s] = dict(best_null=best_null, planted=pl, excess=(best_pl - best_null) if best_pl is not None else None,
                      null_const=lad["N1_const"][s])
    ex = [v["excess"] for v in res.values() if v and v["excess"] is not None]
    return (max(ex) if ex else None), res, hinfo


# ------------------------------------------------------------------ preflight

KAPPAS = (1.0, 0.3, 0.1, 0.03, 0.01)            # information-cost scale search (never 0: information is never free)
INFO_COSTS = ("p_compute", "p_read", "p_write", "p_probe", "p_rollout")


def scaled(g, kappa):
    g2 = copy.deepcopy(g)
    for k in INFO_COSTS:
        g2["resource"][k] = g["resource"][k] * kappa
    return g2


def preflight(g, seed, n_seeds=2, n2_life=300):
    rec = dict(gate=None)
    S, _ = streams(seed)
    try:
        x, rew, dims, adj, node_cell, _ = build(g, S)
    except Exception as ex:
        return False, dict(gate="G0_BUILD", reason=f"{type(ex).__name__}: {ex}")
    cells = x.size
    if cells < 64:
        return False, dict(gate="G0_BUILD", reason=f"{cells} cells < 64")
    cap = mem_cap(g, cells)
    rec.update(cells=cells, cap=cap, dims=dims)
    if cap < sum(dims) + 1 or cap > 0.25 * cells + 1:
        return False, dict(rec, gate="G1_BUDGET")
    T = g["time"]["lifetime"]
    mv, reach, rewarding = dry_run(g, S, x, rew, adj, T)
    rec.update(min_var=mv, dry_reach=reach, rewarding=rewarding)
    if mv < 0.1 or reach < 0.3 or rewarding < 0.01:
        return False, dict(rec, gate="G2_NONDEG")
    # G3 economy calibration: trivial twins, a generic learner panel, the oracle
    Lc = min(T, 600)

    def rate(r, trivial=False):
        if r["status"] == "OK" or (trivial and r.get("degenerate_reason") == "topology"):
            return r["U"] / r["steps"]
        return None
    fits = []
    for kind in CALIB_PANEL:
        try:
            m0 = make(kind, dims, cap, np.random.default_rng(0))
        except ValueError:
            continue
        if m0.n_floats() <= cap:
            fits.append(kind)
    if not fits:
        return False, dict(rec, gate="G3_ECONOMY", reason="no calibration learner fits the budget")

    def twins(kappa, seeds):
        gz = scaled(g, kappa)
        gz["resource"]["metabolism"], gz["resource"]["energy0"] = 0.0, 1e9
        triv, orc = [], []
        for k in seeds:
            for tw in ("random", "frozen"):
                r = run_life(carrier(gz, fits[0]), seed * 10 + k, twin=tw, lifetime=Lc, excursions=False)
                v = rate(r, trivial=True)
                if v is None:
                    return None, f"{tw}: {r.get('status')} {r.get('reason') or r.get('degenerate_reason')}"
                triv.append(v)
            r = run_life(carrier(gz, fits[0]), seed * 10 + 5 + k, twin="oracle", lifetime=Lc, excursions=False)
            v = rate(r)
            if v is None:
                return None, f"oracle: {r.get('status')} {r.get('degenerate_reason')}"
            orc.append(v)
        return dict(triv=triv, orc=orc, gz=gz), None

    def learners(tw, seeds):
        gz = tw["gz"]
        panel = {kind: rate(run_life(carrier(gz, kind), seed * 10 + seeds[0], lifetime=Lc, excursions=False)) for kind in fits}
        ok = {k: v for k, v in panel.items() if v is not None}
        if not ok:
            return None
        best = max(ok, key=ok.get)
        lrn = [ok[best]]
        for k in seeds[1:]:
            v = rate(run_life(carrier(gz, best), seed * 10 + k, lifetime=Lc, excursions=False))
            lrn.append(v if v is not None else -1e9)
        return dict(tw, lrn=lrn, panel=panel, best=best)

    def valuable(t):
        tmax, omin = max(t["triv"]), min(t["orc"])
        return omin > 0 and omin - tmax > 0.02 and omin - tmax > 0.2 * abs(tmax)

    def feasible(c):
        """The directive's three conditions, calibrated: trivial loses, oracle clearly wins, and the best
        generic learner is not hopeless (loses at most half the information gap at the calibrated metabolism)."""
        tmax, lmin, omin = max(c["triv"]), min(c["lrn"]), min(c["orc"])
        gap = omin - tmax
        m = tmax + 0.25 * gap
        return valuable(c) and (lmin - m) >= -0.5 * gap, m
    # (i) is information worth anything here at all? (cheapest information costs)
    t0, err = twins(KAPPAS[-1], [0])
    if t0 is None:
        return False, dict(rec, gate="G3_ECONOMY", reason=err)
    rec.update(info_value=dict(triv=t0["triv"], orc=t0["orc"]))
    if not valuable(t0):
        return False, dict(rec, gate="G3_INFO_VALUELESS")
    # (ii) the most expensive information price at which a generic learner is feasible
    chosen, tried = None, []
    for kappa in KAPPAS:
        t, err = twins(kappa, [0])
        if t is None:
            return False, dict(rec, gate="G3_ECONOMY", reason=err, kappa_search=tried)
        c = learners(t, [0]) if valuable(t) else None
        tried.append(dict(kappa=kappa, triv=t["triv"], orc=t["orc"], lrn=None if c is None else c["lrn"],
                          panel=None if c is None else c["panel"]))
        if c is not None and feasible(c)[0]:
            t2, err = twins(kappa, list(range(n_seeds)))
            c2 = learners(t2, list(range(n_seeds))) if t2 is not None else None
            ok2 = c2 is not None and feasible(c2)[0]
            tried.append(dict(kappa=kappa, confirm=True, ok=bool(ok2)))
            if ok2:
                chosen = (kappa, c2)
            break
    if chosen is None:
        return False, dict(rec, gate="G3_ECONOMY", kappa_search=tried)
    kappa, c = chosen
    triv, orc, lrn = c["triv"], c["orc"], c["lrn"]
    g.update(scaled(g, kappa))
    g["resource"]["kappa"] = kappa
    g["memory"]["carrier"] = c["best"]
    tmax, lmin, omin = max(triv), min(lrn), min(orc)
    _, m = feasible(c)
    net = lmin - m
    if net < 0:  # energy buffer so a feasible learner lives >= 75% of its lifetime (plus 10% margin)
        g["resource"]["energy0"] = float(max(g["resource"]["energy0"], 1.1 * 0.75 * T * (-net) + 10.0))
    g["resource"]["metabolism"] = float(m)
    g["resource"]["calibrated3"] = True
    g["resource"].pop("calibrated", None)
    rec.update(panel_rates=c["panel"], carrier=c["best"], kappa=kappa, kappa_search=tried, rate_trivial=triv,
               rate_learner=lrn, rate_oracle=orc, metabolism_calibrated=m, learner_net_rate=net,
               learning_pays=bool(lmin - tmax >= max(0.01, 0.1 * (omin - tmax))), energy0=g["resource"]["energy0"])
    # G4 exposure + trivial loses + oracle wins
    gc = carrier(g)
    us = [run_life(gc, seed * 10 + k, twin=tw, lifetime=n2_life, excursions=False)["U"]
          for k in range(n_seeds) for tw in ("random", "frozen")]
    ro = run_life(gc, seed * 10 + 9, twin="oracle", lifetime=Lc, excursions=False)
    st, life = experience(g, seed)
    rec.update(trivial_U=us, oracle_U=ro.get("U"), life_frac=life.get("life_frac"), updates=life.get("updates"),
               stream_cells=int(len(np.unique(st["c"]))) if st is not None else 0, stream_len=int(len(st["y"])) if st is not None else 0,
               conversions=life.get("conversions"), carrier_status=life.get("status"))
    if max(us) >= 0:
        return False, dict(rec, gate="G4_TRIVIAL_WINS")
    if ro.get("status") != "OK" or ro.get("U", -1) <= 0:
        return False, dict(rec, gate="G4_ORACLE_FAILS")
    if st is None or life.get("status") != "OK" or life["life_frac"] < 0.75 or life["updates"] < 200 or rec["stream_cells"] < 64:
        return False, dict(rec, gate="G4_EXPOSURE")
    # G5 information demand / G6 surrogate
    dm, dres, hinfo = demand(st, seed)
    rec.update(demand=dm, demand_detail=dres, holdout=hinfo, stream_digest=st["digest"])
    if dm is None or dm < 0.10:
        return False, dict(rec, gate="G5_DEMAND")
    sm, _ = experience(g, seed, field="marg")
    if sm is None:
        return False, dict(rec, gate="G6_SURROGATE", reason="no surrogate stream")
    dms, dres_s, _ = demand(sm, seed)
    rec.update(demand_surrogate=dms)
    if dms is not None and dms > max(0.05, 0.5 * dm):
        return False, dict(rec, gate="G6_SURROGATE")
    return True, dict(rec, gate="ADMITTED")
