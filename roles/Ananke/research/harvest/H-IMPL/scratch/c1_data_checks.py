"""H-IMPL read-only checks against the committed C1 rows (c1_rows/cells.jsonl.gz)."""
import collections, gzip, json, sys
sys.path.insert(0, ".")
from prometheus.ananke import campaign as C

rows = [json.loads(l) for l in gzip.open("roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
print("rows", len(rows), collections.Counter(r["wave"] for r in rows))
cfg = C.CampaignConfig()

def inert(dial, lv, ev, fam):
    """True if this dial cannot change the dynamics/env given the other levels."""
    topo = lv["topology"]
    if dial == "radius": return topo not in ("ring", "torus")
    if dial == "k_random": return topo != "random"
    if dial == "rewire": return topo != "smallworld"
    if dial == "dest_mode": return topo == "global"
    if dial == "update_p": return lv["update_mode"] == "sync"
    if dial == "update_period": return lv["update_mode"] == "async"
    if dial == "adapt_shift": return not lv["plastic_route"] or topo == "global"
    if dial == "collision": return lv["cap"] == 0
    if dial == "loss_per_hop": return lv["loss"] == 0 or (topo not in ("ring", "torus") or lv["radius"] == 1)
    if dial == "gap": return fam != "HOLD"
    if dial == "delta": return fam == "HOLD"
    if dial == "block": return fam != "FLIP"
    if dial == "d": return fam == "HOLD" or topo == "global"
    return False

# (c) B transects on inert dials
B = [r for r in rows if r["wave"] == "B"]
tr = collections.Counter()
for r in B:
    e = r["extra"]
    base_lv, base_ev = r["levels"], r["env_levels"]
    tr[(r["env"]["family"], e["track"], e["transect"], e["base"], inert(e["transect"], base_lv, base_ev, r["env"]["family"]))] += 1
inert_tr = {k: v for k, v in tr.items() if k[-1]}
print("\nB transects total", len(tr), "on an INERT dial:", len(inert_tr))
for k, v in sorted(inert_tr.items()): print("  ", k[:4], "cells", v)
bd = json.load(open("roles/Ananke/pte/c1_rows/boundaries_verdicts.json"))
print("\nboundary verdicts on inert dials:")
base_cells = {r["cell_id"]: r for r in rows}
for v in bd:
    # find a B row of that transect/base to recover base levels
    ex = next(r for r in B if r["env"]["family"] == v["family"] and r["extra"]["transect"] == v["dial"]
              and r["extra"]["base"] == v["base"] and r["extra"]["track"] == v["track"])
    if inert(v["dial"], ex["levels"], ex["env_levels"], v["family"]):
        print("  ", v["label"], v["family"], v["track"], v["metric"], v["dial"], "base", v["base"], "means", [round(x,3) for x in v["means"]])

# (a) REACH_BEYOND_HOP on MAJ/XOR
EV = [r for r in rows if r["kind"] == "evolve"]
for fam in ("MAJ", "XOR", "RELAY", "HOLD", "FLIP"):
    rs = [r for r in EV if r["env"]["family"] == fam]
    rb = [r for r in rs if C.classify(r, cfg)["REACH_BEYOND_HOP"]]
    loc = [r for r in rb if r["result"]["held"]["comm_delta"] < 0.02]
    print(f"\n{fam}: evolve {len(rs)}; REACH_BEYOND_HOP {len(rb)}; of which comm_delta<.02: {len(loc)}")
D = [r for r in rows if r["wave"] == "D" and r["kind"] == "adjudicate"]
for r in D:
    print("  D", r["env"]["family"], r["extra"]["source_cell"][:8], "twin beyond_hop", r["result"]["twin"]["beyond_hop"],
          "reach", round(r["result"]["twin"]["reach"], 2), "d", r["env"]["d"], "n", r["physics"]["n_sites"],
          "size_x2.25->", r["result"]["transplants"].get("size_x2.25"))
# (b) MEMORY_WITHOUT_USE on HOLD
mw = [r for r in EV if "MEMORY_WITHOUT_USE" in r.get("anomalies", [])]
print("\nMEMORY_WITHOUT_USE flags", len(mw), collections.Counter(r["env"]["family"] for r in mw))
hold = [r for r in EV if r["env"]["family"] == "HOLD"]
def mwu(r, scale):
    tw, h = r["result"].get("twin", {}), r["result"]["held"]
    return tw.get("persist", 0) > 3 * scale and tw.get("div_frac_readout", 0) > 0.25 and h["acc"] <= 0.55
print("HOLD flags with delta:", sum(mwu(r, r["env"]["delta"]) for r in hold), " with gap:", sum(mwu(r, r["env"]["gap"]) for r in hold))
# (d) B2 search seed collisions
B2 = [r for r in rows if r["wave"] == "B2"]
ss = collections.defaultdict(list)
for r in B2: ss[r["search_seed"]].append((r["env"]["family"], r["extra"]["track"], r["extra"]["transect"], r["kind"]))
col = {k: v for k, v in ss.items() if len(v) > 1}
print("\nB2 rows", len(B2), "distinct seeds", len(ss), "seeds shared by >1 row", len(col))
for k, v in list(col.items())[:6]: print("  ", k, v)
allss = collections.defaultdict(list)
for r in rows: allss[r["search_seed"]].append((r["wave"], r["kind"]))
print("search_seed shared across rows (all waves):", sum(1 for v in allss.values() if len(v) > 1))
# (f) global cells recorded as dest_mode=all
g = [r for r in rows if r["physics"]["topology"] == "global"]
print("\nglobal cells", len(g), "levels.dest_mode=='all' while physics sample:", sum(r["levels"]["dest_mode"] == "all" for r in g))
# (h) transplant size factor
for r in D:
    print("  D size", r["physics"]["n_sites"], "->", 144 if r["physics"]["n_sites"] < 144 else 324)
