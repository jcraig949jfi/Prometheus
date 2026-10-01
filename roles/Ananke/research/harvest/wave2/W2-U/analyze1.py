"""Per-family construction-capped NULL table (XOR/FLIP from task1, RELAY/MAJ from W2-P out/construction_capped + task2)."""
import json, pathlib, collections
H = pathlib.Path(__file__).resolve().parent
d = json.load(open(H / "out/task1_xor_flip.json"))
w2p = json.load(open(H.parent / "W2-P/out/task2_timing.json"))["rows"]
cc = json.load(open(H.parent / "W2-P/out/construction_capped.json"))
out = {}
def cnt(rows, key, thr_key="signal_attainable"):
    return sum(1 for o in rows if key(o) < o[thr_key])
for fam in ("XOR", "FLIP"):
    rs = [o for o in d["rows"] if o["family"] == fam]
    N = [o for o in rs if not o["SIGNAL"]]
    f = {"evolve": len(rs), "SIGNAL": len(rs) - len(N), "NULL": len(N),
         "thr_values": sorted({round(o["signal_attainable"], 4) for o in rs}),
         "hplant_lc_lt_.60": sum(o["hplant_lc"] < .60 for o in N),
         "lc_lt_thr": cnt(N, lambda o: o["ceil"]["lc"]),
         "joint_strict_lt_thr": cnt(N, lambda o: o["ceil"]["joint"]),
         "joint_le_.55": sum(o["ceil"]["joint"] <= .55 for o in N),
         "joint_lt_.60": sum(o["ceil"]["joint"] < .60 for o in N)}
    if fam == "FLIP":
        f["joint_block_lt_thr"] = cnt(N, lambda o: o["ceil"]["joint_block"])
        f["copy_block_lt_thr"] = cnt(N, lambda o: o["ceil"]["copy_block"])
        f["joint_block_le_.55"] = sum(o["ceil"]["joint_block"] <= .55 for o in N)
    lc_set = {o["cell"] for o in N if o["ceil"]["lc"] < o["signal_attainable"]}
    j_set = {o["cell"] for o in N if o["ceil"]["joint"] < o["signal_attainable"]}
    f["timing_added_strict"] = sorted(c[:8] for c in j_set - lc_set)
    if fam == "FLIP":
        b_set = {o["cell"] for o in N if o["ceil"]["joint_block"] < o["signal_attainable"]}
        f["timing_added_block"] = sorted(c[:8] for c in b_set - lc_set)
    hp = {o["cell"] for o in N if o["hplant_lc"] < .60}
    f["hplant_not_in_lc_thr"] = sorted(c[:8] for c in hp - lc_set)
    f["lc_thr_not_in_hplant"] = sorted(c[:8] for c in lc_set - hp)
    # held-set checks
    f["held_lo99_gt_heldset_joint"] = [(o["cell"][:8], o["held_lo99"], o["ceil_heldset"]["joint"]) for o in rs if o["held_lo99"] > o["ceil_heldset"]["joint"]]
    f["held_acc_gt_heldset_joint"] = [(o["cell"][:8], o["held_acc"], round(o["ceil_heldset"]["joint"], 3)) for o in rs if o["held_acc"] > o["ceil_heldset"]["joint"] + 1e-9]
    f["max_held_lo99"] = max(o["held_lo99"] for o in rs)
    # by mode
    f["by_mode"] = {m: {"NULL": sum(o["update_mode"] == m for o in N),
                        "lc_capped": sum(o["update_mode"] == m and o["ceil"]["lc"] < o["signal_attainable"] for o in N),
                        "joint_capped": sum(o["update_mode"] == m and o["ceil"]["joint"] < o["signal_attainable"] for o in N),
                        "mean_lc": round(sum(o["ceil"]["lc"] for o in N if o["update_mode"] == m) / max(1, sum(o["update_mode"] == m for o in N)), 3),
                        "mean_joint": round(sum(o["ceil"]["joint"] for o in N if o["update_mode"] == m) / max(1, sum(o["update_mode"] == m for o in N)), 3),
                        **({"mean_joint_block": round(sum(o["ceil"]["joint_block"] for o in N if o["update_mode"] == m) / max(1, sum(o["update_mode"] == m for o in N)), 3)} if fam == "FLIP" else {})}
                    for m in ("sync", "async")}
    out[fam] = f
for fam in ("RELAY", "MAJ"):
    rs = [o for o in w2p if o["family"] == fam]
    N = [o for o in rs if not o["SIGNAL"]]
    out[fam] = {"evolve": len(rs), "SIGNAL": len(rs) - len(N), "NULL": len(N),
                "joint_strict_lt_thr(W2-P)": cc[fam]["construction_capped"],
                "lc_lt_thr": sum(o["ceil_lc"] < o["signal_attainable"] for o in N),
                "joint_lt_thr": sum(o["ceil_joint"] < o["signal_attainable"] for o in N),
                "joint_le_.55": sum(o["ceil_joint"] <= .55 for o in N)}
json.dump(out, open(H / "out/task1_summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
