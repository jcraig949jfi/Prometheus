"""Step 4: tables from s1_multiseed.json (no VM runs)."""
import json, pathlib
from collections import Counter

D = json.loads(pathlib.Path(__file__).with_name("s1_multiseed.json").read_text())
OUT = pathlib.Path(__file__).with_suffix(".json")


def verdict(k, K=8):
    return "ACCEPT" if k >= 7 else "REJECT" if k <= 1 else "INDETERMINATE"


rows, C = [], Counter()
for r in D["rows"]:
    s = str(r["p11_side"])
    per = r["sides"][s]
    oth = r["sides"][str(1 - r["p11_side"])]
    rec = per[0]["CVTR_accept"]
    assert per[0]["record_reproduced"] and oth[0]["record_reproduced"]
    ko = sum(p["CVTR_accept"] for p in per[1:])
    kr = sum(p["RSTAR_accept"] for p in per[1:])
    kb = sum(p["base_fid_floor_ok"] for p in per[1:])
    ke = sum(a["CVTR_accept"] or b["CVTR_accept"] for a, b in zip(per[1:], oth[1:]))
    fp_like = sum(p["CVTR_accept"] and not p["base_fid_floor_ok"] for p in per[1:])
    x = {"key": r["key"], "cell": r["cell"], "side": r["p11_side"], "record_side": rec,
         "record_either": r["record_CVTR_accept_either"], "p_CVTR": ko / 8, "p_CVTR_either": ke / 8,
         "p_RSTAR": kr / 8, "p_base_floor": kb / 8, "seeds_accept_with_base_collapsed": fp_like,
         "verdict_CVTR_K8": verdict(ko), "verdict_RSTAR_K8": verdict(kr)}
    rows.append(x)
    g = "side%d" % r["p11_side"]
    C[g + "_n"] += 1
    C[g + "_record_accept"] += rec
    C[g + "_flip_vs_majority"] += rec != (ko >= 4.5)       # record vs majority of 8 (ties at 4 count as reject)
    C[g + "_tie4"] += ko == 4
    C[g + "_seed_dependent"] += 0 < ko < 8
    C[g + "_flip_either"] += r["record_CVTR_accept_either"] != (ke >= 4.5)
    C[g + "_" + x["verdict_CVTR_K8"]] += 1
    C[g + "_RSTAR_" + x["verdict_RSTAR_K8"]] += 1
    C[g + "_genomes_with_accept_on_collapsed_base"] += fp_like > 0
    C[g + "_sum_accepts"] += ko
    C[g + "_sum_rstar"] += kr
    C["all_flip_vs_majority"] += rec != (ko >= 4.5)
    C["all_seed_dependent"] += 0 < ko < 8
    # mean |record - p|: expected disagreement of a single seed with the K=8 estimate
    C["all_record_accept_but_p_le_0.5"] += rec and ko <= 4
    C["all_record_reject_but_p_ge_0.5"] += (not rec) and ko >= 4
hist = Counter((x["side"], x["p_CVTR"]) for x in rows)
OUT.write_text(json.dumps({"summary": C, "hist_side_p": {"%d:%.3f" % k: v for k, v in sorted(hist.items())},
                           "rows": rows}, indent=1))
print(json.dumps(C, indent=0, sort_keys=True))
print(sorted(hist.items()))
for x in rows:
    if x["record_side"] != (x["p_CVTR"] > 0.5) or 0 < x["p_CVTR"] < 1 or x["p_RSTAR"] != x["p_CVTR"]:
        print(x["key"], x["side"], "rec", int(x["record_side"]), "pC %.3f pE %.3f pR* %.3f floor %.3f collapsedAcc %d" % (
            x["p_CVTR"], x["p_CVTR_either"], x["p_RSTAR"], x["p_base_floor"], x["seeds_accept_with_base_collapsed"]))
