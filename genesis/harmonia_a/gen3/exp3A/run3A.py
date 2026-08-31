#!/usr/bin/env python
"""GEN-3A -- frozen analysis per FREEZE_3A.txt."""

import json
import sys

import numpy as np

sys.path.insert(0, "..")
import common as cm

STAT_SEED = 20260902
COVS = ("s_live", "inf_density", "b_live", "balance_dev", "live_vars",
        "anf_support", "depth", "forced_neutral_floor",
        "forced_local_bound")
AXES = ("s_live", "inf_density")


def endpoint(geo, key, rng):
    sub = [g for g in geo if g[key] is not None]
    lv = np.array([g["level"] for g in sub])
    sd = np.array([g["seed"] for g in sub])
    y = np.array([g[key] for g in sub], float)
    obs, p = cm.perm_p_eta2(lv, y, sd, rng)
    per_seed = {int(s): cm.eta2(lv[sd == s], y[sd == s])
                for s in cm.MASTER_SEEDS}
    support = {int(l): int((lv == l).sum()) for l in range(5)}
    means = {int(l): float(y[lv == l].mean()) for l in range(5)}
    gate = (obs >= 0.25 and p <= 0.01
            and all(v >= 0.15 for v in per_seed.values()))
    return dict(n=len(sub), eta2=obs, perm_p=p, per_seed=per_seed,
                support=support, level_means=means, gate_pass=bool(gate))


def main():
    rng = np.random.default_rng(STAT_SEED)
    geo = cm.per_object_vector_outcomes()
    cell_n = {}
    for g in geo:
        cell_n[g["level"]] = cell_n.get(g["level"], 0) + 1

    report = {"endpoints": {}}
    for key, name in (("small_share", "E1_small_share"),
                      ("destr_share", "E2_destr_share"),
                      ("mass_N", "E3_mass_N")):
        report["endpoints"][name] = endpoint(geo, key, rng)

    support_ok = all(
        report["endpoints"]["E1_small_share"]["support"].get(l, 0)
        >= 0.6 * cell_n[l] for l in range(5))

    # E4 association table on the conditional shares
    sub = [g for g in geo if g["small_share"] is not None]
    X = {k: np.array([g[k] for g in sub], float) for k in COVS}
    assoc = {}
    for tgt in ("small_share", "destr_share"):
        y = np.array([g[tgt] for g in sub], float)
        t = {}
        for k in COVS:
            t[k] = dict(rho=round(cm.spearman(X[k], y), 4))
        core = ["balance_dev", "live_vars", "anf_support", "depth"]
        for ax in AXES:
            others = [a for a in AXES if a != ax] + core
            Z = np.column_stack([X[k] for k in others])
            t[ax]["partial"] = round(cm.partial_spearman(X[ax], y, Z), 4)
        Zax = np.column_stack([X[a] for a in AXES])
        for c in COVS:
            if c not in AXES:
                t[c]["partial_vs_axes"] = round(
                    cm.partial_spearman(X[c], y, Zax), 4)
        assoc[tgt] = t
    report["E4"] = assoc

    e1 = report["endpoints"]["E1_small_share"]["gate_pass"]
    e2 = report["endpoints"]["E2_destr_share"]["gate_pass"]
    if not support_ok:
        verdict = "INDETERMINATE"
    elif e1 or e2:
        verdict = "TRANSFER_STRUCTURE_RECOVERED"
    else:
        verdict = "NO_TRANSFER_STRUCTURE"
    report["verdict"] = verdict

    # frozen candidate handoff to 3B
    cands = sorted({k for tgt in assoc for k in COVS
                    if abs(assoc[tgt][k]["rho"]) >= 0.3})
    report["candidates_for_3B"] = cands

    json.dump(report, open("results/analysis_3A.json", "w"), indent=1)
    for name, ep in report["endpoints"].items():
        print(f"{name}: eta2={ep['eta2']:.4f} p={ep['perm_p']:.4f} "
              f"per-seed={[round(v,3) for v in ep['per_seed'].values()]} "
              f"gate={'PASS' if ep['gate_pass'] else 'FAIL'}")
        print(f"   level means: "
              f"{ {l: round(m,4) for l,m in ep['level_means'].items()} }")
    print("balance_dev partial (small_share):",
          assoc["small_share"]["balance_dev"]["partial_vs_axes"],
          "| Gen-1 was +0.52 on old LOCAL_SHARE")
    print("VERDICT:", verdict)
    print("candidates_for_3B:", cands)


if __name__ == "__main__":
    main()
