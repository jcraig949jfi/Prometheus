"""W2-4: aggregate w4_results.json (+ w4_suff.json if present) -> w4_summary.json and printed tables.

    python -B w4_summarize.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics as st

HERE = pathlib.Path(__file__).resolve().parent
R = json.loads((HERE / "w4_results.json").read_text())["genomes"]
SUFF = HERE / "w4_suff.json"
S = {r["id"]: r for r in json.loads(SUFF.read_text())["genomes"]} if SUFF.exists() else {}
GRPS = ("SF", "SD", "E700", "SPEC", "MIN3", "MIN5")


def med(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    q = st.quantiles(v, n=4) if len(v) > 1 else [v[0]] * 3
    return {"median": st.median(v), "q1": q[0], "q3": q[2], "min": min(v), "max": max(v), "n": len(v)}


def mwu(a, b):
    """Mann-Whitney U two-sided p by exact permutation-free normal approximation (ties averaged)."""
    allv = sorted([(x, 0) for x in a] + [(x, 1) for x in b])
    ranks = {}
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[k] = (i + j) / 2 + 1
        i = j + 1
    ra = sum(ranks[k] for k, (x, gg) in enumerate(allv) if gg == 0)
    n1, n2 = len(a), len(b)
    u = ra - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    sd = (n1 * n2 * (n1 + n2 + 1) / 12) ** 0.5
    if sd == 0:
        return u, 1.0
    z = (u - mu) / sd
    import math
    p = math.erfc(abs(z) / 2 ** 0.5)
    return u, p


def genome_summary(r):
    o = {"id": r["id"], "grp": r["grp"], "cell": r["cell"], "status": r["status"], "wt": r["wt"],
         "n_T": len(r["transmitted"]), "pass_side": r.get("pass_side"), "env": r.get("env")}
    if r["status"] != "OK":
        return o
    pos = r["pos"]
    cls = {x["p"]: x["cls"] for x in pos}
    T = set(r["transmitted"])
    o["counts"] = dict(collections.Counter(cls.values()))
    est = [x for x in pos if x["cls"] == "EST_ONLY"]
    o["est_initial"] = [(x["p"], x["killed"]) for x in est]
    conf = [x for x in est if x.get("re_same", {}).get("cls") == "EST_ONLY"
            and set(x["re_same"]["killed"]) & set(x["killed"])]
    o["est_confirmed"] = [(x["p"], sorted(set(x["re_same"]["killed"]) & set(x["killed"]))) for x in conf]
    o["est_value_robust"] = [x["p"] for x in conf if x.get("re_val2", {}).get("cls") == "EST_ONLY"]
    o["est_reassay_other"] = {x["p"]: x.get("re_same", {}).get("cls") for x in est if x not in conf}
    part = [x for x in pos if x["cls"] == "CONV_PARTIAL"]
    o["partial_reassay"] = {x["p"]: x.get("re_same", {}).get("cls") for x in part}
    conv = sorted(p for p, c in cls.items() if c == "CONV_NEC")
    o["conv_nec"] = conv
    ti = r.get("trace") or {}
    cp = ti.get("copy_pos")
    o["copy_pos"], o["copy_op"] = cp, ti.get("copy_op")
    o["setter_pos"] = ti.get("setter_pos")
    o["HL_DE_BC"] = (ti.get("HL"), ti.get("DE"), ti.get("BC"))
    zs = (r.get("env") or {}).get("zero_side") or 0
    o["conv_primitive"] = [p for p in conv if p == cp]
    o["conv_operand_rescued"] = [x["p"] for x in pos if x["cls"] == "CONV_NEC" and x.get("rescue_operand") is not None
                                 and zs > 0 and x["rescue_operand"] >= 0.5 * zs]
    o["passengers"] = sorted(p for p in T if cls[p] == "NEUTRAL")
    o["idle_not_T"] = sorted(p for p in range(64) if p not in T and cls[p] == "NEUTRAL")
    o["causal_not_T"] = sorted(p for p in range(64) if p not in T and cls[p] != "NEUTRAL")
    o["gains"] = [(x["p"], x["gains"]) for x in pos if x["gains"]]
    null = r["null"]
    o["null_est"] = sum(1 for x in null if x["cls"] == "EST_ONLY")
    o["null_est_confirmed"] = sum(1 for x in null if x["cls"] == "EST_ONLY" and x.get("re_same", {}).get("cls") == "EST_ONLY")
    o["null_cls"] = dict(collections.Counter(x["cls"] for x in null))
    o["null_n"] = len(null)
    # deletion (instruction-level removal) vs byte-level corruption
    dl = r.get("deletion", [])
    o["deletion"] = [(d["p"], d["bytes"], d["cls"], d["killed"]) for d in dl]
    subst = []
    for d in dl:
        span = range(d["p"], d["p"] + d["len"])
        if any(cls.get(p) == "CONV_NEC" for p in span) and d["cls"] not in ("CONV_NEC", "CONV_PARTIAL"):
            subst.append((d["p"], d["bytes"], d["cls"], d["killed"]))
    o["env_default_substituted_instr"] = subst
    o["deletion_conv_nec_instr"] = [(d["p"], d["bytes"]) for d in dl if d["cls"] == "CONV_NEC"]
    o["deletion_est_only_instr"] = [(d["p"], d["bytes"], d["killed"]) for d in dl if d["cls"] == "EST_ONLY"]
    # FOR comparison
    if r.get("for_collapse") is not None:
        fc = set(r["for_collapse"])
        o["for_collapse_n"] = len(fc)
        o["for_collapse_in_convnec"] = len(fc & set(conv))
        o["for_collapse_in_est"] = len(fc & {p for p, _ in o["est_confirmed"]})
        o["convnec_not_for"] = sorted(set(conv) - fc)
    if "motif_len" in r:
        ml = r["motif_len"]
        o["pad_est_initial"] = sum(1 for x in est if x["p"] >= ml)
        o["pad_est_confirmed"] = sum(1 for p, _ in o["est_confirmed"] if p >= ml)
        o["pad_n"] = 64 - ml
    # environment-level dependence (class 4) and physics (class 5)
    e = r.get("env") or {}
    z0 = e.get("zero") or 0
    if z0 > 0:
        o["env_regs_supplied"] = [k[4:] for k in e if k.startswith("reg_") and e[k] <= 0.5 * z0]
        o["env_flags_supplied"] = e.get("flags_set", z0) <= 0.5 * z0
        o["env_donor_random_ratio"] = round(e["donor_random"] / z0, 3)
        o["env_partner_random_ratio"] = round(e["partner_random"] / z0, 3)
        o["side_only"] = [s for s in (0, 1) if e["side%d_only" % s] >= 0.5 * 2 * z0 * 0.5 and e["side%d_only" % (1 - s)] <= 0.25 * 2 * z0]
        o["base_ratio"] = round(e["base_conv"] / z0, 3)
        o["base_intact"] = e["base_intact"]
        o["phys_stock_ratio"] = round(e["stock_vm"] / z0, 3)
        o["phys_tape256_ratio"] = round(e["tape256"] / z0, 3)
        o["phys_slice"] = {s: round(e["slice_%d" % s] / z0, 3) for s in (150, 600, 1200)}
        if e.get("zero_side"):
            o["operand_entry_ratio"] = round(e["operand_entry_side"] / e["zero_side"], 3)
    if r["id"] in S:
        o["suff"] = {k: {kk: v[kk] for kk in ("n", "Z_ratio", "C_ratio", "K_ratio", "P2_ratio", "draws_Z_ge_half")}
                     | {"NOP_Z": v["NOP"]["Z"]} for k, v in S[r["id"]]["res"].items()}
    return o


def main():
    G = [genome_summary(r) for r in R]
    out = {"genomes": G, "groups": {}}
    for gname in GRPS:
        gs = [g for g in G if g["grp"] == gname and g["status"] == "OK"]
        if not gs:
            continue
        agg = {"n": len(gs), "n_status_not_ok": sum(1 for g in G if g["grp"] == gname and g["status"] != "OK")}
        for k in ("CONV_NEC", "CONV_PARTIAL", "EST_ONLY", "NEUTRAL"):
            agg[k] = med([g["counts"].get(k, 0) for g in gs])
        agg["est_confirmed"] = med([len(g["est_confirmed"]) for g in gs])
        agg["est_confirmed_total"] = sum(len(g["est_confirmed"]) for g in gs)
        agg["est_initial_total"] = sum(len(g["est_initial"]) for g in gs)
        agg["est_value_robust_total"] = sum(len(g["est_value_robust"]) for g in gs)
        agg["est_by_readout"] = dict(collections.Counter(k for g in gs for _, ks in g["est_confirmed"] for k in ks))
        agg["n_T"] = med([g["n_T"] for g in gs])
        agg["passengers"] = med([len(g["passengers"]) for g in gs])
        agg["null_est"] = [sum(g["null_est"] for g in gs), sum(g["null_n"] for g in gs)]
        agg["null_est_confirmed"] = sum(g["null_est_confirmed"] for g in gs)
        agg["null_cls"] = dict(sum((collections.Counter(g["null_cls"]) for g in gs), collections.Counter()))
        agg["env_regs"] = dict(collections.Counter(x for g in gs for x in g.get("env_regs_supplied", [])))
        agg["genomes_any_env_reg"] = sum(1 for g in gs if g.get("env_regs_supplied"))
        agg["side_only"] = dict(collections.Counter(str(g.get("side_only")) for g in gs))
        agg["stock_dead"] = sum(1 for g in gs if g.get("phys_stock_ratio", 1) <= 0.25)
        agg["tape256_dead"] = sum(1 for g in gs if g.get("phys_tape256_ratio", 1) <= 0.5)
        agg["slice150_dead"] = sum(1 for g in gs if g.get("phys_slice", {}).get(150, 1) <= 0.5)
        agg["slice1200_dead"] = sum(1 for g in gs if g.get("phys_slice", {}).get(1200, 1) <= 0.5)
        agg["base_ratio"] = med([g.get("base_ratio") for g in gs])
        agg["base_intact"] = med([g.get("base_intact") for g in gs])
        agg["conv_primitive"] = sum(len(g["conv_primitive"]) for g in gs)
        agg["conv_operand_rescued"] = sum(len(g["conv_operand_rescued"]) for g in gs)
        agg["conv_total"] = sum(len(g["conv_nec"]) for g in gs)
        agg["env_default_substituted_instr"] = sum(len(g["env_default_substituted_instr"]) for g in gs)
        agg["deletion_instr_total"] = sum(len(g["deletion"]) for g in gs)
        agg["deletion_conv_nec_instr"] = med([len(g["deletion_conv_nec_instr"]) for g in gs])
        agg["deletion_est_only_instr_total"] = sum(len(g["deletion_est_only_instr"]) for g in gs)
        agg["wt_C_ge_0.1"] = sum(1 for g in gs if g["wt"]["C"] >= 0.1)
        agg["wt"] = {k: med([g["wt"][k] for g in gs]) for k in ("Z", "R", "K", "C", "P2")}
        if any("suff" in g for g in gs):
            agg["suff"] = {}
            for sname in ("S_conv", "S_est", "S_exec"):
                v = [g["suff"][sname] for g in gs if "suff" in g]
                agg["suff"][sname] = {"n": med([x["n"] for x in v]), "Z_ratio": med([x["Z_ratio"] for x in v]),
                                      "C_ratio": med([x["C_ratio"] for x in v]), "K_ratio": med([x["K_ratio"] for x in v]),
                                      "P2_ratio": med([x["P2_ratio"] for x in v]),
                                      "genomes_Z_ge_half_all_draws": sum(1 for x in v if x["draws_Z_ge_half"] == 2),
                                      "genomes_Z_ratio_ge_half": sum(1 for x in v if (x["Z_ratio"] or 0) >= 0.5),
                                      "genomes_C_ratio_ge_half": sum(1 for x in v if x["C_ratio"] is not None and x["C_ratio"] >= 0.5),
                                      "genomes_C_defined": sum(1 for x in v if x["C_ratio"] is not None),
                                      "genomes_P2_ratio_ge_half": sum(1 for x in v if x["P2_ratio"] is not None and x["P2_ratio"] >= 0.5),
                                      "genomes_P2_defined": sum(1 for x in v if x["P2_ratio"] is not None)}
        out["groups"][gname] = agg
    sf = [len(g["est_confirmed"]) for g in G if g["grp"] in ("SF",) and g["status"] == "OK"]
    sd = [len(g["est_confirmed"]) for g in G if g["grp"] in ("SD",) and g["status"] == "OK"]
    out["SF_vs_SD_est_confirmed_mwu"] = mwu(sf, sd) if sf and sd else None
    sfc = [g for g in G if g["grp"] in ("SF", "E700") and g["status"] == "OK" and g["wt"]["C"] >= 0.1]
    sdc = [g for g in G if g["grp"] == "SD" and g["status"] == "OK" and g["wt"]["C"] >= 0.1]
    out["C_defined"] = {"SF+E700": len(sfc), "SD": len(sdc)}
    (HERE / "w4_summary.json").write_text(json.dumps(out, indent=1))
    for gname, agg in out["groups"].items():
        print("==", gname, json.dumps(agg))
    print("SF vs SD est_confirmed MWU", out["SF_vs_SD_est_confirmed_mwu"], out["C_defined"])


if __name__ == "__main__":
    main()
