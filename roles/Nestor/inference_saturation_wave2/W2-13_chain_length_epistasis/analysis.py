"""W2-13 step 3: does an evolved excess of strict synthetic lethality survive conditioning on executed pre-copy length?

    python -B analysis.py -> analysis.json (+ stdout)
Unit = genome; outcome = strict lethal count k out of n = null-0 sampled pairs (genomes with n = 0 carry no weight).
Models (EVO = 1 for evolved):
  WLS   rate = a + b*X + c*EVO               weights n           (primary, linear-probability)
  WLSi  rate = a + b*X + c*EVO + d*X*EVO     weights n           (slope difference)
  GLM   logit p = a + b*X + c*EVO            binomial, IRLS      (secondary)
X = L_pre (primary), alternatives L_exec, D_pre, frac_both_pre (share of the genome's null-0 pairs whose two
positions are both executed pre-copy in the seed-12345 trace).
CI: 4,000 genome-level bootstrap resamples stratified by group (percentile). Permutation p (two-sided, 4,000):
  FL  Freedman-Lane: residuals of the reduced model (rate ~ X) permuted, full model refit, |t_c| compared;
  STR evolved/unevolved labels permuted within X-quintile strata.
Contrasts: PRIMARY = EVO_SD vs RAND (same function COMPETENT; random hits = the T3 comparator);
  S1 = EVO_SD+EVO_SF vs RAND; S2 = EVO_SD vs RAND+PLANT; S3 = all evolved vs all unevolved.
Also: pair-class rates (both pre / one pre / neither) by group and a nearest-L_pre matched comparison.
"""
import json
import math
import pathlib
import random

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / "lengths.json"))["rows"]
NB = NP = 4000
for r in D:
    r["frac_both_pre"] = (r["n_null0_both_pre"] / r["n_null0"]) if r["n_null0"] else None
    r["EVO"] = int(r["group"].startswith("EVO"))


def design(rs, x, inter=False):
    X = [[1.0, r[x], float(r["EVO"])] + ([r[x] * r["EVO"]] if inter else []) for r in rs]
    return np.array(X), np.array([r["n_strict"] / r["n_null0"] for r in rs]), np.array([r["n_null0"] for r in rs], float)


def wls(X, y, w):
    W = np.sqrt(w)
    Xw, yw = X * W[:, None], y * W
    beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    res = yw - Xw @ beta
    dof = max(len(y) - X.shape[1], 1)
    s2 = res @ res / dof
    cov = s2 * np.linalg.pinv(Xw.T @ Xw)
    return beta, np.sqrt(np.maximum(np.diag(cov), 1e-30))


def glm(X, k, n, it=100):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        eta = np.clip(X @ b, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        w = n * p * (1 - p) + 1e-9
        z = eta + (k - n * p) / w
        b_new = np.linalg.lstsq(X * np.sqrt(w)[:, None], z * np.sqrt(w), rcond=None)[0]
        done = np.max(np.abs(b_new - b)) < 1e-9
        b = b_new
        if done:
            break
    p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
    cov = np.linalg.pinv(X.T @ (X * (n * p * (1 - p))[:, None]))
    return b, np.sqrt(np.diag(cov))


def fit(rs, x):
    rs = [r for r in rs if r["n_null0"] and r[x] is not None]
    X, y, w = design(rs, x)
    beta, se = wls(X, y, w)
    Xi, _, _ = design(rs, x, True)
    bi, sei = wls(Xi, y, w)
    k = np.array([r["n_strict"] for r in rs], float)
    gb, gse = glm(X, k, w)
    rng = random.Random(20261013)
    groups = {}
    for i, r in enumerate(rs):
        groups.setdefault(r["EVO"], []).append(i)
    boot_c, boot_b, boot_d = [], [], []
    for _ in range(NB):
        idx = [rng.choice(g) for g in groups.values() for _ in g]
        bb, _ = wls(X[idx], y[idx], w[idx])
        bbi, _ = wls(Xi[idx], y[idx], w[idx])
        boot_c.append(bb[2]); boot_b.append(bb[1]); boot_d.append(bbi[3])
    ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]  # noqa: E731
    # Freedman-Lane
    Xr = X[:, :2]
    br, _ = wls(Xr, y, w)
    fitted, resid = Xr @ br, y - Xr @ br
    t_obs = beta[2] / se[2]
    perm = list(range(len(y)))
    ge = 0
    for _ in range(NP):
        rng.shuffle(perm)
        bp, sp = wls(X, fitted + resid[perm], w)
        ge += abs(bp[2] / sp[2]) >= abs(t_obs) - 1e-12
    p_fl = (ge + 1) / (NP + 1)
    # stratified label permutation within X quintiles
    xs = np.array([r[x] for r in rs], float)
    qs = np.quantile(xs, [0.2, 0.4, 0.6, 0.8])
    strata = np.searchsorted(qs, xs, side="right")
    lab = X[:, 2].copy()
    ge = 0
    for _ in range(NP):
        lp = lab.copy()
        for s in set(strata.tolist()):
            ii = np.where(strata == s)[0]
            v = lp[ii].tolist(); rng.shuffle(v); lp[ii] = v
        Xp = X.copy(); Xp[:, 2] = lp
        bp, _ = wls(Xp, y, w)
        ge += abs(bp[2]) >= abs(beta[2]) - 1e-12
    p_str = (ge + 1) / (NP + 1)
    strata_mix = {int(s): [int(sum(lab[strata == s] == 1)), int(sum(lab[strata == s] == 0))] for s in sorted(set(strata.tolist()))}
    return {"n_genomes": len(rs), "n_evo": int(sum(X[:, 2])), "n_unevo": int(len(rs) - sum(X[:, 2])),
            "WLS": {"a": beta[0], "b_X": beta[1], "c_EVO": beta[2], "se_c": se[2], "se_b": se[1],
                    "boot95_c": ci(boot_c), "boot95_b": ci(boot_b), "p_perm_FL": p_fl, "p_perm_strat": p_str,
                    "strata_evo_unevo_counts": strata_mix},
            "WLS_interaction": {"b_X": bi[1], "c_EVO": bi[2], "d_XxEVO": bi[3], "se_d": sei[3], "boot95_d": ci(boot_d)},
            "GLM": {"b_X": gb[1], "c_EVO_logodds": gb[2], "se_c": gse[2], "OR_EVO": math.exp(gb[2]),
                    "OR95_wald": [math.exp(gb[2] - 1.96 * gse[2]), math.exp(gb[2] + 1.96 * gse[2])]},
            "X_range_min_med_max": {"evo": [float(min(xs[lab == 1])), float(np.median(xs[lab == 1])), float(max(xs[lab == 1]))],
                                    "unevo": [float(min(xs[lab == 0])), float(np.median(xs[lab == 0])), float(max(xs[lab == 0]))]}}


def pooled(rs):
    n = sum(r["n_null0"] for r in rs); k = sum(r["n_strict"] for r in rs)
    return {"genomes": len(rs), "with_pairs": sum(1 for r in rs if r["n_null0"]), "null0_pairs": n, "strict": k,
            "rate": k / n if n else None}


def pairclass(rs):
    out = {}
    for r in rs:
        pre = set(r["pre_set"])
        for i, j, l, nu in r["pairs"]:
            if nu != 0:
                continue
            c = {2: "both_pre", 1: "one_pre", 0: "neither"}[(i in pre) + (j in pre)]
            o = out.setdefault(c, [0, 0]); o[0] += 1; o[1] += bool(l)
    return {c: {"pairs": v[0], "strict": v[1], "rate": v[1] / v[0]} for c, v in sorted(out.items())}


def matched(evo, une, x="L_pre"):
    """Each unevolved genome with pairs gets the 3 evolved genomes nearest in X (with pairs); pooled rates compared."""
    ev = [r for r in evo if r["n_null0"] and r[x] is not None]
    rows, ke, ku = [], [0, 0], [0, 0]
    for u in une:
        if not u["n_null0"] or u[x] is None:
            continue
        nn = sorted(ev, key=lambda r: abs(r[x] - u[x]))[:3]
        ku[0] += u["n_null0"]; ku[1] += u["n_strict"]
        for r in nn:
            ke[0] += r["n_null0"] / 3; ke[1] += r["n_strict"] / 3
        rows.append({"u": u["name"], "uX": u[x], "u_rate": u["n_strict"] / u["n_null0"], "evoX": [r[x] for r in nn],
                     "evo_rate": sum(r["n_strict"] for r in nn) / sum(r["n_null0"] for r in nn)})
    return {"unevolved_rate": ku[1] / ku[0] if ku[0] else None, "matched_evolved_rate": ke[1] / ke[0] if ke[0] else None,
            "rows": rows}


G = {g: [r for r in D if r["group"] == g] for g in ("EVO_SD", "EVO_SF", "RAND", "PLANT")}
CON = {"PRIMARY_SDvsRAND": G["EVO_SD"] + G["RAND"], "S1_allEVOvsRAND": G["EVO_SD"] + G["EVO_SF"] + G["RAND"],
       "S2_SDvsRAND+PLANT": G["EVO_SD"] + G["RAND"] + G["PLANT"], "S3_allvsall": D}
out = {"pooled": {g: pooled(v) for g, v in G.items()},
       "per_genome": {g: [{k: r[k] for k in ("name", "L_pre", "L_exec", "D_pre", "frac_both_pre", "n_disp", "n_null0",
                                              "n_strict", "n_seed_copy", "L_pre_by_seed")} for r in v] for g, v in G.items()},
       "pairclass": {g: pairclass(v) for g, v in G.items()},
       "matched_L_pre": {"RAND_vs_SD": matched(G["EVO_SD"], G["RAND"]), "PLANT_vs_SD": matched(G["EVO_SD"], G["PLANT"]),
                         "RAND_vs_allEVO": matched(G["EVO_SD"] + G["EVO_SF"], G["RAND"])},
       "fits": {}}
for cname, rs in CON.items():
    for x in ("L_pre", "L_exec", "D_pre", "frac_both_pre"):
        if cname != "PRIMARY_SDvsRAND" and x != "L_pre":
            continue
        f = out["fits"]["%s|%s" % (cname, x)] = fit(rs, x)
        print(cname, x, f["n_evo"], f["n_unevo"], "c=%.4f boot%s pFL=%.4f pSTR=%.4f b=%.5f d=%.5f boot_d%s OR=%.2f%s" % (
            f["WLS"]["c_EVO"], [round(v, 4) for v in f["WLS"]["boot95_c"]], f["WLS"]["p_perm_FL"], f["WLS"]["p_perm_strat"],
            f["WLS"]["b_X"], f["WLS_interaction"]["d_XxEVO"], [round(v, 5) for v in f["WLS_interaction"]["boot95_d"]],
            f["GLM"]["OR_EVO"], [round(v, 2) for v in f["GLM"]["OR95_wald"]]), flush=True)
json.dump(out, open(HERE / "analysis.json", "w"), indent=1, default=float)
for g, v in out["pooled"].items():
    print(g, v)
for g, v in out["pairclass"].items():
    print(g, v)
print({k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in out["matched_L_pre"].items()})
for g in G:
    xs = [r["L_pre"] for r in G[g] if r["L_pre"] is not None]
    print(g, "L_pre median", np.median(xs) if xs else None, "min/max", min(xs) if xs else None, max(xs) if xs else None,
          "no-copy", sum(r["L_pre"] is None for r in G[g]))
