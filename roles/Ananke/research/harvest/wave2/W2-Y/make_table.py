"""W2-Y: merge verdict_table.json (light cone) + verdict_table_flood.json + task3_decay -> out/verdict_table.txt"""
import json, pathlib, collections
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
LC = json.load(open(HERE / "out/verdict_table.json"))
FL = {o["verdict"]: o for o in json.load(open(HERE / "out/verdict_table_flood.json"))}
DK = json.load(open(HERE / "out/task3_decay_B.json"))["rows"]
ref = collections.defaultdict(lambda: collections.defaultdict(list))
for d in DK:
    ref[(d["family"], d["base"])][d["li"]].append(d["refresh"])
FINAL = {("RELAY", "delta"): "IDENTITY (transport-time ceiling)", ("RELAY", "decay_shift"): "PLANT-DESIGN (vanishes under relay_refresh)",
         ("FLIP", "decay_shift"): "PLANT-DESIGN (vanishes under relay_refresh)",
         ("RELAY", "economy"): "NOT IDENTITY; energy budget (physics?) unresolved", ("MAJ", "economy"): "NOT IDENTITY; energy budget (physics?) unresolved",
         ("MAJ", "topology"): "IDENTITY (flood ceiling)", ("HOLD", "decay_shift"): "PLANT-DESIGN [I] (write-once latch x integer decay)",
         ("HOLD", "gap"): "PLANT-DESIGN [I] (same latch erosion, decay 1)"}
lines = ["# | verdict | label | means | LC ceil | LC pred/resid/class | FLOOD ceil | FLOOD pred/resid/class | B2 resid (flood or LC) | FINAL"]
for i, o in enumerate(LC, 1):
    v = f'{o["family"]} {o["dial"]} b{o["base"]} {o["track"]} {o["metric"]} {o["between"]}'
    lab = o["label"][15:]
    if o["metric"] not in ("acc", "plant"):
        lines.append(f'{i} | {v} | {lab} | {o["obs_means"]} | {o["ceil"]} | NA d_ceil={o["d_ceil"]} | - | - | - | PROGRAM-SPACE (not an accuracy metric)')
        continue
    f = FL.get(v)
    lc = f'{o["pred_step"]:+.3f}/{o["residual"]:+.3f}/{o["class"]}'
    fl = f'{f["pred"]:+.3f}/{f["resid"]:+.3f}/{f["class_flood"]}' if f else "-"
    b2 = f.get("B2_resid") if f else o.get("B2_resid")
    fin = FINAL.get((o["family"], o["dial"]), "")
    if o["family"] == "HOLD" and o["metric"] == "acc":
        fin = "NOT REPRODUCED (B2 jump sign reversed); ceiling flat"
    if o["dial"] == "decay_shift" and (o["family"], o["base"]) in ref and o["metric"] == "plant":
        r = ref[(o["family"], o["base"])]
        fin += " refresh means " + str([round(float(np.mean(r[k])), 3) for k in sorted(r)])
    lines.append(f'{i} | {v} | {lab} | {o["obs_means"]} | {o["ceil"]} | {lc} | {f["flood_ceil"] if f else "-"} | {fl} | {b2} | {fin}')
(HERE / "out/verdict_table.txt").write_text("\n".join(lines))
print("\n".join(lines))
