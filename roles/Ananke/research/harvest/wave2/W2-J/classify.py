"""Per-row classification of all 83 XOR evolve rows (no engine; reads out/*.json). Writes out/table.json, out/table.md.
PLANT-SOLVED: a scored W2-J plant has lo99 > .60 on 64 fresh worlds (tier ext = prog_len > 16; c1 = <= 16 lines,
              genome-space override only; strict = row's own genome fields).
CAPPED-LC1:   H-PLANT census light cone < .60 (the given 36).
CAPPED-LC2:   W2-J reach bound (async wake incl. sensors, loss, fanout, dup, jitter) < .60 on 64 fresh worlds
              (point estimate; 'robust' if its 99% world-bootstrap upper limit is also < .60).
UNDECIDED:    neither."""
from wj_common import *

rows = {o["cell"]: o for o in json.load(open(OUT / "rows83.json"))}
LC = lc()
R = {o["cell"]: o for o in json.load(open(OUT / "lc_robust.json"))["rows"]}
scored = {}
for f in ("score_A.json", "score_C1.json"):
    for s in json.load(open(OUT / f))["rows"]:
        scored.setdefault(s["cell"], []).append(s)
dev = {}
for f in ("screen2.json", "screen3_clk4a.json", "screen3_clk4b.json", "screen3_ttlws.json", "screen3_clk3a.json"):
    for s in json.load(open(OUT / f))["rows"]:
        if s["cell"] not in dev or s["acc"] > dev[s["cell"]]["acc"]:
            dev[s["cell"]] = s
cheat_dev = {s["cell"]: s for s in json.load(open(OUT / "dev_cheat_U.json"))["rows"]}
table = []
for c, o in rows.items():
    p = o["phys"]
    lc1 = LC[c]["bound"]
    rb = R[c]
    rec = {"cell": c, "wave": o["wave"], "env": f"d{o['env']['d']} dl{o['env']['delta']}",
           "phys": f"{p['topology']}{p['n_sites']} r{p['radius']} {p['dest_mode']}/f{p['fanout']} "
                   f"{p['update_mode']}{'' if p['update_mode'] == 'async' else p['update_period']}"
                   f"{'' if p['update_mode'] == 'sync' else ' p' + str(p['update_p'])} loss{p['loss']}{'/hop' if p['loss_per_hop'] else ''} "
                   f"cap{p['cap']}{p['collision'][:3]} dec{p['decay_shift']} nz{p['noise']} lat{p['lat_base']}+{p['lat_hop']}~{p['lat_jitter']} "
                   f"dup{p['dup']} L{p['prog_len']} D{p['state_dim']} P{p['payload_width']} C{p['channels']} mut{p['mut_site']} "
                   f"eco{p['e_income']}/{p['c_emit']}/{p['c_op']}/{p['c_mem']}/{p['e_max']}",
           "held_acc": o["held_acc"], "held_lo99": o["held_lo99"], "lc1_census": lc1,
           "lc1_fresh": rb["lc1"], "lc2": rb["lc2"], "lc2_ci99": rb["lc2_ci99"], "econ": p["c_op"] > 0}
    best = None
    for s in scored.get(c, []):
        n = s["normal"]
        if best is None or n["lo99"] > best["lo99"]:
            best = {"tier": "c1" if s["len"] <= 16 else "ext", "fam": s["fam"], "len": s["len"], "acc": n["acc"],
                    "lo99": n["lo99"], "hi99": n["hi99"], "override": s["override"],
                    "mf": s.get("mf_s2_zeroed", {}).get("acc"),
                    "nor": s.get("nor_cheat", {}).get("acc"), "nor_lo99": s.get("nor_cheat", {}).get("lo99")}
    c1 = [s for s in scored.get(c, []) if s["len"] <= 16]
    rec["plant_scored"] = best
    rec["plant_c1"] = ({"acc": c1[0]["normal"]["acc"], "lo99": c1[0]["normal"]["lo99"], "override": c1[0]["override"]}
                       if c1 else None)
    rec["plant_dev"] = ({"fam": dev[c]["fam"], "len": dev[c]["len"], "acc": dev[c]["acc"]} if c in dev else None)
    if c in cheat_dev:
        rec["nor_dev"] = cheat_dev[c]["nor"]["acc"]
    if best and best["lo99"] > 0.60:
        cls = "PLANT-SOLVED"
    elif lc1 < 0.60:
        cls = "CAPPED-LC1"
    elif rb["lc2"] < 0.60:
        cls = "CAPPED-LC2" + ("" if rb["lc2_ci99"][1] < 0.60 else "(point)")
    else:
        cls = "UNDECIDED" + ("-ECONOMY" if rec["econ"] else "")
    rec["class"] = cls
    table.append(rec)
import collections
cnt = collections.Counter(t["class"] for t in table)
print(cnt)
save("table.json", {"rows": table, "counts": dict(cnt)})
lines = ["| cell | wave | env | physics | held acc / lo99 | lc1 census | lc1 fresh | lc2 [99%] | plant (64 fresh) | C1-space plant | NOR cheat | class |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for t in sorted(table, key=lambda t: (t["class"], -t["lc2"])):
    b = t["plant_scored"]
    ps = (f"{b['fam']} L{b['len']} {b['acc']:.3f} [{b['lo99']:.3f}] mf {b['mf']:.3f}" if b else
          (f"DEV16 {t['plant_dev']['fam']} {t['plant_dev']['acc']:.3f}" if t["plant_dev"] else "-"))
    c1 = f"{t['plant_c1']['acc']:.3f} [{t['plant_c1']['lo99']:.3f}]" if t["plant_c1"] else "-"
    nor = (f"{b['nor']:.3f} [{b['nor_lo99']:.3f}]" if b and b.get("nor") is not None else
           (f"DEV16 {t['nor_dev']:.3f}" if "nor_dev" in t else "-"))
    lines.append(f"| {t['cell'][:8]} | {t['wave']} | {t['env']} | {t['phys']} | {t['held_acc']:.3f} / {t['held_lo99']:.3f} | "
                 f"{t['lc1_census']:.3f} | {t['lc1_fresh']:.3f} | {t['lc2']:.3f} [{t['lc2_ci99'][0]:.3f},{t['lc2_ci99'][1]:.3f}] | "
                 f"{ps} | {c1} | {nor} | {t['class']} |")
(OUT / "table.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines[:3]))
