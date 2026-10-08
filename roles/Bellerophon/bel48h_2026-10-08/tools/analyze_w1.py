"""BEL-48H Window 1 v2 analysis (rules: BEL_48H_PREREG.md s3 + amendment 1; committed before W1 v2 results exist).

    python3 analyze_w1.py RESULTS.jsonl OUT.json"""
import json
import math
import random
import sys
from collections import Counter, defaultdict

from analyze_w2 import wilson


def mcnemar_exact(b, c):
    """two-sided exact McNemar on discordant counts b (only first), c (only second)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n), 6)


def var(xs):
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def main(res_path, out_path):
    R = [json.loads(l) for l in open(res_path)]
    voids = [r for r in R if r.get("void")]
    R = [r for r in R if not r.get("void")]
    out = {"n_results": len(R) + len(voids), "voids": len(voids), "void_ids": [v["id"] for v in voids][:50]}
    # ---- lane A: physics invariance -------------------------------------------------------------------------------------
    for lane in ("A1", "A2", "A3", "A4"):
        by = defaultdict(dict)
        for r in R:
            if r["lane"] == lane:
                by[(r["cell"], r["pair"])][r["arm"]] = r["end_hash"]
        full = {k: v for k, v in by.items() if len(v) == 2}
        same = sum(1 for v in full.values() if len(set(v.values())) == 1)
        out[lane] = {"pairs": len(full), "identical": same, "differ": len(full) - same,
                     "differ_by_cell": dict(Counter(k[0] for k, v in full.items() if len(set(v.values())) > 1))}
    out["W1-P1"] = {"holds": out["A1"]["pairs"] == 100 and out["A1"]["differ"] == 0, **out["A1"]}
    out["W1-P2"] = {"holds": out["A2"]["differ"] >= 1, **out["A2"]}
    out["W1-P3"] = {"holds": out["A3"]["pairs"] == 100 and out["A3"]["differ"] == 0 and out["A4"]["differ"] >= 19,
                    "A3": out["A3"], "A4": out["A4"]}
    # ---- lane B: dual-ruler baseline -------------------------------------------------------------------------------------
    B = [r for r in R if r["lane"] in ("B1", "B2")]
    tot = Counter()
    for r in B:
        tot.update(r["dual"]["B"])
    sr_res = tot["sr_res"]
    # SR_res and SR_prov differ: count per run |sr_res - sr_prov| is a lower bound; births-level disagreement needs rows,
    # so use the pooled difference of counts AND the per-run max as the frozen proxy (documented in the report)
    diff_lb = sum(abs(r["dual"]["B"].get("sr_res", 0) - r["dual"]["B"].get("sr_prov", 0)) for r in B)
    out["W1-P4"] = {"sr_res_births": sr_res, "sr_res_vs_prov_count_diff": diff_lb,
                    "frac_diff": round(diff_lb / sr_res, 5) if sr_res else None,
                    "sr_res_not_func_child": tot["sr_res_not_func_child"],
                    "frac_not_func": round(tot["sr_res_not_func_child"] / sr_res, 5) if sr_res else None,
                    "func_child_not_sr_res": tot["func_child_not_sr_res"]}
    out["W1-P4"]["holds"] = (sr_res > 0 and diff_lb / sr_res < 0.01 and tot["sr_res_not_func_child"] / sr_res < 0.05) if sr_res else "NOT_TESTABLE"
    cells = defaultdict(list)
    for r in R:
        if r["lane"] in ("B1", "B2", "B3"):
            cells[r["lane"] + ":" + r["cell"]].append(r)
    per = {}
    b1_res = b1_trb = 0; b1_n = 0; mc_b = mc_c = 0
    sus_hist = sus_trb = 0; spont_trb_runs = 0
    g6 = [0, 0]
    for c, rs in sorted(cells.items()):
        n = len(rs)
        sres = [r["dual"]["B"].get("sr_res", 0) > 0 for r in rs]
        strb = [r["dual"]["B"].get("trb", 0) > 0 for r in rs]
        hist_sus = [(r["summary"]["sr_max_depth"] or 0) >= 3 and (r["summary"]["sr_alive_end"] or 0) > 0 for r in rs]
        trb_sus = [r["dual"]["trb_max_depth"] >= 3 and r["dual"]["trb_alive"] > 0 for r in rs]
        conf = Counter()
        for r in rs:
            conf.update({k: v for k, v in r["dual"]["B"].items() if k.startswith("res_")})
        births = sum(r["dual"]["B"].get("births", 0) for r in rs)
        per[c] = {"runs": n, "extinct": sum(r["summary"]["extinct"] for r in rs),
                  "spont_res": sum(sres), "spont_res_wilson": wilson(sum(sres), n),
                  "spont_trb": sum(strb), "spont_trb_wilson": wilson(sum(strb), n),
                  "sustained_hist": sum(hist_sus), "sustained_trb": sum(trb_sus),
                  "births": births, "confusion": dict(conf),
                  "ruler_disagree_frac_births": round(sum(v for k, v in conf.items() if k.split("__")[0][4:] != k.split("__")[1][5:]) / births, 4) if births else None,
                  "mixed_origin_frac": round(sum(r["dual"]["B"].get("mixed_origin", 0) for r in rs) / births, 4) if births else None,
                  "constructed_frac": round(sum(r["dual"]["B"].get("constructed", 0) for r in rs) / births, 4) if births else None,
                  "alive_root_disagree_mean": round(sum(r["dual"]["glin_root_disagree_alive"] / max(1, r["dual"]["n_alive"]) for r in rs) / n, 4),
                  "trb_signatures_pooled": len({tuple(x[0]) for r in rs for x in r["dual"]["trb_mech_top"]}),
                  "geom_disagree": sum(1 for r in rs for g in (r["geom"] or {}).values() if g and g["v1"] != g["written"]),
                  "geom_n": sum(1 for r in rs for g in (r["geom"] or {}).values() if g)}
        if c.startswith("B1:"):
            b1_n += n; b1_res += sum(sres); b1_trb += sum(strb)
            mc_b += sum(1 for a, b in zip(sres, strb) if a and not b); mc_c += sum(1 for a, b in zip(sres, strb) if b and not a)
        if c.startswith(("B1:", "B2:")):
            for r, t, hs, ts in zip(rs, strb, hist_sus, trb_sus):
                if t:
                    spont_trb_runs += 1; sus_hist += hs; sus_trb += ts
                    ft = r["dual"]["first"].get("trb") or {}
                    g6[1] += 1; g6[0] += ft.get("writer_mech", "init") != "init"
    out["cells"] = per
    out["W1-P5"] = {"spont_res": [b1_res, b1_n], "spont_trb": [b1_trb, b1_n], "wilson_trb": wilson(b1_trb, b1_n),
                    "mcnemar_only_res": mc_b, "only_trb": mc_c, "p": mcnemar_exact(mc_b, mc_c),
                    "holds": b1_trb > 0 and (wilson(b1_trb, b1_n)[0] or 0) > 0 and mc_c == 0,
                    "per_cell_G1_survives": {c[3:]: per[c]["spont_trb"] >= 1 for c in per if c.startswith("B1:")}}
    out["W1-P6"] = {"spont_trb_runs": spont_trb_runs, "sustained_hist": sus_hist, "sustained_trb": sus_trb,
                    "rates": [round(sus_hist / spont_trb_runs, 4), round(sus_trb / spont_trb_runs, 4)] if spont_trb_runs else None,
                    "holds": abs(sus_hist - sus_trb) / spont_trb_runs <= 0.10 if spont_trb_runs else "NOT_TESTABLE"}
    out["W1-P7"] = {"copy_born_first_trb_writers": g6, "holds": (g6[0] / g6[1] >= 0.9) if g6[1] else "NOT_TESTABLE"}
    # ---- controls ----------------------------------------------------------------------------------------------------------
    ctl = {}
    for c in ("pos_seeded_replicator", "cheat_bare_ldir", "cheat_smear", "cheat_capture_partial"):
        rs = cells.get("B3:" + c, [])
        if c.startswith("pos"):
            ctl[c] = {"sustained_trb": per.get("B3:" + c, {}).get("sustained_trb"), "runs": len(rs), "ok": (per.get("B3:" + c, {}).get("sustained_trb") or 0) >= 27}
        else:
            z = sum(1 for r in rs if r["dual"]["B"].get("trb", 0) == 0)
            ctl[c] = {"zero_trb_runs": z, "runs": len(rs), "ok": z == len(rs) == 30}
    out["controls"] = ctl
    # ---- lane C: pairing -------------------------------------------------------------------------------------------------
    C = [r for r in R if r["lane"] == "C1"]
    pc = {}
    for arm in ("HISTORICAL", "PAIRED"):
        rs = [r for r in C if r["arm"] == arm]
        dv = [r["rng_div_tick"] for r in rs]
        diffs = [r["a"]["summary"]["final_alive"] - r["b"]["summary"]["final_alive"] for r in rs]
        pc[arm] = {"pairs": len(rs), "init_rng_equal": sum(r["init_rng_equal"] for r in rs),
                   "rng_div_le5": sum(1 for d in dv if d is not None and d <= 5), "rng_never_div": sum(1 for d in dv if d is None),
                   "rng_div_ticks": dict(Counter(dv)), "diff_final_alive_mean": round(sum(diffs) / len(diffs), 3) if diffs else None,
                   "diff_var": round(var(diffs), 3) if len(diffs) > 1 else None, "_diffs": diffs}
    if all(pc.get(a, {}).get("_diffs") for a in ("HISTORICAL", "PAIRED")):
        rng = random.Random(4801); h, p = pc["HISTORICAL"]["_diffs"], pc["PAIRED"]["_diffs"]
        ratios = sorted(var([rng.choice(p) for _ in p]) / max(1e-9, var([rng.choice(h) for _ in h])) for _ in range(2000))
        ci = [round(ratios[49], 4), round(ratios[1949], 4)]
        pv = pc["PAIRED"]
        out["W1-P8"] = {"var_ratio_paired_over_hist": round(var(p) / var(h), 4), "ci95": ci,
                        "div_le5_share_paired": round(pv["rng_div_le5"] / pv["pairs"], 4),
                        "holds": pv["rng_div_le5"] / pv["pairs"] >= 0.9 and ci[1] >= 0.8}
    for a in pc:
        pc[a].pop("_diffs", None)
    out["C1"] = pc
    # ---- W1-P9 geometry ------------------------------------------------------------------------------------------------------
    gc = {c: (per[c]["geom_disagree"], per[c]["geom_n"]) for c in per}
    copy_cells = [v for c, v in gc.items() if "ENDOGENOUS_COPY" in c]
    dis = sum(v[0] for v in copy_cells); nn = sum(v[1] for v in copy_cells)
    out["W1-P9"] = {"copy_agree": [nn - dis, nn], "by_cell": gc, "holds": ((nn - dis) / nn >= 0.95) if nn else "NOT_TESTABLE"}
    json.dump(out, open(out_path, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in out if k.startswith("W1-") or k == "controls"}, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
