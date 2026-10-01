"""W-S bookkeeping: per pair-trial arrival features, predictors, accuracy + CI.
Predictor definitions are frozen in PLAN.md s3; this file implements them."""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from prometheus.ananke import lens_swap as LS

PRED_NAMES = ("P3_cone", "P1_first", "P2_dflight", "P4_last", "P5_dleaf", "P6_share")


def pair_index(elog: dict, pairs: int):
    """{pair: {recipient: [(te, arr, v, jit, dist)]}} over both mirror sides (deduped)."""
    idx = [defaultdict(set) for _ in range(pairs)]
    te = elog["te"]
    for side, rk, dk, lk in (("A", "recA", "dlA", "delay"), ("B", "recB", "dlB", "delayB")):
        m = elog[dk].astype(bool)
        for i in np.flatnonzero(m):
            p = int(elog["p"][i])
            idx[p][int(elog[rk][i])].add((int(te[i]), int(te[i] + elog[lk][i]), int(elog["v"][i]),
                                         int(elog["jit"][i]), int(elog["dist"][i])))
    return idx


def cone_leaves(pidx: dict, a: int, t0: int, tau: int, ro: int):
    """Backward cone of the readout (a, ro) through mirror-different deliveries emitted at te >= t0.
    Returns the set of leaf kinds: 'S' (delivered by tau, i.e. held in a site/inbox at the swap) and
    'F' (emitted <= tau, delivered after tau: in flight at the swap). A copy emitted after tau by v
    recurses into v's own deliveries up to its emit tick; with none it is an 'S' leaf (v's
    difference was held in v's site state at the swap)."""
    memo = {}

    def rec(u, T):
        key = (u, T)
        if key in memo:
            return memo[key]
        memo[key] = set()
        out = set()
        for (te, arr, v, _j, _d) in pidx.get(u, ()):
            if te < t0 or arr > T:
                continue
            if te <= tau:
                out.add("S" if arr <= tau else "F")
            else:
                sub = rec(v, te)
                out |= sub if sub else {"S"}
        memo[key] = out
        return out

    return rec(a, ro)


def three_way(leaves: set) -> str:
    if not leaves:
        return "U"
    if leaves == {"S"}:
        return "S"
    if leaves == {"F"}:
        return "C"
    return "M"


def features(pidx: dict, a: int, s: int, t0: int, tau: int, ro: int) -> dict:
    """All predictors + descriptors for one pair-trial at swap tick tau."""
    direct = sorted(x for x in pidx.get(a, ()) if x[0] >= t0 and x[1] <= ro)   # (te, arr, v, jit, dist)
    arr = [x[1] for x in direct]
    f = {"n_direct": len(direct), "arr_rel": [x - tau for x in arr]}
    if direct:
        first = min(direct, key=lambda x: (x[1], x[0]))
        last = max(direct, key=lambda x: (x[1], x[0]))
        f["P1_first"] = "S" if first[1] <= tau else "C"
        f["P4_last"] = "S" if last[1] <= tau else "C"
        f["first_arr_rel"] = first[1] - tau
        f["first_te_rel"] = first[0] - tau
        f["first_jit"] = first[3]
        f["first_dist"] = first[4]
        f["first_from_source"] = int(first[2] == s)
        f["first_jit_cross"] = int(first[1] - first[3] <= tau < first[1])
        # all copies emitted at the first-arrival copy's (te, v): did jitter split them across tau?
        sib = [x for x in direct if x[0] == first[0] and x[2] == first[2]]
        f["first_sib_split"] = int(any(x[1] <= tau for x in sib) and any(x[1] > tau for x in sib))
    else:
        f["P1_first"] = f["P4_last"] = "U"
    held = [x for x in direct if x[0] <= tau]
    f["P2_dflight"] = "C" if any(x[1] > tau for x in held) else "S"
    f["P5_dleaf"] = three_way({"S" if x[1] <= tau else "F" for x in held})
    lv = cone_leaves(pidx, a, t0, tau, ro)
    f["P3_cone"] = three_way(lv)
    f["P3b_cone_any"] = "C" if "F" in lv else ("S" if lv else "U")
    nf = sum(1 for x in held if x[1] > tau)
    f["P6_share"] = "U" if not held else ("C" if nf / len(held) > 0.5 else "S")
    f["n_direct_flight"] = nf
    f["n_direct_held"] = sum(1 for x in held if x[1] <= tau)
    return f


def accuracy(pred: np.ndarray, pat: np.ndarray, pair: np.ndarray, n_boot=2000, seed=0, alpha=0.01):
    """Accuracy of pred (S/C/M/U) against pat over pair-trials with pat in {S, C}; M/U count as errors.
    99% bootstrap over pairs."""
    keep = np.isin(pat, ("S", "C"))
    pred, pat, pair = pred[keep], pat[keep], pair[keep]
    n = len(pat)
    if n == 0:
        return {"n": 0, "acc": None, "ci99": None}
    corr = (pred == pat).astype(float)
    up = np.unique(pair)
    by = {p: np.flatnonzero(pair == p) for p in up}
    acc = float(corr.mean())
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        pr = rng.choice(up, size=len(up))
        ii = np.concatenate([by[p] for p in pr])
        bs.append(corr[ii].mean())
    return {"n": int(n), "acc": acc, "ci99": (float(np.quantile(bs, alpha / 2)), float(np.quantile(bs, 1 - alpha / 2))),
            "fS_true": float(np.mean(pat == "S")),
            "pred_counts": {x: int(np.sum(pred == x)) for x in ("S", "C", "M", "U")}}


def shuffled(pred: np.ndarray, pat: np.ndarray, seed=0) -> np.ndarray:
    """MUST-FAIL input: predictor labels permuted across the S/C pair-trials."""
    out = pred.copy()
    keep = np.flatnonzero(np.isin(pat, ("S", "C")))
    out[keep] = np.random.default_rng(seed).permutation(pred[keep])
    return out


def loo_pair_majority(pat: np.ndarray, pair: np.ndarray) -> np.ndarray:
    """H3: predict each pair-trial by the majority S/C of the same pair's OTHER pair-trials (same stratum)."""
    out = np.full(len(pat), "U", dtype="<U1")
    for i in range(len(pat)):
        oth = (pair == pair[i]) & (np.arange(len(pat)) != i) & np.isin(pat, ("S", "C"))
        ns, nc = np.sum(pat[oth] == "S"), np.sum(pat[oth] == "C")
        if ns > nc:
            out[i] = "S"
        elif nc > ns:
            out[i] = "C"
    return out


def table(run: dict, env, offsets, trials, Pd: int, period: int, delta: int):
    """Rows (one per eligible pair-trial x offset): pair, trial, offset, phase, pattern, targeted pattern,
    arm agreement, features."""
    ep = run["ep"]
    M = run["normal"].shape[0]
    P = M // 2
    src = ep.schedule.sense_idx[:, 0].numpy()
    cue_idx = {}
    for k in trials:
        wi = pair_index(run["cue_logs"][k], M)            # per world m (cue-flip twin log)
        merged = []
        for p in range(P):
            d = defaultdict(set)
            for m in (2 * p, 2 * p + 1):
                for u, xs in wi[m].items():
                    d[u] |= xs
            merged.append(d)
        cue_idx[k] = merged
    rows = []
    for o in offsets:
        R = run["res"]
        site, s0s = R["site"][o]
        chan, s0c = R["chan"][o]
        tab = LS.pair_trial_table(run["normal"], site, chan, s0s, s0c, trials)
        tgt = None
        if "site_a" in R:
            sa, s0sa = R["site_a"][o]
            fa, s0fa = R["flight_a"][o]
            tgt = LS.pair_trial_table(run["normal"], sa, fa, s0sa, s0fa, trials)
        for k in trials:
            t0 = k * Pd
            tau = t0 + o
            ro = int(ep.ro_tick[0, k])
            for p in range(P):
                if not tab["ok"][p, k]:
                    continue
                a = int(run["ro_site"][2 * p])
                r = {"pair": p, "trial": k, "o": o, "q": tau % period, "tau_rel_ro": tau - ro,
                     "pat": str(tab["pat"][p, k]), "t0": t0,
                     "y_same_prev": int(ep.y[2 * p, k] == ep.y[2 * p, k - 1])}
                if tgt is not None:
                    r["pat_tgt"] = str(tgt["pat"][p, k])
                    # does the flight_a arm reproduce the chan arm (both partners), site_a the site arm?
                    r["fa_eq_chan"] = int(np.array_equal(fa[2 * p:2 * p + 2, k], chan[2 * p:2 * p + 2, k]))
                    r["sa_eq_site"] = int(np.array_equal(sa[2 * p:2 * p + 2, k], site[2 * p:2 * p + 2, k]))
                r["cue_diff_ro"] = int(run["cue_diff"][k][2 * p]) + int(run["cue_diff"][k][2 * p + 1])
                r.update(features(cue_idx[k][p], a, int(src[2 * p]), t0, tau, ro))
                rows.append(r)
    return rows


def inflight_check(run: dict, trials, offsets, Pd: int, te_shift: int = 0):
    """KA-L: for each (pair, trial, offset in snaps), the set of in-flight slots addressed to the readout
    site whose content differs between mirror partners (real Msum/Mcnt) vs the set predicted from the
    log (mirror-different copies with te <= tau < arr). te_shift != 0 is the MUST-FAIL input.
    Returns (n_checked, n_equal, n_nonempty_real, n_real_subset_of_pred). Pass = every real difference
    is predicted (subset); equality can fail only where two logged copies cancel in the slot sum."""
    M = run["normal"].shape[0]
    P = M // 2
    el = dict(run["elog"])
    el["te"] = el["te"] + te_shift
    pidx = pair_index(el, P)
    LM = run["LM"]
    nchk = neq = nne = nsub = 0
    for (k, o), (Ms, Mc) in run["snaps"].items():
        tau = k * Pd + o
        Ms, Mc = Ms.numpy(), Mc.numpy()
        for p in range(P):
            a = int(run["ro_site"][2 * p])
            dA = Ms[:, 2 * p, a], Mc[:, 2 * p, a]
            dB = Ms[:, 2 * p + 1, a], Mc[:, 2 * p + 1, a]
            real = {s for s in range(LM) if not (np.array_equal(dA[0][s], dB[0][s]) and np.array_equal(dA[1][s], dB[1][s]))}
            pred = {arr % LM for (te, arr, *_r) in pidx[p].get(a, ()) if te <= tau < arr}
            nchk += 1
            neq += int(real == pred)
            nsub += int(real <= pred)
            nne += int(bool(real))
    return nchk, neq, nne, nsub
