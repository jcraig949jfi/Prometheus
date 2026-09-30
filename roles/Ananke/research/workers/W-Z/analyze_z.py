"""PLAN s4 frozen outputs from out/runs_w*.jsonl -> out/row_table.csv, out/group_table.csv, out/summary.json."""
import collections
import csv
import glob
import json

import zcommon as Z

runs = {}
errors = []
cpu = 0.0
for fn in sorted(glob.glob(str(Z.OUT / "runs_w*.jsonl"))):
    for line in open(fn):
        if not line.strip():
            continue
        x = json.loads(line)
        cpu += x.get("cpu_s", 0.0)
        if "error" in x:
            errors.append((x["gid"], x["error"]))
            continue
        runs[tuple(x["group"])] = x
first, rest = Z.order()
G = Z.groups()
r3 = Z.rel3_rows()
wo = Z.wo_rows()

rows = []
for k in first + rest:
    if k not in runs:
        continue
    x = runs[k]
    for r in G[k]:
        u = r3[r["vid"]]
        v = x["arms"][r["arm"]]
        bound = u["rel3"].split("|")
        rows.append({"vid": r["vid"], "gid": x["gid"], "source": r["source"], "specimen": r["specimen"],
                     "family": r["family"], "arm": r["arm"], "offset": x["offset_used"],
                     "WO_abs_single": u["single"], "WO_every": wo[r["vid"]]["every"], "WQ_rel2": u["rel2"],
                     "WU_status": u["status"], "WU_rel3": u["rel3"], "WU_zclass": u["zclass"],
                     "new": v["label"], "new_transfer": v["transfer"], "new_certificate": v["certificate"],
                     "new_z": None if v["zci"]["z"] is None else round(v["zci"]["z"], 4),
                     "new_normal_lo": round(v["normal"][1], 4), "new_abs": v["abs"], "K": v["K"], "P": v["P"],
                     "new_in_rel3_bound": v["label"] in bound, "new_eq_rel2": v["label"] == u["rel2"]})
with open(Z.OUT / "row_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

amb = [r for r in rows if r["WU_status"] == "AMBIGUOUS"]
det = [r for r in rows if r["WU_status"] == "DETERMINED"]


def ct(sub, a, b):
    c = collections.Counter((r[a], r[b]) for r in sub)
    return {x: {y: n for (xx, y), n in sorted(c.items()) if xx == x} for x in sorted({r[a] for r in sub})}


groups = []
for k in first + rest:
    if k not in runs:
        continue
    x = runs[k]
    arms = x["arms"]
    rec = {a for a, v in arms.items() if v["recorded"]}
    cls = Z.group_class([(v["label"], v["transfer"]) for v in arms.values()])
    cls_rec = Z.group_class([(v["label"], v["transfer"]) for a, v in arms.items() if a in rec])
    groups.append({"gid": x["gid"], "priority": "AMBIG" if k in first else "REST", "source": k[0],
                   "specimen": k[2], "offset": x["offset_used"], "trial_set": k[4], "family": k[5],
                   "n_arms": len(arms), "arms_recorded": ",".join(sorted(rec)),
                   "flip_arms": ",".join(f"{a}:{v['transfer']}" for a, v in sorted(arms.items()) if v["label"] == "FLIP_REL"),
                   "labels": ";".join(f"{a}={v['label']}" for a, v in sorted(arms.items())),
                   "class": cls, "class_recorded_only": cls_rec,
                   "WU_rel3_labels": ";".join(sorted({r3[r['vid']]['rel3'] for r in G[k]}))})
with open(Z.OUT / "group_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(groups[0]))
    w.writeheader()
    w.writerows(groups)

cc = collections.Counter(g["class"] for g in groups)
cn = cc.get("CARRIER-NAMED", 0) / max(1, len(groups))
pa = sum(r["new_eq_rel2"] for r in amb)
cons = sum(r["new"] == r["WU_rel3"] for r in det)
S = {
    "coverage": {"groups_done": len(groups), "groups_total": len(G), "ambig_groups_done": sum(g["priority"] == "AMBIG" for g in groups),
                 "rows_done": len(rows), "rows_total": 733, "ambig_rows_done": len(amb), "determined_rows_done": len(det),
                 "errors": errors},
    "compute": {"specimen_cpu_s": round(cpu, 1), "specimen_core_h": round(cpu / 3600, 3)},
    "Pa": {"n": len(amb), "eq_rel2": pa, "frac": round(pa / max(1, len(amb)), 4), "bar": 0.70,
           "verdict": "HELD" if len(amb) == 64 and pa / 64 >= 0.70 else ("FAILED" if len(amb) == 64 else "INCOMPLETE"),
           "in_rel3_bound": sum(r["new_in_rel3_bound"] for r in amb),
           "rel3bound_x_new": ct(amb, "WU_rel3", "new"), "rel2_x_new": ct(amb, "WQ_rel2", "new"),
           "rows": [(r["vid"], r["specimen"][:8], r["arm"], r["offset"], r["WQ_rel2"], r["WU_rel3"], r["new"],
                     r["new_transfer"], r["new_z"]) for r in amb]},
    "Pb": {"classes": dict(cc), "classes_recorded_only": dict(collections.Counter(g["class_recorded_only"] for g in groups)),
           "carrier_named_frac": round(cn, 4), "band": [0.25, 0.45],
           "verdict": "HELD" if 0.25 <= cn <= 0.45 else "FAILED",
           "classes_ambig_groups": dict(collections.Counter(g["class"] for g in groups if g["priority"] == "AMBIG")),
           "classes_by_source": ct(groups, "source", "class"), "classes_by_family": ct(groups, "family", "class")},
    "consistency": {"n": len(det), "eq": cons, "frac": round(cons / max(1, len(det)), 4), "bar": 0.95,
                    "verdict": "PASS" if cons / max(1, len(det)) >= 0.95 else "BELOW_BAR",
                    "rel3_x_new": ct(det, "WU_rel3", "new"),
                    "disagreements": [(r["vid"], r["specimen"][:8], r["arm"], r["offset"], r["WU_rel3"], r["new"],
                                       r["new_z"], r["new_normal_lo"]) for r in det if r["new"] != r["WU_rel3"]]},
    "new_marginal": dict(collections.Counter(r["new"] for r in rows)),
    "flip_transfer": dict(collections.Counter(r["new_transfer"] for r in rows if r["new"] == "FLIP_REL")),
    "abs_single_x_new": ct(rows, "WO_abs_single", "new"),
}
json.dump(S, open(Z.OUT / "summary.json", "w"), indent=1, default=str)
for k in ("coverage", "compute"):
    print(k, json.dumps(S[k]))
print("Pa", {k: S["Pa"][k] for k in ("n", "eq_rel2", "frac", "verdict", "in_rel3_bound")})
print("Pa rel3bound_x_new", json.dumps(S["Pa"]["rel3bound_x_new"]))
print("Pa rel2_x_new", json.dumps(S["Pa"]["rel2_x_new"]))
print("Pb", {k: S["Pb"][k] for k in ("classes", "classes_recorded_only", "carrier_named_frac", "verdict", "classes_ambig_groups")})
print("consistency", {k: S["consistency"][k] for k in ("n", "eq", "frac", "verdict")})
print("consistency rel3_x_new", json.dumps(S["consistency"]["rel3_x_new"]))
print("new_marginal", S["new_marginal"], "flip_transfer", S["flip_transfer"])
