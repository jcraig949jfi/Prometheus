"""Per-row classification (reads out/*.json only; no engine runs).
PLANT-SOLVED: an in-genome-space member has held lo99 > .55 (C1 SIGNAL bar) AND mean > its own DICT
(single-sensor) mean; zero_comm is .500 for every member scored. PLANT-SOLVED-INT additionally lo99 > .70.
UNDECIDED otherwise; tag LC-P if the k=5 light-cone bound < .60 (no program can reach SIGNAL level),
tag INT-UNATTAINABLE(LC) if the bound <= .70. INT_LEAK rows are a post-hoc member (no dev selection)."""
import json, glob
import w2m_common as c
O = c.OUT
lc = {o["cell"]: o for o in json.load(open(O / "lc_maj.json"))["rows"]}
leak = {}
for f in glob.glob(str(O / "econ_check_*.json")):
    for o in json.load(open(f))["rows"]: leak[o["cell"]] = o
rows = []
for which in ("signal", "null"):
    for o in json.load(open(O / f"score_{which}.json"))["rows"]:
        cands = [(o["selected"], o["held"]["acc"], o["held"]["lo99"], o["DICT"]["acc"], "dev-selected")]
        if o["cell"] in leak:
            L = leak[o["cell"]]; cands.append(("INT_LEAK", L["acc"], L["lo99"], L["DICT"], "post-hoc"))
        best = max(cands, key=lambda x: x[2])
        solved = best[2] > 0.55 and best[1] > best[3]
        cls = ("PLANT-SOLVED-INT" if best[2] > 0.70 else "PLANT-SOLVED") if solved else "UNDECIDED"
        tags = []
        if lc[o["cell"]]["lc_bound"] < 0.60: tags.append("LC-P")
        elif lc[o["cell"]]["lc_bound"] <= 0.70: tags.append("INT-UNATTAINABLE(LC)")
        ovr = o.get("INT_2_override")
        rec = {"cell": o["cell"][:8], "set": which, "placement": o["placement"], "lc": round(lc[o["cell"]]["lc_bound"], 3),
               "champ": round(o["champ_held"], 3), "champ_lo99": round(o["champ_lo99"], 3),
               "member": best[0], "plant": round(best[1], 3), "plant_lo99": round(best[2], 3), "plant_DICT": round(best[3], 3),
               "class": cls, "tags": tags, "override_INT_2": round(ovr["acc"], 3) if ovr else None}
        if which == "signal":
            rec["plant_minus_champ_ci"] = [round(x, 3) for x in o["plant_minus_champ"][1:]]
            rec["dictplant_minus_champ_ci"] = [round(x, 3) for x in o["dictplant_minus_champ"][1:]]
            rec["champ_DICT"] = round(o["champ_DICT"]["acc"], 3)
            rec["FIRST"] = round(o["FIRST"]["acc"], 3)
        rows.append(rec)
c.save("classification.json", rows)
import collections
print(collections.Counter((r["set"], r["placement"] == "one_hop", r["class"]) for r in rows))
for r in rows:
    print(" | ".join(str(r.get(k)) for k in ("cell", "set", "placement", "lc", "champ", "champ_lo99", "member", "plant", "plant_lo99", "plant_DICT", "class", "tags", "override_INT_2", "champ_DICT", "FIRST", "plant_minus_champ_ci", "dictplant_minus_champ_ci")))
