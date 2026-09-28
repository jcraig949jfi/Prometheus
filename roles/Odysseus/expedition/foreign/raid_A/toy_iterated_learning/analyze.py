#!/usr/bin/env python3
"""Evaluate result.json against PREREG.md s5 (criteria fixed before the run). stdlib only."""
import json, os, statistics as st
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "result.json")))
CH = D["chains"]


def arm(kind, B, f):
    return [c for c in CH if c["kind"] == kind and c["B"] == B and c["filter"] == f]


def at(cs, g, k):
    return [c["traj"][str(g)][k] for c in cs]


def med(x):
    return round(st.median(x), 3)


def mean(x):
    return round(st.mean(x), 3)


table = []
for kind in ["HOLISTIC", "NNCOPY", "ASSOC", "PLANTED"]:
    for B in (16, 64):
        for f in (0, 1):
            cs = arm(kind, B, f)
            row = {"arm": f"{kind} B{B} F{f}"}
            for g in (0, 1, 5, 30):
                row[f"z{g}"] = med(at(cs, g, "z"))
            for g in (1, 30):
                row[f"ls{g}"] = mean(at(cs, g, "learn_same"))
                row[f"la{g}"] = mean(at(cs, g, "learn_assoc"))
                row[f"ex{g}"] = mean(at(cs, g, "expr"))
            row["stab"] = mean([c["stab_last5"] for c in cs])
            table.append(row)

V = {}
h = arm("HOLISTIC", 16, 0) + arm("HOLISTIC", 16, 1)
V["V1_holistic_null"] = {"median_z30": med(at(h, 30, "z")), "pass": st.median(at(h, 30, "z")) < 2}
p = arm("PLANTED", 16, 1)
V["V2_planted_positive"] = {"median_z30": med(at(p, 30, "z")), "mean_learn_same30": mean(at(p, 30, "learn_same")),
                            "pass": st.median(at(p, 30, "z")) > 5 and st.mean(at(p, 30, "learn_same")) > 0.8}
a = arm("ASSOC", 16, 1)
d_ls = st.mean(at(a, 30, "learn_same")) - st.mean(at(a, 1, "learn_same"))
nz = sum(z30 > z1 for z30, z1 in zip(at(a, 30, "z"), at(a, 1, "z")))
K = {}
K["K1_ratchet_vs_onestep"] = {"delta_learn_same": round(d_ls, 3), "chains_z30_gt_z1": nz,
                              "pass": d_ls >= 0.30 and nz >= 16}
b64 = arm("ASSOC", 64, 0) + arm("ASSOC", 64, 1)
K["K2_bottleneck_necessary"] = {"median_z30_B64": med(at(b64, 30, "z")), "mean_ls30_B64": mean(at(b64, 30, "learn_same")),
                                "pass": st.median(at(b64, 30, "z")) < 2 and st.mean(at(b64, 30, "learn_same")) < 0.2}
sigs = [c["traj"]["30"]["align"] for c in a if c["traj"]["30"]["z"] > 3]
K["K3_convention_invented"] = {"n_chains_z_gt3": len(sigs), "distinct_signatures": len(set(sigs)),
                               "signatures": dict(Counter(sigs)), "pass": len(set(sigs)) >= 5}
K["K4_content_dependence"] = {"perm_acc": mean([c["perm_assoc"] for c in a]), "intact_la30": mean(at(a, 30, "learn_assoc")),
                              "pass": st.mean([c["perm_assoc"] for c in a]) <= 0.05 and st.mean(at(a, 30, "learn_assoc")) >= 0.5}
K["K5_ceiling_vs_recompute"] = {"recomp_la": mean([c["recomp_learn_assoc"] for c in a]), "recomp_z_median": med([c["recomp_z"] for c in a]),
                                "chain_la30": mean(at(a, 30, "learn_assoc")),
                                "pass": st.mean([c["recomp_learn_assoc"] for c in a]) <= 0.1 and st.mean(at(a, 30, "learn_assoc")) >= 0.5}
a0 = arm("ASSOC", 16, 0)
E = {}
E["E1_expressivity_filter"] = {"expr30_F0": mean(at(a0, 30, "expr")), "expr30_F1": mean(at(a, 30, "expr")),
                               "as_predicted": st.mean(at(a, 30, "expr")) - st.mean(at(a0, 30, "expr")) >= 0.2}
n1 = arm("NNCOPY", 16, 1)
E["E2_nncopy_minimal_bias"] = {"ls30": mean(at(n1, 30, "learn_same")), "expr30": mean(at(n1, 30, "expr")),
                               "z30_median": med(at(n1, 30, "z")),
                               "prediction_no_ratchet_held": st.mean(at(n1, 30, "learn_same")) < 0.3 or st.mean(at(n1, 30, "expr")) < 0.3,
                               "strong_ratchet": st.mean(at(n1, 30, "learn_same")) >= 0.5 and st.mean(at(n1, 30, "expr")) >= 0.5}
# supplementary (not preregistered): per-chain ASSOC B16 F1 trajectories, align at z>3 in F0
SUPP = {"ASSOC_B16_F1_traj_mean": {g: {k: mean(at(a, g, k)) for k in ("z", "expr", "learn_same", "learn_assoc")}
                                    for g in (0, 1, 2, 5, 10, 20, 30)},
        "NNCOPY_B16_F1_traj_mean": {g: {k: mean(at(n1, g, k)) for k in ("z", "expr", "learn_same", "learn_assoc")}
                                     for g in (0, 1, 2, 5, 10, 20, 30)}}
out = {"table": table, "validity": V, "kills": K, "exploratory": E, "supplementary_not_prereg": SUPP}
json.dump(out, open(os.path.join(HERE, "analysis.json"), "w"), indent=1)
for r in table:
    print(r)
for blk in (V, K, E):
    for k, v in blk.items():
        print(k, v)
print(json.dumps(SUPP, indent=0))
