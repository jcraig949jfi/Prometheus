"""Negative-control crossover on engine plants + verdict-change table vs recorded verdicts."""
import csv, json
from collections import defaultdict
E = json.load(open("out/plants_engine_r0_P1S.json"))["cells"] + json.load(open("out/plants_engine_r0_P1SK.json"))["cells"]
checks = {"FLIP_REL": ("P1S", "S1"), "NO_EFFECT_REL": ("P1S", "S0"), "CHANCE_REL": ("P1S", "S1_half"),
          "CHANCE_REL(tie)": ("P1SK", "S"), "FLIP_REL(site_all)": ("P1SK", "site_all")}
wrong_input = {"FLIP_REL": ("P1S", "S0"), "NO_EFFECT_REL": ("P1S", "S1"), "CHANCE_REL": ("P1S", "S1"),
               "CHANCE_REL(tie)": ("P1SK", "site_all"), "FLIP_REL(site_all)": ("P1SK", "S")}
idx = {(c["plant"], c["arm"], c["q"]): c for c in E}
neg = []
for chk, (pl, arm) in checks.items():
    want = chk.split("(")[0]
    for q in sorted({c["q"] for c in E}):
        c = idx[(pl, arm, q)]
        if not c["verdict"] != "NOT_ELIGIBLE":
            continue
        w = idx[(wrong_input[chk][0], wrong_input[chk][1], q)]
        absf = {"FLIP_REL": "FLIP", "NO_EFFECT_REL": "NO-EFFECT", "CHANCE_REL": "CHANCE"}[want]
        neg.append({"check": chk, "q": q, "normal": round(c["normal"][0], 3), "right_input": arm, "right_pass": c["verdict"] == want,
                    "wrong_input": wrong_input[chk][1], "wrong_verdict": w["verdict"], "wrong_fails": w["verdict"] != want,
                    "absolute_on_right_input": c["absolute"], "absolute_pass": c["absolute"] == absf})
for n in neg:
    print(n)
# recorded verdicts
wl = json.load(open("../W-L/out/carriers_champs.json"))
mine = json.load(open("out/specimens_wl.json"))
rows = []
for tag, r in mine.items():
    for back in ("back0", "back1"):
        if back not in r:
            continue
        for arm, v in r[back].items():
            rec = wl.get(tag, {}).get(back, {}).get(arm, {}).get("verdict")
            rows.append(["W-L " + tag, back, arm, rec, v["absolute"], v["verdict"], round(v["normal"][0], 3), round(v["normal"][1], 3),
                         round(v["swap"][0], 3), round(v["swap"][1], 3), round(v["swap"][2], 3), None if v["z"] is None else round(v["z"], 2)])
wf = {r["cell"]: r for r in csv.DictReader(open("../W-F/out/census_table.csv"))}
c1 = json.load(open("out/specimens_c1.json"))
colmap = {("mid", "site_all"): "site_all", ("mid", "channel_all"): "channel_all", ("mid", "joint"): "joint",
          ("late", "site_all"): "late_site", ("late", "channel_all"): "late_chan"}
for cid, r in c1.items():
    for lab in ("mid", "late", "mid_every"):
        for arm, v in r[lab].items():
            rec = wf[cid[:8]].get(colmap.get((lab.replace("_every", ""), arm), ""), None)
            rows.append(["C1 " + cid[:8] + " " + r["family"], lab, arm, rec, v["absolute"], v["verdict"], round(v["normal"][0], 3),
                         round(v["normal"][1], 3), round(v["swap"][0], 3), round(v["swap"][1], 3), round(v["swap"][2], 3),
                         None if v["z"] is None else round(v["z"], 2)])
    for lab in ("mid_census", "late_census"):
        print(cid[:8], lab, r[lab]["class"], {k: r[lab][k] for k in ("eligible", "fS", "fC", "fN", "identity")})
hdr = ["specimen", "arm_time", "arm", "recorded(abs,M64)", "abs(mine)", "REL(mine)", "normal", "n_lo99", "swap", "s_lo99", "s_hi99", "z"]
with open("out/verdict_changes.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
for r in rows:
    print(" | ".join(str(x) for x in r))
json.dump({"negative_controls": neg}, open("out/negative_controls.json", "w"), indent=1)
