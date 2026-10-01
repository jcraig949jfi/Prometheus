"""W2-12 step 2-3: founder-independence models over the comparable 7ae3 table (splice OFF, BASE, tier M).

Parameterisation (complementary log-log; independence is exact, not approximate):
    -log(1 - P_bk) = exp(a_b) * k**beta
Independence  <=>  beta = 1   (P = 1 - (1-p_b)^k, with p_b = 1 - exp(-exp(a_b)))
Models
    A    single p1, beta=1                                   (1 par)
    A2   single p1, beta free                                (2)
    B_FE block-specific p1 (fixed), beta=1                   (#blocks)
    B_RE p1 random per block: a_b ~ N(mu, s^2), beta=1       (2)
    B_BB p1 ~ Beta(u, v) per block (beta-binomial-type), beta=1 (2)
    C_FE block fixed + beta free                             (#blocks+1)
    C_RE random block + beta free                            (3)
    C_BB Beta block + beta free                              (3)
    C_PW block fixed + pairwise hazard: -log(1-P) = k*l_b + g*k(k-1)/2   (#blocks+1)
    SAT  every (block, k) cell its own rate
Cross-validation: leave-one-experiment-out (LOBO). Two scores:
    marg : log marginal likelihood of the held-out block's entire data (a new batch, p_b unknown)
    cond : for k-dose blocks only, log predictive of the held-out block's k>1 arms given its own k=1 arm
           (RE/BB: posterior over p_b; *_plugin: p_b = MLE of its k=1 arm)
"""
import json
import math
import pathlib
from collections import defaultdict

import numpy as np
from scipy import optimize, stats

HERE = pathlib.Path(__file__).resolve().parent
T = json.loads((HERE / "run_table.json").read_text())
ROWS = [r for r in T if r["comparable"]]
BLOCKS = sorted({r["block"] for r in ROWS})
DOSE_BLOCKS = sorted({r["block"] for r in ROWS if r["k"] > 1})
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(40)
GH_W = GH_W / GH_W.sum()
_Z = np.linspace(-12.0, 6.0, 721)          # logit grid for the Beta mixture
PGRID = 1 / (1 + np.exp(-_Z))
PJAC = PGRID * (1 - PGRID) * (_Z[1] - _Z[0])  # dp = p(1-p) dz
EPS = 1e-12
DOSSIER_630 = {"c_runaway_confirm", "x_h2_norecomb", "x_critical_mass", "c_critical_mass", "x_dose_curve",
               "x_ticket", "x_decay", "x_sterile"}


def cells(endpoint, rows=ROWS):
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        c[(r["block"], r["k"])][0] += endpoint(r["depth"])
        c[(r["block"], r["k"])][1] += 1
    return {key: tuple(v) for key, v in c.items()}


def ll_binom(x, n, P):
    P = np.clip(P, EPS, 1 - EPS)
    return x * np.log(P) + (n - x) * np.log1p(-P)


def Pk(a, k, beta=1.0):
    return -np.expm1(-np.exp(a) * np.power(float(k), beta))


def Pk_pw(lam, k, g):
    h = max(k * lam + g * k * (k - 1) / 2.0, 1e-15)
    return -math.expm1(-h)


def by_block(cs):
    d = defaultdict(list)
    for (b, k), (x, n) in cs.items():
        d[b].append((k, x, n))
    return d


def block_ll_fixed(a, arms, beta=1.0):
    return float(sum(ll_binom(x, n, Pk(a, k, beta)) for k, x, n in arms))


def block_ll_re(mu, s, arms, beta=1.0):
    a = mu + s * GH_X
    tot = np.zeros_like(a)
    for k, x, n in arms:
        tot = tot + ll_binom(x, n, Pk(a, k, beta))
    m = tot.max()
    return float(m + math.log(float(np.sum(GH_W * np.exp(tot - m)))))


A_GRID = np.log(-np.log1p(-PGRID))


def block_ll_bb(u, v, arms, beta=1.0):
    tot = stats.beta.logpdf(PGRID, u, v)
    for k, x, n in arms:
        tot = tot + ll_binom(x, n, Pk(A_GRID, k, beta))
    m = tot.max()
    return float(m + math.log(float(np.sum(np.exp(tot - m) * PJAC))))


def _nll_factory(model, cs):
    bb = by_block(cs)
    blocks = sorted(bb)
    nb = len(blocks)

    def nll(th):
        if model == "A":
            return -sum(block_ll_fixed(th[0], bb[b]) for b in blocks)
        if model == "A2":
            return -sum(block_ll_fixed(th[0], bb[b], th[1]) for b in blocks)
        if model == "B_FE":
            return -sum(block_ll_fixed(th[i], bb[b]) for i, b in enumerate(blocks))
        if model == "C_FE":
            return -sum(block_ll_fixed(th[i], bb[b], th[nb]) for i, b in enumerate(blocks))
        if model == "C_PW":
            return -sum(sum(float(ll_binom(x, n, Pk_pw(math.exp(th[i]), k, th[nb]))) for k, x, n in bb[b])
                        for i, b in enumerate(blocks))
        if model == "B_RE":
            return -sum(block_ll_re(th[0], math.exp(th[1]), bb[b]) for b in blocks)
        if model == "C_RE":
            return -sum(block_ll_re(th[0], math.exp(th[1]), bb[b], th[2]) for b in blocks)
        if model == "B_BB":
            return -sum(block_ll_bb(math.exp(min(th[0], 9.0)), math.exp(min(th[1], 11.0)), bb[b]) for b in blocks)
        if model == "C_BB":
            return -sum(block_ll_bb(math.exp(min(th[0], 9.0)), math.exp(min(th[1], 11.0)), bb[b], th[2]) for b in blocks)
        raise KeyError(model)
    return nll, blocks, nb


def fit(model, cs):
    nll, blocks, nb = _nll_factory(model, cs)
    bb = by_block(cs)
    a0 = math.log(-math.log(1 - 0.1))
    if model in ("B_FE", "C_FE", "C_PW"):
        # start each block at its own k=1 rate (or pooled)
        st = []
        for b in blocks:
            x, n = sum(x for k, x, n in bb[b] if k == 1), sum(n for k, x, n in bb[b] if k == 1)
            p = min(max(x / n if n else 0.1, 0.005), 0.9)
            st.append(math.log(-math.log1p(-p)) if model != "C_PW" else math.log(-math.log1p(-p)))
        x0 = st + ([1.0] if model == "C_FE" else [0.0] if model == "C_PW" else [])
    else:
        x0 = {"A": [a0], "A2": [a0, 1.0], "B_RE": [a0, math.log(0.3)], "C_RE": [a0, math.log(0.3), 1.0],
              "B_BB": [math.log(2.0), math.log(18.0)], "C_BB": [math.log(2.0), math.log(18.0), 1.0]}[model]
    starts = [x0]
    if model in ("B_RE", "C_RE"):
        starts += [[a0, math.log(0.03)] + x0[2:], [a0, math.log(1.0)] + x0[2:]]
    if model in ("B_BB", "C_BB"):
        starts += [[math.log(30.0), math.log(250.0)] + x0[2:], [math.log(0.7), math.log(6.0)] + x0[2:]]
    best = None
    for s0 in starts:
        meth = "L-BFGS-B" if len(s0) > 4 else "Nelder-Mead"
        r = optimize.minimize(nll, s0, method=meth) if meth == "L-BFGS-B" else optimize.minimize(
            nll, s0, method=meth, options={"maxiter": 4000, "maxfev": 4000, "xatol": 1e-6, "fatol": 1e-8})
        r2 = optimize.minimize(nll, r.x, method="Nelder-Mead",
                               options={"maxiter": 4000, "maxfev": 4000, "xatol": 1e-6, "fatol": 1e-8})
        if r2.fun < r.fun:
            r = r2
        if best is None or r.fun < best.fun:
            best = r
    return {"ll": -float(best.fun), "theta": [float(v) for v in best.x], "npar": len(best.x), "blocks": blocks}


def sat_ll(cs):
    return float(sum(ll_binom(x, n, x / n) for (x, n) in cs.values()))


def chi2_sf(x, df):
    return float(stats.chi2.sf(max(x, 0.0), df))


def profile_ci(cs, model, mle, lo=0.2, hi=4.0):
    """95% profile-likelihood CI for beta (last parameter)."""
    nll, blocks, nb = _nll_factory(model, cs)
    th = list(mle["theta"])
    idx = len(th) - 1
    target = mle["ll"] - 0.5 * stats.chi2.ppf(0.95, 1)

    def prof(bv):
        def sub(o):
            return nll(list(o) + [bv])
        meth = "L-BFGS-B" if idx > 4 else "Nelder-Mead"
        r = optimize.minimize(sub, th[:idx], method=meth)
        return -float(r.fun) - target
    b0 = th[idx]
    out = []
    for edge in (lo, hi):
        try:
            out.append(round(float(optimize.brentq(prof, min(b0, edge), max(b0, edge), xtol=1e-3)), 3))
        except ValueError:
            out.append(None)
    return out


def lobo(cs, models=("A", "A2", "B_RE", "C_RE")):
    bb = by_block(cs)
    res = {m: {"marg": 0.0, "cond": 0.0, "per_block": {}} for m in models}
    for hb in sorted(bb):
        train = {key: v for key, v in cs.items() if key[0] != hb}
        arms = bb[hb]
        k1 = [a for a in arms if a[0] == 1]
        kx = [a for a in arms if a[0] > 1]
        for m in models:
            th = fit(m, train)["theta"]
            beta = th[-1] if m in ("A2", "C_RE", "C_BB") else 1.0
            if m in ("A", "A2"):
                marg = block_ll_fixed(th[0], arms, beta)
                cond = block_ll_fixed(th[0], kx, beta) if kx else None
            elif m in ("B_RE", "C_RE"):
                marg = block_ll_re(th[0], math.exp(th[1]), arms, beta)
                cond = marg - block_ll_re(th[0], math.exp(th[1]), k1, beta) if kx else None
            else:
                marg = block_ll_bb(math.exp(th[0]), math.exp(th[1]), arms, beta)
                cond = marg - block_ll_bb(math.exp(th[0]), math.exp(th[1]), k1, beta) if kx else None
            res[m]["marg"] += marg
            if cond is not None:
                res[m]["cond"] += cond
            res[m]["per_block"][hb] = {"marg": round(marg, 3), "cond": None if cond is None else round(cond, 3)}
    for tag, free in (("B_FE_plugin", False), ("C_FE_plugin", True)):
        tot, per = 0.0, {}
        for hb in DOSE_BLOCKS:
            arms = bb[hb]
            x1, n1 = next((x, n) for k, x, n in arms if k == 1)
            a_b = math.log(-math.log1p(-min(max(x1 / n1, 1e-3), 1 - 1e-3)))
            beta = 1.0
            if free:
                beta = fit("C_FE", {key: v for key, v in cs.items() if key[0] != hb})["theta"][-1]
            c = block_ll_fixed(a_b, [a for a in arms if a[0] > 1], beta)
            tot += c
            per[hb] = {"cond": round(c, 3), "beta_train": round(beta, 3)}
        res[tag] = {"cond": tot, "per_block": per}
    return res


def analyse_endpoint(name, endpoint, rows=ROWS, do_cv=True, do_ci=True):
    cs = cells(endpoint, rows)
    out = {"endpoint": name, "cells": {"%s|k%d" % key: list(v) for key, v in sorted(cs.items())}}
    fits = {m: fit(m, cs) for m in (("A", "A2", "B_FE", "C_FE", "C_PW", "B_RE", "C_RE", "B_BB", "C_BB") if do_cv
                                    else ("A", "A2", "B_FE", "C_FE", "C_PW"))}
    llsat, nsat = sat_ll(cs), len(cs)
    out["fits"] = {m: {"ll": round(f["ll"], 4), "npar": f["npar"], "aic": round(2 * f["npar"] - 2 * f["ll"], 3)}
                   for m, f in fits.items()}
    out["fits"]["SAT"] = {"ll": round(llsat, 4), "npar": nsat, "aic": round(2 * nsat - 2 * llsat, 3)}
    out["beta_hat"] = {m: round(fits[m]["theta"][-1], 4) for m in ("A2", "C_FE", "C_RE", "C_BB") if m in fits}
    out["pairwise_g_hat"] = round(fits["C_PW"]["theta"][-1], 5)
    out["pairwise_lambda_mean"] = round(float(np.mean(np.exp(fits["C_PW"]["theta"][:-1]))), 5)
    if "B_RE" in fits:
        out["re_sd_cloglog"] = {"B_RE": round(math.exp(fits["B_RE"]["theta"][1]), 4),
                                "C_RE": round(math.exp(fits["C_RE"]["theta"][1]), 4)}
        u, v = math.exp(fits["B_BB"]["theta"][0]), math.exp(fits["B_BB"]["theta"][1])
        out["bb_p1"] = {"mean": round(u / (u + v), 4), "u+v": round(u + v, 2),
                        "sd": round(math.sqrt(u * v / ((u + v) ** 2 * (u + v + 1))), 4)}
    out["p1_fixed_by_block"] = {b: round(float(1 - math.exp(-math.exp(a))), 4)
                                for b, a in zip(fits["B_FE"]["blocks"], fits["B_FE"]["theta"])}
    out["p1_A"] = round(float(1 - math.exp(-math.exp(fits["A"]["theta"][0]))), 4)

    def lrt(m0, m1, df=None, boundary=False):
        l1 = llsat if m1 == "SAT" else fits[m1]["ll"]
        G = 2 * (l1 - fits[m0]["ll"])
        d = df if df is not None else ((nsat if m1 == "SAT" else fits[m1]["npar"]) - fits[m0]["npar"])
        p = chi2_sf(G, d)
        if boundary:
            p = 0.5 * p if G > 1e-9 else 1.0
        return {"G": round(G, 3), "df": d, "p": round(p, 5)}
    out["lrt"] = {
        "A_vs_SAT (one p1, independence, every cell)": lrt("A", "SAT"),
        "A_vs_B_FE (batch heterogeneity of p1, beta=1)": lrt("A", "B_FE"),
        "A_vs_A2 (superadditivity with pooled p1)": lrt("A", "A2"),
        "B_FE_vs_C_FE (superadditivity given block p1)": lrt("B_FE", "C_FE"),
        "B_FE_vs_C_PW (pairwise term given block p1)": lrt("B_FE", "C_PW"),
        "C_FE_vs_SAT (residual lack of fit after beta)": lrt("C_FE", "SAT"),
        "B_FE_vs_SAT (independence with block p1)": lrt("B_FE", "SAT"),
    }
    if "B_RE" in fits:
        out["lrt"].update({
            "A_vs_B_RE (RE variance, boundary 50:50)": lrt("A", "B_RE", df=1, boundary=True),
            "B_RE_vs_C_RE (superadditivity given RE)": lrt("B_RE", "C_RE"),
            "B_BB_vs_C_BB (superadditivity given Beta p1)": lrt("B_BB", "C_BB")})
    if do_ci:
        out["beta_ci95_profile"] = {m: profile_ci(cs, m, fits[m]) for m in ("A2", "C_FE")}
    bb = by_block(cs)
    per = {}
    for b in (DOSE_BLOCKS if do_cv else ()):
        sub = {key: v for key, v in cs.items() if key[0] == b}
        f0, f1, ls = fit("B_FE", sub), fit("C_FE", sub), sat_ll(sub)
        G = 2 * (ls - f0["ll"])
        per[b] = {"arms(k,x,n)": sorted(bb[b]), "p1_joint": round(float(1 - math.exp(-math.exp(f0["theta"][0]))), 4),
                  "beta_hat": round(f1["theta"][-1], 3),
                  "lrt_indep_vs_sat": {"G": round(G, 3), "df": len(sub) - 1, "p": round(chi2_sf(G, len(sub) - 1), 5)},
                  "expected_under_own_joint_p1": {str(k): round(n * float(Pk(f0["theta"][0], k)), 2)
                                                  for k, x, n in sorted(bb[b])}}
    out["per_dose_block"] = per
    if do_cv:
        cv = lobo(cs)
        out["cv_lobo"] = {m: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in d.items()}
                          for m, d in cv.items()}
    return out


def pooled_plugin(endpoint, pool_filter, k=4):
    pool = [r for r in ROWS if r["k"] == 1 and pool_filter(r)]
    p1 = sum(endpoint(r["depth"]) for r in pool) / len(pool)
    kk = [r for r in ROWS if r["k"] == k]
    x = sum(endpoint(r["depth"]) for r in kk)
    q = 1 - (1 - p1) ** k
    return {"pool_n": len(pool), "p1": round(p1, 4), "k": k, "obs": x, "n": len(kk), "exp": round(q * len(kk), 2),
            "upper_tail_p": round(float(stats.binom.sf(x - 1, len(kk), q)), 5)}


if __name__ == "__main__":
    E5 = lambda d: int(d >= 5)
    E20 = lambda d: int(d >= 20)
    rep = {"n_rows": len(ROWS), "blocks": BLOCKS, "dose_blocks": DOSE_BLOCKS}
    rep["plugin"] = {
        "d5_pool630_k4": pooled_plugin(E5, lambda r: r["block"] in DOSSIER_630),
        "d5_pool798_k4": pooled_plugin(E5, lambda r: True),
        "d5_pool798_k2": pooled_plugin(E5, lambda r: True, 2),
        "d5_pool798_k8": pooled_plugin(E5, lambda r: True, 8),
        "d20_pool630_k4": pooled_plugin(E20, lambda r: r["block"] in DOSSIER_630),
        "d20_pool798_k4": pooled_plugin(E20, lambda r: True),
        "d5_dose_blocks_k1_only_k4": pooled_plugin(E5, lambda r: r["block"] in DOSE_BLOCKS),
    }
    import time
    t0 = time.time()
    rep["d5"] = analyse_endpoint("depth>=5", E5)
    print("d5 done", time.time() - t0, flush=True)
    (HERE / "models.json").write_text(json.dumps(rep, indent=1))
    rep["d20"] = analyse_endpoint("depth>=20", E20)
    rows630 = [r for r in ROWS if r["block"] in DOSSIER_630]
    rep["d5_pool630_only"] = analyse_endpoint("depth>=5 (630 set)", E5, rows630, do_cv=False, do_ci=False)["lrt"]
    rep["d20_pool630_only"] = analyse_endpoint("depth>=20 (630 set)", E20, rows630, do_cv=False, do_ci=False)["lrt"]
    rep["drop_one_dose_block"] = {}
    for drop in DOSE_BLOCKS:
        rr = [r for r in ROWS if r["block"] != drop]
        for nm, ep in (("d5", E5), ("d20", E20)):
            a = analyse_endpoint(nm, ep, rr, do_cv=False, do_ci=False)
            rep["drop_one_dose_block"]["%s_without_%s" % (nm, drop)] = {
                "beta_C_FE": a["beta_hat"]["C_FE"], "lrt": {k: v["p"] for k, v in a["lrt"].items()}}
    (HERE / "models.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep["plugin"], indent=1))
    for nm in ("d5", "d20"):
        r = rep[nm]
        print("=====", nm)
        for key in ("fits", "beta_hat", "beta_ci95_profile", "pairwise_g_hat", "re_sd_cloglog", "bb_p1", "p1_A",
                    "p1_fixed_by_block", "lrt", "per_dose_block"):
            print(key, json.dumps(r[key], indent=1))
        print("CV", json.dumps({m: {"marg": v.get("marg"), "cond": v.get("cond")} for m, v in r["cv_lobo"].items()},
                               indent=1))
        print("CV per block cond", json.dumps({m: v["per_block"] for m, v in r["cv_lobo"].items()}, indent=0)[:3000])
    print("630 only d5", json.dumps(rep["d5_pool630_only"], indent=1))
    print("630 only d20", json.dumps(rep["d20_pool630_only"], indent=1))
    print("drop", json.dumps(rep["drop_one_dose_block"], indent=1))
