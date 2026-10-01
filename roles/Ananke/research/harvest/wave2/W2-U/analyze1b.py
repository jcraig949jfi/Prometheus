import json, pathlib
H = pathlib.Path(__file__).resolve().parent
d = json.load(open(H / "out/task1b_big.json"))["rows"]
t1 = {o["cell"]: o for o in json.load(open(H / "out/task1_xor_flip.json"))["rows"]}
w2p = {o["cell"]: o for o in json.load(open(H.parent / "W2-P/out/task2_timing.json"))["rows"]}
S = {}
for fam in ("RELAY", "MAJ", "XOR", "FLIP"):
    rs = [o for o in d if o["family"] == fam]
    N = [o for o in rs if not o["SIGNAL"]]
    def c(src, key, rows=N): return sum(1 for o in rows if o[src][key] < o["thr"])
    s = {"evolve": len(rs), "SIGNAL": len(rs) - len(N), "NULL": len(N),
         "big_lc": c("big", "lc"), "big_joint": c("big", "joint"),
         "held_lc": c("held", "lc"), "held_joint": c("held", "joint"),
         "big_joint_le_.55": sum(o["big"]["joint"] <= .55 for o in N),
         "held_joint_le_.55": sum(o["held"]["joint"] <= .55 for o in N),
         "big_and_held_joint": sum(1 for o in N if o["big"]["joint"] < o["thr"] and o["held"]["joint"] < o["thr"]),
         "either_big_or_held_joint": sum(1 for o in N if o["big"]["joint"] < o["thr"] or o["held"]["joint"] < o["thr"]),
         "borderline_big(thr±.03)": sum(1 for o in N if abs(o["big"]["joint"] - o["thr"]) < .03)}
    if fam == "FLIP":
        s.update(big_block=c("big", "joint_block"), held_block=c("held", "joint_block"),
                 big_copy=c("big", "copy_block"), held_copy=c("held", "copy_block"))
    if fam in ("XOR", "FLIP"):
        s["fresh128_joint"] = sum(1 for o in N if t1[o["cell"]]["ceil"]["joint"] < o["thr"])
        s["hplant_lc_.60"] = sum(1 for o in N if t1[o["cell"]]["hplant_lc"] < .60)
    else:
        s["w2p_fresh128_joint"] = sum(1 for o in N if w2p[o["cell"]]["ceil_joint"] < w2p[o["cell"]]["signal_attainable"])
    s["sig_violations_big"] = [(o["cell"][:8], o["held_acc"], o["big"]["joint"]) for o in rs if o["SIGNAL"] and o["held_lo99"] > o["big"]["joint"]]
    s["sig_violations_held"] = [(o["cell"][:8], o["held_lo99"], o["held"]["joint"]) for o in rs if o["SIGNAL"] and o["held_lo99"] > o["held"]["joint"]]
    sig = [o for o in rs if o["SIGNAL"]]
    if sig:
        s["sig_min_margin_held(ceil-acc)"] = min((round(o["held"]["joint"] - o["held_acc"], 3), o["cell"][:8]) for o in sig)
    s["any_lo99_gt_heldceil"] = [(o["cell"][:8], o["held_lo99"], round(o["held"]["joint"], 3)) for o in rs if o["held_lo99"] > o["held"]["joint"] + 1e-9]
    # time/async decomposition
    s["async_added_big"] = sorted(o["cell"][:8] for o in N if o["big"]["joint"] < o["thr"] <= o["big"]["lc"])
    S[fam] = s
tot = {k: sum(S[f][k] for f in S) for k in ("NULL", "big_joint", "held_joint", "big_and_held_joint", "either_big_or_held_joint")}
S["TOTAL"] = tot
json.dump(S, open(H / "out/task1b_summary.json", "w"), indent=1)
print(json.dumps(S, indent=1))
