#!/usr/bin/env python
"""
HARMONIA A GEN-1 -- frozen analysis. Implements the endpoints and gates
of HARMONIA_A_GEN1_FREEZE.txt verbatim, nothing else. Run after
bench1.py. Permutation/bootstrap seed 20260901.
"""

import json
from collections import defaultdict

import numpy as np

LOCAL_BAND = 0.25
N_LEVELS = 5
MASTER_SEEDS = (11, 22, 33, 44, 55)
MIN_NONZERO = 5            # local_share defined only with >= 5 nonzero d
SUPPORT_FRAC = 0.60        # every level must retain >= 60% of objects
PERM_N = 1000
BOOT_N = 5000
STAT_SEED = 20260901
ETA2_POOLED_GATE = 0.25
ETA2_SEED_GATE = 0.15
PERM_P_GATE = 0.01
PARTIAL_KEEP = 0.30
PARTIAL_LOSE = 0.15
AXES = ("s_live", "inf_density")
CONFOUNDS = ("b_live", "balance_dev", "live_vars", "anf_support",
             "depth", "forced_neutral_floor", "forced_local_bound")
DYADIC = [0.0] + [2.0 ** -k for k in range(10, -1, -1)]


# ------------------------------------------------ small stats library

def ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    # average ties
    vals, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt) - cnt
    avg = csum + (cnt - 1) / 2.0
    return avg[inv]


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def partial_spearman(x, y, Z):
    """Partial rank correlation of x,y given columns Z (rank-transform
    everything, residualize by least squares, correlate residuals)."""
    rx, ry = ranks(x), ranks(y)
    if Z.shape[1] == 0:
        return spearman(x, y)
    RZ = np.column_stack([ranks(Z[:, j]) for j in range(Z.shape[1])])
    A = np.column_stack([np.ones(len(rx)), RZ])
    bx, *_ = np.linalg.lstsq(A, rx, rcond=None)
    by, *_ = np.linalg.lstsq(A, ry, rcond=None)
    ex, ey = rx - A @ bx, ry - A @ by
    den = np.sqrt((ex ** 2).sum() * (ey ** 2).sum())
    return float((ex * ey).sum() / den) if den > 0 else 0.0


def eta2(levels, y):
    y = np.asarray(y, float)
    gm = y.mean()
    ssb = sum(len(y[levels == l]) * (y[levels == l].mean() - gm) ** 2
              for l in np.unique(levels))
    sst = ((y - gm) ** 2).sum()
    return float(ssb / sst) if sst > 0 else 0.0


# ------------------------------------------------ load

def load():
    objs = [json.loads(l) for l in open("results/objects.jsonl")]
    rows = [json.loads(l) for l in open("results/rows.jsonl")]
    return objs, rows


def geometry(objs, rows):
    by_obj = defaultdict(list)
    for r in rows:
        if r["arm"] == "NAT":
            by_obj[(r["seed"], r["level"], r["obj"])].append(r["d"])
    out = []
    for o in objs:
        ds = np.array(by_obj[(o["seed"], o["level"], o["obj"])])
        nz = ds[ds > 0]
        g = dict(o)
        g["balance_dev"] = abs(o["balance"] - 0.5)
        g["n_edits"] = len(ds)
        g["n_nonzero"] = int(len(nz))
        g["neutral"] = float(np.mean(ds == 0))
        g["local"] = float(np.mean((ds > 0) & (ds <= LOCAL_BAND)))
        g["far"] = float(np.mean(ds > LOCAL_BAND))
        g["local_share"] = (float(np.mean(nz <= LOCAL_BAND))
                            if len(nz) >= MIN_NONZERO else None)
        g["med_nonzero"] = float(np.median(nz)) if len(nz) else None
        g["d_q"] = ([float(np.quantile(nz, q))
                     for q in (0.1, 0.25, 0.5, 0.75, 0.9)]
                    if len(nz) else None)
        hist, _ = np.histogram(ds, bins=DYADIC)
        g["hist_dyadic"] = [int(np.sum(ds == 0.0))] + hist.tolist()
        hist64, _ = np.histogram(ds, bins=64, range=(0.0, 1.0))
        g["hist_linear64"] = hist64.tolist()
        del g["gates"]          # provenance lives in objects.jsonl
        out.append(g)
    return out


# ------------------------------------------------ frozen analysis

def perm_p(levels, y, seeds, rng):
    obs = eta2(levels, y)
    hits = 0
    for _ in range(PERM_N):
        yp = y.copy()
        lp = levels.copy()
        for s in np.unique(seeds):
            m = seeds == s
            lp[m] = rng.permutation(levels[m])
        if eta2(lp, y) >= obs:
            hits += 1
    return obs, (hits + 1) / (PERM_N + 1)


def endpoint_block(geo, key, rng):
    sub = [g for g in geo if g[key] is not None]
    levels = np.array([g["level"] for g in sub])
    seeds = np.array([g["seed"] for g in sub])
    y = np.array([g[key] for g in sub], float)
    obs, p = perm_p(levels, y, seeds, rng)
    per_seed = {int(s): eta2(levels[seeds == s], y[seeds == s])
                for s in MASTER_SEEDS}
    idx = np.arange(len(sub))
    boots = []
    for _ in range(BOOT_N):
        pick = rng.integers(len(idx), size=len(idx))
        boots.append(eta2(levels[pick], y[pick]))
    lvl_means = {int(l): float(y[levels == l].mean())
                 for l in range(N_LEVELS) if (levels == l).any()}
    support = {int(l): int((levels == l).sum()) for l in range(N_LEVELS)}
    return dict(n=len(sub), eta2=obs, perm_p=p, per_seed=per_seed,
                eta2_ci95=[float(np.percentile(boots, 2.5)),
                           float(np.percentile(boots, 97.5))],
                level_means=lvl_means, support=support)


def main():
    rng = np.random.default_rng(STAT_SEED)
    objs, rows = load()
    geo = geometry(objs, rows)
    with open("results/objects_geometry.jsonl", "w") as fh:
        for g in geo:
            fh.write(json.dumps(g) + "\n")

    report = {"endpoints": {}, "gates": {}, "e4_associations": {}}

    # ---- G_HARNESS: sham vs native at the extreme levels
    sham_d = defaultdict(list)
    nat_d = defaultdict(list)
    for r in rows:
        if r["level"] in (0, N_LEVELS - 1):
            (sham_d if r["arm"] == "SHAM" else nat_d)[r["level"]].append(
                r["d"])
    hh = {}
    ok = True
    for l, sd in sham_d.items():
        sd, nd = np.array(sd), np.array(nat_d[l])
        dn = abs(np.mean((sd > 0) & (sd <= LOCAL_BAND)) -
                 np.mean((nd > 0) & (nd <= LOCAL_BAND)))
        dz = abs(np.mean(sd == 0) - np.mean(nd == 0))
        hh[str(l)] = dict(d_local=float(dn), d_neutral=float(dz))
        ok &= dn <= 0.03 and dz <= 0.03
    report["gates"]["G_HARNESS"] = dict(
        levels=hh, tol=0.03, verdict="PASS" if ok else "HARNESS_SUSPECT")

    # ---- G_LADDER: realized bins non-overlapping and populated
    lv = defaultdict(list)
    for g in geo:
        lv[g["level"]].append(g["s_live"])
    ordered = all(max(lv[l]) <= min(lv[l + 1]) + 1e-12
                  for l in range(N_LEVELS - 1))
    report["gates"]["G_LADDER"] = dict(
        realized=[[float(min(lv[l])), float(max(lv[l]))]
                  for l in range(N_LEVELS)],
        verdict="PASS" if ordered else "HARNESS_SUSPECT")

    # ---- endpoints E1/E2/E3
    for key, name in (("local_share", "E1_local_share"),
                      ("neutral", "E2_neutral"),
                      ("med_nonzero", "E3_med_nonzero")):
        report["endpoints"][name] = endpoint_block(geo, key, rng)

    # E1 support rule: every level retains >= 60% of its objects
    e1 = report["endpoints"]["E1_local_share"]
    cell_n = defaultdict(int)
    for g in geo:
        cell_n[g["level"]] += 1
    e1_support_ok = all(
        e1["support"].get(l, 0) >= SUPPORT_FRAC * cell_n[l]
        for l in range(N_LEVELS))
    primary = "E1_local_share" if e1_support_ok else "E2_neutral"
    report["gates"]["G_SUPPORT"] = dict(
        e1_support_ok=e1_support_ok, primary_endpoint=primary)

    # ---- E4: association table (object level)
    subkeys = [g for g in geo if g["local_share"] is not None]
    y = {k: np.array([g[k] for g in subkeys], float)
         for k in ("local_share", "neutral")}
    X = {k: np.array([g[k] for g in subkeys], float)
         for k in AXES + CONFOUNDS}
    assoc = {}
    for target in ("local_share", "neutral"):
        t = {}
        for k in AXES + CONFOUNDS:
            t[k] = dict(rho=spearman(X[k], y[target]))
        # partials for the two axis candidates: control the other axis
        # + core confounds (NOT the forced quantities, reported separately)
        core = ["balance_dev", "live_vars", "anf_support", "depth"]
        for ax in AXES:
            others = [a for a in AXES if a != ax] + core
            Z = np.column_stack([X[k] for k in others])
            t[ax]["partial_vs_other_axis_and_core"] = partial_spearman(
                X[ax], y[target], Z)
            Zf = np.column_stack(
                [X[k] for k in others
                 + ["forced_neutral_floor", "forced_local_bound"]])
            t[ax]["partial_vs_other_axis_core_and_forced"] = \
                partial_spearman(X[ax], y[target], Zf)
        # confound dominance: each confound controlling both axes
        Zax = np.column_stack([X[a] for a in AXES])
        for c in CONFOUNDS:
            t[c]["partial_vs_both_axes"] = partial_spearman(
                X[c], y[target], Zax)
        assoc[target] = t
    report["e4_associations"] = assoc

    # ---- verdict (frozen)
    if (report["gates"]["G_HARNESS"]["verdict"] != "PASS"
            or report["gates"]["G_LADDER"]["verdict"] != "PASS"):
        verdict, mech = "HARNESS_SUSPECT", None
    else:
        ep = report["endpoints"][primary]
        gate_pass = (ep["eta2"] >= ETA2_POOLED_GATE
                     and ep["perm_p"] <= PERM_P_GATE
                     and all(v >= ETA2_SEED_GATE
                             for v in ep["per_seed"].values()))
        if not gate_pass:
            verdict, mech = "NO_LOW_DIMENSIONAL_TRANSFER_COORDINATE", None
        else:
            tgt = "local_share" if primary == "E1_local_share" \
                else "neutral"
            t = assoc[tgt]
            ps = t["s_live"]["partial_vs_other_axis_and_core"]
            pb = t["inf_density"]["partial_vs_other_axis_and_core"]
            conf = {c: t[c]["partial_vs_both_axes"] for c in CONFOUNDS}
            top_conf = max(conf, key=lambda c: abs(conf[c]))
            if (abs(pb) >= PARTIAL_KEEP and abs(ps) < PARTIAL_LOSE):
                verdict = "BEHAVIORAL_INFLUENCE_DOMINATES_LIVENESS"
                mech = "BEHAVIORAL"
            elif abs(ps) >= PARTIAL_KEEP:
                verdict = "TRANSFER_COORDINATE_SUPPORTED"
                mech = "STRUCTURAL" if abs(pb) < PARTIAL_LOSE else "BOTH"
            elif (abs(conf[top_conf]) >= PARTIAL_KEEP
                  and abs(ps) < PARTIAL_LOSE and abs(pb) < PARTIAL_LOSE):
                verdict = "ALTERNATE_COORDINATE_DOMINATES"
                mech = f"CONFOUND:{top_conf}"
            else:
                verdict = "TRANSFER_COORDINATE_SUPPORTED"
                mech = "UNRESOLVED_COLLINEAR"
    report["verdict"] = dict(verdict=verdict, mechanism=mech,
                             primary_endpoint=primary)

    json.dump(report, open("results/analysis_gen1.json", "w"), indent=1)

    for name in ("E1_local_share", "E2_neutral", "E3_med_nonzero"):
        ep = report["endpoints"][name]
        print(f"{name}: n={ep['n']} eta2={ep['eta2']:.4f} "
              f"p={ep['perm_p']:.4f} per-seed="
              f"{[round(v,3) for v in ep['per_seed'].values()]}")
        print(f"   level means: "
              f"{ {l: round(m,4) for l,m in ep['level_means'].items()} }")
    for gname, gv in report["gates"].items():
        print(f"{gname}: {gv.get('verdict', gv)}")
    print("VERDICT:", report["verdict"])


if __name__ == "__main__":
    main()
