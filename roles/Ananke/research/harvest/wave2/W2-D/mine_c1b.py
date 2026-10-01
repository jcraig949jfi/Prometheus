"""Refinements: plant-in-genome-space test, transect co-variation of plant vs evolved acc,
selector-noise ceiling from clear nulls, champion train/held reproducibility. No engine."""
import json, pathlib, collections
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / "out/mine_c1.json"))
import gzip
ROOT = HERE.parents[5]
R = {r["cell_id"]: r for r in (json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"))}
F = D["rows"]
out = {}
for fam, need in (("RELAY", 12), ("HOLD", 9), ("MAJ", 12)):
    xs = [x for x in F if x["fam"] == fam]
    for x in xs:
        x["L"] = R[x["cell"]]["physics"]["prog_len"]
    nul = [x for x in xs if not x["sig"]]
    inspace = [x for x in nul if x["L"] >= need]
    viable = [x for x in inspace if x["plant"] >= .75]
    viable90 = [x for x in inspace if x["plant"] >= .90]
    sig = [x for x in xs if x["sig"]]
    out[fam] = {"null": len(nul), "null_prog_len_fits_plant": len(inspace),
                "null_plant_ge_.75_in_space": len(viable), "null_plant_ge_.90_in_space": len(viable90),
                "null_plant_ge_.75_any_L": sum(1 for x in nul if x["plant"] >= .75),
                "signal_rows": len(sig), "signal_plant_ge_.75": sum(1 for x in sig if x["plant"] >= .75),
                "viable_null_held_median": round(float(np.median([x["held"] for x in viable])), 3) if viable else None,
                "viable_null_lo_gt_.5": sum(1 for x in viable if x["lo"] > .5)}
    print(fam, out[fam])
# MAJ note: relay_flood of one sensor gives ~1-flip_p; it is a partial plant, not a family solution.
# transects: within each (family, transect, base) group, Spearman-like sign agreement between plant and held
grp = collections.defaultdict(list)
for x in F:
    r = R[x["cell"]]
    e = r.get("extra", {})
    if r["wave"] in ("B", "B2") and "transect" in e:
        grp[(x["fam"], e["transect"], e["base"])].append((e["level_index"], x["plant"], x["held"]))
tr = []
for k, v in grp.items():
    lv = collections.defaultdict(list)
    for li, p, h in v:
        lv[li].append((p, h))
    idx = sorted(lv)
    if len(idx) < 3:
        continue
    P = np.array([np.mean([a for a, _ in lv[i]]) for i in idx]); H = np.array([np.mean([b for _, b in lv[i]]) for i in idx])
    c = float(np.corrcoef(P, H)[0, 1]) if P.std() > 0 and H.std() > 0 else None
    tr.append({"fam": k[0], "dial": k[1], "base": k[2], "levels": len(idx), "plant": P.round(3).tolist(),
               "held": H.round(3).tolist(), "corr": c,
               "plant_range": float(P.max() - P.min()), "held_range": float(H.max() - H.min())})
out["transects"] = tr
for t in tr:
    print(t["fam"], t["dial"], t["base"], "plant", t["plant"], "held", t["held"], "r", None if t["corr"] is None else round(t["corr"], 2))
# selector noise ceiling: late-gen max_acc (8 worlds) on clear nulls (hi99 < .55, lo99 <= .5)
cn = collections.defaultdict(list)
for x in F:
    if x["lo"] <= .5 and x["hi"] < .55:
        cn[x["fam"]].append(x["mx_last"])
out["selector_ceiling_clear_nulls"] = {f: {"n": len(v), "median": round(float(np.median(v)), 3), "q90": round(float(np.quantile(v, .9)), 3)} for f, v in cn.items()}
print("selector ceiling (late max_acc @ M=8 on clear nulls)", out["selector_ceiling_clear_nulls"])
# champion winner's curse: champ_train_final (M=16, max of 96) vs held for clear nulls
wc = collections.defaultdict(list)
for x in F:
    if x["lo"] <= .5:
        wc[x["fam"]].append(x["train_final"])
out["train_final_on_nulls"] = {f: {"n": len(v), "median": round(float(np.median(v)), 3), "q90": round(float(np.quantile(v, .9)), 3), "max": round(max(v), 3)} for f, v in wc.items()}
print("champ_train_final on held-null rows", out["train_final_on_nulls"])
# all FLIP/XOR evolve rows: physics digests and light-cone placement
for fam in ("FLIP", "XOR"):
    xs = [x for x in F if x["fam"] == fam]
    capped = [x for x in xs if x["lc"] is not None and x["lc"] < .60]
    out[fam + "_lc"] = {"evolve": len(xs), "lc_known": sum(1 for x in xs if x["lc"] is not None), "capped_lt_.60": len(capped),
                        "uncapped_null": sum(1 for x in xs if not x["sig"] and (x["lc"] is None or x["lc"] >= .60))}
    print(fam, out[fam + "_lc"])
json.dump(out, open(HERE / "out/mine_c1b.json", "w"), indent=1)
