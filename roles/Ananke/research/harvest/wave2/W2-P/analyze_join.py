"""Join task1 (champions), task1b (plant) and task2 (ceilings); per-family construction-capped counts."""
import json, pathlib, collections
import numpy as np
H = pathlib.Path(__file__).resolve().parent
ROOT = H.parents[5]
t1 = {o["cell"]: o for o in json.load(open(H / "out/task1_maj_inward.json"))["rows"]}
t1b = {o["cell"]: o for o in json.load(open(H / "out/task1b_plant_inward.json"))["rows"]}
t2 = {o["cell"]: o for o in json.load(open(H / "out/task2_timing.json"))["rows"]}
lc = json.load(open(ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"))["rows"]
import gzip
kind = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l); kind[r["cell_id"]] = (r["kind"], bool(r["labels"].get("SIGNAL")) if isinstance(r.get("labels"), dict) else None)
# Task 1 table
print("TASK1 table: cell8 | topo | mode | d | delta | rec held | KA | champ fresh orig/in (lo99 in) | plant fresh orig/in | ceil joint orig/in")
grp = collections.defaultdict(list)
for c, o in t1.items():
    p, q = t1b[c], t2[c]
    capped_in = q["ceil_joint_inward"] < q["signal_attainable"]
    capped_or = q["ceil_joint"] < q["signal_attainable"]
    grp["capped_inward" if capped_in else "open_inward"].append(o)
    print(f"{c[:8]} | {o['topology'][:5]} | {o['update_mode']} | {o['d']} | {o['delta']} | {o['rec_held_acc']:.3f} | {int(o['ka_exact'])} | "
          f"{o['fresh_orig']['acc']:.3f}/{o['fresh_in']['acc']:.3f} ({o['fresh_in']['lo99']:.3f}) | "
          f"{p['fresh_orig']['acc']:.3f}/{p['fresh_in']['acc']:.3f} | {q['ceil_joint']:.3f}/{q['ceil_joint_inward']:.3f}")
for k, v in grp.items():
    print(k, len(v), "champ mean fresh orig %.4f in %.4f" % (np.mean([o["fresh_orig"]["acc"] for o in v]), np.mean([o["fresh_in"]["acc"] for o in v])),
          "plant mean orig %.4f in %.4f" % (np.mean([t1b[o["cell"]]["fresh_orig"]["acc"] for o in v]), np.mean([t1b[o["cell"]]["fresh_in"]["acc"] for o in v])))
# per-family construction-capped NULL counts
res = {}
for fam in ("RELAY", "MAJ"):
    N = [o for o in t2.values() if o["family"] == fam and not o["SIGNAL"]]
    cap_joint = {o["cell"] for o in N if o["ceil_joint"] < o["signal_attainable"]}
    hpl = {o["cell"] for o in lc if o["family"] == fam and kind[o["cell"]] == ("evolve", False) and o["bound"] < 0.60}
    place = {o["cell"] for o in N if "ceil_joint_inward" in o and o["ceil_joint"] < o["signal_attainable"] <= o["ceil_joint_inward"]}
    res[fam] = {"NULL_evolve": len(N), "construction_capped": len(cap_joint | hpl),
                "of_which_placement_only": len(place), "hplant_lc_lt_.60": len(hpl),
                "hplant_not_in_mine": sorted(c[:8] for c in hpl - cap_joint),
                "mine_not_in_hplant": sorted(c[:8] for c in cap_joint - hpl)}
for fam in ("XOR", "FLIP"):
    xs = [o for o in lc if o["family"] == fam and kind[o["cell"]][0] == "evolve"]
    res[fam] = {"NULL_evolve": sum(1 for o in xs if not kind[o["cell"]][1]),
                "construction_capped_lc_only(H-PLANT bound<.60)": sum(1 for o in xs if o["bound"] < .60 and not kind[o["cell"]][1])}
print(json.dumps(res, indent=1))
json.dump(res, open(H / "out/construction_capped.json", "w"), indent=1)
