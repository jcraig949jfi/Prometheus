"""W2-W step 1: collect every Wave-2 source label per C1 NULL evolve cell (and HOLD) from saved out/ files.
No engine runs. Output: out/labels.json (one dict per cell, source fields only, no final class)."""
import json, gzip, re, os, sys
from pathlib import Path

H = Path(__file__).resolve().parents[2]          # .../research/harvest
W2 = H / "wave2"
ROOT = H.parents[3]
OUT = Path(__file__).resolve().parent / "out"; OUT.mkdir(exist_ok=True)

def J(p): return json.load(open(p))

# ---------- population: W2-T table (exactly the held lo99 <= .55 evolve rows; verified == labels.SIGNAL false)
T = J(W2 / "W2-T/out/table_t.json")["rows"]
cells = {r["cell"]: {"family": r["family"], "cell": r["cell"]} for r in T}
full = {c[:8]: c for c in cells}
assert len(full) == len(cells) == 512
def fid(k):
    return full.get(k[:8]) if k[:8] in full else None

# ---------- C1 rows (physics fields used by P-1b / P-2 rules)
rows = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l)
    if r["cell_id"] in cells and r["kind"] == "evolve":
        rows[r["cell_id"]] = r
assert len(rows) == 512, len(rows)

import math
def hops(r):  # P-1b's hop-demand rule (P-1/mh_plant_census.py)
    ph = r["physics"]; d = r["env"]["d"]; t = ph["topology"]
    if t == "global": return 1
    if t in ("ring", "torus"): return math.ceil(d / ph["radius"])
    return d

for c, o in cells.items():
    r = rows[c]; ph = r["physics"]; pl = r["result"].get("plant") or {}
    o.update(wave=r["wave"], topology=ph["topology"], update_mode=ph["update_mode"], d=r["env"]["d"],
             delta=r["env"]["delta"], decay_shift=ph["decay_shift"], prog_len=ph["prog_len"],
             state_dim=ph["state_dim"], c_op=ph["c_op"], cap=ph["cap"], collision=ph["collision"],
             loss=ph["loss"], held_lo99=r["result"]["held"]["lo99"] if "held" in r["result"] else None,
             rec_plant=pl.get("plant"), rec_plant_acc=pl.get("acc"), rec_plant_prog_len=pl.get("prog_len_used"))
    o["rec_plant_in_space"] = (pl.get("prog_len_used") == ph["prog_len"]) if pl else None

# ---------- W2-T
for r in T:
    o = cells[r["cell"]]
    o.update(w2t_class=r["class"], w2t_marginal=r["marginal"], w2t_combined=r["combined_bound"],
             w2t_flags="|".join(k for k, v in r["flags"].items() if v), w2t_max_acc=r["max_acc_any_gen"],
             w2t_lc_census=r["lc_census"], w2t_full_replay=r["full"])

# ---------- H-PLANT lc_census (all kinds; keyed by cell id)
lc = {x["cell"]: x["bound"] for x in J(H / "H-PLANT/out/lc_census.json")["rows"]}
for c, o in cells.items():
    o["hplant_lc"] = lc.get(c)

# ---------- W2-D mine_c1 placement tags
place = J(W2 / "W2-D/out/mine_c1.json")["place"]
for c, o in cells.items():
    o["w2d_tags"] = "|".join(place.get(c, []))

# ---------- W2-J (XOR)
for r in J(W2 / "W2-J/out/table.json")["rows"]:
    c = fid(r["cell"]); o = cells[c]
    o.update(w2j_class=r["class"], w2j_lc2=r.get("lc2"), w2j_lc2_hi=(r.get("lc2_ci99") or [None, None])[1],
             w2j_lc1_fresh=r.get("lc1_fresh"))
    ps = r.get("plant_scored"); pc = r.get("plant_c1")
    o["w2j_plant_lo99"] = ps.get("lo99") if isinstance(ps, dict) else None
    o["w2j_c1space_lo99"] = pc.get("lo99") if isinstance(pc, dict) else None

# ---------- W2-L (FLIP) t1 table: 58 non-light-cone rows; the other 24 FLIP rows are W2-L's P (light cone)
w2l = {}
for line in open(W2 / "W2-L/out/t1_table.md"):
    m = re.match(r"\| ([0-9a-f]{16}) \|.*\*\*(PLANT-SOLVED|R-CANDIDATE|UNDECIDED)\*\*", line)
    if m: w2l[m.group(1)] = m.group(2)
assert len(w2l) == 58, len(w2l)
for c, o in cells.items():
    if o["family"] == "FLIP":
        o["w2l_class"] = w2l.get(c, "P(lightcone)")

# ---------- W2-S (FLIP) revised placement (REPORT s3), rebuilt from t2_table + report reassignments
epi = {x["cell"]: x["acc_bound"] for x in J(W2 / "W2-S/out/epidemic_bound.json")}
t2 = {}
for line in open(W2 / "W2-S/out/t2_table.md"):
    m = re.match(r"\| ([0-9a-f]{8}) \|.*\| ([^|]+) \|\s*$", line)
    if m: t2[m.group(1)] = m.group(2).strip()
assert len(t2) == 41, len(t2)
DEMOTED = {"17b093a7", "2aefc9fe", "a4d9f2e4", "f6cfdf82", "bfa85a55"}   # W2-S F4
for c, o in cells.items():
    if o["family"] != "FLIP": continue
    o["w2s_epidemic"] = epi.get(c)
    k = c[:8]; L = o["w2l_class"]
    if L == "P(lightcone)": s = "P(lightcone)"
    elif L == "PLANT-SOLVED": s = "PLANT-SOLVED"
    elif L == "R-CANDIDATE": s = "UNDECIDED(demoted R-CAND, copy-range)" if k in DEMOTED else "R-CANDIDATE"
    else:
        t = t2[k]
        if epi.get(c) is not None and epi[c] < 0.60: s = "P(epidemic)"
        elif t.startswith("UNDECIDED"): s = "UNDECIDED(plant inadequate)"
        elif k == "12492333": s = "UNDECIDED(fails at 32 pairs)"
        elif t.startswith("PLANT-DESIGN (econ"): s = "PLANT-DESIGN(econ, confirmed)"
        elif t.startswith("PLANT-DESIGN/P joint"): s = "PLANT-DESIGN(econ joint, screen only)"
        elif t.startswith("P-candidate"): s = "P-CANDIDATE(single timing dial)"
        elif t.startswith("joint (screen"): s = "P-CANDIDATE(joint, screen only)"
        elif t.startswith("joint"): s = "P-CANDIDATE(joint, confirmed)"
        else: raise ValueError(t)
    o["w2s_class"] = s

# ---------- W2-M (MAJ): k-sensor light cone (all 162) + 30-row sample classification
for r in J(W2 / "W2-M/out/lc_maj.json")["rows"]:
    if r["cell"] in cells:
        cells[r["cell"]].update(w2m_lc=r["lc_bound"], w2m_placement=r["placement"])
for r in J(W2 / "W2-M/out/classification.json"):
    if r["set"] == "signal": continue
    c = fid(r["cell"]); o = cells[c]
    weak = r["cell"] in ("437ca0ac", "070257d7", "13a086e9", "3d20243a")
    o["w2m_class"] = r["class"] + ("(weak)" if (weak and r["class"] == "PLANT-SOLVED") else "") + \
        (("[" + ",".join(r["tags"]) + "]") if r["tags"] else "")
    o["w2m_plant_lo99"] = r.get("plant_lo99"); o["w2m_override_INT2"] = r.get("override_INT_2")

# ---------- W2-P (RELAY/MAJ joint ceilings; MAJ inward)
for r in J(W2 / "W2-P/out/task2_timing.json")["rows"]:
    if r["cell"] in cells:
        o = cells[r["cell"]]
        o["w2p_joint"] = r["ceil_joint"]; o["w2p_thr"] = r["signal_attainable"]
        if "ceil_joint_inward" in r: o["w2p_inward"] = r["ceil_joint_inward"]
# inward ceilings live in task2 rows under some key; fall back to the report's MAJ table
P_INWARD = {"e41b7b13": .811, "5edb4474": .819, "09c6dc85": .814, "699c8b2a": .732, "0677e0ae": .619,
            "0327a9ab": .670}   # W2-P s1 F3: the 6 placement-only rows (inward ceiling >= .614)
# inward joint ceilings for the 35 MAJ graph rows: W2-P REPORT TASK1 table, last column "ceiling orig / inward"
for line in open(W2 / "W2-P/REPORT.md", encoding="utf-8"):
    m = re.match(r"\| ([0-9a-f]{8}) \| (random|smallworld) \|.*\| (\.\d+) / (\.\d+) \|\s*$", line)
    if m and fid(m.group(1)):
        cells[fid(m.group(1))]["w2p_inward"] = float(m.group(4))
for c, o in cells.items():
    if o["family"] in ("RELAY", "MAJ") and "w2p_joint" in o:
        o["w2p_capped"] = o["w2p_joint"] < o["w2p_thr"]
        o["w2p_placement_only"] = c[:8] in P_INWARD
    elif o["family"] in ("XOR", "FLIP"):
        o["w2p_capped"] = (o["hplant_lc"] is not None and o["hplant_lc"] < 0.60)   # W2-P used H-PLANT for these

# ---------- W2-U (1024-world and exact-held joint ceilings, all four families)
for r in J(W2 / "W2-U/out/task1b_big.json")["rows"]:
    if r["cell"] in cells:
        o = cells[r["cell"]]
        o.update(w2u_joint=r["big"]["joint"], w2u_joint_held=r["held"]["joint"], w2u_thr=r["thr"],
                 w2u_lc_big=r["big"]["lc"])
        if "joint_block" in r["big"]:
            o["w2u_joint_block"] = r["big"]["joint_block"]; o["w2u_copy_block"] = r["big"]["copy_block"]
        o["w2u_capped"] = r["big"]["joint"] < r["thr"]
        o["w2u_capped_held"] = r["held"]["joint"] < r["thr"]

# ---------- W2-O sample (16): checklist class from REPORT s3 table
W2O = {"6f82f9c7": "ADMISSIBLE", "2a226bec": "INERT", "abb5fb81": "ADMISSIBLE(LC marginal)", "9c941931": "CAPPED",
       "75779d26": "CAPPED(+flat)", "f30f89b0": "CAPPED", "b3e89ef5": "CAPPED", "64d33b89": "ADMISSIBLE",
       "94ced72f": "ADMISSIBLE(partly inert)", "e553999d": "INERT+flat", "3222a6ff": "ADMISSIBLE",
       "89bd6fdb": "ADMISSIBLE(energy death)", "c9d2ff6e": "INERT+flat", "0327a9ab": "INERT+flat",
       "6e0ca725": "ADMISSIBLE(transient)", "87216808": "ADMISSIBLE"}
for k, v in W2O.items():
    c = fid(k)
    if c: cells[c]["w2o_class"] = v
    else: print("W2-O cell not in population:", k)

# ---------- W2-I hop verdicts (only NULL cells it touched)
for r in J(W2 / "W2-I/hop_verdicts.json")["rows"]:
    c = fid(r["cell"])
    if c: cells[c]["w2i_verdict"] = r["verdict"] + ((" " + r["refinement"]) if r["refinement"] else "")

# ---------- W2-Q lottery (NULL / HOLD cells it touched)
for k, v in J(W2 / "W2-Q/out/q2_lottery.json").items():
    c = fid(k)
    if c: cells[c]["w2q"] = "lottery-panel (rules=%s, near-SIGNAL NULL)" % v["rules"]

# ---------- P-1b (hop demand x relay_flood viability) and P-2 (decay artefact), RELAY only
for c, o in cells.items():
    if o["family"] != "RELAY": continue
    h = hops(rows[c]); ok = (o["rec_plant_acc"] or 0) > 0.60
    o["p1b"] = ("multi" if h >= 2 else "one") + "-hop/" + ("plant-ok" if ok else "plant-fail") + \
        ("" if (o["hplant_lc"] or 0) >= 0.95 else "/lc<.95")
    o["p2_decay_artefact"] = (not ok) and o["decay_shift"] > 0

json.dump(list(cells.values()), open(OUT / "labels.json", "w"), indent=0)
print("cells", len(cells))
