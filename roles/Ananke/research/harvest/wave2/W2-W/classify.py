"""W2-W step 2: final per-cell placement from out/labels.json (collect.py). No engine runs.
Writes null_placement.csv (454 C1 NULL evolve cells + 58 HOLD), out/placement.json, out/summary.json.
Class rules are in DEFINITIONS below and in the report; first match wins."""
import json, csv
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
L = json.load(open(HERE / "out/labels.json"))
BAR = 0.60          # impossibility convention shared by H-PLANT, W2-J, W2-M, W2-O, W2-T, W2-S
SIGBAR = 0.55       # plant competence = lo99 > .55 (C1's SIGNAL rule); W2-J used .60, W2-T used mean >= .60

EV = {  # evidence paths (relative to harvest/)
    "W2-T": "wave2/W2-T/out/table_t.json", "W2-U": "wave2/W2-U/out/task1b_big.json",
    "W2-J": "wave2/W2-J/out/table.json", "W2-S": "wave2/W2-S/out/t2_table.md;wave2/W2-S/out/epidemic_bound.json",
    "W2-L": "wave2/W2-L/out/t1_table.md", "W2-M": "wave2/W2-M/out/classification.json;wave2/W2-M/out/lc_maj.json",
    "W2-P": "wave2/W2-P/out/task2_timing.json;wave2/W2-P/REPORT.md(TASK1 inward)",
    "C1": "roles/Ananke/pte/c1_rows/cells.jsonl.gz(result.plant)", "P-2": "wave2/P-1/decay_plant*.json", "W2-W": "wave2/W2-W/out/refresh_check.json",
}

def certificates(o):
    """Sound any-program upper bounds with controlled sampling error, as (value, source)."""
    c = []
    if o.get("w2t_combined") is not None: c.append((o["w2t_combined"], "W2-T combined lc+exact-wake, held set"))
    if o.get("w2u_joint") is not None: c.append((o["w2u_joint"], "W2-U joint, 1024 worlds"))
    if o.get("w2u_joint_held") is not None: c.append((o["w2u_joint_held"], "W2-U joint, held set"))
    if o.get("w2j_lc2_hi") is not None: c.append((o["w2j_lc2_hi"], "W2-J LC2 99% upper, 64 fresh worlds"))
    if o.get("w2s_epidemic") is not None: c.append((o["w2s_epidemic"], "W2-S epidemic bound (analytic)"))
    if o.get("w2m_lc") is not None: c.append((o["w2m_lc"], "W2-M k-sensor light cone, held set"))
    return c

def ceiling_lt_thr(o):
    thr = o.get("w2u_thr") or o.get("w2p_thr") or 0.614
    vals = [v for v, _ in certificates(o) if "LC2" not in _]
    pt = o.get("w2j_lc2")
    if pt is not None: vals.append(pt)
    return any(v < thr for v in vals), thr

RC = {r["cell"]: r for r in json.load(open(HERE / "out/refresh_check.json"))["rows"]}

def plant_tier(o):
    """Best task-solving plant evidence, independent of admissibility: (tier, source, note)."""
    fam = o["family"]; k = o["cell"][:8]
    if o.get("w2l_class") == "PLANT-SOLVED": return "IN_SPACE", "W2-L", "P-FLIP in exact genome space"
    wm = o.get("w2m_class") or ""
    if wm.startswith("PLANT-SOLVED"):
        return "IN_SPACE", "W2-M", "MAJ integrator member fitting the row genome" + (" (weak/post hoc)" if "weak" in wm else "")
    if fam in ("RELAY", "HOLD") and (o["rec_plant_acc"] or 0) >= BAR:
        if o["rec_plant_in_space"]:
            return "IN_SPACE", "C1", "recorded %s acc %.3f at own prog_len" % (o["rec_plant"], o["rec_plant_acc"])
        return "OVERRIDE", "C1", "recorded %s acc %.3f only at prog_len %s > own %s" % (
            o["rec_plant"], o["rec_plant_acc"], o["rec_plant_prog_len"], o["prog_len"])
    rc = RC.get(o["cell"])
    if rc and rc["refresh"] >= BAR and rc["refresh_lo99"] > SIGBAR:
        return ("IN_SPACE" if rc["refresh_in_space"] else "OVERRIDE"), "W2-W",             "relay_refresh (15 lines) %.3f [lo99 %.3f]; decay-0 relay_flood %.3f" % (rc["refresh"], rc["refresh_lo99"], rc["flood_decay0"])
    if o.get("w2j_class") == "PLANT-SOLVED":
        if (o.get("w2j_c1space_lo99") or 0) > SIGBAR:
            return "OVERRIDE", "W2-J", "16-line C1-space plant lo99 %.3f (row genome raised)" % o["w2j_c1space_lo99"]
        return "BEYOND_C1", "W2-J", "only a >16-line plant (lo99 %.3f)" % (o.get("w2j_plant_lo99") or 0)
    if k == "c7ec8097": return "OVERRIDE", "W2-M", "INT_2 at prog_len 14, payload 2 (C1 space), lo99 .636"
    if (o.get("w2s_class") or "") == "R-CANDIDATE": return "BEYOND_C1", "W2-S", "only 22-28-line refresh plants (> C1 prog_len 16)"
    return "NONE", "", ""

def classify(o):
    fam = o["family"]; k = o["cell"][:8]
    cert = certificates(o)
    best = min(cert) if cert else (None, None)
    o["best_bound"] = round(best[0], 4) if cert else None; o["best_bound_src"] = best[1]
    ev = []
    # 1. construction placement (MAJ graph rows capped as placed, open under inward placement by a margin
    #    larger than the gap between W2-P's model and the tightest certificate)
    if o.get("w2p_placement_only"):
        gap = (o["w2p_joint"] - best[0]) if cert else 0.0
        if o["w2p_inward"] - max(gap, 0) >= o["w2p_thr"]:
            return "CONSTRUCTION_PLACEMENT", ["W2-P"], "capped as placed (min bound %.3f); inward %.3f" % (best[0], o["w2p_inward"])
    # 2. P proven
    if cert and best[0] < BAR:
        srcs = sorted({s for v, s in cert if v < BAR})
        return "P_PROVEN", [s.split()[0] for s in srcs], "; ".join("%s=%.3f" % (s, v) for v, s in cert if v < BAR)
    # 3-5. admissibility (W2-T exclusive classes; W2-T order puts TRUNCATED first)
    wt = o["w2t_class"]
    if wt == "TRUNCATED": return "LATCHED_PARTIAL", ["W2-T"], "early-latch champion (W2-T F4)"
    if wt == "INERT": return "INERT", ["W2-T"], "readout dead in >= 48/64 held worlds"
    if wt == "FLAT": return "FLAT", ["W2-T"], "max_acc over all generations <= .5"
    # 6. admissible (incl. MARGINAL and the one DEGRADED cell)
    t, tsrc, tnote = plant_tier(o)
    if t == "IN_SPACE": return "PLANT_SOLVED_IN_SPACE", [tsrc], tnote
    if t == "OVERRIDE": return "PLANT_SOLVED_OVERRIDE", [tsrc], tnote
    if t == "BEYOND_C1": return "R_CANDIDATE", [tsrc], tnote
    ws = o.get("w2s_class") or ""
    if ws.startswith("PLANT-DESIGN"): return "PLANT_DESIGN", ["W2-S"], ws
    lt, thr = ceiling_lt_thr(o)
    if ws.startswith("P-CANDIDATE"): return "P_CANDIDATE", ["W2-S"], ws
    if lt: return "P_CANDIDATE", ["W2-U/W2-P/W2-J"], "a bound in [.60, %.3f) or W2-J LC2 point < .60 with CI straddling" % thr
    if fam == "RELAY" and o["cell"] in RC:
        rc = RC[o["cell"]]
        return "UNDECIDED", ["W2-W"], "relay_flood and relay_refresh both fail (refresh %.3f, decay-0 flood %.3f): decay is not the binding dial" % (rc["refresh"], rc["flood_decay0"])
    return "UNDECIDED", [], (o.get("w2j_class") or ws or (o.get("w2m_class") or "") or "no plant, no cap")

rows = []
for o in L:
    cls, srcs, why = classify(o)
    t, tsrc, tnote = plant_tier(o)
    o["plant_tier"] = t; o["plant_src"] = tsrc; o["plant_note"] = tnote
    rc = RC.get(o["cell"])
    o["w2w_refresh"] = ("%.3f[lo%.3f]/flood_d0 %.3f" % (rc["refresh"], rc["refresh_lo99"], rc["flood_decay0"])) if rc else None
    o["final_class"] = cls; o["final_basis"] = why
    o["evidence_path"] = ";".join(EV.get(s, s) for s in dict.fromkeys(
        [x.replace("/W2-P/W2-J", "") for x in srcs] or ["W2-T"]))
    o["admissible"] = o["w2t_class"] in ("ADMISSIBLE", "DEGRADED")
    o["eligible_strict"] = cls == "PLANT_SOLVED_IN_SPACE" and o["admissible"] and not o["w2t_marginal"]
    o["eligible_lenient"] = cls == "PLANT_SOLVED_IN_SPACE" and o["admissible"]
    rows.append(o)

COLS = ["family", "cell", "wave", "topology", "update_mode", "d", "delta", "decay_shift", "prog_len", "c_op",
        "hplant_lc", "w2d_tags", "w2j_class", "w2j_lc2", "w2j_lc2_hi", "w2l_class", "w2s_class", "w2s_epidemic",
        "w2m_lc", "w2m_placement", "w2m_class", "w2p_joint", "w2p_inward", "w2p_capped", "w2u_joint",
        "w2u_joint_held", "w2u_thr", "w2u_capped", "w2t_class", "w2t_marginal", "w2t_combined", "w2t_flags",
        "w2o_class", "w2i_verdict", "w2q", "p1b", "p2_decay_artefact", "rec_plant", "rec_plant_acc",
        "rec_plant_in_space", "w2w_refresh", "plant_tier", "plant_src", "plant_note", "best_bound", "best_bound_src", "final_class", "final_basis", "admissible",
        "eligible_strict", "eligible_lenient", "evidence_path"]
def fmt(v):
    if isinstance(v, float): return "%.4f" % v
    return "" if v is None else v
order = {"XOR": 0, "FLIP": 1, "RELAY": 2, "MAJ": 3, "HOLD": 4}
rows.sort(key=lambda o: (order[o["family"]], o["final_class"], o["cell"]))
with open(HERE / "null_placement.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(COLS)
    for o in rows: w.writerow([fmt(o.get(c)) for c in COLS])
json.dump(rows, open(HERE / "out/placement.json", "w"), indent=0)

# ---- summary
S = defaultdict(Counter)
for o in rows: S[o["family"]][o["final_class"]] += 1
CAP = {"P_PROVEN", "CONSTRUCTION_PLACEMENT"}
den = {}
for fam in ["XOR", "FLIP", "RELAY", "MAJ", "HOLD"]:
    rr = [o for o in rows if o["family"] == fam]
    den[fam] = {"n": len(rr),
                "eligible_strict": sum(o["eligible_strict"] for o in rr),
                "eligible_lenient": sum(o["eligible_lenient"] for o in rr),
                "physics_capped": sum(o["final_class"] in CAP for o in rr),
                "of_which_construction_placement": sum(o["final_class"] == "CONSTRUCTION_PLACEMENT" for o in rr),
                "P_CANDIDATE": sum(o["final_class"] == "P_CANDIDATE" for o in rr),
                "plant_in_space_any_admissibility": sum(o["plant_tier"] == "IN_SPACE" for o in rr),
                "plant_in_space_but_INERT_FLAT_LATCHED": sum(o["plant_tier"] == "IN_SPACE" and o["final_class"] in ("INERT", "FLAT", "LATCHED_PARTIAL") for o in rr)}
    den[fam]["open"] = den[fam]["n"] - den[fam]["eligible_lenient"] - den[fam]["physics_capped"]
tot = {k: sum(den[f][k] for f in ["XOR", "FLIP", "RELAY", "MAJ"]) for k in den["XOR"]}
json.dump({"by_family": {f: dict(S[f]) for f in S}, "denominator": den, "denominator_4fam": tot},
          open(HERE / "out/summary.json", "w"), indent=1)
for f in ["XOR", "FLIP", "RELAY", "MAJ", "HOLD"]:
    print(f, dict(sorted(S[f].items())), den[f])
print("4fam", tot)
