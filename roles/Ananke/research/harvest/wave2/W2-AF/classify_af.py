"""Classify task-1 (MAJ) and task-2 (RELAY) cells from saved out/ files only (no engine runs), then update
W2-W's eligibility counts and denominator table. Writes out/task1_table.csv, out/task2_table.csv,
out/denominator_update.json.
MAJ rules (dev-selected member over the 7-member a priori menu, scored on the row's 64 held worlds):
  PLANT_SOLVED_IN_SPACE/strict : held lo99 > .55 and paired (member - DICT) 99% lo > 0
  PLANT_SOLVED_IN_SPACE/weak   : held lo99 > .55 and mean > DICT mean, paired lo <= 0
  PLANT_SOLVED_OVERRIDE        : no in-space pass; genome-raised INT_1/INT_2 (<= 16 lines) lo99 > .55
  UNDECIDED                    : otherwise
  flags: INT_LEAK_ONLY (sel_af = INT_LEAK and the 6-member W2-M selection fails); NO_INTEGRATION_REACH (the
  member hears only lane-1 = one-hop sensors and the row's mean count of one-hop sensors is < 3, so its
  'strict' pass cannot be integration: W2-M's DICT cues sensor 0, which envs.build places FARTHEST).
RELAY rules (task 2): P_PROVEN(EC) if the epidemic-cone bound's 99.9% upper end < .60; otherwise the binding
  dial(s) from single-dial neutralisation (>= .60 on 16 worlds); the variant step was not run (compute cap), so
  no cell can be PLANT_SOLVED or P_CANDIDATE under the brief's definitions and the rest stay UNDECIDED."""
import json, csv, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; O = HERE / "out"
P = {p["cell"]: p for p in csv.DictReader(open(HERE.parent / "W2-W/null_placement.csv"))}
LC = {x["cell"]: x for x in json.load(open(HERE.parent / "W2-M/out/lc_maj.json"))["rows"]}
LANE1 = {"INT_CO", "INT_1", "INT_1A6", "INT_1G", "INT_LEAK", "FIRST"}

# ---------------- task 1
t1 = []
for l in open(O / "task1_rows.jsonl"):
    o = json.loads(l); s = o["sel_af"]; h = o["held"][s]
    tier = "UNDECIDED"
    if h["lo99"] > .55 and h["acc"] > h["DICT"]:
        tier = "PLANT_SOLVED_IN_SPACE/strict" if h["int_minus_dict"][1] > 0 else "PLANT_SOLVED_IN_SPACE/weak"
    elif "override" in o and "lo99" in o["override"] and o["override"]["lo99"] > .55:
        tier = "PLANT_SOLVED_OVERRIDE" + ("/strict" if o["override"]["int_minus_dict"][1] > 0 else "/weak")
    flags = []
    w = o["sel_w2m"]
    w_pass = bool(w and o["held"][w]["lo99"] > .55)
    if tier.startswith("PLANT") and s == "INT_LEAK" and not w_pass: flags.append("INT_LEAK_ONLY")
    n1 = LC[o["cell"]]["mean_sensors_one_hop"]
    if tier.endswith("strict") and s in LANE1 and n1 < 3: flags.append("NO_INTEGRATION_REACH(n1=%.1f)" % n1)
    p = P[o["cell"]]
    t1.append({"cell": o["cell"], "w2w_class": o["w2w_class"], "w2m_scored": o["w2m_scored"], "placement": o["placement"],
               "topology": o["topology"], "update": o["update_mode"], "cap": f'{o["cap"]}/{o["collision"]}', "economy": o["economy"],
               "genome": "%d/%d/%d" % tuple(o["genome_space"].values()), "lc_bound": round(o["lc_bound"], 3),
               "sel_af": s, "sel_w2m": w, "acc": round(h["acc"], 3), "lo99": round(h["lo99"], 3), "DICT": round(h["DICT"], 3),
               "int_minus_dict_lo": round(h["int_minus_dict"][1], 3),
               "w2m_menu_acc": round(o["held"][w]["acc"], 3) if w else None, "w2m_menu_lo99": round(o["held"][w]["lo99"], 3) if w else None,
               "zero_comm": o["zero_comm_sel_af"], "override": (f'{o["override"]["member"]} {o["override"]["acc"]:.3f}/{o["override"]["lo99"]:.3f}'
                                                                 if "override" in o and "lo99" in o["override"] else (o.get("override") or {}).get("note", "")),
               "champ_held": round(o["champ_held"], 3), "plant_tier": tier, "flags": ";".join(flags),
               "admissible": p["admissible"], "marginal": p["w2t_marginal"]})
with open(O / "task1_table.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(t1[0])); wr.writeheader(); wr.writerows(t1)

# ---------------- task 2
EC = {x["cell"]: x for x in json.load(open(O / "epicone.json"))["rows"]}
DL = {json.loads(l)["cell"]: json.loads(l) for l in open(O / "task2_dials.jsonl")}
t2 = []
for cid, d in DL.items():
    e = EC[cid]; res = d["res"]
    single = {k: v[0] for k, v in res.items() if k not in ("actual", "ALL")}
    bind = sorted([k for k, v in single.items() if v >= .60], key=lambda k: -single[k])
    if e["EC_bound_upper"] < .60:
        cls = "P_PROVEN(EC)"
    else:
        cls = "UNDECIDED"
    kind = ("single:" + ",".join(bind)) if bind else ("conjunctive(ALL=%.2f)" % res["ALL"][0] if res["ALL"][0] >= .60 else "none(ALL=%.2f)" % res["ALL"][0])
    p = P[cid]
    t2.append({"cell": cid, "w2w_class": p["final_class"], "admissible": p["admissible"], "w2w_best_bound": p["best_bound"],
               "EC_bound": round(e["EC_bound"], 3), "EC_upper": round(e["EC_bound_upper"], 3), "P_informed": round(e["P_informed"], 3),
               "refresh_actual16": round(res["actual"][0], 3), "ALL_off": round(res["ALL"][0], 3),
               **{f"rm_{k}": round(v, 3) for k, v in single.items()}, "binding": kind, "class": cls})
keys = sorted({k for r in t2 for k in r}, key=lambda k: (not k.startswith(("cell", "w2w", "adm", "EC", "P_", "refresh", "ALL")), k))
with open(O / "task2_table.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=["cell", "w2w_class", "admissible", "w2w_best_bound", "EC_bound", "EC_upper", "P_informed",
                                       "refresh_actual16", "ALL_off", "rm_update", "rm_loss", "rm_cap", "rm_jitter", "rm_noise",
                                       "rm_economy", "rm_dest", "rm_dup", "binding", "class"])
    wr.writeheader(); wr.writerows(t2)

# ---------------- counts
C1 = collections.Counter((r["w2w_class"], r["plant_tier"]) for r in t1)
C2 = collections.Counter((r["w2w_class"], r["class"], r["binding"].split(":")[0].split("(")[0]) for r in t2)
summary = {"task1_counts": {f"{a} -> {b}": n for (a, b), n in C1.items()},
           "task1_flags": collections.Counter(f for r in t1 for f in r["flags"].split(";") if f).most_common(),
           "task2_counts": {f"{a} -> {b} [{c}]": n for (a, b, c), n in C2.items()},
           "task1_n": len(t1), "task2_n": len(t2)}
json.dump(summary, open(O / "denominator_update.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
for r in t1:
    print(r["cell"][:8], r["placement"][:5], r["topology"][:5], r["sel_af"], "%.3f/%.3f D %.3f dlo %.3f" % (r["acc"], r["lo99"], r["DICT"], r["int_minus_dict_lo"]),
          r["plant_tier"], r["flags"], "adm", r["admissible"], "marg", r["marginal"], "ovr", r["override"])
for r in t2:
    print(r["cell"][:8], r["EC_upper"], r["binding"], r["class"], r["admissible"])
