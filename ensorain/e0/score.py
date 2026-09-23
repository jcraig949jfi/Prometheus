"""Frozen E0 scorer (PREREG_E0 part 1 s5-s7, part 2 s4 and A6).
Committed before any confirmatory row. Usage: python -m ensorain.e0.score
Reads ensorain/runs/confirm_M{1,2,3,4}.jsonl and genome_c0_cap{96,168}.json.
"""
import json
import collections
import numpy as np

from .world import World, D
from .tt import ranks_of_order, n_params_for_ranks

NON_TT = ("LRU", "HASH", "KNN", "ADDITIVE", "RF", "LOWRANK")
STRUCT = ("ADDITIVE", "RF", "LOWRANK", "TT_FIXED", "TT_TUNED", "TT_PLANTED", "TT_EVOLVED")
RNG = np.random.default_rng(20260923)
BOOT = 10_000


def load(which):
    rows = []
    try:
        with open(f"ensorain/runs/confirm_{which}.jsonl") as f:
            for line in f:
                r = json.loads(line)
                if r.get("status") == "OK":
                    rows.append(r)
    except FileNotFoundError:
        pass
    return rows


def per_inst(rows, arm, cap, lam, cls=0, key="harvest"):
    d = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == arm and r["cap"] == cap and abs(r["lam"] - lam) < 1e-9 and r["class_seed"] == cls:
            d[r["inst_seed"]].append(r[key])
    return {i: float(np.mean(v)) for i, v in d.items()}


def paired(a, b):
    ks = sorted(set(a) & set(b))
    return np.array([a[k] for k in ks]), np.array([b[k] for k in ks])


def boot_lo(diff):
    if len(diff) == 0:
        return float("nan")
    idx = RNG.integers(len(diff), size=(BOOT, len(diff)))
    return float(np.quantile(diff[idx].mean(1), 0.025))


def best_non_tt(rows, cap, lam, cls=0):
    best, bm = None, -1e18
    for a in NON_TT:
        v = per_inst(rows, a, cap, lam, cls)
        if v and np.mean(list(v.values())) > bm:
            best, bm = a, float(np.mean(list(v.values())))
    return best


def table(rows):
    agg = collections.defaultdict(list)
    for r in rows:
        agg[(r["class_seed"], r["lam"], r["cap"], r["arm"])].append(r)
    out = []
    for k in sorted(agg):
        v = agg[k]
        out.append("%d %4.2f %5d %-14s n=%3d harv %8.1f sd %7.1f steps %6.0f acc %.2f r2unv %8.2f kflops %8.1f" % (
            k[0], k[1], k[2], k[3], len(v), np.mean([r["harvest"] for r in v]), np.std([r["harvest"] for r in v]),
            np.mean([r["steps"] for r in v]), np.mean([r["dec_acc"] for r in v]),
            np.nanmedian([r["r2_unv"] for r in v]), np.mean([r["flops"] for r in v]) / 1e3))
    return out


def main():
    M1, M2, M3, M4 = (load(w) for w in ("M1", "M2", "M3", "M4"))
    rep = {}
    print("== TABLE M1 (class lam cap arm)")
    print("\n".join(table(M1)))

    # ---------------- controls
    ctrl = {}
    caps = sorted({r["cap"] for r in M1})
    # NEGATIVE literal: |median r2_unv| <= .05 in R for every structural learner at every cap
    neg_lit, neg_gov, neg_harv_lit, neg_harv_gov = True, True, True, True
    for cap in caps:
        for a in STRUCT:
            v = [r["r2_unv"] for r in M1 if r["arm"] == a and r["cap"] == cap and r["lam"] == 1.0]
            if not v:
                continue
            m = float(np.nanmedian(v))
            neg_lit &= abs(m) <= 0.05
            neg_gov &= m <= 0.05
        lru = per_inst(M1, "LRU", cap, 1.0)
        nom = per_inst(M1, "NOMEM", cap, 1.0)
        sd_lru = np.std(list(lru.values())) if lru else 0
        sd_nom = np.std(list(nom.values())) if nom else 0
        for a in STRUCT + NON_TT:
            v = per_inst(M1, a, cap, 1.0)
            if not v:
                continue
            m = np.mean(list(v.values()))
            if lru and m - np.mean(list(lru.values())) > sd_lru:
                neg_harv_lit = False
            if nom and m - np.mean(list(nom.values())) > sd_nom:
                neg_harv_gov = False
    ctrl["NEG_r2_literal"] = neg_lit
    ctrl["NEG_r2_governing"] = neg_gov
    ctrl["NEG_harvest_vs_LRU_literal"] = neg_harv_lit
    ctrl["NEG_harvest_vs_NOMEM_governing"] = neg_harv_gov
    # POSITIVE: ORACLE top (excl. TT_SVD_INJECT) in C and R at every cap; planted R2_unv >= .5 at 168
    top_ok, top_lit = True, True
    for cap in caps:
        for lam in (0.0, 1.0):
            means = {}
            for a in {r["arm"] for r in M1}:
                v = per_inst(M1, a, cap, lam)
                if v:
                    means[a] = np.mean(list(v.values()))
            if not means:
                continue
            top_lit &= max(means, key=means.get) == "ORACLE"
            m2 = {a: m for a, m in means.items() if a != "TT_SVD_INJECT"}
            top_ok &= max(m2, key=m2.get) == "ORACLE"
    pl = [r["r2_unv"] for r in M1 if r["arm"] == "TT_PLANTED" and r["cap"] == 168 and r["lam"] == 0.0]
    ctrl["POS_oracle_top_literal"] = top_lit
    ctrl["POS_oracle_top_governing"] = top_ok
    ctrl["POS_planted_r2unv_168"] = float(np.nanmedian(pl)) if pl else float("nan")
    ctrl["POS_planted_ok"] = bool(pl) and float(np.nanmedian(pl)) >= 0.5
    # CHEAT: smuggler refused; SVD inject within 10% of ORACLE at 168 and 384 in C
    from . import memories as MM
    from .life import live
    try:
        live(World(0, 10000), MM.CheatSmuggler(168), 168, seed=0)
        ctrl["CHEAT_smuggler_refused"] = False
    except MM.AuditError as ex:
        ctrl["CHEAT_smuggler_refused"] = True
        ctrl["CHEAT_smuggler_msg"] = str(ex)
    inj_ok = True
    for cap in (168, 384):
        o = per_inst(M1, "ORACLE", cap, 0.0)
        s = per_inst(M1, "TT_SVD_INJECT", cap, 0.0)
        if not o or not s:
            inj_ok = False
            continue
        ctrl[f"CHEAT_inject_ratio_{cap}"] = float(np.mean(list(s.values())) / np.mean(list(o.values())))
        inj_ok &= ctrl[f"CHEAT_inject_ratio_{cap}"] >= 0.9
    ctrl["CHEAT_inject_ok"] = inj_ok
    controls_pass = (ctrl["NEG_r2_governing"] and ctrl["NEG_harvest_vs_NOMEM_governing"] and ctrl["POS_oracle_top_governing"]
                     and ctrl["POS_planted_ok"] and ctrl["CHEAT_smuggler_refused"] and ctrl["CHEAT_inject_ok"])
    controls_pass_literal = (ctrl["NEG_r2_literal"] and ctrl["NEG_harvest_vs_LRU_literal"] and ctrl["POS_oracle_top_literal"]
                             and ctrl["POS_planted_ok"] and ctrl["CHEAT_smuggler_refused"] and ctrl["CHEAT_inject_ok"])
    rep["controls"] = ctrl
    rep["controls_pass_governing"] = controls_pass
    rep["controls_pass_literal"] = controls_pass_literal

    # ---------------- H1
    h1 = {}
    h1_ok = True
    for cap in (96, 168):
        bc, br = best_non_tt(M1, cap, 0.0), best_non_tt(M1, cap, 1.0)
        tc, b = paired(per_inst(M1, "TT_TUNED", cap, 0.0), per_inst(M1, bc, cap, 0.0))
        margin = tc.mean() / b.mean() - 1 if len(b) else float("nan")
        lo = boot_lo(tc - b)
        tr, b2 = paired(per_inst(M1, "TT_TUNED", cap, 1.0), per_inst(M1, br, cap, 1.0))
        dc = {i: v for i, v in zip(sorted(set(per_inst(M1, "TT_TUNED", cap, 0.0)) & set(per_inst(M1, bc, cap, 0.0))), tc - b)}
        dr = {i: v for i, v in zip(sorted(set(per_inst(M1, "TT_TUNED", cap, 1.0)) & set(per_inst(M1, br, cap, 1.0))), tr - b2)}
        x, y = paired(dc, dr)
        inter_lo = boot_lo(x - y)
        ok = margin >= 0.10 and lo > 0 and inter_lo > 0
        h1[cap] = dict(best_C=bc, best_R=br, TT_mean=float(tc.mean()) if len(tc) else None,
                       best_mean=float(b.mean()) if len(b) else None, margin=float(margin), ci_lo=lo,
                       interaction_mean=float((x - y).mean()) if len(x) else None, interaction_lo=inter_lo, pass_=ok)
        h1_ok &= ok
    rep["H1"] = h1
    rep["H1_pass"] = h1_ok

    # ---------------- H2
    h2 = {}
    harvest_ok = False
    for cap in (96, 168):
        e, t = paired(per_inst(M1, "TT_EVOLVED", cap, 0.0), per_inst(M1, "TT_TUNED", cap, 0.0))
        if len(e) == 0:
            continue
        m = e.mean() / t.mean() - 1
        lo = boot_lo(e - t)
        ok = m >= 0.10 and lo > 0
        h2[f"harvest_{cap}"] = dict(evolved=float(e.mean()), tuned=float(t.mean()), margin=float(m), ci_lo=lo, pass_=ok)
        harvest_ok |= ok
    w = World(0, 10000)
    dense = w.dense_obs()
    rr = np.random.default_rng(5150)
    rand = [n_params_for_ranks(ranks_of_order(dense, tuple(rr.permutation(D))), [4] * D) for _ in range(200)]
    med = float(np.median(rand))
    latent = n_params_for_ranks(ranks_of_order(dense, tuple(int(i) for i in np.argsort(w.perm))), [4] * D)
    observed = n_params_for_ranks(ranks_of_order(dense, tuple(range(D))), [4] * D)
    order_ok = False
    for cap in (96, 168):
        try:
            with open(f"ensorain/runs/genome_c0_cap{cap}.json") as f:
                g = json.load(f)["genome"]
        except FileNotFoundError:
            continue
        need = n_params_for_ranks(ranks_of_order(dense, tuple(g["order"])), [4] * D)
        h2[f"order_{cap}"] = dict(order=g["order"], need=need, random_median=med, latent=latent, observed=observed,
                                  exact_latent=list(g["order"]) == [int(i) for i in np.argsort(w.perm)], pass_=need < med)
        order_ok |= need < med
    cross = {}
    cross_ok = True
    for cap in (96, 168):
        e0, t0 = paired(per_inst(M1, "TT_EVOLVED", cap, 0.0), per_inst(M1, "TT_TUNED", cap, 0.0))
        e1, t1 = paired(per_inst(M3, "TT_EVOLVED", cap, 0.0, cls=1), per_inst(M3, "TT_TUNED", cap, 0.0, cls=1))
        if len(e0) and len(e1):
            g0, g1 = float(e0.mean() - t0.mean()), float(e1.mean() - t1.mean())
            cross[cap] = dict(gain_class0=g0, gain_class1=g1, pass_=g1 <= 0.5 * g0)
            if h2.get(f"harvest_{cap}", {}).get("pass_"):
                cross_ok &= g1 <= 0.5 * g0
    h2["cross_class"] = cross
    rep["H2"] = h2
    rep["H2_pass"] = bool(harvest_ok and order_ok and cross_ok)
    rep["H2_parts"] = dict(harvest=harvest_ok, order=order_ok, cross=cross_ok)

    # ---------------- H3
    lams = (0.0, 0.25, 0.5, 0.75, 1.0)
    allrows = M1 + M2
    adv = []
    last_lo = None
    for lam in lams:
        b = best_non_tt(allrows, 168, lam)
        t, bb = paired(per_inst(allrows, "TT_TUNED", 168, lam), per_inst(allrows, b, 168, lam))
        adv.append(float((t - bb).mean()) if len(t) else float("nan"))
        if lam == 1.0:
            last_lo = boot_lo(t - bb)
            last_hi = float(np.quantile((t - bb)[RNG.integers(len(t), size=(BOOT, len(t)))].mean(1), 0.975)) if len(t) else float("nan")
    from scipy.stats import spearmanr
    rho = float(spearmanr(lams, adv).statistic) if not any(np.isnan(adv)) else float("nan")
    h3_ok = rho <= -0.9 and (last_lo <= 0 <= last_hi or last_hi < 0)
    rep["H3"] = dict(adv=adv, rho=rho, M1_ci=(last_lo, last_hi), pass_=bool(h3_ok))
    rep["H3_pass"] = bool(h3_ok)

    # ---------------- verdict (part 1 s7)
    if not controls_pass:
        v = "INDETERMINATE (controls)"
    elif not h1_ok:
        v = "B"
    elif not rep["H2_pass"]:
        v = "B-MUNDANE"
    elif rep["H3_pass"]:
        v = "A"
    else:
        v = "A-WEAK"
    rep["VERDICT"] = v

    # ---------------- secondary M4 (kappa 0), not gated
    if M4:
        print("== TABLE M4 (kappa=0, secondary)")
        print("\n".join(table(M4)))
    print("== REPORT")
    print(json.dumps(rep, indent=1, default=str))
    with open("ensorain/runs/score_E0.json", "w") as f:
        json.dump(rep, f, indent=1, default=str)


if __name__ == "__main__":
    main()
