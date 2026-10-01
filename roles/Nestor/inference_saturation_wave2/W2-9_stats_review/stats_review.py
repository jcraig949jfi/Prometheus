"""W2-9 statistical-method review of the NPE confirmatory verdicts. READ-ONLY on campaign files.

    python -B stats_review.py  -> stats_review.json (and a printed digest)

Recomputes every frozen decision statistic from the committed results, then runs the robustness, power, clustering and
endpoint checks described in REPORT.md. No world is run. Monte-Carlo parts use a fixed RNG seed (20260930).
"""
from __future__ import annotations

import glob
import json
import math
import pathlib
import sys

import numpy as np
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parent.parent / "campaigns"
C9X = CAMP / "c9x-explore-2026-09-24"
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
P2 = CAMP / "npe-p2-endogenous-heredity-2026-09-27"
A3 = CAMP / "npe-arc3-2026-09-28"
FR = CAMP / "npe-frontier-2026-09-30"
for bad in ("holdout_D2", "c3_holdout", "nestor_secrets"):          # boundary guard
    assert bad not in str(CAMP)
RNG = np.random.default_rng(20260930)
OUT = {}


def J(p):
    return json.loads(pathlib.Path(p).read_text())


def fisher_g(a, n1, b, n2):
    """one-sided Fisher exact, H1: arm1 rate > arm2 rate (the campaign's own hypergeometric upper tail)."""
    return float(stats.fisher_exact([[a, n1 - a], [b, n2 - b]], alternative="greater")[1])


def fisher_2s(a, n1, b, n2):
    return float(stats.fisher_exact([[a, n1 - a], [b, n2 - b]], alternative="two-sided")[1])


def fisher_mid(a, n1, b, n2):
    k = a + b
    hg = stats.hypergeom(n1 + n2, n1, k)
    return float(hg.sf(a) + 0.5 * hg.pmf(a))


def sign_p(up, down):
    n = up + down
    return float(sum(math.comb(n, x) for x in range(up, n + 1)) / 2 ** n) if n else 1.0


def min_count_fisher(n1, n2, b, alpha):
    """smallest treatment count a (control count b) with one-sided Fisher p < alpha."""
    for a in range(0, n1 + 1):
        if fisher_g(a, n1, b, n2) < alpha:
            return a
    return None


def min_sign(alpha, down=0):
    for up in range(1, 200):
        if sign_p(up, down) < alpha:
            return up
    return None


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    adj = [None] * m
    run = 0.0
    for r, i in enumerate(idx):
        run = max(run, min(1.0, (m - r) * pvals[i]))
        adj[i] = run
    return adj


def bh(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i], reverse=True)
    m = len(pvals)
    adj = [None] * m
    run = 1.0
    for r, i in enumerate(idx):
        rank = m - r
        run = min(run, pvals[i] * m / rank)
        adj[i] = run
    return adj


def cmh_exact_strat(tables, sims=200000):
    """stratified (by cluster) conditional permutation test of a 2-arm binary outcome; one-sided (arm1 > arm2).
    tables: list of (a, n1, b, n2). Statistic = sum of arm-1 successes; null = hypergeometric per stratum."""
    obs = sum(t[0] for t in tables)
    draws = np.zeros(sims, dtype=np.int64)
    for a, n1, b, n2 in tables:
        k = a + b
        if k == 0:
            continue
        draws += RNG.hypergeometric(n1, n2, k, size=sims)
    return float((draws >= obs).mean()), int(obs), float(sum(stats.hypergeom(t[1] + t[3], t[1], t[0] + t[2]).mean() for t in tables))


# ===================================================================================================== C-SELFLOC
def c_selfloc():
    d = C9X / "c_selfloc_confirm"
    res, cells = J(d / "RESULTS.json"), J(d / "CELLS.json")
    by = {}
    for r in res:
        by.setdefault(r["k"], {})[r["arm"]] = r
    n = len(cells)
    out = {"n_cells": n}
    for thr in (1, 2, 3, 5):
        l = sum(by[k]["SEED_LOC"]["max_causal_depth"] >= thr for k in by)
        o = sum(by[k]["SEED_ONLY"]["max_causal_depth"] >= thr for k in by)
        up = sum(by[k]["SEED_LOC"]["max_causal_depth"] >= thr > by[k]["SEED_ONLY"]["max_causal_depth"] for k in by)
        dn = sum(by[k]["SEED_ONLY"]["max_causal_depth"] >= thr > by[k]["SEED_LOC"]["max_causal_depth"] for k in by)
        out["depth_ge%d" % thr] = {"LOC": l, "ONLY": o, "fisher_unpaired": fisher_g(l, n, o, n), "mcnemar_exact": sign_p(up, dn),
                                   "discordant": [up, dn]}
    per = {}
    for k, c in enumerate(cells):
        ph = c["physics"]
        per.setdefault(ph, [0, 0, 0])
        per[ph][0] += 1
        per[ph][1] += by[k]["SEED_LOC"]["max_causal_depth"] >= 3
        per[ph][2] += by[k]["SEED_LOC"]["max_causal_depth"] >= 1
    out["per_physics_n_d3_d1"] = per
    # leave-one-physics-out: does the frozen rule (scaled: >=4 of 36 -> >= 4*n'/36) still pass?
    lopo = {}
    for ph in per:
        ks = [k for k, c in enumerate(cells) if c["physics"] != ph]
        l3 = sum(by[k]["SEED_LOC"]["max_causal_depth"] >= 3 for k in ks)
        o3 = sum(by[k]["SEED_ONLY"]["max_causal_depth"] >= 3 for k in ks)
        l1 = sum(by[k]["SEED_LOC"]["max_causal_depth"] >= 1 for k in ks)
        o1 = sum(by[k]["SEED_ONLY"]["max_causal_depth"] >= 1 for k in ks)
        p = fisher_g(l1, len(ks), o1, len(ks))
        lopo[ph] = {"l3": l3, "o3": o3, "p": p, "pass_unscaled_bar4": l3 >= 4 and o3 == 0 and p < 0.01}
    out["leave_one_physics_out"] = lopo
    # power under the exploratory rates (X-SELFLOC-SEEDED 15/23 d>=1, 5/23 d>=3, 0/23 both in SEED_ONLY), independent cells
    sims = 100000
    d3 = RNG.binomial(1, 5 / 23, size=(sims, n))
    # d>=1 is implied by d>=3; draw d>=1 conditional
    d1 = np.maximum(d3, RNG.binomial(1, (15 / 23 - 5 / 23) / (1 - 5 / 23), size=(sims, n)))
    l3s, l1s = d3.sum(1), d1.sum(1)
    pmap = {a: fisher_g(a, n, 0, n) for a in range(n + 1)}
    ok = (l3s >= 4) & np.array([pmap[a] < 0.01 for a in l1s])
    out["power_at_exploratory_rates_given_ONLY_zero"] = float(ok.mean())
    out["min_LOC_d1_for_p<0.01_given_ONLY_0"] = min_count_fisher(n, n, 0, 0.01)
    out["null_FPR_bound"] = "<= 0.01 (Fisher condition alone, exact test is conservative)"
    return out


# ===================================================================================================== C-ENERGY
def c_energy():
    d = C9X / "c_energy_confirm"
    res = J(d / "RESULTS.json")
    B = {r["k"]: r for r in res if r["arm"] == "BASE"}
    I = {r["k"]: r for r in res if r["arm"] == "INHERIT"}
    out = {}
    for thr in (1, 2, 3, 5):
        up = sum(I[k]["max_causal_depth"] >= thr > B[k]["max_causal_depth"] for k in B)
        dn = sum(B[k]["max_causal_depth"] >= thr > I[k]["max_causal_depth"] for k in B)
        out["depth_ge%d" % thr] = {"BASE": sum(B[k]["max_causal_depth"] >= thr for k in B),
                                   "INHERIT": sum(I[k]["max_causal_depth"] >= thr for k in B), "disc": [up, dn], "sign_p": sign_p(up, dn)}
    lopo = {}
    for pr in ("COMPETITION", "METABOLIC", "RESOURCE_GATED"):
        ks = [k for k in B if B[k]["pressure"] != pr]
        up = sum(I[k]["max_causal_depth"] >= 2 > B[k]["max_causal_depth"] for k in ks)
        dn = sum(B[k]["max_causal_depth"] >= 2 > I[k]["max_causal_depth"] for k in ks)
        i2, b2 = sum(I[k]["max_causal_depth"] >= 2 for k in ks), sum(B[k]["max_causal_depth"] >= 2 for k in ks)
        lopo[pr] = {"disc": [up, dn], "p": sign_p(up, dn), "diff": i2 - b2, "pass": i2 - b2 >= 4 and sign_p(up, dn) < 0.05}
    out["leave_one_pressure_out"] = lopo
    # worst-case single-cell deletion
    flips = 0
    for drop in B:
        ks = [k for k in B if k != drop]
        up = sum(I[k]["max_causal_depth"] >= 2 > B[k]["max_causal_depth"] for k in ks)
        dn = sum(B[k]["max_causal_depth"] >= 2 > I[k]["max_causal_depth"] for k in ks)
        diff = sum(I[k]["max_causal_depth"] >= 2 for k in ks) - sum(B[k]["max_causal_depth"] >= 2 for k in ks)
        flips += not (diff >= 4 and sign_p(up, dn) < 0.05)
    out["single_cell_deletions_that_flip"] = flips
    # how many discordant-up cells could be removed before failing
    up, dn = out["depth_ge2"]["disc"]
    k = 0
    while sign_p(up - k, dn) < 0.05 and (20 - k) - 4 >= 4:
        k += 1
    out["up_cells_removable_before_fail"] = k - 1 if k else 0
    # power at exploratory 7/19 vs 1/19 (independent marginals), n=40
    sims = 100000
    bi, bb = RNG.binomial(1, 7 / 19, (sims, 40)), RNG.binomial(1, 1 / 19, (sims, 40))
    upv, dnv = ((bi == 1) & (bb == 0)).sum(1), ((bb == 1) & (bi == 0)).sum(1)
    diffv = bi.sum(1) - bb.sum(1)
    sp = np.array([sign_p(u, d_) for u, d_ in zip(upv, dnv)])
    out["power_at_exploratory_rates"] = float(((diffv >= 4) & (sp < 0.05)).mean())
    out["null_FPR"] = "<= 0.05 (sign test level; diff>=4 is additional)"
    return out


# ===================================================================================================== C-DENSE
def c_dense():
    d = C9X / "c_dense_confirm"
    res, cells = J(d / "RESULTS.json"), J(d / "CELLS.json")
    P = {r["k"]: r for r in res if r["arm"] == "PERMISSIVE"}
    D = {r["k"]: r for r in res if r["arm"] == "PERMISSIVE_DENSE"}
    n = len(cells)
    out = {"n": n}
    for thr in (1, 2, 3, 5, 10):
        dd = sum(D[k]["replication_events"] >= thr for k in D)
        pp = sum(P[k]["replication_events"] >= thr for k in P)
        out["repl_events_ge%d" % thr] = {"DENSE": dd, "PERM": pp, "fisher": fisher_g(dd, n, pp, n),
                                          "pass_rule_shape": dd >= 10 and pp <= 1 and fisher_g(dd, n, pp, n) < 0.001}
    d2 = sum(D[k]["max_causal_depth"] >= 2 for k in D)
    out["secondary_depth_ge2"] = {"DENSE": d2, "PERM": sum(P[k]["max_causal_depth"] >= 2 for k in P),
                                  "fisher": fisher_g(d2, n, 0, n)}
    out["events_in_replicating_cells"] = sorted(D[k]["replication_events"] for k in D if D[k]["replication_events"] > 0)
    out["births_vs_events_DENSE_total"] = [sum(D[k]["births"] for k in D), sum(D[k]["replication_events"] for k in D)]
    per = {}
    for k, c in enumerate(cells):
        per.setdefault(c["physics"], [0, 0])
        per[c["physics"]][0] += 1
        per[c["physics"]][1] += D[k]["replication_events"] > 0
    out["per_physics_n_repl"] = per
    out["min_DENSE_for_p<0.001_given_PERM0"] = min_count_fisher(n, n, 0, 0.001)
    # power at exploratory 23/47 vs 0/47
    sims = 100000
    x = RNG.binomial(n, 23 / 47, sims)
    out["power_at_exploratory_rates"] = float(((x >= 10) & (np.array([fisher_g(a, n, 0, n) for a in range(n + 1)])[x] < 0.001)).mean())
    return out


# ===================================================================================================== C-ABLATE
def c_ablate():
    d = C9X / "c_ablate_confirm"
    res = J(d / "RESULTS.json")
    by = {}
    for r in res:
        by.setdefault(r["k"], {})[r["arm"]] = r
    ks = sorted(by)

    def rule(arm, kk):
        up = sum(by[k]["FULL"]["R"] and not by[k][arm]["R"] for k in kk)
        dn = sum(by[k][arm]["R"] and not by[k]["FULL"]["R"] for k in kk)
        diff = sum(by[k]["FULL"]["R"] for k in kk) - sum(by[k][arm]["R"] for k in kk)
        p = sign_p(up, dn)
        return diff, (up, dn), p, (diff >= 8 and p < 0.01)
    out = {}
    for arm, name in (("NO_LOC", "LOC_NECESSARY"), ("NO_SEARCH", "SEARCH_NECESSARY")):
        diff, disc, p, ok = rule(arm, ks)
        flips = [k for k in ks if rule(arm, [x for x in ks if x != k])[3] != ok]
        out[name] = {"diff": diff, "disc": disc, "p": p, "verdict_ok": ok, "single_cell_deletions_that_flip": len(flips),
                     "p_if_one_up_cell_removed": sign_p(disc[0] - 1, disc[1]),
                     "p_if_one_concordant_success_is_lost": None}
    # Holm within the experiment's 3 rules (ENERGY p = 1)
    ps = [out["LOC_NECESSARY"]["p"], out["SEARCH_NECESSARY"]["p"], 1.0]
    out["holm_within_experiment"] = holm(ps)
    # SEARCH at bar thresholds
    out["SEARCH_min_up_for_p<0.01_with_down=1"] = min_sign(0.01, 1)
    # ENERGY_FOR_DEPTH eligibility given observed FULL D2 = 3, and power at exploratory rates
    fullD2 = sum(by[k]["FULL"]["D2"] for k in ks)
    out["ENERGY_FOR_DEPTH"] = {"FULL_D2_observed": fullD2, "best_case_p_given_FULL_D2": sign_p(fullD2, 0),
                               "eligible_given_observed_FULL": sign_p(fullD2, 0) < 0.05,
                               "min_up_for_sign_p<0.05_with_down0": min_sign(0.05, 0)}
    # power at exploratory X-DENSE-ABLATE rates over n=40 (FULL D2 11/47, NO_ENERGY D2 6/47; R 27/47 vs 26/47)
    sims = 100000
    f, e = RNG.binomial(1, 11 / 47, (sims, 40)), RNG.binomial(1, 6 / 47, (sims, 40))
    fr, er = RNG.binomial(40, 27 / 47, sims), RNG.binomial(40, 26 / 47, sims)
    up, dn = ((f == 1) & (e == 0)).sum(1), ((e == 1) & (f == 0)).sum(1)
    sp = np.array([sign_p(u, d_) for u, d_ in zip(up, dn)])
    out["ENERGY_FOR_DEPTH"]["power_at_exploratory_rates_indep"] = float(((np.abs(fr - er) <= 4) & (f.sum(1) - e.sum(1) >= 3) & (sp < 0.05)).mean())
    # SEARCH power at exploratory 27/47 vs 5/47 (indep)
    f, s = RNG.binomial(1, 27 / 47, (sims, 40)), RNG.binomial(1, 5 / 47, (sims, 40))
    up, dn = ((f == 1) & (s == 0)).sum(1), ((s == 1) & (f == 0)).sum(1)
    sp = np.array([sign_p(u, d_) for u, d_ in zip(up, dn)])
    out["SEARCH_NECESSARY"]["power_at_exploratory_rates_indep"] = float(((f.sum(1) - s.sum(1) >= 8) & (sp < 0.01)).mean())
    out["SEARCH_NECESSARY"]["exploratory_vs_confirm_drop"] = {"explore": "27/47 -> 5/47 (81% drop)", "confirm": "15/40 -> 6/40 (60% drop)"}
    return out


# ===================================================================================================== splice / runaway family
def splice_family():
    run = J(C9X / "c_runaway_confirm" / "RESULTS.json")
    cm = J(C9X / "c_critical_mass" / "RESULTS.json")
    nr = J(C9X / "c_norecomb_confirm" / "RESULTS.json")
    at = J(C9X / "c_atomic" / "RESULTS.json")
    out = {}
    N = 150
    R = {a: [r["depth"] for r in run if r["arm"] == a] for a in ("BASE", "NO_RECOMB")}
    thr_tab = {}
    for t in (5, 10, 15, 20, 30, 50, 100):
        a, b = sum(x >= t for x in R["NO_RECOMB"]), sum(x >= t for x in R["BASE"])
        thr_tab[t] = {"NO_RECOMB": a, "BASE": b, "fisher": fisher_g(a, N, b, N), "mid_p": fisher_mid(a, N, b, N),
                      "two_sided": fisher_2s(a, N, b, N), "frozen_rule_shape_pass": a >= 4 and b == 0 and fisher_g(a, N, b, N) < 0.01}
    out["C_RUNAWAY_thresholds"] = thr_tab
    out["C_RUNAWAY_min_count_for_p<0.01_given_BASE0"] = min_count_fisher(N, N, 0, 0.01)
    out["C_RUNAWAY_NO_RECOMB_depths_ge20"] = sorted(x for x in R["NO_RECOMB"] if x >= 20)
    out["C_RUNAWAY_depth_ge1"] = {a: sum(x >= 1 for x in R[a]) for a in R}
    # the same physical condition (7ae3, arm-B, splice OFF, k=1, plain write-back) appears in 4 seed blocks
    blocks = {
        "C-RUNAWAY NO_RECOMB (9_990_500+)": R["NO_RECOMB"],
        "C-CRITICAL-MASS k=1 (9_996_000+)": [r["depth"] for r in cm if r["k"] == 1],
        "C-ATOMIC C1 BASE (12_000_000+)": [r["depth"] for r in at if r["specimen"].startswith("7ae3") and r["arm"] == "BASE"],
        "C-NORECOMB 7ae3 NO_RECOMB (9_985_000+)": [r["depth"] for r in nr if r["spec"].startswith("7ae3") and r["arm"] == "NO_RECOMB"],
    }
    tab = {k: {"n": len(v), "ge20": sum(x >= 20 for x in v), "ge5": sum(x >= 5 for x in v)} for k, v in blocks.items()}
    out["splice_off_k1_blocks"] = tab
    for key in ("ge20", "ge5"):
        obs = np.array([[t[key], t["n"] - t[key]] for t in tab.values()])
        chi2, p, dof, _ = stats.chi2_contingency(obs)
        out["heterogeneity_" + key] = {"chi2": round(float(chi2), 3), "p": float(p), "dof": int(dof),
                                       "pooled": [int(obs[:, 0].sum()), int(obs.sum())]}
    # splice ON blocks (7ae3, k=1, plain)
    on = {"C-RUNAWAY BASE": R["BASE"], "C-NORECOMB 7ae3 BASE": [r["depth"] for r in nr if r["spec"].startswith("7ae3") and r["arm"] == "BASE"]}
    out["splice_on_blocks"] = {k: {"n": len(v), "ge5": sum(x >= 5 for x in v), "ge20": sum(x >= 20 for x in v), "max": max(v)} for k, v in on.items()}
    a, b = out["splice_on_blocks"]["C-NORECOMB 7ae3 BASE"]["ge5"], out["splice_on_blocks"]["C-RUNAWAY BASE"]["ge5"]
    out["splice_on_ge5_block_heterogeneity_fisher_2s"] = fisher_2s(a, 24, b, 150)
    # power of C-RUNAWAY's rule at the pooled splice-off runaway rate of the OTHER blocks (excluding C-RUNAWAY itself)
    others = [v for k, v in blocks.items() if not k.startswith("C-RUNAWAY")]
    k_o, n_o = sum(sum(x >= 20 for x in v) for v in others), sum(len(v) for v in others)
    rate_o = k_o / n_o
    sims = 200000
    for lab, r_off in (("pooled_other_blocks_%d_of_%d" % (k_o, n_o), rate_o), ("exploratory_3_of_64", 3 / 64),
                       ("all_blocks_pooled", (k_o + 7) / (n_o + 150))):
        x = RNG.binomial(N, r_off, sims)
        out.setdefault("C_RUNAWAY_power_given_BASE_rate_0", {})[lab] = {"rate": round(r_off, 4), "P_confirm": float((x >= 7).mean())}
    # C-NORECOMB eligibility: pooled n=48, c2a8 never reached d>=5 in either arm
    out["C_NORECOMB_min_count_for_rule_given_BASE0"] = max(min_count_fisher(48, 48, 0, 0.01), math.ceil(0.15 * 48))
    out["C_NORECOMB_min_count_for_rule_given_BASE5"] = max(min_count_fisher(48, 48, 5, 0.01), 5 + math.ceil(0.15 * 48))
    for lab, (pa, pb) in {"exploratory 3/16 vs 0/16 on 7ae3 only, c2a8 at 0": (3 / 16 / 2, 0.0),
                          "exploratory, c2a8 behaving like 7ae3": (3 / 16, 0.0)}.items():
        xa, xb = RNG.binomial(48, pa, sims), RNG.binomial(48, pb, sims)
        pm = np.array([[fisher_g(i, 48, j, 48) if i + j > 0 else 1 for j in range(10)] for i in range(49)])
        ok = ((xa - xb) / 48 >= 0.15) & (pm[xa, np.minimum(xb, 9)] < 0.01)
        out.setdefault("C_NORECOMB_power", {})[lab] = float(ok.mean())
    # C-CRITICAL-MASS
    k1 = [r["depth"] for r in cm if r["k"] == 1]
    k4 = [r["depth"] for r in cm if r["k"] == 4]
    cmo = {}
    for t in (3, 5, 10, 20, 50):
        a, b = sum(x >= t for x in k4), sum(x >= t for x in k1)
        p1 = b / 80
        cmo[t] = {"k4": a, "k1": b, "fisher": fisher_g(a, 80, b, 80), "indep_tickets_expected_k4": round(80 * (1 - (1 - p1) ** 4), 1)}
    out["C_CRITICAL_MASS_thresholds"] = cmo
    # P(CONFIRM) under the pure independent-ticket model (no interaction) for a range of single-founder rates
    pc = {}
    pmat = {}
    for p1 in (0.0625, 0.08, 0.108, 0.15):
        p4 = 1 - (1 - p1) ** 4
        a, b = RNG.binomial(80, p4, sims), RNG.binomial(80, p1, sims)
        ok = []
        for i, j in zip(a[:20000], b[:20000]):
            key = (int(i), int(j))
            if key not in pmat:
                pmat[key] = fisher_g(*key[:1], 80, key[1], 80)
            ok.append((i - j) / 80 >= 0.20 and pmat[key] < 0.001)
        pc[str(p1)] = {"p4_indep": round(p4, 3), "P_confirm": float(np.mean(ok))}
    out["C_CRITICAL_MASS_P_confirm_under_independent_tickets"] = pc
    # observed k4 vs independent-ticket expectation with p1 uncertainty (parametric bootstrap on p1 ~ Beta(6,76))
    p1s = RNG.beta(5 + 1, 75 + 1, sims)
    x4 = RNG.binomial(80, 1 - (1 - p1s) ** 4)
    out["C_CRITICAL_MASS_superadditivity_p_bayes_bootstrap"] = float((x4 >= sum(x >= 5 for x in k4)).mean())
    return out


# ===================================================================================================== C-ATOMIC
def c_atomic():
    at = J(C9X / "c_atomic" / "RESULTS.json")
    p1 = [r for r in at if r["specimen"].startswith("7ae3")]
    out = {}
    for t in (5, 10, 20, 50, 100):
        a = sum(r["depth"] >= t for r in p1 if r["arm"] == "ATOMIC")
        b = sum(r["depth"] >= t for r in p1 if r["arm"] == "BASE")
        out["C1_ge%d" % t] = {"ATOMIC": a, "BASE": b, "fisher": fisher_g(a, 80, b, 80), "diff": (a - b) / 80}
    p2 = [r for r in at if not r["specimen"].startswith("7ae3")]
    specs = sorted({r["specimen"] for r in p2})
    capable = [s for s in specs if any(r["depth"] >= 5 for r in p2 if r["specimen"] == s)]
    out["C2_specimens_with_any_depth_ge5_either_arm"] = len(capable)
    out["C2_specimens_with_any_depth_ge20_either_arm"] = sum(any(r["depth"] >= 20 for r in p2 if r["specimen"] == s) for s in specs)
    out["C2_eligibility_note"] = ("needs >= 4 specimens with more ATOMIC than BASE runaways; only %d of 15 specimens ever reached "
                                  "depth >= 5 in either arm" % len(capable))
    out["C2_min_pooled_ATOMIC_for_p<0.001_given_BASE0"] = min_count_fisher(120, 120, 0, 0.001)
    return out


# ===================================================================================================== C-SWAP-ACQUIRE
def c_swap():
    res = J(C9X / "c_swap_acquire" / "RESULTS.json")

    def hit(r, thr=20, anc=0.9):
        return r["depth"] >= thr and r["anc0_share"] >= anc
    out = {}
    for thr in (10, 20, 30):
        for anc in (0.5, 0.9):
            g = sum(hit(r, thr, anc) for r in res if r["arm"] == "GENOME")
            rr = sum(hit(r, thr, anc) for r in res if r["arm"] == "RANDOM")
            out["d%d_anc%.1f" % (thr, anc)] = {"GENOME": g, "RANDOM": rr, "fisher": fisher_g(g, 240, rr, 240)}
    g = out["d20_anc0.9"]["GENOME"]
    out["alpha_needed_to_confirm"] = out["d20_anc0.9"]["fisher"]
    out["min_GENOME_for_p<0.001_given_RANDOM0"] = min_count_fisher(240, 240, 0, 0.001)
    per = {}
    for sp in ("9cba", "e160"):
        a = sum(hit(r) for r in res if r["arm"] == "GENOME" and r["specimen"].startswith(sp))
        per[sp] = {"GENOME": a, "fisher_vs_0_of_120": fisher_g(a, 120, 0, 120)}
    out["per_cell"] = per
    out["founder_rooted_ge20_GENOME"] = sum(r["founder_depth"] >= 20 for r in res if r["arm"] == "GENOME")
    sims = 200000
    out["power_at_rates"] = {str(r): float((RNG.binomial(240, r, sims) >= 10).mean()) for r in (0.0375, 0.05, 0.125)}
    return out


# ===================================================================================================== C-CORE
def c_core():
    res = J(C9X / "c_core" / "RESULTS.json")
    run = [r for r in res if r["depth"] >= 20 and r["anc0_share"] >= 0.9]
    CORE = (23, 24, 52, 53)

    def classify(r, ft=0.8, st=0.2, core=CORE):
        f = r["freq"]
        c4 = all(p < len(f) and f[p] >= ft for p in core)
        others = [f[p] for p in range(len(f)) if p not in core]
        sp = (sum(x >= ft for x in others) < st * len(others)) if others else False
        return c4 and sp
    out = {"runaways": len(run)}
    grid = {}
    for ft in (0.6, 0.7, 0.75, 0.8, 0.85, 0.9):
        for st in (0.1, 0.15, 0.2, 0.25):
            k = sum(classify(r, ft, st) for r in run)
            grid["f%.2f_s%.2f" % (ft, st)] = [k, len(run), k >= 0.6 * len(run)]
    out["threshold_grid"] = grid
    k = sum(classify(r) for r in run)
    out["observed"] = [k, len(run), round(k / len(run), 4), "bar", 0.6 * len(run)]
    out["wilson95"] = wilson(k, len(run))
    out["P_theta_ge_0.6_beta_posterior_uniform_prior"] = float(stats.beta(k + 1, len(run) - k + 1).sf(0.6))
    out["qualifying_runs_removable_before_fail"] = next(j for j in range(k + 1) if (k - j) < 0.6 * (len(run) - j)) - 1
    out["classification_flips_at_fixed_n_to_fail"] = k - math.ceil(0.6 * len(run) - 1e-9) + 1
    # without position 53 (the weakest core byte), and with the 3 best-conserved non-core positions as alternative "cores"
    out["core_23_24_52_only"] = sum(classify(r, core=(23, 24, 52)) for r in run)
    # permutation-style chance check: how often would 4 random positions all have freq >= 0.8 in a runaway?
    cnt = 0
    tot = 0
    for r in run:
        f = r["freq"]
        hi = sum(x >= 0.8 for x in f)
        L = len(f)
        cnt += math.comb(hi, 4) / math.comb(L, 4) if hi >= 4 else 0
        tot += 1
    out["mean_P_4_random_positions_all_conserved"] = cnt / tot
    out["eligibility_prior"] = {"runaways_expected": "~37 (C-ATOMIC 46/80)", "observed_runaways": len(run),
                                "P_pass_if_true_rate_0.6_at_n27": float(stats.binom(27, 0.6).sf(math.ceil(0.6 * 27) - 1)),
                                "P_pass_if_true_rate_0.8_at_n27": float(stats.binom(27, 0.8).sf(math.ceil(0.6 * 27) - 1))}
    return out


# ===================================================================================================== C9-H1R
def c9_h1r():
    res = J(C9X / "c9_h1r" / "RESULTS.json")
    by = {}
    for r in res:
        by.setdefault(r["seed"], {})[r["arm"]] = r["held_max_final"] or 0.0
    seeds = sorted(by)
    A = {a: np.array([by[s][a] for s in seeds]) for a in ("gate_off_cost_vm", "gate_on_cost_vm", "gate_off_cost_free", "gate_on_cost_free")}

    def MI(ix):
        m = {a: A[a][ix].mean() for a in A}
        M = ((m["gate_on_cost_vm"] + m["gate_on_cost_free"]) - (m["gate_off_cost_vm"] + m["gate_off_cost_free"])) / 2
        I = (m["gate_on_cost_free"] - m["gate_off_cost_free"]) - (m["gate_on_cost_vm"] - m["gate_off_cost_vm"])
        return M, I
    M0, I0 = MI(np.arange(len(seeds)))
    sims = 20000
    bs = np.array([MI(RNG.integers(0, len(seeds), len(seeds))) for _ in range(sims)])
    out = {"M": round(M0, 4), "I": round(I0, 4),
           "M_boot95": [round(float(x), 4) for x in np.percentile(bs[:, 0], [2.5, 97.5])],
           "I_boot95": [round(float(x), 4) for x in np.percentile(bs[:, 1], [2.5, 97.5])],
           "P_boot_|I|>=0.15": float((np.abs(bs[:, 1]) >= 0.15).mean()),
           "P_boot_|M|>=0.15": float((np.abs(bs[:, 0]) >= 0.15).mean()),
           "FREE_arms_identical_per_seed": int(sum(A["gate_off_cost_free"] == A["gate_on_cost_free"])),
           "gated_vm_all_zero": int(sum(A["gate_on_cost_vm"] == 0)),
           "ungated_vm_value_counts": {str(k): int(v) for k, v in zip(*np.unique(A["gate_off_cost_vm"], return_counts=True))},
           "I_equals_ungated_vm_mean": bool(abs(I0 - A["gate_off_cost_vm"].mean()) < 1e-9)}
    # sign-flip permutation test of I (per-seed interaction contrast), two-sided
    c = (A["gate_on_cost_free"] - A["gate_off_cost_free"]) - (A["gate_on_cost_vm"] - A["gate_off_cost_vm"])
    signs = RNG.choice([-1, 1], size=(sims, len(c)))
    perm = np.abs((signs * c).mean(1))
    out["I_signflip_p_two_sided"] = float((perm >= abs(c.mean())).mean())
    out["I_nonzero_seeds"] = int((c != 0).sum())
    out["M_signflip_p_two_sided"] = float((np.abs((signs * ((A["gate_on_cost_vm"] + A["gate_on_cost_free"] - A["gate_off_cost_vm"] - A["gate_off_cost_free"]) / 2)).mean(1))
                                           >= abs(M0)).mean())
    return out


# ===================================================================================================== C-DENSE-COPY
def c_dense_copy():
    fs = sorted(glob.glob(str(W1 / "c_dense_copy" / "results" / "*.json")))
    res = [J(f) for f in fs]
    out = {}

    def l2(r):
        return any(c["L2"] > 0 for c in r["checkpoints"])
    for cell in ("7ae3", "ffa6"):
        a = sum(l2(r) for r in res if r["arm"] == "DENSE_COPY" and r["cell"] == cell)
        b = sum(l2(r) for r in res if r["arm"] == "PLAIN" and r["cell"] == cell)
        out[cell] = {"DENSE": a, "PLAIN": b, "fisher_of_32": fisher_g(a, 32, b, 32)}
    tabs = [(out[c]["DENSE"], 32, out[c]["PLAIN"], 32) for c in ("7ae3", "ffa6")]
    out["stratified_perm_p"] = cmh_exact_strat(tabs, 100000)[0]
    for need in (2, 3):
        a = sum(sum(c["L2"] > 0 for c in r["checkpoints"]) >= need for r in res if r["arm"] == "DENSE_COPY")
        b = sum(sum(c["L2"] > 0 for c in r["checkpoints"]) >= need for r in res if r["arm"] == "PLAIN")
        out["L2_at_>=%d_checkpoints" % need] = {"DENSE": a, "PLAIN": b, "fisher": fisher_g(a, 64, b, 64)}
    a = sum(r["checkpoints"][-1]["L2"] > 0 for r in res if r["arm"] == "DENSE_COPY")
    b = sum(r["checkpoints"][-1]["L2"] > 0 for r in res if r["arm"] == "PLAIN")
    out["L2_at_final_checkpoint"] = {"DENSE": a, "PLAIN": b, "fisher": fisher_g(a, 64, b, 64)}
    return out


# ===================================================================================================== C-STATELESS (+ FFA6)
def c_stateless(sub):
    d = W1 / sub
    res = [J(f) for s in ("dense", "stateless") for f in sorted(glob.glob(str(d / s / "results" / "*.json")))]

    def l2(r):
        return any(c["L2"] > 0 for c in r["checkpoints"])
    out = {}
    cells = sorted({r["cell"] for r in res})
    for arm in ("DENSE", "STATELESS"):
        rs = [r for r in res if r["arm"] == arm]
        out[arm] = {"n": len(rs), "L2": sum(l2(r) for r in rs), "est_given_L2": sum(l2(r) and r["depth"] >= 20 for r in rs),
                    "runaway_all": sum(r["depth"] >= 20 for r in rs), "runaway_without_L2": sum((not l2(r)) and r["depth"] >= 20 for r in rs)}
    S, D = out["STATELESS"], out["DENSE"]
    out["frozen_conditional_fisher"] = fisher_g(S["est_given_L2"], S["L2"], D["est_given_L2"], D["L2"])
    out["unconditional_runaway_fisher"] = fisher_g(S["runaway_all"], S["n"], D["runaway_all"], D["n"])
    out["L2_rate_fisher_2s"] = fisher_2s(S["L2"], S["n"], D["L2"], D["n"])
    tabs = []
    per = {}
    for c in cells:
        s = [r for r in res if r["arm"] == "STATELESS" and r["cell"] == c and l2(r)]
        dd = [r for r in res if r["arm"] == "DENSE" and r["cell"] == c and l2(r)]
        tabs.append((sum(r["depth"] >= 20 for r in s), len(s), sum(r["depth"] >= 20 for r in dd), len(dd)))
        per[c] = tabs[-1]
    out["per_cell_(S_est,S_L2,D_est,D_L2)"] = per
    if len(cells) > 1:
        out["cell_stratified_perm_p_conditional"] = cmh_exact_strat(tabs, 100000)[0]
    # leave-one-run-out on the conditional rule
    flips = 0
    for i in range(len(res)):
        rr = res[:i] + res[i + 1:]
        Sx = [r for r in rr if r["arm"] == "STATELESS" and l2(r)]
        Dx = [r for r in rr if r["arm"] == "DENSE" and l2(r)]
        a, b = sum(r["depth"] >= 20 for r in Sx), sum(r["depth"] >= 20 for r in Dx)
        ok = len(Sx) >= 15 and len(Dx) >= 15 and a / len(Sx) - b / len(Dx) >= 0.25 and fisher_g(a, len(Sx), b, len(Dx)) < 0.001
        flips += ok != (out["frozen_conditional_fisher"] < 0.001 and S["est_given_L2"] / S["L2"] - D["est_given_L2"] / D["L2"] >= 0.25)
    out["single_run_deletions_that_flip"] = flips
    # paired-by-seed view (seeds are shared; random populations, no implant -> streams equal until first divergence)
    seeds = sorted({(r["cell"], r["seed"]) for r in res})
    m = {(r["cell"], r["seed"], r["arm"]): r for r in res}
    up = sum(m[(c, s, "STATELESS")]["depth"] >= 20 and not m[(c, s, "DENSE")]["depth"] >= 20 for c, s in seeds)
    dn = sum(m[(c, s, "DENSE")]["depth"] >= 20 and not m[(c, s, "STATELESS")]["depth"] >= 20 for c, s in seeds)
    out["paired_runaway_mcnemar"] = {"disc": [up, dn], "p": sign_p(up, dn)}
    both_l2 = sum(l2(m[(c, s, "STATELESS")]) and l2(m[(c, s, "DENSE")]) for c, s in seeds)
    out["seeds_with_L2_in_both_arms"] = both_l2
    return out


# ===================================================================================================== C-ZERO-SPECIFIC
def c_zero():
    res = [J(f) for f in sorted(glob.glob(str(P2 / "c_zero_specific" / "results" / "*.json")))]
    out = {}
    donors = sorted({r["donor"] for r in res})
    per = {d: {a: sum(bool(r["S5"]) for r in res if r["donor"] == d and r["policy"] == a) for a in ("ZERO", "CONST", "CARRY", "RANDOM")}
           for d in donors}
    out["per_donor_S5_of_3"] = per
    z = np.array([per[d]["ZERO"] for d in donors])
    c = np.array([per[d]["CONST"] for d in donors])
    out["donors_ZERO>CONST"] = int((z > c).sum())
    out["donors_ZERO<CONST"] = int((z < c).sum())
    out["donor_sign_test_p"] = sign_p(int((z > c).sum()), int((z < c).sum()))
    out["donor_wilcoxon_p_one_sided"] = float(stats.wilcoxon(z, c, alternative="greater", zero_method="wilcox").pvalue)
    tabs = [(int(per[d]["ZERO"]), 3, int(per[d]["CONST"]), 3) for d in donors]
    out["donor_stratified_perm_p"] = cmh_exact_strat(tabs, 200000)[0]
    # cluster bootstrap over donors for the share difference
    sims = 20000
    idx = RNG.integers(0, len(donors), (sims, len(donors)))
    diffs = (z[idx].sum(1) - c[idx].sum(1)) / (3 * len(donors))
    out["cluster_boot_diff95"] = [round(float(x), 4) for x in np.percentile(diffs, [2.5, 97.5])]
    out["cluster_boot_P_diff<0.25"] = float((diffs < 0.25).mean())
    # leave-one-donor-out
    lodo = []
    for i, d in enumerate(donors):
        zz, cc = z.sum() - z[i], c.sum() - c[i]
        n = 3 * (len(donors) - 1)
        lodo.append(fisher_g(int(zz), n, int(cc), n))
    out["leave_one_donor_out_max_p"] = max(lodo)
    # design effect: ICC of ZERO-arm S5 by donor (ANOVA estimator)
    y = np.array([[int(bool(r["S5"])) for r in res if r["donor"] == d and r["policy"] == "ZERO"] for d in donors], float)
    msb = 3 * ((y.mean(1) - y.mean()) ** 2).sum() / (len(donors) - 1)
    msw = ((y - y.mean(1, keepdims=True)) ** 2).sum() / (len(donors) * 2)
    icc = (msb - msw) / (msb + 2 * msw) if (msb + 2 * msw) > 0 else 0
    out["ICC_ZERO_by_donor"] = round(float(icc), 3)
    out["design_effect_(1+(m-1)ICC)"] = round(float(1 + 2 * icc), 3)
    out["origin_split"] = {o: {a: sum(bool(r["S5"]) for r in res if r["origin"] == o and r["policy"] == a) for a in ("ZERO", "CONST")}
                           for o in ("7ae3", "ffa6")}
    out["frozen_fisher_recomputed"] = fisher_g(int(z.sum()), 48, int(c.sum()), 48)
    out["depth_ge20_regardless_of_anc0"] = {a: sum(int(r["depth"]) >= 20 for r in res if r["policy"] == a) for a in ("ZERO", "CONST", "CARRY", "RANDOM")}
    return out


# ===================================================================================================== C-A3-INTERNALIZE
def c_a3():
    res = [J(f) for f in sorted(glob.glob(str(A3 / "c_a3_internalize" / "results" / "*.json")))]

    def d0_not(r):
        return bool(r["d0_free"]) and not any(r["d0_free"])

    def ev(r, last_rule="last_free", min_free=1, min_share=0.0, final=False, min_cps=1):
        cps = r["checkpoints"]
        if not d0_not(r):
            return False
        freecps = [c for c in cps if c["free"] >= min_free and (c["free"] / c["competent"] if c["competent"] else 0) >= min_share]
        if len(freecps) < min_cps:
            return False
        last = cps[-1] if final else (freecps[-1] if freecps else None)
        if last is None or last["free"] < min_free:
            return False
        return last["free_in_L"] >= 0.8 * last["free"] and last["L_share"] >= 0.5
    out = {"frozen_events": sum(ev(r) for r in res)}
    out["variants"] = {
        "free>=2_genomes": sum(ev(r, min_free=2) for r in res),
        "free>=5_genomes": sum(ev(r, min_free=5) for r in res),
        "free_share_of_competent>=0.25": sum(ev(r, min_share=0.25) for r in res),
        "free_share_of_competent>=0.5": sum(ev(r, min_share=0.5) for r in res),
        "held_at_final_checkpoint": sum(ev(r, final=True) for r in res),
        "free_at_>=2_checkpoints": sum(ev(r, min_cps=2) for r in res),
        "free_at_>=3_checkpoints": sum(ev(r, min_cps=3) for r in res),
    }
    rows = []
    for r in res:
        if ev(r):
            cps = r["checkpoints"]
            fc = [c for c in cps if c["free"] > 0]
            rows.append({"run": "%s %s" % (r["cell"], r["seed"]), "n_free_cps": len(fc), "max_free": max(c["free"] for c in fc),
                         "max_free_share": round(max(c["free"] / c["competent"] for c in fc if c["competent"]), 3),
                         "last_free": fc[-1]["free"], "last_competent": fc[-1]["competent"], "final_free": cps[-1]["free"],
                         "free_series": [c["free"] for c in cps if c["epoch"] >= fc[0]["epoch"]]})
    out["event_rows"] = rows
    # null calibration: the instrument has no control arm. Count the eligible denominator (D0 not free and L ever >= 0.5)
    elig = [r for r in res if d0_not(r) and any(c["L_share"] >= 0.5 for c in r["checkpoints"])]
    out["eligible_L_ever_ge0.5"] = len(elig)
    out["events_among_eligible"] = sum(ev(r) for r in elig)
    # flicker statistic: among all runs with any free genome, fraction of free-bearing checkpoints followed by a 0
    fl, tot = 0, 0
    for r in res:
        cps = r["checkpoints"]
        for a, b in zip(cps, cps[1:]):
            if a["free"] > 0:
                tot += 1
                fl += b["free"] == 0
    out["free_checkpoint_followed_by_zero"] = [fl, tot]
    # cell heterogeneity of events per donor run
    for c in ("7ae3", "ffa6"):
        out["donor_runs_" + c] = sum(r["d0_epoch"] is not None for r in res if r["cell"] == c)
        out["events_" + c] = sum(ev(r) for r in res if r["cell"] == c)
    out["cell_fisher_2s"] = fisher_2s(out["events_ffa6"], out["donor_runs_ffa6"], out["events_7ae3"], out["donor_runs_7ae3"])
    out["poisson_P_ge4_at_explore_rate"] = float(stats.poisson(144 * 3 / 96).sf(3))
    out["poisson_P_ge4_at_half_explore_rate"] = float(stats.poisson(144 * 1.5 / 96).sf(3))
    return out


# ===================================================================================================== X-MAT-INTERNALIZE
def x_mat():
    v = J(FR / "x_mat_internalize" / "VERDICT.json")
    rows = [r for r in v["rows"] if r["group"] == "EVENT"]
    out = {"rows": []}
    worst = []
    for r in rows:
        res = J(FR / "x_mat_internalize" / "results" / ("%s_%d.json" % (r["cell"], r["seed"])))
        ep = r["endpoint"]["epoch"]
        tg = {t["epoch"]: t for t in res["tags"]}
        t = tg[ep]
        fl = t["free_L"]
        att = fl["ENDO"] + fl["XENO"]
        X = fl["XENO"] / att if att else None
        Xw = (fl["XENO"] + fl["MUT"]) / (att + fl["MUT"]) if att + fl["MUT"] else None
        Xw2 = (fl["XENO"] + fl["MUT"] + fl["OTHER"]) / fl["bytes"] if fl["bytes"] else None
        Lsh = t["L"]["orgs"] / t["all"]["orgs"] if t["all"]["orgs"] else None
        cps = res["record"]["checkpoints"]
        first = next(c for c in cps if c["free"] > 0)
        tf = tg[first["epoch"]]["free_L"]
        attf = tf["ENDO"] + tf["XENO"]
        # max XENO share of L over the trajectory
        mx = max(((x["L"]["XENO"] / (x["L"]["ENDO"] + x["L"]["XENO"])) if (x["L"]["ENDO"] + x["L"]["XENO"]) else 0, x["epoch"]) for x in res["tags"])
        row = {"run": "%s %d" % (r["cell"], r["seed"]), "epoch": ep, "free_L_orgs": fl["orgs"], "X": round(X, 4) if X is not None else None,
               "X_if_MUT_is_XENO": round(Xw, 4) if Xw is not None else None,
               "X_if_MUT_and_OTHER_are_XENO": round(Xw2, 4) if Xw2 is not None else None,
               "L_share_orgs_at_endpoint": round(Lsh, 4) if Lsh is not None else None,
               "X_at_first_free_cp": round(tf["XENO"] / attf, 4) if attf else None, "first_free_epoch": first["epoch"],
               "max_XENO_share_in_L_(value,epoch)": [round(mx[0], 4), mx[1]]}
        out["rows"].append(row)
        worst.append(Xw)
    out["ENDOGENOUS_count_under_worst_case_MUT_as_XENO"] = sum(x is not None and x <= 0.2 for x in worst)
    out["TRANSPLANTED_count_under_worst_case"] = sum(x is not None and x >= 0.5 for x in worst)
    out["events_with_L_share_1.0_at_endpoint"] = sum(r["L_share_orgs_at_endpoint"] == 1.0 for r in out["rows"])
    return out


# ===================================================================================================== multiplicity
def multiplicity(o):
    fam = [
        ("C-SELFLOC", 1.5743855399988262e-10, 0.01, "CONFIRMED"),
        ("C-ENERGY", 7.2479248046875e-05, 0.05, "CONFIRMED"),
        ("C-DENSE", 3.818418688334954e-05, 0.001, "CONFIRMED"),
        ("C-ABLATE LOC", 6.103515625e-05, 0.01, "CONFIRMED"),
        ("C-ABLATE SEARCH", 0.005859375, 0.01, "CONFIRMED"),
        ("C-ABLATE ENERGY_FOR_DEPTH", 1.0, 0.05, "NOT_CONFIRMED"),
        ("C-NORECOMB", 0.6299647209439876, 0.01, "NOT_CONFIRMED"),
        ("C-RUNAWAY", 0.007273002114564385, 0.01, "CONFIRMED"),
        ("C-CRITICAL-MASS", 7.964166050817117e-11, 0.001, "CONFIRMED"),
        ("C-ATOMIC C1", 4.3525251992963394e-17, 0.001, "CONFIRMED"),
        ("C-ATOMIC C2", 0.5, 0.001, "NOT_CONFIRMED"),
        ("C-SWAP-ACQUIRE", 0.001809543403312012, 0.001, "NOT_CONFIRMED"),
        ("C-DENSE-COPY", 1.0171264457572148e-14, 0.001, "CONFIRMED"),
        ("C-STATELESS", 0.012202679231868602, 0.001, "NOT_CONFIRMED"),
        ("C-STATELESS-FFA6", 3.2683982483484046e-05, 0.001, "CONFIRMED"),
        ("C-ZERO-SPECIFIC", 2.4383205059153568e-08, 0.001, "CONFIRMED"),
        ("C9-H1R (sign-flip p for I, computed here)", o["C9-H1R"]["I_signflip_p_two_sided"], None, "COST_INTERACTION_ONLY"),
    ]
    ps = [f[1] for f in fam]
    ho, b = holm(ps), bh(ps)
    rows = []
    for (name, p, a, v), h, q in zip(fam, ho, b):
        rows.append({"test": name, "p": p, "own_alpha": a, "verdict": v, "holm_adj": h, "bh_q": q,
                     "survives_holm_0.05": h < 0.05, "survives_holm_0.01": h < 0.01, "survives_bh_0.05": q < 0.05})
    exp_fp = sum(f[2] for f in fam if f[2])
    return {"family": rows, "m": len(fam), "sum_of_alphas_(expected_false_confirms_if_all_nulls_true)": exp_fp,
            "bonferroni_0.05_threshold": 0.05 / len(fam),
            "non_p_rules": ["C-CORE (proportion bar 0.6, 17/27)", "C-A3-INTERNALIZE (count bar >= 4, 8/144)",
                            "X-MAT-INTERNALIZE (classification >= 6/8)"],
            "claim_level_retests": {"splice limits heredity": ["C-NORECOMB p=0.63 (fail)", "C-RUNAWAY p=0.0073 (pass)"],
                                    "state persistence limits establishment": ["C-STATELESS p=0.012 (fail)", "C-STATELESS-FFA6 p=3.3e-5 (pass)"],
                                    "7ae3 genome enables runaway beyond own cell": ["C-ATOMIC C2 (fail)", "C-SWAP-ACQUIRE p=0.0018 (fail)"]}}


def main():
    OUT["C-SELFLOC"] = c_selfloc()
    OUT["C-ENERGY"] = c_energy()
    OUT["C-DENSE"] = c_dense()
    OUT["C-ABLATE"] = c_ablate()
    OUT["SPLICE_FAMILY (C-RUNAWAY, C-NORECOMB, C-CRITICAL-MASS)"] = splice_family()
    OUT["C-ATOMIC"] = c_atomic()
    OUT["C-SWAP-ACQUIRE"] = c_swap()
    OUT["C-CORE"] = c_core()
    OUT["C9-H1R"] = c9_h1r()
    OUT["C-DENSE-COPY"] = c_dense_copy()
    OUT["C-STATELESS"] = c_stateless("c_stateless")
    OUT["C-STATELESS-FFA6"] = c_stateless("c_stateless_ffa6")
    OUT["C-ZERO-SPECIFIC"] = c_zero()
    OUT["C-A3-INTERNALIZE"] = c_a3()
    OUT["X-MAT-INTERNALIZE"] = x_mat()
    OUT["MULTIPLICITY"] = multiplicity(OUT)
    (HERE / "stats_review.json").write_text(json.dumps(OUT, indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)))
    print(json.dumps(OUT, indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)))


if __name__ == "__main__":
    sys.exit(main())
